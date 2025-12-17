"""
ResidentInfo 서비스 구현체

요양원 내부 입소자 관리 정보 서비스의 구현체입니다.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
import math

from app.domain.entities.resident_info import ResidentInfo
from app.interfaces.services.resident_info_service_interface import IResidentInfoService
from app.interfaces.repositories.resident_info_repository import IResidentInfoRepository


class ResidentInfoService(IResidentInfoService):
    """요양원 내부 입소자 관리 정보 서비스 구현체"""
    
    def __init__(self, resident_repository: IResidentInfoRepository):
        self.resident_repository = resident_repository
    
    async def create_resident_info(self, user_id: UUID, resident_data: Dict[str, Any]) -> ResidentInfo:
        """입소자 정보를 생성합니다."""
        # 도메인 엔티티 생성
        resident_info = ResidentInfo(
            user_id=user_id,
            admission_date=resident_data["admission_date"],
            resident_number=resident_data.get("resident_number"),
            nickname=resident_data.get("nickname"),
            discharge_date=resident_data.get("discharge_date"),
            room_number=resident_data.get("room_number"),
            floor_number=resident_data.get("floor_number"),
            bed_number=resident_data.get("bed_number"),
            adl_level=resident_data.get("adl_level", "independent"),
            mobility_level=resident_data.get("mobility_level"),
            cognitive_level=resident_data.get("cognitive_level"),
            medication_schedule=resident_data.get("medication_schedule"),
            medication_notes=resident_data.get("medication_notes"),
            special_notes=resident_data.get("special_notes"),
            incidents=resident_data.get("incidents"),
            dietary_restrictions=resident_data.get("dietary_restrictions"),
            emergency_contacts=resident_data.get("emergency_contacts"),
            insurance_info=resident_data.get("insurance_info"),
            medical_facility_info=resident_data.get("medical_facility_info"),
            care_level=resident_data.get("care_level"),
            guardian_name=resident_data.get("guardian_name"),
            guardian_relationship=resident_data.get("guardian_relationship"),
            guardian_phone=resident_data.get("guardian_phone"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 리포지토리를 통해 저장
        return await self.resident_repository.create_resident_info(resident_info)
    
    async def get_resident_info(self, user_id: UUID) -> Optional[ResidentInfo]:
        """입소자 정보를 조회합니다."""
        return await self.resident_repository.get_resident_info_by_user_id(user_id)
    
    async def get_resident_info_by_number(self, resident_number: str) -> Optional[ResidentInfo]:
        """입소자 번호로 입소자 정보를 조회합니다."""
        return await self.resident_repository.get_resident_info_by_resident_number(resident_number)
    
    async def update_resident_info(self, user_id: UUID, resident_data: Dict[str, Any]) -> Optional[ResidentInfo]:
        """입소자 정보를 업데이트합니다."""
        return await self.resident_repository.update_resident_info(user_id, resident_data)
    
    async def delete_resident_info(self, user_id: UUID) -> bool:
        """입소자 정보를 삭제합니다."""
        return await self.resident_repository.delete_resident_info(user_id)
    
    async def get_all_residents(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """모든 입소자 정보를 조회합니다 (페이지네이션)."""
        skip = (page - 1) * size
        residents = await self.resident_repository.get_all_residents(skip=skip, limit=size)
        total = await self.resident_repository.count_residents()
        pages = math.ceil(total / size) if total > 0 else 0
        
        return {
            "residents": residents,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
    
    async def get_current_residents(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """현재 입소 중인 입소자 정보를 조회합니다 (페이지네이션)."""
        skip = (page - 1) * size
        residents = await self.resident_repository.get_current_residents(skip=skip, limit=size)
        total = await self.resident_repository.count_current_residents()
        pages = math.ceil(total / size) if total > 0 else 0
        
        return {
            "residents": residents,
            "total": total,
            "page": page,
            "size": size,
            "pages": pages
        }
    
    async def get_residents_by_room(self, room_number: str) -> List[ResidentInfo]:
        """특정 생활실의 입소자 정보를 조회합니다."""
        return await self.resident_repository.get_residents_by_room(room_number)
    
    async def get_residents_by_floor(self, floor_number: int) -> List[ResidentInfo]:
        """특정 층의 입소자 정보를 조회합니다."""
        return await self.resident_repository.get_residents_by_floor(floor_number)
    
    async def get_residents_by_adl_level(self, adl_level: str) -> List[ResidentInfo]:
        """특정 ADL 수준의 입소자 정보를 조회합니다."""
        return await self.resident_repository.get_residents_by_adl_level(adl_level)
    
    async def search_residents(self, keyword: str) -> List[ResidentInfo]:
        """키워드로 입소자 정보를 검색합니다."""
        return await self.resident_repository.search_residents(keyword)
    
    async def discharge_resident(self, user_id: UUID, discharge_date: date) -> Optional[ResidentInfo]:
        """입소자를 퇴소 처리합니다."""
        resident = await self.resident_repository.get_resident_info_by_user_id(user_id)
        if not resident:
            return None
        
        if resident.discharge_date is not None:
            raise ValueError("이미 퇴소 처리된 입소자입니다.")
        
        if discharge_date < resident.admission_date:
            raise ValueError("퇴소일은 입소일 이후여야 합니다.")
        
        return await self.resident_repository.update_resident_info(user_id, {"discharge_date": discharge_date})
    
    async def add_incident(self, user_id: UUID, incident: Dict[str, Any]) -> Optional[ResidentInfo]:
        """사건/사고 기록을 추가합니다."""
        resident = await self.resident_repository.get_resident_info_by_user_id(user_id)
        if not resident:
            return None
        
        resident.add_incident(incident)
        
        # incidents를 업데이트
        return await self.resident_repository.update_resident_info(
            user_id,
            {"incidents": resident.incidents}
        )
    
    async def update_medication_schedule(self, user_id: UUID, schedule: List[Dict[str, Any]]) -> Optional[ResidentInfo]:
        """복약 일정을 업데이트합니다."""
        resident = await self.resident_repository.get_resident_info_by_user_id(user_id)
        if not resident:
            return None
        
        resident.update_medication_schedule(schedule)
        
        # medication_schedule을 업데이트
        return await self.resident_repository.update_resident_info(
            user_id,
            {"medication_schedule": resident.medication_schedule}
        )

