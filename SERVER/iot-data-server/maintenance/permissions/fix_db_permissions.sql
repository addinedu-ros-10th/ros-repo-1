-- 데이터베이스 권한 문제 해결을 위한 SQL 스크립트
-- PostgreSQL 슈퍼유저 또는 데이터베이스 소유자로 실행해야 합니다.

-- 1. 현재 연결된 사용자 확인
SELECT current_user, session_user, current_database();

-- 2. users 테이블 소유자 확인
SELECT 
    schemaname,
    tablename,
    tableowner,
    tablespace
FROM pg_tables 
WHERE tablename = 'users';

-- 3. svc_app 사용자에게 users 테이블 권한 부여
-- SELECT 권한 부여
GRANT SELECT ON TABLE users TO svc_app;

-- INSERT, UPDATE, DELETE 권한도 필요하다면
GRANT INSERT, UPDATE, DELETE ON TABLE users TO svc_app;

-- 모든 권한 부여 (필요한 경우)
-- GRANT ALL PRIVILEGES ON TABLE users TO svc_app;

-- 4. public 스키마에 대한 권한 확인
SELECT 
    nspname,
    nspowner::regrole,
    nspacl
FROM pg_namespace 
WHERE nspname = 'public';

-- 5. public 스키마에 대한 권한 부여 (필요한 경우)
GRANT USAGE ON SCHEMA public TO svc_app;
GRANT CREATE ON SCHEMA public TO svc_app;

-- 6. 기존 테이블들에 대한 권한 부여
-- 모든 public 스키마 테이블에 대한 권한 부여
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE ' || quote_ident(r.tablename) || ' TO svc_app';
    END LOOP;
END $$;

-- 7. 권한 부여 확인
SELECT 
    grantee,
    table_name,
    privilege_type,
    is_grantable
FROM information_schema.table_privileges 
WHERE table_name = 'users' 
AND table_schema = 'public'
ORDER BY grantee, privilege_type;

-- 8. 사용자 권한 확인
SELECT 
    usename,
    usecreatedb,
    usesuper,
    usebypassrls
FROM pg_user 
WHERE usename = 'svc_app';
