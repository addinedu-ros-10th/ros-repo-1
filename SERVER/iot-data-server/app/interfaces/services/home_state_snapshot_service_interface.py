from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from app.api.v1.schemas import (
    HomeStateSnapshotCreate, HomeStateSnapshotUpdate, 
    HomeStateSnapshotResponse, HomeStateSnapshotListResponse
)


class IHomeStateSnapshotService(ABC):
    """홈 상태 스냅샷 서비스 인터페이스"""
    
    @abstractmethod
    async def create_snapshot(self, snapshot_data: HomeStateSnapshotCreate) -> HomeStateSnapshotResponse:
        """홈 상태 스냅샷 생성"""
        pass
    
    @abstractmethod
    async def get_snapshot_by_time_and_user(
        self, time: datetime, user_id: UUID
    ) -> Optional[HomeStateSnapshotResponse]:
        """특정 시간과 사용자의 스냅샷 조회"""
        pass
    
    @abstractmethod
    async def get_latest_snapshot_by_user(self, user_id: UUID) -> Optional[HomeStateSnapshotResponse]:
        """사용자의 최신 스냅샷 조회"""
        pass
    
    @abstractmethod
    async def get_snapshots_by_user(
        self, user_id: UUID, limit: int = 100
    ) -> List[HomeStateSnapshotResponse]:
        """사용자의 스냅샷 목록 조회"""
        pass
    
    @abstractmethod
    async def get_snapshots_by_time_range(
        self, user_id: UUID, start_time: datetime, end_time: datetime
    ) -> List[HomeStateSnapshotResponse]:
        """특정 시간 범위의 스냅샷 조회"""
        pass
    
    @abstractmethod
    async def get_snapshots_by_alert_level(
        self, user_id: UUID, alert_level: str
    ) -> List[HomeStateSnapshotResponse]:
        """특정 경보 수준의 스냅샷 조회"""
        pass
    
    @abstractmethod
    async def update_snapshot(
        self, time: datetime, user_id: UUID, snapshot_data: HomeStateSnapshotUpdate
    ) -> Optional[HomeStateSnapshotResponse]:
        """스냅샷 업데이트"""
        pass
    
    @abstractmethod
    async def delete_snapshot(self, time: datetime, user_id: UUID) -> bool:
        """스냅샷 삭제"""
        pass
    
    @abstractmethod
    async def get_all_snapshots(
        self, skip: int = 0, limit: int = 100
    ) -> HomeStateSnapshotListResponse:
        """전체 스냅샷 목록 조회 (페이지네이션)"""
        pass
    
    @abstractmethod
    async def get_environmental_alerts(
        self, user_id: UUID, start_time: datetime, end_time: datetime
    ) -> List[HomeStateSnapshotResponse]:
        """환경 관련 경보가 있는 스냅샷 조회"""
        pass
    
    @abstractmethod
    async def update_alert_level(
        self, time: datetime, user_id: UUID, alert_level: str, reason: str
    ) -> Optional[HomeStateSnapshotResponse]:
        """경보 수준 업데이트"""
        pass
    
    @abstractmethod
    async def add_action_log(
        self, time: datetime, user_id: UUID, action: str, result: str, notes: str = None
    ) -> Optional[HomeStateSnapshotResponse]:
        """처리 내역 추가"""
        pass
