# 배회 감지 시나리오 테스트 샘플

**작성일**: 2025-11-23  
**목적**: 배회 감지 시나리오 테스트용 완성된 JSON 샘플

---

## API 엔드포인트

```
POST /api/templates/scenario
```

---

## 기본 요청 형식

```json
{
  "scenario": "wandering_detection",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "location": "1층 복도",
    "camera_id": "camera_001"
  }
}
```

---

## 완성된 테스트 샘플

### 샘플 1: 1층 복도 배회 감지
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

**cURL 명령어:**
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

### 샘플 2: 2층 계단 배회 감지
```json
{
  "scenario": "wandering_detection",
  "nickname": "Akaza",
  "additional_data": {
    "location": "2층 계단",
    "camera_id": "camera_002"
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
    "scenario": "wandering_detection",
    "nickname": "Akaza",
    "additional_data": {
      "location": "2층 계단",
      "camera_id": "camera_002"
    }
  }'
```

---

### 샘플 3: 1층 로비 배회 감지
```json
{
  "scenario": "wandering_detection",
  "user_id": "00000000-0000-0000-0000-000000000001",
  "additional_data": {
    "location": "1층 로비",
    "camera_id": "camera_003"
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
    "scenario": "wandering_detection",
    "user_id": "00000000-0000-0000-0000-000000000001",
    "additional_data": {
      "location": "1층 로비",
      "camera_id": "camera_003"
    }
  }'
```

---

### 샘플 4: 3층 복도 배회 감지
```json
{
  "scenario": "wandering_detection",
  "nickname": "Zenitsu Agatsuma",
  "additional_data": {
    "location": "3층 복도",
    "camera_id": "camera_004"
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
    "scenario": "wandering_detection",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "location": "3층 복도",
      "camera_id": "camera_004"
    }
  }'
```

---

### 샘플 5: 지하 1층 주차장 배회 감지
```json
{
  "scenario": "wandering_detection",
  "nickname": "Akaza",
  "additional_data": {
    "location": "지하 1층 주차장",
    "camera_id": "camera_005"
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
    "scenario": "wandering_detection",
    "nickname": "Akaza",
    "additional_data": {
      "location": "지하 1층 주차장",
      "camera_id": "camera_005"
    }
  }'
```

---

## 예상 LCD 표시 내용

배회 감지 시나리오는 다음과 같은 형식으로 LCD에 표시됩니다:

```
타이틀: ⚠️ [닉네임] 어르신 발견
라인1: 위치: [탐지 위치]
라인2: 생활실: [생활실 정보]
라인3: 안전을 위해 생활실로 복귀해주세요
타임스탬프: [현재 시간]
```

**예시:**
```
⚠️ Zenitsu Agatsuma 어르신 발견
위치: 1층 복도
생활실: 3층 302호 A번
안전을 위해 생활실로 복귀해주세요
2025-11-23 15:30:00
```

---

## 필드 설명

### 필수 필드
- `scenario`: `"wandering_detection"` (고정값)
- `user_id` 또는 `nickname`: 어르신 식별자 (둘 중 하나 필수)

### additional_data 필드
- `location` (필수): 탐지된 위치 (예: "1층 복도", "2층 계단")
- `camera_id` (선택): 카메라 ID (예: "camera_001")

---

## 응답 예시

```json
{
  "success": true,
  "template": {
    "title": "⚠️ Zenitsu Agatsuma 어르신 발견",
    "lines": [
      "위치: 1층 복도",
      "생활실: 3층 302호 A번",
      "안전을 위해 생활실로 복귀해주세요"
    ],
    "show_timestamp": true
  },
  "scenario": "wandering_detection",
  "description": "배회 감지 템플릿: 어르신 정보, 현재 위치, 생활실 복귀 안내"
}
```

---

## 참고사항

1. **user_id vs nickname**: 둘 중 하나만 제공하면 됩니다. 둘 다 제공하면 `user_id`가 우선됩니다.
2. **location 필드**: 실제 탐지된 위치를 정확히 입력하세요.
3. **camera_id 필드**: 선택적이지만, 로깅 및 추적을 위해 제공하는 것을 권장합니다.
4. **LCD 표시**: 성공 시 `success: true`와 함께 LCD에 표시됩니다.

