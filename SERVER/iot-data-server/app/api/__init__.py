"""
API 라우터 등록

모든 API 라우터를 메인 애플리케이션에 등록합니다.
"""

from fastapi import APIRouter

from app.api.v1 import users, devices, user_relationships, user_profiles, cds, dht, flame, imu, loadcell, mq5, mq7, rfid, sound, tcrt5000, ultrasonic
from app.api.v1 import edge_flame, edge_pir, edge_reed, edge_tilt
from app.api.v1 import actuator_buzzer, actuator_irtx, actuator_relay, actuator_servo
from app.api.v1 import device_rtc
from app.api.v1 import home_state_snapshots, sensor_event_buttons, sensor_raw_temperatures

# 메인 API 라우터
api_router = APIRouter()

# ORM 기준 API 그룹화 등록 (prefix 설정)
# Users & Devices 그룹
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(user_relationships.router, prefix="/user-relationships", tags=["user-relationships"])
api_router.include_router(user_profiles.router, prefix="/user-profiles", tags=["user-profiles"])

# Raw 센서 데이터 그룹
api_router.include_router(cds.router, prefix="/cds", tags=["sensors"])
api_router.include_router(dht.router, prefix="/dht", tags=["sensors"])
api_router.include_router(flame.router, prefix="/flame", tags=["sensors"])
api_router.include_router(imu.router, prefix="/imu", tags=["sensors"])
api_router.include_router(loadcell.router, prefix="/loadcell", tags=["sensors"])
api_router.include_router(mq5.router, prefix="/mq5", tags=["sensors"])
api_router.include_router(mq7.router, prefix="/mq7", tags=["sensors"])
api_router.include_router(rfid.router, prefix="/rfid", tags=["sensors"])
api_router.include_router(sound.router, prefix="/sound", tags=["sensors"])
api_router.include_router(tcrt5000.router, prefix="/tcrt5000", tags=["sensors"])
api_router.include_router(ultrasonic.router, prefix="/ultrasonic", tags=["sensors"])

# Edge 센서 그룹
api_router.include_router(edge_flame.router, prefix="/edge-flame", tags=["edge-sensors"])
api_router.include_router(edge_pir.router, prefix="/edge-pir", tags=["edge-sensors"])
api_router.include_router(edge_reed.router, prefix="/edge-reed", tags=["edge-sensors"])
api_router.include_router(edge_tilt.router, prefix="/edge-tilt", tags=["edge-sensors"])

# Actuator 로그 그룹
api_router.include_router(actuator_buzzer.router, prefix="/actuator-buzzer", tags=["actuators"])
api_router.include_router(actuator_irtx.router, prefix="/actuator-irtx", tags=["actuators"])
api_router.include_router(actuator_relay.router, prefix="/actuator-relay", tags=["actuators"])
api_router.include_router(actuator_servo.router, prefix="/actuator-servo", tags=["actuators"])

# DeviceRTCStatus 그룹
api_router.include_router(device_rtc.router, prefix="/device-rtc", tags=["device-status"])

# Home State Snapshots & Sensor Event Buttons Group
api_router.include_router(home_state_snapshots.router, prefix="/home-state-snapshots", tags=["home-state-snapshots"])
api_router.include_router(sensor_event_buttons.router, prefix="/sensor-event-buttons", tags=["sensor-event-buttons"])

# Sensor Raw Temperature Group
api_router.include_router(sensor_raw_temperatures.router, prefix="/sensor-raw-temperatures", tags=["sensor-raw-temperatures"])

__all__ = ["api_router"]

