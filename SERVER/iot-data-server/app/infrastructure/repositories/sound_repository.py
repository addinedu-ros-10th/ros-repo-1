"""
Sound 센서 데이터 리포지토리 구현체

Clean Architecture 원칙에 따라 Sound 센서 데이터에 대한 데이터 접근을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.interfaces.repositories.sensor_repository import ISoundRepository
from app.infrastructure.models import SensorRawSound
from app.api.v1.schemas import (
    SensorRawSoundCreate,
    SensorRawSoundUpdate,
    SensorRawSoundResponse
)


class SoundRepository(ISoundRepository):
    """Sound 센서 데이터 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: SensorRawSoundCreate) -> SensorRawSoundResponse:
        """Sound 센서 데이터 생성"""
        # 실제 DB 테이블 구조에 맞게 매핑 (time, device_id, raw_payload만 사용)
        orm_data = {
            "time": data.time,
            "device_id": data.device_id,
            "raw_payload": data.raw_payload
        }
        
        db_data = SensorRawSound(**orm_data)
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return SensorRawSoundResponse.from_orm(db_data)
    
    async def get_by_id(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawSoundResponse]:
        """특정 시간의 Sound 센서 데이터 조회"""
        query = select(SensorRawSound).where(
            and_(
                SensorRawSound.device_id == device_id,
                SensorRawSound.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        data = result.scalar_one_or_none()
        
        if data:
            return SensorRawSoundResponse.from_orm(data)
        return None
    
    async def get_latest(self, device_id: str) -> Optional[SensorRawSoundResponse]:
        """최신 Sound 센서 데이터 조회"""
        query = (
            select(SensorRawSound)
            .where(SensorRawSound.device_id == device_id)
            .order_by(SensorRawSound.time.desc())
        )
        
        result = self.db.execute(query)
        data = result.scalars().first()
        
        if data:
            return SensorRawSoundResponse.from_orm(data)
        return None
    
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit_count: int = 100
    ) -> List[SensorRawSoundResponse]:
        """Sound 센서 데이터 목록 조회"""
        query = select(SensorRawSound)
        
        # 필터 조건 추가
        if device_id:
            query = query.where(SensorRawSound.device_id == device_id)
        if start_time:
            query = query.where(SensorRawSound.time >= start_time)
        if end_time:
            query = query.where(SensorRawSound.time <= end_time)
        
        # 시간 역순으로 정렬하고 제한
        query = query.order_by(SensorRawSound.time.desc()).limit(limit_count)
        
        result = self.db.execute(query)
        data_list = result.scalars().all()
        
        # 결과를 리스트로 변환하여 반환
        return [SensorRawSoundResponse.from_orm(data) for data in data_list]
    
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawSoundUpdate
    ) -> Optional[SensorRawSoundResponse]:
        """Sound 센서 데이터 수정"""
        query = select(SensorRawSound).where(
            and_(
                SensorRawSound.device_id == device_id,
                SensorRawSound.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        db_data = result.scalar_one_or_none()
        
        if not db_data:
            return None
        
        # 업데이트할 필드만 수정
        update_data = data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_data, field, value)
        
        await self.db.commit()
        await self.db.refresh(db_data)
        return SensorRawSoundResponse.from_orm(db_data)
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Sound 센서 데이터 삭제"""
        query = select(SensorRawSound).where(
            and_(
                SensorRawSound.device_id == device_id,
                SensorRawSound.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        db_data = result.scalar_one_or_none()
        
        if not db_data:
            return False
        
        await self.db.delete(db_data)
        await self.db.commit()
        return True
    
    async def get_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """Sound 센서 데이터 기본 통계 조회"""
        return await self.get_audio_statistics(device_id, start_time, end_time)
    
    async def get_audio_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """오디오 통계 정보 조회"""
        query = select(SensorRawSound).where(SensorRawSound.device_id == device_id)
        
        if start_time:
            query = query.where(SensorRawSound.time >= start_time)
        if end_time:
            query = query.where(SensorRawSound.time <= end_time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "total_records": 0,
                "avg_db": 0,
                "max_db": 0,
                "min_db": 0,
                "noise_level": "quiet"
            }
        
        # 통계 계산
        db_values = [data.db_value for data in data_list if data.db_value is not None]
        analog_values = [data.analog_value for data in data_list if data.analog_value is not None]
        
        if not db_values:
            return {
                "device_id": device_id,
                "total_records": len(data_list),
                "avg_db": 0,
                "max_db": 0,
                "min_db": 0,
                "noise_level": "unknown"
            }
        
        avg_db = sum(db_values) / len(db_values)
        max_db = max(db_values)
        min_db = min(db_values)
        
        # 소음 수준 분류
        if avg_db < 30:
            noise_level = "very_quiet"
        elif avg_db < 50:
            noise_level = "quiet"
        elif avg_db < 70:
            noise_level = "moderate"
        elif avg_db < 90:
            noise_level = "loud"
        else:
            noise_level = "very_loud"
        
        return {
            "device_id": device_id,
            "total_records": len(data_list),
            "avg_db": round(avg_db, 2),
            "max_db": round(max_db, 2),
            "min_db": round(min_db, 2),
            "noise_level": noise_level,
            "db_samples": len(db_values),
            "analog_samples": len(analog_values)
        }
    
    async def get_noise_alerts(
        self,
        device_id: str,
        threshold_db: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """소음 알림 조회"""
        query = select(SensorRawSound).where(
            and_(
                SensorRawSound.device_id == device_id,
                SensorRawSound.db_value > threshold_db
            )
        )
        
        if start_time:
            query = query.where(SensorRawSound.time >= start_time)
        if end_time:
            query = query.where(SensorRawSound.time <= end_time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        return {
            "device_id": device_id,
            "threshold_db": threshold_db,
            "alert_count": len(data_list),
            "alerts": [
                {
                    "time": data.time.isoformat(),
                    "db_value": data.db_value,
                    "analog_value": data.analog_value,
                    "exceeded_by": round(data.db_value - threshold_db, 2)
                }
                for data in data_list
            ]
        } 