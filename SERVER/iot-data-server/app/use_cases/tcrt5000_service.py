"""
TCRT5000 센서 데이터 서비스 구현체

Clean Architecture 원칙에 따라 TCRT5000 센서 데이터에 대한 비즈니스 로직을 담당합니다.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

from app.interfaces.services.sensor_service_interface import ITCRT5000Service
from app.interfaces.repositories.sensor_repository import ITCRT5000Repository
from app.api.v1.schemas import (
    SensorRawTCRT5000Create,
    SensorRawTCRT5000Update,
    SensorRawTCRT5000Response
)


class TCRT5000Service(ITCRT5000Service):
    """TCRT5000 센서 데이터 서비스 구현체"""
    
    def __init__(self, tcrt5000_repository: ITCRT5000Repository):
        self.tcrt5000_repository = tcrt5000_repository
    
    async def create_sensor_data(self, data: SensorRawTCRT5000Create) -> SensorRawTCRT5000Response:
        """TCRT5000 센서 데이터 생성"""
        try:
            
            # 리포지토리를 통한 데이터 생성
            created_data = await self.tcrt5000_repository.create(data)
            return created_data
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TCRT5000 센서 데이터 생성 실패: {str(e)}")
    
    async def get_sensor_data(
        self,
        device_id: str,
        timestamp: datetime
    ) -> Optional[SensorRawTCRT5000Response]:
        """특정 시간의 TCRT5000 센서 데이터 조회"""
        try:
            data = await self.tcrt5000_repository.get_by_id(device_id, timestamp)
            if not data:
                raise HTTPException(status_code=404, detail="TCRT5000 센서 데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TCRT5000 센서 데이터 조회 실패: {str(e)}")
    
    async def get_latest_sensor_data(self, device_id: str) -> Optional[SensorRawTCRT5000Response]:
        """최신 TCRT5000 센서 데이터 조회"""
        try:
            data = await self.tcrt5000_repository.get_latest(device_id)
            if not data:
                raise HTTPException(status_code=404, detail="해당 디바이스의 TCRT5000 센서 데이터를 찾을 수 없습니다")
            return data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TCRT5000 센서 데이터 조회 실패: {str(e)}")
    
    async def get_sensor_data_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[SensorRawTCRT5000Response]:
        """TCRT5000 센서 데이터 목록 조회"""
        try:
            # 비즈니스 로직 검증
            if limit < 1 or limit > 1000:
                raise ValueError("조회 개수는 1에서 1000 사이여야 합니다")
            
            if start_time and end_time and start_time > end_time:
                raise ValueError("시작 시간은 종료 시간보다 이전이어야 합니다")
            
            data_list = await self.tcrt5000_repository.get_list(
                device_id=device_id,
                start_time=start_time,
                end_time=end_time,
                limit_count=limit
            )
            return data_list
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TCRT5000 센서 데이터 목록 조회 실패: {str(e)}")
    
    async def update_sensor_data(
        self,
        device_id: str,
        timestamp: datetime,
        data: SensorRawTCRT5000Update
    ) -> Optional[SensorRawTCRT5000Response]:
        """TCRT5000 센서 데이터 수정"""
        try:
            # 비즈니스 로직 검증
            if data.analog_value is not None and (data.analog_value < 0 or data.analog_value > 1023):
                raise ValueError("아날로그 값은 0에서 1023 사이여야 합니다")
            
            # 리포지토리를 통한 데이터 수정
            updated_data = await self.tcrt5000_repository.update(device_id, timestamp, data)
            if not updated_data:
                raise HTTPException(status_code=404, detail="수정할 TCRT5000 센서 데이터를 찾을 수 없습니다")
            
            return updated_data
            
        except HTTPException:
            raise
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TCRT5000 센서 데이터 수정 실패: {str(e)}")
    
    async def delete_sensor_data(self, device_id: str, timestamp: datetime) -> bool:
        """TCRT5000 센서 데이터 삭제"""
        try:
            success = await self.tcrt5000_repository.delete(device_id, timestamp)
            if not success:
                raise HTTPException(status_code=404, detail="삭제할 TCRT5000 센서 데이터를 찾을 수 없습니다")
            
            return success
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TCRT5000 센서 데이터 삭제 실패: {str(e)}")
    
    async def get_sensor_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """TCRT5000 센서 데이터 기본 통계 조회"""
        try:
            stats = await self.tcrt5000_repository.get_statistics(device_id, start_time, end_time)
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"TCRT5000 센서 통계 조회 실패: {str(e)}")
    
    async def get_proximity_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """근접 감지 통계 정보 조회"""
        try:
            stats = await self.tcrt5000_repository.get_proximity_statistics(device_id, start_time, end_time)
            return stats
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"근접 감지 통계 조회 실패: {str(e)}")
    
    async def analyze_motion_patterns(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """움직임 패턴 분석"""
        try:
            # 분석 윈도우 검증
            if analysis_window < 60 or analysis_window > 86400:  # 1분 ~ 24시간
                raise ValueError("분석 윈도우는 60초에서 86400초 사이여야 합니다")
            
            patterns = await self.tcrt5000_repository.analyze_motion_patterns(device_id, analysis_window)
            return patterns
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"움직임 패턴 분석 실패: {str(e)}") 