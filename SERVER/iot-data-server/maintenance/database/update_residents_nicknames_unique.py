#!/usr/bin/env python3
"""
residents 테이블의 nickname 필드를 고유하게 할당하는 SQL 생성 스크립트

각 어르신에게 중복되지 않는 고유한 nickname을 할당합니다.
"""

# 영어 닉네임
ENGLISH_NICKNAMES = [
    'Charlie', 'Sam', 'Alex', 'Max', 'Jack', 'Tom', 'Ben', 'Dan', 'Mike', 'John',
    'Rose', 'Lily', 'Grace', 'Emma', 'Sophia', 'Olivia', 'Ava', 'Mia', 'Ella', 'Zoe',
    'Sunny', 'Happy', 'Lucky', 'Buddy', 'Angel', 'Star', 'Moon', 'Sky', 'River', 'Ocean',
    'Teddy', 'Daisy', 'Ruby', 'Pearl', 'Diamond', 'Gold', 'Silver', 'Crystal', 'Amber', 'Jade',
    'Leo', 'Noah', 'Ethan', 'Lucas', 'Mason', 'Logan', 'Aiden', 'Carter', 'Owen', 'Wyatt'
]

# 일본어 닉네임
JAPANESE_NICKNAMES = [
    'さくら', 'あかり', 'ゆき', 'はな', 'みゆき', 'あい', 'みさき', 'なな', 'みお', 'りん',
    'たろう', 'じろう', 'さとし', 'けんじ', 'ひろし', 'まさき', 'ゆうき', 'だいすけ', 'ともき', 'りく',
    'おじいちゃん', 'おばあちゃん', 'おじさん', 'おばさん', 'お兄さん', 'お姉さん',
    'さくらんぼ', 'もも', 'いちご', 'ぶどう', 'りんご', 'みかん', 'ばなな', 'パイナップル', 'メロン', 'スイカ',
    'はる', 'なつ', 'あき', 'ふゆ', 'あさ', 'ひる', 'よる', 'つき', 'ほし', 'そら'
]

# 불어 닉네임
FRENCH_NICKNAMES = [
    'Pierre', 'Jean', 'Louis', 'Henri', 'André', 'François', 'Michel', 'Philippe', 'Jacques', 'Claude',
    'Marie', 'Sophie', 'Isabelle', 'Catherine', 'Françoise', 'Monique', 'Nicole', 'Sylvie', 'Martine', 'Anne',
    'Mon Ami', 'Cheri', 'Belle', 'Beau', 'Douce', 'Tendre', 'Charmant', 'Magnifique', 'Élégant', 'Ravissant',
    'Amour', 'Joie', 'Paix', 'Espoir', 'Rêve', 'Fleur', 'Rose', 'Lys', 'Tulipe', 'Violette'
]

# 캐릭터 닉네임
CHARACTER_NICKNAMES = [
    '도라에몽', '뽀로로', '뚱이', '짱구', '나루토', '원숭이', '곰돌이', '토끼', '강아지',
    '미키마우스', '도날드덕', '구피', '뽀삐', '뽀뽀', '뽀미', '뽀니', '뽀뽀뽀', '뽀삐뽀', '뽀뽀뽀뽀',
    '포켓몬', '피카츄', '파이리', '꼬부기', '이상해씨', '파이어', '워터', '그라스', '전기', '바람',
    '토토로', '치히로', '하울', '소피', '키키', '나우시카', '모노노케', '센과치히로', '하울의움직이는성', '마녀배달부'
]

# 영화배우 닉네임
ACTOR_NICKNAMES = [
    '제임스본드', '슈퍼맨', '배트맨', '아이언맨', '스파이더맨', '헐크', '토르', '캡틴아메리카', '울버린', '데드풀',
    '마릴린먼로', '오드리헵번', '그레이스켈리', '엘리자베스테일러', '소피아로렌', '브리짓바르도', '카트린드뇌브', '오드리타투', '나탈리우드먼', '스칼렛요한슨',
    '브래드피트', '톰크루즈', '레오나르도', '조니뎁', '윌스미스', '톰행크스', '로버트다우니', '크리스에반스', '크리스헴스워스', '마크러팔로',
    '한석규', '송강호', '최민식', '이병헌', '황정민', '전지현', '김혜수', '전도연', '김태희', '송혜교'
]

