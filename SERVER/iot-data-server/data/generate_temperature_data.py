import csv
import random
import json
from datetime import datetime, timedelta

# --- 설정 ---
DEVICE_INFO_FILENAME = "temperature_devices.csv"
NUM_DAYS = 180
OUTPUT_FILENAME = "temperature_data.sql"
# ----------------

def read_device_ids():
    """파일에서 device_id 목록을 읽어옵니다."""
    try:
        with open(DEVICE_INFO_FILENAME, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return [row['device_id'] for row in reader]
    except FileNotFoundError:
        print(f"오류: '{DEVICE_INFO_FILENAME}' 파일을 찾을 수 없습니다.")
        return None

def get_seasonal_baseline(date):
    """날짜에 따라 계절별 기본 온도를 반환합니다."""
    month = date.month
    if month in [6, 7, 8]: return 26.0  # 여름
    if month in [12, 1, 2]: return 18.0  # 겨울
    if month in [3, 4, 5]: return 20.0   # 봄
    return 22.0 # 가을

def generate_daily_temp_events(base_date):
    """하루 동안의 온도/습도 변화 이벤트 목록을 생성합니다."""
    events = {} # time: {temp, humidity}
    
    baseline_temp = get_seasonal_baseline(base_date)
    
    # 1. 주기적 측정 (10분 간격)
    current_time = base_date.replace(hour=0, minute=0, second=0)
    end_of_day = current_time + timedelta(days=1)
    
    while current_time < end_of_day:
        # 일일 온도 변화 (밤에 낮고 낮에 높음)
        daily_fluctuation = (current_time.hour - 12) / 12.0 # -1 to 1 scale
        temp = baseline_temp - (daily_fluctuation * 2) + random.uniform(-0.5, 0.5)
        humidity = 50 + (daily_fluctuation * -10) + random.uniform(-5, 5) # 온도가 높으면 습도 낮음
        
        events[current_time] = {'temp': round(temp, 2), 'humidity': round(humidity, 2)}
        current_time += timedelta(minutes=10)

    # 2. 샤워 이벤트 (기존 측정값 덮어쓰기)
    num_showers = random.choice([1, 1, 1, 2]) # 하루 1~2회
    shower_hours = random.sample([random.randint(6,9), random.randint(19,22)], num_showers)
    
    for hour in shower_hours:
        shower_start_time = base_date.replace(hour=hour, minute=random.randint(0, 59))
        
        # 샤워 중 (온도/습도 급상승)
        for i in range(3): # 0, 5, 10분 후
            t = shower_start_time + timedelta(minutes=i*5)
            temp = baseline_temp + random.uniform(5, 8)
            humidity = random.uniform(85, 98)
            events[t] = {'temp': round(temp, 2), 'humidity': round(humidity, 2)}
            
        # 샤워 후 (서서히 복귀)
        for i in range(1, 5): # 20, 30, 40, 50분 후
            t = shower_start_time + timedelta(minutes=10 + i*10)
            temp_decrease = (i/4) * 5 # 점차 5도 감소
            humidity_decrease = (i/4) * 40 # 점차 40% 감소
            events[t] = {
                'temp': round(baseline_temp + random.uniform(3, 5) - temp_decrease, 2),
                'humidity': round(80 - humidity_decrease, 2)
            }

    return sorted(events.items())


def main():
    """메인 실행 함수"""
    device_ids = read_device_ids()
    if not device_ids: return

    print(f"총 {len(device_ids)}개의 디바이스에 대한 온도 데이터 생성을 시작합니다...")
    
    total_events = 0
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        for device_id in device_ids:
            print(f"디바이스 {device_id[:18]}... 의 데이터 생성 중...")
            for i in range(NUM_DAYS):
                current_date = datetime.now() - timedelta(days=i)
                daily_events = generate_daily_temp_events(current_date)
                
                for time, data in daily_events:
                    total_events += 1
                    payload = {
                        "temperature_celsius": data['temp'],
                        "humidity_percent": data['humidity'],
                        "unit": "metric"
                    }
                    
                    time_val = time.strftime('%Y-%m-%d %H:%M:%S.%f')
                    payload_val = json.dumps(payload).replace("'", "''")
                    
                    sql = (f"INSERT INTO sensor_raw_temperature (time, device_id, temperature_celsius, humidity_percent, raw_payload) "
                           f"VALUES ('{time_val}', '{device_id}', {data['temp']}, {data['humidity']}, '{payload_val}');")
                    f.write(sql + "\n")

    print(f"\n총 약 {total_events:,} 건의 온도 데이터가 생성되었습니다.")
    print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")

if __name__ == "__main__":
    main()