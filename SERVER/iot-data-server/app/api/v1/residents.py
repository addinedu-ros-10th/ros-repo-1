"""
요양원 내부 입소자 관리 정보 API 라우터

요양원 내부 입소자 관리 정보를 관리하는 API 엔드포인트를 제공합니다.
"""

from typing import List, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import get_resident_info_service
from app.interfaces.services.resident_info_service_interface import IResidentInfoService
from app.domain.entities.resident_info import ResidentInfo
from app.api.v1.schemas import (
    ResidentInfoCreate,
    ResidentInfoUpdate,
    ResidentInfoResponse,
    ResidentInfoListResponse,
    IncidentCreate,
    MedicationScheduleUpdate,
    SuccessResponse,
    ErrorResponse
)

router = APIRouter(tags=["요양원 내부 입소자 관리"])


def _entity_to_response(entity: ResidentInfo) -> ResidentInfoResponse:
    """도메인 엔티티를 응답 스키마로 변환"""
    return ResidentInfoResponse(
        user_id=entity.user_id,
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
        guardian_phone=entity.guardian_phone,
        created_at=entity.created_at,
        updated_at=entity.updated_at
    )


@router.post("/create/{user_id}", response_model=ResidentInfoResponse, status_code=status.HTTP_201_CREATED)
async def create_resident_info(
    user_id: UUID,
    resident_data: ResidentInfoCreate,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    입소자 정보 생성
    
    - **user_id**: 사용자 ID (users 테이블의 user_id)
    - **admission_date**: 입소일 (필수)
    - **resident_number**: 요양원 내부 관리 번호 (선택)
    - **nickname**: 애칭 (선택)
    - 기타 입소자 관리 정보들
    """
    try:
        # 스키마를 딕셔너리로 변환
        resident_dict = resident_data.dict(exclude_none=True)
        
        # 서비스를 통한 입소자 정보 생성
        created_resident = await resident_service.create_resident_info(user_id, resident_dict)
        
        return _entity_to_response(created_resident)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"입소자 정보 생성 중 오류가 발생했습니다: {str(e)}")


@router.get("/{user_id}", response_model=ResidentInfoResponse)
async def get_resident_info(
    user_id: UUID,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    입소자 정보 조회
    
    - **user_id**: 사용자 ID
    """
    resident = await resident_service.get_resident_info(user_id)
    
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="입소자 정보를 찾을 수 없습니다.")
    
    return _entity_to_response(resident)


