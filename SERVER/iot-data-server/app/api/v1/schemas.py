"""
API 스키마 정의

FastAPI 엔드포인트의 요청/응답 모델을 정의합니다.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from uuid import UUID


# ============================================================================
# 사용자 관련 스키마
# ============================================================================

class UserBase(BaseModel):
    """사용자 기본 스키마"""
    user_name: str = Field(..., min_length=1, max_length=100, description="사용자 이름")
    email: Optional[EmailStr] = Field(None, description="이메일 주소")
    phone_number: Optional[str] = Field(None, description="전화번호")
    user_role: str = Field(..., description="사용자 역할")

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            # 전화번호 형식 검증 (한국 전화번호)
            import re
            # 01012345678 형식 허용 (11자리)
            phone_pattern = re.compile(r'^01[0-9]{8,9}$')
            if not phone_pattern.match(v):
                raise ValueError('올바른 전화번호 형식이 아닙니다')
        return v

    @validator('user_role')
    def validate_user_role(cls, v):
        allowed_roles = ['admin', 'caregiver', 'family', 'care_target']
        if v not in allowed_roles:
            raise ValueError(f'허용되지 않는 역할입니다. 허용된 역할: {allowed_roles}')
        return v


class UserCreate(UserBase):
    """사용자 생성 요청 스키마"""
    pass


class UserUpdate(BaseModel):
    """사용자 수정 요청 스키마"""
    user_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    user_role: Optional[str] = None

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if v is not None:
            import re
            # 01012345678 형식 허용 (11자리)
            phone_pattern = re.compile(r'^01[0-9]{8,9}$')
            if not phone_pattern.match(v):
                raise ValueError('올바른 전화번호 형식이 아닙니다')
        return v

    @validator('user_role')
    def validate_user_role(cls, v):
        if v is not None:
            allowed_roles = ['admin', 'caregiver', 'family', 'care_target']
            if v not in allowed_roles:
                raise ValueError(f'허용되지 않는 역할입니다. 허용된 역할: {allowed_roles}')
        return v


class UserResponse(UserBase):
    """사용자 응답 스키마"""
    user_id: UUID
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """사용자 목록 응답 스키마"""
    users: List[UserResponse]
    total: int
    page: int
    size: int


# ============================================================================
# 디바이스 관련 스키마
# ============================================================================

class DeviceBase(BaseModel):
    """디바이스 기본 스키마"""
    location_label: Optional[str] = Field(None, max_length=200, description="설치 위치 라벨")


class DeviceCreate(DeviceBase):
    """디바이스 생성 요청 스키마"""
    device_id: str = Field(..., min_length=1, max_length=64, description="디바이스 고유 ID")
    user_id: Optional[UUID] = Field(None, description="할당된 사용자 ID")


class DeviceUpdate(BaseModel):
    """디바이스 수정 요청 스키마"""
    location_label: Optional[str] = Field(None, max_length=200)
    user_id: Optional[UUID] = None


class DeviceResponse(DeviceBase):
    """디바이스 응답 스키마"""
    device_id: str
    user_id: Optional[UUID] = None
    installed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """디바이스 목록 응답 스키마"""
    devices: List[DeviceResponse]
    total: int
    page: int
    size: int


class DeviceAssignmentRequest(BaseModel):
    """디바이스 할당 요청 스키마"""
    user_id: UUID = Field(..., description="할당할 사용자 ID")


# ============================================================================
# 공통 응답 스키마
# ============================================================================

class SuccessResponse(BaseModel):
    """성공 응답 스키마"""
    message: str
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """에러 응답 스키마"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginationParams(BaseModel):
    """페이지네이션 파라미터"""
    page: int = Field(1, ge=1, description="페이지 번호")
    size: int = Field(10, ge=1, le=100, description="페이지 크기")


# ============================================================================
# 센서 데이터 스키마
# ============================================================================

# CDS (조도 센서) 스키마
class CDSDataCreate(BaseModel):
    """CDS 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    lux_value: Optional[float] = None
    raw_payload: Optional[dict] = None


class CDSDataUpdate(BaseModel):
    """CDS 센서 데이터 수정 스키마"""
    analog_value: Optional[int] = None
    lux_value: Optional[float] = None
    raw_payload: Optional[dict] = None


class CDSDataResponse(BaseModel):
    """CDS 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    lux_value: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# DHT (온습도 센서) 스키마
