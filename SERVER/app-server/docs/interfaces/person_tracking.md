# 전신 인식 인터페이스 명세서

## 개요

전신 추적을 통한 로봇 추종 기능을 제공합니다. 사람의 전신을 추적하여 로봇이 따라다니는 기능을 구현합니다.

## 시스템 구성

- **Robot Controller**: ROS2 기반 로봇 제어 시스템
- **Central Server**: FastAPI 기반 중앙 서버
- **AI Server**: 전신 추적 서버

---

## Robot Controller <-> Central Server

### IF-01: 전신 인식 이벤트 전송

**Interface ID**: IF-PERSON-01  
**Function/Description**: 로봇이 전신을 인식/추적했을 때 중앙 서버로 이벤트 전송  
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
  "category": "person",
  "unique_key": "track_006",
  "meta": {
    "distance_m": 1.8,
    "pose": {
      "x": 2.5,
      "y": -0.5,
      "yaw": 0.12
    },
    "velocity": {
      "vx": 0.3,
      "vy": 0.0,
      "vz": 0.0
    },
    "lost": false,
    "mobility_level": "normal",
    "confidence": 0.90
  },
  "detected_at": "2025-11-10T10:23:10Z",
  "processing_info": {
    "intent": "start_follow",
    "api_calls": [],
    "cmds": [
      {
        "topic": "/robot/cmd",
        "payload": {
          "type": "FOLLOW",
          "target_id": "track_006",
          "distance": 1.5
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
  "detection_event_id": "550e8400-e29b-41d4-a716-446655440003",
  "robot_id": "robot-001",
  "category": "person",
  "unique_key": "track_006",
  "meta": {
    "distance_m": 1.8,
    "pose": {
      "x": 2.5,
      "y": -0.5,
      "yaw": 0.12
    },
    "velocity": {
      "vx": 0.3,
      "vy": 0.0,
      "vz": 0.0
    },
    "lost": false,
    "mobility_level": "normal",
    "confidence": 0.90
  },
  "detected_at": "2025-11-10T10:23:10Z",
  "processing_info": {
    "intent": "start_follow",
    "api_calls": [],
    "cmds": [
      {
        "topic": "/robot/cmd",
        "payload": {
          "type": "FOLLOW",
          "target_id": "track_006",
          "distance": 1.5
        }
      }
    ],
    "scenario_state": "RUN"
  },
  "processed_status": "accepted",
  "created_at": "2025-11-10T10:23:10Z"
}
```

**400 Bad Request**
```json
{
  "detail": "Invalid RobotDetectionEvent payload"
}
```

### IF-02: 전신 레지스트리 조회

**Interface ID**: IF-PERSON-02  
**Function/Description**: 전신 레지스트리 정보 조회  
**Sender**: Robot Controller / Admin GUI  
**Receiver**: Central Server  
**Endpoint**: `/api/v1/detections/registry/person/{unique_key}`  
**Method**: `GET`

#### Request Data
- **Path Parameter**: `unique_key` (예: `track_006`)

#### Response Data / Status Code / Description

**200 OK**
```json
{
  "key": "track_006",
  "data": {
    "person_key": "track_006",
    "preferred_follow_distance_m": 1.5,
    "mobility_level": "normal",
    "action_plan": {
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
    },
    "updated_at": "2025-11-10T10:23:10Z"
  },
  "updated_at": "2025-11-10T10:23:10Z"
}
```

**404 Not Found**
```json
{
  "detail": "Registry not found: person/track_006"
}
```

---

## Central Server <-> AI Server

### IF-03: 전신 추적 시작 명령

**Interface ID**: IF-PERSON-03  
**Function/Description**: AI 서버에 전신 추적 시작 명령  
**Sender**: Central Server  
**Receiver**: AI Server  
**Endpoint**: `/start_tracking` (예상)  
**Method**: `POST`

#### Request Data
```json
{
  "robot_id": "robot-001",
  "target_id": "track_006"
}
```

#### Response Data
```json
{
  "status_code": 200,
  "message": "Tracking started"
}
```

### IF-04: 전신 추적 목표 전송

**Interface ID**: IF-PERSON-04  
**Function/Description**: AI 서버 트래킹 결과를 좌표 변환 후 로봇에 전달  
**Sender**: Central Server  
**Receiver**: Robot Controller  
**Type**: ROS2 Topic  
**Topic Name**: `/trackingGoal`  
**Message Type**: `geometry_msgs/Point`

#### Message Data
```json
{
  "x": 2.5,
  "y": -0.5,
  "z": 0.0
}
```

---

## 데이터베이스 설계

### detection_event 테이블 (공통)
- `detection_event_id`: UUID (PK)
- `robot_id`: TEXT
- `category`: TEXT ('person')
- `unique_key`: TEXT (예: 'track_006')
- `meta`: JSONB (카테고리별 부가정보)
- `detected_at`: TIMESTAMP
- `processing_info`: JSONB
- `processed_status`: TEXT
- `created_at`: TIMESTAMP

### person_registry 테이블
- `person_key`: TEXT (PK) - 개인 논리 키 (예: 'track_006')
- `preferred_follow_distance_m`: NUMERIC(4,2) - 선호 추종 거리(m) (기본값: 1.5)
- `mobility_level`: TEXT - 보행속도/주의필요 등 (예: 'normal', 'slow', 'fast')
- `action_plan`: JSONB - 기본 처리 계획
- `updated_at`: TIMESTAMP

### 인덱스
- `idx_detection_event_cat_key`: (category, unique_key)
- `idx_detection_event_robot`: (robot_id)
- `idx_detection_event_time`: (detected_at DESC)

---

## 처리 흐름

1. **로봇이 전신 인식**
   - 카메라에서 전신 감지
   - 추적 ID 할당 (예: 'track_006')
   - 위치, 속도, 거리 정보 추출

2. **중앙 서버로 이벤트 전송**
   - `POST /api/v1/detections` 호출
   - `category: "person"`, `unique_key: "track_006"` 포함
   - 헤더에 `X-Robot-ID: robot-001` 필수
   - 위치, 속도, 거리 정보 포함

3. **레지스트리 조회/업데이트**
   - `person_registry` 테이블에서 개인 정보 조회
   - 없으면 자동 생성, 있으면 업데이트
   - `meta` 필드의 `distance_m`, `mobility_level` 정보 저장
   - `preferred_follow_distance_m` 저장

4. **액션 실행**
   - `processing_info`의 `api_calls` 및 `cmds` 실행
   - 예: 로봇 추종 명령 (`intent: "start_follow"`)
   - Redis Streams를 통해 비동기 처리 (Redis가 활성화된 경우)
   - Redis가 없으면 로그만 출력

5. **처리 상태 업데이트**
   - `processed_status`: 'accepted' → 'done' / 'failed'
   - 실제 액션 실행은 별도 워커 프로세스에서 처리

---

## 샘플 시나리오

### 시나리오 1: 추종 시작

1. 로봇이 복도에서 사람 전신 인식
2. 중앙 서버로 이벤트 전송 (`intent: "start_follow"`)
3. 레지스트리에서 개인 정보 확인
4. 로봇 추종 명령 전송 (`distance: 1.5m`)
5. 로봇이 사람을 따라다님

### 시나리오 2: 추종 중단

1. 로봇이 추종 중인 사람이 사라짐 (`lost: true`)
2. 중앙 서버로 이벤트 전송 (`intent: "stop_follow"`)
3. 로봇 추종 중단 명령 전송
4. 로봇이 대기 위치로 복귀

### 시나리오 3: 거리 조정

1. 로봇이 추종 중인 사람의 보행 속도 감지
2. `mobility_level: "slow"` 감지
3. 레지스트리에서 `preferred_follow_distance_m: 1.0` 확인
4. 로봇 추종 거리 조정 명령 전송

---

## Intent 타입

### start_follow
- 추종 시작
- `cmds`에 `FOLLOW` 명령 포함
- `distance` 필드로 추종 거리 지정

### stop_follow
- 추종 중단
- `cmds`에 `STOP` 명령 포함
- 사람이 사라졌을 때 사용

### none
- 액션 없음
- 단순 추적만 수행

---

## 주의사항

1. **추적 ID**: `unique_key`는 추적 세션별로 고유해야 함
2. **거리 관리**: `preferred_follow_distance_m`로 개인별 선호 거리 저장
3. **보행 속도**: `mobility_level`로 보행 속도에 따른 추종 거리 조정
4. **사라짐 처리**: `lost: true`일 때 추종 중단 처리 필요
5. **좌표계**: `pose`는 로봇 기준 상대 좌표 또는 맵 기준 절대 좌표
6. **신뢰도**: `confidence` 값이 0.8 이상일 때만 처리 권장
7. **실시간 처리**: 추종은 실시간성이 중요하므로 지연 최소화 필요
8. **헤더 필수**: `X-Robot-ID` 헤더는 필수입니다. 누락 시 422 에러 발생
9. **액션 실행**: Redis가 활성화되어 있으면 비동기 처리, 없으면 로그만 출력

## 실제 구현 확인

### 코드 위치
- 라우터: `app/adapters/http/robot_detection_router.py`
- 액션 실행기: `app/services/robot_detection_action_executor.py`
- 유즈케이스: `app/application/use_cases/robot_detection_use_cases.py`
- 리포지토리: `app/adapters/repositories/robot_detection_repository_impl.py`

### 테스트 코드
- 통합 테스트: `tests/integration/test_robot_detection_api.py`
- 테스트 실행: `pytest tests/integration/test_robot_detection_api.py -v`

