# residents 테이블 업데이트 리포트

**작업일**: 2024년  
**작업 내용**: residents 테이블에 기본 정보 필드 추가 및 조인 쿼리 가이드

---

## ✅ 완료된 작업

### 1. 테이블 구조 업데이트
- ✅ `residents` 테이블에 기본 정보 필드 추가
  - `user_name`: 사용자 이름
  - `email`: 이메일 주소
  - `phone_number`: 전화번호
- ✅ 기존 데이터 업데이트 (users 테이블에서 정보 복사)
- ✅ 인덱스 추가 (검색 성능 향상)

### 2. 코드 업데이트
- ✅ ORM 모델 업데이트 (`app/infrastructure/models.py`)
- ✅ 도메인 엔티티 업데이트 (`app/domain/entities/resident_info.py`)
- ✅ 리포지토리 업데이트 (`app/infrastructure/repositories/resident_info_repository.py`)
- ✅ API 스키마 업데이트 (`app/api/v1/schemas.py`)

### 3. 문서 작성
- ✅ 조인 쿼리 가이드 작성 (`docs/JOIN_QUERIES_GUIDE.md`)

---

## 📊 업데이트된 테이블 구조

### residents 테이블 (업데이트 후)

```sql
CREATE TABLE residents (
    -- 기본 키
    user_id UUID PRIMARY KEY,
    
    -- 기본 정보 (새로 추가됨)
    user_name TEXT,           -- 사용자 이름
    email TEXT,               -- 이메일 주소
    phone_number TEXT,        -- 전화번호
    
    -- 입소 관리 정보
    resident_number VARCHAR(20),
    nickname VARCHAR(50),
    admission_date DATE NOT NULL,
    discharge_date DATE,
    
    -- 생활실 정보
    room_number VARCHAR(20),
    floor_number INTEGER,
    bed_number VARCHAR(10),
    
    -- ADL 수준
    adl_level VARCHAR(20),
    mobility_level VARCHAR(20),
    cognitive_level VARCHAR(20),
    
    -- 복약 관리
    medication_schedule JSONB,
    medication_notes TEXT,
    
    -- 특이사항
    special_notes JSONB,
    incidents JSONB,
    dietary_restrictions JSONB,
    emergency_contacts JSONB,
    insurance_info JSONB,
    medical_facility_info JSONB,
    
    -- 기타 관리 정보
    care_level VARCHAR(20),
    guardian_name VARCHAR(100),
    guardian_relationship VARCHAR(50),
    guardian_phone VARCHAR(20),
    
    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE
);
```

---

## 🔗 테이블 조인 방법

### 모든 테이블이 `user_id`를 기준으로 조인 가능

#### 1. residents ↔ users 조인

```sql
SELECT 
    r.*,
    u.user_role
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id;
```

**참고**: 이제 `residents` 테이블에 기본 정보가 있어 조인 없이도 조회 가능합니다.

#### 2. residents ↔ user_profiles 조인

```sql
SELECT 
    r.*,
    up.date_of_birth,
    up.gender,
    up.medical_history
FROM residents r
INNER JOIN user_profiles up ON r.user_id = up.user_id;
```

#### 3. residents ↔ user_relationships 조인 (N:N)

```sql
-- 입소자와 담당 직원 관계 조회
SELECT 
    r.user_name AS resident_name,
    r.room_number,
    u_caregiver.user_name AS caregiver_name,
    ur.relationship_type
FROM residents r
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_caregiver ON ur.subject_user_id = u_caregiver.user_id
WHERE ur.relationship_type = 'caregiver'
  AND ur.status = 'active';
```

#### 4. 전체 테이블 통합 조인

```sql
-- 모든 테이블을 한 번에 조인
SELECT 
    r.*,
    u.user_role,
    up.date_of_birth,
    up.gender,
    up.medical_history
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
LEFT JOIN user_profiles up ON r.user_id = up.user_id;
```

---

## 📝 N:N 조인 예시

### 입소자별 담당 직원 목록

```sql
SELECT 
    r.user_name AS resident_name,
    r.room_number,
    array_agg(u_caregiver.user_name) AS caregiver_names
FROM residents r
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_caregiver ON ur.subject_user_id = u_caregiver.user_id
WHERE ur.relationship_type = 'caregiver'
  AND ur.status = 'active'
GROUP BY r.user_name, r.room_number;
```

### 입소자별 가족 목록

```sql
SELECT 
    r.user_name AS resident_name,
    r.room_number,
    json_agg(
        json_build_object(
            'name', u_family.user_name,
            'phone', u_family.phone_number
        )
    ) AS family_members
FROM residents r
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_family ON ur.subject_user_id = u_family.user_id
WHERE ur.relationship_type = 'family'
  AND ur.status = 'active'
GROUP BY r.user_name, r.room_number;
```

---

## ✅ 검증 결과

### 데이터 확인

```
📊 샘플 데이터:
   user_id: 00000000-0000-0000-0000-000000000001
   user_name: 정도현
   email: jdohyun@example.com
   phone_number: 010-3210-4801
   resident_number: R-2024-001
   nickname: Akaza
   room_number: 302
```

**결과**: ✅ 기본 정보가 정상적으로 저장되어 있음

---

## 🎯 주요 변경 사항 요약

| 항목 | 변경 전 | 변경 후 |
|------|--------|---------|
| **기본 정보** | users 테이블 조인 필요 | residents 테이블에 직접 포함 |
| **조회 성능** | 조인 필요 | 조인 없이 조회 가능 |
| **코드 복잡도** | 조인 로직 필요 | 단순 조회 가능 |
| **조인 가능성** | 가능 | 가능 (더 유연함) |

---

## 📚 생성된 파일

1. `maintenance/database/update_residents_table_add_basic_info.sql` - 테이블 업데이트 SQL
2. `docs/JOIN_QUERIES_GUIDE.md` - 조인 쿼리 가이드
3. `docs/RESIDENTS_TABLE_UPDATE_REPORT.md` - 업데이트 리포트 (본 문서)

---

## 🔍 다음 단계

1. ✅ 테이블 구조 업데이트 완료
2. ✅ 코드 업데이트 완료
3. ✅ 데이터 업데이트 완료
4. ⏳ API 테스트 (선택사항)

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

