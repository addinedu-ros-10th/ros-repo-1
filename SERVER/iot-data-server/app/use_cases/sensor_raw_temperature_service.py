from typing import List, Optional
from datetime import datetime
from app.interfaces.services.sensor_raw_temperature_service_interface import ISensorRawTemperatureService
from app.interfaces.repositories.sensor_raw_temperature_repository import ISensorRawTemperatureRepository
from app.domain.entities.sensor_raw_temperature import SensorRawTemperature
from app.api.v1.schemas import (
    SensorRawTemperatureCreate, SensorRawTemperatureUpdate,
    SensorRawTemperatureResponse, SensorRawTemperatureListResponse
)


class SensorRawTemperatureService(ISensorRawTemperatureService):
    """온도 센서 원시 데이터 서비스 구현체"""
    
    def __init__(self, temperature_repository: ISensorRawTemperatureRepository):
        self.temperature_repository = temperature_repository
    
    async def create_temperature_data(self, temperature_data: SensorRawTemperatureCreate) -> SensorRawTemperatureResponse:
        """온도 센서 데이터 생성"""
        # Pydantic 스키마를 도메인 엔티티로 변환
        temperature_entity = SensorRawTemperature(
            time=temperature_data.time,
            device_id=temperature_data.device_id,
            temperature_celsius=temperature_data.temperature_celsius,
            humidity_percent=temperature_data.humidity_percent,
            raw_payload=temperature_data.raw_payload
        )
        
        # 리포지토리를 통해 저장
        created_temperature = await self.temperature_repository.create_temperature_data(temperature_entity)
        
        # 도메인 엔티티를 Pydantic 응답 스키마로 변환
        return SensorRawTemperatureResponse.from_orm(created_temperature)
    
    async def get_temperature_data_by_time_and_device(
        self, time: datetime, device_id: str
    ) -> Optional[SensorRawTemperatureResponse]:
        """특정 시간과 디바이스의 온도 데이터 조회"""
        temperature = await self.temperature_repository.get_temperature_data_by_time_and_device(time, device_id)
        if temperature:
            return SensorRawTemperatureResponse.from_orm(temperature)
        return None
    
    async def get_latest_temperature_data_by_device(self, device_id: str) -> Optional[SensorRawTemperatureResponse]:
        """디바이스의 최신 온도 데이터 조회"""
        temperature = await self.temperature_repository.get_latest_temperature_data_by_device(device_id)
        if temperature:
            return SensorRawTemperatureResponse.from_orm(temperature)
        return None
    
    async def get_temperature_data_by_device(
        self, device_id: str, limit: int = 100
    ) -> List[SensorRawTemperatureResponse]:
        """디바이스의 온도 데이터 목록 조회"""
        temperatures = await self.temperature_repository.get_temperature_data_by_device(device_id, limit)
        return [SensorRawTemperatureResponse.from_orm(temp) for temp in temperatures]
    
    async def get_temperature_data_by_time_range(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> List[SensorRawTemperatureResponse]:
        """특정 시간 범위의 온도 데이터 조회"""
        temperatures = await self.temperature_repository.get_temperature_data_by_time_range(device_id, start_time, end_time)
        return [SensorRawTemperatureResponse.from_orm(temp) for temp in temperatures]
    
    async def get_temperature_data_by_temperature_range(
        self, device_id: str, min_temp: float, max_temp: float
    ) -> List[SensorRawTemperatureResponse]:
        """특정 온도 범위의 데이터 조회"""
        temperatures = await self.temperature_repository.get_temperature_data_by_temperature_range(device_id, min_temp, max_temp)
        return [SensorRawTemperatureResponse.from_orm(temp) for temp in temperatures]
    
    async def get_extreme_temperature_data(
        self, device_id: str, limit: int = 100
    ) -> List[SensorRawTemperatureResponse]:
        """극한 온도 데이터 조회 (0°C 이하 또는 50°C 이상)"""
        temperatures = await self.temperature_repository.get_extreme_temperature_data(device_id, limit)
        return [SensorRawTemperatureResponse.from_orm(temp) for temp in temperatures]
    
    async def update_temperature_data(
        self, time: datetime, device_id: str, temperature_data: SensorRawTemperatureUpdate
    ) -> Optional[SensorRawTemperatureResponse]:
        """온도 데이터 업데이트"""
        # None이 아닌 필드만 추출
        update_data = {k: v for k, v in temperature_data.dict().items() if v is not None}
        
        if not update_data:
            return None
        
        updated_temperature = await self.temperature_repository.update_temperature_data(time, device_id, update_data)
        if updated_temperature:
            return SensorRawTemperatureResponse.from_orm(updated_temperature)
        return None
    
    async def delete_temperature_data(self, time: datetime, device_id: str) -> bool:
        """온도 데이터 삭제"""
        return await self.temperature_repository.delete_temperature_data(time, device_id)
    
    async def get_all_temperature_data(
        self, skip: int = 0, limit: int = 100
    ) -> SensorRawTemperatureListResponse:
        """전체 온도 데이터 목록 조회 (페이지네이션)"""
        temperatures = await self.temperature_repository.get_all_temperature_data(skip, limit)
        total = len(temperatures)  # 실제로는 전체 개수를 별도로 조회해야 함
        
        return SensorRawTemperatureListResponse(
            items=[SensorRawTemperatureResponse.from_orm(temp) for temp in temperatures],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 1
        )
    
    async def get_average_temperature_by_device(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> Optional[float]:
        """디바이스의 평균 온도 조회"""
        return await self.temperature_repository.get_average_temperature_by_device(device_id, start_time, end_time)
    
    async def get_temperature_statistics_by_device(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> dict:
        """디바이스의 온도 통계 정보 조회 (최소, 최대, 평균)"""
        return await self.temperature_repository.get_temperature_statistics_by_device(device_id, start_time, end_time)
