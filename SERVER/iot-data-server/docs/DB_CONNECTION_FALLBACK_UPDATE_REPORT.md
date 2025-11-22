# 데이터베이스 연결 Fallback 메커니즘 업데이트 리포트

**작성일**: 2024년  
**목적**: env 파일의 HOST 연결 실패 시 `host.docker.internal`로 자동 재시도

---

## 📋 업데이트 요약

### 변경 사항
1. **Fallback 메커니즘 추가**: env 파일의 DB_HOST로 연결 실패 시 `host.docker.internal`로 자동 재시도
2. **명확한 로그 메시지**: 각 단계별로 상세한 로그 메시지 출력
3. **지연 초기화**: 엔진을 필요할 때 생성하도록 변경

---

## 🔧 수정된 파일

### 1. `app/infrastructure/database.py`

#### 주요 변경 사항

**1. 전역 변수 초기화 변경**
```python
# 변경 전: 즉시 엔진 생성
engine = create_engine(DATABASE_URL, ...)

# 변경 후: 지연 초기화
engine = None
async_engine = None
SessionLocal = None
```

**2. `_create_engine_with_fallback()` 함수 추가**
- env 파일의 DB_HOST로 먼저 연결 시도
- 실패 시 에러 메시지 출력
- `host.docker.internal`로 재시도
- 각 단계별 상세한 로그 출력

**3. `get_db()` 함수 수정**
- `_create_engine_with_fallback()` 호출하여 엔진 생성
- 엔진이 없을 때만 생성 (재사용)

**4. `get_db_session()` 함수 수정**
- 비동기 엔진 생성 시 fallback 메커니즘 적용
- 연결 테스트 추가

**5. `create_tables()` 함수 수정**
- 엔진 생성 시 fallback 메커니즘 사용

**6. `test_connection()` 함수 수정**
- fallback 메커니즘 사용

---

## 📝 로그 메시지 흐름

### 시나리오 1: env 파일의 HOST로 연결 성공

```
🔌 데이터베이스 연결 시도: 192.168.0.8:15432
✅ 데이터베이스 연결 성공: 192.168.0.8:15432
```

### 시나리오 2: env 파일의 HOST로 연결 실패 → host.docker.internal로 재시도 성공

```
🔌 데이터베이스 연결 시도: 192.168.0.8:15432
================================================================================
❌ 데이터베이스 연결 실패
   env 파일(.env.local)의 DB_HOST 값: 192.168.0.8
   env 파일(.env.local)의 DB_PORT 값: 15432

💡 env 파일의 HOST로 DB 연결이 불가능합니다.
   .env.local 파일을 확인하고 DB_HOST 값을 수정해주세요.

   상세 오류: [Errno 113] No route to host
================================================================================

================================================================================
🔄 일단은 host.docker.internal에 접근을 시도합니다...
================================================================================
✅ host.docker.internal로 데이터베이스 연결 성공!
================================================================================
```

### 시나리오 3: 두 방법 모두 실패

```
🔌 데이터베이스 연결 시도: 192.168.0.8:15432
================================================================================
❌ 데이터베이스 연결 실패
   env 파일(.env.local)의 DB_HOST 값: 192.168.0.8
   env 파일(.env.local)의 DB_PORT 값: 15432

💡 env 파일의 HOST로 DB 연결이 불가능합니다.
   .env.local 파일을 확인하고 DB_HOST 값을 수정해주세요.

   상세 오류: [Errno 113] No route to host
================================================================================

================================================================================
🔄 일단은 host.docker.internal에 접근을 시도합니다...
================================================================================
================================================================================
❌ host.docker.internal로도 데이터베이스 연결 실패

💡 해결 방법:
   1. .env.local 파일의 DB_HOST 값을 확인하세요.
   2. PostgreSQL 서버가 실행 중인지 확인하세요.
   3. 방화벽 설정을 확인하세요.
   4. docker-compose.yml에 extra_hosts 설정이 있는지 확인하세요.

   원본 오류 (env HOST): [Errno 113] No route to host
   Fallback 오류 (host.docker.internal): [Errno 111] Connection refused
================================================================================
```

---

## 🔄 동작 흐름

