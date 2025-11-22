# 배회 탐지 안내 기능 테스트 가이드

## 개요
어르신 배회 탐지 시 생활관 복귀 안내 기능을 테스트하는 방법을 안내합니다.

---

## 1. 테스트 API 확인

### ✅ 생성된 테스트 API

**엔드포인트**: `POST /api/test/wandering-detection`

**요청 형식**:
```json
{
    "resident_name": "정도현",           // 선택사항: 어르신 성함
    "nickname": "Akaza",                 // 선택사항: 어르신 nickname
    "detection_location": "1층 복도"      // 선택사항: 탐지 위치 (기본값: "복도")
}
```

**응답 형식**:
```json
{
    "success": true,
    "message": "배회 탐지 시뮬레이션 완료",
    "detection_info": {
        "resident_name": "정도현",
        "nickname": "Akaza",
        "detection_location": "1층 복도",
        "detected_at": "2025-01-22T10:30:00.000000"
    },
    "guidance_result": {
        "success": true,
        "resident_found": true,
        "resident_info": { ... },
        "guidance_messages": [
            "안녕하세요, 정도현 어르신! ...",
            "정도현 어르신, 생활실로 안내해드리겠습니다. ...",
            "정도현 어르신, 생활실로 가시면 됩니다. ..."
        ]
    }
}
```

---

## 2. 테스트 방법

### 방법 1: cURL을 사용한 API 테스트 (권장)

#### 서버 실행
```bash
cd AI/llm-gateway
docker compose up -d
# 또는
python -m uvicorn src.main:app --reload
```

#### 테스트 1: nickname으로 탐지
```bash
curl -X POST "http://localhost:8000/api/test/wandering-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도"
  }'
```

#### 테스트 2: 성함으로 탐지
```bash
curl -X POST "http://localhost:8000/api/test/wandering-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "resident_name": "정도현",
    "detection_location": "2층 로비"
  }'
```

#### 테스트 3: nickname과 성함 모두 제공
```bash
curl -X POST "http://localhost:8000/api/test/wandering-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "resident_name": "정도현",
    "nickname": "Akaza",
    "detection_location": "3층 계단"
  }'
```

#### 테스트 4: 존재하지 않는 어르신
```bash
curl -X POST "http://localhost:8000/api/test/wandering-detection" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "존재하지않는닉네임",
    "detection_location": "1층 복도"
  }'
```

### 방법 2: Postman 또는 HTTP 클라이언트 사용

1. **URL**: `POST http://localhost:8000/api/test/wandering-detection`
2. **Headers**: `Content-Type: application/json`
3. **Body** (JSON):
   ```json
   {
       "nickname": "Akaza",
       "detection_location": "1층 복도"
   }
   ```
4. **응답 확인**:
   - `success: true` 확인
   - `guidance_result.guidance_messages` 배열에 3개 이상의 안내 메시지 확인
   - `guidance_result.resident_info`에 어르신 정보 확인

### 방법 3: Python 스크립트로 테스트

```python
import requests
import json

# 테스트 API 호출
url = "http://localhost:8000/api/test/wandering-detection"
payload = {
    "nickname": "Akaza",
    "detection_location": "1층 복도"
}

response = requests.post(url, json=payload)
result = response.json()

print("=== 배회 탐지 테스트 결과 ===")
print(f"성공 여부: {result['success']}")
print(f"\n탐지 정보:")
print(f"  - 닉네임: {result['detection_info']['nickname']}")
print(f"  - 위치: {result['detection_info']['detection_location']}")
print(f"\n안내 메시지:")
for i, msg in enumerate(result['guidance_result']['guidance_messages'], 1):
    print(f"  {i}. {msg}")
```

---

## 3. 음성 인터페이스를 통한 테스트

### 개요
음성 인터페이스를 통해 배회 탐지 안내 기능을 테스트하려면, 음성으로 배회 탐지 상황을 설명하면 LLM이 자동으로 `guide_wandering_resident_to_room` 함수를 호출합니다.

### 테스트 시나리오

#### 시나리오 1: 음성으로 배회 탐지 상황 전달

1. **서버 실행**
   ```bash
   cd AI/llm-gateway
   docker compose up -d
   ```

2. **음성 인터페이스 접속**
   - 브라우저에서 `http://localhost:8000/tests/user_testing/test_alfred_voice.html` 접속
   - 또는 `http://localhost:8000/tests/user_testing/test_voice.html` 접속

