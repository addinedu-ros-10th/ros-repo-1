#!/usr/bin/env python3
"""
테스트용 디바이스 생성 스크립트
통합 테스트를 위한 디바이스 데이터 생성
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from datetime import datetime

async def create_test_devices():
    """테스트용 디바이스 생성"""
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
        
        # 현재 devices 테이블 상태 확인
        current_count = await conn.fetchval("SELECT COUNT(*) FROM devices")
        print(f"현재 devices 테이블 레코드 수: {current_count}")
        
        # 기존 사용자 ID 가져오기
        existing_user_ids = await conn.fetch("SELECT user_id FROM users LIMIT 2")
        if not existing_user_ids:
            print("❌ 사용자가 존재하지 않습니다. 먼저 테스트용 사용자를 생성해주세요.")
            await conn.close()
            return
        
        user_id_1 = existing_user_ids[0]['user_id']
        user_id_2 = existing_user_ids[1]['user_id'] if len(existing_user_ids) > 1 else existing_user_ids[0]['user_id']
        
        print(f"사용할 사용자 ID: {user_id_1}, {user_id_2}")
        
        # 테스트용 디바이스 데이터 (실제 테이블 구조에 맞춤)
        test_devices = [
            {
                'device_id': 'test_device_001',
                'user_id': user_id_1,
                'location_label': 'Test Lab 001',
                'installed_at': datetime.now()
            },
            {
                'device_id': 'test_device_002', 
                'user_id': user_id_2,
                'location_label': 'Test Lab 002',
                'installed_at': datetime.now()
            },
            {
                'device_id': 'test_device_003',
                'user_id': user_id_1,
                'location_label': 'Test Lab 003',
                'installed_at': datetime.now()
            }
        ]
        
        # 테스트용 디바이스 생성
        created_count = 0
        for device in test_devices:
            try:
                # 디바이스가 이미 존재하는지 확인
                exists = await conn.fetchval(
                    "SELECT COUNT(*) FROM devices WHERE device_id = $1",
                    device['device_id']
                )
                
                if exists == 0:
                    await conn.execute("""
                        INSERT INTO devices (device_id, user_id, location_label, installed_at)
                        VALUES ($1, $2, $3, $4)
                    """, device['device_id'], device['user_id'], 
                         device['location_label'], device['installed_at'])
                    
                    print(f"✅ 디바이스 생성: {device['device_id']}")
                    created_count += 1
                else:
                    print(f"ℹ️ 디바이스 이미 존재: {device['device_id']}")
                    
            except Exception as e:
                print(f"❌ 디바이스 생성 실패 {device['device_id']}: {e}")
        
        # 최종 상태 확인
        final_count = await conn.fetchval("SELECT COUNT(*) FROM devices")
        print(f"\n📊 디바이스 생성 완료:")
        print(f"  - 새로 생성된 디바이스: {created_count}개")
        print(f"  - 전체 디바이스 수: {final_count}개")
        
        await conn.close()
        print("\n✅ 테스트용 디바이스 생성 완료")
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_devices()) 