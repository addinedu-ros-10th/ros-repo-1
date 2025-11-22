import csv
import random
import json
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# --- .env 파일에서 DB 접속 정보 로드 ---
load_dotenv('../.env.local')
DB_CONFIG = {
    "host": os.getenv("DB_HOST"), "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"), "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432")
}
# -----------------------------------------

def read_device_info_from_csv(filename):
    user_devices = {}
    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                user_id = row['user_id']
                if user_id not in user_devices: user_devices[user_id] = []
                user_devices[user_id].append(row)
    except FileNotFoundError:
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다. 1단계 가이드를 먼저 실행하세요.")
        exit()
    return user_devices

def fetch_all_sensor_data_for_user(cursor, user_id):
    queries = { 'pir': "SELECT time, p.device_id, raw_payload, d.location_label FROM sensor_edge_pir p JOIN devices d ON p.device_id = d.device_id WHERE d.user_id = %s", 'rfid': "SELECT time, device_id, raw_payload FROM sensor_raw_rfid WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)", 'reed': "SELECT time, device_id, raw_payload FROM sensor_edge_reed WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)", 'sound': "SELECT time, s.device_id, raw_payload, d.location_label FROM sensor_raw_sound s JOIN devices d ON s.device_id = d.device_id WHERE d.user_id = %s", 'loadcell': "SELECT time, l.device_id, raw_payload, d.location_label FROM sensor_raw_loadcell l JOIN devices d ON l.device_id = d.device_id WHERE d.user_id = %s", 'temperature': "SELECT time, device_id, raw_payload, temperature_celsius FROM sensor_raw_temperature WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)", 'mq5': "SELECT time, device_id, raw_payload FROM sensor_raw_mq5 WHERE device_id IN (SELECT device_id FROM devices WHERE user_id = %s)", 'mq7': "SELECT time, m.device_id, raw_payload, d.location_label FROM sensor_raw_mq7 m JOIN devices d ON m.device_id = d.device_id WHERE d.user_id = %s", }
    all_events = []
    print(f"    - DB에서 {user_id[:8]}... 의 모든 센서 데이터 조회 중...")
    for sensor_type, query in queries.items():
        cursor.execute(query, (user_id,))
        for row in cursor.fetchall():
            event = {'time': row[0], 'device_id': row[1], 'payload': row[2] or {}, 'type': sensor_type}
            if sensor_type in ['pir', 'sound', 'loadcell', 'mq7']: event['location'] = row[3]
            if sensor_type == 'temperature': event['value'] = row[3]
            all_events.append(event)
    return sorted(all_events, key=lambda x: x['time'])

