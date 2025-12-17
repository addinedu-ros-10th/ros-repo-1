"""
사용자 관계 API 라우터

사용자 간의 관계(돌봄, 가족, 관리)를 관리하는 API 엔드포인트를 제공합니다.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import get_user_relationship_service
from app.interfaces.services.user_relationship_service_interface import IUserRelationshipService
from app.api.v1.schemas import (
    UserRelationshipCreate,
    UserRelationshipUpdate,
    UserRelationshipResponse,
    UserRelationshipListResponse
)

router = APIRouter(tags=["사용자 관계"])


@router.post("/create", response_model=UserRelationshipResponse, status_code=201)
async def create_user_relationship(
    relationship_data: UserRelationshipCreate,
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    사용자 관계 생성
    
    - **subject_user_id**: 관계의 주체 (돌봄 제공자, 가족, 관리자)
    - **target_user_id**: 관계의 대상 (돌봄을 받는 사용자)
    - **relationship_type**: 관계 유형 (caregiver, family, admin)
    - **status**: 관계 상태 (pending, active, inactive)
    
    예시:
    ```json
    {
        "subject_user_id": "123e4567-e89b-12d3-a456-426614174000",
        "target_user_id": "123e4567-e89b-12d3-a456-426614174001",
        "relationship_type": "caregiver",
        "status": "active"
    }
    ```
    """
    try:
        return await relationship_service.create_relationship(relationship_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"관계 생성 실패: {str(e)}")


@router.get("/{relationship_id}", response_model=UserRelationshipResponse)
async def get_user_relationship(
    relationship_id: UUID,
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    ID로 사용자 관계 조회
    
    - **relationship_id**: 조회할 관계의 고유 ID
    
    관계가 존재하지 않는 경우 404 오류를 반환합니다.
    """
    relationship = await relationship_service.get_relationship_by_id(relationship_id)
    if not relationship:
        raise HTTPException(status_code=404, detail="관계를 찾을 수 없습니다")
    return relationship


@router.get("/user/{user_id}/as-subject", response_model=List[UserRelationshipResponse])
async def get_user_relationships_as_subject(
    user_id: UUID,
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    사용자가 주체인 관계들 조회
    
    - **user_id**: 관계의 주체가 되는 사용자 ID
    
    해당 사용자가 돌봄 제공자, 가족, 관리자로서 맺은 모든 관계를 반환합니다.
    """
    return await relationship_service.get_relationships_by_user(user_id, as_subject=True)


@router.get("/user/{user_id}/as-target", response_model=List[UserRelationshipResponse])
async def get_user_relationships_as_target(
    user_id: UUID,
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    사용자가 대상인 관계들 조회
    
    - **user_id**: 관계의 대상이 되는 사용자 ID
    
    해당 사용자가 돌봄을 받는 대상으로서 맺어진 모든 관계를 반환합니다.
    """
    return await relationship_service.get_relationships_by_user(user_id, as_subject=False)


@router.get("/type/{relationship_type}", response_model=List[UserRelationshipResponse])
async def get_relationships_by_type(
    relationship_type: str,
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    특정 유형의 관계들 조회
    
    - **relationship_type**: 조회할 관계 유형 (caregiver, family, admin)
    
    해당 유형의 모든 활성 관계를 반환합니다.
    """
    return await relationship_service.get_relationships_by_type(relationship_type)


@router.put("/{relationship_id}/status", response_model=UserRelationshipResponse)
async def update_relationship_status(
    relationship_id: UUID,
    status: str = Query(..., description="새로운 관계 상태 (pending, active, inactive)"),
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    관계 상태 업데이트
    
    - **relationship_id**: 업데이트할 관계의 고유 ID
    - **status**: 새로운 상태 (pending, active, inactive)
    
    관계가 존재하지 않는 경우 404 오류를 반환합니다.
    """
    if status not in ["pending", "active", "inactive"]:
        raise HTTPException(status_code=400, detail="유효하지 않은 상태입니다")
    
    updated_relationship = await relationship_service.update_relationship_status(relationship_id, status)
    if not updated_relationship:
        raise HTTPException(status_code=404, detail="관계를 찾을 수 없습니다")
    return updated_relationship


@router.delete("/{relationship_id}", status_code=204)
async def delete_user_relationship(
    relationship_id: UUID,
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    사용자 관계 삭제
    
    - **relationship_id**: 삭제할 관계의 고유 ID
    
    관계가 존재하지 않는 경우 404 오류를 반환합니다.
    """
    success = await relationship_service.delete_relationship(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail="관계를 찾을 수 없습니다")


@router.get("/", response_model=UserRelationshipListResponse)
async def get_all_user_relationships(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(100, ge=1, le=1000, description="반환할 항목 수"),
    relationship_service: IUserRelationshipService = Depends(get_user_relationship_service)
):
    """
    모든 사용자 관계 조회 (페이지네이션)
    
    - **skip**: 건너뛸 항목 수 (기본값: 0)
    - **limit**: 반환할 항목 수 (기본값: 100, 최대: 1000)
    
    페이지네이션을 지원하여 대량의 데이터를 효율적으로 조회할 수 있습니다.
    """
    relationships = await relationship_service.get_all_relationships(skip, limit)
    total = await relationship_service.count_relationships()
    
    return UserRelationshipListResponse(
        relationships=relationships,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=limit
    )
