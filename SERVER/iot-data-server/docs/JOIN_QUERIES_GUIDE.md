# 테이블 조인 쿼리 가이드

**작성일**: 2024년  
**목적**: residents, users, user_profiles, user_relationships 테이블 간 조인 쿼리 방법

---

## 📊 테이블 관계도

```
users (1) ──< (1) user_profiles
users (1) ──< (1) residents
users (1) ──< (*) user_relationships (subject_user_id)
users (1) ──< (*) user_relationships (target_user_id)
```

**공통 키**: 모든 테이블이 `user_id`를 기준으로 조인 가능

---

## 🔗 기본 조인 방법

### 1. residents + users 조인

```sql
-- 입소자 정보와 사용자 기본 정보 함께 조회
SELECT 
    r.*,
    u.user_name,
    u.user_role,
    u.email,
    u.phone_number
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
WHERE r.user_id = '00000000-0000-0000-0000-000000000001';
```

**참고**: 이제 `residents` 테이블에 `user_name`, `email`, `phone_number`가 있으므로 조인 없이도 조회 가능합니다.

---

### 2. residents + user_profiles 조인

```sql
-- 입소자 정보와 프로필 정보 함께 조회
SELECT 
    r.*,
    up.date_of_birth,
    up.gender,
    up.address,
    up.address_detail,
    up.medical_history,
    up.significant_notes,
    up.current_status
FROM residents r
INNER JOIN user_profiles up ON r.user_id = up.user_id
WHERE r.user_id = '00000000-0000-0000-0000-000000000001';
```

---

### 3. residents + user_relationships 조인 (N:N)

#### 입소자와 담당 직원 관계 조회

```sql
-- 입소자와 담당 직원(caregiver) 관계 조회
SELECT 
    r.resident_number,
    r.user_name AS resident_name,
    r.room_number,
    u_caregiver.user_name AS caregiver_name,
    u_caregiver.email AS caregiver_email,
    u_caregiver.phone_number AS caregiver_phone,
    ur.relationship_type,
    ur.status AS relationship_status,
    ur.created_at AS relationship_created_at
FROM residents r
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_caregiver ON ur.subject_user_id = u_caregiver.user_id
WHERE ur.relationship_type = 'caregiver'
  AND ur.status = 'active'
  AND r.discharge_date IS NULL
ORDER BY r.room_number;
```

#### 입소자와 가족 관계 조회

```sql
-- 입소자와 가족(family) 관계 조회
SELECT 
    r.resident_number,
    r.user_name AS resident_name,
    r.room_number,
    u_family.user_name AS family_name,
    u_family.email AS family_email,
    u_family.phone_number AS family_phone,
    ur.relationship_type,
    ur.status AS relationship_status
FROM residents r
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_family ON ur.subject_user_id = u_family.user_id
WHERE ur.relationship_type = 'family'
  AND ur.status = 'active'
  AND r.discharge_date IS NULL
ORDER BY r.room_number;
```

---

### 4. 전체 정보 통합 조회 (모든 테이블 조인)

```sql
-- 입소자의 모든 정보를 한 번에 조회
SELECT 
    -- residents 테이블 (기본 정보 포함)
    r.user_id,
    r.user_name,
    r.email,
    r.phone_number,
    r.resident_number,
    r.nickname,
    r.room_number,
    r.floor_number,
    r.admission_date,
    r.discharge_date,
    r.adl_level,
    r.mobility_level,
    r.cognitive_level,
    r.care_level,
    r.guardian_name,
    r.guardian_relationship,
    r.guardian_phone,
    
    -- user_profiles 테이블
    up.date_of_birth,
    up.gender,
    up.address,
    up.address_detail,
    up.medical_history,
    up.significant_notes,
    up.current_status,
    
    -- users 테이블 (추가 정보)
    u.user_role,
    u.created_at AS user_created_at
    
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
LEFT JOIN user_profiles up ON r.user_id = up.user_id
WHERE r.user_id = '00000000-0000-0000-0000-000000000001';
```

---

## 🔄 N:N 조인 예시

### 입소자별 담당 직원 목록 조회

```sql
-- 각 입소자별로 담당 직원 목록 조회
SELECT 
    r.resident_number,
    r.user_name AS resident_name,
    r.room_number,
    array_agg(u_caregiver.user_name) AS caregiver_names,
    array_agg(u_caregiver.phone_number) AS caregiver_phones
FROM residents r
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_caregiver ON ur.subject_user_id = u_caregiver.user_id
WHERE ur.relationship_type = 'caregiver'
  AND ur.status = 'active'
  AND r.discharge_date IS NULL
GROUP BY r.resident_number, r.user_name, r.room_number
ORDER BY r.room_number;
```

