from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID


class HomeStateSnapshot:
    """홈 상태 스냅샷 도메인 엔티티 (Digital Twin State)"""
    
    def __init__(
        self,
        time: datetime,
        user_id: UUID,
        entrance_pir_motion: Optional[bool] = None,
        entrance_rfid_status: Optional[str] = None,
        entrance_reed_is_closed: Optional[bool] = None,
        livingroom_pir_1_motion: Optional[bool] = None,
        livingroom_pir_2_motion: Optional[bool] = None,
        livingroom_sound_db: Optional[float] = None,
        livingroom_mq7_co_ppm: Optional[float] = None,
        livingroom_button_state: Optional[str] = None,
        kitchen_pir_motion: Optional[bool] = None,
        kitchen_sound_db: Optional[float] = None,
        kitchen_mq5_gas_ppm: Optional[float] = None,
        kitchen_loadcell_1_kg: Optional[float] = None,
        kitchen_loadcell_2_kg: Optional[float] = None,
        kitchen_button_state: Optional[str] = None,
        kitchen_buzzer_is_on: Optional[bool] = None,
        bedroom_pir_motion: Optional[bool] = None,
        bedroom_sound_db: Optional[float] = None,
        bedroom_mq7_co_ppm: Optional[float] = None,
        bedroom_loadcell_kg: Optional[float] = None,
        bedroom_button_state: Optional[str] = None,
        bathroom_pir_motion: Optional[bool] = None,
        bathroom_sound_db: Optional[float] = None,
        bathroom_temp_celsius: Optional[float] = None,
        bathroom_button_state: Optional[str] = None,
        detected_activity: Optional[str] = None,
        alert_level: Optional[str] = None,
        alert_reason: Optional[str] = None,
        action_log: Optional[Dict[str, Any]] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        self.time = time
        self.user_id = user_id
        self.entrance_pir_motion = entrance_pir_motion
        self.entrance_rfid_status = entrance_rfid_status
        self.entrance_reed_is_closed = entrance_reed_is_closed
        self.livingroom_pir_1_motion = livingroom_pir_1_motion
        self.livingroom_pir_2_motion = livingroom_pir_2_motion
        self.livingroom_sound_db = livingroom_sound_db
        self.livingroom_mq7_co_ppm = livingroom_mq7_co_ppm
        self.livingroom_button_state = livingroom_button_state
        self.kitchen_pir_motion = kitchen_pir_motion
        self.kitchen_sound_db = kitchen_sound_db
        self.kitchen_mq5_gas_ppm = kitchen_mq5_gas_ppm
        self.kitchen_loadcell_1_kg = kitchen_loadcell_1_kg
        self.kitchen_loadcell_2_kg = kitchen_loadcell_2_kg
        self.kitchen_button_state = kitchen_button_state
        self.kitchen_buzzer_is_on = kitchen_buzzer_is_on
        self.bedroom_pir_motion = bedroom_pir_motion
        self.bedroom_sound_db = bedroom_sound_db
        self.bedroom_mq7_co_ppm = bedroom_mq7_co_ppm
        self.bedroom_loadcell_kg = bedroom_loadcell_kg
        self.bedroom_button_state = bedroom_button_state
        self.bathroom_pir_motion = bathroom_pir_motion
        self.bathroom_sound_db = bathroom_sound_db
        self.bathroom_temp_celsius = bathroom_temp_celsius
        self.bathroom_button_state = bathroom_button_state
        self.detected_activity = detected_activity
        self.alert_level = alert_level
        self.alert_reason = alert_reason
        self.action_log = action_log or {}
        self.extra_data = extra_data or {}

    def update_alert_level(self, new_level: str, reason: str) -> None:
        """경보 수준 업데이트"""
        valid_levels = ['Normal', 'Attention', 'Warning', 'Emergency']
        if new_level not in valid_levels:
            raise ValueError(f'경보 수준은 {", ".join(valid_levels)} 중 하나여야 합니다')
        
        self.alert_level = new_level
        self.alert_reason = reason

    def add_action_log(self, action: str, result: str, notes: str = None) -> None:
        """처리 내역 추가"""
        action_entry = {
            "action_taken": action,
            "timestamp": datetime.utcnow().isoformat(),
            "result": result,
            "notes": notes
        }
        
        if "actions" not in self.action_log:
            self.action_log["actions"] = []
        
        self.action_log["actions"].append(action_entry)

    def is_emergency_level(self) -> bool:
        """응급 상황 여부 확인"""
        return self.alert_level == 'Emergency'

    def is_attention_required(self) -> bool:
        """주의가 필요한 상황 여부 확인"""
        return self.alert_level in ['Attention', 'Warning', 'Emergency']

    def get_motion_count(self) -> int:
        """모션 감지된 구역 수 계산"""
        motion_sensors = [
            self.entrance_pir_motion,
            self.livingroom_pir_1_motion,
            self.livingroom_pir_2_motion,
            self.kitchen_pir_motion,
            self.bedroom_pir_motion,
            self.bathroom_pir_motion
        ]
        return sum(1 for sensor in motion_sensors if sensor is True)

    def get_environmental_alerts(self) -> list:
        """환경 관련 경보 목록 반환"""
        alerts = []
        
        if self.livingroom_mq7_co_ppm and self.livingroom_mq7_co_ppm > 50:
            alerts.append(f"거실 일산화탄소 농도 높음: {self.livingroom_mq7_co_ppm} PPM")
        
        if self.kitchen_mq5_gas_ppm and self.kitchen_mq5_gas_ppm > 100:
            alerts.append(f"주방 가스 농도 높음: {self.kitchen_mq5_gas_ppm} PPM")
        
        if self.bedroom_mq7_co_ppm and self.bedroom_mq7_co_ppm > 50:
            alerts.append(f"침실 일산화탄소 농도 높음: {self.bedroom_mq7_co_ppm} PPM")
        
        if self.bathroom_temp_celsius and self.bathroom_temp_celsius > 40:
            alerts.append(f"욕실 온도 높음: {self.bathroom_temp_celsius}°C")
        
        return alerts

    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "time": self.time,
            "user_id": str(self.user_id),
            "entrance_pir_motion": self.entrance_pir_motion,
            "entrance_rfid_status": self.entrance_rfid_status,
            "entrance_reed_is_closed": self.entrance_reed_is_closed,
            "livingroom_pir_1_motion": self.livingroom_pir_1_motion,
            "livingroom_pir_2_motion": self.livingroom_pir_2_motion,
            "livingroom_sound_db": self.livingroom_sound_db,
            "livingroom_mq7_co_ppm": self.livingroom_mq7_co_ppm,
            "livingroom_button_state": self.livingroom_button_state,
            "kitchen_pir_motion": self.kitchen_pir_motion,
            "kitchen_sound_db": self.kitchen_sound_db,
            "kitchen_mq5_gas_ppm": self.kitchen_mq5_gas_ppm,
            "kitchen_loadcell_1_kg": self.kitchen_loadcell_1_kg,
            "kitchen_loadcell_2_kg": self.kitchen_loadcell_2_kg,
            "kitchen_button_state": self.kitchen_button_state,
            "kitchen_buzzer_is_on": self.kitchen_buzzer_is_on,
            "bedroom_pir_motion": self.bedroom_pir_motion,
            "bedroom_sound_db": self.bedroom_sound_db,
            "bedroom_mq7_co_ppm": self.bedroom_mq7_co_ppm,
            "bedroom_loadcell_kg": self.bedroom_loadcell_kg,
            "bedroom_button_state": self.bedroom_button_state,
            "bathroom_pir_motion": self.bathroom_pir_motion,
            "bathroom_sound_db": self.bathroom_sound_db,
            "bathroom_temp_celsius": self.bathroom_temp_celsius,
            "bathroom_button_state": self.bathroom_button_state,
            "detected_activity": self.detected_activity,
            "alert_level": self.alert_level,
            "alert_reason": self.alert_reason,
            "action_log": self.action_log,
            "extra_data": self.extra_data
        }
