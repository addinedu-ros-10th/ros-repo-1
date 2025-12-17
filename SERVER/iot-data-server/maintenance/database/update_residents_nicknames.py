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
from typing import List

# 영어 닉네임
ENGLISH_NICKNAMES = [
    'Charlie', 'Sam', 'Alex', 'Max', 'Jack', 'Tom', 'Ben', 'Dan', 'Mike', 'John',
    'Rose', 'Lily', 'Grace', 'Emma', 'Sophia', 'Olivia', 'Ava', 'Mia', 'Ella', 'Zoe',
    'Sunny', 'Happy', 'Lucky', 'Buddy', 'Angel', 'Star', 'Moon', 'Sky', 'River', 'Ocean',
    'Teddy', 'Daisy', 'Ruby', 'Pearl', 'Diamond', 'Gold', 'Silver', 'Crystal', 'Amber', 'Jade'
]

# 일본어 닉네임
JAPANESE_NICKNAMES = [
    'さくら', 'あかり', 'ゆき', 'はな', 'みゆき', 'あい', 'みさき', 'なな', 'みお', 'りん',
    'たろう', 'じろう', 'さとし', 'けんじ', 'ひろし', 'まさき', 'ゆうき', 'だいすけ', 'ともき', 'りく',
    'おじいちゃん', 'おばあちゃん', 'おじさん', 'おばさん', 'お兄さん', 'お姉さん',
    'さくらんぼ', 'もも', 'いちご', 'ぶどう', 'りんご', 'みかん', 'ばなな', 'パイナップル', 'メロン', 'スイカ'
]

# 불어 닉네임
FRENCH_NICKNAMES = [
    'Pierre', 'Jean', 'Louis', 'Henri', 'André', 'François', 'Michel', 'Philippe', 'Jacques', 'Claude',
    'Marie', 'Sophie', 'Isabelle', 'Catherine', 'Françoise', 'Monique', 'Nicole', 'Sylvie', 'Martine', 'Anne',
    'Mon Ami', 'Cheri', 'Belle', 'Beau', 'Douce', 'Tendre', 'Charmant', 'Magnifique', 'Élégant', 'Ravissant'
]

# 캐릭터 닉네임
CHARACTER_NICKNAMES = [
    '도라에몽', '뽀로로', '뚱이', '짱구', '원피스', '나루토', '원숭이', '곰돌이', '토끼', '강아지',
    '미키마우스', '도날드덕', '구피', '뽀삐', '뽀뽀', '뽀미', '뽀니', '뽀뽀뽀', '뽀삐뽀', '뽀뽀뽀뽀',
    '포켓몬', '피카츄', '파이리', '꼬부기', '이상해씨', '파이어', '워터', '그라스', '전기', '바람'
]

# 영화배우 닉네임
ACTOR_NICKNAMES = [
    '제임스본드', '슈퍼맨', '배트맨', '아이언맨', '스파이더맨', '헐크', '토르', '캡틴아메리카', '울버린', '데드풀',
    '마릴린먼로', '오드리헵번', '그레이스켈리', '엘리자베스테일러', '소피아로렌', '브리짓바르도', '카트린드뇌브', '오드리타투', '나탈리우드먼', '스칼렛요한슨',
    '브래드피트', '톰크루즈', '레오나르도', '조니뎁', '윌스미스', '톰행크스', '로버트다우니', '크리스에반스', '크리스헴스워스', '마크러팔로'
]

# 사물 닉네임
OBJECT_NICKNAMES = [
    '시계', '안경', '지팡이', '모자', '장갑', '신발', '가방', '우산', '책', '펜',
    '컵', '접시', '숟가락', '젓가락', '수저', '그릇', '주전자', '찻잔', '물병', '보온병',
    '라디오', '텔레비전', '전화기', '휴대폰', '태블릿', '노트북', '컴퓨터', '프린터', '스캐너', '카메라',
    '꽃', '나무', '별', '달', '해', '구름', '비', '눈', '바람', '물'
]

