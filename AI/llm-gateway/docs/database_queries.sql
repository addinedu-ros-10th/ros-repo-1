-- ============================================
-- LLM Gateway PostgreSQL 데이터베이스 쿼리 모음
-- ============================================
-- 
-- 이 파일에는 영구 DB에서 테이블을 조회하기 위한 
-- 유용한 SQL 쿼리들이 포함되어 있습니다.
--
-- 사용법:
-- 1. PostgreSQL 클라이언트에 연결
-- 2. 필요한 쿼리를 복사하여 실행
-- 3. 결과를 확인
--
-- ============================================

-- ============================================
-- 1. 대화 세션 관련 쿼리
-- ============================================

-- 1.1. 모든 대화 세션 조회
SELECT 
    session_id,
    user_id,
    system_prompt,
    created_at,
    updated_at
FROM conversation_sessions
ORDER BY updated_at DESC;

-- 1.2. 최근 활성 세션 조회 (최근 24시간 내 업데이트)
SELECT 
    session_id,
    user_id,
    system_prompt,
    created_at,
    updated_at,
    EXTRACT(EPOCH FROM (NOW() - updated_at)) / 3600 AS hours_since_update
FROM conversation_sessions
WHERE updated_at >= NOW() - INTERVAL '24 hours'
ORDER BY updated_at DESC;

-- 1.3. 특정 세션의 메타데이터 조회
SELECT 
    session_id,
    user_id,
    system_prompt,
    created_at,
    updated_at
FROM conversation_sessions
WHERE session_id = 'your_session_id_here';

-- 1.4. 사용자별 세션 수 집계
SELECT 
    user_id,
    COUNT(*) AS session_count,
    MIN(created_at) AS first_session,
    MAX(updated_at) AS last_activity
FROM conversation_sessions
WHERE user_id IS NOT NULL
GROUP BY user_id
ORDER BY session_count DESC;

-- ============================================
-- 2. 대화 메시지 관련 쿼리
-- ============================================

-- 2.1. 특정 세션의 모든 메시지 조회
SELECT 
    id,
    session_id,
    role,
    content,
    created_at
FROM conversation_messages
WHERE session_id = 'your_session_id_here'
ORDER BY created_at ASC;

-- 2.2. 세션별 메시지 수 집계
SELECT 
    cm.session_id,
    COUNT(*) AS message_count,
    COUNT(CASE WHEN role = 'user' THEN 1 END) AS user_messages,
    COUNT(CASE WHEN role = 'assistant' THEN 1 END) AS assistant_messages,
    COUNT(CASE WHEN role = 'system' THEN 1 END) AS system_messages,
    MIN(cm.created_at) AS first_message,
    MAX(cm.created_at) AS last_message
FROM conversation_messages cm
GROUP BY cm.session_id
ORDER BY message_count DESC
LIMIT 20;

-- 2.3. 최근 메시지 조회 (최근 100개)
SELECT 
    cm.id,
    cm.session_id,
    cm.role,
    LEFT(cm.content, 100) AS content_preview,  -- 처음 100자만 표시
    cm.created_at
FROM conversation_messages cm
ORDER BY cm.created_at DESC
LIMIT 100;

-- 2.4. 특정 세션의 대화 히스토리 (시스템 프롬프트 포함)
SELECT 
    cm.role,
    cm.content,
    cm.created_at
FROM conversation_messages cm
WHERE cm.session_id = 'your_session_id_here'
ORDER BY cm.created_at ASC;

-- 2.5. 세션과 메시지를 함께 조회 (JOIN)
SELECT 
    cs.session_id,
    cs.user_id,
    cs.system_prompt,
    COUNT(cm.id) AS message_count,
    MAX(cm.created_at) AS last_message_time,
    cs.updated_at AS session_updated
FROM conversation_sessions cs
LEFT JOIN conversation_messages cm ON cs.session_id = cm.session_id
GROUP BY cs.session_id, cs.user_id, cs.system_prompt, cs.updated_at
ORDER BY last_message_time DESC NULLS LAST
LIMIT 20;

-- ============================================
-- 3. API 요청 로그 관련 쿼리
-- ============================================

