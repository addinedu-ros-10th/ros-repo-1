#!/usr/bin/env python3
"""
residents 테이블의 nickname 필드를 다양한 방식으로 채우는 스크립트

다양한 스타일의 닉네임 생성:
- 영어
- 일본어
- 불어
- 캐릭터
- 영화배우
- 사물
- ~~꾼
- ~~쟁이
- ~~영감
- ~~할멈
"""

import random
from typing import List, Dict

# 영어 닉네임
ENGLISH_NICKNAMES = [
    'Charlie', 'Sam', 'Alex', 'Max', 'Jack', 'Tom', 'Ben', 'Dan', 'Mike', 'John',
    'Rose', 'Lily', 'Grace', 'Emma', 'Sophia', 'Olivia', 'Ava', 'Mia', 'Ella', 'Zoe',
    'Sunny', 'Happy', 'Lucky', 'Buddy', 'Angel', 'Star', 'Moon', 'Sky', 'River', 'Ocean'
]

# 일본어 닉네임
JAPANESE_NICKNAMES = [
    'さくら', 'あかり', 'ゆき', 'はな', 'みゆき', 'あい', 'みさき', 'なな', 'みお', 'りん',
    'たろう', 'じろう', 'さとし', 'けんじ', 'ひろし', 'まさき', 'ゆうき', 'だいすけ', 'ともき', 'りく',
    'おじいちゃん', 'おばあちゃん', 'おじさん', 'おばさん', 'お兄さん', 'お姉さん'
]

# 불어 닉네임
FRENCH_NICKNAMES = [
    'Pierre', 'Jean', 'Louis', 'Henri', 'André', 'François', 'Michel', 'Philippe', 'Jacques', 'Claude',
    'Marie', 'Sophie', 'Isabelle', 'Catherine', 'Françoise', 'Monique', 'Nicole', 'Sylvie', 'Martine', 'Anne',
    'Mon Ami', 'Cheri', 'Belle', 'Beau', 'Douce', 'Tendre'
]

# 캐릭터 닉네임
CHARACTER_NICKNAMES = [
    '도라에몽', '뽀로로', '뚱이', '짱구', '원피스', '나루토', '원숭이', '곰돌이', '토끼', '강아지',
    '미키마우스', '도날드덕', '구피', '뽀삐', '뽀뽀', '뽀미', '뽀니', '뽀뽀뽀', '뽀삐뽀', '뽀뽀뽀뽀'
]

# 영화배우 닉네임
ACTOR_NICKNAMES = [
    '제임스본드', '슈퍼맨', '배트맨', '아이언맨', '스파이더맨', '헐크', '토르', '캡틴아메리카', '울버린', '데드풀',
    '마릴린먼로', '오드리헵번', '그레이스켈리', '엘리자베스테일러', '소피아로렌', '브리짓바르도', '카트린드뇌브', '오드리타투', '나탈리우드먼', '스칼렛요한슨'
]

# 사물 닉네임
OBJECT_NICKNAMES = [
    '시계', '안경', '지팡이', '모자', '장갑', '신발', '가방', '우산', '책', '펜',
    '컵', '접시', '숟가락', '젓가락', '수저', '그릇', '주전자', '찻잔', '물병', '보온병',
    '라디오', '텔레비전', '전화기', '휴대폰', '태블릿', '노트북', '컴퓨터', '프린터', '스캐너', '카메라'
]

# ~~꾼 패턴
KKUN_PATTERNS = [
    '이야기꾼', '웃음꾼', '노래꾼', '춤꾼', '장기꾼', '바둑꾼', '체스꾼', '카드꾼', '낚시꾼', '등산꾼',
    '독서꾼', '영화꾼', '드라마꾼', '음악꾼', '요리꾼', '청소꾼', '정리꾼', '수집꾼', '기억꾼', '이야기꾼'
]

# ~~쟁이 패턴
JAENGI_PATTERNS = [
    '웃음쟁이', '장난쟁이', '말쟁이', '이야기쟁이', '노래쟁이', '춤쟁이', '놀림쟁이', '장난쟁이', '귀여운쟁이', '예쁜쟁이',
    '똑똑쟁이', '영리쟁이', '재치쟁이', '유머쟁이', '활발쟁이', '밝은쟁이', '명랑쟁이', '쾌활쟁이', '활기쟁이', '에너지쟁이'
]

