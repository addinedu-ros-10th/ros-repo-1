"""
Buzzer 액추에이터 로그 리포지토리 구현체

Buzzer 액추에이터 로그 데이터에 대한 데이터 접근 계층을 구현합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import ActuatorLogBuzzer
from app.interfaces.repositories.actuator_repository import IActuatorBuzzerRepository


class ActuatorBuzzerRepository(IActuatorBuzzerRepository):
    """Buzzer 액추에이터 로그 리포지토리 구현체"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(self, actuator_data: ActuatorLogBuzzer) -> ActuatorLogBuzzer:
        """Buzzer 액추에이터 로그 생성"""
        self.db_session.add(actuator_data)
        await self.db_session.commit()
        await self.db_session.refresh(actuator_data)
        return actuator_data
    
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogBuzzer]:
        """ID로 Buzzer 액추에이터 로그 조회"""
        query = select(ActuatorLogBuzzer).where(
            and_(
                ActuatorLogBuzzer.device_id == device_id,
                ActuatorLogBuzzer.time == timestamp
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogBuzzer]:
        """최신 Buzzer 액추에이터 로그 조회"""
        query = select(ActuatorLogBuzzer).where(
            ActuatorLogBuzzer.device_id == device_id
        ).order_by(ActuatorLogBuzzer.time.desc()).limit(1)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        buzzer_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogBuzzer]:
        """Buzzer 액추에이터 로그 목록 조회"""
        conditions = []
        
        if device_id:
            conditions.append(ActuatorLogBuzzer.device_id == device_id)
        if start_time:
            conditions.append(ActuatorLogBuzzer.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogBuzzer.time <= end_time)
        if buzzer_type:
            conditions.append(ActuatorLogBuzzer.buzzer_type == buzzer_type)
        if state:
            conditions.append(ActuatorLogBuzzer.state == state)
        
        query = select(ActuatorLogBuzzer)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ActuatorLogBuzzer.time.desc()).limit(limit).offset(offset)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogBuzzer]:
        """Buzzer 액추에이터 로그 수정"""
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
        """Buzzer 액추에이터 로그 삭제"""
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
        """Buzzer 액추에이터 로그 통계 조회"""
        conditions = [ActuatorLogBuzzer.device_id == device_id]
        
        if start_time:
            conditions.append(ActuatorLogBuzzer.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogBuzzer.time <= end_time)
        
        # 전체 로그 수
        total_count_query = select(func.count()).where(and_(*conditions))
        total_count_result = await self.db_session.execute(total_count_query)
        total_count = total_count_result.scalar()
        
        # 상태별 통계
        state_stats_query = select(
            ActuatorLogBuzzer.state,
            func.count(ActuatorLogBuzzer.state)
        ).where(and_(*conditions)).group_by(ActuatorLogBuzzer.state)
        state_stats_result = await self.db_session.execute(state_stats_query)
        state_stats = dict(state_stats_result.all())
        
        # 부저 타입별 통계
        type_stats_query = select(
            ActuatorLogBuzzer.buzzer_type,
            func.count(ActuatorLogBuzzer.buzzer_type)
        ).where(and_(*conditions)).group_by(ActuatorLogBuzzer.buzzer_type)
        type_stats_result = await self.db_session.execute(type_stats_query)
        type_stats = dict(type_stats_result.all())
        
        # 주파수 통계 (null이 아닌 경우만)
        freq_conditions = conditions + [ActuatorLogBuzzer.freq_hz.isnot(None)]
        freq_stats_query = select(
            func.avg(ActuatorLogBuzzer.freq_hz),
            func.min(ActuatorLogBuzzer.freq_hz),
            func.max(ActuatorLogBuzzer.freq_hz)
        ).where(and_(*freq_conditions))
        freq_stats_result = await self.db_session.execute(freq_stats_query)
        freq_stats = freq_stats_result.fetchone()
        
        # 지속시간 통계 (null이 아닌 경우만)
        duration_conditions = conditions + [ActuatorLogBuzzer.duration_ms.isnot(None)]
        duration_stats_query = select(
            func.avg(ActuatorLogBuzzer.duration_ms),
            func.min(ActuatorLogBuzzer.duration_ms),
            func.max(ActuatorLogBuzzer.duration_ms)
        ).where(and_(*duration_conditions))
        duration_stats_result = await self.db_session.execute(duration_stats_query)
        duration_stats = duration_stats_result.fetchone()
        
        return {
            "total_count": total_count,
            "state_statistics": state_stats,
            "buzzer_type_statistics": type_stats,
            "frequency_statistics": {
                "average": float(freq_stats[0]) if freq_stats[0] else None,
                "minimum": int(freq_stats[1]) if freq_stats[1] else None,
                "maximum": int(freq_stats[2]) if freq_stats[2] else None
            },
            "duration_statistics": {
                "average": float(duration_stats[0]) if duration_stats[0] else None,
                "minimum": int(duration_stats[1]) if duration_stats[1] else None,
                "maximum": int(duration_stats[2]) if duration_stats[2] else None
            }
        }