-- 3.1. 최근 API 요청 로그 조회
SELECT 
    id,
    session_id,
    endpoint,
    method,
    status_code,
    processing_time_ms,
    created_at
FROM api_request_logs
ORDER BY created_at DESC
LIMIT 100;

-- 3.2. 엔드포인트별 요청 통계
SELECT 
    endpoint,
    method,
    COUNT(*) AS request_count,
    COUNT(CASE WHEN status_code >= 200 AND status_code < 300 THEN 1 END) AS success_count,
    COUNT(CASE WHEN status_code >= 400 THEN 1 END) AS error_count,
    AVG(processing_time_ms) AS avg_processing_time_ms,
    MIN(processing_time_ms) AS min_processing_time_ms,
    MAX(processing_time_ms) AS max_processing_time_ms
FROM api_request_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY endpoint, method
ORDER BY request_count DESC;

-- 3.3. 에러 로그 조회 (4xx, 5xx)
SELECT 
    id,
    session_id,
    endpoint,
    method,
    status_code,
    request_data,
    response_data,
    processing_time_ms,
    created_at
FROM api_request_logs
WHERE status_code >= 400
ORDER BY created_at DESC
LIMIT 50;

-- 3.4. 특정 세션의 API 요청 이력
SELECT 
    id,
    endpoint,
    method,
    status_code,
    processing_time_ms,
    created_at
FROM api_request_logs
WHERE session_id = 'your_session_id_here'
ORDER BY created_at DESC;

-- 3.5. 느린 요청 조회 (처리 시간이 긴 요청)
SELECT 
    id,
    session_id,
    endpoint,
    method,
    status_code,
    processing_time_ms,
    created_at
FROM api_request_logs
WHERE processing_time_ms > 1000  -- 1초 이상
ORDER BY processing_time_ms DESC
LIMIT 50;

-- 3.6. 시간대별 요청 통계 (시간별)
SELECT 
    DATE_TRUNC('hour', created_at) AS hour,
    COUNT(*) AS request_count,
    AVG(processing_time_ms) AS avg_processing_time_ms,
    COUNT(CASE WHEN status_code >= 400 THEN 1 END) AS error_count
FROM api_request_logs
WHERE created_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', created_at)
ORDER BY hour DESC;

-- ============================================
-- 4. 비용 로그 관련 쿼리
-- ============================================

-- 4.1. 최근 비용 로그 조회
SELECT 
    id,
    session_id,
    service_type,
    model,
    input_tokens,
    output_tokens,
    cost_usd,
    created_at
FROM cost_logs
ORDER BY created_at DESC
LIMIT 100;

-- 4.2. 일별 비용 집계
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS request_count,
    SUM(cost_usd) AS total_cost_usd,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens,
    AVG(cost_usd) AS avg_cost_usd
FROM cost_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 4.3. 서비스 타입별 비용 집계
SELECT 
    service_type,
    COUNT(*) AS request_count,
    SUM(cost_usd) AS total_cost_usd,
    AVG(cost_usd) AS avg_cost_usd,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens
FROM cost_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY service_type
ORDER BY total_cost_usd DESC;

-- 4.4. 모델별 비용 집계
SELECT 
    model,
    COUNT(*) AS request_count,
    SUM(cost_usd) AS total_cost_usd,
    AVG(cost_usd) AS avg_cost_usd,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens,
    AVG(input_tokens) AS avg_input_tokens,
    AVG(output_tokens) AS avg_output_tokens
FROM cost_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY model
ORDER BY total_cost_usd DESC;

-- 4.5. 세션별 비용 집계 (상위 20개)
SELECT 
    session_id,
    COUNT(*) AS request_count,
    SUM(cost_usd) AS total_cost_usd,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens
FROM cost_logs
GROUP BY session_id
ORDER BY total_cost_usd DESC
LIMIT 20;

-- 4.6. 월별 비용 집계
SELECT 
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS request_count,
    SUM(cost_usd) AS total_cost_usd,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens
FROM cost_logs
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;

-- 4.7. 서비스 타입 및 모델별 비용 상세
SELECT 
    service_type,
    model,
    COUNT(*) AS request_count,
    SUM(cost_usd) AS total_cost_usd,
    AVG(cost_usd) AS avg_cost_usd
