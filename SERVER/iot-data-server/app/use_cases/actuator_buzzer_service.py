"""
Buzzer 액추에이터 로그 서비스 구현체

Buzzer 액추에이터 로그 데이터에 대한 비즈니스 로직을 구현합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import HTTPException
from app.infrastructure.models import ActuatorLogBuzzer
from app.interfaces.repositories.actuator_repository import IActuatorBuzzerRepository
from app.interfaces.services.actuator_service_interface import IActuatorBuzzerService
from app.api.v1.schemas import (
    ActuatorBuzzerDataCreate, ActuatorBuzzerDataUpdate, ActuatorBuzzerDataResponse
)


class ActuatorBuzzerService(IActuatorBuzzerService):
    """Buzzer 액추에이터 로그 서비스 구현체"""
    
    def __init__(self, repository: IActuatorBuzzerRepository):
        self.repository = repository
    
    async def create_actuator_data(self, data: ActuatorBuzzerDataCreate) -> ActuatorBuzzerDataResponse:
        """Buzzer 액추에이터 로그 생성"""
        # 비즈니스 로직 검증
        await self._validate_buzzer_data(data)
        
        # ORM 모델 생성
        actuator_data = ActuatorLogBuzzer(
            time=data.time,
            device_id=data.device_id,
            buzzer_type=data.buzzer_type,
            state=data.state,
            freq_hz=data.freq_hz,
            duration_ms=data.duration_ms,
            reason=data.reason,
            raw_payload=data.raw_payload
        )
        
        # 리포지토리를 통한 데이터 저장
        created_data = await self.repository.create(actuator_data)
        
        # 응답 스키마로 변환
        return ActuatorBuzzerDataResponse(
            time=created_data.time,
            device_id=created_data.device_id,
            buzzer_type=created_data.buzzer_type,
            state=created_data.state,
            freq_hz=created_data.freq_hz,
            duration_ms=created_data.duration_ms,
            reason=created_data.reason,
            raw_payload=created_data.raw_payload
        )
    
    async def get_actuator_data(self, device_id: str, timestamp: datetime) -> Optional[ActuatorBuzzerDataResponse]:
        """Buzzer 액추에이터 로그 조회"""
        actuator_data = await self.repository.get_by_id(device_id, timestamp)
        if not actuator_data:
            return None
        
        return ActuatorBuzzerDataResponse(
            time=actuator_data.time,
            device_id=actuator_data.device_id,
            buzzer_type=actuator_data.buzzer_type,
            state=actuator_data.state,
            freq_hz=actuator_data.freq_hz,
            duration_ms=actuator_data.duration_ms,
            reason=actuator_data.reason,
            raw_payload=actuator_data.raw_payload
        )
    
    async def get_latest_actuator_data(self, device_id: str) -> Optional[ActuatorBuzzerDataResponse]:
        """최신 Buzzer 액추에이터 로그 조회"""
        actuator_data = await self.repository.get_latest(device_id)
        if not actuator_data:
            return None
        
        return ActuatorBuzzerDataResponse(
            time=actuator_data.time,
            device_id=actuator_data.device_id,
            buzzer_type=actuator_data.buzzer_type,
            state=actuator_data.state,
            freq_hz=actuator_data.freq_hz,
            duration_ms=actuator_data.duration_ms,
            reason=actuator_data.reason,
            raw_payload=actuator_data.raw_payload
        )
    
    async def get_actuator_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        buzzer_type: Optional[str] = None,
        state: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorBuzzerDataResponse]:
        """Buzzer 액추에이터 로그 목록 조회"""
        # 비즈니스 로직 검증
        if limit > 1000:
            raise HTTPException(status_code=400, detail="최대 1000개까지 조회 가능합니다")
        
        actuator_data_list = await self.repository.get_list(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            buzzer_type=buzzer_type,
            state=state,
            limit=limit,
            offset=offset
        )
        
        # 응답 스키마로 변환
        return [
            ActuatorBuzzerDataResponse(
                time=data.time,
                device_id=data.device_id,
                buzzer_type=data.buzzer_type,
                state=data.state,
                freq_hz=data.freq_hz,
                duration_ms=data.duration_ms,
                reason=data.reason,
                raw_payload=data.raw_payload
            )
            for data in actuator_data_list
        ]
    
    async def update_actuator_data(
        self, 
        device_id: str, 
        timestamp: datetime, 
        data: ActuatorBuzzerDataUpdate
    ) -> Optional[ActuatorBuzzerDataResponse]:
        """Buzzer 액추에이터 로그 수정"""
        # 업데이트할 데이터 검증
        update_data = {}
        if data.buzzer_type is not None:
            update_data['buzzer_type'] = data.buzzer_type
        if data.state is not None:
            update_data['state'] = data.state
        if data.freq_hz is not None:
            update_data['freq_hz'] = data.freq_hz
        if data.duration_ms is not None:
            update_data['duration_ms'] = data.duration_ms
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
        return ActuatorBuzzerDataResponse(
            time=updated_data.time,
            device_id=updated_data.device_id,
            buzzer_type=updated_data.buzzer_type,
            state=updated_data.state,
            freq_hz=updated_data.freq_hz,
            duration_ms=updated_data.duration_ms,
            reason=updated_data.reason,
            raw_payload=updated_data.raw_payload
        )
    
    async def delete_actuator_data(self, device_id: str, timestamp: datetime) -> bool:
        """Buzzer 액추에이터 로그 삭제"""
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
        """Buzzer 액추에이터 로그 통계 조회"""
        return await self.repository.get_statistics(device_id, start_time, end_time)
    
    async def _validate_buzzer_data(self, data: ActuatorBuzzerDataCreate) -> None:
        """Buzzer 데이터 비즈니스 로직 검증"""
        # 주파수 검증
        if data.freq_hz is not None and (data.freq_hz < 20 or data.freq_hz > 20000):
            raise HTTPException(
                status_code=400, 
                detail="주파수는 20Hz ~ 20kHz 범위 내에 있어야 합니다"
            )
        
        # 지속시간 검증
        if data.duration_ms is not None and (data.duration_ms < 0 or data.duration_ms > 60000):
            raise HTTPException(
                status_code=400, 
                detail="지속시간은 0ms ~ 60초 범위 내에 있어야 합니다"
            )
        
        # 부저 타입 검증
        valid_buzzer_types = ['piezo', 'magnetic', 'mechanical', 'digital']
        if data.buzzer_type not in valid_buzzer_types:
            raise HTTPException(
                status_code=400, 
                detail=f"유효하지 않은 부저 타입입니다. 허용된 타입: {valid_buzzer_types}"
            )
        
        # 상태 검증
        valid_states = ['on', 'off', 'pulse', 'tone']
        if data.state not in valid_states:
            raise HTTPException(
                status_code=400, 
                detail=f"유효하지 않은 상태입니다. 허용된 상태: {valid_states}"
            )
