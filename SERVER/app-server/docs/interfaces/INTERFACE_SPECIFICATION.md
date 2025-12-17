# Interface Specification

**문서 버전**: 1.0.0  
**최종 업데이트**: 2025-11-10  
**작성자**: Development Team

## 개요

이 문서는 Central Server (App Server)와 외부 시스템 간의 인터페이스 명세를 정의합니다.

### 시스템 구성

- **Central Server**: FastAPI 기반 중앙 서버 (이 프로젝트)
- **Robot Controller**: ROS2 기반 로봇 제어 시스템
- **AI Server**: 딥러닝 모델 기반 인식 서버
- **Admin GUI**: 관리자 웹 인터페이스
- **User GUI**: 사용자 웹 인터페이스 (향후 구현)

### Base URL

- **Production**: `http(s)://<host>/api/v1`
- **Development**: `http://localhost:8000/api/v1`

---

## Robot Controller <-> Central Server

| Interface ID | Function/Description | Sender | Receiver | Endpoint | Method | Request Data | Response Data / Status Code / Description |
|-------------|---------------------|--------|----------|----------|--------|--------------|-------------------------------------------|
| IF-RC-01 | 로봇 인식 이벤트 수집 (ArUco 마커) | Robot | Central | `/api/v1/detections` | POST | `{"category": "aruco", "unique_key": "ARUCO_23", "meta": {...}, "detected_at": "2025-11-10T10:20:30Z", "processing_info": {...}}`<br>**Headers**: `X-Robot-ID: robot-001` | **201 Created**: `{"detection_event_id": "uuid", "robot_id": "robot-001", ...}`<br>**400 Bad Request**: Invalid payload<br>**422 Unprocessable Entity**: Missing X-Robot-ID header |
| IF-RC-02 | 로봇 인식 이벤트 수집 (OCR 텍스트) | Robot | Central | `/api/v1/detections` | POST | `{"category": "text", "unique_key": "식당", "meta": {...}, "detected_at": "2025-11-10T10:20:30Z", "processing_info": {...}}`<br>**Headers**: `X-Robot-ID: robot-001` | **201 Created**: Detection event response<br>**400 Bad Request**: Invalid payload |
| IF-RC-03 | 로봇 인식 이벤트 수집 (얼굴 인식) | Robot | Central | `/api/v1/detections` | POST | `{"category": "face", "unique_key": "face_hash_abc123", "meta": {...}, "detected_at": "2025-11-10T10:20:30Z", "processing_info": {...}}`<br>**Headers**: `X-Robot-ID: robot-001` | **201 Created**: Detection event response<br>**400 Bad Request**: Invalid payload |
| IF-RC-04 | 로봇 인식 이벤트 수집 (전신 추적) | Robot | Central | `/api/v1/detections` | POST | `{"category": "person", "unique_key": "person_track_001", "meta": {...}, "detected_at": "2025-11-10T10:20:30Z", "processing_info": {...}}`<br>**Headers**: `X-Robot-ID: robot-001` | **201 Created**: Detection event response<br>**400 Bad Request**: Invalid payload |
| IF-RC-05 | 인식 이벤트 목록 조회 | Robot | Central | `/api/v1/detections` | GET | **Query Params**: `?category=aruco&robot_id=robot-001&since=2025-11-10T00:00:00Z&until=2025-11-10T23:59:59Z&skip=0&limit=100` | **200 OK**: `[{"detection_event_id": "uuid", ...}, ...]`<br>**400 Bad Request**: Invalid query parameters |
| IF-RC-06 | 인식 이벤트 단건 조회 | Robot | Central | `/api/v1/detections/{event_id}` | GET | **Path Parameter**: `event_id` (UUID) | **200 OK**: `{"detection_event_id": "uuid", ...}`<br>**404 Not Found**: Event not found |
| IF-RC-07 | 레지스트리 조회 (공통) | Robot | Central | `/api/v1/detections/registry/{category}/{unique_key}` | GET | **Path Parameters**: `category` (aruco/text/face/person), `unique_key` (예: `ARUCO_23`, `식당`, face hash, person tracking ID) | **200 OK**: `{"key": "ARUCO_23", "data": {...}, "updated_at": "..."}`<br>**404 Not Found**: Registry not found |
| IF-RC-11 | 액션 실행 요청 | Robot | Central | `/api/v1/detections/actions/execute` | POST | `{"event_id": "uuid", "robot_id": "robot-001"}` | **200 OK**: `{"status": "accepted", "message": "Action queued"}`<br>**404 Not Found**: Event not found |