class HomeState:
    """사용자의 집 전체 상태를 관리하는 클래스"""
    def __init__(self, user_id):
        self.user_id = user_id
        self.state = {
            'time': None, 'user_id': self.user_id, 'entrance_pir_motion': False, 'entrance_rfid_status': 'in', 'entrance_reed_is_closed': True, 'livingroom_pir_1_motion': False, 'livingroom_pir_2_motion': False, 'livingroom_sound_db': 0, 'livingroom_mq7_co_ppm': 10, 'livingroom_button_state': None, 'kitchen_pir_motion': False, 'kitchen_sound_db': 0, 'kitchen_mq5_gas_ppm': 200, 'kitchen_loadcell_1_kg': 10.0, 'kitchen_loadcell_2_kg': 12.0, 'kitchen_button_state': None, 'kitchen_buzzer_is_on': False, 'bedroom_pir_motion': False, 'bedroom_sound_db': 0, 'bedroom_mq7_co_ppm': 10, 'bedroom_loadcell_kg': 0.0, 'bedroom_button_state': None, 'bathroom_pir_motion': False, 'bathroom_sound_db': 0, 'bathroom_temp_celsius': 22.0, 'bathroom_button_state': None, 'detected_activity': 'Idle', 'alert_level': 'Normal', 'alert_reason': None, 'action_log': None, 'extra_data': None
        }
        self.last_known_state = self.state.copy()

    def update_and_get_snapshot(self, event):
        """이벤트를 기반으로 상태를 업데이트하고 현재 스냅샷을 반환합니다."""
        # 이전 상태를 현재 상태로 복사
        self.state = self.last_known_state.copy()
        self.state['time'] = event['time']
        self.state.update({'alert_level': 'Normal', 'alert_reason': None, 'action_log': None}) # 기본값 초기화
        
        # --- 센서 유형별 상태 업데이트 (완성된 로직) ---
        evt_type = event['type']
        payload = event['payload']
        location = event.get('location', '')

        if evt_type == 'pir':
            # device_id의 마지막 부분을 보고 어떤 PIR인지 구분
            part_name = event['device_id'].rsplit('_', 1)[-1]
            if part_name == '1': self.state['entrance_pir_motion'] = True
            elif part_name == '2': self.state['livingroom_pir_1_motion'] = True
            elif part_name == '3': self.state['livingroom_pir_2_motion'] = True
            elif part_name == '4': self.state['kitchen_pir_motion'] = True
            elif part_name == '5': self.state['bathroom_pir_motion'] = True 
            elif part_name == '6': self.state['bedroom_pir_motion'] = True
        elif evt_type == 'rfid': self.state['entrance_rfid_status'] = payload.get('status', 'in')
        elif evt_type == 'reed': self.state['entrance_reed_is_closed'] = payload.get('switch_state', True)
        elif evt_type == 'sound':
            db = payload.get('db_level', 0)
            if 'Living Room' in location: self.state['livingroom_sound_db'] = db
            elif 'Kitchen' in location: self.state['kitchen_sound_db'] = db
            elif 'Bedroom' in location: self.state['bedroom_sound_db'] = db
            elif 'Bathroom' in location: self.state['bathroom_sound_db'] = db
        elif evt_type == 'mq5': self.state['kitchen_mq5_gas_ppm'] = payload.get('gas_ppm', 200)
        elif evt_type == 'mq7':
            ppm = payload.get('co_ppm', 10)
            if 'Living Room' in location: self.state['livingroom_mq7_co_ppm'] = ppm
            elif 'Bedroom' in location: self.state['bedroom_mq7_co_ppm'] = ppm
        elif evt_type == 'loadcell':
            kg = payload.get('weight_kg', 0)
            if 'Bedroom' in location: self.state['bedroom_loadcell_kg'] = kg
            else: # Kitchen
                part_name = event['device_id'].rsplit('_', 1)[-1]
                if part_name == '1': self.state['kitchen_loadcell_1_kg'] = kg
                elif part_name == '2': self.state['kitchen_loadcell_2_kg'] = kg
        elif evt_type == 'temperature': self.state['bathroom_temp_celsius'] = event.get('value', 22.0)
        
        self.last_known_state = self.state.copy() # 마지막 상태 업데이트
        return self.state.copy()

    # --- 추가된 함수 ---
    def get_current_state(self):
        """현재 상태의 복사본을 반환합니다."""
        return self.state.copy()

