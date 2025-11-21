"""
Ultrasonic 초음파 센서 데이터 API

Clean Architecture 원칙에 따라 Ultrasonic 초음파 센서의 원시 데이터를 관리하는 API 엔드포인트를 제공합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.core.container import container
from app.interfaces.services.sensor_service_interface import IUltrasonicService
from app.api.v1.schemas import (
    SensorRawUltrasonicCreate,
    SensorRawUltrasonicUpdate,
    SensorRawUltrasonicResponse
)

router = APIRouter()


def get_ultrasonic_service(db: AsyncSession = Depends(get_db)) -> IUltrasonicService:
    """Ultrasonic 초음파 센서 서비스 의존성 주입"""
    return container.get_ultrasonic_service(db)


@router.post("/create", response_model=SensorRawUltrasonicResponse, status_code=201)
async def create_ultrasonic_data(
    data: SensorRawUltrasonicCreate,
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """
    Ultrasonic 초음파 센서 데이터 생성
    
    - **time**: 거리 측정 시간 (ISO 8601 형식)
    - **device_id**: 초음파 센서 디바이스 ID (필수)
    - **raw_payload**: 원시 거리 데이터 (JSON 형태, 선택)
    
    Ultrasonic 센서는 거리 측정, 물체 감지, 자동차 주차 보조 등에 사용됩니다.
    
    예시:
    ```json
    {
        "time": "2025-08-23T15:00:00.000Z",
        "device_id": "ultrasonic_sensor_001",
        "raw_payload": {"distance_cm": 25.5, "signal_strength": 0.9, "echo_time": 0.15}
    }
    ```
    """
    return await ultrasonic_service.create_sensor_data(data)


@router.get("/list", response_model=List[SensorRawUltrasonicResponse])
async def get_ultrasonic_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit_count: int = Query(100, description="조회할 데이터 개수", ge=1, le=1000),
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """Ultrasonic 초음파 센서 데이터 목록 조회"""
    return await ultrasonic_service.get_sensor_data_list(
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit_count
    )


@router.get("/latest", response_model=Optional[SensorRawUltrasonicResponse])
async def get_latest_ultrasonic_data(
    device_id: str = Query(..., description="디바이스 ID"),
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """특정 디바이스의 최신 Ultrasonic 초음파 센서 데이터 조회"""
    return await ultrasonic_service.get_latest_sensor_data(device_id)


@router.get("/{device_id}/{timestamp}", response_model=SensorRawUltrasonicResponse)
async def get_ultrasonic_data(
    device_id: str,
    timestamp: datetime,
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """특정 시간의 Ultrasonic 초음파 센서 데이터 조회"""
    return await ultrasonic_service.get_sensor_data(device_id, timestamp)


@router.put("/{device_id}/{timestamp}", response_model=SensorRawUltrasonicResponse)
async def update_ultrasonic_data(
    device_id: str,
    timestamp: datetime,
    data: SensorRawUltrasonicUpdate,
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """Ultrasonic 초음파 센서 데이터 수정"""
    return await ultrasonic_service.update_sensor_data(device_id, timestamp, data)


@router.delete("/{device_id}/{timestamp}")
async def delete_ultrasonic_data(
    device_id: str,
    timestamp: datetime,
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """Ultrasonic 초음파 센서 데이터 삭제"""
    success = await ultrasonic_service.delete_sensor_data(device_id, timestamp)
    if success:
        return {"message": "데이터가 성공적으로 삭제되었습니다"}
    return {"message": "데이터 삭제 실패"}


@router.get("/{device_id}/stats/distance", response_model=dict)
async def get_ultrasonic_distance_stats(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """Ultrasonic 초음파 센서의 거리 측정 통계 정보 조회"""
    return await ultrasonic_service.get_distance_statistics(device_id, start_time, end_time)


@router.get("/{device_id}/analysis/distance-trends", response_model=dict)
async def analyze_ultrasonic_distance_trends(
    device_id: str,
    analysis_window: int = Query(3600, description="분석 윈도우 (초)"),
    ultrasonic_service: IUltrasonicService = Depends(get_ultrasonic_service)
):
    """Ultrasonic 초음파 센서의 거리 트렌드 분석"""
    return await ultrasonic_service.analyze_distance_trends(device_id, analysis_window)
