-- ============================================
-- 테이블 존재 여부 확인 및 생성 스크립트
-- ============================================
-- 
-- 이 스크립트는:
-- 1. 현재 데이터베이스의 테이블 존재 여부를 확인합니다
-- 2. 테이블이 없으면 생성합니다
-- 3. 스키마 정보를 확인합니다
--
-- 사용법:
-- psql -h localhost -p 15432 -U svc_dev -d iot_care -f check_and_create_tables.sql
-- 또는
-- psql에서 직접 실행: \i check_and_create_tables.sql
--
-- ============================================

-- 현재 데이터베이스 및 스키마 확인
SELECT 
    current_database() AS database_name,
    current_schema() AS current_schema;

-- ============================================
-- 1. 테이블 존재 여부 확인
-- ============================================

-- 1.1. public 스키마의 모든 테이블 확인
SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- 1.2. LLM Gateway 관련 테이블 존재 여부 확인
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

-- 1.3. 모든 스키마에서 테이블 검색
SELECT 
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
ORDER BY table_schema, table_name;

-- ============================================
-- 2. 테이블 생성 (테이블이 없을 경우에만)
-- ============================================

-- 2.1. 대화 세션 테이블 생성
CREATE TABLE IF NOT EXISTS conversation_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255),
    system_prompt TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_user_created ON conversation_sessions(user_id, created_at);

-- 2.2. 대화 메시지 테이블 생성
CREATE TABLE IF NOT EXISTS conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_session_created ON conversation_messages(session_id, created_at);

-- 2.3. API 요청 로그 테이블 생성
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

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_session_created ON api_request_logs(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_endpoint_created ON api_request_logs(endpoint, created_at);

-- 2.4. 비용 로그 테이블 생성
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

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_session_created ON cost_logs(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_service_created ON cost_logs(service_type, created_at);

-- ============================================
-- 3. 생성 후 확인
-- ============================================

-- 3.1. 테이블 구조 확인
SELECT 
    table_name,
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_schema = 'public'
    AND table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
ORDER BY table_name, ordinal_position;

-- 3.2. 인덱스 확인
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
ORDER BY tablename, indexname;

-- 3.3. 테이블별 데이터 수 확인
SELECT 
    'conversation_sessions' AS table_name,
    COUNT(*) AS row_count
FROM conversation_sessions
UNION ALL
SELECT 
    'conversation_messages' AS table_name,
    COUNT(*) AS row_count
FROM conversation_messages
UNION ALL
SELECT 
    'api_request_logs' AS table_name,
    COUNT(*) AS row_count
FROM api_request_logs
UNION ALL
SELECT 
    'cost_logs' AS table_name,
    COUNT(*) AS row_count
FROM cost_logs;

-- ============================================
-- 4. 테이블 삭제 (필요시 주석 해제)
-- ============================================

-- 주의: 이 명령은 모든 데이터를 삭제합니다!
-- DROP TABLE IF EXISTS cost_logs CASCADE;
-- DROP TABLE IF EXISTS api_request_logs CASCADE;
-- DROP TABLE IF EXISTS conversation_messages CASCADE;
-- DROP TABLE IF EXISTS conversation_sessions CASCADE;

-- ============================================
-- 5. 스키마 권한 확인
-- ============================================

-- 현재 사용자 권한 확인
SELECT 
    grantee,
    privilege_type
FROM information_schema.role_table_grants
WHERE table_schema = 'public'
    AND table_name IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
    AND grantee = current_user;

