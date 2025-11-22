"""
ROS2 API Server 통합 테스트
"""
import httpx
import asyncio
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8003"


async def test_health_check():
    """헬스 체크 테스트"""
    print("=== 헬스 체크 테스트 ===")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"상태 코드: {response.status_code}")
            data = response.json()
            print(f"응답: {json.dumps(data, indent=2, ensure_ascii=False)}")
            assert response.status_code == 200
            print("✅ 헬스 체크 통과\n")
            return True
        except Exception as e:
            print(f"❌ 헬스 체크 실패: {e}\n")
            return False


async def test_detection_resident():
    """어르신 탐지 API 테스트"""
    print("=== 어르신 탐지 API 테스트 ===")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            data = {
                "nickname": "Akaza",
                "detection_location": "1층 복도",
                "detection_confidence": 0.95,
                "camera_id": "camera_001",
                "display_format": "basic"
            }
            response = await client.post(
                f"{BASE_URL}/api/detection/resident",
                json=data
            )
            print(f"상태 코드: {response.status_code}")
            result = response.json()
            print(f"응답: {json.dumps(result, indent=2, ensure_ascii=False)}")
            assert response.status_code == 200
            assert result.get("success") is True
            print("✅ 어르신 탐지 API 통과\n")
            return True
        except Exception as e:
            print(f"❌ 어르신 탐지 API 실패: {e}\n")
            return False


async def test_scenario_template(scenario: str, additional_data: Dict[str, Any]):
    """시나리오 템플릿 테스트"""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            data = {
                "scenario": scenario,
                "nickname": "Akaza",
                "additional_data": additional_data
            }
            response = await client.post(
                f"{BASE_URL}/api/templates/scenario",
                json=data
            )
            print(f"  상태 코드: {response.status_code}")
            result = response.json()
            print(f"  타이틀: {result.get('template', {}).get('title', 'N/A')}")
            print(f"  라인 수: {len(result.get('template', {}).get('lines', []))}")
            assert response.status_code == 200
            assert result.get("success") is not False
            return True
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            return False


async def test_all_scenarios():
    """모든 시나리오 템플릿 테스트"""
    print("=== 시나리오 템플릿 테스트 ===")
    
    scenarios = [
        {
            "scenario": "morning_greeting",
            "additional_data": {"weather": "맑은"}
        },
        {
            "scenario": "meal_assistance",
            "additional_data": {"menu": "된장찌개", "meal_time": "12:00"}
        },
        {
            "scenario": "conversation",
            "additional_data": {
                "topic": "오늘 날씨 이야기",
                "destination": "3층 302호 생활실"
            }
        },
        {
            "scenario": "wandering_detection",
            "additional_data": {"location": "1층 복도", "camera_id": "camera_001"}
        },
        {
            "scenario": "visitor_guidance",
            "additional_data": {
                "visitor_name": "정기우",
                "visitor_relationship": "아들",
                "meeting_room": "면회실"
            }
        }
    ]
    
    results = []
    for scenario_data in scenarios:
        scenario_name = scenario_data["scenario"]
        print(f"\n{scenario_name} 테스트 중...")
        success = await test_scenario_template(
            scenario_data["scenario"],
            scenario_data["additional_data"]
        )
        results.append((scenario_name, success))
    
    print("\n=== 시나리오 테스트 결과 ===")
    for name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    return all_passed


async def test_error_cases():
    """에러 케이스 테스트"""
    print("\n=== 에러 케이스 테스트 ===")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. user_id와 nickname 모두 없는 경우
        print("1. user_id와 nickname 모두 없는 경우 테스트...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/detection/resident",
                json={
                    "detection_location": "1층 복도",
                    "detection_confidence": 0.95,
                    "camera_id": "camera_001"
                }
            )
            assert response.status_code == 400
            print("  ✅ 올바른 에러 응답 (400)")
        except Exception as e:
            print(f"  ❌ 실패: {e}")
        
        # 2. 존재하지 않는 어르신
        print("2. 존재하지 않는 어르신 테스트...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/detection/resident",
                json={
                    "nickname": "존재하지않는어르신",
                    "detection_location": "1층 복도",
                    "detection_confidence": 0.95,
                    "camera_id": "camera_001"
                }
            )
            # 404 또는 500 가능
            assert response.status_code in [404, 500]
            print(f"  ✅ 올바른 에러 응답 ({response.status_code})")
        except Exception as e:
            print(f"  ❌ 실패: {e}")
        
        # 3. 알 수 없는 시나리오
        print("3. 알 수 없는 시나리오 테스트...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/templates/scenario",
                json={
                    "scenario": "unknown_scenario",
                    "nickname": "Akaza"
                }
            )
            assert response.status_code == 400
            print("  ✅ 올바른 에러 응답 (400)")
        except Exception as e:
            print(f"  ❌ 실패: {e}")


async def main():
    """모든 테스트 실행"""
    print("=" * 50)
    print("ROS2 API Server 통합 테스트")
    print("=" * 50)
    print(f"테스트 대상: {BASE_URL}\n")
    
    results = []
    
    # 헬스 체크
    health_ok = await test_health_check()
    results.append(("헬스 체크", health_ok))
    
    if not health_ok:
        print("⚠️  서버가 실행 중이지 않습니다. 서버를 먼저 실행해주세요.")
        print("   docker-compose up -d")
        return
    
    # 어르신 탐지 API
    detection_ok = await test_detection_resident()
    results.append(("어르신 탐지 API", detection_ok))
    
    # 시나리오 템플릿
    scenarios_ok = await test_all_scenarios()
    results.append(("시나리오 템플릿", scenarios_ok))
    
    # 에러 케이스
    await test_error_cases()
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    for name, success in results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 모든 테스트 통과!")
    else:
        print("❌ 일부 테스트 실패")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())

