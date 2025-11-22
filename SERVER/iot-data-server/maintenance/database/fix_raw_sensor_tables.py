#!/usr/bin/env python3
"""
Raw 센서 테이블 스키마 수정 스크립트
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def fix_raw_sensor_tables():
    """Raw 센서 테이블들의 스키마를 수정합니다."""
    
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
        print("🔧 Raw 센서 테이블 스키마 수정 시작...")
        
        # 1. sensor_raw_cds 테이블 수정
        print("📝 sensor_raw_cds 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_raw_cds CASCADE;
            CREATE TABLE sensor_raw_cds (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                analog_value INTEGER,
                lux_value NUMERIC,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        # 2. sensor_raw_dht 테이블 수정
        print("📝 sensor_raw_dht 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_raw_dht CASCADE;
            CREATE TABLE sensor_raw_dht (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                temperature NUMERIC,
                humidity NUMERIC,
                heat_index NUMERIC,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        # 3. sensor_raw_flame 테이블 수정
        print("📝 sensor_raw_flame 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_raw_flame CASCADE;
            CREATE TABLE sensor_raw_flame (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                analog_value INTEGER,
                digital_value BOOLEAN,
                flame_detected BOOLEAN,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        # 4. sensor_raw_imu 테이블 수정
        print("📝 sensor_raw_imu 테이블 수정 중...")
        cur.execute("""
            DROP TABLE IF EXISTS sensor_raw_imu CASCADE;
            CREATE TABLE sensor_raw_imu (
                time TIMESTAMP WITH TIME ZONE,
                device_id VARCHAR(64),
                accel_x NUMERIC,
                accel_y NUMERIC,
                accel_z NUMERIC,
                gyro_x NUMERIC,
                gyro_y NUMERIC,
                gyro_z NUMERIC,
                mag_x NUMERIC,
                mag_y NUMERIC,
                mag_z NUMERIC,
                temperature NUMERIC,
                raw_payload JSONB,
                PRIMARY KEY (time, device_id)
            );
        """)
        
        conn.commit()
        print("✅ 모든 Raw 센서 테이블 수정 완료!")
        
        # 테이블 구조 확인
        print("\n🔍 수정된 테이블 구조 확인:")
        tables = ['sensor_raw_cds', 'sensor_raw_dht', 'sensor_raw_flame', 'sensor_raw_imu']
        
        for table_name in tables:
            print(f"\n📋 {table_name} 테이블 구조:")
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"  - {col[0]}: {col[1]} {nullable}{default}")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    fix_raw_sensor_tables()