FROM cost_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY service_type, model
ORDER BY total_cost_usd DESC;

-- ============================================
-- 5. 통합 분석 쿼리
-- ============================================

-- 5.1. 세션별 전체 통계 (세션, 메시지, 비용 통합)
SELECT 
    cs.session_id,
    cs.user_id,
    cs.created_at AS session_created,
    cs.updated_at AS session_updated,
    COUNT(DISTINCT cm.id) AS message_count,
    SUM(cl.cost_usd) AS total_cost_usd,
    COUNT(DISTINCT arl.id) AS api_request_count,
    MAX(cm.created_at) AS last_message_time
FROM conversation_sessions cs
LEFT JOIN conversation_messages cm ON cs.session_id = cm.session_id
LEFT JOIN cost_logs cl ON cs.session_id = cl.session_id
LEFT JOIN api_request_logs arl ON cs.session_id = arl.session_id
GROUP BY cs.session_id, cs.user_id, cs.created_at, cs.updated_at
ORDER BY session_updated DESC
LIMIT 20;

-- 5.2. 일별 종합 통계
SELECT 
    DATE(created_at) AS date,
    -- 세션 통계
    (SELECT COUNT(DISTINCT session_id) FROM conversation_sessions WHERE DATE(created_at) = DATE(cl.created_at)) AS new_sessions,
    -- 메시지 통계
    (SELECT COUNT(*) FROM conversation_messages WHERE DATE(created_at) = DATE(cl.created_at)) AS message_count,
    -- API 요청 통계
    (SELECT COUNT(*) FROM api_request_logs WHERE DATE(created_at) = DATE(cl.created_at)) AS api_request_count,
    -- 비용 통계
    COUNT(*) AS cost_log_count,
    SUM(cost_usd) AS total_cost_usd,
    SUM(input_tokens) AS total_input_tokens,
    SUM(output_tokens) AS total_output_tokens
FROM cost_logs cl
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- 5.3. 활성 세션 조회 (최근 24시간 내 활동)
SELECT 
    cs.session_id,
    cs.user_id,
    COUNT(cm.id) AS message_count,
    SUM(cl.cost_usd) AS total_cost,
    MAX(cm.created_at) AS last_message,
    MAX(arl.created_at) AS last_api_request
FROM conversation_sessions cs
LEFT JOIN conversation_messages cm ON cs.session_id = cm.session_id
LEFT JOIN cost_logs cl ON cs.session_id = cl.session_id
LEFT JOIN api_request_logs arl ON cs.session_id = arl.session_id
WHERE cs.updated_at >= NOW() - INTERVAL '24 hours'
GROUP BY cs.session_id, cs.user_id
HAVING COUNT(cm.id) > 0 OR COUNT(arl.id) > 0
ORDER BY last_message DESC NULLS LAST, last_api_request DESC NULLS LAST;

-- ============================================
-- 6. 데이터 정리 및 관리 쿼리
-- ============================================

-- 6.1. 오래된 세션 조회 (30일 이상 미사용)
SELECT 
    session_id,
    user_id,
    created_at,
    updated_at,
    EXTRACT(EPOCH FROM (NOW() - updated_at)) / 86400 AS days_inactive
FROM conversation_sessions
WHERE updated_at < NOW() - INTERVAL '30 days'
ORDER BY updated_at ASC;

-- 6.2. 테이블별 데이터 수 확인
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

-- 6.3. 테이블별 데이터 크기 확인 (PostgreSQL)
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
    AND tablename IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
ORDER BY size_bytes DESC;

-- 6.4. 인덱스 사용 현황 확인
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_indexes
WHERE schemaname = 'public'
    AND tablename IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs')
ORDER BY tablename, indexname;

-- ============================================
-- 7. 유용한 뷰 생성 (선택사항)
-- ============================================

