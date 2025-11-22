from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import selectinload
from datetime import date, datetime

from app.domain.entities.user_profile import UserProfile
from app.infrastructure.models import UserProfile as UserProfileModel
from app.interfaces.repositories.user_profile_repository import IUserProfileRepository


class UserProfileRepository(IUserProfileRepository):
    """사용자 프로필 리포지토리 구현체"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_profile(self, profile: UserProfile) -> UserProfile:
        """사용자 프로필을 생성합니다."""
        db_profile = UserProfileModel(
            user_id=profile.user_id,
            date_of_birth=profile.date_of_birth,
            gender=profile.gender,
            address=profile.address,
            address_detail=profile.address_detail,
            medical_history=profile.medical_history,
            significant_notes=profile.significant_notes,
            current_status=profile.current_status,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
        
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        
        return UserProfile(
            user_id=db_profile.user_id,
            date_of_birth=db_profile.date_of_birth,
            gender=db_profile.gender,
            address=db_profile.address,
            address_detail=db_profile.address_detail,
            medical_history=db_profile.medical_history,
            significant_notes=db_profile.significant_notes,
            current_status=db_profile.current_status,
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at
        )
    
    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """사용자 ID로 프로필을 조회합니다."""
        result = await self.db.execute(
            select(UserProfileModel).where(UserProfileModel.user_id == user_id)
        )
        db_profile = result.scalar_one_or_none()
        
        if db_profile is None:
            return None
        
        return UserProfile(
            user_id=db_profile.user_id,
            date_of_birth=db_profile.date_of_birth,
            gender=db_profile.gender,
            address=db_profile.address,
            address_detail=db_profile.address_detail,
            medical_history=db_profile.medical_history,
            significant_notes=db_profile.significant_notes,
            current_status=db_profile.current_status,
            created_at=db_profile.created_at,
            updated_at=db_profile.updated_at
        )
    
    async def update_profile(self, user_id: UUID, profile_data: dict) -> Optional[UserProfile]:
        """사용자 프로필을 업데이트합니다."""
        # updated_at 필드를 현재 시간으로 설정
        profile_data['updated_at'] = datetime.utcnow()
        
        result = await self.db.execute(
            update(UserProfileModel)
            .where(UserProfileModel.user_id == user_id)
            .values(**profile_data)
        )
        
        if result.rowcount == 0:
            return None
        
        self.db.commit()
        
        # 업데이트된 프로필을 반환
        return await self.get_profile_by_user_id(user_id)
    
    async def delete_profile(self, user_id: UUID) -> bool:
        """사용자 프로필을 삭제합니다."""
        result = await self.db.execute(
            delete(UserProfileModel).where(UserProfileModel.user_id == user_id)
        )
        
        if result.rowcount == 0:
            return False
        
        self.db.commit()
        return True
    
    async def get_profiles_by_gender(self, gender: str) -> List[UserProfile]:
        """특정 성별의 프로필들을 조회합니다."""
        result = await self.db.execute(
            select(UserProfileModel).where(UserProfileModel.gender == gender)
        )
        db_profiles = result.scalars().all()
        
        return [
            UserProfile(
                user_id=profile.user_id,
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                address=profile.address,
                address_detail=profile.address_detail,
                medical_history=profile.medical_history,
                significant_notes=profile.significant_notes,
                current_status=profile.current_status,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            for profile in db_profiles
        ]
    
    async def get_profiles_by_age_range(self, min_age: int, max_age: int) -> List[UserProfile]:
        """특정 연령대의 프로필들을 조회합니다."""
        today = date.today()
        max_birth_date = today.replace(year=today.year - min_age)
        min_birth_date = today.replace(year=today.year - max_age)
        
        result = await self.db.execute(
            select(UserProfileModel).where(
                UserProfileModel.date_of_birth.between(min_birth_date, max_birth_date)
            )
        )
        db_profiles = result.scalars().all()
        
        return [
            UserProfile(
                user_id=profile.user_id,
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                address=profile.address,
                address_detail=profile.address_detail,
                medical_history=profile.medical_history,
                significant_notes=profile.significant_notes,
                current_status=profile.current_status,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            for profile in db_profiles
        ]
    
    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        """모든 사용자 프로필을 조회합니다."""
        result = await self.db.execute(
            select(UserProfileModel)
            .offset(skip)
            .limit(limit)
        )
        db_profiles = result.scalars().all()
        
        return [
            UserProfile(
                user_id=profile.user_id,
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                address=profile.address,
                address_detail=profile.address_detail,
                medical_history=profile.medical_history,
                significant_notes=profile.significant_notes,
                current_status=profile.current_status,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            for profile in db_profiles
        ]
    
    async def count_profiles(self) -> int:
        """사용자 프로필의 총 개수를 반환합니다."""
        result = await self.db.execute(select(UserProfileModel))
        return len(result.scalars().all())
    
    async def search_profiles_by_medical_history(self, keyword: str) -> List[UserProfile]:
        """병력에 특정 키워드가 포함된 프로필들을 검색합니다."""
        result = await self.db.execute(
            select(UserProfileModel).where(
                UserProfileModel.medical_history.ilike(f'%{keyword}%')
            )
        )
        db_profiles = result.scalars().all()
        
        return [
            UserProfile(
                user_id=profile.user_id,
                date_of_birth=profile.date_of_birth,
                gender=profile.gender,
                address=profile.address,
                address_detail=profile.address_detail,
                medical_history=profile.medical_history,
                significant_notes=profile.significant_notes,
                current_status=profile.current_status,
                created_at=profile.created_at,
                updated_at=profile.updated_at
            )
            for profile in db_profiles
        ]

