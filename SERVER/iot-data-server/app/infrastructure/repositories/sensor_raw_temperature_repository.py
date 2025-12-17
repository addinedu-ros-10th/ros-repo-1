from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.domain.entities.sensor_raw_temperature import SensorRawTemperature
from app.infrastructure.models import SensorRawTemperature as SensorRawTemperatureModel
from app.interfaces.repositories.sensor_raw_temperature_repository import ISensorRawTemperatureRepository


class SensorRawTemperatureRepository(ISensorRawTemperatureRepository):
    """온도 센서 원시 데이터 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_temperature_data(self, temperature_data: SensorRawTemperature) -> SensorRawTemperature:
        """온도 센서 데이터 생성"""
        db_temperature = SensorRawTemperatureModel(
            time=temperature_data.time,
            device_id=temperature_data.device_id,
            temperature_celsius=temperature_data.temperature_celsius,
            humidity_percent=temperature_data.humidity_percent,
            raw_payload=temperature_data.raw_payload
        )
        
        self.db.add(db_temperature)
        self.db.commit()
        self.db.refresh(db_temperature)
        
        return self._to_domain_entity(db_temperature)
    
    async def get_temperature_data_by_time_and_device(
        self, time: datetime, device_id: str
    ) -> Optional[SensorRawTemperature]:
        """특정 시간과 디바이스의 온도 데이터 조회"""
        result = self.db.execute(
            select(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.time == time,
                SensorRawTemperatureModel.device_id == device_id
            )
        )
        data = result.scalar_one_or_none()
        
        if data:
            return self._to_domain_entity(data)
        return None
    
    async def get_latest_temperature_data_by_device(self, device_id: str) -> Optional[SensorRawTemperature]:
        """디바이스의 최신 온도 데이터 조회"""
        result = self.db.execute(
            select(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.device_id == device_id
            ).order_by(SensorRawTemperatureModel.time.desc()).limit(1)
        )
        data = result.scalars().first()
        
        if data:
            return self._to_domain_entity(data)
        return None
    
    async def get_temperature_data_by_device(
        self, device_id: str, limit: int = 100
    ) -> List[SensorRawTemperature]:
        """디바이스의 온도 데이터 목록 조회"""
        result = self.db.execute(
            select(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.device_id == device_id
            ).order_by(SensorRawTemperatureModel.time.desc()).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_temperature_data_by_time_range(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> List[SensorRawTemperature]:
        """특정 시간 범위의 온도 데이터 조회"""
        result = self.db.execute(
            select(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.device_id == device_id,
                SensorRawTemperatureModel.time >= start_time,
                SensorRawTemperatureModel.time <= end_time
            ).order_by(SensorRawTemperatureModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_temperature_data_by_temperature_range(
        self, device_id: str, min_temp: float, max_temp: float
    ) -> List[SensorRawTemperature]:
        """특정 온도 범위의 데이터 조회"""
        result = self.db.execute(
            select(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.device_id == device_id,
                SensorRawTemperatureModel.temperature_celsius >= min_temp,
                SensorRawTemperatureModel.temperature_celsius <= max_temp
            ).order_by(SensorRawTemperatureModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_extreme_temperature_data(
        self, device_id: str, limit: int = 100
    ) -> List[SensorRawTemperature]:
        """극한 온도 데이터 조회 (0°C 이하 또는 50°C 이상)"""
        result = self.db.execute(
            select(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.device_id == device_id,
                (SensorRawTemperatureModel.temperature_celsius <= 0) | 
                (SensorRawTemperatureModel.temperature_celsius >= 50)
            ).order_by(SensorRawTemperatureModel.time.desc()).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def update_temperature_data(
        self, time: datetime, device_id: str, temperature_data: dict
    ) -> Optional[SensorRawTemperature]:
        """온도 데이터 업데이트"""
        result = self.db.execute(
            update(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.time == time,
                SensorRawTemperatureModel.device_id == device_id
            ).values(**temperature_data)
        )
        
        if result.rowcount > 0:
            self.db.commit()
            return await self.get_temperature_data_by_time_and_device(time, device_id)
        return None
    
    async def delete_temperature_data(self, time: datetime, device_id: str) -> bool:
        """온도 데이터 삭제"""
        result = self.db.execute(
            delete(SensorRawTemperatureModel).where(
                SensorRawTemperatureModel.time == time,
                SensorRawTemperatureModel.device_id == device_id
            )
        )
        
        if result.rowcount > 0:
            self.db.commit()
            return True
        return False
    
    async def get_all_temperature_data(
        self, skip: int = 0, limit: int = 100
    ) -> List[SensorRawTemperature]:
        """전체 온도 데이터 목록 조회 (페이지네이션)"""
        result = self.db.execute(
            select(SensorRawTemperatureModel).order_by(
                SensorRawTemperatureModel.time.desc()
            ).offset(skip).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def count_temperature_data_by_device(self, device_id: str) -> int:
        """디바이스의 온도 데이터 개수 조회"""
        result = self.db.execute(
            select(func.count(SensorRawTemperatureModel.time)).where(
                SensorRawTemperatureModel.device_id == device_id
            )
        )
        return result.scalar()
    
    async def get_average_temperature_by_device(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> Optional[float]:
        """디바이스의 평균 온도 조회"""
        result = self.db.execute(
            select(func.avg(SensorRawTemperatureModel.temperature_celsius)).where(
                SensorRawTemperatureModel.device_id == device_id,
                SensorRawTemperatureModel.time >= start_time,
                SensorRawTemperatureModel.time <= end_time
            )
        )
        return result.scalar()
    
    async def get_temperature_statistics_by_device(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> dict:
        """디바이스의 온도 통계 정보 조회 (최소, 최대, 평균)"""
        result = self.db.execute(
            select(
                func.min(SensorRawTemperatureModel.temperature_celsius).label('min_temp'),
                func.max(SensorRawTemperatureModel.temperature_celsius).label('max_temp'),
                func.avg(SensorRawTemperatureModel.temperature_celsius).label('avg_temp'),
                func.count(SensorRawTemperatureModel.time).label('count')
            ).where(
                SensorRawTemperatureModel.device_id == device_id,
                SensorRawTemperatureModel.time >= start_time,
                SensorRawTemperatureModel.time <= end_time
            )
        )
        stats = result.fetchone()
        
        if stats:
            return {
                'min_temperature': float(stats.min_temp) if stats.min_temp else None,
                'max_temperature': float(stats.max_temp) if stats.max_temp else None,
                'avg_temperature': float(stats.avg_temp) if stats.avg_temp else None,
                'data_count': stats.count
            }
        return {}
    
    def _to_domain_entity(self, db_model: SensorRawTemperatureModel) -> SensorRawTemperature:
        """ORM 모델을 도메인 엔티티로 변환"""
        return SensorRawTemperature(
            time=db_model.time,
            device_id=db_model.device_id,
            temperature_celsius=float(db_model.temperature_celsius),
            humidity_percent=float(db_model.humidity_percent) if db_model.humidity_percent else None,
            raw_payload=db_model.raw_payload
        )
