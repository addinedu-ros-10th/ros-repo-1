#!/usr/bin/env python3
"""
키워드 인식 및 음성 지문 API 테스트 스크립트
"""
import requests
import json
import base64
import sys

API_BASE_URL = "http://localhost:8001"

def test_keyword_check():
    """키워드 확인 API 테스트"""
    print("\n" + "="*60)
    print("1. 키워드 확인 API 테스트")
    print("="*60)
    
    test_cases = [
        {
            "name": "정확한 키워드 매칭",
            "stt_result": "alfred",
            "base_keyword": "alfred",
            "expected": True
        },
        {
            "name": "키워드 포함",
            "stt_result": "hello alfred",
            "base_keyword": "alfred",
            "expected": True
        },
        {
            "name": "유사한 키워드 (오타)",
            "stt_result": "rarpred",
            "base_keyword": "alfred",
            "expected": True  # 유사도 70% 이상이면 인식
        },
        {
            "name": "완전히 다른 단어",
            "stt_result": "hello",
            "base_keyword": "alfred",
            "expected": False
        }
    ]
    
    results = []
    for test in test_cases:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/keyword/check",
                json={
                    "stt_result": test["stt_result"],
                    "base_keyword": test["base_keyword"],
                    "session_id": "test_session_123"
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                is_keyword = data.get("is_keyword", False)
                similarity = data.get("similarity", 0)
                matched = data.get("matched_keyword")
                
                status = "✅" if is_keyword == test["expected"] else "❌"
                print(f"{status} {test['name']}")
                print(f"   STT 결과: '{test['stt_result']}'")
                print(f"   키워드 인식: {is_keyword} (기대: {test['expected']})")
                print(f"   유사도: {similarity:.2%}")
                print(f"   매칭된 키워드: {matched}")
                
                results.append({
                    "test": test["name"],
                    "success": is_keyword == test["expected"],
                    "data": data
                })
            else:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                results.append({
                    "test": test["name"],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
        except requests.exceptions.ConnectionError:
            print(f"❌ {test['name']}: 서버에 연결할 수 없습니다.")
            print(f"   서버가 실행 중인지 확인하세요: {API_BASE_URL}")
            results.append({
                "test": test["name"],
                "success": False,
                "error": "Connection error"
            })
        except Exception as e:
            print(f"❌ {test['name']}: 오류 발생")
            print(f"   {str(e)}")
            results.append({
                "test": test["name"],
                "success": False,
                "error": str(e)
            })
        print()
    
    return results


def test_voiceprint_register():
    """음성 지문 등록 API 테스트"""
    print("\n" + "="*60)
    print("2. 음성 지문 등록 API 테스트")
    print("="*60)
    
    # 더미 오디오 데이터 (실제로는 Base64 인코딩된 오디오)
    dummy_audio = base64.b64encode(b"dummy audio data for testing").decode('utf-8')
    
    test_cases = [
        {
            "name": "신규 음성 지문 등록",
            "base_keyword": "alfred",
            "stt_keyword": "alfred",
            "audio_data": dummy_audio,
            "session_id": "test_session_123"
        },
        {
            "name": "오타 키워드 음성 지문 등록",
            "base_keyword": "alfred",
            "stt_keyword": "rarpred",
            "audio_data": dummy_audio,
            "session_id": "test_session_123"
        }
    ]
    
    results = []
    for test in test_cases:
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/keyword/voiceprint/register",
                json={
                    "base_keyword": test["base_keyword"],
                    "stt_keyword": test["stt_keyword"],
                    "audio_data": test["audio_data"],
                    "session_id": test["session_id"]
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                voiceprint_id = data.get("voiceprint_id")
                is_new = data.get("is_new", False)
                
                status = "✅" if success else "❌"
                print(f"{status} {test['name']}")
                print(f"   성공: {success}")
                print(f"   음성 지문 ID: {voiceprint_id}")
                print(f"   신규 등록: {is_new}")
                print(f"   메시지: {data.get('message', 'N/A')}")
                
                results.append({
                    "test": test["name"],
                    "success": success,
                    "voiceprint_id": voiceprint_id,
                    "data": data
                })
            elif response.status_code == 503:
                print(f"⚠️  {test['name']}: 데이터베이스가 초기화되지 않았습니다")
                print(f"   서버 로그를 확인하세요")
                results.append({
                    "test": test["name"],
                    "success": False,
                    "error": "Database not initialized"
                })
            else:
                print(f"❌ {test['name']}: HTTP {response.status_code}")
                print(f"   응답: {response.text}")
                results.append({
                    "test": test["name"],
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                })
        except requests.exceptions.ConnectionError:
            print(f"❌ {test['name']}: 서버에 연결할 수 없습니다.")
            print(f"   서버가 실행 중인지 확인하세요: {API_BASE_URL}")
            results.append({
                "test": test["name"],
                "success": False,
                "error": "Connection error"
            })
        except Exception as e:
            print(f"❌ {test['name']}: 오류 발생")
            print(f"   {str(e)}")
            results.append({
                "test": test["name"],
                "success": False,
                "error": str(e)
            })
        print()
    
    return results


def test_voiceprint_list():
    """음성 지문 조회 API 테스트"""
    print("\n" + "="*60)
    print("3. 음성 지문 조회 API 테스트")
    print("="*60)
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/keyword/voiceprint",
            params={
                "base_keyword": "alfred"
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            voiceprints = data.get("voiceprints", [])
            
            print(f"✅ 조회 성공")
            print(f"   등록된 음성 지문 개수: {len(voiceprints)}")
            
            if voiceprints:
                print("\n   등록된 음성 지문 목록:")
                for vp in voiceprints[:5]:  # 최대 5개만 표시
                    print(f"   - ID: {vp.get('id')}")
                    print(f"     기준 키워드: {vp.get('base_keyword')}")
                    print(f"     STT 키워드: {vp.get('stt_keyword')}")
                    print(f"     세션 ID: {vp.get('session_id')}")
                    print(f"     생성일: {vp.get('created_at')}")
                    print(f"     활성화: {vp.get('is_active')}")
                    print()
            else:
                print("   등록된 음성 지문이 없습니다.")
            
            return {
                "success": success,
                "count": len(voiceprints),
                "voiceprints": voiceprints
            }
        else:
            print(f"❌ HTTP {response.status_code}")
            print(f"   응답: {response.text}")
            return {
                "success": False,
                "error": f"HTTP {response.status_code}"
            }
    except requests.exceptions.ConnectionError:
        print(f"❌ 서버에 연결할 수 없습니다.")
        print(f"   서버가 실행 중인지 확인하세요: {API_BASE_URL}")
        return {
            "success": False,
            "error": "Connection error"
        }
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("키워드 인식 및 음성 지문 API 테스트")
    print("="*60)
    print(f"API 서버: {API_BASE_URL}")
    print(f"서버가 실행 중인지 확인 후 테스트를 진행하세요.")
    print()
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{API_BASE_URL}/docs", timeout=2)
        print("✅ 서버 연결 확인됨")
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다.")
        print(f"   서버를 먼저 실행하세요: cd AI/llm-gateway && python -m uvicorn src.main:app --reload")
        sys.exit(1)
    except Exception as e:
        print(f"⚠️  서버 연결 확인 실패: {str(e)}")
        print("   계속 진행합니다...")
    
    # 테스트 실행
    keyword_results = test_keyword_check()
    voiceprint_register_results = test_voiceprint_register()
    voiceprint_list_result = test_voiceprint_list()
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    keyword_success = sum(1 for r in keyword_results if r.get("success", False))
    print(f"키워드 확인: {keyword_success}/{len(keyword_results)} 성공")
    
    voiceprint_success = sum(1 for r in voiceprint_register_results if r.get("success", False))
    print(f"음성 지문 등록: {voiceprint_success}/{len(voiceprint_register_results)} 성공")
    
    if voiceprint_list_result.get("success"):
        print(f"음성 지문 조회: ✅ 성공 ({voiceprint_list_result.get('count', 0)}개 등록됨)")
    else:
        print(f"음성 지문 조회: ❌ 실패")
    
    print("\n" + "="*60)
    print("테스트 완료")
    print("="*60)


if __name__ == "__main__":
    main()

