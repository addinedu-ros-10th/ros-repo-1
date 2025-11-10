# SERVER/app-server 프로젝트 리포트

**작성일**: 2025-01-27  
**프로젝트 경로**: `SERVER/app-server`

---

## 📋 프로젝트 개요

`app-server`는 **FastAPI 기반의 BFF (Backend-for-Frontend) 및 메인 API 게이트웨이** 서버입니다. Deep Learning/IoT Care 애플리케이션을 위한 백엔드 서버로, 스케줄러, 관리자 패널, ML 레지스트리, 알림 시스템 등 다양한 기능을 제공합니다.

### 주요 목적
- 인증, 라우팅, API 집계 로직 제공
- ML 모델 레지스트리 관리 (Dataset, Experiment, Frame Prediction, Detection Event)
- 스케줄 작업 관리 및 실행
- 실시간 알림 시스템 (WebSocket 기반)
- 관리자 패널 제공 (SQLAdmin)

---

## 🏗️ 아키텍처

### 아키텍처 패턴
- **헥사고날 아키텍처 (Hexagonal Architecture)** - 부분 적용
- **Repository Pattern**
- **Dependency Injection** (dependency-injector)
- **Factory Pattern**

### 레이어 구조
```
app/
├── domain/              # 도메인 레이어
│   ├── entities/        # 엔티티 (Dataset, Experiment, ScheduledJob 등)
│   ├── ports/           # 포트 인터페이스 (Repository, Service)
│   ├── services/        # 도메인 서비스
│   └── value_objects/   # 값 객체
├── application/         # 애플리케이션 레이어
│   ├── dto/            # 데이터 전송 객체
│   └── use_cases/      # 유즈케이스
├── adapters/           # 어댑터 레이어
│   ├── http/           # HTTP 라우터 (FastAPI)
│   ├── repositories/   # 리포지토리 구현
│   └── scheduler/      # 스케줄러 어댑터
├── infrastructure/     # 인프라 레이어
│   ├── db/             # 데이터베이스 (SQLAlchemy, Alembic)
│   ├── di/             # 의존성 주입
│   └── settings.py     # 설정 관리
├── services/           # 애플리케이션 서비스
│   ├── scheduler_service.py
│   ├── notify_dispatcher.py
│   └── ws_notify.py
└── admin/              # 관리자 패널 (SQLAdmin)
```

---

## 🛠️ 기술 스택

### 핵심 프레임워크
- **Python**: 3.12 (strict requirement: `>=3.12,<3.13`)
- **FastAPI**: 0.104.0+ (비동기 웹 프레임워크)
- **Uvicorn**: 0.24.0+ (ASGI 서버)

### 데이터베이스
- **PostgreSQL** (비동기)
  - `SQLAlchemy[asyncio]`: 2.0.0+ (ORM)
  - `asyncpg`: 0.29.0+ (비동기 PostgreSQL 드라이버)
  - `psycopg2-binary`: 2.9.0+ (동기 드라이버, SQLAdmin용)
  - `Alembic`: 1.13.0+ (마이그레이션)

### 스케줄러
- **APScheduler**: 3.10.0+ (고급 Python 스케줄러)

### 관리자 UI
- **SQLAdmin**: 0.17.0+ (FastAPI용 관리자 패널)

### 인증 및 보안
- **python-jose[cryptography]**: 3.3.0+ (JWT)
- **passlib[bcrypt]**: 1.7.4+ (비밀번호 해싱)

### 기타 주요 라이브러리
- **Pydantic**: 2.5.0+ (데이터 검증)
- **Pydantic Settings**: 2.1.0+ (설정 관리)
- **Redis**: 5.0.0+ (캐시)
- **httpx**: 0.25.0+ (HTTP 클라이언트)
- **dependency-injector**: 4.41.0+ (의존성 주입)
- **structlog**: 23.2.0+ (구조화된 로깅)

### 개발 도구
- **pytest**: 7.4.0+ (테스트)
- **black**: 23.0.0+ (코드 포맷팅)
- **isort**: 5.12.0+ (import 정렬)
- **mypy**: 1.7.0+ (타입 체킹)

