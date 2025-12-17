# 데이터베이스 마이그레이션 가이드

## 개요

세션 관리 기능을 DB 기반으로 전환하면서 `conversation_sessions` 테이블에 `name`과 `nickname` 필드가 추가되었습니다.

## 자동 마이그레이션 vs 수동 마이그레이션

### 자동 마이그레이션 (제한적)

서버가 시작될 때:
- ✅ **테이블이 없으면 자동 생성** (새로운 필드 포함)
- ❌ **기존 테이블에 컬럼 추가는 자동으로 되지 않음**

따라서 **기존 데이터베이스를 사용 중이라면 수동 마이그레이션이 필요합니다.**

## 마이그레이션 방법

### 방법 1: SQL 스크립트 실행 (권장)

#### 1.1 마이그레이션 SQL 파일 확인
```bash
cat AI/llm-gateway/maintenance/database/add_session_name_nickname.sql
```

#### 1.2 데이터베이스에 연결하여 실행

**PostgreSQL 직접 연결:**
```bash
psql -U your_db_user -d your_database_name -f AI/llm-gateway/maintenance/database/add_session_name_nickname.sql
```

**Docker 컨테이너를 통한 실행:**
```bash
# PostgreSQL 컨테이너 이름 확인
docker ps | grep postgres

# 컨테이너 내부에서 실행
docker exec -i your_postgres_container psql -U your_db_user -d your_database_name < AI/llm-gateway/maintenance/database/add_session_name_nickname.sql
```

**환경 변수 사용:**
```bash
# .env 파일에서 DB 정보 확인 후
source .env
psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f AI/llm-gateway/maintenance/database/add_session_name_nickname.sql
```

### 방법 2: 수동 SQL 실행

데이터베이스 클라이언트(psql, pgAdmin, DBeaver 등)에서 직접 실행:

```sql
-- 1. name 필드 추가 (이미 존재하면 무시)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'conversation_sessions' 
        AND column_name = 'name'
    ) THEN
        ALTER TABLE conversation_sessions ADD COLUMN name VARCHAR(255);
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
    END IF;
END $$;

-- 3. 인덱스 추가
CREATE INDEX IF NOT EXISTS idx_nickname ON conversation_sessions(nickname);
CREATE INDEX IF NOT EXISTS idx_name ON conversation_sessions(name);
```

### 방법 3: Python 스크립트로 실행

```python
# migrate_sessions_table.py
import os
import sys
sys.path.insert(0, 'AI/llm-gateway/src')

from database import db_manager

def migrate():
    db_manager.initialize()
    
    with db_manager.get_session() as session:
        # name 필드 추가
        session.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'conversation_sessions' 
                    AND column_name = 'name'
                ) THEN
                    ALTER TABLE conversation_sessions ADD COLUMN name VARCHAR(255);
                END IF;
            END $$;
        """)
        
        # nickname 필드 추가
        session.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'conversation_sessions' 
                    AND column_name = 'nickname'
                ) THEN
                    ALTER TABLE conversation_sessions ADD COLUMN nickname VARCHAR(255);
                END IF;
            END $$;
        """)
        
        # 인덱스 추가
        session.execute("CREATE INDEX IF NOT EXISTS idx_nickname ON conversation_sessions(nickname)")
        session.execute("CREATE INDEX IF NOT EXISTS idx_name ON conversation_sessions(name)")
        
        session.commit()
        print("✅ 마이그레이션 완료")

if __name__ == "__main__":
    migrate()
```

## 마이그레이션 확인

### 테이블 구조 확인

```sql
-- 컬럼 확인
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'conversation_sessions'
ORDER BY ordinal_position;

-- 인덱스 확인
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'conversation_sessions';
```

### API로 확인

```bash
# 세션 목록 조회 (정상 작동하면 마이그레이션 성공)
curl http://localhost:8001/api/sessions
```

## 문제 해결

### 오류: "column already exists"

이미 마이그레이션이 완료된 상태입니다. 무시해도 됩니다.

### 오류: "table does not exist"

테이블이 없으면 서버 시작 시 자동으로 생성됩니다. 서버를 재시작하세요.

### 오류: "permission denied"

데이터베이스 사용자에게 ALTER TABLE 권한이 필요합니다:

```sql
GRANT ALL PRIVILEGES ON TABLE conversation_sessions TO your_db_user;
```

## 자동 마이그레이션 개선 (향후)

향후 자동 마이그레이션을 지원하려면 Alembic 같은 마이그레이션 도구를 도입하는 것을 고려할 수 있습니다.

