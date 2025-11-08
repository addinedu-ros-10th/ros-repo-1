# 데이터베이스 초기화 개선 리포트

**작성일**: 2025-11-05  
**목적**: 프레임워크에서 DB 테이블을 자동으로 관리하도록 개선

---

## 🔧 개선 내용

### 문제점
- 서버 시작 시 테이블 생성이 실패해도 조용히 무시됨
- 테이블 존재 여부 검증 없음
- 수동으로 테이블을 생성해야 하는 상황 발생

### 개선 사항

#### 1. 테이블 생성 후 검증 추가 ✅

**변경 전**:
```python
def create_tables(self):
    Base.metadata.create_all(bind=self.engine, checkfirst=True)
    logger.info("Database tables created/verified successfully")
```

**변경 후**:
```python
def create_tables(self):
    # 생성 전 테이블 목록 확인
    existing_tables_before = set(inspector.get_table_names())
    
    # 테이블 생성
    Base.metadata.create_all(bind=self.engine, checkfirst=True)
    
    # 생성 후 검증
    existing_tables_after = set(inspector.get_table_names())
    required_tables = {'conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs'}
    missing_tables = required_tables - existing_tables_after
    
    # 누락된 테이블이 있으면 개별 생성 시도
    if missing_tables:
        self._create_missing_tables(missing_tables)
    
    # 최종 검증
    return all_tables_exist
```

#### 2. 누락된 테이블 자동 생성 ✅

**새로 추가된 메서드**: `_create_missing_tables()`

- SQLAlchemy의 `create_all()`이 실패할 경우
- 개별 테이블을 SQL로 직접 생성 시도
- 각 테이블에 대해 `CREATE TABLE IF NOT EXISTS` 실행

#### 3. 명확한 로그 및 출력 ✅

**개선 사항**:
- `print()` 문 추가로 콘솔에 즉시 표시
- 각 단계별 성공/실패 메시지 출력
- 테이블별 생성 상태 표시

**출력 예시**:
```
✓ Created new tables: conversation_sessions, conversation_messages
✓ Database tables verified: api_request_logs, cost_logs, conversation_messages, conversation_sessions
```

또는

```
✗ Failed to create required tables: conversation_sessions
✓ Created table: conversation_sessions
✓ Database tables verified: api_request_logs, cost_logs, conversation_messages, conversation_sessions
```

#### 4. Health Check 엔드포인트 개선 ✅

**추가된 기능**: `verify_tables()` 메서드

- 각 테이블의 존재 여부 확인
- 테이블별 데이터 수 확인
- Health Check API에서 상세 정보 제공

**Health Check 응답 예시**:
```json
{
  "services": {
    "database": {
      "connected": true,
      "initialized": true,
      "tables": {
        "conversation_sessions": {
          "exists": true,
          "row_count": 10
        },
        "conversation_messages": {
          "exists": true,
          "row_count": 45
        },
        "api_request_logs": {
          "exists": true,
          "row_count": 120
        },
        "cost_logs": {
          "exists": true,
          "row_count": 30
        }
      },
      "all_tables_exist": true
    }
  }
}
```

#### 5. 에러 처리 강화 ✅

**개선 사항**:
- 예외 발생 시 상세한 스택 트레이스 로깅 (`exc_info=True`)
- 실패 시에도 서버는 계속 실행 (graceful degradation)
- 명확한 에러 메시지 출력

---

## 📋 변경된 파일

### `src/database.py`

1. **`create_tables()` 메서드 개선**
   - 테이블 생성 전/후 검증 로직 추가
   - 반환값 추가 (`bool`: 성공/실패)
   - 누락된 테이블 자동 생성 호출

2. **`_create_missing_tables()` 메서드 추가**
   - 누락된 테이블을 SQL로 직접 생성
   - 각 테이블에 대한 개별 SQL 스크립트 포함
   - 인덱스도 함께 생성

3. **`health_check()` 메서드 개선**
   - 테이블 존재 여부 확인 추가
   - 필수 테이블이 모두 있는지 검증

4. **`verify_tables()` 메서드 추가**
   - 테이블 존재 여부 상세 확인
   - 테이블별 데이터 수 조회
   - Health Check API에서 사용

### `src/main.py`