```
시작
  ↓
env 파일의 DB_HOST로 연결 시도
  ↓
성공? ──Yes──> ✅ 연결 성공
  ↓ No
에러 메시지 출력
  ↓
"일단은 host.docker.internal에 접근을 시도합니다" 메시지 출력
  ↓
host.docker.internal로 재시도
  ↓
성공? ──Yes──> ✅ Fallback 연결 성공
  ↓ No
에러 메시지 출력
  ↓
❌ 연결 실패 (예외 발생)
```

---

## ✅ 주요 특징

1. **명확한 에러 메시지**: env 파일의 HOST로 연결 실패 시 상세한 안내 메시지
2. **자동 Fallback**: 사용자 개입 없이 `host.docker.internal`로 자동 재시도
3. **상세한 로그**: 각 단계별로 무엇을 시도하고 있는지 명확히 표시
4. **지연 초기화**: 엔진을 필요할 때만 생성하여 불필요한 연결 시도 방지

---

## 🧪 테스트 시나리오

### 테스트 1: 정상 연결
- `.env.local`의 `DB_HOST`가 올바른 주소
- 예상 결과: 첫 시도에서 연결 성공

### 테스트 2: env HOST 실패, Fallback 성공
- `.env.local`의 `DB_HOST`가 접근 불가능한 주소
- `host.docker.internal`로는 접근 가능
- 예상 결과: 첫 시도 실패 → Fallback 성공

### 테스트 3: 모두 실패
- `.env.local`의 `DB_HOST`와 `host.docker.internal` 모두 접근 불가능
- 예상 결과: 두 시도 모두 실패, 상세한 에러 메시지 출력

---

## 📝 코드 변경 상세

### 추가된 함수

**`_create_engine_with_fallback()`**
- 동기 엔진 생성 및 fallback 처리
- 전역 `engine`과 `SessionLocal` 초기화

### 수정된 함수

**`get_db()`**
- `_create_engine_with_fallback()` 호출
- 엔진이 없을 때만 생성

**`get_db_session()`**
- 비동기 엔진 생성 시 fallback 메커니즘 적용
- 연결 테스트 추가

**`create_tables()`**
- `_create_engine_with_fallback()` 호출

**`test_connection()`**
- `_create_engine_with_fallback()` 사용

---

## 🚀 사용 방법

### 1. 기본 사용 (변경 없음)
```python
# 기존과 동일하게 사용
from app.infrastructure.database import get_db, get_db_session

# FastAPI 의존성으로 사용
@app.get("/")
async def endpoint(db: Session = Depends(get_db)):
    ...
```

### 2. 자동 Fallback 동작
- env 파일의 DB_HOST로 연결 실패 시 자동으로 `host.docker.internal`로 재시도
- 사용자 개입 불필요

---

## ⚠️ 주의 사항

1. **엔진 재사용**: 엔진은 한 번 생성되면 재사용됩니다.
2. **Fallback은 연결 오류에만 적용**: 인증 오류 등은 fallback하지 않습니다.
3. **로그 출력**: 연결 실패 시 상세한 로그가 출력됩니다.

---

## 📊 성능 영향

- **초기 연결**: 약간의 지연 (두 번 시도)
- **이후 연결**: 기존과 동일 (엔진 재사용)
- **메모리**: 엔진은 한 번만 생성되므로 메모리 사용량 동일

---

## 🔍 디버깅

### 로그 확인
```bash
docker logs iot-care-app --tail 100 | grep -E "데이터베이스|DB|연결"
```

### 연결 상태 확인
```bash
docker exec -it iot-care-app python3 scripts/check_db_status.py
```

---

## ✅ 검증 체크리스트

- [x] env 파일의 HOST로 먼저 연결 시도
- [x] 연결 실패 시 명확한 에러 메시지 출력
- [x] `host.docker.internal`로 자동 재시도
- [x] 재시도 시도 메시지 출력
- [x] 두 방법 모두 실패 시 상세한 에러 메시지
- [x] 동기/비동기 모두 fallback 메커니즘 적용
- [x] 엔진 지연 초기화 구현
- [x] 린터 오류 없음 확인

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

