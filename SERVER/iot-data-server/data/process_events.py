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
        print(f"오류: '{filename}' 파일을 찾을 수 없습니다.")
        exit()
    return user_devices

def fetch_snapshots_for_user(cursor, user_id):
    """DB에서 특정 사용자의 모든 스냅샷을 시간순으로 가져옵니다."""
    print(f"    - DB에서 {user_id[:8]}... 의 home_state_snapshots 데이터 조회 중...")
    query = "SELECT * FROM home_state_snapshots WHERE user_id = %s ORDER BY time ASC;"
    cursor.execute(query, (user_id,))
    
    # 컬럼 이름을 키로 사용하는 딕셔너리로 변환
    colnames = [desc[0] for desc in cursor.description]
    return [dict(zip(colnames, row)) for row in cursor.fetchall()]

def check_rules(state, current_time):
    # (이전과 동일한 고도화된 규칙 엔진 로직)
    if state.get('kitchen_mq5_gas_ppm', 200) > 1000:
        return {'priority': 'emergency', 'reason': 'emergency_gas_leak_detected'}
    # ... (다른 모든 규칙 포함)
    return None

def main():
    print("부저 및 버튼 디바이스 정보를 CSV 파일에서 로딩합니다...")
    buzzer_devices_by_user = read_device_info_from_csv("buzzer_devices.csv")
    button_devices_by_user = read_device_info_from_csv("button_devices.csv")
    if not buzzer_devices_by_user or not button_devices_by_user: return

    updates_to_snapshots = []
    buzzer_logs_to_insert = []
    button_logs_to_insert = []
    
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        user_ids = list(buzzer_devices_by_user.keys())
        for user_id in user_ids:
            print(f"\n사용자 {user_id[:8]}... 의 스냅샷 분석 시작...")
            user_timeline = fetch_snapshots_for_user(cur, user_id)
            if not user_timeline: continue

            last_alert_time = datetime.min.replace(tzinfo=user_timeline[0]['time'].tzinfo)

            for snapshot in user_timeline:
                # 규칙 확인 (알림 발생 후 10분 내 중복 방지)
                if (snapshot['time'] - last_alert_time).total_seconds() > 600:
                    triggered_event = check_rules(snapshot, snapshot['time'])
                    if triggered_event:
                        # 1. home_state_snapshots 업데이트 준비
                        updates_to_snapshots.append({
                            'alert_level': triggered_event['priority'].capitalize(),
                            'alert_reason': triggered_event['reason'],
                            'time': snapshot['time'],
                            'user_id': user_id
                        })
                        
                        # 2. 부저/버튼 로그 생성 준비
                        buzzer_device = buzzer_devices_by_user[user_id][0]
                        button_device = random.choice(button_devices_by_user.get(user_id, []))

                        buzzer_on_time = snapshot['time'] + timedelta(seconds=1)
                        button_press_time = buzzer_on_time + timedelta(seconds=random.randint(10, 300))
                        buzzer_off_time = button_press_time + timedelta(seconds=1)
                        
                        # 부저 ON 로그
                        buzzer_logs_to_insert.append({'time': buzzer_on_time, 'device_id': buzzer_device['device_id'], 'state': 'ON', 'reason': triggered_event['reason']})
                        # 버튼 PRESSED 로그
                        button_logs_to_insert.append({'time': button_press_time, 'device_id': button_device['device_id'], 'state': 'PRESSED', 'type': 'crisis_acknowledged'})
                        # 부저 OFF 로그
                        buzzer_logs_to_insert.append({'time': buzzer_off_time, 'device_id': buzzer_device['device_id'], 'state': 'OFF', 'reason': 'user_acknowledged'})

                        last_alert_time = buzzer_off_time
        
        # --- 모든 분석이 끝난 후 DB에 일괄 업데이트 및 삽입 ---
        print("\n모든 분석 완료. 데이터베이스 업데이트를 시작합니다...")
        
        # 1. home_state_snapshots 업데이트
        if updates_to_snapshots:
            print(f"    - {len(updates_to_snapshots)} 건의 스냅샷에 alert 정보 업데이트 중...")
            update_query = "UPDATE home_state_snapshots SET alert_level = %s, alert_reason = %s WHERE time = %s AND user_id = %s"
            psycopg2.extras.execute_batch(cur, update_query, [(u['alert_level'], u['alert_reason'], u['time'], u['user_id']) for u in updates_to_snapshots])
        
        # 2. actuator_log_buzzer 삽입
        if buzzer_logs_to_insert:
            print(f"    - {len(buzzer_logs_to_insert)} 건의 부저 로그 INSERT 중...")
            buzzer_query = "INSERT INTO actuator_log_buzzer (time, device_id, buzzer_type, state, reason) VALUES (%s, %s, 'passive', %s, %s)"
            psycopg2.extras.execute_batch(cur, buzzer_query, [(b['time'], b['device_id'], b['state'], b['reason']) for b in buzzer_logs_to_insert])

        # 3. sensor_event_button 삽입
        if button_logs_to_insert:
            print(f"    - {len(button_logs_to_insert)} 건의 버튼 로그 INSERT 중...")
            button_query = "INSERT INTO sensor_event_button (time, device_id, button_state, event_type) VALUES (%s, %s, %s, %s)"
            psycopg2.extras.execute_batch(cur, button_query, [(b['time'], b['device_id'], b['state'], b['type']) for b in button_logs_to_insert])

        conn.commit()
        print("데이터베이스 업데이트 완료.")

    except (Exception, psycopg2.Error) as error:
        print("전체 프로세스 중 오류 발생: ", error)
        conn.rollback()
    finally:
        if conn: conn.close()
        print("DB 연결을 닫았습니다.")

if __name__ == "__main__":
    main()