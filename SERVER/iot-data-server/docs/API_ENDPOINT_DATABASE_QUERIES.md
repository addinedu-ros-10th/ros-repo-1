# 주요 API 엔드포인트 데이터베이스 조회 가이드

**작성일**: 2024년  
**목적**: DB Tool로 직접 데이터를 조회하기 위한 SQL 쿼리 가이드

---

## 📋 목차

1. [API 엔드포인트별 조회 테이블](#api-엔드포인트별-조회-테이블)
2. [기본 조회 쿼리](#기본-조회-쿼리)
3. [JOIN 조회 쿼리](#join-조회-쿼리)
4. [조건별 조회 쿼리](#조건별-조회-쿼리)
5. [통계 조회 쿼리](#통계-조회-쿼리)

---

## API 엔드포인트별 조회 테이블

### 1. `/api/v1/residents/*` - 입소자 관리 API

**조회 테이블**: `residents`

| API 엔드포인트 | HTTP 메서드 | 조회 테이블 | 주요 조건 |
|--------------|-----------|-----------|---------|
| `/residents/{user_id}` | GET | `residents` | `user_id = ?` |
| `/residents/number/{resident_number}` | GET | `residents` | `resident_number = ?` |
| `/residents/` | GET | `residents` | 전체 조회 (페이지네이션) |
| `/residents/current/list` | GET | `residents` | `discharge_date IS NULL` |
| `/residents/room/{room_number}` | GET | `residents` | `room_number = ? AND discharge_date IS NULL` |
| `/residents/floor/{floor_number}` | GET | `residents` | `floor_number = ? AND discharge_date IS NULL` |
| `/residents/adl/{adl_level}` | GET | `residents` | `adl_level = ? AND discharge_date IS NULL` |
| `/residents/search/{keyword}` | GET | `residents` | 키워드 검색 (LIKE) |

---

### 2. `/api/v1/users/*` - 사용자 관리 API

**조회 테이블**: `users`

| API 엔드포인트 | HTTP 메서드 | 조회 테이블 | 주요 조건 |
|--------------|-----------|-----------|---------|
| `/users/{user_id}` | GET | `users` | `user_id = ?` |
| `/users/list` | GET | `users` | 전체 조회 (페이지네이션, 역할 필터) |

---

### 3. `/api/v1/user-profiles/*` - 사용자 프로필 API

**조회 테이블**: `user_profiles`

| API 엔드포인트 | HTTP 메서드 | 조회 테이블 | 주요 조건 |
|--------------|-----------|-----------|---------|
| `/user-profiles/{user_id}` | GET | `user_profiles` | `user_id = ?` |
| `/user-profiles/list` | GET | `user_profiles` | 전체 조회 (페이지네이션) |

---

### 4. `/api/v1/user-relationships/*` - 사용자 관계 API

**조회 테이블**: `user_relationships`

| API 엔드포인트 | HTTP 메서드 | 조회 테이블 | 주요 조건 |
|--------------|-----------|-----------|---------|
| `/user-relationships/{relationship_id}` | GET | `user_relationships` | `relationship_id = ?` |
| `/user-relationships/user/{user_id}/as-subject` | GET | `user_relationships` | `subject_user_id = ?` |
| `/user-relationships/user/{user_id}/as-target` | GET | `user_relationships` | `target_user_id = ?` |
| `/user-relationships/list` | GET | `user_relationships` | 전체 조회 (페이지네이션) |

---

## 기본 조회 쿼리

### 1. 입소자 정보 조회

#### 사용자 ID로 입소자 정보 조회
```sql
-- GET /api/v1/residents/{user_id}
SELECT * 
FROM residents 
WHERE user_id = '00000000-0000-0000-0000-000000000001';
```

#### 입소자 번호로 조회
```sql
-- GET /api/v1/residents/number/{resident_number}
SELECT * 
FROM residents 
WHERE resident_number = 'R-2024-001';
```

#### 전체 입소자 목록 조회 (페이지네이션)
```sql
-- GET /api/v1/residents/?page=1&size=10
SELECT * 
FROM residents 
ORDER BY admission_date DESC 
LIMIT 10 OFFSET 0;
```

#### 현재 입소 중인 입소자만 조회
```sql
-- GET /api/v1/residents/current/list
SELECT * 
FROM residents 
WHERE discharge_date IS NULL 
ORDER BY admission_date DESC;
```

---

### 2. 사용자 정보 조회

#### 사용자 ID로 조회
```sql
-- GET /api/v1/users/{user_id}
SELECT * 
FROM users 
WHERE user_id = '00000000-0000-0000-0000-000000000001';
```

#### 역할별 사용자 조회
```sql
-- GET /api/v1/users/list?role=care_target
SELECT * 
FROM users 
WHERE user_role = 'care_target'
ORDER BY created_at DESC;
```

#### 전체 사용자 목록 조회
```sql
-- GET /api/v1/users/list?page=1&size=10
SELECT * 
FROM users 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 0;
```

---

### 3. 사용자 프로필 조회

#### 사용자 ID로 프로필 조회
```sql
-- GET /api/v1/user-profiles/{user_id}
SELECT * 
FROM user_profiles 
WHERE user_id = '00000000-0000-0000-0000-000000000001';
```

#### 전체 프로필 목록 조회
```sql
-- GET /api/v1/user-profiles/list?page=1&size=10
SELECT * 
FROM user_profiles 
ORDER BY created_at DESC 
LIMIT 10 OFFSET 0;
```

---

### 4. 사용자 관계 조회

#### 관계 ID로 조회
```sql
-- GET /api/v1/user-relationships/{relationship_id}
SELECT * 
FROM user_relationships 
WHERE relationship_id = '00000000-0000-0000-0000-000000000020';
```

#### 사용자가 주체인 관계 조회
```sql
-- GET /api/v1/user-relationships/user/{user_id}/as-subject
SELECT * 
FROM user_relationships 
WHERE subject_user_id = '00000000-0000-0000-0000-000000000005'
ORDER BY created_at DESC;
```

#### 사용자가 대상인 관계 조회
```sql
-- GET /api/v1/user-relationships/user/{user_id}/as-target
SELECT * 
FROM user_relationships 
WHERE target_user_id = '00000000-0000-0000-0000-000000000001'
ORDER BY created_at DESC;
```

---

## JOIN 조회 쿼리

### 1. 입소자 + 사용자 정보 JOIN 조회

#### 입소자와 사용자 기본 정보 함께 조회
```sql
-- 입소자 정보와 사용자 기본 정보를 함께 조회
SELECT 
    r.*,
    u.user_name,
    u.user_role,
    u.email,
    u.phone_number,
    u.created_at AS user_created_at
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
WHERE r.user_id = '00000000-0000-0000-0000-000000000001';
```

#### 현재 입소 중인 입소자 + 사용자 정보
```sql
SELECT 
    r.resident_number,
    r.nickname,
    r.room_number,
    r.floor_number,
    r.admission_date,
    u.user_name,
    u.user_role,
    u.email,
    u.phone_number
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
WHERE r.discharge_date IS NULL
ORDER BY r.admission_date DESC;
```

---

### 2. 입소자 + 사용자 프로필 JOIN 조회

#### 입소자와 프로필 정보 함께 조회
```sql
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

### 3. 입소자 + 관계 정보 JOIN 조회

#### 입소자와 담당 직원 관계 조회
```sql
-- 입소자와 담당 직원(caregiver) 관계 조회
SELECT 
    r.resident_number,
    r.nickname,
    r.room_number,
    u_resident.user_name AS resident_name,
    u_caregiver.user_name AS caregiver_name,
    u_caregiver.email AS caregiver_email,
    u_caregiver.phone_number AS caregiver_phone,
    ur.relationship_type,
    ur.status AS relationship_status
FROM residents r
INNER JOIN users u_resident ON r.user_id = u_resident.user_id
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
    r.nickname,
    r.room_number,
    u_resident.user_name AS resident_name,
    u_family.user_name AS family_name,
    u_family.email AS family_email,
    u_family.phone_number AS family_phone,
    ur.relationship_type,
    ur.status AS relationship_status
FROM residents r
INNER JOIN users u_resident ON r.user_id = u_resident.user_id
INNER JOIN user_relationships ur ON r.user_id = ur.target_user_id
INNER JOIN users u_family ON ur.subject_user_id = u_family.user_id
WHERE ur.relationship_type = 'family'
  AND ur.status = 'active'
  AND r.discharge_date IS NULL
ORDER BY r.room_number;
```

---

### 4. 전체 정보 통합 조회

#### 입소자 + 사용자 + 프로필 + 관계 통합 조회
```sql
-- 입소자의 모든 정보를 한 번에 조회
SELECT 
    -- 입소자 정보
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
    
    -- 사용자 기본 정보
    u.user_name,
    u.user_role,
    u.email,
    u.phone_number,
    
    -- 프로필 정보
    up.date_of_birth,
    up.gender,
    up.address,
    up.medical_history,
    up.significant_notes,
    up.current_status,
    
    -- 보호자 정보 (residents 테이블)
    r.guardian_name,
    r.guardian_relationship,
    r.guardian_phone
    
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
LEFT JOIN user_profiles up ON r.user_id = up.user_id
WHERE r.user_id = '00000000-0000-0000-0000-000000000001';
```

---

## 조건별 조회 쿼리

### 1. 생활실별 입소자 조회

```sql
-- GET /api/v1/residents/room/{room_number}
SELECT * 
FROM residents 
WHERE room_number = '302'
  AND discharge_date IS NULL
ORDER BY bed_number;
```

### 2. 층별 입소자 조회

```sql
-- GET /api/v1/residents/floor/{floor_number}
SELECT * 
FROM residents 
WHERE floor_number = 3
  AND discharge_date IS NULL
ORDER BY room_number, bed_number;
```

### 3. ADL 수준별 입소자 조회

```sql
-- GET /api/v1/residents/adl/{adl_level}
SELECT * 
FROM residents 
WHERE adl_level = 'partial_assistance'
  AND discharge_date IS NULL
ORDER BY admission_date DESC;
```

### 4. 키워드 검색

```sql
-- GET /api/v1/residents/search/{keyword}
SELECT * 
FROM residents 
WHERE 
    resident_number ILIKE '%Akaza%'
    OR nickname ILIKE '%Akaza%'
    OR room_number ILIKE '%Akaza%'
    OR guardian_name ILIKE '%Akaza%'
ORDER BY admission_date DESC;
```

### 5. 복약 일정이 있는 입소자 조회

```sql
-- 복약 일정이 있는 입소자만 조회
SELECT * 
FROM residents 
WHERE medication_schedule IS NOT NULL
  AND discharge_date IS NULL
ORDER BY room_number;
```

### 6. 사건/사고 기록이 있는 입소자 조회

```sql
-- 사건/사고 기록이 있는 입소자만 조회
SELECT * 
FROM residents 
WHERE incidents IS NOT NULL
  AND jsonb_array_length(incidents) > 0
  AND discharge_date IS NULL
ORDER BY admission_date DESC;
```

---

## 통계 조회 쿼리

### 1. 입소자 통계

#### 전체 입소자 수
```sql
SELECT COUNT(*) AS total_residents
FROM residents;
```

#### 현재 입소 중인 입소자 수
```sql
SELECT COUNT(*) AS current_residents
FROM residents
WHERE discharge_date IS NULL;
```

#### 생활실별 입소자 수
```sql
SELECT 
    room_number,
    COUNT(*) AS resident_count
FROM residents
WHERE discharge_date IS NULL
GROUP BY room_number
ORDER BY room_number;
```

#### 층별 입소자 수
```sql
SELECT 
    floor_number,
    COUNT(*) AS resident_count
FROM residents
WHERE discharge_date IS NULL
GROUP BY floor_number
ORDER BY floor_number;
```

#### ADL 수준별 입소자 수
```sql
SELECT 
    adl_level,
    COUNT(*) AS resident_count
FROM residents
WHERE discharge_date IS NULL
GROUP BY adl_level
ORDER BY 
    CASE adl_level
        WHEN 'independent' THEN 1
        WHEN 'partial_assistance' THEN 2
        WHEN 'full_assistance' THEN 3
    END;
```

#### 거동 수준별 입소자 수
```sql
SELECT 
    mobility_level,
    COUNT(*) AS resident_count
FROM residents
WHERE discharge_date IS NULL
GROUP BY mobility_level
ORDER BY mobility_level;
```

#### 인지 수준별 입소자 수
```sql
SELECT 
    cognitive_level,
    COUNT(*) AS resident_count
FROM residents
WHERE discharge_date IS NULL
GROUP BY cognitive_level
ORDER BY 
    CASE cognitive_level
        WHEN 'normal' THEN 1
        WHEN 'mild_impairment' THEN 2
        WHEN 'moderate_impairment' THEN 3
        WHEN 'severe_impairment' THEN 4
    END;
```

---

### 2. 사용자 통계

#### 역할별 사용자 수
```sql
SELECT 
    user_role,
    COUNT(*) AS user_count
FROM users
GROUP BY user_role
ORDER BY user_role;
```

#### 입소자별 담당 직원 수
```sql
SELECT 
    r.resident_number,
    r.nickname,
    COUNT(ur.relationship_id) AS caregiver_count
FROM residents r
LEFT JOIN user_relationships ur ON r.user_id = ur.target_user_id
    AND ur.relationship_type = 'caregiver'
    AND ur.status = 'active'
WHERE r.discharge_date IS NULL
GROUP BY r.resident_number, r.nickname
ORDER BY r.room_number;
```

#### 입소자별 가족 수
```sql
SELECT 
    r.resident_number,
    r.nickname,
    COUNT(ur.relationship_id) AS family_count
FROM residents r
LEFT JOIN user_relationships ur ON r.user_id = ur.target_user_id
    AND ur.relationship_type = 'family'
    AND ur.status = 'active'
WHERE r.discharge_date IS NULL
GROUP BY r.resident_number, r.nickname
ORDER BY r.room_number;
```

---

### 3. 복약 관리 통계

#### 복약 일정이 있는 입소자 수
```sql
SELECT COUNT(*) AS residents_with_medication
FROM residents
WHERE medication_schedule IS NOT NULL
  AND discharge_date IS NULL;
```

#### 복약 시간대별 입소자 수
```sql
SELECT 
    CASE 
        WHEN medication_schedule::text LIKE '%morning%' THEN 'morning'
        WHEN medication_schedule::text LIKE '%noon%' THEN 'noon'
        WHEN medication_schedule::text LIKE '%evening%' THEN 'evening'
        ELSE 'none'
    END AS medication_time,
    COUNT(*) AS resident_count
FROM residents
WHERE discharge_date IS NULL
GROUP BY medication_time
ORDER BY medication_time;
```

---

## 유용한 조회 쿼리 모음

### 1. 입소자 전체 정보 대시보드 쿼리

```sql
-- 입소자의 모든 정보를 한 번에 조회 (대시보드용)
SELECT 
    -- 기본 정보
    r.resident_number,
    r.nickname,
    u.user_name,
    r.room_number,
    r.floor_number,
    r.bed_number,
    
    -- 상태 정보
    r.adl_level,
    r.mobility_level,
    r.cognitive_level,
    r.care_level,
    
    -- 입소 정보
    r.admission_date,
    r.discharge_date,
    CASE 
        WHEN r.discharge_date IS NULL THEN '입소 중'
        ELSE '퇴소'
    END AS status,
    
    -- 프로필 정보
    up.date_of_birth,
    up.gender,
    up.medical_history,
    
    -- 보호자 정보
    r.guardian_name,
    r.guardian_relationship,
    r.guardian_phone,
    
    -- 복약 정보
    CASE 
        WHEN r.medication_schedule IS NOT NULL THEN '있음'
        ELSE '없음'
    END AS has_medication,
    
    -- 사건/사고 정보
    CASE 
        WHEN r.incidents IS NOT NULL AND jsonb_array_length(r.incidents) > 0 
        THEN jsonb_array_length(r.incidents)
        ELSE 0
    END AS incident_count
    
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
LEFT JOIN user_profiles up ON r.user_id = up.user_id
WHERE r.discharge_date IS NULL
ORDER BY r.floor_number, r.room_number, r.bed_number;
```

### 2. 입소자별 담당 직원 및 가족 정보 조회

```sql
-- 입소자별 담당 직원과 가족 정보를 함께 조회
SELECT 
    r.resident_number,
    r.nickname,
    r.room_number,
    u_resident.user_name AS resident_name,
    
    -- 담당 직원 정보
    STRING_AGG(DISTINCT u_caregiver.user_name, ', ') AS caregivers,
    STRING_AGG(DISTINCT u_caregiver.phone_number, ', ') AS caregiver_phones,
    
    -- 가족 정보
    STRING_AGG(DISTINCT u_family.user_name, ', ') AS families,
    STRING_AGG(DISTINCT u_family.phone_number, ', ') AS family_phones
    
FROM residents r
INNER JOIN users u_resident ON r.user_id = u_resident.user_id
LEFT JOIN user_relationships ur_caregiver ON r.user_id = ur_caregiver.target_user_id
    AND ur_caregiver.relationship_type = 'caregiver'
    AND ur_caregiver.status = 'active'
LEFT JOIN users u_caregiver ON ur_caregiver.subject_user_id = u_caregiver.user_id
LEFT JOIN user_relationships ur_family ON r.user_id = ur_family.target_user_id
    AND ur_family.relationship_type = 'family'
    AND ur_family.status = 'active'
LEFT JOIN users u_family ON ur_family.subject_user_id = u_family.user_id
WHERE r.discharge_date IS NULL
GROUP BY r.resident_number, r.nickname, r.room_number, u_resident.user_name
ORDER BY r.room_number;
```

### 3. 최근 입소자 조회

```sql
-- 최근 30일 내 입소한 입소자 조회
SELECT 
    r.resident_number,
    r.nickname,
    u.user_name,
    r.room_number,
    r.admission_date,
    r.adl_level,
    r.mobility_level
FROM residents r
INNER JOIN users u ON r.user_id = u.user_id
WHERE r.admission_date >= CURRENT_DATE - INTERVAL '30 days'
  AND r.discharge_date IS NULL
ORDER BY r.admission_date DESC;
```

### 4. 복약 일정이 필요한 입소자 조회

```sql
-- 복약 일정이 있지만 특이사항이 없는 입소자 조회
SELECT 
    r.resident_number,
    r.nickname,
    r.room_number,
    r.medication_schedule,
    r.medication_notes
FROM residents r
WHERE r.medication_schedule IS NOT NULL
  AND (r.medication_notes IS NULL OR r.medication_notes = '')
  AND r.discharge_date IS NULL
ORDER BY r.room_number;
```

---

## JSONB 필드 조회 팁

### 1. JSONB 필드에서 특정 값 조회

```sql
-- special_notes에서 건강 상태 조회
SELECT 
    resident_number,
    nickname,
    special_notes->'health' AS health_info,
    special_notes->'emotional' AS emotional_info,
    special_notes->'psychological' AS psychological_info
FROM residents
WHERE discharge_date IS NULL;
```

### 2. JSONB 배열 길이 조회

```sql
-- 사건/사고 기록 개수 조회
SELECT 
    resident_number,
    nickname,
    jsonb_array_length(incidents) AS incident_count,
    incidents
FROM residents
WHERE incidents IS NOT NULL
  AND jsonb_array_length(incidents) > 0
ORDER BY incident_count DESC;
```

### 3. JSONB 배열에서 특정 조건 검색

```sql
-- 특정 사건 유형이 있는 입소자 조회
SELECT 
    resident_number,
    nickname,
    incidents
FROM residents
WHERE incidents @> '[{"incident_type": "낙상"}]'::jsonb
  AND discharge_date IS NULL;
```

---

## 참고 사항

### 테이블 관계도

```
users (1) ──< (1) residents
users (1) ──< (1) user_profiles
users (1) ──< (*) user_relationships (subject_user_id)
users (1) ──< (*) user_relationships (target_user_id)
```

### 주요 필드 설명

- **residents.user_id**: `users.user_id`와 1:1 관계 (FK)
- **user_relationships.subject_user_id**: 관계의 주체 (직원, 가족, 관리자)
- **user_relationships.target_user_id**: 관계의 대상 (입소자)
- **user_relationships.relationship_type**: `caregiver`, `family`, `admin`
- **residents.discharge_date**: `NULL`이면 현재 입소 중

---

**작성자**: AI Assistant  
**최종 업데이트**: 2024년