1. **`startup_event()` 개선**
   - `create_tables()` 반환값 확인
   - 성공/실패에 따른 명확한 메시지 출력
   - 예외 처리 강화

2. **`root()` Health Check 엔드포인트 개선**
   - `verify_tables()` 호출하여 상세 정보 제공
   - 테이블별 상태 정보 포함

---

## 🚀 동작 방식

### 서버 시작 시

1. **데이터베이스 연결**
   ```python
   db_manager.initialize()
   ```

2. **테이블 생성 시도**
   ```python
   tables_created = db_manager.create_tables()
   ```

3. **테이블 생성 프로세스**
   - SQLAlchemy `create_all()` 시도
   - 생성 후 테이블 존재 여부 검증
   - 누락된 테이블이 있으면 `_create_missing_tables()` 호출
   - SQL로 직접 생성 시도
   - 최종 검증

4. **결과 출력**
   - 성공: `✓ Database connected and all tables verified`
   - 실패: `⚠ Database connected but table creation had issues (check logs)`

### Health Check API

`GET /` 엔드포인트에서:
- 데이터베이스 연결 상태
- 각 테이블의 존재 여부
- 테이블별 데이터 수
- 전체 테이블 존재 여부

---

## ✅ 검증 방법

### 1. 서버 로그 확인

```bash
docker compose logs llm-gateway | grep -i "database\|table"
```

**성공 메시지**:
```
✓ Database connected and all tables verified
✓ Database tables verified: api_request_logs, cost_logs, conversation_messages, conversation_sessions
```

### 2. Health Check API 확인

```bash
curl http://localhost:8000/ | jq '.services.database'
```

**예상 응답**:
```json
{
  "connected": true,
  "initialized": true,
  "tables": {
    "conversation_sessions": {"exists": true, "row_count": 0},
    "conversation_messages": {"exists": true, "row_count": 0},
    "api_request_logs": {"exists": true, "row_count": 0},
    "cost_logs": {"exists": true, "row_count": 0}
  },
  "all_tables_exist": true
}
```

### 3. 직접 쿼리 확인

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs');
```

---

## 🔄 Fallback 메커니즘

### 다단계 Fallback

1. **1차 시도**: SQLAlchemy `create_all()`
   - ORM 기반 테이블 생성
   - 가장 표준적인 방법

2. **2차 시도**: SQL 직접 실행
   - `_create_missing_tables()` 메서드
   - 개별 테이블을 SQL로 생성
   - `CREATE TABLE IF NOT EXISTS` 사용

3. **3차 Fallback**: 서버 계속 실행
   - 테이블 생성 실패해도 서버는 계속 실행
   - DB 기능만 사용 불가
   - 다른 기능(Redis, API)은 정상 작동

---

## 📝 사용자 가이드

### 정상 동작 시

서버 시작 시 자동으로:
1. 데이터베이스 연결
2. 테이블 생성/검증
3. 성공 메시지 출력

**추가 작업 불필요** ✅

### 문제 발생 시

1. **로그 확인**
   ```bash
   docker compose logs llm-gateway
   ```

2. **Health Check 확인**
   ```bash
   curl http://localhost:8000/
   ```

3. **수동 생성 (최후의 수단)**
   ```bash
   psql -h localhost -p 15432 -U svc_dev -d iot_care -f docs/check_and_create_tables.sql
   ```

---

## 🎯 개선 효과

### Before
- ❌ 테이블 생성 실패 시 조용히 무시
- ❌ 수동으로 테이블 생성 필요
- ❌ 테이블 존재 여부 확인 불가

### After
- ✅ 테이블 생성 후 자동 검증
- ✅ 누락된 테이블 자동 생성 시도
- ✅ 명확한 로그 및 콘솔 출력
- ✅ Health Check에서 테이블 상태 확인
- ✅ 다단계 Fallback 메커니즘

---

## 📚 참고

- **데이터베이스 스키마**: `docs/database_schema.md`
- **DB 사용 현황**: `docs/DB_USAGE_REPORT.md`
- **테이블 생성 스크립트**: `docs/check_and_create_tables.sql`
- **테이블 생성 진단**: `docs/TABLE_CREATION_REPORT.md`

---

**리포트 작성자**: AI Assistant  
**최종 업데이트**: 2025-11-05

