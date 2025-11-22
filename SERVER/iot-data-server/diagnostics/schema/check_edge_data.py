#!/usr/bin/env python3
"""
Edge 센서 데이터 확인 스크립트
특수문자 문제를 피하여 데이터베이스에 안전하게 접근
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check_edge_data():
    """Edge 센서 데이터 확인"""
    # .env.local 파일 로드
    load_dotenv('../.env.local')
    
    # DB 연결 정보
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT')),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME')
    }
    
    print(f"DB 연결 정보: {db_config['host']}:{db_config['port']}")
    
    try:
        # DB 연결
        conn = await asyncpg.connect(**db_config)
        print("✅ DB 연결 성공")
        
        # Edge 센서 테이블들의 데이터 확인
        edge_tables = [
            'sensor_edge_flame',
            'sensor_edge_pir', 
            'sensor_edge_reed',
            'sensor_edge_tilt'
        ]
        
        for table_name in edge_tables:
            try:
                # 테이블의 레코드 수 확인
                count_result = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                print(f"\n📊 {table_name}: {count_result} 레코드")
                
                if count_result > 0:
                    # 샘플 데이터 확인
                    sample_result = await conn.fetch(f"SELECT device_id FROM {table_name} LIMIT 3")
                    device_ids = [row[0] for row in sample_result]
                    print(f"  샘플 device_ids: {device_ids}")
                    
                    # devices 테이블에 존재하는지 확인
                    for device_id in device_ids:
                        exists = await conn.fetchval("SELECT COUNT(*) FROM devices WHERE device_id = $1", device_id)
                        status = "✅ 존재" if exists > 0 else "❌ 존재하지 않음"
                        print(f"    {device_id}: {status}")
                        
            except Exception as e:
                print(f"❌ {table_name} 조회 실패: {e}")
        
        # Raw 센서 테이블들의 컬럼 구조 확인
        raw_tables = [
            'sensor_raw_loadcell',
            'sensor_raw_mq5',
            'sensor_raw_mq7', 
            'sensor_raw_rfid',
            'sensor_raw_sound',
            'sensor_raw_tcrt5000',
            'sensor_raw_ultrasonic'
        ]
        
        print(f"\n🔍 Raw 센서 테이블 구조 확인:")
        for table_name in raw_tables:
            try:
                columns = await conn.fetch(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                
                print(f"\n📋 {table_name}:")
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"  - {col['column_name']}: {col['data_type']} ({nullable})")
                    
            except Exception as e:
                print(f"❌ {table_name} 구조 확인 실패: {e}")
        
        await conn.close()
        print("\n✅ 데이터 확인 완료")
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(check_edge_data()) 