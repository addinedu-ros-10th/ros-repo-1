#!/usr/bin/env python3
"""
안전한 데이터베이스 초기화 스크립트

기존 PostgreSQL 데이터베이스의 테이블을 보존하면서 Alembic을 안전하게 초기화합니다.
"""

import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.infrastructure.database import init_database, get_table_names, get_table_schema
from app.infrastructure.redis_client import init_redis
from app.core.config import get_settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/safe_db_init.log')
    ]
)

logger = logging.getLogger(__name__)


def analyze_existing_schema():
    """기존 데이터베이스 스키마를 분석합니다."""
    logger.info("=== 기존 데이터베이스 스키마 분석 시작 ===")
    
    try:
        # 데이터베이스 초기화
        init_database()
        
        # 기존 테이블 목록 조회
        existing_tables = get_table_names()
        
        if not existing_tables:
            logger.warning("기존 테이블이 발견되지 않았습니다.")
            return []
        
        logger.info(f"기존 테이블 {len(existing_tables)}개 발견: {existing_tables}")
        
        # 각 테이블의 상세 스키마 분석
        schema_analysis = {}
        for table_name in existing_tables:
            logger.info(f"테이블 '{table_name}' 스키마 분석 중...")
            schema_info = get_table_schema(table_name)
            
            if schema_info:
                schema_analysis[table_name] = schema_info
                logger.info(f"테이블 '{table_name}' 스키마 분석 완료")
                
                # 컬럼 정보 로깅
                columns = schema_info.get('columns', [])
                logger.info(f"  - 컬럼 수: {len(columns)}")
                for col in columns[:5]:  # 처음 5개 컬럼만 로깅
                    logger.info(f"    * {col['name']}: {col['type']} ({'NULL' if col['nullable'] else 'NOT NULL'})")
                
                if len(columns) > 5:
                    logger.info(f"    ... 및 {len(columns) - 5}개 컬럼 더")
                
                # 제약조건 정보 로깅
                constraints = schema_info.get('constraints', [])
                if constraints:
                    logger.info(f"  - 제약조건: {[c['type'] for c in constraints]}")
            else:
                logger.warning(f"테이블 '{table_name}' 스키마 분석 실패")
        
        logger.info("=== 기존 데이터베이스 스키마 분석 완료 ===")
        return schema_analysis
        
    except Exception as e:
        logger.error(f"스키마 분석 중 오류 발생: {e}")
        raise


