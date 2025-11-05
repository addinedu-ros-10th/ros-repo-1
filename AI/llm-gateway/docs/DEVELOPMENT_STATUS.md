# AI/llm-gateway 프로젝트 개발 현황 리포트

**브랜치**: `feat/AI/llm-gateway__voice_interface__RP-22`  
**작성일**: 2025-01-27

---

## 📊 프로젝트 개요

FastAPI 기반 한국어 음성 인터페이스 서버로, OpenAI Whisper (STT), ChatGPT, TTS를 통합한 API 서버입니다.

### 핵심 기능
- 🎤 **STT (Speech-to-Text)**: 음성 파일을 텍스트로 변환
- 💬 **ChatGPT 통합**: 텍스트 채팅 및 스트리밍 채팅
- 🔊 **TTS (Text-to-Speech)**: 텍스트를 음성 파일로 변환
- 🔄 **통합 음성 처리**: STT → ChatGPT → TTS 원스톱 처리
- 📡 **WebSocket 지원**: 실시간 양방향 통신
- 💾 **Redis 세션 관리**: 분산 환경 지원, 30일 TTL
- 🗄️ **PostgreSQL 영구 저장**: 대화 히스토리, API 로그, 비용 추적

---

## 🏗️ 프로젝트 구조

```
AI/llm-gateway/
├── main.py                    # FastAPI 서버 메인 파일
├── config.py                  # 환경변수 및 설정 관리
├── database.py                # PostgreSQL 데이터베이스 관리
├── redis_session.py           # Redis 세션 관리
├── requirements.txt            # Python 의존성 패키지
├── Dockerfile                 # 서버 컨테이너 이미지 정의
├── docker-compose.yml         # 서버 및 Redis 컨테이너 구성
├── README.md                  # 사용 가이드 및 API 문서
├── database_schema.md          # 데이터베이스 스키마 설계 문서
├── WEBSOCKET_TEST_GUIDE.md    # WebSocket 테스트 가이드
├── test_websocket.html        # WebSocket 채팅 테스트 인터페이스
├── test_voice.html            # 음성 인터페이스 테스트 인터페이스
└── test_websocket.py          # Python WebSocket 클라이언트
```

---

## 🐛 디버깅 및 개선 사항

### 1. Pydantic Settings Validation 오류 해결

**문제점**:
- `openai_api_key`가 필수 필드로 설정되어 있어 환경변수가 없을 때 서버 시작 실패
- `ValidationError: Field required` 발생

**해결**:
- `openai_api_key`를 `Optional[str]`로 변경하여 기본값 `None` 허용
- `main.py`에서 환경변수 `OPENAI_API_KEY`를 폴백으로 사용하도록 개선

**변경 파일**: `config.py`, `main.py`

```python
# 변경 전
openai_api_key: str = Field(..., description="OpenAI API 키")

# 변경 후
openai_api_key: Optional[str] = Field(default=None, description="OpenAI API 키")
```

---

### 2. 환경 파일 로드 설정 오류 수정

**문제점**:
- `env_file = ".env,local"` 형식이 잘못되어 환경 파일 로드 실패

**해결**:
- `env_file = [".env", ".env.local"]`로 수정하여 순차적으로 로드
- `.env` 파일이 먼저 로드되고, `.env.local`이 나중에 로드되어 우선순위 적용

**변경 파일**: `config.py`

```python
# 변경 전
env_file = ".env,local"

# 변경 후
env_file = [".env", ".env.local"]  # .env와 .env.local 파일을 순차적으로 로드
```

---

### 3. Docker Compose 전용 환경변수 처리

**문제점**:
- `REDIS_EXTERNAL_PORT` 등 Docker Compose 전용 환경변수가 `.env.local`에 있어 Pydantic이 `Extra inputs are not permitted` 오류 발생

**해결**:
- `Config` 클래스에 `extra = "ignore"` 추가하여 정의되지 않은 환경변수 무시

**변경 파일**: `config.py`

```python
class Config:
    env_file = [".env", ".env.local"]
    env_file_encoding = "utf-8"
    case_sensitive = False
    extra = "ignore"  # 정의되지 않은 환경변수는 무시 (Docker Compose 전용 변수 등)
```

---

### 4. TTS 스트리밍 로직 개선

**문제점**:
- 이전에 `async for chunk in response.iter_bytes()` 사용 시 `TypeError` 발생 (해결됨)
- 스트리밍 로직이 여러 response 타입을 지원하도록 개선 필요

**개선**:
- `response.content` 우선 사용 (OpenAI SDK v1.0+ 권장 방식)
- 여러 response 타입 지원 (bytes, content 속성 등)
- 에러 처리 강화

**변경 파일**: `main.py`

---

### 5. ROS2 환경 호환성 개선

**문제점**:
- `pip install` 시 dependency conflicts 경고 발생
  - `launch-ros` requires `setuptools`
  - `generate-parameter-library-py` requires `jinja2`, `typeguard`

**해결**:
- `requirements.txt`에 누락된 의존성 추가

**변경 파일**: `requirements.txt`

```python
# 추가된 의존성
setuptools>=65.0.0  # 기본 패키지 관리 도구
jinja2>=3.1.0  # 템플릿 엔진 (일부 ROS2 패키지 필요)
typeguard>=4.0.0  # 타입 체크 유틸리티 (일부 ROS2 패키지 필요)
```

---

## 📝 주요 변경사항 요약

### 변경된 파일

1. **`config.py`**
   - `openai_api_key` 필드를 Optional로 변경
   - `env_file` 설정 수정 (리스트 형식)
   - `extra = "ignore"` 추가

2. **`main.py`**
   - OpenAI 클라이언트 초기화 시 환경변수 폴백 추가
   - TTS 스트리밍 로직 개선 (이전 수정사항 유지)

3. **`requirements.txt`**
   - ROS2 호환성을 위한 의존성 추가 (`setuptools`, `jinja2`, `typeguard`)

---

## ✅ 현재 상태

### 완료된 작업
- ✅ FastAPI 서버 구축 (STT, Chat, TTS, WebSocket)
- ✅ Docker Compose 운영 환경 구성
- ✅ Redis 세션 관리 구현
- ✅ PostgreSQL 데이터베이스 통합
- ✅ 테스트 환경 구축 (HTML, Python 클라이언트)
- ✅ 환경변수 설정 오류 해결
- ✅ Pydantic Settings validation 오류 해결
- ✅ ROS2 환경 호환성 개선

### 향후 개선 사항
- [ ] 비용 추적 로직 구현 완성
- [ ] API 요청 로깅 완성
- [ ] 성능 최적화
- [ ] 보안 강화 (API 키 암호화 등)

---

## 🚀 배포 및 테스트

### 로컬 테스트
```bash
cd AI/llm-gateway
docker-compose up -d
docker-compose logs -f llm-gateway
```

### 테스트 페이지
- WebSocket 테스트: `http://localhost:8000/test_websocket.html`
- 음성 인터페이스 테스트: `http://localhost:8000/test_voice.html`

---

## 📚 참고 문서

- `README.md`: 사용 가이드 및 API 문서
- `database_schema.md`: 데이터베이스 스키마 설계
- `WEBSOCKET_TEST_GUIDE.md`: WebSocket 테스트 가이드

