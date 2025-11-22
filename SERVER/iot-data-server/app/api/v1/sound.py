"""
Sound 센서 데이터 API

Clean Architecture 원칙에 따라 Sound 센서의 원시 데이터를 관리하는 API 엔드포인트를 제공합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.core.container import container
from app.interfaces.services.sensor_service_interface import ISoundService
from app.api.v1.schemas import (
    SensorRawSoundCreate,
    SensorRawSoundUpdate,
    SensorRawSoundResponse
)

router = APIRouter()


def get_sound_service(db: AsyncSession = Depends(get_db)) -> ISoundService:
    """Sound 센서 서비스 의존성 주입"""
    return container.get_sound_service(db)


@router.post("/create", response_model=SensorRawSoundResponse, status_code=201)
async def create_sound_data(
    data: SensorRawSoundCreate,
    sound_service: ISoundService = Depends(get_sound_service)
):
    """
    Sound 센서 데이터 생성
    
    - **time**: 소리 감지 시간 (ISO 8601 형식)
    - **device_id**: 소리 센서 디바이스 ID (필수)
    - **raw_payload**: 원시 소리 데이터 (JSON 형태, 선택)
    
    Sound 센서는 소음 모니터링, 보안 감시, 환경 모니터링 등에 사용됩니다.
    
    예시:
    ```json
    {
        "time": "2025-08-23T15:00:00.000Z",
        "device_id": "sound_sensor_001",
        "raw_payload": {"decibel": 65.5, "frequency": 440, "duration": 2.5}
    }
    ```
    """
    return await sound_service.create_sensor_data(data)


@router.get("/list", response_model=List[SensorRawSoundResponse])
async def get_sound_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit_count: int = Query(100, description="조회할 데이터 개수", ge=1, le=1000),
    sound_service: ISoundService = Depends(get_sound_service)
):
    """Sound 센서 데이터 목록 조회"""
    return await sound_service.get_sensor_data_list(
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        limit=limit_count
    )


@router.get("/latest", response_model=Optional[SensorRawSoundResponse])
async def get_latest_sound_data(
    device_id: str = Query(..., description="디바이스 ID"),
    sound_service: ISoundService = Depends(get_sound_service)
):
    """특정 디바이스의 최신 Sound 센서 데이터 조회"""
    return await sound_service.get_latest_sensor_data(device_id)


@router.get("/{device_id}/{timestamp}", response_model=SensorRawSoundResponse)
async def get_sound_data(
    device_id: str,
    timestamp: datetime,
    sound_service: ISoundService = Depends(get_sound_service)
):
    """특정 시간의 Sound 센서 데이터 조회"""
    return await sound_service.get_sensor_data(device_id, timestamp)


@router.put("/{device_id}/{timestamp}", response_model=SensorRawSoundResponse)
async def update_sound_data(
    device_id: str,
    timestamp: datetime,
    data: SensorRawSoundUpdate,
    sound_service: ISoundService = Depends(get_sound_service)
):
    """Sound 센서 데이터 수정"""
    return await sound_service.update_sensor_data(device_id, timestamp, data)


@router.delete("/{device_id}/{timestamp}")
async def delete_sound_data(
    device_id: str,
    timestamp: datetime,
    sound_service: ISoundService = Depends(get_sound_service)
):
    """Sound 센서 데이터 삭제"""
    success = await sound_service.delete_sensor_data(device_id, timestamp)
    if success:
        return {"message": "데이터가 성공적으로 삭제되었습니다"}
    return {"message": "데이터 삭제 실패"}


@router.get("/{device_id}/stats/audio", response_model=dict)
async def get_sound_audio_stats(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    sound_service: ISoundService = Depends(get_sound_service)
):
    """Sound 센서의 오디오 통계 정보 조회"""
    return await sound_service.get_audio_statistics(device_id, start_time, end_time)


@router.get("/{device_id}/alerts/noise", response_model=dict)
async def get_sound_noise_alerts(
    device_id: str,
    threshold_db: float = Query(80.0, description="소음 임계값 (dB)"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    sound_service: ISoundService = Depends(get_sound_service)
):
    """Sound 센서의 소음 알림 조회"""
    return await sound_service.get_noise_alerts(device_id, threshold_db, start_time, end_time)