def check_alembic_status():
    """Alembic 상태를 확인합니다."""
    logger.info("=== Alembic 상태 확인 ===")
    
    try:
        # alembic current 명령어 실행
        import subprocess
        result = subprocess.run(
            ['alembic', 'current'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            current_revision = result.stdout.strip()
            if current_revision:
                logger.info(f"현재 Alembic 리비전: {current_revision}")
            else:
                logger.info("Alembic이 아직 초기화되지 않았습니다.")
        else:
            logger.warning(f"Alembic 상태 확인 실패: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Alembic 상태 확인 중 오류 발생: {e}")


def safe_alembic_init():
    """Alembic을 안전하게 초기화합니다."""
    logger.info("=== 안전한 Alembic 초기화 시작 ===")
    
    try:
        import subprocess
        
        # 1단계: 현재 DB 상태를 head로 stamp (기존 테이블 보존)
        logger.info("1단계: 기존 테이블을 보존하면서 Alembic 초기화...")
        
        result = subprocess.run(
            ['alembic', 'stamp', 'head'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            logger.info("✅ alembic stamp head 성공 - 기존 테이블이 보존되었습니다.")
        else:
            logger.error(f"❌ alembic stamp head 실패: {result.stderr}")
            raise Exception("Alembic 초기화 실패")
        
        # 2단계: 현재 상태 확인
        logger.info("2단계: Alembic 상태 확인...")
        check_alembic_status()
        
        # 3단계: 기존 스키마 기반 마이그레이션 파일 생성 (선택사항)
        logger.info("3단계: 기존 스키마 기반 마이그레이션 파일 생성...")
        
        result = subprocess.run(
            ['alembic', 'revision', '--autogenerate', '-m', 'Initial migration from existing schema'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        if result.returncode == 0:
            logger.info("✅ 자동 마이그레이션 파일 생성 성공")
            
            # 생성된 마이그레이션 파일 경로 찾기
            versions_dir = project_root / 'alembic' / 'versions'
            if versions_dir.exists():
                migration_files = list(versions_dir.glob('*.py'))
                if migration_files:
                    latest_migration = max(migration_files, key=lambda x: x.stat().st_mtime)
                    logger.info(f"생성된 마이그레이션 파일: {latest_migration.name}")
                    
                    # 마이그레이션 파일 내용 확인 및 안전성 검토
                    review_migration_file(latest_migration)
        else:
            logger.warning(f"⚠️ 자동 마이그레이션 파일 생성 실패: {result.stderr}")
            logger.info("수동으로 마이그레이션 파일을 생성해야 할 수 있습니다.")
        
        logger.info("=== 안전한 Alembic 초기화 완료 ===")
        
    except Exception as e:
        logger.error(f"Alembic 초기화 중 오류 발생: {e}")
        raise


def review_migration_file(migration_file_path):
    """생성된 마이그레이션 파일을 검토하여 안전성을 확인합니다."""
    logger.info(f"=== 마이그레이션 파일 안전성 검토: {migration_file_path.name} ===")
    
    try:
        with open(migration_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 위험한 작업이 포함되어 있는지 확인
        dangerous_operations = [
            'drop_table',
            'drop_column',
            'drop_index',
            'drop_constraint'
        ]
        
        found_dangerous = []
        for operation in dangerous_operations:
            if operation in content:
                found_dangerous.append(operation)
        
        if found_dangerous:
            logger.warning(f"⚠️ 위험한 작업이 발견되었습니다: {found_dangerous}")
            logger.warning("이 마이그레이션 파일을 수정하여 위험한 작업을 제거해야 합니다.")
            
            # 안전한 마이그레이션 파일로 수정
            safe_content = make_migration_safe(content)
            
            with open(migration_file_path, 'w', encoding='utf-8') as f:
                f.write(safe_content)
            
            logger.info("✅ 마이그레이션 파일을 안전하게 수정했습니다.")
        else:
            logger.info("✅ 마이그레이션 파일에 위험한 작업이 없습니다.")
            
    except Exception as e:
        logger.error(f"마이그레이션 파일 검토 중 오류 발생: {e}")


def make_migration_safe(content):
    """마이그레이션 파일을 안전하게 수정합니다."""
    logger.info("마이그레이션 파일을 안전하게 수정 중...")
    
    # 위험한 작업을 주석 처리
    safe_content = content
    
    # drop_table 주석 처리
    safe_content = safe_content.replace('drop_table', '# drop_table (SAFETY: 주석 처리됨)')
    
    # drop_column 주석 처리
    safe_content = safe_content.replace('drop_column', '# drop_column (SAFETY: 주석 처리됨)')
    
    # drop_index 주석 처리
    safe_content = safe_content.replace('drop_index', '# drop_index (SAFETY: 주석 처리됨)')
    
    # drop_constraint 주석 처리
    safe_content = safe_content.replace('drop_constraint', '# drop_constraint (SAFETY: 주석 처리됨)')
    
    # 안전성 주석 추가
    safety_comment = '''
# ========================================
# 안전성 주의사항:
# 이 마이그레이션 파일은 기존 테이블을 보존하기 위해
# 위험한 작업(drop_table, drop_column 등)이 주석 처리되었습니다.
# 필요시 수동으로 검토하고 안전한 작업만 활성화하세요.
# ========================================
'''
    
    # 파일 상단에 안전성 주석 추가
    if '"""' in safe_content:
        # 첫 번째 docstring 다음에 주석 추가
        parts = safe_content.split('"""', 2)
        if len(parts) >= 3:
            safe_content = parts[0] + '"""' + parts[1] + '"""' + safety_comment + parts[2]
    
    return safe_content


def test_connections():
    """데이터베이스 및 Redis 연결을 테스트합니다."""
    logger.info("=== 연결 테스트 시작 ===")
    
    try:
        # PostgreSQL 연결 테스트
        logger.info("PostgreSQL 연결 테스트 중...")
        init_database()
        logger.info("✅ PostgreSQL 연결 성공")
        
        # Redis 연결 테스트
        logger.info("Redis 연결 테스트 중...")
        init_redis()
        logger.info("✅ Redis 연결 성공")
        
        logger.info("=== 연결 테스트 완료 ===")
        
    except Exception as e:
        logger.error(f"연결 테스트 중 오류 발생: {e}")
        raise


def main():
    """메인 함수"""
    logger.info("🚀 안전한 데이터베이스 초기화 시작")
    
    try:
        # 1. 연결 테스트
        test_connections()
        
        # 2. 기존 스키마 분석
        schema_analysis = analyze_existing_schema()
        
        # 3. Alembic 안전 초기화
        safe_alembic_init()
        
        # 4. 최종 상태 확인
        logger.info("=== 최종 상태 확인 ===")
        check_alembic_status()
        
        logger.info("🎉 안전한 데이터베이스 초기화가 완료되었습니다!")
        logger.info("이제 새로운 마이그레이션을 안전하게 생성할 수 있습니다.")
        
    except Exception as e:
        logger.error(f"❌ 초기화 중 오류 발생: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