3. **음성 입력 예시**
   - "Akaza 어르신이 1층 복도에서 배회하고 있어요"
   - "정도현 어르신이 복도에 계신데 생활실로 안내해주세요"
   - "2층 로비에서 어르신 배회가 탐지되었어요. nickname은 Akaza예요"
   - "어르신이 계단에서 발견되었어요. 성함은 정도현이에요"

4. **예상 동작**
   - LLM이 음성을 텍스트로 변환 (STT)
   - LLM이 배회 탐지 상황을 인식
   - LLM이 자동으로 `guide_wandering_resident_to_room` 함수 호출
   - 어르신 정보 조회 (`/api/residents/search/{keyword}`)
   - 안내 메시지 생성 (최소 3회 반복)
   - 안내 메시지를 음성으로 변환하여 재생 (TTS)

#### 시나리오 2: 통합 음성 처리 API 직접 호출

**엔드포인트**: `POST /api/voice/process`

**요청 예시** (cURL):
```bash
curl -X POST "http://localhost:8000/api/voice/process?session_id=test123" \
  -F "audio=@wandering_detection_audio.mp3" \
  -F "response_format=json"
```

**요청 예시** (Python):
```python
import requests

url = "http://localhost:8000/api/voice/process"
files = {
    "audio": open("wandering_detection_audio.mp3", "rb")
}
params = {
    "session_id": "test123",
    "response_format": "json"
}

response = requests.post(url, files=files, params=params)
result = response.json()

print("STT 결과:", result.get("stt_text"))
print("LLM 응답:", result.get("response_text"))
print("함수 호출 결과:", result.get("function_calls"))
```

**음성 파일 내용 예시**:
- "Akaza 어르신이 1층 복도에서 배회하고 있어요. 생활실로 안내해주세요"

---

## 4. 운영 시나리오: Deep Learning 기반 객체 탐지

### 개요
실제 운영 환경에서는 Deep Learning 모델이 어르신을 탐지하면, 자동으로 API를 호출하여 안내 메시지를 생성하고 재생합니다.

### 운영용 API 엔드포인트

**엔드포인트**: `POST /api/wandering/detection` ✅

> **참고**: 운영 환경에서 Deep Learning 모델이 어르신을 탐지했을 때 호출하는 API입니다.

**요청 형식**:
```json
{
    "resident_name": "정도현",           // 선택사항: 어르신 성함
    "nickname": "Akaza",                 // 선택사항: 어르신 nickname
    "detection_location": "1층 복도",     // 필수: 탐지 위치
    "detection_confidence": 0.95,        // 선택사항: 탐지 신뢰도 (0.0~1.0)
    "camera_id": "camera_001",          // 선택사항: 카메라 ID
    "timestamp": "2025-01-22T10:30:00Z" // 선택사항: 탐지 시간 (ISO 8601)
}
```

**응답 형식**:
```json
{
    "success": true,
    "detection_id": "det_1234567890",
    "detection_info": {
        "resident_name": "정도현",
        "nickname": "Akaza",
        "detection_location": "1층 복도",
        "detection_confidence": 0.95,
        "camera_id": "camera_001",
        "timestamp": "2025-01-22T10:30:00Z",
        "detected_at": "2025-01-22T10:30:00.000000"
    },
    "resident_found": true,
    "guidance_messages": [
        "안녕하세요, 정도현 어르신! ...",
        "정도현 어르신, 생활실로 안내해드리겠습니다. ...",
        "정도현 어르신, 생활실로 가시면 됩니다. ..."
    ],
    "resident_info": { ... },
    "tts_audio_url": "/api/tts/audio/det_1234567890",
    "room_info": {
        "room_number": "101",
        "floor": "1층",
        "building": "본관"
    }
}
```

### 운영 시나리오 흐름

```
[Deep Learning 모델]
    ↓ (어르신 탐지)
[객체 인식 결과]
    ↓ (어르신 식별 정보: nickname 또는 성함)
[API 호출]
    ↓ POST /api/wandering/detection
[LLM Gateway]
    ↓ guide_wandering_resident_to_room 함수 호출
[어르신 정보 조회]
    ↓ /api/residents/search/{keyword}
[안내 메시지 생성]
    ↓ (최소 3회 반복 메시지)
[TTS 변환]
    ↓ /api/tts
[음성 재생]
    ↓ (스피커/로봇을 통한 안내)
```

### 운영용 API 테스트 예시

