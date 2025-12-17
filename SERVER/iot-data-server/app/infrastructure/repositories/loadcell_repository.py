"""
LoadCell 센서 데이터 리포지토리 구현체

Clean Architecture 원칙에 따라 LoadCell 센서 데이터에 대한 데이터 접근을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.interfaces.repositories.sensor_repository import ILoadCellRepository
from app.infrastructure.models import SensorRawLoadCell
from app.api.v1.schemas import (
    SensorRawLoadCellCreate,
    SensorRawLoadCellUpdate,
    SensorRawLoadCellResponse
)


class LoadCellRepository(ILoadCellRepository):
    """LoadCell 센서 데이터 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: SensorRawLoadCellCreate) -> SensorRawLoadCellResponse:
        """로드셀 센서 데이터 생성"""
        # 실제 DB 테이블 구조에 맞게 매핑 (time, device_id, raw_payload만 사용)
        orm_data = {
            "time": data.time,
            "device_id": data.device_id,
            "raw_payload": data.raw_payload
        }

        print(orm_data)
        
        db_data = SensorRawLoadCell(**orm_data)
        self.db.add(db_data)
        await self.db.commit()
        await self.db.refresh(db_data)
        return SensorRawLoadCellResponse.from_orm(db_data)
    
    async def get_by_id(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawLoadCellResponse]:
        """특정 시간의 로드셀 센서 데이터 조회"""
        query = select(SensorRawLoadCell).where(
            and_(
                SensorRawLoadCell.device_id == device_id,
                SensorRawLoadCell.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        data = result.scalar_one_or_none()
        
        if data:
            return SensorRawLoadCellResponse.from_orm(data)
        return None
    
    async def get_latest(self, device_id: str) -> Optional[SensorRawLoadCellResponse]:
        """최신 로드셀 센서 데이터 조회"""
        query = (
            select(SensorRawLoadCell)
            .where(SensorRawLoadCell.device_id == device_id)
            .order_by(SensorRawLoadCell.time.desc())
        )
        
        result = self.db.execute(query)
        data = result.scalars().first()
        
        if data:
            return SensorRawLoadCellResponse.from_orm(data)
        return None
    
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit_count: int = 100
    ) -> List[SensorRawLoadCellResponse]:
        """로드셀 센서 데이터 목록 조회"""
        print(f"device_id: {device_id}, start_time: {start_time}, end_time: {end_time}, limit_count: {limit_count}")
        query = select(SensorRawLoadCell)
        
        # 필터 조건 추가
        if device_id:
            query = query.where(SensorRawLoadCell.device_id == device_id)
        if start_time:
            query = query.where(SensorRawLoadCell.time >= start_time)
        if end_time:
            query = query.where(SensorRawLoadCell.time <= end_time)
        
        # 시간 역순으로 정렬하고 제한
        query = query.order_by(SensorRawLoadCell.time.desc()).limit(limit_count)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        # 결과를 리스트로 변환하여 반환
        return [SensorRawLoadCellResponse.from_orm(data) for data in data_list]
    
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawLoadCellUpdate
    ) -> Optional[SensorRawLoadCellResponse]:
        """로드셀 센서 데이터 수정"""
        query = select(SensorRawLoadCell).where(
            and_(
                SensorRawLoadCell.device_id == device_id,
                SensorRawLoadCell.time == timestamp
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
        return SensorRawLoadCellResponse.from_orm(db_data)
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """로드셀 센서 데이터 삭제"""
        query = select(SensorRawLoadCell).where(
            and_(
                SensorRawLoadCell.device_id == device_id,
                SensorRawLoadCell.time == timestamp
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
        """로드셀 센서 데이터 기본 통계 조회"""
        return await self.get_weight_statistics(device_id, start_time, end_time)
    
    async def get_weight_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """로드셀 센서의 무게 통계 정보 조회"""
        query = select(SensorRawLoadCell).where(SensorRawLoadCell.device_id == device_id)
        
        if start_time:
            query = query.where(SensorRawLoadCell.time >= start_time)
        if end_time:
            query = query.where(SensorRawLoadCell.time <= end_time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "total_records": 0,
                "weight_stats": None,
                "calibration_status": None
            }
        
        # 무게 데이터가 있는 레코드만 필터링
        weight_data = [d.weight_kg for d in data_list if d.weight_kg is not None]
        calibrated_count = sum(1 for d in data_list if d.calibrated)
        
        stats = {
            "device_id": device_id,
            "total_records": len(data_list),
            "weight_stats": {
                "count": len(weight_data),
                "min": min(weight_data) if weight_data else None,
                "max": max(weight_data) if weight_data else None,
                "avg": sum(weight_data) / len(weight_data) if weight_data else None
            },
            "calibration_status": {
                "calibrated_count": calibrated_count,
                "total_count": len(data_list),
                "calibration_rate": calibrated_count / len(data_list) if data_list else 0
            }
        }
        
        return stats
