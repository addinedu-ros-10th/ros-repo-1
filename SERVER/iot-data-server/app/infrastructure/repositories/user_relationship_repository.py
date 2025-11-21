from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.domain.entities.user_relationship import UserRelationship
from app.infrastructure.models import UserRelationship as UserRelationshipModel
from app.interfaces.repositories.user_relationship_repository import IUserRelationshipRepository


class UserRelationshipRepository(IUserRelationshipRepository):
    """사용자 관계 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_relationship(self, relationship: UserRelationship) -> UserRelationship:
        """사용자 관계를 생성합니다."""
        db_relationship = UserRelationshipModel(
            relationship_id=relationship.relationship_id,
            subject_user_id=relationship.subject_user_id,
            target_user_id=relationship.target_user_id,
            relationship_type=relationship.relationship_type,
            status=relationship.status,
            created_at=relationship.created_at,
            updated_at=relationship.updated_at
        )
        
        self.db.add(db_relationship)
        self.db.commit()
        self.db.refresh(db_relationship)
        
        return UserRelationship(
            relationship_id=db_relationship.relationship_id,
            subject_user_id=db_relationship.subject_user_id,
            target_user_id=db_relationship.target_user_id,
            relationship_type=db_relationship.relationship_type,
            status=db_relationship.status,
            created_at=db_relationship.created_at,
            updated_at=db_relationship.updated_at
        )
    
    async def get_relationship_by_id(self, relationship_id: UUID) -> Optional[UserRelationship]:
        """ID로 사용자 관계를 조회합니다."""
        result = await self.db.execute(
            select(UserRelationshipModel).where(UserRelationshipModel.relationship_id == relationship_id)
        )
        db_relationship = result.scalar_one_or_none()
        
        if db_relationship is None:
            return None
        
        return UserRelationship(
            relationship_id=db_relationship.relationship_id,
            subject_user_id=db_relationship.subject_user_id,
            target_user_id=db_relationship.target_user_id,
            relationship_type=db_relationship.relationship_type,
            status=db_relationship.status,
            created_at=db_relationship.created_at,
            updated_at=db_relationship.updated_at
        )
    
    async def get_relationships_by_user(self, user_id: UUID, as_subject: bool = True) -> List[UserRelationship]:
        """사용자와 관련된 관계들을 조회합니다."""
        if as_subject:
            result = await self.db.execute(
                select(UserRelationshipModel).where(UserRelationshipModel.subject_user_id == user_id)
            )
        else:
            result = await self.db.execute(
                select(UserRelationshipModel).where(UserRelationshipModel.target_user_id == user_id)
            )
        
        db_relationships = result.scalars().all()
        
        return [
            UserRelationship(
                relationship_id=rel.relationship_id,
                subject_user_id=rel.subject_user_id,
                target_user_id=rel.target_user_id,
                relationship_type=rel.relationship_type,
                status=rel.status,
                created_at=rel.created_at,
                updated_at=rel.updated_at
            )
            for rel in db_relationships
        ]
    
    async def get_relationships_by_type(self, relationship_type: str) -> List[UserRelationship]:
        """특정 유형의 관계들을 조회합니다."""
        result = await self.db.execute(
            select(UserRelationshipModel).where(UserRelationshipModel.relationship_type == relationship_type)
        )
        db_relationships = result.scalars().all()
        
        return [
            UserRelationship(
                relationship_id=rel.relationship_id,
                subject_user_id=rel.subject_user_id,
                target_user_id=rel.target_user_id,
                relationship_type=rel.relationship_type,
                status=rel.status,
                created_at=rel.created_at,
                updated_at=rel.updated_at
            )
            for rel in db_relationships
        ]
    
    async def update_relationship_status(self, relationship_id: UUID, status: str) -> Optional[UserRelationship]:
        """관계 상태를 업데이트합니다."""
        result = await self.db.execute(
            update(UserRelationshipModel)
            .where(UserRelationshipModel.relationship_id == relationship_id)
            .values(status=status, updated_at=UserRelationshipModel.updated_at)
        )
        
        if result.rowcount == 0:
            return None
        
        self.db.commit()
        
        # 업데이트된 관계를 반환
        return await self.get_relationship_by_id(relationship_id)
    
    async def delete_relationship(self, relationship_id: UUID) -> bool:
        """사용자 관계를 삭제합니다."""
        result = await self.db.execute(
            delete(UserRelationshipModel).where(UserRelationshipModel.relationship_id == relationship_id)
        )
        
        if result.rowcount == 0:
            return False
        
        self.db.commit()
        return True
    
    async def get_all_relationships(self, skip: int = 0, limit: int = 100) -> List[UserRelationship]:
        """모든 사용자 관계를 조회합니다."""
        result = await self.db.execute(
            select(UserRelationshipModel)
            .offset(skip)
            .limit(limit)
        )
        db_relationships = result.scalars().all()
        
        return [
            UserRelationship(
                relationship_id=rel.relationship_id,
                subject_user_id=rel.subject_user_id,
                target_user_id=rel.target_user_id,
                relationship_type=rel.relationship_type,
                status=rel.status,
                created_at=rel.created_at,
                updated_at=rel.updated_at
            )
            for rel in db_relationships
        ]
    
    async def count_relationships(self) -> int:
        """사용자 관계의 총 개수를 반환합니다."""
        result = await self.db.execute(select(UserRelationshipModel))
        return len(result.scalars().all())

