# svc_app 유저 권한 부여 가이드

**작성일**: 2024년  
**목적**: svc_app 유저에게 모든 데이터베이스와 테이블에 대한 모든 권한 부여

---

## 📋 부여되는 권한

### 1. 데이터베이스 권한
- 모든 데이터베이스에 대한 연결 권한 (`CONNECT`)

### 2. 스키마 권한
- `public` 스키마에 대한 모든 권한 (`ALL`)
- 스키마 사용 권한 (`USAGE`)

### 3. 테이블 권한
- 기존 테이블에 대한 모든 권한 (`ALL PRIVILEGES`)
- 향후 생성될 테이블에 대한 기본 권한 (`ALTER DEFAULT PRIVILEGES`)

### 4. 시퀀스 권한
- 기존 시퀀스에 대한 모든 권한 (`ALL PRIVILEGES`)
- 향후 생성될 시퀀스에 대한 기본 권한 (`ALTER DEFAULT PRIVILEGES`)

### 5. 함수 권한
- 기존 함수에 대한 실행 권한 (`EXECUTE`)
- 향후 생성될 함수에 대한 기본 권한 (`ALTER DEFAULT PRIVILEGES`)

---

## 🚀 실행 방법

### 방법 1: Python 스크립트 사용 (권장)

```bash
cd SERVER/iot-data-server
python3 maintenance/database/grant_all_privileges_to_svc_app_python.py
```

**요구사항**:
- `.env.local` 파일에 데이터베이스 연결 정보가 있어야 함
- 슈퍼유저 권한이 있는 사용자로 연결되어야 함

---

### 방법 2: SQL 스크립트 사용

#### 2-1. psql로 실행

```bash
# postgres 데이터베이스에 연결하여 실행
psql -h <DB_HOST> -p <DB_PORT> -U postgres -d postgres -f maintenance/database/grant_all_privileges_to_svc_app_simple.sql

# iot_care 데이터베이스에 연결하여 스키마 권한 부여
psql -h <DB_HOST> -p <DB_PORT> -U postgres -d iot_care -f maintenance/database/grant_all_privileges_to_svc_app.sql
```

#### 2-2. SQL 파일 직접 실행

```sql
-- 1. postgres 데이터베이스에 연결
\c postgres

-- 2. 사용자 생성 및 데이터베이스 권한 부여
-- (grant_all_privileges_to_svc_app_simple.sql의 1-2번 섹션 실행)

-- 3. iot_care 데이터베이스에 연결
\c iot_care

-- 4. 스키마 및 테이블 권한 부여
-- (grant_all_privileges_to_svc_app_simple.sql의 4-8번 섹션 실행)
```

---

### 방법 3: 수동 실행

#### 3-1. 사용자 생성 (없는 경우)

```sql
CREATE USER svc_app WITH PASSWORD 'your_password_here';
```

#### 3-2. 데이터베이스 연결 권한 부여

```sql
-- postgres 데이터베이스에 연결
\c postgres

-- 모든 데이터베이스에 연결 권한 부여
GRANT CONNECT ON DATABASE iot_care TO svc_app;
-- 다른 데이터베이스가 있다면 반복
```

#### 3-3. 스키마 및 테이블 권한 부여

```sql
-- iot_care 데이터베이스에 연결
\c iot_care

-- 스키마 권한
GRANT ALL ON SCHEMA public TO svc_app;
GRANT USAGE ON SCHEMA public TO svc_app;

-- 기본 권한 설정
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO svc_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO svc_app;

-- 기존 테이블 권한
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO svc_app;

-- 기존 시퀀스 권한
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO svc_app;

-- 기존 함수 권한
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO svc_app;
```

---

## ✅ 권한 확인

### 1. 사용자 정보 확인

```sql
SELECT 
    usename,
    usecreatedb,
    usesuper,
    usebypassrls
FROM pg_user 
WHERE usename = 'svc_app';
```

### 2. 데이터베이스 권한 확인

```sql
SELECT 
    datname,
    datacl
FROM pg_database 
WHERE datname = 'iot_care';
```

### 3. 테이블 권한 확인

```sql
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.table_privileges 
WHERE grantee = 'svc_app'
ORDER BY table_name, privilege_type;
```

### 4. 스키마 권한 확인

```sql
SELECT 
    nspname,
    nspowner::regrole,
    nspacl
FROM pg_namespace 
WHERE nspname = 'public';
```

---

## 📝 생성된 파일

1. `maintenance/database/grant_all_privileges_to_svc_app.sql` - 전체 SQL 스크립트
2. `maintenance/database/grant_all_privileges_to_svc_app_simple.sql` - 간단 버전 SQL 스크립트
3. `maintenance/database/grant_all_privileges_to_svc_app_python.py` - Python 스크립트

---

## ⚠️ 주의사항

### 보안
- `svc_app` 유저의 비밀번호를 안전하게 설정하세요
- 프로덕션 환경에서는 최소 권한 원칙을 고려하세요

### 권한 범위
- 이 스크립트는 `svc_app` 유저에게 **모든 권한**을 부여합니다
- 필요에 따라 특정 권한만 부여하도록 수정할 수 있습니다

### 실행 권한
- 이 스크립트는 **슈퍼유저** 또는 **데이터베이스 소유자** 권한이 필요합니다
- 일반 사용자로는 실행할 수 없습니다

---

## 🔍 문제 해결

### 오류: "permission denied"
- 슈퍼유저 권한이 있는 사용자로 연결했는지 확인
- 데이터베이스 소유자 권한이 있는지 확인

### 오류: "role does not exist"
- `svc_app` 유저가 생성되지 않았을 수 있음
- 스크립트의 사용자 생성 부분을 먼저 실행

### 오류: "database does not exist"
- `iot_care` 데이터베이스가 존재하는지 확인
- 데이터베이스 이름이 올바른지 확인

---

**작성자**: AI Assistant  
**작성일**: 2024년

