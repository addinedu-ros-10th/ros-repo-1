"""
TCRT5000 근접 센서 데이터 API

Clean Architecture 원칙에 따라 TCRT5000 근접 센서의 원시 데이터를 관리하는 API 엔드포인트를 제공합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.core.container import container
from app.interfaces.services.sensor_service_interface import ITCRT5000Service
from app.api.v1.schemas import (
    SensorRawTCRT5000Create,
    SensorRawTCRT5000Update,
    SensorRawTCRT5000Response
)

router = APIRouter()


def get_tcrt5000_service(db: AsyncSession = Depends(get_db)) -> ITCRT5000Service:
    """TCRT5000 근접 센서 서비스 의존성 주입"""
    return container.get_tcrt5000_service(db)


@router.post("/create", response_model=SensorRawTCRT5000Response, status_code=201)
async def create_tcrt5000_data(
    data: SensorRawTCRT5000Create,
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """
    TCRT5000 근접 센서 데이터 생성
    
    - **time**: 근접 감지 시간 (ISO 8601 형식)
    - **device_id**: 근접 센서 디바이스 ID (필수)
    - **raw_payload**: 원시 근접 데이터 (JSON 형태, 선택)
    
    TCRT5000은 적외선 근접 센서로, 물체 감지, 자동문, 로봇 등에 사용됩니다.
    
    예시:
    ```json
    {
        "time": "2025-08-23T15:00:00.000Z",
        "device_id": "proximity_sensor_001",
        "raw_payload": {"detected": true, "distance": 15, "reflection": 0.8}
    }
    ```
    """
    return await tcrt5000_service.create_sensor_data(data)


@router.get("/list", response_model=List[SensorRawTCRT5000Response])
async def get_tcrt5000_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit_count: int = Query(100, description="조회할 데이터 개수", ge=1, le=1000),
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """TCRT5000 근접 센서 데이터 목록 조회"""
    return await tcrt5000_service.get_sensor_data_list(
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit_count
    )


@router.get("/latest", response_model=Optional[SensorRawTCRT5000Response])
async def get_latest_tcrt5000_data(
    device_id: str = Query(..., description="디바이스 ID"),
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """특정 디바이스의 최신 TCRT5000 근접 센서 데이터 조회"""
    return await tcrt5000_service.get_latest_sensor_data(device_id)


@router.get("/{device_id}/{timestamp}", response_model=SensorRawTCRT5000Response)
async def get_tcrt5000_data(
    device_id: str,
    timestamp: datetime,
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """특정 시간의 TCRT5000 근접 센서 데이터 조회"""
    return await tcrt5000_service.get_sensor_data(device_id, timestamp)


@router.put("/{device_id}/{timestamp}", response_model=SensorRawTCRT5000Response)
async def update_tcrt5000_data(
    device_id: str,
    timestamp: datetime,
    data: SensorRawTCRT5000Update,
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """TCRT5000 근접 센서 데이터 수정"""
    return await tcrt5000_service.update_sensor_data(device_id, timestamp, data)


@router.delete("/{device_id}/{timestamp}")
async def delete_tcrt5000_data(
    device_id: str,
    timestamp: datetime,
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """TCRT5000 근접 센서 데이터 삭제"""
    success = await tcrt5000_service.delete_sensor_data(device_id, timestamp)
    if success:
        return {"message": "데이터가 성공적으로 삭제되었습니다"}
    return {"message": "데이터 삭제 실패"}


@router.get("/{device_id}/stats/proximity", response_model=dict)
async def get_tcrt5000_proximity_stats(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """TCRT5000 근접 센서의 근접 감지 통계 정보 조회"""
    return await tcrt5000_service.get_proximity_statistics(device_id, start_time, end_time)


@router.get("/{device_id}/analysis/motion-patterns", response_model=dict)
async def analyze_tcrt5000_motion_patterns(
    device_id: str,
    analysis_window: int = Query(3600, description="분석 윈도우 (초)"),
    tcrt5000_service: ITCRT5000Service = Depends(get_tcrt5000_service)
):
    """TCRT5000 근접 센서의 움직임 패턴 분석"""
    return await tcrt5000_service.analyze_motion_patterns(device_id, analysis_window)