# ~~영감 패턴
YEONGGAM_PATTERNS = [
    '웃음영감', '이야기영감', '노래영감', '춤영감', '장기영감', '바둑영감', '낚시영감', '등산영감', '독서영감', '영화영감',
    '음악영감', '요리영감', '청소영감', '정리영감', '수집영감', '기억영감', '지혜영감', '경험영감', '인생영감', '철학영감'
]

# ~~할멈 패턴
HALMEOM_PATTERNS = [
    '웃음할멈', '이야기할멈', '노래할멈', '춤할멈', '장기할멈', '바둑할멈', '낚시할멈', '등산할멈', '독서할멈', '영화할멈',
    '음악할멈', '요리할멈', '청소할멈', '정리할멈', '수집할멈', '기억할멈', '지혜할멈', '경험할멈', '인생할멈', '철학할멈'
]

# 추가 패턴
ADDITIONAL_PATTERNS = [
    '할아버지', '할머니', '아저씨', '아주머니', '어르신', '선생님', '선배님', '고수님', '고수님', '달인님',
    '천재', '명인', '고수', '달인', '대가', '거장', '대가', '명장', '고수', '달인',
    '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기'
]

def generate_nickname(gender: str, age: int, medical_history: str = '') -> str:
    """다양한 스타일의 닉네임 생성"""
    
    # 성별과 나이에 따라 적절한 패턴 선택
    patterns = []
    
    # 영어 닉네임 (모든 경우)
    patterns.append(('english', random.choice(ENGLISH_NICKNAMES)))
    
    # 일본어 닉네임 (모든 경우)
    patterns.append(('japanese', random.choice(JAPANESE_NICKNAMES)))
    
    # 불어 닉네임 (모든 경우)
    patterns.append(('french', random.choice(FRENCH_NICKNAMES)))
    
    # 캐릭터 닉네임 (모든 경우)
    patterns.append(('character', random.choice(CHARACTER_NICKNAMES)))
    
    # 영화배우 닉네임 (모든 경우)
    patterns.append(('actor', random.choice(ACTOR_NICKNAMES)))
    
    # 사물 닉네임 (모든 경우)
    patterns.append(('object', random.choice(OBJECT_NICKNAMES)))
    
    # ~~꾼 패턴 (모든 경우)
    patterns.append(('kkun', random.choice(KKUN_PATTERNS)))
    
    # ~~쟁이 패턴 (모든 경우)
    patterns.append(('jaengi', random.choice(JAENGI_PATTERNS)))
    
    # ~~영감 패턴 (남성, 70세 이상)
    if gender == 'male' and age >= 70:
        patterns.append(('yeonggam', random.choice(YEONGGAM_PATTERNS)))
    
    # ~~할멈 패턴 (여성, 70세 이상)
    if gender == 'female' and age >= 70:
        patterns.append(('halmeom', random.choice(HALMEOM_PATTERNS)))
    
    # 추가 패턴 (모든 경우)
    patterns.append(('additional', random.choice(ADDITIONAL_PATTERNS)))
    
    # 랜덤하게 하나 선택
    selected_pattern = random.choice(patterns)
    return selected_pattern[1]

def generate_nickname_update_sql() -> str:
    """nickname 업데이트 SQL 생성"""
    
    sql = "-- ============================================================\n"
    sql += "-- residents 테이블 nickname 필드 업데이트\n"
    sql += "-- 다양한 스타일의 사실적인 닉네임 생성\n"
    sql += "-- ============================================================\n\n"
    
    sql += "-- 닉네임 업데이트 (다양한 스타일)\n"
    sql += "UPDATE residents SET nickname = CASE user_id\n"
    
    # 100개의 다양한 닉네임 생성
    nicknames = []
    for i in range(100):
        gender = random.choice(['male', 'female'])
        age = random.randint(70, 105)
        medical_history = random.choice(['고혈압', '당뇨', '치매', '관절염', ''])
        
        nickname = generate_nickname(gender, age, medical_history)
        nicknames.append(nickname)
    
    # 실제로는 user_id를 조회해서 업데이트해야 하므로
    # 여기서는 임시로 UUID를 사용하지 않고, 실제 데이터베이스에서 조회하는 방식으로 변경
    sql += "-- 실제 user_id를 조회하여 업데이트\n"
    sql += "-- 아래는 예시이며, 실제로는 데이터베이스에서 조회하여 업데이트합니다.\n\n"
    
    return sql

