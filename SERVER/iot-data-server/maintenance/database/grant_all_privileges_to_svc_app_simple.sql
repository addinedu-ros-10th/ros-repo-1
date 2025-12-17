-- ============================================================
-- svc_app 유저에게 모든 데이터베이스와 테이블 권한 부여 (간단 버전)
-- ============================================================
-- 
-- 사용 방법:
-- 1. PostgreSQL 슈퍼유저로 postgres 데이터베이스에 연결
-- 2. 이 스크립트를 실행
-- 
-- 또는 psql로 실행:
-- psql -h <host> -p <port> -U postgres -f grant_all_privileges_to_svc_app_simple.sql
-- ============================================================

-- 1. svc_app 유저가 존재하지 않으면 생성
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'svc_app') THEN
        CREATE USER svc_app WITH PASSWORD 'change_me_please';
        RAISE NOTICE 'svc_app 유저가 생성되었습니다. 비밀번호를 변경해주세요.';
    ELSE
        RAISE NOTICE 'svc_app 유저가 이미 존재합니다.';
    END IF;
END
$$;

-- 2. 모든 데이터베이스에 대한 연결 권한 부여
DO $$
DECLARE
    db_name TEXT;
BEGIN
    FOR db_name IN 
        SELECT datname 
        FROM pg_database 
        WHERE datistemplate = false 
        AND datname NOT IN ('postgres', 'template0', 'template1')
    LOOP
        BEGIN
            EXECUTE format('GRANT CONNECT ON DATABASE %I TO svc_app', db_name);
            RAISE NOTICE '데이터베이스 %에 연결 권한 부여 완료', db_name;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE '데이터베이스 % 권한 부여 실패: %', db_name, SQLERRM;
        END;
    END LOOP;
END
$$;

-- 3. iot_care 데이터베이스에 연결하여 스키마 및 테이블 권한 부여
\c iot_care

-- 4. public 스키마에 대한 모든 권한 부여
GRANT ALL ON SCHEMA public TO svc_app;
GRANT USAGE ON SCHEMA public TO svc_app;

-- 5. 기본 권한 설정 (향후 생성될 객체에 대한 권한)
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO svc_app;

-- 6. 기존 테이블에 대한 모든 권한 부여
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO svc_app;

-- 7. 기존 시퀀스에 대한 모든 권한 부여
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO svc_app;

-- 8. 기존 함수에 대한 실행 권한 부여
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO svc_app;

-- 9. 권한 확인 쿼리 (참고용)
-- 다음 쿼리로 권한을 확인할 수 있습니다:
/*
SELECT 
    grantee, 
    table_schema,
    table_name, 
    privilege_type
FROM information_schema.table_privileges 
WHERE grantee = 'svc_app'
ORDER BY table_name, privilege_type;
*/

-- 10. 완료 메시지
DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'svc_app 유저 권한 부여 완료!';
    RAISE NOTICE '========================================';
END
$$;

