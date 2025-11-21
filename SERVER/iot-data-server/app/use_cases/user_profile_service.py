from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.domain.entities.user_profile import UserProfile
from app.interfaces.services.user_profile_service_interface import IUserProfileService
from app.interfaces.repositories.user_profile_repository import IUserProfileRepository
from app.api.v1.schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse


class UserProfileService(IUserProfileService):
    """사용자 프로필 서비스 구현체"""
    
    def __init__(self, profile_repository: IUserProfileRepository):
        self.profile_repository = profile_repository
    
    async def create_profile(self, profile_data: UserProfileCreate, user_id: UUID) -> UserProfileResponse:
        """사용자 프로필을 생성합니다."""
        # 도메인 엔티티 생성
        profile = UserProfile(
            user_id=user_id,
            date_of_birth=profile_data.date_of_birth,
            gender=profile_data.gender,
            address=profile_data.address,
            address_detail=profile_data.address_detail,
            medical_history=profile_data.medical_history,
            significant_notes=profile_data.significant_notes,
            current_status=profile_data.current_status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 리포지토리를 통해 저장
        created_profile = await self.profile_repository.create_profile(profile)
        
        # 응답 스키마로 변환
        return UserProfileResponse(
            user_id=created_profile.user_id,
            date_of_birth=created_profile.date_of_birth,
            gender=created_profile.gender,
            address=created_profile.address,
            address_detail=created_profile.address_detail,
            medical_history=created_profile.medical_history,
            significant_notes=created_profile.significant_notes,
            current_status=created_profile.current_status,
            created_at=created_profile.created_at,
            updated_at=created_profile.updated_at
        )
    
    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[UserProfileResponse]:
        """사용자 ID로 프로필을 조회합니다."""
        profile = await self.profile_repository.get_profile_by_user_id(user_id)
        
        if profile is None:
            return None
        
        return UserProfileResponse(
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
    
    async def update_profile(self, user_id: UUID, profile_data: UserProfileUpdate) -> Optional[UserProfileResponse]:
        """사용자 프로필을 업데이트합니다."""
        # 업데이트할 데이터 준비
        update_data = {}
        if profile_data.address is not None:
            update_data['address'] = profile_data.address
        if profile_data.address_detail is not None:
            update_data['address_detail'] = profile_data.address_detail
        if profile_data.medical_history is not None:
            update_data['medical_history'] = profile_data.medical_history
        if profile_data.significant_notes is not None:
            update_data['significant_notes'] = profile_data.significant_notes
        if profile_data.current_status is not None:
            update_data['current_status'] = profile_data.current_status
        
        # 리포지토리를 통해 업데이트
        updated_profile = await self.profile_repository.update_profile(user_id, update_data)
        
        if updated_profile is None:
            return None
        
        # 응답 스키마로 변환
        return UserProfileResponse(
            user_id=updated_profile.user_id,
            date_of_birth=updated_profile.date_of_birth,
            gender=updated_profile.gender,
            address=updated_profile.address,
            address_detail=updated_profile.address_detail,
            medical_history=updated_profile.medical_history,
            significant_notes=updated_profile.significant_notes,
            current_status=updated_profile.current_status,
            created_at=updated_profile.created_at,
            updated_at=updated_profile.updated_at
        )
    
    async def delete_profile(self, user_id: UUID) -> bool:
        """사용자 프로필을 삭제합니다."""
        return await self.profile_repository.delete_profile(user_id)
    
    async def get_profiles_by_gender(self, gender: str) -> List[UserProfileResponse]:
        """특정 성별의 프로필들을 조회합니다."""
        profiles = await self.profile_repository.get_profiles_by_gender(gender)
        
        return [
            UserProfileResponse(
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
            for profile in profiles
        ]
    
    async def get_profiles_by_age_range(self, min_age: int, max_age: int) -> List[UserProfileResponse]:
        """특정 연령대의 프로필들을 조회합니다."""
        profiles = await self.profile_repository.get_profiles_by_age_range(min_age, max_age)
        
        return [
            UserProfileResponse(
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
            for profile in profiles
        ]
    
    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> List[UserProfileResponse]:
        """모든 사용자 프로필을 조회합니다."""
        profiles = await self.profile_repository.get_all_profiles(skip, limit)
        
        return [
            UserProfileResponse(
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
            for profile in profiles
        ]
    
    async def count_profiles(self) -> int:
        """사용자 프로필의 총 개수를 반환합니다."""
        return await self.profile_repository.count_profiles()
    
    async def search_profiles_by_medical_history(self, keyword: str) -> List[UserProfileResponse]:
        """병력에 특정 키워드가 포함된 프로필들을 검색합니다."""
        profiles = await self.profile_repository.search_profiles_by_medical_history(keyword)
        
        return [
            UserProfileResponse(
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
            for profile in profiles
        ]

