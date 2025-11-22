"""
RFID 센서 데이터 API

Clean Architecture 원칙에 따라 RFID 센서의 원시 데이터를 관리하는 API 엔드포인트를 제공합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.core.container import container
from app.interfaces.services.sensor_service_interface import IRFIDService
from app.api.v1.schemas import (
    SensorRawRFIDCreate,
    SensorRawRFIDUpdate,
    SensorRawRFIDResponse
)

router = APIRouter()


def get_rfid_service(db: AsyncSession = Depends(get_db)) -> IRFIDService:
    """RFID 센서 서비스 의존성 주입"""
    return container.get_rfid_service(db)


@router.post("/create", response_model=SensorRawRFIDResponse, status_code=201)
async def create_rfid_data(
    data: SensorRawRFIDCreate,
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """
    RFID 센서 데이터 생성
    
    - **time**: RFID 카드 인식 시간 (ISO 8601 형식)
    - **device_id**: RFID 리더 디바이스 ID (필수)
    - **raw_payload**: 원시 RFID 데이터 (JSON 형태, 선택)
    
    RFID 센서는 접근 제어, 출입 관리, 자산 추적 등에 사용됩니다.
    
    예시:
    ```json
    {
        "time": "2025-08-23T15:00:00.000Z",
        "device_id": "rfid_reader_001",
        "raw_payload": {"card_id": "1234567890", "reader_location": "main_entrance"}
    }
    ```
    """
    return await rfid_service.create_sensor_data(data)


@router.get("/list", response_model=List[SensorRawRFIDUpdate])
async def get_rfid_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit_count: int = Query(100, description="조회할 데이터 개수", ge=1, le=1000),
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """RFID 센서 데이터 목록 조회"""
    return await rfid_service.get_sensor_data_list(
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit_count
    )


@router.get("/latest", response_model=Optional[SensorRawRFIDUpdate])
async def get_latest_rfid_data(
    device_id: str = Query(..., description="디바이스 ID"),
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """특정 디바이스의 최신 RFID 센서 데이터 조회"""
    return await rfid_service.get_latest_sensor_data(device_id)


@router.get("/{device_id}/{timestamp}", response_model=SensorRawRFIDResponse)
async def get_rfid_data(
    device_id: str,
    timestamp: datetime,
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """특정 시간의 RFID 센서 데이터 조회"""
    return await rfid_service.get_sensor_data(device_id, timestamp)


@router.put("/{device_id}/{timestamp}", response_model=SensorRawRFIDResponse)
async def update_rfid_data(
    device_id: str,
    timestamp: datetime,
    data: SensorRawRFIDResponse,
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """RFID 센서 데이터 수정"""
    return await rfid_service.update_sensor_data(device_id, timestamp, data)


@router.delete("/{device_id}/{timestamp}")
async def delete_rfid_data(
    device_id: str,
    timestamp: datetime,
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """RFID 센서 데이터 삭제"""
    success = await rfid_service.delete_sensor_data(device_id, timestamp)
    if success:
        return {"message": "데이터가 성공적으로 삭제되었습니다"}
    return {"message": "데이터 삭제 실패"}


@router.get("/{device_id}/stats/cards", response_model=dict)
async def get_rfid_card_stats(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """RFID 센서의 카드 통계 정보 조회"""
    return await rfid_service.get_card_statistics(device_id, start_time, end_time)


@router.get("/{device_id}/history", response_model=dict)
async def get_rfid_read_history(
    device_id: str,
    card_id: Optional[str] = Query(None, description="카드 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    rfid_service: IRFIDService = Depends(get_rfid_service)
):
    """RFID 센서의 읽기 이력 조회"""
    return await rfid_service.get_read_history(device_id, card_id, start_time, end_time)
