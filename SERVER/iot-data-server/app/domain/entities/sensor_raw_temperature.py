from datetime import datetime
from typing import Optional, Dict, Any


class SensorRawTemperature:
    """온도 센서 원시 데이터 도메인 엔티티"""
    
    def __init__(
        self,
        time: datetime,
        device_id: str,
        temperature_celsius: float,
        humidity_percent: Optional[float] = None,
        raw_payload: Optional[Dict[str, Any]] = None
    ):
        self.time = time
        self.device_id = device_id
        self.temperature_celsius = temperature_celsius
        self.humidity_percent = humidity_percent
        self.raw_payload = raw_payload or {}

    def get_temperature_fahrenheit(self) -> float:
        """섭씨를 화씨로 변환"""
        return (self.temperature_celsius * 9/5) + 32

    def get_temperature_kelvin(self) -> float:
        """섭씨를 켈빈으로 변환"""
        return self.temperature_celsius + 273.15

    def is_extreme_temperature(self) -> bool:
        """극한 온도 여부 확인 (0°C 이하 또는 50°C 이상)"""
        return self.temperature_celsius <= 0 or self.temperature_celsius >= 50

    def is_comfortable_temperature(self) -> bool:
        """쾌적한 온도 여부 확인 (18°C ~ 26°C)"""
        return 18 <= self.temperature_celsius <= 26

    def is_humidity_comfortable(self) -> bool:
        """쾌적한 습도 여부 확인 (30% ~ 70%)"""
        if self.humidity_percent is None:
            return False
        return 30 <= self.humidity_percent <= 70

    def get_heat_index(self) -> Optional[float]:
        """체감 온도 계산 (Heat Index) - 습도가 있을 때만"""
        if self.humidity_percent is None:
            return None
        
        # 간단한 체감 온도 공식 (Steadman 공식 기반)
        t = self.temperature_celsius
        h = self.humidity_percent
        
        if t < 27:
            return t  # 27°C 미만에서는 체감 온도 변화 미미
        
        # 체감 온도 계산
        hi = 0.5 * (t + 61.0 + ((t - 68.0) * 1.2) + (h * 0.094))
        
        # 보정
        if hi > 80:
            hi = -42.379 + 2.04901523 * t + 10.14333127 * h - 0.22475541 * t * h - 6.83783 * 10**-3 * t**2 - 5.481717 * 10**-2 * h**2 + 1.22874 * 10**-3 * t**2 * h + 8.5282 * 10**-4 * t * h**2 - 1.99 * 10**-6 * t**2 * h**2
        
        return round(hi, 1)

    def add_raw_data(self, key: str, value: Any) -> None:
        """원시 데이터에 키-값 쌍 추가"""
        self.raw_payload[key] = value

    def get_raw_data(self, key: str, default: Any = None) -> Any:
        """원시 데이터에서 특정 키의 값 반환"""
        return self.raw_payload.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "time": self.time,
            "device_id": self.device_id,
            "temperature_celsius": self.temperature_celsius,
            "humidity_percent": self.humidity_percent,
            "raw_payload": self.raw_payload
        }

    def __str__(self) -> str:
        """엔티티를 문자열로 표현"""
        return f"SensorRawTemperature(time={self.time}, device_id={self.device_id}, temp={self.temperature_celsius}°C, humidity={self.humidity_percent}%)"
