"""
DHT (온습도 센서) API 엔드포인트

DHT 센서 데이터의 CRUD 작업을 처리합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database import get_db_session
from app.infrastructure.models import SensorRawDHT
from app.api.v1.schemas import DHTDataCreate, DHTDataResponse, DHTDataUpdate

router = APIRouter(tags=["DHT Sensor"])


@router.post("/create", response_model=DHTDataResponse, status_code=201)
async def create_dht_data(
    dht_data: DHTDataCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """DHT 센서 데이터 생성"""
    try:
        db_dht = SensorRawDHT(
            time=dht_data.time,
            device_id=dht_data.device_id,
            temperature=dht_data.temperature,
            humidity=dht_data.humidity,
            heat_index=dht_data.heat_index,
            raw_payload=dht_data.raw_payload
        )
        db.add(db_dht)
        await db.commit()
        await db.refresh(db_dht)
        
        return DHTDataResponse(
            time=db_dht.time,
            device_id=db_dht.device_id,
            temperature=db_dht.temperature,
            humidity=db_dht.humidity,
            heat_index=db_dht.heat_index,
            raw_payload=db_dht.raw_payload
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DHT 데이터 생성 실패: {str(e)}")


@router.get("/", response_model=List[DHTDataResponse])
async def get_dht_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, description="조회 개수 제한"),
    db: AsyncSession = Depends(get_db_session)
):
    """DHT 센서 데이터 목록 조회"""
    try:
        query = select(SensorRawDHT)
        
        if device_id:
            query = query.where(SensorRawDHT.device_id == device_id)
        
        if start_time and end_time:
            query = query.where(
                and_(
                    SensorRawDHT.time >= start_time,
                    SensorRawDHT.time <= end_time
                )
            )
        
        query = query.order_by(SensorRawDHT.time.desc()).limit(limit)
        
        result = await db.execute(query)
        dht_list = result.scalars().all()
        
        return [
            DHTDataResponse(
                time=dht.time,
                device_id=dht.device_id,
                temperature=dht.temperature,
                humidity=dht.humidity,
                heat_index=dht.heat_index,
                raw_payload=dht.raw_payload
            )
            for dht in dht_list
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DHT 데이터 조회 실패: {str(e)}")


@router.get("/{device_id}/{timestamp}", response_model=DHTDataResponse)
async def get_dht_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 시간의 DHT 센서 데이터 조회"""
    try:
        query = select(SensorRawDHT).where(
            and_(
                SensorRawDHT.device_id == device_id,
                SensorRawDHT.time == timestamp
            )
        )
        
        result = await db.execute(query)
        dht_data = result.scalar_one_or_none()
        
        if not dht_data:
            raise HTTPException(status_code=404, detail="DHT 데이터를 찾을 수 없습니다")
        
        return DHTDataResponse(
            time=dht_data.time,
            device_id=dht_data.device_id,
            temperature=dht_data.temperature,
            humidity=dht_data.humidity,
            raw_payload=dht_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DHT 데이터 조회 실패: {str(e)}")


@router.put("/{device_id}/{timestamp}", response_model=DHTDataResponse)
async def update_dht_data(
    device_id: str,
    timestamp: datetime,
    dht_data: DHTDataUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """DHT 센서 데이터 수정"""
    try:
        query = select(SensorRawDHT).where(
            and_(
                SensorRawDHT.device_id == device_id,
                SensorRawDHT.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_dht = result.scalar_one_or_none()
        
        if not db_dht:
            raise HTTPException(status_code=404, detail="DHT 데이터를 찾을 수 없습니다")
        
        # 업데이트할 필드만 수정
        if dht_data.temperature is not None:
            db_dht.temperature = dht_data.temperature
        if dht_data.humidity is not None:
            db_dht.humidity = dht_data.humidity
        if dht_data.heat_index is not None:
            db_dht.heat_index = dht_data.heat_index
        if dht_data.raw_payload is not None:
            db_dht.raw_payload = dht_data.raw_payload
        
        await db.commit()
        await db.refresh(db_dht)
        
        return DHTDataResponse(
            time=db_dht.time,
            device_id=db_dht.device_id,
            temperature=db_dht.temperature,
            humidity=db_dht.humidity,
            heat_index=db_dht.heat_index,
            raw_payload=db_dht.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DHT 데이터 수정 실패: {str(e)}")


@router.delete("/{device_id}/{timestamp}")
async def delete_dht_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """DHT 센서 데이터 삭제"""
    try:
        query = select(SensorRawDHT).where(
            and_(
                SensorRawDHT.device_id == device_id,
                SensorRawDHT.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_dht = result.scalar_one_or_none()
        
        if not db_dht:
            raise HTTPException(status_code=404, detail="DHT 데이터를 찾을 수 없습니다")
        
        await db.delete(db_dht)
        await db.commit()
        
        return {"message": "DHT 데이터가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"DHT 데이터 삭제 실패: {str(e)}")


@router.get("/{device_id}/latest", response_model=DHTDataResponse)
async def get_latest_dht_data(
    device_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 디바이스의 최신 DHT 센서 데이터 조회"""
    try:
        query = select(SensorRawDHT).where(
            SensorRawDHT.device_id == device_id
        ).order_by(SensorRawDHT.time.desc()).limit(1)
        
        result = await db.execute(query)
        dht_data = result.scalar_one_or_none()
        
        if not dht_data:
            raise HTTPException(status_code=404, detail="DHT 데이터를 찾을 수 없습니다")
        
        return DHTDataResponse(
            time=dht_data.time,
            device_id=dht_data.device_id,
            temperature=dht_data.temperature,
            humidity=dht_data.humidity,
            raw_payload=dht_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최신 DHT 데이터 조회 실패: {str(e)}")


@router.get("/{device_id}/stats/summary")
async def get_dht_stats_summary(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    db: AsyncSession = Depends(get_db_session)
):
    """DHT 센서 데이터 통계 요약"""
    try:
        query = select(SensorRawDHT).where(
            SensorRawDHT.device_id == device_id
        )
        
        if start_time and end_time:
            query = query.where(
                and_(
                    SensorRawDHT.time >= start_time,
                    SensorRawDHT.time <= end_time
                )
            )
        
        result = await db.execute(query)
        dht_list = result.scalars().all()
        
        if not dht_list:
            raise HTTPException(status_code=404, detail="DHT 데이터를 찾을 수 없습니다")
        
        # 온도 통계
        temperatures = [dht.temperature for dht in dht_list if dht.temperature is not None]
        humidity_values = [dht.humidity for dht in dht_list if dht.humidity is not None]
        
        stats = {
            "device_id": device_id,
            "data_count": len(dht_list),
            "temperature": {
                "count": len(temperatures),
                "min": min(temperatures) if temperatures else None,
                "max": max(temperatures) if temperatures else None,
                "avg": sum(temperatures) / len(temperatures) if temperatures else None
            },
            "humidity": {
                "count": len(humidity_values),
                "min": min(humidity_values) if humidity_values else None,
                "max": max(humidity_values) if humidity_values else None,
                "avg": sum(humidity_values) / len(humidity_values) if humidity_values else None
            }
        }
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DHT 통계 조회 실패: {str(e)}")
