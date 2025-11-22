# LCD 표시 템플릿 사용 가이드

**작성일**: 2025-01-22  
**API 서버**: ROS2 API Server

---

## 개요

ROS2 API Server는 다양한 상황에 맞는 LCD 표시 템플릿을 제공합니다. 각 시나리오별로 적절한 템플릿을 선택하여 사용할 수 있습니다.

---

## 시나리오별 템플릿 사용법

### 1. 아침인사 시나리오 (`morning_greeting`)

**목적**: 로봇이 어르신을 처음 만나거나 아침에 인사할 때

**엔드포인트**: `POST /api/templates/scenario`

**요청 예시**:
```json
{
  "scenario": "morning_greeting",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "weather": "맑은"
  }
}
```

**또는 nickname 사용**:
```json
{
  "scenario": "morning_greeting",
  "nickname": "Akaza",
  "additional_data": {
    "weather": "맑은"
  }
}
```

**LCD 표시 예시**:
```
타이틀: 안녕하세요! Akaza 어르신
라인1: 오늘은 2025년 1월 22일
라인2: 화요일, 맑은 날씨입니다
라인3: 좋은 하루 되세요!
타임스탬프: 2025-01-22 08:00:00
```

**추가 데이터 필드**:
- `weather` (선택적): 날씨 정보 (예: "맑은", "흐린", "비")

**cURL 예시**:
```bash
curl -X POST "http://localhost:8003/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "morning_greeting",
    "nickname": "Akaza",
    "additional_data": {
      "weather": "맑은"
    }
  }'
```

---

### 2. 식사 지원 시나리오 (`meal_assistance`)

**목적**: 식사 시간에 어르신을 도와주거나 식사 정보를 안내할 때

**요청 예시**:
```json
{
  "scenario": "meal_assistance",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "menu": "된장찌개",
    "meal_time": "12:00"
  }
}
```

**LCD 표시 예시**:
```
타이틀: 식사 시간입니다
라인1: 오늘의 메뉴: 된장찌개
라인2: 저염식, 당뇨식 준비
라인3: 천천히 드세요
타임스탬프: 2025-01-22 12:00:00
```

**추가 데이터 필드**:
- `menu` (필수): 오늘의 식사 메뉴
- `meal_time` (선택적): 식사 시간 (예: "12:00")

**cURL 예시**:
```bash
curl -X POST "http://localhost:8003/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "meal_assistance",
    "nickname": "Akaza",
    "additional_data": {
      "menu": "된장찌개",
      "meal_time": "12:00"
    }
  }'
```

---

### 3. 맞춤형 이동식 대화 시나리오 (`conversation`)

**목적**: 로봇이 어르신과 함께 이동하면서 대화할 때

**요청 예시**:
```json
{
  "scenario": "conversation",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "topic": "오늘 날씨 이야기",
    "destination": "3층 302호 생활실"
  }
}
```

**LCD 표시 예시**:
```
타이틀: Akaza 어르신과 대화 중
라인1: 주제: 오늘 날씨 이야기
라인2: 목적지: 3층 302호 생활실
라인3: 천천히 걸어가세요
타임스탬프: 2025-01-22 14:30:00
```

**추가 데이터 필드**:
- `topic` (필수): 현재 대화 주제
- `destination` (필수): 이동 목적지

**cURL 예시**:
```bash
curl -X POST "http://localhost:8003/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "conversation",
    "nickname": "Akaza",
    "additional_data": {
      "topic": "오늘 날씨 이야기",
      "destination": "3층 302호 생활실"
    }
  }'
```

---

### 4. 배회 감지 시나리오 (`wandering_detection`)

**목적**: DL YOLO가 어르신의 배회를 감지했을 때

**요청 예시**:
```json
{
  "scenario": "wandering_detection",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "location": "1층 복도",
    "camera_id": "camera_001"
  }
}
```

**LCD 표시 예시**:
```
타이틀: ⚠️ Akaza 어르신 발견
라인1: 위치: 1층 복도
라인2: 생활실: 3층 302호 A번
라인3: 안전을 위해 생활실로 복귀해주세요
타임스탬프: 2025-01-22 15:30:00
```

**추가 데이터 필드**:
- `location` (필수): 탐지 위치 (예: "1층 복도")
- `camera_id` (선택적): 카메라 ID

**cURL 예시**:
```bash
curl -X POST "http://localhost:8003/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "wandering_detection",
    "nickname": "Akaza",
    "additional_data": {
      "location": "1층 복도",
      "camera_id": "camera_001"
    }
  }'
```

**참고**: 이 시나리오는 `/api/detection/resident` 엔드포인트를 사용하는 것이 더 적합할 수 있습니다.