---

## 🚀 주요 기능

### 1. ML 레지스트리 API
- **Dataset API** (`/api/v1/datasets`)
  - CRUD 작업 (생성, 조회, 수정, 삭제)
  - 필터링 및 페이징
- **Experiment API** (`/api/v1/experiments`)
  - 실험 관리
  - 데이터셋과의 연관 관계
- **Frame Prediction API** (`/api/v1/frame-predictions`)
  - 프레임 예측 데이터 관리
  - 배치 생성 지원
- **Detection Event API** (`/api/v1/detection-events`)
  - 이벤트 감지 데이터 관리

### 2. 스케줄러 시스템
- **APScheduler 통합**
  - Cron 표현식 기반 스케줄링
  - 작업 수동 실행
  - 작업 상태 모니터링
- **스케줄 작업 관리**
  - `/api/v1/scheduled-jobs`: 작업 목록 조회
  - `/api/v1/scheduler/status`: 스케줄러 상태
  - `/api/v1/scheduler/reload`: 스케줄러 재로드

### 3. 알림 시스템
- **WebSocket 기반 실시간 알림**
  - `/ws/notify`: WebSocket 엔드포인트
  - 백그라운드 디스패처를 통한 비동기 알림 처리
- **알림 관리 API**
  - `/api/v1/notify/messages`: 메시지 관리
  - `/api/v1/notify/deliveries`: 배송 관리
  - `/api/v1/notify/devices`: 디바이스 관리
  - `/api/v1/notify/queues`: 큐 관리

### 4. 관리자 패널
- **SQLAdmin 통합**
  - `/admin`: 웹 기반 관리자 인터페이스
  - 스케줄 작업 관리 UI
  - 데이터베이스 모델 CRUD

### 5. 데이터베이스 관리
- **멀티 엔진 지원**
  - `DB_APP_URL`: 신규 스키마 (쓰기 허용)
  - `DB_LEGACY_URL`: 레거시 스키마 (읽기 전용)
  - `ML_DB_URL`: ML 스키마 (ML 레지스트리 전용, 없으면 DB_APP_URL 사용)
- **Alembic 마이그레이션**
  - 비삭제 정책 적용
  - 타임존: Asia/Seoul

---

## 📁 프로젝트 구조

```
SERVER/app-server/
├── app/                          # 메인 애플리케이션 코드
│   ├── main.py                   # FastAPI 앱 팩토리
│   ├── scheduler_app.py          # 스케줄러 앱
│   ├── domain/                   # 도메인 레이어
│   ├── application/              # 애플리케이션 레이어
│   ├── adapters/                 # 어댑터 레이어
│   ├── infrastructure/           # 인프라 레이어
│   ├── services/                 # 애플리케이션 서비스
│   └── admin/                    # 관리자 패널
├── docker/                       # Docker 설정
│   ├── compose.base.yml          # 기본 Docker Compose
│   ├── compose.local.yml         # 로컬 환경
│   ├── compose.prod.yml          # 프로덕션 환경
│   ├── python.Dockerfile         # Python 이미지
│   └── nginx.Dockerfile          # Nginx 이미지
├── nginx/                        # Nginx 설정
│   ├── nginx.conf
│   └── conf.d/
├── scripts/                      # 유틸리티 스크립트
│   ├── docker_compose_manager.sh
│   ├── ssh_tunnel_manager.sh
│   └── test_db_connection.py
├── secret/                       # 환경 변수 파일 (Git 제외)
│   ├── .env.local                # 로컬 환경
│   └── .env.prod                 # 프로덕션 환경
├── staging/                      # 스테이징 문서
├── docs/                         # 문서
│   ├── apis/                     # API 문서
│   └── *.md                      # 개발 가이드
├── tests/                        # 테스트 코드
├── alembic.ini                   # Alembic 설정
└── pyproject.toml                # 프로젝트 설정
```

---

## 🔧 실행 요구사항

