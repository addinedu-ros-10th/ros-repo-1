"""
ResidentInfo 리포지토리 구현체

요양원 내부 입소자 관리 정보 리포지토리의 PostgreSQL 구현체입니다.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from sqlalchemy.orm import selectinload

from app.interfaces.repositories.resident_info_repository import IResidentInfoRepository
from app.domain.entities.resident_info import ResidentInfo
from app.infrastructure.models import ResidentInfo as ResidentInfoModel


class ResidentInfoRepository(IResidentInfoRepository):
    """요양원 내부 입소자 관리 정보 리포지토리 구현체"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
    
    def _model_to_entity(self, model: ResidentInfoModel) -> Optional[ResidentInfo]:
        """ORM 모델을 도메인 엔티티로 변환"""
        if model is None:
            return None
        return ResidentInfo(
            user_id=UUID(str(model.user_id)),
            user_name=model.user_name,
            email=model.email,
            phone_number=model.phone_number,
            resident_number=model.resident_number,
            nickname=model.nickname,
            admission_date=model.admission_date,
            discharge_date=model.discharge_date,
            room_number=model.room_number,
            floor_number=model.floor_number,
            bed_number=model.bed_number,
            adl_level=model.adl_level,
            mobility_level=model.mobility_level,
            cognitive_level=model.cognitive_level,
            medication_schedule=model.medication_schedule,
            medication_notes=model.medication_notes,
            special_notes=model.special_notes,
            incidents=model.incidents,
            dietary_restrictions=model.dietary_restrictions,
            emergency_contacts=model.emergency_contacts,
            insurance_info=model.insurance_info,
            medical_facility_info=model.medical_facility_info,
            care_level=model.care_level,
            guardian_name=model.guardian_name,
            guardian_relationship=model.guardian_relationship,
            guardian_phone=model.guardian_phone,
            created_at=model.created_at or datetime.utcnow(),
            updated_at=model.updated_at or datetime.utcnow()
        )
    
    def _entity_to_model(self, entity: ResidentInfo) -> ResidentInfoModel:
        """도메인 엔티티를 ORM 모델로 변환"""
        return ResidentInfoModel(
            user_id=str(entity.user_id),
            user_name=entity.user_name,
            email=entity.email,
            phone_number=entity.phone_number,
            resident_number=entity.resident_number,
            nickname=entity.nickname,
            admission_date=entity.admission_date,
            discharge_date=entity.discharge_date,
            room_number=entity.room_number,
            floor_number=entity.floor_number,
            bed_number=entity.bed_number,
            adl_level=entity.adl_level,
            mobility_level=entity.mobility_level,
            cognitive_level=entity.cognitive_level,
            medication_schedule=entity.medication_schedule,
            medication_notes=entity.medication_notes,
            special_notes=entity.special_notes,
            incidents=entity.incidents,
            dietary_restrictions=entity.dietary_restrictions,
            emergency_contacts=entity.emergency_contacts,
            insurance_info=entity.insurance_info,
            medical_facility_info=entity.medical_facility_info,
            care_level=entity.care_level,
            guardian_name=entity.guardian_name,
            guardian_relationship=entity.guardian_relationship,
            guardian_phone=entity.guardian_phone
        )
    
    async def create_resident_info(self, resident_info: ResidentInfo) -> ResidentInfo:
        """입소자 정보를 생성합니다."""
        model = self._entity_to_model(resident_info)
        self.db.add(model)
        await self.db.commit()
        await self.db.refresh(model)
        return self._model_to_entity(model)
    
    async def get_resident_info_by_user_id(self, user_id: UUID) -> Optional[ResidentInfo]:
        """사용자 ID로 입소자 정보를 조회합니다."""
        stmt = select(ResidentInfoModel).where(ResidentInfoModel.user_id == str(user_id))
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def get_resident_info_by_resident_number(self, resident_number: str) -> Optional[ResidentInfo]:
        """입소자 번호로 입소자 정보를 조회합니다."""
        stmt = select(ResidentInfoModel).where(ResidentInfoModel.resident_number == resident_number)
        result = await self.db.execute(stmt)
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def update_resident_info(self, user_id: UUID, resident_data: Dict[str, Any]) -> Optional[ResidentInfo]:
        """입소자 정보를 업데이트합니다."""
        resident_data["updated_at"] = datetime.utcnow()
        stmt = (
            update(ResidentInfoModel)
            .where(ResidentInfoModel.user_id == str(user_id))
            .values(**resident_data)
            .returning(ResidentInfoModel)
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        model = result.scalar_one_or_none()
        return self._model_to_entity(model) if model else None
    
    async def delete_resident_info(self, user_id: UUID) -> bool:
        """입소자 정보를 삭제합니다."""
        stmt = delete(ResidentInfoModel).where(ResidentInfoModel.user_id == str(user_id))
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
    
    async def get_all_residents(self, skip: int = 0, limit: int = 100) -> List[ResidentInfo]:
        """모든 입소자 정보를 조회합니다."""
        stmt = select(ResidentInfoModel).offset(skip).limit(limit).order_by(ResidentInfoModel.admission_date.desc())
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_current_residents(self, skip: int = 0, limit: int = 100) -> List[ResidentInfo]:
        """현재 입소 중인 입소자 정보를 조회합니다."""
        stmt = (
            select(ResidentInfoModel)
            .where(ResidentInfoModel.discharge_date.is_(None))
            .offset(skip)
            .limit(limit)
            .order_by(ResidentInfoModel.admission_date.desc())
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_residents_by_room(self, room_number: str) -> List[ResidentInfo]:
        """특정 생활실의 입소자 정보를 조회합니다."""
        stmt = (
            select(ResidentInfoModel)
            .where(ResidentInfoModel.room_number == room_number)
            .where(ResidentInfoModel.discharge_date.is_(None))
            .order_by(ResidentInfoModel.bed_number)
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_residents_by_floor(self, floor_number: int) -> List[ResidentInfo]:
        """특정 층의 입소자 정보를 조회합니다."""
        stmt = (
            select(ResidentInfoModel)
            .where(ResidentInfoModel.floor_number == floor_number)
            .where(ResidentInfoModel.discharge_date.is_(None))
            .order_by(ResidentInfoModel.room_number)
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def get_residents_by_adl_level(self, adl_level: str) -> List[ResidentInfo]:
        """특정 ADL 수준의 입소자 정보를 조회합니다."""
        stmt = (
            select(ResidentInfoModel)
            .where(ResidentInfoModel.adl_level == adl_level)
            .where(ResidentInfoModel.discharge_date.is_(None))
            .order_by(ResidentInfoModel.admission_date.desc())
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]
    
    async def count_residents(self) -> int:
        """입소자 정보의 총 개수를 반환합니다."""
        stmt = select(func.count()).select_from(ResidentInfoModel)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def count_current_residents(self) -> int:
        """현재 입소 중인 입소자의 수를 반환합니다."""
        stmt = (
            select(func.count())
            .select_from(ResidentInfoModel)
            .where(ResidentInfoModel.discharge_date.is_(None))
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def search_residents(self, keyword: str) -> List[ResidentInfo]:
        """키워드로 입소자 정보를 검색합니다."""
        stmt = (
            select(ResidentInfoModel)
            .where(
                or_(
                    ResidentInfoModel.resident_number.ilike(f"%{keyword}%"),
                    ResidentInfoModel.nickname.ilike(f"%{keyword}%"),
                    ResidentInfoModel.room_number.ilike(f"%{keyword}%"),
                    ResidentInfoModel.guardian_name.ilike(f"%{keyword}%")
                )
            )
            .order_by(ResidentInfoModel.admission_date.desc())
        )
        result = await self.db.execute(stmt)
        models = result.scalars().all()
        return [self._model_to_entity(model) for model in models]

