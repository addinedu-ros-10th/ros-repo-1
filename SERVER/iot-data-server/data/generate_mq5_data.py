import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "mq5_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "mq5_data.sql"
CRISIS_EVENT_PROBABILITY = 0.0003 # 0.03%
# ----------------

def read_device_ids():
    try:
        with open(DEVICE_INFO_FILENAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row['device_id'] for row in reader]
    except FileNotFoundError:
        print(f"오류: '{DEVICE_INFO_FILENAME}' 파일을 찾을 수 없습니다.")
        return None

def generate_daily_mq5_events(base_date):
    events = {} # time: {ppm, event_type}

    # 1. 주기적 측정 (1분 간격)
    current_time = base_date.replace(hour=0, minute=0, second=0)
    end_of_day = current_time + timedelta(days=1)
    while current_time < end_of_day:
        ppm = round(random.uniform(150, 250), 2)
        events[current_time] = {'ppm': ppm, 'event_type': 'heartbeat_1min'}
        current_time += timedelta(minutes=1)

    # 2. 관심 이벤트 (요리)
    for hour in [random.randint(7,8), random.randint(12,13), random.randint(18,19)]:
        cook_time = base_date.replace(hour=hour, minute=random.randint(0, 59))
        events[cook_time] = {'ppm': round(random.uniform(300, 500), 2), 'event_type': 'attention_cooking'}
    
    # 3. 위기 이벤트 (가스 누출)
    if random.random() < CRISIS_EVENT_PROBABILITY:
        crisis_time = base_date.replace(hour=random.randint(1, 23), minute=random.randint(0, 59))
        events[crisis_time] = {'ppm': round(random.uniform(1000, 5000), 2), 'event_type': 'crisis_gas_leak'}

    return sorted(events.items())

def main():
    device_ids = read_device_ids()
    if not device_ids: return

    print(f"총 {len(device_ids)}개의 디바이스에 대한 MQ-5 데이터 생성을 시작합니다...")
    
    total_events = 0
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        for device_id in device_ids:
            print(f"디바이스 {device_id[:18]}... 의 데이터 생성 중...")
            for i in range(NUM_DAYS):
                current_date = datetime.now() - timedelta(days=i)
                daily_events = generate_daily_mq5_events(current_date)
                
                for time, event_data in daily_events:
                    total_events += 1
                    payload = {
                        "gas_ppm": event_data['ppm'], "event_type": event_data['event_type'],
                        "temperature_c": round(random.uniform(20.0, 28.0), 1),
                        "humidity_percent": round(random.uniform(45.0, 65.0), 1),
                        "status": "ok" if event_data['ppm'] < 1000 else "danger"
                    }
                    time_val = time.strftime('%Y-%m-%d %H:%M:%S.%f')
                    payload_val = json.dumps(payload).replace("'", "''")
                    sql = f"INSERT INTO sensor_raw_mq5 (time, device_id, raw_payload) VALUES ('{time_val}', '{device_id}', '{payload_val}');"
                    f.write(sql + "\n")

    print(f"\n총 약 {total_events:,} 건의 MQ-5 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()