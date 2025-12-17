"""
MQ5 가스 센서 데이터 리포지토리 구현체

Clean Architecture 원칙에 따라 MQ5 가스 센서 데이터에 대한 데이터 접근을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.interfaces.repositories.sensor_repository import IMQ5Repository
from app.infrastructure.models import SensorRawMQ5
from app.api.v1.schemas import (
    SensorRawMQ5Create,
    SensorRawMQ5Update,
    SensorRawMQ5Response
)


class MQ5Repository(IMQ5Repository):
    """MQ5 가스 센서 데이터 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: SensorRawMQ5Create) -> SensorRawMQ5Response:
        """MQ5 가스 센서 데이터 생성"""
        # 실제 DB 테이블 구조에 맞게 매핑 (time, device_id, raw_payload만 사용)
        orm_data = {
            "time": data.time,
            "device_id": data.device_id,
            "raw_payload": data.raw_payload
        }
        
        db_data = SensorRawMQ5(**orm_data)
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return SensorRawMQ5Response.from_orm(data)
    
    async def get_by_id(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawMQ5Response]:
        """특정 시간의 MQ5 가스 센서 데이터 조회"""
        query = select(SensorRawMQ5).where(
            and_(
                SensorRawMQ5.device_id == device_id,
                SensorRawMQ5.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        data = result.scalar_one_or_none()
        
        if data:
            return SensorRawMQ5Response.from_attributes(data)
        return None
    
    async def get_latest(self, device_id: str) -> Optional[SensorRawMQ5Response]:
        """최신 MQ5 가스 센서 데이터 조회"""
        query = (
            select(SensorRawMQ5)
            .where(SensorRawMQ5.device_id == device_id)
            .order_by(SensorRawMQ5.time.desc())
        )
        
        result = self.db.execute(query)
        data = result.scalars().first()
        
        if data:
            return SensorRawMQ5Response.from_attributes(data)
        return None
    
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit_count: int = 100
    ) -> List[SensorRawMQ5Response]:
        print("repository get_list 호출")
        try:
            query = select(SensorRawMQ5)
            
            # 필터 조건 추가
            if device_id:
                query = query.where(SensorRawMQ5.device_id == device_id)
            if start_time:
                query = query.where(SensorRawMQ5.time >= start_time)
            if end_time:
                query = query.where(SensorRawMQ5.time <= end_time)
            
            # 시간 역순으로 정렬하고 제한
            query = query.order_by(SensorRawMQ5.time.desc()).limit(limit_count)
            
            result = self.db.execute(query)
            # SQLAlchemy 모델 객체들의 리스트를 가져옴
            data_list = result.scalars().all()

            print("repository get_list 조회 값")
            print(data_list)
            
            # SQLAlchemy 모델을 Pydantic 모델로 변환
            # return [SensorRawMQ5Response.from_attributes(data) for data in data_list]
            return [SensorRawMQ5Response.from_orm(data) for data in data_list]
            # return data_list
            
        except Exception as e:
            # 오류 발생 시 로깅 후 빈 리스트 반환
            print(f"get_list 오류: {e}")
            return []
    
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawMQ5Update
    ) -> Optional[SensorRawMQ5Response]:
        """MQ5 가스 센서 데이터 수정"""
        query = select(SensorRawMQ5).where(
            and_(
                SensorRawMQ5.device_id == device_id,
                SensorRawMQ5.time == timestamp
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
        return SensorRawMQ5Response.from_attributes(db_data)
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """MQ5 가스 센서 데이터 삭제"""
        query = select(SensorRawMQ5).where(
            and_(
                SensorRawMQ5.device_id == device_id,
                SensorRawMQ5.time == timestamp
            )
        )
        
        result = await self.db.execute(query)
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
        """MQ5 가스 센서 데이터 기본 통계 조회"""
        return await self.get_gas_statistics(device_id, start_time, end_time)
    
    async def get_gas_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """MQ5 가스 센서의 가스 농도 통계 정보 조회"""
        query = select(SensorRawMQ5).where(SensorRawMQ5.device_id == device_id)
        
        if start_time:
            query = query.where(SensorRawMQ5.time >= start_time)
        if end_time:
            query = query.where(SensorRawMQ5.time <= end_time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "total_records": 0,
                "gas_stats": None,
                "gas_type_distribution": None
            }
        
        # Raw 센서 데이터는 raw_payload만 가지고 있음
        stats = {
            "device_id": device_id,
            "total_records": len(data_list),
            "raw_data_stats": {
                "total_records": len(data_list),
                "has_raw_payload": len([d for d in data_list if d.raw_payload])
            }
        }
        
        return stats
    
    async def get_high_concentration_alerts(
        self,
        device_id: str,
        threshold_ppm: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """MQ5 가스 센서의 높은 농도 알림 조회"""
        # Raw 센서 모델은 ppm_value 필드가 없으므로 빈 결과 반환
        query = select(SensorRawMQ5).where(
            and_(
                SensorRawMQ5.device_id == device_id,
                SensorRawMQ5.device_id == "nonexistent"  # 항상 false가 되도록
            )
        )
        
        if start_time:
            query = query.where(SensorRawMQ5.time >= start_time)
        if end_time:
            query = query.where(SensorRawMQ5.time <= end_time)
        
        result = await self.db.execute(query)
        alert_data = result.scalars().all()
        
        # Raw 센서 데이터는 ppm_value, analog_value, gas_type 필드가 없음
        return {
            "device_id": device_id,
            "threshold_ppm": threshold_ppm,
            "total_alerts": 0,
            "alerts": [],
            "alert_summary": {
                "high_level": 0,
                "medium_level": 0
            },
            "note": "Raw 센서 모델은 ppm_value, analog_value, gas_type 필드를 지원하지 않습니다."
        }
