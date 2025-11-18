# OCR 문자인식 인터페이스 명세서

## 개요

OCR(Optical Character Recognition)을 통한 공간 식별 및 안내 기능을 제공합니다.

## 시스템 구성

- **Robot Controller**: ROS2 기반 로봇 제어 시스템
- **Central Server**: FastAPI 기반 중앙 서버
- **AI Server**: OCR 텍스트 인식 서버

---

## Robot Controller <-> Central Server

### IF-01: OCR 텍스트 인식 이벤트 전송

**Interface ID**: IF-OCR-01  
**Function/Description**: 로봇이 OCR로 텍스트를 인식했을 때 중앙 서버로 이벤트 전송  
**Sender**: Robot Controller  
**Receiver**: Central Server  
**Endpoint**: `/api/v1/detections`  
**Method**: `POST`

#### Request Headers
```
X-Robot-ID: robot-001
Content-Type: application/json
```

#### Request Data
```json
{
  "category": "text",
  "unique_key": "식당",
  "meta": {
    "lang": "ko",
    "room_code": "DINING-01",
    "synonyms": ["식당", "레스토랑", "다이닝"],
    "bbox": [200, 60, 120, 45],
    "confidence": 0.88,
    "raw_text": "식당"
  },
  "detected_at": "2025-11-10T10:22:01Z",
  "processing_info": {
    "intent": "announce",
    "api_calls": [],
    "cmds": [
      {
        "topic": "/robot/say",
        "payload": {
          "text": "식당에 도착했습니다."
        }
      }
    ],
    "scenario_state": "RUN"
  }
}
```

#### Response Data / Status Code / Description

**201 Created**
```json
{
  "detection_event_id": "550e8400-e29b-41d4-a716-446655440001",
  "robot_id": "robot-001",
  "category": "text",
  "unique_key": "식당",
  "meta": {
    "lang": "ko",
    "room_code": "DINING-01",
    "synonyms": ["식당", "레스토랑", "다이닝"],
    "bbox": [200, 60, 120, 45],
    "confidence": 0.88,
    "raw_text": "식당"
  },
  "detected_at": "2025-11-10T10:22:01Z",
  "processing_info": {
    "intent": "announce",
    "api_calls": [],
    "cmds": [
      {
        "topic": "/robot/say",
        "payload": {
          "text": "식당에 도착했습니다."
        }
      }
    ],
    "scenario_state": "RUN"
  },
  "processed_status": "accepted",
  "created_at": "2025-11-10T10:22:01Z"
}
```

**400 Bad Request**
```json
{
  "detail": "Invalid RobotDetectionEvent payload"
}
```

### IF-02: OCR 텍스트 레지스트리 조회

**Interface ID**: IF-OCR-02  
**Function/Description**: OCR 텍스트 레지스트리 정보 조회  
**Sender**: Robot Controller / Admin GUI  
**Receiver**: Central Server  
**Endpoint**: `/api/v1/detections/registry/text/{unique_key}`  
**Method**: `GET`

#### Request Data
- **Path Parameter**: `unique_key` (예: `식당`)

#### Response Data / Status Code / Description

**200 OK**
```json
{
  "key": "식당",
  "data": {
    "text_key": "식당",
    "room_code": "DINING-01",
    "lang": "ko",
    "synonyms": ["식당", "레스토랑", "다이닝"],
    "action_plan": {
      "intent": "announce",
      "cmds": [
        {
          "topic": "/robot/say",
          "payload": {
            "text": "식당에 도착했습니다."
          }
        }
      ]
    },
    "updated_at": "2025-11-10T10:22:01Z"
  },
  "updated_at": "2025-11-10T10:22:01Z"
}
```

**404 Not Found**
```json
{
  "detail": "Registry not found: text/식당"
}
```

---

## Central Server <-> AI Server

### IF-03: OCR 텍스트 인식 요청 (향후 구현)

**Interface ID**: IF-OCR-03  
**Function/Description**: AI 서버에 OCR 텍스트 인식 요청  
**Sender**: Central Server  
**Receiver**: AI Server  
**Endpoint**: `/detect/text` (예상)  
**Method**: `POST`

#### Request Data
```json
{
  "robot_id": "robot-001",
  "image": "base64_encoded_image",
  "lang": "ko",
  "timestamp": 1722601200
}
```

#### Response Data
```json
{
  "status_code": 200,
  "detections": [
    {
      "text": "식당",
      "confidence": 0.88,
      "bbox": [200, 60, 120, 45],
      "lang": "ko"
    }
  ]
}
```

