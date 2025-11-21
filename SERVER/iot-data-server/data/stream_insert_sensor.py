# -*- coding: utf-8 -*-
"""
stream_insert_sensor.py
- 목적: 200만+ 행 SQL INSERT를 기간 단위(일/시간)로 나눠 DB에 직접 적재.
- 특징:
  * MQ-5 / MQ-7 모두 지원 (--sensor mq5|mq7)
  * 기존 스크립트의 생성 규칙을 유지:
      - MQ-7: co_ppm, temp 18~25, hum 40~60, ok/ warning(50), event_type normal/co_spike, 위기확률 0.0005
      - MQ-5: gas_ppm, temp 20~28, hum 45~65, ok/ danger(1000), event_type normal/lpg_spike, 위기확률 0.0003
    (기존 파일의 필드명/임계값을 그대로 반영)
  * 1분 간격 샘플 (원본 규칙과 동일한 주기)
  * 윈도우 단위(기본 1일)로 COMMIT → 메모리/트랜잭션 부담↓, 실패 지점 재시작 쉬움
  * COPY(STDIN, CSV) 기반 초고속 로드 또는 execute_values 배치 INSERT 선택
  * COPY는 행을 큰 덩어리(chunk_rows)로 나눠 여러 번 호출 → 메모리 폭주 방지
사용 예:
  pip install psycopg2-binary
  python stream_insert_sensor.py \
    --sensor mq7 \
    --devices-csv mq7_devices.csv \
    --table sensor_raw_mq7 \
    --days 90 \
    --window-days 1 \
    --method copy \
    --dsn "postgresql://USER:PW@HOST:5432/DB"
"""

import argparse
import csv
import io
import json
import os
import random
from datetime import datetime, timedelta

import psycopg2
from psycopg2.extras import execute_values

from dotenv import load_dotenv

# .env.prod 파일 로드
load_dotenv('../.env.local')


# 환경변수 확인
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

print(DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)


# ------------------------
# 0) 생성 규칙 (원본 유지)
# ------------------------
CRISIS_EVENT_PROBABILITY = {
    "mq7": 0.0005,  # 0.05%
    "mq5": 0.0003,  # 0.03%
}

def gen_payload_mq7(ppm: int, is_crisis: bool):
    """MQ-7: 원본 규칙 반영 (필드/범위/임계 동일)"""
    return {
        "co_ppm": ppm,
        "event_type": "co_spike" if is_crisis else "normal",
        "temperature_c": round(random.uniform(18.0, 25.0), 1),
        "humidity_percent": round(random.uniform(40.0, 60.0), 1),
        "status": "warning" if ppm >= 50 else "ok",
    }

def gen_payload_mq5(ppm: int, is_crisis: bool):
    """MQ-5: 원본 규칙 반영 (필드/범위/임계 동일)"""
    return {
        "gas_ppm": ppm,
        "event_type": "lpg_spike" if is_crisis else "normal",
        "temperature_c": round(random.uniform(20.0, 28.0), 1),
        "humidity_percent": round(random.uniform(45.0, 65.0), 1),
        "status": "danger" if ppm >= 1000 else "ok",
    }

def sample_ppm(sensor: str, crisis: bool) -> int:
    """원본 규칙에 맞는 대략의 ppm 분포 (평시/위기 범위 유지)"""
    if sensor == "mq7":
        # 평시: 0~50, 위기: 100~400
        return random.randint(100, 400) if crisis else random.randint(0, 50)
    # mq5: 평시 0~800, 위기 1000~3000
    return random.randint(1000, 3000) if crisis else random.randint(0, 800)


