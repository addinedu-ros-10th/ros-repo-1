"""
Edge Reed 센서 데이터 API

Reed 스위치 센서의 Edge 처리된 데이터를 관리하는 API 엔드포인트입니다.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import container
from app.infrastructure.database import get_db_session
from app.interfaces.services.sensor_service_interface import IEdgeReedService
from app.api.v1.schemas import (
    EdgeReedDataCreate,
    EdgeReedDataUpdate,
    EdgeReedDataResponse
)

router = APIRouter(tags=["Edge Reed 센서"])


def get_edge_reed_service(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeReedService:
    """Edge Reed 서비스 의존성 주입"""
    return container.get_edge_reed_service(db_session)


@router.post("/create", response_model=EdgeReedDataResponse, status_code=201)
async def create_edge_reed_data(
    data: EdgeReedDataCreate,
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """Edge Reed 센서 데이터 생성"""
    try:
        return await edge_reed_service.create_sensor_data(data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=List[EdgeReedDataResponse])
async def get_edge_reed_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, ge=1, le=1000, description="조회 제한"),
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """Edge Reed 센서 데이터 목록 조회"""
    try:
        return await edge_reed_service.get_sensor_data_list(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/latest/{device_id}", response_model=EdgeReedDataResponse)
async def get_latest_edge_reed_data(
    device_id: str,
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """최신 Edge Reed 센서 데이터 조회"""
    try:
        data = await edge_reed_service.get_latest_sensor_data(device_id)
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"디바이스 {device_id}의 Edge Reed 센서 데이터를 찾을 수 없습니다."
            )
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/{timestamp}", response_model=EdgeReedDataResponse)
async def get_edge_reed_data(
    device_id: str,
    timestamp: datetime,
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """특정 시간의 Edge Reed 센서 데이터 조회"""
    try:
        data = await edge_reed_service.get_sensor_data(device_id, timestamp)
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"해당 시간의 Edge Reed 센서 데이터를 찾을 수 없습니다."
            )
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{device_id}/{timestamp}", response_model=EdgeReedDataResponse)
async def update_edge_reed_data(
    device_id: str,
    timestamp: datetime,
    data: EdgeReedDataUpdate,
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """Edge Reed 센서 데이터 수정"""
    try:
        return await edge_reed_service.update_sensor_data(device_id, timestamp, data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{device_id}/{timestamp}")
async def delete_edge_reed_data(
    device_id: str,
    timestamp: datetime,
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """Edge Reed 센서 데이터 삭제"""
    try:
        await edge_reed_service.delete_sensor_data(device_id, timestamp)
        return JSONResponse(
            status_code=200,
            content={"message": "Edge Reed 센서 데이터가 성공적으로 삭제되었습니다."}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/statistics")
async def get_edge_reed_statistics(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """Edge Reed 센서 데이터 통계 조회"""
    try:
        return await edge_reed_service.get_sensor_statistics(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{device_id}/history/activations")
async def get_edge_reed_switch_activation_history(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    edge_reed_service: IEdgeReedService = Depends(get_edge_reed_service)
):
    """스위치 활성화 이력 조회"""
    try:
        return await edge_reed_service.get_switch_activation_history(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
