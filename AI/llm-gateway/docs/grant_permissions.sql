-- ============================================
-- 테이블 권한 부여 스크립트
-- ============================================
-- 
-- 이 스크립트는 svc_app 및 기타 사용자에게 
-- LLM Gateway 테이블에 대한 권한을 부여합니다.
--
-- 사용법:
-- psql -h localhost -p 15432 -U svc_dev -d iot_care -f grant_permissions.sql
-- 또는
-- psql에서 직접 실행: \i grant_permissions.sql
--
-- ============================================

-- 현재 데이터베이스 및 스키마 확인
SELECT 
    current_database() AS database_name,
    current_schema() AS current_schema;

-- ============================================
-- 1. 테이블 존재 여부 및 스키마 확인
-- ============================================

SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name IN (
        'conversation_sessions',
        'conversation_messages',
        'api_request_logs',
        'cost_logs'
    )
ORDER BY table_name;

-- ============================================
-- 2. svc_app 사용자에게 권한 부여
-- ============================================

-- 각 테이블에 대해 SELECT, INSERT, UPDATE, DELETE 권한 부여
GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversation_sessions TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversation_messages TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.api_request_logs TO svc_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON public.cost_logs TO svc_app;

-- 시퀀스 권한 부여 (SERIAL 컬럼용)
GRANT USAGE, SELECT ON SEQUENCE conversation_messages_id_seq TO svc_app;
GRANT USAGE, SELECT ON SEQUENCE api_request_logs_id_seq TO svc_app;
GRANT USAGE, SELECT ON SEQUENCE cost_logs_id_seq TO svc_app;

-- ============================================
-- 3. 권한 확인
-- ============================================

-- svc_app이 가진 권한 확인
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.role_table_grants
WHERE grantee = 'svc_app'
    AND table_name IN (
        'conversation_sessions',
        'conversation_messages',
        'api_request_logs',
        'cost_logs'
    )
ORDER BY table_name, privilege_type;

-- ============================================
-- 4. 추가 사용자 권한 부여 (필요시)
-- ============================================
-- 다른 사용자에게도 권한을 부여하려면 아래를 수정하세요:
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversation_sessions TO your_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.conversation_messages TO your_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.api_request_logs TO your_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON public.cost_logs TO your_user;

