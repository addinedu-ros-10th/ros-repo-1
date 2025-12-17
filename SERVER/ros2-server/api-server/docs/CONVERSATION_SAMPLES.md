# 맞춤형 이동식 대화 시나리오 테스트 샘플

**작성일**: 2025-11-23  
**목적**: 맞춤형 이동식 대화 시나리오 테스트용 완성된 JSON 샘플

---

## API 엔드포인트

```
POST /api/templates/scenario
```

---

## 기본 요청 형식

```json
{
  "scenario": "conversation",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "topic": "오늘 날씨 이야기",
    "destination": "3층 302호 생활실"
  }
}
```

---

## 완성된 테스트 샘플

### 샘플 1: 생활실로 이동하며 날씨 이야기
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

**cURL 명령어:**
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

### 샘플 2: 식당으로 이동하며 식사 메뉴 이야기
```json
{
  "scenario": "conversation",
  "nickname": "Akaza",
  "additional_data": {
    "topic": "오늘 식사 메뉴",
    "destination": "1층 식당"
  }
}
```

**cURL 명령어:**
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Akaza",
    "additional_data": {
      "topic": "오늘 식사 메뉴",
      "destination": "1층 식당"
    }
  }'
```

---

### 샘플 3: 복도 산책하며 건강 이야기
```json
{
  "scenario": "conversation",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "topic": "건강 이야기",
    "destination": "2층 복도"
  }
}
```

**cURL 명령어:**
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "user_id": "00000000-0000-0000-0000-000000000001",
    "additional_data": {
      "topic": "건강 이야기",
      "destination": "2층 복도"
    }
  }'
```

---

### 샘플 4: 휴게실로 이동하며 가족 이야기
```json
{
  "scenario": "conversation",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "topic": "가족 이야기",
    "destination": "2층 휴게실"
  }
}
```

**cURL 명령어:**
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "topic": "가족 이야기",
      "destination": "2층 휴게실"
    }
  }'
```

---

### 샘플 5: 면회실로 이동하며 옛날 이야기
```json
{
  "scenario": "conversation",
  "nickname": "Akaza",
  "additional_data": {
    "topic": "옛날 이야기",
    "destination": "1층 면회실"
  }
}
```

**cURL 명령어:**
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Akaza",
    "additional_data": {
      "topic": "옛날 이야기",
      "destination": "1층 면회실"
    }
  }'
```

---

### 샘플 6: 운동실로 이동하며 운동 이야기
```json
{
  "scenario": "conversation",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "topic": "운동 이야기",
    "destination": "지하 1층 운동실"
  }
}
```

**cURL 명령어:**
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "topic": "운동 이야기",
      "destination": "지하 1층 운동실"
    }
  }'
```

---

### 샘플 7: 정원으로 이동하며 자연 이야기
```json
{
  "scenario": "conversation",
  "nickname": "Akaza",
  "additional_data": {
    "topic": "자연 이야기",
    "destination": "1층 정원"
  }
}
```

**cURL 명령어:**
```bash
curl -X 'POST' \
  'http://localhost:8004/api/templates/scenario' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Akaza",
    "additional_data": {
      "topic": "자연 이야기",
      "destination": "1층 정원"
    }
  }'
```

---

## 예상 LCD 표시 내용

맞춤형 이동식 대화 시나리오는 다음과 같은 형식으로 LCD에 표시됩니다:

```
타이틀: [닉네임] 어르신과 대화 중
라인1: 주제: [대화 주제]
라인2: 목적지: [이동 목적지]
라인3: 천천히 걸어가세요
타임스탬프: [현재 시간]
```

**예시:**
```
Zenitsu Agatsuma 어르신과 대화 중
주제: 오늘 날씨 이야기
목적지: 3층 302호 생활실
천천히 걸어가세요
2025-11-23 14:30:00
```

---

## 필드 설명

### 필수 필드
- `scenario`: `"conversation"` (고정값)
- `user_id` 또는 `nickname`: 어르신 식별자 (둘 중 하나 필수)

### additional_data 필드
- `topic` (필수): 현재 대화 주제 (예: "오늘 날씨 이야기", "건강 이야기")
- `destination` (필수): 이동 목적지 (예: "3층 302호 생활실", "1층 식당")

---

## 대화 주제 예시

다양한 대화 주제를 사용할 수 있습니다:

- **일상 주제**: "오늘 날씨 이야기", "오늘 식사 메뉴", "오늘 일정"
- **건강 주제**: "건강 이야기", "운동 이야기", "약 복용 이야기"
- **추억 주제**: "옛날 이야기", "가족 이야기", "추억 이야기"
- **취미 주제**: "취미 이야기", "책 이야기", "음악 이야기"
- **자연 주제**: "자연 이야기", "계절 이야기", "꽃 이야기"

---

## 목적지 예시

다양한 목적지를 사용할 수 있습니다:

- **생활실**: "3층 302호 생활실", "2층 201호 생활실"
- **공용 공간**: "1층 식당", "2층 휴게실", "1층 로비"
- **특수 공간**: "1층 면회실", "지하 1층 운동실", "1층 정원"
- **복도**: "2층 복도", "3층 복도"

---

## 응답 예시

```json
{
  "success": true,
  "template": {
    "title": "Zenitsu Agatsuma 어르신과 대화 중",
    "lines": [
      "주제: 오늘 날씨 이야기",
      "목적지: 3층 302호 생활실",
      "천천히 걸어가세요"
    ],
    "show_timestamp": true
  },
  "scenario": "conversation",
  "description": "맞춤형 이동식 대화 템플릿: 현재 대화 주제, 이동 목적지, 안전 주의사항 표시"
}
```

---

## 참고사항

1. **user_id vs nickname**: 둘 중 하나만 제공하면 됩니다. 둘 다 제공하면 `user_id`가 우선됩니다.
2. **topic 필드**: 어르신과의 대화 주제를 명확하게 입력하세요.
3. **destination 필드**: 실제 이동 목적지를 정확히 입력하세요.
4. **LCD 표시**: 성공 시 `success: true`와 함께 LCD에 표시됩니다.
5. **안전 주의**: 이동 중 안전을 위해 "천천히 걸어가세요" 메시지가 자동으로 포함됩니다.

