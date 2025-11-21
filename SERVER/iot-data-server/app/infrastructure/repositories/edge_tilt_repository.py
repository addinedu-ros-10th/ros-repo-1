"""
Edge Tilt 센서 데이터 리포지토리 구현체

Tilt 기울기 센서의 Edge 처리된 데이터를 관리합니다.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import SensorEdgeTilt
from app.interfaces.repositories.sensor_repository import IEdgeTiltRepository
from app.api.v1.schemas import EdgeTiltDataCreate, EdgeTiltDataUpdate, EdgeTiltDataResponse


class EdgeTiltRepository(IEdgeTiltRepository):
    """Edge Tilt 센서 데이터 리포지토리 구현체"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, data: EdgeTiltDataCreate) -> EdgeTiltDataResponse:
        """Edge Tilt 센서 데이터 생성"""
        db_data = SensorEdgeTilt(
            device_id=data.device_id,
            time=data.time,
            tilt_detected=data.tilt_detected,
            confidence=data.confidence,
            tilt_angle=data.tilt_angle,
            tilt_direction=data.tilt_direction,
            processing_time=data.processing_time
        )
        
        self.db_session.add(db_data)
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgeTiltDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            tilt_detected=db_data.tilt_detected,
            confidence=db_data.confidence,
            tilt_angle=db_data.tilt_angle,
            tilt_direction=db_data.tilt_direction,
            processing_time=db_data.processing_time
        )

    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[EdgeTiltDataResponse]:
        """특정 시간의 Edge Tilt 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgeTilt).where(
                and_(
                    SensorEdgeTilt.device_id == device_id,
                    SensorEdgeTilt.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgeTiltDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            tilt_detected=db_data.tilt_detected,
            confidence=db_data.confidence,
            tilt_angle=db_data.tilt_angle,
            tilt_direction=db_data.tilt_direction,
            processing_time=db_data.processing_time
        )

    async def get_latest(self, device_id: str) -> Optional[EdgeTiltDataResponse]:
        """최신 Edge Tilt 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgeTilt).where(
                SensorEdgeTilt.device_id == device_id
            ).order_by(SensorEdgeTilt.time.desc()).limit(1)
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgeTiltDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            tilt_detected=db_data.tilt_detected,
            confidence=db_data.confidence,
            tilt_angle=db_data.tilt_angle,
            tilt_direction=db_data.tilt_direction,
            processing_time=db_data.processing_time
        )

    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EdgeTiltDataResponse]:
        """Edge Tilt 센서 데이터 목록 조회"""
        query = select(SensorEdgeTilt)
        
        if device_id:
            query = query.where(SensorEdgeTilt.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgeTilt.time >= start_time)
        
        if end_time:
            query = query.where(SensorEdgeTilt.time <= end_time)
        
        query = query.order_by(SensorEdgeTilt.time.desc()).limit(limit)
        
        result = await self.db_session.execute(query)
        db_data_list = result.scalars().all()
        
        return [
            EdgeTiltDataResponse(
                device_id=db_data.device_id,
                time=db_data.time,
                tilt_detected=db_data.tilt_detected,
                confidence=db_data.confidence,
                tilt_angle=db_data.tilt_angle,
                tilt_direction=db_data.tilt_direction,
                processing_time=db_data.processing_time
            )
            for db_data in db_data_list
        ]

    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: EdgeTiltDataUpdate
    ) -> Optional[EdgeTiltDataResponse]:
        """Edge Tilt 센서 데이터 수정"""
        result = await self.db_session.execute(
            select(SensorEdgeTilt).where(
                and_(
                    SensorEdgeTilt.device_id == device_id,
                    SensorEdgeTilt.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
        
        # 업데이트할 필드만 수정
        if data.tilt_detected is not None:
            db_data.tilt_detected = data.tilt_detected
        if data.confidence is not None:
            db_data.confidence = data.confidence
        if data.tilt_angle is not None:
            db_data.tilt_angle = data.tilt_angle
        if data.tilt_direction is not None:
            db_data.tilt_direction = data.tilt_direction
        if data.processing_time is not None:
            db_data.processing_time = data.processing_time
        
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgeTiltDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            tilt_detected=db_data.tilt_detected,
            confidence=db_data.confidence,
            tilt_angle=db_data.tilt_angle,
            tilt_direction=db_data.tilt_direction,
            processing_time=db_data.processing_time
        )

    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Edge Tilt 센서 데이터 삭제"""
        result = await self.db_session.execute(
            select(SensorEdgeTilt).where(
                and_(
                    SensorEdgeTilt.device_id == device_id,
                    SensorEdgeTilt.time == timestamp
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
        """Edge Tilt 센서 데이터 통계 조회"""
        query = select(SensorEdgeTilt).where(SensorEdgeTilt.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgeTilt.time >= start_time)
        if end_time:
            query = query.where(SensorEdgeTilt.time <= end_time)
        
        result = await self.db_session.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "total_records": 0,
                "tilt_detected_count": 0,
                "tilt_detected_rate": 0.0,
                "avg_confidence": 0.0,
                "tilt_angle_stats": {},
                "tilt_direction_stats": {},
                "processing_time_stats": {}
            }
        
        total_records = len(data_list)
        tilt_detected_count = sum(1 for data in data_list if data.tilt_detected)
        tilt_detected_rate = (tilt_detected_count / total_records) * 100 if total_records > 0 else 0
        
        confidence_values = [data.confidence for data in data_list if data.confidence is not None]
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
        
        # 기울기 각도 통계
        angle_values = [data.tilt_angle for data in data_list if data.tilt_angle is not None]
        angle_stats = {}
        if angle_values:
            angle_stats = {
                "min": min(angle_values),
                "max": max(angle_values),
                "avg": sum(angle_values) / len(angle_values)
            }
        
        # 기울기 방향 통계
        direction_counts = {}
        for data in data_list:
            if data.tilt_direction:
                direction_counts[data.tilt_direction] = direction_counts.get(data.tilt_direction, 0) + 1
        
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
            "tilt_detected_count": tilt_detected_count,
            "tilt_detected_rate": round(tilt_detected_rate, 2),
            "avg_confidence": round(avg_confidence, 2),
            "tilt_angle_stats": angle_stats,
            "tilt_direction_stats": direction_counts,
            "processing_time_stats": processing_time_stats
        }

    async def analyze_tilt_trends(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """기울기 트렌드 분석"""
        from datetime import timedelta
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=analysis_window)
        
        query = select(SensorEdgeTilt).where(
            and_(
                SensorEdgeTilt.device_id == device_id,
                SensorEdgeTilt.time >= start_time,
                SensorEdgeTilt.time <= end_time,
                SensorEdgeTilt.tilt_detected == True
            )
        ).order_by(SensorEdgeTilt.time)
        
        result = await self.db_session.execute(query)
        tilt_data_list = result.scalars().all()
        
        if not tilt_data_list:
            return {
                "analysis_window_seconds": analysis_window,
                "total_tilts": 0,
                "tilt_frequency": 0.0,
                "peak_hours": [],
                "angle_trends": {},
                "direction_patterns": {}
            }
        
        total_tilts = len(tilt_data_list)
        tilt_frequency = total_tilts / (analysis_window / 3600)  # 시간당 기울기 수
        
        # 시간대별 기울기 분포
        hour_counts = {}
        for data in tilt_data_list:
            hour = data.time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = [{"hour": hour, "count": count} for hour, count in peak_hours]
        
        # 각도 트렌드
        angle_ranges = {"low": 0, "medium": 0, "high": 0}
        for data in tilt_data_list:
            if data.tilt_angle is not None:
                if data.tilt_angle < 15:
                    angle_ranges["low"] += 1
                elif data.tilt_angle < 45:
                    angle_ranges["medium"] += 1
                else:
                    angle_ranges["high"] += 1
        
        # 방향 패턴
        direction_patterns = {}
        for data in tilt_data_list:
            if data.tilt_direction:
                direction_patterns[data.tilt_direction] = direction_patterns.get(data.tilt_direction, 0) + 1
        
        return {
            "analysis_window_seconds": analysis_window,
            "total_tilts": total_tilts,
            "tilt_frequency": round(tilt_frequency, 2),
            "peak_hours": peak_hours,
            "angle_trends": angle_ranges,
            "direction_patterns": direction_patterns
        }
