# 테이블 및 데이터 생성 현황 최종 리포트

**점검일**: 2024년  
**데이터베이스 연결**: ✅ 정상  
**점검 완료**: ✅ 완료

---

## 📊 점검 결과

### ✅ 데이터베이스 연결 상태
- **상태**: ✅ 정상
- **호스트**: 192.168.0.13:15432
- **데이터베이스**: iot_care
- **사용자**: svc_dev

### ✅ 테이블 존재 현황

| 테이블 | 상태 | 데이터 개수 | 비고 |
|--------|------|------------|------|
| `users` | ✅ 존재 | **275개** | 정상 |
| `user_profiles` | ✅ 존재 | **274개** | 정상 |
| `user_relationships` | ✅ 존재 | **511개** | 정상 |
| `residents` | ❌ **없음** | - | **생성 필요** |

### 📋 users 테이블 역할별 분포

| 역할 | 개수 | 비율 |
|------|------|------|
| `care_target` (입소자) | **101개** | 36.7% |
| `caregiver` (직원) | **30개** | 10.9% |
| `family` (면회객) | **121개** | 44.0% |
| `admin` (관리자) | **23개** | 8.4% |
| **합계** | **275개** | 100% |

### 📋 user_relationships 테이블 관계 유형별 분포

| 관계 유형 | 개수 | 설명 |
|----------|------|------|
| `caregiver` | **100개** | 직원 → 입소자 돌봄 관계 |
| `family` | **311개** | 가족 → 입소자 관계 |
| `admin` | **100개** | 관리자 → 입소자 관계 |
| **합계** | **511개** | |

---

## ❌ 발견된 문제

### 문제 1: `residents` 테이블이 없음

**현재 상태**:
- ❌ `residents` 테이블이 데이터베이스에 존재하지 않음
- ❌ `/api/v1/residents/*` API 엔드포인트가 모두 실패할 것으로 예상

**영향**:
- 입소자 상세 정보 관리 불가능
- 입소자 관련 API 모두 사용 불가

**해결 필요**: ✅ **즉시 조치 필요**

---

## ✅ API 정상화를 위한 필요한 조치

### 🔴 우선순위 1: `residents` 테이블 생성 (필수)

#### 방법 1: SQL 파일 직접 실행 (권장)

**가장 확실한 방법**:

```bash
# PostgreSQL에 직접 접속하여 SQL 파일 실행
cd SERVER/iot-data-server
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql
```

**실행 결과 확인**:
```sql
-- 테이블 생성 확인
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -c "\dt residents"

-- 또는
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'residents');"
```

#### 방법 2: 애플리케이션 재시작 (자동 생성)

**주의**: 현재 애플리케이션 시작 시 테이블 생성이 실패하고 있음

```bash
# Docker 컨테이너 재시작
docker-compose restart app

# 로그 확인
docker logs iot-care-app --tail 50 | grep -E "테이블|table|create"
```

**문제 해결 후**: 애플리케이션 재시작 시 자동으로 테이블 생성됨

---

### 🟡 우선순위 2: 목업 데이터 삽입 (선택사항)

**목적**: API 테스트를 위한 샘플 데이터

**현재 상태**:
- `users` 테이블에 `care_target` 역할 사용자 101명 존재
- 이 중 일부를 `residents` 테이블에 연결 가능

**데이터 삽입**:

```bash
# 통합 SQL 파일 실행
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql
```

**주의사항**:
- `ON CONFLICT DO NOTHING` 처리로 기존 데이터와 충돌 없음
- 기존 `users` 데이터는 유지됨
- `residents` 테이블에만 추가 데이터 삽입

**예상 결과**:
- `residents` 테이블에 4명의 입소자 정보 추가
- 기존 `users` 데이터와 연결됨

---

## 📋 단계별 실행 가이드

### Step 1: 테이블 생성 (필수)

```bash
cd SERVER/iot-data-server

# SQL 파일 실행
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql
```

**예상 출력**:
```
CREATE TABLE
CREATE INDEX
CREATE INDEX
...
COMMENT
```

### Step 2: 테이블 생성 확인

```bash
# 확인 스크립트 실행
python3 scripts/check_table_data_status.py

# 또는 직접 확인
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -c "\dt residents"
```

