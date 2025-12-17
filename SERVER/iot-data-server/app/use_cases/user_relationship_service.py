from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.domain.entities.user_relationship import UserRelationship
from app.interfaces.services.user_relationship_service_interface import IUserRelationshipService
from app.interfaces.repositories.user_relationship_repository import IUserRelationshipRepository
from app.api.v1.schemas import UserRelationshipCreate, UserRelationshipUpdate, UserRelationshipResponse


class UserRelationshipService(IUserRelationshipService):
    """사용자 관계 서비스 구현체"""
    
    def __init__(self, relationship_repository: IUserRelationshipRepository):
        self.relationship_repository = relationship_repository
    
    async def create_relationship(self, relationship_data: UserRelationshipCreate) -> UserRelationshipResponse:
        """사용자 관계를 생성합니다."""
        # 도메인 엔티티 생성
        relationship = UserRelationship(
            relationship_id=uuid4(),
            subject_user_id=relationship_data.subject_user_id,
            target_user_id=relationship_data.target_user_id,
            relationship_type=relationship_data.relationship_type,
            status=relationship_data.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 리포지토리를 통해 저장
        created_relationship = await self.relationship_repository.create_relationship(relationship)
        
        # 응답 스키마로 변환
        return UserRelationshipResponse(
            relationship_id=created_relationship.relationship_id,
            subject_user_id=created_relationship.subject_user_id,
            target_user_id=created_relationship.target_user_id,
            relationship_type=created_relationship.relationship_type,
            status=created_relationship.status,
            created_at=created_relationship.created_at,
            updated_at=created_relationship.updated_at
        )
    
    async def get_relationship_by_id(self, relationship_id: UUID) -> Optional[UserRelationshipResponse]:
        """ID로 사용자 관계를 조회합니다."""
        relationship = await self.relationship_repository.get_relationship_by_id(relationship_id)
        
        if relationship is None:
            return None
        
        return UserRelationshipResponse(
            relationship_id=relationship.relationship_id,
            subject_user_id=relationship.subject_user_id,
            target_user_id=relationship.target_user_id,
            relationship_type=relationship.relationship_type,
            status=relationship.status,
            created_at=relationship.created_at,
            updated_at=relationship.updated_at
        )
    
    async def get_relationships_by_user(self, user_id: UUID, as_subject: bool = True) -> List[UserRelationshipResponse]:
        """사용자와 관련된 관계들을 조회합니다."""
        relationships = await self.relationship_repository.get_relationships_by_user(user_id, as_subject)
        
        return [
            UserRelationshipResponse(
                relationship_id=rel.relationship_id,
                subject_user_id=rel.subject_user_id,
                target_user_id=rel.target_user_id,
                relationship_type=rel.relationship_type,
                status=rel.status,
                created_at=rel.created_at,
                updated_at=rel.updated_at
            )
            for rel in relationships
        ]
    
    async def get_relationships_by_type(self, relationship_type: str) -> List[UserRelationshipResponse]:
        """특정 유형의 관계들을 조회합니다."""
        relationships = await self.relationship_repository.get_relationships_by_type(relationship_type)
        
        return [
            UserRelationshipResponse(
                relationship_id=rel.relationship_id,
                subject_user_id=rel.subject_user_id,
                target_user_id=rel.target_user_id,
                relationship_type=rel.relationship_type,
                status=rel.status,
                created_at=rel.created_at,
                updated_at=rel.updated_at
            )
            for rel in relationships
        ]
    
    async def update_relationship_status(self, relationship_id: UUID, status: str) -> Optional[UserRelationshipResponse]:
        """관계 상태를 업데이트합니다."""
        updated_relationship = await self.relationship_repository.update_relationship_status(relationship_id, status)
        
        if updated_relationship is None:
            return None
        
        return UserRelationshipResponse(
            relationship_id=updated_relationship.relationship_id,
            subject_user_id=updated_relationship.subject_user_id,
            target_user_id=updated_relationship.target_user_id,
            relationship_type=updated_relationship.relationship_type,
            status=updated_relationship.status,
            created_at=updated_relationship.created_at,
            updated_at=updated_relationship.updated_at
        )
    
    async def delete_relationship(self, relationship_id: UUID) -> bool:
        """사용자 관계를 삭제합니다."""
        return await self.relationship_repository.delete_relationship(relationship_id)
    
    async def get_all_relationships(self, skip: int = 0, limit: int = 100) -> List[UserRelationshipResponse]:
        """모든 사용자 관계를 조회합니다."""
        relationships = await self.relationship_repository.get_all_relationships(skip, limit)
        
        return [
            UserRelationshipResponse(
                relationship_id=rel.relationship_id,
                subject_user_id=rel.subject_user_id,
                target_user_id=rel.target_user_id,
                relationship_type=rel.relationship_type,
                status=rel.status,
                created_at=rel.created_at,
                updated_at=rel.updated_at
            )
            for rel in relationships
        ]
    
    async def count_relationships(self) -> int:
        """사용자 관계의 총 개수를 반환합니다."""
        return await self.relationship_repository.count_relationships()