---

## AI Server <-> Central Server

| Interface ID | Function/Description | Sender | Receiver | Endpoint | Method | Request Data | Response Data / Status Code / Description |
|-------------|---------------------|--------|----------|----------|--------|--------------|-------------------------------------------|
| IF-AI-01 | 장애물 감지 정보 송신 | Central | AI | `/obstacle/detected` | POST | `{"robot_id": "robot-001", "left_angle": "10.0", "right_angle": "30.0", "timestamp": 1722601200}` | **200 OK**: `{"status_code": 200}`<br>**400 Bad Request**: Invalid payload |
| IF-AI-02 | 추적 시작 명령 | Central | AI | `/start_tracking` | POST | `{"robot_id": "robot-001"}` | **200 OK**: `{"status_code": 200}`<br>**400 Bad Request**: Invalid robot_id |
| IF-AI-03 | 손동작(come) 인식 이벤트 송신 | AI | Central | `/gesture/come` | POST | `{"robot_id": "robot-001", "left_angle": "10.0", "right_angle": "30.0", "timestamp": 1722601202}` | **200 OK**: `{"status_code": 200}`<br>**400 Bad Request**: Invalid payload |
| IF-AI-04 | 길안내 중 사람 사라짐 | AI | Central | `/user_disappear` | POST | `{"robot_id": "robot-001"}` | **200 OK**: `{"status_code": 200}`<br>**400 Bad Request**: Invalid robot_id |
| IF-AI-05 | 사라졌던 사람 다시 나타남 | AI | Central | `/user_appear` | POST | `{"robot_id": "robot-001"}` | **200 OK**: `{"status_code": 200}`<br>**400 Bad Request**: Invalid robot_id |

**참고**: AI Server 인터페이스는 향후 구현 예정입니다. 현재는 Central Server가 Robot Controller로부터 직접 인식 이벤트를 수신합니다.

---

## Admin GUI <-> Central Server

### ML 레지스트리 API

