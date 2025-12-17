"""
CDS (조도 센서) API 엔드포인트

CDS 센서 데이터의 CRUD 작업을 처리합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database import get_db_session
from app.infrastructure.models import SensorRawCDS
from app.api.v1.schemas import CDSDataCreate, CDSDataResponse, CDSDataUpdate

router = APIRouter(tags=["CDS Sensor"])


@router.post("/create", response_model=CDSDataResponse, status_code=201)
async def create_cds_data(
    cds_data: CDSDataCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """CDS 센서 데이터 생성"""
    try:
        db_cds = SensorRawCDS(
            time=cds_data.time,
            device_id=cds_data.device_id,
            analog_value=cds_data.analog_value,
            lux_value=cds_data.lux_value,
            raw_payload=cds_data.raw_payload
        )
        db.add(db_cds)
        await db.commit()
        await db.refresh(db_cds)
        
        return CDSDataResponse(
            time=db_cds.time,
            device_id=db_cds.device_id,
            analog_value=db_cds.analog_value,
            lux_value=db_cds.lux_value,
            raw_payload=db_cds.raw_payload
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"CDS 데이터 생성 실패: {str(e)}")


@router.get("/list", response_model=List[CDSDataResponse])
async def get_cds_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, description="조회 개수 제한"),
    db: AsyncSession = Depends(get_db_session)
):
    """CDS 센서 데이터 목록 조회"""
    try:
        query = select(SensorRawCDS)
        
        if device_id:
            query = query.where(SensorRawCDS.device_id == device_id)
        
        if start_time and end_time:
            query = query.where(
                and_(
                    SensorRawCDS.time >= start_time,
                    SensorRawCDS.time <= end_time
                )
            )
        
        query = query.order_by(SensorRawCDS.time.desc()).limit(limit)
        
        result = await db.execute(query)
        cds_list = result.scalars().all()
        
        # 결과를 리스트로 변환하여 반환
        return [
            CDSDataResponse(
                time=cds.time,
                device_id=cds.device_id,
                analog_value=cds.analog_value,
                lux_value=cds.lux_value,
                raw_payload=cds.raw_payload
            )
            for cds in cds_list
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CDS 데이터 조회 실패: {str(e)}")


@router.get("/{device_id}/{timestamp}", response_model=CDSDataResponse)
async def get_cds_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 시간의 CDS 센서 데이터 조회"""
    try:
        query = select(SensorRawCDS).where(
            and_(
                SensorRawCDS.device_id == device_id,
                SensorRawCDS.time == timestamp
            )
        )
        
        result = await db.execute(query)
        cds_data = result.scalar_one_or_none()
        
        if not cds_data:
            raise HTTPException(status_code=404, detail="CDS 데이터를 찾을 수 없습니다")
        
        return CDSDataResponse(
            time=cds_data.time,
            device_id=cds_data.device_id,
            analog_value=cds_data.analog_value,
            lux_value=cds_data.lux_value,
            raw_payload=cds_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CDS 데이터 조회 실패: {str(e)}")


@router.put("/{device_id}/{timestamp}", response_model=CDSDataResponse)
async def update_cds_data(
    device_id: str,
    timestamp: datetime,
    cds_data: CDSDataUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """CDS 센서 데이터 수정"""
    try:
        query = select(SensorRawCDS).where(
            and_(
                SensorRawCDS.device_id == device_id,
                SensorRawCDS.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_cds = result.scalar_one_or_none()
        
        if not db_cds:
            raise HTTPException(status_code=404, detail="CDS 데이터를 찾을 수 없습니다")
        
        # 업데이트할 필드만 수정
        if cds_data.analog_value is not None:
            db_cds.analog_value = cds_data.analog_value
        if cds_data.lux_value is not None:
            db_cds.lux_value = cds_data.lux_value
        if cds_data.raw_payload is not None:
            db_cds.raw_payload = cds_data.raw_payload
        
        await db.commit()
        await db.refresh(db_cds)
        
        return CDSDataResponse(
            time=db_cds.time,
            device_id=db_cds.device_id,
            analog_value=db_cds.analog_value,
            lux_value=db_cds.lux_value,
            raw_payload=db_cds.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"CDS 데이터 수정 실패: {str(e)}")


@router.delete("/{device_id}/{timestamp}")
async def delete_cds_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """CDS 센서 데이터 삭제"""
    try:
        query = select(SensorRawCDS).where(
            and_(
                SensorRawCDS.device_id == device_id,
                SensorRawCDS.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_cds = result.scalar_one_or_none()
        
        if not db_cds:
            raise HTTPException(status_code=404, detail="CDS 데이터를 찾을 수 없습니다")
        
        await db.delete(db_cds)
        await db.commit()
        
        return {"message": "CDS 데이터가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"CDS 데이터 삭제 실패: {str(e)}")


@router.get("/{device_id}/latest", response_model=CDSDataResponse)
async def get_latest_cds_data(
    device_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 디바이스의 최신 CDS 센서 데이터 조회"""
    try:
        query = select(SensorRawCDS).where(
            SensorRawCDS.device_id == device_id
        ).order_by(SensorRawCDS.time.desc()).limit(1)
        
        result = await db.execute(query)
        cds_data = result.scalar_one_or_none()
        
        if not cds_data:
            raise HTTPException(status_code=404, detail="CDS 데이터를 찾을 수 없습니다")
        
        return CDSDataResponse(
            time=cds_data.time,
            device_id=cds_data.device_id,
            analog_value=cds_data.analog_value,
            lux_value=cds_data.lux_value,
            raw_payload=cds_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최신 CDS 데이터 조회 실패: {str(e)}")
