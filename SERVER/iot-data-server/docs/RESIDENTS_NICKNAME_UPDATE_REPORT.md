# residents 테이블 nickname 필드 업데이트 리포트

**작성일**: 2024년  
**목적**: residents 테이블의 nickname 필드를 다양한 스타일로 채우기

---

## ✅ 생성 완료

### 생성된 닉네임 유형

| 유형 | 개수 | 예시 |
|------|------|------|
| **영어** | 40개 | Charlie, Sam, Alex, Max, Jack, Rose, Lily, Grace, Emma, Sophia |
| **일본어** | 36개 | さくら, あかり, ゆき, はな, たろう, じろう, おじいちゃん, おばあちゃん |
| **불어** | 30개 | Pierre, Jean, Louis, Marie, Sophie, Mon Ami, Cheri, Belle |
| **캐릭터** | 30개 | 도라에몽, 뽀로로, 뚱이, 짱구, 원피스, 나루토, 미키마우스, 도날드덕 |
| **영화배우** | 30개 | 제임스본드, 슈퍼맨, 배트맨, 아이언맨, 마릴린먼로, 오드리헵번 |
| **사물** | 40개 | 시계, 안경, 지팡이, 모자, 장갑, 신발, 가방, 우산, 책, 펜 |
| **~~꾼** | 30개 | 이야기꾼, 웃음꾼, 노래꾼, 춤꾼, 장기꾼, 바둑꾼, 낚시꾼, 등산꾼 |
| **~~쟁이** | 30개 | 웃음쟁이, 장난쟁이, 말쟁이, 이야기쟁이, 노래쟁이, 춤쟁이, 귀여운쟁이 |
| **~~영감** | 30개 | 웃음영감, 이야기영감, 노래영감, 춤영감, 장기영감, 바둑영감, 낚시영감 |
| **~~할멈** | 30개 | 웃음할멈, 이야기할멈, 노래할멈, 춤할멈, 장기할멈, 바둑할멈, 낚시할멈 |

**총 닉네임 풀**: 약 326개 (중복 제거 후)

---

## 📋 생성된 SQL 파일

### 파일 위치
- `maintenance/database/update_residents_nicknames.sql`

### SQL 구조

#### 방법 1: 성별과 나이에 따라 적절한 닉네임 할당 (권장)
- **80세 이상 남성**: ~~영감, ~~꾼 패턴
- **80세 이상 여성**: ~~할멈, ~~쟁이 패턴
- **70세 이상 남성**: ~~꾼, 캐릭터, 영화배우 패턴
- **70세 이상 여성**: ~~쟁이, 캐릭터, 사물 패턴
- **기타**: 영어, 일본어, 불어, 캐릭터 패턴

#### 방법 2: 모든 어르신에게 랜덤 닉네임 할당
- 모든 닉네임 풀에서 랜덤 선택
- 기존 닉네임도 업데이트 (주석 처리됨)

---

## 🚀 실행 방법

### 방법 1: Python 스크립트 사용

```bash
cd SERVER/iot-data-server
python3 scripts/execute_sql_file.py maintenance/database/update_residents_nicknames.sql
```

### 방법 2: psql로 직접 실행

```bash
psql -h <DB_HOST> -p <DB_PORT> -U <DB_USER> -d iot_care -f maintenance/database/update_residents_nicknames.sql
```

### 방법 3: SQL 파일 내용 복사하여 실행

1. `maintenance/database/update_residents_nicknames.sql` 파일 열기
2. 방법 1의 SQL만 복사하여 PostgreSQL 클라이언트에서 실행

---

## 📊 닉네임 할당 로직

### 성별 및 나이 기반 할당

```sql
-- 80세 이상 남성
WHEN up.gender = 'male' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN
    -- ~~영감, ~~꾼 패턴

-- 80세 이상 여성
WHEN up.gender = 'female' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN
    -- ~~할멈, ~~쟁이 패턴

-- 70세 이상 남성
WHEN up.gender = 'male' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 70 THEN
    -- ~~꾼, 캐릭터, 영화배우 패턴

-- 70세 이상 여성
WHEN up.gender = 'female' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 70 THEN
    -- ~~쟁이, 캐릭터, 사물 패턴

-- 기타
ELSE
    -- 영어, 일본어, 불어, 캐릭터 패턴
```

---

## ✅ 업데이트 후 확인

### 닉네임이 할당되었는지 확인

