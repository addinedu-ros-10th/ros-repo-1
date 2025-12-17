# ROS2 API Server

FastAPI 기반 ROS2 및 LCD 제어 API 서버

## 개요

Deep Learning 컴포넌트가 어르신을 탐지했을 때, 로봇 LCD에 어르신 정보를 표시하기 위한 API 서버입니다.

## 주요 기능

- 🔍 **어르신 탐지**: DL 컴포넌트가 어르신을 탐지했을 때 LCD에 정보 표시
- 📋 **시나리오 템플릿**: 다양한 상황에 맞는 LCD 표시 템플릿 제공
- 🏥 **어르신 정보 조회**: iot-data-server를 통한 어르신 정보 조회
- 🖥️ **LCD 제어**: ROS2 서비스를 통한 로봇 LCD 제어

## 빠른 시작

### 1. 환경 변수 설정

```bash
cp .env.example .env.local
# .env.local 파일을 편집하여 설정 수정
```

### 2. Docker Compose로 실행

```bash
docker-compose up -d
```

### 3. API 문서 확인

브라우저에서 `http://localhost:8003/docs` 접속

## 포트 설정

- **FastAPI 서버**: 외부 8003, 내부 8000
- **Redis**: 외부 16381, 내부 6379
- **Caddy HTTP**: 외부 8080, 내부 80
- **Caddy HTTPS**: 외부 8443, 내부 443

## API 엔드포인트

### 어르신 탐지
- `POST /api/detection/resident` - 어르신 탐지 및 LCD 표시

### 시나리오 템플릿
- `POST /api/templates/scenario` - 시나리오별 템플릿 생성 및 표시

### 헬스 체크
- `GET /health` - 서버 상태 확인
- `GET /api/lcd/status` - LCD 상태 조회 (향후 구현)

## 시나리오 템플릿

1. **morning_greeting**: 아침인사
2. **meal_assistance**: 식사 지원
3. **conversation**: 맞춤형 이동식 대화
4. **wandering_detection**: 배회 감지
5. **visitor_guidance**: 면회객 안내

자세한 사용법은 [템플릿 사용 가이드](docs/TEMPLATE_USAGE_GUIDE.md)를 참조하세요.

## 개발

### 로컬 개발 환경

```bash
# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 어르신 탐지 테스트
curl -X POST "http://localhost:8000/api/detection/resident" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001"
  }'
```

## 문서

- [템플릿 사용 가이드](docs/TEMPLATE_USAGE_GUIDE.md)
- [LCD 표시 시나리오 템플릿](../docs/LCD_DISPLAY_SCENARIO_TEMPLATES.md)
- [FastAPI 서버 구축 계획](../docs/FASTAPI_SERVER_BUILD_PLAN.md)

## 라이선스

프로젝트 라이선스에 따릅니다.

