# 데이터베이스 마이그레이션 가이드

## 마이그레이션 자동 실행 여부

**현재 설정에서는 마이그레이션이 자동으로 실행되지 않습니다.**

Docker Compose를 다시 시작해도 마이그레이션은 자동으로 실행되지 않으므로, **수동으로 실행해야 합니다**.

## 마이그레이션 실행 방법

### 1. Docker 컨테이너 내에서 실행

```bash
# 실행 중인 컨테이너에 접속
docker compose exec api bash

# 컨테이너 내에서 마이그레이션 실행
alembic upgrade head
```

### 2. 호스트에서 직접 실행

```bash
# 환경 변수 설정 확인
export DB_APP_URL=postgresql+asyncpg://user:pass@host:port/dbname

# 마이그레이션 실행
cd SERVER/app-server
alembic upgrade head
```

### 3. Docker Compose 명령으로 실행

```bash
# 한 줄로 실행
docker compose exec api alembic upgrade head
```

## 자동 마이그레이션 설정 (선택사항)

자동 마이그레이션을 원한다면 `docker/compose.base.yml`의 command를 수정할 수 있습니다:

```yaml
command: >
  sh -c "alembic upgrade head && 
         uvicorn app.main:create_app 
         --factory --host 0.0.0.0 --port 8000 
         --log-level info"
```

**주의**: 프로덕션 환경에서는 자동 마이그레이션보다는 수동 실행을 권장합니다.

## 마이그레이션 확인

```bash
# 현재 마이그레이션 버전 확인
docker compose exec api alembic current

# 마이그레이션 히스토리 확인
docker compose exec api alembic history
```

## 롤백

```bash
# 이전 버전으로 롤백
docker compose exec api alembic downgrade -1

# 특정 버전으로 롤백
docker compose exec api alembic downgrade <revision_id>
```

