from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from app.core.container import get_sensor_raw_temperature_service
from app.interfaces.services.sensor_raw_temperature_service_interface import ISensorRawTemperatureService
from app.api.v1.schemas import (
    SensorRawTemperatureCreate, SensorRawTemperatureUpdate,
    SensorRawTemperatureResponse, SensorRawTemperatureListResponse
)

router = APIRouter(tags=["온도 센서 원시 데이터"])

@router.post("/create", response_model=SensorRawTemperatureResponse, status_code=201)
async def create_sensor_raw_temperature(
    temperature_data: SensorRawTemperatureCreate = Body(...),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """온도 센서 원시 데이터 생성
    
    LM35 등 온도 센서의 원시 측정 데이터를 기록합니다.
    
    **요청 데이터**:
    - time: 측정 시간 (필수)
    - device_id: 디바이스 ID (필수)
    - temperature_celsius: 섭씨 단위의 온도 값 (필수)
    - humidity_percent: 상대 습도 값 % (선택)
    - raw_payload: 원시 데이터 (선택)
    
    **응답**:
    - 생성된 온도 센서 데이터 정보
    
    **사용 예시**:
    ```json
    {
        "time": "2025-08-23T15:30:00Z",
        "device_id": "temp_sensor_001",
        "temperature_celsius": 23.5,
        "humidity_percent": 65.2
    }
    ```
    """
    try:
        return await temperature_service.create_temperature_data(temperature_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"온도 데이터 생성 실패: {str(e)}")

@router.get("/{time}/{device_id}", response_model=SensorRawTemperatureResponse)
async def get_sensor_raw_temperature(
    time: datetime = Path(..., description="측정 시간"),
    device_id: str = Path(..., description="디바이스 ID"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """특정 시간과 디바이스의 온도 데이터 조회
    
    **경로 매개변수**:
    - time: 측정 시간 (ISO 8601 형식)
    - device_id: 디바이스 ID
    
    **응답**:
    - 해당 시간의 온도 센서 데이터 정보
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/2025-08-23T15:30:00Z/temp_sensor_001
    ```
    """
    temperature = await temperature_service.get_temperature_data_by_time_and_device(time, device_id)
    if not temperature:
        raise HTTPException(status_code=404, detail="온도 데이터를 찾을 수 없습니다")
    return temperature

@router.get("/latest/{device_id}", response_model=SensorRawTemperatureResponse)
async def get_latest_sensor_raw_temperature(
    device_id: str = Path(..., description="디바이스 ID"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """디바이스의 최신 온도 데이터 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **응답**:
    - 가장 최근에 측정된 온도 센서 데이터 정보
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/latest/temp_sensor_001
    ```
    """
    temperature = await temperature_service.get_latest_temperature_data_by_device(device_id)
    if not temperature:
        raise HTTPException(status_code=404, detail="온도 데이터를 찾을 수 없습니다")
    return temperature

@router.get("/device/{device_id}", response_model=List[SensorRawTemperatureResponse])
async def get_sensor_raw_temperatures_by_device(
    device_id: str = Path(..., description="디바이스 ID"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 데이터 개수"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """디바이스의 온도 데이터 목록 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - limit: 조회할 데이터 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 디바이스의 온도 데이터 목록 (최신순)
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/device/temp_sensor_001?limit=50
    ```
    """
    temperatures = await temperature_service.get_temperature_data_by_device(device_id, limit)
    return temperatures

@router.get("/time-range/{device_id}", response_model=List[SensorRawTemperatureResponse])
async def get_sensor_raw_temperatures_by_time_range(
    device_id: str = Path(..., description="디바이스 ID"),
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """특정 시간 범위의 온도 데이터 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 지정된 시간 범위의 온도 데이터 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/time-range/temp_sensor_001?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    temperatures = await temperature_service.get_temperature_data_by_time_range(device_id, start_time, end_time)
    return temperatures

@router.get("/temperature-range/{device_id}", response_model=List[SensorRawTemperatureResponse])
async def get_sensor_raw_temperatures_by_temperature_range(
    device_id: str = Path(..., description="디바이스 ID"),
    min_temp: float = Query(..., description="최소 온도"),
    max_temp: float = Query(..., description="최대 온도"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """특정 온도 범위의 데이터 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - min_temp: 최소 온도
    - max_temp: 최대 온도
    
    **응답**:
    - 지정된 온도 범위의 데이터 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/temperature-range/temp_sensor_001?min_temp=20&max_temp=30
    ```
    """
    temperatures = await temperature_service.get_temperature_data_by_temperature_range(device_id, min_temp, max_temp)
    return temperatures

@router.get("/extreme/{device_id}", response_model=List[SensorRawTemperatureResponse])
async def get_extreme_temperature_data(
    device_id: str = Path(..., description="디바이스 ID"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 데이터 개수"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """극한 온도 데이터 조회 (0°C 이하 또는 50°C 이상)
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - limit: 조회할 데이터 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 극한 온도 데이터 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/extreme/temp_sensor_001?limit=50
    ```
    """
    temperatures = await temperature_service.get_extreme_temperature_data(device_id, limit)
    return temperatures

@router.put("/{time}/{device_id}", response_model=SensorRawTemperatureResponse)
async def update_sensor_raw_temperature(
    time: datetime = Path(..., description="측정 시간"),
    device_id: str = Path(..., description="디바이스 ID"),
    temperature_data: SensorRawTemperatureUpdate = Body(...),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """온도 데이터 업데이트
    
    **경로 매개변수**:
    - time: 측정 시간 (ISO 8601 형식)
    - device_id: 디바이스 ID
    
    **요청 데이터**:
    - 업데이트할 필드들 (None이 아닌 필드만 업데이트)
    
    **응답**:
    - 업데이트된 온도 데이터 정보
    
    **사용 예시**:
    ```json
    {
        "temperature_celsius": 24.2,
        "humidity_percent": 68.5
    }
    ```
    """
    temperature = await temperature_service.update_temperature_data(time, device_id, temperature_data)
    if not temperature:
        raise HTTPException(status_code=404, detail="온도 데이터를 찾을 수 없습니다")
    return temperature

@router.delete("/{time}/{device_id}")
async def delete_sensor_raw_temperature(
    time: datetime = Path(..., description="측정 시간"),
    device_id: str = Path(..., description="디바이스 ID"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """온도 데이터 삭제
    
    **경로 매개변수**:
    - time: 측정 시간 (ISO 8601 형식)
    - device_id: 디바이스 ID
    
    **응답**:
    - 삭제 성공 여부
    
    **사용 예시**:
    ```
    DELETE /api/sensor-raw-temperatures/2025-08-23T15:30:00Z/temp_sensor_001
    ```
    """
    success = await temperature_service.delete_temperature_data(time, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="온도 데이터를 찾을 수 없습니다")
    return {"message": "온도 데이터가 성공적으로 삭제되었습니다"}

@router.get("/", response_model=SensorRawTemperatureListResponse)
async def get_all_sensor_raw_temperatures(
    skip: int = Query(0, ge=0, description="건너뛸 데이터 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 데이터 개수"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """전체 온도 데이터 목록 조회 (페이지네이션)
    
    **쿼리 매개변수**:
    - skip: 건너뛸 데이터 개수 (기본값: 0)
    - limit: 조회할 데이터 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 온도 데이터 목록 및 페이지네이션 정보
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/?skip=100&limit=50
    ```
    """
    temperatures = await temperature_service.get_all_temperature_data(skip, limit)
    return temperatures

@router.get("/average/{device_id}")
async def get_average_temperature_by_device(
    device_id: str = Path(..., description="디바이스 ID"),
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """디바이스의 평균 온도 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 지정된 시간 범위의 평균 온도
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/average/temp_sensor_001?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    avg_temp = await temperature_service.get_average_temperature_by_device(device_id, start_time, end_time)
    if avg_temp is None:
        raise HTTPException(status_code=404, detail="해당 기간의 온도 데이터를 찾을 수 없습니다")
    return {"device_id": device_id, "average_temperature": round(avg_temp, 2)}

@router.get("/statistics/{device_id}")
async def get_temperature_statistics_by_device(
    device_id: str = Path(..., description="디바이스 ID"),
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    temperature_service: ISensorRawTemperatureService = Depends(get_sensor_raw_temperature_service)
):
    """디바이스의 온도 통계 정보 조회 (최소, 최대, 평균)
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 온도 통계 정보 (최소, 최대, 평균, 데이터 개수)
    
    **사용 예시**:
    ```
    GET /api/sensor-raw-temperatures/statistics/temp_sensor_001?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    stats = await temperature_service.get_temperature_statistics_by_device(device_id, start_time, end_time)
    if not stats:
        raise HTTPException(status_code=404, detail="해당 기간의 온도 데이터를 찾을 수 없습니다")
    return {"device_id": device_id, **stats}
