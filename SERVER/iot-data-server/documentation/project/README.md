# IoT Care Backend - WAS Server

## 📋 프로젝트 개요

독거노인 통합 돌봄 서비스 백엔드 시스템을 위한 Docker Compose 기반 FastAPI 프로젝트입니다.

## 🏗️ 아키텍처

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL (외부 서버 연결)
- **Cache & Session**: Redis
- **Web Server**: Caddy (리버스 프록시 + SSL)
- **Container**: Docker Compose
- **Architecture**: Clean Architecture + Dependency Injection

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 환경 변수 파일 생성
cp env.example .env

# .env 파일 수정 (데이터베이스 연결 정보 등)
```

### 2. Docker Compose 실행

```bash
# 로컬 환경
./docker-run.sh local

# 개발 환경
./docker-run.sh dev

# 운영 환경
./docker-run.sh prod
```

### 3. 수동 실행

```bash
# 로컬 환경
docker-compose up -d

# 개발 환경
docker-compose -f docker-compose.dev.yml up -d

# 운영 환경
docker-compose -f docker-compose.prod.yml up -d
```

## 📁 프로젝트 구조

```
services/was-server/
├── app/                    # FastAPI 애플리케이션
│   ├── domain/            # 도메인 모델
│   ├── use_cases/         # 비즈니스 로직
│   ├── interfaces/        # 인터페이스 (컨트롤러, 리포지토리)
│   ├── infrastructure/    # 인프라 구현
│   └── main.py           # 애플리케이션 진입점
├── alembic/               # 데이터베이스 마이그레이션
├── tests/                 # 테스트 코드
├── docker/                # Docker 관련 파일
├── docs/                  # 문서
├── config/                # 설정 파일
├── logs/                  # 로그 파일
├── docker-compose.yml     # 로컬 환경
├── docker-compose.dev.yml # 개발 환경
├── docker-compose.prod.yml # 운영 환경
├── Caddyfile*             # Caddy 설정
├── Dockerfile             # FastAPI 컨테이너 빌드
├── requirements.txt       # Python 패키지
├── .gitignore            # Git 무시 파일
├── env.example           # 환경 변수 예시
└── docker-run.sh         # 실행 스크립트
```

## 🔧 환경별 설정

### Local Environment
- **Port**: 8000 (FastAPI), 80 (Caddy), 16379 (Redis)
- **Database**: localhost:15432
- **SSL**: 비활성화

### Development Environment
- **Port**: 8001 (FastAPI), 8080 (Caddy), 16380 (Redis)
- **Database**: localhost:15432
- **SSL**: 비활성화
- **Debug**: 활성화

### Production Environment
- **Port**: 8000 (FastAPI), 80/443 (Caddy), 6379 (Redis)
- **Database**: EC2 PostgreSQL 서버
- **SSL**: Let's Encrypt 자동 적용
- **Workers**: 4개

## 🌐 서비스 접속

### Local
- **FastAPI**: http://localhost:8000
- **Caddy**: http://localhost
- **API Docs**: http://localhost:8000/docs

### Development
- **FastAPI**: http://localhost:8001
- **Caddy**: http://localhost:8080
- **API Docs**: http://localhost:8001/docs

### Production
- **FastAPI**: 내부 네트워크
- **Caddy**: https://your-domain.com
- **API Docs**: https://your-domain.com/docs

## 📊 모니터링

### Health Check
```bash
# 애플리케이션 상태 확인
curl http://localhost/health

# 컨테이너 상태 확인
docker-compose ps
```

### 로그 확인
```bash
# 전체 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f app
docker-compose logs -f redis
docker-compose logs -f caddy
```

## 🔒 보안

- **PostgreSQL**: 외부 서버 직접 연결
- **Redis**: 컨테이너 내부 네트워크
- **Caddy**: 자동 SSL 인증서 관리
- **FastAPI**: 보안 헤더 자동 적용

## 🧪 테스트

```bash
# 테스트 실행
pytest

# 테스트 커버리지
pytest --cov=app

# HTML 리포트 생성
pytest --html=test-report.html
```

## 📝 개발 가이드

자세한 개발 가이드는 `docs/` 폴더를 참조하세요.

## 🤝 기여

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