| Interface ID | Function/Description | Sender | Receiver | Endpoint | Method | Request Data | Response Data / Status Code / Description |
|-------------|---------------------|--------|----------|----------|--------|--------------|-------------------------------------------|
| IF-ADMIN-01 | 데이터셋 목록 조회 | GUI | Central | `/api/v1/datasets` | GET | **Query Params**: `?skip=0&limit=100` | **200 OK**: `[{"dataset_id": "uuid", "name": "...", ...}, ...]` |
| IF-ADMIN-02 | 데이터셋 단건 조회 | GUI | Central | `/api/v1/datasets/{dataset_id}` | GET | **Path Parameter**: `dataset_id` (UUID) | **200 OK**: Dataset data<br>**404 Not Found**: Dataset not found |
| IF-ADMIN-03 | 데이터셋 생성 | GUI | Central | `/api/v1/datasets` | POST | `{"name": "AIHub_Fall", "version": "v1", "storage_path": "s3://bucket/path", "class_schema": {...}, "tags": [...]}` | **201 Created**: Dataset data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-04 | 데이터셋 수정 | GUI | Central | `/api/v1/datasets/{dataset_id}` | PUT | `{"name": "...", "description": "..."}` (partial update) | **200 OK**: Updated dataset<br>**404 Not Found**: Dataset not found |
| IF-ADMIN-05 | 데이터셋 삭제 | GUI | Central | `/api/v1/datasets/{dataset_id}` | DELETE | **Path Parameter**: `dataset_id` | **204 No Content**<br>**404 Not Found**: Dataset not found |
| IF-ADMIN-06 | 데이터셋 이름으로 검색 | GUI | Central | `/api/v1/datasets/name/{name}` | GET | **Path Parameter**: `name`<br>**Query Params**: `?skip=0&limit=100` | **200 OK**: List of datasets |
| IF-ADMIN-07 | 데이터셋 태그로 필터링 | GUI | Central | `/api/v1/datasets/tag/{tag}` | GET | **Path Parameter**: `tag`<br>**Query Params**: `?skip=0&limit=100` | **200 OK**: List of datasets |
| IF-ADMIN-08 | 실험 목록 조회 | GUI | Central | `/api/v1/experiments` | GET | **Query Params**: `?skip=0&limit=100` | **200 OK**: List of experiments |
| IF-ADMIN-09 | 실험 단건 조회 | GUI | Central | `/api/v1/experiments/{experiment_id}` | GET | **Path Parameter**: `experiment_id` (UUID) | **200 OK**: Experiment data<br>**404 Not Found**: Experiment not found |
| IF-ADMIN-10 | 실험 생성 | GUI | Central | `/api/v1/experiments` | POST | `{"name": "exp-lstm-v1", "dataset_id": "uuid", "model_path": "s3://bucket/models/model.pt", "framework": "pytorch", ...}` | **201 Created**: Experiment data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-11 | 실험 수정 | GUI | Central | `/api/v1/experiments/{experiment_id}` | PUT | `{"name": "...", "metrics": {...}}` (partial update) | **200 OK**: Updated experiment<br>**404 Not Found**: Experiment not found |
| IF-ADMIN-12 | 실험 삭제 | GUI | Central | `/api/v1/experiments/{experiment_id}` | DELETE | **Path Parameter**: `experiment_id` | **204 No Content**<br>**404 Not Found**: Experiment not found |
| IF-ADMIN-13 | 데이터셋별 실험 목록 조회 | GUI | Central | `/api/v1/experiments/dataset/{dataset_id}` | GET | **Path Parameter**: `dataset_id`<br>**Query Params**: `?skip=0&limit=100` | **200 OK**: List of experiments |
| IF-ADMIN-14 | 프레임 예측 목록 조회 | GUI | Central | `/api/v1/frame-predictions` | GET | **Query Params**: `?session_id={uuid}&experiment_id={uuid}&skip=0&limit=100` | **200 OK**: List of frame predictions |
| IF-ADMIN-15 | 프레임 예측 단건 조회 | GUI | Central | `/api/v1/frame-predictions/{frame_pred_id}` | GET | **Path Parameter**: `frame_pred_id` (int) | **200 OK**: Frame prediction data<br>**404 Not Found**: Not found |
| IF-ADMIN-16 | 프레임 예측 생성 (단건) | GUI | Central | `/api/v1/frame-predictions` | POST | `{"session_id": "uuid", "experiment_id": "uuid", "input_uri": "file:///video.mp4", "frame_index": 100, "probabilities": {...}, "label_pred": "fall"}` | **201 Created**: Frame prediction data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-17 | 프레임 예측 생성 (배치) | GUI | Central | `/api/v1/frame-predictions/batch` | POST | `{"items": [{...}, {...}]}` | **201 Created**: List of frame predictions<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-18 | 프레임 예측 삭제 | GUI | Central | `/api/v1/frame-predictions/{frame_pred_id}` | DELETE | **Path Parameter**: `frame_pred_id` | **204 No Content**<br>**404 Not Found**: Not found |
| IF-ADMIN-19 | 감지 이벤트 목록 조회 | GUI | Central | `/api/v1/detection-events` | GET | **Query Params**: `?session_id={uuid}&experiment_id={uuid}&skip=0&limit=100` | **200 OK**: List of detection events |
| IF-ADMIN-20 | 감지 이벤트 단건 조회 | GUI | Central | `/api/v1/detection-events/{event_id}` | GET | **Path Parameter**: `event_id` (UUID) | **200 OK**: Detection event data<br>**404 Not Found**: Not found |
| IF-ADMIN-21 | 감지 이벤트 생성 | GUI | Central | `/api/v1/detection-events` | POST | `{"session_id": "uuid", "experiment_id": "uuid", "input_uri": "file:///video.mp4", "start_frame": 120, "end_frame": 150, "event_type": "fall_detected", "top_label": "fall", ...}` | **201 Created**: Detection event data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-22 | 감지 이벤트 삭제 | GUI | Central | `/api/v1/detection-events/{event_id}` | DELETE | **Path Parameter**: `event_id` | **204 No Content**<br>**404 Not Found**: Not found |

### 스케줄러 API

