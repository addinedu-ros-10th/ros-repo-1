"""
로봇 인식 이벤트 도메인 엔티티
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from uuid import UUID, uuid4

DetectionCategory = Literal["aruco", "text", "face", "person"]
IntentType = Literal["open_door", "start_follow", "stop_follow", "announce", "none"]
ProcessedStatus = Literal["accepted", "done", "failed"]
ScenarioState = Literal["INIT", "RUN", "END"]


@dataclass
class APICall:
    """API 호출 정보"""
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "POST"
    url: str = ""
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None


@dataclass
class Cmd:
    """ROS2/메시지 큐 명령"""
    topic: str = ""
    payload: Dict[str, Any] = None

    def __post_init__(self):
        if self.payload is None:
            self.payload = {}


@dataclass
class ProcessingInfo:
    """처리 정보"""
    intent: IntentType = "none"
    api_calls: Optional[List[APICall]] = None
    cmds: Optional[List[Cmd]] = None
    scenario_state: Optional[ScenarioState] = None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = {"intent": self.intent}
        if self.api_calls:
            result["api_calls"] = [
                {
                    "method": call.method,
                    "url": call.url,
                    "headers": call.headers,
                    "body": call.body,
                }
                for call in self.api_calls
            ]
        if self.cmds:
            result["cmds"] = [
                {
                    "topic": cmd.topic,
                    "payload": cmd.payload,
                }
                for cmd in self.cmds
            ]
        if self.scenario_state:
            result["scenario_state"] = self.scenario_state
        return result


@dataclass
class RobotDetectionEvent:
    """로봇 인식 이벤트 엔티티"""
    robot_id: str
    category: DetectionCategory
    unique_key: str
    meta: Dict[str, Any]
    detected_at: datetime
    processing_info: ProcessingInfo
    detection_event_id: Optional[UUID] = None
    processed_status: ProcessedStatus = "accepted"
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.detection_event_id is None:
            self.detection_event_id = uuid4()
        if self.created_at is None:
            self.created_at = datetime.utcnow()

    def is_valid(self) -> bool:
        """엔티티 유효성 검증"""
        # 기본 필수 필드 검증
        if not self.robot_id or not isinstance(self.robot_id, str):
            return False
        if not self.category or self.category not in ["aruco", "text", "face", "person"]:
            return False
        if not self.unique_key or not isinstance(self.unique_key, str):
            return False
        if not isinstance(self.meta, dict):
            return False
        if not isinstance(self.detected_at, datetime):
            return False
        if not isinstance(self.processing_info, ProcessingInfo):
            return False

        # 카테고리별 메타 검증
        if not self._validate_meta():
            return False

        return True

    def _validate_meta(self) -> bool:
        """카테고리별 메타 데이터 검증"""
        if self.category == "aruco":
            # ArUco: marker_id, entrance_id, bbox, confidence 등
            return True  # 기본 검증만 수행
        elif self.category == "text":
            # OCR: lang, bbox, room_code, confidence 등
            return True
        elif self.category == "face":
            # 얼굴: role, consent, last_verified_at 등
            return True
        elif self.category == "person":
            # 전신: distance_m, pose, velocity, lost 등
            return True
        return True

