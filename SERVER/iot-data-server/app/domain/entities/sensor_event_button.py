from datetime import datetime
from typing import Optional, Dict, Any


class SensorEventButton:
    """버튼 이벤트 센서 도메인 엔티티"""
    
    def __init__(
        self,
        time: datetime,
        device_id: str,
        button_state: str,
        event_type: str,
        press_duration_ms: Optional[int] = None,
        raw_payload: Optional[Dict[str, Any]] = None
    ):
        self.time = time
        self.device_id = device_id
        self.button_state = button_state
        self.event_type = event_type
        self.press_duration_ms = press_duration_ms
        self.raw_payload = raw_payload or {}

    def is_long_press(self) -> bool:
        """장시간 누름 여부 확인 (1초 이상)"""
        return self.press_duration_ms and self.press_duration_ms >= 1000

    def is_crisis_event(self) -> bool:
        """위기 상황 이벤트 여부 확인"""
        return self.event_type == 'crisis_acknowledged'

    def is_assistance_request(self) -> bool:
        """도움 요청 이벤트 여부 확인"""
        return self.event_type == 'assistance_request'

    def is_medication_check(self) -> bool:
        """복약 체크 이벤트 여부 확인"""
        return self.event_type == 'medication_check'

    def get_press_duration_seconds(self) -> Optional[float]:
        """누름 지속 시간을 초 단위로 반환"""
        if self.press_duration_ms:
            return self.press_duration_ms / 1000.0
        return None

    def add_raw_data(self, key: str, value: Any) -> None:
        """원시 데이터에 키-값 쌍 추가"""
        self.raw_payload[key] = value

    def get_raw_data(self, key: str, default: Any = None) -> Any:
        """원시 데이터에서 특정 키의 값 반환"""
        return self.raw_payload.get(key, default)

    def is_valid_button_state(self) -> bool:
        """유효한 버튼 상태인지 확인"""
        valid_states = ['PRESSED', 'RELEASED', 'LONG_PRESS']
        return self.button_state in valid_states

    def is_valid_event_type(self) -> bool:
        """유효한 이벤트 타입인지 확인"""
        valid_types = ['crisis_acknowledged', 'assistance_request', 'medication_check']
        return self.event_type in valid_types

    def get_event_priority(self) -> int:
        """이벤트 우선순위 반환 (높을수록 우선순위 높음)"""
        priority_map = {
            'crisis_acknowledged': 3,  # 최고 우선순위
            'assistance_request': 2,   # 높은 우선순위
            'medication_check': 1      # 일반 우선순위
        }
        return priority_map.get(self.event_type, 0)

    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "time": self.time,
            "device_id": self.device_id,
            "button_state": self.button_state,
            "event_type": self.event_type,
            "press_duration_ms": self.press_duration_ms,
            "raw_payload": self.raw_payload
        }

    def __str__(self) -> str:
        """엔티티를 문자열로 표현"""
        return f"SensorEventButton(time={self.time}, device_id={self.device_id}, event_type={self.event_type}, button_state={self.button_state})"