### 입소자별 가족 목록 조회

```sql
-- 각 입소자별로 가족 목록 조회
SELECT 
    r.resident_number,
    r.user_name AS resident_name,
    r.room_number,
    json_agg(
        json_build_object(
            'name', u_family.user_name,
            'phone', u_family.phone_number,
            'email', u_family.email,
            'relationship_status', ur.status
        )
    ) AS family_members
FROM residents r
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_family ON ur.subject_user_id = u_family.user_id
WHERE ur.relationship_type = 'family'
  AND ur.status = 'active'
  AND r.discharge_date IS NULL
GROUP BY r.resident_number, r.user_name, r.room_number
ORDER BY r.room_number;
```

---

## 🔍 복잡한 조인 쿼리 예시

### 입소자 + 프로필 + 담당 직원 + 가족 통합 조회

```sql
-- 입소자의 모든 정보와 관계 정보를 한 번에 조회
WITH resident_info AS (
    SELECT 
        r.*,
        up.date_of_birth,
        up.gender,
        up.medical_history
    FROM residents r
    LEFT JOIN user_profiles up ON r.user_id = up.user_id
    WHERE r.discharge_date IS NULL
),
caregivers AS (
    SELECT 
        ur.target_user_id,
        json_agg(
            json_build_object(
                'name', u.user_name,
                'phone', u.phone_number,
                'email', u.email
            )
        ) AS caregiver_list
    FROM user_relationships ur
    INNER JOIN users u ON ur.subject_user_id = u.user_id
    WHERE ur.relationship_type = 'caregiver'
      AND ur.status = 'active'
    GROUP BY ur.target_user_id
),
families AS (
    SELECT 
        ur.target_user_id,
        json_agg(
            json_build_object(
                'name', u.user_name,
                'phone', u.phone_number,
                'email', u.email
            )
        ) AS family_list
    FROM user_relationships ur
    INNER JOIN users u ON ur.subject_user_id = u.user_id
    WHERE ur.relationship_type = 'family'
      AND ur.status = 'active'
    GROUP BY ur.target_user_id
)
SELECT 
    ri.*,
    c.caregiver_list,
    f.family_list
FROM resident_info ri
LEFT JOIN caregivers c ON ri.user_id = c.target_user_id
LEFT JOIN families f ON ri.user_id = f.target_user_id
ORDER BY ri.room_number;
```

---

## 📝 Python/SQLAlchemy 조인 예시

### SQLAlchemy ORM을 사용한 조인

```python
from sqlalchemy.orm import joinedload
from app.infrastructure.models import ResidentInfo, User, UserProfile, UserRelationship

# 입소자 정보와 사용자 정보 함께 조회
resident = session.query(ResidentInfo)\
    .options(joinedload(ResidentInfo.user))\
    .filter(ResidentInfo.user_id == user_id)\
    .first()

# 입소자 정보와 프로필 정보 함께 조회
resident = session.query(ResidentInfo)\
    .join(User)\
    .join(UserProfile)\
    .filter(ResidentInfo.user_id == user_id)\
    .first()

# 입소자와 담당 직원 관계 조회
relationships = session.query(UserRelationship)\
    .join(User, UserRelationship.subject_user_id == User.user_id)\
    .filter(UserRelationship.target_user_id == resident_user_id)\
    .filter(UserRelationship.relationship_type == 'caregiver')\
    .filter(UserRelationship.status == 'active')\
    .all()
```

---

## ✅ 조인 가능성 요약

| 조인 조합 | 가능 여부 | 방법 |
|----------|----------|------|
| residents ↔ users | ✅ 가능 | `r.user_id = u.user_id` |
| residents ↔ user_profiles | ✅ 가능 | `r.user_id = up.user_id` |
| residents ↔ user_relationships | ✅ 가능 (N:N) | `r.user_id = ur.target_user_id` 또는 `r.user_id = ur.subject_user_id` |
| users ↔ user_profiles | ✅ 가능 | `u.user_id = up.user_id` |
| users ↔ user_relationships | ✅ 가능 (N:N) | `u.user_id = ur.subject_user_id` 또는 `u.user_id = ur.target_user_id` |
| user_profiles ↔ user_relationships | ✅ 가능 | `up.user_id = ur.subject_user_id` 또는 `up.user_id = ur.target_user_id` |

---

## 🎯 주요 포인트

1. **공통 키**: 모든 테이블이 `user_id`를 기준으로 조인 가능
2. **N:N 관계**: `user_relationships` 테이블을 통해 N:N 조인 가능
3. **기본 정보 중복**: `residents` 테이블에 기본 정보가 있어 조인 없이도 조회 가능
4. **유연한 조인**: 필요에 따라 여러 테이블을 자유롭게 조인 가능

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

