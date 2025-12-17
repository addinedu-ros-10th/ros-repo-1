# /api/v1/notify/queue API 사용법

## 개요

`/api/v1/notify/queue` API는 알림 메시지를 생성하고 큐에 추가하는 엔드포인트입니다.

## 엔드포인트 정보

- **URL**: `POST /api/v1/notify/queue`
- **Base URL**: `http://localhost:8000` (또는 서버 주소)
- **Content-Type**: `application/json`
- **응답 코드**: `201 Created`

## 요청 스키마 (NotifyQueueRequest)

```json
{
  "kind": "string",              // 필수: 알림 종류 (notify.kind_enum)
  "severity": "string",           // 선택: 심각도 (기본값: "green", notify.severity_enum)
  "title": "string",             // 선택: 제목
  "body": "string",              // 선택: 본문
  "data": {},                    // 선택: 추가 데이터 (JSON 객체)
  "scheduled_at": "datetime",    // 선택: 예약 시간 (ISO 8601)
  "expires_at": "datetime",      // 선택: 만료 시간 (ISO 8601, None → 무기한)
  "recipients": ["uuid"],        // 필수: 수신자 UUID 리스트
  "channel": "string",           // 선택: 채널 (기본값: "websocket", notify.channel_enum)
  "created_by": "uuid",          // 선택: 생성자 UUID
  "created_ip": "string"         // 선택: 생성자 IP 주소
}
```

## 응답 스키마 (NotifyQueueResponse)

```json
{
  "message_id": "uuid",          // 생성된 메시지 ID
  "queued_count": 0              // 큐에 추가된 개수
}
```

## 사용 예시

### 기본 사용법 (curl)

```bash
curl -X POST "http://localhost:8000/api/v1/notify/queue" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "info",
    "severity": "green",
    "title": "Hello",
    "body": "From curl",
    "data": {"k": 1},
    "recipients": ["11111111-1111-1111-1111-111111111111"],
    "channel": "websocket"
  }'
```

### Python 예시

```python
import requests
import uuid

url = "http://localhost:8000/api/v1/notify/queue"
payload = {
    "kind": "info",
    "severity": "green",
    "title": "알림 제목",
    "body": "알림 본문 내용",
    "data": {
        "custom_field": "custom_value",
        "timestamp": "2025-11-22T13:00:00Z"
    },
    "recipients": [
        str(uuid.UUID("11111111-1111-1111-1111-111111111111"))
    ],
    "channel": "websocket"
}

response = requests.post(url, json=payload)
print(response.status_code)  # 201
print(response.json())
# {
#   "message_id": "550e8400-e29b-41d4-a716-446655440000",
#   "queued_count": 1
# }
```

### JavaScript/TypeScript 예시

```javascript
const url = 'http://localhost:8000/api/v1/notify/queue';
const payload = {
  kind: 'info',
  severity: 'green',
  title: '알림 제목',
  body: '알림 본문 내용',
  data: {
    customField: 'customValue',
    timestamp: new Date().toISOString()
  },
  recipients: ['11111111-1111-1111-1111-111111111111'],
  channel: 'websocket'
};

fetch(url, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(payload)
})
  .then(response => response.json())
  .then(data => {
    console.log('Message ID:', data.message_id);
    console.log('Queued count:', data.queued_count);
  });
```

## 필드 설명

### kind (필수)
알림 종류를 나타내는 문자열입니다. `notify.kind_enum`에 정의된 값 중 하나여야 합니다.

### severity (선택)
알림의 심각도를 나타냅니다. 기본값은 `"green"`입니다.
- `notify.severity_enum`에 정의된 값 사용

### title (선택)
알림의 제목입니다.

### body (선택)
알림의 본문 내용입니다.

### data (선택)
추가 데이터를 담는 JSON 객체입니다. 자유롭게 정의할 수 있습니다.

### scheduled_at (선택)
알림을 예약할 시간입니다. ISO 8601 형식의 datetime 문자열입니다.
- 예: `"2025-11-22T14:00:00Z"`

