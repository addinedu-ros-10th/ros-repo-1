#!/usr/bin/env python3
"""
svc_app 계정에 필요한 권한을 부여하는 스크립트
"""

import os
import psycopg2
from dotenv import load_dotenv

# .env.local 파일 로드
load_dotenv('../.env.local')

def grant_permissions_to_svc_app():
    """svc_app 계정에 필요한 권한 부여"""
    
    print("🔧 svc_app 계정에 필요한 권한 부여 시작...")
    
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
        
        # 1. 현재 사용자 권한 확인
        cur.execute("SELECT current_user, session_user, current_database();")
        user_info = cur.fetchone()
        print(f"현재 사용자: {user_info[0]}")
        print(f"세션 사용자: {user_info[1]}")
        print(f"현재 데이터베이스: {user_info[2]}")
        
        # 2. 권한 부여할 테이블 목록
        tables_to_grant = [
            # 사용자 테이블
            "users",
            # Raw 센서 테이블
            "sensor_raw_cds", "sensor_raw_dht", "sensor_raw_flame", "sensor_raw_imu",
            "sensor_raw_loadcell", "sensor_raw_mq5", "sensor_raw_mq7", "sensor_raw_rfid",
            "sensor_raw_sound", "sensor_raw_tcrt5000", "sensor_raw_ultrasonic",
            # Edge 센서 테이블
            "sensor_edge_flame", "sensor_edge_pir", "sensor_edge_reed", "sensor_edge_tilt",
            # 액추에이터 테이블
            "actuator_log_buzzer", "actuator_log_ir_tx", "actuator_log_relay", "actuator_log_servo",
            # 기타 테이블
            "devices", "device_rtc_status", "alembic_version"
        ]
        
        print(f"\n🔑 권한 부여할 테이블 수: {len(tables_to_grant)}")
        
        # 3. 각 테이블에 권한 부여
        granted_tables = []
        failed_tables = []
        
        for table_name in tables_to_grant:
            try:
                # 테이블 존재 여부 확인
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table_name,))
                
                table_exists = cur.fetchone()[0]
                
                if table_exists:
                    # 권한 부여
                    cur.execute(f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE {table_name} TO svc_app;")
                    granted_tables.append(table_name)
                    print(f"   ✅ {table_name}: 권한 부여 완료")
                else:
                    failed_tables.append(f"{table_name} (테이블 없음)")
                    print(f"   ⚠️  {table_name}: 테이블이 존재하지 않음")
                    
            except Exception as e:
                failed_tables.append(f"{table_name} (오류: {e})")
                print(f"   ❌ {table_name}: 권한 부여 실패 - {e}")
        
        # 4. 변경사항 커밋
        conn.commit()
        print(f"\n💾 모든 변경사항이 커밋되었습니다.")
        
        # 5. 권한 부여 결과 요약
        print(f"\n📊 권한 부여 결과:")
        print(f"   ✅ 성공: {len(granted_tables)}개 테이블")
        print(f"   ❌ 실패: {len(failed_tables)}개 테이블")
        
        if granted_tables:
            print(f"\n✅ 권한 부여 성공한 테이블:")
            for table in granted_tables:
                print(f"   - {table}")
        
        if failed_tables:
            print(f"\n❌ 권한 부여 실패한 테이블:")
            for table in failed_tables:
                print(f"   - {table}")
        
        # 6. svc_app의 users 테이블 권한 확인
        print(f"\n🔍 svc_app의 users 테이블 권한 확인:")
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
        
        users_privileges = cur.fetchall()
        
        if users_privileges:
            print(f"{'권한받은자':<20} {'테이블명':<15} {'권한타입':<15} {'부여가능':<8}")
            print("-" * 60)
            for privilege in users_privileges:
                print(f"{privilege[0]:<20} {privilege[1]:<15} {privilege[2]:<15} {str(privilege[3]):<8}")
        else:
            print("❌ svc_app에게 users 테이블 권한이 없습니다.")
        
        cur.close()
        conn.close()
        
        print(f"\n{'='*60}")
        print("✅ 권한 부여 완료!")
        print(f"{'='*60}")
        print(f"\n🎯 다음 단계:")
        print(f"1. API 서버를 재시작하세요")
        print(f"2. Swagger UI에서 사용자 목록 API를 테스트해보세요")
        print(f"3. 권한 문제가 해결되었는지 확인하세요")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        print(f"오류 타입: {type(e).__name__}")

if __name__ == "__main__":
    grant_permissions_to_svc_app()
