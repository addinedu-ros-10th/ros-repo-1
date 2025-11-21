#!/usr/bin/env python3
"""
Edge 센서 테이블 직접 수정 스크립트
"""

import psycopg2
from psycopg2.extras import RealDictCursor

def fix_edge_tables():
    """Edge 센서 테이블들을 직접 수정합니다."""
    
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
        print("🔧 Edge 센서 테이블 직접 수정 시작...")
        
        # 1. sensor_edge_reed 테이블에 누락된 컬럼 추가
        print("📝 sensor_edge_reed 테이블에 누락된 컬럼 추가 중...")
        cur.execute("""
            ALTER TABLE sensor_edge_reed 
            ADD COLUMN IF NOT EXISTS confidence NUMERIC,
            ADD COLUMN IF NOT EXISTS magnetic_strength NUMERIC,
            ADD COLUMN IF NOT EXISTS processing_time NUMERIC;
        """)
        
        # 2. sensor_edge_tilt 테이블에 누락된 컬럼 추가
        print("📝 sensor_edge_tilt 테이블에 누락된 컬럼 추가 중...")
        cur.execute("""
            ALTER TABLE sensor_edge_tilt 
            ADD COLUMN IF NOT EXISTS confidence NUMERIC,
            ADD COLUMN IF NOT EXISTS processing_time NUMERIC;
        """)
        
        # 3. sensor_edge_flame 테이블에 누락된 컬럼 추가
        print("📝 sensor_edge_flame 테이블에 누락된 컬럼 추가 중...")
        cur.execute("""
            ALTER TABLE sensor_edge_flame 
            ADD COLUMN IF NOT EXISTS processing_time NUMERIC;
        """)
        
        conn.commit()
        print("✅ Edge 센서 테이블 수정 완료!")
        
        # 테이블 구조 확인
        print("\n🔍 수정된 테이블 구조 확인:")
        tables = ['sensor_edge_flame', 'sensor_edge_pir', 'sensor_edge_reed', 'sensor_edge_tilt']
        
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
    fix_edge_tables() 