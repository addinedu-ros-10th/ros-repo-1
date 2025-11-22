#!/usr/bin/env python3
"""
API 상태 확인 스크립트
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_api_status():
    """API 상태를 테스트합니다."""
    base_url = "http://localhost"
    
    print(f"🔍 API 상태 확인 시작 - {datetime.now()}")
    print(f"📍 대상 URL: {base_url}")
    print("=" * 60)
    
    # 1. 헬스 체크
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            print(f"✅ 헬스 체크: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 헬스 체크 실패: {e}")
        return
    
    # 2. Swagger UI 확인
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/docs")
            print(f"✅ Swagger UI: {response.status_code}")
    except Exception as e:
        print(f"❌ Swagger UI 확인 실패: {e}")
    
    # 3. Users API 테스트
    print("\n👥 Users API 테스트:")
    
    # GET 요청
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/users/list")
            print(f"  GET /api/users/list: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"  ❌ GET 요청 실패: {e}")
    
    # POST 요청
    test_user_data = {
        "user_name": "test_user_api",
        "email": "test_api@example.com",
        "phone_number": "01012345678",
        "user_role": "user"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/users/create",
                json=test_user_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"  POST /api/users/create: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"    응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"    오류 응답: {response.text}")
    except Exception as e:
        print(f"  ❌ POST 요청 실패: {e}")
    
    # 4. CDS API 테스트
    print("\n📡 CDS API 테스트:")
    
    # GET 요청
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/api/cds/list")
            print(f"  GET /api/cds/list: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"    응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"  ❌ GET 요청 실패: {e}")
    
    # POST 요청
    test_cds_data = {
        "time": datetime.now().isoformat(),
        "device_id": "test_device_001",
        "analog_value": 512,
        "lux_value": 100.5,
        "raw_payload": {"test": "data"}
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/api/cds/create",
                json=test_cds_data,
                headers={"Content-Type": "application/json"}
            )
            print(f"  POST /api/cds/create: {response.status_code}")
            if response.status_code in [200, 201]:
                data = response.json()
                print(f"    응답 데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
            else:
                print(f"    오류 응답: {response.text}")
    except Exception as e:
        print(f"  ❌ POST 요청 실패: {e}")
    
    print("\n" + "=" * 60)
    print("🏁 API 상태 확인 완료")

if __name__ == "__main__":
    asyncio.run(test_api_status())


