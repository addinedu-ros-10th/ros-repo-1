import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "buzzer_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "buzzer_data.sql"
# ----------------

# --- 이벤트 발생 확률 정의 ---
PROB_ATTENTION = 0.10  # 관심 (10%)
PROB_WARNING = 0.02    # 주의 (2%)
PROB_EMERGENCY = 0.005 # 응급 (0.5%)
# ----------------------------

def read_device_ids():
    """파일에서 device_id 목록을 읽어옵니다."""
    try:
        with open(DEVICE_INFO_FILENAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row['device_id'] for row in reader]
    except FileNotFoundError:
        print(f"오류: '{DEVICE_INFO_FILENAME}' 파일을 찾을 수 없습니다.")
        return None

def get_random_time(base_date):
    """하루 중 랜덤한 시간을 생성합니다."""
    return base_date.replace(hour=random.randint(0, 23), minute=random.randint(0, 59)) + \
           timedelta(seconds=random.randint(0, 59), microseconds=random.randint(0, 999999))

def main():
    """메인 실행 함수"""
    device_ids = read_device_ids()
    if not device_ids: return

    print(f"총 {len(device_ids)}개의 디바이스에 대한 부저 로그 생성을 시작합니다...")
    
    event_definitions = {
        'attention': {'reason': 'attention_no_movement_24h', 'freq': 1000, 'duration': 1000, 'off_delay_mins': 5},
        'warning': {'reason': 'warning_fall_no_response', 'freq': 2000, 'duration': 3000, 'off_delay_mins': 10},
        'emergency': {'reason': 'emergency_gas_leak_detected', 'freq': 3500, 'duration': 10000, 'off_delay_mins': 60}
    }
    
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        total_events = 0
        for device_id in device_ids:
            # print(f"디바이스 {device_id[:18]}... 의 데이터 생성 중...")
            for i in range(NUM_DAYS):
                current_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=i)
                
                event_type = None
                rand_val = random.random()
                if rand_val < PROB_EMERGENCY:
                    event_type = 'emergency'
                elif rand_val < PROB_EMERGENCY + PROB_WARNING:
                    event_type = 'warning'
                elif rand_val < PROB_EMERGENCY + PROB_WARNING + PROB_ATTENTION:
                    event_type = 'attention'

                if event_type:
                    total_events += 1
                    event_time = get_random_time(current_date)
                    event_info = event_definitions[event_type]
                    
                    # --- ON/BEEP 이벤트 로그 생성 ---
                    on_payload = { "event_trigger": event_info['reason'], "priority": event_type.upper() }
                    on_sql = (f"INSERT INTO actuator_log_buzzer (time, device_id, buzzer_type, state, freq_hz, duration_ms, reason, raw_payload) "
                              f"VALUES ('{event_time.strftime('%Y-%m-%d %H:%M:%S.%f')}', '{device_id}', 'passive', 'ON', "
                              f"{event_info['freq']}, {event_info['duration']}, '{event_info['reason']}', '{json.dumps(on_payload)}');")
                    f.write(on_sql + "\n")
                    
                    # --- OFF 이벤트 로그 생성 ---
                    off_time = event_time + timedelta(minutes=event_info['off_delay_mins'])
                    off_payload = { "event_trigger": event_info['reason'], "priority": event_type.upper(), "action": "user_acknowledged" }
                    off_sql = (f"INSERT INTO actuator_log_buzzer (time, device_id, buzzer_type, state, reason, raw_payload) "
                               f"VALUES ('{off_time.strftime('%Y-%m-%d %H:%M:%S.%f')}', '{device_id}', 'passive', 'OFF', "
                               f"'user_acknowledged', '{json.dumps(off_payload)}');")
                    f.write(off_sql + "\n")

    print(f"\n총 약 {total_events * 2:,} 건의 부저 로그 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")


if __name__ == "__main__":
    main()