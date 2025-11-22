"""
IMU (관성 측정 장치) API 엔드포인트

IMU 센서 데이터의 CRUD 작업을 처리합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.infrastructure.database import get_db_session
from app.infrastructure.models import SensorRawIMU
from app.api.v1.schemas import IMUDataCreate, IMUDataResponse, IMUDataUpdate

router = APIRouter(tags=["IMU Sensor"])


@router.post("/create", response_model=IMUDataResponse, status_code=201)
async def create_imu_data(
    imu_data: IMUDataCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """IMU 센서 데이터 생성"""
    try:
        db_imu = SensorRawIMU(
            time=imu_data.time,
            device_id=imu_data.device_id,
            accel_x=imu_data.accel_x,
            accel_y=imu_data.accel_y,
            accel_z=imu_data.accel_z,
            gyro_x=imu_data.gyro_x,
            gyro_y=imu_data.gyro_y,
            gyro_z=imu_data.gyro_z,
            mag_x=imu_data.mag_x,
            mag_y=imu_data.mag_y,
            mag_z=imu_data.mag_z,
            temperature=imu_data.temperature,
            raw_payload=imu_data.raw_payload
        )
        db.add(db_imu)
        await db.commit()
        await db.refresh(db_imu)
        
        return IMUDataResponse(
            time=db_imu.time,
            device_id=db_imu.device_id,
            accel_x=db_imu.accel_x,
            accel_y=db_imu.accel_y,
            accel_z=db_imu.accel_z,
            gyro_x=db_imu.gyro_x,
            gyro_y=db_imu.gyro_y,
            gyro_z=db_imu.gyro_z,
            mag_x=db_imu.mag_x,
            mag_y=db_imu.mag_y,
            mag_z=db_imu.mag_z,
            temperature=db_imu.temperature,
            raw_payload=db_imu.raw_payload
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"IMU 데이터 생성 실패: {str(e)}")


@router.get("/list", response_model=List[IMUDataResponse])
async def get_imu_data_list(
    device_id: Optional[str] = Query(None, description="디바이스 ID"),
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    limit: int = Query(100, description="조회 개수 제한"),
    db: AsyncSession = Depends(get_db_session)
):
    """IMU 센서 데이터 목록 조회"""
    try:
        query = select(SensorRawIMU)
        
        if device_id:
            query = query.where(SensorRawIMU.device_id == device_id)
        
        if start_time and end_time:
            query = query.where(
                and_(
                    SensorRawIMU.time >= start_time,
                    SensorRawIMU.time <= end_time
                )
            )
        
        query = query.order_by(SensorRawIMU.time.desc()).limit(limit)
        
        result = await db.execute(query)
        imu_list = result.scalars().all()
        
        return [
            IMUDataResponse(
                time=imu.time,
                device_id=imu.device_id,
                accel_x=imu.accel_x,
                accel_y=imu.accel_y,
                accel_z=imu.accel_z,
                gyro_x=imu.gyro_x,
                gyro_y=imu.gyro_y,
                gyro_z=imu.gyro_z,
                raw_payload=imu.raw_payload
            )
            for imu in imu_list
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMU 데이터 조회 실패: {str(e)}")


@router.get("/{device_id}/{timestamp}", response_model=IMUDataResponse)
async def get_imu_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 시간의 IMU 센서 데이터 조회"""
    try:
        query = select(SensorRawIMU).where(
            and_(
                SensorRawIMU.device_id == device_id,
                SensorRawIMU.time == timestamp
            )
        )
        
        result = await db.execute(query)
        imu_data = result.scalar_one_or_none()
        
        if not imu_data:
            raise HTTPException(status_code=404, detail="IMU 데이터를 찾을 수 없습니다")
        
        return IMUDataResponse(
            time=imu_data.time,
            device_id=imu_data.device_id,
            accel_x=imu_data.accel_x,
            accel_y=imu_data.accel_y,
            accel_z=imu_data.accel_z,
            gyro_x=imu_data.gyro_x,
            gyro_y=imu_data.gyro_y,
            gyro_z=imu_data.gyro_z,
            raw_payload=imu_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMU 데이터 조회 실패: {str(e)}")


@router.put("/{device_id}/{timestamp}", response_model=IMUDataResponse)
async def update_imu_data(
    device_id: str,
    timestamp: datetime,
    imu_data: IMUDataUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """IMU 센서 데이터 수정"""
    try:
        query = select(SensorRawIMU).where(
            and_(
                SensorRawIMU.device_id == device_id,
                SensorRawIMU.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_imu = result.scalar_one_or_none()
        
        if not db_imu:
            raise HTTPException(status_code=404, detail="IMU 데이터를 찾을 수 없습니다")
        
        # 업데이트할 필드만 수정
        if imu_data.accel_x is not None:
            db_imu.accel_x = imu_data.accel_x
        if imu_data.accel_y is not None:
            db_imu.accel_y = imu_data.accel_y
        if imu_data.accel_z is not None:
            db_imu.accel_z = imu_data.accel_z
        if imu_data.gyro_x is not None:
            db_imu.gyro_x = imu_data.gyro_x
        if imu_data.gyro_y is not None:
            db_imu.gyro_y = imu_data.gyro_y
        if imu_data.gyro_z is not None:
            db_imu.gyro_z = imu_data.gyro_z
        if imu_data.raw_payload is not None:
            db_imu.raw_payload = imu_data.raw_payload
        
        await db.commit()
        await db.refresh(db_imu)
        
        return IMUDataResponse(
            time=db_imu.time,
            device_id=db_imu.device_id,
            accel_x=db_imu.accel_x,
            accel_y=db_imu.accel_y,
            accel_z=db_imu.accel_z,
            gyro_x=db_imu.gyro_x,
            gyro_y=db_imu.gyro_y,
            gyro_z=db_imu.gyro_z,
            mag_x=db_imu.mag_x,
            mag_y=db_imu.mag_y,
            mag_z=db_imu.mag_z,
            temperature=db_imu.temperature,
            raw_payload=db_imu.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"IMU 데이터 수정 실패: {str(e)}")


@router.delete("/{device_id}/{timestamp}")
async def delete_imu_data(
    device_id: str,
    timestamp: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    """IMU 센서 데이터 삭제"""
    try:
        query = select(SensorRawIMU).where(
            and_(
                SensorRawIMU.device_id == device_id,
                SensorRawIMU.time == timestamp
            )
        )
        
        result = await db.execute(query)
        db_imu = result.scalar_one_or_none()
        
        if not db_imu:
            raise HTTPException(status_code=404, detail="IMU 데이터를 찾을 수 없습니다")
        
        await db.delete(db_imu)
        await db.commit()
        
        return {"message": "IMU 데이터가 성공적으로 삭제되었습니다"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"IMU 데이터 삭제 실패: {str(e)}")


@router.get("/{device_id}/latest", response_model=IMUDataResponse)
async def get_latest_imu_data(
    device_id: str,
    db: AsyncSession = Depends(get_db_session)
):
    """특정 디바이스의 최신 IMU 센서 데이터 조회"""
    try:
        query = select(SensorRawIMU).where(
            SensorRawIMU.device_id == device_id
        ).order_by(SensorRawIMU.time.desc()).limit(1)
        
        result = await db.execute(query)
        imu_data = result.scalar_one_or_none()
        
        if not imu_data:
            raise HTTPException(status_code=404, detail="IMU 데이터를 찾을 수 없습니다")
        
        return IMUDataResponse(
            time=imu_data.time,
            device_id=imu_data.device_id,
            accel_x=imu_data.accel_x,
            accel_y=imu_data.accel_y,
            accel_z=imu_data.accel_z,
            gyro_x=imu_data.gyro_x,
            gyro_y=imu_data.gyro_y,
            gyro_z=imu_data.gyro_z,
            raw_payload=imu_data.raw_payload
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최신 IMU 데이터 조회 실패: {str(e)}")


@router.get("/{device_id}/motion/analysis")
async def analyze_motion_pattern(
    device_id: str,
    start_time: Optional[datetime] = Query(None, description="시작 시간"),
    end_time: Optional[datetime] = Query(None, description="종료 시간"),
    db: AsyncSession = Depends(get_db_session)
):
    """IMU 센서 데이터를 이용한 동작 패턴 분석"""
    try:
        query = select(SensorRawIMU).where(
            SensorRawIMU.device_id == device_id
        )
        
        if start_time and end_time:
            query = query.where(
                and_(
                    SensorRawIMU.time >= start_time,
                    SensorRawIMU.time <= end_time
                )
            )
        
        query = query.order_by(SensorRawIMU.time.desc()).limit(1000)  # 최근 1000개 데이터
        
        result = await db.execute(query)
        imu_list = result.scalars().all()
        
        if not imu_list:
            raise HTTPException(status_code=404, detail="IMU 데이터를 찾을 수 없습니다")
        
        # 가속도 데이터 분석
        accel_x_values = [imu.accel_x for imu in imu_list if imu.accel_x is not None]
        accel_y_values = [imu.accel_y for imu in imu_list if imu.accel_y is not None]
        accel_z_values = [imu.accel_z for imu in imu_list if imu.accel_z is not None]
        
        # 자이로스코프 데이터 분석
        gyro_x_values = [imu.gyro_x for imu in imu_list if imu.gyro_x is not None]
        gyro_y_values = [imu.gyro_y for imu in imu_list if imu.gyro_y is not None]
        gyro_z_values = [imu.gyro_z for imu in imu_list if imu.gyro_z is not None]
        
        analysis = {
            "device_id": device_id,
            "data_count": len(imu_list),
            "time_range": {
                "start": imu_list[-1].time if imu_list else None,
                "end": imu_list[0].time if imu_list else None
            },
            "acceleration": {
                "x_axis": {
                    "count": len(accel_x_values),
                    "min": min(accel_x_values) if accel_x_values else None,
                    "max": max(accel_x_values) if accel_x_values else None,
                    "avg": sum(accel_x_values) / len(accel_x_values) if accel_x_values else None
                },
                "y_axis": {
                    "count": len(accel_y_values),
                    "min": min(accel_y_values) if accel_y_values else None,
                    "max": max(accel_y_values) if accel_y_values else None,
                    "avg": sum(accel_y_values) / len(accel_y_values) if accel_y_values else None
                },
                "z_axis": {
                    "count": len(accel_z_values),
                    "min": min(accel_z_values) if accel_z_values else None,
                    "max": max(accel_z_values) if accel_z_values else None,
                    "avg": sum(accel_z_values) / len(accel_z_values) if accel_z_values else None
                }
            },
            "gyroscope": {
                "x_axis": {
                    "count": len(gyro_x_values),
                    "min": min(gyro_x_values) if gyro_x_values else None,
                    "max": max(gyro_x_values) if gyro_x_values else None,
                    "avg": sum(gyro_x_values) / len(gyro_x_values) if gyro_x_values else None
                },
                "y_axis": {
                    "count": len(gyro_y_values),
                    "min": min(gyro_y_values) if gyro_y_values else None,
                    "max": max(gyro_y_values) if gyro_y_values else None,
                    "avg": sum(gyro_y_values) / len(gyro_y_values) if gyro_y_values else None
                },
                "z_axis": {
                    "count": len(gyro_z_values),
                    "min": min(gyro_z_values) if gyro_z_values else None,
                    "max": max(gyro_z_values) if gyro_z_values else None,
                    "avg": sum(gyro_z_values) / len(gyro_z_values) if gyro_z_values else None
                }
            }
        }
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"IMU 동작 패턴 분석 실패: {str(e)}")
