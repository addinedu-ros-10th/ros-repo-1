# 요양원 입소자 관리 테이블 및 API 구현 현황 리포트

**작성일**: 2024년  
**프로젝트**: SERVER/iot-data-server  
**작업 내용**: `residents` 테이블 생성 및 REST API 구현

---

## 📋 목차

1. [작업 개요](#작업-개요)
2. [작업 수행 현황](#작업-수행-현황)
3. [생성된 파일 목록](#생성된-파일-목록)
4. [데이터베이스 구조](#데이터베이스-구조)
5. [API 엔드포인트 목록](#api-엔드포인트-목록)
6. [데이터 확인 가이드](#데이터-확인-가이드)
7. [API 테스트 가이드](#api-테스트-가이드)
8. [다음 단계](#다음-단계)

---

## 작업 개요

요양원 내부 입소자 정보를 관리하기 위한 `residents` 테이블과 REST API를 구현했습니다.

### 주요 기능

- ✅ 입소자 상세 정보 관리 (입소일, 퇴소일, 생활실 정보 등)
- ✅ 복약 일정 및 특이사항 관리
- ✅ 건강/정서/심리 상태 관리 (JSONB)
- ✅ 사건/사고 기록 관리 (JSONB)
- ✅ 식이 제한 관리
- ✅ 응급 연락처 관리
- ✅ 보험 정보 및 의료 기관 연계 정보 관리
- ✅ REST API를 통한 CRUD 작업 지원

---

## 작업 수행 현황

### ✅ 완료된 작업

| 작업 항목 | 상태 | 파일 경로 |
|---------|------|----------|
| **1. 데이터베이스 테이블 생성 SQL** | ✅ 완료 | `maintenance/database/create_residents_table.sql` |
| **2. 목업 데이터 SQL** | ✅ 완료 | `maintenance/database/insert_all_users_mock_data.sql` |
| **3. ORM 모델** | ✅ 완료 | `app/infrastructure/models.py` (ResidentInfo 클래스) |
| **4. 도메인 엔티티** | ✅ 완료 | `app/domain/entities/resident_info.py` |
| **5. 리포지토리 인터페이스** | ✅ 완료 | `app/interfaces/repositories/resident_info_repository.py` |
| **6. 리포지토리 구현** | ✅ 완료 | `app/infrastructure/repositories/resident_info_repository.py` |
| **7. 서비스 인터페이스** | ✅ 완료 | `app/interfaces/services/resident_info_service_interface.py` |
| **8. 서비스 구현** | ✅ 완료 | `app/use_cases/resident_info_service.py` |
| **9. API 스키마** | ✅ 완료 | `app/api/v1/schemas.py` (ResidentInfo 관련 스키마) |
| **10. API 엔드포인트** | ✅ 완료 | `app/api/v1/residents.py` |
| **11. 의존성 주입 설정** | ✅ 완료 | `app/core/container.py` |
| **12. API 라우터 등록** | ✅ 완료 | `app/api/__init__.py` |

---

## 생성된 파일 목록

### 1. 데이터베이스 관련 파일

```
SERVER/iot-data-server/
├── maintenance/
│   └── database/
│       ├── create_residents_table.sql          # 테이블 생성 SQL
│       └── insert_all_users_mock_data.sql     # 통합 목업 데이터 SQL
```

### 2. 애플리케이션 코드 파일

```
SERVER/iot-data-server/
├── app/
│   ├── infrastructure/
│   │   ├── models.py                          # ORM 모델 (ResidentInfo 추가)
│   │   └── repositories/
│   │       └── resident_info_repository.py     # 리포지토리 구현
│   ├── domain/
│   │   └── entities/
│   │       └── resident_info.py              # 도메인 엔티티
│   ├── interfaces/
│   │   ├── repositories/
│   │   │   └── resident_info_repository.py     # 리포지토리 인터페이스
│   │   └── services/
│   │       └── resident_info_service_interface.py  # 서비스 인터페이스
│   ├── use_cases/
│   │   └── resident_info_service.py           # 서비스 구현
│   ├── api/
│   │   ├── v1/
│   │   │   ├── schemas.py                     # API 스키마 (ResidentInfo 추가)
│   │   │   └── residents.py                  # API 엔드포인트
│   │   └── __init__.py                        # API 라우터 등록
│   └── core/
│       └── container.py                       # 의존성 주입 설정
```

---

## 데이터베이스 구조

### `residents` 테이블 스키마

```sql
CREATE TABLE residents (
    -- 기본 키
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- 입소 관리 정보
    resident_number VARCHAR(20) UNIQUE,      -- 요양원 내부 관리 번호
    nickname VARCHAR(50),                     -- 애칭
    admission_date DATE NOT NULL,             -- 입소일
    discharge_date DATE,                      -- 퇴소일 (NULL이면 현재 입소 중)
    
    -- 생활실 정보
    room_number VARCHAR(20),                  -- 생활실 번호
    floor_number INTEGER,                     -- 층수
    bed_number VARCHAR(10),                   -- 침대 번호
    
    -- ADL 수준
    adl_level VARCHAR(20),                    -- independent, partial_assistance, full_assistance
    mobility_level VARCHAR(20),               -- independent, walker, wheelchair, bedridden
    cognitive_level VARCHAR(20),              -- normal, mild_impairment, moderate_impairment, severe_impairment
    
    -- 복약 관리
    medication_schedule JSONB,                -- 복약 일정 (JSON)
    medication_notes TEXT,                    -- 복약 특이사항
    
    -- 특이사항 (JSONB)
    special_notes JSONB,                      -- 건강, 정서, 심리 상태
    incidents JSONB,                          -- 사건/사고 기록
    dietary_restrictions JSONB,               -- 식이 제한
    emergency_contacts JSONB,                 -- 응급 연락처
    insurance_info JSONB,                     -- 보험 정보
    medical_facility_info JSONB,              -- 의료 기관 정보
    
    -- 기타 관리 정보
    care_level VARCHAR(20),                   -- 요양 등급
    guardian_name VARCHAR(100),                -- 보호자 이름
    guardian_relationship VARCHAR(50),           -- 보호자 관계
    guardian_phone VARCHAR(20),                -- 보호자 전화번호
    
    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 테이블 관계

```
users (1) ──< (1) residents
users (1) ──< (1) user_profiles
users (1) ──< (*) user_relationships (subject_user_id)
users (1) ──< (*) user_relationships (target_user_id)
```

---

## API 엔드포인트 목록

### 기본 경로

모든 API는 `/api/v1/residents` 경로를 사용합니다.

### 1. 입소자 정보 생성

```http
POST /api/v1/residents/create/{user_id}
Content-Type: application/json

{
  "resident_number": "R-2024-001",
  "nickname": "Akaza",
  "admission_date": "2022-03-15",
  "room_number": "302",
  "floor_number": 3,
  "bed_number": "A",
  "adl_level": "partial_assistance",
  "mobility_level": "walker",
  "cognitive_level": "mild_impairment",
  ...
}
```

### 2. 입소자 정보 조회

```http
# 사용자 ID로 조회
GET /api/v1/residents/{user_id}

# 입소자 번호로 조회
GET /api/v1/residents/number/{resident_number}
```

### 3. 입소자 정보 수정

```http
PUT /api/v1/residents/{user_id}
Content-Type: application/json

{
  "room_number": "303",
  "adl_level": "full_assistance",
  ...
}
```

### 4. 입소자 정보 삭제

```http
DELETE /api/v1/residents/{user_id}
```

### 5. 입소자 목록 조회

```http
# 전체 목록 (페이지네이션)
GET /api/v1/residents/?page=1&size=10

# 현재 입소 중인 입소자만 조회
GET /api/v1/residents/current/list?page=1&size=10
```

### 6. 조건별 조회

```http
# 생활실별 조회
GET /api/v1/residents/room/{room_number}

# 층별 조회
GET /api/v1/residents/floor/{floor_number}

# ADL 수준별 조회
GET /api/v1/residents/adl/{adl_level}

# 키워드 검색
GET /api/v1/residents/search/{keyword}
```

### 7. 특수 기능

```http
# 퇴소 처리
POST /api/v1/residents/{user_id}/discharge?discharge_date=2024-12-31

# 사건/사고 기록 추가
POST /api/v1/residents/{user_id}/incidents
Content-Type: application/json

{
  "incident_date": "2024-01-15",
  "incident_type": "낙상",
  "location": "화장실",
  "severity": "경미",
  "description": "...",
  "action_taken": "...",
  "preventive_measures": "..."
}

# 복약 일정 업데이트
PUT /api/v1/residents/{user_id}/medication-schedule
Content-Type: application/json

{
  "schedule": {
    "morning": ["고혈압약", "당뇨약"],
    "noon": [],
    "evening": ["수면유도제"]
  },
  "notes": "식후 30분 복용"
}
```

---

## 데이터 확인 가이드

### 1. 데이터베이스 직접 확인 (PostgreSQL)

#### 서버 접속

```bash
# Docker 컨테이너 내부에서 PostgreSQL 접속
docker exec -it iot-care-postgres psql -U svc_dev -d your_database_name

# 또는 로컬에서 접속
psql -h localhost -U svc_dev -d your_database_name
```

#### 테이블 생성 확인

```sql
-- 테이블 존재 확인
\dt residents

-- 테이블 구조 확인
\d residents

-- 인덱스 확인
\di residents
```

#### 데이터 확인

```sql
-- 전체 입소자 조회
SELECT * FROM residents;

-- 특정 입소자 조회
SELECT * FROM residents WHERE user_id = '00000000-0000-0000-0000-000000000001';

-- 입소자 수 확인
SELECT COUNT(*) FROM residents;

-- 현재 입소 중인 입소자 조회
SELECT * FROM residents WHERE discharge_date IS NULL;

-- 생활실별 입소자 조회
SELECT * FROM residents WHERE room_number = '302';

-- users 테이블과 JOIN 조회
SELECT 
    u.user_name,
    u.user_role,
    r.resident_number,
    r.nickname,
    r.room_number,
    r.admission_date
FROM users u
LEFT JOIN residents r ON u.user_id = r.user_id
WHERE u.user_role = 'care_target';
```

### 2. 테이블 생성 및 데이터 삽입

#### 방법 1: SQL 파일 직접 실행

```bash
# PostgreSQL에 연결하여 SQL 파일 실행
psql -U svc_dev -d your_database_name -f maintenance/database/create_residents_table.sql
psql -U svc_dev -d your_database_name -f maintenance/database/insert_all_users_mock_data.sql
```

#### 방법 2: Docker 컨테이너 내부에서 실행

```bash
# SQL 파일을 컨테이너로 복사
docker cp maintenance/database/create_residents_table.sql iot-care-postgres:/tmp/
docker cp maintenance/database/insert_all_users_mock_data.sql iot-care-postgres:/tmp/

# 컨테이너 내부에서 실행
docker exec -i iot-care-postgres psql -U svc_dev -d your_database_name < /tmp/create_residents_table.sql
docker exec -i iot-care-postgres psql -U svc_dev -d your_database_name < /tmp/insert_all_users_mock_data.sql
```

#### 방법 3: Python 스크립트로 실행 (권장)

```python
# app/infrastructure/database.py의 create_tables() 함수가 자동으로 테이블을 생성합니다.
# FastAPI 애플리케이션이 시작될 때 자동으로 실행됩니다.

# 또는 수동으로 실행:
from app.infrastructure.database import create_tables
create_tables()
```

### 3. 데이터베이스 관리 도구 사용

#### pgAdmin

1. pgAdmin을 실행하고 서버에 연결
2. 데이터베이스 선택
3. `Schemas` > `public` > `Tables`에서 `residents` 테이블 확인
4. 우클릭 > `View/Edit Data` > `All Rows`로 데이터 확인

#### DBeaver

1. DBeaver를 실행하고 PostgreSQL 연결 설정
2. 데이터베이스 선택
3. `residents` 테이블을 찾아 데이터 확인

---

## API 테스트 가이드

### 1. 서버 실행 확인

```bash
# Docker Compose로 서버 실행
cd SERVER/iot-data-server
docker-compose up -d

# 서버 상태 확인
curl http://localhost:8000/docs
```

### 2. Swagger UI를 통한 API 테스트

1. 브라우저에서 `http://localhost:8000/docs` 접속
2. `residents` 태그를 찾아 API 엔드포인트 확인
3. 각 엔드포인트를 클릭하여 `Try it out` 버튼 클릭
4. 필요한 파라미터 입력 후 `Execute` 버튼 클릭

### 3. cURL을 통한 API 테스트

#### 입소자 정보 생성

```bash
curl -X POST "http://localhost:8000/api/v1/residents/create/00000000-0000-0000-0000-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "resident_number": "R-2024-001",
    "nickname": "Akaza",
    "admission_date": "2022-03-15",
    "room_number": "302",
    "floor_number": 3,
    "bed_number": "A",
    "adl_level": "partial_assistance",
    "mobility_level": "walker",
    "cognitive_level": "mild_impairment",
    "medication_schedule": {
      "morning": ["고혈압약", "당뇨약"],
      "noon": [],
      "evening": ["수면유도제"]
    },
    "medication_notes": "식후 30분 복용",
    "special_notes": {
      "health": {"blood_pressure": "고혈압 주의"},
      "emotional": {"anxiety": "야간 불안감"}
    },
    "care_level": "2등급",
    "guardian_name": "정기우",
    "guardian_relationship": "아들",
    "guardian_phone": "010-9911-2670"
  }'
```

#### 입소자 정보 조회

```bash
# 사용자 ID로 조회
curl "http://localhost:8000/api/v1/residents/00000000-0000-0000-0000-000000000001"

# 입소자 번호로 조회
curl "http://localhost:8000/api/v1/residents/number/R-2024-001"

# 전체 목록 조회
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"

# 현재 입소 중인 입소자 조회
curl "http://localhost:8000/api/v1/residents/current/list?page=1&size=10"

# 생활실별 조회
curl "http://localhost:8000/api/v1/residents/room/302"

# 층별 조회
curl "http://localhost:8000/api/v1/residents/floor/3"

# 키워드 검색
curl "http://localhost:8000/api/v1/residents/search/Akaza"
```

#### 입소자 정보 수정

```bash
curl -X PUT "http://localhost:8000/api/v1/residents/00000000-0000-0000-0000-000000000001" \
  -H "Content-Type: application/json" \
  -d '{
    "room_number": "303",
    "adl_level": "full_assistance"
  }'
```

#### 퇴소 처리

```bash
curl -X POST "http://localhost:8000/api/v1/residents/00000000-0000-0000-0000-000000000001/discharge?discharge_date=2024-12-31"
```

#### 사건/사고 기록 추가

```bash
curl -X POST "http://localhost:8000/api/v1/residents/00000000-0000-0000-0000-000000000001/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_date": "2024-01-15",
    "incident_type": "낙상",
    "location": "화장실",
    "severity": "경미",
    "description": "야간 화장실 이동 중 미끄러짐",
    "action_taken": "응급실 방문, X-ray 촬영, 골절 없음 확인",
    "preventive_measures": "화장실 바닥 미끄럼 방지 매트 설치"
  }'
```

### 4. Python을 통한 API 테스트

```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/residents"

# 입소자 정보 조회
response = requests.get(f"{BASE_URL}/00000000-0000-0000-0000-000000000001")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 전체 목록 조회
response = requests.get(f"{BASE_URL}/?page=1&size=10")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))

# 입소자 정보 수정
data = {
    "room_number": "303",
    "adl_level": "full_assistance"
}
response = requests.put(
    f"{BASE_URL}/00000000-0000-0000-0000-000000000001",
    json=data
)
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
```

### 5. Postman을 통한 API 테스트

1. Postman을 실행
2. 새 Collection 생성: "Residents API"
3. 각 엔드포인트에 대한 Request 추가
4. 환경 변수 설정:
   - `base_url`: `http://localhost:8000/api/v1/residents`
   - `user_id`: `00000000-0000-0000-0000-000000000001`
5. 각 Request를 실행하여 결과 확인

---

## 다음 단계

### 권장 사항

1. **테이블 생성 및 데이터 삽입**
   - `create_residents_table.sql` 실행하여 테이블 생성
   - `insert_all_users_mock_data.sql` 실행하여 목업 데이터 삽입

2. **API 테스트**
   - Swagger UI (`http://localhost:8000/docs`)를 통해 모든 엔드포인트 테스트
   - 실제 데이터로 CRUD 작업 테스트

3. **통합 테스트**
   - 다른 테이블(`users`, `user_profiles`, `user_relationships`)과의 JOIN 조회 테스트
   - 관계 데이터 일관성 확인

4. **문서화**
   - API 사용 예시 추가
   - 에러 처리 가이드 작성

5. **성능 최적화**
   - 인덱스 성능 확인
   - 쿼리 최적화

---

## 문제 해결

### 테이블이 생성되지 않는 경우

1. PostgreSQL 연결 확인
2. `create_residents_table.sql` 파일 경로 확인
3. 권한 확인 (`svc_dev` 사용자 권한)

### 데이터가 삽입되지 않는 경우

1. `users` 테이블에 해당 `user_id`가 존재하는지 확인
2. 외래 키 제약조건 확인
3. `ON CONFLICT` 처리 확인

### API가 동작하지 않는 경우

1. 서버가 실행 중인지 확인 (`docker-compose ps`)
2. 로그 확인 (`docker-compose logs app`)
3. 데이터베이스 연결 확인

---

## 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 공식 문서](https://docs.sqlalchemy.org/)
- [PostgreSQL 공식 문서](https://www.postgresql.org/docs/)

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

