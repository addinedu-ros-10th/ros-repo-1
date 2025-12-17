import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "pir_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "pir_data.sql"
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

def generate_daily_pattern_events(user_devices_list, base_date):
    """하루 동안의 생활 패턴에 따른 이벤트 목록을 생성합니다."""
    events = []
    
    device_map = {label.split(' - ')[0]: dev['device_id'] for dev in user_devices_list for label in [dev['location_label']]}

    # 시간대별 활동 시뮬레이션
    # 1. 기상 (6:00 ~ 7:00)
    wakeup_time = base_date.replace(hour=6, minute=random.randint(0, 59))
    for _ in range(random.randint(5, 15)):
        # --- 수정된 부분: 초와 마이크로초를 랜덤하게 추가하여 시간 고유성 보장 ---
        event_time = wakeup_time + timedelta(
            minutes=random.randint(0, 60), 
            seconds=random.randint(0, 59), 
            microseconds=random.randint(0, 999999)
        )
        location_key = random.choice(['Bedroom', 'Bathroom'])
        if device_map.get(location_key):
            events.append({'time': event_time, 'device_id': device_map[location_key]})

    # 2. 아침식사 (7:00 ~ 9:00)
    breakfast_time = base_date.replace(hour=random.randint(7, 8), minute=random.randint(0, 59))
    for _ in range(random.randint(10, 20)):
        event_time = breakfast_time + timedelta(
            minutes=random.randint(0, 90), 
            seconds=random.randint(0, 59), 
            microseconds=random.randint(0, 999999)
        )
        location_key = random.choice(['Kitchen', 'Living Room'])
        if device_map.get(location_key):
            events.append({'time': event_time, 'device_id': device_map[location_key]})

    # 3. 낮 활동 및 외출 (10:00 ~ 17:00)
    if random.random() < 0.7:
        out_time = base_date.replace(hour=random.randint(10, 13), minute=random.randint(0, 59), second=random.randint(0, 59))
        in_time = out_time + timedelta(hours=random.randint(1, 4), minutes=random.randint(0, 59))
        if device_map.get('Entrance'):
            events.append({'time': out_time, 'device_id': device_map['Entrance']})
            events.append({'time': in_time, 'device_id': device_map['Entrance']})
    
    for _ in range(random.randint(30, 60)):
        event_time = base_date.replace(
            hour=random.randint(9, 17), 
            minute=random.randint(0, 59),
            second=random.randint(0, 59), 
            microsecond=random.randint(0, 999999)
        )
        if device_map.get('Living Room'):
            events.append({'time': event_time, 'device_id': device_map['Living Room']})

    # 4. 저녁 및 취침 준비 (18:00 ~ 22:00)
    dinner_time = base_date.replace(hour=random.randint(18, 19), minute=random.randint(0, 59))
    for _ in range(random.randint(40, 70)):
        event_time = dinner_time + timedelta(
            minutes=random.randint(0, 240),
            seconds=random.randint(0, 59), 
            microseconds=random.randint(0, 999999)
        )
        location_key = random.choice(['Kitchen', 'Living Room', 'Bathroom', 'Bedroom'])
        if device_map.get(location_key):
            events.append({'time': event_time, 'device_id': device_map[location_key]})
            
    return sorted(events, key=lambda x: x['time'])


def main():
    """메인 실행 함수"""
    user_devices = read_device_info()
    if not user_devices:
        print("데이터 생성을 중단합니다.")
        return

    print(f"총 {len(user_devices)}명의 사용자에 대한 데이터 생성을 시작합니다...")
    
    today = datetime.now()
    total_events = 0
    
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        for user_id, devices in user_devices.items():
            print(f"사용자 {user_id[:8]}... 의 데이터 생성 중...")
            for i in range(NUM_DAYS):
                current_date = today - timedelta(days=i)
                daily_events = generate_daily_pattern_events(devices, current_date)
                total_events += len(daily_events)
                
                for event in daily_events:
                    confidence = round(random.uniform(0.85, 1.0), 2)
                    processing_time = round(random.uniform(5.0, 50.0), 2)
                    
                    payload = {
                        "confidence": confidence,
                        "motion_direction": random.choice(['left-to-right', 'towards-sensor', 'away-from-sensor']),
                        "motion_speed": round(random.uniform(0.5, 1.5), 2),
                        "processing_time_ms": processing_time,
                        "raw_signal_voltage": round(random.uniform(3.1, 3.3), 2)
                    }
                    
                    time_val = event['time'].strftime('%Y-%m-%d %H:%M:%S.%f %z')
                    payload_val = json.dumps(payload).replace("'", "''")
                    
                    sql = f"INSERT INTO sensor_edge_pir (time, device_id, motion_detected, confidence, processing_time, raw_payload) VALUES ('{time_val}', '{event['device_id']}', true, {confidence}, {processing_time}, '{payload_val}');"
                    f.write(sql + "\n")

    print(f"\n총 약 {total_events:,} 건의 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()