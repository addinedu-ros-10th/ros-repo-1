# 시나리오 템플릿 테스트 샘플

**작성일**: 2025-11-23  
**목적**: DB 데이터 기반 시나리오 템플릿 테스트용 JSON 샘플

---

## 사용 방법

```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '<JSON_BODY>'
```

---

## 1. 아침인사 시나리오 (`morning_greeting`)

### 샘플 1: user_id 사용
```json
{
  "scenario": "morning_greeting",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "weather": "맑은"
  }
}
```

### 샘플 2: nickname 사용
```json
{
  "scenario": "morning_greeting",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "weather": "맑은"
  }
}
```

### 샘플 3: 날씨 없이
```json
{
  "scenario": "morning_greeting",
  "nickname": "Akaza"
}
```

### cURL 명령어
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "morning_greeting",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "weather": "맑은"
    }
  }'
```

---

## 2. 식사 지원 시나리오 (`meal_assistance`)

### 샘플 1: 점심 식사
```json
{
  "scenario": "meal_assistance",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "menu": "된장찌개",
    "meal_time": "12:00"
  }
}
```

### 샘플 2: 저녁 식사
```json
{
  "scenario": "meal_assistance",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "menu": "김치볶음밥",
    "meal_time": "18:00"
  }
}
```

### 샘플 3: 아침 식사
```json
{
  "scenario": "meal_assistance",
  "nickname": "Akaza",
  "additional_data": {
    "menu": "미역국",
    "meal_time": "08:00"
  }
}
```

### cURL 명령어
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "meal_assistance",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "menu": "된장찌개",
      "meal_time": "12:00"
    }
  }'
```

---

## 3. 맞춤형 이동식 대화 시나리오 (`conversation`)

### 샘플 1: 생활실로 이동
```json
{
  "scenario": "conversation",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "topic": "오늘 날씨 이야기",
    "destination": "3층 302호 생활실"
  }
}
```

### 샘플 2: 식당으로 이동
```json
{
  "scenario": "conversation",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "topic": "오늘 식사 메뉴",
    "destination": "1층 식당"
  }
}
```

### 샘플 3: 복도 산책
```json
{
  "scenario": "conversation",
  "nickname": "Akaza",
  "additional_data": {
    "topic": "건강 이야기",
    "destination": "2층 복도"
  }
}
```

### cURL 명령어
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "topic": "오늘 날씨 이야기",
      "destination": "3층 302호 생활실"
    }
  }'
```

---

## 4. 배회 감지 시나리오 (`wandering_detection`)

### 샘플 1: 1층 복도 탐지
```json
{
  "scenario": "wandering_detection",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "location": "1층 복도",
    "camera_id": "camera_001"
  }
}
```

### 샘플 2: 2층 계단 탐지
```json
{
  "scenario": "wandering_detection",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "location": "2층 계단",
    "camera_id": "camera_002"
  }
}
```

### 샘플 3: 로비 탐지
```json
{
  "scenario": "wandering_detection",
  "nickname": "Akaza",
  "additional_data": {
    "location": "1층 로비",
    "camera_id": "camera_003"
  }
}
```

### cURL 명령어
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "wandering_detection",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "location": "1층 복도",
      "camera_id": "camera_001"
    }
  }'
```

---

## 5. 면회객 안내 시나리오 (`visitor_guidance`)

### 샘플 1: 아들 면회
```json
{
  "scenario": "visitor_guidance",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "visitor_name": "정기우",
    "visitor_relationship": "아들",
    "meeting_room": "면회실"
  }
}
```

### 샘플 2: 딸 면회
```json
{
  "scenario": "visitor_guidance",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "visitor_name": "정미영",
    "visitor_relationship": "딸",
    "meeting_room": "면회실"
  }
}
```

### 샘플 3: 배우자 면회
```json
{
  "scenario": "visitor_guidance",
  "nickname": "Akaza",
  "additional_data": {
    "visitor_name": "김영희",
    "visitor_relationship": "배우자",
    "meeting_room": "2층 휴게실"
  }
}
```

### cURL 명령어
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "visitor_guidance",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "visitor_name": "정기우",
      "visitor_relationship": "아들",
      "meeting_room": "면회실"
    }
  }'
```

---

## 전체 테스트 스크립트

```bash
#!/bin/bash
# 시나리오 템플릿 전체 테스트

BASE_URL="http://localhost:8004/api/templates/scenario"

echo "============================================================"
echo "시나리오 템플릿 테스트"
echo "============================================================"
echo ""

# 1. 아침인사
echo "1. 아침인사 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "morning_greeting",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "weather": "맑은"
    }
  }'
echo ""
echo ""

# 2. 식사 지원
echo "2. 식사 지원 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "meal_assistance",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "menu": "된장찌개",
      "meal_time": "12:00"
    }
  }'
echo ""
echo ""

# 3. 맞춤형 이동식 대화
echo "3. 맞춤형 이동식 대화 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "topic": "오늘 날씨 이야기",
      "destination": "3층 302호 생활실"
    }
  }'
echo ""
echo ""

# 4. 배회 감지
echo "4. 배회 감지 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "wandering_detection",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "location": "1층 복도",
      "camera_id": "camera_001"
    }
  }'
echo ""
echo ""

# 5. 면회객 안내
echo "5. 면회객 안내 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "visitor_guidance",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "visitor_name": "정기우",
      "visitor_relationship": "아들",
      "meeting_room": "면회실"
    }
  }'
echo ""
echo ""

echo "============================================================"
echo "테스트 완료"
echo "============================================================"
```

---

## 참고사항

1. **user_id vs nickname**: 둘 중 하나만 제공하면 됩니다. 둘 다 제공하면 user_id가 우선됩니다.
2. **additional_data**: 시나리오별로 필요한 필드가 다릅니다. 선택적 필드는 생략 가능합니다.
3. **응답 확인**: `success: true`와 `display_sent: true`를 확인하세요.

