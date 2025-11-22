# 어르신 100명 데이터 생성 가이드

**작성일**: 2024년  
**목적**: 사실적인 어르신 데이터 100명 및 관계자 데이터 생성 및 삽입

---

## 📋 생성된 데이터 규모

### 전체 데이터

| 테이블 | 생성 개수 | 설명 |
|--------|----------|------|
| **users** | 335개 | 100명 어르신 + 약 200명 가족 + 25명 직원 |
| **user_profiles** | 335개 | 모든 사용자 프로필 |
| **residents** | 100개 | 어르신 입소자 정보 |
| **user_relationships** | 459개 | 관계 정보 |

### 상세 내역

#### 어르신 (care_target)
- **100명**의 어르신
- 실제 한국 이름 사용
- 1920년대 ~ 1955년대 출생 (70세 ~ 105세)
- 다양한 병력 및 상태 정보

#### 가족 (family)
- **약 200명**의 가족 구성원
- 각 어르신당 1-3명의 가족
- 관계 유형: 아들, 딸, 배우자, 손자, 손녀, 며느리, 사위

#### 직원 (caregiver)
- **25명**의 직원
- 역할: 간호사, 사회복지사, 요양보호사, 물리치료사, 작업치료사
- 각 어르신당 1-2명의 담당 직원 배정

#### 관계 (user_relationships)
- **459개**의 관계
  - caregiver 관계: 약 150개
  - family 관계: 약 250개
  - admin 관계: 100개

---

## 🚀 데이터 삽입 방법

### 방법 1: Python 스크립트 사용

```bash
cd SERVER/iot-data-server
python3 scripts/execute_sql_file.py maintenance/database/insert_100_residents_realistic_data.sql
```

### 방법 2: psql로 직접 실행

```bash
cd SERVER/iot-data-server
psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d iot_care -f maintenance/database/insert_100_residents_realistic_data.sql
```

### 방법 3: SQL 파일 내용 복사하여 실행

1. `maintenance/database/insert_100_residents_realistic_data.sql` 파일 열기
2. 내용을 복사하여 PostgreSQL 클라이언트에서 실행

---

## 📊 데이터 특징

### 사실적인 데이터

1. **이름**
   - 실제 한국 이름 사용
   - 다양한 성씨 (김, 이, 박, 최 등)
   - 실제 사용되는 이름 조합

2. **주소**
   - 서울특별시 실제 지역구 사용
   - 실제 주소 형식

3. **병력**
   - 실제 요양원에서 흔한 병력
   - 고혈압, 당뇨, 치매, 관절염 등
   - 1-4개의 병력 조합

4. **생활실**
   - 실제 생활실 번호 체계
   - 1-5층, 각 층 1-30호
   - 침대 번호: A, B, C

5. **입소일**
   - 2018년부터 현재까지의 실제 날짜
   - 다양한 입소 시기

6. **관계**
   - 실제 가족 관계 패턴
   - 아들, 딸, 배우자, 손자, 손녀 등
   - 연령대에 맞는 관계 설정

### 데이터 다양성

- **나이**: 70세 ~ 105세
- **성별**: 남성/여성 균형
- **ADL 수준**: independent, partial_assistance, full_assistance
- **이동 수준**: independent, walker, wheelchair, bedridden
- **인지 수준**: normal, mild_impairment, moderate_impairment, severe_impairment
- **병력**: 다양한 조합

---

## 🔍 데이터 예시

### 어르신 예시
```json
{
  "user_name": "김기준",
  "resident_number": "R-2023-001",
  "room_number": "302",
  "floor_number": 3,
  "adl_level": "partial_assistance",
  "mobility_level": "walker",
  "medical_history": "고혈압, 당뇨병, 관절염"
}
```

### 가족 예시
```json
{
  "user_name": "김민수",
  "relationship": "아들",
  "phone_number": "010-XXXX-XXXX"
}
```

### 직원 예시
```json
{
  "user_name": "박미영",
  "role": "간호사",
  "phone_number": "010-XXXX-XXXX"
}
```

---

## ✅ 삽입 후 확인

### 데이터 개수 확인

```sql
-- users 테이블
SELECT user_role, COUNT(*) 
FROM users 
GROUP BY user_role;

-- residents 테이블
SELECT COUNT(*) FROM residents;

-- user_relationships 테이블
SELECT relationship_type, COUNT(*) 
FROM user_relationships 
GROUP BY relationship_type;
```

### 샘플 데이터 확인

```sql
-- 어르신 목록
SELECT 
    r.resident_number,
    r.user_name,
    r.room_number,
    u.user_role
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
LIMIT 10;
```

---

## 📝 생성된 파일

1. `maintenance/database/insert_100_residents_realistic_data.sql` - SQL 삽입 스크립트
2. `maintenance/database/generate_realistic_residents_data.py` - 데이터 생성 Python 스크립트

---

## 🔄 데이터 재생성

데이터를 다시 생성하려면:

```bash
cd SERVER/iot-data-server
python3 maintenance/database/generate_realistic_residents_data.py
```

이렇게 하면 새로운 SQL 파일이 생성됩니다.

---

**작성자**: AI Assistant  
**작성일**: 2024년

