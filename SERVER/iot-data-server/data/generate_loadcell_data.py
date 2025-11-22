import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "loadcell_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "loadcell_data.sql"
CRISIS_EVENT_PROBABILITY = 0.001 # 0.1%
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

def get_random_time(base_time, plus_minutes_max):
    """기준 시간에 랜덤한 분/초/마이크로초를 더해 고유한 시간을 만듭니다."""
    return base_time + timedelta(
        minutes=random.randint(0, plus_minutes_max),
        seconds=random.randint(0, 59),
        microseconds=random.randint(0, 999999)
    )

def main():
    user_devices = read_device_info()
    if not user_devices: return

    print(f"총 {len(user_devices)}명의 사용자에 대한 로드셀 데이터 생성을 시작합니다...")
    
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        total_events = 0
        for user_id, devices in user_devices.items():
            print(f"사용자 {user_id[:8]}... 의 데이터 생성 중...")

            bedroom_sensor = next((d for d in devices if 'Bedroom' in d['location_label']), None)
            kitchen_sensors = [d for d in devices if 'Kitchen' in d['location_label']]
            
            kitchen_inventory = {}
            if len(kitchen_sensors) > 0:
                kitchen_inventory[kitchen_sensors[0]['device_id']] = {'name': 'Rice', 'max': 10.0, 'current': 10.0}
            if len(kitchen_sensors) > 1:
                kitchen_inventory[kitchen_sensors[1]['device_id']] = {'name': 'Water', 'max': 12.0, 'current': 12.0}

            for i in range(NUM_DAYS):
                current_date = datetime.now() - timedelta(days=i)
                daily_events = []

                if bedroom_sensor:
                    sleep_start_time = get_random_time(current_date.replace(hour=22), 120)
                    wake_up_offset = timedelta(hours=random.randint(7,9), seconds=random.randint(0, 59), microseconds=random.randint(0,999999))
                    wake_up_time = sleep_start_time + wake_up_offset
                    user_weight = round(random.uniform(50, 70), 2)
                    
                    daily_events.append({'time': sleep_start_time, 'device_id': bedroom_sensor['device_id'], 'weight': user_weight, 'type': 'sleep_start'})
                    daily_events.append({'time': wake_up_time, 'device_id': bedroom_sensor['device_id'], 'weight': 0.0, 'type': 'sleep_end'})

                    # --- 수정된 부분: 야간 활동 시간 생성 시 초와 마이크로초 추가 ---
                    for _ in range(random.randint(1, 2)):
                        out_of_bed_offset = timedelta(hours=random.randint(1, 6), seconds=random.randint(0,59), microseconds=random.randint(0,999999))
                        return_offset = timedelta(minutes=random.randint(5, 15), seconds=random.randint(0,59), microseconds=random.randint(0,999999))
                        out_of_bed_time = sleep_start_time + out_of_bed_offset
                        return_time = out_of_bed_time + return_offset
                        daily_events.append({'time': out_of_bed_time, 'device_id': bedroom_sensor['device_id'], 'weight': 0.0, 'type': 'night_movement_start'})
                        daily_events.append({'time': return_time, 'device_id': bedroom_sensor['device_id'], 'weight': user_weight, 'type': 'night_movement_end'})
                    
                    if random.random() < CRISIS_EVENT_PROBABILITY:
                         crisis_offset = timedelta(hours=random.randint(2, 5), seconds=random.randint(0,59), microseconds=random.randint(0,999999))
                         crisis_time = sleep_start_time + crisis_offset
                         daily_events.append({'time': crisis_time, 'device_id': bedroom_sensor['device_id'], 'weight': 0.0, 'type': 'crisis_not_returned_to_bed'})


                for dev_id, item in kitchen_inventory.items():
                    if random.randint(1, 10) == 1:
                        item['current'] = item['max']
                        restock_time = get_random_time(current_date.replace(hour=14), 240)
                        daily_events.append({'time': restock_time, 'device_id': dev_id, 'weight': item['current'], 'type': f"{item['name']}_restock"})

                    # --- 수정된 부분: 식료품 소모 시간 생성 시 초와 마이크로초 추가 ---
                    for hour in [8, 13, 18]:
                        if item['current'] > 0:
                            consumption = item['max'] * random.uniform(0.01, 0.03)
                            item['current'] = max(0, item['current'] - consumption)
                            consumption_time = get_random_time(current_date.replace(hour=hour), 60)
                            daily_events.append({'time': consumption_time, 'device_id': dev_id, 'weight': round(item['current'],2), 'type': f"{item['name']}_consumption"})
                
                if random.random() < 0.05:
                     attention_time = get_random_time(current_date.replace(hour=20), 60)
                     for dev_id, item in kitchen_inventory.items():
                         daily_events.append({'time': attention_time, 'device_id': dev_id, 'weight': round(item['current'],2), 'type': f"attention_no_consumption"})

                for event in sorted(daily_events, key=lambda x: x['time']):
                    total_events += 1
                    payload = { "event_type": event['type'], "weight_kg": event['weight'] }
                    time_val = event['time'].strftime('%Y-%m-%d %H:%M:%S.%f')
                    payload_val = json.dumps(payload).replace("'", "''")
                    sql = f"INSERT INTO sensor_raw_loadcell (time, device_id, raw_payload) VALUES ('{time_val}', '{event['device_id']}', '{payload_val}');"
                    f.write(sql + "\n")

    print(f"\n총 약 {total_events:,} 건의 로드셀 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()