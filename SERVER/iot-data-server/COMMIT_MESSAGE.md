# 커밋 메시지

## 제목
feat: 요양원 입소자 관리 시스템 구현 및 테이블 구조 개선

## 본문

### 주요 기능
- residents 테이블 생성 및 기본 정보 필드 추가
- 입소자 관리 REST API 구현 (15개 엔드포인트)
- 데이터베이스 연결 Fallback 메커니즘 추가
- 전화번호 검증 로직 개선 (하이픈 포함 형식 허용)

### 데이터베이스
- residents 테이블 생성 (25개 컬럼)
- 기본 정보 필드 추가 (user_name, email, phone_number)
- 목업 데이터 삽입 (4명의 입소자 정보)
- 모든 테이블이 user_id를 기준으로 조인 가능

### API 구현
- 입소자 정보 CRUD API
- 다양한 조회 기능 (생활실별, 층별, ADL 수준별, 키워드 검색)
- 사건/사고 기록 추가, 복약 일정 업데이트, 퇴소 처리

### 코드 개선
- ORM 모델, 도메인 엔티티, 리포지토리, 서비스 구현
- 데이터베이스 연결 Fallback 메커니즘 (env HOST 실패 시 host.docker.internal 재시도)
- 전화번호 검증 로직 개선 (하이픈 포함 형식 허용)

### 문서 및 스크립트
- 조인 쿼리 가이드 작성
- API 기능 점검 리포트 작성
- 테이블 상태 확인 스크립트 작성
- SQL 파일 실행 스크립트 작성

### 테스트
- 모든 API 엔드포인트 정상 작동 확인 (15개)
- 데이터베이스 조인 쿼리 테스트 완료
- N:N 관계 조회 테스트 완료

## 변경된 파일
- maintenance/database/create_residents_table.sql (신규)
- maintenance/database/update_residents_table_add_basic_info.sql (신규)
- app/infrastructure/models.py (수정)
- app/domain/entities/resident_info.py (수정)
- app/infrastructure/repositories/resident_info_repository.py (수정)
- app/api/v1/schemas.py (수정)
- app/api/v1/residents.py (수정)
- app/infrastructure/database.py (수정)
- app/core/config.py (수정)
- app/main.py (수정)
- scripts/check_table_data_status.py (신규)
- scripts/execute_sql_file.py (신규)
- docs/* (다수 문서 추가)