class DHTDataCreate(BaseModel):
    """DHT 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    heat_index: Optional[float] = None
    raw_payload: Optional[dict] = None


class DHTDataUpdate(BaseModel):
    """DHT 센서 데이터 수정 스키마"""
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    heat_index: Optional[float] = None
    raw_payload: Optional[dict] = None


class DHTDataResponse(BaseModel):
    """DHT 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    heat_index: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# Flame (화재 감지 센서) 스키마
class FlameDataCreate(BaseModel):
    """Flame 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    flame_detected: Optional[bool] = None
    raw_payload: Optional[dict] = None


class FlameDataUpdate(BaseModel):
    """Flame 센서 데이터 수정 스키마"""
    analog_value: Optional[int] = None
    flame_detected: Optional[bool] = None
    raw_payload: Optional[dict] = None


class FlameDataResponse(BaseModel):
    """Flame 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    flame_detected: Optional[bool] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# 기존 센서 데이터 스키마 (향후 확장용)
class SensorDataBase(BaseModel):
    """센서 데이터 기본 스키마"""
    device_id: str
    timestamp: datetime
    value: float
    unit: Optional[str] = None


class SensorDataResponse(SensorDataBase):
    """센서 데이터 응답 스키마"""
    id: int

    class Config:
        from_attributes = True


# IMU (관성 측정 장치) 센서 스키마
class IMUDataCreate(BaseModel):
    """IMU 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    mag_x: Optional[float] = None
    mag_y: Optional[float] = None
    mag_z: Optional[float] = None
    temperature: Optional[float] = None
    raw_payload: Optional[dict] = None


class IMUDataUpdate(BaseModel):
    """IMU 센서 데이터 수정 스키마"""
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    mag_x: Optional[float] = None
    mag_y: Optional[float] = None
    mag_z: Optional[float] = None
    temperature: Optional[float] = None
    raw_payload: Optional[dict] = None


class IMUDataResponse(BaseModel):
    """IMU 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    mag_x: Optional[float] = None
    mag_y: Optional[float] = None
    mag_z: Optional[float] = None
    temperature: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# LoadCell (로드셀) 센서 스키마
class LoadCellDataCreate(BaseModel):
    """LoadCell 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_value: Optional[int] = None
    weight_kg: Optional[float] = None
    calibrated: Optional[bool] = None
    raw_payload: Optional[dict] = None


class LoadCellDataUpdate(BaseModel):
    """LoadCell 센서 데이터 수정 스키마"""
    raw_value: Optional[int] = None
    weight_kg: Optional[float] = None
    calibrated: Optional[bool] = None
    raw_payload: Optional[dict] = None


class LoadCellDataResponse(BaseModel):
    """LoadCell 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_value: Optional[int] = None
    weight_kg: Optional[float] = None
    calibrated: Optional[bool] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# MQ5 (가스 센서) 스키마
class MQ5DataCreate(BaseModel):
    """MQ5 가스 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    ppm_value: Optional[float] = None
    gas_type: Optional[str] = None
    raw_payload: Optional[dict] = None


class MQ5DataUpdate(BaseModel):
    """MQ5 가스 센서 데이터 수정 스키마"""
    analog_value: Optional[int] = None
    ppm_value: Optional[float] = None
    gas_type: Optional[str] = None
    raw_payload: Optional[dict] = None


class MQ5DataResponse(BaseModel):
    """MQ5 가스 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    ppm_value: Optional[float] = None
    gas_type: Optional[str] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# MQ7 (가스 센서) 스키마
class MQ7DataCreate(BaseModel):
    """MQ7 가스 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    ppm_value: Optional[float] = None
    gas_type: Optional[str] = None
    raw_payload: Optional[dict] = None


class MQ7DataUpdate(BaseModel):
    """MQ7 가스 센서 데이터 수정 스키마"""
    analog_value: Optional[int] = None
    ppm_value: Optional[int] = None
    gas_type: Optional[str] = None
    raw_payload: Optional[dict] = None


class MQ7DataResponse(BaseModel):
    """MQ7 가스 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    ppm_value: Optional[float] = None
    gas_type: Optional[str] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# RFID (RFID 센서) 스키마
class RFIDDataCreate(BaseModel):
    """RFID 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    card_id: Optional[str] = None
    card_type: Optional[str] = None
    read_success: Optional[bool] = None
    raw_payload: Optional[dict] = None


class RFIDDataUpdate(BaseModel):
    """RFID 센서 데이터 수정 스키마"""
    card_id: Optional[str] = None
    card_type: Optional[str] = None
    read_success: Optional[bool] = None
    raw_payload: Optional[dict] = None


class RFIDDataResponse(BaseModel):
    """RFID 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    card_id: Optional[str] = None
    card_type: Optional[str] = None
    read_success: Optional[bool] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# Sound (사운드 센서) 스키마
