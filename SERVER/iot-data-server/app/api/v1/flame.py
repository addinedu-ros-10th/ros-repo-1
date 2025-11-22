"""
Flame (화재 감지 센서) API 엔드포인트

Flame 센서 데이터의 CRUD 작업을 처리합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database import get_db_session
from app.infrastructure.models import SensorRawFlame
from app.api.v1.schemas import FlameDataCreate, FlameDataResponse, FlameDataUpdate

router = APIRouter(tags=["Flame Sensor"])


@router.post("/", response_model=FlameDataResponse, status_code=201)
async def create_flame_data(
    flame_data: FlameDataCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Flame 센서 데이터 생성"""
    try:
        db_flame = SensorRawFlame(
            time=flame_data.time,
            device_id=flame_data.device_id,
            analog_value=flame_data.analog_value,
            flame_detected=flame_data.flame_detected,
            raw_payload=flame_data.raw_payload
        )
        db.add(db_flame)
        await db.commit()
        await db.refresh(db_flame)
        
        return FlameDataResponse(
            time=db_flame.time,
            device_id=db_flame.device_id,
            analog_value=db_flame.analog_value,
            flame_detected=db_flame.flame_detected,
            raw_payload=db_flame.raw_payload
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Flame 데이터 생성 실패: {str(e)}")


@router.get("/", response_model=List[FlameDataResponse])
async def get_flame_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, description="조회 개수 제한"),
    db: AsyncSession = Depends(get_db_session)
):
    """Flame 센서 데이터 목록 조회"""
    try:
        query = select(SensorRawFlame)
        
        if device_id:
            query = query.where(SensorRawFlame.device_id == device_id)
        
        if start_time and end_time:
            query = query.where(
                and_(
                    SensorRawFlame.time >= start_time,
                    SensorRawFlame.time <= end_time
                )
            )
        
        query = query.order_by(SensorRawFlame.time.desc()).limit(limit)
        
        result = await db.execute(query)
        flame_list = result.scalars().all()
        
        return [
            FlameDataResponse(
                time=flame.time,
                device_id=flame.device_id,
                analog_value=flame.analog_value,
                flame_detected=flame.flame_detected,
                raw_payload=flame.raw_payload
            )
            for flame in flame_list
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flame 데이터 조회 실패: {str(e)}")


@router.get("/{device_id}/{timestamp}", response_model=FlameDataResponse)
async def get_flame_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 시간의 Flame 센서 데이터 조회"""
    try:
        query = select(SensorRawFlame).where(
            and_(
                SensorRawFlame.device_id == device_id,
                SensorRawFlame.time == timestamp
            )
        )
        
        result = await db.execute(query)
        flame_data = result.scalar_one_or_none()
        
        if not flame_data:
            raise HTTPException(status_code=404, detail="Flame 데이터를 찾을 수 없습니다")
        
        return FlameDataResponse(
            time=flame_data.time,
            device_id=flame_data.device_id,
            analog_value=flame_data.analog_value,
            flame_detected=flame_data.flame_detected,
            raw_payload=flame_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flame 데이터 조회 실패: {str(e)}")


@router.put("/{device_id}/{timestamp}", response_model=FlameDataResponse)
async def update_flame_data(
    device_id: str,
    timestamp: datetime,
    flame_data: FlameDataUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Flame 센서 데이터 수정"""
    try:
        query = select(SensorRawFlame).where(
            and_(
                SensorRawFlame.device_id == device_id,
                SensorRawFlame.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_flame = result.scalar_one_or_none()
        
        if not db_flame:
            raise HTTPException(status_code=404, detail="Flame 데이터를 찾을 수 없습니다")
        
        # 업데이트할 필드만 수정
        if flame_data.analog_value is not None:
            db_flame.analog_value = flame_data.analog_value
        if flame_data.flame_detected is not None:
            db_flame.flame_detected = flame_data.flame_detected
        if flame_data.raw_payload is not None:
            db_flame.raw_payload = flame_data.raw_payload
        
        await db.commit()
        await db.refresh(db_flame)
        
        return FlameDataResponse(
            time=db_flame.time,
            device_id=db_flame.device_id,
            analog_value=db_flame.analog_value,
            flame_detected=db_flame.flame_detected,
            raw_payload=db_flame.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Flame 데이터 수정 실패: {str(e)}")


@router.delete("/{device_id}/{timestamp}")
async def delete_flame_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """Flame 센서 데이터 삭제"""
    try:
        query = select(SensorRawFlame).where(
            and_(
                SensorRawFlame.device_id == device_id,
                SensorRawFlame.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_flame = result.scalar_one_or_none()
        
        if not db_flame:
            raise HTTPException(status_code=404, detail="Flame 데이터를 찾을 수 없습니다")
        
        await db.delete(db_flame)
        await db.commit()
        
        return {"message": "Flame 데이터가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Flame 데이터 삭제 실패: {str(e)}")


@router.get("/{device_id}/latest", response_model=FlameDataResponse)
async def get_latest_flame_data(
    device_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 디바이스의 최신 Flame 센서 데이터 조회"""
    try:
        query = select(SensorRawFlame).where(
            SensorRawFlame.device_id == device_id
        ).order_by(SensorRawFlame.time.desc()).limit(1)
        
        result = await db.execute(query)
        flame_data = result.scalar_one_or_none()
        
        if not flame_data:
            raise HTTPException(status_code=404, detail="Flame 데이터를 찾을 수 없습니다")
        
        return FlameDataResponse(
            time=flame_data.time,
            device_id=flame_data.device_id,
            analog_value=flame_data.analog_value,
            flame_detected=flame_data.flame_detected,
            raw_payload=flame_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최신 Flame 데이터 조회 실패: {str(e)}")


@router.get("/{device_id}/alerts")
async def get_flame_alerts(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    db: AsyncSession = Depends(get_db_session)
):
    """Flame 센서 알림 데이터 조회"""
    try:
        query = select(SensorRawFlame).where(
            and_(
                SensorRawFlame.device_id == device_id,
                SensorRawFlame.flame_detected == True
            )
        )
        
        if start_time and end_time:
            query = query.where(
                and_(
                    SensorRawFlame.time >= start_time,
                    SensorRawFlame.time <= end_time
                )
            )
        
        query = query.order_by(SensorRawFlame.time.desc())
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        return {
            "device_id": device_id,
            "alert_count": len(alerts),
            "alerts": [
                {
                    "time": alert.time,
                    "analog_value": alert.analog_value,
                    "raw_payload": alert.raw_payload
                }
                for alert in alerts
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flame 알림 조회 실패: {str(e)}")
