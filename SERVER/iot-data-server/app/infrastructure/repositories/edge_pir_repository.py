"""
Edge PIR 센서 데이터 리포지토리 구현체

PIR 모션 감지 센서의 Edge 처리된 데이터를 관리합니다.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.models import SensorEdgePIR
from app.interfaces.repositories.sensor_repository import IEdgePIRRepository
from app.api.v1.schemas import EdgePIRDataCreate, EdgePIRDataUpdate, EdgePIRDataResponse


class EdgePIRRepository(IEdgePIRRepository):
    """Edge PIR 센서 데이터 리포지토리 구현체"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, data: EdgePIRDataCreate) -> EdgePIRDataResponse:
        """Edge PIR 센서 데이터 생성"""
        db_data = SensorEdgePIR(
            device_id=data.device_id,
            time=data.time,
            motion_detected=data.motion_detected,
            confidence=data.confidence,
            motion_direction=data.motion_direction,
            motion_speed=data.motion_speed,
            processing_time=data.processing_time
        )
        
        self.db_session.add(db_data)
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgePIRDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            motion_detected=db_data.motion_detected,
            confidence=db_data.confidence,
            motion_direction=db_data.motion_direction,
            motion_speed=db_data.motion_speed,
            processing_time=db_data.processing_time
        )

    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[EdgePIRDataResponse]:
        """특정 시간의 Edge PIR 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgePIR).where(
                and_(
                    SensorEdgePIR.device_id == device_id,
                    SensorEdgePIR.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgePIRDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            motion_detected=db_data.motion_detected,
            confidence=db_data.confidence,
            motion_direction=db_data.motion_direction,
            motion_speed=db_data.motion_speed,
            processing_time=db_data.processing_time
        )

    async def get_latest(self, device_id: str) -> Optional[EdgePIRDataResponse]:
        """최신 Edge PIR 센서 데이터 조회"""
        result = await self.db_session.execute(
            select(SensorEdgePIR).where(
                SensorEdgePIR.device_id == device_id
            ).order_by(SensorEdgePIR.time.desc()).limit(1)
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
            
        return EdgePIRDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            motion_detected=db_data.motion_detected,
            confidence=db_data.confidence,
            motion_direction=db_data.motion_direction,
            motion_speed=db_data.motion_speed,
            processing_time=db_data.processing_time
        )

    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[EdgePIRDataResponse]:
        """Edge PIR 센서 데이터 목록 조회"""
        query = select(SensorEdgePIR)
        
        if device_id:
            query = query.where(SensorEdgePIR.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgePIR.time >= start_time)
        
        if end_time:
            query = query.where(SensorEdgePIR.time <= end_time)
        
        query = query.order_by(SensorEdgePIR.time.desc()).limit(limit)
        
        result = await self.db_session.execute(query)
        db_data_list = result.scalars().all()
        
        return [
            EdgePIRDataResponse(
                device_id=db_data.device_id,
                time=db_data.time,
                motion_detected=db_data.motion_detected,
                confidence=db_data.confidence,
                motion_direction=db_data.motion_direction,
                motion_speed=db_data.motion_speed,
                processing_time=db_data.processing_time
            )
            for db_data in db_data_list
        ]

    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: EdgePIRDataUpdate
    ) -> Optional[EdgePIRDataResponse]:
        """Edge PIR 센서 데이터 수정"""
        result = await self.db_session.execute(
            select(SensorEdgePIR).where(
                and_(
                    SensorEdgePIR.device_id == device_id,
                    SensorEdgePIR.time == timestamp
                )
            )
        )
        
        db_data = result.scalar_one_or_none()
        if not db_data:
            return None
        
        # 업데이트할 필드만 수정
        if data.motion_detected is not None:
            db_data.motion_detected = data.motion_detected
        if data.confidence is not None:
            db_data.confidence = data.confidence
        if data.motion_direction is not None:
            db_data.motion_direction = data.motion_direction
        if data.motion_speed is not None:
            db_data.motion_speed = data.motion_speed
        if data.processing_time is not None:
            db_data.processing_time = data.processing_time
        
        await self.db_session.commit()
        await self.db_session.refresh(db_data)
        
        return EdgePIRDataResponse(
            device_id=db_data.device_id,
            time=db_data.time,
            motion_detected=db_data.motion_detected,
            confidence=db_data.confidence,
            motion_direction=db_data.motion_direction,
            motion_speed=db_data.motion_speed,
            processing_time=db_data.processing_time
        )

    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Edge PIR 센서 데이터 삭제"""
        result = await self.db_session.execute(
            select(SensorEdgePIR).where(
                and_(
                    SensorEdgePIR.device_id == device_id,
                    SensorEdgePIR.time == timestamp
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
        """Edge PIR 센서 데이터 통계 조회"""
        query = select(SensorEdgePIR).where(SensorEdgePIR.device_id == device_id)
        
        if start_time:
            query = query.where(SensorEdgePIR.time >= start_time)
        if end_time:
            query = query.where(SensorEdgePIR.time <= end_time)
        
        result = await self.db_session.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "total_records": 0,
                "motion_detected_count": 0,
                "motion_detected_rate": 0.0,
                "avg_confidence": 0.0,
                "motion_direction_stats": {},
                "motion_speed_stats": {},
                "processing_time_stats": {}
            }
        
        total_records = len(data_list)
        motion_detected_count = sum(1 for data in data_list if data.motion_detected)
        motion_detected_rate = (motion_detected_count / total_records) * 100 if total_records > 0 else 0
        
        confidence_values = [data.confidence for data in data_list if data.confidence is not None]
        avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
        
        # 모션 방향 통계
        direction_counts = {}
        for data in data_list:
            if data.motion_direction:
                direction_counts[data.motion_direction] = direction_counts.get(data.motion_direction, 0) + 1
        
        # 모션 속도 통계
        speed_values = [data.motion_speed for data in data_list if data.motion_speed is not None]
        speed_stats = {}
        if speed_values:
            speed_stats = {
                "min": min(speed_values),
                "max": max(speed_values),
                "avg": sum(speed_values) / len(speed_values)
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
            "motion_detected_count": motion_detected_count,
            "motion_detected_rate": round(motion_detected_rate, 2),
            "avg_confidence": round(avg_confidence, 2),
            "motion_direction_stats": direction_counts,
            "motion_speed_stats": speed_stats,
            "processing_time_stats": processing_time_stats
        }

    async def analyze_motion_patterns(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """모션 패턴 분석"""
        from datetime import timedelta
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=analysis_window)
        
        query = select(SensorEdgePIR).where(
            and_(
                SensorEdgePIR.device_id == device_id,
                SensorEdgePIR.time >= start_time,
                SensorEdgePIR.time <= end_time,
                SensorEdgePIR.motion_detected == True
            )
        ).order_by(SensorEdgePIR.time)
        
        result = await self.db_session.execute(query)
        motion_data_list = result.scalars().all()
        
        if not motion_data_list:
            return {
                "analysis_window_seconds": analysis_window,
                "total_motions": 0,
                "motion_frequency": 0.0,
                "peak_hours": [],
                "direction_patterns": {},
                "speed_patterns": {}
            }
        
        total_motions = len(motion_data_list)
        motion_frequency = total_motions / (analysis_window / 3600)  # 시간당 모션 수
        
        # 시간대별 모션 분포
        hour_counts = {}
        for data in motion_data_list:
            hour = data.time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hours = [{"hour": hour, "count": count} for hour, count in peak_hours]
        
        # 방향 패턴
        direction_patterns = {}
        for data in motion_data_list:
            if data.motion_direction:
                direction_patterns[data.motion_direction] = direction_patterns.get(data.motion_direction, 0) + 1
        
        # 속도 패턴
        speed_ranges = {"slow": 0, "medium": 0, "fast": 0}
        for data in motion_data_list:
            if data.motion_speed is not None:
                if data.motion_speed < 1.0:
                    speed_ranges["slow"] += 1
                elif data.motion_speed < 3.0:
                    speed_ranges["medium"] += 1
                else:
                    speed_ranges["fast"] += 1
        
        return {
            "analysis_window_seconds": analysis_window,
            "total_motions": total_motions,
            "motion_frequency": round(motion_frequency, 2),
            "peak_hours": peak_hours,
            "direction_patterns": direction_patterns,
            "speed_patterns": speed_ranges
        }
