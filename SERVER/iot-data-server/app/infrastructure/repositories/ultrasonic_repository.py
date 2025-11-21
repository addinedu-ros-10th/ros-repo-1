"""
Ultrasonic 센서 데이터 리포지토리 구현체

Clean Architecture 원칙에 따라 Ultrasonic 센서 데이터에 대한 데이터 접근을 담당합니다.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.interfaces.repositories.sensor_repository import IUltrasonicRepository
from app.infrastructure.models import SensorRawUltrasonic
from app.api.v1.schemas import (
    SensorRawUltrasonicCreate,
    SensorRawUltrasonicUpdate,
    SensorRawUltrasonicResponse
)


class UltrasonicRepository(IUltrasonicRepository):
    """Ultrasonic 센서 데이터 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: SensorRawUltrasonicCreate) -> SensorRawUltrasonicResponse:
        """Ultrasonic 센서 데이터 생성"""
        # 실제 DB 테이블 구조에 맞게 매핑 (time, device_id, raw_payload만 사용)
        orm_data = {
            "time": data.time,
            "device_id": data.device_id,
            "raw_payload": data.raw_payload
        }
        
        db_data = SensorRawUltrasonic(**orm_data)
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return SensorRawUltrasonicResponse.from_orm(db_data)
    
    async def get_by_id(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawUltrasonicResponse]:
        """특정 시간의 Ultrasonic 센서 데이터 조회"""
        query = select(SensorRawUltrasonic).where(
            and_(
                SensorRawUltrasonic.device_id == device_id,
                SensorRawUltrasonic.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        data = result.scalar_one_or_none()
        
        if data:
            return SensorRawUltrasonicResponse.from_orm(data)
        return None
    
    async def get_latest(self, device_id: str) -> Optional[SensorRawUltrasonicResponse]:
        """최신 Ultrasonic 센서 데이터 조회"""
        query = (
            select(SensorRawUltrasonic)
            .where(SensorRawUltrasonic.device_id == device_id)
            .order_by(SensorRawUltrasonic.time.desc())
        )
        
        result = self.db.execute(query)
        data = result.scalars().first()
        
        if data:
            return SensorRawUltrasonicResponse.from_orm(data)
        return None
    
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit_count: int = 100
    ) -> List[SensorRawUltrasonicResponse]:
        """Ultrasonic 센서 데이터 목록 조회"""
        query = select(SensorRawUltrasonic)
        
        # 필터 조건 추가
        if device_id:
            query = query.where(SensorRawUltrasonic.device_id == device_id)
        if start_time:
            query = query.where(SensorRawUltrasonic.time >= start_time)
        if end_time:
            query = query.where(SensorRawUltrasonic.time <= end_time)
        
        # 시간 역순으로 정렬하고 제한
        query = query.order_by(SensorRawUltrasonic.time.desc()).limit(limit_count)
        
        result = self.db.execute(query)
        data_list = result.scalars().all()
        
        # 결과를 리스트로 변환하여 반환
        return [SensorRawUltrasonicResponse.from_orm(data) for data in data_list]
    
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawUltrasonicUpdate
    ) -> Optional[SensorRawUltrasonicResponse]:
        """Ultrasonic 센서 데이터 수정"""
        query = select(SensorRawUltrasonic).where(
            and_(
                SensorRawUltrasonic.device_id == device_id,
                SensorRawUltrasonic.time == timestamp
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
        return SensorRawUltrasonicResponse.from_orm(db_data)
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Ultrasonic 센서 데이터 삭제"""
        query = select(SensorRawUltrasonic).where(
            and_(
                SensorRawUltrasonic.device_id == device_id,
                SensorRawUltrasonic.time == timestamp
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
        """Ultrasonic 센서 데이터 기본 통계 조회"""
        return await self.get_distance_statistics(device_id, start_time, end_time)
    
    async def get_distance_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """거리 측정 통계 정보 조회"""
        query = select(SensorRawUltrasonic).where(SensorRawUltrasonic.device_id == device_id)
        
        if start_time:
            query = query.where(SensorRawUltrasonic.time >= start_time)
        if end_time:
            query = query.where(SensorRawUltrasonic.time <= end_time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "total_records": 0,
                "avg_distance_cm": 0,
                "max_distance_cm": 0,
                "min_distance_cm": 0,
                "measurement_valid_count": 0
            }
        
        # 통계 계산
        distance_values = [data.distance_cm for data in data_list if data.distance_cm is not None]
        valid_measurements = [data for data in data_list if data.measurement_valid]
        
        if not distance_values:
            return {
                "device_id": device_id,
                "total_records": len(data_list),
                "avg_distance_cm": 0,
                "max_distance_cm": 0,
                "min_distance_cm": 0,
                "measurement_valid_count": len(valid_measurements)
            }
        
        avg_distance = sum(distance_values) / len(distance_values)
        max_distance = max(distance_values)
        min_distance = min(distance_values)
        
        return {
            "device_id": device_id,
            "total_records": len(data_list),
            "avg_distance_cm": round(avg_distance, 2),
            "max_distance_cm": round(max_distance, 2),
            "min_distance_cm": round(min_distance, 2),
            "measurement_valid_count": len(valid_measurements),
            "distance_samples": len(distance_values)
        }
    
    async def analyze_distance_trends(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """거리 트렌드 분석"""
        # 분석 시간 범위 계산
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(seconds=analysis_window)
        
        query = select(SensorRawUltrasonic).where(
            and_(
                SensorRawUltrasonic.device_id == device_id,
                SensorRawUltrasonic.time >= start_time,
                SensorRawUltrasonic.time <= end_time,
                SensorRawUltrasonic.measurement_valid == True
            )
        ).order_by(SensorRawUltrasonic.time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "analysis_window_seconds": analysis_window,
                "total_records": 0,
                "trend": "no_data"
            }
        
        if len(data_list) < 2:
            return {
                "device_id": device_id,
                "analysis_window_seconds": analysis_window,
                "total_records": len(data_list),
                "trend": "insufficient_data"
            }
        
        # 거리 변화 분석
        distances = [data.distance_cm for data in data_list if data.distance_cm is not None]
        if len(distances) < 2:
            return {
                "device_id": device_id,
                "analysis_window_seconds": analysis_window,
                "total_records": len(data_list),
                "trend": "insufficient_distance_data"
            }
        
        # 거리 변화율 계산
        distance_changes = []
        for i in range(1, len(distances)):
            change = distances[i] - distances[i-1]
            distance_changes.append(change)
        
        avg_change = sum(distance_changes) / len(distance_changes)
        
        # 트렌드 분류
        if abs(avg_change) < 1:
            trend = "stable"
        elif avg_change > 5:
            trend = "increasing_rapidly"
        elif avg_change > 1:
            trend = "increasing_slowly"
        elif avg_change < -5:
            trend = "decreasing_rapidly"
        else:
            trend = "decreasing_slowly"
        
        # 변동성 분석
        variance = sum((x - avg_change) ** 2 for x in distance_changes) / len(distance_changes)
        std_dev = variance ** 0.5
        
        # 알림 생성
        alerts = []
        if abs(avg_change) > 10:
            alerts.append("거리 변화가 급격합니다")
        if std_dev > 20:
            alerts.append("거리 측정이 불안정합니다") 
        
        return {
            "device_id": device_id,
            "analysis_window_seconds": analysis_window,
            "total_records": len(data_list),
            "trend": trend,
            "avg_change_cm": round(avg_change, 2),
            "std_deviation": round(std_dev, 2),
            "distance_samples": len(distances),
            "alerts": alerts
        } 