import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "reed_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "reed_data.sql"
# ----------------

def read_device_ids():
    """파일에서 device_id 목록을 읽어옵니다."""
    try:
        with open(DEVICE_INFO_FILENAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            device_ids = [row['device_id'] for row in reader]
        return device_ids
    except FileNotFoundError:
        print(f"오류: '{DEVICE_INFO_FILENAME}' 파일을 찾을 수 없습니다.")
        print("먼저 'get_device_ids.py' 스크립트를 실행하여 디바이스 ID 목록을 생성해주세요.")
        return []

def generate_daily_outing_events(base_date):
    """하루 동안의 외출/귀가 이벤트 쌍을 생성합니다."""
    events = []
    
    rand_val = random.random()
    if rand_val < 0.75:
        num_outings = 1
    elif rand_val < 0.90:
        num_outings = 0
    else:
        num_outings = 2

    outing_times = sorted([random.randint(9, 18) for _ in range(num_outings)])

    for hour in outing_times:
        start_time = base_date.replace(hour=hour, minute=random.randint(0, 59))
        
        # --- 수정된 부분: 모든 timedelta에 microseconds 추가 ---
        # 외출 이벤트 (문 열림 -> 닫힘)
        open_time = start_time + timedelta(seconds=random.randint(1, 5), microseconds=random.randint(0, 999999))
        close_time = open_time + timedelta(seconds=random.randint(5, 15), microseconds=random.randint(0, 999999))
        events.append({'time': open_time, 'state': False})
        events.append({'time': close_time, 'state': True})

        # 귀가 이벤트 (문 열림 -> 닫힘)
        return_time = start_time + timedelta(hours=random.randint(1, 5), minutes=random.randint(0, 59))
        open_time_return = return_time + timedelta(seconds=random.randint(1, 5), microseconds=random.randint(0, 999999))
        close_time_return = open_time_return + timedelta(seconds=random.randint(5, 15), microseconds=random.randint(0, 999999))
        events.append({'time': open_time_return, 'state': False})
        events.append({'time': close_time_return, 'state': True})

    return sorted(events, key=lambda x: x['time'])

def main():
    """메인 실행 함수"""
    device_ids = read_device_ids()
    if not device_ids:
        print("데이터 생성을 중단합니다.")
        return

    print(f"총 {len(device_ids)}개의 디바이스에 대한 데이터 생성을 시작합니다...")
    
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        for device_id in device_ids:
            today = datetime.now()
            for i in range(NUM_DAYS):
                current_date = today - timedelta(days=i)
                daily_events = generate_daily_outing_events(current_date)
                
                for event in daily_events:
                    switch_state = event['state']
                    
                    payload = {
                        "magnetic_field_detected": switch_state,
                        "magnetic_strength_gauss": round(random.uniform(300, 400), 2) if switch_state else round(random.uniform(0, 10), 2),
                        "confidence": round(random.uniform(0.95, 1.0), 2),
                        "processing_time_ms": round(random.uniform(1.0, 10.0), 2)
                    }
                    
                    time_val = event['time'].strftime('%Y-%m-%d %H:%M:%S.%f %z')
                    payload_val = json.dumps(payload).replace("'", "''")
                    
                    sql = (f"INSERT INTO sensor_edge_reed "
                           f"(time, device_id, switch_state, magnetic_field_detected, confidence, magnetic_strength, processing_time, raw_payload) "
                           f"VALUES ('{time_val}', '{device_id}', {switch_state}, {payload['magnetic_field_detected']}, "
                           f"{payload['confidence']}, {payload['magnetic_strength_gauss']}, {payload['processing_time_ms']}, '{payload_val}');")
                    f.write(sql + "\n")
    
    with open(OUTPUT_FILENAME, "r", encoding="utf-8") as f:
        total_events = len(f.readlines())

    print(f"\n총 약 {total_events:,} 건의 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()