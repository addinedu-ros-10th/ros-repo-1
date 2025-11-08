# AI / llm-gateway

**FastAPI 기반 한국어 음성 인터페이스 서버**

OpenAI Whisper (STT) + ChatGPT + TTS 통합 API 서버

---

## 📋 목차

- [개요](#개요)
- [기능](#기능)
- [시작하기](#시작하기)
- [환경 설정](#환경-설정)
- [API 엔드포인트](#api-엔드포인트)
- [사용 예시](#사용-예시)
- [확장 및 개선](#확장-및-개선)

---

## 개요

이 서버는 한국어 음성 인터페이스를 위한 통합 API를 제공합니다. OpenAI의 Whisper, ChatGPT, TTS API를 활용하여 음성 입력부터 음성 응답까지의 전체 파이프라인을 처리합니다.

**주요 특징:**
- 🎤 **STT (Speech-to-Text)**: 음성을 텍스트로 변환
- 💬 **ChatGPT 통합**: 자연어 대화 처리
- 🔊 **TTS (Text-to-Speech)**: 텍스트를 음성으로 변환
- 🔄 **통합 처리**: 음성 입력 → 대화 → 음성 응답 원스톱 처리
- 📡 **WebSocket 지원**: 실시간 양방향 통신
- 🔧 **환경변수 기반 설정**: `.env` 파일로 간편한 설정 관리

---

## 기능

### 1. 음성 인식 (STT)
- OpenAI Whisper API를 사용한 고품질 음성 인식
- 한국어 지원 최적화

### 2. 텍스트 채팅
- 일반 채팅 및 스트리밍 채팅 지원
- 세션별 대화 히스토리 관리
- 커스텀 시스템 프롬프트 지원

### 3. 음성 합성 (TTS)
- OpenAI TTS API를 사용한 자연스러운 음성 생성
- 다양한 음성 옵션 제공

### 4. 통합 음성 처리
- 단일 요청으로 STT → ChatGPT → TTS 전체 프로세스 처리
- 클라이언트 구현 단순화

### 5. WebSocket 실시간 통신
- 실시간 양방향 통신 지원
- 스트리밍 응답 전송

---

## 시작하기

### 1. 사전 요구사항

- Python 3.8 이상 (로컬 개발 시)
- Docker & Docker Compose (운영 환경 권장)
- OpenAI API 키
- PostgreSQL 데이터베이스 (외부 DB 사용)

### 2. 설치 방법

#### 방법 A: Docker Compose 사용 (권장)

```bash
# AI/llm-gateway 디렉토리로 이동
cd AI/llm-gateway

# .env 파일 생성
cp .env.example .env
# .env 파일 편집하여 OPENAI_API_KEY 및 DB 설정 추가

# Docker Compose로 서버 및 Redis 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f llm-gateway
```

#### 방법 B: 로컬 개발 환경

```bash
# AI/llm-gateway 디렉토리로 이동
cd AI/llm-gateway

# 가상환경 생성 (선택사항, 권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 3. 데이터베이스 설정

외부 PostgreSQL 데이터베이스를 사용합니다. 데이터베이스 스키마는 서버 시작 시 자동으로 생성되거나, `database_schema.md` 파일의 SQL 스크립트를 수동으로 실행할 수 있습니다.

**데이터베이스 생성:**
```sql
CREATE DATABASE llm_gateway;
```

**환경변수 설정:**
```env
DB_URL=postgresql://user:password@host:5432/llm_gateway
```

자세한 스키마 정보는 [database_schema.md](./database_schema.md)를 참고하세요.

### 4. 환경 설정

`.env` 파일을 생성하고 필요한 환경변수를 설정합니다:

```bash
# .env.example 파일을 참고하여 .env 파일 생성
cp .env.example .env  # 또는 직접 생성

# .env 파일 편집
nano .env  # 또는 원하는 편집기 사용
```

**필수 환경변수:**
```env
OPENAI_API_KEY=your_openai_api_key_here
```

**선택 환경변수 (기본값 사용 가능):**
```env
# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false
RELOAD=false

# CORS 설정
CORS_ORIGINS=*

# ChatGPT 기본 설정
DEFAULT_CHAT_MODEL=gpt-4o-mini
DEFAULT_SYSTEM_PROMPT=당신은 친절한 한국어 AI 어시스턴트입니다.

# TTS 기본 설정
DEFAULT_TTS_VOICE=alloy
DEFAULT_TTS_MODEL=tts-1
```

### 5. 서버 실행

#### Docker Compose 사용 시

```bash
# 서버 시작
docker-compose up -d

# 서버 중지
docker-compose down

# 로그 확인
docker-compose logs -f llm-gateway

# Redis 로그 확인
docker-compose logs -f redis

# 컨테이너 재시작
docker-compose restart llm-gateway
```

#### 로컬 개발 환경

```bash
# 방법 1: Python으로 직접 실행
python main.py

# 방법 2: Uvicorn으로 실행 (권장)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 방법 3: 환경변수에 따라 자동 설정
uvicorn main:app --reload
```

**중요**: 로컬 개발 시 Redis를 별도로 실행해야 합니다:

```bash
# Redis Docker 컨테이너 실행
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 또는 로컬 Redis 설치 후
redis-server
```

서버가 실행되면 다음 URL에서 접근할 수 있습니다:
- **API 서버**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/ (Redis 및 DB 상태 확인)

---

## 환경 설정

### 환경변수 상세 설명

#### 필수 설정

| 변수명 | 설명 | 예시 |
|--------|------|------|
| `OPENAI_API_KEY` | OpenAI API 키 | `sk-...` |

#### 서버 설정

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `SERVER_HOST` | 서버 호스트 주소 | `0.0.0.0` |
| `SERVER_PORT` | 서버 포트 | `8000` |
| `DEBUG` | 디버그 모드 | `false` |
| `RELOAD` | 자동 리로드 (개발 모드) | `false` |

#### CORS 설정

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `CORS_ORIGINS` | 허용할 오리진 (쉼표로 구분, `*`는 모든 오리진) | `*` |

#### ChatGPT 설정

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DEFAULT_CHAT_MODEL` | 기본 ChatGPT 모델 | `gpt-4o-mini` |
| `DEFAULT_SYSTEM_PROMPT` | 기본 시스템 프롬프트 | `당신은 친절한 한국어 AI 어시스턴트입니다.` |

#### TTS 설정

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `DEFAULT_TTS_VOICE` | 기본 TTS 음성 (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`) | `alloy` |
| `DEFAULT_TTS_MODEL` | 기본 TTS 모델 (`tts-1`, `tts-1-hd`) | `tts-1` |

#### 데이터베이스 설정 (선택사항, 향후 확장용)

| 변수명 | 설명 |
|--------|------|
| `DB_URL` | 데이터베이스 연결 URL (예: `postgresql://user:pass@host:port/db`) |
| `DB_HOST` | 데이터베이스 호스트 |
| `DB_PORT` | 데이터베이스 포트 |
| `DB_NAME` | 데이터베이스 이름 |
| `DB_USER` | 데이터베이스 사용자 |
| `DB_PASSWORD` | 데이터베이스 비밀번호 |

#### Redis 설정 (선택사항, 세션 관리용)

| 변수명 | 설명 | 기본값 |
|--------|------|--------|
| `REDIS_URL` | Redis 연결 URL | - |
| `REDIS_HOST` | Redis 호스트 | `localhost` |
| `REDIS_PORT` | Redis 포트 | `6379` |
| `REDIS_PASSWORD` | Redis 비밀번호 | - |

---

## API 엔드포인트

### Health Check

```http
GET /
```

서버 상태 및 사용 가능한 엔드포인트 목록 확인

### STT (Speech-to-Text)

```http
POST /api/stt
Content-Type: multipart/form-data

audio: [음성 파일]
```

음성 파일을 텍스트로 변환

**응답 예시:**
```json
{
  "success": true,
  "text": "안녕하세요",
  "language": "ko"
}
```

### 텍스트 채팅

```http
POST /api/chat
Content-Type: application/json

{
  "message": "안녕하세요",
  "session_id": "user123",
  "system_prompt": "당신은 친절한 AI 어시스턴트입니다.",
  "model": "gpt-4o-mini"
}
```

**응답 예시:**
```json
{
  "success": true,
  "response": "안녕하세요! 무엇을 도와드릴까요?",
  "session_id": "user123",
  "model": "gpt-4o-mini"
}
```

### 스트리밍 채팅

```http
POST /api/chat/stream
Content-Type: application/json

{
  "message": "안녕하세요",
  "session_id": "user123"
}
```

Server-Sent Events (SSE) 형식으로 실시간 응답 스트리밍

### TTS (Text-to-Speech)

```http
POST /api/tts
Content-Type: application/json

{
  "text": "안녕하세요",
  "voice": "alloy",
  "model": "tts-1"
}
```

**응답:** MP3 형식의 음성 파일 (스트리밍)

### 통합 음성 처리

```http
POST /api/voice/process
Content-Type: multipart/form-data

audio: [음성 파일]
session_id: "user123"
voice: "alloy"
model: "gpt-4o-mini"
```

음성 입력 → ChatGPT → 음성 응답 전체 프로세스 처리

**응답:** Multipart 형식 (메타데이터 + 음성 파일)

### WebSocket 실시간 통신

```http
WS /ws/voice
```

WebSocket을 통한 실시간 양방향 통신

**메시지 형식:**
```json
{
  "type": "text",
  "message": "안녕하세요"
}
```

### 세션 관리

```http
GET /api/session/{session_id}
DELETE /api/session/{session_id}
```

세션 히스토리 조회 및 삭제

---

## 사용 예시

### Python 예시

```python
import requests

# STT
with open("audio.mp3", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/stt",
        files={"audio": f}
    )
    print(response.json())

# Chat
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "message": "안녕하세요",
        "session_id": "user123"
    }
)
print(response.json())

# TTS
response = requests.post(
    "http://localhost:8000/api/tts",
    json={"text": "안녕하세요"}
)
with open("output.mp3", "wb") as f:
    f.write(response.content)
```

### cURL 예시

```bash
# STT
curl -X POST "http://localhost:8000/api/stt" \
  -F "audio=@audio.mp3"

# Chat
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요",
    "session_id": "user123"
  }'

# TTS
curl -X POST "http://localhost:8000/api/tts" \
  -H "Content-Type: application/json" \
  -d '{"text": "안녕하세요"}' \
  --output speech.mp3
```

### JavaScript/TypeScript 예시

```javascript
// STT
const formData = new FormData();
formData.append('audio', audioFile);

const sttResponse = await fetch('http://localhost:8000/api/stt', {
  method: 'POST',
  body: formData
});
const sttData = await sttResponse.json();

// Chat
const chatResponse = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: '안녕하세요',
    session_id: 'user123'
  })
});
const chatData = await chatResponse.json();

// TTS
const ttsResponse = await fetch('http://localhost:8000/api/tts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: '안녕하세요' })
});
const audioBlob = await ttsResponse.blob();
```

---

## 운영 환경 구성

### Docker Compose 구조

이 프로젝트는 Docker Compose를 사용하여 다음 서비스를 구성합니다:

- **llm-gateway**: FastAPI 서버 컨테이너
- **redis**: Redis 컨테이너 (세션 관리)

### 데이터베이스 관리

#### 스키마 자동 생성

서버 시작 시 `database.py`의 `db_manager.create_tables()` 메서드가 자동으로 테이블을 생성합니다.

#### 수동 스키마 생성

`database_schema.md` 파일의 SQL 스크립트를 직접 실행할 수 있습니다:

```bash
psql -h your_host -U your_user -d llm_gateway -f database_schema.sql
```

### 세션 관리 전략

1. **Redis**: 빠른 읽기/쓰기를 위한 캐시 (30일 TTL)
   - 실시간 세션 관리
   - 분산 환경에서 세션 공유
   - 자동 만료 관리

2. **PostgreSQL**: 영구 저장 및 백업
   - 대화 히스토리 영구 저장
   - API 요청 로그 저장
   - 비용 추적 및 분석

### 프레임워크에서의 관리 방안

#### 1. 세션 관리

```python
# Redis에서 세션 조회 (빠른 접근)
messages = await redis_session_manager.get_session(session_id)

# PostgreSQL에 영구 저장 (백그라운드)
save_conversation_to_db(session_id, messages)
```

#### 2. 로깅

```python
# API 요청 로깅
log_api_request(
    session_id=session_id,
    endpoint="/api/chat",
    method="POST",
    request_data=request_data,
    response_data=response_data,
    status_code=200,
    processing_time_ms=processing_time
)

# 비용 로깅
log_cost(
    session_id=session_id,
    service_type="chat",
    model=model,
    input_tokens=input_tokens,
    output_tokens=output_tokens,
    cost_usd=cost_usd
)
```

#### 3. Fallback 메커니즘

Redis나 DB 연결 실패 시 메모리 기반 fallback으로 자동 전환되어 서비스 중단을 방지합니다.

## 확장 및 개선

### 현재 구현 사항

- ✅ 기본 STT, ChatGPT, TTS 통합
- ✅ 환경변수 기반 설정 관리
- ✅ Redis 기반 세션 관리
- ✅ PostgreSQL 영구 저장
- ✅ API 요청 로깅
- ✅ 비용 추적
- ✅ WebSocket 실시간 통신
- ✅ CORS 설정
- ✅ Docker Compose 구성
- ✅ Fallback 메커니즘

### 향후 개선 가능한 사항

1. **인증 및 권한 관리**
   - API 키 기반 인증
   - 사용자별 권한 관리
   - Rate Limiting

2. **모니터링 및 헬스체크**
   - Prometheus 메트릭
   - 로깅 시스템 통합
   - 에러 추적

3. **성능 최적화**
   - 비동기 처리 최적화
   - 캐싱 전략
   - 로드 밸런싱
   - 파티셔닝 (대용량 로그 테이블)

4. **데이터 아카이빙**
   - 오래된 로그 자동 아카이빙
   - 데이터 보관 정책

---

## 기술 스택

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **OpenAI API**: Whisper, ChatGPT, TTS
- **Uvicorn**: ASGI 서버
- **Pydantic**: 데이터 검증 및 설정 관리
- **Python-multipart**: 파일 업로드 처리
- **Aiofiles**: 비동기 파일 I/O

---

## 문제 해결

### OpenAI API 키 오류

```
Error: Invalid API key
```

`.env` 파일에 올바른 `OPENAI_API_KEY`가 설정되어 있는지 확인하세요.

### 포트 충돌

```
Error: Address already in use
```

다른 포트를 사용하거나 기존 프로세스를 종료하세요:
```bash
# 포트 변경
uvicorn main:app --port 8001

# 또는 기존 프로세스 종료
lsof -ti:8000 | xargs kill
```

### 의존성 설치 오류

```bash
# Python 버전 확인 (3.8 이상 필요)
python --version

# 가상환경 재생성
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 라이선스

프로젝트 라이선스에 따라 배포됩니다.

---

## Maintainer

- TBD

---

## 참고 자료

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [OpenAI API 문서](https://platform.openai.com/docs)
- [Uvicorn 문서](https://www.uvicorn.org/)
