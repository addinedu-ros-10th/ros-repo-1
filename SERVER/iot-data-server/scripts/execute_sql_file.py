#!/usr/bin/env python3
"""
SQL 파일 실행 스크립트

데이터베이스에 SQL 파일을 실행합니다.
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

def execute_sql_file(sql_file_path: str):
    """SQL 파일을 실행합니다."""
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
        
        # SQL 파일 읽기
        sql_path = project_root / sql_file_path
        if not sql_path.exists():
            print(f"❌ SQL 파일을 찾을 수 없습니다: {sql_path}")
            sys.exit(1)
        
        print(f"\n📄 SQL 파일: {sql_path}")
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 데이터베이스 연결
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=5
        )
        
        print("✅ 데이터베이스 연결 성공!")
        
        # SQL 실행
        cur = conn.cursor()
        print(f"\n🚀 SQL 파일 실행 중...")
        
        # SQL을 세미콜론으로 분리하여 하나씩 실행
        # (CREATE TABLE IF NOT EXISTS 등은 여러 문장일 수 있음)
        cur.execute(sql_content)
        conn.commit()
        
        print("✅ SQL 파일 실행 완료!")
        
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ 데이터베이스 연결 실패: {e}")
        return False
    except psycopg2.Error as e:
        print(f"\n❌ SQL 실행 오류: {e}")
        if conn:
            conn.rollback()
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python3 execute_sql_file.py <sql_file_path>")
        print("예시: python3 execute_sql_file.py maintenance/database/create_residents_table.sql")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    
    print("=" * 80)
    print("SQL 파일 실행")
    print("=" * 80)
    
    success = execute_sql_file(sql_file)
    
    if success:
        print("\n✅ SQL 파일 실행 완료!")
    else:
        print("\n❌ SQL 파일 실행 실패!")
        sys.exit(1)