---

### 5. 면회객 안내 시나리오 (`visitor_guidance`)

**목적**: 면회객이 방문했을 때 어르신을 안내하거나 면회객 정보를 표시할 때

**요청 예시**:
```json
{
  "scenario": "visitor_guidance",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "visitor_name": "정기우",
    "visitor_relationship": "아들",
    "meeting_room": "면회실"
  }
}
```

**LCD 표시 예시**:
```
타이틀: 면회객 안내
라인1: 방문자: 정기우 (아들)
라인2: Akaza 어르신 면회
라인3: 면회실로 안내 중
타임스탬프: 2025-01-22 16:00:00
```

**추가 데이터 필드**:
- `visitor_name` (필수): 면회객 이름
- `visitor_relationship` (필수): 면회객 관계 (예: "아들", "딸", "배우자")
- `meeting_room` (선택적): 면회 장소 (기본값: "면회실")

**cURL 예시**:
```bash
curl -X POST "http://localhost:8003/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "visitor_guidance",
    "nickname": "Akaza",
    "additional_data": {
      "visitor_name": "정기우",
      "visitor_relationship": "아들",
      "meeting_room": "면회실"
    }
  }'
```

---

## 어르신 탐지 API (`/api/detection/resident`)

DL 컴포넌트가 어르신을 탐지했을 때 사용하는 전용 엔드포인트입니다.

**엔드포인트**: `POST /api/detection/resident`

**요청 예시**:
```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "nickname": "Akaza",
  "detection_location": "1층 복도",
  "detection_confidence": 0.95,
  "camera_id": "camera_001",
  "timestamp": "2025-01-22T10:30:00Z",
  "display_format": "basic"
}
```

**응답 예시**:
```json
{
  "success": true,
  "message": "Resident information displayed on LCD",
  "data": {
    "user_id": "00000000-0000-0000-0000-000000000001",
    "name": "정도현",
    "nickname": "Akaza",
    "room": "3층 302호 A번",
    "display_sent": true,
    "lcd_display_data": {
      "title": "Akaza 어르신",
      "lines": [
        "생활실: 3층 302호 A번",
        "상태: 보행기 사용",
        "주의: 낙상 위험 높음"
      ],
      "show_timestamp": true
    }
  }
}
```

**표시 형식 옵션**:
- `basic`: 기본 형식 (3줄)
- `detailed`: 상세 형식 (5줄)
- `urgent`: 긴급 형식 (⚠️ 표시)

**cURL 예시**:
```bash
curl -X POST "http://localhost:8003/api/detection/resident" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001",
    "display_format": "basic"
  }'
```

---

## Python 클라이언트 예시

```python
import httpx

async def display_morning_greeting(nickname: str, weather: str = "맑은"):
    """아침인사 표시"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8003/api/templates/scenario",
            json={
                "scenario": "morning_greeting",
                "nickname": nickname,
                "additional_data": {
                    "weather": weather
                }
            }
        )
        return response.json()

async def detect_resident(nickname: str, location: str, confidence: float):
    """어르신 탐지 및 LCD 표시"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8003/api/detection/resident",
            json={
                "nickname": nickname,
                "detection_location": location,
                "detection_confidence": confidence,
                "camera_id": "camera_001",
                "display_format": "basic"
            }
        )
        return response.json()
```

---

## 에러 처리

### 400 Bad Request
- `user_id`와 `nickname`이 모두 없는 경우
- 필수 `additional_data` 필드가 누락된 경우
- 알 수 없는 시나리오 타입

### 404 Not Found
- 어르신 정보를 찾을 수 없는 경우

### 500 Internal Server Error
- iot-data-server API 호출 실패
- ROS2 서비스 호출 실패
- 기타 서버 오류

---

## 템플릿 선택 가이드

| 상황 | 권장 엔드포인트 | 시나리오 타입 |
|------|---------------|-------------|
| DL 탐지 | `/api/detection/resident` | - |
| 아침 인사 | `/api/templates/scenario` | `morning_greeting` |
| 식사 시간 | `/api/templates/scenario` | `meal_assistance` |
| 이동 중 대화 | `/api/templates/scenario` | `conversation` |
| 배회 감지 | `/api/detection/resident` 또는 `/api/templates/scenario` | `wandering_detection` |
| 면회객 방문 | `/api/templates/scenario` | `visitor_guidance` |

---

## 추가 정보

- API 문서: `http://localhost:8003/docs`
- 헬스 체크: `http://localhost:8003/health`
- 상세 템플릿 설명: `../docs/LCD_DISPLAY_SCENARIO_TEMPLATES.md`

