"""
DeviceRTCStatus 리포지토리 구현체

Clean Architecture 원칙에 따라 디바이스 RTC 상태 데이터에 대한 데이터 접근을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.interfaces.repositories.device_rtc_repository import IDeviceRTCStatusRepository
from app.infrastructure.models import DeviceRTCStatus
from app.api.v1.schemas import (
    DeviceRTCDataCreate,
    DeviceRTCDataUpdate,
    DeviceRTCDataResponse
)


class DeviceRTCStatusRepository(IDeviceRTCStatusRepository):
    """디바이스 RTC 상태 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: DeviceRTCDataCreate) -> DeviceRTCDataResponse:
        """RTC 상태 데이터 생성"""
        db_data = DeviceRTCStatus(**data.dict())
        self.db.add(db_data)
        self.db.commit()
        self.db.refresh(db_data)
        return DeviceRTCDataResponse.from_orm(db_data)
    
    async def get_by_id(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[DeviceRTCDataResponse]:
        """특정 시간의 RTC 상태 데이터 조회"""
        query = select(DeviceRTCStatus).where(
            and_(
                DeviceRTCStatus.device_id == device_id,
                DeviceRTCStatus.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        data = result.scalar_one_or_none()
        
        if data:
            return DeviceRTCDataResponse.from_orm(data)
        return None
    
    async def get_latest(self, device_id: str) -> Optional[DeviceRTCDataResponse]:
        """최신 RTC 상태 데이터 조회"""
        query = (
            select(DeviceRTCStatus)
            .where(DeviceRTCStatus.device_id == device_id)
            .order_by(DeviceRTCStatus.time.desc())
        )
        
        result = self.db.execute(query)
        data = result.scalars().first()
        
        if data:
            return DeviceRTCDataResponse.from_orm(data)
        return None
    
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit_count: int = 100
    ) -> List[DeviceRTCDataResponse]:
        """RTC 상태 데이터 목록 조회"""
        query = select(DeviceRTCStatus)
        
        # 필터 조건 추가
        if device_id:
            query = query.where(DeviceRTCStatus.device_id == device_id)
        if start_time:
            query = query.where(DeviceRTCStatus.time >= start_time)
        if end_time:
            query = query.where(DeviceRTCStatus.time <= end_time)
        
        # 시간 역순으로 정렬하고 제한
        query = query.order_by(DeviceRTCStatus.time.desc()).limit(limit_count)
        
        result = self.db.execute(query)
        data_list = result.scalars().all()
        
        # 결과를 리스트로 변환하여 반환
        return [DeviceRTCDataResponse.from_orm(data) for data in data_list]
    
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: DeviceRTCDataUpdate
    ) -> Optional[DeviceRTCDataResponse]:
        """RTC 상태 데이터 수정"""
        query = select(DeviceRTCStatus).where(
            and_(
                DeviceRTCStatus.device_id == device_id,
                DeviceRTCStatus.time == timestamp
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
        return DeviceRTCDataResponse.from_orm(db_data)
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """RTC 상태 데이터 삭제"""
        query = select(DeviceRTCStatus).where(
            and_(
                DeviceRTCStatus.device_id == device_id,
                DeviceRTCStatus.time == timestamp
            )
        )
        
        result = self.db.execute(query)
        db_data = result.scalar_one_or_none()
        
        if not db_data:
            return False
        
        await self.db.delete(db_data)
        await self.db.commit()
        return True
    
    async def get_sync_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """동기화 통계 정보 조회"""
        query = select(DeviceRTCStatus).where(DeviceRTCStatus.device_id == device_id)
        
        if start_time:
            query = query.where(DeviceRTCStatus.time >= start_time)
        if end_time:
            query = query.where(DeviceRTCStatus.time <= end_time)
        
        result = self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "total_records": 0,
                "sync_sources": {},
                "avg_drift_ms": 0,
                "max_drift_ms": 0,
                "min_drift_ms": 0
            }
        
        # 통계 계산
        drift_values = [data.drift_ms for data in data_list if data.drift_ms is not None]
        sync_sources = {}
        
        for data in data_list:
            if data.sync_source:
                sync_sources[data.sync_source] = sync_sources.get(data.sync_source, 0) + 1
        
        return {
            "device_id": device_id,
            "total_records": len(data_list),
            "sync_sources": sync_sources,
            "avg_drift_ms": sum(drift_values) / len(drift_values) if drift_values else 0,
            "max_drift_ms": max(drift_values) if drift_values else 0,
            "min_drift_ms": min(drift_values) if drift_values else 0,
            "drift_samples": len(drift_values)
        }
    
    async def get_drift_analysis(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """시간 드리프트 분석 정보 조회"""
        query = select(DeviceRTCStatus).where(DeviceRTCStatus.device_id == device_id)
        
        if start_time:
            query = query.where(DeviceRTCStatus.time >= start_time)
        if end_time:
            query = query.where(DeviceRTCStatus.time <= end_time)
        
        result = await self.db.execute(query)
        data_list = result.scalars().all()
        
        if not data_list:
            return {
                "device_id": device_id,
                "drift_trend": "stable",
                "drift_rate_ms_per_hour": 0,
                "stability_score": 0,
                "recommendations": ["데이터가 부족합니다"]
            }
        
        # 드리프트 트렌드 분석
        drift_values = [data.drift_ms for data in data_list if data.drift_ms is not None]
        if len(drift_values) < 2:
            return {
                "device_id": device_id,
                "drift_trend": "insufficient_data",
                "drift_rate_ms_per_hour": 0,
                "stability_score": 0,
                "recommendations": ["더 많은 데이터가 필요합니다"]
            }
        
        # 시간 간격별 드리프트 변화율 계산
        sorted_data = sorted(data_list, key=lambda x: x.time)
        drift_changes = []
        time_intervals = []
        
        for i in range(1, len(sorted_data)):
            if sorted_data[i].drift_ms is not None and sorted_data[i-1].drift_ms is not None:
                drift_diff = sorted_data[i].drift_ms - sorted_data[i-1].drift_ms
                time_diff = (sorted_data[i].time - sorted_data[i-1].time).total_seconds() / 3600  # 시간 단위
                
                if time_diff > 0:
                    drift_rate = drift_diff / time_diff
                    drift_changes.append(drift_rate)
                    time_intervals.append(time_diff)
        
        if not drift_changes:
            return {
                "device_id": device_id,
                "drift_trend": "stable",
                "drift_rate_ms_per_hour": 0,
                "stability_score": 0,
                "recommendations": ["드리프트 변화가 없습니다"]
            }
        
        avg_drift_rate = sum(drift_changes) / len(drift_changes)
        
        # 안정성 점수 계산 (드리프트 변화의 표준편차 기반)
        variance = sum((x - avg_drift_rate) ** 2 for x in drift_changes) / len(drift_changes)
        std_dev = variance ** 0.5
        
        if std_dev < 10:
            stability_score = 90
            drift_trend = "very_stable"
        elif std_dev < 50:
            stability_score = 70
            drift_trend = "stable"
        elif std_dev < 100:
            stability_score = 50
            drift_trend = "moderate"
        else:
            stability_score = 30
            drift_trend = "unstable"
        
        # 권장사항 생성
        recommendations = []
        if stability_score < 50:
            recommendations.append("RTC 동기화 주기를 단축하세요")
            recommendations.append("더 정확한 시간 소스를 사용하세요")
        elif stability_score < 70:
            recommendations.append("정기적인 RTC 동기화를 권장합니다")
        else:
            recommendations.append("현재 설정이 적절합니다")
        
        return {
            "device_id": device_id,
            "drift_trend": drift_trend,
            "drift_rate_ms_per_hour": round(avg_drift_rate, 2),
            "stability_score": stability_score,
            "std_deviation": round(std_dev, 2),
            "total_samples": len(drift_changes),
            "recommendations": recommendations
        } 