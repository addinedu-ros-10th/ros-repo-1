"""
LoadCell 센서 데이터 API

Clean Architecture 원칙에 따라 로드셀 센서의 원시 데이터를 관리하는 API 엔드포인트를 제공합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db_session
from app.core.container import container
from app.interfaces.services.sensor_service_interface import ILoadCellService
from app.api.v1.schemas import (
    SensorRawLoadCellCreate,
    SensorRawLoadCellUpdate,
    SensorRawLoadCellResponse
)

router = APIRouter()


def get_loadcell_service(db: AsyncSession = Depends(get_db_session)) -> ILoadCellService:
    """LoadCell 센서 서비스 의존성 주입"""
    return container.get_loadcell_service(db)


@router.post("/create", response_model=SensorRawLoadCellResponse, status_code=201)
async def create_loadcell_data(
    data: SensorRawLoadCellCreate,
    loadcell_service: ILoadCellService = Depends(get_loadcell_service)
):
    """
    로드셀 센서 데이터 생성
    
    - **time**: 무게 측정 시간 (ISO 8601 형식)
    - **device_id**: 로드셀 센서 디바이스 ID (필수)
    - **raw_payload**: 원시 무게 데이터 (JSON 형태, 선택)
    
    로드셀은 무게 측정, 계량, 압력 감지 등에 사용됩니다.
    
    예시:
    ```json
    {
        "time": "2025-08-23T15:00:00.000Z",
        "device_id": "loadcell_sensor_001",
        "raw_payload": {"weight_kg": 2.5, "calibration_factor": 1.02, "temperature": 22.0}
    }
    ```
    """
    return await loadcell_service.create_sensor_data(data)


@router.get("/list", response_model=List[SensorRawLoadCellResponse])
async def get_loadcell_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit_count: int = Query(100, description="조회할 데이터 개수", ge=1, le=1000),
    loadcell_service: ILoadCellService = Depends(get_loadcell_service)
):
    """로드셀 센서 데이터 목록 조회"""
    return await loadcell_service.get_sensor_data_list(
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit_count
    )


@router.get("/latest", response_model=Optional[SensorRawLoadCellResponse])
async def get_latest_loadcell_data(
    device_id: str = Query(..., description="디바이스 ID"),
    loadcell_service: ILoadCellService = Depends(get_loadcell_service)
):
    """특정 디바이스의 최신 로드셀 센서 데이터 조회"""
    return await loadcell_service.get_latest_sensor_data(device_id)


@router.get("/{device_id}/{timestamp}", response_model=SensorRawLoadCellResponse)
async def get_loadcell_data(
    device_id: str,
    timestamp: datetime,
    loadcell_service: ILoadCellService = Depends(get_loadcell_service)
):
    """특정 시간의 로드셀 센서 데이터 조회"""
    return await loadcell_service.get_sensor_data(device_id, timestamp)


@router.put("/{device_id}/{timestamp}", response_model=SensorRawLoadCellResponse)
async def update_loadcell_data(
    device_id: str,
    timestamp: datetime,
    data: SensorRawLoadCellUpdate,
    loadcell_service: ILoadCellService = Depends(get_loadcell_service)
):
    """로드셀 센서 데이터 수정"""
    return await loadcell_service.update_sensor_data(device_id, timestamp, data)


@router.delete("/{device_id}/{timestamp}")
async def delete_loadcell_data(
    device_id: str,
    timestamp: datetime,
    loadcell_service: ILoadCellService = Depends(get_loadcell_service)
):
    """로드셀 센서 데이터 삭제"""
    success = await loadcell_service.delete_sensor_data(device_id, timestamp)
    if success:
        return {"message": "데이터가 성공적으로 삭제되었습니다"}
    return {"message": "데이터 삭제 실패"}


@router.get("/{device_id}/stats/weight", response_model=dict)
async def get_loadcell_weight_stats(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    loadcell_service: ILoadCellService = Depends(get_loadcell_service)
):
    """로드셀 센서의 무게 통계 정보 조회"""
    return await loadcell_service.get_weight_statistics(device_id, start_time, end_time)
