"""
Edge Flame 센서 데이터 리포지토리 구현체

화재 감지 센서의 Edge 처리된 데이터를 관리합니다.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.models import SensorEdgeFlame
from app.interfaces.repositories.sensor_repository import IEdgeFlameRepository
from app.api.v1.schemas import EdgeFlameDataCreate, EdgeFlameDataUpdate, EdgeFlameDataResponse


class EdgeFlameRepository(IEdgeFlameRepository):
    """Edge Flame 센서 데이터 리포지토리 구현체"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, data: EdgeFlameDataCreate) -> EdgeFlameDataResponse:
        """Edge Flame 센서 데이터 생성"""
        db_data = SensorEdgeFlame(
            device_id=data.device_id,
            time=data.time,
            flame_detected=data.flame_detected,
            confidence=data.confidence,
            alert_level=data.alert_level,
            raw_payload=data.raw_payload
        )
        
        self.db_session.add(db_data)
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgeFlameDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            flame_detected=db_data.flame_detected,
            confidence=db_data.confidence,
            alert_level=db_data.alert_level,
            raw_payload=db_data.raw_payload
        )

    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[EdgeFlameDataResponse]:
        """특정 시간의 Edge Flame 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgeFlame).where(
                and_(
                    SensorEdgeFlame.device_id == device_id,
                    SensorEdgeFlame.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgeFlameDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            flame_detected=db_data.flame_detected,
            confidence=db_data.confidence,
            alert_level=db_data.alert_level,
            raw_payload=db_data.raw_payload
        )

    async def get_latest(self, device_id: str) -> Optional[EdgeFlameDataResponse]:
        """최신 Edge Flame 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgeFlame).where(
                SensorEdgeFlame.device_id == device_id
            ).order_by(SensorEdgeFlame.time.desc()).limit(1)
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgeFlameDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            flame_detected=db_data.flame_detected,
            confidence=db_data.confidence,
            alert_level=db_data.alert_level,
            raw_payload=db_data.raw_payload
        )

    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EdgeFlameDataResponse]:
        """Edge Flame 센서 데이터 목록 조회"""
        query = select(SensorEdgeFlame)
        
        if device_id:
            query = query.where(SensorEdgeFlame.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgeFlame.time >= start_time)
        
        if end_time:
            query = query.where(SensorEdgeFlame.time <= end_time)
        
        query = query.order_by(SensorEdgeFlame.time.desc()).limit(limit)
        
        result = await self.db_session.execute(query)
        db_data_list = result.scalars().all()
        
        return [
            EdgeFlameDataResponse(
                device_id=db_data.device_id,
                time=db_data.time,
                flame_detected=db_data.flame_detected,
                confidence=db_data.confidence,
                alert_level=db_data.alert_level,
                raw_payload=db_data.raw_payload
            )
            for db_data in db_data_list
        ]

    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: EdgeFlameDataUpdate
    ) -> Optional[EdgeFlameDataResponse]:
        """Edge Flame 센서 데이터 수정"""
        result = await self.db_session.execute(
            select(SensorEdgeFlame).where(
                and_(
                    SensorEdgeFlame.device_id == device_id,
                    SensorEdgeFlame.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
        
        # 업데이트할 필드만 수정
        if data.flame_detected is not None:
            db_data.flame_detected = data.flame_detected
        if data.confidence is not None:
            db_data.confidence = data.confidence
        if data.alert_level is not None:
            db_data.alert_level = data.alert_level
        if data.raw_payload is not None:
            db_data.raw_payload = data.raw_payload
        
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgeFlameDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            flame_detected=db_data.flame_detected,
            confidence=db_data.confidence,
            alert_level=db_data.alert_level,
            raw_payload=db_data.raw_payload
        )

    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Edge Flame 센서 데이터 삭제"""
        result = await self.db_session.execute(
            select(SensorEdgeFlame).where(
                and_(
                    SensorEdgeFlame.device_id == device_id,
                    SensorEdgeFlame.time == timestamp
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
        """Edge Flame 센서 데이터 통계 조회"""
        query = select(SensorEdgeFlame).where(SensorEdgeFlame.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgeFlame.time >= start_time)
        if end_time:
            query = query.where(SensorEdgeFlame.time <= end_time)
        
        result = await self.db_session.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "total_records": 0,
                "flame_detected_count": 0,
                "flame_detected_rate": 0.0,
                "avg_confidence": 0.0,
                "high_alert_count": 0,
                "processing_time_stats": {}
            }
        
        total_records = len(data_list)
        flame_detected_count = sum(1 for data in data_list if data.flame_detected)
        flame_detected_rate = (flame_detected_count / total_records) * 100 if total_records > 0 else 0
        
        confidence_values = [data.confidence for data in data_list if data.confidence is not None]
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
        
        high_alert_count = sum(1 for data in data_list if data.alert_level == "high")
        
        # processing_time은 Edge Flame 센서에서 사용하지 않음
        processing_time_stats = {}
        
        return {
            "total_records": total_records,
            "flame_detected_count": flame_detected_count,
            "flame_detected_rate": round(flame_detected_rate, 2),
            "avg_confidence": round(avg_confidence, 2),
            "high_alert_count": high_alert_count,
            "processing_time_stats": processing_time_stats
        }

    async def get_flame_detection_alerts(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """화재 감지 알림 조회"""
        query = select(SensorEdgeFlame).where(
            and_(
                SensorEdgeFlame.device_id == device_id,
                SensorEdgeFlame.flame_detected == True
            )
        )
        
        if start_time:
            query = query.where(SensorEdgeFlame.time >= start_time)
        if end_time:
            query = query.where(SensorEdgeFlame.time <= end_time)
        
        query = query.order_by(SensorEdgeFlame.time.desc())
        
        result = await self.db_session.execute(query)
        alert_data_list = result.scalars().all()
        
        alerts = []
        for data in alert_data_list:
            alerts.append({
                "timestamp": data.time,
                "confidence": data.confidence,
                "alert_level": data.alert_level,
                "raw_payload": data.raw_payload
            })
        
        return {
            "total_alerts": len(alerts),
            "alerts": alerts
        }
