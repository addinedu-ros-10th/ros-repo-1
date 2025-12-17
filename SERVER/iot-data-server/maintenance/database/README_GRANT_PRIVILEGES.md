# svc_app 유저 권한 부여 스크립트

## 빠른 시작

### Python 스크립트 사용 (권장)

```bash
cd SERVER/iot-data-server
python3 maintenance/database/grant_all_privileges_to_svc_app_python.py
```

### SQL 스크립트 사용

```bash
# postgres 데이터베이스에 연결하여 실행
psql -h <DB_HOST> -p <DB_PORT> -U postgres -f maintenance/database/grant_all_privileges_to_svc_app_simple.sql
```

## 부여되는 권한

- ✅ 모든 데이터베이스 연결 권한
- ✅ public 스키마 모든 권한
- ✅ 모든 테이블 모든 권한
- ✅ 모든 시퀀스 모든 권한
- ✅ 모든 함수 실행 권한
- ✅ 향후 생성될 객체에 대한 기본 권한

## 상세 가이드

`docs/GRANT_PRIVILEGES_TO_SVC_APP_GUIDE.md` 참조

