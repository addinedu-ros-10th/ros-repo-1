-- ============================================================
-- svc_app 유저에게 모든 데이터베이스와 테이블 권한 부여
-- ============================================================
-- 
-- 이 스크립트는 svc_app 유저에게 다음 권한을 부여합니다:
-- 1. 모든 데이터베이스에 대한 연결 권한
-- 2. public 스키마에 대한 모든 권한
-- 3. 모든 테이블에 대한 모든 권한
-- 4. 모든 시퀀스에 대한 모든 권한
-- 5. 향후 생성될 테이블/시퀀스에 대한 기본 권한
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
-- (각 데이터베이스별로 실행 필요)
DO $$
DECLARE
    db_name TEXT;
BEGIN
    FOR db_name IN 
        SELECT datname 
        FROM pg_database 
        WHERE datistemplate = false 
        AND datname != 'postgres'
    LOOP
        EXECUTE format('GRANT CONNECT ON DATABASE %I TO svc_app', db_name);
        RAISE NOTICE '데이터베이스 %에 연결 권한 부여: %', db_name, 'svc_app';
    END LOOP;
END
$$;

-- 3. 현재 데이터베이스(iot_care)에 대한 모든 권한 부여
-- (이 스크립트는 iot_care 데이터베이스에서 실행되어야 함)
\c iot_care

-- 4. public 스키마에 대한 모든 권한 부여
GRANT ALL ON SCHEMA public TO svc_app;
GRANT USAGE ON SCHEMA public TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO svc_app;

-- 5. 기존 테이블에 대한 모든 권한 부여
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO svc_app;

-- 6. 기존 시퀀스에 대한 모든 권한 부여
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO svc_app;

-- 7. 기존 함수에 대한 실행 권한 부여
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO svc_app;

-- 8. 테이블 소유권 변경 (선택사항 - 필요시 주석 해제)
-- ALTER TABLE users OWNER TO svc_app;
-- ALTER TABLE user_profiles OWNER TO svc_app;
-- ALTER TABLE user_relationships OWNER TO svc_app;
-- ALTER TABLE residents OWNER TO svc_app;

-- 9. 권한 확인 (참고용)
-- 다음 쿼리로 권한을 확인할 수 있습니다:
-- SELECT grantee, privilege_type, table_name 
-- FROM information_schema.table_privileges 
-- WHERE grantee = 'svc_app';

