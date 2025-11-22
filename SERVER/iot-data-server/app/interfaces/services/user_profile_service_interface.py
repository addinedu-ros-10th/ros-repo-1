from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.api.v1.schemas import UserProfileCreate, UserProfileUpdate, UserProfileResponse


class IUserProfileService(ABC):
    """사용자 프로필 서비스 인터페이스"""
    
    @abstractmethod
    async def create_profile(self, profile_data: UserProfileCreate, user_id: UUID) -> UserProfileResponse:
        """사용자 프로필을 생성합니다."""
        pass
    
    @abstractmethod
    async def get_profile_by_user_id(self, user_id: UUID) -> Optional[UserProfileResponse]:
        """사용자 ID로 프로필을 조회합니다."""
        pass
    
    @abstractmethod
    async def update_profile(self, user_id: UUID, profile_data: UserProfileUpdate) -> Optional[UserProfileResponse]:
        """사용자 프로필을 업데이트합니다."""
        pass
    
    @abstractmethod
    async def delete_profile(self, user_id: UUID) -> bool:
        """사용자 프로필을 삭제합니다."""
        pass
    
    @abstractmethod
    async def get_profiles_by_gender(self, gender: str) -> List[UserProfileResponse]:
        """특정 성별의 프로필들을 조회합니다."""
        pass
    
    @abstractmethod
    async def get_profiles_by_age_range(self, min_age: int, max_age: int) -> List[UserProfileResponse]:
        """특정 연령대의 프로필들을 조회합니다."""
        pass
    
    @abstractmethod
    async def get_all_profiles(self, skip: int = 0, limit: int = 100) -> List[UserProfileResponse]:
        """모든 사용자 프로필을 조회합니다."""
        pass
    
    @abstractmethod
    async def count_profiles(self) -> int:
        """사용자 프로필의 총 개수를 반환합니다."""
        pass
    
    @abstractmethod
    async def search_profiles_by_medical_history(self, keyword: str) -> List[UserProfileResponse]:
        """병력에 특정 키워드가 포함된 프로필들을 검색합니다."""
        pass

