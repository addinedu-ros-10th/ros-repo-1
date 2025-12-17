#!/usr/bin/env python3
"""
간단한 데이터베이스 권한 수정 스크립트
"""

import os
import psycopg2
from dotenv import load_dotenv

# .env.prod 파일 로드
load_dotenv('.env.prod')

def fix_database_permissions():
    """데이터베이스 권한 수정"""
    
    print("🔧 데이터베이스 권한 수정 시작...")
    
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
        # PostgreSQL 연결 (슈퍼유저 또는 소유자 계정으로)
        print("\n⚠️  주의: 이 스크립트는 슈퍼유저 또는 데이터베이스 소유자 계정으로 실행해야 합니다.")
        print("현재 계정이 권한이 없다면, 슈퍼유저로 직접 실행하세요.")
        
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
        
        # 1. 현재 사용자 권한 확인
        cur.execute("SELECT current_user, session_user, current_database();")
        user_info = cur.fetchone()
        print(f"현재 사용자: {user_info[0]}")
        print(f"세션 사용자: {user_info[1]}")
        print(f"현재 데이터베이스: {user_info[2]}")
        
        # 2. users 테이블 존재 확인
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'users'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("\n❌ users 테이블이 존재하지 않습니다.")
            print("테이블을 먼저 생성해야 합니다.")
            return
        
        print("\n✅ users 테이블이 존재합니다.")
        
        # 3. 권한 부여 시도
        try:
            print("\n🔑 권한 부여 중...")
            
            # SELECT 권한 부여
            cur.execute("GRANT SELECT ON TABLE users TO svc_app;")
            print("✅ SELECT 권한 부여 완료")
            
            # INSERT, UPDATE, DELETE 권한 부여
            cur.execute("GRANT INSERT, UPDATE, DELETE ON TABLE users TO svc_app;")
            print("✅ INSERT, UPDATE, DELETE 권한 부여 완료")
            
            # public 스키마 권한 부여
            cur.execute("GRANT USAGE ON SCHEMA public TO svc_app;")
            print("✅ public 스키마 USAGE 권한 부여 완료")
            
            # 변경사항 커밋
            conn.commit()
            print("✅ 모든 권한 부여 완료 및 커밋됨")
            
        except Exception as e:
            print(f"\n❌ 권한 부여 실패: {e}")
            print("슈퍼유저 또는 데이터베이스 소유자 계정으로 실행해야 합니다.")
            conn.rollback()
            return
        
        # 4. 권한 부여 확인
        print("\n🔍 권한 부여 확인:")
        cur.execute("""
            SELECT 
                grantee,
                table_name,
                privilege_type,
                is_grantable
            FROM information_schema.table_privileges 
            WHERE table_name = 'users' 
            AND table_schema = 'public'
            AND grantee = 'svc_app'
            ORDER BY privilege_type;
        """)
        privileges = cur.fetchall()
        
        if privileges:
            print(f"{'권한받은자':<20} {'테이블명':<15} {'권한타입':<15} {'부여가능':<8}")
            print("-" * 60)
            for privilege in privileges:
                print(f"{privilege[0]:<20} {privilege[1]:<15} {privilege[2]:<15} {str(privilege[3]):<8}")
        else:
            print("❌ svc_app 사용자에게 부여된 권한이 없습니다.")
        
        cur.close()
        conn.close()
        
        print("\n✅ 데이터베이스 권한 수정 완료!")
        print("\n🎯 다음 단계:")
        print("1. API 서버를 재시작하세요")
        print("2. 사용자 목록 API를 다시 테스트해보세요")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")

if __name__ == "__main__":
    fix_database_permissions()
