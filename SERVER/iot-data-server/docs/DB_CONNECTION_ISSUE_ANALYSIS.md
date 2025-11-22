# 데이터베이스 연결 및 테이블 생성 문제 분석 리포트

**작성일**: 2024년  
**문제**: `[Errno 113] No route to host` 및 `relation "residents" does not exist`

---

## 🔍 문제 진단 결과

### 1. 데이터베이스 연결 오류 (`[Errno 113] No route to host`)

**현재 상태:**
- `.env.local` 파일의 `DB_HOST=192.168.0.8`
- Docker 컨테이너 내부에서도 동일한 값 사용
- 로컬에서도 연결 실패: `Connection refused`

**원인 분석:**
1. **DB_HOST 주소 문제**: `192.168.0.8`이 Docker 컨테이너에서 접근 불가능한 주소일 수 있음
2. **네트워크 라우팅 문제**: Docker 컨테이너에서 호스트 머신의 IP로 접근할 때 라우팅 실패
3. **PostgreSQL 서버 상태**: PostgreSQL 서버가 실행되지 않았거나 해당 IP에서 수신하지 않음

**해결 방법:**
- Docker 컨테이너에서 호스트 머신에 접근하려면:
  - `host.docker.internal` 사용 (Linux에서는 `extra_hosts` 설정 필요)
  - 호스트 머신의 실제 IP 주소 사용 (Docker 브리지 네트워크에서 접근 가능한 주소)
  - Docker 네트워크 모드 조정

---

### 2. 테이블 생성 문제 (`relation "residents" does not exist`)

**현재 상태:**
- `app/main.py`의 `lifespan` 함수에서 `create_tables()` 호출
- `create_tables()`는 `Base.metadata.create_all(bind=engine)` 실행
- `ResidentInfo` 모델이 `Base`를 상속받고 있음

**원인 분석:**
1. **모델 임포트 누락**: `create_tables()` 실행 시 `ResidentInfo` 모델이 임포트되지 않았을 수 있음
2. **연결 실패로 인한 테이블 생성 실패**: DB 연결이 실패하면 테이블 생성도 실패
3. **비동기 엔진 문제**: 비동기 엔진을 사용하는데 동기 엔진으로 테이블 생성 시도

**해결 방법:**
- `app/main.py`에서 `ResidentInfo` 모델을 명시적으로 임포트
- DB 연결 성공 후 테이블 생성
- SQL 파일을 직접 실행하여 테이블 생성

---

## 📋 해결 계획

### 단계 1: DB_HOST 환경변수 수정

**목표**: Docker 컨테이너에서 호스트 머신의 PostgreSQL에 접근 가능하도록 설정

**방법 1: `host.docker.internal` 사용 (권장)**
```yaml
# docker-compose.yml
services:
  app:
    extra_hosts:
      - "host.docker.internal:host-gateway"
```

그리고 `.env.local`에서:
```
DB_HOST=host.docker.internal
```

**방법 2: 호스트 머신의 실제 IP 사용**
- 호스트 머신의 IP 주소 확인
- Docker 브리지 네트워크에서 접근 가능한 IP 사용
- `.env.local`의 `DB_HOST` 업데이트

**방법 3: Docker 네트워크 모드 변경**
```yaml
# docker-compose.yml
services:
  app:
    network_mode: "host"  # 호스트 네트워크 모드 사용
```

---

### 단계 2: 테이블 생성 수정

**목표**: `residents` 테이블이 확실히 생성되도록 수정

**방법 1: 모델 명시적 임포트**
```python
# app/main.py
from app.infrastructure.models import ResidentInfo  # 명시적 임포트 추가
```

**방법 2: SQL 파일 직접 실행**
- `create_residents_table.sql` 파일을 직접 실행
- 애플리케이션 시작 시 SQL 파일 실행 스크립트 추가

**방법 3: Alembic 마이그레이션 사용**
- Alembic을 사용하여 테이블 생성
- 마이그레이션 파일 생성 및 실행

---

## 🛠️ 권장 해결 순서

1. **DB 연결 문제 해결** (우선순위 1)
   - Docker 컨테이너에서 호스트 머신 접근 방법 확인
   - `DB_HOST` 환경변수 수정
   - 연결 테스트

2. **테이블 생성 문제 해결** (우선순위 2)
   - 모델 명시적 임포트 추가
   - SQL 파일 직접 실행 옵션 제공
   - 테이블 생성 확인

3. **검증**
   - DB 연결 성공 확인
   - `residents` 테이블 존재 확인
   - API 엔드포인트 테스트

---

## 📝 다음 단계

사용자 피드백 요청:
1. PostgreSQL 서버가 어디에 실행 중인가요? (로컬 호스트? 원격 서버?)
2. Docker 컨테이너에서 호스트 머신에 접근하는 방법을 선호하시나요?
   - `host.docker.internal` 사용
   - 호스트 IP 직접 사용
   - 네트워크 모드 변경
3. 테이블 생성 방법을 선호하시나요?
   - ORM 자동 생성 (모델 임포트)
   - SQL 파일 직접 실행
   - Alembic 마이그레이션

