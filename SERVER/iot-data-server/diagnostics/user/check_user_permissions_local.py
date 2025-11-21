#!/usr/bin/env python3
"""
svc_dev와 svc_app 계정 권한 확인 스크립트 (.env.local 사용)
"""

import os
import psycopg2
from dotenv import load_dotenv

# .env.local 파일 로드
load_dotenv('../.env.local')

def check_user_permissions():
    """사용자 계정 권한 확인"""
    
    print("🔍 svc_dev와 svc_app 계정 권한 확인 시작...")
    print("📁 환경변수 파일: .env.local")
    
    # 환경변수 확인
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    
    print(f"\n📋 환경변수:")
    print(f"DB_HOST: {DB_HOST}")
    print(f"DB_PORT: {DB_PORT}")
    print(f"DB_USER: {DB_USER}")
    print(f"DB_NAME: {DB_NAME}")
    
    # 확인할 사용자 목록
    users_to_check = ['svc_dev', 'svc_app']
    
    try:
        # PostgreSQL 연결
        print(f"\n🔌 데이터베이스 연결 시도 중...")
        print(f"   호스트: {DB_HOST}:{DB_PORT}")
        print(f"   데이터베이스: {DB_NAME}")
        print(f"   사용자: {DB_USER}")
        
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME,
            connect_timeout=10
        )
        
        cur = conn.cursor()
        
        print("\n✅ 데이터베이스 연결 성공!")
        
        for username in users_to_check:
            print(f"\n{'='*60}")
            print(f"👤 {username} 계정 권한 확인")
            print(f"{'='*60}")
            
            # 1. 사용자 존재 여부 확인
            cur.execute("""
                SELECT 
                    usename,
                    usecreatedb,
                    usesuper,
                    usebypassrls,
                    passwd IS NOT NULL as has_password
                FROM pg_user 
                WHERE usename = %s;
            """, (username,))
            
            user_info = cur.fetchone()
            
            if user_info:
                print(f"✅ 사용자 존재: {user_info[0]}")
                print(f"   데이터베이스 생성 권한: {user_info[1]}")
                print(f"   슈퍼유저 권한: {user_info[2]}")
                print(f"   RLS 우회 권한: {user_info[3]}")
                print(f"   비밀번호 설정: {user_info[4]}")
            else:
                print(f"❌ 사용자 {username}가 존재하지 않습니다.")
                continue
            
            # 2. 데이터베이스별 권한 확인
            cur.execute("""
                SELECT 
                    datname,
                    datacl
                FROM pg_database 
                WHERE datname = %s;
            """, (DB_NAME,))
            
            db_info = cur.fetchone()
            if db_info:
                print(f"\n📊 데이터베이스 '{db_info[0]}' 권한:")
                print(f"   ACL: {db_info[1]}")
            
            # 3. 스키마 권한 확인
            cur.execute("""
                SELECT 
                    nspname,
                    nspowner::regrole,
                    nspacl
                FROM pg_namespace 
                WHERE nspname = 'public';
            """)
            
            schema_info = cur.fetchone()
            if schema_info:
                print(f"\n🏗️ public 스키마 권한:")
                print(f"   소유자: {schema_info[1]}")
                print(f"   ACL: {schema_info[2]}")
            
            # 4. users 테이블 권한 확인
            cur.execute("""
                SELECT 
                    grantee,
                    table_name,
                    privilege_type,
                    is_grantable
                FROM information_schema.table_privileges 
                WHERE table_name = 'users' 
                AND table_schema = 'public'
                AND grantee = %s
                ORDER BY privilege_type;
            """, (username,))
            
            table_privileges = cur.fetchall()
            
            if table_privileges:
                print(f"\n🔑 users 테이블 권한:")
                print(f"{'권한받은자':<20} {'테이블명':<15} {'권한타입':<15} {'부여가능':<8}")
                print("-" * 60)
                for privilege in table_privileges:
                    print(f"{privilege[0]:<20} {privilege[1]:<15} {privilege[2]:<15} {str(privilege[3]):<8}")
            else:
                print(f"\n❌ {username}에게 users 테이블 권한이 없습니다.")
            
            # 5. 모든 테이블 권한 확인
            cur.execute("""
                SELECT 
                    table_name,
                    privilege_type,
                    is_grantable
                FROM information_schema.table_privileges 
                WHERE table_schema = 'public'
                AND grantee = %s
                ORDER BY table_name, privilege_type;
            """, (username,))
            
            all_table_privileges = cur.fetchall()
            
            if all_table_privileges:
                print(f"\n🔑 전체 테이블 권한:")
                print(f"{'테이블명':<25} {'권한타입':<15} {'부여가능':<8}")
                print("-" * 50)
                for privilege in all_table_privileges:
                    print(f"{privilege[0]:<25} {privilege[1]:<15} {str(privilege[2]):<8}")
            else:
                print(f"\n❌ {username}에게 public 스키마 테이블 권한이 없습니다.")
        
        cur.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print("✅ 모든 사용자 권한 확인 완료!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")
        
        # 연결 실패 시 추가 정보 제공
        if "connection" in str(e).lower():
            print(f"\n🔍 연결 문제 해결 방법:")
            print(f"1. SSH 터널이 활성화되어 있는지 확인")
            print(f"2. DB_HOST ({DB_HOST})가 올바른지 확인")
            print(f"3. DB_PORT ({DB_PORT})가 올바른지 확인")
            print(f"4. 방화벽 설정 확인")
            print(f"5. PostgreSQL 서버가 실행 중인지 확인")

if __name__ == "__main__":
    check_user_permissions()