def generate_nickname_update_sql_v2() -> str:
    """nickname 업데이트 SQL 생성 (실제 사용 가능한 버전)"""
    
    sql = "-- ============================================================\n"
    sql += "-- residents 테이블 nickname 필드 업데이트\n"
    sql += "-- 다양한 스타일의 사실적인 닉네임 생성\n"
    sql += "-- ============================================================\n\n"
    
    sql += "-- 방법 1: 랜덤 닉네임 할당 (모든 어르신에게)\n"
    sql += "UPDATE residents r\n"
    sql += "SET nickname = (\n"
    sql += "    SELECT CASE (random() * 10)::int\n"
    
    # 다양한 패턴을 SQL CASE 문으로 생성
    all_nicknames = []
    all_nicknames.extend(ENGLISH_NICKNAMES[:10])
    all_nicknames.extend(JAPANESE_NICKNAMES[:10])
    all_nicknames.extend(FRENCH_NICKNAMES[:10])
    all_nicknames.extend(CHARACTER_NICKNAMES[:10])
    all_nicknames.extend(ACTOR_NICKNAMES[:10])
    all_nicknames.extend(OBJECT_NICKNAMES[:10])
    all_nicknames.extend(KKUN_PATTERNS[:10])
    all_nicknames.extend(JAENGI_PATTERNS[:10])
    all_nicknames.extend(YEONGGAM_PATTERNS[:10])
    all_nicknames.extend(HALMEOM_PATTERNS[:10])
    
    # SQL CASE 문 생성
    for i, nickname in enumerate(all_nicknames[:100]):
        sql += f"        WHEN {i} THEN '{nickname}'\n"
    
    sql += "        ELSE '친구'\n"
    sql += "    END\n"
    sql += ")\n"
    sql += "WHERE nickname IS NULL;\n\n"
    
    # 방법 2: 성별과 나이에 따라 적절한 닉네임 할당
    sql += "-- 방법 2: 성별과 나이에 따라 적절한 닉네임 할당\n"
    sql += "UPDATE residents r\n"
    sql += "INNER JOIN user_profiles up ON r.user_id = up.user_id\n"
    sql += "SET nickname = CASE\n"
    sql += "    WHEN up.gender = 'male' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN\n"
    sql += "        (SELECT nickname FROM (VALUES "
    male_old = YEONGGAM_PATTERNS[:5] + KKUN_PATTERNS[:5]
    for i, nick in enumerate(male_old):
        sql += f"('{nick}')" + (',' if i < len(male_old) - 1 else '')
    sql += ") AS t(nickname) ORDER BY random() LIMIT 1)\n"
    sql += "    WHEN up.gender = 'female' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN\n"
    sql += "        (SELECT nickname FROM (VALUES "
    female_old = HALMEOM_PATTERNS[:5] + JAENGI_PATTERNS[:5]
    for i, nick in enumerate(female_old):
        sql += f"('{nick}')" + (',' if i < len(female_old) - 1 else '')
    sql += ") AS t(nickname) ORDER BY random() LIMIT 1)\n"
    sql += "    ELSE\n"
    sql += "        (SELECT nickname FROM (VALUES "
    general = ENGLISH_NICKNAMES[:5] + JAPANESE_NICKNAMES[:5] + CHARACTER_NICKNAMES[:5]
    for i, nick in enumerate(general):
        sql += f"('{nick}')" + (',' if i < len(general) - 1 else '')
    sql += ") AS t(nickname) ORDER BY random() LIMIT 1)\n"
    sql += "END\n"
    sql += "WHERE r.nickname IS NULL;\n\n"
    
    return sql