class SoundDataCreate(BaseModel):
    """Sound 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    db_value: Optional[float] = None
    threshold_exceeded: Optional[bool] = None
    raw_payload: Optional[dict] = None


class SoundDataUpdate(BaseModel):
    """Sound 센서 데이터 수정 스키마"""
    analog_value: Optional[int] = None
    db_value: Optional[float] = None
    threshold_exceeded: Optional[bool] = None
    raw_payload: Optional[dict] = None


class SoundDataResponse(BaseModel):
    """Sound 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    db_value: Optional[float] = None
    threshold_exceeded: Optional[bool] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# TCRT5000 (근접 센서) 스키마
class TCRT5000DataCreate(BaseModel):
    """TCRT5000 근접 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    digital_value: Optional[bool] = None
    analog_value: Optional[int] = None
    object_detected: Optional[bool] = None
    raw_payload: Optional[dict] = None


class TCRT5000DataUpdate(BaseModel):
    """TCRT5000 근접 센서 데이터 수정 스키마"""
    digital_value: Optional[bool] = None
    analog_value: Optional[int] = None
    object_detected: Optional[bool] = None
    raw_payload: Optional[dict] = None


class TCRT5000DataResponse(BaseModel):
    """TCRT5000 근접 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    digital_value: Optional[bool] = None
    analog_value: Optional[int] = None
    object_detected: Optional[bool] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# Ultrasonic (초음파 센서) 스키마
class UltrasonicDataCreate(BaseModel):
    """Ultrasonic 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    distance_cm: Optional[float] = None
    raw_value: Optional[int] = None
    measurement_valid: Optional[bool] = None
    raw_payload: Optional[dict] = None


class UltrasonicDataUpdate(BaseModel):
    """Ultrasonic 센서 데이터 수정 스키마"""
    distance_cm: Optional[float] = None
    raw_value: Optional[int] = None
    measurement_valid: Optional[bool] = None
    raw_payload: Optional[dict] = None


class UltrasonicDataResponse(BaseModel):
    """Ultrasonic 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    distance_cm: Optional[float] = None
    raw_value: Optional[int] = None
    measurement_valid: Optional[bool] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# Edge 센서 스키마들
class EdgeFlameDataCreate(BaseModel):
    """Edge Flame 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    flame_detected: bool
    confidence: Optional[float] = None
    alert_level: Optional[str] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgeFlameDataUpdate(BaseModel):
    """Edge Flame 센서 데이터 수정 스키마"""
    flame_detected: Optional[bool] = None
    confidence: Optional[float] = None
    alert_level: Optional[str] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgeFlameDataResponse(BaseModel):
    """Edge Flame 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    flame_detected: bool
    confidence: Optional[float] = None
    alert_level: Optional[str] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


class EdgePIRDataCreate(BaseModel):
    """Edge PIR 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    motion_detected: bool
    confidence: Optional[float] = None
    motion_direction: Optional[str] = None
    motion_speed: Optional[float] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgePIRDataUpdate(BaseModel):
    """Edge PIR 센서 데이터 수정 스키마"""
    motion_detected: Optional[bool] = None
    confidence: Optional[float] = None
    motion_direction: Optional[str] = None
    motion_speed: Optional[float] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgePIRDataResponse(BaseModel):
    """Edge PIR 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    motion_detected: bool
    confidence: Optional[float] = None
    motion_direction: Optional[str] = None
    motion_speed: Optional[float] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


class EdgeReedDataCreate(BaseModel):
    """Edge Reed 스위치 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    switch_state: bool
    confidence: Optional[float] = None
    magnetic_field_detected: Optional[bool] = None
    magnetic_strength: Optional[float] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgeReedDataUpdate(BaseModel):
    """Edge Reed 스위치 센서 데이터 수정 스키마"""
    switch_state: Optional[bool] = None
    confidence: Optional[float] = None
    magnetic_field_detected: Optional[bool] = None
    magnetic_strength: Optional[float] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgeReedDataResponse(BaseModel):
    """Edge Reed 스위치 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    switch_state: bool
    confidence: Optional[float] = None
    magnetic_field_detected: Optional[bool] = None
    magnetic_strength: Optional[float] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


class EdgeTiltDataCreate(BaseModel):
    """Edge Tilt 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    tilt_detected: bool
    confidence: Optional[float] = None
    tilt_angle: Optional[float] = None
    tilt_direction: Optional[str] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgeTiltDataUpdate(BaseModel):
    """Edge Tilt 센서 데이터 수정 스키마"""
    tilt_detected: Optional[bool] = None
    confidence: Optional[float] = None
    tilt_angle: Optional[float] = None
    tilt_direction: Optional[str] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None


class EdgeTiltDataResponse(BaseModel):
    """Edge Tilt 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    tilt_detected: bool
    confidence: Optional[float] = None
    tilt_angle: Optional[float] = None
    tilt_direction: Optional[str] = None
    processing_time: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# Actuator 로그 스키마들
