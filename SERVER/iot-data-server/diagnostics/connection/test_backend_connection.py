#!/usr/bin/env python3
"""
간단한 연결 테스트 스크립트

데이터베이스 및 Redis 연결을 테스트합니다.
"""

import os
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_database_connection():
    """PostgreSQL 데이터베이스 연결을 테스트합니다."""
    logger.info("=== PostgreSQL 연결 테스트 시작 ===")
    
    try:
        from app.infrastructure.database import test_connection, get_table_names
        
        # 연결 테스트
        if test_connection():
            logger.info("✅ PostgreSQL 연결 성공")
            
            # 기존 테이블 목록 조회
            tables = get_table_names()
            if tables:
                logger.info(f"📋 기존 테이블 {len(tables)}개 발견:")
                for table in tables:
                    logger.info(f"  - {table}")
            else:
                logger.info("📋 기존 테이블이 없습니다.")
            
            return True
        else:
            logger.error("❌ PostgreSQL 연결 실패")
            return False
            
    except Exception as e:
        logger.error(f"❌ PostgreSQL 연결 테스트 중 오류: {e}")
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


def test_config():
    """설정 파일을 테스트합니다."""
    logger.info("=== 설정 파일 테스트 시작 ===")
    
    try:
        from app.core.config import get_settings
        
        settings = get_settings()
        logger.info(f"✅ 환경: {settings.ENVIRONMENT}")
        logger.info(f"✅ 데이터베이스 URL: {settings.DATABASE_URL}")
        logger.info(f"✅ Redis URL: {settings.REDIS_URL}")
        logger.info(f"✅ Redis 호스트: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 설정 파일 테스트 중 오류: {e}")
        return False


def main():
    """메인 함수"""
    logger.info("🚀 연결 테스트 시작")
    
    results = []
    
    # 1. 설정 파일 테스트
    results.append(("설정 파일", test_config()))
    
    # 2. PostgreSQL 연결 테스트
    results.append(("PostgreSQL", test_database_connection()))
    
    # 3. Redis 연결 테스트
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

