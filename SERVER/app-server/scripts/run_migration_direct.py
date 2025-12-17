#!/usr/bin/env python3
"""
마이그레이션 직접 실행 스크립트
Alembic 없이 SQL을 직접 실행
"""

import psycopg2
from psycopg2 import sql
import sys

# 연결 정보
CONN_PARAMS = {
    'host': 'localhost',
    'port': 15432,
    'user': 'svc_dev',
    'password': 'IOT_dev_123!@#',
    'database': 'iot_care'
}

def run_migration():
    """마이그레이션 실행"""
    print("=" * 60)
    print("로봇 인식 이벤트 테이블 마이그레이션 실행")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**CONN_PARAMS)
        conn.autocommit = False  # 트랜잭션 사용
        cur = conn.cursor()
        
        print("\n1. ENUM 타입 생성...")
        
        # detection_category ENUM 생성
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE detection_category AS ENUM ('aruco', 'text', 'face', 'person');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        print("   ✅ detection_category ENUM 생성 완료")
        
        # intent_type ENUM 생성
        cur.execute("""
            DO $$ BEGIN
                CREATE TYPE intent_type AS ENUM ('open_door', 'start_follow', 'stop_follow', 'announce', 'none');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """)
        print("   ✅ intent_type ENUM 생성 완료")
        
        print("\n2. detection_event 테이블 생성...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS detection_event (
                detection_event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                robot_id TEXT NOT NULL,
                category TEXT NOT NULL,
                unique_key TEXT NOT NULL,
                meta JSONB NOT NULL,
                detected_at TIMESTAMPTZ NOT NULL,
                processing_info JSONB NOT NULL,
                processed_status TEXT NOT NULL DEFAULT 'accepted',
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        print("   ✅ detection_event 테이블 생성 완료")
        
        print("\n3. 인덱스 생성...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_detection_event_time 
            ON detection_event (detected_at DESC);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_detection_event_cat_key 
            ON detection_event (category, unique_key);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_detection_event_robot 
            ON detection_event (robot_id);
        """)
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_detection_event_status 
            ON detection_event (processed_status);
        """)
        print("   ✅ 인덱스 생성 완료")
        
        print("\n4. TimescaleDB 하이퍼테이블 변환 (조건부)...")
        cur.execute("""
            DO $$ 
            BEGIN
                IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                    PERFORM create_hypertable('detection_event', 'detected_at', if_not_exists => TRUE);
                    RAISE NOTICE 'TimescaleDB hypertable created for detection_event';
                ELSE
                    RAISE NOTICE 'TimescaleDB extension not found, using regular table';
                END IF;
            EXCEPTION
                WHEN OTHERS THEN
                    RAISE NOTICE 'Could not create hypertable: %', SQLERRM;
            END $$;
        """)
        print("   ✅ TimescaleDB 처리 완료")
        
        print("\n5. 레지스트리 테이블 생성...")
        
        # marker_registry
        cur.execute("""
            CREATE TABLE IF NOT EXISTS marker_registry (
                marker_key TEXT PRIMARY KEY,
                entrance_id TEXT,
                zone TEXT,
                pose JSONB,
                description TEXT,
                action_plan JSONB,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        print("   ✅ marker_registry 테이블 생성 완료")
        
        # text_registry
        cur.execute("""
            CREATE TABLE IF NOT EXISTS text_registry (
                text_key TEXT PRIMARY KEY,
                room_code TEXT,
                lang TEXT,
                synonyms TEXT[],
                action_plan JSONB,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        print("   ✅ text_registry 테이블 생성 완료")
        
        # face_registry
        cur.execute("""
            CREATE TABLE IF NOT EXISTS face_registry (
                face_key TEXT PRIMARY KEY,
                role TEXT CHECK (role IN ('elder', 'caregiver', 'visitor')),
                consent BOOLEAN NOT NULL DEFAULT FALSE,
                pii_ref TEXT,
                policy JSONB,
                action_plan JSONB,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        print("   ✅ face_registry 테이블 생성 완료")
        
        # person_registry
        cur.execute("""
            CREATE TABLE IF NOT EXISTS person_registry (
                person_key TEXT PRIMARY KEY,
                preferred_follow_distance_m NUMERIC(4, 2) DEFAULT 1.5,
                mobility_level TEXT,
                action_plan JSONB,
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
        """)
        print("   ✅ person_registry 테이블 생성 완료")
        
        print("\n6. Alembic 버전 업데이트...")
        # 현재 버전 확인
        cur.execute("SELECT version_num FROM alembic_version;")
        current_version = cur.fetchone()
        if current_version:
            print(f"   현재 버전: {current_version[0]}")
        
        # 새 버전으로 업데이트
        cur.execute("""
            UPDATE alembic_version 
            SET version_num = '20251110_robot_detection';
        """)
        print("   ✅ Alembic 버전 업데이트 완료: 20251110_robot_detection")
        
        # 커밋
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✅ 마이그레이션 완료!")
        print("=" * 60)
        print("\n생성된 테이블:")
        print("  - detection_event")
        print("  - marker_registry")
        print("  - text_registry")
        print("  - face_registry")
        print("  - person_registry")
        
        # 생성 확인
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename IN ('detection_event', 'marker_registry', 'text_registry', 'face_registry', 'person_registry')
            ORDER BY tablename;
        """)
        created_tables = cur.fetchall()
        print(f"\n생성 확인: {len(created_tables)}개 테이블")
        for table in created_tables:
            print(f"  ✅ {table[0]}")
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"\n❌ 데이터베이스 오류: {e}")
        if conn:
            conn.rollback()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        sys.exit(1)

if __name__ == "__main__":
    run_migration()

