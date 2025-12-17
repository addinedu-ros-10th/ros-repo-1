# 📁 IoT Care Backend - 새로운 파일 구조 가이드

## 🎯 **파일 구조 리팩터링 목적**
서버 프레임워크에서 관리되지 않는 파일들을 기능별로 분류하여 체계적인 관리와 유지보수를 목적으로 합니다.

## 🏗️ **새로운 디렉토리 구조**

### **📂 maintenance/** - 유지보수 및 관리 도구
- **`database/`** - 데이터베이스 테이블 생성 및 수정
  - `create_tables.py` - 테이블 생성 스크립트
  - `fix_database.py` - 데이터베이스 수정 스크립트
  - `fix_edge_tables.py` - Edge 테이블 수정 스크립트
  - `fix_raw_sensor_tables.py` - 센서 테이블 수정 스크립트

- **`data/`** - 테스트 데이터 생성
  - `create_test_devices.py` - 테스트 디바이스 생성
  - `create_test_users.py` - 테스트 사용자 생성

- **`permissions/`** - 데이터베이스 권한 관리
  - `fix_db_permissions.sql` - 권한 수정 SQL 스크립트
  - `fix_permissions_simple.py` - 권한 수정 스크립트
  - `grant_permissions_script.py` - 권한 부여 스크립트
  - `grant_permissions_to_svc_app.sql` - 서비스 앱 권한 부여

- **`cleanup/`** - 데이터 정리
  - `clean_edge_data.py` - Edge 데이터 정리
  - `clean_raw_data.py` - 원시 데이터 정리

### **🔍 diagnostics/** - 진단 및 모니터링 도구
- **`connection/`** - 연결 상태 확인
  - `test_db_connection.py` - DB 연결 상태 확인

- **`schema/`** - 데이터베이스 스키마 확인
  - `check_db_permissions.py` - DB 권한 확인
  - `check_db_schema.py` - DB 스키마 확인
  - `check_edge_data.py` - Edge 데이터 확인
  - `check_raw_tables.py` - 원시 테이블 확인
  - `check_table_structure.py` - 테이블 구조 확인

- **`api/`** - API 상태 확인
  - `check_api_logs.py` - API 로그 확인
  - `check_api_simple.py` - API 간단 확인

- **`user/`** - 사용자 권한 확인
  - `check_user_permissions.py` - 사용자 권한 확인
  - `check_user_permissions_local.py` - 로컬 사용자 권한 확인

### **⚙️ environment/** - 환경 설정 및 스크립트
- **`scripts/`** - 프로젝트 실행 스크립트
  - `start_project.sh` - 프로젝트 시작 스크립트 (Linux/Mac)
  - `start_project.bat` - 프로젝트 시작 스크립트 (Windows)
  - `docker-run.sh` - Docker 실행 스크립트

- **`install/`** - 패키지 설치 스크립트
  - `install_packages.bat` - 패키지 설치 (Windows)
  - `install_packages.ps1` - 패키지 설치 (PowerShell)
  - `activate_and_install.bat` - 가상환경 활성화 및 설치 (Windows)
  - `activate_and_install.ps1` - 가상환경 활성화 및 설치 (PowerShell)

- **`update/`** - 환경 변수 업데이트
  - `update_env_vars.sh` - 환경 변수 업데이트 (Linux/Mac)
  - `update_env_vars_macos.sh` - macOS 환경 변수 업데이트

### **📚 documentation/** - 문서 및 가이드
- **`project/`** - 프로젝트 관련 문서
  - `README.md` - 프로젝트 메인 문서
  - `README_AUTO_ENV_UPDATE.md` - 자동 환경 업데이트 가이드
  - `PROJECT_COMPLETION_CHECKLIST.md` - 프로젝트 완성 체크리스트
  - `PROJECT_COMPLETION_REPORT.md` - 프로젝트 완성 보고서
  - `API_INTEGRATION_TEST_REPORT.md` - API 통합 테스트 보고서

### **🛠️ utilities/** - 유틸리티 도구
- **`testing/`** - 테스트 관련 도구
  - `test_all_apis.py` - API 통합 테스트
  - `test_api_status_local.py` - API 상태 확인 (포트 미지정)
  - `test_api_endpoints.sh` - API 엔드포인트 테스트 스크립트
  - `integration_test_results_*.json` - 통합 테스트 결과 파일

- **`access/`** - 접근 테스트 도구
  - `test_direct_access.py` - 직접 접근 테스트

## 🔒 **프레임워크 관리 파일 (이동하지 않음)**

### **🏗️ 핵심 애플리케이션**
- `app/` - FastAPI 애플리케이션 소스 코드
- `main.py` - 애플리케이션 진입점
- `requirements.txt` - Python 의존성
- `alembic.ini` - 데이터베이스 마이그레이션 설정

### **🐳 컨테이너화**
- `Dockerfile` - Docker 이미지 빌드
- `docker-compose*.yml` - Docker Compose 설정

### **🌐 웹 서버**
- `Caddyfile*` - Caddy 웹 서버 설정

### **🧪 테스트**
- `tests/` - 단위 테스트 및 통합 테스트

## ✅ **리팩터링 검증 결과**

### **🔍 영향도 분석**
- **Docker Compose**: 상대 경로 사용으로 파일 이동에 영향 없음
- **FastAPI**: 표준 구조 유지, 외부 파일 참조 없음
- **스크립트**: 상대 경로 사용으로 파일 이동에 영향 없음

### **🚀 실행 테스트**
프레임워크나 Docker Compose 프로젝트 실행에 문제가 없음을 확인했습니다.

## 📋 **사용 가이드**

### **1. 유지보수 작업**
```bash
# 데이터베이스 수정이 필요한 경우
cd maintenance/database/
python fix_database.py

# 권한 문제 해결이 필요한 경우
cd maintenance/permissions/
python grant_permissions_script.py
```

### **2. 진단 및 모니터링**
```bash
# 데이터베이스 연결 상태 확인
cd diagnostics/connection/
python test_db_connection.py

# API 상태 확인
cd diagnostics/api/
python check_api_simple.py
```

### **3. 환경 설정**
```bash
# 프로젝트 시작
cd environment/scripts/
./start_project.sh

# 환경 변수 업데이트
cd environment/update/
./update_env_vars.sh
```

## 🔄 **향후 관리 방침**

1. **새로운 유지보수 도구**는 해당 기능의 디렉토리에 추가
2. **진단 도구**는 기능별로 적절한 diagnostics 하위 디렉토리에 배치
3. **환경 설정 스크립트**는 플랫폼별로 environment 하위에 배치
4. **문서**는 목적별로 documentation 하위에 배치

---

**작성일**: 2025-08-25  
**작성자**: AI Assistant  
**프로젝트**: IoT Care Backend 파일 구조 리팩터링



