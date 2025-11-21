#!/usr/bin/env python3
"""
DB 테이블 구조 확인 스크립트
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

async def check_table_structure():
    """테이블 구조 확인"""
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
        
        # 테이블 목록 조회
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'sensor_%'
            ORDER BY table_name
        """)
        
        print(f"\n📋 센서 테이블 목록:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # 주요 테이블 구조 확인
        target_tables = [
            'sensor_raw_loadcell',
            'sensor_raw_mq5', 
            'sensor_raw_mq7',
            'sensor_raw_rfid',
            'sensor_raw_sound',
            'sensor_raw_tcrt5000',
            'sensor_raw_ultrasonic'
        ]
        
        for table_name in target_tables:
            try:
                columns = await conn.fetch(f"""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}'
                    ORDER BY ordinal_position
                """)
                
                print(f"\n🔍 {table_name} 테이블 구조:")
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"  - {col['column_name']}: {col['data_type']} ({nullable})")
                    
            except Exception as e:
                print(f"❌ {table_name} 테이블 조회 실패: {e}")
        
        await conn.close()
        print("\n✅ 테이블 구조 확인 완료")
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(check_table_structure()) 