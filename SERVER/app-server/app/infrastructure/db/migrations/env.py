import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from urllib.parse import quote_plus

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# 환경 변수 로딩
from dotenv import load_dotenv
load_dotenv()

# 모델 임포트 (신규 스키마만)
from app.infrastructure.db.models import Base

# Alembic 설정 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 신규 스키마 메타데이터만 사용 (비삭제 정책)
target_metadata = Base.metadata


def get_database_url():
    """데이터베이스 URL을 올바르게 구성"""
    db_url = os.getenv('DB_APP_URL')
    if not db_url:
        raise ValueError("DB_APP_URL 환경 변수가 설정되지 않았습니다.")
    
    # asyncpg를 psycopg2로 변경 (Alembic 호환성)
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    # URL 파싱하여 비밀번호 인코딩
    if '://' in db_url:
        scheme, rest = db_url.split('://', 1)
        if '@' in rest:
            user_pass, host_db = rest.split('@', 1)
            if ':' in user_pass:
                user, password = user_pass.split(':', 1)
                # 비밀번호 URL 인코딩
                password = quote_plus(password)
                user_pass = f"{user}:{password}"
            rest = f"{user_pass}@{host_db}"
        db_url = f"{scheme}://{rest}"
    
    return db_url


def run_migrations_offline() -> None:
    """오프라인 모드로 마이그레이션 실행"""
    context.configure(
        url="postgresql://svc_dev:IOT_dev_123%21%40%23@0.0.0.0:15432/iot_care",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # 비삭제 정책을 위한 설정
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """온라인 모드로 마이그레이션 실행"""
    # 직접 연결 파라미터 사용
    connectable = engine_from_config(
        {
            "sqlalchemy.url": "postgresql://svc_dev:IOT_dev_123%21%40%23@0.0.0.0:15432/iot_care",
            "sqlalchemy.poolclass": "NullPool"
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # 비삭제 정책을 위한 설정
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    비삭제 정책을 위한 객체 필터링
    관리 대상 테이블만 포함하여 기존 테이블 보호
    """
    # 테이블인 경우
    if type_ == "table":
        # 관리 대상 테이블 목록 (화이트리스트)
        # 이 목록에 있는 테이블만 Alembic이 관리
        managed_tables = {
            "scheduled_jobs",  # 기존 관리 테이블
            "detection_event",  # 신규: 로봇 인식 이벤트
            "marker_registry",  # 신규: ArUco 마커 레지스트리
            "text_registry",    # 신규: OCR 텍스트 레지스트리
            "face_registry",    # 신규: 얼굴 레지스트리
            "person_registry",  # 신규: 전신/개인 프로필 레지스트리
        }
        
        # 관리 대상 테이블만 포함
        if name in managed_tables:
            return True
        
        # 시스템 테이블 (alembic_version)은 항상 포함
        if name == "alembic_version":
            return True
        
        # 기타 테이블은 제외 (기존 테이블 보호)
        # 이렇게 하면 autogenerate 시에도 기존 테이블이 변경되지 않음
        return False
    
    # 인덱스인 경우
    if type_ == "index":
        # 관리 대상 테이블의 인덱스만 포함
        # 인덱스 이름에서 테이블 이름 추출 (일반적인 패턴)
        for table_name in ["scheduled_jobs", "detection_event", "marker_registry", 
                          "text_registry", "face_registry", "person_registry"]:
            if name.startswith(f"ix_{table_name}") or name.startswith(f"idx_{table_name}"):
                return True
        # 레거시 테이블의 인덱스 제외
        if name.startswith("ix_legacy_"):
            return False
        # 기타 인덱스는 제외 (안전을 위해)
        return False
    
    # 기타 객체 (제약조건, 시퀀스 등)는 포함
    return True


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
