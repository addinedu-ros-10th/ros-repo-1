import psycopg2
from datetime import datetime
from dotenv import load_dotenv
import os

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

OUTPUT_FILENAME = "regenerate_devices.sql"

# 올바르게 매핑된 24개의 센서 목록
SENSOR_BLUEPRINT = [
    {'location': 'Entrance', 'sensor_name': 'PIR 모션 인식센서', 'part_name': 'PIR_Motion_Sensor_1'},
    {'location': 'Entrance', 'sensor_name': '13.56 RFID 모듈', 'part_name': 'RC522_RFID_Module_1'},
    {'location': 'Entrance', 'sensor_name': '리드 스위치 센서', 'part_name': 'Reed_Switch_Module_1'},
    {'location': 'Living Room', 'sensor_name': 'PIR 모션 인식센서', 'part_name': 'PIR_Motion_Sensor_2'},
    {'location': 'Living Room', 'sensor_name': '사운드 센서', 'part_name': 'Sound_Sensor_Module_1'},
    {'location': 'Living Room', 'sensor_name': '12mm Push Button', 'part_name': 'Push_Button_1'},
    {'location': 'Living Room', 'sensor_name': 'PIR 모션 인식센서', 'part_name': 'PIR_Motion_Sensor_3'},
    {'location': 'Living Room', 'sensor_name': '아두이노 MQ-7 일산화탄소 가스 센서 모듈', 'part_name': 'MQ7_CO_Sensor_1'},
    {'location': 'Kitchen', 'sensor_name': '무게 센서 로드셀', 'part_name': 'Load_Cell_1'},
    {'location': 'Kitchen', 'sensor_name': '무게 센서 로드셀', 'part_name': 'Load_Cell_2'},
    {'location': 'Kitchen', 'sensor_name': 'PIR 모션 인식센서', 'part_name': 'PIR_Motion_Sensor_4'},
    {'location': 'Kitchen', 'sensor_name': '사운드 센서', 'part_name': 'Sound_Sensor_Module_2'},
    {'location': 'Kitchen', 'sensor_name': '5V 수동부저', 'part_name': 'Passive_Buzzer_1'},
    {'location': 'Kitchen', 'sensor_name': '아두이노 가스센서 모듈 MQ-5', 'part_name': 'MQ5_Gas_Sensor_1'},
    {'location': 'Kitchen', 'sensor_name': '12mm Push Button', 'part_name': 'Push_Button_2'},
    {'location': 'Bathroom', 'sensor_name': 'PIR 모션 인식센서', 'part_name': 'PIR_Motion_Sensor_5'},
    {'location': 'Bathroom', 'sensor_name': '사운드 센서', 'part_name': 'Sound_Sensor_Module_3'},
    {'location': 'Bathroom', 'sensor_name': '12mm Push Button', 'part_name': 'Push_Button_3'},
    {'location': 'Bedroom', 'sensor_name': 'LM35 온도센서', 'part_name': 'LM35_Temp_Sensor_1'},
    {'location': 'Bedroom', 'sensor_name': '사운드 센서', 'part_name': 'Sound_Sensor_Module_4'},
    {'location': 'Bedroom', 'sensor_name': '무게 센서 로드셀', 'part_name': 'Load_Cell_3'},
    {'location': 'Bedroom', 'sensor_name': '아두이노 MQ-7 일산화탄소 가스 센서 모듈', 'part_name': 'MQ7_CO_Sensor_2'},
    {'location': 'Bedroom', 'sensor_name': '12mm Push Button', 'part_name': 'Push_Button_4'},
    {'location': 'Bedroom', 'sensor_name': 'PIR 모션 인식센서', 'part_name': 'PIR_Motion_Sensor_6'}
]

def generate_devices_sql():
    """DB에서 돌봄 대상자 user_id를 조회하여 devices 테이블 INSERT SQL을 생성합니다."""
    
    # 1. DB에서 돌봄 대상자 user_id 조회
    user_ids = []
    conn = None
    try:
        print("데이터베이스에 연결하여 돌봄 대상자 정보를 조회합니다...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_role = 'care_target';")
        results = cur.fetchall()
        user_ids = [row[0] for row in results]
        cur.close()
        print(f"총 {len(user_ids)}명의 돌봄 대상자를 찾았습니다.")
    except psycopg2.Error as e:
        print(f"데이터베이스 오류: {e}")
        return
    finally:
        if conn:
            conn.close()

    if not user_ids:
        print("경고: 돌봄 대상자가 없습니다. SQL 파일을 생성하지 않습니다.")
        return

    # 2. SQL 파일 생성
    sql_statements = []
    # --- 중요: 기존 데이터를 모두 삭제하고 트랜잭션으로 묶습니다 ---
    sql_statements.append("BEGIN;")
    # CASCADE 옵션으로 다른 테이블의 참조 제약조건 문제를 해결합니다.
    sql_statements.append("TRUNCATE TABLE devices CASCADE;")
    sql_statements.append("\n-- ##### 재생성된 devices 테이블 데이터 #####")

    total_devices = 0
    for user_id in user_ids:
        for sensor in SENSOR_BLUEPRINT:
            device_id = f"{user_id}_{sensor['part_name']}"
            location_label = f"{sensor['location']} - {sensor['sensor_name']}"
            
            # user_id는 uuid 타입이므로 따옴표로 감싸줍니다.
            sql = (f"INSERT INTO devices (device_id, user_id, location_label, installed_at) "
                   f"VALUES ('{device_id}', '{user_id}', '{location_label}', NOW());")
            sql_statements.append(sql)
            total_devices += 1

    sql_statements.append("\nCOMMIT;")
    
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))
    
    print(f"\n총 {total_devices}개의 디바이스 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")


if __name__ == "__main__":
    generate_devices_sql()