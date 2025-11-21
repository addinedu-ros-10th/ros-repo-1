#!/usr/bin/env python3
"""
데이터베이스 권한 및 테이블 상태 확인 스크립트
"""

import os
import psycopg2
from dotenv import load_dotenv

# .env.prod 파일 로드
load_dotenv('.env.prod')

def check_database_permissions():
    """데이터베이스 권한 및 테이블 상태 확인"""
    
    print("🔍 데이터베이스 권한 및 테이블 상태 확인 시작...")
    
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
    
    try:
        # PostgreSQL 연결
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
        
        # 1. 현재 사용자 정보 확인
        print("\n👤 현재 사용자 정보:")
        cur.execute("SELECT current_user, session_user, current_database();")
        user_info = cur.fetchone()
        print(f"현재 사용자: {user_info[0]}")
        print(f"세션 사용자: {user_info[1]}")
        print(f"현재 데이터베이스: {user_info[2]}")
        
        # 2. 사용자 권한 확인
        print("\n🔐 사용자 권한 확인:")
        cur.execute("""
            SELECT 
                usename,
                usecreatedb,
                usesuper,
                usebypassrls
            FROM pg_user 
            WHERE usename = current_user;
        """)
        user_privileges = cur.fetchone()
        if user_privileges:
            print(f"사용자: {user_privileges[0]}")
            print(f"데이터베이스 생성 권한: {user_privileges[1]}")
            print(f"슈퍼유저 권한: {user_privileges[2]}")
            print(f"RLS 우회 권한: {user_privileges[3]}")
        
        # 3. 테이블 목록 및 소유자 확인
        print("\n📋 테이블 목록 및 소유자:")
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                tableowner,
                hasindexes,
                hasrules,
                hastriggers
            FROM pg_tables 
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)
        tables = cur.fetchall()
        
        if tables:
            print(f"{'스키마':<15} {'테이블명':<20} {'소유자':<15} {'인덱스':<8} {'규칙':<6} {'트리거':<8}")
            print("-" * 80)
            for table in tables:
                print(f"{table[0]:<15} {table[1]:<20} {table[2]:<15} {str(table[3]):<8} {str(table[4]):<6} {str(table[5]):<8}")
        else:
            print("❌ public 스키마에 테이블이 없습니다.")
        
        # 4. users 테이블 상세 정보 확인
        print("\n👥 users 테이블 상세 정보:")
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                tableowner,
                tablespace,
                hasindexes,
                hasrules,
                hastriggers
            FROM pg_tables 
            WHERE tablename = 'users';
        """)
        users_table = cur.fetchone()
        
        if users_table:
            print(f"스키마: {users_table[0]}")
            print(f"테이블명: {users_table[1]}")
            print(f"소유자: {users_table[2]}")
            print(f"테이블스페이스: {users_table[3]}")
            print(f"인덱스 여부: {users_table[4]}")
            print(f"규칙 여부: {users_table[5]}")
            print(f"트리거 여부: {users_table[6]}")
        else:
            print("❌ users 테이블을 찾을 수 없습니다.")
        
        # 5. 테이블 권한 확인
        print("\n🔑 테이블 권한 확인:")
        cur.execute("""
            SELECT 
                grantee,
                table_name,
                privilege_type,
                is_grantable
            FROM information_schema.table_privileges 
            WHERE table_name = 'users' 
            AND table_schema = 'public'
            ORDER BY grantee, privilege_type;
        """)
        table_privileges = cur.fetchall()
        
        if table_privileges:
            print(f"{'권한받은자':<20} {'테이블명':<15} {'권한타입':<15} {'부여가능':<8}")
            print("-" * 60)
            for privilege in table_privileges:
                print(f"{privilege[0]:<20} {privilege[1]:<15} {privilege[2]:<15} {str(privilege[3]):<8}")
        else:
            print("❌ users 테이블에 대한 권한 정보를 찾을 수 없습니다.")
        
        # 6. 스키마 권한 확인
        print("\n🏗️ 스키마 권한 확인:")
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
            print(f"스키마명: {schema_info[0]}")
            print(f"소유자: {schema_info[1]}")
            print(f"권한: {schema_info[2]}")
        
        cur.close()
        conn.close()
        
        print("\n✅ 데이터베이스 권한 확인 완료!")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")

if __name__ == "__main__":
    check_database_permissions()
