"""
Ultrasonic 센서 데이터 서비스 구현체

Clean Architecture 원칙에 따라 Ultrasonic 센서 데이터에 대한 비즈니스 로직을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from app.interfaces.services.sensor_service_interface import IUltrasonicService
from app.interfaces.repositories.sensor_repository import IUltrasonicRepository
from app.api.v1.schemas import (
    SensorRawUltrasonicCreate,
    SensorRawUltrasonicUpdate,
    SensorRawUltrasonicResponse
)


class UltrasonicService(IUltrasonicService):
    """Ultrasonic 센서 데이터 서비스 구현체"""
    
    def __init__(self, ultrasonic_repository: IUltrasonicRepository):
        self.ultrasonic_repository = ultrasonic_repository
    
    async def create_sensor_data(self, data: SensorRawUltrasonicCreate) -> SensorRawUltrasonicResponse:
        """Ultrasonic 센서 데이터 생성"""
        try:
            
            # 리포지토리를 통한 데이터 생성
            created_data = await self.ultrasonic_repository.create(data)
            return created_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ultrasonic 센서 데이터 생성 실패: {str(e)}")
    
    async def get_sensor_data(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawUltrasonicResponse]:
        """특정 시간의 Ultrasonic 센서 데이터 조회"""
        try:
            data = await self.ultrasonic_repository.get_by_id(device_id, timestamp)
            if not data:
                raise HTTPException(status_code=404, detail="Ultrasonic 센서 데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ultrasonic 센서 데이터 조회 실패: {str(e)}")
    
    async def get_latest_sensor_data(self, device_id: str) -> Optional[SensorRawUltrasonicResponse]:
        """최신 Ultrasonic 센서 데이터 조회"""
        try:
            data = await self.ultrasonic_repository.get_latest(device_id)
            if not data:
                raise HTTPException(status_code=404, detail="해당 디바이스의 Ultrasonic 센서 데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ultrasonic 센서 데이터 조회 실패: {str(e)}")
    
    async def get_sensor_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SensorRawUltrasonicResponse]:
        """Ultrasonic 센서 데이터 목록 조회"""
        try:
            # 비즈니스 로직 검증
            if limit < 1 or limit > 1000:
                raise ValueError("조회 개수는 1에서 1000 사이여야 합니다")
            
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            data_list = await self.ultrasonic_repository.get_list(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit_count=limit
            )
            return data_list
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ultrasonic 센서 데이터 목록 조회 실패: {str(e)}")
    
    async def update_sensor_data(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawUltrasonicUpdate
    ) -> Optional[SensorRawUltrasonicResponse]:
        """Ultrasonic 센서 데이터 수정"""
        try:
            # 비즈니스 로직 검증
            if data.distance_cm is not None and (data.distance_cm < 0 or data.distance_cm > 1000):
                raise ValueError("거리 값은 0에서 1000cm 사이여야 합니다")
            
            if data.raw_value is not None and (data.raw_value < 0 or data.raw_value > 65535):
                raise ValueError("원시 값은 0에서 65535 사이여야 합니다")
            
            # 리포지토리를 통한 데이터 수정
            updated_data = await self.ultrasonic_repository.update(device_id, timestamp, data)
            if not updated_data:
                raise HTTPException(status_code=404, detail="수정할 Ultrasonic 센서 데이터를 찾을 수 없습니다")
            
            return updated_data
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ultrasonic 센서 데이터 수정 실패: {str(e)}")
    
    async def delete_sensor_data(self, device_id: str, timestamp: datetime) -> bool:
        """Ultrasonic 센서 데이터 삭제"""
        try:
            success = await self.ultrasonic_repository.delete(device_id, timestamp)
            if not success:
                raise HTTPException(status_code=404, detail="삭제할 Ultrasonic 센서 데이터를 찾을 수 없습니다")
            
            return success
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ultrasonic 센서 데이터 삭제 실패: {str(e)}")
    
    async def get_sensor_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """Ultrasonic 센서 데이터 기본 통계 조회"""
        try:
            stats = await self.ultrasonic_repository.get_statistics(device_id, start_time, end_time)
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ultrasonic 센서 통계 조회 실패: {str(e)}")
    
    async def get_distance_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """거리 측정 통계 정보 조회"""
        try:
            stats = await self.ultrasonic_repository.get_distance_statistics(device_id, start_time, end_time)
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"거리 측정 통계 조회 실패: {str(e)}")
    
    async def analyze_distance_trends(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """거리 트렌드 분석"""
        try:
            # 분석 윈도우 검증
            if analysis_window < 60 or analysis_window > 86400:  # 1분 ~ 24시간
                raise ValueError("분석 윈도우는 60초에서 86400초 사이여야 합니다")
            
            trends = await self.ultrasonic_repository.analyze_distance_trends(device_id, analysis_window)
            return trends
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"거리 트렌드 분석 실패: {str(e)}") 