-- 7.1. 세션 상세 뷰 생성
-- CREATE OR REPLACE VIEW v_session_details AS
-- SELECT 
--     cs.session_id,
--     cs.user_id,
--     cs.system_prompt,
--     cs.created_at AS session_created,
--     cs.updated_at AS session_updated,
--     COUNT(DISTINCT cm.id) AS message_count,
--     SUM(cl.cost_usd) AS total_cost_usd,
--     COUNT(DISTINCT arl.id) AS api_request_count,
--     MAX(cm.created_at) AS last_message_time
-- FROM conversation_sessions cs
-- LEFT JOIN conversation_messages cm ON cs.session_id = cm.session_id
-- LEFT JOIN cost_logs cl ON cs.session_id = cl.session_id
-- LEFT JOIN api_request_logs arl ON cs.session_id = arl.session_id
-- GROUP BY cs.session_id, cs.user_id, cs.system_prompt, cs.created_at, cs.updated_at;

-- 사용 예시:
-- SELECT * FROM v_session_details ORDER BY session_updated DESC LIMIT 20;

-- 7.2. 일별 통계 뷰 생성
-- CREATE OR REPLACE VIEW v_daily_stats AS
-- SELECT 
--     DATE(created_at) AS date,
--     COUNT(DISTINCT session_id) AS unique_sessions,
--     COUNT(*) AS total_requests,
--     SUM(cost_usd) AS total_cost_usd,
--     AVG(cost_usd) AS avg_cost_usd,
--     SUM(input_tokens) AS total_input_tokens,
--     SUM(output_tokens) AS total_output_tokens
-- FROM cost_logs
-- GROUP BY DATE(created_at);

-- 사용 예시:
-- SELECT * FROM v_daily_stats ORDER BY date DESC LIMIT 30;

-- ============================================
-- 8. 데이터 삭제 쿼리 (주의: 백업 후 사용)
-- ============================================

-- 8.1. 특정 세션의 모든 데이터 삭제
-- DELETE FROM conversation_messages WHERE session_id = 'your_session_id_here';
-- DELETE FROM api_request_logs WHERE session_id = 'your_session_id_here';
-- DELETE FROM cost_logs WHERE session_id = 'your_session_id_here';
-- DELETE FROM conversation_sessions WHERE session_id = 'your_session_id_here';

-- 8.2. 오래된 로그 삭제 (30일 이상)
-- DELETE FROM api_request_logs WHERE created_at < NOW() - INTERVAL '30 days';
-- DELETE FROM cost_logs WHERE created_at < NOW() - INTERVAL '30 days';

-- 8.3. 오래된 세션 삭제 (90일 이상 미사용)
-- DELETE FROM conversation_messages WHERE session_id IN (
--     SELECT session_id FROM conversation_sessions 
--     WHERE updated_at < NOW() - INTERVAL '90 days'
-- );
-- DELETE FROM conversation_sessions WHERE updated_at < NOW() - INTERVAL '90 days';

-- ============================================
-- 9. 성능 모니터링 쿼리
-- ============================================

-- 9.1. 느린 쿼리 확인 (PostgreSQL 9.3+)
-- SELECT 
--     query,
--     calls,
--     total_time,
--     mean_time,
--     max_time
-- FROM pg_stat_statements
-- WHERE query LIKE '%conversation%' OR query LIKE '%cost_log%'
-- ORDER BY mean_time DESC
-- LIMIT 20;

-- 9.2. 테이블 통계 정보 확인
-- SELECT 
--     schemaname,
--     tablename,
--     n_live_tup AS live_rows,
--     n_dead_tup AS dead_rows,
--     last_vacuum,
--     last_autovacuum,
--     last_analyze,
--     last_autoanalyze
-- FROM pg_stat_user_tables
-- WHERE tablename IN ('conversation_sessions', 'conversation_messages', 'api_request_logs', 'cost_logs');

-- ============================================
-- 사용 팁
-- ============================================
--
-- 1. 세션 ID 찾기:
--    SELECT session_id FROM conversation_sessions ORDER BY updated_at DESC LIMIT 10;
--
-- 2. 특정 기간 데이터 조회:
--    WHERE created_at >= '2025-11-01' AND created_at < '2025-12-01'
--
-- 3. 대용량 데이터 조회 시:
--    LIMIT 절을 사용하여 결과를 제한하세요.
--
-- 4. 백업:
--    중요 쿼리 실행 전에 데이터를 백업하세요.
--
-- 5. 인덱스:
--    자주 사용하는 컬럼에 인덱스가 생성되어 있습니다.
--    - session_id
--    - created_at
--    - (session_id, created_at) 복합 인덱스
--
-- ============================================