#### cURL로 테스트
```bash
curl -X POST "http://localhost:8000/api/wandering/detection" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001"
  }'
```

### Deep Learning 모델 연동 예시 (Python)

```python
import requests
import json
from datetime import datetime

def detect_wandering_resident(resident_name=None, nickname=None, location="복도"):
    """
    Deep Learning 모델에서 어르신 배회 탐지 시 호출하는 함수
    """
    url = "http://localhost:8000/api/wandering/detection"
    
    payload = {
        "resident_name": resident_name,
        "nickname": nickname,
        "detection_location": location,
        "detection_confidence": 0.95,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # None 값 제거
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success") and result.get("resident_found"):
            # 안내 메시지 출력
            print("=== 배회 탐지 안내 ===")
            for i, msg in enumerate(result["guidance_messages"], 1):
                print(f"{i}. {msg}")
            
            # TTS 오디오 재생 (로봇/스피커)
            if "tts_audio_url" in result:
                play_audio(result["tts_audio_url"])
            
            return result
        else:
            print("어르신을 찾을 수 없습니다.")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"API 호출 실패: {e}")
        return None

# 사용 예시
# Deep Learning 모델이 "Akaza"를 탐지한 경우
detect_wandering_resident(nickname="Akaza", location="1층 복도")
```

---

## 5. 테스트 체크리스트

### 기능 테스트

- [ ] **어르신 정보 조회**
  - [ ] nickname으로 조회 성공
  - [ ] 성함으로 조회 성공
  - [ ] 존재하지 않는 어르신 처리

- [ ] **안내 메시지 생성**
  - [ ] 최소 3개의 안내 메시지 생성 확인
  - [ ] 메시지에 어르신 이름 포함 확인
  - [ ] 메시지에 생활실 정보 포함 확인
  - [ ] 친절한 톤 확인

- [ ] **음성 인터페이스**
  - [ ] STT로 배회 탐지 상황 인식
  - [ ] LLM이 자동으로 함수 호출
  - [ ] TTS로 안내 메시지 재생

### 에러 처리 테스트

- [ ] 어르신을 찾을 수 없는 경우
- [ ] API 타임아웃 처리
- [ ] 네트워크 오류 처리
- [ ] 잘못된 파라미터 처리

### 성능 테스트

- [ ] API 응답 시간 (목표: 3초 이내)
- [ ] 동시 요청 처리
- [ ] 메모리 사용량

---

## 6. 문제 해결

### 문제 1: 어르신을 찾을 수 없음

**증상**: `resident_found: false`

**해결 방법**:
1. `/api/residents/search/{keyword}` API로 직접 검색하여 어르신이 존재하는지 확인
2. nickname 또는 성함의 철자 확인
3. 데이터베이스에 해당 어르신 데이터가 있는지 확인

### 문제 2: 안내 메시지가 3개 미만

**증상**: `guidance_messages` 배열에 2개 이하의 메시지

**해결 방법**:
1. `_generate_guidance_messages` 함수 로직 확인
2. LLM의 함수 호출 결과 확인
3. 로그에서 메시지 생성 과정 확인

### 문제 3: 음성 인터페이스에서 함수가 호출되지 않음

**증상**: LLM이 함수를 호출하지 않고 일반 응답만 생성

**해결 방법**:
1. System Prompt에 배회 탐지 안내 기능 설명이 포함되어 있는지 확인
2. 사용자 입력이 배회 탐지 상황을 명확히 설명하는지 확인
3. TOOLS 리스트에 `guide_wandering_resident_to_room`이 포함되어 있는지 확인

---

## 7. 추가 리소스

- **구현 계획서**: `docs/WANDERING_DETECTION_GUIDANCE_IMPLEMENTATION_PLAN.md`
- **API 문서**: `http://localhost:8000/docs` (Swagger UI)
- **음성 인터페이스 테스트**: `http://localhost:8000/tests/user_testing/test_alfred_voice.html`

---

## 8. 운영 환경 배포 시 주의사항

1. **보안**: 운영 환경에서는 인증/인가 추가 필요
2. **로깅**: 모든 배회 탐지 이벤트 로깅
3. **모니터링**: API 응답 시간 및 에러율 모니터링
4. **알림**: 배회 탐지 시 담당자에게 알림 전송 고려
5. **TTS 캐싱**: 동일한 안내 메시지는 TTS 결과 캐싱 고려

---

**작성일**: 2025-01-22  
**버전**: 1.0
