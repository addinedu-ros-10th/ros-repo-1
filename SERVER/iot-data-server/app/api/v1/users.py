"""
사용자 API 엔드포인트

사용자 생성, 조회, 수정, 삭제를 위한 REST API를 제공합니다.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    SuccessResponse, ErrorResponse, PaginationParams
)
from app.core.container import container
from app.infrastructure.database import get_db_session
from app.interfaces.repositories.user_repository import IUserRepository
from app.interfaces.services.user_service_interface import IUserService
from app.domain.entities.user import User

router = APIRouter(tags=["users"])


def get_user_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUserRepository:
    """사용자 리포지토리 의존성 주입"""
    return container.get_user_repository(db_session)


def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> IUserService:
    """사용자 서비스 의존성 주입"""
    return container.get_user_service(db_session)


@router.post("/create", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    user_service: IUserService = Depends(get_user_service)
):
    """
    새로운 사용자 생성
    
    - **user_name**: 사용자 이름 (필수)
    - **email**: 이메일 주소 (선택)
    - **phone_number**: 전화번호 (선택)
    - **user_role**: 사용자 역할 (admin, caregiver, family, user)
    """
    try:
        # 서비스를 통한 사용자 생성
        created_user = await user_service.create_user(
            name=user_data.user_name,
            role=user_data.user_role,
            email=user_data.email,
            phone=user_data.phone_number
        )
        
        return UserResponse(
            user_id=created_user.user_id,
            user_name=created_user.user_name,
            email=created_user.email,
            phone_number=created_user.phone_number,
            user_role=created_user.user_role,
            created_at=created_user.created_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/list", response_model=UserListResponse)
async def get_users(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    role: Optional[str] = Query(None, description="역할별 필터링"),
    user_repository: IUserRepository = Depends(get_user_repository)
):
    """
    사용자 목록 조회 (페이지네이션 지원)
    
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 10, 최대: 100)
    - **role**: 역할별 필터링 (선택)
    """
    try:
        # 페이지네이션 계산
        offset = (page - 1) * size
        
        if role:
            users = await user_repository.get_by_role(role)
        else:
            users = await user_repository.get_all()
        
        # 페이지네이션 적용
        total = len(users)
        paginated_users = users[offset:offset + size]
        
        # 응답 데이터 구성
        user_responses = []
        for user in paginated_users:
            try:
                user_response = UserResponse(
                    user_id=user.user_id,
                    user_name=user.user_name,
                    email=user.email,
                    phone_number=user.phone_number,
                    user_role=user.user_role,
                    created_at=user.created_at
                )
                user_responses.append(user_response)
            except Exception as e:
                print(f"사용자 응답 생성 오류: {e}, 사용자: {user.user_id}")
                # 기본값으로 응답 생성
                user_response = UserResponse(
                    user_id=user.user_id,
                    user_name=user.user_name or "",
                    email=user.email,
                    phone_number=user.phone_number,
                    user_role=user.user_role or "user",
                    created_at=None
                )
                user_responses.append(user_response)
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    user_repository: IUserRepository = Depends(get_user_repository)
):
    """
    특정 사용자 조회
    
    - **user_id**: 조회할 사용자의 UUID
    """
    try:
        user = await user_repository.get_by_id(str(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        return UserResponse(
            user_id=user.user_id,
            user_name=user.user_name,
            email=user.email,
            phone_number=user.phone_number,
            user_role=user.user_role,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    user_service: IUserService = Depends(get_user_service)
):
    """
    사용자 정보 수정
    
    - **user_id**: 수정할 사용자의 UUID
    - **user_data**: 수정할 사용자 정보
    """
    try:
        # 기존 사용자 조회
        existing_user = await user_service.get_user_by_id(str(user_id))
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # 업데이트할 필드만 적용
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="수정할 데이터가 없습니다"
            )
        
        # 사용자 정보 업데이트
        updated_user = await user_service.update_user(str(user_id), update_data)
        
        return UserResponse(
            user_id=updated_user.user_id,
            user_name=updated_user.user_name,
            email=updated_user.email,
            phone_number=updated_user.phone_number,
            user_role=updated_user.user_role,
            created_at=updated_user.created_at
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: UUID,
    user_service: IUserService = Depends(get_user_service)
):
    """
    사용자 삭제
    
    - **user_id**: 삭제할 사용자의 UUID
    """
    try:
        # 사용자 존재 여부 확인
        existing_user = await user_service.get_user_by_id(str(user_id))
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # 사용자 삭제
        await user_service.delete_user(str(user_id))
        
        return SuccessResponse(
            message="사용자가 성공적으로 삭제되었습니다",
            data={"user_id": str(user_id)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{user_id}/devices")
async def get_user_devices(
    user_id: UUID,
    user_service: IUserService = Depends(get_user_service)
):
    """
    사용자에게 할당된 디바이스 목록 조회
    
    - **user_id**: 디바이스를 조회할 사용자의 UUID
    """
    try:
        # 사용자 존재 여부 확인
        user = await user_service.get_user_by_id(str(user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자를 찾을 수 없습니다"
            )
        
        # 사용자의 디바이스 목록 조회 (향후 구현)
        # devices = await user_service.get_user_devices(str(user_id))
        
        return SuccessResponse(
            message="사용자 디바이스 조회 성공",
            data={
                "user_id": str(user_id),
                "devices": []  # 향후 실제 디바이스 목록으로 교체
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 디바이스 조회 중 오류가 발생했습니다: {str(e)}"
        ) 