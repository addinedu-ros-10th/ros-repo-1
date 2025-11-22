"""
ResidentInfo 리포지토리 인터페이스

요양원 내부 입소자 관리 정보 리포지토리의 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from app.domain.entities.resident_info import ResidentInfo


class IResidentInfoRepository(ABC):
    """요양원 내부 입소자 관리 정보 리포지토리 인터페이스"""
    
    @abstractmethod
    async def create_resident_info(self, resident_info: ResidentInfo) -> ResidentInfo:
        """입소자 정보를 생성합니다."""
        pass
    
    @abstractmethod
    async def get_resident_info_by_user_id(self, user_id: UUID) -> Optional[ResidentInfo]:
        """사용자 ID로 입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_resident_info_by_resident_number(self, resident_number: str) -> Optional[ResidentInfo]:
        """입소자 번호로 입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def update_resident_info(self, user_id: UUID, resident_data: Dict[str, Any]) -> Optional[ResidentInfo]:
        """입소자 정보를 업데이트합니다."""
        pass
    
    @abstractmethod
    async def delete_resident_info(self, user_id: UUID) -> bool:
        """입소자 정보를 삭제합니다."""
        pass
    
    @abstractmethod
    async def get_all_residents(self, skip: int = 0, limit: int = 100) -> List[ResidentInfo]:
        """모든 입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_current_residents(self, skip: int = 0, limit: int = 100) -> List[ResidentInfo]:
        """현재 입소 중인 입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_residents_by_room(self, room_number: str) -> List[ResidentInfo]:
        """특정 생활실의 입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_residents_by_floor(self, floor_number: int) -> List[ResidentInfo]:
        """특정 층의 입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_residents_by_adl_level(self, adl_level: str) -> List[ResidentInfo]:
        """특정 ADL 수준의 입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def count_residents(self) -> int:
        """입소자 정보의 총 개수를 반환합니다."""
        pass
    
    @abstractmethod
    async def count_current_residents(self) -> int:
        """현재 입소 중인 입소자의 수를 반환합니다."""
        pass
    
    @abstractmethod
    async def search_residents(self, keyword: str) -> List[ResidentInfo]:
        """키워드로 입소자 정보를 검색합니다."""
        pass