@router.get("/number/{resident_number}", response_model=ResidentInfoResponse)
async def get_resident_info_by_number(
    resident_number: str,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    입소자 번호로 입소자 정보 조회
    
    - **resident_number**: 요양원 내부 관리 번호
    """
    resident = await resident_service.get_resident_info_by_number(resident_number)
    
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="입소자 정보를 찾을 수 없습니다.")
    
    return _entity_to_response(resident)


@router.put("/{user_id}", response_model=ResidentInfoResponse)
async def update_resident_info(
    user_id: UUID,
    resident_data: ResidentInfoUpdate,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    입소자 정보 수정
    
    - **user_id**: 사용자 ID
    - 수정할 필드들만 포함하여 전송
    """
    try:
        # 스키마를 딕셔너리로 변환 (None 값 제외)
        update_dict = resident_data.dict(exclude_none=True)
        
        if not update_dict:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="수정할 정보가 없습니다.")
        
        updated_resident = await resident_service.update_resident_info(user_id, update_dict)
        
        if not updated_resident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="입소자 정보를 찾을 수 없습니다.")
        
        return _entity_to_response(updated_resident)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"입소자 정보 수정 중 오류가 발생했습니다: {str(e)}")


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_resident_info(
    user_id: UUID,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    입소자 정보 삭제
    
    - **user_id**: 사용자 ID
    """
    deleted = await resident_service.delete_resident_info(user_id)
    
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="입소자 정보를 찾을 수 없습니다.")
    
    return SuccessResponse(message="입소자 정보가 삭제되었습니다.")


@router.get("/", response_model=ResidentInfoListResponse)
async def get_all_residents(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    모든 입소자 정보 조회 (페이지네이션)
    
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 10, 최대: 100)
    """
    result = await resident_service.get_all_residents(page=page, size=size)
    
    residents_response = [_entity_to_response(r) for r in result["residents"]]
    
    return ResidentInfoListResponse(
        residents=residents_response,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/current/list", response_model=ResidentInfoListResponse)
async def get_current_residents(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    현재 입소 중인 입소자 정보 조회 (페이지네이션)
    
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 10, 최대: 100)
    """
    result = await resident_service.get_current_residents(page=page, size=size)
    
    residents_response = [_entity_to_response(r) for r in result["residents"]]
    
    return ResidentInfoListResponse(
        residents=residents_response,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/room/{room_number}", response_model=List[ResidentInfoResponse])
async def get_residents_by_room(
    room_number: str,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    특정 생활실의 입소자 정보 조회
    
    - **room_number**: 생활실 번호
    """
    residents = await resident_service.get_residents_by_room(room_number)
    
    return [_entity_to_response(r) for r in residents]


@router.get("/floor/{floor_number}", response_model=List[ResidentInfoResponse])
async def get_residents_by_floor(
    floor_number: int,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    특정 층의 입소자 정보 조회
    
    - **floor_number**: 층수
    """
    residents = await resident_service.get_residents_by_floor(floor_number)
    
    return [_entity_to_response(r) for r in residents]


@router.get("/adl/{adl_level}", response_model=List[ResidentInfoResponse])
async def get_residents_by_adl_level(
    adl_level: str,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    특정 ADL 수준의 입소자 정보 조회
    
    - **adl_level**: ADL 수준 (independent, partial_assistance, full_assistance)
    """
    residents = await resident_service.get_residents_by_adl_level(adl_level)
    
    return [_entity_to_response(r) for r in residents]


@router.get("/search/{keyword}", response_model=List[ResidentInfoResponse])
async def search_residents(
    keyword: str,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    키워드로 입소자 정보 검색
    
    - **keyword**: 검색 키워드 (입소자 번호, 애칭, 생활실 번호, 보호자 이름 등)
    """
    residents = await resident_service.search_residents(keyword)
    
    return [_entity_to_response(r) for r in residents]


@router.post("/{user_id}/discharge", response_model=ResidentInfoResponse)
async def discharge_resident(
    user_id: UUID,
    discharge_date: date = Query(..., description="퇴소일"),
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    입소자 퇴소 처리
    
    - **user_id**: 사용자 ID
    - **discharge_date**: 퇴소일
    """
    try:
        discharged_resident = await resident_service.discharge_resident(user_id, discharge_date)
        
        if not discharged_resident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="입소자 정보를 찾을 수 없습니다.")
        
        return _entity_to_response(discharged_resident)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"퇴소 처리 중 오류가 발생했습니다: {str(e)}")


@router.post("/{user_id}/incidents", response_model=ResidentInfoResponse)
async def add_incident(
    user_id: UUID,
    incident: IncidentCreate,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    사건/사고 기록 추가
    
    - **user_id**: 사용자 ID
    - **incident**: 사건/사고 정보
    """
    try:
        incident_dict = incident.dict()
        updated_resident = await resident_service.add_incident(user_id, incident_dict)
        
        if not updated_resident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="입소자 정보를 찾을 수 없습니다.")
        
        return _entity_to_response(updated_resident)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"사건/사고 기록 추가 중 오류가 발생했습니다: {str(e)}")


@router.put("/{user_id}/medication-schedule", response_model=ResidentInfoResponse)
async def update_medication_schedule(
    user_id: UUID,
    schedule_data: MedicationScheduleUpdate,
    resident_service: IResidentInfoService = Depends(get_resident_info_service)
):
    """
    복약 일정 업데이트
    
    - **user_id**: 사용자 ID
    - **schedule**: 복약 일정 리스트
    """
    try:
        updated_resident = await resident_service.update_medication_schedule(user_id, schedule_data.schedule)
        
        if not updated_resident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="입소자 정보를 찾을 수 없습니다.")
        
        return _entity_to_response(updated_resident)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"복약 일정 업데이트 중 오류가 발생했습니다: {str(e)}")