| Interface ID | Function/Description | Sender | Receiver | Endpoint | Method | Request Data | Response Data / Status Code / Description |
|-------------|---------------------|--------|----------|----------|--------|--------------|-------------------------------------------|
| IF-ADMIN-23 | 스케줄 작업 목록 조회 | GUI | Central | `/api/v1/scheduled-jobs` | GET | **Query Params**: `?enabled_only=false` | **200 OK**: `{"jobs": [...], "count": 10}` |
| IF-ADMIN-24 | 스케줄 작업 단건 조회 | GUI | Central | `/api/v1/scheduled-jobs/{job_id}` | GET | **Path Parameter**: `job_id` (string) | **200 OK**: Job data<br>**404 Not Found**: Job not found |
| IF-ADMIN-25 | 스케줄 작업 생성 | GUI | Central | `/api/v1/scheduled-jobs` | POST | `{"name": "daily_backup", "func": "app.tasks.backup:run", "cron": "0 2 * * *", "args": [], "kwargs": {}, "enabled": true}` | **200 OK**: Created job data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-26 | 스케줄 작업 수정 | GUI | Central | `/api/v1/scheduled-jobs/{job_id}` | PUT | `{"name": "...", "cron": "...", "enabled": false}` (partial update) | **200 OK**: Updated job data<br>**404 Not Found**: Job not found |
| IF-ADMIN-27 | 스케줄 작업 삭제 | GUI | Central | `/api/v1/scheduled-jobs/{job_id}` | DELETE | **Path Parameter**: `job_id` | **200 OK**: `{"message": "Job deleted successfully"}`<br>**404 Not Found**: Job not found |
| IF-ADMIN-28 | 스케줄 작업 즉시 실행 | GUI | Central | `/api/v1/scheduled-jobs/{job_id}/execute` | POST | **Path Parameter**: `job_id` | **200 OK**: `{"status": "success", "result": {...}}`<br>**404 Not Found**: Job not found |
| IF-ADMIN-29 | 스케줄러 상태 조회 | GUI | Central | `/api/v1/scheduler/status` | GET | - | **200 OK**: `{"scheduler_running": true, "active_jobs": 5, "jobs": [...], "timestamp": "..."}` |
| IF-ADMIN-30 | 스케줄러 재로드 | GUI | Central | `/api/v1/scheduler/reload` | POST | - | **200 OK**: `{"status": "success", "message": "스케줄러 재로드 완료", "timestamp": "..."}` |
| IF-ADMIN-30-1 | 내부 스케줄 작업 목록 조회 | Internal | Central | `/internal/scheduled-jobs` | GET | - | **200 OK**: Internal job list |
| IF-ADMIN-30-2 | 내부 작업 수동 실행 | Internal | Central | `/internal/scheduled-jobs/{job_id}/execute` | POST | **Path Parameter**: `job_id` | **200 OK**: Execution result |
| IF-ADMIN-30-3 | 내부 테이블 목록 조회 | Internal | Central | `/internal/tables` | GET | - | **200 OK**: Table list |
| IF-ADMIN-30-4 | 내부 데이터베이스 정보 조회 | Internal | Central | `/internal/database/info` | GET | - | **200 OK**: Database info |

### 알림 시스템 API

