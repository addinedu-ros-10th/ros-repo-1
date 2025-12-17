# 요양원 내부 입소자 관리 정보 테이블 구현 리포트

## 📋 개요

요양원 내부 사용자 정보를 관리하기 위한 `residents` 테이블과 REST API를 구현했습니다. 이 테이블은 기존 `users`, `user_profiles`, `user_relationships` 테이블과 연계하여 요양원에서 필요한 모든 입소자 관리 정보를 체계적으로 관리합니다.

## 🗄️ 데이터베이스 스키마

### 테이블명: `residents`

#### 주요 필드

1. **기본 정보**
   - `user_id` (PK, FK → users.user_id): 사용자 ID (1:1 관계)
   - `resident_number`: 요양원 내부 관리 번호 (예: R-2024-001)
   - `nickname`: 애칭 (일본어 이름 등)

2. **입소 관리**
   - `admission_date`: 입소일 (필수)
   - `discharge_date`: 퇴소일 (NULL이면 현재 입소 중)

3. **생활실 정보**
   - `room_number`: 생활실 번호 (예: 302호)
   - `floor_number`: 층수
   - `bed_number`: 침대 번호

4. **ADL (일상생활 활동) 수준**
   - `adl_level`: independent, partial_assistance, full_assistance
   - `mobility_level`: independent, walker, wheelchair, bedridden
   - `cognitive_level`: normal, mild_impairment, moderate_impairment, severe_impairment

5. **복약 관리**
   - `medication_schedule` (JSONB): 복약 일정
   - `medication_notes`: 복약 특이사항

6. **특이사항 (JSONB)**
   - `special_notes`: 건강, 정서, 심리 상태
   - `incidents`: 사건/사고 기록
   - `dietary_restrictions`: 식이 제한

7. **연락처 및 보험 정보 (JSONB)**
   - `emergency_contacts`: 응급 연락처
   - `insurance_info`: 보험 정보
   - `medical_facility_info`: 의료 기관 정보

8. **기타 관리 정보**
   - `care_level`: 요양 등급
   - `guardian_name`, `guardian_relationship`, `guardian_phone`: 보호자 정보

## 🏗️ 아키텍처

### 계층 구조

```
API Layer (FastAPI)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
    ↓
Domain Entities
    ↓
ORM Models (SQLAlchemy)
    ↓
PostgreSQL Database
```

### 구현된 컴포넌트

1. **ORM 모델**: `app/infrastructure/models.py` - `ResidentInfo` 클래스
2. **도메인 엔티티**: `app/domain/entities/resident_info.py`
3. **Repository 인터페이스**: `app/interfaces/repositories/resident_info_repository.py`
4. **Repository 구현체**: `app/infrastructure/repositories/resident_info_repository.py`
5. **Service 인터페이스**: `app/interfaces/services/resident_info_service_interface.py`
6. **Service 구현체**: `app/use_cases/resident_info_service.py`
7. **API 스키마**: `app/api/v1/schemas.py` - `ResidentInfo*` 클래스들
8. **API 엔드포인트**: `app/api/v1/residents.py`
9. **의존성 주입**: `app/core/container.py`

## 🔌 REST API 엔드포인트

### 기본 CRUD

- `POST /api/residents/create/{user_id}`: 입소자 정보 생성
- `GET /api/residents/{user_id}`: 입소자 정보 조회
- `GET /api/residents/number/{resident_number}`: 입소자 번호로 조회
- `PUT /api/residents/{user_id}`: 입소자 정보 수정
- `DELETE /api/residents/{user_id}`: 입소자 정보 삭제

### 목록 조회

- `GET /api/residents/`: 모든 입소자 정보 조회 (페이지네이션)
- `GET /api/residents/current/list`: 현재 입소 중인 입소자 조회 (페이지네이션)

### 필터링 조회

- `GET /api/residents/room/{room_number}`: 특정 생활실의 입소자 조회
- `GET /api/residents/floor/{floor_number}`: 특정 층의 입소자 조회
- `GET /api/residents/adl/{adl_level}`: 특정 ADL 수준의 입소자 조회
- `GET /api/residents/search/{keyword}`: 키워드로 검색

### 특수 기능

