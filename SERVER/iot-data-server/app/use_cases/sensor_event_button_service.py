from typing import List, Optional
from datetime import datetime
from app.interfaces.services.sensor_event_button_service_interface import ISensorEventButtonService
from app.interfaces.repositories.sensor_event_button_repository import ISensorEventButtonRepository
from app.domain.entities.sensor_event_button import SensorEventButton
from app.api.v1.schemas import (
    SensorEventButtonCreate, SensorEventButtonUpdate,
    SensorEventButtonResponse, SensorEventButtonListResponse
)


class SensorEventButtonService(ISensorEventButtonService):
    """버튼 이벤트 센서 서비스 구현체"""
    
    def __init__(self, button_event_repository: ISensorEventButtonRepository):
        self.button_event_repository = button_event_repository
    
    async def create_button_event(self, button_event_data: SensorEventButtonCreate) -> SensorEventButtonResponse:
        """버튼 이벤트 생성"""
        # Pydantic 스키마를 도메인 엔티티로 변환
        button_event_entity = SensorEventButton(
            time=button_event_data.time,
            device_id=button_event_data.device_id,
            button_state=button_event_data.button_state,
            event_type=button_event_data.event_type,
            press_duration_ms=button_event_data.press_duration_ms,
            raw_payload=button_event_data.raw_payload
        )
        
        # 리포지토리를 통해 저장
        created_event = await self.button_event_repository.create_button_event(button_event_entity)
        
        # 도메인 엔티티를 Pydantic 응답 스키마로 변환
        return SensorEventButtonResponse.from_orm(created_event)
    
    async def get_button_event_by_time_and_device(
        self, time: datetime, device_id: str
    ) -> Optional[SensorEventButtonResponse]:
        """특정 시간과 디바이스의 버튼 이벤트 조회"""
        event = await self.button_event_repository.get_button_event_by_time_and_device(time, device_id)
        if event:
            return SensorEventButtonResponse.from_orm(event)
        return None
    
    async def get_latest_button_event_by_device(self, device_id: str) -> Optional[SensorEventButtonResponse]:
        """디바이스의 최신 버튼 이벤트 조회"""
        event = await self.button_event_repository.get_latest_button_event_by_device(device_id)
        if event:
            return SensorEventButtonResponse.from_orm(event)
        return None
    
    async def get_button_events_by_device(
        self, device_id: str, limit: int = 100
    ) -> List[SensorEventButtonResponse]:
        """디바이스의 버튼 이벤트 목록 조회"""
        events = await self.button_event_repository.get_button_events_by_device(device_id, limit)
        return [SensorEventButtonResponse.from_orm(event) for event in events]
    
    async def get_button_events_by_event_type(
        self, event_type: str, limit: int = 100
    ) -> List[SensorEventButtonResponse]:
        """특정 이벤트 타입의 버튼 이벤트 조회"""
        events = await self.button_event_repository.get_button_events_by_event_type(event_type, limit)
        return [SensorEventButtonResponse.from_orm(event) for event in events]
    
    async def get_button_events_by_button_state(
        self, button_state: str, limit: int = 100
    ) -> List[SensorEventButtonResponse]:
        """특정 버튼 상태의 이벤트 조회"""
        events = await self.button_event_repository.get_button_events_by_button_state(button_state, limit)
        return [SensorEventButtonResponse.from_orm(event) for event in events]
    
    async def get_button_events_by_time_range(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """특정 시간 범위의 버튼 이벤트 조회"""
        events = await self.button_event_repository.get_button_events_by_time_range(device_id, start_time, end_time)
        return [SensorEventButtonResponse.from_orm(event) for event in events]
    
    async def update_button_event(
        self, time: datetime, device_id: str, event_data: SensorEventButtonUpdate
    ) -> Optional[SensorEventButtonResponse]:
        """버튼 이벤트 업데이트"""
        # None이 아닌 필드만 추출
        update_data = {k: v for k, v in event_data.dict().items() if v is not None}
        
        if not update_data:
            return None
        
        updated_event = await self.button_event_repository.update_button_event(time, device_id, update_data)
        if updated_event:
            return SensorEventButtonResponse.from_orm(updated_event)
        return None
    
    async def delete_button_event(self, time: datetime, device_id: str) -> bool:
        """버튼 이벤트 삭제"""
        return await self.button_event_repository.delete_button_event(time, device_id)
    
    async def get_all_button_events(
        self, skip: int = 0, limit: int = 100
    ) -> SensorEventButtonListResponse:
        """전체 버튼 이벤트 목록 조회 (페이지네이션)"""
        events = await self.button_event_repository.get_all_button_events(skip, limit)
        total = len(events)  # 실제로는 전체 개수를 별도로 조회해야 함
        
        return SensorEventButtonListResponse(
            items=[SensorEventButtonResponse.from_orm(event) for event in events],
            total=total,
            page=skip // limit + 1 if limit > 0 else 1,
            size=limit,
            pages=(total + limit - 1) // limit if limit > 0 else 1
        )
    
    async def get_crisis_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """위기 상황 이벤트 조회"""
        events = await self.button_event_repository.get_crisis_events(start_time, end_time)
        return [SensorEventButtonResponse.from_orm(event) for event in events]
    
    async def get_assistance_requests(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """도움 요청 이벤트 조회"""
        events = await self.button_event_repository.get_assistance_requests(start_time, end_time)
        return [SensorEventButtonResponse.from_orm(event) for event in events]
    
    async def get_medication_checks(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """복약 체크 이벤트 조회"""
        events = await self.button_event_repository.get_medication_checks(start_time, end_time)
        return [SensorEventButtonResponse.from_orm(event) for event in events]
    
    async def get_high_priority_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButtonResponse]:
        """높은 우선순위 이벤트 조회"""
        # 위기 상황과 도움 요청 이벤트를 조회하여 우선순위별로 정렬
        crisis_events = await self.button_event_repository.get_crisis_events(start_time, end_time)
        assistance_events = await self.button_event_repository.get_assistance_requests(start_time, end_time)
        
        # 우선순위별로 정렬 (위기 상황 > 도움 요청)
        high_priority_events = []
        
        # 위기 상황 이벤트 추가 (우선순위 3)
        for event in crisis_events:
            high_priority_events.append((event, 3))
        
        # 도움 요청 이벤트 추가 (우선순위 2)
        for event in assistance_events:
            high_priority_events.append((event, 2))
        
        # 우선순위 내림차순으로 정렬
        high_priority_events.sort(key=lambda x: x[1], reverse=True)
        
        # 이벤트만 반환
        return [SensorEventButtonResponse.from_orm(event) for event, _ in high_priority_events]