| Interface ID | Function/Description | Sender | Receiver | Endpoint | Method | Request Data | Response Data / Status Code / Description |
|-------------|---------------------|--------|----------|----------|--------|--------------|-------------------------------------------|
| IF-ADMIN-31 | 알림 메시지 목록 조회 | GUI | Central | `/api/v1/notify/messages` | GET | **Query Params**: `?skip=0&limit=100&kind=alert&severity=high` | **200 OK**: List of messages |
| IF-ADMIN-32 | 알림 메시지 단건 조회 | GUI | Central | `/api/v1/notify/messages/{message_id}` | GET | **Path Parameter**: `message_id` (UUID) | **200 OK**: Message data<br>**404 Not Found**: Message not found |
| IF-ADMIN-33 | 알림 메시지 생성 | GUI | Central | `/api/v1/notify/messages` | POST | `{"kind": "alert", "severity": "high", "title": "...", "body": "...", "metadata": {...}}` | **201 Created**: Message data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-34 | 알림 메시지 수정 | GUI | Central | `/api/v1/notify/messages/{message_id}` | PUT | `{"title": "...", "body": "..."}` (partial update) | **200 OK**: Updated message<br>**404 Not Found**: Message not found |
| IF-ADMIN-35 | 알림 메시지 삭제 | GUI | Central | `/api/v1/notify/messages/{message_id}` | DELETE | **Path Parameter**: `message_id` | **204 No Content**<br>**404 Not Found**: Message not found |
| IF-ADMIN-36 | 알림 디바이스 목록 조회 | GUI | Central | `/api/v1/notify/devices` | GET | **Query Params**: `?skip=0&limit=100` | **200 OK**: List of devices |
| IF-ADMIN-37 | 알림 디바이스 단건 조회 | GUI | Central | `/api/v1/notify/devices/{device_id}` | GET | **Path Parameter**: `device_id` (UUID) | **200 OK**: Device data<br>**404 Not Found**: Device not found |
| IF-ADMIN-38 | 알림 디바이스 생성 | GUI | Central | `/api/v1/notify/devices` | POST | `{"device_type": "web", "user_id": "user-001", "metadata": {...}}` | **201 Created**: Device data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-39 | 알림 디바이스 수정 | GUI | Central | `/api/v1/notify/devices/{device_id}` | PUT | `{"metadata": {...}}` (partial update) | **200 OK**: Updated device<br>**404 Not Found**: Device not found |
| IF-ADMIN-40 | 알림 디바이스 삭제 | GUI | Central | `/api/v1/notify/devices/{device_id}` | DELETE | **Path Parameter**: `device_id` | **204 No Content**<br>**404 Not Found**: Device not found |
| IF-ADMIN-41 | 알림 전송 목록 조회 | GUI | Central | `/api/v1/notify/deliveries` | GET | **Query Params**: `?skip=0&limit=100&message_id={uuid}&device_id={uuid}` | **200 OK**: List of deliveries |
| IF-ADMIN-42 | 알림 전송 단건 조회 | GUI | Central | `/api/v1/notify/deliveries/{delivery_id}` | GET | **Path Parameter**: `delivery_id` (UUID) | **200 OK**: Delivery data<br>**404 Not Found**: Delivery not found |
| IF-ADMIN-43 | 알림 전송 생성 | GUI | Central | `/api/v1/notify/deliveries` | POST | `{"message_id": "uuid", "device_id": "uuid", "scheduled_at": "2025-11-10T10:00:00Z"}` | **201 Created**: Delivery data<br>**400 Bad Request**: Invalid payload |
| IF-ADMIN-44 | 알림 전송 수정 | GUI | Central | `/api/v1/notify/deliveries/{delivery_id}` | PUT | `{"status": "sent", "sent_at": "2025-11-10T10:00:01Z"}` | **200 OK**: Updated delivery<br>**404 Not Found**: Delivery not found |
| IF-ADMIN-45 | 알림 전송 삭제 | GUI | Central | `/api/v1/notify/deliveries/{delivery_id}` | DELETE | **Path Parameter**: `delivery_id` | **204 No Content**<br>**404 Not Found**: Delivery not found |
| IF-ADMIN-46 | 알림 읽음 처리 | GUI | Central | `/api/v1/notify/deliveries/{delivery_id}/read` | POST | **Path Parameter**: `delivery_id` | **200 OK**: `{"status": "read", "read_at": "..."}`<br>**404 Not Found**: Delivery not found |
| IF-ADMIN-47 | 알림 확인 처리 | GUI | Central | `/api/v1/notify/deliveries/{delivery_id}/ack` | POST | **Path Parameter**: `delivery_id` | **200 OK**: `{"status": "acknowledged", "ack_at": "..."}`<br>**404 Not Found**: Delivery not found |
| IF-ADMIN-48 | 알림 큐에 추가 | GUI | Central | `/api/v1/notify/queue` | POST | `{"message_id": "uuid", "device_ids": ["uuid1", "uuid2"], "priority": 1}` | **201 Created**: Queue data<br>**400 Bad Request**: Invalid payload |

### 시스템 정보 API

