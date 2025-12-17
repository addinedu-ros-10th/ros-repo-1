# 테이블 및 데이터 생성 상태 점검 리포트

**점검일**: 2024년  
**점검 결과**: 데이터베이스 연결 정상, 테이블 및 데이터 상태 확인 완료

---

## 📊 점검 결과 요약

### ✅ 데이터베이스 연결
- **상태**: ✅ 정상
- **호스트**: 192.168.0.13:15432
- **데이터베이스**: iot_care
- **사용자**: svc_dev

### ✅ 테이블 존재 상태

| 테이블 | 상태 | 설명 |
|--------|------|------|
| `users` | ✅ 존재 | 사용자 기본 정보 테이블 |
| `user_profiles` | ✅ 존재 | 사용자 상세 프로필 테이블 |
| `user_relationships` | ✅ 존재 | 사용자 간 관계 테이블 |
| `residents` | ❌ **없음** | **입소자 관리 정보 테이블 (생성 필요)** |

### 📊 데이터 개수 현황

| 테이블 | 데이터 개수 | 상태 |
|--------|------------|------|
| `users` | **275개** | ✅ 데이터 존재 |
| `user_profiles` | **274개** | ✅ 데이터 존재 |
| `user_relationships` | **511개** | ✅ 데이터 존재 |
| `residents` | **테이블 없음** | ❌ 테이블 생성 필요 |

### 📋 users 테이블 역할별 분포

| 역할 | 개수 | 설명 |
|------|------|------|
| `care_target` | **101개** | 입소자 |
| `caregiver` | **30개** | 직원 |
| `family` | **121개** | 면회객/가족 |
| `admin` | **23개** | 관리자 |
| **합계** | **275개** | |

### 📋 user_relationships 테이블 관계 유형별 분포

| 관계 유형 | 개수 | 설명 |
|----------|------|------|
| `caregiver` | **100개** | 직원 → 입소자 돌봄 관계 |
| `family` | **311개** | 가족 → 입소자 관계 |
| `admin` | **100개** | 관리자 → 입소자 관계 |
| **합계** | **511개** | |

---

## ❌ 발견된 문제

### 1. `residents` 테이블이 없음

**영향**:
- `/api/v1/residents/*` API 엔드포인트가 모두 실패
- 입소자 상세 정보 관리 불가능

**해결 필요**: 테이블 생성 필요

---

## ✅ 필요한 조치

### 🔴 우선순위 1: `residents` 테이블 생성

#### 방법 1: 자동 생성 (권장)

**동작**: FastAPI 애플리케이션 재시작 시 자동 생성

```bash
# Docker 컨테이너 재시작
cd SERVER/iot-data-server
docker-compose restart app

# 로그 확인
docker logs iot-care-app --tail 50 | grep -E "테이블|table|create"

# 예상 메시지: "✅ 데이터베이스 테이블 생성 완료"
```

**확인**:
```bash
# 컨테이너 내부에서 확인
docker exec -it iot-care-app python3 -c "
from app.infrastructure.database import get_table_names
tables = get_table_names()
if 'residents' in tables:
    print('✅ residents 테이블 생성 완료')
else:
    print('❌ residents 테이블이 없습니다')
"
```

#### 방법 2: SQL 파일 직접 실행

**사용 시나리오**: 자동 생성이 실패한 경우

```bash
# PostgreSQL에 직접 접속하여 실행
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql
```

**또는 Docker 컨테이너 내부에서**:
```bash
# SQL 파일을 컨테이너로 복사
docker cp maintenance/database/create_residents_table.sql iot-care-app:/tmp/

# 컨테이너 내부에서 실행
docker exec -it iot-care-app sh -c "psql -h \$DB_HOST -p \$DB_PORT -U \$DB_USER -d \$DB_NAME -f /tmp/create_residents_table.sql"
```

---

### 🟡 우선순위 2: `residents` 테이블에 데이터 삽입 (선택사항)

**현재 상태**: 
- `users` 테이블에 `care_target` 역할 사용자 101명 존재
- 이 중 일부를 `residents` 테이블에 연결 가능

**목업 데이터 삽입**:

```bash
# 통합 SQL 파일 실행 (모든 테이블 데이터 포함)
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql
```

**주의사항**:
- `ON CONFLICT DO NOTHING` 처리로 기존 데이터와 충돌 없음
- 기존 `users` 데이터는 유지되고, `residents` 테이블에만 추가 데이터 삽입

---

## 📋 단계별 실행 가이드

### Step 1: 테이블 생성 확인

```bash
# 방법 1: Python 스크립트로 확인
cd SERVER/iot-data-server
python3 scripts/check_table_data_status.py

# 방법 2: 직접 SQL 실행
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -c "\dt residents"
```

### Step 2: 테이블 생성 (없는 경우)

```bash
# 방법 1: 애플리케이션 재시작 (자동 생성)
docker-compose restart app

# 방법 2: SQL 파일 직접 실행
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql
```

### Step 3: 테이블 생성 확인

```bash
# 확인 스크립트 재실행
python3 scripts/check_table_data_status.py

# 또는 직접 확인
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'residents');"
```

### Step 4: 데이터 삽입 (선택사항)

```bash
# 목업 데이터 삽입
psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql
```

### Step 5: API 테스트

```bash
# 입소자 목록 조회
curl "http://localhost:8000/api/v1/residents/?page=1&size=10"

# Swagger UI 접속
# 브라우저에서: http://localhost:8000/docs
```

---

## 🔍 상세 확인 쿼리

### 테이블 존재 확인

```sql
-- residents 테이블 존재 확인
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'residents'
) AS residents_exists;
```

### 테이블 구조 확인 (생성 후)

```sql
-- residents 테이블 구조 확인
\d residents

-- 또는
SELECT 
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'residents'
ORDER BY ordinal_position;
```

### 데이터 확인 (삽입 후)

```sql
-- residents 테이블 데이터 개수
SELECT COUNT(*) FROM residents;

-- 입소자 목록
SELECT 
    r.resident_number,
    r.nickname,
    r.room_number,
    u.user_name
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
ORDER BY r.room_number;
```

---

## 📊 예상 결과

### 테이블 생성 성공 시

```
✅ residents 테이블이 존재합니다!
```

### 데이터 삽입 성공 시

```
residents: 4개 (또는 더 많은 데이터)
```

### API 정상 작동 시

```json
{
  "residents": [...]]],
  "total": 4,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

---

## 🎯 다음 단계 요약

1. ✅ **데이터베이스 연결**: 정상
2. ✅ **기존 테이블**: 모두 존재 (users, user_profiles, user_relationships)
3. ❌ **residents 테이블**: 생성 필요
4. ⏳ **데이터 삽입**: 테이블 생성 후 선택적으로 실행
5. ⏳ **API 테스트**: 테이블 생성 후 테스트

---

## 💡 권장 작업 순서

1. **테이블 생성** (필수)
   ```bash
   docker-compose restart app
   # 또는
   psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/create_residents_table.sql
   ```

2. **생성 확인** (필수)
   ```bash
   python3 scripts/check_table_data_status.py
   ```

3. **데이터 삽입** (선택)
   ```bash
   psql -h 192.168.0.13 -p 15432 -U svc_dev -d iot_care -f maintenance/database/insert_all_users_mock_data.sql
   ```

4. **API 테스트** (검증)
   ```bash
   curl "http://localhost:8000/api/v1/residents/?page=1&size=10"
   ```

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

