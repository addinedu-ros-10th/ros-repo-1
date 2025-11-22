#!/usr/bin/env python3
"""
API 서버 로그 확인 및 문제 진단 스크립트
"""

import os
import requests
import json
from datetime import datetime

def check_api_status():
    """API 서버 상태 및 로그 확인"""
    
    print("🔍 API 서버 상태 및 로그 확인 시작...")
    
    # AWS EC2 URL
    base_url = "http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com"
    
    print(f"\n📋 테스트 대상: {base_url}")
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 기본 엔드포인트 테스트
    print(f"\n{'='*60}")
    print("🌐 기본 엔드포인트 테스트")
    print(f"{'='*60}")
    
    endpoints = [
        ("/", "루트"),
        ("/health", "헬스체크"),
        ("/docs", "Swagger UI"),
        ("/redoc", "ReDoc"),
        ("/openapi.json", "OpenAPI 스키마")
    ]
    
    for endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 {description} 테스트: {url}")
            
            response = requests.get(url, timeout=10)
            print(f"   상태 코드: {response.status_code}")
            print(f"   응답 헤더: {dict(response.headers)}")
            
            if response.status_code == 200:
                if endpoint == "/docs":
                    # Swagger UI HTML 내용 확인
                    content = response.text
                    if "swagger-ui" in content.lower():
                        print("   ✅ Swagger UI HTML 로드 성공")
                    else:
                        print("   ⚠️  Swagger UI HTML에 swagger-ui 키워드 없음")
                        print(f"   📄 응답 내용 일부: {content[:200]}...")
                elif endpoint == "/openapi.json":
                    # OpenAPI 스키마 JSON 확인
                    try:
                        schema = response.json()
                        print(f"   ✅ OpenAPI 스키마 로드 성공")
                        print(f"   📊 API 경로 수: {len(schema.get('paths', {}))}")
                    except json.JSONDecodeError:
                        print("   ❌ JSON 파싱 실패")
                else:
                    print(f"   ✅ {description} 응답 성공")
                    if len(response.text) < 100:
                        print(f"   📄 응답 내용: {response.text}")
            else:
                print(f"   ❌ {description} 응답 실패")
                print(f"   📄 응답 내용: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ {description} 테스트 실패: {e}")
    
    # 2. 사용자 API 테스트
    print(f"\n{'='*60}")
    print("👥 사용자 API 테스트")
    print(f"{'='*60}")
    
    user_endpoints = [
        ("/api/users/list?page=1&size=10", "사용자 목록 조회"),
        ("/api/users/1", "사용자 상세 조회"),
        ("/api/users", "사용자 생성 (POST)")
    ]
    
    for endpoint, description in user_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 {description} 테스트: {url}")
            
            if "POST" in description:
                # POST 요청 테스트
                test_data = {
                    "user_name": "test_user",
                    "email": "test@example.com",
                    "phone_number": "010-1234-5678",
                    "user_role": "user"
                }
                response = requests.post(url, json=test_data, timeout=10)
            else:
                # GET 요청 테스트
                response = requests.get(url, timeout=10)
            
            print(f"   상태 코드: {response.status_code}")
            print(f"   응답 헤더: {dict(response.headers)}")
            
            if response.status_code == 200:
                print(f"   ✅ {description} 성공")
                try:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"   📊 응답 데이터: {len(data)}개 항목")
                    elif isinstance(data, dict):
                        print(f"   📊 응답 데이터: {list(data.keys())}")
                except:
                    print(f"   📄 응답 내용: {response.text[:200]}...")
            elif response.status_code == 422:
                print(f"   ⚠️  {description} - 유효성 검사 실패 (예상됨)")
                print(f"   📄 오류 내용: {response.text[:200]}...")
            else:
                print(f"   ❌ {description} 실패")
                print(f"   📄 응답 내용: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ {description} 테스트 실패: {e}")
    
    # 3. CORS 및 헤더 테스트
    print(f"\n{'='*60}")
    print("🌐 CORS 및 헤더 테스트")
    print(f"{'='*60}")
    
    try:
        # OPTIONS 요청으로 CORS 확인
        url = f"{base_url}/api/users/list"
        response = requests.options(url, timeout=10)
        print(f"\n🔍 CORS OPTIONS 테스트: {url}")
        print(f"   상태 코드: {response.status_code}")
        print(f"   CORS 헤더: {dict(response.headers)}")
        
        # User-Agent 헤더 테스트
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8'
        }
        
        response = requests.get(f"{base_url}/api/users/list?page=1&size=10", 
                              headers=headers, timeout=10)
        print(f"\n🔍 커스텀 헤더 테스트")
        print(f"   상태 코드: {response.status_code}")
        print(f"   응답 헤더: {dict(response.headers)}")
        
    except Exception as e:
        print(f"   ❌ CORS/헤더 테스트 실패: {e}")
    
    print(f"\n{'='*60}")
    print("✅ API 서버 상태 확인 완료!")
    print(f"{'='*60}")

if __name__ == "__main__":
    check_api_status()
