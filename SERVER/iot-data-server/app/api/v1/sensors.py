"""
센서 API 엔드포인트

센서 데이터 수집, 조회 및 모니터링을 위한 REST API를 제공합니다.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    SensorDataResponse, SuccessResponse, PaginationParams
)
from app.core.container import container
from app.infrastructure.database import get_db_session
from app.interfaces.repositories.device_repository import IDeviceRepository

router = APIRouter()


def get_device_repository(db_session: AsyncSession = Depends(get_db_session)) -> IDeviceRepository:
    """디바이스 리포지토리 의존성 주입"""
    return container.get_device_repository(db_session)


@router.get("/", response_model=List[SensorDataResponse])
async def get_sensor_data(
    device_id: Optional[str] = Query(None, description="디바이스 ID 필터링"),
    sensor_type: Optional[str] = Query(None, description="센서 타입 필터링"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 데이터 개수"),
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    센서 데이터 조회
    
    - **device_id**: 특정 디바이스의 데이터만 조회 (선택)
    - **sensor_type**: 센서 타입별 필터링 (선택)
    - **start_time**: 시작 시간 (선택)
    - **end_time**: 종료 시간 (선택)
    - **limit**: 조회할 데이터 개수 (기본값: 100, 최대: 1000)
    """
    try:
        # 디바이스 ID가 제공된 경우 디바이스 존재 여부 확인
        if device_id:
            device = await device_repository.get_by_id(device_id)
            if not device:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="지정된 디바이스를 찾을 수 없습니다"
                )
        
        # 기본 시간 범위 설정 (24시간)
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        # 센서 데이터 조회 (향후 실제 구현)
        # 실제로는 센서 데이터 리포지토리를 통해 조회
        sensor_data = []
        
        # 임시 데이터 생성 (테스트용)
        if device_id:
            # 특정 디바이스의 센서 데이터 시뮬레이션
            for i in range(min(limit, 10)):
                timestamp = start_time + timedelta(minutes=i * 15)
                if timestamp <= end_time:
                    sensor_data.append({
                        "id": i + 1,
                        "device_id": device_id,
                        "timestamp": timestamp,
                        "value": 20.0 + (i % 10),  # 온도 시뮬레이션
                        "unit": "°C"
                    })
        
        return [
            SensorDataResponse(
                id=data["id"],
                device_id=data["device_id"],
                timestamp=data["timestamp"],
                value=data["value"],
                unit=data["unit"]
            )
            for data in sensor_data
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"센서 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{device_id}/latest", response_model=SensorDataResponse)
async def get_latest_sensor_data(
    device_id: str,
    sensor_type: Optional[str] = Query(None, description="센서 타입"),
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    특정 디바이스의 최신 센서 데이터 조회
    
    - **device_id**: 디바이스 ID
    - **sensor_type**: 센서 타입 (선택)
    """
    try:
        # 디바이스 존재 여부 확인
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 최신 센서 데이터 조회 (향후 실제 구현)
        # 실제로는 센서 데이터 리포지토리를 통해 조회
        latest_data = {
            "id": 1,
            "device_id": device_id,
            "timestamp": datetime.utcnow(),
            "value": 22.5,  # 임시 데이터
            "unit": "°C"
        }
        
        return SensorDataResponse(**latest_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"최신 센서 데이터 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{device_id}/history", response_model=List[SensorDataResponse])
async def get_sensor_history(
    device_id: str,
    hours: int = Query(24, ge=1, le=168, description="조회할 시간 범위 (시간)"),
    sensor_type: Optional[str] = Query(None, description="센서 타입"),
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    특정 디바이스의 센서 데이터 히스토리 조회
    
    - **device_id**: 디바이스 ID
    - **hours**: 조회할 시간 범위 (1-168시간, 기본값: 24시간)
    - **sensor_type**: 센서 타입 (선택)
    """
    try:
        # 디바이스 존재 여부 확인
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 시간 범위 계산
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # 센서 히스토리 데이터 조회 (향후 실제 구현)
        # 실제로는 센서 데이터 리포지토리를 통해 조회
        history_data = []
        
        # 임시 히스토리 데이터 생성 (테스트용)
        for i in range(min(hours, 24)):  # 최대 24개 데이터 포인트
            timestamp = start_time + timedelta(hours=i)
            if timestamp <= end_time:
                history_data.append({
                    "id": i + 1,
                    "device_id": device_id,
                    "timestamp": timestamp,
                    "value": 20.0 + (i % 5),  # 온도 변화 시뮬레이션
                    "unit": "°C"
                })
        
        return [
            SensorDataResponse(
                id=data["id"],
                device_id=data["id"],
                timestamp=data["timestamp"],
                value=data["value"],
                unit=data["unit"]
            )
            for data in history_data
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"센서 히스토리 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{device_id}/alerts")
async def get_device_alerts(
    device_id: str,
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    특정 디바이스의 알림 조회
    
    - **device_id**: 디바이스 ID
    """
    try:
        # 디바이스 존재 여부 확인
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 디바이스 알림 조회 (향후 실제 구현)
        # 실제로는 알림 리포지토리를 통해 조회
        alerts = [
            {
                "id": 1,
                "device_id": device_id,
                "type": "temperature_high",
                "message": "온도가 임계값을 초과했습니다",
                "severity": "warning",
                "timestamp": datetime.utcnow() - timedelta(minutes=30),
                "resolved": False
            }
        ]
        
        return SuccessResponse(
            message="디바이스 알림 조회 성공",
            data={
                "device_id": device_id,
                "alerts": alerts,
                "total": len(alerts)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 알림 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/types")
async def get_sensor_types():
    """
    지원하는 센서 타입 목록 조회
    """
    try:
        sensor_types = [
            {
                "type": "temperature",
                "name": "온도 센서",
                "unit": "°C",
                "description": "환경 온도 측정"
            },
            {
                "type": "humidity",
                "name": "습도 센서",
                "unit": "%",
                "description": "환경 습도 측정"
            },
            {
                "type": "motion",
                "name": "동작 감지 센서",
                "unit": "boolean",
                "description": "움직임 감지"
            },
            {
                "type": "light",
                "name": "조도 센서",
                "unit": "lux",
                "description": "주변 밝기 측정"
            },
            {
                "type": "gas",
                "name": "가스 센서",
                "unit": "ppm",
                "description": "유해 가스 농도 측정"
            }
        ]
        
        return SuccessResponse(
            message="센서 타입 목록 조회 성공",
            data={
                "sensor_types": sensor_types,
                "total": len(sensor_types)
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"센서 타입 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/stats/overview")
async def get_sensor_stats_overview():
    """
    센서 데이터 통계 개요 조회
    """
    try:
        # 센서 통계 데이터 (향후 실제 구현)
        # 실제로는 통계 서비스를 통해 조회
        stats = {
            "total_devices": 25,
            "active_devices": 23,
            "total_sensors": 150,
            "data_points_today": 8640,
            "alerts_today": 3,
            "avg_temperature": 22.5,
            "avg_humidity": 45.2
        }
        
        return SuccessResponse(
            message="센서 통계 개요 조회 성공",
            data=stats
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"센서 통계 개요 조회 중 오류가 발생했습니다: {str(e)}"
        ) 