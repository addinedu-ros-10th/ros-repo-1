# 프로젝트 구조 가이드

## 📁 디렉토리 구조

```
AI/llm-gateway/
│
├── src/                          # 소스 코드
│   ├── __init__.py              # 패키지 초기화
│   ├── main.py                  # FastAPI 애플리케이션 메인
│   ├── config.py                # 환경변수 및 설정
│   ├── database.py              # PostgreSQL 관리
│   └── redis_session.py         # Redis 세션 관리
│
├── tests/                        # 테스트 코드 (TDD)
│   ├── conftest.py              # pytest 설정 및 fixtures
│   ├── unit/                    # 단위 테스트
│   │   └── __init__.py
│   ├── integration/             # 통합 테스트
│   │   └── __init__.py
│   ├── e2e/                     # E2E 테스트
│   │   └── __init__.py
│   └── user_testing/            # 사용자 테스트 도구
│       ├── __init__.py
│       ├── test_voice.html      # 음성 인터페이스 테스트 UI
│       ├── test_websocket.html  # WebSocket 채팅 테스트 UI
│       └── test_websocket.py    # Python 클라이언트
│
├── docs/                         # 문서
│   ├── database_schema.md       # DB 스키마
│   ├── REDIS_SETUP.md           # Redis 설정
│   ├── WEBSOCKET_TEST_GUIDE.md  # WebSocket 가이드
│   └── ...
│
├── scripts/                      # 유틸리티 스크립트
│   └── run_tests.sh             # 테스트 실행
│
├── logs/                         # 로그 파일 (gitignore)
│
├── docker-compose.yml            # Docker Compose 설정
├── Dockerfile                    # Docker 이미지 정의
├── requirements.txt              # 프로덕션 의존성
├── requirements-dev.txt          # 개발 의존성
├── pytest.ini                   # pytest 설정
├── Makefile                     # 빌드 명령어
├── .gitignore                   # Git 제외 파일
└── README.md                    # 프로젝트 메인 문서
```

## 🎯 각 디렉토리의 역할

### `src/` - 소스 코드
**목적**: 애플리케이션의 핵심 비즈니스 로직

- **`main.py`**: FastAPI 애플리케이션
  - API 엔드포인트 정의
  - STT, Chat, TTS, WebSocket 처리
  - 통합 음성 처리 파이프라인

- **`config.py`**: 설정 관리
  - 환경변수 로드
  - Pydantic Settings 클래스

- **`database.py`**: 데이터베이스 관리
  - PostgreSQL 연결
  - ORM 모델 정의
  - 세션 관리

- **`redis_session.py`**: Redis 세션 관리
  - 세션 저장/로드
  - TTL 관리
  - 연결 풀 관리

### `tests/` - 테스트 코드

**TDD 방식으로 개발**하므로, 모든 기능은 테스트 코드를 먼저 작성합니다.

#### `tests/unit/` - 단위 테스트
**목적**: 개별 함수/클래스의 독립적인 테스트

```python
# tests/unit/test_config.py
def test_config_loading():
    # config.py의 개별 함수 테스트
    pass
```

**특징**:
- 빠른 실행 속도
- 외부 의존성 모킹 (DB, Redis, OpenAI API)
- 독립적인 테스트

#### `tests/integration/` - 통합 테스트
**목적**: 여러 모듈 간 상호작용 테스트

```python
# tests/integration/test_stt_chat_tts.py
@pytest.mark.integration
async def test_stt_to_chat_integration():
    # STT → Chat 통합 테스트
    pass
```

**특징**:
- 실제 DB/Redis 연결 사용
- 모듈 간 상호작용 검증
- 중간 속도 실행

#### `tests/e2e/` - E2E 테스트
**목적**: 전체 워크플로우 테스트

```python
# tests/e2e/test_voice_conversation.py
@pytest.mark.e2e
async def test_full_voice_conversation():
    # 음성 입력 → STT → Chat → TTS → 음성 출력
    # 전체 파이프라인 테스트
    pass
```

**특징**:
- 실제 서버 실행
- 전체 시나리오 검증
- 느린 실행 속도

#### `tests/user_testing/` - 사용자 테스트 도구
**목적**: 실제 사용자 시나리오 테스트

- **`test_voice.html`**: 브라우저 기반 음성 인터페이스 테스트
- **`test_websocket.html`**: WebSocket 채팅 테스트
- **`test_websocket.py`**: Python 클라이언트 테스트

**사용 방법**:
```bash
# 서버 실행
docker compose up -d

# 브라우저에서 열기
open http://localhost:8000/tests/user_testing/test_voice.html
```

### `docs/` - 문서
**목적**: 프로젝트 문서 및 가이드

- 설정 가이드
- API 문서
- 개발 리포트
- 트러블슈팅 가이드

### `scripts/` - 유틸리티 스크립트
**목적**: 개발/배포 자동화 스크립트

- 테스트 실행
- 코드 품질 검사
- 배포 스크립트

## 🔄 개발 워크플로우 (TDD)

### 1. 테스트 작성 (Red)
```python
# tests/unit/test_stt.py
def test_stt_endpoint():
    # 실패하는 테스트 작성
    response = client.post("/api/stt", files={"audio": ...})
    assert response.status_code == 200
```

### 2. 코드 구현 (Green)
```python
# src/main.py
@app.post("/api/stt")
async def speech_to_text(audio: UploadFile):
    # 최소한의 코드로 테스트 통과
    ...
```

### 3. 리팩토링 (Refactor)
```python
# 코드 개선 및 중복 제거
# 테스트는 계속 통과해야 함
```

### 4. 사용자 테스트
- `tests/user_testing/` 도구로 실제 사용 시나리오 검증
- 사용자 피드백 수집
- 개선 사항 반영

## 📝 파일 명명 규칙

### 테스트 파일
- `test_*.py`: pytest가 자동으로 인식
- `tests/unit/test_config.py`: 단위 테스트
- `tests/integration/test_database.py`: 통합 테스트
- `tests/e2e/test_voice_pipeline.py`: E2E 테스트

### 소스 파일
- `snake_case.py`: Python 표준
- `main.py`: 애플리케이션 엔트리 포인트
- `config.py`: 설정 관련

## 🚀 빠른 시작

### 개발 환경 설정
```bash
# 의존성 설치
make install

# 테스트 실행
make test

# 서버 실행
make run
```

### TDD로 새 기능 추가
```bash
# 1. 테스트 작성
vim tests/unit/test_new_feature.py

# 2. 테스트 실행 (실패 확인)
pytest tests/unit/test_new_feature.py

# 3. 코드 구현
vim src/main.py

# 4. 테스트 실행 (통과 확인)
pytest tests/unit/test_new_feature.py

# 5. 리팩토링
# 6. 사용자 테스트
```

## 📚 추가 리소스

- [README.md](README.md): 프로젝트 개요
- [docs/](docs/): 상세 문서
- [pytest.ini](pytest.ini): 테스트 설정

