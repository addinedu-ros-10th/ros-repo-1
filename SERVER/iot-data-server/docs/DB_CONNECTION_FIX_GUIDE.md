# 데이터베이스 연결 문제 해결 가이드

## 🔍 문제 요약

1. **DB 연결 오류**: `[Errno 113] No route to host`
2. **테이블 생성 실패**: `relation "residents" does not exist`

## ✅ 해결된 사항

### 1. 테이블 생성 문제 해결
- `app/main.py`에서 `ResidentInfo` 모델을 명시적으로 임포트하도록 수정
- `create_tables()` 실행 시 모든 모델이 포함되도록 보장

### 2. DB_HOST 환경변수 처리 개선
- `app/core/config.py`에서 Docker 컨테이너 내부 실행 여부 감지
- 호스트 접근 문제에 대한 경고 로그 추가

## 🛠️ 추가 해결 방법

### 방법 1: host.docker.internal 사용 (권장)

**docker-compose.yml**에 이미 `extra_hosts` 설정이 있으므로, `.env.local`에서:

```bash
# .env.local
DB_HOST=host.docker.internal
```

그리고 Docker 컨테이너 재시작:
```bash
docker-compose down
docker-compose up -d
```

### 방법 2: 호스트 머신의 실제 IP 사용

1. 호스트 머신의 IP 주소 확인:
```bash
# Linux/Mac
ip addr show | grep -E "inet " | grep -v 127.0.0.1

# 또는
hostname -I
```

2. `.env.local` 파일 수정:
```bash
# 예시: 호스트 IP가 192.168.0.10인 경우
DB_HOST=192.168.0.10
```

3. Docker 컨테이너 재시작:
```bash
docker-compose down
docker-compose up -d
```

### 방법 3: USE_HOST_DOCKER_INTERNAL 환경변수 사용

`.env.local`에 추가:
```bash
USE_HOST_DOCKER_INTERNAL=true
DB_HOST=host.docker.internal
```

## 📋 테이블 생성 확인

테이블이 생성되었는지 확인:

```bash
# 컨테이너 내부에서 확인
docker exec -it iot-care-app python3 scripts/check_db_status.py

# 또는 직접 SQL 실행
docker exec -it iot-care-app psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "\dt residents"
```

## 🔄 문제 해결 체크리스트

- [ ] `.env.local`의 `DB_HOST` 값이 Docker 컨테이너에서 접근 가능한 주소인지 확인
- [ ] `host.docker.internal` 사용 시 `docker-compose.yml`에 `extra_hosts` 설정 확인
- [ ] PostgreSQL 서버가 실행 중이고 해당 IP에서 수신 중인지 확인
- [ ] 방화벽 설정 확인 (PostgreSQL 포트 열림)
- [ ] Docker 컨테이너 재시작 후 로그 확인
- [ ] `residents` 테이블 생성 확인

## 🐛 문제가 지속되는 경우

1. **네트워크 연결 테스트**:
```bash
# 컨테이너 내부에서 호스트 접근 테스트
docker exec -it iot-care-app ping -c 3 host.docker.internal
docker exec -it iot-care-app ping -c 3 192.168.0.8
```

2. **PostgreSQL 연결 테스트**:
```bash
# 컨테이너 내부에서 직접 연결 테스트
docker exec -it iot-care-app psql -h host.docker.internal -p 15432 -U svc_dev -d iot_care
```

3. **로그 확인**:
```bash
docker logs iot-care-app --tail 100
```

