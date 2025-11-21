from typing import List, Optional
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from app.core.container import get_home_state_snapshot_service
from app.interfaces.services.home_state_snapshot_service_interface import IHomeStateSnapshotService
from app.api.v1.schemas import (
    HomeStateSnapshotCreate, HomeStateSnapshotUpdate, 
    HomeStateSnapshotResponse, HomeStateSnapshotListResponse
)

router = APIRouter(tags=["홈 상태 스냅샷"])

@router.post("/create", response_model=HomeStateSnapshotResponse, status_code=201)
async def create_home_state_snapshot(
    snapshot_data: HomeStateSnapshotCreate = Body(...),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """홈 상태 스냅샷 생성
    
    매 순간의 집 전체 센서 상태를 기록하는 스냅샷을 생성합니다.
    Digital Twin State로 활용되어 실시간 홈 모니터링에 사용됩니다.
    
    **요청 데이터**:
    - time: 스냅샷 시간 (필수)
    - user_id: 사용자 ID (필수)
    - 각 구역별 센서 상태 (선택)
    - 경보 수준 및 이유 (선택)
    
    **응답**:
    - 생성된 홈 상태 스냅샷 정보
    
    **사용 예시**:
    ```json
    {
        "time": "2025-08-23T15:30:00Z",
        "user_id": "123e4567-e89b-12d3-a456-426614174000",
        "entrance_pir_motion": true,
        "kitchen_mq5_gas_ppm": 25.5,
        "alert_level": "Normal"
    }
    ```
    """
    try:
        return await snapshot_service.create_snapshot(snapshot_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"스냅샷 생성 실패: {str(e)}")

@router.get("/{time}/{user_id}", response_model=HomeStateSnapshotResponse)
async def get_home_state_snapshot(
    time: datetime = Path(..., description="스냅샷 시간"),
    user_id: UUID = Path(..., description="사용자 ID"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """특정 시간과 사용자의 홈 상태 스냅샷 조회
    
    **경로 매개변수**:
    - time: 스냅샷 시간 (ISO 8601 형식)
    - user_id: 사용자 ID (UUID)
    
    **응답**:
    - 해당 시간의 홈 상태 스냅샷 정보
    
    **사용 예시**:
    ```
    GET /api/home-state-snapshots/2025-08-23T15:30:00Z/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    snapshot = await snapshot_service.get_snapshot_by_time_and_user(time, user_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="스냅샷을 찾을 수 없습니다")
    return snapshot

@router.get("/latest/{user_id}", response_model=HomeStateSnapshotResponse)
async def get_latest_home_state_snapshot(
    user_id: UUID = Path(..., description="사용자 ID"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """사용자의 최신 홈 상태 스냅샷 조회
    
    **경로 매개변수**:
    - user_id: 사용자 ID (UUID)
    
    **응답**:
    - 가장 최근에 생성된 홈 상태 스냅샷 정보
    
    **사용 예시**:
    ```
    GET /api/home-state-snapshots/latest/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    snapshot = await snapshot_service.get_latest_snapshot_by_user(user_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="스냅샷을 찾을 수 없습니다")
    return snapshot

@router.get("/user/{user_id}", response_model=List[HomeStateSnapshotResponse])
async def get_home_state_snapshots_by_user(
    user_id: UUID = Path(..., description="사용자 ID"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 스냅샷 개수"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """사용자의 홈 상태 스냅샷 목록 조회
    
    **경로 매개변수**:
    - user_id: 사용자 ID (UUID)
    
    **쿼리 매개변수**:
    - limit: 조회할 스냅샷 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 사용자의 홈 상태 스냅샷 목록 (최신순)
    
    **사용 예시**:
    ```
    GET /api/home-state-snapshots/user/123e4567-e89b-12d3-a456-426614174000?limit=50
    ```
    """
    snapshots = await snapshot_service.get_snapshots_by_user(user_id, limit)
    return snapshots

@router.get("/time-range/{user_id}", response_model=List[HomeStateSnapshotResponse])
async def get_home_state_snapshots_by_time_range(
    user_id: UUID = Path(..., description="사용자 ID"),
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """특정 시간 범위의 홈 상태 스냅샷 조회
    
    **경로 매개변수**:
    - user_id: 사용자 ID (UUID)
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - 지정된 시간 범위의 홈 상태 스냅샷 목록
    
    **사용 예시**:
    ```
    GET /api/home-state-snapshots/time-range/123e4567-e89b-12d3-a456-426614174000?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    snapshots = await snapshot_service.get_snapshots_by_time_range(user_id, start_time, end_time)
    return snapshots

@router.get("/alert-level/{user_id}/{alert_level}", response_model=List[HomeStateSnapshotResponse])
async def get_home_state_snapshots_by_alert_level(
    user_id: UUID = Path(..., description="사용자 ID"),
    alert_level: str = Path(..., description="경보 수준 (Normal, Attention, Warning, Emergency)"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """특정 경보 수준의 홈 상태 스냅샷 조회
    
    **경로 매개변수**:
    - user_id: 사용자 ID (UUID)
    - alert_level: 경보 수준
    
    **응답**:
    - 지정된 경보 수준의 홈 상태 스냅샷 목록
    
    **사용 예시**:
    ```
    GET /api/home-state-snapshots/alert-level/123e4567-e89b-12d3-a456-426614174000/Warning
    ```
    """
    valid_levels = ['Normal', 'Attention', 'Warning', 'Emergency']
    if alert_level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 경보 수준입니다. 허용된 값: {', '.join(valid_levels)}")
    
    snapshots = await snapshot_service.get_snapshots_by_alert_level(user_id, alert_level)
    return snapshots

@router.put("/{time}/{user_id}/alert-level", response_model=HomeStateSnapshotResponse)
async def update_home_state_snapshot_alert_level(
    time: datetime = Path(..., description="스냅샷 시간"),
    user_id: UUID = Path(..., description="사용자 ID"),
    alert_level: str = Query(..., description="새로운 경보 수준"),
    reason: str = Query(..., description="경보 수준 변경 이유"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """홈 상태 스냅샷의 경보 수준 업데이트
    
    **경로 매개변수**:
    - time: 스냅샷 시간 (ISO 8601 형식)
    - user_id: 사용자 ID (UUID)
    
    **쿼리 매개변수**:
    - alert_level: 새로운 경보 수준
    - reason: 경보 수준 변경 이유
    
    **응답**:
    - 업데이트된 홈 상태 스냅샷 정보
    
    **사용 예시**:
    ```
    PUT /api/home-state-snapshots/2025-08-23T15:30:00Z/123e4567-e89b-12d3-a456-426614174000/alert-level?alert_level=Warning&reason=가스 농도 증가
    ```
    """
    valid_levels = ['Normal', 'Attention', 'Warning', 'Emergency']
    if alert_level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"유효하지 않은 경보 수준입니다. 허용된 값: {', '.join(valid_levels)}")
    
    snapshot = await snapshot_service.update_alert_level(time, user_id, alert_level, reason)
    if not snapshot:
        raise HTTPException(status_code=404, detail="스냅샷을 찾을 수 없습니다")
    return snapshot

@router.put("/{time}/{user_id}", response_model=HomeStateSnapshotResponse)
async def update_home_state_snapshot(
    time: datetime = Path(..., description="스냅샷 시간"),
    user_id: UUID = Path(..., description="사용자 ID"),
    snapshot_data: HomeStateSnapshotUpdate = Body(...),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """홈 상태 스냅샷 업데이트
    
    **경로 매개변수**:
    - time: 스냅샷 시간 (ISO 8601 형식)
    - user_id: 사용자 ID (UUID)
    
    **요청 데이터**:
    - 업데이트할 필드들 (None이 아닌 필드만 업데이트)
    
    **응답**:
    - 업데이트된 홈 상태 스냅샷 정보
    
    **사용 예시**:
    ```json
    {
        "kitchen_mq5_gas_ppm": 35.2,
        "alert_level": "Attention",
        "alert_reason": "가스 농도 증가 감지"
    }
    ```
    """
    snapshot = await snapshot_service.update_snapshot(time, user_id, snapshot_data)
    if not snapshot:
        raise HTTPException(status_code=404, detail="스냅샷을 찾을 수 없습니다")
    return snapshot

@router.delete("/{time}/{user_id}")
async def delete_home_state_snapshot(
    time: datetime = Path(..., description="스냅샷 시간"),
    user_id: UUID = Path(..., description="사용자 ID"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """홈 상태 스냅샷 삭제
    
    **경로 매개변수**:
    - time: 스냅샷 시간 (ISO 8601 형식)
    - user_id: 사용자 ID (UUID)
    
    **응답**:
    - 삭제 성공 여부
    
    **사용 예시**:
    ```
    DELETE /api/home-state-snapshots/2025-08-23T15:30:00Z/123e4567-e89b-12d3-a456-426614174000
    ```
    """
    success = await snapshot_service.delete_snapshot(time, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="스냅샷을 찾을 수 없습니다")
    return {"message": "스냅샷이 성공적으로 삭제되었습니다"}

@router.get("/", response_model=HomeStateSnapshotListResponse)
async def get_all_home_state_snapshots(
    skip: int = Query(0, ge=0, description="건너뛸 스냅샷 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회할 스냅샷 개수"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """전체 홈 상태 스냅샷 목록 조회 (페이지네이션)
    
    **쿼리 매개변수**:
    - skip: 건너뛸 스냅샷 개수 (기본값: 0)
    - limit: 조회할 스냅샷 개수 (기본값: 100, 최대: 1000)
    
    **응답**:
    - 홈 상태 스냅샷 목록 및 페이지네이션 정보
    
    **사용 예시**:
    ```
    GET /api/home-state-snapshots/?skip=100&limit=50
    ```
    """
    snapshots = await snapshot_service.get_all_snapshots(skip, limit)
    return snapshots

@router.get("/environmental-alerts/{user_id}", response_model=List[HomeStateSnapshotResponse])
async def get_environmental_alerts(
    user_id: UUID = Path(..., description="사용자 ID"),
    start_time: datetime = Query(..., description="시작 시간"),
    end_time: datetime = Query(..., description="종료 시간"),
    snapshot_service: IHomeStateSnapshotService = Depends(get_home_state_snapshot_service)
):
    """환경 관련 경보가 있는 스냅샷 조회
    
    **경로 매개변수**:
    - user_id: 사용자 ID (UUID)
    
    **쿼리 매개변수**:
    - start_time: 시작 시간 (ISO 8601 형식)
    - end_time: 종료 시간 (ISO 8601 형식)
    
    **응답**:
    - Warning 또는 Emergency 경보 수준의 스냅샷 목록
    
    **사용 예시**:
    ```
    GET /api/home-state-snapshots/environmental-alerts/123e4567-e89b-12d3-a456-426614174000?start_time=2025-08-23T00:00:00Z&end_time=2025-08-23T23:59:59Z
    ```
    """
    snapshots = await snapshot_service.get_environmental_alerts(user_id, start_time, end_time)
    return snapshots
