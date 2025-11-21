import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_ID_FILENAME = "device_ids.txt"  # 1단계에서 생성된 파일
NUM_DAYS = 180                        # 데이터 생성 기간 (6개월)
OUTPUT_FILENAME = "rfid_data.sql"
# ----------------

def read_device_ids():
    """파일에서 device_id 목록을 읽어옵니다."""
    try:
        with open(DEVICE_ID_FILENAME, "r", encoding="utf-8") as f:
            device_ids = [line.strip() for line in f if line.strip()]
        return device_ids
    except FileNotFoundError:
        print(f"오류: '{DEVICE_ID_FILENAME}' 파일을 찾을 수 없습니다.")
        print("먼저 'get_device_ids.py' 스크립트를 실행하여 디바이스 ID 목록을 생성해주세요.")
        return []

def get_random_event_times_for_day(base_date):
    """하루 동안의 랜덤 이벤트 시간(3~4회)을 생성합니다."""
    event_times = []
    num_events = random.choice([3, 4])
    event_times.append(base_date.replace(hour=random.randint(7, 10), minute=random.randint(0, 59)))
    event_times.append(base_date.replace(hour=random.randint(12, 16), minute=random.randint(0, 59)))
    event_times.append(base_date.replace(hour=random.randint(17, 19), minute=random.randint(0, 59)))
    if num_events == 4:
        event_times.append(base_date.replace(hour=random.randint(20, 22), minute=random.randint(0, 59)))
    return sorted(event_times)

def main():
    """메인 실행 함수"""
    print(f"'{DEVICE_ID_FILENAME}' 파일에서 디바이스 ID를 읽는 중...")
    device_ids = read_device_ids()
    
    if not device_ids:
        print("데이터 생성을 중단합니다.")
        return

    print(f"총 {len(device_ids)}개의 디바이스에 대한 데이터 생성을 시작합니다...")
    
    sql_statements = []
    today = datetime.now()

    for device_id in device_ids:
        rfid_uid = f"0x{random.randint(0, 0xFFFFFFFF):08X}"
        for i in range(NUM_DAYS):
            current_date = today - timedelta(days=i)
            event_times = get_random_event_times_for_day(current_date)
            status = 'out'
            
            for event_time in event_times:
                payload = {
                    "rfid_uid": rfid_uid,
                    "command_code": "0x01",
                    "status": status,
                    "event_time": event_time.isoformat()
                }
                time_val = event_time.strftime('%Y-%m-%d %H:%M:%S.%f %z')
                payload_val = json.dumps(payload).replace("'", "''")
                sql = f"INSERT INTO sensor_raw_rfid (time, device_id, raw_payload) VALUES ('{time_val}', '{device_id}', '{payload_val}');"
                sql_statements.append(sql)
                status = 'in' if status == 'out' else 'out'

    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))
        
    print(f"총 {len(sql_statements):,} 건의 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()