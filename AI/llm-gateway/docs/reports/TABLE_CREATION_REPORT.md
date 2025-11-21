# 테이블 생성 문제 진단 리포트

**작성일**: 2025-11-05  
**문제**: `relation "conversation_sessions" does not exist` 에러

---

## 🔍 문제 분석

### 에러 메시지
```
[42P01] ERROR: relation "conversation_sessions" does not exist
```

### 확인된 사항
1. **DB 연결 정보**: 
   - 데이터베이스: `iot_care`
   - 사용자: `svc_dev`
   - 호스트: `localhost:15432`

2. **시도한 데이터베이스**:
   - `postgres.public` - 실패
   - `iot_care.public` - 실패

3. **서버 상태**: 
   - Docker compose 기반 서버 기동 시 DB 연결은 정상적으로 이루어짐

---

## 🤔 가능한 원인

### 1. 테이블이 생성되지 않았을 가능성 ⚠️

**가능성**: 높음

**원인 추정**:
- 서버 시작 시 테이블 생성이 실패했지만 에러가 조용히 무시되었을 수 있음
- `create_tables()` 메서드의 예외 처리가 너무 관대함
- 로그 레벨이 낮아서 에러 메시지가 출력되지 않았을 수 있음

**코드 확인**:
```python
# src/database.py:276-295
def create_tables(self):
    try:
        Base.metadata.create_all(bind=self.engine, checkfirst=True)
        logger.info("Database tables created/verified successfully")
    except (OperationalError, ProgrammingError) as e:
        error_str = str(e).lower()
        if 'already exists' in error_str or 'duplicate' in error_str:
            logger.info("Tables/indices already exist, skipping creation")
        else:
            logger.error(f"Failed to create tables: {e}")
            raise
```

**문제점**:
- `logger.info()`는 기본 로그 레벨에서 출력되지 않을 수 있음
- `print()` 문이 없어서 콘솔에 표시되지 않을 수 있음

### 2. 다른 스키마에 생성되었을 가능성

**가능성**: 낮음 (기본적으로 `public` 스키마 사용)

**확인 방법**: 아래 쿼리 실행
```sql
SELECT table_schema, table_name 
FROM information_schema.tables 
WHERE table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs');
```

### 3. 다른 데이터베이스에 생성되었을 가능성

**가능성**: 낮음 (서버는 `iot_care` DB에 연결)

---

## ✅ 해결 방법

### 방법 1: 테이블 존재 여부 확인 및 수동 생성 (권장)

**1단계: 테이블 존재 여부 확인**
```sql
-- 현재 데이터베이스 확인
SELECT current_database();

-- 테이블 존재 여부 확인
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'conversation_sessions') 
        THEN 'EXISTS' 
        ELSE 'NOT EXISTS' 
    END AS conversation_sessions,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'conversation_messages') 
        THEN 'EXISTS' 
        ELSE 'NOT EXISTS' 
    END AS conversation_messages,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'api_request_logs') 
        THEN 'EXISTS' 
        ELSE 'NOT EXISTS' 
    END AS api_request_logs,
    CASE 
        WHEN EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'cost_logs') 
        THEN 'EXISTS' 
        ELSE 'NOT EXISTS' 
    END AS cost_logs;
```

**2단계: 테이블 수동 생성**
`docs/check_and_create_tables.sql` 파일을 실행하세요:

```bash
# PostgreSQL 클라이언트로 연결
psql -h localhost -p 15432 -U svc_dev -d iot_care

# 스크립트 실행
\i docs/check_and_create_tables.sql
```

또는 직접 쿼리 실행:
```sql
-- 1. 대화 세션 테이블
CREATE TABLE IF NOT EXISTS conversation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    system_prompt TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_created ON conversation_sessions(user_id, created_at);

-- 2. 대화 메시지 테이블
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_session_created ON conversation_messages(session_id, created_at);

-- 3. API 요청 로그 테이블
CREATE TABLE IF NOT EXISTS api_request_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    request_data JSONB,
    response_data JSONB,
    status_code INTEGER NOT NULL,
    processing_time_ms FLOAT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_session_created ON api_request_logs(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_endpoint_created ON api_request_logs(endpoint, created_at);

-- 4. 비용 로그 테이블
CREATE TABLE IF NOT EXISTS cost_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    service_type VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_session_created ON cost_logs(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_service_created ON cost_logs(service_type, created_at);
```

### 방법 2: 서버 로그 확인

**Docker 컨테이너 로그 확인**:
```bash
cd AI/llm-gateway
docker compose logs llm-gateway | grep -i "database\|table\|create"
```

**확인할 메시지**:
- `✓ Database connected and tables created` - 성공
- `Database tables created/verified successfully` - 성공
- `⚠ Database initialization failed` - 실패
- `Failed to create tables` - 실패

### 방법 3: 코드 개선 (향후)

테이블 생성 실패 시 더 명확한 로그를 출력하도록 개선:

```python
def create_tables(self):
    """테이블 생성 (중복 테이블/인덱스 오류 무시)"""
    if not self.engine:
        logger.warning("Cannot create tables: database engine not initialized")
        print("⚠ Cannot create tables: database engine not initialized")
        return
    
    try:
        Base.metadata.create_all(bind=self.engine, checkfirst=True)
        logger.info("Database tables created/verified successfully")
        print("✓ Database tables created/verified successfully")
        
        # 테이블 생성 확인
        with self.get_session() as session:
            from sqlalchemy import inspect
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            print(f"✓ Existing tables: {', '.join(tables)}")
    except Exception as e:
        logger.error(f"Failed to create tables: {e}", exc_info=True)
        print(f"✗ Failed to create tables: {e}")
        raise
```

---

## 📋 확인 체크리스트

다음 명령어들을 순서대로 실행하여 상태를 확인하세요:

### 1. 데이터베이스 연결 확인
```sql
SELECT current_database(), current_user;
```

### 2. 테이블 존재 여부 확인
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs');
```

### 3. 서버 로그 확인
```bash
docker compose logs llm-gateway | grep -i "database\|table"
```

### 4. 테이블 생성 (없을 경우)
```bash
psql -h localhost -p 15432 -U svc_dev -d iot_care -f docs/check_and_create_tables.sql
```

### 5. 생성 후 확인
```sql
SELECT 
    'conversation_sessions' AS table_name,
    COUNT(*) AS row_count
FROM conversation_sessions;
```

---

## 🔧 권장 조치

1. **즉시 조치**: `docs/check_and_create_tables.sql` 파일을 실행하여 테이블 생성
2. **서버 로그 확인**: 테이블 생성 실패 원인 파악
3. **코드 개선**: 테이블 생성 실패 시 더 명확한 에러 메시지 출력

---

## 📝 참고 파일

- **테이블 생성 스크립트**: `docs/check_and_create_tables.sql`
- **데이터베이스 스키마**: `docs/database_schema.md`
- **DB 사용 현황**: `docs/DB_USAGE_REPORT.md`
- **데이터베이스 코드**: `src/database.py`

---

**리포트 작성자**: AI Assistant  
**최종 업데이트**: 2025-11-05