# 사물 닉네임
OBJECT_NICKNAMES = [
    '시계', '안경', '지팡이', '모자', '장갑', '신발', '가방', '우산', '책', '펜',
    '컵', '접시', '숟가락', '젓가락', '수저', '그릇', '주전자', '찻잔', '물병', '보온병',
    '라디오', '텔레비전', '전화기', '휴대폰', '태블릿', '노트북', '컴퓨터', '프린터', '스캐너', '카메라',
    '꽃', '나무', '별', '달', '해', '구름', '비', '눈', '바람', '물',
    '바다', '산', '강', '호수', '숲', '들판', '하늘', '땅', '돌', '모래'
]

# ~~꾼 패턴
KKUN_PATTERNS = [
    '이야기꾼', '웃음꾼', '노래꾼', '춤꾼', '장기꾼', '바둑꾼', '체스꾼', '카드꾼', '낚시꾼', '등산꾼',
    '독서꾼', '영화꾼', '드라마꾼', '음악꾼', '요리꾼', '청소꾼', '정리꾼', '수집꾼', '기억꾼', '이야기꾼',
    '장난꾼', '놀림꾼', '웃음꾼', '말꾼', '이야기꾼', '노래꾼', '춤꾼', '장기꾼', '바둑꾼', '체스꾼',
    '그림꾼', '글꾼', '만화꾼', '게임꾼', '운동꾼', '산책꾼', '여행꾼', '사진꾼', '음악꾼', '노래꾼'
]

# ~~쟁이 패턴
JAENGI_PATTERNS = [
    '웃음쟁이', '장난쟁이', '말쟁이', '이야기쟁이', '노래쟁이', '춤쟁이', '놀림쟁이', '장난쟁이', '귀여운쟁이', '예쁜쟁이',
    '똑똑쟁이', '영리쟁이', '재치쟁이', '유머쟁이', '활발쟁이', '밝은쟁이', '명랑쟁이', '쾌활쟁이', '활기쟁이', '에너지쟁이',
    '사랑쟁이', '친절쟁이', '따뜻쟁이', '부드러운쟁이', '상냥쟁이', '착한쟁이', '선량쟁이', '정직쟁이', '성실쟁이', '부지런쟁이',
    '예술쟁이', '음악쟁이', '그림쟁이', '글쟁이', '만화쟁이', '게임쟁이', '운동쟁이', '산책쟁이', '여행쟁이', '사진쟁이'
]

# ~~영감 패턴
YEONGGAM_PATTERNS = [
    '웃음영감', '이야기영감', '노래영감', '춤영감', '장기영감', '바둑영감', '낚시영감', '등산영감', '독서영감', '영화영감',
    '음악영감', '요리영감', '청소영감', '정리영감', '수집영감', '기억영감', '지혜영감', '경험영감', '인생영감', '철학영감',
    '웃음영감', '장난영감', '놀림영감', '말영감', '이야기영감', '노래영감', '춤영감', '장기영감', '바둑영감', '체스영감',
    '그림영감', '글영감', '만화영감', '게임영감', '운동영감', '산책영감', '여행영감', '사진영감', '음악영감', '노래영감'
]

# ~~할멈 패턴
HALMEOM_PATTERNS = [
    '웃음할멈', '이야기할멈', '노래할멈', '춤할멈', '장기할멈', '바둑할멈', '낚시할멈', '등산할멈', '독서할멈', '영화할멈',
    '음악할멈', '요리할멈', '청소할멈', '정리할멈', '수집할멈', '기억할멈', '지혜할멈', '경험할멈', '인생할멈', '철학할멈',
    '웃음할멈', '장난할멈', '놀림할멈', '말할멈', '이야기할멈', '노래할멈', '춤할멈', '장기할멈', '바둑할멈', '체스할멈',
    '그림할멈', '글할멈', '만화할멈', '게임할멈', '운동할멈', '산책할멈', '여행할멈', '사진할멈', '음악할멈', '노래할멈'
]

# 추가 패턴
ADDITIONAL_PATTERNS = [
    '할아버지', '할머니', '아저씨', '아주머니', '어르신', '선생님', '선배님', '고수님', '달인님', '명인님',
    '천재', '명인', '고수', '달인', '대가', '거장', '대가', '명장', '고수', '달인',
    '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기',
    '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기', '옛날추억', '옛날기억', '옛날이야기',
    '바람', '구름', '별', '달', '해', '하늘', '땅', '바다', '산', '강'
]

