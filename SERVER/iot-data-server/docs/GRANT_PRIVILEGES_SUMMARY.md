# svc_app 유저 권한 부여 요약

**작성일**: 2024년  
**목적**: svc_app 유저에게 모든 데이터베이스와 테이블에 대한 모든 권한 부여

---

## ✅ 생성된 스크립트

### 1. SQL 스크립트
- `maintenance/database/grant_all_privileges_to_svc_app.sql` - 전체 SQL 스크립트
- `maintenance/database/grant_all_privileges_to_svc_app_simple.sql` - 간단 버전 (권장)

### 2. Python 스크립트
- `maintenance/database/grant_all_privileges_to_svc_app_python.py` - 자동화 스크립트

---

## 🚀 빠른 실행

### 방법 1: SQL 스크립트 (가장 간단)

```bash
cd SERVER/iot-data-server

# PostgreSQL 슈퍼유저로 실행
psql -h <DB_HOST> -p <DB_PORT> -U postgres -f maintenance/database/grant_all_privileges_to_svc_app_simple.sql
```

### 방법 2: Python 스크립트

```bash
cd SERVER/iot-data-server

# .env.local 파일이 있는 경우
python3 maintenance/database/grant_all_privileges_to_svc_app_python.py

# 환경 변수를 직접 설정하는 경우
DB_HOST=<host> DB_PORT=<port> DB_USER=<user> DB_PASSWORD=<password> \
python3 maintenance/database/grant_all_privileges_to_svc_app_python.py
```

---

## 📋 부여되는 권한

| 권한 유형 | 권한 내용 |
|----------|----------|
| **데이터베이스** | 모든 데이터베이스 연결 권한 |
| **스키마** | public 스키마 모든 권한 |
| **테이블** | 모든 테이블 모든 권한 (기존 + 향후 생성) |
| **시퀀스** | 모든 시퀀스 모든 권한 (기존 + 향후 생성) |
| **함수** | 모든 함수 실행 권한 (기존 + 향후 생성) |

---

## ✅ 실행 후 확인

```sql
-- 1. 사용자 확인
SELECT usename, usecreatedb, usesuper FROM pg_user WHERE usename = 'svc_app';

-- 2. 테이블 권한 확인
SELECT table_name, privilege_type 
FROM information_schema.table_privileges 
WHERE grantee = 'svc_app'
ORDER BY table_name;
```

---

## 📚 상세 가이드

`docs/GRANT_PRIVILEGES_TO_SVC_APP_GUIDE.md` 참조

---

**작성자**: AI Assistant  
**작성일**: 2024년

