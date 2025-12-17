#!/usr/bin/env python3
"""
Raw 센서 테이블 구조 확인
"""
import asyncio
from app.infrastructure.database import get_db

async def check_raw_tables():
    """Raw 센서 테이블 구조 확인"""
    async for db in get_db():
        break
    
    tables = [
        'sensor_raw_loadcell',
        'sensor_raw_mq5',
        'sensor_raw_mq7', 
        'sensor_raw_rfid',
        'sensor_raw_sound',
        'sensor_raw_tcrt5000',
        'sensor_raw_ultrasonic'
    ]
    
    for table_name in tables:
        try:
            result = await db.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)
            
            print(f"\n🔍 {table_name} 테이블:")
            for row in result:
                nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                print(f"  - {row[0]}: {row[1]} ({nullable})")
                
        except Exception as e:
            print(f"❌ {table_name} 조회 실패: {e}")
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(check_raw_tables()) 