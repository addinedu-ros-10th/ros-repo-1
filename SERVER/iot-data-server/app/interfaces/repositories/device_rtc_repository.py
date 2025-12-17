"""
DeviceRTCStatus 리포지토리 인터페이스

디바이스 RTC 상태 데이터에 대한 리포지토리 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class IDeviceRTCStatusRepository(ABC):
    """디바이스 RTC 상태 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create(self, data: BaseModel) -> BaseModel:
        """RTC 상태 데이터 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[BaseModel]:
        """특정 시간의 RTC 상태 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_latest(self, device_id: str) -> Optional[BaseModel]:
        """최신 RTC 상태 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[BaseModel]:
        """RTC 상태 데이터 목록 조회"""
        pass
    
    @abstractmethod
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: BaseModel
    ) -> Optional[BaseModel]:
        """RTC 상태 데이터 수정"""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """RTC 상태 데이터 삭제"""
        pass
    
    @abstractmethod
    async def get_sync_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """동기화 통계 정보 조회"""
        pass
    
    @abstractmethod
    async def get_drift_analysis(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """시간 드리프트 분석 정보 조회"""
        pass 