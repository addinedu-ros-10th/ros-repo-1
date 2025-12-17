"""
데이터베이스 연결 모듈

SQLAlchemy를 사용한 PostgreSQL 데이터베이스 연결 및 세션 관리를 담당합니다.
"""

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Generator, AsyncGenerator
import logging

from app.core.config import get_settings

# 로거 설정
logger = logging.getLogger(__name__)

# 설정 가져오기
settings = get_settings()

# 데이터베이스 URL
DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy 엔진 생성 (지연 초기화)
engine = None

# 비동기 엔진 생성 (지연 초기화)
async_engine = None

# 세션 팩토리 (엔진 생성 후 초기화)
SessionLocal = None

# 베이스 클래스 생성 (모델 상속용)
Base = declarative_base()

# 메타데이터 (마이그레이션용)
metadata = MetaData()


def _create_engine_with_fallback():
    """
    데이터베이스 엔진을 생성합니다.
    env 파일의 HOST로 먼저 시도하고, 실패하면 host.docker.internal로 재시도합니다.
    """
    global engine, SessionLocal
    
    if engine is not None:
        return engine
    
    try:
        # 1단계: env 파일의 DB_HOST로 먼저 시도
        logger.info(f"🔌 데이터베이스 연결 시도: {settings.DB_HOST}:{settings.DB_PORT}")
        engine = create_engine(
            DATABASE_URL,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
        )
        # 연결 테스트
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info(f"✅ 데이터베이스 연결 성공: {settings.DB_HOST}:{settings.DB_PORT}")
        
        # SessionLocal 생성
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        return engine
        
    except Exception as e:
        # env 파일의 HOST로 연결 실패
        error_str = str(e).lower()
        is_connection_error = any(keyword in error_str for keyword in 
            ['connection', 'connect', 'network', 'route', 'refused', 'timeout', 'no route'])
        
        if is_connection_error:
            logger.error("=" * 80)
            logger.error("❌ 데이터베이스 연결 실패")
            logger.error(f"   env 파일(.env.local)의 DB_HOST 값: {settings.DB_HOST}")
            logger.error(f"   env 파일(.env.local)의 DB_PORT 값: {settings.DB_PORT}")
            logger.error("")
            logger.error("💡 env 파일의 HOST로 DB 연결이 불가능합니다.")
            logger.error("   .env.local 파일을 확인하고 DB_HOST 값을 수정해주세요.")
            logger.error("")
            logger.error(f"   상세 오류: {e}")
            logger.error("=" * 80)
            
            # 2단계: host.docker.internal로 재시도
            logger.info("")
            logger.info("=" * 80)
            logger.info("🔄 일단은 host.docker.internal에 접근을 시도합니다...")
            logger.info("=" * 80)
            
            # host.docker.internal을 사용한 URL 생성
            from urllib.parse import quote_plus
            encoded_password = quote_plus(settings.DB_PASSWORD)
            fallback_url = f"postgresql://{settings.DB_USER}:{encoded_password}@host.docker.internal:{settings.DB_PORT}/{settings.DB_NAME}"
            
            try:
                engine = create_engine(
                    fallback_url,
                    poolclass=QueuePool,
                    pool_size=5,
                    max_overflow=10,
                    pool_pre_ping=True,
                    pool_recycle=3600,
                    echo=settings.DEBUG,
                )
                # 연결 테스트
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logger.info("✅ host.docker.internal로 데이터베이스 연결 성공!")
                logger.info("=" * 80)
                
                # SessionLocal 생성
                SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=engine
                )
                return engine
                
            except Exception as fallback_error:
                logger.error("=" * 80)
                logger.error("❌ host.docker.internal로도 데이터베이스 연결 실패")
                logger.error("")
                logger.error("💡 해결 방법:")
                logger.error("   1. .env.local 파일의 DB_HOST 값을 확인하세요.")
                logger.error("   2. PostgreSQL 서버가 실행 중인지 확인하세요.")
                logger.error("   3. 방화벽 설정을 확인하세요.")
                logger.error("   4. docker-compose.yml에 extra_hosts 설정이 있는지 확인하세요.")
                logger.error("")
                logger.error(f"   원본 오류 (env HOST): {e}")
                logger.error(f"   Fallback 오류 (host.docker.internal): {fallback_error}")
                logger.error("=" * 80)
                raise fallback_error
        else:
            # 연결 오류가 아닌 다른 오류
            logger.error(f"데이터베이스 엔진 생성 오류: {e}")
            raise


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션을 생성하는 의존성 함수
    
    FastAPI의 Depends에서 사용됩니다.
    """
    global SessionLocal
    
    # 엔진이 없으면 생성 (fallback 포함)
    _create_engine_with_fallback()
    
    db = SessionLocal()
    try:
        logger.debug("데이터베이스 세션 생성")
        yield db
    except Exception as e:
        logger.error(f"데이터베이스 세션 오류: {e}")
        db.rollback()
        raise
    finally:
        logger.debug("데이터베이스 세션 종료")
        db.close()


async def get_session() -> AsyncSession:
    """
    비동기 데이터베이스 세션을 생성하는 함수
    
    PostgreSQL 리포지토리에서 사용됩니다.
    """
    global async_engine
    
    if async_engine is None:
        # 동기 URL을 비동기 URL로 변환
        async_database_url = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
        
        async_engine = create_async_engine(
            async_database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=settings.DEBUG,
        )
    
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    return async_session()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션을 생성하는 의존성 함수
    
    FastAPI의 Depends에서 사용됩니다.
    """
    global async_engine
    
    if async_engine is None:
        # 1단계: env 파일의 DB_HOST로 먼저 시도
        async_database_url = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
        
        try:
            async_engine = create_async_engine(
                async_database_url,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=settings.DEBUG,
            )
            # 연결 테스트 (pool_pre_ping이 있지만 명시적으로 테스트)
            async with async_engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info(f"✅ 데이터베이스 연결 성공: {settings.DB_HOST}:{settings.DB_PORT}")
        except Exception as e:
            # env 파일의 HOST로 연결 실패
            error_str = str(e).lower()
            is_connection_error = any(keyword in error_str for keyword in 
                ['connection', 'connect', 'network', 'route', 'refused', 'timeout', 'no route'])
            
            if is_connection_error:
                logger.error("=" * 80)
                logger.error("❌ 데이터베이스 연결 실패")
                logger.error(f"   env 파일(.env.local)의 DB_HOST 값: {settings.DB_HOST}")
                logger.error(f"   env 파일(.env.local)의 DB_PORT 값: {settings.DB_PORT}")
                logger.error("")
                logger.error("💡 env 파일의 HOST로 DB 연결이 불가능합니다.")
                logger.error("   .env.local 파일을 확인하고 DB_HOST 값을 수정해주세요.")
                logger.error("")
                logger.error(f"   상세 오류: {e}")
                logger.error("=" * 80)
                
                # 2단계: host.docker.internal로 재시도
                logger.info("")
                logger.info("=" * 80)
                logger.info("🔄 일단은 host.docker.internal에 접근을 시도합니다...")
                logger.info("=" * 80)
                
                # host.docker.internal을 사용한 URL 생성
                from urllib.parse import quote_plus
                encoded_password = quote_plus(settings.DB_PASSWORD)
                fallback_url = f"postgresql+asyncpg://{settings.DB_USER}:{encoded_password}@host.docker.internal:{settings.DB_PORT}/{settings.DB_NAME}"
                
                try:
                    # 기존 엔진이 있으면 닫기
                    if async_engine is not None:
                        await async_engine.dispose()
                    
                    async_engine = create_async_engine(
                        fallback_url,
                        poolclass=QueuePool,
                        pool_size=5,
                        max_overflow=10,
                        pool_pre_ping=True,
                        pool_recycle=3600,
                        echo=settings.DEBUG,
                    )
                    # 연결 테스트
                    async with async_engine.connect() as conn:
                        await conn.execute(text("SELECT 1"))
                    logger.info("✅ host.docker.internal로 데이터베이스 연결 성공!")
                    logger.info("=" * 80)
                except Exception as fallback_error:
                    logger.error("=" * 80)
                    logger.error("❌ host.docker.internal로도 데이터베이스 연결 실패")
                    logger.error("")
                    logger.error("💡 해결 방법:")
                    logger.error("   1. .env.local 파일의 DB_HOST 값을 확인하세요.")
                    logger.error("   2. PostgreSQL 서버가 실행 중인지 확인하세요.")
                    logger.error("   3. 방화벽 설정을 확인하세요.")
                    logger.error("   4. docker-compose.yml에 extra_hosts 설정이 있는지 확인하세요.")
                    logger.error("")
                    logger.error(f"   원본 오류 (env HOST): {e}")
                    logger.error(f"   Fallback 오류 (host.docker.internal): {fallback_error}")
                    logger.error("=" * 80)
                    raise fallback_error
            else:
                # 연결 오류가 아닌 다른 오류
                logger.error(f"데이터베이스 엔진 생성 오류: {e}")
                raise
    
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            logger.debug("비동기 데이터베이스 세션 생성")
            yield session
        except Exception as e:
            # 연결 관련 오류인지 확인
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ['connection', 'connect', 'network', 'route', 'refused', 'timeout']):
                logger.error("=" * 80)
                logger.error("❌ 데이터베이스 연결 오류 발생")
                logger.error(f"   env 파일(.env.local)의 DB_HOST 값: {settings.DB_HOST}")
                logger.error(f"   env 파일(.env.local)의 DB_PORT 값: {settings.DB_PORT}")
                logger.error("")
                logger.error("💡 env 파일의 HOST로 DB 연결이 불가능합니다.")
                logger.error("   .env.local 파일을 확인하고 DB_HOST 값을 수정해주세요.")
                logger.error("")
                logger.error(f"   상세 오류: {e}")
                logger.error("=" * 80)
            else:
                logger.error(f"비동기 데이터베이스 세션 오류: {e}")
            await session.rollback()
            raise
        finally:
            logger.debug("비동기 데이터베이스 세션 종료")




