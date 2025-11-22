"""
ResidentInfo 서비스 인터페이스

요양원 내부 입소자 관리 정보 서비스의 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date

from app.domain.entities.resident_info import ResidentInfo


class IResidentInfoService(ABC):
    """요양원 내부 입소자 관리 정보 서비스 인터페이스"""
    
    @abstractmethod
    async def create_resident_info(self, user_id: UUID, resident_data: Dict[str, Any]) -> ResidentInfo:
        """입소자 정보를 생성합니다."""
        pass
    
    @abstractmethod
    async def get_resident_info(self, user_id: UUID) -> Optional[ResidentInfo]:
        """입소자 정보를 조회합니다."""
        pass
    
    @abstractmethod
    async def get_resident_info_by_number(self, resident_number: str) -> Optional[ResidentInfo]:
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
    async def get_all_residents(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """모든 입소자 정보를 조회합니다 (페이지네이션)."""
        pass
    
    @abstractmethod
    async def get_current_residents(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """현재 입소 중인 입소자 정보를 조회합니다 (페이지네이션)."""
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
    async def search_residents(self, keyword: str) -> List[ResidentInfo]:
        """키워드로 입소자 정보를 검색합니다."""
        pass
    
    @abstractmethod
    async def discharge_resident(self, user_id: UUID, discharge_date: date) -> Optional[ResidentInfo]:
        """입소자를 퇴소 처리합니다."""
        pass
    
    @abstractmethod
    async def add_incident(self, user_id: UUID, incident: Dict[str, Any]) -> Optional[ResidentInfo]:
        """사건/사고 기록을 추가합니다."""
        pass
    
    @abstractmethod
    async def update_medication_schedule(self, user_id: UUID, schedule: List[Dict[str, Any]]) -> Optional[ResidentInfo]:
        """복약 일정을 업데이트합니다."""
        pass

