# Robot Detection API Documentation

## 개요

로봇 인식 이벤트 수집 API는 4개 카테고리(ArUco 마커, OCR 텍스트, 얼굴, 전신)의 인식 결과를 수집하고 처리하는 RESTful API입니다.

**Base URL**: `http(s)://<host>/api/v1`

## 인증

- **Header**: `X-Robot-ID: <robot_id>` (필수)
- **Header**: `Authorization: Bearer <token>` (선택, 향후 구현)

## 엔드포인트

### 1. 인식 이벤트 수집

**POST** `/detections`

로봇이 인식한 결과를 전송합니다.

#### 요청 헤더
```
X-Robot-ID: robot-001
Content-Type: application/json
```

#### 요청 본문
```json
{
  "category": "aruco|text|face|person",
  "unique_key": "string",
  "meta": {
    "key": "value"
  },
  "detected_at": "2025-11-10T10:20:30Z",
  "processing_info": {
    "intent": "open_door|start_follow|stop_follow|announce|none",
    "api_calls": [
      {
        "method": "POST",
        "url": "https://sec.local/door/open",
        "headers": {},
        "body": {}
      }
    ],
    "cmds": [
      {
        "topic": "/robot/cmd",
        "payload": {
          "type": "FOLLOW",
          "target_id": "P001"
        }
      }
    ],
    "scenario_state": "INIT|RUN|END"
  }
}
```

#### 응답 (201 Created)
```json
{
  "detection_event_id": "uuid",
  "robot_id": "robot-001",
  "category": "aruco",
  "unique_key": "ARUCO_23",
  "meta": {},
  "detected_at": "2025-11-10T10:20:30Z",
  "processing_info": {
    "intent": "open_door",
    "api_calls": [],
    "cmds": [],
    "scenario_state": "INIT"
  },
  "processed_status": "accepted",
  "created_at": "2025-11-10T10:20:30Z"
}
```

### 2. 인식 이벤트 목록 조회

**GET** `/detections`

필터링 조건으로 인식 이벤트 목록을 조회합니다.

#### 쿼리 파라미터
- `category` (optional): 인식 카테고리 (`aruco`, `text`, `face`, `person`)
- `unique_key` (optional): 고유 키
- `robot_id` (optional): 로봇 ID
- `since` (optional): 시작 시간 (ISO 8601)
- `until` (optional): 종료 시간 (ISO 8601)
- `skip` (optional, default: 0): 건너뛸 개수
- `limit` (optional, default: 100, max: 1000): 조회 개수

#### 예시
```
GET /api/v1/detections/?category=aruco&robot_id=robot-001&limit=50
```

#### 응답 (200 OK)
```json
[
  {
    "detection_event_id": "uuid",
    "robot_id": "robot-001",
    "category": "aruco",
    "unique_key": "ARUCO_23",
    "meta": {},
    "detected_at": "2025-11-10T10:20:30Z",
    "processing_info": {},
    "processed_status": "accepted",
    "created_at": "2025-11-10T10:20:30Z"
  }
]
```

### 3. 인식 이벤트 단건 조회

**GET** `/detections/{event_id}`

특정 인식 이벤트를 조회합니다.

#### 경로 파라미터
- `event_id`: 이벤트 UUID

#### 응답 (200 OK)
```json
{
  "detection_event_id": "uuid",
  "robot_id": "robot-001",
  "category": "aruco",
  "unique_key": "ARUCO_23",
  "meta": {},
  "detected_at": "2025-11-10T10:20:30Z",
  "processing_info": {},
  "processed_status": "accepted",
  "created_at": "2025-11-10T10:20:30Z"
}
```

#### 응답 (404 Not Found)
```json
{
  "detail": "Detection event not found"
}
```

### 4. 레지스트리 조회

**GET** `/detections/registry/{category}/{unique_key}`

카테고리별 레지스트리 정보를 조회합니다.

#### 경로 파라미터
- `category`: 카테고리 (`aruco`, `text`, `face`, `person`)
- `unique_key`: 고유 키

#### 예시
```
GET /api/v1/detections/registry/aruco/ARUCO_23
```