def create_tables():
    """데이터베이스 테이블을 생성합니다."""
    global engine
    
    # 엔진이 없으면 생성 (fallback 포함)
    _create_engine_with_fallback()
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logger.error(f"테이블 생성 오류: {e}")
        raise


def drop_tables():
    """데이터베이스 테이블을 삭제합니다. (주의: 개발 환경에서만 사용)"""
    if settings.ENVIRONMENT == "production":
        logger.warning("프로덕션 환경에서는 테이블 삭제가 금지됩니다.")
        return
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("데이터베이스 테이블 삭제 완료")
    except Exception as e:
        logger.error(f"테이블 삭제 오류: {e}")
        raise


def test_connection() -> bool:
    """데이터베이스 연결을 테스트합니다."""
    global engine
    
    # 엔진이 없으면 생성 (fallback 포함)
    try:
        _create_engine_with_fallback()
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            logger.info("데이터베이스 연결 테스트 성공")
            return True
    except Exception as e:
        # _create_engine_with_fallback에서 이미 로그를 출력하므로 여기서는 간단히 처리
        logger.error(f"데이터베이스 연결 테스트 실패: {e}")
        return False


def get_table_names() -> list:
    """데이터베이스의 모든 테이블 이름을 반환합니다."""
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            table_names = [row[0] for row in result]
            logger.info(f"테이블 목록 조회 성공: {len(table_names)}개 테이블")
            return table_names
    except Exception as e:
        logger.error(f"테이블 목록 조회 실패: {e}")
        return []


