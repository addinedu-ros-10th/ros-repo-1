"""
Edge Flame 센서 데이터 API

화재 감지 센서의 Edge 처리된 데이터를 관리하는 API 엔드포인트입니다.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import container
from app.infrastructure.database import get_db_session
from app.interfaces.services.sensor_service_interface import IEdgeFlameService
from app.api.v1.schemas import (
    EdgeFlameDataCreate,
    EdgeFlameDataUpdate,
    EdgeFlameDataResponse
)

router = APIRouter(tags=["Edge Flame 센서"])


def get_edge_flame_service(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeFlameService:
    """Edge Flame 서비스 의존성 주입"""
    return container.get_edge_flame_service(db_session)


@router.post("/create", response_model=EdgeFlameDataResponse, status_code=201)
async def create_edge_flame_data(
    data: EdgeFlameDataCreate,
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """Edge Flame 센서 데이터 생성"""
    try:
        return await edge_flame_service.create_sensor_data(data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[EdgeFlameDataResponse])
async def get_edge_flame_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, ge=1, le=1000, description="조회 제한"),
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """Edge Flame 센서 데이터 목록 조회"""
    try:
        return await edge_flame_service.get_sensor_data_list(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest/{device_id}", response_model=EdgeFlameDataResponse)
async def get_latest_edge_flame_data(
    device_id: str,
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """최신 Edge Flame 센서 데이터 조회"""
    try:
        data = await edge_flame_service.get_latest_sensor_data(device_id)
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"디바이스 {device_id}의 Edge Flame 센서 데이터를 찾을 수 없습니다."
            )
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/{timestamp}", response_model=EdgeFlameDataResponse)
async def get_edge_flame_data(
    device_id: str,
    timestamp: datetime,
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """특정 시간의 Edge Flame 센서 데이터 조회"""
    try:
        data = await edge_flame_service.get_sensor_data(device_id, timestamp)
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"해당 시간의 Edge Flame 센서 데이터를 찾을 수 없습니다."
            )
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{device_id}/{timestamp}", response_model=EdgeFlameDataResponse)
async def update_edge_flame_data(
    device_id: str,
    timestamp: datetime,
    data: EdgeFlameDataUpdate,
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """Edge Flame 센서 데이터 수정"""
    try:
        return await edge_flame_service.update_sensor_data(device_id, timestamp, data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{device_id}/{timestamp}")
async def delete_edge_flame_data(
    device_id: str,
    timestamp: datetime,
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """Edge Flame 센서 데이터 삭제"""
    try:
        await edge_flame_service.delete_sensor_data(device_id, timestamp)
        return JSONResponse(
            status_code=200,
            content={"message": "Edge Flame 센서 데이터가 성공적으로 삭제되었습니다."}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/statistics")
async def get_edge_flame_statistics(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """Edge Flame 센서 데이터 통계 조회"""
    try:
        return await edge_flame_service.get_sensor_statistics(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/alerts/flame-detection")
async def get_edge_flame_detection_alerts(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    edge_flame_service: IEdgeFlameService = Depends(get_edge_flame_service)
):
    """화재 감지 알림 조회"""
    try:
        return await edge_flame_service.get_flame_detection_alerts(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