# ------------------------
# 1) 장치 목록 로딩
# ------------------------
def read_device_ids(devices_csv: str):
    """
    devices_csv 헤더 예시:
      - mq7_devices.csv: device_id[, user_id, ...] (원본 파일과 동일)
      - mq5_devices.csv: device_id[, ...]
    어떤 CSV라도 device_id 열만 있으면 동작.
    """
    device_ids = []
    with open(devices_csv, "r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            did = (row.get("device_id") or row.get("DEVICE_ID") or row.get("id") or "").strip()
            if did:
                device_ids.append(did)
    if not device_ids:
        raise ValueError(f"CSV({devices_csv})에서 device_id를 찾지 못했습니다.")
    return device_ids


# ------------------------
# 2) 시간 윈도우 생성 (일 단위 기본)
# ------------------------
def iter_time_windows(start: datetime, end: datetime, window_days: int, window_hours: int = 0):
    if window_hours and window_days:
        raise ValueError("window-days 또는 window-hours 중 하나만 지정하세요.")
    if not window_days and not window_hours:
        window_days = 1
    cur = start
    delta = timedelta(hours=window_hours) if window_hours else timedelta(days=window_days)
    while cur < end:
        nxt = min(cur + delta, end)
        yield cur, nxt
        cur = nxt


# ------------------------
# 3) 윈도우 내 1분 간격 이벤트 생성 (원본 주기 유지)
# ------------------------
def generate_rows(sensor: str, device_ids, win_start: datetime, win_end: datetime):
    """
    반환: (time_str, device_id, payload_json_str)
    - 1분 간격(원본과 동일) 샘플
    - CRISIS_EVENT_PROBABILITY에 따라 드문 위기 이벤트 삽입(원본 규칙 유지)
    """
    crisis_p = CRISIS_EVENT_PROBABILITY[sensor]
    step = timedelta(minutes=1)
    # 장치별/분단위 순회 → 메모리 폭주 방지 위해 generator로 한 줄씩 뱉음
    for device_id in device_ids:
        t = win_start.replace(second=0, microsecond=0)
        while t < win_end:
            is_crisis = (random.random() < crisis_p)
            ppm = sample_ppm(sensor, is_crisis)
            if sensor == "mq7":
                payload = gen_payload_mq7(ppm, is_crisis)
            else:
                payload = gen_payload_mq5(ppm, is_crisis)
            yield (t.strftime('%Y-%m-%d %H:%M:%S.%f'), device_id, json.dumps(payload, ensure_ascii=False))
            t += step


# ------------------------
# 4) 적재기: COPY (추천) / 배치 INSERT
# ------------------------
def load_copy_streaming(conn, table: str, rows_iter, chunk_rows: int = 200_000):
    """
    큰 데이터를 한 번에 메모리에 담지 않고, chunk_rows 단위로 COPY를 여러 번 실행.
    """
    total = 0
    buf = io.StringIO()
    writer = csv.writer(buf)
    for i, row in enumerate(rows_iter, 1):
        writer.writerow(row)
        if i % chunk_rows == 0:
            buf.seek(0)
            sql = f"COPY {table} (time, device_id, raw_payload) FROM STDIN WITH (FORMAT csv)"
            with conn.cursor() as cur:
                cur.copy_expert(sql, buf)
            total += chunk_rows
            buf.close()
            buf = io.StringIO()
            writer = csv.writer(buf)
    # 잔여 플러시
    rem = buf.tell()
    if rem:
        buf.seek(0)
        sql = f"COPY {table} (time, device_id, raw_payload) FROM STDIN WITH (FORMAT csv)"
        with conn.cursor() as cur:
            cur.copy_expert(sql, buf)
        total += sum(1 for _ in io.StringIO(buf.getvalue()))
    buf.close()
    return total

def load_insert_batch(conn, table: str, rows_iter, batch_size: int = 10_000):
    """
    execute_values 배치 INSERT (COPY가 어려운 환경에서 대안)
    """
    tpl = "(%s, %s, %s::jsonb)"
    total = 0
    batch = []
    with conn.cursor() as cur:
        for row in rows_iter:
            batch.append(row)
            if len(batch) >= batch_size:
                execute_values(cur, f"INSERT INTO {table} (time, device_id, raw_payload) VALUES %s", batch, template=tpl)
                total += len(batch)
                batch.clear()
        if batch:
            execute_values(cur, f"INSERT INTO {table} (time, device_id, raw_payload) VALUES %s", batch, template=tpl)
            total += len(batch)
    return total


# ------------------------
# 5) 메인: 기간 단위로 생성 → 적재 → 커밋
# ------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sensor", choices=["mq5", "mq7"], required=True, help="센서 종류")
    ap.add_argument("--devices-csv", required=True, help="device_id 헤더를 포함한 CSV (예: mq7_devices.csv)")
    ap.add_argument("--table", required=True, help="타깃 테이블명 (예: sensor_raw_mq7, sensor_raw_mq5)")
    ap.add_argument("--days", type=int, default=180, help="과거 며칠치 생성 (시작일 미지정 시 today - days)")
    ap.add_argument("--start", type=str, default=None, help="시작일 YYYY-MM-DD (미지정 시 today - days)")
    ap.add_argument("--end", type=str, default=None, help="종료일 YYYY-MM-DD (미지정 시 오늘, 미포함)")
    ap.add_argument("--window-days", type=int, default=1, help="윈도우(일 단위)")
    ap.add_argument("--window-hours", type=int, default=0, help="윈도우(시간 단위) — days와 동시 사용 불가")
    ap.add_argument("--method", choices=["copy", "insert"], default="copy", help="적재 방식")
    ap.add_argument("--chunk-rows", type=int, default=200_000, help="COPY 스트리밍 시 묶는 행 수")
    ap.add_argument("--batch-size", type=int, default=10_000, help="INSERT 배치 크기")

    # 접속 정보
    ap.add_argument("--dsn", type=str, default=None, help="postgresql://user:pass@host:port/db")
    ap.add_argument("--host", type=str, default=DB_HOST)
    ap.add_argument("--port", type=int, default=DB_PORT)
    ap.add_argument("--user", type=str, default=DB_USER)
    ap.add_argument("--password", type=str, default=DB_PASSWORD)
    ap.add_argument("--dbname", type=str, default=DB_NAME)
    args = ap.parse_args()

    # 기간 계산
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end = datetime.fromisoformat(args.end) if args.end else today
    start = datetime.fromisoformat(args.start) if args.start else (end - timedelta(days=args.days))
    if not (start < end):
        raise ValueError("기간이 잘못되었습니다. start < end 여야 합니다.")

    device_ids = read_device_ids(args.devices_csv)
    print(f"장치 {len(device_ids):,}대 | 기간 {start.date()} ~ {end.date()} | 윈도우 {args.window_days or args.window_hours} {'days' if args.window_days else 'hours'} | 모드 {args.method}")

    # DB 연결
    if args.dsn:
        conn = psycopg2.connect(args.dsn)
    else:
        conn = psycopg2.connect(
            host=args.host or os.getenv("PGHOST", "localhost"),
            port=args.port or int(os.getenv("PGPORT", "5432")),
            user=args.user or os.getenv("PGUSER"),
            password=args.password or os.getenv("PGPASSWORD"),
            dbname=args.dbname or os.getenv("PGDATABASE"),
        )
    conn.autocommit = False

    total = 0
    try:
        # 세션 튜닝: 커밋 대기 제거 (로드 중 속도↑)
        with conn.cursor() as cur:
            cur.execute("SET LOCAL synchronous_commit = off;")

        for win_s, win_e in iter_time_windows(start, end, args.window_days, args.window_hours):
            print(f"\n▶ 윈도우: {win_s} ~ {win_e}  생성/적재 시작")

            rows_iter = generate_rows(args.sensor, device_ids, win_s, win_e)

            if args.method == "copy":
                inserted = load_copy_streaming(conn, args.table, rows_iter, chunk_rows=args.chunk_rows)
            else:
                inserted = load_insert_batch(conn, args.table, rows_iter, batch_size=args.batch_size)

            conn.commit()
            total += inserted
            print(f"✓ 커밋 완료 | 이번 윈도우 삽입: {inserted:,}행 | 누적: {total:,}행")

        print(f"\n✅ 전체 완료: 총 {total:,}행 삽입")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
