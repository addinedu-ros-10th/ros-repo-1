from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.api.v1.schemas import (
    SensorEventButtonCreate, SensorEventButtonUpdate,
    SensorEventButtonResponse, SensorEventButtonListResponse
)


class ISensorEventButtonService(ABC):
    """버튼 이벤트 센서 서비스 인터페이스"""
    
    @abstractmethod
    async def create_button_event(self, button_event_data: SensorEventButtonCreate) -> SensorEventButtonResponse:
        """버튼 이벤트 생성"""
        pass
    
    @abstractmethod
    async def get_button_event_by_time_and_device(
        self, time: datetime, device_id: str
    ) -> Optional[SensorEventButtonResponse]:
        """특정 시간과 디바이스의 버튼 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_latest_button_event_by_device(self, device_id: str) -> Optional[SensorEventButtonResponse]:
        """디바이스의 최신 버튼 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_button_events_by_device(
        self, device_id: str, limit: int = 100
    ) -> List[SensorEventButtonResponse]:
        """디바이스의 버튼 이벤트 목록 조회"""
        pass
    
    @abstractmethod
    async def get_button_events_by_event_type(
        self, event_type: str, limit: int = 100
    ) -> List[SensorEventButtonResponse]:
        """특정 이벤트 타입의 버튼 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_button_events_by_button_state(
        self, button_state: str, limit: int = 100
    ) -> List[SensorEventButtonResponse]:
        """특정 버튼 상태의 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_button_events_by_time_range(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """특정 시간 범위의 버튼 이벤트 조회"""
        pass
    
    @abstractmethod
    async def update_button_event(
        self, time: datetime, device_id: str, event_data: SensorEventButtonUpdate
    ) -> Optional[SensorEventButtonResponse]:
        """버튼 이벤트 업데이트"""
        pass
    
    @abstractmethod
    async def delete_button_event(self, time: datetime, device_id: str) -> bool:
        """버튼 이벤트 삭제"""
        pass
    
    @abstractmethod
    async def get_all_button_events(
        self, skip: int = 0, limit: int = 100
    ) -> SensorEventButtonListResponse:
        """전체 버튼 이벤트 목록 조회 (페이지네이션)"""
        pass
    
    @abstractmethod
    async def get_crisis_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """위기 상황 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_assistance_requests(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """도움 요청 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_medication_checks(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """복약 체크 이벤트 조회"""
        pass
    
    @abstractmethod
    async def get_high_priority_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """높은 우선순위 이벤트 조회"""
        pass