def check_rules(state, current_time):
    """(고도화 버전) 현재 상태를 기반으로 규칙을 확인하고, 발동된 이벤트 정보를 반환합니다."""
    
    # --- 응급(Emergency) 규칙 ---
    # 화재 위험: CO 농도 50ppm 초과 & 온도 40도 초과
    if state.get('livingroom_mq7_co_ppm', 10) > 50 and state.get('bathroom_temp_celsius', 22) > 40:
        return {'priority': 'emergency', 'reason': 'emergency_fire_risk_detected'}
    if state.get('bedroom_mq7_co_ppm', 10) > 50 and state.get('bathroom_temp_celsius', 22) > 40:
        return {'priority': 'emergency', 'reason': 'emergency_fire_risk_detected'}
    
    # 가스 누출
    if state.get('kitchen_mq5_gas_ppm', 200) > 1000:
        return {'priority': 'emergency', 'reason': 'emergency_gas_leak_detected'}
        
    # 비명 또는 낙상 소리 감지
    if state.get('last_sound_type') in ['shout_for_help', 'thud_fall']:
        # 동일한 소리 이벤트로 중복 알림이 발생하는 것을 방지
        if state.get('last_crisis_sound_time') != state.get('last_sound_time'):
            state['last_crisis_sound_time'] = state.get('last_sound_time') # 처리된 이벤트로 기록
            return {'priority': 'emergency', 'reason': 'emergency_scream_or_fall_detected'}
            
    # --- 주의(Warning) 규칙 ---
    # 욕실 내 장시간 움직임 없음
    if state.get('last_location') == 'Bathroom' and (current_time - state.get('last_motion_time', current_time)).total_seconds() > 1800: # 30분
        if not state.get('is_sleeping', False): # 수면 중이 아닐 때만
             return {'priority': 'warning', 'reason': 'warning_no_movement_in_bathroom'}
             
    # 24시간 이상 장기 외출
    if state.get('entrance_rfid_status') == 'out' and (current_time - state.get('last_rfid_time', current_time)).total_seconds() > 86400: # 24시간
         return {'priority': 'warning', 'reason': 'warning_long_absence'}
         
    # 폭염/한파 위험
    temp = state.get('bathroom_temp_celsius', 22)
    if (temp > 30 or temp < 10) and (current_time - state.get('last_motion_time', current_time)).total_seconds() > 14400: # 4시간
        return {'priority': 'warning', 'reason': 'warning_extreme_temperature_and_no_movement'}

    # --- 관심(Attention) 규칙 ---
    # 식사 거름 의심
    current_hour = current_time.hour
    if current_hour in [12, 13, 18, 19]: # 점심/저녁 시간
        if (current_time - state.get('last_kitchen_activity_time', current_time)).total_seconds() > 14400: # 4시간 동안 주방 활동 없음
            return {'priority': 'attention', 'reason': 'attention_meal_skipped_suspected'}
            
    # 12시간 이상 움직임 없음 (재실 시)
    if state.get('entrance_rfid_status') == 'in' and (current_time - state.get('last_motion_time', current_time)).total_seconds() > 43200: # 12시간
        return {'priority': 'attention', 'reason': 'attention_no_movement_12h'}
    
    return None

def insert_snapshots_batch(conn, snapshots):
    if not snapshots: return
    cols = snapshots[0].keys()
    query_template = f"INSERT INTO home_state_snapshots ({', '.join(cols)}) VALUES %s"
    def format_row(row):
        return tuple(json.dumps(row.get(col)) if isinstance(row.get(col), dict) else row.get(col) for col in cols)
    data_to_insert = [format_row(row) for row in snapshots]
    cursor = conn.cursor()
    try:
        print(f"    - {len(data_to_insert):,} 건의 스냅샷 데이터를 DB에 INSERT 중...")
        psycopg2.extras.execute_values(cursor, query_template, data_to_insert, page_size=500)
        conn.commit()
    except (Exception, psycopg2.Error) as error:
        print("INSERT 중 오류 발생: ", error)
        conn.rollback()
    finally:
        cursor.close()

