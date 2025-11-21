"""
디바이스 API 엔드포인트

디바이스 생성, 조회, 수정, 삭제 및 사용자 할당을 위한 REST API를 제공합니다.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import (
    DeviceCreate, DeviceUpdate, DeviceResponse, DeviceListResponse,
    DeviceAssignmentRequest, SuccessResponse
)
from app.core.container import container
from app.infrastructure.database import get_db_session
from app.interfaces.repositories.device_repository import IDeviceRepository
from app.interfaces.repositories.user_repository import IUserRepository
from app.domain.entities.device import Device

router = APIRouter()


def get_device_repository(db_session: AsyncSession = Depends(get_db_session)) -> IDeviceRepository:
    """디바이스 리포지토리 의존성 주입"""
    return container.get_device_repository(db_session)


def get_user_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUserRepository:
    """사용자 리포지토리 의존성 주입"""
    return container.get_user_repository(db_session)


@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    device_data: DeviceCreate,
    device_repository: IDeviceRepository = Depends(get_device_repository),
    user_repository: IUserRepository = Depends(get_user_repository)
):
    """
    새로운 디바이스 생성
    
    - **device_id**: 디바이스 고유 ID (필수)
    - **location_label**: 설치 위치 라벨 (선택)
    - **user_id**: 할당할 사용자 ID (선택)
    """
    try:
        # 사용자 ID가 제공된 경우 사용자 존재 여부 확인
        if device_data.user_id:
            user = await user_repository.get_by_id(str(device_data.user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="할당할 사용자를 찾을 수 없습니다"
                )
        
        # 도메인 엔티티 생성
        device = Device(
            device_id=device_data.device_id,
            user_id=device_data.user_id if device_data.user_id else None,
            location_label=device_data.location_label
        )
        
        # 리포지토리를 통한 디바이스 생성
        created_device = await device_repository.create(device)
        
        return DeviceResponse(
            device_id=created_device.device_id,
            user_id=UUID(created_device.user_id) if created_device.user_id else None,
            location_label=created_device.location_label,
            installed_at=created_device.installed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    특정 디바이스 조회
    
    - **device_id**: 조회할 디바이스의 ID
    """
    try:
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        return DeviceResponse(
            device_id=device.device_id,
            user_id=UUID(device.user_id) if device.user_id else None,
            location_label=device.location_label,
            installed_at=device.installed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/", response_model=DeviceListResponse)
async def get_devices(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 크기"),
    user_id: Optional[UUID] = Query(None, description="사용자별 필터링"),
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    디바이스 목록 조회 (페이지네이션 지원)
    
    - **page**: 페이지 번호 (기본값: 1)
    - **size**: 페이지 크기 (기본값: 10, 최대: 100)
    - **user_id**: 사용자별 필터링 (선택)
    """
    try:
        # 페이지네이션 계산
        offset = (page - 1) * size
        
        if user_id:
            devices = await device_repository.get_by_user_id(str(user_id))
        else:
            devices = await device_repository.get_all()
        
        # 페이지네이션 적용
        total = len(devices)
        paginated_devices = devices[offset:offset + size]
        
        # 응답 데이터 구성
        device_responses = [
            DeviceResponse(
                device_id=device.device_id,
                user_id=UUID(device.user_id) if device.user_id else None,
                location_label=device.location_label,
                installed_at=device.installed_at
            )
            for device in paginated_devices
        ]
        
        return DeviceListResponse(
            devices=device_responses,
            total=total,
            page=page,
            size=size
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 목록 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    device_repository: IDeviceRepository = Depends(get_device_repository),
    user_repository: IUserRepository = Depends(get_user_repository)
):
    """
    디바이스 정보 수정
    
    - **device_id**: 수정할 디바이스의 ID
    - **device_data**: 수정할 디바이스 정보
    """
    try:
        # 기존 디바이스 조회
        existing_device = await device_repository.get_by_id(device_id)
        if not existing_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 사용자 ID가 변경되는 경우 사용자 존재 여부 확인
        if device_data.user_id:
            user = await user_repository.get_by_id(str(device_data.user_id))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="할당할 사용자를 찾을 수 없습니다"
                )
        
        # 업데이트할 필드만 적용
        update_data = device_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="수정할 데이터가 없습니다"
            )
        
        # 디바이스 정보 업데이트
        updated_device = await device_repository.update(device_id, update_data)
        
        return DeviceResponse(
            device_id=updated_device.device_id,
            user_id=UUID(updated_device.user_id) if updated_device.user_id else None,
            location_label=updated_device.location_label,
            installed_at=updated_device.installed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 수정 중 오류가 발생했습니다: {str(e)}"
        )


@router.delete("/{device_id}", response_model=SuccessResponse)
async def delete_device(
    device_id: str,
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    디바이스 삭제
    
    - **device_id**: 삭제할 디바이스의 ID
    """
    try:
        # 디바이스 존재 여부 확인
        existing_device = await device_repository.get_by_id(device_id)
        if not existing_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 디바이스 삭제
        await device_repository.delete(device_id)
        
        return SuccessResponse(
            message="디바이스가 성공적으로 삭제되었습니다",
            data={"device_id": device_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 삭제 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/{device_id}/assign", response_model=SuccessResponse)
async def assign_device_to_user(
    device_id: str,
    assignment_data: DeviceAssignmentRequest,
    device_repository: IDeviceRepository = Depends(get_device_repository),
    user_repository: IUserRepository = Depends(get_user_repository)
):
    """
    디바이스를 사용자에게 할당
    
    - **device_id**: 할당할 디바이스의 ID
    - **user_id**: 할당할 사용자의 UUID
    """
    try:
        # 디바이스 존재 여부 확인
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 사용자 존재 여부 확인
        user = await user_repository.get_by_id(str(assignment_data.user_id))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="할당할 사용자를 찾을 수 없습니다"
            )
        
        # 디바이스 할당
        await device_repository.assign_to_user(device_id, str(assignment_data.user_id))
        
        return SuccessResponse(
            message="디바이스가 성공적으로 사용자에게 할당되었습니다",
            data={
                "device_id": device_id,
                "user_id": str(assignment_data.user_id)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 할당 중 오류가 발생했습니다: {str(e)}"
        )


@router.post("/{device_id}/unassign", response_model=SuccessResponse)
async def unassign_device_from_user(
    device_id: str,
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    디바이스 사용자 할당 해제
    
    - **device_id**: 할당 해제할 디바이스의 ID
    """
    try:
        # 디바이스 존재 여부 확인
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 디바이스 할당 해제
        await device_repository.unassign_from_user(device_id)
        
        return SuccessResponse(
            message="디바이스 할당이 성공적으로 해제되었습니다",
            data={"device_id": device_id}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 할당 해제 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/{device_id}/status")
async def get_device_status(
    device_id: str,
    device_repository: IDeviceRepository = Depends(get_device_repository)
):
    """
    디바이스 상태 조회
    
    - **device_id**: 상태를 조회할 디바이스의 ID
    """
    try:
        # 디바이스 존재 여부 확인
        device = await device_repository.get_by_id(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="디바이스를 찾을 수 없습니다"
            )
        
        # 디바이스 상태 정보 (향후 확장)
        status_info = {
            "device_id": device_id,
            "status": "online",  # 기본값, 향후 실제 상태로 교체
            "last_seen": device.installed_at,
            "assigned_user": device.user_id,
            "location": device.location_label
        }
        
        return SuccessResponse(
            message="디바이스 상태 조회 성공",
            data=status_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"디바이스 상태 조회 중 오류가 발생했습니다: {str(e)}"
        ) 