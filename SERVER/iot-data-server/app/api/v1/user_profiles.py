"""
사용자 프로필 API 라우터

사용자의 상세 프로필 및 돌봄 서비스 관련 정보를 관리하는 API 엔드포인트를 제공합니다.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import get_user_profile_service
from app.interfaces.services.user_profile_service_interface import IUserProfileService
from app.api.v1.schemas import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    UserProfileListResponse
)

router = APIRouter(tags=["사용자 프로필"])


@router.post("/create/{user_id}", response_model=UserProfileResponse, status_code=201)
async def create_user_profile(
    user_id: UUID,
    profile_data: UserProfileCreate,
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    사용자 프로필 생성
    
    - **user_id**: 프로필을 생성할 사용자의 ID
    - **date_of_birth**: 사용자의 생년월일 (YYYY-MM-DD 형식)
    - **gender**: 성별 (male, female, other)
    - **address**: 주소 (선택)
    - **address_detail**: 상세 주소 (선택)
    - **medical_history**: 병력 (선택)
    - **significant_notes**: 특이사항 (선택)
    - **current_status**: 현재 상태 (선택)
    
    예시:
    ```json
    {
        "date_of_birth": "1980-01-01",
        "gender": "male",
        "address": "서울시 강남구",
        "address_detail": "123-45",
        "medical_history": "고혈압, 당뇨",
        "significant_notes": "특정 약물 알러지 있음",
        "current_status": "거동 불편, 보조기구 사용"
    }
    ```
    """
    try:
        return await profile_service.create_profile(profile_data, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프로필 생성 실패: {str(e)}")


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID,
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    사용자 ID로 프로필 조회
    
    - **user_id**: 조회할 사용자의 ID
    
    프로필이 존재하지 않는 경우 404 오류를 반환합니다.
    """
    profile = await profile_service.get_profile_by_user_id(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
    return profile


@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(
    user_id: UUID,
    profile_data: UserProfileUpdate,
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    사용자 프로필 업데이트
    
    - **user_id**: 업데이트할 사용자의 ID
    - **profile_data**: 업데이트할 프로필 데이터 (일부 필드만 업데이트 가능)
    
    프로필이 존재하지 않는 경우 404 오류를 반환합니다.
    """
    updated_profile = await profile_service.update_profile(user_id, profile_data)
    if not updated_profile:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")
    return updated_profile


@router.delete("/{user_id}", status_code=204)
async def delete_user_profile(
    user_id: UUID,
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    사용자 프로필 삭제
    
    - **user_id**: 삭제할 사용자의 ID
    
    프로필이 존재하지 않는 경우 404 오류를 반환합니다.
    """
    success = await profile_service.delete_profile(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다")


@router.get("/gender/{gender}", response_model=List[UserProfileResponse])
async def get_profiles_by_gender(
    gender: str,
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    특정 성별의 프로필들 조회
    
    - **gender**: 조회할 성별 (male, female, other)
    
    해당 성별의 모든 프로필을 반환합니다.
    """
    if gender not in ["male", "female", "other"]:
        raise HTTPException(status_code=400, detail="유효하지 않은 성별입니다")
    
    return await profile_service.get_profiles_by_gender(gender)


@router.get("/age-range/{min_age}/{max_age}", response_model=List[UserProfileResponse])
async def get_profiles_by_age_range(
    min_age: int = Path(..., ge=0, le=150, description="최소 나이"),
    max_age: int = Path(..., ge=0, le=150, description="최대 나이"),
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    특정 연령대의 프로필들 조회
    
    - **min_age**: 최소 나이 (0-150)
    - **max_age**: 최대 나이 (0-150)
    
    해당 연령대의 모든 프로필을 반환합니다.
    """
    if min_age > max_age:
        raise HTTPException(status_code=400, detail="최소 나이는 최대 나이보다 클 수 없습니다")
    
    return await profile_service.get_profiles_by_age_range(min_age, max_age)


@router.get("/search/medical-history", response_model=List[UserProfileResponse])
async def search_profiles_by_medical_history(
    keyword: str = Query(..., min_length=1, description="검색할 병력 키워드"),
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    병력에 특정 키워드가 포함된 프로필들 검색
    
    - **keyword**: 검색할 병력 키워드 (최소 1자)
    
    병력에 해당 키워드가 포함된 모든 프로필을 반환합니다.
    """
    return await profile_service.search_profiles_by_medical_history(keyword)


@router.get("/", response_model=UserProfileListResponse)
async def get_all_user_profiles(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=1000, description="반환할 항목 수"),
    profile_service: IUserProfileService = Depends(get_user_profile_service)
):
    """
    모든 사용자 프로필 조회 (페이지네이션)
    
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 반환할 항목 수 (기본값: 100, 최대: 1000)
    
    페이지네이션을 지원하여 대량의 데이터를 효율적으로 조회할 수 있습니다.
    """
    profiles = await profile_service.get_all_profiles(skip, limit)
    total = await profile_service.count_profiles()
    
    return UserProfileListResponse(
        profiles=profiles,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit
    )
