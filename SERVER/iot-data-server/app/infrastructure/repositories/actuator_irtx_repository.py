"""
IR TX 액추에이터 로그 리포지토리 구현체

IR TX 액추에이터 로그 데이터에 대한 데이터 접근 계층을 구현합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import ActuatorLogIRTX
from app.interfaces.repositories.actuator_repository import IActuatorIRTXRepository


class ActuatorIRTXRepository(IActuatorIRTXRepository):
    """IR TX 액추에이터 로그 리포지토리 구현체"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(self, actuator_data: ActuatorLogIRTX) -> ActuatorLogIRTX:
        """IR TX 액추에이터 로그 생성"""
        self.db_session.add(actuator_data)
        await self.db_session.commit()
        await self.db_session.refresh(actuator_data)
        return actuator_data
    
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogIRTX]:
        """ID로 IR TX 액추에이터 로그 조회"""
        query = select(ActuatorLogIRTX).where(
            and_(
                ActuatorLogIRTX.device_id == device_id,
                ActuatorLogIRTX.time == timestamp
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogIRTX]:
        """최신 IR TX 액추에이터 로그 조회"""
        query = select(ActuatorLogIRTX).where(
            ActuatorLogIRTX.device_id == device_id
        ).order_by(ActuatorLogIRTX.time.desc()).limit(1)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        protocol: Optional[str] = None,
        command_hex: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogIRTX]:
        """IR TX 액추에이터 로그 목록 조회"""
        conditions = []
        
        if device_id:
            conditions.append(ActuatorLogIRTX.device_id == device_id)
        if start_time:
            conditions.append(ActuatorLogIRTX.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogIRTX.time <= end_time)
        if protocol:
            conditions.append(ActuatorLogIRTX.protocol == protocol)
        if command_hex:
            conditions.append(ActuatorLogIRTX.command_hex == command_hex)
        
        query = select(ActuatorLogIRTX)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ActuatorLogIRTX.time.desc()).limit(limit).offset(offset)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogIRTX]:
        """IR TX 액추에이터 로그 수정"""
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
        """IR TX 액추에이터 로그 삭제"""
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
        """IR TX 액추에이터 로그 통계 조회"""
        conditions = [ActuatorLogIRTX.device_id == device_id]
        
        if start_time:
            conditions.append(ActuatorLogIRTX.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogIRTX.time <= end_time)
        
        # 전체 로그 수
        total_count_query = select(func.count()).where(and_(*conditions))
        total_count_result = await self.db_session.execute(total_count_query)
        total_count = total_count_result.scalar()
        
        # 프로토콜별 통계
        protocol_stats_query = select(
            ActuatorLogIRTX.protocol,
            func.count(ActuatorLogIRTX.protocol)
        ).where(and_(*conditions)).group_by(ActuatorLogIRTX.protocol)
        protocol_stats_result = await self.db_session.execute(protocol_stats_query)
        protocol_stats = dict(protocol_stats_result.all())
        
        # 명령어별 통계
        command_stats_query = select(
            ActuatorLogIRTX.command_hex,
            func.count(ActuatorLogIRTX.command_hex)
        ).where(and_(*conditions)).group_by(ActuatorLogIRTX.command_hex)
        command_stats_result = await self.db_session.execute(command_stats_query)
        command_stats = dict(command_stats_result.all())
        
        # 반복 횟수 통계 (null이 아닌 경우만)
        repeat_conditions = conditions + [ActuatorLogIRTX.repeat_cnt.isnot(None)]
        repeat_stats_query = select(
            func.avg(ActuatorLogIRTX.repeat_cnt),
            func.min(ActuatorLogIRTX.repeat_cnt),
            func.max(ActuatorLogIRTX.repeat_cnt)
        ).where(and_(*repeat_conditions))
        repeat_stats_result = await self.db_session.execute(repeat_stats_query)
        repeat_stats = repeat_stats_result.fetchone()
        
        return {
            "total_count": total_count,
            "protocol_statistics": protocol_stats,
            "command_statistics": command_stats,
            "repeat_count_statistics": {
                "average": float(repeat_stats[0]) if repeat_stats[0] else None,
                "minimum": int(repeat_stats[1]) if repeat_stats[1] else None,
                "maximum": int(repeat_stats[2]) if repeat_stats[2] else None
            }
        }
