"""
Relay 액추에이터 로그 리포지토리 구현체

Relay 액추에이터 로그 데이터에 대한 데이터 접근 계층을 구현합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import ActuatorLogRelay
from app.interfaces.repositories.actuator_repository import IActuatorRelayRepository


class ActuatorRelayRepository(IActuatorRelayRepository):
    """Relay 액추에이터 로그 리포지토리 구현체"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(self, actuator_data: ActuatorLogRelay) -> ActuatorLogRelay:
        """Relay 액추에이터 로그 생성"""
        self.db_session.add(actuator_data)
        await self.db_session.commit()
        await self.db_session.refresh(actuator_data)
        return actuator_data
    
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogRelay]:
        """ID로 Relay 액추에이터 로그 조회"""
        query = select(ActuatorLogRelay).where(
            and_(
                ActuatorLogRelay.device_id == device_id,
                ActuatorLogRelay.time == timestamp
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogRelay]:
        """최신 Relay 액추에이터 로그 조회"""
        query = select(ActuatorLogRelay).where(
            ActuatorLogRelay.device_id == device_id
        ).order_by(ActuatorLogRelay.time.desc()).limit(1)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogRelay]:
        """Relay 액추에이터 로그 목록 조회"""
        conditions = []
        
        if device_id:
            conditions.append(ActuatorLogRelay.device_id == device_id)
        if start_time:
            conditions.append(ActuatorLogRelay.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogRelay.time <= end_time)
        if channel is not None:
            conditions.append(ActuatorLogRelay.channel == channel)
        if state:
            conditions.append(ActuatorLogRelay.state == state)
        
        query = select(ActuatorLogRelay)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ActuatorLogRelay.time.desc()).limit(limit).offset(offset)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogRelay]:
        """Relay 액추에이터 로그 수정"""
        actuator_data = await self.get_by_id(device_id, timestamp)
        if not actuator_data:
            return None
        
        for key, value in update_data.items():
            if hasattr(actuator_data, key):
                setattr(actuator_data, key, value)
        
        await self.db_session.commit()
        await self.db_session.refresh(actuator_data)
        return actuator_data
    
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """Relay 액추에이터 로그 삭제"""
        actuator_data = await self.get_by_id(device_id, timestamp)
        if not actuator_data:
            return False
        
        await self.db_session.delete(actuator_data)
        await self.db_session.commit()
        return True
    
    async def get_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Relay 액추에이터 로그 통계 조회"""
        conditions = [ActuatorLogRelay.device_id == device_id]
        
        if start_time:
            conditions.append(ActuatorLogRelay.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogRelay.time <= end_time)
        
        # 전체 로그 수
        total_count_query = select(func.count()).where(and_(*conditions))
        total_count_result = await self.db_session.execute(total_count_query)
        total_count = total_count_result.scalar()
        
        # 상태별 통계
        state_stats_query = select(
            ActuatorLogRelay.state,
            func.count(ActuatorLogRelay.state)
        ).where(and_(*conditions)).group_by(ActuatorLogRelay.state)
        state_stats_result = await self.db_session.execute(state_stats_query)
        state_stats = dict(state_stats_result.all())
        
        # 채널별 통계
        channel_stats_query = select(
            ActuatorLogRelay.channel,
            func.count(ActuatorLogRelay.channel)
        ).where(and_(*conditions)).group_by(ActuatorLogRelay.channel)
        channel_stats_result = await self.db_session.execute(channel_stats_query)
        channel_stats = dict(channel_stats_result.all())
        
        return {
            "total_count": total_count,
            "state_statistics": state_stats,
            "channel_statistics": channel_stats
        }