- `POST /api/residents/{user_id}/discharge`: 입소자 퇴소 처리
- `POST /api/residents/{user_id}/incidents`: 사건/사고 기록 추가
- `PUT /api/residents/{user_id}/medication-schedule`: 복약 일정 업데이트

## 📊 목업 데이터

### 생성된 입소자 정보

1. **정도현 (Akaza)**
   - 입소일: 2022-03-15
   - 생활실: 302호 (3층)
   - ADL: 부분 도움 필요
   - 주요 병력: 고혈압, 당뇨, 낙상 이력

2. **한기문 (Gyomei Himejima)**
   - 입소일: 2021-08-20
   - 생활실: 205호 (2층)
   - ADL: 전면 도움 필요
   - 주요 병력: 당뇨, 고지혈증, 심부전, 시각장애

3. **이강열 (Kyojuro Rengoku)**
   - 입소일: 2023-01-10
   - 생활실: 108호 (1층)
   - ADL: 독립적
   - 주요 병력: 고혈압, 협심증, 관절염

4. **김선우 (Zenitsu Agatsuma)**
   - 입소일: 2023-05-20
   - 생활실: 407호 (4층)
   - ADL: 부분 도움 필요
   - 주요 병력: 불안장애, 불면증, 경도 치매

## 🔗 테이블 간 관계

```
users (1) ──── (1) user_profiles
  │
  │ (1)
  │
  └─── (1) residents
         │
         └─── (N) user_relationships (N) ──── (1) users
```

- `users` ↔ `residents`: 1:1 관계 (입소자만 residents 테이블에 데이터 존재)
- `users` ↔ `user_profiles`: 1:1 관계
- `users` ↔ `user_relationships`: 1:N 관계 (돌봄, 가족, 관리 관계)

## 📝 사용 방법

### 1. 데이터베이스 테이블 생성

```sql
-- SQL 스크립트 실행
\i maintenance/database/create_residents_table.sql
```

또는 Python 코드로:

```python
from app.infrastructure.database import create_tables
create_tables()  # 모든 테이블 생성 (residents 포함)
```

### 2. 목업 데이터 삽입

```sql
-- SQL 스크립트 실행
\i maintenance/database/insert_residents_mock_data.sql
```

### 3. API 사용 예시

```bash
# 입소자 정보 조회
curl -X GET "http://localhost:8000/api/residents/00000000-0000-0000-0000-000000000001"

# 현재 입소 중인 입소자 목록 조회
curl -X GET "http://localhost:8000/api/residents/current/list?page=1&size=10"

# 특정 생활실의 입소자 조회
curl -X GET "http://localhost:8000/api/residents/room/302"

# 사건/사고 기록 추가
curl -X POST "http://localhost:8000/api/residents/00000000-0000-0000-0000-000000000001/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_date": "2024-01-20",
    "incident_type": "낙상",
    "location": "화장실",
    "severity": "경미",
    "description": "야간 화장실 이동 중 미끄러짐",
    "action_taken": "응급실 방문, X-ray 촬영",
    "preventive_measures": "화장실 바닥 미끄럼 방지 매트 설치"
  }'
```

## ✅ 완료된 작업

- [x] 데이터베이스 테이블 설계 및 SQL 생성
- [x] ORM 모델 생성
- [x] 도메인 엔티티 생성
- [x] Repository 인터페이스 및 구현체 생성
- [x] Service 인터페이스 및 구현체 생성
- [x] API 스키마 정의
- [x] REST API 엔드포인트 생성
- [x] 의존성 주입 설정
- [x] API 라우터 등록
- [x] 목업 데이터 생성

## 🎯 다음 단계 (선택사항)

1. **테스트 코드 작성**: Unit 테스트 및 Integration 테스트
2. **API 문서화**: Swagger/OpenAPI 문서 보완
3. **검색 기능 강화**: Full-text search, 복합 조건 검색
4. **통계 API**: 입소자 통계, 건강 상태 추이 등
5. **알림 기능**: 복약 시간 알림, 건강 상태 모니터링 등

## 📚 참고 파일

- SQL 스크립트: `maintenance/database/create_residents_table.sql`
- 목업 데이터: `maintenance/database/insert_residents_mock_data.sql`
- API 문서: `http://localhost:8000/docs` (서버 실행 후)

