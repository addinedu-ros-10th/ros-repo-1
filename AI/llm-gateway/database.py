"""
데이터베이스 관리 모듈

대화 히스토리, 요청 로그, 비용 관리 등을 영구 저장하기 위한 데이터베이스 모듈입니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON, Index, text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import json
import logging

from config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

Base = declarative_base()


# ============= 데이터베이스 모델 =============

class ConversationSession(Base):
    """대화 세션 테이블"""
    __tablename__ = "conversation_sessions"
    
    session_id = Column(String(255), primary_key=True, index=True)
    user_id = Column(String(255), index=True, nullable=True)  # 사용자 ID (향후 확장용)
    system_prompt = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 인덱스
    __table_args__ = (
        Index('idx_user_created', 'user_id', 'created_at'),
    )


class ConversationMessage(Base):
    """대화 메시지 테이블"""
    __tablename__ = "conversation_messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), index=True, nullable=False)
    role = Column(String(50), nullable=False)  # system, user, assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 인덱스
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
    )


class APIRequestLog(Base):
    """API 요청 로그 테이블"""
    __tablename__ = "api_request_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), index=True, nullable=True)
    endpoint = Column(String(255), nullable=False)
    method = Column(String(10), nullable=False)
    request_data = Column(JSON, nullable=True)
    response_data = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=False)
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 인덱스
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
        Index('idx_endpoint_created', 'endpoint', 'created_at'),
    )


class CostLog(Base):
    """비용 로그 테이블 (OpenAI API 사용 비용 추적)"""
    __tablename__ = "cost_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), index=True, nullable=True)
    service_type = Column(String(50), nullable=False)  # stt, chat, tts
    model = Column(String(100), nullable=False)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    cost_usd = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 인덱스
    __table_args__ = (
        Index('idx_session_created', 'session_id', 'created_at'),
        Index('idx_service_created', 'service_type', 'created_at'),
    )


# ============= 데이터베이스 관리 클래스 =============

class DatabaseManager:
    """데이터베이스 관리자"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False
    
    def initialize(self):
        """데이터베이스 연결 초기화"""
        from urllib.parse import quote_plus
        import re
        import os
        
        try:
            if settings.db_url:
                logger.debug(f"DB URL (raw): {settings.db_url}")
                # URL을 통한 연결
                raw_url = settings.db_url.strip()
                if not raw_url or raw_url == "your_db_url_here":
                    logger.debug("DB URL not configured or using placeholder")
                    return None
                
                # Docker 컨테이너 내부에서 localhost를 host.docker.internal로 변환
                # 컨테이너 내부인지 확인 (.dockerenv 파일 존재 여부로 판단)
                if os.path.exists('/.dockerenv') and 'localhost' in raw_url:
                    raw_url = raw_url.replace('localhost', 'host.docker.internal')
                    logger.info(f"DB URL adjusted for Docker: host.docker.internal")
                
                # URL 파싱하여 특수문자 인코딩 처리
                # 비밀번호에 #, @, ! 등의 특수문자가 포함될 수 있으므로
                # URL을 수동으로 파싱하여 각 구성 요소를 인코딩한 후 재조합
                try:
                    # postgresql://user:password@host:port/database 형식 파싱
                    # 비밀번호에 @가 포함될 수 있으므로, 마지막 @를 기준으로 분리
                    # 형식: scheme://[user[:password]@]host[:port][/database]
                    
                    # scheme 추출
                    if '://' not in raw_url:
                        raise ValueError("Invalid URL format: missing ://")
                    
                    scheme_part, rest = raw_url.split('://', 1)
                    scheme = scheme_part.strip()
                    
                    # @가 있는지 확인 (사용자 인증 정보 포함 여부)
                    # 호스트/포트/database 부분에서 마지막으로 나타나는 @를 찾아야 함
                    # 하지만 비밀번호에 @가 포함될 수 있으므로, 역순으로 검색
                    # 형식: [user:password@]host[:port][/database]
                    # 비밀번호의 @는 이미 인코딩되어 있어야 하지만, 
                    # 사용자가 인코딩하지 않은 상태로 제공할 수 있음
                    
                    # 더 안전한 방법: 정규식으로 마지막 @를 찾되, 
                    # 포트(:숫자)나 경로(/) 이후의 @는 무시
                    # 패턴: user:password@host:port/db
                    # 마지막 @는 host 앞에 있어야 함
                    
                    # @ 다음에 호스트가 오고, 그 다음 :port나 /path가 오는 패턴 찾기
                    # 호스트 이름은 알파벳, 숫자, 점, 하이픈, 언더스코어만 포함
                    # 예: @localhost:15432 또는 @localhost/iot_care
                    # 비밀번호에 @가 포함될 수 있으므로, 호스트 이름 패턴으로 정확히 매칭
                    at_pattern = r'@([a-zA-Z0-9._-]+)(?::(\d+))?(/[^?#]*)?$'
                    match = re.search(at_pattern, rest)
                    
                    if match:
                        # match가 성공하면 @ 이전까지가 사용자:비밀번호
                        auth_part = rest[:match.start()]  # user:password 또는 user
                        
                        host = match.group(1)
                        port = match.group(2)
                        path = match.group(3) or ''
                        
                        # 사용자와 비밀번호 분리
                        if ':' in auth_part:
                            user, password = auth_part.split(':', 1)
                        else:
                            user = auth_part
                            password = None
                    else:
                        # @가 없으면 인증 정보 없음
                        user = None
                        password = None
                        # host:port/path 형식 파싱
                        if '/' in rest:
                            host_port, path = rest.split('/', 1)
                            path = '/' + path
                        else:
                            host_port = rest
                            path = ''
                        
                        if ':' in host_port:
                            host, port = host_port.rsplit(':', 1)
                        else:
                            host = host_port
                            port = None
                    
                    # 각 구성 요소 인코딩
                    encoded_user = quote_plus(user) if user else None
                    encoded_password = quote_plus(password) if password else None
                    encoded_host = host  # 호스트는 일반적으로 인코딩 불필요
                    
                    # 데이터베이스 이름 인코딩 (path에서 '/' 제거)
                    db_name = path.lstrip('/')
                    encoded_db_name = quote_plus(db_name, safe='') if db_name else ''
                    
                    # URL 재구성
                    if encoded_user and encoded_password:
                        netloc = f"{encoded_user}:{encoded_password}@{encoded_host}"
                    elif encoded_user:
                        netloc = f"{encoded_user}@{encoded_host}"
                    else:
                        netloc = encoded_host
                    
                    if port:
                        netloc = f"{netloc}:{port}"
                    
                    if encoded_db_name:
                        path = f"/{encoded_db_name}"
                    else:
                        path = ""
                    
                    db_url = f"{scheme}://{netloc}{path}"
                    logger.debug(f"DB URL (encoded): {db_url}")
                except Exception as parse_error:
                    logger.warning(f"URL parsing error: {parse_error}, using raw URL")
                    # 파싱 실패 시 원본 URL 사용 (기존 동작)
                    db_url = raw_url
            elif settings.db_host:
                logger.debug(f"DB HOST: {settings.db_host}")
                # 개별 설정을 통한 연결
                # 필수 필드 확인
                if not settings.db_host.strip() or not settings.db_name or not settings.db_user:
                    logger.debug("DB host configuration incomplete")
                    return None
                
                # URL 인코딩 (특수문자 처리)
                db_user = quote_plus(str(settings.db_user))
                db_host = settings.db_host.strip()
                
                # Docker 컨테이너 내부에서 localhost를 host.docker.internal로 변환
                if os.path.exists('/.dockerenv') and db_host == 'localhost':
                    db_host = 'host.docker.internal'
                    logger.info(f"DB HOST adjusted for Docker: host.docker.internal")
                
                db_port = settings.db_port or 5432
                db_name = settings.db_name.strip()
                
                if settings.db_password:
                    db_password = quote_plus(str(settings.db_password))
                    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                else:
                    db_url = f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}"
            else:
                # DB 설정이 없으면 None 반환
                return None
            
            # 빈 URL 체크
            if not db_url or db_url.startswith("postgresql://@"):
                return None
            
            self.engine = create_engine(
                db_url,
                poolclass=NullPool,  # 비동기 환경에서는 NullPool 사용 권장
                echo=settings.debug,
                pool_pre_ping=True  # 연결 상태 확인 후 재연결
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self._initialized = True
            logger.info("Database connection initialized successfully")
            return self.engine
        except Exception as e:
            logger.error(f"Database initialization error: {e}", exc_info=True)
            return None
    
    def create_tables(self):
        """테이블 생성 (중복 테이블/인덱스 오류 무시)"""
        if not self.engine:
            logger.warning("Cannot create tables: database engine not initialized")
            return
        
        try:
            Base.metadata.create_all(bind=self.engine, checkfirst=True)
            logger.info("Database tables created/verified successfully")
        except (OperationalError, ProgrammingError) as e:
            # 중복 테이블/인덱스 오류는 무시 (이미 존재하는 경우)
            error_str = str(e).lower()
            if 'already exists' in error_str or 'duplicate' in error_str:
                logger.info("Tables/indices already exist, skipping creation")
            else:
                logger.error(f"Failed to create tables: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error during table creation: {e}")
            raise
    
    @contextmanager
    def get_session(self):
        """세션 컨텍스트 매니저"""
        if not self._initialized:
            self.initialize()
        
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Set DB_URL or DB_HOST in .env")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """동기 세션 반환 (비권장, 레거시 코드용)"""
        if not self._initialized:
            self.initialize()
        
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized. Set DB_URL or DB_HOST in .env")
        
        return self.SessionLocal()
    
    def health_check(self) -> bool:
        """데이터베이스 연결 상태 확인"""
        try:
            if not self.engine:
                logger.debug("Health check failed: engine not initialized")
                return False
            with self.engine.connect() as conn:
                # SQLAlchemy 2.0+에서는 text() 함수로 SQL 문자열을 감싸야 함
                # SELECT는 read-only이므로 commit 불필요
                conn.execute(text("SELECT 1"))
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False


# 전역 데이터베이스 관리자 인스턴스
db_manager = DatabaseManager()


# ============= 편의 함수 =============

def save_conversation_to_db(session_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None):
    """대화 히스토리를 DB에 저장"""
    if not db_manager._initialized:
        logger.debug("Database not initialized, skipping conversation save")
        return
    
    try:
        with db_manager.get_session() as session:
            # 세션 정보 저장/업데이트
            db_session = session.query(ConversationSession).filter_by(session_id=session_id).first()
            if not db_session:
                db_session = ConversationSession(
                    session_id=session_id,
                    system_prompt=system_prompt or settings.default_system_prompt
                )
                session.add(db_session)
                logger.debug(f"Created new conversation session: {session_id}")
            else:
                db_session.updated_at = datetime.utcnow()
                logger.debug(f"Updated conversation session: {session_id}")
            
            # 기존 메시지 삭제 후 재저장 (간단한 구현)
            deleted_count = session.query(ConversationMessage).filter_by(session_id=session_id).delete()
            if deleted_count > 0:
                logger.debug(f"Deleted {deleted_count} existing messages for session: {session_id}")
            
            # 메시지 저장
            for msg in messages:
                db_message = ConversationMessage(
                    session_id=session_id,
                    role=msg["role"],
                    content=msg["content"]
                )
                session.add(db_message)
            logger.debug(f"Saved {len(messages)} messages for session: {session_id}")
    except Exception as e:
        logger.error(f"Failed to save conversation to DB: {e}", exc_info=True)


def load_conversation_from_db(session_id: str) -> List[Dict[str, str]]:
    """DB에서 대화 히스토리 로드"""
    if not db_manager._initialized:
        logger.debug("Database not initialized, returning empty conversation")
        return []
    
    try:
        with db_manager.get_session() as session:
            messages = session.query(ConversationMessage)\
                .filter_by(session_id=session_id)\
                .order_by(ConversationMessage.created_at)\
                .all()
            
            result = [{"role": msg.role, "content": msg.content} for msg in messages]
            logger.debug(f"Loaded {len(result)} messages for session: {session_id}")
            return result
    except Exception as e:
        logger.error(f"Failed to load conversation from DB: {e}", exc_info=True)
        return []


def log_api_request(session_id: Optional[str], endpoint: str, method: str, 
                   request_data: Optional[Dict], response_data: Optional[Dict],
                   status_code: int, processing_time_ms: Optional[float] = None):
    """API 요청 로그 저장"""
    if not db_manager._initialized:
        return
    
    try:
        with db_manager.get_session() as session:
            log = APIRequestLog(
                session_id=session_id,
                endpoint=endpoint,
                method=method,
                request_data=request_data,
                response_data=response_data,
                status_code=status_code,
                processing_time_ms=processing_time_ms
            )
            session.add(log)
            logger.debug(f"Logged API request: {method} {endpoint} (status: {status_code})")
    except Exception as e:
        logger.error(f"Failed to log API request: {e}", exc_info=True)


def log_cost(session_id: Optional[str], service_type: str, model: str,
            input_tokens: Optional[int], output_tokens: Optional[int], cost_usd: float):
    """비용 로그 저장"""
    if not db_manager._initialized:
        return
    
    try:
        with db_manager.get_session() as session:
            cost_log = CostLog(
                session_id=session_id,
                service_type=service_type,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost_usd=cost_usd
            )
            session.add(cost_log)
            logger.debug(f"Logged cost: {service_type}/{model} - ${cost_usd:.6f}")
    except Exception as e:
        logger.error(f"Failed to log cost: {e}", exc_info=True)


