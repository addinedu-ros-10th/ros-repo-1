"""
User 서비스 인터페이스

사용자 관련 비즈니스 로직을 위한 추상 인터페이스입니다.
Clean Architecture의 의존성 역전 원칙을 구현합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.user import User


class IUserService(ABC):
    """사용자 서비스 인터페이스"""
    
    @abstractmethod
    async def create_user(self, name: str, role: str = "user", email: str = None, phone: str = None) -> User:
        """새로운 사용자를 생성합니다."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_all_users(self) -> List[User]:
        """모든 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_users_by_role(self, role: str) -> List[User]:
        """역할별 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def update_user_profile(self, user_id: UUID, name: str = None, email: str = None, phone: str = None) -> User:
        """사용자 프로필을 업데이트합니다."""
        pass
    
    @abstractmethod
    async def change_user_role(self, user_id: UUID, new_role: str) -> User:
        """사용자 역할을 변경합니다."""
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: UUID) -> bool:
        """사용자를 삭제합니다."""
        pass
    
    @abstractmethod
    async def validate_user_permissions(self, user: User, required_role: str) -> bool:
        """사용자 권한을 검증합니다."""
        pass
    
    @abstractmethod
    async def can_manage_user(self, admin_user: User, target_user: User) -> bool:
        """사용자 관리 권한을 확인합니다."""
        pass 