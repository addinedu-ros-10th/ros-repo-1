from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.api.v1.schemas import UserRelationshipCreate, UserRelationshipUpdate, UserRelationshipResponse


class IUserRelationshipService(ABC):
    """사용자 관계 서비스 인터페이스"""
    
    @abstractmethod
    async def create_relationship(self, relationship_data: UserRelationshipCreate) -> UserRelationshipResponse:
        """사용자 관계를 생성합니다."""
        pass
    
    @abstractmethod
    async def get_relationship_by_id(self, relationship_id: UUID) -> Optional[UserRelationshipResponse]:
        """ID로 사용자 관계를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_relationships_by_user(self, user_id: UUID, as_subject: bool = True) -> List[UserRelationshipResponse]:
        """사용자와 관련된 관계들을 조회합니다."""
        pass
    
    @abstractmethod
    async def get_relationships_by_type(self, relationship_type: str) -> List[UserRelationshipResponse]:
        """특정 유형의 관계들을 조회합니다."""
        pass
    
    @abstractmethod
    async def update_relationship_status(self, relationship_id: UUID, status: str) -> Optional[UserRelationshipResponse]:
        """관계 상태를 업데이트합니다."""
        pass
    
    @abstractmethod
    async def delete_relationship(self, relationship_id: UUID) -> bool:
        """사용자 관계를 삭제합니다."""
        pass
    
    @abstractmethod
    async def get_all_relationships(self, skip: int = 0, limit: int = 100) -> List[UserRelationshipResponse]:
        """모든 사용자 관계를 조회합니다."""
        pass
    
    @abstractmethod
    async def count_relationships(self) -> int:
        """사용자 관계의 총 개수를 반환합니다."""
        pass

