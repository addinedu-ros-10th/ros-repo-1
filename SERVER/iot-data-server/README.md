# SERVER / iot-data-server

Path: `SERVER/iot-data-server`

Purpose
- IoT 디바이스로부터 데이터 수집 및 저장, 조회 API 제공

Tech
- Python, FastAPI, InfluxDB / Timescale / PostgreSQL (옵션)

Getting started (placeholder)
1. Configure DB settings in `.env`
2. Run: `uvicorn iot_api.main:app --reload`

Maintainer
- TBD

Notes
- 데이터 스키마 및 retention 정책을 문서화하세요.