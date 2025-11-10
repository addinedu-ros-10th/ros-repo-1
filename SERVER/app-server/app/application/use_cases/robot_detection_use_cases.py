"""
로봇 인식 이벤트 유즈케이스
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.domain.entities.robot_detection_event import (
    RobotDetectionEvent,
    ProcessingInfo,
    APICall,
    Cmd,
)
from app.domain.ports.robot_detection_repository import (
    RobotDetectionRepository,
    MarkerRegistryRepository,
    TextRegistryRepository,
    FaceRegistryRepository,
    PersonRegistryRepository,
)
from app.application.dto.robot_detection_dto import (
    RobotDetectionCreateRequest,
)


class CreateRobotDetectionUseCase:
    """로봇 인식 이벤트 생성 유즈케이스"""

    def __init__(
        self,
        repository: RobotDetectionRepository,
        marker_registry: Optional[MarkerRegistryRepository] = None,
        text_registry: Optional[TextRegistryRepository] = None,
        face_registry: Optional[FaceRegistryRepository] = None,
        person_registry: Optional[PersonRegistryRepository] = None,
    ):
        self.repository = repository
        self.marker_registry = marker_registry
        self.text_registry = text_registry
        self.face_registry = face_registry
        self.person_registry = person_registry

    async def execute(
        self, request: RobotDetectionCreateRequest, robot_id: str
    ) -> RobotDetectionEvent:
        """이벤트 생성 및 레지스트리 업데이트"""
        # ProcessingInfo 변환
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

        # 엔티티 생성
        entity = RobotDetectionEvent(
            robot_id=robot_id,
            category=request.category,
            unique_key=request.unique_key,
            meta=request.meta,
            detected_at=request.detected_at,
            processing_info=processing_info,
        )

        # 유효성 검증
        if not entity.is_valid():
            raise ValueError("Invalid RobotDetectionEvent payload")

        # 레지스트리 업데이트 (옵션)
        await self._update_registry(entity)

        # 이벤트 저장
        return await self.repository.save(entity)

    async def _update_registry(self, entity: RobotDetectionEvent):
        """레지스트리 업데이트 (카테고리별)"""
        if entity.category == "aruco" and self.marker_registry:
            # ArUco 레지스트리 업데이트
            await self.marker_registry.upsert(
                entity.unique_key,
                {
                    "entrance_id": entity.meta.get("entrance_id"),
                    "zone": entity.meta.get("zone"),
                    "pose": entity.meta.get("pose"),
                    "action_plan": entity.processing_info.to_dict(),
                },
            )
        elif entity.category == "text" and self.text_registry:
            # OCR 레지스트리 업데이트
            await self.text_registry.upsert(
                entity.unique_key,
                {
                    "room_code": entity.meta.get("room_code"),
                    "lang": entity.meta.get("lang"),
                    "action_plan": entity.processing_info.to_dict(),
                },
            )
        elif entity.category == "face" and self.face_registry:
            # 얼굴 레지스트리 업데이트
            await self.face_registry.upsert(
                entity.unique_key,
                {
                    "role": entity.meta.get("role"),
                    "consent": entity.meta.get("consent") == "Y",
                    "action_plan": entity.processing_info.to_dict(),
                },
            )
        elif entity.category == "person" and self.person_registry:
            # 전신 레지스트리 업데이트
            await self.person_registry.upsert(
                entity.unique_key,
                {
                    "preferred_follow_distance_m": entity.meta.get("distance_m"),
                    "mobility_level": entity.meta.get("mobility_level"),
                    "action_plan": entity.processing_info.to_dict(),
                },
            )


class GetRobotDetectionUseCase:
    """로봇 인식 이벤트 단건 조회 유즈케이스"""

    def __init__(self, repository: RobotDetectionRepository):
        self.repository = repository

    async def execute(self, event_id: UUID) -> Optional[RobotDetectionEvent]:
        """ID로 이벤트 조회"""
        return await self.repository.find_by_id(event_id)


class ListRobotDetectionsUseCase:
    """로봇 인식 이벤트 목록 조회 유즈케이스"""

    def __init__(self, repository: RobotDetectionRepository):
        self.repository = repository

    async def execute(
        self,
        *,
        category: Optional[str] = None,
        unique_key: Optional[str] = None,
        robot_id: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RobotDetectionEvent]:
        """필터로 이벤트 목록 조회"""
        return await self.repository.find_by_filters(
            category=category,
            unique_key=unique_key,
            robot_id=robot_id,
            since=since,
            until=until,
            skip=skip,
            limit=limit,
        )


class GetRegistryUseCase:
    """레지스트리 조회 유즈케이스"""

    def __init__(
        self,
        marker_registry: Optional[MarkerRegistryRepository] = None,
        text_registry: Optional[TextRegistryRepository] = None,
        face_registry: Optional[FaceRegistryRepository] = None,
        person_registry: Optional[PersonRegistryRepository] = None,
    ):
        self.marker_registry = marker_registry
        self.text_registry = text_registry
        self.face_registry = face_registry
        self.person_registry = person_registry

    async def execute(
        self, category: str, unique_key: str
    ) -> Optional[Dict[str, Any]]:
        """카테고리와 키로 레지스트리 조회"""
        if category == "aruco" and self.marker_registry:
            return await self.marker_registry.find_by_key(unique_key)
        elif category == "text" and self.text_registry:
            return await self.text_registry.find_by_key(unique_key)
        elif category == "face" and self.face_registry:
            return await self.face_registry.find_by_key(unique_key)
        elif category == "person" and self.person_registry:
            return await self.person_registry.find_by_key(unique_key)
        return None

