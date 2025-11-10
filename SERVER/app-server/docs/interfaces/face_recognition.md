# 얼굴 인식 인터페이스 명세서

## 개요

얼굴 인식을 통한 면회자/보호자 식별 기능을 제공합니다. PII(개인정보) 보호를 위해 얼굴 식별키는 해시만 저장됩니다.

## 시스템 구성

- **Robot Controller**: ROS2 기반 로봇 제어 시스템
- **Central Server**: FastAPI 기반 중앙 서버
- **AI Server**: 얼굴 인식 서버

---

## Robot Controller <-> Central Server

### IF-01: 얼굴 인식 이벤트 전송

**Interface ID**: IF-FACE-01  
**Function/Description**: 로봇이 얼굴을 인식했을 때 중앙 서버로 이벤트 전송  
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
  "category": "face",
  "unique_key": "facehash_abcd1234",
  "meta": {
    "role": "visitor",
    "consent": "Y",
    "last_verified_at": "2025-11-10T10:21:50Z",
    "confidence": 0.92,
    "bbox": [150, 100, 80, 100]
  },
  "detected_at": "2025-11-10T10:21:55Z",
  "processing_info": {
    "intent": "announce",
    "api_calls": [],
    "cmds": [
      {
        "topic": "/robot/notify",
        "payload": {
          "type": "VISITOR_ARRIVED",
          "face_key": "facehash_abcd1234"
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
  "detection_event_id": "550e8400-e29b-41d4-a716-446655440002",
  "robot_id": "robot-001",
  "category": "face",
  "unique_key": "facehash_abcd1234",
  "meta": {
    "role": "visitor",
    "consent": "Y",
    "last_verified_at": "2025-11-10T10:21:50Z",
    "confidence": 0.92,
    "bbox": [150, 100, 80, 100]
  },
  "detected_at": "2025-11-10T10:21:55Z",
  "processing_info": {
    "intent": "announce",
    "api_calls": [],
    "cmds": [
      {
        "topic": "/robot/notify",
        "payload": {
          "type": "VISITOR_ARRIVED",
          "face_key": "facehash_abcd1234"
        }
      }
    ],
    "scenario_state": "RUN"
  },
  "processed_status": "accepted",
  "created_at": "2025-11-10T10:21:55Z"
}
```

**400 Bad Request**
```json
{
  "detail": "Invalid RobotDetectionEvent payload"
}
```

### IF-02: 얼굴 레지스트리 조회

**Interface ID**: IF-FACE-02  
**Function/Description**: 얼굴 레지스트리 정보 조회 (PII 보호)  
**Sender**: Robot Controller / Admin GUI  
**Receiver**: Central Server  
**Endpoint**: `/api/v1/detections/registry/face/{unique_key}`  
**Method**: `GET`

#### Request Data
- **Path Parameter**: `unique_key` (예: `facehash_abcd1234`)

#### Response Data / Status Code / Description

**200 OK**
```json
{
  "key": "facehash_abcd1234",
  "data": {
    "face_key": "facehash_abcd1234",
    "role": "visitor",
    "consent": true,
    "pii_ref": "pii_vault_key_xyz789",
    "policy": {
      "retention_days": 90,
      "masking": true
    },
    "action_plan": {
      "intent": "announce",
      "cmds": [
        {
          "topic": "/robot/notify",
          "payload": {
            "type": "VISITOR_ARRIVED"
          }
        }
      ]
    },
    "updated_at": "2025-11-10T10:21:55Z"
  },
  "updated_at": "2025-11-10T10:21:55Z"
}
```

**404 Not Found**
```json
{
  "detail": "Registry not found: face/facehash_abcd1234"
}
```

---

## Central Server <-> AI Server

### IF-03: 얼굴 인식 요청 (향후 구현)

**Interface ID**: IF-FACE-03  
**Function/Description**: AI 서버에 얼굴 인식 요청  
**Sender**: Central Server  
**Receiver**: AI Server  
**Endpoint**: `/detect/face` (예상)  
**Method**: `POST`

#### Request Data
```json
{
  "robot_id": "robot-001",
  "image": "base64_encoded_image",
  "timestamp": 1722601200
}
```

#### Response Data
```json
{
  "status_code": 200,
  "detections": [
    {
      "face_key": "facehash_abcd1234",
      "confidence": 0.92,
      "bbox": [150, 100, 80, 100],
      "role": "visitor",
      "consent": true
    }
  ]
}
```

---

## 데이터베이스 설계

### detection_event 테이블 (공통)
- `detection_event_id`: UUID (PK)
- `robot_id`: TEXT
- `category`: TEXT ('face')
- `unique_key`: TEXT (예: 'facehash_abcd1234')
- `meta`: JSONB (카테고리별 부가정보)
- `detected_at`: TIMESTAMP
- `processing_info`: JSONB
- `processed_status`: TEXT
- `created_at`: TIMESTAMP

### face_registry 테이블 (PII 보호)
- `face_key`: TEXT (PK) - 얼굴 식별키 해시
- `role`: TEXT - 역할 ('elder' | 'caregiver' | 'visitor')
- `consent`: BOOLEAN - 동의 여부 (기본값: false)
- `pii_ref`: TEXT - 외부 금고/암호화 저장소 key (선택)
- `policy`: JSONB - 보관기간/마스킹 등
- `action_plan`: JSONB - 기본 처리 계획
- `updated_at`: TIMESTAMP

### 제약조건
- `ck_face_registry_role`: `role IN ('elder', 'caregiver', 'visitor')`

### 인덱스
- `idx_detection_event_cat_key`: (category, unique_key)
- `idx_detection_event_robot`: (robot_id)
- `idx_detection_event_time`: (detected_at DESC)

---

## 처리 흐름

1. **로봇이 얼굴 인식**
   - 카메라에서 얼굴 감지
   - 얼굴 특징 추출 및 해시 생성 (예: 'facehash_abcd1234')

2. **중앙 서버로 이벤트 전송**
   - `POST /api/v1/detections` 호출
   - `category: "face"`, `unique_key: "facehash_abcd1234"` 포함
   - 헤더에 `X-Robot-ID: robot-001` 필수
   - **중요**: 원본 얼굴 이미지는 전송하지 않음 (PII 보호)

3. **레지스트리 조회/업데이트**
   - `face_registry` 테이블에서 얼굴 정보 조회
   - 없으면 자동 생성, 있으면 업데이트
   - `meta` 필드의 `role`, `consent` 정보 저장
   - `consent` 필드로 동의 여부 관리

4. **액션 실행**
   - `processing_info`의 `api_calls` 및 `cmds` 실행
   - 예: 면회자 도착 알림
   - Redis Streams를 통해 비동기 처리 (Redis가 활성화된 경우)
   - Redis가 없으면 로그만 출력

5. **처리 상태 업데이트**
   - `processed_status`: 'accepted' → 'done' / 'failed'
   - 실제 액션 실행은 별도 워커 프로세스에서 처리

---

## 샘플 시나리오

### 시나리오 1: 면회자 인식

1. 로봇이 면회실에서 얼굴 인식
2. 중앙 서버로 이벤트 전송 (`role: "visitor"`)
3. 레지스트리에서 얼굴 정보 확인
4. 보호자에게 면회자 도착 알림
5. 로봇이 면회자에게 인사

### 시나리오 2: 보호자 인식

1. 로봇이 복도에서 보호자 얼굴 인식
2. 중앙 서버로 이벤트 전송 (`role: "caregiver"`)
3. 레지스트리에서 보호자 정보 확인
4. 환자에게 보호자 도착 알림

### 시나리오 3: 동의 관리

1. 로봇이 새로운 얼굴 인식
2. 레지스트리에 `consent: false`로 저장
3. 관리자에게 동의 요청 알림
4. 동의 후 `consent: true`로 업데이트

---

## PII 보호 정책

### 1. 얼굴 식별키 해시
- 원본 얼굴 이미지는 저장하지 않음
- 얼굴 특징 벡터를 해시화하여 `face_key` 생성
- 해시는 역변환 불가능 (단방향)

### 2. 외부 금고 연동
- 원본 얼굴 데이터는 별도 암호화 저장소에 보관
- `pii_ref` 필드로 외부 저장소 key 참조
- 접근 권한이 있는 경우에만 원본 데이터 조회 가능

### 3. 보관 정책
- `policy` 필드에 보관기간 설정
- 예: `{"retention_days": 90, "masking": true}`
- 보관기간 경과 시 자동 삭제 또는 마스킹

### 4. 역할 기반 접근 제어
- `role` 필드로 역할 구분
  - `elder`: 환자
  - `caregiver`: 보호자
  - `visitor`: 면회자

---

## 주의사항

1. **PII 보호**: 얼굴 식별키는 해시만 저장, 원본 이미지 저장 금지
2. **동의 관리**: `consent` 필드로 동의 여부 필수 확인
3. **신뢰도**: `confidence` 값이 0.85 이상일 때만 처리 권장
4. **중복 방지**: 동일 얼굴에 대한 연속 인식은 debounce 처리 필요
5. **보관 정책**: `policy` 필드로 데이터 보관기간 관리
6. **역할 검증**: `role` 필드는 제약조건으로 검증
7. **헤더 필수**: `X-Robot-ID` 헤더는 필수입니다. 누락 시 422 에러 발생
8. **액션 실행**: Redis가 활성화되어 있으면 비동기 처리, 없으면 로그만 출력

## 실제 구현 확인

### 코드 위치
- 라우터: `app/adapters/http/robot_detection_router.py`
- 액션 실행기: `app/services/robot_detection_action_executor.py`
- 유즈케이스: `app/application/use_cases/robot_detection_use_cases.py`
- 리포지토리: `app/adapters/repositories/robot_detection_repository_impl.py`

### 테스트 코드
- 통합 테스트: `tests/integration/test_robot_detection_api.py`
- 테스트 실행: `pytest tests/integration/test_robot_detection_api.py -v`

