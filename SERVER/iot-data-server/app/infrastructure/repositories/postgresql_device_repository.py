"""
PostgreSQL Device 리포지토리 구현체

실제 데이터베이스와 연동하는 Device 리포지토리입니다.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.interfaces.repositories.device_repository import IDeviceRepository
from app.domain.entities.device import Device
from app.infrastructure.models import Device as DeviceModel
from app.infrastructure.database import get_session


class PostgreSQLDeviceRepository(IDeviceRepository):
    """PostgreSQL 기반 Device 리포지토리"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def _get_session(self) -> AsyncSession:
        """세션 가져오기 - 생성자에서 받은 세션 사용"""
        return self.db_session
    
    async def create(self, device: Device) -> Device:
        """디바이스 생성"""
        session = await self._get_session()
        
        # 도메인 엔티티를 ORM 모델로 변환
        device_model = DeviceModel(
            device_id=device.device_id,
            user_id=device.user_id,
            location_label=device.location_label,
            installed_at=device.installed_at or datetime.utcnow()
        )
        
        session.add(device_model)
        await session.commit()
        await session.refresh(device_model)
        
        # ORM 모델을 도메인 엔티티로 변환하여 반환
        return Device(
            device_id=device_model.device_id,
            user_id=str(device_model.user_id) if device_model.user_id else None,
            location_label=device_model.location_label,
            installed_at=device_model.installed_at
        )
    
    async def get_by_id(self, device_id: str) -> Optional[Device]:
        """ID로 디바이스 조회"""
        session = await self._get_session()
        
        stmt = select(DeviceModel).where(DeviceModel.device_id == device_id)
        result = await session.execute(stmt)
        device_model = result.scalar_one_or_none()
        
        if device_model is None:
            return None
        
        # ORM 모델을 도메인 엔티티로 변환
        return Device(
            device_id=device_model.device_id,
            user_id=str(device_model.user_id) if device_model.user_id else None,
            location_label=device_model.location_label,
            installed_at=device_model.installed_at
        )
    
    async def get_by_user_id(self, user_id: str) -> List[Device]:
        """사용자별 디바이스 조회"""
        session = await self._get_session()
        
        stmt = select(DeviceModel).where(DeviceModel.user_id == user_id)
        result = await session.execute(stmt)
        device_models = result.scalars().all()
        
        # ORM 모델들을 도메인 엔티티로 변환
        devices = []
        for device_model in device_models:
            device = Device(
                device_id=device_model.device_id,
                user_id=str(device_model.user_id) if device_model.user_id else None,
                location_label=device_model.location_label,
                installed_at=device_model.installed_at
            )
            devices.append(device)
        
        return devices
    
    async def get_all(self) -> List[Device]:
        """모든 디바이스 조회"""
        session = await self._get_session()
        
        stmt = select(DeviceModel)
        result = await session.execute(stmt)
        device_models = result.scalars().all()
        
        # ORM 모델들을 도메인 엔티티로 변환
        devices = []
        for device_model in device_models:
            device = Device(
                device_id=device_model.device_id,
                user_id=str(device_model.user_id) if device_model.user_id else None,
                location_label=device_model.location_label,
                installed_at=device_model.installed_at
            )
            devices.append(device)
        
        return devices
    
    async def update(self, device: Device) -> Device:
        """디바이스 정보 업데이트"""
        session = await self._get_session()
        
        stmt = (
            update(DeviceModel)
            .where(DeviceModel.device_id == device.device_id)
            .values(
                user_id=device.user_id,
                location_label=device.location_label,
                installed_at=device.installed_at
            )
        )
        
        await session.execute(stmt)
        await session.commit()
        
        # 업데이트된 디바이스 정보 반환
        return await self.get_by_id(device.device_id)
    
    async def delete(self, device_id: str) -> bool:
        """디바이스 삭제"""
        session = await self._get_session()
        
        stmt = delete(DeviceModel).where(DeviceModel.device_id == device_id)
        result = await session.execute(stmt)
        await session.commit()
        
        return result.rowcount > 0
    
    async def assign_to_user(self, device_id: str, user_id: str) -> Device:
        """디바이스를 사용자에게 할당"""
        session = await self._get_session()
        
        stmt = (
            update(DeviceModel)
            .where(DeviceModel.device_id == device_id)
            .values(user_id=user_id)
        )
        
        await session.execute(stmt)
        await session.commit()
        
        # 할당된 디바이스 정보 반환
        return await self.get_by_id(device_id)
    
    async def unassign_from_user(self, device_id: str) -> Device:
        """디바이스 사용자 할당 해제"""
        session = await self._get_session()
        
        stmt = (
            update(DeviceModel)
            .where(DeviceModel.device_id == device_id)
            .values(user_id=None)
        )
        
        await session.execute(stmt)
        await session.commit()
        
        # 할당 해제된 디바이스 정보 반환
        return await self.get_by_id(device_id)
    
    async def exists(self, device_id: str) -> bool:
        """디바이스 존재 여부 확인"""
        session = await self._get_session()
        
        stmt = select(DeviceModel).where(DeviceModel.device_id == device_id)
        result = await session.execute(stmt)
        device_model = result.scalar_one_or_none()
        
        return device_model is not None
    
    async def close(self):
        """세션 종료"""
        if self._session:
            await self._session.close()
            self._session = None 