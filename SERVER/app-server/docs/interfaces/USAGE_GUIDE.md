# 로봇 인식 시스템 사용 가이드

## 개요

이 가이드는 처음 이 프로젝트를 보는 사람들이 로봇 인식 시스템을 이해하고 테스트하며 사용할 수 있도록 작성되었습니다.

## 빠른 시작

### 1. 환경 설정

#### 필수 요구사항
- Python 3.12
- PostgreSQL 데이터베이스
- Redis (선택사항, 액션 실행을 위해 권장)

#### 환경 변수 설정

`.env.local` 파일 생성:
```bash
APP_ENV=local
DEBUG=true
DB_APP_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
ROBOT_DETECTION_STREAM=detections:actions
```

### 2. 서버 실행

```bash
# 의존성 설치
pip install -e .

# 데이터베이스 마이그레이션
alembic upgrade head

# 서버 실행
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### 3. API 문서 확인

브라우저에서 다음 URL 접속:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API 사용 예시

### ArUco 마커 인식 이벤트 전송

```bash
curl -X POST "http://localhost:8000/api/v1/detections" \
  -H "X-Robot-ID: robot-001" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "aruco",
    "unique_key": "ARUCO_23",
    "meta": {
      "entrance_id": "E-1",
      "zone": "Hall-A",
      "bbox": [120, 80, 64, 64],
      "confidence": 0.95
    },
    "detected_at": "2025-11-10T10:20:30Z",
    "processing_info": {
      "intent": "open_door",
      "api_calls": [
        {
          "method": "POST",
          "url": "https://sec.local/door/open",
          "body": {"entrance_id": "E-1"}
        }
      ],
      "cmds": [],
      "scenario_state": "INIT"
    }
  }'
```

### 인식 이벤트 목록 조회

```bash
# 모든 이벤트 조회
curl "http://localhost:8000/api/v1/detections"

# 카테고리별 필터링
curl "http://localhost:8000/api/v1/detections?category=aruco"

# 로봇별 필터링
curl "http://localhost:8000/api/v1/detections?robot_id=robot-001"

# 시간 범위 필터링
curl "http://localhost:8000/api/v1/detections?since=2025-11-10T00:00:00Z&until=2025-11-10T23:59:59Z"

# 페이징
curl "http://localhost:8000/api/v1/detections?skip=0&limit=10"
```

### 레지스트리 조회

```bash
# ArUco 마커 레지스트리
curl "http://localhost:8000/api/v1/detections/registry/aruco/ARUCO_23"

# OCR 텍스트 레지스트리
curl "http://localhost:8000/api/v1/detections/registry/text/식당"

# 얼굴 레지스트리
curl "http://localhost:8000/api/v1/detections/registry/face/facehash_abcd1234"

# 전신 레지스트리
curl "http://localhost:8000/api/v1/detections/registry/person/track_006"
```

### 액션 수동 실행

```bash
curl -X POST "http://localhost:8000/api/v1/detections/actions/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

## 테스트

### 통합 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/

# 로봇 인식 API 테스트만 실행
pytest tests/integration/test_robot_detection_api.py -v