### 필수 요구사항
1. **Python 3.12** (정확히 3.12.x 버전 필요)
   ```bash
   python3 --version  # Python 3.12.3 확인됨 ✅
   ```

2. **PostgreSQL 데이터베이스**
   - 신규 스키마용 DB (DB_APP_URL)
   - 레거시 스키마용 DB (DB_LEGACY_URL, 선택)
   - ML 스키마용 DB (ML_DB_URL, 없으면 DB_APP_URL 사용)

3. **Redis** (캐시용)

4. **Docker & Docker Compose**
   ```bash
   docker --version        # Docker 설치 확인됨 ✅
   docker compose version  # Docker Compose v2.24.6 확인됨 ✅
   ```

### 선택적 요구사항
- **SSH 터널** (로컬 개발 시 원격 DB 접근용)
- **Nginx** (프로덕션 환경)

---

## ⚙️ 환경 설정

### 환경 변수 파일
프로젝트는 환경별 설정 파일을 사용합니다:
- `secret/.env.local`: 로컬 개발 환경
- `secret/.env.prod`: 프로덕션 환경

### 필수 환경 변수

#### 기본 애플리케이션 설정
```bash
APP_ENV=local                    # 또는 production
DEBUG=true                       # 로컬: true, 프로덕션: false
API_V1_STR=/api/v1
```

#### 데이터베이스 설정
```bash
DB_MODE=local_ssh               # 또는 aws_internal
DB_APP_URL=postgresql+asyncpg://user:pass@host:port/dbname
DB_LEGACY_URL=postgresql+asyncpg://user:pass@host:port/dbname  # 선택
ML_DB_URL=postgresql+asyncpg://user:pass@host:port/dbname      # 선택 (없으면 DB_APP_URL 사용)
```

#### Redis 설정
```bash
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=                  # 선택
REDIS_DB=0
```

#### 보안 설정
```bash
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
```

#### 관리자 설정
```bash
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123          # 프로덕션에서는 강력한 비밀번호 사용
ADMIN_EMAIL=admin@localhost
```

#### 스케줄러 설정
```bash
SCHEDULER_TIMEZONE=Asia/Seoul
SCHEDULER_MAX_WORKERS=10
SCHEDULER_COALESCE=true
```

#### SSH 터널 설정 (로컬 개발 시)
```bash
SSH_TUNNEL_ENABLE=true
SSH_TUNNEL_LOCAL_PORT=15432
SSH_TUNNEL_REMOTE_HOST=<rds-host>
SSH_TUNNEL_REMOTE_PORT=5432
SSH_TUNNEL_BASTION_HOST=<bastion-ip>
SSH_TUNNEL_USER=ubuntu
SSH_TUNNEL_KEY_PATH=~/.ssh/id_rsa
```

**전체 환경 변수 목록은 `staging/env_variables_guide.md` 참조**

---

## 🚀 실행 방법

### 1. 로컬 개발 환경 (Docker Compose)

```bash
cd SERVER/app-server

# 환경 변수 파일 준비
cp secret/.env.local.example secret/.env.local
# secret/.env.local 파일을 편집하여 실제 값 입력

# Docker Compose로 실행
docker compose -f docker/compose.base.yml -f docker/compose.local.yml \
  --env-file secret/.env.local up -d

# 로그 확인
docker compose logs -f api
```

### 2. 직접 실행 (로컬 개발)

```bash
cd SERVER/app-server

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate    # Windows

# 의존성 설치
pip install -e .

# 환경 변수 설정
export APP_ENV=local
export DB_APP_URL=postgresql+asyncpg://user:pass@localhost:15432/dbname
# ... 기타 환경 변수 설정

# 애플리케이션 실행
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload
```

### 3. 프로덕션 환경

```bash
cd SERVER/app-server

# 환경 변수 파일 준비
cp secret/.env.prod.example secret/.env.prod
# secret/.env.prod 파일을 편집하여 실제 값 입력

# Docker Compose로 실행
docker compose -f docker/compose.base.yml -f docker/compose.prod.yml \
  --env-file secret/.env.prod up -d
```

