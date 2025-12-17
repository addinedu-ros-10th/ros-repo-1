"""
로봇 인식 이벤트 리포지토리 구현
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

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
from app.infrastructure.db.models.robot_detection_models import (
    RobotDetectionEventModel,
    MarkerRegistryModel,
    TextRegistryModel,
    FaceRegistryModel,
    PersonRegistryModel,
)


class RobotDetectionRepositoryImpl(RobotDetectionRepository):
    """로봇 인식 이벤트 리포지토리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, event: RobotDetectionEvent) -> RobotDetectionEvent:
        """이벤트 저장"""
        model = RobotDetectionEventModel(
            detection_event_id=event.detection_event_id,
            robot_id=event.robot_id,
            category=event.category,
            unique_key=event.unique_key,
            meta=event.meta,
            detected_at=event.detected_at,
            processing_info=event.processing_info.to_dict(),
            processed_status=event.processed_status,
        )
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        event.created_at = model.created_at
        return event

    async def find_by_id(self, event_id: UUID) -> Optional[RobotDetectionEvent]:
        """ID로 이벤트 조회"""
        result = await self.session.execute(
            select(RobotDetectionEventModel).where(
                RobotDetectionEventModel.detection_event_id == event_id
            )
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return self._to_entity(model)

    async def find_by_filters(
        self,
        category: Optional[str] = None,
        unique_key: Optional[str] = None,
        robot_id: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[RobotDetectionEvent]:
        """필터로 이벤트 목록 조회"""
        stmt = (
            select(RobotDetectionEventModel)
            .order_by(RobotDetectionEventModel.detected_at.desc())
            .offset(skip)
            .limit(limit)
        )

        conditions = []
        if category is not None:
            conditions.append(RobotDetectionEventModel.category == category)
        if unique_key is not None:
            conditions.append(RobotDetectionEventModel.unique_key == unique_key)
        if robot_id is not None:
            conditions.append(RobotDetectionEventModel.robot_id == robot_id)
        if since is not None:
            conditions.append(RobotDetectionEventModel.detected_at >= since)
        if until is not None:
            conditions.append(RobotDetectionEventModel.detected_at <= until)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: RobotDetectionEventModel) -> RobotDetectionEvent:
        """모델을 엔티티로 변환"""
        # ProcessingInfo 복원
        processing_dict = model.processing_info
        api_calls = None
        if "api_calls" in processing_dict and processing_dict["api_calls"]:
            api_calls = [
                APICall(
                    method=call.get("method", "POST"),
                    url=call.get("url", ""),
                    headers=call.get("headers"),
                    body=call.get("body"),
                )
                for call in processing_dict["api_calls"]
            ]

        cmds = None
        if "cmds" in processing_dict and processing_dict["cmds"]:
            cmds = [
                Cmd(topic=cmd.get("topic", ""), payload=cmd.get("payload", {}))
                for cmd in processing_dict["cmds"]
            ]

        processing_info = ProcessingInfo(
            intent=processing_dict.get("intent", "none"),
            api_calls=api_calls,
            cmds=cmds,
            scenario_state=processing_dict.get("scenario_state"),
        )

        return RobotDetectionEvent(
            detection_event_id=model.detection_event_id,
            robot_id=model.robot_id,
            category=model.category,  # type: ignore
            unique_key=model.unique_key,
            meta=model.meta,
            detected_at=model.detected_at,
            processing_info=processing_info,
            processed_status=model.processed_status,  # type: ignore
            created_at=model.created_at,
        )


class MarkerRegistryRepositoryImpl(MarkerRegistryRepository):
    """ArUco 마커 레지스트리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_key(self, marker_key: str) -> Optional[Dict[str, Any]]:
        """마커 키로 조회"""
        result = await self.session.execute(
            select(MarkerRegistryModel).where(MarkerRegistryModel.marker_key == marker_key)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return {
            "marker_key": model.marker_key,
            "entrance_id": model.entrance_id,
            "zone": model.zone,
            "pose": model.pose,
            "description": model.description,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }

    async def upsert(self, marker_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """마커 레지스트리 생성/업데이트"""
        result = await self.session.execute(
            select(MarkerRegistryModel).where(MarkerRegistryModel.marker_key == marker_key)
        )
        model = result.scalar_one_or_none()

        if model:
            # 업데이트
            for key, value in data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
        else:
            # 생성
            model = MarkerRegistryModel(
                marker_key=marker_key,
                entrance_id=data.get("entrance_id"),
                zone=data.get("zone"),
                pose=data.get("pose"),
                description=data.get("description"),
                action_plan=data.get("action_plan"),
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return {
            "marker_key": model.marker_key,
            "entrance_id": model.entrance_id,
            "zone": model.zone,
            "pose": model.pose,
            "description": model.description,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }


class TextRegistryRepositoryImpl(TextRegistryRepository):
    """OCR 텍스트 레지스트리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_key(self, text_key: str) -> Optional[Dict[str, Any]]:
        """텍스트 키로 조회"""
        result = await self.session.execute(
            select(TextRegistryModel).where(TextRegistryModel.text_key == text_key)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return {
            "text_key": model.text_key,
            "room_code": model.room_code,
            "lang": model.lang,
            "synonyms": model.synonyms,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }

    async def upsert(self, text_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """텍스트 레지스트리 생성/업데이트"""
        result = await self.session.execute(
            select(TextRegistryModel).where(TextRegistryModel.text_key == text_key)
        )
        model = result.scalar_one_or_none()

        if model:
            # 업데이트
            for key, value in data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
        else:
            # 생성
            model = TextRegistryModel(
                text_key=text_key,
                room_code=data.get("room_code"),
                lang=data.get("lang"),
                synonyms=data.get("synonyms"),
                action_plan=data.get("action_plan"),
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return {
            "text_key": model.text_key,
            "room_code": model.room_code,
            "lang": model.lang,
            "synonyms": model.synonyms,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }


class FaceRegistryRepositoryImpl(FaceRegistryRepository):
    """얼굴 레지스트리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_key(self, face_key: str) -> Optional[Dict[str, Any]]:
        """얼굴 키로 조회"""
        result = await self.session.execute(
            select(FaceRegistryModel).where(FaceRegistryModel.face_key == face_key)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return {
            "face_key": model.face_key,
            "role": model.role,
            "consent": model.consent,
            "pii_ref": model.pii_ref,
            "policy": model.policy,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }

    async def upsert(self, face_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """얼굴 레지스트리 생성/업데이트"""
        result = await self.session.execute(
            select(FaceRegistryModel).where(FaceRegistryModel.face_key == face_key)
        )
        model = result.scalar_one_or_none()

        if model:
            # 업데이트
            for key, value in data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
        else:
            # 생성
            model = FaceRegistryModel(
                face_key=face_key,
                role=data.get("role"),
                consent=data.get("consent", False),
                pii_ref=data.get("pii_ref"),
                policy=data.get("policy"),
                action_plan=data.get("action_plan"),
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return {
            "face_key": model.face_key,
            "role": model.role,
            "consent": model.consent,
            "pii_ref": model.pii_ref,
            "policy": model.policy,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }


class PersonRegistryRepositoryImpl(PersonRegistryRepository):
    """전신/개인 프로필 레지스트리 구현"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_key(self, person_key: str) -> Optional[Dict[str, Any]]:
        """개인 키로 조회"""
        result = await self.session.execute(
            select(PersonRegistryModel).where(PersonRegistryModel.person_key == person_key)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return {
            "person_key": model.person_key,
            "preferred_follow_distance_m": float(model.preferred_follow_distance_m)
            if model.preferred_follow_distance_m
            else None,
            "mobility_level": model.mobility_level,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }

    async def upsert(self, person_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """개인 레지스트리 생성/업데이트"""
        result = await self.session.execute(
            select(PersonRegistryModel).where(PersonRegistryModel.person_key == person_key)
        )
        model = result.scalar_one_or_none()

        if model:
            # 업데이트
            for key, value in data.items():
                if hasattr(model, key):
                    setattr(model, key, value)
        else:
            # 생성
            model = PersonRegistryModel(
                person_key=person_key,
                preferred_follow_distance_m=data.get("preferred_follow_distance_m"),
                mobility_level=data.get("mobility_level"),
                action_plan=data.get("action_plan"),
            )
            self.session.add(model)

        await self.session.commit()
        await self.session.refresh(model)

        return {
            "person_key": model.person_key,
            "preferred_follow_distance_m": float(model.preferred_follow_distance_m)
            if model.preferred_follow_distance_m
            else None,
            "mobility_level": model.mobility_level,
            "action_plan": model.action_plan,
            "updated_at": model.updated_at.isoformat() if model.updated_at else None,
        }

