"""
User 리포지토리 인터페이스

사용자 데이터 접근을 위한 추상 인터페이스입니다.
Clean Architecture의 의존성 역전 원칙을 구현합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from app.domain.entities.user import User


class IUserRepository(ABC):
    """사용자 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """새로운 사용자를 생성합니다."""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[User]:
        """모든 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_by_role(self, role: str) -> List[User]:
        """역할별 사용자를 조회합니다."""
        pass
    
    @abstractmethod
    async def update(self, user_id: str, update_data: dict) -> User:
        """사용자 정보를 업데이트합니다."""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """사용자를 삭제합니다."""
        pass
    
    @abstractmethod
    async def exists(self, user_id: UUID) -> bool:
        """사용자 존재 여부를 확인합니다."""
        pass 