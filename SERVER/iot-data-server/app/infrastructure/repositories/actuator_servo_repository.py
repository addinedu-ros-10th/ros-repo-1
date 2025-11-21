"""
Servo 액추에이터 로그 리포지토리 구현체

Servo 액추에이터 로그 데이터에 대한 데이터 접근 계층을 구현합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.models import ActuatorLogServo
from app.interfaces.repositories.actuator_repository import IActuatorServoRepository


class ActuatorServoRepository(IActuatorServoRepository):
    """Servo 액추에이터 로그 리포지토리 구현체"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def create(self, actuator_data: ActuatorLogServo) -> ActuatorLogServo:
        """Servo 액추에이터 로그 생성"""
        self.db_session.add(actuator_data)
        await self.db_session.commit()
        await self.db_session.refresh(actuator_data)
        return actuator_data
    
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ActuatorLogServo]:
        """ID로 Servo 액추에이터 로그 조회"""
        query = select(ActuatorLogServo).where(
            and_(
                ActuatorLogServo.device_id == device_id,
                ActuatorLogServo.time == timestamp
            )
        )
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_latest(self, device_id: str) -> Optional[ActuatorLogServo]:
        """최신 Servo 액추에이터 로그 조회"""
        query = select(ActuatorLogServo).where(
            ActuatorLogServo.device_id == device_id
        ).order_by(ActuatorLogServo.time.desc()).limit(1)
        result = await self.db_session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_list(
        self, 
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[int] = None,
        angle_deg: Optional[float] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorLogServo]:
        """Servo 액추에이터 로그 목록 조회"""
        conditions = []
        
        if device_id:
            conditions.append(ActuatorLogServo.device_id == device_id)
        if start_time:
            conditions.append(ActuatorLogServo.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogServo.time <= end_time)
        if channel is not None:
            conditions.append(ActuatorLogServo.channel == channel)
        if angle_deg is not None:
            conditions.append(ActuatorLogServo.angle_deg == angle_deg)
        
        query = select(ActuatorLogServo)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ActuatorLogServo.time.desc()).limit(limit).offset(offset)
        result = await self.db_session.execute(query)
        return result.scalars().all()
    
    async def update(
        self, 
        device_id: str, 
        timestamp: datetime, 
        update_data: Dict[str, Any]
    ) -> Optional[ActuatorLogServo]:
        """Servo 액추에이터 로그 수정"""
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
        """Servo 액추에이터 로그 삭제"""
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
        """Servo 액추에이터 로그 통계 조회"""
        conditions = [ActuatorLogServo.device_id == device_id]
        
        if start_time:
            conditions.append(ActuatorLogServo.time >= start_time)
        if end_time:
            conditions.append(ActuatorLogServo.time <= end_time)
        
        # 전체 로그 수
        total_count_query = select(func.count()).where(and_(*conditions))
        total_count_result = await self.db_session.execute(total_count_query)
        total_count = total_count_result.scalar()
        
        # 채널별 통계
        channel_stats_query = select(
            ActuatorLogServo.channel,
            func.count(ActuatorLogServo.channel)
        ).where(and_(*conditions)).group_by(ActuatorLogServo.channel)
        channel_stats_result = await self.db_session.execute(channel_stats_query)
        channel_stats = dict(channel_stats_result.all())
        
        # 각도 통계 (null이 아닌 경우만)
        angle_conditions = conditions + [ActuatorLogServo.angle_deg.isnot(None)]
        angle_stats_query = select(
            func.avg(ActuatorLogServo.angle_deg),
            func.min(ActuatorLogServo.angle_deg),
            func.max(ActuatorLogServo.angle_deg)
        ).where(and_(*angle_conditions))
        angle_stats_result = await self.db_session.execute(angle_stats_query)
        angle_stats = angle_stats_result.fetchone()
        
        # PWM 통계 (null이 아닌 경우만)
        pwm_conditions = conditions + [ActuatorLogServo.pwm_us.isnot(None)]
        pwm_stats_query = select(
            func.avg(ActuatorLogServo.pwm_us),
            func.min(ActuatorLogServo.pwm_us),
            func.max(ActuatorLogServo.pwm_us)
        ).where(and_(*pwm_conditions))
        pwm_stats_result = await self.db_session.execute(pwm_stats_query)
        pwm_stats = pwm_stats_result.fetchone()
        
        return {
            "total_count": total_count,
            "channel_statistics": channel_stats,
            "angle_statistics": {
                "average": float(angle_stats[0]) if angle_stats[0] else None,
                "minimum": float(angle_stats[1]) if angle_stats[1] else None,
                "maximum": float(angle_stats[2]) if angle_stats[2] else None
            },
            "pwm_statistics": {
                "average": float(pwm_stats[0]) if pwm_stats[0] else None,
                "minimum": int(pwm_stats[1]) if pwm_stats[1] else None,
                "maximum": int(pwm_stats[2]) if pwm_stats[2] else None
            }
        }
