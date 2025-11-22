"""
DeviceRTCStatus API

Clean Architecture 원칙에 따라 디바이스 RTC 상태 데이터를 관리하는 API 엔드포인트를 제공합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.core.container import container
from app.interfaces.services.device_rtc_service_interface import IDeviceRTCStatusService
from app.api.v1.schemas import (
    DeviceRTCDataCreate,
    DeviceRTCDataUpdate,
    DeviceRTCDataResponse
)

router = APIRouter()


def get_device_rtc_service(db: AsyncSession = Depends(get_db)) -> IDeviceRTCStatusService:
    """DeviceRTCStatus 서비스 의존성 주입"""
    return container.get_device_rtc_service(db)


@router.post("/", response_model=DeviceRTCDataResponse, status_code=201)
async def create_device_rtc_status(
    data: DeviceRTCDataCreate,
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """디바이스 RTC 상태 데이터 생성"""
    return await rtc_service.create_rtc_status(data)


@router.get("/", response_model=List[DeviceRTCDataResponse])
async def get_device_rtc_status_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit_count: int = Query(100, description="조회할 데이터 개수", ge=1, le=1000),
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """디바이스 RTC 상태 데이터 목록 조회"""
    return await rtc_service.get_rtc_status_list(
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit_count
    )


@router.get("/latest", response_model=Optional[DeviceRTCDataResponse])
async def get_latest_device_rtc_status(
    device_id: str = Query(..., description="디바이스 ID"),
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """특정 디바이스의 최신 RTC 상태 데이터 조회"""
    return await rtc_service.get_latest_rtc_status(device_id)


@router.get("/{device_id}/{timestamp}", response_model=DeviceRTCDataResponse)
async def get_device_rtc_status(
    device_id: str,
    timestamp: datetime,
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """특정 시간의 디바이스 RTC 상태 데이터 조회"""
    return await rtc_service.get_rtc_status(device_id, timestamp)


@router.put("/{device_id}/{timestamp}", response_model=DeviceRTCDataResponse)
async def update_device_rtc_status(
    device_id: str,
    timestamp: datetime,
    data: DeviceRTCDataUpdate,
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """디바이스 RTC 상태 데이터 수정"""
    return await rtc_service.update_rtc_status(device_id, timestamp, data)


@router.delete("/{device_id}/{timestamp}")
async def delete_device_rtc_status(
    device_id: str,
    timestamp: datetime,
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """디바이스 RTC 상태 데이터 삭제"""
    success = await rtc_service.delete_rtc_status(device_id, timestamp)
    if success:
        return {"message": "RTC 상태 데이터가 성공적으로 삭제되었습니다"}
    return {"message": "RTC 상태 데이터 삭제 실패"}


@router.get("/{device_id}/stats/sync", response_model=dict)
async def get_device_rtc_sync_statistics(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """디바이스 RTC 동기화 통계 정보 조회"""
    return await rtc_service.get_sync_statistics(device_id, start_time, end_time)


@router.get("/{device_id}/stats/drift", response_model=dict)
async def get_device_rtc_drift_analysis(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """디바이스 RTC 시간 드리프트 분석 정보 조회"""
    return await rtc_service.get_drift_analysis(device_id, start_time, end_time)


@router.get("/{device_id}/health", response_model=dict)
async def get_device_rtc_health(
    device_id: str,
    rtc_service: IDeviceRTCStatusService = Depends(get_device_rtc_service)
):
    """디바이스 RTC 시간 동기화 상태 건강도 조회"""
    return await rtc_service.get_time_sync_health(device_id) 