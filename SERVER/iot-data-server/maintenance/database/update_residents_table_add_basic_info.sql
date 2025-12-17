-- ============================================================
-- residents 테이블에 기본 정보 필드 추가
-- ============================================================
-- 
-- users 테이블과 동일한 기본 정보를 residents 테이블에도 추가하여
-- 조인 없이도 기본 정보를 조회할 수 있도록 합니다.
--
-- 추가 필드:
-- - user_name: 사용자 이름 (users.user_name과 동일)
-- - email: 이메일 주소 (users.email과 동일)
-- - phone_number: 전화번호 (users.phone_number과 동일)
-- ============================================================

-- 1. 기본 정보 필드 추가
ALTER TABLE residents
ADD COLUMN IF NOT EXISTS user_name TEXT,
ADD COLUMN IF NOT EXISTS email TEXT,
ADD COLUMN IF NOT EXISTS phone_number TEXT;

-- 2. 기존 데이터 업데이트 (users 테이블에서 정보 복사)
UPDATE residents r
SET 
    user_name = u.user_name,
    email = u.email,
    phone_number = u.phone_number
FROM users u
WHERE r.user_id = u.user_id
  AND (r.user_name IS NULL OR r.email IS NULL OR r.phone_number IS NULL);

-- 3. 인덱스 추가 (검색 성능 향상)
CREATE INDEX IF NOT EXISTS idx_residents_user_name ON residents(user_name);
CREATE INDEX IF NOT EXISTS idx_residents_email ON residents(email);
CREATE INDEX IF NOT EXISTS idx_residents_phone_number ON residents(phone_number);

-- 4. 코멘트 추가
COMMENT ON COLUMN residents.user_name IS '사용자 이름 (users.user_name과 동일)';
COMMENT ON COLUMN residents.email IS '이메일 주소 (users.email과 동일)';
COMMENT ON COLUMN residents.phone_number IS '전화번호 (users.phone_number과 동일)';

