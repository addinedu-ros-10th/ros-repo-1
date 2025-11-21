"""
SQLAlchemy ORM 모델

데이터베이스의 모든 테이블에 대한 SQLAlchemy ORM 모델을 정의합니다.
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, SmallInteger, BigInteger
from sqlalchemy import DateTime, UUID, ForeignKey, JSON, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, JSONB

Base = declarative_base()


class User(Base):
    """사용자 테이블 ORM 모델"""
    __tablename__ = "users"
    
    user_id: Mapped[str] = Column(PostgresUUID, primary_key=True)
    user_role: Mapped[str] = Column(String(20), nullable=False)
    user_name: Mapped[str] = Column(Text, nullable=False)
    email: Mapped[Optional[str]] = Column(Text, nullable=True)
    phone_number: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    
    # 관계 정의
    devices: Mapped[List["Device"]] = relationship("Device", back_populates="user")
    relationships_as_subject: Mapped[List["UserRelationship"]] = relationship("UserRelationship", foreign_keys="UserRelationship.subject_user_id", back_populates="subject_user")
    relationships_as_target: Mapped[List["UserRelationship"]] = relationship("UserRelationship", foreign_keys="UserRelationship.target_user_id", back_populates="target_user")
    profile: Mapped[Optional["UserProfile"]] = relationship("UserProfile", back_populates="user", uselist=False)
    home_state_snapshots: Mapped[List["HomeStateSnapshot"]] = relationship("HomeStateSnapshot", back_populates="user")


class Device(Base):
    """디바이스 테이블 ORM 모델"""
    __tablename__ = "devices"
    
    device_id: Mapped[str] = Column(String(64), primary_key=True)
    user_id: Mapped[Optional[str]] = Column(PostgresUUID, ForeignKey("users.user_id"), nullable=True)
    location_label: Mapped[Optional[str]] = Column(Text, nullable=True)
    installed_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    
    # 관계 정의
    user: Mapped[Optional[User]] = relationship("User", back_populates="devices")
    button_events: Mapped[List["SensorEventButton"]] = relationship("SensorEventButton", back_populates="device")
    temperature_events: Mapped[List["SensorRawTemperature"]] = relationship("SensorRawTemperature", back_populates="device")


class DeviceRTCStatus(Base):
    """디바이스 RTC 상태 테이블 ORM 모델"""
    __tablename__ = "device_rtc_status"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    rtc_epoch_s: Mapped[Optional[int]] = Column(BigInteger, nullable=True)
    drift_ms: Mapped[Optional[int]] = Column(Integer, nullable=True)
    sync_source: Mapped[Optional[str]] = Column(Text, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


# 센서 데이터 테이블들
class SensorRawCDS(Base):
    """CDS 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_cds"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    analog_value: Mapped[Optional[int]] = Column(Integer, nullable=True)
    lux_value: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawDHT(Base):
    """DHT 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_dht"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    temperature: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    humidity: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    heat_index: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawFlame(Base):
    """화염 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_flame"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    analog_value: Mapped[Optional[int]] = Column(Integer, nullable=True)
    flame_detected: Mapped[Optional[bool]] = Column(Boolean, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawIMU(Base):
    """IMU 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_imu"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    accel_x: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    accel_y: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    accel_z: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    gyro_x: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    gyro_y: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    gyro_z: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    mag_x: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    mag_y: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    mag_z: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    temperature: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawLoadCell(Base):
    """로드셀 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_loadcell"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawMQ5(Base):
    """MQ5 가스 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_mq5"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawMQ7(Base):
    """MQ7 가스 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_mq7"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawRFID(Base):
    """RFID 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_rfid"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawSound(Base):
    """사운드 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_sound"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawTCRT5000(Base):
    """TCRT5000 근접 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_tcrt5000"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorRawUltrasonic(Base):
    """초음파 센서 원시 데이터 테이블 ORM 모델"""
    __tablename__ = "sensor_raw_ultrasonic"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


# 엣지 센서 테이블들
class SensorEdgeFlame(Base):
    """화염 엣지 센서 테이블 ORM 모델"""
    __tablename__ = "sensor_edge_flame"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    flame_detected: Mapped[bool] = Column(Boolean, nullable=False)
    confidence: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    alert_level: Mapped[Optional[str]] = Column(Text, nullable=True)
    processing_time: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorEdgePIR(Base):
    """PIR 엣지 센서 테이블 ORM 모델"""
    __tablename__ = "sensor_edge_pir"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    motion_detected: Mapped[bool] = Column(Boolean, nullable=False)
    confidence: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    motion_direction: Mapped[Optional[str]] = Column(Text, nullable=True)
    motion_speed: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    processing_time: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorEdgeReed(Base):
    """Reed 스위치 엣지 센서 테이블 ORM 모델"""
    __tablename__ = "sensor_edge_reed"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    switch_state: Mapped[bool] = Column(Boolean, nullable=False)
    confidence: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    magnetic_field_detected: Mapped[Optional[bool]] = Column(Boolean, nullable=True)
    magnetic_strength: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    processing_time: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class SensorEdgeTilt(Base):
    """틸트 센서 엣지 테이블 ORM 모델"""
    __tablename__ = "sensor_edge_tilt"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    tilt_detected: Mapped[bool] = Column(Boolean, nullable=False)
    confidence: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    tilt_angle: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    tilt_direction: Mapped[Optional[str]] = Column(Text, nullable=True)
    processing_time: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


# 액추에이터 로그 테이블들
class ActuatorLogBuzzer(Base):
    """부저 액추에이터 로그 테이블 ORM 모델"""
    __tablename__ = "actuator_log_buzzer"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    buzzer_type: Mapped[str] = Column(Text, nullable=False)
    state: Mapped[str] = Column(Text, nullable=False)
    freq_hz: Mapped[Optional[int]] = Column(Integer, nullable=True)
    duration_ms: Mapped[Optional[int]] = Column(Integer, nullable=True)
    reason: Mapped[Optional[str]] = Column(Text, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class ActuatorLogIRTX(Base):
    """IR 송신 액추에이터 로그 테이블 ORM 모델"""
    __tablename__ = "actuator_log_ir_tx"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    protocol: Mapped[Optional[str]] = Column(Text, nullable=True)
    address_hex: Mapped[Optional[str]] = Column(Text, nullable=True)
    command_hex: Mapped[str] = Column(Text, nullable=False)
    repeat_cnt: Mapped[Optional[int]] = Column(Integer, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class ActuatorLogRelay(Base):
    """릴레이 액추에이터 로그 테이블 ORM 모델"""
    __tablename__ = "actuator_log_relay"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    channel: Mapped[int] = Column(SmallInteger, nullable=False, default=1)
    state: Mapped[str] = Column(Text, nullable=False)
    reason: Mapped[Optional[str]] = Column(Text, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


class ActuatorLogServo(Base):
    """서보 액추에이터 로그 테이블 ORM 모델"""
    __tablename__ = "actuator_log_servo"
    
    time: Mapped[datetime] = Column(DateTime(timezone=True), primary_key=True)
    device_id: Mapped[str] = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    channel: Mapped[int] = Column(SmallInteger, nullable=False, default=1)
    angle_deg: Mapped[Optional[Numeric]] = Column(Numeric, nullable=True)
    pwm_us: Mapped[Optional[int]] = Column(Integer, nullable=True)
    reason: Mapped[Optional[str]] = Column(Text, nullable=True)
    raw_payload: Mapped[Optional[dict]] = Column(JSONB, nullable=True)


# 사용자 관계 테이블
class UserRelationship(Base):
    """사용자 간의 관계(돌봄, 가족, 관리)를 정의하는 ORM 모델"""
    __tablename__ = "user_relationships"
    
    relationship_id: Mapped[str] = Column(PostgresUUID, primary_key=True)
    subject_user_id: Mapped[str] = Column(PostgresUUID, ForeignKey("users.user_id"), nullable=False)
    target_user_id: Mapped[str] = Column(PostgresUUID, ForeignKey("users.user_id"), nullable=False)
    relationship_type: Mapped[str] = Column(String(20), nullable=False)
    status: Mapped[str] = Column(String(20), nullable=False, default="active")
    created_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    
    # 관계 정의
    subject_user: Mapped["User"] = relationship("User", foreign_keys=[subject_user_id], back_populates="relationships_as_subject")
    target_user: Mapped["User"] = relationship("User", foreign_keys=[target_user_id], back_populates="relationships_as_target")


# 사용자 프로필 테이블
class UserProfile(Base):
    """사용자의 상세 프로필 및 돌봄 서비스 관련 정보를 정의하는 ORM 모델"""
    __tablename__ = "user_profiles"
    
    user_id: Mapped[str] = Column(PostgresUUID, ForeignKey("users.user_id"), primary_key=True)
    date_of_birth: Mapped[date] = Column(Date, nullable=False)
    gender: Mapped[str] = Column(String(10), nullable=False)
    address: Mapped[Optional[str]] = Column(Text, nullable=True)
    address_detail: Mapped[Optional[str]] = Column(Text, nullable=True)
    medical_history: Mapped[Optional[str]] = Column(Text, nullable=True)
    significant_notes: Mapped[Optional[str]] = Column(Text, nullable=True)
    current_status: Mapped[Optional[str]] = Column(Text, nullable=True)
    created_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    
    # 관계 정의
    user: Mapped["User"] = relationship("User", back_populates="profile")


class HomeStateSnapshot(Base):
    """홈 상태 스냅샷 테이블 (Digital Twin State)"""
    __tablename__ = "home_state_snapshots"

    time = Column(DateTime(timezone=True), primary_key=True)
    user_id = Column(PostgresUUID, ForeignKey("users.user_id"), primary_key=True)
    
    # 입구 센서
    entrance_pir_motion = Column(Boolean)
    entrance_rfid_status = Column(Text)
    entrance_reed_is_closed = Column(Boolean)
    
    # 거실 센서
    livingroom_pir_1_motion = Column(Boolean)
    livingroom_pir_2_motion = Column(Boolean)
    livingroom_sound_db = Column(Numeric)
    livingroom_mq7_co_ppm = Column(Numeric)
    livingroom_button_state = Column(Text)
    
    # 주방 센서
    kitchen_pir_motion = Column(Boolean)
    kitchen_sound_db = Column(Numeric)
    kitchen_mq5_gas_ppm = Column(Numeric)
    kitchen_loadcell_1_kg = Column(Numeric)
    kitchen_loadcell_2_kg = Column(Numeric)
    kitchen_button_state = Column(Text)
    kitchen_buzzer_is_on = Column(Boolean)
    
    # 침실 센서
    bedroom_pir_motion = Column(Boolean)
    bedroom_sound_db = Column(Numeric)
    bedroom_mq7_co_ppm = Column(Numeric)
    bedroom_loadcell_kg = Column(Numeric)
    bedroom_button_state = Column(Text)
    
    # 욕실 센서
    bathroom_pir_motion = Column(Boolean)
    bathroom_sound_db = Column(Numeric)
    bathroom_temp_celsius = Column(Numeric)
    bathroom_button_state = Column(Text)
    
    # 분석 결과
    detected_activity = Column(Text)
    alert_level = Column(Text)
    alert_reason = Column(Text)
    action_log = Column(JSONB)
    extra_data = Column(JSONB)
    
    # 관계 설정
    user = relationship("User", back_populates="home_state_snapshots")


class SensorEventButton(Base):
    """버튼 이벤트 센서 테이블"""
    __tablename__ = "sensor_event_button"

    time = Column(DateTime(timezone=True), primary_key=True)
    device_id = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    button_state = Column(Text, nullable=False)
    event_type = Column(Text, nullable=False)
    press_duration_ms = Column(Integer)
    raw_payload = Column(JSONB)
    
    # 관계 설정
    device = relationship("Device", back_populates="button_events")


class SensorRawTemperature(Base):
    """온도 센서 원시 데이터 테이블"""
    __tablename__ = "sensor_raw_temperature"

    time = Column(DateTime(timezone=True), primary_key=True)
    device_id = Column(String(64), ForeignKey("devices.device_id"), primary_key=True)
    temperature_celsius = Column(Numeric, nullable=False)
    humidity_percent = Column(Numeric)
    raw_payload = Column(JSONB)
    
    # 관계 설정
    device = relationship("Device", back_populates="temperature_events")


# Alembic 버전 테이블
class AlembicVersion(Base):
    """Alembic 버전 테이블 ORM 모델"""
    __tablename__ = "alembic_version"
    
    version_num: Mapped[str] = Column(String, primary_key=True)


# 모든 모델을 리스트로 관리
__all__ = [
    "Base",
    "User",
    "Device", 
    "DeviceRTCStatus",
    "SensorRawCDS",
    "SensorRawDHT",
    "SensorRawFlame",
    "SensorRawIMU",
    "SensorRawLoadCell",
    "SensorRawMQ5",
    "SensorRawMQ7",
    "SensorRawRFID",
    "SensorRawSound",
    "SensorRawTCRT5000",
    "SensorRawUltrasonic",
    "SensorEdgeFlame",
    "SensorEdgePIR",
    "SensorEdgeReed",
    "SensorEdgeTilt",
    "ActuatorLogBuzzer",
    "ActuatorLogIRTX",
    "ActuatorLogRelay",
    "ActuatorLogServo",
    "UserRelationship",
    "UserProfile",
    "HomeStateSnapshot",
    "SensorEventButton",
    "AlembicVersion",
    "SensorRawTemperature"
] 