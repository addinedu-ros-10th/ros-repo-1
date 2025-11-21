#!/usr/bin/env python3
"""
Raw 센서 데이터 정리 스크립트
외래 키 제약조건을 위반하는 데이터를 정리
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def clean_raw_data():
    """Raw 센서 데이터 정리"""
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
        
        # Raw 센서 테이블들의 문제 데이터 정리
        raw_tables = [
            'sensor_raw_cds',
            'sensor_raw_dht',
            'sensor_raw_flame',
            'sensor_raw_imu',
            'sensor_raw_loadcell',
            'sensor_raw_mq5',
            'sensor_raw_mq7',
            'sensor_raw_rfid',
            'sensor_raw_sound',
            'sensor_raw_tcrt5000',
            'sensor_raw_ultrasonic'
        ]
        
        for table_name in raw_tables:
            try:
                print(f"\n🧹 {table_name} 테이블 정리 중...")
                
                # devices 테이블에 존재하지 않는 device_id를 가진 레코드 삭제
                delete_result = await conn.execute(f"""
                    DELETE FROM {table_name} 
                    WHERE device_id NOT IN (SELECT device_id FROM devices)
                """)
                
                print(f"  삭제된 레코드: {delete_result.split()[-1] if 'DELETE' in delete_result else '0'}")
                
                # 남은 레코드 수 확인
                count_result = await conn.fetchval(f"SELECT COUNT(*) FROM {table_name}")
                print(f"  남은 레코드: {count_result}")
                
            except Exception as e:
                print(f"❌ {table_name} 정리 실패: {e}")
        
        await conn.close()
        print("\n✅ 데이터 정리 완료")
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(clean_raw_data()) 