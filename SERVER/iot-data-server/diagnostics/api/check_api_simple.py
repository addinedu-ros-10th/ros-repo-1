#!/usr/bin/env python3
"""
간단한 API 서버 상태 확인 스크립트 (requests 모듈 없이)
"""

import urllib.request
import urllib.error
import json
from datetime import datetime

def check_api_status():
    """API 서버 상태 확인"""
    
    print("🔍 API 서버 상태 확인 시작...")
    
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
        ("/openapi.json", "OpenAPI 스키마")
    ]
    
    for endpoint, description in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 {description} 테스트: {url}")
            
            # HTTP 요청
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                content = response.read().decode('utf-8')
                headers = dict(response.getheaders())
                
                print(f"   상태 코드: {status_code}")
                print(f"   Content-Type: {headers.get('content-type', 'N/A')}")
                
                if status_code == 200:
                    if endpoint == "/docs":
                        # Swagger UI HTML 내용 확인
                        if "swagger-ui" in content.lower():
                            print("   ✅ Swagger UI HTML 로드 성공")
                        else:
                            print("   ⚠️  Swagger UI HTML에 swagger-ui 키워드 없음")
                            print(f"   📄 응답 내용 일부: {content[:200]}...")
                    elif endpoint == "/openapi.json":
                        # OpenAPI 스키마 JSON 확인
                        try:
                            schema = json.loads(content)
                            print(f"   ✅ OpenAPI 스키마 로드 성공")
                            print(f"   📊 API 경로 수: {len(schema.get('paths', {}))}")
                        except json.JSONDecodeError:
                            print("   ❌ JSON 파싱 실패")
                    else:
                        print(f"   ✅ {description} 응답 성공")
                        if len(content) < 100:
                            print(f"   📄 응답 내용: {content}")
                else:
                    print(f"   ❌ {description} 응답 실패")
                    print(f"   📄 응답 내용: {content[:200]}...")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP 오류: {e.code} - {e.reason}")
            try:
                error_content = e.read().decode('utf-8')
                print(f"   📄 오류 내용: {error_content[:200]}...")
            except:
                pass
        except urllib.error.URLError as e:
            print(f"   ❌ URL 오류: {e.reason}")
        except Exception as e:
            print(f"   ❌ {description} 테스트 실패: {e}")
    
    # 2. 사용자 API 테스트
    print(f"\n{'='*60}")
    print("👥 사용자 API 테스트")
    print(f"{'='*60}")
    
    user_endpoints = [
        ("/api/users/list?page=1&size=10", "사용자 목록 조회"),
        ("/api/users/1", "사용자 상세 조회")
    ]
    
    for endpoint, description in user_endpoints:
        try:
            url = f"{base_url}{endpoint}"
            print(f"\n🔍 {description} 테스트: {url}")
            
            # HTTP GET 요청
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            req.add_header('Accept', 'application/json')
            
            with urllib.request.urlopen(req, timeout=10) as response:
                status_code = response.getcode()
                content = response.read().decode('utf-8')
                headers = dict(response.getheaders())
                
                print(f"   상태 코드: {status_code}")
                print(f"   Content-Type: {headers.get('content-type', 'N/A')}")
                
                if status_code == 200:
                    print(f"   ✅ {description} 성공")
                    try:
                        data = json.loads(content)
                        if isinstance(data, list):
                            print(f"   📊 응답 데이터: {len(data)}개 항목")
                        elif isinstance(data, dict):
                            print(f"   📊 응답 데이터: {list(data.keys())}")
                    except:
                        print(f"   📄 응답 내용: {content[:200]}...")
                else:
                    print(f"   ❌ {description} 실패")
                    print(f"   📄 응답 내용: {content[:200]}...")
                    
        except urllib.error.HTTPError as e:
            print(f"   ❌ HTTP 오류: {e.code} - {e.reason}")
            try:
                error_content = e.read().decode('utf-8')
                print(f"   📄 오류 내용: {error_content[:200]}...")
            except:
                pass
        except urllib.error.URLError as e:
            print(f"   ❌ URL 오류: {e.reason}")
        except Exception as e:
            print(f"   ❌ {description} 테스트 실패: {e}")
    
    print(f"\n{'='*60}")
    print("✅ API 서버 상태 확인 완료!")
    print(f"{'='*60}")

if __name__ == "__main__":
    check_api_status()
