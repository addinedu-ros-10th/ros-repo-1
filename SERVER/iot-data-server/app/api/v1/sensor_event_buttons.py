from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from app.core.container import get_sensor_event_button_service
from app.interfaces.services.sensor_event_button_service_interface import ISensorEventButtonService
from app.api.v1.schemas import (
    SensorEventButtonCreate, SensorEventButtonUpdate,
    SensorEventButtonResponse, SensorEventButtonListResponse
)

router = APIRouter(tags=["버튼 이벤트 센서"])

@router.post("/create", response_model=SensorEventButtonResponse, status_code=201)
async def create_sensor_event_button(
    button_event_data: SensorEventButtonCreate,
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """버튼 이벤트 센서 생성
    
    푸시버튼 입력 이벤트(위기 해제, 복약 체크 등)를 기록합니다.
    
    **요청 데이터**:
    - time: 이벤트 발생 시간 (필수)
    - device_id: 디바이스 ID (필수)
    - button_state: 버튼의 물리적 상태 (PRESSED, RELEASED, LONG_PRESS)
    - event_type: 버튼 입력의 목적 (crisis_acknowledged, assistance_request, medication_check)
    - press_duration_ms: 버튼 누름 지속 시간 (밀리초, 선택)
    - raw_payload: 원시 데이터 (선택)
    
    **응답**:
    - 생성된 버튼 이벤트 정보
    
    **사용 예시**:
    ```json
    {
        "time": "2025-08-23T15:30:00Z",
        "device_id": "kitchen_button_001",
        "button_state": "PRESSED",
        "event_type": "crisis_acknowledged",
        "press_duration_ms": 500
    }
    ```
    """
    try:
        return await button_service.create_button_event(button_event_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"버튼 이벤트 생성 실패: {str(e)}")

@router.get("/{time}/{device_id}", response_model=SensorEventButtonResponse)
async def get_sensor_event_button(
    time: datetime = Path(..., description="이벤트 발생 시간"),
    device_id: str = Path(..., description="디바이스 ID"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """특정 시간과 디바이스의 버튼 이벤트 조회
    
    **경로 매개변수**:
    - time: 이벤트 발생 시간 (ISO 8601 형식)
    - device_id: 디바이스 ID
    
    **응답**:
    - 해당 시간의 버튼 이벤트 정보
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/2025-08-23T15:30:00Z/kitchen_button_001
    ```
    """
    event = await button_service.get_button_event_by_time_and_device(time, device_id)
    if not event:
        raise HTTPException(status_code=404, detail="버튼 이벤트를 찾을 수 없습니다")
    return event

@router.get("/latest/{device_id}", response_model=SensorEventButtonResponse)
async def get_latest_sensor_event_button(
    device_id: str = Path(..., description="디바이스 ID"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """디바이스의 최신 버튼 이벤트 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **응답**:
    - 가장 최근에 발생한 버튼 이벤트 정보
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/latest/kitchen_button_001
    ```
    """
    event = await button_service.get_latest_button_event_by_device(device_id)
    if not event:
        raise HTTPException(status_code=404, detail="버튼 이벤트를 찾을 수 없습니다")
    return event

@router.get("/device/{device_id}", response_model=List[SensorEventButtonResponse])
async def get_sensor_event_buttons_by_device(
    device_id: str = Path(..., description="디바이스 ID"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 이벤트 개수"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """디바이스의 버튼 이벤트 목록 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - limit: 조회할 이벤트 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 디바이스의 버튼 이벤트 목록 (최신순)
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/device/kitchen_button_001?limit=50
    ```
    """
    events = await button_service.get_button_events_by_device(device_id, limit)
    return events

@router.get("/event-type/{event_type}", response_model=List[SensorEventButtonResponse])
async def get_sensor_event_buttons_by_event_type(
    event_type: str = Path(..., description="이벤트 타입"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 이벤트 개수"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """특정 이벤트 타입의 버튼 이벤트 조회
    
    **경로 매개변수**:
    - event_type: 이벤트 타입 (crisis_acknowledged, assistance_request, medication_check)
    
    **쿼리 매개변수**:
    - limit: 조회할 이벤트 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 지정된 이벤트 타입의 버튼 이벤트 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/event-type/crisis_acknowledged?limit=50
    ```
    """
    valid_types = ['crisis_acknowledged', 'assistance_request', 'medication_check']
    if event_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 이벤트 타입입니다. 허용된 값: {', '.join(valid_types)}")
    
    events = await button_service.get_button_events_by_event_type(event_type, limit)
    return events

@router.get("/button-state/{button_state}", response_model=List[SensorEventButtonResponse])
async def get_sensor_event_buttons_by_button_state(
    button_state: str = Path(..., description="버튼 상태"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 이벤트 개수"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """특정 버튼 상태의 이벤트 조회
    
    **경로 매개변수**:
    - button_state: 버튼 상태 (PRESSED, RELEASED, LONG_PRESS)
    
    **쿼리 매개변수**:
    - limit: 조회할 이벤트 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 지정된 버튼 상태의 이벤트 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/button-state/LONG_PRESS?limit=50
    ```
    """
    valid_states = ['PRESSED', 'RELEASED', 'LONG_PRESS']
    if button_state not in valid_states:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 버튼 상태입니다. 허용된 값: {', '.join(valid_states)}")
    
    events = await button_service.get_button_events_by_button_state(button_state, limit)
    return events

@router.get("/time-range/{device_id}", response_model=List[SensorEventButtonResponse])
async def get_sensor_event_buttons_by_time_range(
    device_id: str = Path(..., description="디바이스 ID"),
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """특정 시간 범위의 버튼 이벤트 조회
    
    **경로 매개변수**:
    - device_id: 디바이스 ID
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 지정된 시간 범위의 버튼 이벤트 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/time-range/kitchen_button_001?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    events = await button_service.get_button_events_by_time_range(device_id, start_time, end_time)
    return events

@router.put("/{time}/{device_id}", response_model=SensorEventButtonResponse)
async def update_sensor_event_button(
    time: datetime = Path(..., description="이벤트 발생 시간"),
    device_id: str = Path(..., description="디바이스 ID"),
    event_data: SensorEventButtonUpdate = Body(...),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """버튼 이벤트 업데이트
    
    **경로 매개변수**:
    - time: 이벤트 발생 시간 (ISO 8601 형식)
    - device_id: 디바이스 ID
    
    **요청 데이터**:
    - 업데이트할 필드들 (None이 아닌 필드만 업데이트)
    
    **응답**:
    - 업데이트된 버튼 이벤트 정보
    
    **사용 예시**:
    ```json
    {
        "button_state": "RELEASED",
        "press_duration_ms": 750
    }
    ```
    """
    event = await button_service.update_button_event(time, device_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="버튼 이벤트를 찾을 수 없습니다")
    return event

@router.delete("/{time}/{device_id}")
async def delete_sensor_event_button(
    time: datetime = Path(..., description="이벤트 발생 시간"),
    device_id: str = Path(..., description="디바이스 ID"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """버튼 이벤트 삭제
    
    **경로 매개변수**:
    - time: 이벤트 발생 시간 (ISO 8601 형식)
    - device_id: 디바이스 ID
    
    **응답**:
    - 삭제 성공 여부
    
    **사용 예시**:
    ```
    DELETE /api/sensor-event-buttons/2025-08-23T15:30:00Z/kitchen_button_001
    ```
    """
    success = await button_service.delete_button_event(time, device_id)
    if not success:
        raise HTTPException(status_code=404, detail="버튼 이벤트를 찾을 수 없습니다")
    return {"message": "버튼 이벤트가 성공적으로 삭제되었습니다"}

@router.get("/", response_model=SensorEventButtonListResponse)
async def get_all_sensor_event_buttons(
    skip: int = Query(0, ge=0, description="건너뛸 이벤트 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 이벤트 개수"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """전체 버튼 이벤트 목록 조회 (페이지네이션)
    
    **쿼리 매개변수**:
    - skip: 건너뛸 이벤트 개수 (기본값: 0)
    - limit: 조회할 이벤트 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 버튼 이벤트 목록 및 페이지네이션 정보
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/?skip=100&limit=50
    ```
    """
    events = await button_service.get_all_button_events(skip, limit)
    return events

@router.get("/crisis-events", response_model=List[SensorEventButtonResponse])
async def get_crisis_events(
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """위기 상황 이벤트 조회
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 위기 상황 해제 이벤트 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/crisis-events?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    events = await button_service.get_crisis_events(start_time, end_time)
    return events

@router.get("/assistance-requests", response_model=List[SensorEventButtonResponse])
async def get_assistance_requests(
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """도움 요청 이벤트 조회
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 도움 요청 이벤트 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/assistance-requests?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    events = await button_service.get_assistance_requests(start_time, end_time)
    return events

@router.get("/medication-checks", response_model=List[SensorEventButtonResponse])
async def get_medication_checks(
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """복약 체크 이벤트 조회
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 복약 체크 이벤트 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/medication-checks?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    events = await button_service.get_medication_checks(start_time, end_time)
    return events

@router.get("/high-priority-events", response_model=List[SensorEventButtonResponse])
async def get_high_priority_events(
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    button_service: ISensorEventButtonService = Depends(get_sensor_event_button_service)
):
    """높은 우선순위 이벤트 조회
    
    위기 상황과 도움 요청 이벤트를 우선순위별로 정렬하여 조회합니다.
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 우선순위별로 정렬된 높은 우선순위 이벤트 목록
    
    **사용 예시**:
    ```
    GET /api/sensor-event-buttons/high-priority-events?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    events = await button_service.get_high_priority_events(start_time, end_time)
    return events
