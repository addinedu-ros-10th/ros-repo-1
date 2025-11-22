# 테이블 및 데이터 생성 현황 리포트

**작성일**: 2024년  
**프로젝트**: SERVER/iot-data-server  
**목적**: 테이블 및 데이터 생성 상태 확인 및 API 정상화 가이드

---

## 📋 목차

1. [현황 요약](#현황-요약)
2. [테이블 생성 상태](#테이블-생성-상태)
3. [데이터 생성 상태](#데이터-생성-상태)
4. [API 상태](#api-상태)
5. [필요한 조치](#필요한-조치)
6. [단계별 실행 가이드](#단계별-실행-가이드)

---

## 현황 요약

### ✅ 준비 완료된 항목

| 항목 | 상태 | 설명 |
|------|------|------|
| **테이블 생성 SQL** | ✅ 준비됨 | `create_residents_table.sql` 파일 존재 |
| **목업 데이터 SQL** | ✅ 준비됨 | `insert_all_users_mock_data.sql` 파일 존재 |
| **ORM 모델** | ✅ 완료 | `ResidentInfo` 모델 정의 완료 |
| **API 엔드포인트** | ✅ 완료 | `/api/v1/residents/*` 엔드포인트 구현 완료 |
| **의존성 주입** | ✅ 완료 | 서비스 및 리포지토리 등록 완료 |

### ❓ 확인 필요 항목

| 항목 | 상태 | 확인 방법 |
|------|------|----------|
| **residents 테이블 존재** | ❓ 미확인 | DB 직접 조회 필요 |
| **users 테이블 데이터** | ❓ 미확인 | DB 직접 조회 필요 |
| **user_profiles 테이블 데이터** | ❓ 미확인 | DB 직접 조회 필요 |
| **user_relationships 테이블 데이터** | ❓ 미확인 | DB 직접 조회 필요 |
| **residents 테이블 데이터** | ❓ 미확인 | DB 직접 조회 필요 |

---

## 테이블 생성 상태

### 1. 생성해야 할 테이블

#### `residents` 테이블
- **상태**: ❓ 미확인 (DB 직접 확인 필요)
- **SQL 파일**: `maintenance/database/create_residents_table.sql`
- **ORM 모델**: `app/infrastructure/models.py`의 `ResidentInfo` 클래스
- **자동 생성**: `app/main.py`의 `lifespan` 함수에서 `create_tables()` 호출 시 자동 생성

#### 기존 테이블 (확인 필요)
- `users` - 사용자 기본 정보
- `user_profiles` - 사용자 상세 프로필
- `user_relationships` - 사용자 간 관계

### 2. 테이블 생성 확인 방법

#### 방법 1: DB Tool로 직접 확인

```sql
-- 모든 테이블 목록 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- residents 테이블 존재 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'residents'
);

-- residents 테이블 구조 확인
\d residents
```

#### 방법 2: Python 스크립트로 확인

```python
from app.infrastructure.database import get_table_names, get_table_schema

# 모든 테이블 목록
tables = get_table_names()
print(f"테이블 목록: {tables}")

# residents 테이블 확인
if 'residents' in tables:
    schema = get_table_schema('residents')
    print(f"residents 테이블 구조: {schema}")
else:
    print("residents 테이블이 존재하지 않습니다.")
```

---

## 데이터 생성 상태

### 1. 생성해야 할 데이터

#### `users` 테이블 데이터
- **상태**: ❓ 미확인
- **예상 데이터**: 12명 (입소자 4명, 직원 4명, 면회객 4명)
- **SQL 파일**: `insert_all_users_mock_data.sql` (1단계)

#### `user_profiles` 테이블 데이터
- **상태**: ❓ 미확인
- **예상 데이터**: 12명의 프로필 정보
- **SQL 파일**: `insert_all_users_mock_data.sql` (2단계)

#### `user_relationships` 테이블 데이터
- **상태**: ❓ 미확인
- **예상 데이터**: 돌봄 관계, 가족 관계, 관리자 관계
- **SQL 파일**: `insert_all_users_mock_data.sql` (3단계)

#### `residents` 테이블 데이터
- **상태**: ❓ 미확인
- **예상 데이터**: 입소자 4명의 상세 정보
- **SQL 파일**: `insert_all_users_mock_data.sql` (4단계)

### 2. 데이터 확인 방법

#### 방법 1: DB Tool로 직접 확인

```sql
-- users 테이블 데이터 개수
SELECT COUNT(*) FROM users;
SELECT user_role, COUNT(*) FROM users GROUP BY user_role;

-- user_profiles 테이블 데이터 개수
SELECT COUNT(*) FROM user_profiles;

-- user_relationships 테이블 데이터 개수
SELECT relationship_type, COUNT(*) FROM user_relationships GROUP BY relationship_type;

-- residents 테이블 데이터 개수
SELECT COUNT(*) FROM residents;

-- residents 테이블 데이터 확인
SELECT 
    r.resident_number,
    r.nickname,
    r.room_number,
    u.user_name,
    u.user_role
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id;
```

#### 방법 2: API로 확인

```bash
# 입소자 목록 조회
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"

# 특정 입소자 조회
curl "http://localhost:8000/api/v1/residents/00000000-0000-0000-0000-000000000001"
```

---

## API 상태

### ✅ 구현 완료된 API 엔드포인트

| 엔드포인트 | HTTP 메서드 | 상태 | 설명 |
|-----------|-----------|------|------|
| `/api/v1/residents/create/{user_id}` | POST | ✅ 완료 | 입소자 정보 생성 |
| `/api/v1/residents/{user_id}` | GET | ✅ 완료 | 입소자 정보 조회 |
| `/api/v1/residents/number/{resident_number}` | GET | ✅ 완료 | 입소자 번호로 조회 |
| `/api/v1/residents/` | GET | ✅ 완료 | 전체 목록 조회 |
| `/api/v1/residents/current/list` | GET | ✅ 완료 | 현재 입소 중인 입소자 조회 |
| `/api/v1/residents/room/{room_number}` | GET | ✅ 완료 | 생활실별 조회 |
| `/api/v1/residents/floor/{floor_number}` | GET | ✅ 완료 | 층별 조회 |
| `/api/v1/residents/adl/{adl_level}` | GET | ✅ 완료 | ADL 수준별 조회 |
| `/api/v1/residents/search/{keyword}` | GET | ✅ 완료 | 키워드 검색 |
| `/api/v1/residents/{user_id}/discharge` | POST | ✅ 완료 | 퇴소 처리 |
| `/api/v1/residents/{user_id}/incidents` | POST | ✅ 완료 | 사건/사고 기록 추가 |
| `/api/v1/residents/{user_id}/medication-schedule` | PUT | ✅ 완료 | 복약 일정 업데이트 |

### ⚠️ API 정상화를 위한 전제 조건

1. **데이터베이스 연결 성공**
   - env 파일의 DB_HOST로 연결 가능하거나
   - `host.docker.internal`로 연결 가능해야 함

2. **테이블 생성 완료**
   - `residents` 테이블이 존재해야 함
   - `users`, `user_profiles`, `user_relationships` 테이블이 존재해야 함

3. **데이터 존재 (선택사항)**
   - 테스트를 위해 목업 데이터가 있으면 좋음
   - 없어도 API는 정상 작동 (빈 결과 반환)

---

## 필요한 조치

### 🔴 우선순위 1: 데이터베이스 연결 확인

**목표**: DB 연결이 정상적으로 이루어지는지 확인

**확인 방법**:
```bash
# Docker 컨테이너 로그 확인
docker logs iot-care-app --tail 50 | grep -E "데이터베이스|DB|연결"

# 연결 성공 메시지 확인
# 예상: "✅ 데이터베이스 연결 성공" 또는 "✅ host.docker.internal로 데이터베이스 연결 성공"
```

**문제 해결**:
- 연결 실패 시 `.env.local`의 `DB_HOST` 값 확인
- `host.docker.internal` fallback이 작동하는지 확인

---

### 🟡 우선순위 2: 테이블 생성 확인 및 실행

**목표**: `residents` 테이블이 존재하는지 확인하고, 없으면 생성

#### 방법 1: 자동 생성 (권장)

**동작**: FastAPI 애플리케이션 시작 시 `create_tables()` 함수가 자동으로 실행됨

**확인**:
```bash
# 애플리케이션 로그 확인
docker logs iot-care-app | grep -E "테이블|table|create"

# 예상 메시지: "✅ 데이터베이스 테이블 생성 완료"
```

**문제 해결**:
- 로그에 "❌ 데이터베이스 테이블 생성 실패"가 보이면 DB 연결 문제일 가능성 높음
- DB 연결 문제를 먼저 해결

#### 방법 2: SQL 파일 직접 실행

**사용 시나리오**: 자동 생성이 실패한 경우

**실행 방법**:

**옵션 A: psql로 직접 실행**
```bash
# PostgreSQL에 직접 접속하여 실행
psql -h <DB_HOST> -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql
```

**옵션 B: Docker 컨테이너 내부에서 실행**
```bash
# SQL 파일을 컨테이너로 복사
docker cp maintenance/database/create_residents_table.sql iot-care-app:/tmp/

# 컨테이너 내부에서 psql 실행 (DB에 직접 접속)
docker exec -it iot-care-app sh -c "psql -h \$DB_HOST -p \$DB_PORT -U \$DB_USER -d \$DB_NAME -f /tmp/create_residents_table.sql"
```

**옵션 C: Python 스크립트로 실행**
```python
# 컨테이너 내부에서 실행
from app.infrastructure.database import create_tables
create_tables()
```

---

### 🟢 우선순위 3: 데이터 삽입

**목표**: 목업 데이터를 삽입하여 API 테스트 가능하도록 함

#### 방법 1: 통합 SQL 파일 실행 (권장)

**파일**: `maintenance/database/insert_all_users_mock_data.sql`

**실행 방법**:

**옵션 A: psql로 직접 실행**
```bash
psql -h <DB_HOST> -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql
```

**옵션 B: Docker 컨테이너 내부에서 실행**
```bash
# SQL 파일을 컨테이너로 복사
docker cp maintenance/database/insert_all_users_mock_data.sql iot-care-app:/tmp/

# 컨테이너 내부에서 실행
docker exec -it iot-care-app sh -c "psql -h \$DB_HOST -p \$DB_PORT -U \$DB_USER -d \$DB_NAME -f /tmp/insert_all_users_mock_data.sql"
```

**주의사항**:
- `ON CONFLICT DO NOTHING` 또는 `ON CONFLICT DO UPDATE` 처리로 중복 실행 가능
- 기존 데이터가 있어도 안전하게 실행 가능

#### 방법 2: 단계별 실행

필요한 테이블만 선택적으로 데이터 삽입:

```sql
-- 1단계: users 테이블만
-- insert_all_users_mock_data.sql의 1단계 부분만 실행

-- 2단계: user_profiles 테이블만
-- insert_all_users_mock_data.sql의 2단계 부분만 실행

-- 3단계: user_relationships 테이블만
-- insert_all_users_mock_data.sql의 3단계 부분만 실행

-- 4단계: residents 테이블만
-- insert_all_users_mock_data.sql의 4단계 부분만 실행
```

---

### 🔵 우선순위 4: API 테스트

**목표**: API가 정상적으로 작동하는지 확인

#### 1. 서버 상태 확인

```bash
# 서버가 실행 중인지 확인
docker ps | grep iot-care-app

# 헬스체크
curl http://localhost:8000/health

# Swagger UI 접속
# 브라우저에서: http://localhost:8000/docs
```

#### 2. API 엔드포인트 테스트

```bash
# 입소자 목록 조회
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"

# 특정 입소자 조회 (데이터가 있는 경우)
curl "http://localhost:8000/api/v1/residents/00000000-0000-0000-0000-000000000001"

# 현재 입소 중인 입소자 조회
curl "http://localhost:8000/api/v1/residents/current/list?page=1&size=10"
```

---

## 단계별 실행 가이드

### 📋 체크리스트

#### 1단계: 환경 확인
- [ ] Docker 컨테이너가 실행 중인지 확인
- [ ] `.env.local` 파일의 DB 설정 확인
- [ ] DB 연결이 성공하는지 확인

#### 2단계: 테이블 생성
- [ ] `residents` 테이블이 존재하는지 확인
- [ ] 없으면 테이블 생성 (자동 또는 수동)

#### 3단계: 데이터 삽입
- [ ] `users` 테이블에 데이터가 있는지 확인
- [ ] `user_profiles` 테이블에 데이터가 있는지 확인
- [ ] `user_relationships` 테이블에 데이터가 있는지 확인
- [ ] `residents` 테이블에 데이터가 있는지 확인
- [ ] 없으면 목업 데이터 삽입

#### 4단계: API 테스트
- [ ] 서버가 정상 실행 중인지 확인
- [ ] Swagger UI 접속 확인
- [ ] API 엔드포인트 테스트

---

### 🚀 빠른 시작 가이드

#### 시나리오 1: 처음부터 시작 (테이블/데이터 모두 없음)

```bash
# 1. Docker 컨테이너 재시작 (테이블 자동 생성)
cd SERVER/iot-data-server
docker-compose down
docker-compose up -d

# 2. 로그 확인 (테이블 생성 확인)
docker logs iot-care-app --tail 50 | grep -E "테이블|table"

# 3. 데이터 삽입 (DB Tool 또는 psql 사용)
# 방법 A: DB Tool에서 SQL 파일 실행
# - maintenance/database/insert_all_users_mock_data.sql

# 방법 B: psql로 실행
psql -h <DB_HOST> -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql

# 4. API 테스트
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"
```

#### 시나리오 2: 테이블은 있지만 데이터가 없음

```bash
# 1. 데이터만 삽입
psql -h <DB_HOST> -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql

# 2. 데이터 확인
psql -h <DB_HOST> -p 15432 -U svc_dev -d iot_care -c "SELECT COUNT(*) FROM residents;"

# 3. API 테스트
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"
```

#### 시나리오 3: 모든 것이 준비된 상태 (확인만 필요)

```bash
# 1. 테이블 존재 확인
psql -h <DB_HOST> -p 15432 -U svc_dev -d iot_care -c "\dt residents"

# 2. 데이터 개수 확인
psql -h <DB_HOST> -p 15432 -U svc_dev -d iot_care -c "SELECT COUNT(*) FROM residents;"

# 3. API 테스트
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"
```

---

## 🔍 상태 확인 쿼리 모음

### 테이블 존재 확인

```sql
-- 모든 테이블 목록
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;

-- residents 테이블 존재 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'residents'
) AS residents_exists;
```

### 데이터 개수 확인

```sql
-- 각 테이블의 데이터 개수
SELECT 
    'users' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 
    'user_profiles', COUNT(*) FROM user_profiles
UNION ALL
SELECT 
    'user_relationships', COUNT(*) FROM user_relationships
UNION ALL
SELECT 
    'residents', COUNT(*) FROM residents;
```

### 역할별 사용자 수

```sql
SELECT user_role, COUNT(*) AS count
FROM users
GROUP BY user_role
ORDER BY user_role;
```

### 입소자 정보 확인

```sql
-- 입소자 기본 정보
SELECT 
    r.resident_number,
    r.nickname,
    r.room_number,
    r.floor_number,
    r.admission_date,
    u.user_name,
    u.user_role
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
ORDER BY r.room_number;
```

### 관계 정보 확인

```sql
-- 입소자별 담당 직원 수
SELECT 
    r.nickname AS resident_name,
    COUNT(ur.relationship_id) AS caregiver_count
FROM residents r
LEFT JOIN user_relationships ur ON r.user_id = ur.target_user_id
    AND ur.relationship_type = 'caregiver'
    AND ur.status = 'active'
GROUP BY r.nickname
ORDER BY r.nickname;
```

---

## 📊 예상 결과

### 테이블 생성 성공 시

```
✅ 데이터베이스 테이블 생성 완료
```

### 데이터 삽입 성공 시

```sql
-- 예상 결과
users: 12개
user_profiles: 12개
user_relationships: 12개 (caregiver 4개, family 4개, admin 4개)
residents: 4개
```

### API 정상 작동 시

```json
{
  "residents": [...],
  "total": 4,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

---

## 🐛 문제 해결

### 문제 1: 테이블이 생성되지 않음

**증상**: `relation "residents" does not exist`

**해결 방법**:
1. DB 연결 확인
2. `create_tables()` 함수가 실행되었는지 로그 확인
3. SQL 파일 직접 실행

### 문제 2: 데이터가 삽입되지 않음

**증상**: API 호출 시 빈 결과 반환

**해결 방법**:
1. `users` 테이블에 데이터가 있는지 확인
2. 외래 키 제약조건 확인
3. SQL 파일 직접 실행

### 문제 3: API가 500 에러 반환

**증상**: `Internal Server Error`

**해결 방법**:
1. 서버 로그 확인: `docker logs iot-care-app --tail 100`
2. DB 연결 상태 확인
3. 테이블 존재 확인

---

## 📝 다음 단계

1. **DB 연결 확인** → 연결 성공 확인
2. **테이블 생성** → `residents` 테이블 존재 확인
3. **데이터 삽입** → 목업 데이터 삽입
4. **API 테스트** → 모든 엔드포인트 정상 작동 확인

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

