#!/usr/bin/env python3
"""
데이터베이스 테이블 구조 확인 스크립트
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# .env.local 파일 로드
load_dotenv('../.env.local')

async def check_table_structure():
    """데이터베이스 테이블 구조를 확인합니다."""
    try:
        # 데이터베이스 연결
        conn = await asyncpg.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        print("🔍 데이터베이스 테이블 구조 확인 중...")
        print("=" * 60)
        
        # 센서 관련 테이블들 확인
        sensor_tables = [
            'sensor_raw_loadcell',
            'sensor_raw_mq5', 
            'sensor_raw_mq7',
            'sensor_raw_rfid',
            'sensor_raw_sound',
            'sensor_raw_tcrt5000',
            'sensor_raw_ultrasonic',
            'sensor_edge_flame',
            'sensor_edge_pir',
            'sensor_edge_reed',
            'sensor_edge_tilt'
        ]
        
        for table_name in sensor_tables:
            try:
                # 테이블 존재 여부 확인
                exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = $1)",
                    table_name
                )
                
                if exists:
                    # 컬럼 정보 조회
                    columns = await conn.fetch(
                        """
                        SELECT column_name, data_type, is_nullable, column_default
                        FROM information_schema.columns 
                        WHERE table_name = $1 
                        ORDER BY ordinal_position
                        """,
                        table_name
                    )
                    
                    print(f"\n📋 {table_name} 테이블:")
                    print("-" * 40)
                    for col in columns:
                        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                        default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                        print(f"  {col['column_name']:<20} {col['data_type']:<15} {nullable}{default}")
                else:
                    print(f"\n❌ {table_name} 테이블이 존재하지 않습니다.")
                    
            except Exception as e:
                print(f"\n❌ {table_name} 테이블 확인 중 오류: {e}")
        
        await conn.close()
        print("\n" + "=" * 60)
        print("🏁 데이터베이스 테이블 구조 확인 완료")
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(check_table_structure())


