-- ============================================================
-- residents 테이블 nickname 필드 고유하게 업데이트
-- 각 어르신에게 중복되지 않는 고유한 nickname 할당
-- ============================================================
-- 
-- 기존 nickname 유지:
--   - Akaza
--   - Kyojuro Rengoku
--   - Gyomei Himejima
--   - Zenitsu Agatsuma
--
-- 중복된 nickname 교체:
--   - 밝은쟁이
--   - 원피스
--   - 영화꾼
-- ============================================================

-- 각 어르신에게 고유한 nickname 할당
WITH nickname_pool AS (
    SELECT unnest(ARRAY[
        'Charlie', 'Sam', 'Alex', 'Max', 'Jack', 'Tom', 'Ben', 'Dan', 'Mike', 'John',
        'Rose', 'Lily', 'Grace', 'Emma', 'Sophia', 'Olivia', 'Ava', 'Mia', 'Ella', 'Zoe',
        'Sunny', 'Happy', 'Lucky', 'Buddy', 'Angel', 'Star', 'Moon', 'Sky', 'River', 'Ocean',
        'Teddy', 'Daisy', 'Ruby', 'Pearl', 'Diamond', 'Gold', 'Silver', 'Crystal', 'Amber', 'Jade',
        'Leo', 'Noah', 'Ethan', 'Lucas', 'Mason', 'Logan', 'Aiden', 'Carter', 'Owen', 'Wyatt',
        'さくら', 'あかり', 'ゆき', 'はな', 'みゆき', 'あい', 'みさき', 'なな', 'みお', 'りん',
        'たろう', 'じろう', 'さとし', 'けんじ', 'ひろし', 'まさき', 'ゆうき', 'だいすけ', 'ともき', 'りく',
        'おじいちゃん', 'おばあちゃん', 'おじさん', 'おばさん', 'お兄さん', 'お姉さん',
        'さくらんぼ', 'もも', 'いちご', 'ぶどう', 'りんご', 'みかん', 'ばなな', 'パイナップル', 'メロン', 'スイカ',
        'はる', 'なつ', 'あき', 'ふゆ', 'あさ', 'ひる', 'よる', 'つき', 'ほし', 'そら',
        'Pierre', 'Jean', 'Louis', 'Henri', 'André', 'François', 'Michel', 'Philippe', 'Jacques', 'Claude',
        'Marie', 'Sophie', 'Isabelle', 'Catherine', 'Françoise', 'Monique', 'Nicole', 'Sylvie', 'Martine', 'Anne',
        'Mon Ami', 'Cheri', 'Belle', 'Beau', 'Douce', 'Tendre', 'Charmant', 'Magnifique', 'Élégant', 'Ravissant',
        'Amour', 'Joie', 'Paix', 'Espoir', 'Rêve', 'Fleur', 'Rose', 'Lys', 'Tulipe', 'Violette',
        '도라에몽', '뽀로로', '뚱이', '짱구', '나루토', '원숭이', '곰돌이', '토끼', '강아지',
        '미키마우스', '도날드덕', '구피', '뽀삐', '뽀뽀', '뽀미', '뽀니', '뽀뽀뽀', '뽀삐뽀', '뽀뽀뽀뽀',
        '포켓몬', '피카츄', '파이리', '꼬부기', '이상해씨', '파이어', '워터', '그라스', '전기', '바람',
        '토토로', '치히로', '하울', '소피', '키키', '나우시카', '모노노케', '센과치히로', '하울의움직이는성', '마녀배달부',
        '제임스본드', '슈퍼맨', '배트맨', '아이언맨', '스파이더맨', '헐크', '토르', '캡틴아메리카', '울버린', '데드풀',
        '마릴린먼로', '오드리헵번', '그레이스켈리', '엘리자베스테일러', '소피아로렌', '브리짓바르도', '카트린드뇌브', '오드리타투', '나탈리우드먼', '스칼렛요한슨',
        '브래드피트', '톰크루즈', '레오나르도', '조니뎁', '윌스미스', '톰행크스', '로버트다우니', '크리스에반스', '크리스헴스워스', '마크러팔로',
        '한석규', '송강호', '최민식', '이병헌', '황정민', '전지현', '김혜수', '전도연', '김태희', '송혜교',
        '시계', '안경', '지팡이', '모자', '장갑', '신발', '가방', '우산', '책', '펜',
        '컵', '접시', '숟가락', '젓가락', '수저', '그릇', '주전자', '찻잔', '물병', '보온병',
        '라디오', '텔레비전', '전화기', '휴대폰', '태블릿', '노트북', '컴퓨터', '프린터', '스캐너', '카메라',
        '꽃', '나무', '별', '달', '해', '구름', '비', '눈', '바람', '물',
        '바다', '산', '강', '호수', '숲', '들판', '하늘', '땅', '돌', '모래',
        '이야기꾼', '웃음꾼', '노래꾼', '춤꾼', '장기꾼', '바둑꾼', '체스꾼', '카드꾼', '낚시꾼', '등산꾼',
        '독서꾼', '드라마꾼', '음악꾼', '요리꾼', '청소꾼', '정리꾼', '수집꾼', '기억꾼',
        '그림꾼', '글꾼', '만화꾼', '게임꾼', '운동꾼', '산책꾼', '여행꾼', '사진꾼',
        '웃음쟁이', '장난쟁이', '말쟁이', '이야기쟁이', '노래쟁이', '춤쟁이', '놀림쟁이', '귀여운쟁이', '예쁜쟁이',
        '똑똑쟁이', '영리쟁이', '재치쟁이', '유머쟁이', '활발쟁이', '명랑쟁이', '쾌활쟁이', '활기쟁이', '에너지쟁이',
        '사랑쟁이', '친절쟁이', '따뜻쟁이', '부드러운쟁이', '상냥쟁이', '착한쟁이', '선량쟁이', '정직쟁이', '성실쟁이', '부지런쟁이',
        '예술쟁이', '음악쟁이', '그림쟁이', '글쟁이', '만화쟁이', '게임쟁이', '운동쟁이', '산책쟁이', '여행쟁이', '사진쟁이',
        '웃음영감', '이야기영감', '노래영감', '춤영감', '장기영감', '바둑영감', '낚시영감', '등산영감', '독서영감',
        '음악영감', '요리영감', '청소영감', '정리영감', '수집영감', '기억영감', '지혜영감', '경험영감', '인생영감', '철학영감',
        '그림영감', '글영감', '만화영감', '게임영감', '운동영감', '산책영감', '여행영감', '사진영감',
        '웃음할멈', '이야기할멈', '노래할멈', '춤할멈', '장기할멈', '바둑할멈', '낚시할멈', '등산할멈', '독서할멈',
        '음악할멈', '요리할멈', '청소할멈', '정리할멈', '수집할멈', '기억할멈', '지혜할멈', '경험할멈', '인생할멈', '철학할멈',
        '그림할멈', '글할멈', '만화할멈', '게임할멈', '운동할멈', '산책할멈', '여행할멈', '사진할멈',
        '할아버지', '할머니', '아저씨', '아주머니', '어르신', '선생님', '선배님', '고수님', '달인님', '명인님',
        '천재', '명인', '고수', '달인', '대가', '거장', '명장'
    ]) AS nickname
),
resident_list AS (
    SELECT 
        r.user_id,
        ROW_NUMBER() OVER (ORDER BY r.user_id) AS rn
    FROM residents r
    WHERE r.nickname IS NULL 
       OR r.nickname = ''
       OR r.nickname IN ('밝은쟁이', '원피스', '영화꾼')
       OR (r.nickname NOT IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')
           AND EXISTS (
               SELECT 1 FROM residents r2 
               WHERE r2.nickname = r.nickname AND r2.user_id != r.user_id
           ))
),
used_nicknames AS (
    SELECT DISTINCT nickname
    FROM residents
    WHERE nickname IS NOT NULL 
      AND nickname != ''
      AND nickname IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')
),
available_nicknames AS (
    SELECT 
        np.nickname,
        ROW_NUMBER() OVER (ORDER BY random()) AS rn
    FROM nickname_pool np
    WHERE np.nickname NOT IN (SELECT nickname FROM used_nicknames)
),
nickname_assignment AS (
    SELECT 
        rl.user_id,
        an.nickname AS new_nickname,
        ROW_NUMBER() OVER (PARTITION BY an.nickname ORDER BY rl.user_id) AS dup_check
    FROM resident_list rl
    CROSS JOIN LATERAL (
        SELECT nickname, rn
        FROM available_nicknames
        WHERE nickname NOT IN (
            SELECT DISTINCT nickname 
            FROM residents 
            WHERE nickname IS NOT NULL 
              AND nickname != ''
              AND nickname NOT IN ('Akaza', 'Kyojuro Rengoku', 'Gyomei Himejima', 'Zenitsu Agatsuma')
        )
        ORDER BY rn
        LIMIT 1
    ) an
)
UPDATE residents r
SET nickname = na.new_nickname
FROM nickname_assignment na
WHERE r.user_id = na.user_id
  AND na.dup_check = 1;

-- ============================================================
-- 닉네임 업데이트 완료
-- ============================================================
