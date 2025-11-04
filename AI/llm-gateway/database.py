"""
데이터베이스 관리 모듈

대화 히스토리, 요청 로그, 비용 관리 등을 영구 저장하기 위한 데이터베이스 모듈입니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import json

from config import settings

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
        
        try:
            if settings.db_url:
                # URL을 통한 연결
                db_url = settings.db_url.strip()
                if not db_url or db_url == "your_db_url_here":
                    return None
            elif settings.db_host:
                # 개별 설정을 통한 연결
                # 필수 필드 확인
                if not settings.db_host.strip() or not settings.db_name or not settings.db_user:
                    return None
                
                # URL 인코딩 (특수문자 처리)
                db_user = quote_plus(str(settings.db_user))
                db_host = settings.db_host.strip()
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
                echo=settings.debug
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self._initialized = True
            return self.engine
        except Exception as e:
            print(f"Database initialization error: {e}")
            return None
    
    def create_tables(self):
        """테이블 생성"""
        if self.engine:
            Base.metadata.create_all(bind=self.engine)
    
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
                return False
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            print(f"Database health check failed: {e}")
            return False


# 전역 데이터베이스 관리자 인스턴스
db_manager = DatabaseManager()


# ============= 편의 함수 =============

def save_conversation_to_db(session_id: str, messages: List[Dict[str, str]], system_prompt: Optional[str] = None):
    """대화 히스토리를 DB에 저장"""
    if not db_manager._initialized:
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
            else:
                db_session.updated_at = datetime.utcnow()
            
            # 기존 메시지 삭제 후 재저장 (간단한 구현)
            session.query(ConversationMessage).filter_by(session_id=session_id).delete()
            
            # 메시지 저장
            for msg in messages:
                db_message = ConversationMessage(
                    session_id=session_id,
                    role=msg["role"],
                    content=msg["content"]
                )
                session.add(db_message)
    except Exception as e:
        print(f"Failed to save conversation to DB: {e}")


def load_conversation_from_db(session_id: str) -> List[Dict[str, str]]:
    """DB에서 대화 히스토리 로드"""
    if not db_manager._initialized:
        return []
    
    try:
        with db_manager.get_session() as session:
            messages = session.query(ConversationMessage)\
                .filter_by(session_id=session_id)\
                .order_by(ConversationMessage.created_at)\
                .all()
            
            return [{"role": msg.role, "content": msg.content} for msg in messages]
    except Exception as e:
        print(f"Failed to load conversation from DB: {e}")
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
    except Exception as e:
        print(f"Failed to log API request: {e}")


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
    except Exception as e:
        print(f"Failed to log cost: {e}")