class ActuatorBuzzerDataCreate(BaseModel):
    """Buzzer 액추에이터 로그 생성 스키마"""
    time: datetime
    device_id: str
    buzzer_type: str
    state: str
    freq_hz: Optional[int] = None
    duration_ms: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorBuzzerDataUpdate(BaseModel):
    """Buzzer 액추에이터 로그 수정 스키마"""
    buzzer_type: Optional[str] = None
    state: Optional[str] = None
    freq_hz: Optional[int] = None
    duration_ms: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorBuzzerDataResponse(BaseModel):
    """Buzzer 액추에이터 로그 응답 스키마"""
    time: datetime
    device_id: str
    buzzer_type: str
    state: str
    freq_hz: Optional[int] = None
    duration_ms: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


class ActuatorIRTXDataCreate(BaseModel):
    """IR TX 액추에이터 로그 생성 스키마"""
    time: datetime
    device_id: str
    protocol: Optional[str] = None
    address_hex: Optional[str] = None
    command_hex: str
    repeat_cnt: Optional[int] = None
    raw_payload: Optional[dict] = None


class ActuatorIRTXDataUpdate(BaseModel):
    """IR TX 액추에이터 로그 수정 스키마"""
    protocol: Optional[str] = None
    address_hex: Optional[str] = None
    command_hex: Optional[str] = None
    repeat_cnt: Optional[int] = None
    raw_payload: Optional[dict] = None


class ActuatorIRTXDataResponse(BaseModel):
    """IR TX 액추에이터 로그 응답 스키마"""
    time: datetime
    device_id: str
    protocol: Optional[str] = None
    address_hex: Optional[str] = None
    command_hex: str
    repeat_cnt: Optional[int] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# ============================================================================
# Actuator 로그 관련 스키마
# ============================================================================

class ActuatorBuzzerDataCreate(BaseModel):
    """Buzzer 액추에이터 로그 생성 스키마"""
    time: datetime
    device_id: str
    buzzer_type: str
    state: str
    freq_hz: Optional[int] = None
    duration_ms: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorBuzzerDataUpdate(BaseModel):
    """Buzzer 액추에이터 로그 수정 스키마"""
    buzzer_type: Optional[str] = None
    state: Optional[str] = None
    freq_hz: Optional[int] = None
    duration_ms: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorBuzzerDataResponse(BaseModel):
    """Buzzer 액추에이터 로그 응답 스키마"""
    time: datetime
    device_id: str
    buzzer_type: str
    state: str
    freq_hz: Optional[int] = None
    duration_ms: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


class ActuatorIRTXDataCreate(BaseModel):
    """IR TX 액추에이터 로그 생성 스키마"""
    time: datetime
    device_id: str
    protocol: Optional[str] = None
    address_hex: Optional[str] = None
    command_hex: str
    repeat_cnt: Optional[int] = None
    raw_payload: Optional[dict] = None


class ActuatorIRTXDataUpdate(BaseModel):
    """IR TX 액추에이터 로그 수정 스키마"""
    protocol: Optional[str] = None
    address_hex: Optional[str] = None
    command_hex: Optional[str] = None
    repeat_cnt: Optional[int] = None
    raw_payload: Optional[dict] = None


class ActuatorIRTXDataResponse(BaseModel):
    """IR TX 액추에이터 로그 응답 스키마"""
    time: datetime
    device_id: str
    protocol: Optional[str] = None
    address_hex: Optional[str] = None
    command_hex: str
    repeat_cnt: Optional[int] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


class ActuatorRelayDataCreate(BaseModel):
    """Relay 액추에이터 로그 생성 스키마"""
    time: datetime
    device_id: str
    channel: int
    state: str
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorRelayDataUpdate(BaseModel):
    """Relay 액추에이터 로그 수정 스키마"""
    channel: Optional[int] = None
    state: Optional[str] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorRelayDataResponse(BaseModel):
    """Relay 액추에이터 로그 응답 스키마"""
    time: datetime
    device_id: str
    channel: int
    state: str
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


class ActuatorServoDataCreate(BaseModel):
    """Servo 액추에이터 로그 생성 스키마"""
    time: datetime
    device_id: str
    channel: int
    angle_deg: Optional[float] = None
    pwm_us: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorServoDataUpdate(BaseModel):
    """Servo 액추에이터 로그 수정 스키마"""
    channel: Optional[int] = None
    angle_deg: Optional[float] = None
    pwm_us: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None