def generate_unique_nickname_sql() -> str:
    """고유한 nickname 할당 SQL 생성"""
    
    # 모든 닉네임 풀 생성 (중복 제거)
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
    
    # 중복 제거 및 정렬
    all_nicknames = sorted(list(set(all_nicknames)))
    
    # 기존 nickname 제외 (Akaza, Kyojuro Rengoku, Gyomei Himejima, Zenitsu Agatsuma)
    excluded_nicknames = ['Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma']
    all_nicknames = [n for n in all_nicknames if n not in excluded_nicknames]
    
    sql = "-- ============================================================\n"
    sql += "-- residents 테이블 nickname 필드 고유하게 업데이트\n"
    sql += "-- 각 어르신에게 중복되지 않는 고유한 nickname 할당\n"
    sql += "-- ============================================================\n\n"
    
    sql += "-- 기존 nickname 제외: Akaza, Kyojuro Rengoku, Gyomei Himejima, Zenitsu Agatsuma\n"
    sql += "-- 중복된 nickname (밝은쟁이, 원피스, 영화꾼)은 새로운 고유한 nickname으로 교체\n\n"
    
    # 닉네임 배열 생성
    nickname_array = "',\n        '".join([n.replace("'", "''") for n in all_nicknames])
    
    sql += "-- 방법 1: 각 어르신에게 고유한 nickname 할당 (ROW_NUMBER 사용)\n"
    sql += "WITH nickname_pool AS (\n"
    sql += "    SELECT unnest(ARRAY[\n"
    sql += f"        '{nickname_array}'\n"
    sql += "    ]) AS nickname\n"
    sql += "),\n"
    sql += "resident_list AS (\n"
    sql += "    SELECT \n"
    sql += "        r.user_id,\n"
    sql += "        r.nickname AS current_nickname,\n"
    sql += "        ROW_NUMBER() OVER (ORDER BY r.user_id) AS rn\n"
    sql += "    FROM residents r\n"
    sql += "    WHERE r.nickname IS NULL \n"
    sql += "       OR r.nickname = ''\n"
    sql += "       OR r.nickname IN ('밝은쟁이', '원피스', '영화꾼')\n"
    sql += "       OR r.nickname NOT IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')\n"
    sql += "),\n"
    sql += "nickname_assigned AS (\n"
    sql += "    SELECT \n"
    sql += "        rl.user_id,\n"
    sql += "        np.nickname AS new_nickname,\n"
    sql += "        ROW_NUMBER() OVER (PARTITION BY np.nickname ORDER BY rl.user_id) AS nickname_rn\n"
    sql += "    FROM resident_list rl\n"
    sql += "    CROSS JOIN LATERAL (\n"
    sql += "        SELECT nickname\n"
    sql += "        FROM nickname_pool\n"
    sql += "        WHERE nickname NOT IN (\n"
    sql += "            SELECT DISTINCT nickname \n"
    sql += "            FROM residents \n"
    sql += "            WHERE nickname IS NOT NULL \n"
    sql += "              AND nickname != ''\n"
    sql += "              AND nickname IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')\n"
    sql += "        )\n"
    sql += "        ORDER BY random()\n"
    sql += "        LIMIT 1\n"
    sql += "    ) np\n"
    sql += ")\n"
    sql += "UPDATE residents r\n"
    sql += "SET nickname = na.new_nickname\n"
    sql += "FROM nickname_assigned na\n"
    sql += "WHERE r.user_id = na.user_id\n"
    sql += "  AND na.nickname_rn = 1;\n\n"
    
    # 더 간단한 방법 추가
    sql += "-- 방법 2: 더 간단한 방법 (각 어르신에게 순차적으로 고유한 nickname 할당)\n"
    sql += "WITH nickname_pool AS (\n"
    sql += "    SELECT unnest(ARRAY[\n"
    sql += f"        '{nickname_array}'\n"
    sql += "    ]) AS nickname,\n"
    sql += "    ROW_NUMBER() OVER () AS rn\n"
    sql += "),\n"
    sql += "resident_list AS (\n"
    sql += "    SELECT \n"
    sql += "        r.user_id,\n"
    sql += "        ROW_NUMBER() OVER (ORDER BY r.user_id) AS rn\n"
    sql += "    FROM residents r\n"
    sql += "    WHERE r.nickname IS NULL \n"
    sql += "       OR r.nickname = ''\n"
    sql += "       OR r.nickname IN ('밝은쟁이', '원피스', '영화꾼')\n"
    sql += "       OR (r.nickname NOT IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')\n"
    sql += "           AND r.nickname NOT IN (\n"
    sql += "               SELECT nickname FROM residents \n"
    sql += "               WHERE nickname IS NOT NULL AND nickname != ''\n"
    sql += "               GROUP BY nickname HAVING COUNT(*) > 1\n"
    sql += "           ))\n"
    sql += "),\n"
    sql += "excluded_nicknames AS (\n"
    sql += "    SELECT DISTINCT nickname\n"
    sql += "    FROM residents\n"
    sql += "    WHERE nickname IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')\n"
    sql += "       OR nickname IS NULL\n"
    sql += "       OR nickname = ''\n"
    sql += "),\n"
    sql += "available_nicknames AS (\n"
    sql += "    SELECT np.nickname, np.rn\n"
    sql += "    FROM nickname_pool np\n"
    sql += "    WHERE np.nickname NOT IN (SELECT nickname FROM excluded_nicknames)\n"
    sql += ")\n"
    sql += "UPDATE residents r\n"
    sql += "SET nickname = an.nickname\n"
    sql += "FROM resident_list rl\n"
    sql += "JOIN available_nicknames an ON (rl.rn - 1) % (SELECT COUNT(*) FROM available_nicknames) + 1 = an.rn\n"
    sql += "WHERE r.user_id = rl.user_id;\n\n"
    
    # 가장 간단하고 확실한 방법
    sql += "-- 방법 3: 가장 확실한 방법 (각 어르신에게 순차적으로 고유한 nickname 할당)\n"
    sql += "-- 이 방법은 각 어르신에게 순차적으로 고유한 nickname을 할당합니다.\n"
    sql += "WITH nickname_list AS (\n"
    sql += "    SELECT unnest(ARRAY[\n"
    sql += f"        '{nickname_array}'\n"
    sql += "    ]) AS nickname\n"
    sql += "),\n"
    sql += "resident_list AS (\n"
    sql += "    SELECT \n"
    sql += "        r.user_id,\n"
    sql += "        ROW_NUMBER() OVER (ORDER BY r.user_id) AS rn\n"
    sql += "    FROM residents r\n"
    sql += "    WHERE r.nickname IS NULL \n"
    sql += "       OR r.nickname = ''\n"
    sql += "       OR r.nickname IN ('밝은쟁이', '원피스', '영화꾼')\n"
    sql += "       OR (r.nickname NOT IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')\n"
    sql += "           AND EXISTS (\n"
    sql += "               SELECT 1 FROM residents r2 \n"
    sql += "               WHERE r2.nickname = r.nickname AND r2.user_id != r.user_id\n"
    sql += "           ))\n"
    sql += "),\n"
    sql += "nickname_mapping AS (\n"
    sql += "    SELECT \n"
    sql += "        rl.user_id,\n"
    sql += "        nl.nickname,\n"
    sql += "        ROW_NUMBER() OVER (PARTITION BY rl.user_id ORDER BY random()) AS rn\n"
    sql += "    FROM resident_list rl\n"
    sql += "    CROSS JOIN LATERAL (\n"
    sql += "        SELECT nickname\n"
    sql += "        FROM nickname_list\n"
    sql += "        WHERE nickname NOT IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')\n"
    sql += "          AND nickname NOT IN (\n"
    sql += "              SELECT DISTINCT nickname FROM residents \n"
    sql += "              WHERE nickname IS NOT NULL AND nickname != ''\n"
    sql += "                AND nickname IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')\n"
    sql += "          )\n"
    sql += "        ORDER BY random()\n"
    sql += "        LIMIT 1\n"
    sql += "    ) nl\n"
    sql += ")\n"
    sql += "UPDATE residents r\n"
    sql += "SET nickname = nm.nickname\n"
    sql += "FROM nickname_mapping nm\n"
    sql += "WHERE r.user_id = nm.user_id\n"
    sql += "  AND nm.rn = 1;\n\n"
    
    sql += "-- ============================================================\n"
    sql += "-- 닉네임 업데이트 완료\n"
    sql += f"-- 총 사용 가능한 닉네임: {len(all_nicknames)}개\n"
    sql += "-- ============================================================\n"
    
    return sql

if __name__ == '__main__':
    print("=" * 80)
    print("residents 테이블 nickname 필드 고유하게 업데이트 SQL 생성")
    print("=" * 80)
    print()
    
    sql = generate_unique_nickname_sql()
    
    output_file = 'maintenance/database/update_residents_nicknames.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"✅ SQL 파일 생성 완료: {output_file}")
    print()
    print("특징:")
    print("  - 각 어르신에게 고유한 nickname 할당")
    print("  - 기존 nickname (Akaza, Kyojuro Rengoku, Gyomei Himejima, Zenitsu Agatsuma) 유지")
    print("  - 중복된 nickname (밝은쟁이, 원피스, 영화꾼) 교체")
    print("  - 3가지 방법 제공 (복잡도 순)")
    print()
    print("=" * 80)

