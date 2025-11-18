"""
로봇 인식 이벤트 리포지토리 포트 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from app.domain.entities.robot_detection_event import RobotDetectionEvent


class RobotDetectionRepository(ABC):
    """로봇 인식 이벤트 리포지토리 인터페이스"""

    @abstractmethod
    async def save(self, event: RobotDetectionEvent) -> RobotDetectionEvent:
        """이벤트 저장"""
        pass

    @abstractmethod
    async def find_by_id(self, event_id: UUID) -> Optional[RobotDetectionEvent]:
        """ID로 이벤트 조회"""
        pass

    @abstractmethod
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
        pass


class RegistryRepository(ABC):
    """레지스트리 리포지토리 인터페이스 (공통)"""

    @abstractmethod
    async def find_by_key(self, category: str, unique_key: str) -> Optional[Dict[str, Any]]:
        """카테고리와 키로 레지스트리 조회"""
        pass

    @abstractmethod
    async def upsert(self, category: str, unique_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """레지스트리 생성/업데이트"""
        pass


class MarkerRegistryRepository(ABC):
    """ArUco 마커 레지스트리 인터페이스"""

    @abstractmethod
    async def find_by_key(self, marker_key: str) -> Optional[Dict[str, Any]]:
        """마커 키로 조회"""
        pass

    @abstractmethod
    async def upsert(self, marker_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """마커 레지스트리 생성/업데이트"""
        pass


class TextRegistryRepository(ABC):
    """OCR 텍스트 레지스트리 인터페이스"""

    @abstractmethod
    async def find_by_key(self, text_key: str) -> Optional[Dict[str, Any]]:
        """텍스트 키로 조회"""
        pass

    @abstractmethod
    async def upsert(self, text_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """텍스트 레지스트리 생성/업데이트"""
        pass


class FaceRegistryRepository(ABC):
    """얼굴 레지스트리 인터페이스"""

    @abstractmethod
    async def find_by_key(self, face_key: str) -> Optional[Dict[str, Any]]:
        """얼굴 키로 조회"""
        pass

    @abstractmethod
    async def upsert(self, face_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """얼굴 레지스트리 생성/업데이트"""
        pass


class PersonRegistryRepository(ABC):
    """전신/개인 프로필 레지스트리 인터페이스"""

    @abstractmethod
    async def find_by_key(self, person_key: str) -> Optional[Dict[str, Any]]:
        """개인 키로 조회"""
        pass

    @abstractmethod
    async def upsert(self, person_key: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """개인 레지스트리 생성/업데이트"""
        pass

