#!/usr/bin/env python3
"""
svc_app 유저에게 모든 데이터베이스와 테이블 권한 부여 스크립트

이 스크립트는 Python으로 작성되어 psycopg2를 사용하여
svc_app 유저에게 모든 권한을 부여합니다.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# 프로젝트 루트 설정
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))

# 환경 변수 로드 (여러 경로 시도)
env_files = [
    project_root / '.env.local',
    script_dir.parent / '.env.local',
    Path('.env.local'),
    Path('.env.dev'),
    Path('.env.prod'),
]
env_loaded = False
for env_file in env_files:
    if env_file.exists():
        load_dotenv(env_file, override=True)
        print(f"✅ 환경 변수 로드: {env_file}")
        env_loaded = True
        break

if not env_loaded:
    print("⚠️  .env 파일을 찾을 수 없습니다.")
    print("   환경 변수를 직접 설정하거나 .env.local 파일을 확인하세요.")
    print("   또는 환경 변수를 직접 설정: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD")

def get_db_config():
    """데이터베이스 설정 가져오기"""
    return {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }

def create_user_if_not_exists(conn, username='svc_app', password=None):
    """사용자가 없으면 생성"""
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 1 FROM pg_user WHERE usename = %s
        """, (username,))
        exists = cur.fetchone()
        
        if not exists:
            if password is None:
                password = 'change_me_please'
            cur.execute(f"""
                CREATE USER {username} WITH PASSWORD %s
            """, (password,))
            print(f"✅ {username} 유저가 생성되었습니다.")
        else:
            print(f"ℹ️  {username} 유저가 이미 존재합니다.")
    except Exception as e:
        print(f"❌ 사용자 생성 오류: {e}")
    finally:
        cur.close()

def grant_database_privileges(conn, username='svc_app'):
    """모든 데이터베이스에 연결 권한 부여"""
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT datname 
            FROM pg_database 
            WHERE datistemplate = false 
            AND datname NOT IN ('postgres', 'template0', 'template1')
        """)
        databases = cur.fetchall()
        
        for (db_name,) in databases:
            try:
                cur.execute(f"""
                    GRANT CONNECT ON DATABASE {db_name} TO {username}
                """)
                print(f"✅ 데이터베이스 '{db_name}'에 연결 권한 부여")
            except Exception as e:
                print(f"⚠️  데이터베이스 '{db_name}' 권한 부여 실패: {e}")
    finally:
        cur.close()

def grant_schema_privileges(conn, username='svc_app', schema='public'):
    """스키마에 대한 모든 권한 부여"""
    cur = conn.cursor()
    try:
        # 스키마 권한
        cur.execute(f"""
            GRANT ALL ON SCHEMA {schema} TO {username}
        """)
        cur.execute(f"""
            GRANT USAGE ON SCHEMA {schema} TO {username}
        """)
        print(f"✅ 스키마 '{schema}'에 대한 권한 부여")
        
        # 기본 권한 설정 (향후 생성될 객체)
        cur.execute(f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} 
            GRANT ALL ON TABLES TO {username}
        """)
        cur.execute(f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} 
            GRANT ALL ON SEQUENCES TO {username}
        """)
        cur.execute(f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} 
            GRANT ALL ON FUNCTIONS TO {username}
        """)
        cur.execute(f"""
            ALTER DEFAULT PRIVILEGES IN SCHEMA {schema} 
            GRANT ALL ON TYPES TO {username}
        """)
        print(f"✅ 스키마 '{schema}'의 기본 권한 설정")
    except Exception as e:
        print(f"❌ 스키마 권한 부여 오류: {e}")
    finally:
        cur.close()

def grant_table_privileges(conn, username='svc_app', schema='public'):
    """모든 테이블에 대한 권한 부여"""
    cur = conn.cursor()
    try:
        cur.execute(f"""
            GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {schema} TO {username}
        """)
        print(f"✅ 스키마 '{schema}'의 모든 테이블에 권한 부여")
    except Exception as e:
        print(f"❌ 테이블 권한 부여 오류: {e}")
    finally:
        cur.close()

def grant_sequence_privileges(conn, username='svc_app', schema='public'):
    """모든 시퀀스에 대한 권한 부여"""
    cur = conn.cursor()
    try:
        cur.execute(f"""
            GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {schema} TO {username}
        """)
        print(f"✅ 스키마 '{schema}'의 모든 시퀀스에 권한 부여")
    except Exception as e:
        print(f"❌ 시퀀스 권한 부여 오류: {e}")
    finally:
        cur.close()

def grant_function_privileges(conn, username='svc_app', schema='public'):
    """모든 함수에 대한 실행 권한 부여"""
    cur = conn.cursor()
    try:
        cur.execute(f"""
            GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA {schema} TO {username}
        """)
        print(f"✅ 스키마 '{schema}'의 모든 함수에 실행 권한 부여")
    except Exception as e:
        print(f"❌ 함수 권한 부여 오류: {e}")
    finally:
        cur.close()

def verify_privileges(conn, username='svc_app', schema='public'):
    """권한 확인"""
    cur = conn.cursor()
    try:
        # 테이블 권한 확인
        cur.execute(f"""
            SELECT table_name, privilege_type
            FROM information_schema.table_privileges
            WHERE grantee = %s AND table_schema = %s
            ORDER BY table_name, privilege_type
        """, (username, schema))
        table_privs = cur.fetchall()
        
        if table_privs:
            print(f"\n📊 {username} 유저의 테이블 권한:")
            current_table = None
            for table, priv in table_privs:
                if table != current_table:
                    print(f"  {table}:")
                    current_table = table
                print(f"    - {priv}")
        else:
            print(f"\n⚠️  {username} 유저에게 테이블 권한이 없습니다.")
    finally:
        cur.close()

def main():
    """메인 함수"""
    config = get_db_config()
    
    print("=" * 80)
    print("svc_app 유저 권한 부여 스크립트")
    print("=" * 80)
    print(f"\n데이터베이스 연결 정보:")
    print(f"  호스트: {config['host']}:{config['port']}")
    print(f"  사용자: {config['user']}")
    print()
    
    # postgres 데이터베이스에 연결 (사용자 생성 및 데이터베이스 권한)
    try:
        conn_postgres = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database='postgres',
            user=config['user'],
            password=config['password']
        )
        conn_postgres.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        print("1. 사용자 생성/확인")
        create_user_if_not_exists(conn_postgres)
        
        print("\n2. 모든 데이터베이스에 연결 권한 부여")
        grant_database_privileges(conn_postgres)
        
        conn_postgres.close()
    except Exception as e:
        print(f"❌ postgres 데이터베이스 연결 오류: {e}")
        return
    
    # iot_care 데이터베이스에 연결 (스키마 및 테이블 권한)
    try:
        conn_iot_care = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database='iot_care',
            user=config['user'],
            password=config['password']
        )
        conn_iot_care.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        print("\n3. 스키마 권한 부여")
        grant_schema_privileges(conn_iot_care)
        
        print("\n4. 테이블 권한 부여")
        grant_table_privileges(conn_iot_care)
        
        print("\n5. 시퀀스 권한 부여")
        grant_sequence_privileges(conn_iot_care)
        
        print("\n6. 함수 권한 부여")
        grant_function_privileges(conn_iot_care)
        
        print("\n7. 권한 확인")
        verify_privileges(conn_iot_care)
        
        conn_iot_care.close()
        
        print("\n" + "=" * 80)
        print("✅ 모든 권한 부여 완료!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ iot_care 데이터베이스 연결 오류: {e}")
        return

if __name__ == '__main__':
    main()

