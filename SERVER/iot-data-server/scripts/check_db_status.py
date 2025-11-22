#!/usr/bin/env python3
"""
데이터베이스 상태 확인 스크립트

DB 연결 및 테이블 존재 여부를 확인합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# .env.local 파일 로드
env_file = project_root / ".env.local"
if env_file.exists():
    load_dotenv(env_file)
else:
    print("⚠️  .env.local 파일을 찾을 수 없습니다.")
    sys.exit(1)

def check_db_connection():
    """데이터베이스 연결 확인"""
    try:
        db_host = os.getenv("DB_HOST")
        db_port = os.getenv("DB_PORT")
        db_name = os.getenv("DB_NAME")
        db_user = os.getenv("DB_USER")
        db_password = os.getenv("DB_PASSWORD")
        
        print(f"\n🔍 데이터베이스 연결 정보:")
        print(f"   호스트: {db_host}:{db_port}")
        print(f"   데이터베이스: {db_name}")
        print(f"   사용자: {db_user}")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5
        )
        
        print("✅ 데이터베이스 연결 성공!")
        
        # 테이블 목록 조회
        cur = conn.cursor()
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        print(f"\n📊 현재 테이블 목록 ({len(tables)}개):")
        for table in tables:
            print(f"   - {table}")
        
        # residents 테이블 확인
        if "residents" in tables:
            print("\n✅ residents 테이블이 존재합니다!")
            
            # 테이블 구조 확인
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'residents'
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            print(f"\n📋 residents 테이블 구조 ({len(columns)}개 컬럼):")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                print(f"   - {col[0]}: {col[1]} ({nullable})")
            
            # 데이터 개수 확인
            cur.execute("SELECT COUNT(*) FROM residents")
            count = cur.fetchone()[0]
            print(f"\n📊 residents 테이블 데이터 개수: {count}개")
        else:
            print("\n❌ residents 테이블이 존재하지 않습니다!")
            print("   테이블을 생성해야 합니다.")
        
        cur.close()
        conn.close()
        
        return True, tables
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ 데이터베이스 연결 실패: {e}")
        print("\n💡 해결 방법:")
        print("   1. DB_HOST가 올바른지 확인 (Docker 컨테이너에서 접근 가능한 주소)")
        print("   2. PostgreSQL 서버가 실행 중인지 확인")
        print("   3. 방화벽 설정 확인")
        print("   4. 네트워크 연결 확인")
        return False, []
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        return False, []

if __name__ == "__main__":
    print("=" * 60)
    print("데이터베이스 상태 확인")
    print("=" * 60)
    
    success, tables = check_db_connection()
    
    if success:
        print("\n✅ 데이터베이스 상태 확인 완료!")
    else:
        print("\n❌ 데이터베이스 상태 확인 실패!")
        sys.exit(1)

