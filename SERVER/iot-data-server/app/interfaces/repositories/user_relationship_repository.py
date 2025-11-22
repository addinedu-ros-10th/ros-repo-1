from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.user_relationship import UserRelationship


class IUserRelationshipRepository(ABC):
    """사용자 관계 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create_relationship(self, relationship: UserRelationship) -> UserRelationship:
        """사용자 관계를 생성합니다."""
        pass
    
    @abstractmethod
    async def get_relationship_by_id(self, relationship_id: UUID) -> Optional[UserRelationship]:
        """ID로 사용자 관계를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_relationships_by_user(self, user_id: UUID, as_subject: bool = True) -> List[UserRelationship]:
        """사용자와 관련된 관계들을 조회합니다."""
        pass
    
    @abstractmethod
    async def get_relationships_by_type(self, relationship_type: str) -> List[UserRelationship]:
        """특정 유형의 관계들을 조회합니다."""
        pass
    
    @abstractmethod
    async def update_relationship_status(self, relationship_id: UUID, status: str) -> Optional[UserRelationship]:
        """관계 상태를 업데이트합니다."""
        pass
    
    @abstractmethod
    async def delete_relationship(self, relationship_id: UUID) -> bool:
        """사용자 관계를 삭제합니다."""
        pass
    
    @abstractmethod
    async def get_all_relationships(self, skip: int = 0, limit: int = 100) -> List[UserRelationship]:
        """모든 사용자 관계를 조회합니다."""
        pass
    
    @abstractmethod
    async def count_relationships(self) -> int:
        """사용자 관계의 총 개수를 반환합니다."""
        pass

