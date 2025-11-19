"""
데이터베이스 관리 모듈

대화 히스토리, 요청 로그, 비용 관리 등을 영구 저장하기 위한 데이터베이스 모듈입니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, Float, JSON, Index, text, Boolean
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
import json
import logging
import os

from .config import settings

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


class KeywordVoiceprint(Base):
    """키워드 음성 지문 테이블"""
    __tablename__ = "keyword_voiceprints"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    base_keyword = Column(String(255), nullable=False, index=True)  # 기준 키워드 (예: "alfred")
    stt_keyword = Column(String(255), nullable=False)  # STT 결과 키워드 (예: "rarpred")
    audio_data = Column(Text, nullable=True)  # 음성 지문 오디오 (Base64)
    session_id = Column(String(255), index=True, nullable=True)  # 세션 ID
    user_id = Column(String(255), index=True, nullable=True)  # 사용자 ID (향후 확장용)
    is_active = Column(Boolean, default=True, nullable=False)  # 활성화 여부
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 인덱스
    __table_args__ = (
        Index('idx_base_stt_keyword', 'base_keyword', 'stt_keyword'),
    )


class SystemPrompt(Base):
    """System Prompt 테이블"""
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)  # 프롬프트 이름
    content = Column(Text, nullable=False)  # 프롬프트 내용
    description = Column(Text, nullable=True)  # 프롬프트 설명 (선택사항)
    is_default = Column(Boolean, default=False, nullable=False)  # 기본 프롬프트 여부 (여러 개 가능)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 인덱스
    __table_args__ = (
        Index('idx_system_prompts_name', 'name'),
        Index('idx_system_prompts_created', 'created_at'),
        Index('idx_system_prompts_default', 'is_default'),
    )


class SystemPromptUsage(Base):
    """마지막 사용 System Prompt 추적 테이블"""
    __tablename__ = "system_prompt_usage"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), index=True, nullable=True)  # 사용자 ID (향후 확장용)
    session_id = Column(String(255), index=True, nullable=True)  # 세션 ID
    system_prompt_id = Column(Integer, nullable=False, index=True)  # 사용한 System Prompt ID
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 인덱스
    __table_args__ = (
        Index('idx_user_session', 'user_id', 'session_id'),
        Index('idx_prompt_usage_created', 'created_at'),
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
        """테이블 생성 (중복 테이블/인덱스 오류 무시, 생성 후 검증)"""
        if not self.engine:
            logger.warning("Cannot create tables: database engine not initialized")
            print("⚠ Cannot create tables: database engine not initialized")
            return False
        
        from sqlalchemy import inspect
        inspector = inspect(self.engine)
        required_tables = {'conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs', 'keyword_voiceprints', 'system_prompts', 'system_prompt_usage'}
        
        # 현재 스키마 확인
        try:
            with self.engine.connect() as conn:
                current_schema = conn.execute(text("SELECT current_schema()")).scalar()
                logger.debug(f"Current schema: {current_schema}")
        except Exception as e:
            logger.warning(f"Could not get current schema: {e}")
            current_schema = "public"
        
        try:
            # 테이블 생성 전에 현재 테이블 목록 확인
            existing_tables_before = set(inspector.get_table_names())
            logger.debug(f"Existing tables before creation: {existing_tables_before}")
            
            # SQLAlchemy로 테이블 생성 시도 (예외 발생해도 계속 진행)
            try:
                Base.metadata.create_all(bind=self.engine, checkfirst=True)
                logger.debug("Base.metadata.create_all() completed without exception")
            except (OperationalError, ProgrammingError) as create_error:
                # create_all()에서 예외가 발생했지만, 일부 테이블은 생성되었을 수 있음
                # 'already exists' 에러는 무시하고 계속 진행
                error_str = str(create_error).lower()
                if 'already exists' in error_str or 'duplicate' in error_str:
                    logger.debug(f"Got 'already exists' error from create_all(): {create_error}")
                else:
                    logger.warning(f"create_all() raised exception: {create_error}")
            except Exception as create_error:
                logger.warning(f"Unexpected error from create_all(): {create_error}")
            
            # 테이블 생성 후 검증 (스키마 명시)
            # inspector.get_table_names()는 기본적으로 모든 스키마를 보지만, 명시적으로 public 스키마 확인
            try:
                # public 스키마의 테이블만 확인
                with self.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                            AND table_type = 'BASE TABLE'
                    """))
                    existing_tables_after = {row[0] for row in result}
            except Exception as e:
                logger.warning(f"Could not query information_schema, using inspector: {e}")
                existing_tables_after = set(inspector.get_table_names())
            logger.debug(f"Existing tables after create_all() (public schema): {existing_tables_after}")
            
            created_tables = existing_tables_after - existing_tables_before
            missing_tables = required_tables - existing_tables_after
            
            # 누락된 테이블이 있으면 SQL로 직접 생성
            if missing_tables:
                logger.warning(f"Missing tables detected after create_all(): {missing_tables}")
                print(f"⚠ Missing tables detected: {', '.join(missing_tables)}")
                print(f"Attempting to create missing tables via SQL...")
                self._create_missing_tables(missing_tables)
                
                # 재검증 (스키마 명시, 재시도 로직)
                import time
                time.sleep(0.3)  # 테이블 생성 후 커밋 대기
                
                # 최대 5번 재시도
                all_verified = False
                for retry in range(5):
                    try:
                        with self.engine.connect() as conn:
                            # EXISTS를 사용하여 각 테이블 존재 여부 확인
                            existing_tables_after = set()
                            for table in required_tables:
                                result = conn.execute(text(f"""
                                    SELECT EXISTS (
                                        SELECT 1 
                                        FROM information_schema.tables 
                                        WHERE table_schema = 'public' 
                                            AND table_name = '{table}'
                                    )
                                """))
                                if result.scalar():
                                    existing_tables_after.add(table)
                            
                            missing_tables = required_tables - existing_tables_after
                            if not missing_tables:
                                all_verified = True
                                logger.info(f"All missing tables created successfully via SQL (verified on retry {retry + 1})")
                                print(f"✓ All missing tables created successfully via SQL")
                                break
                            elif retry < 4:
                                logger.debug(f"Retry {retry + 1}: Still missing {missing_tables}, waiting...")
                                time.sleep(0.2 * (retry + 1))  # 재시도마다 대기 시간 증가
                    except Exception as e:
                        logger.warning(f"Could not query information_schema for re-verification (retry {retry + 1}): {e}")
                        if retry < 4:
                            time.sleep(0.2 * (retry + 1))
                
                if not all_verified:
                    # 최종 확인 (다른 방법 시도)
                    try:
                        with self.engine.connect() as conn:
                            result = conn.execute(text("""
                                SELECT table_name 
                                FROM information_schema.tables 
                                WHERE table_schema = 'public' 
                                    AND table_type = 'BASE TABLE'
                                    AND table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
                            """))
                            existing_tables_after = {row[0] for row in result}
                            missing_tables = required_tables - existing_tables_after
                            
                            if missing_tables:
                                logger.error(f"Still missing tables after SQL creation: {missing_tables}")
                                print(f"✗ Still missing tables after SQL creation: {', '.join(missing_tables)}")
                                # 디버깅: 실제로 존재하는 테이블 확인
                                all_tables_result = conn.execute(text("""
                                    SELECT table_name 
                                    FROM information_schema.tables 
                                    WHERE table_schema = 'public' 
                                        AND table_type = 'BASE TABLE'
                                    ORDER BY table_name
                                """))
                                all_existing = [row[0] for row in all_tables_result]
                                print(f"Debug: All existing tables in public schema: {', '.join(all_existing)}")
                                return False
                            else:
                                logger.info(f"All tables verified on final check")
                                print(f"✓ All missing tables created successfully via SQL (final check)")
                                return True
                    except Exception as e:
                        logger.error(f"Final verification failed: {e}", exc_info=True)
                        print(f"✗ Final verification failed: {e}")
                        return False
            
            if created_tables:
                logger.info(f"Created new tables via SQLAlchemy: {', '.join(created_tables)}")
                print(f"✓ Created new tables: {', '.join(created_tables)}")
            
            # 최종 확인 (스키마 명시)
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                            AND table_type = 'BASE TABLE'
                    """))
                    existing_tables = {row[0] for row in result}
            except Exception as e:
                logger.warning(f"Could not query information_schema for final verification: {e}")
                existing_tables = set(inspector.get_table_names())
            all_tables_exist = required_tables.issubset(existing_tables)
            
            if all_tables_exist:
                logger.info("Database tables created/verified successfully")
                print(f"✓ Database tables verified: {', '.join(sorted(required_tables))}")
                
                # 권한 부여
                try:
                    self._grant_permissions()
                except Exception as perm_error:
                    logger.warning(f"Failed to grant permissions: {perm_error}")
                    print(f"⚠ Failed to grant permissions: {perm_error}")
                
                return True
            else:
                missing = required_tables - existing_tables
                logger.error(f"Missing tables after all attempts: {missing}")
                print(f"✗ Missing tables: {', '.join(missing)}")
                return False
                
        except (OperationalError, ProgrammingError) as e:
            # 중복 테이블/인덱스 오류는 무시 (이미 존재하는 경우)
            error_str = str(e).lower()
            if 'already exists' in error_str or 'duplicate' in error_str:
                logger.info(f"Got 'already exists' error: {e}")
                print("⚠ Got 'already exists' error, verifying tables...")
                # 중복 오류인 경우에도 테이블 존재 여부 확인
                try:
                    from sqlalchemy import inspect
                    inspector = inspect(self.engine)
                    existing_tables = set(inspector.get_table_names())
                    required_tables = {'conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs', 'keyword_voiceprints', 'system_prompts', 'system_prompt_usage'}
                    
                    if required_tables.issubset(existing_tables):
                        print(f"✓ All required tables verified: {', '.join(sorted(required_tables))}")
                        logger.info("All required tables exist despite 'already exists' error")
                        return True
                    else:
                        missing = required_tables - existing_tables
                        logger.warning(f"Some tables missing despite 'already exists' error: {missing}")
                        print(f"⚠ Some tables missing: {', '.join(missing)}")
                        # 누락된 테이블을 SQL로 직접 생성 시도
                        print(f"Attempting to create missing tables via SQL...")
                        self._create_missing_tables(missing)
                        # 재검증
                        existing_tables = set(inspector.get_table_names())
                        missing = required_tables - existing_tables
                        if missing:
                            logger.error(f"Still missing tables after SQL creation: {missing}")
                            print(f"✗ Still missing tables after SQL creation: {', '.join(missing)}")
                            return False
                        else:
                            print(f"✓ All tables created successfully via SQL")
                            logger.info("All tables created successfully via SQL")
                            return True
                except Exception as verify_error:
                    logger.error(f"Error verifying tables: {verify_error}", exc_info=True)
                    print(f"✗ Error verifying tables: {verify_error}")
                    return False
            else:
                logger.error(f"Failed to create tables: {e}", exc_info=True)
                print(f"✗ Failed to create tables: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error during table creation: {e}", exc_info=True)
            print(f"✗ Unexpected error during table creation: {e}")
            raise
    
    def _grant_permissions(self):
        """다른 사용자 계정에 테이블 권한 부여"""
        try:
            required_tables = {'conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs', 'keyword_voiceprints', 'system_prompts', 'system_prompt_usage'}
            
            # 권한을 부여할 추가 사용자 목록 (환경 변수에서 읽거나 기본값 사용)
            additional_users = []
            if hasattr(settings, 'db_additional_users') and settings.db_additional_users:
                additional_users = settings.db_additional_users.split(',')
            elif os.getenv('DB_ADDITIONAL_USERS'):
                additional_users = os.getenv('DB_ADDITIONAL_USERS').split(',')
            
            # 기본적으로 svc_app 계정에 권한 부여
            if 'svc_app' not in additional_users:
                additional_users.append('svc_app')
            
            if not additional_users:
                logger.debug("No additional users to grant permissions")
                return
            
            with self.engine.begin() as conn:
                for user in additional_users:
                    user = user.strip()
                    if not user:
                        continue
                    
                    try:
                        # 먼저 사용자 존재 여부 확인
                        user_check = conn.execute(text("""
                            SELECT EXISTS (
                                SELECT 1 
                                FROM pg_user 
                                WHERE usename = :username
                            )
                        """), {"username": user})
                        user_exists = user_check.scalar()
                        
                        if not user_exists:
                            logger.warning(f"User {user} does not exist in pg_user, skipping permission grant")
                            print(f"⚠ User {user} does not exist, skipping permission grant")
                            continue
                        
                        # 각 테이블에 대해 SELECT, INSERT, UPDATE, DELETE 권한 부여
                        for table in required_tables:
                            try:
                                # 테이블 권한 부여
                                conn.execute(text(f"""
                                    GRANT SELECT, INSERT, UPDATE, DELETE ON public.{table} TO :username
                                """), {"username": user})
                                
                                # 시퀀스 권한 (SERIAL 컬럼용) - 존재하는 경우에만
                                # conversation_sessions는 PRIMARY KEY가 VARCHAR이므로 시퀀스가 없음
                                if table != 'conversation_sessions':
                                    try:
                                        conn.execute(text(f"""
                                            GRANT USAGE, SELECT ON SEQUENCE {table}_id_seq TO :username
                                        """), {"username": user})
                                    except Exception as seq_error:
                                        # 시퀀스가 없거나 권한 부여 실패는 경고만 출력
                                        error_str = str(seq_error).lower()
                                        if 'does not exist' not in error_str:
                                            logger.debug(f"Could not grant sequence permissions for {table}: {seq_error}")
                                
                                logger.debug(f"Granted permissions on {table} to {user}")
                            except Exception as table_error:
                                error_str = str(table_error).lower()
                                logger.warning(f"Failed to grant permissions on {table} to {user}: {table_error}")
                                print(f"⚠ Failed to grant permissions on {table} to {user}: {table_error}")
                        
                        logger.info(f"Successfully granted permissions to user: {user}")
                        print(f"✓ Granted permissions to user: {user}")
                    except Exception as e:
                        error_str = str(e).lower()
                        logger.error(f"Error processing user {user}: {e}", exc_info=True)
                        print(f"⚠ Error processing user {user}: {e}")
        except Exception as e:
            logger.warning(f"Error granting permissions: {e}", exc_info=True)
            print(f"⚠ Error granting permissions: {e}")
    
    def _create_missing_tables(self, missing_tables: set):
        """누락된 테이블을 개별적으로 생성 시도"""
        from sqlalchemy import text
        
        # 각 테이블과 인덱스를 분리하여 생성 (인덱스 생성 실패 시에도 테이블은 생성되도록)
        table_creation_sql = {
            'conversation_sessions': [
                text("""
                    CREATE TABLE IF NOT EXISTS conversation_sessions (
                        session_id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255),
                        system_prompt TEXT,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """),
                text("CREATE INDEX IF NOT EXISTS idx_user_created ON conversation_sessions(user_id, created_at)")
            ],
            'conversation_messages': [
                text("""
                    CREATE TABLE IF NOT EXISTS conversation_messages (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255) NOT NULL,
                        role VARCHAR(50) NOT NULL,
                        content TEXT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """),
                text("CREATE INDEX IF NOT EXISTS idx_session_created ON conversation_messages(session_id, created_at)")
            ],
            'api_request_logs': [
                text("""
                    CREATE TABLE IF NOT EXISTS api_request_logs (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255),
                        endpoint VARCHAR(255) NOT NULL,
                        method VARCHAR(10) NOT NULL,
                        request_data JSONB,
                        response_data JSONB,
                        status_code INTEGER NOT NULL,
                        processing_time_ms FLOAT,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """),
                text("CREATE INDEX IF NOT EXISTS idx_session_created ON api_request_logs(session_id, created_at)"),
                text("CREATE INDEX IF NOT EXISTS idx_endpoint_created ON api_request_logs(endpoint, created_at)")
            ],
            'cost_logs': [
                text("""
                    CREATE TABLE IF NOT EXISTS cost_logs (
                        id SERIAL PRIMARY KEY,
                        session_id VARCHAR(255),
                        service_type VARCHAR(50) NOT NULL,
                        model VARCHAR(100) NOT NULL,
                        input_tokens INTEGER,
                        output_tokens INTEGER,
                        cost_usd FLOAT NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """),
                text("CREATE INDEX IF NOT EXISTS idx_session_created ON cost_logs(session_id, created_at)"),
                text("CREATE INDEX IF NOT EXISTS idx_service_created ON cost_logs(service_type, created_at)")
            ],
            'keyword_voiceprints': [
                text("""
                    CREATE TABLE IF NOT EXISTS keyword_voiceprints (
                        id SERIAL PRIMARY KEY,
                        base_keyword VARCHAR(255) NOT NULL,
                        stt_keyword VARCHAR(255) NOT NULL,
                        audio_data TEXT,
                        session_id VARCHAR(255),
                        user_id VARCHAR(255),
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """),
                text("CREATE INDEX IF NOT EXISTS idx_base_keyword ON keyword_voiceprints(base_keyword)"),
                text("CREATE INDEX IF NOT EXISTS idx_session_id ON keyword_voiceprints(session_id)"),
                text("CREATE INDEX IF NOT EXISTS idx_user_id ON keyword_voiceprints(user_id)"),
                text("CREATE INDEX IF NOT EXISTS idx_base_stt_keyword ON keyword_voiceprints(base_keyword, stt_keyword)")
            ],
            'system_prompts': [
                text("""
                    CREATE TABLE IF NOT EXISTS system_prompts (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        content TEXT NOT NULL,
                        description TEXT,
                        is_default BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """),
                text("CREATE INDEX IF NOT EXISTS idx_system_prompts_name ON system_prompts(name)"),
                text("CREATE INDEX IF NOT EXISTS idx_system_prompts_created ON system_prompts(created_at)"),
                text("CREATE INDEX IF NOT EXISTS idx_system_prompts_default ON system_prompts(is_default)")
            ],
            'system_prompt_usage': [
                text("""
                    CREATE TABLE IF NOT EXISTS system_prompt_usage (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255),
                        session_id VARCHAR(255),
                        system_prompt_id INTEGER NOT NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                """),
                text("CREATE INDEX IF NOT EXISTS idx_user_id ON system_prompt_usage(user_id)"),
                text("CREATE INDEX IF NOT EXISTS idx_session_id ON system_prompt_usage(session_id)"),
                text("CREATE INDEX IF NOT EXISTS idx_system_prompt_id ON system_prompt_usage(system_prompt_id)"),
                text("CREATE INDEX IF NOT EXISTS idx_user_session ON system_prompt_usage(user_id, session_id)"),
                text("CREATE INDEX IF NOT EXISTS idx_prompt_usage_created ON system_prompt_usage(created_at)")
            ]
        }
        
        for table_name in missing_tables:
            if table_name in table_creation_sql:
                logger.info(f"Attempting to create table: {table_name}")
                print(f"Creating table: {table_name}...")
                
                sql_statements = table_creation_sql[table_name]
                table_created = False
                
                for sql_stmt in sql_statements:
                    try:
                        # engine.begin()은 자동으로 커밋하지만, 명시적으로 처리
                        with self.engine.begin() as conn:
                            conn.execute(sql_stmt)
                        if sql_stmt == sql_statements[0]:  # 첫 번째는 테이블 생성
                            table_created = True
                            logger.info(f"Successfully created table: {table_name}")
                            print(f"✓ Created table: {table_name}")
                    except Exception as e:
                        error_str = str(e).lower()
                        if 'already exists' in error_str or 'duplicate' in error_str:
                            if sql_stmt == sql_statements[0]:  # 테이블 생성
                                logger.info(f"Table {table_name} already exists")
                                print(f"✓ Table {table_name} already exists")
                                table_created = True
                            else:  # 인덱스 생성
                                logger.debug(f"Index already exists for {table_name}")
                        else:
                            # 테이블 생성 실패는 에러, 인덱스 생성 실패는 경고
                            if sql_stmt == sql_statements[0]:
                                logger.error(f"Failed to create table {table_name}: {e}", exc_info=True)
                                print(f"✗ Failed to create table {table_name}: {e}")
                            else:
                                logger.warning(f"Failed to create index for {table_name}: {e}")
                                print(f"⚠ Failed to create index for {table_name}: {e}")
                
                # 테이블 생성 후 즉시 확인 (재시도 로직 포함)
                if table_created:
                    import time
                    verified = False
                    for verify_retry in range(3):
                        try:
                            time.sleep(0.1 * (verify_retry + 1))  # 재시도마다 대기 시간 증가
                            with self.engine.connect() as conn:
                                # PostgreSQL에서 테이블 존재 여부 확인 (다양한 방법 시도)
                                result = conn.execute(text(f"""
                                    SELECT EXISTS (
                                        SELECT 1 
                                        FROM information_schema.tables 
                                        WHERE table_schema = 'public' 
                                            AND table_name = '{table_name}'
                                    )
                                """))
                                exists = result.scalar()
                                if exists:
                                    verified = True
                                    logger.debug(f"Table {table_name} confirmed to exist after creation (retry {verify_retry + 1})")
                                    break
                        except Exception as verify_e:
                            logger.debug(f"Could not verify table {table_name} (retry {verify_retry + 1}): {verify_e}")
                    
                    if not verified:
                        logger.warning(f"Table {table_name} created but not found in verification after 3 retries")
                        print(f"⚠ Table {table_name} created but not found in verification (may be a timing issue)")
                
                if not table_created:
                    logger.error(f"Table {table_name} was not created")
                    print(f"✗ Table {table_name} was not created")
    
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
        """데이터베이스 연결 상태 및 테이블 존재 여부 확인"""
        try:
            if not self.engine:
                logger.debug("Health check failed: engine not initialized")
                return False
            
            # 연결 테스트
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # 필수 테이블 존재 여부 확인
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())
            required_tables = {'conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs', 'keyword_voiceprints', 'system_prompts', 'system_prompt_usage'}
            
            if not required_tables.issubset(existing_tables):
                missing = required_tables - existing_tables
                logger.warning(f"Health check: Missing tables: {missing}")
                return False
            
            logger.debug("Database health check passed")
            return True
        except Exception as e:
            logger.warning(f"Database health check failed: {e}")
            return False
    
    def verify_tables(self) -> dict:
        """테이블 존재 여부를 상세히 확인"""
        if not self.engine:
            return {
                'initialized': False,
                'tables': {},
                'schema': None
            }
        
        try:
            required_tables = {'conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs', 'keyword_voiceprints', 'system_prompts', 'system_prompt_usage'}
            
            # 현재 스키마 및 데이터베이스 정보 확인
            current_schema = None
            current_database = None
            try:
                with self.engine.connect() as conn:
                    current_schema = conn.execute(text("SELECT current_schema()")).scalar()
                    current_database = conn.execute(text("SELECT current_database()")).scalar()
                    logger.debug(f"Current schema: {current_schema}, database: {current_database}")
            except Exception as e:
                logger.warning(f"Could not get schema/database info: {e}")
                current_schema = "public"
            
            # public 스키마의 테이블만 확인
            try:
                with self.engine.connect() as conn:
                    result_query = conn.execute(text("""
                        SELECT table_schema, table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                            AND table_type = 'BASE TABLE'
                            AND table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
                    """))
                    existing_tables = {}
                    for row in result_query:
                        existing_tables[row[1]] = row[0]  # table_name -> table_schema
            except Exception as e:
                logger.warning(f"Could not query information_schema in verify_tables: {e}")
                from sqlalchemy import inspect
                inspector = inspect(self.engine)
                existing_tables = {table: current_schema or "public" for table in inspector.get_table_names()}
            
            result = {
                'initialized': True,
                'schema': current_schema or "public",
                'database': current_database,
                'tables': {}
            }
            
            for table in required_tables:
                result['tables'][table] = {
                    'exists': table in existing_tables,
                    'schema': existing_tables.get(table, None) if table in existing_tables else None,
                    'row_count': None
                }
                
                if table in existing_tables:
                    try:
                        with self.engine.connect() as conn:
                            # 스키마 명시하여 쿼리
                            schema_name = existing_tables[table]
                            row_count = conn.execute(text(f'SELECT COUNT(*) FROM "{schema_name}"."{table}"')).scalar()
                            result['tables'][table]['row_count'] = row_count
                    except Exception as e:
                        logger.warning(f"Could not get row count for {table}: {e}")
            
            result['all_tables_exist'] = required_tables.issubset(existing_tables)
            return result
        except Exception as e:
            logger.error(f"Error verifying tables: {e}", exc_info=True)
            return {
                'initialized': True,
                'error': str(e),
                'tables': {},
                'schema': None
            }


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
            saved_count = 0
            for msg in messages:
                # content가 None인 경우 처리
                content = msg.get("content")
                if content is None:
                    # tool_calls가 있으면 그것을 문자열로 변환
                    if "tool_calls" in msg and msg["tool_calls"]:
                        content = json.dumps(msg["tool_calls"], ensure_ascii=False)
                    else:
                        # content가 None이고 tool_calls도 없으면 빈 문자열로 저장
                        content = ""
                    logger.debug(f"Message with None content converted: role={msg.get('role')}, has_tool_calls={bool(msg.get('tool_calls'))}")
                
                # content는 항상 문자열로 보장 (None이면 빈 문자열)
                db_message = ConversationMessage(
                    session_id=session_id,
                    role=msg["role"],
                    content=content or ""  # None이면 빈 문자열로 저장
                )
                session.add(db_message)
                saved_count += 1
            logger.debug(f"Saved {saved_count} messages for session: {session_id}")
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