def generate_nickname_update_sql_final() -> str:
    """nickname 업데이트 SQL 생성 (최종 버전 - PostgreSQL 문법)"""
    
    sql = "-- ============================================================\n"
    sql += "-- residents 테이블 nickname 필드 업데이트\n"
    sql += "-- 다양한 스타일의 사실적인 닉네임 생성\n"
    sql += "-- ============================================================\n\n"
    
    # 모든 닉네임 풀 생성
    all_nicknames = []
    
    # 영어 닉네임
    all_nicknames.extend(ENGLISH_NICKNAMES)
    # 일본어 닉네임
    all_nicknames.extend(JAPANESE_NICKNAMES)
    # 불어 닉네임
    all_nicknames.extend(FRENCH_NICKNAMES)
    # 캐릭터 닉네임
    all_nicknames.extend(CHARACTER_NICKNAMES)
    # 영화배우 닉네임
    all_nicknames.extend(ACTOR_NICKNAMES)
    # 사물 닉네임
    all_nicknames.extend(OBJECT_NICKNAMES)
    # ~~꾼 패턴
    all_nicknames.extend(KKUN_PATTERNS)
    # ~~쟁이 패턴
    all_nicknames.extend(JAENGI_PATTERNS)
    # ~~영감 패턴
    all_nicknames.extend(YEONGGAM_PATTERNS)
    # ~~할멈 패턴
    all_nicknames.extend(HALMEOM_PATTERNS)
    # 추가 패턴
    all_nicknames.extend(ADDITIONAL_PATTERNS)
    
    # 중복 제거
    all_nicknames = list(set(all_nicknames))
    
    sql += "-- 방법 1: 랜덤 닉네임 할당 (모든 어르신에게)\n"
    sql += "UPDATE residents\n"
    sql += "SET nickname = (\n"
    sql += "    SELECT unnest(ARRAY[\n"
    
    # 배열로 닉네임 리스트 생성
    nickname_array = "',\n        '".join([n.replace("'", "''") for n in all_nicknames])
    sql += f"        '{nickname_array}'\n"
    sql += "    ]) ORDER BY random() LIMIT 1\n"
    sql += ")\n"
    sql += "WHERE nickname IS NULL;\n\n"
    
    # 방법 2: 성별과 나이에 따라 적절한 닉네임 할당
    sql += "-- 방법 2: 성별과 나이에 따라 적절한 닉네임 할당 (더 사실적)\n"
    sql += "UPDATE residents r\n"
    sql += "SET nickname = (\n"
    sql += "    SELECT CASE\n"
    sql += "        WHEN up.gender = 'male' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    male_old_nicks = "',\n                '".join([n.replace("'", "''") for n in (YEONGGAM_PATTERNS + KKUN_PATTERNS)])
    sql += f"                '{male_old_nicks}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "        WHEN up.gender = 'female' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    female_old_nicks = "',\n                '".join([n.replace("'", "''") for n in (HALMEOM_PATTERNS + JAENGI_PATTERNS)])
    sql += f"                '{female_old_nicks}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "        ELSE\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    general_nicks = "',\n                '".join([n.replace("'", "''") for n in (ENGLISH_NICKNAMES + JAPANESE_NICKNAMES + CHARACTER_NICKNAMES + ACTOR_NICKNAMES)])
    sql += f"                '{general_nicks}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "    END\n"
    sql += "    FROM user_profiles up\n"
    sql += "    WHERE up.user_id = r.user_id\n"
    sql += ")\n"
    sql += "WHERE nickname IS NULL;\n\n"
    
    sql += "-- 방법 3: 모든 어르신에게 랜덤 닉네임 할당 (기존 닉네임도 업데이트)\n"
    sql += "UPDATE residents\n"
    sql += "SET nickname = (\n"
    sql += "    SELECT unnest(ARRAY[\n"
    sql += f"        '{nickname_array}'\n"
    sql += "    ]) ORDER BY random() LIMIT 1\n"
    sql += ");\n\n"
    
    sql += "-- ============================================================\n"
    sql += "-- 닉네임 업데이트 완료\n"
    sql += "-- ============================================================\n"
    
    return sql

if __name__ == '__main__':
    print("=" * 80)
    print("residents 테이블 nickname 필드 업데이트 SQL 생성")
    print("=" * 80)
    print()
    
    sql = generate_nickname_update_sql_final()
    
    output_file = 'maintenance/database/update_residents_nicknames.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"✅ SQL 파일 생성 완료: {output_file}")
    print()
    print("=" * 80)