class ActuatorServoDataResponse(BaseModel):
    """Servo 액추에이터 로그 응답 스키마"""
    time: datetime
    device_id: str
    channel: int
    angle_deg: Optional[float] = None
    pwm_us: Optional[int] = None
    reason: Optional[str] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# Device RTC 상태 스키마
class DeviceRTCDataCreate(BaseModel):
    """Device RTC 상태 생성 스키마"""
    time: datetime
    device_id: str
    rtc_epoch_s: Optional[int] = None
    drift_ms: Optional[int] = None
    sync_source: Optional[str] = None
    raw_payload: Optional[dict] = None


class DeviceRTCDataUpdate(BaseModel):
    """Device RTC 상태 수정 스키마"""
    rtc_epoch_s: Optional[int] = None
    drift_ms: Optional[int] = None
    sync_source: Optional[str] = None
    raw_payload: Optional[dict] = None


class DeviceRTCDataResponse(BaseModel):
    """Device RTC 상태 응답 스키마"""
    time: datetime
    device_id: str
    rtc_epoch_s: Optional[int] = None
    drift_ms: Optional[int] = None
    sync_source: Optional[str] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# ============================================================================
# Raw 센서 스키마 (ORM 모드 문제 해결)
# ============================================================================

# Raw CDS 센서 스키마
class SensorRawCDSCreate(BaseModel):
    """Raw CDS 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    lux_value: Optional[float] = None
    raw_payload: Optional[dict] = None


class SensorRawCDSResponse(BaseModel):
    """Raw CDS 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    analog_value: Optional[int] = None
    lux_value: Optional[float] = None
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True


# Raw LoadCell 센서 스키마
class SensorRawLoadCellCreate(BaseModel):
    """Raw LoadCell 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None


class SensorRawLoadCellUpdate(BaseModel):
    """Raw LoadCell 센서 데이터 수정 스키마"""
    raw_payload: Optional[dict] = None


class SensorRawLoadCellResponse(BaseModel):
    """Raw LoadCell 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True


# Raw MQ5 센서 스키마
class SensorRawMQ5Create(BaseModel):
    """Raw MQ5 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None


class SensorRawMQ5Update(BaseModel):
    """Raw MQ5 센서 데이터 수정 스키마"""
    raw_payload: Optional[dict] = None


class SensorRawMQ5Response(BaseModel):
    """Raw MQ5 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True


# Raw MQ7 센서 스키마
class SensorRawMQ7Create(BaseModel):
    """Raw MQ7 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None


class SensorRawMQ7Update(BaseModel):
    """Raw MQ7 센서 데이터 수정 스키마"""
    raw_payload: Optional[dict] = None


class SensorRawMQ7Response(BaseModel):
    """Raw MQ7 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True


# Raw RFID 센서 스키마
class SensorRawRFIDCreate(BaseModel):
    """Raw RFID 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None


class SensorRawRFIDUpdate(BaseModel):
    """Raw RFID 센서 데이터 수정 스키마"""
    raw_payload: Optional[dict] = None


class SensorRawRFIDResponse(BaseModel):
    """Raw RFID 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True


# Raw Sound 센서 스키마
class SensorRawSoundCreate(BaseModel):
    """Raw Sound 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None


class SensorRawSoundUpdate(BaseModel):
    """Raw Sound 센서 데이터 수정 스키마"""
    raw_payload: Optional[dict] = None


class SensorRawSoundResponse(BaseModel):
    """Raw Sound 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True


# Raw TCRT5000 센서 스키마
class SensorRawTCRT5000Create(BaseModel):
    """Raw TCRT5000 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None


class SensorRawTCRT5000Update(BaseModel):
    """Raw TCRT5000 센서 데이터 수정 스키마"""
    raw_payload: Optional[dict] = None


class SensorRawTCRT5000Response(BaseModel):
    """Raw TCRT5000 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True