# 특정 테스트만 실행
pytest tests/integration/test_robot_detection_api.py::test_create_aruco_detection -v
```

### 테스트 샘플 코드

프로젝트에 포함된 테스트 코드를 참고하세요:
- `tests/integration/test_robot_detection_api.py`

주요 테스트 케이스:
- ArUco 마커 인식 이벤트 생성
- OCR 텍스트 인식 이벤트 생성
- 인식 이벤트 목록 조회
- 인식 이벤트 단건 조회
- 레지스트리 조회
- X-Robot-ID 헤더 누락 검증

---

## 카테고리별 사용 예시

### 1. ArUco 마커

**용도**: 출입구 제어, 위치 인식

**예시 시나리오**:
1. 로봇이 1층 로비에서 ArUco 마커 #23 인식
2. 중앙 서버로 이벤트 전송
3. 레지스트리에서 마커 정보 확인 (출입구 E-1)
4. 보안 서버에 출입구 열기 요청
5. 출입구 열림

### 2. OCR 텍스트

**용도**: 공간 식별, 안내

**예시 시나리오**:
1. 로봇이 "식당" 표지판 인식
2. 중앙 서버로 이벤트 전송
3. 레지스트리에서 텍스트 정보 확인
4. 로봇 음성 안내: "식당에 도착했습니다."

### 3. 얼굴 인식

**용도**: 면회자/보호자 식별

**예시 시나리오**:
1. 로봇이 면회실에서 얼굴 인식
2. 중앙 서버로 이벤트 전송 (얼굴 해시만 전송)
3. 레지스트리에서 얼굴 정보 확인
4. 보호자에게 면회자 도착 알림

### 4. 전신 인식

**용도**: 로봇 추종

**예시 시나리오**:
1. 로봇이 복도에서 사람 전신 인식
2. 중앙 서버로 이벤트 전송
3. 레지스트리에서 개인 정보 확인
4. 로봇 추종 명령 전송 (거리: 1.5m)
5. 로봇이 사람을 따라다님

---

## 액션 실행기 설정

### Redis 설정 (권장)

Redis를 사용하면 액션이 비동기로 처리됩니다.

```bash
# Redis 설치 (Docker)
docker run -d -p 6379:6379 redis:latest

# 환경 변수 설정
export REDIS_URL=redis://localhost:6379/0
export ROBOT_DETECTION_STREAM=detections:actions
```

### Redis 없이 사용 (개발/테스트)

Redis가 없어도 API는 정상 작동하지만, 액션은 로그만 출력됩니다.

```bash
# 환경 변수에서 REDIS_URL 제거 또는 주석 처리
# export REDIS_URL=redis://localhost:6379/0
```

---

## 데이터베이스 확인

### 테이블 확인

```bash
# API를 통한 확인
curl "http://localhost:8000/api/v1/tables"

# 직접 SQL 쿼리
psql -h localhost -U user -d dbname -c "SELECT * FROM detection_event LIMIT 10;"
```

### 레지스트리 확인

```bash
# ArUco 마커 레지스트리
psql -h localhost -U user -d dbname -c "SELECT * FROM marker_registry;"

# OCR 텍스트 레지스트리
psql -h localhost -U user -d dbname -c "SELECT * FROM text_registry;"

# 얼굴 레지스트리
psql -h localhost -U user -d dbname -c "SELECT * FROM face_registry;"

# 전신 레지스트리
psql -h localhost -U user -d dbname -c "SELECT * FROM person_registry;"
```

---

## 문제 해결

### 1. X-Robot-ID 헤더 누락

**에러**: `422 Unprocessable Entity`

**해결**: 요청 헤더에 `X-Robot-ID` 추가

```bash
curl -H "X-Robot-ID: robot-001" ...
```

### 2. Redis 연결 실패

**증상**: 액션 실행 시 `status: "logged"` 반환

**해결**:
- Redis 서버가 실행 중인지 확인
- `REDIS_URL` 환경 변수 확인
- 로그에서 연결 오류 확인

### 3. 데이터베이스 연결 실패

**증상**: `500 Internal Server Error`

**해결**:
- 데이터베이스 서버가 실행 중인지 확인
- `DB_APP_URL` 환경 변수 확인
- 마이그레이션이 실행되었는지 확인 (`alembic upgrade head`)

### 4. 레지스트리 조회 실패

**증상**: `404 Not Found`

**해결**:
- 먼저 인식 이벤트를 생성하여 레지스트리 자동 생성
- 또는 관리자 패널에서 수동으로 레지스트리 생성

---

## 관련 문서

- [인터페이스 명세서](./README.md)
- [API 문서](../apis/robot_detections_api.md)
- [DB 설계 문서](../database/robot_detection_schema.md)
- [개발 리포트](../development/commit_report_20251110.md)

---

## 추가 리소스

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)
- [Redis 문서](https://redis.io/docs/)

