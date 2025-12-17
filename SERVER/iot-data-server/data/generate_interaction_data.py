import csv
import random
import json
import psycopg2
from datetime import datetime, timedelta

from dotenv import load_dotenv
import os
import csv

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
    "host": DB_HOST,
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "port": DB_PORT
}
# ---------------------------------------------

OUTPUT_FILENAME = "interaction_data.sql"

def read_device_info_from_csv(filename):
    user_devices = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['user_id']
                if user_id not in user_devices: user_devices[user_id] = []
                user_devices[user_id].append(row)
        return user_devices
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다. 먼저 get_device_ids.py를 실행하세요.")
        return None

def fetch_all_sensor_data_for_user(cursor, user_id):
    """DB에서 특정 사용자의 모든 센서 데이터를 시간순으로 가져옵니다."""
    # --- 수정된 부분: sensor_edge_reed 쿼리 추가 ---
    queries = {
        'pir': "SELECT time, device_id, raw_payload, location_label FROM sensor_edge_pir p JOIN devices d ON p.device_id = d.device_id WHERE d.user_id = %s",
        'rfid': "SELECT time, device_id, raw_payload FROM sensor_raw_rfid WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)",
        'reed': "SELECT time, device_id, raw_payload FROM sensor_edge_reed WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)",
        'sound': "SELECT time, device_id, raw_payload FROM sensor_raw_sound WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)",
        'loadcell': "SELECT time, device_id, raw_payload, location_label FROM sensor_raw_loadcell l JOIN devices d ON l.device_id = d.device_id WHERE d.user_id = %s",
        'temperature': "SELECT time, device_id, raw_payload, temperature_celsius FROM sensor_raw_temperature WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)",
        'mq5': "SELECT time, device_id, raw_payload FROM sensor_raw_mq5 WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)",
        'mq7': "SELECT time, device_id, raw_payload FROM sensor_raw_mq7 WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)",
    }
    
    all_events = []
    print(f"    - DB에서 {user_id[:8]}... 의 모든 센서 데이터 조회 중...")
    for sensor_type, query in queries.items():
        cursor.execute(query, (user_id,))
        for row in cursor.fetchall():
            event = {'time': row[0], 'device_id': row[1], 'payload': row[2], 'type': sensor_type}
            if 'location_label' in query: event['location'] = row[3]
            if 'temperature_celsius' in query: event['value'] = row[3]
            all_events.append(event)
            
    return sorted(all_events, key=lambda x: x['time'])

def check_rules(state, current_time):
    """(고도화 버전) 현재 상태를 기반으로 규칙을 확인하고, 발동된 이벤트 정보를 반환합니다."""
    # --- 응급(Emergency) 규칙 ---
    if state.get('gas_level', 0) > 1000:
        return {'priority': 'emergency', 'reason': 'emergency_gas_leak_detected'}
    if state.get('last_sound_type') in ['shout_for_help', 'thud_fall']:
        if state.get('last_crisis_sound_time') != state.get('last_sound_time'):
            state['last_crisis_sound_time'] = state.get('last_sound_time')
            return {'priority': 'emergency', 'reason': 'emergency_scream_or_fall_detected'}
            
    # --- 주의(Warning) 규칙 ---
    if state.get('last_location') == 'Bathroom' and (current_time - state.get('last_motion_time', current_time)).total_seconds() > 1800: # 30분
        if not state.get('is_sleeping', False):
             return {'priority': 'warning', 'reason': 'warning_no_movement_in_bathroom'}
    if state.get('is_out', False) and (current_time - state.get('last_rfid_time', current_time)).total_seconds() > 86400: # 24시간
         return {'priority': 'warning', 'reason': 'warning_long_absence'}
    if state.get('temperature', 22) > 30 or state.get('temperature', 22) < 10:
        return {'priority': 'warning', 'reason': 'warning_extreme_temperature'}

    # --- 관심(Attention) 규칙 ---
    current_hour = current_time.hour
    if current_hour in [12, 13, 18, 19]: # 점심/저녁 시간
        if (current_time - state.get('last_kitchen_activity_time', current_time)).total_seconds() > 14400: # 4시간
            return {'priority': 'attention', 'reason': 'attention_meal_skipped_suspected'}
    if not state.get('is_out', False) and (current_time - state.get('last_motion_time', current_time)).total_seconds() > 43200: # 12시간
        return {'priority': 'attention', 'reason': 'attention_no_movement_12h'}
    
    return None