# ~~꾼 패턴
KKUN_PATTERNS = [
    '이야기꾼', '웃음꾼', '노래꾼', '춤꾼', '장기꾼', '바둑꾼', '체스꾼', '카드꾼', '낚시꾼', '등산꾼',
    '독서꾼', '영화꾼', '드라마꾼', '음악꾼', '요리꾼', '청소꾼', '정리꾼', '수집꾼', '기억꾼', '이야기꾼',
    '장난꾼', '놀림꾼', '웃음꾼', '말꾼', '이야기꾼', '노래꾼', '춤꾼', '장기꾼', '바둑꾼', '체스꾼'
]

# ~~쟁이 패턴
JAENGI_PATTERNS = [
    '웃음쟁이', '장난쟁이', '말쟁이', '이야기쟁이', '노래쟁이', '춤쟁이', '놀림쟁이', '장난쟁이', '귀여운쟁이', '예쁜쟁이',
    '똑똑쟁이', '영리쟁이', '재치쟁이', '유머쟁이', '활발쟁이', '밝은쟁이', '명랑쟁이', '쾌활쟁이', '활기쟁이', '에너지쟁이',
    '사랑쟁이', '친절쟁이', '따뜻쟁이', '부드러운쟁이', '상냥쟁이', '착한쟁이', '선량쟁이', '정직쟁이', '성실쟁이', '부지런쟁이'
]

# ~~영감 패턴
YEONGGAM_PATTERNS = [
    '웃음영감', '이야기영감', '노래영감', '춤영감', '장기영감', '바둑영감', '낚시영감', '등산영감', '독서영감', '영화영감',
    '음악영감', '요리영감', '청소영감', '정리영감', '수집영감', '기억영감', '지혜영감', '경험영감', '인생영감', '철학영감',
    '웃음영감', '장난영감', '놀림영감', '말영감', '이야기영감', '노래영감', '춤영감', '장기영감', '바둑영감', '체스영감'
]

# ~~할멈 패턴
HALMEOM_PATTERNS = [
    '웃음할멈', '이야기할멈', '노래할멈', '춤할멈', '장기할멈', '바둑할멈', '낚시할멈', '등산할멈', '독서할멈', '영화할멈',
    '음악할멈', '요리할멈', '청소할멈', '정리할멈', '수집할멈', '기억할멈', '지혜할멈', '경험할멈', '인생할멈', '철학할멈',
    '웃음할멈', '장난할멈', '놀림할멈', '말할멈', '이야기할멈', '노래할멈', '춤할멈', '장기할멈', '바둑할멈', '체스할멈'
]

# 추가 패턴
ADDITIONAL_PATTERNS = [
    '할아버지', '할머니', '아저씨', '아주머니', '어르신', '선생님', '선배님', '고수님', '달인님', '명인님',
    '천재', '명인', '고수', '달인', '대가', '거장', '대가', '명장', '고수', '달인',
    '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기',
    '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기'
]

