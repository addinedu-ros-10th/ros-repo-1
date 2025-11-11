#!/usr/bin/env python3
"""
기존 테이블 목록 확인 스크립트
마이그레이션 전 기존 테이블 상태 확인
"""

import os
import sys
from urllib.parse import urlparse

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    try:
        import psycopg2
        PSYCOPG2_AVAILABLE = True
    except ImportError:
        PSYCOPG2_AVAILABLE = False

from dotenv import load_dotenv


def get_db_connection_params():
    """데이터베이스 연결 파라미터 가져오기"""
    load_dotenv()
    db_url = os.getenv('DB_APP_URL')
    
    if not db_url:
        # SSH 터널 사용 시 기본값
        return {
            'host': 'localhost',
            'port': 15432,
            'user': 'svc_dev',
            'password': 'IOT_dev_123!@#',
            'database': 'iot_care'
        }
    
    # URL 파싱
    # postgresql+asyncpg:// 또는 postgresql:// 제거
    clean_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    parsed = urlparse(clean_url)
    
    # 비밀번호 URL 디코딩
    from urllib.parse import unquote
    password = unquote(parsed.password) if parsed.password else None
    
    return {
        'host': parsed.hostname or 'localhost',
        'port': parsed.port or 5432,
        'user': parsed.username,
        'password': password,
        'database': parsed.path[1:] if parsed.path else 'postgres'
    }


