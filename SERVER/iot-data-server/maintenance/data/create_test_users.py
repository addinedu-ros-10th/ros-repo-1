#!/usr/bin/env python3
"""
테스트용 사용자 생성 스크립트
통합 테스트를 위한 사용자 데이터 생성
"""
import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

async def create_test_users():
    """테스트용 사용자 생성"""
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
        
        # 현재 users 테이블 상태 확인
        current_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"현재 users 테이블 레코드 수: {current_count}")
        
        # 테스트용 사용자 데이터
        test_users = [
            {
                'user_id': str(uuid.uuid4()),
                'user_role': 'admin',
                'user_name': 'Test Admin User',
                'email': 'admin@test.com',
                'phone_number': '+82-10-1234-5678',
                'created_at': datetime.now()
            },
            {
                'user_id': str(uuid.uuid4()),
                'user_role': 'user',
                'user_name': 'Test Regular User',
                'email': 'user@test.com',
                'phone_number': '+82-10-8765-4321',
                'created_at': datetime.now()
            }
        ]
        
        # 테스트용 사용자 생성
        created_count = 0
        created_user_ids = []
        for user in test_users:
            try:
                await conn.execute("""
                    INSERT INTO users (user_id, user_role, user_name, email, phone_number, created_at)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """, user['user_id'], user['user_role'], user['user_name'], 
                     user['email'], user['phone_number'], user['created_at'])
                
                print(f"✅ 사용자 생성: {user['user_name']} ({user['user_role']})")
                created_count += 1
                created_user_ids.append(user['user_id'])
                    
            except Exception as e:
                print(f"❌ 사용자 생성 실패 {user['user_name']}: {e}")
        
        # 최종 상태 확인
        final_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        print(f"\n📊 사용자 생성 완료:")
        print(f"  - 새로 생성된 사용자: {created_count}개")
        print(f"  - 전체 사용자 수: {final_count}개")
        
        if created_user_ids:
            print(f"  - 생성된 사용자 ID:")
            for user_id in created_user_ids:
                print(f"    {user_id}")
        
        await conn.close()
        print("\n✅ 테스트용 사용자 생성 완료")
        
    except Exception as e:
        print(f"❌ DB 연결 실패: {e}")

if __name__ == "__main__":
    asyncio.run(create_test_users())
