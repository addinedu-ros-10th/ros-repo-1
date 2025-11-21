"""
MQ5 가스 센서 데이터 서비스 구현체

Clean Architecture 원칙에 따라 MQ5 가스 센서 데이터에 대한 비즈니스 로직을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from app.interfaces.services.sensor_service_interface import IMQ5Service
from app.interfaces.repositories.sensor_repository import IMQ5Repository
from app.api.v1.schemas import (
    SensorRawMQ5Create,
    SensorRawMQ5Update,
    SensorRawMQ5Response
)


class MQ5Service(IMQ5Service):
    """MQ5 가스 센서 데이터 서비스 구현체"""
    
    def __init__(self, mq5_repository: IMQ5Repository):
        self.mq5_repository = mq5_repository
    
    async def create_sensor_data(self, data: SensorRawMQ5Create) -> SensorRawMQ5Response:
        """MQ5 가스 센서 데이터 생성"""
        try:
            # 리포지토리를 통한 데이터 생성
            created_data = await self.mq5_repository.create(data)
            return created_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 생성 실패: {str(e)}")
    
    async def get_sensor_data(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawMQ5Response]:
        """특정 시간의 MQ5 가스 센서 데이터 조회"""
        try:
            data = await self.mq5_repository.get_by_id(device_id, timestamp)
            if not data:
                raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    
    async def get_latest_sensor_data(self, device_id: str) -> Optional[SensorRawMQ5Response]:
        """최신 MQ5 가스 센서 데이터 조회"""
        try:
            data = await self.mq5_repository.get_latest(device_id)
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
    ) -> List[SensorRawMQ5Response]:
        """MQ5 가스 센서 데이터 목록 조회"""
        try:
            # 비즈니스 로직 검증 (기존 코드와 동일)
            if not (1 <= limit <= 1000):
                raise ValueError("조회 개수는 1에서 1000 사이여야 합니다")
            
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            # 리포지토리에서 데이터를 즉시 조회하여 Pydantic 모델 리스트로 반환받음
            data_list = await self.mq5_repository.get_list(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit_count=limit
            )
            
            # 리포지토리에서 이미 Pydantic 모델 리스트를 반환하므로, 추가 변환 없이 바로 반환
            return data_list
            # return [SensorRawMQ5Response.model_validate(o) for o in data_list]
                
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            # 리포지토리에서 발생한 예외를 그대로 전파
            raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    
    async def update_sensor_data(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawMQ5Update
    ) -> Optional[SensorRawMQ5Response]:
        """MQ5 가스 센서 데이터 수정"""
        try:
            updated_data = await self.mq5_repository.update(device_id, timestamp, data)
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
        """MQ5 가스 센서 데이터 삭제"""
        try:
            success = await self.mq5_repository.delete(device_id, timestamp)
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
        """MQ5 가스 센서 데이터 기본 통계 조회"""
        return await self.get_gas_statistics(device_id, start_time, end_time)
    
    async def get_gas_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """MQ5 가스 센서의 가스 농도 통계 정보 조회"""
        try:
            # 비즈니스 로직 검증
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            stats = await self.mq5_repository.get_gas_statistics(
                device_id, start_time, end_time
            )
            return stats
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"통계 조회 실패: {str(e)}")
    
    async def get_high_concentration_alerts(
        self,
        device_id: str,
        threshold_ppm: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """MQ5 가스 센서의 높은 농도 알림 조회"""
        try:
            # 비즈니스 로직 검증
            if threshold_ppm <= 0:
                raise ValueError("임계값은 0보다 커야 합니다")
            
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            alerts = await self.mq5_repository.get_high_concentration_alerts(
                device_id, threshold_ppm, start_time, end_time
            )
            return alerts
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"알림 조회 실패: {str(e)}")
