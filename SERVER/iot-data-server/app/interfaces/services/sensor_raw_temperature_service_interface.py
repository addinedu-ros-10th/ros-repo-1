from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.api.v1.schemas import (
    SensorRawTemperatureCreate, SensorRawTemperatureUpdate,
    SensorRawTemperatureResponse, SensorRawTemperatureListResponse
)


class ISensorRawTemperatureService(ABC):
    """온도 센서 원시 데이터 서비스 인터페이스"""
    
    @abstractmethod
    async def create_temperature_data(self, temperature_data: SensorRawTemperatureCreate) -> SensorRawTemperatureResponse:
        """온도 센서 데이터 생성"""
        pass
    
    @abstractmethod
    async def get_temperature_data_by_time_and_device(
        self, time: datetime, device_id: str
    ) -> Optional[SensorRawTemperatureResponse]:
        """특정 시간과 디바이스의 온도 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_latest_temperature_data_by_device(self, device_id: str) -> Optional[SensorRawTemperatureResponse]:
        """디바이스의 최신 온도 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_temperature_data_by_device(
        self, device_id: str, limit: int = 100
    ) -> List[SensorRawTemperatureResponse]:
        """디바이스의 온도 데이터 목록 조회"""
        pass
    
    @abstractmethod
    async def get_temperature_data_by_time_range(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> List[SensorRawTemperatureResponse]:
        """특정 시간 범위의 온도 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_temperature_data_by_temperature_range(
        self, device_id: str, min_temp: float, max_temp: float
    ) -> List[SensorRawTemperatureResponse]:
        """특정 온도 범위의 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_extreme_temperature_data(
        self, device_id: str, limit: int = 100
    ) -> List[SensorRawTemperatureResponse]:
        """극한 온도 데이터 조회 (0°C 이하 또는 50°C 이상)"""
        pass
    
    @abstractmethod
    async def update_temperature_data(
        self, time: datetime, device_id: str, temperature_data: SensorRawTemperatureUpdate
    ) -> Optional[SensorRawTemperatureResponse]:
        """온도 데이터 업데이트"""
        pass
    
    @abstractmethod
    async def delete_temperature_data(self, time: datetime, device_id: str) -> bool:
        """온도 데이터 삭제"""
        pass
    
    @abstractmethod
    async def get_all_temperature_data(
        self, skip: int = 0, limit: int = 100
    ) -> SensorRawTemperatureListResponse:
        """전체 온도 데이터 목록 조회 (페이지네이션)"""
        pass
    
    @abstractmethod
    async def get_average_temperature_by_device(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> Optional[float]:
        """디바이스의 평균 온도 조회"""
        pass
    
    @abstractmethod
    async def get_temperature_statistics_by_device(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> dict:
        """디바이스의 온도 통계 정보 조회 (최소, 최대, 평균)"""
        pass