def check_existing_tables_sync():
    """기존 테이블 목록 확인 (동기 버전)"""
    conn_params = get_db_connection_params()
    
    print("=" * 60)
    print("기존 테이블 목록 확인")
    print("=" * 60)
    print(f"데이터베이스: {conn_params['database']}")
    print(f"호스트: {conn_params['host']}:{conn_params['port']}")
    print()
    
    try:
        if PSYCOPG2_AVAILABLE:
            import psycopg2
            conn = psycopg2.connect(**conn_params)
            conn.autocommit = True
            cur = conn.cursor()
        else:
            print("❌ psycopg2 또는 asyncpg가 설치되어 있지 않습니다.")
            print("   Docker 컨테이너를 통해 확인하세요:")
            print("   docker compose exec api python scripts/check_existing_tables.py")
            return
        
        # public 스키마의 모든 테이블 조회
        cur.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        tables = cur.fetchall()
        
        print(f"기존 테이블 개수: {len(tables)}")
        print()
        print("테이블 목록:")
        print("-" * 60)
        for table in tables:
            print(f"  - {table[0]} ({table[1]})")
        
        # 신규 테이블이 이미 존재하는지 확인
        new_tables = [
            'detection_event',
            'marker_registry',
            'text_registry',
            'face_registry',
            'person_registry'
        ]
        
        existing_new_tables = [t[0] for t in tables if t[0] in new_tables]
        
        print()
        print("=" * 60)
        print("신규 테이블 존재 여부 확인")
        print("=" * 60)
        for table_name in new_tables:
            if table_name in existing_new_tables:
                print(f"  ⚠️  {table_name}: 이미 존재함 (마이그레이션 필요 없음)")
            else:
                print(f"  ✅ {table_name}: 없음 (마이그레이션으로 생성됨)")
        
        # Alembic 버전 확인
        print()
        print("=" * 60)
        print("Alembic 마이그레이션 버전")
        print("=" * 60)
        try:
            cur.execute("SELECT version_num FROM alembic_version;")
            version = cur.fetchone()
            if version:
                print(f"  현재 버전: {version[0]}")
            else:
                print("  ⚠️  Alembic 버전 정보 없음")
        except Exception as e:
            print(f"  ⚠️  Alembic 버전 테이블 없음: {e}")
        
        # ENUM 타입 확인
        print()
        print("=" * 60)
        print("ENUM 타입 확인")
        print("=" * 60)
        cur.execute("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e' 
            AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ORDER BY typname;
        """)
        
        enums = cur.fetchall()
        
        if enums:
            for enum in enums:
                print(f"  - {enum[0]}")
        else:
            print("  (ENUM 타입 없음)")
        
        # 신규 ENUM 타입 확인
        new_enums = ['detection_category', 'intent_type']
        existing_enums = [e[0] for e in enums]
        
        print()
        for enum_name in new_enums:
            if enum_name in existing_enums:
                print(f"  ⚠️  {enum_name}: 이미 존재함")
            else:
                print(f"  ✅ {enum_name}: 없음 (마이그레이션으로 생성됨)")
        
        cur.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("결론")
        print("=" * 60)
        if existing_new_tables:
            print("⚠️  일부 신규 테이블이 이미 존재합니다.")
            print("   마이그레이션 실행 전 확인이 필요합니다.")
            print(f"   존재하는 테이블: {', '.join(existing_new_tables)}")
        else:
            print("✅ 신규 테이블이 모두 없습니다.")
            print("   마이그레이션을 안전하게 실행할 수 있습니다.")
            print()
            print("마이그레이션 실행:")
            print("  docker compose exec api alembic upgrade head")
            print("  또는")
            print("  alembic upgrade head")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def check_existing_tables_async():
    """기존 테이블 목록 확인 (비동기 버전)"""
    conn_params = get_db_connection_params()
    
    print("=" * 60)
    print("기존 테이블 목록 확인 (비동기)")
    print("=" * 60)
    print(f"데이터베이스: {conn_params['database']}")
    print(f"호스트: {conn_params['host']}:{conn_params['port']}")
    print()
    
    try:
        conn = await asyncpg.connect(**conn_params)
        
        # public 스키마의 모든 테이블 조회
        tables = await conn.fetch("""
            SELECT table_name, table_type
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """)
        
        print(f"기존 테이블 개수: {len(tables)}")
        print()
        print("테이블 목록:")
        print("-" * 60)
        for table in tables:
            print(f"  - {table['table_name']} ({table['table_type']})")
        
        # 신규 테이블이 이미 존재하는지 확인
        new_tables = [
            'detection_event',
            'marker_registry',
            'text_registry',
            'face_registry',
            'person_registry'
        ]
        
        existing_new_tables = [t['table_name'] for t in tables if t['table_name'] in new_tables]
        
        # Alembic 버전 확인
        print()
        print("=" * 60)
        print("Alembic 마이그레이션 버전")
        print("=" * 60)
        try:
            version = await conn.fetchval("SELECT version_num FROM alembic_version;")
            print(f"  현재 버전: {version}")
        except Exception as e:
            print(f"  ⚠️  Alembic 버전 테이블 없음: {e}")
        
        # ENUM 타입 확인
        print()
        print("=" * 60)
        print("ENUM 타입 확인")
        print("=" * 60)
        enums = await conn.fetch("""
            SELECT typname 
            FROM pg_type 
            WHERE typtype = 'e' 
            AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ORDER BY typname;
        """)
        
        if enums:
            for enum in enums:
                print(f"  - {enum['typname']}")
        else:
            print("  (ENUM 타입 없음)")
        
        # 신규 ENUM 타입 확인
        new_enums = ['detection_category', 'intent_type']
        existing_enums = [e['typname'] for e in enums]
        
        print()
        for enum_name in new_enums:
            if enum_name in existing_enums:
                print(f"  ⚠️  {enum_name}: 이미 존재함")
            else:
                print(f"  ✅ {enum_name}: 없음 (마이그레이션으로 생성됨)")
        
        await conn.close()
        
        print()
        print("=" * 60)
        print("결론")
        print("=" * 60)
        if existing_new_tables:
            print("⚠️  일부 신규 테이블이 이미 존재합니다.")
            print("   마이그레이션 실행 전 확인이 필요합니다.")
        else:
            print("✅ 신규 테이블이 모두 없습니다.")
            print("   마이그레이션을 안전하게 실행할 수 있습니다.")
            print()
            print("마이그레이션 실행:")
            print("  docker compose exec api alembic upgrade head")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    if ASYNCPG_AVAILABLE:
        import asyncio
        asyncio.run(check_existing_tables_async())
    elif PSYCOPG2_AVAILABLE:
        check_existing_tables_sync()
    else:
        print("❌ psycopg2 또는 asyncpg가 설치되어 있지 않습니다.")
        print("   Docker 컨테이너를 통해 확인하세요:")
        print("   docker compose exec api python scripts/check_existing_tables.py")
        sys.exit(1)

