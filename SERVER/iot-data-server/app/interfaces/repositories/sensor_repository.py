"""
센서 데이터 리포지토리 인터페이스

모든 센서 데이터에 대한 공통 리포지토리 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from datetime import datetime
from pydantic import BaseModel

# 제네릭 타입 정의
T = TypeVar('T')
CreateModel = TypeVar('CreateModel', bound=BaseModel)
UpdateModel = TypeVar('UpdateModel', bound=BaseModel)
ResponseModel = TypeVar('ResponseModel', bound=BaseModel)


class ISensorRepository(ABC, Generic[T, CreateModel, UpdateModel, ResponseModel]):
    """센서 데이터 리포지토리 기본 인터페이스"""
    
    @abstractmethod
    async def create(self, data: CreateModel) -> ResponseModel:
        """센서 데이터 생성"""
        pass
    
    @abstractmethod
    async def get_by_id(self, device_id: str, timestamp: datetime) -> Optional[ResponseModel]:
        """특정 시간의 센서 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_latest(self, device_id: str) -> Optional[ResponseModel]:
        """최신 센서 데이터 조회"""
        pass
    
    @abstractmethod
    async def get_list(
        self,
        device_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[ResponseModel]:
        """센서 데이터 목록 조회"""
        pass
    
    @abstractmethod
    async def update(
        self,
        device_id: str,
        timestamp: datetime,
        data: UpdateModel
    ) -> Optional[ResponseModel]:
        """센서 데이터 수정"""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str, timestamp: datetime) -> bool:
        """센서 데이터 삭제"""
        pass
    
    @abstractmethod
    async def get_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """센서 데이터 통계 조회"""
        pass


class ILoadCellRepository(ISensorRepository):
    """로드셀 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_weight_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """무게 통계 정보 조회"""
        pass


class IMQ5Repository(ISensorRepository):
    """MQ5 가스 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_gas_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """가스 농도 통계 정보 조회"""
        pass
    
    @abstractmethod
    async def get_high_concentration_alerts(
        self,
        device_id: str,
        threshold_ppm: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """높은 농도 알림 조회"""
        pass


class IMQ7Repository(ISensorRepository):
    """MQ7 가스 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_gas_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """가스 농도 통계 정보 조회"""
        pass
    
    @abstractmethod
    async def get_high_concentration_alerts(
        self,
        device_id: str,
        threshold_ppm: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """높은 농도 알림 조회"""
        pass


class IRFIDRepository(ISensorRepository):
    """RFID 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_card_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """카드 통계 정보 조회"""
        pass
    
    @abstractmethod
    async def get_read_history(
        self,
        device_id: str,
        card_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """읽기 이력 조회"""
        pass


class ISoundRepository(ISensorRepository):
    """사운드 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_audio_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """오디오 통계 정보 조회"""
        pass
    
    @abstractmethod
    async def get_noise_alerts(
        self,
        device_id: str,
        threshold_db: float,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """소음 알림 조회"""
        pass


class ITCRT5000Repository(ISensorRepository):
    """TCRT5000 근접 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_proximity_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """근접 감지 통계 정보 조회"""
        pass
    
    @abstractmethod
    async def analyze_motion_patterns(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """움직임 패턴 분석"""
        pass


class IUltrasonicRepository(ISensorRepository):
    """초음파 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_distance_statistics(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """거리 측정 통계 정보 조회"""
        pass
    
    @abstractmethod
    async def analyze_distance_trends(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """거리 트렌드 분석"""
        pass


class IEdgeFlameRepository(ISensorRepository):
    """Edge 화재 감지 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_flame_detection_alerts(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """화재 감지 알림 조회"""
        pass


class IEdgePIRRepository(ISensorRepository):
    """Edge PIR 모션 감지 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def analyze_motion_patterns(
        self,
        device_id: str,
        analysis_window: int = 3600
    ) -> dict:
        """모션 패턴 분석"""
        pass


class IEdgeReedRepository(ISensorRepository):
    """Edge Reed 스위치 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_switch_activation_history(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """스위치 활성화 이력 조회"""
        pass


class IEdgeTiltRepository(ISensorRepository):
    """Edge Tilt 기울기 센서 데이터 리포지토리 인터페이스"""
    
    @abstractmethod
    async def analyze_tilt_trends(
        self,
        device_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> dict:
        """기울기 트렌드 분석"""
        pass
