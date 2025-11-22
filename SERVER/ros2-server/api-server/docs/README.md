# ROS2 API Server 문서

## 시나리오 템플릿 가이드

### 📋 주요 문서

1. **[시나리오 템플릿 테스트 샘플 가이드](./SCENARIO_TEMPLATE_TEST_SAMPLES.md)**
   - 모든 시나리오 타입의 테스트 샘플
   - cURL 명령어 예시
   - 전체 테스트 스크립트

2. **[배회 감지 시나리오 샘플](./WANDERING_DETECTION_SAMPLES.md)**
   - 배회 감지 시나리오 상세 가이드
   - 다양한 위치별 샘플
   - LCD 표시 예시

3. **[맞춤형 이동식 대화 시나리오 샘플](./CONVERSATION_SAMPLES.md)**
   - 맞춤형 이동식 대화 시나리오 상세 가이드
   - 다양한 주제 및 목적지 샘플
   - LCD 표시 예시

### 🚀 빠른 시작

#### 1. 아침인사
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

#### 2. 식사 지원
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

#### 3. 배회 감지
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

#### 4. 맞춤형 이동식 대화
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

#### 5. 면회객 안내
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

### 📄 기타 문서

- [테스트 가이드](./TESTING_GUIDE.md)
- [ROS2 연결 문제 해결](./ROS2_CONNECTION_TROUBLESHOOTING.md)
- [스탠드얼론 실행 가이드](./STANDALONE_RUN_GUIDE.md)
- [환경 변수 가이드](./ENV_VARIABLES_GUIDE.md)
