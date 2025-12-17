import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "sound_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "sound_data.sql"
CRISIS_EVENT_PROBABILITY = 0.001 # 하루에 위기 이벤트가 발생할 확률 (0.1%)
# ----------------

def read_device_info():
    """파일에서 디바이스 정보를 읽어 사용자별로 그룹화합니다."""
    user_devices = {}
    try:
        with open(DEVICE_INFO_FILENAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['user_id']
                if user_id not in user_devices:
                    user_devices[user_id] = []
                user_devices[user_id].append(row)
        return user_devices
    except FileNotFoundError:
        print(f"오류: '{DEVICE_INFO_FILENAME}' 파일을 찾을 수 없습니다.")
        return None

def get_random_time(base_time, plus_minutes):
    """기준 시간에 랜덤한 분/초를 더해 고유한 시간을 만듭니다."""
    return base_time + timedelta(
        minutes=random.randint(0, plus_minutes),
        seconds=random.randint(0, 59),
        microseconds=random.randint(0, 999999)
    )

def generate_daily_sound_events(user_devices_list, base_date):
    """하루 동안의 생활 패턴에 따른 사운드 이벤트 목록을 생성합니다."""
    events = []
    device_map = {label.split(' - ')[0].strip(): dev['device_id'] for dev in user_devices_list for label in [dev['location_label']]}

    sound_patterns = {
        "morning": [
            {"location": "Bedroom", "type": "movement_rustle", "db": (40, 50), "freq": (100, 500), "duration": (1, 5)},
            {"location": "Bathroom", "type": "water_running", "db": (60, 70), "freq": (400, 1500), "duration": (30, 180)},
            {"location": "Kitchen", "type": "cooking_clatter", "db": (65, 75), "freq": (800, 4000), "duration": (5, 20)}
        ],
        "daytime": [
            {"location": "Living Room", "type": "television", "db": (55, 65), "freq": (200, 3000), "duration": (600, 1800)},
            {"location": "Living Room", "type": "phone_conversation", "db": (60, 70), "freq": (300, 3500), "duration": (120, 600)}
        ],
        "evening": [
            {"location": "Kitchen", "type": "cooking_clatter", "db": (65, 75), "freq": (800, 4000), "duration": (10, 30)},
            {"location": "Living Room", "type": "television", "db": (55, 65), "freq": (200, 3000), "duration": (1800, 3600)},
            {"location": "Bathroom", "type": "shower", "db": (70, 80), "freq": (500, 2000), "duration": (300, 900)}
        ],
        "night": [
            {"location": "Bedroom", "type": "coughing", "db": (60, 70), "freq": (200, 800), "duration": (1, 3)},
            {"location": "Bedroom", "type": "snoring", "db": (50, 65), "freq": (100, 600), "duration": (5, 15)}
        ]
    }

    # 시간대별 이벤트 생성
    for _ in range(random.randint(3, 5)): # 아침
        p = random.choice(sound_patterns["morning"])
        if device_map.get(p["location"]):
            events.append({"time": get_random_time(base_date.replace(hour=6), 180), "device_id": device_map[p["location"]], "pattern": p})
    for _ in range(random.randint(4, 8)): # 낮
        p = random.choice(sound_patterns["daytime"])
        if device_map.get(p["location"]):
            events.append({"time": get_random_time(base_date.replace(hour=9), 540), "device_id": device_map[p["location"]], "pattern": p})
    for _ in range(random.randint(3, 5)): # 저녁
        p = random.choice(sound_patterns["evening"])
        if device_map.get(p["location"]):
            events.append({"time": get_random_time(base_date.replace(hour=18), 240), "device_id": device_map[p["location"]], "pattern": p})
    for _ in range(random.randint(0, 3)): # 밤
        p = random.choice(sound_patterns["night"])
        if device_map.get(p["location"]):
            events.append({"time": get_random_time(base_date.replace(hour=22), 360), "device_id": device_map[p["location"]], "pattern": p})

    # 위기 이벤트 생성
    if random.random() < CRISIS_EVENT_PROBABILITY:
        crisis_patterns = [
            {"type": "thud_fall", "db": (80, 95), "freq": (50, 500)},
            {"type": "shout_for_help", "db": (90, 105), "freq": (500, 2500)},
            {"type": "smoke_alarm", "db": (100, 110), "freq": (3000, 4000)}
        ]
        p = random.choice(crisis_patterns)
        location = random.choice(list(device_map.keys()))
        events.append({"time": get_random_time(base_date.replace(hour=0), 1439), "device_id": device_map[location], "pattern": {**p, "duration": (10, 30)}})
            
    return sorted(events, key=lambda x: x['time'])

def main():
    """메인 실행 함수"""
    user_devices = read_device_info()
    if not user_devices:
        return

    print(f"총 {len(user_devices)}명의 사용자에 대한 데이터 생성을 시작합니다...")
    
    today = datetime.now()
    total_events = 0
    
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        for user_id, devices in user_devices.items():
            print(f"사용자 {user_id[:8]}... 의 데이터 생성 중...")
            for i in range(NUM_DAYS):
                current_date = today - timedelta(days=i)
                daily_events = generate_daily_sound_events(devices, current_date)
                
                for event in daily_events:
                    total_events += 1
                    p = event['pattern']
                    payload = {
                        "event_type": p['type'],
                        "db_level": round(random.uniform(p['db'][0], p['db'][1]), 2),
                        "dominant_frequency_hz": round(random.uniform(p['freq'][0], p['freq'][1]), 2),
                        "duration_s": round(random.uniform(p['duration'][0], p['duration'][1]), 2)
                    }
                    time_val = event['time'].strftime('%Y-%m-%d %H:%M:%S.%f %z')
                    payload_val = json.dumps(payload).replace("'", "''")
                    
                    sql = f"INSERT INTO sensor_raw_sound (time, device_id, raw_payload) VALUES ('{time_val}', '{event['device_id']}', '{payload_val}');"
                    f.write(sql + "\n")

    print(f"\n총 약 {total_events:,} 건의 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()