# 데이터베이스 연결 문제 해결 요약

## ✅ 적용된 수정 사항

### 1. `host.docker.internal` 설명 문서 작성
- **파일**: `docs/HOST_DOCKER_INTERNAL_EXPLANATION.md`
- **내용**: `host.docker.internal`의 의미와 동작 방식 설명
- **답변**: Docker를 실행하는 호스트 머신의 IP를 자동으로 가리킴 (컨테이너 IP 아님)

### 2. 환경변수 값 그대로 사용하도록 수정
- **파일**: `app/core/config.py`
- **변경 내용**:
  - `DATABASE_URL` 속성에서 복잡한 로직 제거
  - env 파일(`.env.local`)의 `DB_HOST` 값을 그대로 사용
  - 임의로 값을 변경하지 않음

### 3. 연결 실패 시 명확한 로그 메시지 추가
- **파일**: `app/infrastructure/database.py`
- **변경 내용**:
  - `get_db()` 함수: 연결 오류 시 env 파일 확인 메시지 출력
  - `get_db_session()` 함수: 연결 오류 시 env 파일 확인 메시지 출력
  - `test_connection()` 함수: 연결 테스트 실패 시 env 파일 확인 메시지 출력
  - `create_async_engine()` 호출 시 연결 실패 시 상세한 에러 메시지 출력

### 4. 테이블 생성 문제 해결
- **파일**: `app/main.py`
- **변경 내용**: `ResidentInfo` 모델을 명시적으로 임포트하여 테이블 생성 시 포함되도록 보장

---

## 📋 로그 메시지 예시

연결 실패 시 다음과 같은 로그가 출력됩니다:

```
================================================================================
❌ 데이터베이스 연결 오류 발생
   env 파일(.env.local)의 DB_HOST 값: 192.168.0.8
   env 파일(.env.local)의 DB_PORT 값: 15432

💡 env 파일의 HOST로 DB 연결이 불가능합니다.
   .env.local 파일을 확인하고 DB_HOST 값을 수정해주세요.

   상세 오류: [Errno 113] No route to host
================================================================================
```

---

## 🔧 사용자 설정 가이드

### 현재 상황
- PostgreSQL 서버: 로컬 호스트 머신 (원격 서버에 SSH 터널을 15432로 연결)
- DB_HOST 설정: 호스트 머신의 실제 IP 사용
- 서버 상태: 접속 가능

### 권장 설정

**`.env.local` 파일:**
```bash
DB_HOST=<호스트_머신의_실제_IP>
DB_PORT=15432
DB_NAME=iot_care
DB_USER=svc_dev
DB_PASSWORD=<비밀번호>
```

**예시:**
```bash
DB_HOST=192.168.0.10  # 호스트 머신의 실제 IP
DB_PORT=15432
DB_NAME=iot_care
DB_USER=svc_dev
DB_PASSWORD=IOT_dev_123!@#
```

---

## 🚀 다음 단계

1. **`.env.local` 파일의 `DB_HOST` 값을 호스트 머신의 실제 IP로 설정
2. **Docker 컨테이너 재시작**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
3. **로그 확인**:
   ```bash
   docker logs iot-care-app --tail 50
   ```
4. **테이블 생성 확인**:
   ```bash
   docker exec -it iot-care-app python3 scripts/check_db_status.py
   ```

---

## 📝 주요 변경 사항 요약

| 항목 | 변경 전 | 변경 후 |
|------|--------|---------|
| DB_HOST 처리 | 복잡한 로직으로 자동 변경 시도 | env 파일 값 그대로 사용 |
| 연결 실패 로그 | 간단한 에러 메시지 | 상세한 해결 방법 포함 |
| 테이블 생성 | 모델 임포트 누락 가능 | 명시적 임포트로 보장 |

---

## ✅ 검증 체크리스트

- [x] env 파일의 DB_HOST 값을 그대로 사용하도록 수정
- [x] 연결 실패 시 명확한 로그 메시지 추가
- [x] 임의로 연결 값을 설정하지 않도록 수정
- [x] 테이블 생성 문제 해결 (ResidentInfo 모델 명시적 임포트)
- [x] 중복 함수 제거
- [x] 린터 오류 없음 확인

