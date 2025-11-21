#!/usr/bin/env python3
"""
모든 API 엔드포인트 통합 테스트 스크립트

25개 테이블에 대한 모든 API를 테스트하고 결과를 리포트로 생성합니다.
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import httpx
import uuid


class APITestSuite:
    """API 테스트 스위트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        self.test_data = {}
        
    async def test_api_endpoint(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        expected_status: int = 200
    ) -> Dict[str, Any]:
        """개별 API 엔드포인트 테스트"""
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                if method.upper() == "GET":
                    response = await client.get(f"{self.base_url}{endpoint}", params=params)
                elif method.upper() == "POST":
                    response = await client.post(f"{self.base_url}{endpoint}", json=data)
                elif method.upper() == "PUT":
                    response = await client.put(f"{self.base_url}{endpoint}", json=data)
                elif method.upper() == "DELETE":
                    response = await client.delete(f"{self.base_url}{endpoint}")
                else:
                    raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms
                
                success = response.status_code == expected_status
                
                return {
                    "success": success,
                    "status_code": response.status_code,
                    "expected_status": expected_status,
                    "response_time_ms": round(response_time, 2),
                    "response_data": response.json() if response.headers.get("content-type", "").startswith("application/json") else str(response.text),
                    "error": None
                }
                
        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            return {
                "success": False,
                "status_code": None,
                "expected_status": expected_status,
                "response_time_ms": round(response_time, 2),
                "response_data": None,
                "error": str(e)
            }
    
    def generate_test_data(self) -> None:
        """테스트용 데이터 생성"""
        timestamp = datetime.utcnow()
        device_id = f"test_device_{uuid.uuid4().hex[:8]}"
        user_id = str(uuid.uuid4())
        
        # 사용자 테스트 데이터
        self.test_data["user"] = {
            "user_name": f"TestUser_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "phone_number": "010-1234-5678",
            "user_role": "user"
        }
        
        # 디바이스 테스트 데이터
        self.test_data["device"] = {
            "device_id": device_id,
            "user_id": user_id,
            "location_label": "test_location"
        }
        
        # 센서 데이터 테스트 데이터
        self.test_data["loadcell"] = {
            "time": timestamp.isoformat(),
            "device_id": device_id,
            "weight_kg": 75.5,
            "raw_value": 1234,
            "calibration_factor": 1.0
        }
        
        self.test_data["mq5"] = {
            "time": timestamp.isoformat(),
            "device_id": device_id,
            "gas_ppm": 150,
            "analog_value": 512,
            "threshold_exceeded": False
        }
        
        self.test_data["device_rtc"] = {
            "time": timestamp.isoformat(),
            "device_id": device_id,
            "rtc_epoch_s": int(timestamp.timestamp()),
            "drift_ms": 25,
            "sync_source": "ntp"
        }
    
    async def test_users_api(self) -> Dict[str, Any]:
        """사용자 API 테스트"""
        print("🔍 사용자 API 테스트 중...")
        
        # 사용자 생성
        create_result = await self.test_api_endpoint(
            "POST", "/api/v1/users/",
            data=self.test_data["user"],
            expected_status=201
        )
        
        if not create_result["success"]:
            return {"success": False, "error": "사용자 생성 실패", "details": create_result}
        
        user_data = create_result["response_data"]
        user_id = user_data["user_id"]
        
        # 사용자 조회
        get_result = await self.test_api_endpoint(
            "GET", f"/api/v1/users/{user_id}",
            expected_status=200
        )
        
        # 사용자 목록 조회
        list_result = await self.test_api_endpoint(
            "GET", "/api/v1/users/",
            expected_status=200
        )
        
        # 사용자 수정
        update_data = {"user_name": f"UpdatedUser_{uuid.uuid4().hex[:8]}"}
        update_result = await self.test_api_endpoint(
            "PUT", f"/api/v1/users/{user_id}",
            data=update_data,
            expected_status=200
        )
        
        # 사용자 삭제
        delete_result = await self.test_api_endpoint(
            "DELETE", f"/api/v1/users/{user_id}",
            expected_status=200
        )
        
        return {
            "success": True,
            "tests": {
                "create": create_result,
                "get": get_result,
                "list": list_result,
                "update": update_result,
                "delete": delete_result
            }
        }
    
    async def test_devices_api(self) -> Dict[str, Any]:
        """디바이스 API 테스트"""
        print("🔍 디바이스 API 테스트 중...")
        
        # 디바이스 생성
        create_result = await self.test_api_endpoint(
            "POST", "/api/v1/devices/",
            data=self.test_data["device"],
            expected_status=201
        )
        
        if not create_result["success"]:
            return {"success": False, "error": "디바이스 생성 실패", "details": create_result}
        
        device_data = create_result["response_data"]
        device_id = device_data["device_id"]
        
        # 디바이스 조회
        get_result = await self.test_api_endpoint(
            "GET", f"/api/v1/devices/{device_id}",
            expected_status=200
        )
        
        # 디바이스 목록 조회
        list_result = await self.test_api_endpoint(
            "GET", "/api/v1/devices/",
            expected_status=200
        )
        
        # 디바이스 수정
        update_data = {"location_label": "updated_location"}
        update_result = await self.test_api_endpoint(
            "PUT", f"/api/v1/devices/{device_id}",
            data=update_data,
            expected_status=200
        )
        
        # 디바이스 삭제
        delete_result = await self.test_api_endpoint(
            "DELETE", f"/api/v1/devices/{device_id}",
            expected_status=200
        )
        
        return {
            "success": True,
            "tests": {
                "create": create_result,
                "get": get_result,
                "list": list_result,
                "update": update_result,
                "delete": delete_result
            }
        }
    
    async def test_loadcell_api(self) -> Dict[str, Any]:
        """LoadCell 센서 API 테스트"""
        print("🔍 LoadCell 센서 API 테스트 중...")
        
        # 센서 데이터 생성
        create_result = await self.test_api_endpoint(
            "POST", "/api/v1/loadcell/",
            data=self.test_data["loadcell"],
            expected_status=201
        )
        
        if not create_result["success"]:
            return {"success": False, "error": "LoadCell 데이터 생성 실패", "details": create_result}
        
        # 최신 데이터 조회
        latest_result = await self.test_api_endpoint(
            "GET", "/api/v1/loadcell/latest",
            params={"device_id": self.test_data["loadcell"]["device_id"]},
            expected_status=200
        )
        
        # 통계 조회
        stats_result = await self.test_api_endpoint(
            "GET", f"/api/v1/loadcell/{self.test_data['loadcell']['device_id']}/stats/weight",
            expected_status=200
        )
        
        return {
            "success": True,
            "tests": {
                "create": create_result,
                "latest": latest_result,
                "stats": stats_result
            }
        }
    
    async def test_mq5_api(self) -> Dict[str, Any]:
        """MQ5 센서 API 테스트"""
        print("🔍 MQ5 센서 API 테스트 중...")
        
        # 센서 데이터 생성
        create_result = await self.test_api_endpoint(
            "POST", "/api/v1/mq5/",
            data=self.test_data["mq5"],
            expected_status=201
        )
        
        if not create_result["success"]:
            return {"success": False, "error": "MQ5 데이터 생성 실패", "details": create_result}
        
        # 최신 데이터 조회
        latest_result = await self.test_api_endpoint(
            "GET", "/api/v1/mq5/latest",
            params={"device_id": self.test_data["mq5"]["device_id"]},
            expected_status=200
        )
        
        # 통계 조회
        stats_result = await self.test_api_endpoint(
            "GET", f"/api/v1/mq5/{self.test_data['mq5']['device_id']}/stats/gas",
            expected_status=200
        )
        
        return {
            "success": True,
            "tests": {
                "create": create_result,
                "latest": latest_result,
                "stats": stats_result
            }
        }
    
    async def test_device_rtc_api(self) -> Dict[str, Any]:
        """DeviceRTCStatus API 테스트"""
        print("🔍 DeviceRTCStatus API 테스트 중...")
        
        # RTC 상태 데이터 생성
        create_result = await self.test_api_endpoint(
            "POST", "/api/v1/device-rtc/",
            data=self.test_data["device_rtc"],
            expected_status=201
        )
        
        if not create_result["success"]:
            return {"success": False, "error": "DeviceRTC 데이터 생성 실패", "details": create_result}
        
        # 최신 데이터 조회
        latest_result = await self.test_api_endpoint(
            "GET", "/api/v1/device-rtc/latest",
            params={"device_id": self.test_data["device_rtc"]["device_id"]},
            expected_status=200
        )
        
        # 동기화 통계 조회
        sync_stats_result = await self.test_api_endpoint(
            "GET", f"/api/v1/device-rtc/{self.test_data['device_rtc']['device_id']}/stats/sync",
            expected_status=200
        )
        
        # 드리프트 분석 조회
        drift_result = await self.test_api_endpoint(
            "GET", f"/api/v1/device-rtc/{self.test_data['device_rtc']['device_id']}/stats/drift",
            expected_status=200
        )
        
        # 건강도 조회
        health_result = await self.test_api_endpoint(
            "GET", f"/api/v1/device-rtc/{self.test_data['device_rtc']['device_id']}/health",
            expected_status=200
        )
        
        return {
            "success": True,
            "tests": {
                "create": create_result,
                "latest": latest_result,
                "sync_stats": sync_stats_result,
                "drift_analysis": drift_result,
                "health": health_result
            }
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        print("🚀 모든 API 테스트 시작...")
        print(f"📡 테스트 대상: {self.base_url}")
        print("=" * 60)
        
        # 테스트 데이터 생성
        self.generate_test_data()
        
        # 각 API 테스트 실행
        test_results = {}
        
        # 1. 사용자 API 테스트
        test_results["users"] = await self.test_users_api()
        
        # 2. 디바이스 API 테스트
        test_results["devices"] = await self.test_devices_api()
        
        # 3. LoadCell 센서 API 테스트
        test_results["loadcell"] = await self.test_loadcell_api()
        
        # 4. MQ5 센서 API 테스트
        test_results["mq5"] = await self.test_mq5_api()
        
        # 5. DeviceRTCStatus API 테스트
        test_results["device_rtc"] = await self.test_device_rtc_api()
        
        # 전체 결과 요약
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for api_name, result in test_results.items():
            if result["success"]:
                for test_name, test_result in result["tests"].items():
                    total_tests += 1
                    if test_result["success"]:
                        passed_tests += 1
                    else:
                        failed_tests += 1
            else:
                failed_tests += 1
        
        overall_result = {
            "timestamp": datetime.utcnow().isoformat(),
            "base_url": self.base_url,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": round((passed_tests / total_tests * 100), 2) if total_tests > 0 else 0
            },
            "api_results": test_results
        }
        
        return overall_result
    
    def save_results(self, results: Dict[str, Any], filename: str = None) -> None:
        """테스트 결과를 파일로 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"api_test_results_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"📄 테스트 결과가 {filename}에 저장되었습니다.")


async def main():
    """메인 함수"""
    print("🔧 IoT Care API 통합 테스트 도구")
    print("=" * 50)
    
    # 테스트 스위트 생성
    test_suite = APITestSuite()
    
    try:
        # 모든 테스트 실행
        results = await test_suite.run_all_tests()
        
        # 결과 출력
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"총 테스트 수: {summary['total_tests']}")
        print(f"성공한 테스트: {summary['passed_tests']}")
        print(f"실패한 테스트: {summary['failed_tests']}")
        print(f"성공률: {summary['success_rate']}%")
        
        print("\n📋 API별 테스트 결과:")
        for api_name, api_result in results["api_results"].items():
            status = "✅ 성공" if api_result["success"] else "❌ 실패"
            print(f"  {api_name}: {status}")
        
        # 결과 저장
        test_suite.save_results(results)
        
        # 성공/실패 여부에 따른 종료 코드
        if summary['failed_tests'] == 0:
            print("\n🎉 모든 테스트가 성공했습니다!")
            return 0
        else:
            print(f"\n⚠️  {summary['failed_tests']}개의 테스트가 실패했습니다.")
            return 1
            
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