### expires_at (선택)
알림의 만료 시간입니다. ISO 8601 형식의 datetime 문자열입니다.
- `None` 또는 생략 시 무기한 유효

### recipients (필수)
수신자 UUID 리스트입니다. 최소 1개 이상의 UUID가 필요합니다.

### channel (선택)
알림을 전송할 채널입니다. 기본값은 `"websocket"`입니다.
- `notify.channel_enum`에 정의된 값 사용

### created_by (선택)
알림을 생성한 사용자의 UUID입니다.

### created_ip (선택)
알림을 생성한 IP 주소입니다.

## 동작 방식

1. **메시지 생성**: 요청 데이터를 기반으로 `notify_message` 테이블에 메시지가 생성됩니다.
2. **큐잉**: 각 `recipients`와 `channel` 조합에 대해 `notify_delivery` 테이블에 `status='queued'` 상태로 레코드가 생성됩니다.
3. **디스패처 처리**: 백그라운드 디스패처가 큐에 있는 알림을 처리하여 실제 전송을 수행합니다.
4. **WebSocket 전송**: `channel='websocket'`인 경우, WebSocket을 통해 클라이언트에 실시간으로 전달됩니다.

## 상태 전이

알림은 다음 상태로 전이됩니다:
- `queued` → `sent` → `delivered`

## 에러 처리

### 400 Bad Request
- 잘못된 요청 데이터
- 필수 필드 누락
- 잘못된 UUID 형식
- 잘못된 enum 값

### 예시
```json
{
  "detail": "Invalid kind value"
}
```

## 사전 조건

### 환경 변수 설정
다음 환경 변수가 설정되어 있어야 합니다:
- `NOTIFY_ENABLE=true`
- `NOTIFY_DISPATCH_ENABLE=true`
- `NOTIFY_WS_ENABLE=true`

### 데이터베이스
- `notify_message` 테이블
- `notify_delivery` 테이블
- `notify_device` 테이블

## 관련 엔드포인트

- `POST /api/v1/notify/deliveries/{delivery_id}/read`: 읽음 처리
- `POST /api/v1/notify/deliveries/{delivery_id}/ack`: 확인 처리

## 참고 문서

- `SERVER/app-server/staging/notify_testing_guide.md`: 테스트 가이드
- `SERVER/app-server/docs/notification_system_usage_guide.md`: 알림 시스템 사용 가이드
- `SERVER/app-server/docs/notification_system_development.md`: 개발 문서

## 예시 시나리오

### 시나리오 1: 단일 사용자에게 정보 알림 전송

```bash
curl -X POST "http://localhost:8000/api/v1/notify/queue" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "info",
    "title": "시스템 점검 안내",
    "body": "오늘 오후 2시부터 30분간 시스템 점검이 진행됩니다.",
    "recipients": ["11111111-1111-1111-1111-111111111111"],
    "channel": "websocket"
  }'
```

### 시나리오 2: 여러 사용자에게 경고 알림 전송

```bash
curl -X POST "http://localhost:8000/api/v1/notify/queue" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "warning",
    "severity": "yellow",
    "title": "배회 탐지",
    "body": "어르신이 생활실 밖에서 탐지되었습니다.",
    "data": {
      "resident_id": "22222222-2222-2222-2222-222222222222",
      "location": "1층 복도",
      "timestamp": "2025-11-22T13:00:00Z"
    },
    "recipients": [
      "11111111-1111-1111-1111-111111111111",
      "33333333-3333-3333-3333-333333333333"
    ],
    "channel": "websocket"
  }'
```

### 시나리오 3: 예약된 알림

```bash
curl -X POST "http://localhost:8000/api/v1/notify/queue" \
  -H "Content-Type: application/json" \
  -d '{
    "kind": "info",
    "title": "식사 시간 안내",
    "body": "곧 점심 식사 시간입니다.",
    "scheduled_at": "2025-11-22T12:00:00Z",
    "recipients": ["11111111-1111-1111-1111-111111111111"],
    "channel": "websocket"
  }'
```

