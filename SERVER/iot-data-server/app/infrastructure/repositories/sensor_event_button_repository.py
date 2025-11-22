from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.domain.entities.sensor_event_button import SensorEventButton
from app.infrastructure.models import SensorEventButton as SensorEventButtonModel
from app.interfaces.repositories.sensor_event_button_repository import ISensorEventButtonRepository


class SensorEventButtonRepository(ISensorEventButtonRepository):
    """버튼 이벤트 센서 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_button_event(self, button_event: SensorEventButton) -> SensorEventButton:
        """버튼 이벤트 생성"""
        db_button_event = SensorEventButtonModel(
            time=button_event.time,
            device_id=button_event.device_id,
            button_state=button_event.button_state,
            event_type=button_event.event_type,
            press_duration_ms=button_event.press_duration_ms,
            raw_payload=button_event.raw_payload
        )
        
        self.db.add(db_button_event)
        self.db.commit()
        self.db.refresh(db_button_event)
        
        return self._to_domain_entity(db_button_event)
    
    async def get_button_event_by_time_and_device(
        self, time: datetime, device_id: str
    ) -> Optional[SensorEventButton]:
        """특정 시간과 디바이스의 버튼 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.time == time,
                SensorEventButtonModel.device_id == device_id
            )
        )
        data = result.scalar_one_or_none()
        
        if data:
            return self._to_domain_entity(data)
        return None
    
    async def get_latest_button_event_by_device(self, device_id: str) -> Optional[SensorEventButton]:
        """디바이스의 최신 버튼 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.device_id == device_id
            ).order_by(SensorEventButtonModel.time.desc()).limit(1)
        )
        data = result.scalars().first()
        
        if data:
            return self._to_domain_entity(data)
        return None
    
    async def get_button_events_by_device(
        self, device_id: str, limit: int = 100
    ) -> List[SensorEventButton]:
        """디바이스의 버튼 이벤트 목록 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.device_id == device_id
            ).order_by(SensorEventButtonModel.time.desc()).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_button_events_by_event_type(
        self, event_type: str, limit: int = 100
    ) -> List[SensorEventButton]:
        """특정 이벤트 타입의 버튼 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.event_type == event_type
            ).order_by(SensorEventButtonModel.time.desc()).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_button_events_by_button_state(
        self, button_state: str, limit: int = 100
    ) -> List[SensorEventButton]:
        """특정 버튼 상태의 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.button_state == button_state
            ).order_by(SensorEventButtonModel.time.desc()).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_button_events_by_time_range(
        self, device_id: str, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButton]:
        """특정 시간 범위의 버튼 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.device_id == device_id,
                SensorEventButtonModel.time >= start_time,
                SensorEventButtonModel.time <= end_time
            ).order_by(SensorEventButtonModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def update_button_event(
        self, time: datetime, device_id: str, event_data: dict
    ) -> Optional[SensorEventButton]:
        """버튼 이벤트 업데이트"""
        result = self.db.execute(
            update(SensorEventButtonModel).where(
                SensorEventButtonModel.time == time,
                SensorEventButtonModel.device_id == device_id
            ).values(**event_data)
        )
        
        if result.rowcount > 0:
            self.db.commit()
            return await self.get_button_event_by_time_and_device(time, device_id)
        return None
    
    async def delete_button_event(self, time: datetime, device_id: str) -> bool:
        """버튼 이벤트 삭제"""
        result = self.db.execute(
            delete(SensorEventButtonModel).where(
                SensorEventButtonModel.time == time,
                SensorEventButtonModel.device_id == device_id
            )
        )
        
        if result.rowcount > 0:
            self.db.commit()
            return True
        return False
    
    async def get_all_button_events(
        self, skip: int = 0, limit: int = 100
    ) -> List[SensorEventButton]:
        """전체 버튼 이벤트 목록 조회 (페이지네이션)"""
        result = self.db.execute(
            select(SensorEventButtonModel).order_by(
                SensorEventButtonModel.time.desc()
            ).offset(skip).limit(limit)
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def count_button_events_by_device(self, device_id: str) -> int:
        """디바이스의 버튼 이벤트 개수 조회"""
        result = self.db.execute(
            select(func.count(SensorEventButtonModel.time)).where(
                SensorEventButtonModel.device_id == device_id
            )
        )
        return result.scalar()
    
    async def get_crisis_events(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButton]:
        """위기 상황 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.event_type == 'crisis_acknowledged',
                SensorEventButtonModel.time >= start_time,
                SensorEventButtonModel.time <= end_time
            ).order_by(SensorEventButtonModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_assistance_requests(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButton]:
        """도움 요청 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.event_type == 'assistance_request',
                SensorEventButtonModel.time >= start_time,
                SensorEventButtonModel.time <= end_time
            ).order_by(SensorEventButtonModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    async def get_medication_checks(
        self, start_time: datetime, end_time: datetime
    ) -> List[SensorEventButton]:
        """복약 체크 이벤트 조회"""
        result = self.db.execute(
            select(SensorEventButtonModel).where(
                SensorEventButtonModel.event_type == 'medication_check',
                SensorEventButtonModel.time >= start_time,
                SensorEventButtonModel.time <= end_time
            ).order_by(SensorEventButtonModel.time.desc())
        )
        data_list = result.scalars().all()
        
        return [self._to_domain_entity(data) for data in data_list]
    
    def _to_domain_entity(self, db_model: SensorEventButtonModel) -> SensorEventButton:
        """ORM 모델을 도메인 엔티티로 변환"""
        return SensorEventButton(
            time=db_model.time,
            device_id=db_model.device_id,
            button_state=db_model.button_state,
            event_type=db_model.event_type,
            press_duration_ms=db_model.press_duration_ms,
            raw_payload=db_model.raw_payload
        )