---

## 데이터베이스 설계

### detection_event 테이블 (공통)
- `detection_event_id`: UUID (PK)
- `robot_id`: TEXT
- `category`: TEXT ('text')
- `unique_key`: TEXT (예: '식당')
- `meta`: JSONB (카테고리별 부가정보)
- `detected_at`: TIMESTAMP
- `processing_info`: JSONB
- `processed_status`: TEXT
- `created_at`: TIMESTAMP

### text_registry 테이블
- `text_key`: TEXT (PK) - 텍스트 키 (예: '식당')
- `room_code`: TEXT - 방 코드
- `lang`: TEXT - 언어 (예: 'ko', 'en')
- `synonyms`: TEXT[] - 유사 표현 배열
- `action_plan`: JSONB - 기본 처리 계획
- `updated_at`: TIMESTAMP

### 인덱스
- `idx_detection_event_cat_key`: (category, unique_key)
- `idx_detection_event_robot`: (robot_id)
- `idx_detection_event_time`: (detected_at DESC)

---

## 처리 흐름

1. **로봇이 텍스트 인식**
   - 카메라에서 텍스트 감지
   - OCR 엔진으로 텍스트 추출 (예: '식당')

2. **중앙 서버로 이벤트 전송**
   - `POST /api/v1/detections` 호출
   - `category: "text"`, `unique_key: "식당"` 포함
   - 헤더에 `X-Robot-ID: robot-001` 필수

3. **레지스트리 조회/업데이트**
   - `text_registry` 테이블에서 텍스트 정보 조회
   - 없으면 자동 생성, 있으면 업데이트
   - `meta` 필드의 `room_code`, `lang` 정보 저장
   - `synonyms` 배열에 유사 표현 저장

4. **액션 실행**
   - `processing_info`의 `api_calls` 및 `cmds` 실행
   - 예: 로봇 음성 안내 ("식당에 도착했습니다.")
   - Redis Streams를 통해 비동기 처리 (Redis가 활성화된 경우)
   - Redis가 없으면 로그만 출력

5. **처리 상태 업데이트**
   - `processed_status`: 'accepted' → 'done' / 'failed'
   - 실제 액션 실행은 별도 워커 프로세스에서 처리

---

## 샘플 시나리오

### 시나리오 1: 공간 안내

1. 로봇이 "식당" 표지판 인식
2. 중앙 서버로 이벤트 전송 (`intent: "announce"`)
3. 레지스트리에서 텍스트 정보 확인
4. 로봇 음성 안내: "식당에 도착했습니다."
5. 사용자에게 목적지 도착 알림

### 시나리오 2: 다국어 지원

1. 로봇이 "Restaurant" (영문) 표지판 인식
2. `lang: "en"` 포함하여 이벤트 전송
3. 레지스트리에서 `synonyms: ["식당", "Restaurant"]` 확인
4. 한국어 사용자에게는 "식당"으로 안내

### 시나리오 3: 유사 표현 처리

1. 로봇이 "레스토랑" 표지판 인식
2. 레지스트리에서 `synonyms` 배열 확인
3. "레스토랑" → "식당" 매핑
4. 동일한 `room_code`로 처리

---

## 주의사항

1. **텍스트 키 정규화**: 대소문자, 공백 처리 필요
2. **언어 감지**: `lang` 필드로 다국어 지원
3. **유사 표현**: `synonyms` 배열로 동의어 처리
4. **신뢰도**: `confidence` 값이 0.7 이상일 때만 처리 권장
5. **중복 방지**: 동일 텍스트에 대한 연속 인식은 debounce 처리 필요
6. **헤더 필수**: `X-Robot-ID` 헤더는 필수입니다. 누락 시 422 에러 발생
7. **액션 실행**: Redis가 활성화되어 있으면 비동기 처리, 없으면 로그만 출력

## 실제 구현 확인

### 코드 위치
- 라우터: `app/adapters/http/robot_detection_router.py`
- 액션 실행기: `app/services/robot_detection_action_executor.py`
- 유즈케이스: `app/application/use_cases/robot_detection_use_cases.py`
- 리포지토리: `app/adapters/repositories/robot_detection_repository_impl.py`

### 테스트 코드
- 통합 테스트: `tests/integration/test_robot_detection_api.py`
- 테스트 실행: `pytest tests/integration/test_robot_detection_api.py::test_create_text_detection -v`

