#!/usr/bin/env python3
"""
PostgreSQL 연결 직접 테스트 스크립트
"""

import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_direct_connection():
    """환경 변수를 직접 읽어서 PostgreSQL 연결을 테스트합니다."""
    logger.info("=== 직접 연결 테스트 시작 ===")
    
    try:
        # 환경 변수 직접 읽기
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        db_host = os.getenv('DB_HOST')
        db_port = os.getenv('DB_PORT')
        db_name = os.getenv('DB_NAME')
        
        logger.info(f"DB_USER: {db_user}")
        logger.info(f"DB_PASSWORD: {db_password}")
        logger.info(f"DB_HOST: {db_host}")
        logger.info(f"DB_PORT: {db_port}")
        logger.info(f"DB_NAME: {db_name}")
        
        # 데이터베이스 URL 구성 (URL 인코딩 적용)
        from urllib.parse import quote_plus
        
        encoded_password = quote_plus(db_password)
        database_url = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"
        logger.info(f"원본 비밀번호: {db_password}")
        logger.info(f"인코딩된 비밀번호: {encoded_password}")
        logger.info(f"구성된 DATABASE_URL: {database_url}")
        
        # SQLAlchemy로 연결 테스트
        from sqlalchemy import create_engine
        
        try:
            engine = create_engine(database_url)
            with engine.connect() as connection:
                from sqlalchemy import text
                result = connection.execute(text("SELECT 1"))
                logger.info("✅ PostgreSQL 직접 연결 성공")
                return True
        except Exception as e:
            logger.error(f"SQLAlchemy 연결 오류: {e}")
            return False
            
    except Exception as e:
        logger.error(f"❌ PostgreSQL 직접 연결 실패: {e}")
        return False


def test_redis_connection():
    """Redis 연결을 테스트합니다."""
    logger.info("=== Redis 연결 테스트 시작 ===")
    
    try:
        from app.infrastructure.redis_client import test_redis_connection
        
        if test_redis_connection():
            logger.info("✅ Redis 연결 성공")
            return True
        else:
            logger.error("❌ Redis 연결 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ Redis 연결 테스트 중 오류: {e}")
        return False


def main():
    """메인 함수"""
    logger.info("🚀 직접 연결 테스트 시작")
    
    results = []
    
    # 1. PostgreSQL 직접 연결 테스트
    results.append(("PostgreSQL 직접 연결", test_direct_connection()))
    
    # 2. Redis 연결 테스트
    results.append(("Redis", test_redis_connection()))
    
    # 결과 요약
    logger.info("=== 테스트 결과 요약 ===")
    success_count = 0
    for test_name, result in results:
        status = "✅ 성공" if result else "❌ 실패"
        logger.info(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    logger.info(f"전체 {len(results)}개 테스트 중 {success_count}개 성공")
    
    if success_count == len(results):
        logger.info("🎉 모든 테스트가 성공했습니다!")
        return True
    else:
        logger.warning("⚠️ 일부 테스트가 실패했습니다.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 