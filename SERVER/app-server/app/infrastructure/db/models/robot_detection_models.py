"""
로봇 인식 이벤트 모델
APP 스키마 (기본 public)
"""

from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY, ENUM
from sqlalchemy import Text, TIMESTAMP, Boolean, Numeric, text, Index
from uuid import UUID as UUIDType, uuid4
from datetime import datetime
from typing import Optional, Dict, Any, List

from .scheduled_job import Base


class RobotDetectionEventModel(Base):
    """로봇 인식 이벤트 모델 - APP 스키마"""
    __tablename__ = "detection_event"
    __table_args__ = (
        Index('idx_detection_event_time', 'detected_at', postgresql_ops={'detected_at': 'DESC'}),
        Index('idx_detection_event_cat_key', 'category', 'unique_key'),
        Index('idx_detection_event_robot', 'robot_id'),
        Index('idx_detection_event_status', 'processed_status'),
        {'comment': '로봇 인식 이벤트 로그 (공통)'}
    )

    detection_event_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text('gen_random_uuid()'),
        comment="이벤트 고유 ID"
    )
    robot_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="로봇 ID"
    )
    category: Mapped[str] = mapped_column(
        Text,  # ENUM은 마이그레이션에서만 사용, 모델에서는 Text
        nullable=False,
        comment="인식 카테고리 (aruco|text|face|person)"
    )
    unique_key: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="고유 키 (마커/텍스트/얼굴해시/추적ID 등)"
    )
    meta: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="카테고리별 부가정보"
    )
    detected_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        comment="인식 시간(로봇 기준 UTC 권장)"
    )
    processing_info: Mapped[Dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        comment="처리 정보 (intent/api_calls/cmds/scenario_state)"
    )
    processed_status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default=text("'accepted'"),
        comment="처리 상태 (accepted|done|failed)"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment="생성 시간"
    )

    def __repr__(self) -> str:
        return f"<RobotDetectionEventModel(id={self.detection_event_id}, robot={self.robot_id}, category={self.category})>"


class MarkerRegistryModel(Base):
    """ArUco 마커 레지스트리 모델"""
    __tablename__ = "marker_registry"
    __table_args__ = (
        {'comment': 'ArUco 마커 레지스트리'}
    )

    marker_key: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        nullable=False,
        comment="마커 키 (예: ARUCO_23)"
    )
    entrance_id: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="출입구/구역 식별"
    )
    zone: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="구역"
    )
    pose: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="고정 좌표/자세"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="설명"
    )
    action_plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="기본 처리 계획"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment="수정 시간"
    )

    def __repr__(self) -> str:
        return f"<MarkerRegistryModel(key='{self.marker_key}', entrance='{self.entrance_id}')>"


class TextRegistryModel(Base):
    """OCR 텍스트 레지스트리 모델"""
    __tablename__ = "text_registry"
    __table_args__ = (
        {'comment': 'OCR 텍스트 레지스트리'}
    )

    text_key: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        nullable=False,
        comment="텍스트 키 (예: 식당, 응접실)"
    )
    room_code: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="방 코드"
    )
    lang: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="언어"
    )
    synonyms: Mapped[Optional[List[str]]] = mapped_column(
        ARRAY(Text),
        nullable=True,
        comment="유사 표현"
    )
    action_plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="기본 처리 계획"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment="수정 시간"
    )

    def __repr__(self) -> str:
        return f"<TextRegistryModel(key='{self.text_key}', room='{self.room_code}')>"


class FaceRegistryModel(Base):
    """얼굴 레지스트리 모델 (PII 보호)"""
    __tablename__ = "face_registry"
    __table_args__ = (
        {'comment': '얼굴 레지스트리 (PII 보호)'}
    )

    face_key: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        nullable=False,
        comment="얼굴 식별키 해시"
    )
    role: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="역할 (elder|caregiver|visitor)"
    )
    consent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text('false'),
        comment="동의 여부"
    )
    pii_ref: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="외부 금고/암호화 저장소 key(선택)"
    )
    policy: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="보관기간/마스킹 등"
    )
    action_plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="기본 처리 계획"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment="수정 시간"
    )

    def __repr__(self) -> str:
        return f"<FaceRegistryModel(key='{self.face_key}', role='{self.role}')>"


class PersonRegistryModel(Base):
    """전신/개인 프로필 레지스트리 모델"""
    __tablename__ = "person_registry"
    __table_args__ = (
        {'comment': '전신/개인 프로필 레지스트리'}
    )

    person_key: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        nullable=False,
        comment="개인 논리 키"
    )
    preferred_follow_distance_m: Mapped[Optional[float]] = mapped_column(
        Numeric(4, 2),
        nullable=True,
        server_default=text('1.5'),
        comment="선호 추종 거리(m)"
    )
    mobility_level: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="보행속도/주의필요 등"
    )
    action_plan: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONB,
        nullable=True,
        comment="기본 처리 계획"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=text('now()'),
        nullable=False,
        comment="수정 시간"
    )

    def __repr__(self) -> str:
        return f"<PersonRegistryModel(key='{self.person_key}', distance={self.preferred_follow_distance_m})>"