```sql
-- nickname이 NULL이 아닌 어르신 수 확인
SELECT COUNT(*) 
FROM residents 
WHERE nickname IS NOT NULL AND nickname != '';

-- nickname이 NULL인 어르신 수 확인
SELECT COUNT(*) 
FROM residents 
WHERE nickname IS NULL OR nickname = '';

-- 닉네임 유형별 개수 확인
SELECT 
    CASE 
        WHEN nickname LIKE '%영감' THEN '~~영감'
        WHEN nickname LIKE '%할멈' THEN '~~할멈'
        WHEN nickname LIKE '%꾼' THEN '~~꾼'
        WHEN nickname LIKE '%쟁이' THEN '~~쟁이'
        WHEN nickname ~ '^[A-Za-z]+$' THEN '영어'
        WHEN nickname ~ '^[あ-ん]+$' THEN '일본어'
        WHEN nickname ~ '^[가-힣]+$' THEN '한국어'
        ELSE '기타'
    END AS nickname_type,
    COUNT(*) AS count
FROM residents
WHERE nickname IS NOT NULL AND nickname != ''
GROUP BY nickname_type
ORDER BY count DESC;
```

### 샘플 데이터 확인

```sql
-- 닉네임이 할당된 어르신 샘플
SELECT 
    r.resident_number,
    r.user_name,
    r.nickname,
    up.gender,
    EXTRACT(YEAR FROM AGE(up.date_of_birth)) AS age
FROM residents r
INNER JOIN user_profiles up ON r.user_id = up.user_id
WHERE r.nickname IS NOT NULL AND r.nickname != ''
LIMIT 10;
```

---

## 📝 닉네임 예시

### 영어 닉네임
- Charlie, Sam, Alex, Max, Jack, Tom, Ben, Dan, Mike, John
- Rose, Lily, Grace, Emma, Sophia, Olivia, Ava, Mia, Ella, Zoe
- Sunny, Happy, Lucky, Buddy, Angel, Star, Moon, Sky, River, Ocean

### 일본어 닉네임
- さくら (사쿠라), あかり (아카리), ゆき (유키), はな (하나)
- たろう (타로), じろう (지로), さとし (사토시), けんじ (켄지)
- おじいちゃん (할아버지), おばあちゃん (할머니)

### 불어 닉네임
- Pierre, Jean, Louis, Henri, André, François, Michel
- Marie, Sophie, Isabelle, Catherine, Françoise, Monique
- Mon Ami, Cheri, Belle, Beau, Douce, Tendre

### 캐릭터 닉네임
- 도라에몽, 뽀로로, 뚱이, 짱구, 원피스, 나루토
- 미키마우스, 도날드덕, 구피, 뽀삐

### 영화배우 닉네임
- 제임스본드, 슈퍼맨, 배트맨, 아이언맨, 스파이더맨
- 마릴린먼로, 오드리헵번, 그레이스켈리, 엘리자베스테일러

### 사물 닉네임
- 시계, 안경, 지팡이, 모자, 장갑, 신발, 가방, 우산, 책, 펜

### ~~꾼 패턴
- 이야기꾼, 웃음꾼, 노래꾼, 춤꾼, 장기꾼, 바둑꾼, 낚시꾼, 등산꾼

### ~~쟁이 패턴
- 웃음쟁이, 장난쟁이, 말쟁이, 이야기쟁이, 노래쟁이, 춤쟁이, 귀여운쟁이

### ~~영감 패턴
- 웃음영감, 이야기영감, 노래영감, 춤영감, 장기영감, 바둑영감, 낚시영감

### ~~할멈 패턴
- 웃음할멈, 이야기할멈, 노래할멈, 춤할멈, 장기할멈, 바둑할멈, 낚시할멈

---

## 📚 관련 파일

1. **SQL 파일**: `maintenance/database/update_residents_nicknames.sql`
2. **생성 스크립트**: `maintenance/database/update_residents_nicknames.py`

---

## ✅ 완료 상태

- ✅ 닉네임 풀 생성 완료 (326개)
- ✅ SQL 파일 생성 완료
- ✅ 성별 및 나이 기반 할당 로직 구현 완료
- ⏳ 데이터베이스 업데이트 대기 중

---

**작성자**: AI Assistant  
**작성일**: 2024년  
**상태**: ✅ **SQL 파일 생성 완료, 실행 대기 중**

