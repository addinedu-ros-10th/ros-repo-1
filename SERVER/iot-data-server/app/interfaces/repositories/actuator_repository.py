"""
Actuator 로그 리포지토리 인터페이스

액추에이터 로그 데이터에 대한 데이터 접근 계층 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.infrastructure.models import (
    ActuatorLogBuzzer, ActuatorLogIRTX, 
    ActuatorLogRelay, ActuatorLogServo
)


class IActuatorBuzzerRepository(ABC):
    """Buzzer 액추에이터 로그 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create(self, actuator_data: ActuatorLogBuzzer) -> ActuatorLogBuzzer:
        """Buzzer 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogBuzzer]:
        """ID로 Buzzer 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogBuzzer]:
        """최신 Buzzer 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        buzzer_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogBuzzer]:
        """Buzzer 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogBuzzer]:
        """Buzzer 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Buzzer 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Buzzer 액추에이터 로그 통계 조회"""
        pass


class IActuatorIRTXRepository(ABC):
    """IR TX 액추에이터 로그 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create(self, actuator_data: ActuatorLogIRTX) -> ActuatorLogIRTX:
        """IR TX 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogIRTX]:
        """ID로 IR TX 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogIRTX]:
        """최신 IR TX 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        protocol: Optional[str] = None,
        command_hex: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogIRTX]:
        """IR TX 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogIRTX]:
        """IR TX 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """IR TX 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """IR TX 액추에이터 로그 통계 조회"""
        pass


class IActuatorRelayRepository(ABC):
    """Relay 액추에이터 로그 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create(self, actuator_data: ActuatorLogRelay) -> ActuatorLogRelay:
        """Relay 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogRelay]:
        """ID로 Relay 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogRelay]:
        """최신 Relay 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogRelay]:
        """Relay 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogRelay]:
        """Relay 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Relay 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Relay 액추에이터 로그 통계 조회"""
        pass


class IActuatorServoRepository(ABC):
    """Servo 액추에이터 로그 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create(self, actuator_data: ActuatorLogServo) -> ActuatorLogServo:
        """Servo 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogServo]:
        """ID로 Servo 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogServo]:
        """최신 Servo 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[int] = None,
        angle_deg: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogServo]:
        """Servo 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogServo]:
        """Servo 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Servo 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Servo 액추에이터 로그 통계 조회"""
        pass
