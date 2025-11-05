# LLM Gateway - 음성 인터페이스 서버

**FastAPI 기반 실시간 한국어 음성 인터페이스 서버**

OpenAI Whisper (STT) + ChatGPT + TTS 통합 API 서버로, 실시간 대화 방식의 음성 인터페이스를 제공합니다.

---

## 📋 목차

- [프로젝트 구조](#프로젝트-구조)
- [개요](#개요)
- [기능](#기능)
- [시작하기](#시작하기)
- [개발 워크플로우 (TDD)](#개발-워크플로우-tdd)
- [테스트](#테스트)
- [API 엔드포인트](#api-엔드포인트)
- [환경 설정](#환경-설정)

---

## 📁 프로젝트 구조

> 📖 **상세 구조 설명**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 참고

```
AI/llm-gateway/
├── src/                    # 소스 코드
│   ├── main.py            # FastAPI 애플리케이션 메인
│   ├── config.py          # 환경변수 및 설정 관리
│   ├── database.py        # PostgreSQL 데이터베이스 관리
│   └── redis_session.py   # Redis 세션 관리
│
├── tests/                  # 테스트 코드 (TDD)
│   ├── unit/              # 단위 테스트
│   ├── integration/       # 통합 테스트
│   ├── e2e/              # E2E 테스트
│   └── user_testing/      # 사용자 테스트 도구
│       ├── test_voice.html      # 음성 인터페이스 테스트 UI
│       ├── test_websocket.html  # WebSocket 채팅 테스트 UI
│       └── test_websocket.py    # Python 클라이언트 테스트
│
├── docs/                   # 문서
│   ├── database_schema.md # 데이터베이스 스키마
│   ├── REDIS_SETUP.md     # Redis 설정 가이드
│   └── ...
│
├── scripts/                # 유틸리티 스크립트
│   └── run_tests.sh       # 테스트 실행 스크립트
│
├── docker-compose.yml      # Docker Compose 설정
├── Dockerfile              # Docker 이미지 정의
├── requirements.txt        # 프로덕션 의존성
├── requirements-dev.txt    # 개발 의존성
├── pytest.ini             # pytest 설정
└── Makefile               # 빌드 명령어
```

### 디렉토리 설명

#### `src/` - 소스 코드
- **`main.py`**: FastAPI 애플리케이션의 메인 엔트리 포인트
  - STT, Chat, TTS, WebSocket 엔드포인트
  - 통합 음성 처리 파이프라인
- **`config.py`**: 환경변수 관리 및 설정
- **`database.py`**: PostgreSQL 데이터베이스 연결 및 관리
- **`redis_session.py`**: Redis 세션 관리 및 캐싱

#### `tests/` - 테스트 코드
- **`unit/`**: 단위 테스트
  - 개별 함수/클래스 단위 테스트
  - 모킹을 통한 독립적 테스트
- **`integration/`**: 통합 테스트
  - 여러 모듈 간 상호작용 테스트
  - DB, Redis 연결 테스트
- **`e2e/`**: End-to-End 테스트
  - 전체 워크플로우 테스트
  - STT → Chat → TTS 파이프라인 테스트
- **`user_testing/`**: 사용자 테스트 도구
  - 브라우저 기반 테스트 UI (`test_voice.html`, `test_websocket.html`)
  - Python 클라이언트 테스트 스크립트

#### `docs/` - 문서
- 프로젝트 문서, 설정 가이드, API 문서 등

#### `scripts/` - 유틸리티 스크립트
- 테스트 실행, 배포, 유틸리티 스크립트

---

## 🎯 개요

이 서버는 **실시간 대화 방식의 음성 인터페이스**를 제공합니다. 사용자가 음성으로 질문하면, 서버는 다음 파이프라인을 통해 응답합니다:

```
음성 입력 (STT) → 텍스트 변환 → ChatGPT 처리 → 텍스트 응답 → 음성 출력 (TTS)
```

**주요 특징:**
- 🎤 **STT (Speech-to-Text)**: OpenAI Whisper로 음성을 텍스트로 변환
- 💬 **ChatGPT 통합**: 자연어 대화 처리
- 🔊 **TTS (Text-to-Speech)**: OpenAI TTS로 텍스트를 음성으로 변환
- 🔄 **실시간 통신**: WebSocket 기반 양방향 통신
- 📡 **세션 관리**: Redis 기반 분산 세션 관리
- 💾 **영구 저장**: PostgreSQL 기반 대화 히스토리 저장
- 🧪 **TDD 기반 개발**: 테스트 주도 개발 방식

---

## 🚀 기능

### 1. 음성 인식 (STT)
- OpenAI Whisper API 사용
- 한국어 지원 최적화
- 실시간 음성 스트리밍 지원

### 2. 텍스트 채팅
- 일반 채팅 및 스트리밍 채팅
- 세션별 대화 히스토리 관리
- 커스텀 시스템 프롬프트 지원

### 3. 음성 합성 (TTS)
- OpenAI TTS API 사용
- 다양한 음성 옵션 제공
- 스트리밍 응답 지원

### 4. 통합 음성 처리
- 단일 요청으로 STT → ChatGPT → TTS 전체 프로세스 처리
- 실시간 음성 대화 지원

### 5. WebSocket 실시간 통신
- 실시간 양방향 통신
- 스트리밍 응답 전송
- 세션 관리 및 히스토리 복원

---

## 🏁 시작하기

### 1. 사전 요구사항

- Python 3.11 이상 (로컬 개발 시)
- Docker & Docker Compose (운영 환경 권장)
- OpenAI API 키
- PostgreSQL 데이터베이스 (외부 DB 사용)
- Redis (Docker Compose로 자동 설치)

### 2. 설치 방법

#### 방법 A: Docker Compose 사용 (권장)

```bash
# AI/llm-gateway 디렉토리로 이동
cd AI/llm-gateway

# .env.local 파일 생성 및 설정
cp .env.example .env.local
# .env.local 파일 편집하여 OPENAI_API_KEY 및 DB 설정 추가

# Docker Compose로 서버 및 Redis 실행
docker compose up -d

# 로그 확인
docker compose logs -f llm-gateway
```

#### 방법 B: 로컬 개발 환경

```bash
# AI/llm-gateway 디렉토리로 이동
cd AI/llm-gateway

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 패키지 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 의존성 (테스트 도구 포함)

# Redis 실행 (Docker Compose 사용)
docker compose up -d redis

# 서버 실행
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 환경 설정

`.env.local` 파일에 다음 설정을 추가하세요:

```bash
# OpenAI API 설정
OPENAI_API_KEY=your_openai_api_key_here

# 데이터베이스 설정
DB_URL=postgresql://user:password@host:port/database
# 또는
DB_HOST=host.docker.internal
DB_PORT=15432
DB_NAME=iot_care
DB_USER=svc_dev
DB_PASSWORD=your_password

# Redis 설정 (Docker Compose 사용 시 자동 설정됨)
REDIS_HOST=redis
REDIS_PORT=6379
```

---

## 🧪 개발 워크플로우 (TDD)

이 프로젝트는 **Test-Driven Development (TDD)** 방식으로 개발합니다.

### TDD 사이클

1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트를 통과시키는 최소한의 코드 작성
3. **Refactor**: 코드 리팩토링 및 개선

### 개발 단계

#### 1. 단위 테스트 작성 (`tests/unit/`)

```python
# tests/unit/test_stt.py
import pytest
from src.main import app

@pytest.mark.asyncio
async def test_stt_endpoint():
    # 테스트 코드 작성
    pass
```

#### 2. 통합 테스트 작성 (`tests/integration/`)

```python
# tests/integration/test_voice_pipeline.py
@pytest.mark.integration
async def test_stt_to_chat_to_tts():
    # STT → Chat → TTS 파이프라인 테스트
    pass
```

#### 3. E2E 테스트 작성 (`tests/e2e/`)

```python
# tests/e2e/test_voice_conversation.py
@pytest.mark.e2e
async def test_full_voice_conversation():
    # 전체 음성 대화 시나리오 테스트
    pass
```

#### 4. 사용자 테스트 (`tests/user_testing/`)

- 브라우저에서 `test_voice.html` 열기
- 실제 음성 입력으로 기능 검증
- 사용자 피드백 수집

---

## 🧪 테스트

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 단위 테스트만 실행
pytest tests/unit -v

# 통합 테스트만 실행
pytest tests/integration -v

# E2E 테스트만 실행
pytest tests/e2e -v

# 커버리지 포함 테스트
pytest --cov=src --cov-report=html

# 스크립트 사용
./scripts/run_tests.sh
```

### 테스트 마커

```bash
# 특정 마커만 실행
pytest -m unit          # 단위 테스트만
pytest -m integration   # 통합 테스트만
pytest -m e2e          # E2E 테스트만
pytest -m "not slow"   # 느린 테스트 제외
```

### 사용자 테스트

```bash
# 서버 실행
docker compose up -d

# 브라우저에서 열기
open http://localhost:8000/tests/user_testing/test_voice.html
```

---

## 📡 API 엔드포인트

### STT (Speech-to-Text)
```
POST /api/stt
Content-Type: multipart/form-data
Body: audio file
```

### 텍스트 채팅
```
POST /api/chat
Content-Type: application/json
Body: {"message": "안녕하세요", "session_id": "user123"}
```

### 스트리밍 채팅
```
POST /api/chat/stream
Content-Type: application/json
Response: text/event-stream
```

### TTS (Text-to-Speech)
```
POST /api/tts
Content-Type: application/json
Body: {"text": "안녕하세요", "voice": "alloy"}
Response: audio/mpeg
```

### 통합 음성 처리
```
POST /api/voice/process
Content-Type: multipart/form-data
Body: audio file, session_id, voice
Response: multipart/mixed (metadata + audio)
```

### WebSocket 실시간 통신
```
WS /ws/voice?session_id=user123
```

### Health Check
```
GET /
```

---

## 🔧 환경 설정

자세한 설정 방법은 다음 문서를 참고하세요:

- [데이터베이스 설정](docs/database_schema.md)
- [Redis 설정](docs/REDIS_SETUP.md)
- [WebSocket 테스트 가이드](docs/WEBSOCKET_TEST_GUIDE.md)

---

## 📝 개발 가이드

### 코드 스타일

```bash
# 코드 포맷팅
black src/ tests/

# import 정렬
isort src/ tests/

# 린팅
flake8 src/ tests/

# 타입 체크
mypy src/
```

### 커밋 메시지 규칙

- `feat`: 새로운 기능
- `fix`: 버그 수정
- `test`: 테스트 추가/수정
- `refactor`: 리팩토링
- `docs`: 문서 수정
- `chore`: 기타 작업

---

## 📚 추가 문서

- [개발 현황 리포트](docs/DEVELOPMENT_STATUS.md)
- [디버깅 리포트](docs/DEBUG_REPORT.md)
- [데이터베이스 스키마](docs/database_schema.md)

---

## 🤝 기여하기

1. 기능/테스트 작성
2. 테스트 통과 확인
3. 코드 리뷰 요청
4. 머지

---

## 📄 라이선스

[라이선스 정보]

---

**Happy Coding! 🚀**

