"""
IR TX 액추에이터 로그 서비스 구현체

IR TX 액추에이터 로그 데이터에 대한 비즈니스 로직을 구현합니다.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi import HTTPException
from app.infrastructure.models import ActuatorLogIRTX
from app.interfaces.repositories.actuator_repository import IActuatorIRTXRepository
from app.interfaces.services.actuator_service_interface import IActuatorIRTXService
from app.api.v1.schemas import (
    ActuatorIRTXDataCreate, ActuatorIRTXDataUpdate, ActuatorIRTXDataResponse
)


class ActuatorIRTXService(IActuatorIRTXService):
    """IR TX 액추에이터 로그 서비스 구현체"""
    
    def __init__(self, repository: IActuatorIRTXRepository):
        self.repository = repository
    
    async def create_actuator_data(self, data: ActuatorIRTXDataCreate) -> ActuatorIRTXDataResponse:
        """IR TX 액추에이터 로그 생성"""
        # 비즈니스 로직 검증
        await self._validate_irtx_data(data)
        
        # ORM 모델 생성
        actuator_data = ActuatorLogIRTX(
            time=data.time,
            device_id=data.device_id,
            protocol=data.protocol,
            address_hex=data.address_hex,
            command_hex=data.command_hex,
            repeat_cnt=data.repeat_cnt,
            raw_payload=data.raw_payload
        )
        
        # 리포지토리를 통한 데이터 저장
        created_data = await self.repository.create(actuator_data)
        
        # 응답 스키마로 변환
        return ActuatorIRTXDataResponse(
            time=created_data.time,
            device_id=created_data.device_id,
            protocol=created_data.protocol,
            address_hex=created_data.address_hex,
            command_hex=created_data.command_hex,
            repeat_cnt=created_data.repeat_cnt,
            raw_payload=created_data.raw_payload
        )
    
    async def get_actuator_data(self, device_id: str, timestamp: datetime) -> Optional[ActuatorIRTXDataResponse]:
        """IR TX 액추에이터 로그 조회"""
        actuator_data = await self.repository.get_by_id(device_id, timestamp)
        if not actuator_data:
            return None
        
        return ActuatorIRTXDataResponse(
            time=actuator_data.time,
            device_id=actuator_data.device_id,
            protocol=actuator_data.protocol,
            address_hex=actuator_data.address_hex,
            command_hex=actuator_data.command_hex,
            repeat_cnt=actuator_data.repeat_cnt,
            raw_payload=actuator_data.raw_payload
        )
    
    async def get_latest_actuator_data(self, device_id: str) -> Optional[ActuatorIRTXDataResponse]:
        """최신 IR TX 액추에이터 로그 조회"""
        actuator_data = await self.repository.get_latest(device_id)
        if not actuator_data:
            return None
        
        return ActuatorIRTXDataResponse(
            time=actuator_data.time,
            device_id=actuator_data.device_id,
            protocol=actuator_data.protocol,
            address_hex=actuator_data.address_hex,
            command_hex=actuator_data.command_hex,
            repeat_cnt=actuator_data.repeat_cnt,
            raw_payload=actuator_data.raw_payload
        )
    
    async def get_actuator_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        protocol: Optional[str] = None,
        command_hex: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ActuatorIRTXDataResponse]:
        """IR TX 액추에이터 로그 목록 조회"""
        # 비즈니스 로직 검증
        if limit > 1000:
            raise HTTPException(status_code=400, detail="최대 1000개까지 조회 가능합니다")
        
        actuator_data_list = await self.repository.get_list(
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            protocol=protocol,
            command_hex=command_hex,
            limit=limit,
            offset=offset
        )
        
        # 응답 스키마로 변환
        return [
            ActuatorIRTXDataResponse(
                time=data.time,
                device_id=data.device_id,
                protocol=data.protocol,
                address_hex=data.address_hex,
                command_hex=data.command_hex,
                repeat_cnt=data.repeat_cnt,
                raw_payload=data.raw_payload
            )
            for data in actuator_data_list
        ]
    
    async def update_actuator_data(
        self, 
        device_id: str, 
        timestamp: datetime, 
        data: ActuatorIRTXDataUpdate
    ) -> Optional[ActuatorIRTXDataResponse]:
        """IR TX 액추에이터 로그 수정"""
        # 업데이트할 데이터 검증
        update_data = {}
        if data.protocol is not None:
            update_data['protocol'] = data.protocol
        if data.address_hex is not None:
            update_data['address_hex'] = data.address_hex
        if data.command_hex is not None:
            update_data['command_hex'] = data.command_hex
        if data.repeat_cnt is not None:
            update_data['repeat_cnt'] = data.repeat_cnt
        if data.raw_payload is not None:
            update_data['raw_payload'] = data.raw_payload
        
        if not update_data:
            raise HTTPException(status_code=400, detail="업데이트할 데이터가 없습니다")
        
        # 리포지토리를 통한 데이터 수정
        updated_data = await self.repository.update(device_id, timestamp, update_data)
        if not updated_data:
            raise HTTPException(status_code=404, detail="액추에이터 로그를 찾을 수 없습니다")
        
        # 응답 스키마로 변환
        return ActuatorIRTXDataResponse(
            time=updated_data.time,
            device_id=updated_data.device_id,
            protocol=updated_data.protocol,
            address_hex=updated_data.address_hex,
            command_hex=updated_data.command_hex,
            repeat_cnt=updated_data.repeat_cnt,
            raw_payload=updated_data.raw_payload
        )
    
    async def delete_actuator_data(self, device_id: str, timestamp: datetime) -> bool:
        """IR TX 액추에이터 로그 삭제"""
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
        """IR TX 액추에이터 로그 통계 조회"""
        return await self.repository.get_statistics(device_id, start_time, end_time)
    
    async def _validate_irtx_data(self, data: ActuatorIRTXDataCreate) -> None:
        """IR TX 데이터 비즈니스 로직 검증"""
        # 반복 횟수 검증
        if data.repeat_cnt is not None and (data.repeat_cnt < 1 or data.repeat_cnt > 100):
            raise HTTPException(
                status_code=400, 
                detail="반복 횟수는 1 ~ 100 범위 내에 있어야 합니다"
            )
        
        # 명령어 형식 검증 (16진수)
        if data.command_hex:
            try:
                int(data.command_hex, 16)
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="명령어는 유효한 16진수 형식이어야 합니다"
                )
        
        # 주소 형식 검증 (16진수, 선택사항)
        if data.address_hex:
            try:
                int(data.address_hex, 16)
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail="주소는 유효한 16진수 형식이어야 합니다"
                )
