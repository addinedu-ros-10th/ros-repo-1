"""
로봇 인식 이벤트 RESTful API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_app_session
from app.adapters.repositories.robot_detection_repository_impl import (
    RobotDetectionRepositoryImpl,
    MarkerRegistryRepositoryImpl,
    TextRegistryRepositoryImpl,
    FaceRegistryRepositoryImpl,
    PersonRegistryRepositoryImpl,
)
from app.application.use_cases.robot_detection_use_cases import (
    CreateRobotDetectionUseCase,
    GetRobotDetectionUseCase,
    ListRobotDetectionsUseCase,
    GetRegistryUseCase,
)
from app.application.dto.robot_detection_dto import (
    RobotDetectionCreateRequest,
    RobotDetectionResponse,
    RegistryResponse,
    ActionExecuteRequest,
    ProcessingInfoRequest,
)
from app.services.robot_detection_action_executor import action_executor
from app.domain.entities.robot_detection_event import ProcessingInfo, APICall, Cmd

router = APIRouter(prefix="/api/v1/detections", tags=["robot-detections"])


def get_repository(session: AsyncSession = Depends(get_app_session)) -> RobotDetectionRepositoryImpl:
    """로봇 인식 이벤트 리포지토리 의존성 주입"""
    return RobotDetectionRepositoryImpl(session)


def get_marker_registry(session: AsyncSession = Depends(get_app_session)) -> MarkerRegistryRepositoryImpl:
    """마커 레지스트리 의존성 주입"""
    return MarkerRegistryRepositoryImpl(session)


def get_text_registry(session: AsyncSession = Depends(get_app_session)) -> TextRegistryRepositoryImpl:
    """텍스트 레지스트리 의존성 주입"""
    return TextRegistryRepositoryImpl(session)


def get_face_registry(session: AsyncSession = Depends(get_app_session)) -> FaceRegistryRepositoryImpl:
    """얼굴 레지스트리 의존성 주입"""
    return FaceRegistryRepositoryImpl(session)


def get_person_registry(session: AsyncSession = Depends(get_app_session)) -> PersonRegistryRepositoryImpl:
    """개인 레지스트리 의존성 주입"""
    return PersonRegistryRepositoryImpl(session)


def _entity_to_response(entity) -> RobotDetectionResponse:
    """엔티티를 응답 DTO로 변환"""
    from app.application.dto.robot_detection_dto import (
        ProcessingInfoResponse,
        APICallResponse,
        CmdResponse,
    )
    
    api_calls = None
    if entity.processing_info.api_calls:
        api_calls = [
            APICallResponse(
                method=call.method,
                url=call.url,
                headers=call.headers,
                body=call.body,
            )
            for call in entity.processing_info.api_calls
        ]
    
    cmds = None
    if entity.processing_info.cmds:
        cmds = [
            CmdResponse(topic=cmd.topic, payload=cmd.payload)
            for cmd in entity.processing_info.cmds
        ]
    
    processing_info = ProcessingInfoResponse(
        intent=entity.processing_info.intent,
        api_calls=api_calls,
        cmds=cmds,
        scenario_state=entity.processing_info.scenario_state,
    )
    
    return RobotDetectionResponse(
        detection_event_id=entity.detection_event_id,
        robot_id=entity.robot_id,
        category=entity.category,
        unique_key=entity.unique_key,
        meta=entity.meta,
        detected_at=entity.detected_at,
        processing_info=processing_info,
        processed_status=entity.processed_status,
        created_at=entity.created_at,
    )


@router.post("/", response_model=RobotDetectionResponse, status_code=status.HTTP_201_CREATED)
async def create_detection(
    request: RobotDetectionCreateRequest,
    x_robot_id: str = Header(..., alias="X-Robot-ID"),
    repository: RobotDetectionRepositoryImpl = Depends(get_repository),
    marker_registry: MarkerRegistryRepositoryImpl = Depends(get_marker_registry),
    text_registry: TextRegistryRepositoryImpl = Depends(get_text_registry),
    face_registry: FaceRegistryRepositoryImpl = Depends(get_face_registry),
    person_registry: PersonRegistryRepositoryImpl = Depends(get_person_registry),
):
    """로봇 인식 이벤트 수집 API"""
    try:
        use_case = CreateRobotDetectionUseCase(
            repository=repository,
            marker_registry=marker_registry,
            text_registry=text_registry,
            face_registry=face_registry,
            person_registry=person_registry,
        )
        entity = await use_case.execute(request, robot_id=x_robot_id)

        # 액션 실행 (비동기 큐에 발행)
        await action_executor.execute_actions(
            event_id=entity.detection_event_id,
            processing_info=entity.processing_info,
            robot_id=entity.robot_id,
            category=entity.category,
            unique_key=entity.unique_key,
        )

        return _entity_to_response(entity)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create detection: {str(e)}",
        )


@router.get("/", response_model=List[RobotDetectionResponse])
async def list_detections(
    category: Optional[str] = Query(None, description="인식 카테고리"),
    unique_key: Optional[str] = Query(None, description="고유 키"),
    robot_id: Optional[str] = Query(None, description="로봇 ID"),
    since: Optional[datetime] = Query(None, description="시작 시간"),
    until: Optional[datetime] = Query(None, description="종료 시간"),
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    repository: RobotDetectionRepositoryImpl = Depends(get_repository),
):
    """로봇 인식 이벤트 목록 조회"""
    try:
        use_case = ListRobotDetectionsUseCase(repository)
        entities = await use_case.execute(
            category=category,
            unique_key=unique_key,
            robot_id=robot_id,
            since=since,
            until=until,
            skip=skip,
            limit=limit,
        )
        return [_entity_to_response(e) for e in entities]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list detections: {str(e)}",
        )


@router.get("/{event_id}", response_model=RobotDetectionResponse)
async def get_detection(
    event_id: UUID,
    repository: RobotDetectionRepositoryImpl = Depends(get_repository),
):
    """로봇 인식 이벤트 단건 조회"""
    use_case = GetRobotDetectionUseCase(repository)
    entity = await use_case.execute(event_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Detection event not found"
        )
    return _entity_to_response(entity)


@router.get("/registry/{category}/{unique_key}", response_model=RegistryResponse)
async def get_registry(
    category: str,
    unique_key: str,
    marker_registry: MarkerRegistryRepositoryImpl = Depends(get_marker_registry),
    text_registry: TextRegistryRepositoryImpl = Depends(get_text_registry),
    face_registry: FaceRegistryRepositoryImpl = Depends(get_face_registry),
    person_registry: PersonRegistryRepositoryImpl = Depends(get_person_registry),
):
    """레지스트리 조회"""
    use_case = GetRegistryUseCase(
        marker_registry=marker_registry,
        text_registry=text_registry,
        face_registry=face_registry,
        person_registry=person_registry,
    )
    data = await use_case.execute(category, unique_key)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registry not found: {category}/{unique_key}",
        )
    return RegistryResponse(key=unique_key, data=data)


@router.post("/actions/execute", status_code=status.HTTP_200_OK)
async def execute_action(
    request: ActionExecuteRequest,
    repository: RobotDetectionRepositoryImpl = Depends(get_repository),
):
    """액션 수동 실행 (재시도/수동 트리거)"""
    # 이벤트 조회
    use_case = GetRobotDetectionUseCase(repository)
    entity = await use_case.execute(request.event_id)
    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Detection event not found"
        )

    # 처리 정보 사용 (요청에 있으면 사용, 없으면 엔티티의 것 사용)
    processing_info = entity.processing_info
    if request.processing_info:
        # 요청의 처리 정보로 변환
        api_calls = None
        if request.processing_info.api_calls:
            api_calls = [
                APICall(
                    method=call.method,
                    url=call.url,
                    headers=call.headers,
                    body=call.body,
                )
                for call in request.processing_info.api_calls
            ]

        cmds = None
        if request.processing_info.cmds:
            cmds = [
                Cmd(topic=cmd.topic, payload=cmd.payload)
                for cmd in request.processing_info.cmds
            ]

        processing_info = ProcessingInfo(
            intent=request.processing_info.intent,
            api_calls=api_calls,
            cmds=cmds,
            scenario_state=request.processing_info.scenario_state,
        )

    # 액션 실행
    result = await action_executor.execute_actions(
        event_id=entity.detection_event_id,
        processing_info=processing_info,
        robot_id=entity.robot_id,
        category=entity.category,
        unique_key=entity.unique_key,
    )

    return result

