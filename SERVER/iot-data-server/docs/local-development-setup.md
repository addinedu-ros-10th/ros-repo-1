# 🚀 로컬 개발 환경 설정 가이드

## 📋 개요
로컬 개발 환경에서 IoT Care Backend System을 실행하기 위한 설정 가이드입니다.

## 🔧 필수 사전 준비사항

### 1. Docker & Docker Compose 설치
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 사용자를 docker 그룹에 추가 (재로그인 필요)
sudo usermod -aG docker $USER
```

### 2. Python 가상환경 설정
```bash
# 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate     # Windows
```

## 🌐 네트워크 설정

### 0. 환경변수 파일 변경사항 (중요!)
```bash
# 이전: env.* 파일 사용 (더 이상 사용하지 않음)
# 현재: .env.* 파일 사용 (권장)

# 사용 가능한 환경변수 파일:
# - .env.local: 로컬 개발 환경
# - .env.dev: 개발 환경
# - .env.prod: 프로덕션 환경

# Docker Compose는 자동으로 .env.local 파일을 로드합니다
```

### 1. 개발 PC IP 주소 확인
```bash
# Linux/Mac
ifconfig | grep -E "inet " | grep -v 127.0.0.1

# Windows
ipconfig | findstr "IPv4"

# 주의: Docker 브리지 네트워크 IP는 제외
# - br-*: Docker 브리지 네트워크 (172.18.0.1, 172.17.0.1)
# - docker0: Docker 기본 브리지 (172.17.0.1)
# - veth*: Docker 가상 이더넷 인터페이스
# - 실제 개발 PC IP는 wlo1(무선) 또는 enp3s0(유선)에서 확인
```

### 2. 환경변수 파일 설정
```bash
# .env.local 파일이 이미 존재하는지 확인
ls -la .env.*

# .env.local 파일이 없다면 .env.example에서 복사
cp .env.example .env.local

# DB_HOST 업데이트 (실제 개발 PC IP로 변경)
# 주의: Docker 브리지 IP(172.18.0.1, 172.17.0.1)는 사용하지 마세요
sed -i 's/DB_HOST=.*/DB_HOST=YOUR_ACTUAL_IP/' .env.local

# 예시: 개발 PC IP가 192.168.0.15인 경우
sed -i 's/DB_HOST=.*/DB_HOST=192.168.0.15/' .env.local

# 또는 이더넷을 사용하는 경우
# sed -i 's/DB_HOST=.*/DB_HOST=YOUR_ETHERNET_IP/' .env.local
```

## 🗄️ 데이터베이스 설정

### 1. 외부 PostgreSQL 데이터베이스 정보
```bash
# .env.local 파일 내용 확인
cat .env.local

# 예상 출력:
# Database (PostgreSQL - External)
# DB_USER=svc_dev
# DB_PASSWORD=IOT_dev_123!@#
# DB_HOST=192.168.0.15  # 개발 PC IP (WiFi)
# DB_PORT=15432
# DB_NAME=iot_care

# 네트워크 인터페이스별 IP 주소:
# - WiFi (wlo1): 192.168.0.15 (권장)
# - Docker 브리지: 172.18.0.1, 172.17.0.1 (사용 금지)
# - 이더넷 (enp3s0): 비활성화 상태
```

### 2. 데이터베이스 연결 테스트
```bash
# 포트 연결 테스트
telnet YOUR_DB_HOST YOUR_DB_PORT

# 예시 (WiFi 사용 시)
telnet 192.168.0.15 15432

# 또는 이더넷 사용 시
# telnet YOUR_ETHERNET_IP 15432
```

## 🐳 Docker 컨테이너 실행

### 1. 컨테이너 시작
```bash
# 기존 컨테이너 정리
docker-compose down

# 캐시 제거 및 재빌드 (권장)
docker-compose build --no-cache
docker-compose up -d

# 또는 일반 시작
docker-compose up -d
```

### 2. 컨테이너 상태 확인
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker logs iot-care-app --tail 50

# 서버 상태 확인
curl http://localhost:8000/health
```

## 🔄 서버 재시작 시 필수 작업

### 1. IP 주소 변경 감지 및 업데이트
```bash
# 1. 현재 개발 PC IP 확인
ifconfig | grep -E "inet " | grep -v 127.0.0.1

# 2. .env.local 파일의 DB_HOST 업데이트
sed -i 's/DB_HOST=.*/DB_HOST=NEW_IP_ADDRESS/' .env.local

# 3. 변경사항 확인
grep "DB_HOST" .env.local
```

### 2. Docker 컨테이너 재시작
```bash
# 컨테이너 중지
docker-compose down

# 환경변수 적용 후 재시작
docker-compose up -d

# 서버 상태 확인
sleep 10 && curl http://localhost:8000/health
```

### 3. 데이터베이스 연결 확인
```bash
# 컨테이너 내부에서 환경변수 확인
docker exec -it iot-care-app python -c "
from app.core.config import settings
print(f'DB_HOST: {settings.DB_HOST}, DB_PORT: {settings.DB_PORT}')
"
```

## 🧪 테스트 실행

### 1. 통합 테스트 실행
```bash
# 통합 테스트 실행
python integration_test.py

# 또는 특정 API만 테스트
python -c "
import asyncio
from integration_test import IoTAPIIntegrationTest

async def test_single_api():
    async with IoTAPIIntegrationTest() as tester:
        await tester.test_health_check()
        # 특정 API 테스트 로직

asyncio.run(test_single_api())
"
```

### 2. 문제 해결 체크리스트
- [ ] 개발 PC IP 주소 확인
- [ ] .env.local 파일의 DB_HOST 업데이트
- [ ] Docker 컨테이너 재시작
- [ ] 데이터베이스 연결 테스트
- [ ] 서버 Health Check 성공
- [ ] 통합 테스트 실행

## 🚨 문제 해결

### 1. DB 연결 실패
```bash
# 로그 확인
docker logs iot-care-app --tail 100

# 네트워크 연결 테스트
telnet YOUR_DB_HOST YOUR_DB_PORT

# 환경변수 확인
docker exec -it iot-care-app env | grep DB
```

### 2. API 엔드포인트 404
```bash
# API 라우터 등록 확인
curl http://localhost:8000/docs

# 특정 엔드포인트 테스트
curl http://localhost:8000/api/users
```

### 3. 컨테이너 재시작 문제
```bash
# 강제 정리
docker-compose down --volumes --remove-orphans
docker system prune -f
docker-compose up -d
```

## 📚 추가 리소스

- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [PostgreSQL 연결 가이드](https://www.postgresql.org/docs/)

## 🔗 연관 문서

- [프로젝트 구조 가이드](../doc/project-structure.md)
- [API 구현 진행상황](../task/api-implementation-progress.md)
- [문제 해결 가이드](../task/issues-and-solutions.md)

---

**⚠️ 중요**: 서버 재시작 시마다 개발 PC IP 주소가 변경되었는지 확인하고, `.env.local` 파일을 업데이트해야 합니다!

**🔍 IP 주소 확인 팁**:
```bash
# WiFi IP 확인 (권장)
ifconfig wlo1 | grep "inet " | awk '{print $2}'

# 이더넷 IP 확인
ifconfig enp3s0 | grep "inet " | awk '{print $2}'

# Docker 브리지 IP는 제외 (172.16.0.0/12, 192.168.0.0/16 범위)
ifconfig | grep -E "inet " | grep -v "127.0.0.1\|172\.\|192\.168\."
``` 