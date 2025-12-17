"""
DeviceRTCStatus 서비스 구현체

Clean Architecture 원칙에 따라 디바이스 RTC 상태 데이터에 대한 비즈니스 로직을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from app.interfaces.services.device_rtc_service_interface import IDeviceRTCStatusService
from app.interfaces.repositories.device_rtc_repository import IDeviceRTCStatusRepository
from app.api.v1.schemas import (
    DeviceRTCDataCreate,
    DeviceRTCDataUpdate,
    DeviceRTCDataResponse
)


class DeviceRTCStatusService(IDeviceRTCStatusService):
    """디바이스 RTC 상태 서비스 구현체"""
    
    def __init__(self, rtc_repository: IDeviceRTCStatusRepository):
        self.rtc_repository = rtc_repository
    
    async def create_rtc_status(self, data: DeviceRTCDataCreate) -> DeviceRTCDataResponse:
        """RTC 상태 데이터 생성"""
        try:
            # 비즈니스 로직 검증
            if data.drift_ms is not None and abs(data.drift_ms) > 86400000:  # 24시간을 초과하는 드리프트는 비정상
                raise ValueError("드리프트 값이 비정상적으로 큽니다 (24시간 초과)")
            
            if data.rtc_epoch_s is not None and data.rtc_epoch_s < 0:
                raise ValueError("RTC epoch 시간은 0 이상이어야 합니다")
            
            # 리포지토리를 통한 데이터 생성
            created_data = await self.rtc_repository.create(data)
            return created_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RTC 상태 데이터 생성 실패: {str(e)}")
    
    async def get_rtc_status(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[DeviceRTCDataResponse]:
        """특정 시간의 RTC 상태 데이터 조회"""
        try:
            data = await self.rtc_repository.get_by_id(device_id, timestamp)
            if not data:
                raise HTTPException(status_code=404, detail="RTC 상태 데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RTC 상태 데이터 조회 실패: {str(e)}")
    
    async def get_latest_rtc_status(self, device_id: str) -> Optional[DeviceRTCDataResponse]:
        """최신 RTC 상태 데이터 조회"""
        try:
            data = await self.rtc_repository.get_latest(device_id)
            if not data:
                raise HTTPException(status_code=404, detail="해당 디바이스의 RTC 상태 데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RTC 상태 데이터 조회 실패: {str(e)}")
    
    async def get_rtc_status_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[DeviceRTCDataResponse]:
        """RTC 상태 데이터 목록 조회"""
        try:
            # 비즈니스 로직 검증
            if limit < 1 or limit > 1000:
                raise ValueError("조회 개수는 1에서 1000 사이여야 합니다")
            
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            data_list = await self.rtc_repository.get_list(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit_count=limit
            )
            return data_list
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RTC 상태 데이터 목록 조회 실패: {str(e)}")
    
    async def update_rtc_status(
        self,
        device_id: str,
        timestamp: datetime,
        data: DeviceRTCDataUpdate
    ) -> Optional[DeviceRTCDataResponse]:
        """RTC 상태 데이터 수정"""
        try:
            # 비즈니스 로직 검증
            if data.drift_ms is not None and abs(data.drift_ms) > 86400000:
                raise ValueError("드리프트 값이 비정상적으로 큽니다 (24시간 초과)")
            
            if data.rtc_epoch_s is not None and data.rtc_epoch_s < 0:
                raise ValueError("RTC epoch 시간은 0 이상이어야 합니다")
            
            # 리포지토리를 통한 데이터 수정
            updated_data = await self.rtc_repository.update(device_id, timestamp, data)
            if not updated_data:
                raise HTTPException(status_code=404, detail="수정할 RTC 상태 데이터를 찾을 수 없습니다")
            
            return updated_data
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RTC 상태 데이터 수정 실패: {str(e)}")
    
    async def delete_rtc_status(self, device_id: str, timestamp: datetime) -> bool:
        """RTC 상태 데이터 삭제"""
        try:
            success = await self.rtc_repository.delete(device_id, timestamp)
            if not success:
                raise HTTPException(status_code=404, detail="삭제할 RTC 상태 데이터를 찾을 수 없습니다")
            
            return success
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RTC 상태 데이터 삭제 실패: {str(e)}")
    
    async def get_sync_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """동기화 통계 정보 조회"""
        try:
            stats = await self.rtc_repository.get_sync_statistics(device_id, start_time, end_time)
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"동기화 통계 조회 실패: {str(e)}")
    
    async def get_drift_analysis(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """시간 드리프트 분석 정보 조회"""
        try:
            analysis = await self.rtc_repository.get_drift_analysis(device_id, start_time, end_time)
            return analysis
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"드리프트 분석 조회 실패: {str(e)}")
    
    async def get_time_sync_health(
        self,
        device_id: str
    ) -> dict:
        """시간 동기화 상태 건강도 조회"""
        try:
            # 최신 RTC 상태 조회
            latest_status = await self.rtc_repository.get_latest(device_id)
            if not latest_status:
                return {
                    "device_id": device_id,
                    "health_status": "unknown",
                    "last_sync": None,
                    "drift_level": "unknown",
                    "sync_quality": "unknown",
                    "recommendations": ["RTC 상태 데이터가 없습니다"]
                }
            
            # 건강도 평가
            health_status = "healthy"
            drift_level = "low"
            sync_quality = "good"
            recommendations = []
            
            # 드리프트 기반 건강도 평가
            if latest_status.drift_ms is not None:
                abs_drift = abs(latest_status.drift_ms)
                if abs_drift < 1000:  # 1초 미만
                    drift_level = "very_low"
                    sync_quality = "excellent"
                elif abs_drift < 5000:  # 5초 미만
                    drift_level = "low"
                    sync_quality = "good"
                elif abs_drift < 30000:  # 30초 미만
                    drift_level = "moderate"
                    sync_quality = "fair"
                    health_status = "warning"
                    recommendations.append("RTC 동기화 주기를 단축하세요")
                else:  # 30초 이상
                    drift_level = "high"
                    sync_quality = "poor"
                    health_status = "critical"
                    recommendations.append("즉시 RTC 동기화가 필요합니다")
                    recommendations.append("더 정확한 시간 소스를 사용하세요")
            
            # 마지막 동기화 시간 평가
            last_sync = latest_status.time
            time_since_sync = (datetime.utcnow() - last_sync).total_seconds()
            
            if time_since_sync > 86400:  # 24시간 이상
                health_status = "critical" if health_status == "healthy" else health_status
                recommendations.append("24시간 이상 RTC 동기화가 없습니다")
            elif time_since_sync > 3600:  # 1시간 이상
                if health_status == "healthy":
                    health_status = "warning"
                recommendations.append("정기적인 RTC 동기화를 권장합니다")
            
            # 동기화 소스 평가
            if latest_status.sync_source:
                if latest_status.sync_source.lower() in ["ntp", "gps", "atomic"]:
                    sync_quality = "excellent" if sync_quality == "good" else sync_quality
                elif latest_status.sync_source.lower() in ["manual", "unknown"]:
                    sync_quality = "poor" if sync_quality == "good" else sync_quality
                    recommendations.append("더 정확한 동기화 소스를 사용하세요")
            
            return {
                "device_id": device_id,
                "health_status": health_status,
                "last_sync": last_sync.isoformat(),
                "drift_level": drift_level,
                "sync_quality": sync_quality,
                "current_drift_ms": latest_status.drift_ms,
                "sync_source": latest_status.sync_source,
                "recommendations": recommendations
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"시간 동기화 건강도 조회 실패: {str(e)}") 