#### 응답 (200 OK)
```json
{
  "key": "ARUCO_23",
  "data": {
    "marker_key": "ARUCO_23",
    "entrance_id": "E-1",
    "zone": "Hall-A",
    "pose": {},
    "description": "",
    "action_plan": {},
    "updated_at": "2025-11-10T10:20:30Z"
  },
  "updated_at": "2025-11-10T10:20:30Z"
}
```

### 5. 액션 수동 실행

**POST** `/detections/actions/execute`

이벤트의 액션을 수동으로 실행합니다 (재시도/수동 트리거).

#### 요청 본문
```json
{
  "event_id": "uuid",
  "processing_info": {
    "intent": "open_door",
    "api_calls": [],
    "cmds": []
  }
}
```

#### 응답 (200 OK)
```json
{
  "status": "queued",
  "event_id": "uuid",
  "actions": [],
  "stream_id": "1234567890-0"
}
```

## 카테고리별 샘플 페이로드

### ArUco (출입구 열기)
```json
{
  "category": "aruco",
  "unique_key": "ARUCO_23",
  "meta": {
    "entrance_id": "E-1",
    "zone": "Hall-A",
    "bbox": [120, 80, 64, 64],
    "confidence": 0.95
  },
  "detected_at": "2025-11-10T10:20:30Z",
  "processing_info": {
    "intent": "open_door",
    "api_calls": [
      {
        "method": "POST",
        "url": "https://sec.local/door/open",
        "body": {"entrance_id": "E-1"}
      }
    ],
    "cmds": [],
    "scenario_state": "INIT"
  }
}
```

### OCR (공간 식별)
```json
{
  "category": "text",
  "unique_key": "식당",
  "meta": {
    "lang": "ko",
    "room_code": "DINING-01",
    "bbox": [200, 60, 120, 45],
    "confidence": 0.88
  },
  "detected_at": "2025-11-10T10:22:01Z",
  "processing_info": {
    "intent": "announce",
    "api_calls": [],
    "cmds": [
      {
        "topic": "/robot/say",
        "payload": {"text": "식당에 도착했습니다."}
      }
    ]
  }
}
```

### 얼굴 (면회자 인식)
```json
{
  "category": "face",
  "unique_key": "facehash_abcd1234",
  "meta": {
    "role": "visitor",
    "consent": "Y",
    "last_verified_at": "2025-11-10T10:21:50Z"
  },
  "detected_at": "2025-11-10T10:21:55Z",
  "processing_info": {
    "intent": "announce",
    "cmds": [
      {
        "topic": "/robot/notify",
        "payload": {"type": "VISITOR_ARRIVED"}
      }
    ]
  }
}
```

### 전신/추종
```json
{
  "category": "person",
  "unique_key": "track_006",
  "meta": {
    "distance_m": 1.8,
    "pose": {"yaw": 0.12},
    "velocity": {"vx": 0.3},
    "lost": false
  },
  "detected_at": "2025-11-10T10:23:10Z",
  "processing_info": {
    "intent": "start_follow",
    "cmds": [
      {
        "topic": "/robot/cmd",
        "payload": {
          "type": "FOLLOW",
          "target_id": "track_006",
          "distance": 1.5
        }
      }
    ]
  }
}
```

## 에러 응답

### 400 Bad Request
```json
{
  "detail": "Invalid RobotDetectionEvent payload"
}
```

### 404 Not Found
```json
{
  "detail": "Detection event not found"
}
```

### 422 Unprocessable Entity
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

### 500 Internal Server Error
```json
{
  "detail": "Failed to create detection: <error message>"
}
```

## 처리 상태

- `accepted`: 이벤트가 수신되어 큐에 추가됨
- `done`: 액션이 성공적으로 실행됨
- `failed`: 액션 실행 실패

## 주의사항

1. **타임존**: `detected_at`는 UTC로 표준화되어야 합니다.
2. **PII 보호**: 얼굴 식별키는 해시만 저장됩니다.
3. **비동기 처리**: 액션은 Redis Streams를 통해 비동기로 처리됩니다.
4. **레지스트리**: 이벤트 수신 시 자동으로 레지스트리가 업데이트됩니다.