---

## 🌐 주요 엔드포인트

### 공개 API
- `GET /`: 루트 엔드포인트 (시스템 정보)
- `GET /health`: 헬스 체크
- `GET /docs`: Swagger UI
- `GET /redoc`: ReDoc 문서

### ML 레지스트리 API
- `GET /api/v1/datasets`: 데이터셋 목록
- `POST /api/v1/datasets`: 데이터셋 생성
- `GET /api/v1/experiments`: 실험 목록
- `POST /api/v1/experiments`: 실험 생성
- `GET /api/v1/frame-predictions`: 프레임 예측 목록
- `POST /api/v1/frame-predictions`: 프레임 예측 생성
- `GET /api/v1/detection-events`: 감지 이벤트 목록
- `POST /api/v1/detection-events`: 감지 이벤트 생성

### 스케줄러 API
- `GET /api/v1/scheduled-jobs`: 스케줄 작업 목록
- `GET /api/v1/scheduler/status`: 스케줄러 상태
- `POST /api/v1/scheduler/reload`: 스케줄러 재로드

### 알림 API
- `GET /api/v1/notify/messages`: 알림 메시지 목록
- `POST /api/v1/notify/messages`: 알림 메시지 생성
- `GET /api/v1/notify/devices`: 디바이스 목록
- `WS /ws/notify`: WebSocket 알림 연결

### 관리자 패널
- `GET /admin`: SQLAdmin 관리자 패널

### 내부 API (Internal)
- `GET /internal/scheduled-jobs`: 내부 스케줄 작업 조회
- `POST /internal/scheduled-jobs/{job_id}/execute`: 작업 수동 실행
- `GET /internal/tables`: 데이터베이스 테이블 목록
- `GET /internal/database/info`: 데이터베이스 정보

---

## ⚠️ 현재 환경에서의 제약사항 및 주의사항

### ✅ 확인된 사항
1. **Python 버전**: Python 3.12.3 설치 확인됨 ✅
2. **Docker**: Docker 설치 확인됨 ✅
3. **Docker Compose**: Docker Compose v2.24.6 설치 확인됨 ✅

### ⚠️ 주의사항

#### 1. 환경 변수 파일 누락
- `secret/.env.local` 파일이 존재하지 않을 수 있음
- 환경 변수 파일을 생성하고 필요한 값들을 설정해야 함
- **조치**: `staging/env_variables_guide.md` 참조하여 환경 변수 파일 생성

#### 2. 데이터베이스 연결
- 로컬 개발 시 SSH 터널이 필요할 수 있음
- `DB_APP_URL`, `ML_DB_URL`, `DB_LEGACY_URL` 환경 변수 설정 필수
- **조치**: 
  - SSH 터널 스크립트 사용: `scripts/ssh_tunnel_manager.sh`
  - 또는 직접 DB 연결 정보 설정

#### 3. Redis 서비스
- Docker Compose를 사용하지 않는 경우, Redis 서버를 별도로 실행해야 함
- **조치**: Docker Compose 사용 또는 로컬 Redis 서버 실행

#### 4. 의존성 설치
- 프로젝트는 `pyproject.toml` 기반으로 패키지 관리
- `pip install -e .` 명령으로 설치 필요
- **조치**: 가상환경 생성 후 의존성 설치

#### 5. 데이터베이스 마이그레이션
- Alembic 마이그레이션 실행 필요
- **조치**: 
  ```bash
  alembic upgrade head
  ```

#### 6. 포트 충돌
- 기본 포트: 8000 (API), 80 (Nginx), 6379 (Redis)
- 다른 서비스와 포트 충돌 가능
- **조치**: 환경 변수 또는 Docker Compose 설정에서 포트 변경

#### 7. 파일 권한
- `secret/` 디렉토리 접근 권한 확인 필요
- Docker 볼륨 마운트 시 권한 문제 가능
- **조치**: 적절한 파일 권한 설정

