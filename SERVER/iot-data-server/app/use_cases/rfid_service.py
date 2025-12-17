"""
RFID 센서 데이터 서비스 구현체

Clean Architecture 원칙에 따라 RFID 센서 데이터에 대한 비즈니스 로직을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from app.interfaces.services.sensor_service_interface import IRFIDService
from app.interfaces.repositories.sensor_repository import IRFIDRepository
from app.api.v1.schemas import (
    SensorRawRFIDCreate,
    SensorRawRFIDUpdate,
    SensorRawRFIDResponse
)


class RFIDService(IRFIDService):
    """RFID 센서 데이터 서비스 구현체"""
    
    def __init__(self, rfid_repository: IRFIDRepository):
        self.rfid_repository = rfid_repository
    
    async def create_sensor_data(self, data: SensorRawRFIDCreate) -> SensorRawRFIDResponse:
        """RFID 센서 데이터 생성"""
        try:
            
            # 리포지토리를 통한 데이터 생성
            created_data = await self.rfid_repository.create(data)
            print(created_data)
            return created_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 생성 실패: {str(e)}")
    
    async def get_sensor_data(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawRFIDResponse]:
        """특정 시간의 RFID 센서 데이터 조회"""
        try:
            data = await self.rfid_repository.get_by_id(device_id, timestamp)
            if not data:
                raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    
    async def get_latest_sensor_data(self, device_id: str) -> Optional[SensorRawRFIDResponse]:
        """최신 RFID 센서 데이터 조회"""
        try:
            data = await self.rfid_repository.get_latest(device_id)
            if not data:
                raise HTTPException(status_code=404, detail="해당 디바이스의 데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    
    async def get_sensor_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SensorRawRFIDResponse]:
        """RFID 센서 데이터 목록 조회"""
        try:
            # 비즈니스 로직 검증
            if limit < 1 or limit > 1000:
                raise ValueError("조회 개수는 1에서 1000 사이여야 합니다")
            
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            data_list = await self.rfid_repository.get_list(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit_count=limit
            )
            return data_list
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    
    async def update_sensor_data(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawRFIDUpdate   
    ) -> Optional[SensorRawRFIDResponse]:
        """RFID 센서 데이터 수정"""
        try:
            # 비즈니스 로직 검증
            if data.card_id is not None and len(data.card_id.strip()) == 0:
                raise ValueError("카드 ID는 비어있을 수 없습니다")
            
            updated_data = await self.rfid_repository.update(device_id, timestamp, data)
            if not updated_data:
                raise HTTPException(status_code=404, detail="수정할 데이터를 찾을 수 없습니다")
            
            return updated_data
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 수정 실패: {str(e)}")
    
    async def delete_sensor_data(self, device_id: str, timestamp: datetime) -> bool:
        """RFID 센서 데이터 삭제"""
        try:
            success = await self.rfid_repository.delete(device_id, timestamp)
            if not success:
                raise HTTPException(status_code=404, detail="삭제할 데이터를 찾을 수 없습니다")
            
            return success
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 삭제 실패: {str(e)}")
    
    async def get_sensor_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """RFID 센서 데이터 기본 통계 조회"""
        return await self.get_card_statistics(device_id, start_time, end_time)
    
    async def get_card_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """RFID 센서의 카드 통계 정보 조회"""
        try:
            # 비즈니스 로직 검증
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            stats = await self.rfid_repository.get_card_statistics(
                device_id, start_time, end_time
            )
            return stats
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
    
    async def get_read_history(
        self,
        device_id: str,
        card_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """RFID 센서의 읽기 이력 조회"""
        try:
            # 비즈니스 로직 검증
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            if card_id and len(card_id.strip()) == 0:
                raise ValueError("카드 ID는 비어있을 수 없습니다")
            
            history = await self.rfid_repository.get_read_history(
                device_id, card_id, start_time, end_time
            )
            return history
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"이력 조회 실패: {str(e)}")
