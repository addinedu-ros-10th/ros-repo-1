import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "mq7_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "mq7_data.sql"
CRISIS_EVENT_PROBABILITY = 0.0005 # 0.05%
# ----------------

def read_device_info():
    user_devices = {}
    try:
        with open(DEVICE_INFO_FILENAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['user_id']
                if user_id not in user_devices: user_devices[user_id] = []
                user_devices[user_id].append(row)
        return user_devices
    except FileNotFoundError:
        print(f"오류: '{DEVICE_INFO_FILENAME}' 파일을 찾을 수 없습니다.")
        return None

def generate_daily_mq7_events(base_date):
    events = {} # time: {ppm, event_type}
    
    # 1. 주기적 측정 (1분 간격)
    current_time = base_date.replace(hour=0, minute=0, second=0)
    end_of_day = current_time + timedelta(days=1)
    while current_time < end_of_day:
        ppm = round(random.uniform(5, 15), 2)
        events[current_time] = {'ppm': ppm, 'event_type': 'heartbeat_1min'}
        current_time += timedelta(minutes=1)

    # 2. 관심 이벤트 (기존 이벤트 덮어쓰기)
    cook_time_am = base_date.replace(hour=random.randint(7, 8), minute=random.randint(0, 59))
    events[cook_time_am] = {'ppm': round(random.uniform(20, 35), 2), 'event_type': 'attention_cooking'}
    cook_time_pm = base_date.replace(hour=random.randint(18, 19), minute=random.randint(0, 59))
    events[cook_time_pm] = {'ppm': round(random.uniform(20, 35), 2), 'event_type': 'attention_cooking'}

    # 3. 위기 이벤트
    if random.random() < CRISIS_EVENT_PROBABILITY:
        crisis_time = base_date.replace(hour=random.randint(0, 5), minute=random.randint(0, 59))
        events[crisis_time] = {'ppm': round(random.uniform(50, 200), 2), 'event_type': 'crisis_high_co_level'}

    return sorted(events.items())

def main():
    user_devices = read_device_info()
    if not user_devices: return

    print(f"총 {len(user_devices)}명의 사용자에 대한 MQ-7 데이터 생성을 시작합니다...")
    
    total_events = 0
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        for user_id, devices in user_devices.items():
            print(f"사용자 {user_id[:8]}... 의 데이터 생성 중...")
            for i in range(NUM_DAYS):
                current_date = datetime.now() - timedelta(days=i)
                daily_events = generate_daily_mq7_events(current_date)
                
                for device in devices:
                    for time, event_data in daily_events:
                        total_events += 1
                        payload = {
                            "co_ppm": event_data['ppm'], "event_type": event_data['event_type'],
                            "temperature_c": round(random.uniform(18.0, 25.0), 1),
                            "humidity_percent": round(random.uniform(40.0, 60.0), 1),
                            "status": "ok" if event_data['ppm'] < 50 else "warning"
                        }
                        time_val = time.strftime('%Y-%m-%d %H:%M:%S.%f')
                        payload_val = json.dumps(payload).replace("'", "''")
                        sql = f"INSERT INTO sensor_raw_mq7 (time, device_id, raw_payload) VALUES ('{time_val}', '{device['device_id']}', '{payload_val}');"
                        f.write(sql + "\n")

    print(f"\n총 약 {total_events:,} 건의 MQ-7 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()