---

## 📝 개발 가이드

### API 개발을 이어서 진행하기 위한 가이드

#### 1. 프로젝트 구조 이해
- **헥사고날 아키텍처** 준수
- 새로운 API 추가 시 다음 순서로 작업:
  1. `domain/entities/`: 엔티티 정의
  2. `domain/ports/`: 리포지토리 인터페이스 정의
  3. `infrastructure/db/models/`: SQLAlchemy 모델 정의
  4. `adapters/repositories/`: 리포지토리 구현
  5. `application/use_cases/`: 유즈케이스 구현
  6. `adapters/http/`: HTTP 라우터 구현
  7. `app/main.py`: 라우터 등록

#### 2. 데이터베이스 세션 사용
- ML 레지스트리 API: `get_ml_session()` 사용
- 일반 API: `get_app_session()` 사용
- 레거시 데이터: `get_legacy_session()` 사용

#### 3. 의존성 주입 패턴
```python
from fastapi import Depends
from app.infrastructure.db.session import get_ml_session
from app.adapters.repositories.your_repository_impl import YourRepositoryImpl

def get_repository(session: AsyncSession = Depends(get_ml_session)):
    return YourRepositoryImpl(session)
```

#### 4. 테스트 작성
- `tests/` 디렉토리에 테스트 작성
- pytest 사용
- `tests/unit/`, `tests/integration/`, `tests/e2e/` 구조 준수

#### 5. 코드 스타일
- **Black**: 코드 포맷팅 (라인 길이: 88)
- **isort**: import 정렬
- **mypy**: 타입 체킹 (strict 모드)

---

## 📚 참고 문서

### 프로젝트 내 문서
- `README.md`: 기본 프로젝트 정보
- `staging/env_variables_guide.md`: 환경 변수 가이드
- `docs/app_server_build_action_items_20250912.md`: 빌드 액션 아이템
- `docs/ml_registry_api_development_plan.md`: ML 레지스트리 API 개발 계획
- `docs/notification_system_development.md`: 알림 시스템 개발 문서
- `docs/apis/*.md`: 각 API 엔드포인트 문서

### 외부 문서
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [APScheduler 문서](https://apscheduler.readthedocs.io/)

---

## 🔍 다음 단계

### API 개발을 위한 준비사항
1. ✅ 프로젝트 구조 파악 완료
2. ✅ 환경 요구사항 확인 완료
3. ⏳ 환경 변수 파일 생성 필요
4. ⏳ 데이터베이스 연결 테스트 필요
5. ⏳ 로컬 개발 환경 구축 필요

### 권장 작업 순서
1. **환경 변수 파일 생성**
   ```bash
   cp staging/env_variables_guide.md secret/.env.local
   # 실제 값으로 수정
   ```

2. **데이터베이스 연결 테스트**
   ```bash
   python scripts/test_db_connection.py
   ```

3. **의존성 설치 및 테스트**
   ```bash
   pip install -e .
   pytest tests/
   ```

4. **로컬 서버 실행 및 테스트**
   ```bash
   uvicorn app.main:create_app --factory --reload
   ```

5. **새로운 API 개발 시작**
   - 기존 API 라우터 참조 (`app/adapters/http/`)
   - 헥사고날 아키텍처 패턴 준수

---

## 📞 문제 해결

### 일반적인 문제
1. **데이터베이스 연결 실패**
   - 환경 변수 확인: `DB_APP_URL`, `ML_DB_URL`
   - SSH 터널 상태 확인 (로컬 개발 시)
   - 네트워크 연결 확인

2. **의존성 설치 오류**
   - Python 버전 확인 (3.12 필요)
   - 가상환경 활성화 확인
   - `pip install --upgrade pip` 실행

3. **포트 충돌**
   - 다른 서비스가 포트 사용 중인지 확인
   - 환경 변수에서 포트 변경

4. **마이그레이션 오류**
   - 데이터베이스 스키마 확인
   - Alembic 버전 확인: `alembic current`

---

**리포트 작성 완료**

