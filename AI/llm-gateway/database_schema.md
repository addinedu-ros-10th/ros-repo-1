# 데이터베이스 스키마 설계

이 문서는 LLM Gateway 서버에서 사용하는 데이터베이스 스키마를 설명합니다.

## 개요

외부 PostgreSQL 데이터베이스를 사용하여 다음과 같은 정보를 영구 저장합니다:
- 대화 세션 및 메시지 히스토리
- API 요청 로그
- 비용 추적 (OpenAI API 사용 비용)

## 데이터베이스 설정

### 필수 환경변수

```env
# 방법 1: URL 사용
DB_URL=postgresql://user:password@host:5432/dbname

# 방법 2: 개별 설정
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=llm_gateway
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

## 테이블 스키마

### 1. conversation_sessions (대화 세션)

대화 세션의 메타데이터를 저장합니다.

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| session_id | VARCHAR(255) | PRIMARY KEY | 세션 고유 ID |
| user_id | VARCHAR(255) | NULL, INDEX | 사용자 ID (향후 확장용) |
| system_prompt | TEXT | NULL | 시스템 프롬프트 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정 시간 |

**인덱스:**
- `idx_user_created` (user_id, created_at)

**SQL 생성 예시:**
```sql
CREATE TABLE conversation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    system_prompt TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_created ON conversation_sessions(user_id, created_at);
```

### 2. conversation_messages (대화 메시지)

각 세션의 대화 메시지를 저장합니다.

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | 메시지 고유 ID |
| session_id | VARCHAR(255) | NOT NULL, INDEX, FK | 세션 ID (conversation_sessions 참조) |
| role | VARCHAR(50) | NOT NULL | 메시지 역할 (system, user, assistant) |
| content | TEXT | NOT NULL | 메시지 내용 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |

**인덱스:**
- `idx_session_created` (session_id, created_at)

**SQL 생성 예시:**
```sql
CREATE TABLE conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_created ON conversation_messages(session_id, created_at);
```

### 3. api_request_logs (API 요청 로그)

모든 API 요청을 로깅합니다.

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | 로그 고유 ID |
| session_id | VARCHAR(255) | NULL, INDEX | 세션 ID |
| endpoint | VARCHAR(255) | NOT NULL | API 엔드포인트 |
| method | VARCHAR(10) | NOT NULL | HTTP 메서드 |
| request_data | JSONB | NULL | 요청 데이터 (일부만 저장) |
| response_data | JSONB | NULL | 응답 데이터 (요약 정보) |
| status_code | INTEGER | NOT NULL | HTTP 상태 코드 |
| processing_time_ms | FLOAT | NULL | 처리 시간 (밀리초) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |

**인덱스:**
- `idx_session_created` (session_id, created_at)
- `idx_endpoint_created` (endpoint, created_at)

**SQL 생성 예시:**
```sql
CREATE TABLE api_request_logs (
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

CREATE INDEX idx_session_created ON api_request_logs(session_id, created_at);
CREATE INDEX idx_endpoint_created ON api_request_logs(endpoint, created_at);
```

### 4. cost_logs (비용 로그)

OpenAI API 사용 비용을 추적합니다.

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | 로그 고유 ID |
| session_id | VARCHAR(255) | NULL, INDEX | 세션 ID |
| service_type | VARCHAR(50) | NOT NULL | 서비스 타입 (stt, chat, tts) |
| model | VARCHAR(100) | NOT NULL | 사용된 모델 |
| input_tokens | INTEGER | NULL | 입력 토큰 수 |
| output_tokens | INTEGER | NULL | 출력 토큰 수 |
| cost_usd | FLOAT | NOT NULL | 비용 (USD) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |

**인덱스:**
- `idx_session_created` (session_id, created_at)
- `idx_service_created` (service_type, created_at)

**SQL 생성 예시:**
```sql
CREATE TABLE cost_logs (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255),
    service_type VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd FLOAT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_session_created ON cost_logs(session_id, created_at);
CREATE INDEX idx_service_created ON cost_logs(service_type, created_at);
```

## 전체 스키마 생성 스크립트

```sql
-- 대화 세션 테이블
CREATE TABLE IF NOT EXISTS conversation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    system_prompt TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_created ON conversation_sessions(user_id, created_at);

-- 대화 메시지 테이블
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_session_created ON conversation_messages(session_id, created_at);

-- API 요청 로그 테이블
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

-- 비용 로그 테이블
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

## 데이터베이스 관리

### 자동 테이블 생성

서버 시작 시 `database.py`의 `db_manager.create_tables()` 메서드가 자동으로 테이블을 생성합니다.

### 수동 테이블 생성

위의 SQL 스크립트를 직접 실행하거나, Alembic 같은 마이그레이션 도구를 사용할 수 있습니다.

## 데이터 관리 전략

### 1. 세션 히스토리 관리

- **Redis**: 빠른 읽기/쓰기를 위한 캐시 (30일 TTL)
- **PostgreSQL**: 영구 저장 및 백업

### 2. 로그 보관

- API 요청 로그는 모든 요청을 기록 (분석 및 디버깅용)
- 오래된 로그는 정기적으로 아카이빙 또는 삭제 가능

### 3. 비용 추적

- 각 OpenAI API 호출마다 토큰 사용량과 비용 기록
- 일별/월별 비용 집계 쿼리 예시:

```sql
-- 일별 비용 집계
SELECT 
    DATE(created_at) as date,
    SUM(cost_usd) as total_cost,
    COUNT(*) as request_count
FROM cost_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 세션별 비용 집계
SELECT 
    session_id,
    SUM(cost_usd) as total_cost,
    COUNT(*) as request_count
FROM cost_logs
GROUP BY session_id
ORDER BY total_cost DESC
LIMIT 10;
```

## 확장 고려사항

### 향후 추가 가능한 테이블

1. **users**: 사용자 관리
2. **api_keys**: API 키 관리
3. **rate_limits**: 사용량 제한 관리
4. **audit_logs**: 감사 로그

### 성능 최적화

- 파티셔닝: 날짜별 파티셔닝 (대용량 로그 테이블)
- 아카이빙: 오래된 데이터는 별도 아카이빙 테이블로 이동
- 읽기 전용 복제본: 분석 쿼리용