def main():
    buzzer_devices_by_user = read_device_info_from_csv("buzzer_devices.csv")
    button_devices_by_user = read_device_info_from_csv("button_devices.csv")
    if not buzzer_devices_by_user or not button_devices_by_user: return

    sql_statements = ["BEGIN;", "TRUNCATE TABLE actuator_log_buzzer, sensor_event_button;"]
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for user_id in buzzer_devices_by_user.keys():
            user_timeline = fetch_all_sensor_data_for_user(cur, user_id)
            if not user_timeline: continue
            
            user_state = {'last_motion_time': datetime.min.replace(tzinfo=user_timeline[0]['time'].tzinfo),
                          'last_kitchen_activity_time': datetime.min.replace(tzinfo=user_timeline[0]['time'].tzinfo)}
            last_buzzer_time = datetime.min.replace(tzinfo=user_timeline[0]['time'].tzinfo)

            for event in user_timeline:
                # 1. 상태 업데이트
                if event['type'] == 'pir':
                    user_state['last_motion_time'] = event['time']
                    user_state['last_location'] = event.get('location', '').split(' - ')[0].strip()
                    if user_state['last_location'] == 'Kitchen':
                        user_state['last_kitchen_activity_time'] = event['time']
                if event['type'] == 'sound': 
                    user_state['last_sound_type'] = event['payload'].get('event_type')
                    user_state['last_sound_time'] = event['time']
                if event['type'] == 'mq5': user_state['gas_level'] = event['payload'].get('gas_ppm')
                if event['type'] == 'mq7': user_state['co_level'] = event['payload'].get('co_ppm')
                if event['type'] == 'rfid':
                    user_state['is_out'] = (event['payload'].get('status') == 'out')
                    user_state['last_rfid_time'] = event['time']
                if event['type'] == 'loadcell' and 'Bedroom' in event.get('location', ''):
                    user_state['is_sleeping'] = (event['payload'].get('event_type') == 'sleep_start')
                if event['type'] == 'temperature': user_state['temperature'] = event.get('value')
                # reed switch 상태 업데이트 추가
                if event['type'] == 'reed':
                    user_state['door_is_open'] = not event['payload'].get('switch_state', True)

                # 2. 규칙 확인 (단, 부저가 울리고 10분 내에는 중복 확인 안함)
                if (event['time'] - last_buzzer_time).total_seconds() > 600:
                    triggered_event = check_rules(user_state, event['time'])
                    if triggered_event:
                        buzzer_device_id = buzzer_devices_by_user[user_id][0]['device_id']
                        button_device = random.choice(button_devices_by_user.get(user_id, []))
                        if not button_device: continue
                        
                        # 3. 상호작용 SQL 생성
                        buzzer_on_time = event['time'] + timedelta(seconds=1)
                        on_payload = json.dumps({"event_trigger": triggered_event['reason'], "priority": triggered_event['priority'].upper()}).replace("'", "''")
                        sql_statements.append(f"INSERT INTO actuator_log_buzzer (time, device_id, buzzer_type, state, reason, raw_payload) VALUES ('{buzzer_on_time.isoformat()}', '{buzzer_device_id}', 'passive', 'ON', '{triggered_event['reason']}', '{on_payload}');")
                        
                        button_press_time = buzzer_on_time + timedelta(seconds=random.randint(10, 300))
                        button_payload = json.dumps({"acknowledged_event": triggered_event['reason']}).replace("'", "''")
                        sql_statements.append(f"INSERT INTO sensor_event_button (time, device_id, button_state, event_type, raw_payload) VALUES ('{button_press_time.isoformat()}', '{button_device['device_id']}', 'PRESSED', 'crisis_acknowledged', '{button_payload}');")
                        
                        buzzer_off_time = button_press_time + timedelta(seconds=1)
                        off_payload = json.dumps({"action": "user_acknowledged"}).replace("'", "''")
                        sql_statements.append(f"INSERT INTO actuator_log_buzzer (time, device_id, buzzer_type, state, reason, raw_payload) VALUES ('{buzzer_off_time.isoformat()}', '{buzzer_device_id}', 'passive', 'OFF', 'user_acknowledged', '{off_payload}');")
                        
                        last_buzzer_time = buzzer_off_time
                        user_state['last_sound_type'] = None

            # 독립 이벤트 (복약 체크) 추가
            kitchen_button = next((d for d in button_devices_by_user.get(user_id, []) if 'Kitchen' in d['location_label']), None)
            if kitchen_button:
                for i in range(180):
                    day = datetime.now() - timedelta(days=i)
                    for hour in [8, 20]:
                        med_time = day.replace(hour=hour, minute=random.randint(0,59), second=random.randint(0,59))
                        med_payload = json.dumps({"check_time": med_time.strftime('%H:%M')}).replace("'", "''")
                        sql_statements.append(f"INSERT INTO sensor_event_button (time, device_id, button_state, event_type, raw_payload) VALUES ('{med_time.isoformat()}', '{kitchen_button['device_id']}', 'PRESSED', 'medication_check', '{med_payload}');")

        sql_statements.append("COMMIT;")
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f: f.write("\n".join(sql_statements))
        print(f"\n총 {len(sql_statements) - 2} 건의 상호작용 데이터가 생성되었습니다.")
        print(f"'{OUTPUT_FILENAME}' 파일 생성이 완료되었습니다.")
    except (Exception, psycopg2.Error) as error:
        print("오류: ", error)
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    main()