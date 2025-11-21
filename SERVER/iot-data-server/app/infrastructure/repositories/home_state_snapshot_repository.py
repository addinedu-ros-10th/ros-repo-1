from typing import List, Optional
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.domain.entities.home_state_snapshot import HomeStateSnapshot
from app.infrastructure.models import HomeStateSnapshot as HomeStateSnapshotModel
from app.interfaces.repositories.home_state_snapshot_repository import IHomeStateSnapshotRepository


class HomeStateSnapshotRepository(IHomeStateSnapshotRepository):
    """홈 상태 스냅샷 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_snapshot(self, snapshot: HomeStateSnapshot) -> HomeStateSnapshot:
        """홈 상태 스냅샷 생성"""
        db_snapshot = HomeStateSnapshotModel(
            time=snapshot.time,
            user_id=snapshot.user_id,
            entrance_pir_motion=snapshot.entrance_pir_motion,
            entrance_rfid_status=snapshot.entrance_rfid_status,
            entrance_reed_is_closed=snapshot.entrance_reed_is_closed,
            livingroom_pir_1_motion=snapshot.livingroom_pir_1_motion,
            livingroom_pir_2_motion=snapshot.livingroom_pir_2_motion,
            livingroom_sound_db=snapshot.livingroom_sound_db,
            livingroom_mq7_co_ppm=snapshot.livingroom_mq7_co_ppm,
            livingroom_button_state=snapshot.livingroom_button_state,
            kitchen_pir_motion=snapshot.kitchen_pir_motion,
            kitchen_sound_db=snapshot.kitchen_sound_db,
            kitchen_mq5_gas_ppm=snapshot.kitchen_mq5_gas_ppm,
            kitchen_loadcell_1_kg=snapshot.kitchen_loadcell_1_kg,
            kitchen_loadcell_2_kg=snapshot.kitchen_loadcell_2_kg,
            kitchen_button_state=snapshot.kitchen_button_state,
            kitchen_buzzer_is_on=snapshot.kitchen_buzzer_is_on,
            bedroom_pir_motion=snapshot.bedroom_pir_motion,
            bedroom_sound_db=snapshot.bedroom_sound_db,
            bedroom_mq7_co_ppm=snapshot.bedroom_mq7_co_ppm,
            bedroom_loadcell_kg=snapshot.bedroom_loadcell_kg,
            bedroom_button_state=snapshot.bedroom_button_state,
            bathroom_pir_motion=snapshot.bathroom_pir_motion,
            bathroom_sound_db=snapshot.bathroom_sound_db,
            bathroom_temp_celsius=snapshot.bathroom_temp_celsius,
            bathroom_button_state=snapshot.bathroom_button_state,
            detected_activity=snapshot.detected_activity,
            alert_level=snapshot.alert_level,
            alert_reason=snapshot.alert_reason,
            action_log=snapshot.action_log,
            extra_data=snapshot.extra_data
        )
        
        self.db.add(db_snapshot)
        self.db.commit()
        self.db.refresh(db_snapshot)
        
        return self._to_domain_entity(db_snapshot)
    
    async def get_snapshot_by_time_and_user(
        self, time: datetime, user_id: UUID
    ) -> Optional[HomeStateSnapshot]:
        """특정 시간과 사용자의 스냅샷 조회"""
        result = self.db.execute(
            select(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.time == time,
                HomeStateSnapshotModel.user_id == user_id
            )
        )
        data = result.scalar_one_or_none()
        
        if data:
            return self._to_domain_entity(data)
        return None
    
    async def get_latest_snapshot_by_user(self, user_id: UUID) -> Optional[HomeStateSnapshot]:
        """사용자의 최신 스냅샷 조회"""
        result = self.db.execute(
            select(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.user_id == user_id
            ).order_by(HomeStateSnapshotModel.time.desc()).limit(1)
        )
        data = result.scalars().first()
        
        if data:
            return self._to_domain_entity(data)
        return None
    
    async def get_snapshots_by_user(
        self, user_id: UUID, limit: int = 100
    ) -> List[HomeStateSnapshot]:
        """사용자의 스냅샷 목록 조회"""
        result = self.db.execute(
            select(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.user_id == user_id
            ).order_by(HomeStateSnapshotModel.time.desc()).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_snapshots_by_time_range(
        self, user_id: UUID, start_time: datetime, end_time: datetime
    ) -> List[HomeStateSnapshot]:
        """특정 시간 범위의 스냅샷 조회"""
        result = self.db.execute(
            select(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.user_id == user_id,
                HomeStateSnapshotModel.time >= start_time,
                HomeStateSnapshotModel.time <= end_time
            ).order_by(HomeStateSnapshotModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_snapshots_by_alert_level(
        self, user_id: UUID, alert_level: str
    ) -> List[HomeStateSnapshot]:
        """특정 경보 수준의 스냅샷 조회"""
        result = self.db.execute(
            select(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.user_id == user_id,
                HomeStateSnapshotModel.alert_level == alert_level
            ).order_by(HomeStateSnapshotModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def update_snapshot(
        self, time: datetime, user_id: UUID, snapshot_data: dict
    ) -> Optional[HomeStateSnapshot]:
        """스냅샷 업데이트"""
        result = self.db.execute(
            update(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.time == time,
                HomeStateSnapshotModel.user_id == user_id
            ).values(**snapshot_data)
        )
        
        if result.rowcount > 0:
            self.db.commit()
            return await self.get_snapshot_by_time_and_user(time, user_id)
        return None
    
    async def delete_snapshot(self, time: datetime, user_id: UUID) -> bool:
        """스냅샷 삭제"""
        result = self.db.execute(
            delete(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.time == time,
                HomeStateSnapshotModel.user_id == user_id
            )
        )
        
        if result.rowcount > 0:
            self.db.commit()
            return True
        return False
    
    async def get_all_snapshots(
        self, skip: int = 0, limit: int = 100
    ) -> List[HomeStateSnapshot]:
        """전체 스냅샷 목록 조회 (페이지네이션)"""
        result = self.db.execute(
            select(HomeStateSnapshotModel).order_by(
                HomeStateSnapshotModel.time.desc()
            ).offset(skip).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def count_snapshots_by_user(self, user_id: UUID) -> int:
        """사용자의 스냅샷 개수 조회"""
        result = self.db.execute(
            select(func.count(HomeStateSnapshotModel.time)).where(
                HomeStateSnapshotModel.user_id == user_id
            )
        )
        return result.scalar()
    
    async def get_environmental_alerts(
        self, user_id: UUID, start_time: datetime, end_time: datetime
    ) -> List[HomeStateSnapshot]:
        """환경 관련 경보가 있는 스냅샷 조회"""
        result = self.db.execute(
            select(HomeStateSnapshotModel).where(
                HomeStateSnapshotModel.user_id == user_id,
                HomeStateSnapshotModel.time >= start_time,
                HomeStateSnapshotModel.time <= end_time,
                HomeStateSnapshotModel.alert_level.in_(['Warning', 'Emergency'])
            ).order_by(HomeStateSnapshotModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    def _to_domain_entity(self, db_model: HomeStateSnapshotModel) -> HomeStateSnapshot:
        """ORM 모델을 도메인 엔티티로 변환"""
        return HomeStateSnapshot(
            time=db_model.time,
            user_id=db_model.user_id,
            entrance_pir_motion=db_model.entrance_pir_motion,
            entrance_rfid_status=db_model.entrance_rfid_status,
            entrance_reed_is_closed=db_model.entrance_reed_is_closed,
            livingroom_pir_1_motion=db_model.livingroom_pir_1_motion,
            livingroom_pir_2_motion=db_model.livingroom_pir_2_motion,
            livingroom_sound_db=db_model.livingroom_sound_db,
            livingroom_mq7_co_ppm=db_model.livingroom_mq7_co_ppm,
            livingroom_button_state=db_model.livingroom_button_state,
            kitchen_pir_motion=db_model.kitchen_pir_motion,
            kitchen_sound_db=db_model.kitchen_sound_db,
            kitchen_mq5_gas_ppm=db_model.kitchen_mq5_gas_ppm,
            kitchen_loadcell_1_kg=db_model.kitchen_loadcell_1_kg,
            kitchen_loadcell_2_kg=db_model.kitchen_loadcell_2_kg,
            kitchen_button_state=db_model.kitchen_button_state,
            kitchen_buzzer_is_on=db_model.kitchen_buzzer_is_on,
            bedroom_pir_motion=db_model.bedroom_pir_motion,
            bedroom_sound_db=db_model.bedroom_sound_db,
            bedroom_mq7_co_ppm=db_model.bedroom_mq7_co_ppm,
            bedroom_loadcell_kg=db_model.bedroom_loadcell_kg,
            bedroom_button_state=db_model.bedroom_button_state,
            bathroom_pir_motion=db_model.bathroom_pir_motion,
            bathroom_sound_db=db_model.bathroom_sound_db,
            bathroom_temp_celsius=db_model.bathroom_temp_celsius,
            bathroom_button_state=db_model.bathroom_button_state,
            detected_activity=db_model.detected_activity,
            alert_level=db_model.alert_level,
            alert_reason=db_model.alert_reason,
            action_log=db_model.action_log,
            extra_data=db_model.extra_data
        )