# Raw Ultrasonic 센서 스키마
class SensorRawUltrasonicCreate(BaseModel):
    """Raw Ultrasonic 센서 데이터 생성 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None


class SensorRawUltrasonicUpdate(BaseModel):
    """Raw Ultrasonic 센서 데이터 수정 스키마"""
    raw_payload: Optional[dict] = None


class SensorRawUltrasonicResponse(BaseModel):
    """Raw Ultrasonic 센서 데이터 응답 스키마"""
    time: datetime
    device_id: str
    raw_payload: Optional[dict] = None

    class Config:
        from_attributes = True
        orm_mode = True


# ============================================================================
# 온도 센서 원시 데이터 스키마
# ============================================================================

class SensorRawTemperatureBase(BaseModel):
    """온도 센서 원시 데이터 기본 스키마"""
    temperature_celsius: float = Field(..., description="섭씨 단위의 온도 값")
    humidity_percent: Optional[float] = Field(None, description="상대 습도 값 (%)")
    raw_payload: Optional[Dict[str, Any]] = Field(None, description="원시 데이터")

    @validator('temperature_celsius')
    def validate_temperature(cls, v):
        if v < -273.15:  # 절대 영도 이하
            raise ValueError('온도는 절대 영도(-273.15°C) 이상이어야 합니다')
        if v > 1000:  # 극한 온도 제한
            raise ValueError('온도는 1000°C 이하여야 합니다')
        return v

    @validator('humidity_percent')
    def validate_humidity(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('습도는 0%에서 100% 사이여야 합니다')
        return v

class SensorRawTemperatureCreate(SensorRawTemperatureBase):
    """온도 센서 원시 데이터 생성 스키마"""
    time: datetime = Field(..., description="측정 시간")
    device_id: str = Field(..., description="디바이스 ID")

class SensorRawTemperatureUpdate(BaseModel):
    """온도 센서 원시 데이터 업데이트 스키마"""
    temperature_celsius: Optional[float] = Field(None)
    humidity_percent: Optional[float] = Field(None)
    raw_payload: Optional[Dict[str, Any]] = Field(None)

class SensorRawTemperatureResponse(SensorRawTemperatureBase):
    """온도 센서 원시 데이터 응답 스키마"""
    time: datetime
    device_id: str

    class Config:
        from_attributes = True
        orm_mode = True

class SensorRawTemperatureListResponse(BaseModel):
    """온도 센서 원시 데이터 목록 응답 스키마"""
    items: List[SensorRawTemperatureResponse]
    total: int
    page: int
    size: int
    pages: int

# ============================================================================
# 사용자 관계 관련 스키마
# ============================================================================

class UserRelationshipBase(BaseModel):
    """사용자 관계 기본 스키마"""
    subject_user_id: UUID = Field(..., description="관계의 주체 (돌봄 제공자, 가족, 관리자)")
    target_user_id: UUID = Field(..., description="관계의 대상 (돌봄을 받는 사용자)")
    relationship_type: str = Field(..., description="관계 유형")
    status: str = Field("active", description="관계 상태")

    @validator('relationship_type')
    def validate_relationship_type(cls, v):
        allowed_types = ['caregiver', 'family', 'admin']
        if v not in allowed_types:
            raise ValueError(f'허용되지 않는 관계 유형입니다. 허용된 유형: {allowed_types}')
        return v

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['pending', 'active', 'inactive']
        if v not in allowed_statuses:
            raise ValueError(f'허용되지 않는 상태입니다. 허용된 상태: {allowed_statuses}')
        return v


class UserRelationshipCreate(UserRelationshipBase):
    """사용자 관계 생성 요청 스키마"""
    pass


class UserRelationshipUpdate(BaseModel):
    """사용자 관계 수정 요청 스키마"""
    status: Optional[str] = Field(None, description="관계 상태")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['pending', 'active', 'inactive']
            if v not in allowed_statuses:
                raise ValueError(f'허용되지 않는 상태입니다. 허용된 상태: {allowed_statuses}')
        return v


class UserRelationshipResponse(UserRelationshipBase):
    """사용자 관계 응답 스키마"""
    relationship_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True


class UserRelationshipListResponse(BaseModel):
    """사용자 관계 목록 응답 스키마"""
    relationships: List[UserRelationshipResponse]
    total: int
    page: int
    size: int


# ============================================================================
# 사용자 프로필 관련 스키마
# ============================================================================

class UserProfileBase(BaseModel):
    """사용자 프로필 기본 스키마"""
    date_of_birth: date = Field(..., description="사용자의 생년월일")
    gender: str = Field(..., description="성별")
    address: Optional[str] = Field(None, max_length=500, description="주소")
    address_detail: Optional[str] = Field(None, max_length=200, description="상세 주소")
    medical_history: Optional[str] = Field(None, max_length=1000, description="병력")
    significant_notes: Optional[str] = Field(None, max_length=1000, description="특이사항")
    current_status: Optional[str] = Field(None, max_length=1000, description="현재 상태")

    @validator('gender')
    def validate_gender(cls, v):
        allowed_genders = ['male', 'female', 'other']
        if v not in allowed_genders:
            raise ValueError(f'허용되지 않는 성별입니다. 허용된 성별: {allowed_genders}')
        return v


class UserProfileCreate(UserProfileBase):
    """사용자 프로필 생성 요청 스키마"""
    pass


class UserProfileUpdate(BaseModel):
    """사용자 프로필 수정 요청 스키마"""
    address: Optional[str] = Field(None, max_length=500)
    address_detail: Optional[str] = Field(None, max_length=200)
    medical_history: Optional[str] = Field(None, max_length=1000)
    significant_notes: Optional[str] = Field(None, max_length=1000)
    current_status: Optional[str] = Field(None, max_length=1000)


class UserProfileResponse(UserProfileBase):
    """사용자 프로필 응답 스키마"""
    user_id: UUID
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        orm_mode = True


class UserProfileListResponse(BaseModel):
    """사용자 프로필 목록 응답 스키마"""
    profiles: List[UserProfileResponse]
    total: int
    page: int
    size: int 

# ============================================================================
# 홈 상태 스냅샷 스키마 (Digital Twin State)
# ============================================================================

class HomeStateSnapshotBase(BaseModel):
    """홈 상태 스냅샷 기본 스키마"""
    entrance_pir_motion: Optional[bool] = Field(None, description="입구 PIR 모션 감지 상태")
    entrance_rfid_status: Optional[str] = Field(None, description="입구 RFID 상태")
    entrance_reed_is_closed: Optional[bool] = Field(None, description="입구 리드 스위치 닫힘 상태")
    livingroom_pir_1_motion: Optional[bool] = Field(None, description="거실 PIR1 모션 감지 상태")
    livingroom_pir_2_motion: Optional[bool] = Field(None, description="거실 PIR2 모션 감지 상태")
    livingroom_sound_db: Optional[float] = Field(None, description="거실 소음 데시벨")
    livingroom_mq7_co_ppm: Optional[float] = Field(None, description="거실 일산화탄소 농도 (PPM)")
    livingroom_button_state: Optional[str] = Field(None, description="거실 버튼 상태")
    kitchen_pir_motion: Optional[bool] = Field(None, description="주방 PIR 모션 감지 상태")
    kitchen_sound_db: Optional[float] = Field(None, description="주방 소음 데시벨")
    kitchen_mq5_gas_ppm: Optional[float] = Field(None, description="주방 가스 농도 (PPM)")
    kitchen_loadcell_1_kg: Optional[float] = Field(None, description="주방 로드셀1 무게 (kg)")
    kitchen_loadcell_2_kg: Optional[float] = Field(None, description="주방 로드셀2 무게 (kg)")
    kitchen_button_state: Optional[str] = Field(None, description="주방 버튼 상태")
    kitchen_buzzer_is_on: Optional[bool] = Field(None, description="주방 부저 작동 상태")
    bedroom_pir_motion: Optional[bool] = Field(None, description="침실 PIR 모션 감지 상태")
    bedroom_sound_db: Optional[float] = Field(None, description="침실 소음 데시벨")
    bedroom_mq7_co_ppm: Optional[float] = Field(None, description="침실 일산화탄소 농도 (PPM)")
    bedroom_loadcell_kg: Optional[float] = Field(None, description="침실 로드셀 무게 (kg)")
    bedroom_button_state: Optional[str] = Field(None, description="침실 버튼 상태")
    bathroom_pir_motion: Optional[bool] = Field(None, description="욕실 PIR 모션 감지 상태")
    bathroom_sound_db: Optional[float] = Field(None, description="욕실 소음 데시벨")
    bathroom_temp_celsius: Optional[float] = Field(None, description="욕실 온도 (섭씨)")
    bathroom_button_state: Optional[str] = Field(None, description="욕실 버튼 상태")
    detected_activity: Optional[str] = Field(None, description="감지된 활동")
    alert_level: Optional[str] = Field(None, description="경보 수준 (Normal, Attention, Warning, Emergency)")
    alert_reason: Optional[str] = Field(None, description="경보 발생 이유")
    action_log: Optional[Dict[str, Any]] = Field(None, description="처리 내역 및 결과 (JSON)")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="향후 확장을 위한 예비 데이터 (JSON)")

    @validator('alert_level')
    def validate_alert_level(cls, v):
        if v and v not in ['Normal', 'Attention', 'Warning', 'Emergency']:
            raise ValueError('alert_level은 Normal, Attention, Warning, Emergency 중 하나여야 합니다')
        return v

class HomeStateSnapshotCreate(HomeStateSnapshotBase):
    """홈 상태 스냅샷 생성 스키마"""
    time: datetime = Field(..., description="스냅샷 시간")
    user_id: UUID = Field(..., description="사용자 ID")

class HomeStateSnapshotUpdate(BaseModel):
    """홈 상태 스냅샷 업데이트 스키마"""
    entrance_pir_motion: Optional[bool] = Field(None)
    entrance_rfid_status: Optional[str] = Field(None)
    entrance_reed_is_closed: Optional[bool] = Field(None)
    livingroom_pir_1_motion: Optional[bool] = Field(None)
    livingroom_pir_2_motion: Optional[bool] = Field(None)
    livingroom_sound_db: Optional[float] = Field(None)
    livingroom_mq7_co_ppm: Optional[float] = Field(None)
    livingroom_button_state: Optional[str] = Field(None)
    kitchen_pir_motion: Optional[bool] = Field(None)
    kitchen_sound_db: Optional[float] = Field(None)
    kitchen_mq5_gas_ppm: Optional[float] = Field(None)
    kitchen_loadcell_1_kg: Optional[float] = Field(None)
    kitchen_loadcell_2_kg: Optional[float] = Field(None)
    kitchen_button_state: Optional[str] = Field(None)
    kitchen_buzzer_is_on: Optional[bool] = Field(None)
    bedroom_pir_motion: Optional[bool] = Field(None)
    bedroom_sound_db: Optional[float] = Field(None)
    bedroom_mq7_co_ppm: Optional[float] = Field(None)
    bedroom_loadcell_kg: Optional[float] = Field(None)
    bedroom_button_state: Optional[str] = Field(None)
    bathroom_pir_motion: Optional[bool] = Field(None)
    bathroom_sound_db: Optional[float] = Field(None)
    bathroom_temp_celsius: Optional[float] = Field(None)
    bathroom_button_state: Optional[str] = Field(None)
    detected_activity: Optional[str] = Field(None)
    alert_level: Optional[str] = Field(None)
    alert_reason: Optional[str] = Field(None)
    action_log: Optional[Dict[str, Any]] = Field(None)
    extra_data: Optional[Dict[str, Any]] = Field(None)

class HomeStateSnapshotResponse(HomeStateSnapshotBase):
    """홈 상태 스냅샷 응답 스키마"""
    time: datetime
    user_id: UUID

    class Config:
        from_attributes = True
        orm_mode = True

class HomeStateSnapshotListResponse(BaseModel):
    """홈 상태 스냅샷 목록 응답 스키마"""
    items: List[HomeStateSnapshotResponse]
    total: int
    page: int
    size: int
    pages: int

# ============================================================================
# 버튼 이벤트 센서 스키마
# ============================================================================

class SensorEventButtonBase(BaseModel):
    """버튼 이벤트 센서 기본 스키마"""
    button_state: str = Field(..., description="버튼의 물리적 상태")
    event_type: str = Field(..., description="버튼 입력의 목적")
    press_duration_ms: Optional[int] = Field(None, description="버튼 누름 지속 시간 (밀리초)")
    raw_payload: Optional[Dict[str, Any]] = Field(None, description="원시 데이터")

    @validator('button_state')
    def validate_button_state(cls, v):
        if v not in ['PRESSED', 'RELEASED', 'LONG_PRESS']:
            raise ValueError('button_state는 PRESSED, RELEASED, LONG_PRESS 중 하나여야 합니다')
        return v

    @validator('event_type')
    def validate_event_type(cls, v):
        if v not in ['crisis_acknowledged', 'assistance_request', 'medication_check']:
            raise ValueError('event_type는 crisis_acknowledged, assistance_request, medication_check 중 하나여야 합니다')
        return v

class SensorEventButtonCreate(SensorEventButtonBase):
    """버튼 이벤트 센서 생성 스키마"""
    time: datetime = Field(..., description="이벤트 발생 시간")
    device_id: str = Field(..., description="디바이스 ID")

class SensorEventButtonUpdate(BaseModel):
    """버튼 이벤트 센서 업데이트 스키마"""
    button_state: Optional[str] = Field(None)
    event_type: Optional[str] = Field(None)
    press_duration_ms: Optional[int] = Field(None)
    raw_payload: Optional[Dict[str, Any]] = Field(None)

class SensorEventButtonResponse(SensorEventButtonBase):
    """버튼 이벤트 센서 응답 스키마"""
    time: datetime
    device_id: str

    class Config:
        from_attributes = True
        orm_mode = True

class SensorEventButtonListResponse(BaseModel):
    """버튼 이벤트 센서 목록 응답 스키마"""
    items: List[SensorEventButtonResponse]
    total: int
    page: int
    size: int
    pages: int 