"""
Relay 액추에이터 로그 API

Relay 액추에이터 로그 데이터에 대한 RESTful API 엔드포인트를 제공합니다.
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.container import get_actuator_relay_service
from app.interfaces.services.actuator_service_interface import IActuatorRelayService
from app.api.v1.schemas import (
    ActuatorRelayDataCreate, ActuatorRelayDataUpdate, ActuatorRelayDataResponse
)

router = APIRouter(tags=["actuator-relay"])


@router.post("/create", response_model=ActuatorRelayDataResponse, status_code=201)
async def create_actuator_relay_data(
    data: ActuatorRelayDataCreate,
    service: IActuatorRelayService = Depends(get_actuator_relay_service)
) -> ActuatorRelayDataResponse:
    """Relay 액추에이터 로그 생성"""
    return await service.create_actuator_data(data)


@router.get("/list", response_model=List[ActuatorRelayDataResponse])
async def get_actuator_relay_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    channel: Optional[int] = Query(None, description="채널"),
    state: Optional[str] = Query(None, description="상태"),
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    service: IActuatorRelayService = Depends(get_actuator_relay_service)
) -> List[ActuatorRelayDataResponse]:
    """Relay 액추에이터 로그 목록 조회"""
    return await service.get_actuator_data_list(
        device_id=device_id,
        start_time=start_time,
        end_time=end_time,
        channel=channel,
        state=state,
        limit=limit,
        offset=offset
    )


@router.get("/latest/{device_id}", response_model=ActuatorRelayDataResponse)
async def get_latest_actuator_relay_data(
    device_id: str,
    service: IActuatorRelayService = Depends(get_actuator_relay_service)
) -> ActuatorRelayDataResponse:
    """최신 Relay 액추에이터 로그 조회"""
    data = await service.get_latest_actuator_data(device_id)
    if not data:
        raise HTTPException(status_code=404, detail="액추에이터 로그를 찾을 수 없습니다")
    return data


@router.get("/{device_id}/{timestamp}", response_model=ActuatorRelayDataResponse)
async def get_actuator_relay_data(
    device_id: str,
    timestamp: datetime,
    service: IActuatorRelayService = Depends(get_actuator_relay_service)
) -> ActuatorRelayDataResponse:
    """Relay 액추에이터 로그 조회"""
    data = await service.get_actuator_data(device_id, timestamp)
    if not data:
        raise HTTPException(status_code=404, detail="액추에이터 로그를 찾을 수 없습니다")
    return data


@router.put("/{device_id}/{timestamp}", response_model=ActuatorRelayDataResponse)
async def update_actuator_relay_data(
    device_id: str,
    timestamp: datetime,
    data: ActuatorRelayDataUpdate,
    service: IActuatorRelayService = Depends(get_actuator_relay_service)
) -> ActuatorRelayDataResponse:
    """Relay 액추에이터 로그 수정"""
    return await service.update_actuator_data(device_id, timestamp, data)


@router.delete("/{device_id}/{timestamp}", status_code=204)
async def delete_actuator_relay_data(
    device_id: str,
    timestamp: datetime,
    service: IActuatorRelayService = Depends(get_actuator_relay_service)
) -> None:
    """Relay 액추에이터 로그 삭제"""
    await service.delete_actuator_data(device_id, timestamp)


@router.get("/{device_id}/statistics")
async def get_actuator_relay_statistics(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    service: IActuatorRelayService = Depends(get_actuator_relay_service)
) -> dict:
    """Relay 액추에이터 로그 통계 조회"""
    
    return await service.get_actuator_statistics(device_id, start_time, end_time)