def generate_nickname_update_sql() -> str:
    """nickname 업데이트 SQL 생성 (PostgreSQL 문법)"""
    
    sql = "-- ============================================================\n"
    sql += "-- residents 테이블 nickname 필드 업데이트\n"
    sql += "-- 다양한 스타일의 사실적인 닉네임 생성\n"
    sql += "-- ============================================================\n\n"
    
    # 모든 닉네임 풀 생성
    all_nicknames = []
    all_nicknames.extend(ENGLISH_NICKNAMES)
    all_nicknames.extend(JAPANESE_NICKNAMES)
    all_nicknames.extend(FRENCH_NICKNAMES)
    all_nicknames.extend(CHARACTER_NICKNAMES)
    all_nicknames.extend(ACTOR_NICKNAMES)
    all_nicknames.extend(OBJECT_NICKNAMES)
    all_nicknames.extend(KKUN_PATTERNS)
    all_nicknames.extend(JAENGI_PATTERNS)
    all_nicknames.extend(YEONGGAM_PATTERNS)
    all_nicknames.extend(HALMEOM_PATTERNS)
    all_nicknames.extend(ADDITIONAL_PATTERNS)
    
    # 중복 제거
    all_nicknames = list(set(all_nicknames))
    
    # SQL 배열 생성
    nickname_array = "',\n        '".join([n.replace("'", "''") for n in all_nicknames])
    
    sql += "-- 방법 1: 성별과 나이에 따라 적절한 닉네임 할당 (권장)\n"
    sql += "UPDATE residents r\n"
    sql += "SET nickname = (\n"
    sql += "    SELECT CASE\n"
    sql += "        WHEN up.gender = 'male' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    male_old_nicks = YEONGGAM_PATTERNS + KKUN_PATTERNS
    male_old_array = "',\n                '".join([n.replace("'", "''") for n in list(set(male_old_nicks))])
    sql += f"                '{male_old_array}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "        WHEN up.gender = 'female' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 80 THEN\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    female_old_nicks = HALMEOM_PATTERNS + JAENGI_PATTERNS
    female_old_array = "',\n                '".join([n.replace("'", "''") for n in list(set(female_old_nicks))])
    sql += f"                '{female_old_array}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "        WHEN up.gender = 'male' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 70 THEN\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    male_mid_nicks = KKUN_PATTERNS + CHARACTER_NICKNAMES + ACTOR_NICKNAMES
    male_mid_array = "',\n                '".join([n.replace("'", "''") for n in list(set(male_mid_nicks))])
    sql += f"                '{male_mid_array}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "        WHEN up.gender = 'female' AND EXTRACT(YEAR FROM AGE(up.date_of_birth)) >= 70 THEN\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    female_mid_nicks = JAENGI_PATTERNS + CHARACTER_NICKNAMES + OBJECT_NICKNAMES
    female_mid_array = "',\n                '".join([n.replace("'", "''") for n in list(set(female_mid_nicks))])
    sql += f"                '{female_mid_array}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "        ELSE\n"
    sql += "            (SELECT unnest(ARRAY[\n"
    general_nicks = ENGLISH_NICKNAMES + JAPANESE_NICKNAMES + FRENCH_NICKNAMES + CHARACTER_NICKNAMES
    general_array = "',\n                '".join([n.replace("'", "''") for n in list(set(general_nicks))])
    sql += f"                '{general_array}'\n"
    sql += "            ]) ORDER BY random() LIMIT 1)\n"
    sql += "    END\n"
    sql += "    FROM user_profiles up\n"
    sql += "    WHERE up.user_id = r.user_id\n"
    sql += ")\n"
    sql += "WHERE nickname IS NULL OR nickname = '';\n\n"
    
    sql += "-- 방법 2: 모든 어르신에게 랜덤 닉네임 할당 (기존 닉네임도 업데이트)\n"
    sql += "-- 주의: 이 방법은 모든 닉네임을 랜덤으로 변경합니다.\n"
    sql += "-- UPDATE residents\n"
    sql += "-- SET nickname = (\n"
    sql += "--     SELECT unnest(ARRAY[\n"
    sql += f"--         '{nickname_array}'\n"
    sql += "--     ]) ORDER BY random() LIMIT 1\n"
    sql += "-- );\n\n"
    
    sql += "-- ============================================================\n"
    sql += "-- 닉네임 업데이트 완료\n"
    sql += "-- ============================================================\n"
    
    return sql

if __name__ == '__main__':
    print("=" * 80)
    print("residents 테이블 nickname 필드 업데이트 SQL 생성")
    print("=" * 80)
    print()
    
    sql = generate_nickname_update_sql()
    
    output_file = 'maintenance/database/update_residents_nicknames.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"✅ SQL 파일 생성 완료: {output_file}")
    print()
    print("생성된 닉네임 유형:")
    print(f"  - 영어: {len(ENGLISH_NICKNAMES)}개")
    print(f"  - 일본어: {len(JAPANESE_NICKNAMES)}개")
    print(f"  - 불어: {len(FRENCH_NICKNAMES)}개")
    print(f"  - 캐릭터: {len(CHARACTER_NICKNAMES)}개")
    print(f"  - 영화배우: {len(ACTOR_NICKNAMES)}개")
    print(f"  - 사물: {len(OBJECT_NICKNAMES)}개")
    print(f"  - ~~꾼: {len(KKUN_PATTERNS)}개")
    print(f"  - ~~쟁이: {len(JAENGI_PATTERNS)}개")
    print(f"  - ~~영감: {len(YEONGGAM_PATTERNS)}개")
    print(f"  - ~~할멈: {len(HALMEOM_PATTERNS)}개")
    print()
    print("=" * 80)