| Interface ID | Function/Description | Sender | Receiver | Endpoint | Method | Request Data | Response Data / Status Code / Description |
|-------------|---------------------|--------|----------|----------|--------|--------------|-------------------------------------------|
| IF-ADMIN-49 | 루트 엔드포인트 (시스템 정보) | GUI | Central | `/` | GET | - | **200 OK**: `{"message": "...", "version": "1.0.0", "status": "running", "docs": "/docs", "admin": "/admin", ...}` |
| IF-ADMIN-50 | 헬스 체크 | GUI | Central | `/health` | GET | - | **200 OK**: `{"status": "healthy", "service": "...", "version": "1.0.0", ...}` |
| IF-ADMIN-51 | 데이터베이스 테이블 목록 조회 | GUI | Central | `/api/v1/tables` | GET | - | **200 OK**: `{"tables": [...], "count": 35, "timestamp": "..."}` |
| IF-ADMIN-52 | 데이터베이스 정보 조회 | GUI | Central | `/api/v1/database/info` | GET | - | **200 OK**: Database connection info |
| IF-ADMIN-53 | 관리자 패널 정보 조회 | GUI | Central | `/api/v1/admin/info` | GET | - | **200 OK**: Admin panel info |
| IF-ADMIN-54 | 아키텍처 정보 조회 | GUI | Central | `/api/v1/architecture/info` | GET | - | **200 OK**: Architecture info |

### WebSocket API

| Interface ID | Function/Description | Sender | Receiver | Endpoint | Method | Request Data | Response Data / Status Code / Description |
|-------------|---------------------|--------|----------|----------|--------|--------------|-------------------------------------------|
| IF-ADMIN-55 | WebSocket 알림 연결 | GUI | Central | `/ws` | WebSocket | **Query Params**: `?user_id=user-001` | **WebSocket Connection**: 실시간 알림 수신<br>**400 Bad Request**: Missing user_id |

---

## User GUI <-> Central Server

**참고**: User GUI 인터페이스는 향후 구현 예정입니다. 현재는 Robot Controller가 직접 Central Server와 통신합니다.

---

## 공통 사항

### 인증

- **Header**: `X-Robot-ID: <robot_id>` (로봇 인식 API 필수)
- **Header**: `Authorization: Bearer <token>` (향후 구현 예정)

### 에러 응답 형식

**400 Bad Request**
```json
{
  "detail": "Invalid payload or validation error"
}
```

**404 Not Found**
```json
{
  "detail": "Resource not found"
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

**500 Internal Server Error**
```json
{
  "detail": "Internal server error: <error message>"
}
```

### 데이터 형식

- **날짜/시간**: ISO 8601 형식 (예: `2025-11-10T10:20:30Z`)
- **UUID**: 표준 UUID 형식 (예: `550e8400-e29b-41d4-a716-446655440000`)
- **JSON**: 모든 요청/응답은 JSON 형식

---

## 구현 확인

### 코드 위치

- **로봇 인식 API**: `app/adapters/http/robot_detection_router.py`
- **ML 레지스트리 API**: 
  - `app/adapters/http/dataset_router.py`
  - `app/adapters/http/experiment_router.py`
  - `app/adapters/http/frame_prediction_router.py`
  - `app/adapters/http/detection_event_router.py`
- **스케줄러 API**: `app/adapters/http/scheduled_job_controller.py`, `app/scheduler_app.py`
- **알림 API**: 
  - `app/adapters/http/notify_message_router.py`
  - `app/adapters/http/notify_device_router.py`
  - `app/adapters/http/notify_delivery_router.py`
  - `app/adapters/http/notify_queue_router.py`
- **WebSocket**: `app/adapters/http/ws_router.py`
- **메인 앱**: `app/main.py`

### 테스트

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **통합 테스트**: `tests/integration/`

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0.0 | 2025-11-10 | 초기 버전 작성 | Development Team |

---

## 관련 문서

- [로봇 인식 인터페이스 상세](./README.md)
- [ArUco 마커 인터페이스](./aruco_marker.md)
- [OCR 텍스트 인터페이스](./ocr_text.md)
- [얼굴 인식 인터페이스](./face_recognition.md)
- [전신 추적 인터페이스](./person_tracking.md)
- [API 문서](../apis/)
- [데이터베이스 스키마](../database/robot_detection_schema.md)

