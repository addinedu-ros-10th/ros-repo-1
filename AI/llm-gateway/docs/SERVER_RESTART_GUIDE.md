# 서버 재시작 가이드

## 서버 재시작 시 업데이트 적용 여부

### ✅ 자동 적용되는 것

1. **Python 코드 변경사항**
   - API 엔드포인트 추가/수정
   - 로직 변경
   - 함수 추가/수정

2. **데이터베이스 테이블 생성**
   - 테이블이 없으면 자동 생성
   - 새로 추가된 필드 포함하여 생성

3. **데이터베이스 마이그레이션 (자동)**
   - 기존 테이블에 누락된 컬럼 자동 추가
   - 인덱스 자동 생성
   - 서버 시작 시 자동 실행

### ❌ 수동 작업이 필요한 경우

자동 마이그레이션이 실패한 경우에만 수동 작업이 필요합니다:
- 데이터베이스 권한 부족
- 네트워크 연결 문제
- 데이터베이스 서버 다운

## 서버 재시작 방법

### Docker Compose 사용

```bash
cd AI/llm-gateway
docker compose restart llm-gateway
```

또는 전체 재시작:

```bash
cd AI/llm-gateway
docker compose down
docker compose up -d
```

### 로그 확인

```bash
# 실시간 로그 확인
docker compose logs -f llm-gateway

# 마이그레이션 성공 메시지 확인
docker compose logs llm-gateway | grep -i "migration\|column\|index"
```

### 예상 로그 메시지

**성공 시:**
```
✓ Database connected and all tables verified
Running migration for existing conversation_sessions table...
✅ Added 'name' column to conversation_sessions
✅ Added 'nickname' column to conversation_sessions
```

**이미 마이그레이션된 경우:**
```
Running migration for existing conversation_sessions table...
(컬럼이 이미 존재하므로 조용히 통과)
```

## 마이그레이션 확인

### 방법 1: API 테스트

```bash
# 세션 목록 조회 (정상 작동하면 마이그레이션 성공)
curl http://localhost:8001/api/sessions
```

### 방법 2: 데이터베이스 직접 확인

```sql
-- 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversation_sessions'
ORDER BY ordinal_position;

-- 인덱스 확인
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'conversation_sessions';
```

### 방법 3: 서버 로그 확인

```bash
docker compose logs llm-gateway | grep -E "migration|column|index|Database connected"
```

## 문제 해결

### 오류: "permission denied"

데이터베이스 사용자에게 ALTER TABLE 권한이 필요합니다:

```sql
GRANT ALL PRIVILEGES ON TABLE conversation_sessions TO your_db_user;
```

### 오류: "table does not exist"

테이블이 없으면 서버 시작 시 자동으로 생성됩니다. 서버를 재시작하세요.

### 마이그레이션이 실행되지 않는 경우

수동 마이그레이션 실행:

```bash
psql -U your_user -d your_database -f AI/llm-gateway/maintenance/database/add_session_name_nickname.sql
```

자세한 내용은 `docs/DB_MIGRATION_GUIDE.md`를 참고하세요.

## 요약

**대부분의 경우 서버 재시작만으로 충분합니다!**

1. 서버 재시작
2. 로그에서 마이그레이션 메시지 확인
3. API 테스트로 확인

수동 마이그레이션은 자동 마이그레이션이 실패한 경우에만 필요합니다.

