# ArUco 마커 인터페이스 명세서

## 개요

ArUco 마커 인식을 통한 출입구 제어 및 위치 인식 기능을 제공합니다.

## 시스템 구성

- **Robot Controller**: ROS2 기반 로봇 제어 시스템
- **Central Server**: FastAPI 기반 중앙 서버
- **AI Server**: ArUco 마커 인식 서버

---

## Robot Controller <-> Central Server

### IF-01: ArUco 마커 인식 이벤트 전송

**Interface ID**: IF-ARUCO-01  
**Function/Description**: 로봇이 ArUco 마커를 인식했을 때 중앙 서버로 이벤트 전송  
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
  "category": "aruco",
  "unique_key": "ARUCO_23",
  "meta": {
    "entrance_id": "E-1",
    "zone": "Hall-A",
    "bbox": [120, 80, 64, 64],
    "confidence": 0.95,
    "pose": {
      "x": 5.0,
      "y": -1.0,
      "yaw": -80.0
    }
  },
  "detected_at": "2025-11-10T10:20:30Z",
  "processing_info": {
    "intent": "open_door",
    "api_calls": [
      {
        "method": "POST",
        "url": "https://sec.local/door/open",
        "headers": {},
        "body": {
          "entrance_id": "E-1"
        }
      }
    ],
    "cmds": [],
    "scenario_state": "INIT"
  }
}
```

#### Response Data / Status Code / Description

**201 Created**
```json
{
  "detection_event_id": "550e8400-e29b-41d4-a716-446655440000",
  "robot_id": "robot-001",
  "category": "aruco",
  "unique_key": "ARUCO_23",
  "meta": {
    "entrance_id": "E-1",
    "zone": "Hall-A",
    "bbox": [120, 80, 64, 64],
    "confidence": 0.95,
    "pose": {
      "x": 5.0,
      "y": -1.0,
      "yaw": -80.0
    }
  },
  "detected_at": "2025-11-10T10:20:30Z",
  "processing_info": {
    "intent": "open_door",
    "api_calls": [
      {
        "method": "POST",
        "url": "https://sec.local/door/open",
        "headers": {},
        "body": {
          "entrance_id": "E-1"
        }
      }
    ],
    "cmds": [],
    "scenario_state": "INIT"
  },
  "processed_status": "accepted",
  "created_at": "2025-11-10T10:20:30Z"
}
```

**400 Bad Request**
```json
{
  "detail": "Invalid RobotDetectionEvent payload"
}
```

**422 Unprocessable Entity**
```json
{
  "detail": [
    {
      "loc": ["header", "x-robot-id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### IF-02: ArUco 마커 레지스트리 조회

**Interface ID**: IF-ARUCO-02  
**Function/Description**: ArUco 마커 레지스트리 정보 조회  
**Sender**: Robot Controller / Admin GUI  
**Receiver**: Central Server  
**Endpoint**: `/api/v1/detections/registry/aruco/{unique_key}`  
**Method**: `GET`

#### Request Data
- **Path Parameter**: `unique_key` (예: `ARUCO_23`)

#### Response Data / Status Code / Description

**200 OK**
```json
{
  "key": "ARUCO_23",
  "data": {
    "marker_key": "ARUCO_23",
    "entrance_id": "E-1",
    "zone": "Hall-A",
    "pose": {
      "x": 5.0,
      "y": -1.0,
      "yaw": -80.0
    },
    "description": "1층 로비 출입구",
    "action_plan": {
      "intent": "open_door",
      "api_calls": [
        {
          "method": "POST",
          "url": "https://sec.local/door/open",
          "body": {
            "entrance_id": "E-1"
          }
        }
      ]
    },
    "updated_at": "2025-11-10T10:20:30Z"
  },
  "updated_at": "2025-11-10T10:20:30Z"
}
```

**404 Not Found**
```json
{
  "detail": "Registry not found: aruco/ARUCO_23"
}
```

---

## Central Server <-> AI Server

### IF-03: ArUco 마커 인식 요청 (향후 구현)

**Interface ID**: IF-ARUCO-03  
**Function/Description**: AI 서버에 ArUco 마커 인식 요청  
**Sender**: Central Server  
**Receiver**: AI Server  
**Endpoint**: `/detect/aruco` (예상)  
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
      "marker_id": 23,
      "unique_key": "ARUCO_23",
      "bbox": [120, 80, 64, 64],
      "confidence": 0.95,
      "pose": {
        "x": 5.0,
        "y": -1.0,
        "yaw": -80.0
      }
    }
  ]
}
```

---

## 데이터베이스 설계

### detection_event 테이블 (공통)
- `detection_event_id`: UUID (PK)
- `robot_id`: TEXT
- `category`: TEXT ('aruco')
- `unique_key`: TEXT (예: 'ARUCO_23')
- `meta`: JSONB (카테고리별 부가정보)
- `detected_at`: TIMESTAMP
- `processing_info`: JSONB
- `processed_status`: TEXT
- `created_at`: TIMESTAMP

### marker_registry 테이블
- `marker_key`: TEXT (PK) - 마커 키 (예: 'ARUCO_23')
- `entrance_id`: TEXT - 출입구/구역 식별
- `zone`: TEXT - 구역
- `pose`: JSONB - 고정 좌표/자세
- `description`: TEXT - 설명
- `action_plan`: JSONB - 기본 처리 계획
- `updated_at`: TIMESTAMP

### 인덱스
- `idx_detection_event_cat_key`: (category, unique_key)
- `idx_detection_event_robot`: (robot_id)
- `idx_detection_event_time`: (detected_at DESC)

---

## 처리 흐름

1. **로봇이 ArUco 마커 인식**
   - 카메라에서 ArUco 마커 감지
   - 마커 ID 추출 (예: 23 → 'ARUCO_23')

2. **중앙 서버로 이벤트 전송**
   - `POST /api/v1/detections` 호출
   - `category: "aruco"`, `unique_key: "ARUCO_23"` 포함
   - 헤더에 `X-Robot-ID: robot-001` 필수

3. **레지스트리 조회/업데이트**
   - `marker_registry` 테이블에서 마커 정보 조회
   - 없으면 자동 생성, 있으면 업데이트
   - `meta` 필드의 `entrance_id`, `zone`, `pose` 정보 저장

4. **액션 실행**
   - `processing_info`의 `api_calls` 및 `cmds` 실행
   - 예: 출입구 열기 API 호출
   - Redis Streams를 통해 비동기 처리 (Redis가 활성화된 경우)
   - Redis가 없으면 로그만 출력

5. **처리 상태 업데이트**
   - `processed_status`: 'accepted' → 'done' / 'failed'
   - 실제 액션 실행은 별도 워커 프로세스에서 처리

---

## 샘플 시나리오

### 시나리오 1: 출입구 열기

1. 로봇이 1층 로비에서 ArUco 마커 #23 인식
2. 중앙 서버로 이벤트 전송 (`intent: "open_door"`)
3. 레지스트리에서 마커 정보 확인 (출입구 E-1)
4. 보안 서버에 출입구 열기 요청
5. 출입구 열림 확인

### 시나리오 2: 위치 확인

1. 로봇이 특정 구역에서 ArUco 마커 인식
2. 마커의 `pose` 정보로 로봇 위치 보정
3. 내비게이션 시스템에 위치 정보 전달

---

## 주의사항

1. **마커 키 형식**: `ARUCO_{marker_id}` 형식 권장
2. **좌표계**: 로봇 기준 상대 좌표 또는 맵 기준 절대 좌표
3. **신뢰도**: `confidence` 값이 0.8 이상일 때만 처리 권장
4. **중복 방지**: 동일 마커에 대한 연속 인식은 debounce 처리 필요
5. **헤더 필수**: `X-Robot-ID` 헤더는 필수입니다. 누락 시 422 에러 발생
6. **액션 실행**: Redis가 활성화되어 있으면 비동기 처리, 없으면 로그만 출력

## 실제 구현 확인

### 코드 위치
- 라우터: `app/adapters/http/robot_detection_router.py`
- 액션 실행기: `app/services/robot_detection_action_executor.py`
- 유즈케이스: `app/application/use_cases/robot_detection_use_cases.py`
- 리포지토리: `app/adapters/repositories/robot_detection_repository_impl.py`

### 테스트 코드
- 통합 테스트: `tests/integration/test_robot_detection_api.py`
- 테스트 실행: `pytest tests/integration/test_robot_detection_api.py -v`

