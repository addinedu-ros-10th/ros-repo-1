#!/usr/bin/env python3
"""
데이터베이스 테이블 수정 스크립트
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def fix_database():
    """데이터베이스 테이블을 수정합니다."""
    
    # 데이터베이스 연결
    conn = psycopg2.connect(
        host='192.168.2.81',
        port=15432,
        database='iot_care',
        user='svc_dev',
        password='IOT_dev_123!@#'
    )
    
    cur = conn.cursor()
    
    try:
        print("🔧 데이터베이스 테이블 수정 시작...")
        
        # 1. sensor_edge_flame 테이블 수정
        print("📝 sensor_edge_flame 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_edge_flame CASCADE;
            CREATE TABLE sensor_edge_flame (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                flame_detected BOOLEAN NOT NULL,
                confidence NUMERIC,
                alert_level TEXT,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        # 2. sensor_edge_pir 테이블 수정
        print("📝 sensor_edge_pir 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_edge_pir CASCADE;
            CREATE TABLE sensor_edge_pir (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                motion_detected BOOLEAN NOT NULL,
                confidence NUMERIC,
                motion_direction TEXT,
                motion_speed NUMERIC,
                processing_time NUMERIC,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        # 3. sensor_edge_reed 테이블 수정
        print("📝 sensor_edge_reed 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_edge_reed CASCADE;
            CREATE TABLE sensor_edge_reed (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                switch_state BOOLEAN NOT NULL,
                confidence NUMERIC,
                magnetic_field_detected BOOLEAN,
                magnetic_strength NUMERIC,
                processing_time NUMERIC,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        # 4. sensor_edge_tilt 테이블 수정
        print("📝 sensor_edge_tilt 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_edge_tilt CASCADE;
            CREATE TABLE sensor_edge_tilt (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                tilt_detected BOOLEAN NOT NULL,
                confidence NUMERIC,
                tilt_angle NUMERIC,
                tilt_direction TEXT,
                processing_time NUMERIC,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        # 5. 기본 테이블들도 확인
        print("📝 기본 테이블들 확인 중...")
        
        # users 테이블
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY,
                user_role VARCHAR(20) NOT NULL,
                user_name TEXT NOT NULL,
                email TEXT,
                phone_number TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # devices 테이블
        cur.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id VARCHAR(64) PRIMARY KEY,
                user_id UUID REFERENCES users(user_id),
                location_label TEXT,
                installed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # device_rtc_status 테이블
        cur.execute("""
            CREATE TABLE IF NOT EXISTS device_rtc_status (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64) REFERENCES devices(device_id),
                rtc_epoch_s BIGINT,
                drift_ms INTEGER,
                sync_source TEXT,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        conn.commit()
        print("✅ 모든 테이블 수정 완료!")
        
        # 테이블 목록 확인
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        print(f"\n📊 생성된 테이블 목록 ({len(tables)}개):")
        for table in tables:
            print(f"  - {table[0]}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_database() 