"""
PostgreSQL User 리포지토리 구현체

실제 데이터베이스와 연동하는 User 리포지토리입니다.
"""

from typing import List, Optional
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload

from app.interfaces.repositories.user_repository import IUserRepository
from app.domain.entities.user import User
from app.infrastructure.models import User as UserModel
from app.infrastructure.database import get_session


class PostgreSQLUserRepository(IUserRepository):
    """PostgreSQL 기반 User 리포지토리"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
    
    async def _get_session(self) -> AsyncSession:
        """세션 가져오기 - 주입된 세션 사용"""
        return self.db_session
    
    async def create(self, user: User) -> User:
        """사용자 생성"""
        session = await self._get_session()
        
        # 도메인 엔티티를 ORM 모델로 변환
        user_model = UserModel(
            user_id=user.user_id,
            user_role=user.user_role,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            created_at=user.created_at
        )
        
        session.add(user_model)
        await session.commit()
        await session.refresh(user_model)
        
        # ORM 모델을 도메인 엔티티로 변환하여 반환
        return User(
            user_id=user_model.user_id,
            user_role=user_model.user_role,
            user_name=user_model.user_name,
            email=user_model.email,
            phone_number=user_model.phone_number,
            created_at=user_model.created_at
        )
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        session = await self._get_session()
        
        stmt = select(UserModel).where(UserModel.user_id == user_id)
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model is None:
            return None
        
        # ORM 모델을 도메인 엔티티로 변환
        return User(
            user_id=user_model.user_id,
            user_role=user_model.user_role,
            user_name=user_model.user_name,
            email=user_model.email,
            phone_number=user_model.phone_number,
            created_at=user_model.created_at
        )
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        session = await self._get_session()
        
        stmt = select(UserModel).where(UserModel.email == email)
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if user_model is None:
            return None
        
        # ORM 모델을 도메인 엔티티로 변환
        return User(
            user_id=user_model.user_id,
            user_role=user_model.user_role,
            user_name=user_model.user_name,
            email=user_model.email,
            phone_number=user_model.phone_number,
            created_at=user_model.created_at
        )
    
    async def get_all(self) -> List[User]:
        """모든 사용자 조회"""
        session = await self._get_session()
        
        stmt = select(UserModel)
        result = await session.execute(stmt)
        user_models = result.scalars().all()
        
        # ORM 모델들을 도메인 엔티티로 변환
        users = []
        for user_model in user_models:
            user = User(
                user_id=user_model.user_id,
                user_role=user_model.user_role,
                user_name=user_model.user_name,
                email=user_model.email,
                phone_number=user_model.phone_number,
                created_at=user_model.created_at
            )
            users.append(user)
        
        return users
    
    async def get_by_role(self, role: str) -> List[User]:
        """역할별 사용자 조회"""
        session = await self._get_session()
        
        stmt = select(UserModel).where(UserModel.user_role == role)
        result = await session.execute(stmt)
        user_models = result.scalars().all()
        
        # ORM 모델들을 도메인 엔티티로 변환
        users = []
        for user_model in user_models:
            user = User(
                user_id=user_model.user_id,
                user_role=user_model.user_role,
                user_name=user_model.user_name,
                email=user_model.email,
                phone_number=user_model.phone_number,
                created_at=user_model.created_at
            )
            users.append(user)
        
        return users
    
    async def update(self, user_id: str, update_data: dict) -> User:
        """사용자 정보 업데이트"""
        session = await self._get_session()
        
        stmt = (
            update(UserModel)
            .where(UserModel.user_id == user_id)
            .values(**update_data)
        )
        
        await session.execute(stmt)
        await session.commit()
        
        # 업데이트된 사용자 정보 반환
        return await self.get_by_id(user_id)
    
    async def delete(self, user_id: str) -> bool:
        """사용자 삭제"""
        session = await self._get_session()
        
        stmt = delete(UserModel).where(UserModel.user_id == user_id)
        result = await session.execute(stmt)
        await session.commit()
        
        return result.rowcount > 0
    
    async def exists(self, user_id: str) -> bool:
        """사용자 존재 여부 확인"""
        session = await self._get_session()
        
        stmt = select(UserModel).where(UserModel.user_id == user_id)
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        return user_model is not None
    
    async def close(self):
        """세션 종료 - 더 이상 필요하지 않음"""
        pass 