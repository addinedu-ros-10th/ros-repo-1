# ROS2 API Server 테스트 가이드

**작성일**: 2025-01-22  
**목적**: ROS2 API Server의 다양한 테스트 방법 가이드

---

## 목차

1. [테스트 환경 준비](#테스트-환경-준비)
2. [기본 헬스 체크](#기본-헬스-체크)
3. [어르신 탐지 API 테스트](#어르신-탐지-api-테스트)
4. [시나리오 템플릿 API 테스트](#시나리오-템플릿-api-테스트)
5. [통합 테스트](#통합-테스트)
6. [실제 ROS2 환경 테스트](#실제-ros2-환경-테스트)
7. [문제 해결](#문제-해결)

---

## 테스트 환경 준비

### 1. 환경 변수 설정

```bash
cd SERVER/ros2-server/api-server
cp .env.example .env.local
```

`.env.local` 파일 편집:
```bash
# iot-data-server URL 설정 (실제 서버 주소로 변경)
IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com
# 또는 로컬 테스트
# IOT_DATA_SERVER_URL=http://localhost:8000

# ROS2 설정 (ROS2 환경이 없는 경우 모킹 모드로 동작)
ROS2_NAMESPACE=/pinky
ROS2_SERVICE_TIMEOUT=2.0

# Redis (선택적)
REDIS_ENABLED=false
```

### 2. 서버 실행 방법

#### 방법 1: Docker Compose (권장)

```bash
cd SERVER/ros2-server/api-server
docker-compose up -d
```

서버 로그 확인:
```bash
docker-compose logs -f ros2-api-server
```

#### 방법 2: 로컬 개발 환경

```bash
cd SERVER/ros2-server/api-server

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 기본 헬스 체크

### 1. 서버 상태 확인

```bash
# HTTP 요청
curl http://localhost:8003/health

# 또는 브라우저에서
# http://localhost:8003/health
```

**예상 응답**:
```json
{
  "status": "healthy",
  "services": {
    "ros2": false,  // ROS2 환경이 없으면 false
    "iot_data_server": true
  },
  "timestamp": "2025-01-22T10:30:00"
}
```

### 2. API 문서 확인

브라우저에서 `http://localhost:8003/docs` 접속

Swagger UI에서 모든 API 엔드포인트를 확인하고 테스트할 수 있습니다.

---

## 어르신 탐지 API 테스트

### 1. 기본 테스트 (nickname 사용)

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

### 2. user_id 사용 테스트

```bash
curl -X POST "http://localhost:8003/api/detection/resident" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000001",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001",
    "display_format": "detailed"
  }'
```

### 3. 긴급 형식 테스트

```bash
curl -X POST "http://localhost:8003/api/detection/resident" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001",
    "display_format": "urgent"
  }'
```

### 4. 예상 응답

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

---

## 시나리오 템플릿 API 테스트

### 1. 아침인사 시나리오

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

**예상 응답**:
```json
{
  "success": true,
  "template": {
    "title": "안녕하세요! Akaza 어르신",
    "lines": [
      "오늘은 2025년 1월 22일",
      "화요일, 맑은 날씨입니다",
      "좋은 하루 되세요!"
    ],
    "show_timestamp": true
  },
  "scenario": "morning_greeting",
  "description": "아침인사 템플릿: 친근한 인사와 함께 오늘의 날짜, 날씨 등 기본 정보 제공"
}
```

### 2. 식사 지원 시나리오

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

### 3. 맞춤형 이동식 대화 시나리오

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

### 4. 배회 감지 시나리오

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

### 5. 면회객 안내 시나리오

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

## 통합 테스트

### Python 테스트 스크립트

`api-server/tests/test_api_integration.py` 파일 생성:

```python
import httpx
import asyncio
import json

BASE_URL = "http://localhost:8003"

async def test_health_check():
    """헬스 체크 테스트"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/health")
        print("헬스 체크:", response.json())
        assert response.status_code == 200

async def test_detection_resident():
    """어르신 탐지 API 테스트"""
    async with httpx.AsyncClient() as client:
        data = {
            "nickname": "Akaza",
            "detection_location": "1층 복도",
            "detection_confidence": 0.95,
            "camera_id": "camera_001",
            "display_format": "basic"
        }
        response = await client.post(
            f"{BASE_URL}/api/detection/resident",
            json=data
        )
        print("어르신 탐지:", response.json())
        assert response.status_code == 200

async def test_scenario_templates():
    """시나리오 템플릿 테스트"""
    scenarios = [
        {
            "scenario": "morning_greeting",
            "additional_data": {"weather": "맑은"}
        },
        {
            "scenario": "meal_assistance",
            "additional_data": {"menu": "된장찌개", "meal_time": "12:00"}
        },
        {
            "scenario": "conversation",
            "additional_data": {
                "topic": "오늘 날씨 이야기",
                "destination": "3층 302호 생활실"
            }
        },
        {
            "scenario": "wandering_detection",
            "additional_data": {"location": "1층 복도", "camera_id": "camera_001"}
        },
        {
            "scenario": "visitor_guidance",
            "additional_data": {
                "visitor_name": "정기우",
                "visitor_relationship": "아들",
                "meeting_room": "면회실"
            }
        }
    ]
    
    async with httpx.AsyncClient() as client:
        for scenario_data in scenarios:
            data = {
                "nickname": "Akaza",
                **scenario_data
            }
            response = await client.post(
                f"{BASE_URL}/api/templates/scenario",
                json=data
            )
            print(f"{scenario_data['scenario']}:", response.json())
            assert response.status_code == 200

async def main():
    """모든 테스트 실행"""
    print("=== ROS2 API Server 테스트 시작 ===\n")
    
    try:
        await test_health_check()
        print("✅ 헬스 체크 통과\n")
        
        await test_detection_resident()
        print("✅ 어르신 탐지 API 통과\n")
        
        await test_scenario_templates()
        print("✅ 시나리오 템플릿 API 통과\n")
        
        print("=== 모든 테스트 통과 ===")
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

**실행 방법**:
```bash
cd SERVER/ros2-server/api-server
python tests/test_api_integration.py
```

---

## 실제 ROS2 환경 테스트

### 1. ROS2 서비스 확인

ROS2 환경에서 LCD 컨트롤러 서버가 실행 중인지 확인:

```bash
# ROS2 서비스 목록 확인
ros2 service list | grep lcd_controller

# 예상 출력:
# /lcd_controller/set_display
# /lcd_controller/set_style
# /lcd_controller/clear_display
```

### 2. ROS2 서비스 직접 테스트

```bash
# ROS2 서비스 직접 호출 테스트
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: '테스트', lines: ['라인 1', '라인 2'], show_timestamp: true}"
```

### 3. API 서버에서 ROS2 통신 테스트

ROS2 환경이 있는 경우:
1. `.env.local`에서 ROS2 설정 확인
2. API 서버 실행
3. 어르신 탐지 API 호출
4. LCD에 실제로 표시되는지 확인

**주의사항**:
- ROS2 환경이 없는 경우, API 서버는 모킹 모드로 동작합니다
- `display_sent: false`로 응답되지만, API는 정상 동작합니다

---

## 문제 해결

### 1. iot-data-server 연결 실패

**증상**: `iot_data_server: false` (헬스 체크)

**해결 방법**:
```bash
# iot-data-server URL 확인
curl http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com/health

# .env.local에서 URL 수정
IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com
```

### 2. ROS2 서비스 연결 실패

**증상**: `ros2: false` (헬스 체크), `display_sent: false`

**해결 방법**:
- ROS2 환경이 없는 경우: 정상 동작 (모킹 모드)
- ROS2 환경이 있는 경우:
  ```bash
  # ROS2 서비스 확인
  ros2 service list | grep lcd_controller
  
  # 네트워크 확인 (Docker 컨테이너에서 ROS2 접근)
  # docker-compose.yml에서 network_mode: host 사용 고려
  ```

### 3. 어르신 정보를 찾을 수 없음

**증상**: `404 Not Found` 또는 `ValueError`

**해결 방법**:
```bash
# iot-data-server에서 어르신 정보 확인
curl "http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com/api/v1/residents/search/Akaza"

# 올바른 nickname 또는 user_id 사용 확인
```

### 4. 포트 충돌

**증상**: `Bind for 0.0.0.0:8003 failed: port is already allocated`

**해결 방법**:
```bash
# 포트 사용 중인 프로세스 확인
sudo lsof -i :8003

# 다른 포트 사용
# .env.local에서 SERVER_PORT 변경
# docker-compose.yml에서 포트 매핑 변경
```

---

## 테스트 체크리스트

### 기본 기능 테스트
- [ ] 헬스 체크 API 동작 확인
- [ ] API 문서 접근 가능 (`/docs`)
- [ ] iot-data-server 연결 확인

### 어르신 탐지 API 테스트
- [ ] nickname으로 탐지 테스트
- [ ] user_id로 탐지 테스트
- [ ] basic 형식 테스트
- [ ] detailed 형식 테스트
- [ ] urgent 형식 테스트
- [ ] 에러 처리 테스트 (존재하지 않는 어르신)

### 시나리오 템플릿 API 테스트
- [ ] morning_greeting 테스트
- [ ] meal_assistance 테스트
- [ ] conversation 테스트
- [ ] wandering_detection 테스트
- [ ] visitor_guidance 테스트
- [ ] 각 시나리오별 추가 데이터 테스트

### ROS2 통합 테스트 (ROS2 환경이 있는 경우)
- [ ] ROS2 서비스 연결 확인
- [ ] LCD 표시 동작 확인
- [ ] 실제 로봇 LCD에 표시되는지 확인

---

## 테스트 스크립트

### 전체 테스트 실행 스크립트

`api-server/tests/run_tests.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8003"

echo "=== ROS2 API Server 테스트 시작 ==="
echo ""

# 헬스 체크
echo "1. 헬스 체크 테스트..."
curl -s "$BASE_URL/health" | jq .
echo ""

# 어르신 탐지 API
echo "2. 어르신 탐지 API 테스트..."
curl -s -X POST "$BASE_URL/api/detection/resident" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001",
    "display_format": "basic"
  }' | jq .
echo ""

# 시나리오 템플릿 테스트
echo "3. 아침인사 템플릿 테스트..."
curl -s -X POST "$BASE_URL/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "morning_greeting",
    "nickname": "Akaza",
    "additional_data": {"weather": "맑은"}
  }' | jq .
echo ""

echo "=== 테스트 완료 ==="
```

**실행 방법**:
```bash
chmod +x tests/run_tests.sh
./tests/run_tests.sh
```

---

## 참고

- API 문서: `http://localhost:8003/docs`
- 템플릿 사용 가이드: `docs/TEMPLATE_USAGE_GUIDE.md`
- 로그 확인: `docker-compose logs -f ros2-api-server`