**예상 결과**:
```
✅ residents 테이블 존재
```

### Step 3: 데이터 삽입 (선택사항)

```bash
# 목업 데이터 삽입
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql
```

**예상 출력**:
```
INSERT 0 12
INSERT 0 12
INSERT 0 12
INSERT 0 4
```

### Step 4: 데이터 확인

```bash
# 확인 스크립트 재실행
python3 scripts/check_table_data_status.py

# 또는 직접 확인
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -c "SELECT COUNT(*) FROM residents;"
```

### Step 5: API 테스트

```bash
# 입소자 목록 조회
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"

# 특정 입소자 조회 (데이터가 있는 경우)
curl "http://localhost:8000/api/v1/residents/00000000-0000-0000-0000-000000000001"

# Swagger UI 접속
# 브라우저에서: http://localhost:8000/docs
```

---

## 🔍 상세 확인 쿼리

### 테이블 생성 확인

```sql
-- residents 테이블 존재 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'residents'
) AS residents_exists;

-- 결과가 true면 테이블 존재
```

### 테이블 구조 확인

```sql
-- residents 테이블 구조 확인
\d residents

-- 또는
SELECT 
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'residents'
ORDER BY ordinal_position;
```

### 데이터 확인

```sql
-- residents 테이블 데이터 개수
SELECT COUNT(*) FROM residents;

-- 입소자 목록 (users와 JOIN)
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

-- 현재 입소 중인 입소자 수
SELECT COUNT(*) 
FROM residents 
WHERE discharge_date IS NULL;
```

---

## 📊 예상 최종 상태

### 테이블 생성 후

```
✅ users 테이블 존재 (275개 데이터)
✅ user_profiles 테이블 존재 (274개 데이터)
✅ user_relationships 테이블 존재 (511개 데이터)
✅ residents 테이블 존재 (0개 또는 4개 데이터)
```

### 데이터 삽입 후

```
✅ users 테이블: 275개 (기존 유지)
✅ user_profiles 테이블: 274개 (기존 유지)
✅ user_relationships 테이블: 511개 (기존 유지)
✅ residents 테이블: 4개 (새로 추가)
```

### API 정상 작동 시

```json
// GET /api/v1/residents/?page=1&size=10
{
  "residents": [
    {
      "resident_number": "R-2024-001",
      "nickname": "Akaza",
      "room_number": "302",
      ...
    },
    ...
  ],
  "total": 4,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

---

## 🎯 작업 체크리스트

### 필수 작업

- [ ] **Step 1**: `residents` 테이블 생성
  ```bash
  psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql
  ```

- [ ] **Step 2**: 테이블 생성 확인
  ```bash
  python3 scripts/check_table_data_status.py
  ```

- [ ] **Step 3**: API 테스트
  ```bash
  curl "http://localhost:8000/api/v1/residents/?page=1&size=10"
  ```

### 선택 작업

- [ ] **Step 4**: 목업 데이터 삽입 (API 테스트용)
  ```bash
  psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql
  ```

- [ ] **Step 5**: 데이터 확인
  ```bash
  python3 scripts/check_table_data_status.py
  ```

---

## 💡 빠른 실행 명령어

### 한 번에 실행 (테이블 생성 + 데이터 삽입)

```bash
cd SERVER/iot-data-server

# 1. 테이블 생성
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql

# 2. 데이터 삽입
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql

# 3. 확인
python3 scripts/check_table_data_status.py

# 4. API 테스트
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"
```

---

## 📝 요약

### 현재 상태
- ✅ 데이터베이스 연결: 정상
- ✅ 기존 테이블: 모두 존재 (users, user_profiles, user_relationships)
- ✅ 기존 데이터: 충분히 존재 (users 275개, relationships 511개)
- ❌ **residents 테이블: 없음 (생성 필요)**

### 필요한 조치
1. **필수**: `residents` 테이블 생성
2. **선택**: 목업 데이터 삽입 (API 테스트용)

### 예상 소요 시간
- 테이블 생성: 약 1분
- 데이터 삽입: 약 1분
- 확인 및 테스트: 약 2분
- **총 예상 시간: 약 5분**

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

