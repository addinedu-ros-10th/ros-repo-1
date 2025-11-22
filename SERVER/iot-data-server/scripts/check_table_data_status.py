#!/usr/bin/env python3
"""
테이블 및 데이터 생성 상태 확인 스크립트

테이블 존재 여부와 데이터 개수를 확인합니다.
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

def check_table_data_status():
    """테이블 및 데이터 상태 확인"""
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
        
        print("✅ 데이터베이스 연결 성공!\n")
        
        cur = conn.cursor()
        
        # ============================================================
        # 1. 테이블 존재 확인
        # ============================================================
        print("=" * 80)
        print("📊 테이블 존재 확인")
        print("=" * 80)
        
        required_tables = ['users', 'user_profiles', 'user_relationships', 'residents']
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name IN ('users', 'user_profiles', 'user_relationships', 'residents')
            ORDER BY table_name
        """)
        
        existing_tables = [row[0] for row in cur.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                print(f"✅ {table} 테이블 존재")
            else:
                print(f"❌ {table} 테이블 없음")
        
        # ============================================================
        # 2. 데이터 개수 확인
        # ============================================================
        print("\n" + "=" * 80)
        print("📊 데이터 개수 확인")
        print("=" * 80)
        
        for table in required_tables:
            if table in existing_tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cur.fetchone()[0]
                    print(f"   {table}: {count}개")
                except Exception as e:
                    print(f"   {table}: 확인 실패 ({e})")
            else:
                print(f"   {table}: 테이블 없음 (확인 불가)")
        
        # ============================================================
        # 3. users 테이블 역할별 개수
        # ============================================================
        if 'users' in existing_tables:
            print("\n" + "=" * 80)
            print("📊 users 테이블 역할별 개수")
            print("=" * 80)
            
            try:
                cur.execute("""
                    SELECT user_role, COUNT(*) AS count
                    FROM users
                    GROUP BY user_role
                    ORDER BY user_role
                """)
                results = cur.fetchall()
                for role, count in results:
                    print(f"   {role}: {count}개")
            except Exception as e:
                print(f"   확인 실패: {e}")
        
        # ============================================================
        # 4. user_relationships 테이블 관계 유형별 개수
        # ============================================================
        if 'user_relationships' in existing_tables:
            print("\n" + "=" * 80)
            print("📊 user_relationships 테이블 관계 유형별 개수")
            print("=" * 80)
            
            try:
                cur.execute("""
                    SELECT relationship_type, COUNT(*) AS count
                    FROM user_relationships
                    GROUP BY relationship_type
                    ORDER BY relationship_type
                """)
                results = cur.fetchall()
                for rel_type, count in results:
                    print(f"   {rel_type}: {count}개")
            except Exception as e:
                print(f"   확인 실패: {e}")
        
        # ============================================================
        # 5. residents 테이블 상세 정보
        # ============================================================
        if 'residents' in existing_tables:
            print("\n" + "=" * 80)
            print("📊 residents 테이블 상세 정보")
            print("=" * 80)
            
            try:
                # 현재 입소 중인 입소자 수
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM residents 
                    WHERE discharge_date IS NULL
                """)
                current_count = cur.fetchone()[0]
                print(f"   현재 입소 중: {current_count}명")
                
                # 생활실별 입소자 수
                cur.execute("""
                    SELECT room_number, COUNT(*) AS count
                    FROM residents
                    WHERE discharge_date IS NULL
                    GROUP BY room_number
                    ORDER BY room_number
                """)
                room_results = cur.fetchall()
                if room_results:
                    print(f"   생활실별 입소자:")
                    for room, count in room_results:
                        print(f"      {room}호: {count}명")
                
                # 입소자 목록
                cur.execute("""
                    SELECT 
                        r.resident_number,
                        r.nickname,
                        r.room_number,
                        u.user_name
                    FROM residents r
                    INNER JOIN users u ON r.user_id = u.user_id
                    WHERE r.discharge_date IS NULL
                    ORDER BY r.room_number
                """)
                residents = cur.fetchall()
                if residents:
                    print(f"\n   입소자 목록:")
                    for res_num, nickname, room, name in residents:
                        print(f"      {res_num} | {nickname} ({name}) | {room}호")
            except Exception as e:
                print(f"   확인 실패: {e}")
        
        # ============================================================
        # 6. 종합 상태
        # ============================================================
        print("\n" + "=" * 80)
        print("📋 종합 상태")
        print("=" * 80)
        
        all_tables_exist = all(table in existing_tables for table in required_tables)
        
        if all_tables_exist:
            print("✅ 모든 필수 테이블이 존재합니다.")
        else:
            print("❌ 일부 테이블이 없습니다.")
            missing = [t for t in required_tables if t not in existing_tables]
            print(f"   없는 테이블: {', '.join(missing)}")
        
        # 데이터 존재 여부 확인
        has_data = False
        if 'residents' in existing_tables:
            try:
                cur.execute("SELECT COUNT(*) FROM residents")
                count = cur.fetchone()[0]
                if count > 0:
                    has_data = True
                    print(f"✅ residents 테이블에 데이터가 있습니다 ({count}개)")
                else:
                    print("⚠️  residents 테이블에 데이터가 없습니다.")
            except:
                pass
        
        if not has_data:
            print("\n💡 다음 단계:")
            print("   1. 테이블이 없으면: maintenance/database/create_residents_table.sql 실행")
            print("   2. 데이터가 없으면: maintenance/database/insert_all_users_mock_data.sql 실행")
        
        cur.close()
        conn.close()
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ 데이터베이스 연결 실패: {e}")
        print("\n💡 해결 방법:")
        print("   1. DB_HOST가 올바른지 확인 (Docker 컨테이너에서 접근 가능한 주소)")
        print("   2. PostgreSQL 서버가 실행 중인지 확인")
        print("   3. 방화벽 설정 확인")
        print("   4. 네트워크 연결 확인")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("테이블 및 데이터 생성 상태 확인")
    print("=" * 80)
    
    success = check_table_data_status()
    
    if success:
        print("\n✅ 상태 확인 완료!")
    else:
        print("\n❌ 상태 확인 실패!")
        sys.exit(1)

