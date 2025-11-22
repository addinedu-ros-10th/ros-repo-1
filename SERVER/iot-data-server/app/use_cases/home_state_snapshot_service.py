from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.interfaces.services.home_state_snapshot_service_interface import IHomeStateSnapshotService
from app.interfaces.repositories.home_state_snapshot_repository import IHomeStateSnapshotRepository
from app.domain.entities.home_state_snapshot import HomeStateSnapshot
from app.api.v1.schemas import (
    HomeStateSnapshotCreate, HomeStateSnapshotUpdate,
    HomeStateSnapshotResponse, HomeStateSnapshotListResponse
)


class HomeStateSnapshotService(IHomeStateSnapshotService):
    """홈 상태 스냅샷 서비스 구현체"""
    
    def __init__(self, snapshot_repository: IHomeStateSnapshotRepository):
        self.snapshot_repository = snapshot_repository
    
    async def create_snapshot(self, snapshot_data: HomeStateSnapshotCreate) -> HomeStateSnapshotResponse:
        """홈 상태 스냅샷 생성"""
        # Pydantic 스키마를 도메인 엔티티로 변환
        snapshot_entity = HomeStateSnapshot(
            time=snapshot_data.time,
            user_id=snapshot_data.user_id,
            entrance_pir_motion=snapshot_data.entrance_pir_motion,
            entrance_rfid_status=snapshot_data.entrance_rfid_status,
            entrance_reed_is_closed=snapshot_data.entrance_reed_is_closed,
            livingroom_pir_1_motion=snapshot_data.livingroom_pir_1_motion,
            livingroom_pir_2_motion=snapshot_data.livingroom_pir_2_motion,
            livingroom_sound_db=snapshot_data.livingroom_sound_db,
            livingroom_mq7_co_ppm=snapshot_data.livingroom_mq7_co_ppm,
            livingroom_button_state=snapshot_data.livingroom_button_state,
            kitchen_pir_motion=snapshot_data.kitchen_pir_motion,
            kitchen_sound_db=snapshot_data.kitchen_sound_db,
            kitchen_mq5_gas_ppm=snapshot_data.kitchen_mq5_gas_ppm,
            kitchen_loadcell_1_kg=snapshot_data.kitchen_loadcell_1_kg,
            kitchen_loadcell_2_kg=snapshot_data.kitchen_loadcell_2_kg,
            kitchen_button_state=snapshot_data.kitchen_button_state,
            kitchen_buzzer_is_on=snapshot_data.kitchen_buzzer_is_on,
            bedroom_pir_motion=snapshot_data.bedroom_pir_motion,
            bedroom_sound_db=snapshot_data.bedroom_sound_db,
            bedroom_mq7_co_ppm=snapshot_data.bedroom_mq7_co_ppm,
            bedroom_loadcell_kg=snapshot_data.bedroom_loadcell_kg,
            bedroom_button_state=snapshot_data.bedroom_button_state,
            bathroom_pir_motion=snapshot_data.bathroom_pir_motion,
            bathroom_sound_db=snapshot_data.bathroom_sound_db,
            bathroom_temp_celsius=snapshot_data.bathroom_temp_celsius,
            bathroom_button_state=snapshot_data.bathroom_button_state,
            detected_activity=snapshot_data.detected_activity,
            alert_level=snapshot_data.alert_level,
            alert_reason=snapshot_data.alert_reason,
            action_log=snapshot_data.action_log,
            extra_data=snapshot_data.extra_data
        )
        
        # 리포지토리를 통해 저장
        created_snapshot = await self.snapshot_repository.create_snapshot(snapshot_entity)
        
        # 도메인 엔티티를 Pydantic 응답 스키마로 변환
        return HomeStateSnapshotResponse.from_orm(created_snapshot)
    
    async def get_snapshot_by_time_and_user(
        self, time: datetime, user_id: UUID
    ) -> Optional[HomeStateSnapshotResponse]:
        """특정 시간과 사용자의 스냅샷 조회"""
        snapshot = await self.snapshot_repository.get_snapshot_by_time_and_user(time, user_id)
        if snapshot:
            return HomeStateSnapshotResponse.from_orm(snapshot)
        return None
    
    async def get_latest_snapshot_by_user(self, user_id: UUID) -> Optional[HomeStateSnapshotResponse]:
        """사용자의 최신 스냅샷 조회"""
        snapshot = await self.snapshot_repository.get_latest_snapshot_by_user(user_id)
        if snapshot:
            return HomeStateSnapshotResponse.from_orm(snapshot)
        return None
    
    async def get_snapshots_by_user(
        self, user_id: UUID, limit: int = 100
    ) -> List[HomeStateSnapshotResponse]:
        """사용자의 스냅샷 목록 조회"""
        snapshots = await self.snapshot_repository.get_snapshots_by_user(user_id, limit)
        return [HomeStateSnapshotResponse.from_orm(snapshot) for snapshot in snapshots]
    
    async def get_snapshots_by_time_range(
        self, user_id: UUID, start_time: datetime, end_time: datetime
    ) -> List[HomeStateSnapshotResponse]:
        """특정 시간 범위의 스냅샷 조회"""
        snapshots = await self.snapshot_repository.get_snapshots_by_time_range(user_id, start_time, end_time)
        return [HomeStateSnapshotResponse.from_orm(snapshot) for snapshot in snapshots]
    
    async def get_snapshots_by_alert_level(
        self, user_id: UUID, alert_level: str
    ) -> List[HomeStateSnapshotResponse]:
        """특정 경보 수준의 스냅샷 조회"""
        snapshots = await self.snapshot_repository.get_snapshots_by_alert_level(user_id, alert_level)
        return [HomeStateSnapshotResponse.from_orm(snapshot) for snapshot in snapshots]
    
    async def update_snapshot(
        self, time: datetime, user_id: UUID, snapshot_data: HomeStateSnapshotUpdate
    ) -> Optional[HomeStateSnapshotResponse]:
        """스냅샷 업데이트"""
        # None이 아닌 필드만 추출
        update_data = {k: v for k, v in snapshot_data.dict().items() if v is not None}
        
        if not update_data:
            return None
        
        updated_snapshot = await self.snapshot_repository.update_snapshot(time, user_id, update_data)
        if updated_snapshot:
            return HomeStateSnapshotResponse.from_orm(updated_snapshot)
        return None
    
    async def delete_snapshot(self, time: datetime, user_id: UUID) -> bool:
        """스냅샷 삭제"""
        return await self.snapshot_repository.delete_snapshot(time, user_id)
    
    async def get_all_snapshots(
        self, skip: int = 0, limit: int = 100
    ) -> HomeStateSnapshotListResponse:
        """전체 스냅샷 목록 조회 (페이지네이션)"""
        snapshots = await self.snapshot_repository.get_all_snapshots(skip, limit)
        total = len(snapshots)  # 실제로는 전체 개수를 별도로 조회해야 함
        
        return HomeStateSnapshotListResponse(
            items=[HomeStateSnapshotResponse.from_orm(snapshot) for snapshot in snapshots],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 1
        )
    
    async def get_environmental_alerts(
        self, user_id: UUID, start_time: datetime, end_time: datetime
    ) -> List[HomeStateSnapshotResponse]:
        """환경 관련 경보가 있는 스냅샷 조회"""
        snapshots = await self.snapshot_repository.get_environmental_alerts(user_id, start_time, end_time)
        return [HomeStateSnapshotResponse.from_orm(snapshot) for snapshot in snapshots]
    
    async def update_alert_level(
        self, time: datetime, user_id: UUID, alert_level: str, reason: str
    ) -> Optional[HomeStateSnapshotResponse]:
        """경보 수준 업데이트"""
        update_data = {
            "alert_level": alert_level,
            "alert_reason": reason
        }
        
        updated_snapshot = await self.snapshot_repository.update_snapshot(time, user_id, update_data)
        if updated_snapshot:
            return HomeStateSnapshotResponse.from_orm(updated_snapshot)
        return None
    
    async def add_action_log(
        self, time: datetime, user_id: UUID, action: str, result: str, notes: str = None
    ) -> Optional[HomeStateSnapshotResponse]:
        """처리 내역 추가"""
        # 기존 스냅샷 조회
        snapshot = await self.snapshot_repository.get_snapshot_by_time_and_user(time, user_id)
        if not snapshot:
            return None
        
        # 액션 로그 추가
        snapshot.add_action_log(action, result, notes)
        
        # 업데이트
        update_data = {"action_log": snapshot.action_log}
        updated_snapshot = await self.snapshot_repository.update_snapshot(time, user_id, update_data)
        if updated_snapshot:
            return HomeStateSnapshotResponse.from_orm(updated_snapshot)
        return None
