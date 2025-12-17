"""
Relay 액추에이터 로그 서비스 구현체

Relay 액추에이터 로그 데이터에 대한 비즈니스 로직을 구현합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import HTTPException
from app.infrastructure.models import ActuatorLogRelay
from app.interfaces.repositories.actuator_repository import IActuatorRelayRepository
from app.interfaces.services.actuator_service_interface import IActuatorRelayService
from app.api.v1.schemas import (
    ActuatorRelayDataCreate, ActuatorRelayDataUpdate, ActuatorRelayDataResponse
)


class ActuatorRelayService(IActuatorRelayService):
    """Relay 액추에이터 로그 서비스 구현체"""
    
    def __init__(self, repository: IActuatorRelayRepository):
        self.repository = repository
    
    async def create_actuator_data(self, data: ActuatorRelayDataCreate) -> ActuatorRelayDataResponse:
        """Relay 액추에이터 로그 생성"""
        # 비즈니스 로직 검증
        await self._validate_relay_data(data)
        
        # ORM 모델 생성
        actuator_data = ActuatorLogRelay(
            time=data.time,
            device_id=data.device_id,
            channel=data.channel,
            state=data.state,
            reason=data.reason,
            raw_payload=data.raw_payload
        )
        
        # 리포지토리를 통한 데이터 저장
        created_data = await self.repository.create(actuator_data)
        
        # 응답 스키마로 변환
        return ActuatorRelayDataResponse(
            time=created_data.time,
            device_id=created_data.device_id,
            channel=created_data.channel,
            state=created_data.state,
            reason=created_data.reason,
            raw_payload=created_data.raw_payload
        )
    
    async def get_actuator_data(self, device_id: str, timestamp: datetime) -> Optional[ActuatorRelayDataResponse]:
        """Relay 액추에이터 로그 조회"""
        actuator_data = await self.repository.get_by_id(device_id, timestamp)
        if not actuator_data:
            return None
        
        return ActuatorRelayDataResponse(
            time=actuator_data.time,
            device_id=actuator_data.device_id,
            channel=actuator_data.channel,
            state=actuator_data.state,
            reason=actuator_data.reason,
            raw_payload=actuator_data.raw_payload
        )
    
    async def get_latest_actuator_data(self, device_id: str) -> Optional[ActuatorRelayDataResponse]:
        """최신 Relay 액추에이터 로그 조회"""
        actuator_data = await self.repository.get_latest(device_id)
        if not actuator_data:
            return None
        
        return ActuatorRelayDataResponse(
            time=actuator_data.time,
            device_id=actuator_data.device_id,
            channel=actuator_data.channel,
            state=actuator_data.state,
            reason=actuator_data.reason,
            raw_payload=actuator_data.raw_payload
        )
    
    async def get_actuator_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        channel: Optional[int] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorRelayDataResponse]:
        """Relay 액추에이터 로그 목록 조회"""
        # 비즈니스 로직 검증
        if limit > 1000:
            raise HTTPException(status_code=400, detail="최대 1000개까지 조회 가능합니다")
        
        actuator_data_list = await self.repository.get_list(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            channel=channel,
            state=state,
            limit=limit,
            offset=offset
        )
        
        # 응답 스키마로 변환
        return [
            ActuatorRelayDataResponse(
                time=data.time,
                device_id=data.device_id,
                channel=data.channel,
                state=data.state,
                reason=data.reason,
                raw_payload=data.raw_payload
            )
            for data in actuator_data_list
        ]
    
    async def update_actuator_data(
        self, 
        device_id: str, 
        timestamp: datetime, 
        data: ActuatorRelayDataUpdate
    ) -> Optional[ActuatorRelayDataResponse]:
        """Relay 액추에이터 로그 수정"""
        # 업데이트할 데이터 검증
        update_data = {}
        if data.channel is not None:
            update_data['channel'] = data.channel
        if data.state is not None:
            update_data['state'] = data.state
        if data.reason is not None:
            update_data['reason'] = data.reason
        if data.raw_payload is not None:
            update_data['raw_payload'] = data.raw_payload
        
        if not update_data:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다")
        
        # 리포지토리를 통한 데이터 수정
        updated_data = await self.repository.update(device_id, timestamp, update_data)
        if not updated_data:
            raise HTTPException(status_code=404, detail="액추에이터 로그를 찾을 수 없습니다")
        
        # 응답 스키마로 변환
        return ActuatorRelayDataResponse(
            time=updated_data.time,
            device_id=updated_data.device_id,
            channel=updated_data.channel,
            state=updated_data.state,
            reason=updated_data.reason,
            raw_payload=updated_data.raw_payload
        )
    
    async def delete_actuator_data(self, device_id: str, timestamp: datetime) -> bool:
        """Relay 액추에이터 로그 삭제"""
        success = await self.repository.delete(device_id, timestamp)
        if not success:
            raise HTTPException(status_code=404, detail="액추에이터 로그를 찾을 수 없습니다")
        return success
    
    async def get_actuator_statistics(
        self, 
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Relay 액추에이터 로그 통계 조회"""
        return await self.repository.get_statistics(device_id, start_time, end_time)
    
    async def _validate_relay_data(self, data: ActuatorRelayDataCreate) -> None:
        """Relay 데이터 비즈니스 로직 검증"""
        # 채널 검증
        if data.channel < 1 or data.channel > 16:
            raise HTTPException(
                status_code=400, 
                detail="채널은 1 ~ 16 범위 내에 있어야 합니다"
            )
        
        # 상태 검증
        valid_states = ['on', 'off', 'toggle', 'pulse']
        if data.state not in valid_states:
            raise HTTPException(
                status_code=400, 
                detail=f"유효하지 않은 상태입니다. 허용된 상태: {valid_states}"
            )
