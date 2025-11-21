"""
메모리 기반 Device 리포지토리

테스트와 개발 단계에서 사용하는 인메모리 리포지토리입니다.
실제 데이터베이스 대신 메모리에 데이터를 저장합니다.
"""

from typing import List, Optional, Dict
from uuid import UUID
from app.domain.entities.device import Device
from app.interfaces.repositories.device_repository import IDeviceRepository


class MemoryDeviceRepository(IDeviceRepository):
    """메모리 기반 디바이스 리포지토리"""
    
    def __init__(self):
        self._devices: Dict[str, Device] = {}
        self._user_devices: Dict[UUID, List[str]] = {}
    
    async def create(self, device: Device) -> Device:
        """새로운 디바이스를 생성합니다."""
        if device.device_id in self._devices:
            raise ValueError(f"디바이스가 이미 존재합니다: {device.device_id}")
        
        self._devices[device.device_id] = device
        
        # 사용자에게 할당된 경우 인덱스 업데이트
        if device.user_id:
            if device.user_id not in self._user_devices:
                self._user_devices[device.user_id] = []
            self._user_devices[device.user_id].append(device.device_id)
        
        return device
    
    async def get_by_id(self, device_id: str) -> Optional[Device]:
        """ID로 디바이스를 조회합니다."""
        return self._devices.get(device_id)
    
    async def get_by_user_id(self, user_id: UUID) -> List[Device]:
        """사용자에게 할당된 디바이스 목록을 조회합니다."""
        device_ids = self._user_devices.get(user_id, [])
        return [self._devices[device_id] for device_id in device_ids if device_id in self._devices]
    
    async def get_all(self) -> List[Device]:
        """모든 디바이스를 조회합니다."""
        return list(self._devices.values())
    
    async def update(self, device: Device) -> Device:
        """디바이스 정보를 업데이트합니다."""
        if device.device_id not in self._devices:
            raise ValueError(f"디바이스가 존재하지 않습니다: {device.device_id}")
        
        old_device = self._devices[device.device_id]
        
        # 사용자 할당이 변경된 경우 인덱스 업데이트
        if old_device.user_id != device.user_id:
            # 기존 사용자에서 제거
            if old_device.user_id and old_device.user_id in self._user_devices:
                if device.device_id in self._user_devices[old_device.user_id]:
                    self._user_devices[old_device.user_id].remove(device.device_id)
            
            # 새 사용자에게 추가
            if device.user_id:
                if device.user_id not in self._user_devices:
                    self._user_devices[device.user_id] = []
                self._user_devices[device.user_id].append(device.device_id)
        
        self._devices[device.device_id] = device
        return device
    
    async def delete(self, device_id: str) -> bool:
        """디바이스를 삭제합니다."""
        if device_id not in self._devices:
            return False
        
        device = self._devices[device_id]
        
        # 사용자 할당 해제
        if device.user_id and device.user_id in self._user_devices:
            if device_id in self._user_devices[device.user_id]:
                self._user_devices[device.user_id].remove(device_id)
        
        del self._devices[device_id]
        return True
    
    async def assign_to_user(self, device_id: str, user_id: UUID) -> Device:
        """디바이스를 사용자에게 할당합니다."""
        if device_id not in self._devices:
            raise ValueError(f"디바이스가 존재하지 않습니다: {device_id}")
        
        device = self._devices[device_id]
        device.assign_to_user(user_id)
        
        # 인덱스 업데이트
        if user_id not in self._user_devices:
            self._user_devices[user_id] = []
        self._user_devices[user_id].append(device_id)
        
        return device
    
    async def unassign_from_user(self, device_id: str) -> Device:
        """디바이스의 사용자 할당을 해제합니다."""
        if device_id not in self._devices:
            raise ValueError(f"디바이스가 존재하지 않습니다: {device_id}")
        
        device = self._devices[device_id]
        old_user_id = device.user_id
        
        device.unassign_from_user()
        
        # 인덱스 업데이트
        if old_user_id and old_user_id in self._user_devices:
            if device_id in self._user_devices[old_user_id]:
                self._user_devices[old_user_id].remove(device_id)
        
        return device
    
    async def exists(self, device_id: str) -> bool:
        """디바이스 존재 여부를 확인합니다."""
        return device_id in self._devices
    
    def clear(self) -> None:
        """모든 데이터를 제거합니다 (테스트용)."""
        self._devices.clear()
        self._user_devices.clear() 