"""
Device 리포지토리 인터페이스

IoT 디바이스 데이터 접근을 위한 추상 인터페이스입니다.
Clean Architecture의 의존성 역전 원칙을 구현합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.device import Device


class IDeviceRepository(ABC):
    """디바이스 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create(self, device: Device) -> Device:
        """새로운 디바이스를 생성합니다."""
        pass
    
    @abstractmethod
    async def get_by_id(self, device_id: str) -> Optional[Device]:
        """ID로 디바이스를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Device]:
        """사용자에게 할당된 디바이스 목록을 조회합니다."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[Device]:
        """모든 디바이스를 조회합니다."""
        pass
    
    @abstractmethod
    async def update(self, device: Device) -> Device:
        """디바이스 정보를 업데이트합니다."""
        pass
    
    @abstractmethod
    async def delete(self, device_id: str) -> bool:
        """디바이스를 삭제합니다."""
        pass
    
    @abstractmethod
    async def assign_to_user(self, device_id: str, user_id: UUID) -> Device:
        """디바이스를 사용자에게 할당합니다."""
        pass
    
    @abstractmethod
    async def unassign_from_user(self, device_id: str) -> Device:
        """디바이스의 사용자 할당을 해제합니다."""
        pass
    
    @abstractmethod
    async def exists(self, device_id: str) -> bool:
        """디바이스 존재 여부를 확인합니다."""
        pass 