# main 함수 (수정본)
def main():
    # 1. 스크립트 실행에 필요한 모든 디바이스 정보를 CSV 파일에서 한 번에 로드합니다.
    print("모든 디바이스 정보를 CSV 파일에서 로딩합니다...")
    all_devices_by_user = {}
    csv_files = [
        "pir_devices.csv", "rfid_devices.csv", "reed_devices.csv", 
        "sound_devices.csv", "loadcell_devices.csv", "temperature_devices.csv", 
        "mq5_devices.csv", "mq7_devices.csv", "button_devices.csv", "buzzer_devices.csv"
    ]
    for fname in csv_files:
        user_devices = read_device_info_from_csv(fname)
        if user_devices:
            for user_id, devices in user_devices.items():
                if user_id not in all_devices_by_user:
                    all_devices_by_user[user_id] = []
                all_devices_by_user[user_id].extend(devices)

    # 2. DB에 연결하여 기존 home_state_snapshots 테이블을 비웁니다.
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("DB 연결 성공. 기존 home_state_snapshots 테이블 데이터를 삭제합니다...")
        cur.execute("TRUNCATE TABLE home_state_snapshots;")
        conn.commit()

        # 3. 사용자 목록을 기준으로 한 명씩 타임라인 분석을 시작합니다.
        for user_id, devices in all_devices_by_user.items():
            print(f"\n사용자 {user_id[:8]}... 의 타임라인 처리 시작...")
            user_timeline = fetch_all_sensor_data_for_user(cur, user_id)
            if not user_timeline:
                print("    - 센서 데이터가 없어 건너뜁니다.")
                continue

            home_state = HomeState(user_id)
            snapshots_to_insert = []
            
            # --- 수정된 부분: itertools.groupby를 사용하여 동일 시간대 이벤트를 그룹화 ---
            from itertools import groupby

            for time, events_at_time in groupby(user_timeline, key=lambda x: x['time']):
                # 4-1. 동일 시간대에 발생한 모든 이벤트를 순회하며 상태를 업데이트합니다.
                for event in events_at_time:
                    # update_and_get_snapshot이 내부적으로 last_known_state를 업데이트하므로,
                    # 반환값은 마지막 이벤트 처리 시에만 사용합니다.
                    final_snapshot_for_this_moment = home_state.update_and_get_snapshot(event)

                # 4-2. 해당 시간대의 모든 이벤트 처리가 끝난 후, 최종 스냅샷 하나만 사용합니다.
                current_snapshot = final_snapshot_for_this_moment
                
                # 4-3. 규칙 확인 및 상호작용 생성 (기존 로직과 동일)
                triggered_event = check_rules(home_state.get_current_state(), time)
                if triggered_event:
                    current_snapshot['alert_level'] = triggered_event['priority'].capitalize()
                    current_snapshot['alert_reason'] = triggered_event['reason']

                snapshots_to_insert.append(current_snapshot)
                
                if triggered_event:
                    buzzer_device = next((d for d in devices if 'Buzzer' in d['location_label']), None)
                    button_device = random.choice([d for d in devices if 'Button' in d['location_label']] or [None])
                    
                    if buzzer_device and button_device:
                        # 부저 ON 스냅샷
                        buzzer_on_snapshot = home_state.last_known_state.copy()
                        buzzer_on_time = current_snapshot['time'] + timedelta(seconds=1)
                        buzzer_on_snapshot.update({
                            'time': buzzer_on_time, 'kitchen_buzzer_is_on': True,
                            'alert_level': triggered_event['priority'].capitalize(),
                            'alert_reason': triggered_event['reason']
                        })
                        snapshots_to_insert.append(buzzer_on_snapshot)
                        home_state.last_known_state = buzzer_on_snapshot

                        # 버튼 Pressed 스냅샷
                        button_press_snapshot = home_state.last_known_state.copy()
                        button_press_time = buzzer_on_time + timedelta(seconds=random.randint(10, 300))
                        button_location_key = f"{button_device['location_label'].split(' - ')[0].strip().lower()}_button_state"
                        button_press_snapshot.update({
                            'time': button_press_time,
                            button_location_key.replace(" ", "_"): 'PRESSED',
                            'action_log': {"action_taken": "USER_ACKNOWLEDGED", "result_time": button_press_time.isoformat(), "acknowledged_by": button_device.get('device_id')}
                        })
                        snapshots_to_insert.append(button_press_snapshot)
                        home_state.last_known_state = button_press_snapshot

                        # 부저 OFF 스냅샷
                        buzzer_off_snapshot = home_state.last_known_state.copy()
                        buzzer_off_time = button_press_time + timedelta(seconds=1)
                        buzzer_off_snapshot.update({
                            'time': buzzer_off_time, 'kitchen_buzzer_is_on': False,
                            'alert_level': 'Normal', 'alert_reason': 'Resolved by user'
                        })
                        snapshots_to_insert.append(buzzer_off_snapshot)
                        home_state.last_known_state = buzzer_off_snapshot

                # 5. 스냅샷이 5000개 이상 쌓이면 DB에 일괄 INSERT
                if len(snapshots_to_insert) >= 5000:
                    insert_snapshots_batch(conn, snapshots_to_insert)
                    snapshots_to_insert = []
            
            # 남은 스냅샷 INSERT
            insert_snapshots_batch(conn, snapshots_to_insert)
            
    except (Exception, psycopg2.Error) as error:
        print("전체 프로세스 중 오류 발생: ", error)
    finally:
        if conn: conn.close()
        print("DB 연결을 닫았습니다.")

if __name__ == "__main__":
    main()