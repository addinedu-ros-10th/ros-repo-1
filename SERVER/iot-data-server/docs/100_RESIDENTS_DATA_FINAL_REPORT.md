# 어르신 100명 데이터 생성 최종 리포트

**작성일**: 2024년  
**상태**: ✅ **데이터 생성 완료**

---

## ✅ 생성 완료

### 생성된 데이터 규모

| 테이블 | 생성 개수 | 설명 |
|--------|----------|------|
| **users** | 약 335개 | 100명 어르신 + 약 200명 가족 + 25명 직원 |
| **user_profiles** | 약 335개 | 모든 사용자 프로필 |
| **residents** | **100개** | 어르신 입소자 정보 |
| **user_relationships** | 약 459개 | 관계 정보 |

### 상세 내역

#### 어르신 (care_target) - 100명
- 실제 한국 이름 사용
- 1920년대 ~ 1955년대 출생 (70세 ~ 105세)
- 다양한 병력 및 상태 정보
- 실제 생활실 번호 체계
- 실제 입소일 패턴

#### 가족 (family) - 약 200명
- 각 어르신당 1-3명의 가족
- 관계 유형: 아들, 딸, 배우자, 손자, 손녀, 며느리, 사위
- 연령대에 맞는 관계 설정

#### 직원 (caregiver) - 25명
- 역할: 간호사, 사회복지사, 요양보호사, 물리치료사, 작업치료사
- 각 어르신당 1-2명의 담당 직원 배정

#### 관계 (user_relationships) - 약 459개
- caregiver 관계: 약 150개
- family 관계: 약 250개
- admin 관계: 100개

---

## 📊 데이터 특징

### 사실적인 데이터

1. **이름**: 실제 한국 이름 사용 (김, 이, 박 등)
2. **주소**: 서울특별시 실제 지역구 사용
3. **병력**: 실제 요양원에서 흔한 병력 (고혈압, 당뇨, 치매 등)
4. **생활실**: 실제 생활실 번호 체계 (1-5층, 각 층 1-30호)
5. **입소일**: 2018년부터 현재까지의 실제 날짜
6. **관계**: 실제 가족 관계 패턴

### 데이터 다양성

- **나이**: 70세 ~ 105세
- **성별**: 남성/여성 균형
- **ADL 수준**: independent, partial_assistance, full_assistance
- **이동 수준**: independent, walker, wheelchair, bedridden
- **인지 수준**: normal, mild_impairment, moderate_impairment, severe_impairment
- **병력**: 1-4개의 다양한 병력 조합

---

## 📝 생성된 파일

1. **SQL 파일**: `maintenance/database/insert_100_residents_realistic_data.sql` (350KB, 1271줄)
2. **생성 스크립트**: `maintenance/database/generate_realistic_residents_data.py` (28KB)

---

## 🚀 데이터 삽입 방법

### 방법 1: Python 스크립트 사용 (권장)

```bash
cd SERVER/iot-data-server
python3 scripts/execute_sql_file.py maintenance/database/insert_100_residents_realistic_data.sql
```

### 방법 2: psql로 직접 실행

```bash
psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d iot_care -f maintenance/database/insert_100_residents_realistic_data.sql
```

---

## ✅ 삽입 후 확인

### 데이터 개수 확인

```sql
-- users 테이블 역할별 개수
SELECT user_role, COUNT(*) 
FROM users 
GROUP BY user_role;

-- residents 테이블 개수
SELECT COUNT(*) FROM residents;

-- user_relationships 테이블 관계 유형별 개수
SELECT relationship_type, COUNT(*) 
FROM user_relationships 
GROUP BY relationship_type;
```

### 샘플 데이터 확인

```sql
-- 어르신 목록 (최근 입소자)
SELECT 
    r.resident_number,
    r.user_name,
    r.room_number,
    r.floor_number,
    r.admission_date
FROM residents r
ORDER BY r.admission_date DESC
LIMIT 10;
```

---

## 🎯 데이터 품질

### 사실성
- ✅ 실제 한국 이름 사용
- ✅ 실제 주소 형식
- ✅ 실제 병력 정보
- ✅ 실제 생활실 번호 체계
- ✅ 실제 입소일 패턴
- ✅ 실제 가족 관계 패턴

### 다양성
- ✅ 다양한 연령대
- ✅ 다양한 병력 조합
- ✅ 다양한 ADL 수준
- ✅ 다양한 이동 수준
- ✅ 다양한 인지 수준

### 완전성
- ✅ 모든 필수 필드 포함
- ✅ 관계 데이터 완전
- ✅ JSONB 필드 구조화
- ✅ 응급 연락처 포함

---

## 📚 관련 문서

- `docs/100_RESIDENTS_DATA_GENERATION_GUIDE.md` - 상세 가이드
- `docs/100_RESIDENTS_DATA_GENERATION_REPORT.md` - 생성 리포트

---

**작성자**: AI Assistant  
**작성일**: 2024년  
**상태**: ✅ **데이터 생성 완료, 삽입 대기 중**

