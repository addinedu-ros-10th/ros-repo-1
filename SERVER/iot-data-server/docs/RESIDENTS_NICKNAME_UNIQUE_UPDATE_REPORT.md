# residents 테이블 nickname 고유 업데이트 리포트

**작성일**: 2024년  
**목적**: 각 어르신에게 중복되지 않는 고유한 nickname 할당

---

## ✅ 문제 해결

### 기존 문제
- 제한된 nickname만 생성됨
- 중복된 nickname 발생 (밝은쟁이, 원피스, 영화꾼)

### 해결 방법
- 각 어르신에게 고유한 nickname 할당
- 기존 4개 nickname 유지 (Akaza, Kyojuro Rengoku, Gyomei Himejima, Zenitsu Agatsuma)
- 중복된 nickname 교체

---

## 📋 SQL 쿼리 구조

### 1. nickname_pool CTE
- 300개 이상의 다양한 닉네임 풀 생성
- 영어, 일본어, 불어, 캐릭터, 영화배우, 사물, ~~꾼, ~~쟁이, ~~영감, ~~할멈 등

### 2. resident_list CTE
- nickname이 NULL이거나 빈 문자열인 어르신
- 중복된 nickname을 가진 어르신 (밝은쟁이, 원피스, 영화꾼)
- 기존 4개 nickname을 제외한 중복된 nickname을 가진 어르신

### 3. used_nicknames CTE
- 기존에 사용 중인 nickname (Akaza, Kyojuro Rengoku, Gyomei Himejima, Zenitsu Agatsuma)

### 4. available_nicknames CTE
- 사용 가능한 nickname 풀에서 기존 nickname 제외
- 랜덤 순서로 정렬

### 5. nickname_assignment CTE
- 각 어르신에게 고유한 nickname 할당
- 중복 방지 로직 포함

### 6. UPDATE 문
- nickname_assignment의 결과를 사용하여 residents 테이블 업데이트

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

---

## ✅ 업데이트 후 확인

### 중복 확인

```sql
-- nickname 중복 확인
SELECT nickname, COUNT(*) AS count
FROM residents
WHERE nickname IS NOT NULL AND nickname != ''
GROUP BY nickname
HAVING COUNT(*) > 1
ORDER BY count DESC;
```

### 기존 nickname 유지 확인

```sql
-- 기존 nickname 유지 확인
SELECT user_id, nickname
FROM residents
WHERE nickname IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma');
```

### 전체 nickname 목록 확인

```sql
-- 전체 nickname 목록
SELECT DISTINCT nickname
FROM residents
WHERE nickname IS NOT NULL AND nickname != ''
ORDER BY nickname;
```

---

## 📊 닉네임 유형

| 유형 | 개수 | 예시 |
|------|------|------|
| **영어** | 50개 | Charlie, Sam, Alex, Max, Jack, Rose, Lily, Grace, Emma, Sophia |
| **일본어** | 46개 | さくら, あかり, ゆき, はな, たろう, じろう, おじいちゃん, おばあちゃん |
| **불어** | 40개 | Pierre, Jean, Louis, Marie, Sophie, Mon Ami, Cheri, Belle |
| **캐릭터** | 40개 | 도라에몽, 뽀로로, 뚱이, 짱구, 나루토, 미키마우스, 도날드덕 |
| **영화배우** | 40개 | 제임스본드, 슈퍼맨, 배트맨, 아이언맨, 마릴린먼로, 오드리헵번 |
| **사물** | 50개 | 시계, 안경, 지팡이, 모자, 장갑, 신발, 가방, 우산, 책, 펜 |
| **~~꾼** | 38개 | 이야기꾼, 웃음꾼, 노래꾼, 춤꾼, 장기꾼, 바둑꾼, 낚시꾼, 등산꾼 |
| **~~쟁이** | 40개 | 웃음쟁이, 장난쟁이, 말쟁이, 이야기쟁이, 노래쟁이, 춤쟁이, 귀여운쟁이 |
| **~~영감** | 38개 | 웃음영감, 이야기영감, 노래영감, 춤영감, 장기영감, 바둑영감, 낚시영감 |
| **~~할멈** | 38개 | 웃음할멈, 이야기할멈, 노래할멈, 춤할멈, 장기할멈, 바둑할멈, 낚시할멈 |
| **기타** | 17개 | 할아버지, 할머니, 아저씨, 아주머니, 어르신, 선생님, 고수님, 달인님 |

**총 닉네임 풀**: 약 437개

---

## ✅ 완료 상태

- ✅ 고유한 nickname 할당 로직 구현 완료
- ✅ 기존 nickname 유지 로직 구현 완료
- ✅ 중복 제거 로직 구현 완료
- ✅ SQL 파일 생성 완료
- ⏳ 데이터베이스 업데이트 대기 중

---

**작성자**: AI Assistant  
**작성일**: 2024년  
**상태**: ✅ **SQL 파일 생성 완료, 실행 대기 중**