def get_table_schema(table_name: str) -> dict:
    """특정 테이블의 스키마 정보를 반환합니다."""
    try:
        with engine.connect() as connection:
            # 컬럼 정보 조회
            from sqlalchemy import text
            columns_result = connection.execute(text(f"""
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
                ORDER BY ordinal_position
            """))
            
            columns = []
            for row in columns_result:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3]
                })
            
            # 제약조건 정보 조회
            from sqlalchemy import text
            constraints_result = connection.execute(text(f"""
                SELECT 
                    constraint_name,
                    constraint_type
                FROM information_schema.table_constraints 
                WHERE table_name = '{table_name}' 
                AND table_schema = 'public'
            """))
            
            constraints = []
            for row in constraints_result:
                constraints.append({
                    'name': row[0],
                    'type': row[1]
                })
            
            schema_info = {
                'table_name': table_name,
                'columns': columns,
                'constraints': constraints
            }
            
            logger.info(f"테이블 '{table_name}' 스키마 조회 성공")
            return schema_info
            
    except Exception as e:
        logger.error(f"테이블 '{table_name}' 스키마 조회 실패: {e}")
        return {}


# 데이터베이스 초기화 함수
def init_database():
    """데이터베이스를 초기화합니다."""
    try:
        # 연결 테스트
        if not test_connection():
            raise Exception("데이터베이스 연결 실패")
        
        # 기존 테이블 정보 로깅
        existing_tables = get_table_names()
        if existing_tables:
            logger.info(f"기존 테이블 발견: {existing_tables}")
            
            # 각 테이블의 스키마 정보 로깅
            for table_name in existing_tables:
                schema_info = get_table_schema(table_name)
                if schema_info:
                    logger.info(f"테이블 '{table_name}' 스키마: {schema_info}")
        
        logger.info("데이터베이스 초기화 완료")
        
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise

