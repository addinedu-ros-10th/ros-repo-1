import psycopg2
from dotenv import load_dotenv
import os
import sys
import csv

# .env.prod 파일 로드
load_dotenv('../.env.local')


# 환경변수 확인
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)

# --- 사용자 DB 연결 정보 (반드시 채워주세요) ---
DB_CONFIG = {
    "host": DB_HOST,       # 예: localhost 또는 AWS RDS 엔드포인트
    "dbname": DB_NAME,
    "user": DB_USER,       # 예: svc_app 또는 postgres
    "password": DB_PASSWORD,
    "port": DB_PORT
}
# ---------------------------------------------

OUTPUT_FILENAME = "device_ids.txt"
QUERY = "SELECT device_id FROM devices WHERE location_label = 'Entrance - 13.56 RFID 모듈'"

def fetch_device_ids(sensor_keyword, output_filename):
    """DB에 접속하여 특정 키워드를 포함하는 device_id, user_id, location_label을 조회하고 CSV 파일에 저장합니다."""
    
    query = """
        SELECT device_id, user_id, location_label
        FROM devices
        WHERE location_label LIKE %s;
    """
    
    conn = None
    try:
        print("데이터베이스에 연결 중...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        search_pattern = f'%{sensor_keyword}%'
        print(f"'{search_pattern}' 키워드로 디바이스를 검색합니다...")
        cur.execute(query, (search_pattern,))
        results = cur.fetchall()
        
        if not results:
            print(f"경고: '{sensor_keyword}'를 포함하는 디바이스를 찾을 수 없습니다.")
            return

        print(f"총 {len(results)}개의 '{sensor_keyword}' 디바이스를 찾았습니다.")

        with open(output_filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(['device_id', 'user_id', 'location_label'])  # Header
            writer.writerows(results)
        
        print(f"'{output_filename}' 파일에 디바이스 정보를 성공적으로 저장했습니다.")
        cur.close()

    except psycopg2.Error as e:
        print(f"데이터베이스 오류: {e}")
    finally:
        if conn:
            conn.close()
            print("데이터베이스 연결을 닫았습니다.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("\n사용법: python get_device_ids.py \"<검색할 센서 이름>\" <저장할 파일명.csv>")
        print("예시: python get_device_ids.py \"PIR 모션 인식센서\" pir_devices.csv\n")
        sys.exit(1)
        
    sensor_name = sys.argv[1]
    output_file = sys.argv[2]
    fetch_device_ids(sensor_name, output_file)