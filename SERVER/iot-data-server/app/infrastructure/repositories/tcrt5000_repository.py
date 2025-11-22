"""
TCRT5000 센서 데이터 리포지토리 구현체

Clean Architecture 원칙에 따라 TCRT5000 센서 데이터에 대한 데이터 접근을 담당합니다.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.interfaces.repositories.sensor_repository import ITCRT5000Repository
from app.infrastructure.models import SensorRawTCRT5000
from app.api.v1.schemas import (
    SensorRawTCRT5000Create,
    SensorRawTCRT5000Update,
    SensorRawTCRT5000Response
)


class TCRT5000Repository(ITCRT5000Repository):
    """TCRT5000 센서 데이터 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: SensorRawTCRT5000Create) -> SensorRawTCRT5000Response:
        """TCRT5000 근접 센서 데이터 생성"""
        # 실제 DB 테이블 구조에 맞게 매핑 (time, device_id, raw_payload만 사용)
        orm_data = {
            "time": data.time,
            "device_id": data.device_id,
            "raw_payload": data.raw_payload
        }
        
        db_data = SensorRawTCRT5000(**orm_data)
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return SensorRawTCRT5000Response.from_orm(db_data)
    
    async def get_by_id(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawTCRT5000Response]:
        """특정 시간의 TCRT5000 센서 데이터 조회"""
        query = select(SensorRawTCRT5000).where(
            and_(
                SensorRawTCRT5000.device_id == device_id,
                SensorRawTCRT5000.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        data = result.scalar_one_or_none()
        
        if data:
            return SensorRawTCRT5000Response.from_orm(data)
        return None
    
    async def get_latest(self, device_id: str) -> Optional[SensorRawTCRT5000Response]:
        """최신 TCRT5000 센서 데이터 조회"""
        query = (
            select(SensorRawTCRT5000)
            .where(SensorRawTCRT5000.device_id == device_id)
            .order_by(SensorRawTCRT5000.time.desc())
        )
        
        result = self.db.execute(query)
        data = result.scalars().first()
        
        if data:
            return SensorRawTCRT5000Response.from_orm(data)
        return None
    
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit_count: int = 100
    ) -> List[SensorRawTCRT5000Response]:
        """TCRT5000 센서 데이터 목록 조회"""
        query = select(SensorRawTCRT5000)
        
        # 필터 조건 추가
        if device_id:
            query = query.where(SensorRawTCRT5000.device_id == device_id)
        if start_time:
            query = query.where(SensorRawTCRT5000.time >= start_time)
        if end_time:
            query = query.where(SensorRawTCRT5000.time <= end_time)
        
        # 시간 역순으로 정렬하고 제한
        query = query.order_by(SensorRawTCRT5000.time.desc()).limit(limit_count)
        
        result = self.db.execute(query)
        data_list = result.scalars().all()
        
        # 결과를 리스트로 변환하여 반환
        return [SensorRawTCRT5000Response.from_orm(data) for data in data_list]
    
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data:     SensorRawTCRT5000Update,

    ) -> Optional[SensorRawTCRT5000Response]:
        """TCRT5000 센서 데이터 수정"""
        query = select(SensorRawTCRT5000).where(
            and_(
                SensorRawTCRT5000.device_id == device_id,
                SensorRawTCRT5000.time == timestamp
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
        return SensorRawTCRT5000Response.from_orm(db_data)
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """TCRT5000 센서 데이터 삭제"""
        query = select(SensorRawTCRT5000).where(
            and_(
                SensorRawTCRT5000.device_id == device_id,
                SensorRawTCRT5000.time == timestamp
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
        """TCRT5000 센서 데이터 기본 통계 조회"""
        return await self.get_proximity_statistics(device_id, start_time, end_time)
    
    async def get_proximity_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """근접 감지 통계 정보 조회"""
        query = select(SensorRawTCRT5000).where(SensorRawTCRT5000.device_id == device_id)
        
        if start_time:
            query = query.where(SensorRawTCRT5000.time >= start_time)
        if end_time:
            query = query.where(SensorRawTCRT5000.time <= end_time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "total_records": 0,
                "detection_count": 0,
                "detection_rate": 0,
                "avg_analog_value": 0
            }
        
        # 통계 계산
        detection_count = sum(1 for data in data_list if data.object_detected)
        total_count = len(data_list)
        detection_rate = (detection_count / total_count) * 100 if total_count > 0 else 0
        
        analog_values = [data.analog_value for data in data_list if data.analog_value is not None]
        avg_analog_value = sum(analog_values) / len(analog_values) if analog_values else 0
        
        return {
            "device_id": device_id,
            "total_records": total_count,
            "detection_count": detection_count,
            "detection_rate": round(detection_rate, 2),
            "avg_analog_value": round(avg_analog_value, 2),
            "analog_samples": len(analog_values)
        }
    
    async def analyze_motion_patterns(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """움직임 패턴 분석"""
        # 분석 시간 범위 계산
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=analysis_window)
        
        query = select(SensorRawTCRT5000).where(
            and_(
                SensorRawTCRT5000.device_id == device_id,
                SensorRawTCRT5000.time >= start_time,
                SensorRawTCRT5000.time <= end_time
            )
        ).order_by(SensorRawTCRT5000.time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "analysis_window_seconds": analysis_window,
                "total_records": 0,
                "motion_pattern": "no_data"
            }
        
        # 움직임 패턴 분석
        detections = [data for data in data_list if data.object_detected]
        
        if not detections:
            return {
                "device_id": device_id,
                "analysis_window_seconds": analysis_window,
                "total_records": len(data_list),
                "motion_pattern": "no_motion",
                "detection_count": 0
            }
        
        # 연속 감지 구간 분석
        detection_periods = []
        current_start = None
        
        for data in data_list:
            if data.object_detected and current_start is None:
                current_start = data.time
            elif not data.object_detected and current_start is not None:
                detection_periods.append({
                    "start": current_start.isoformat(),
                    "end": data.time.isoformat(),
                    "duration_seconds": (data.time - current_start).total_seconds()
                })
                current_start = None
        
        # 마지막 감지가 끝나지 않은 경우
        if current_start is not None:
            detection_periods.append({
                "start": current_start.isoformat(),
                "end": end_time.isoformat(),
                "duration_seconds": (end_time - current_start).total_seconds()
            })
        
        # 패턴 분석
        if len(detection_periods) == 0:
            motion_pattern = "continuous_detection"
        elif len(detection_periods) == 1:
            motion_pattern = "single_motion"
        elif len(detection_periods) <= 3:
            motion_pattern = "sparse_motion"
        else:
            motion_pattern = "frequent_motion"
        
        avg_duration = sum(p["duration_seconds"] for p in detection_periods) / len(detection_periods) if detection_periods else 0
        
        return {
            "device_id": device_id,
            "analysis_window_seconds": analysis_window,
            "total_records": len(data_list),
            "motion_pattern": motion_pattern,
            "detection_count": len(detections),
            "detection_periods": len(detection_periods),
            "avg_duration_seconds": round(avg_duration, 2),
            "detection_periods_detail": detection_periods
        } 