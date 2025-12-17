-- 세션 테이블에 name, nickname 필드 추가
-- 실행 방법: psql -U your_user -d your_database -f add_session_name_nickname.sql

-- 1. name 필드 추가 (이미 존재하면 무시)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversation_sessions' 
        AND column_name = 'name'
    ) THEN
        ALTER TABLE conversation_sessions ADD COLUMN name VARCHAR(255);
        RAISE NOTICE 'name 컬럼 추가 완료';
    ELSE
        RAISE NOTICE 'name 컬럼이 이미 존재합니다';
    END IF;
END $$;

-- 2. nickname 필드 추가 (이미 존재하면 무시)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversation_sessions' 
        AND column_name = 'nickname'
    ) THEN
        ALTER TABLE conversation_sessions ADD COLUMN nickname VARCHAR(255);
        RAISE NOTICE 'nickname 컬럼 추가 완료';
    ELSE
        RAISE NOTICE 'nickname 컬럼이 이미 존재합니다';
    END IF;
END $$;

-- 3. 인덱스 추가 (이미 존재하면 무시)
CREATE INDEX IF NOT EXISTS idx_nickname ON conversation_sessions(nickname);
CREATE INDEX IF NOT EXISTS idx_name ON conversation_sessions(name);

-- 완료 메시지
SELECT '세션 테이블 스키마 업데이트 완료' AS status;

