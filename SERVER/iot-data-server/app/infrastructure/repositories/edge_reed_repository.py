"""
Edge Reed 센서 데이터 리포지토리 구현체

Reed 스위치 센서의 Edge 처리된 데이터를 관리합니다.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import SensorEdgeReed
from app.interfaces.repositories.sensor_repository import IEdgeReedRepository
from app.api.v1.schemas import EdgeReedDataCreate, EdgeReedDataUpdate, EdgeReedDataResponse


class EdgeReedRepository(IEdgeReedRepository):
    """Edge Reed 센서 데이터 리포지토리 구현체"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, data: EdgeReedDataCreate) -> EdgeReedDataResponse:
        """Edge Reed 센서 데이터 생성"""
        db_data = SensorEdgeReed(
            device_id=data.device_id,
            time=data.time,
            switch_state=data.switch_state,
            confidence=data.confidence,
            magnetic_strength=data.magnetic_strength,
            processing_time=data.processing_time
        )
        
        self.db_session.add(db_data)
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgeReedDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            switch_state=db_data.switch_state,
            confidence=db_data.confidence,
            magnetic_strength=db_data.magnetic_strength,
            processing_time=db_data.processing_time
        )

    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[EdgeReedDataResponse]:
        """특정 시간의 Edge Reed 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgeReed).where(
                and_(
                    SensorEdgeReed.device_id == device_id,
                    SensorEdgeReed.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgeReedDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            switch_state=db_data.switch_state,
            confidence=db_data.confidence,
            magnetic_strength=db_data.magnetic_strength,
            processing_time=db_data.processing_time
        )

    async def get_latest(self, device_id: str) -> Optional[EdgeReedDataResponse]:
        """최신 Edge Reed 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgeReed).where(
                SensorEdgeReed.device_id == device_id
            ).order_by(SensorEdgeReed.time.desc()).limit(1)
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgeReedDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            switch_state=db_data.switch_state,
            confidence=db_data.confidence,
            magnetic_strength=db_data.magnetic_strength,
            processing_time=db_data.processing_time
        )

    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EdgeReedDataResponse]:
        """Edge Reed 센서 데이터 목록 조회"""
        query = select(SensorEdgeReed)
        
        if device_id:
            query = query.where(SensorEdgeReed.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgeReed.time >= start_time)
        
        if end_time:
            query = query.where(SensorEdgeReed.time <= end_time)
        
        query = query.order_by(SensorEdgeReed.time.desc()).limit(limit)
        
        result = await self.db_session.execute(query)
        db_data_list = result.scalars().all()
        
        return [
            EdgeReedDataResponse(
                device_id=db_data.device_id,
                time=db_data.time,
                switch_state=db_data.switch_state,
                confidence=db_data.confidence,
                magnetic_strength=db_data.magnetic_strength,
                processing_time=db_data.processing_time
            )
            for db_data in db_data_list
        ]

    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: EdgeReedDataUpdate
    ) -> Optional[EdgeReedDataResponse]:
        """Edge Reed 센서 데이터 수정"""
        result = await self.db_session.execute(
            select(SensorEdgeReed).where(
                and_(
                    SensorEdgeReed.device_id == device_id,
                    SensorEdgeReed.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
        
        # 업데이트할 필드만 수정
        if data.switch_state is not None:
            db_data.switch_state = data.switch_state
        if data.confidence is not None:
            db_data.confidence = data.confidence
        if data.magnetic_strength is not None:
            db_data.magnetic_strength = data.magnetic_strength
        if data.processing_time is not None:
            db_data.processing_time = data.processing_time
        
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgeReedDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            switch_state=db_data.switch_state,
            confidence=db_data.confidence,
            magnetic_strength=db_data.magnetic_strength,
            processing_time=db_data.processing_time
        )

    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Edge Reed 센서 데이터 삭제"""
        result = await self.db_session.execute(
            select(SensorEdgeReed).where(
                and_(
                    SensorEdgeReed.device_id == device_id,
                    SensorEdgeReed.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return False
        
        await self.db_session.delete(db_data)
        await self.db_session.commit()
        
        return True

    async def get_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """Edge Reed 센서 데이터 통계 조회"""
        query = select(SensorEdgeReed).where(SensorEdgeReed.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgeReed.time >= start_time)
        if end_time:
            query = query.where(SensorEdgeReed.time <= end_time)
        
        result = await self.db_session.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "total_records": 0,
                "switch_activations": 0,
                "activation_rate": 0.0,
                "avg_confidence": 0.0,
                "magnetic_strength_stats": {},
                "processing_time_stats": {}
            }
        
        total_records = len(data_list)
        switch_activations = sum(1 for data in data_list if data.switch_state)
        activation_rate = (switch_activations / total_records) * 100 if total_records > 0 else 0
        
        confidence_values = [data.confidence for data in data_list if data.confidence is not None]
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
        
        # 자기장 강도 통계
        magnetic_values = [data.magnetic_strength for data in data_list if data.magnetic_strength is not None]
        magnetic_stats = {}
        if magnetic_values:
            magnetic_stats = {
                "min": min(magnetic_values),
                "max": max(magnetic_values),
                "avg": sum(magnetic_values) / len(magnetic_values)
            }
        
        # 처리 시간 통계
        processing_times = [data.processing_time for data in data_list if data.processing_time is not None]
        processing_time_stats = {}
        if processing_times:
            processing_time_stats = {
                "min": min(processing_times),
                "max": max(processing_times),
                "avg": sum(processing_times) / len(processing_times)
            }
        
        return {
            "total_records": total_records,
            "switch_activations": switch_activations,
            "activation_rate": round(activation_rate, 2),
            "avg_confidence": round(avg_confidence, 2),
            "magnetic_strength_stats": magnetic_stats,
            "processing_time_stats": processing_time_stats
        }

    async def get_switch_activation_history(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """스위치 활성화 이력 조회"""
        query = select(SensorEdgeReed).where(
            and_(
                SensorEdgeReed.device_id == device_id,
                SensorEdgeReed.switch_state == True
            )
        )
        
        if start_time:
            query = query.where(SensorEdgeReed.time >= start_time)
        if end_time:
            query = query.where(SensorEdgeReed.time <= end_time)
        
        query = query.order_by(SensorEdgeReed.time.desc())
        
        result = await self.db_session.execute(query)
        activation_data_list = result.scalars().all()
        
        activations = []
        for data in activation_data_list:
            activations.append({
                "timestamp": data.time,
                "confidence": data.confidence,
                "magnetic_strength": data.magnetic_strength,
                "processing_time": data.processing_time
            })
        
        return {
            "total_activations": len(activations),
            "activations": activations
        }
