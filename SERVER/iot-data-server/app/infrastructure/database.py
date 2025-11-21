"""
데이터베이스 연결 모듈

SQLAlchemy를 사용한 PostgreSQL 데이터베이스 연결 및 세션 관리를 담당합니다.
"""

from sqlalchemy import create_engine, MetaData
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

# SQLAlchemy 엔진 생성
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,  # 개발 환경에서만 SQL 로그 출력
)

# 비동기 엔진 생성
async_engine = None

# 세션 팩토리 생성
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 베이스 클래스 생성 (모델 상속용)
Base = declarative_base()

# 메타데이터 (마이그레이션용)
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션을 생성하는 의존성 함수
    
    FastAPI의 Depends에서 사용됩니다.
    """
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
    
    async with async_session() as session:
        try:
            logger.debug("비동기 데이터베이스 세션 생성")
            yield session
        except Exception as e:
            logger.error(f"비동기 데이터베이스 세션 오류: {e}")
            await session.rollback()
            raise
        finally:
            logger.debug("비동기 데이터베이스 세션 종료")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    비동기 데이터베이스 세션을 생성하는 의존성 함수
    
    FastAPI의 Depends에서 사용됩니다.
    """
    async_session = await get_session()
    try:
        logger.debug("비동기 데이터베이스 세션 생성")
        yield async_session
    except Exception as e:
        logger.error(f"비동기 데이터베이스 세션 오류: {e}")
        await async_session.rollback()
        raise
    finally:
        logger.debug("비동기 데이터베이스 세션 종료")
        await async_session.close()


def create_tables():
    """데이터베이스 테이블을 생성합니다."""
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
    try:
        with engine.connect() as connection:
            from sqlalchemy import text
            result = connection.execute(text("SELECT 1"))
            logger.info("데이터베이스 연결 테스트 성공")
            return True
    except Exception as e:
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

