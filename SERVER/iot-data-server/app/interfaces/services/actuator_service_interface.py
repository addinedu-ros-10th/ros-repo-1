"""
Actuator 로그 서비스 인터페이스

액추에이터 로그 데이터에 대한 비즈니스 로직 계층 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime


class IActuatorBuzzerService(ABC):
    """Buzzer 액추에이터 로그 서비스 인터페이스"""
    
    @abstractmethod
    async def create_actuator_data(self, data: "ActuatorBuzzerDataCreate") -> "ActuatorBuzzerDataResponse":
        """Buzzer 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_actuator_data(self, device_id: str, timestamp: datetime) -> Optional["ActuatorBuzzerDataResponse"]:
        """Buzzer 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest_actuator_data(self, device_id: str) -> Optional["ActuatorBuzzerDataResponse"]:
        """최신 Buzzer 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_actuator_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        buzzer_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List["ActuatorBuzzerDataResponse"]:
        """Buzzer 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update_actuator_data(
        self, 
        device_id: str, 
        timestamp: datetime, 
        data: "ActuatorBuzzerDataUpdate"
    ) -> Optional["ActuatorBuzzerDataResponse"]:
        """Buzzer 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete_actuator_data(self, device_id: str, timestamp: datetime) -> bool:
        """Buzzer 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_actuator_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Buzzer 액추에이터 로그 통계 조회"""
        pass


class IActuatorIRTXService(ABC):
    """IR TX 액추에이터 로그 서비스 인터페이스"""
    
    @abstractmethod
    async def create_actuator_data(self, data: "ActuatorIRTXDataCreate") -> "ActuatorIRTXDataResponse":
        """IR TX 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_actuator_data(self, device_id: str, timestamp: datetime) -> Optional["ActuatorIRTXDataResponse"]:
        """IR TX 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest_actuator_data(self, device_id: str) -> Optional["ActuatorIRTXDataResponse"]:
        """최신 IR TX 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_actuator_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        protocol: Optional[str] = None,
        command_hex: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List["ActuatorIRTXDataResponse"]:
        """IR TX 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update_actuator_data(
        self, 
        device_id: str, 
        timestamp: datetime, 
        data: "ActuatorIRTXDataUpdate"
    ) -> Optional["ActuatorIRTXDataResponse"]:
        """IR TX 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete_actuator_data(self, device_id: str, timestamp: datetime) -> bool:
        """IR TX 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_actuator_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """IR TX 액추에이터 로그 통계 조회"""
        pass


class IActuatorRelayService(ABC):
    """Relay 액추에이터 로그 서비스 인터페이스"""
    
    @abstractmethod
    async def create_actuator_data(self, data: "ActuatorRelayDataCreate") -> "ActuatorRelayDataResponse":
        """Relay 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_actuator_data(self, device_id: str, timestamp: datetime) -> Optional["ActuatorRelayDataResponse"]:
        """Relay 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest_actuator_data(self, device_id: str) -> Optional["ActuatorRelayDataResponse"]:
        """최신 Relay 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_actuator_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List["ActuatorRelayDataResponse"]:
        """Relay 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update_actuator_data(
        self, 
        device_id: str, 
        timestamp: datetime, 
        data: "ActuatorRelayDataUpdate"
    ) -> Optional["ActuatorRelayDataResponse"]:
        """Relay 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete_actuator_data(self, device_id: str, timestamp: datetime) -> bool:
        """Relay 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_actuator_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Relay 액추에이터 로그 통계 조회"""
        pass


class IActuatorServoService(ABC):
    """Servo 액추에이터 로그 서비스 인터페이스"""
    
    @abstractmethod
    async def create_actuator_data(self, data: "ActuatorServoDataCreate") -> "ActuatorServoDataResponse":
        """Servo 액추에이터 로그 생성"""
        pass
    
    @abstractmethod
    async def get_actuator_data(self, device_id: str, timestamp: datetime) -> Optional["ActuatorServoDataResponse"]:
        """Servo 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_latest_actuator_data(self, device_id: str) -> Optional["ActuatorServoDataResponse"]:
        """최신 Servo 액추에이터 로그 조회"""
        pass
    
    @abstractmethod
    async def get_actuator_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[int] = None,
        angle_deg: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List["ActuatorServoDataResponse"]:
        """Servo 액추에이터 로그 목록 조회"""
        pass
    
    @abstractmethod
    async def update_actuator_data(
        self, 
        device_id: str, 
        timestamp: datetime, 
        data: "ActuatorServoDataUpdate"
    ) -> Optional["ActuatorServoDataResponse"]:
        """Servo 액추에이터 로그 수정"""
        pass
    
    @abstractmethod
    async def delete_actuator_data(self, device_id: str, timestamp: datetime) -> bool:
        """Servo 액추에이터 로그 삭제"""
        pass
    
    @abstractmethod
    async def get_actuator_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Servo 액추에이터 로그 통계 조회"""
        pass
