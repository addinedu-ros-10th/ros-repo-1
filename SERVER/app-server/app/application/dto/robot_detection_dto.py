"""
로봇 인식 이벤트 DTO
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from uuid import UUID
from datetime import datetime

DetectionCategory = Literal["aruco", "text", "face", "person"]
IntentType = Literal["open_door", "start_follow", "stop_follow", "announce", "none"]
ScenarioState = Literal["INIT", "RUN", "END"]


class APICallRequest(BaseModel):
    """API 호출 요청"""
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] = "POST"
    url: str = Field(..., min_length=1)
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None


class CmdRequest(BaseModel):
    """ROS2/메시지 큐 명령 요청"""
    topic: str = Field(..., min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)


class ProcessingInfoRequest(BaseModel):
    """처리 정보 요청"""
    intent: IntentType = "none"
    api_calls: Optional[List[APICallRequest]] = None
    cmds: Optional[List[CmdRequest]] = None
    scenario_state: Optional[ScenarioState] = None


class RobotDetectionCreateRequest(BaseModel):
    """로봇 인식 이벤트 생성 요청"""
    category: DetectionCategory
    unique_key: str = Field(..., min_length=1)
    meta: Dict[str, Any] = Field(..., description="카테고리별 부가정보")
    detected_at: datetime = Field(..., description="인식 시간(로봇 기준 UTC 권장)")
    processing_info: ProcessingInfoRequest


class APICallResponse(BaseModel):
    """API 호출 응답"""
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    body: Optional[Dict[str, Any]] = None


class CmdResponse(BaseModel):
    """ROS2/메시지 큐 명령 응답"""
    topic: str
    payload: Dict[str, Any]


class ProcessingInfoResponse(BaseModel):
    """처리 정보 응답"""
    intent: str
    api_calls: Optional[List[APICallResponse]] = None
    cmds: Optional[List[CmdResponse]] = None
    scenario_state: Optional[str] = None


class RobotDetectionResponse(BaseModel):
    """로봇 인식 이벤트 응답"""
    detection_event_id: UUID
    robot_id: str
    category: str
    unique_key: str
    meta: Dict[str, Any]
    detected_at: datetime
    processing_info: ProcessingInfoResponse
    processed_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class RegistryResponse(BaseModel):
    """레지스트리 응답 (공통)"""
    key: str
    data: Dict[str, Any]
    updated_at: Optional[datetime] = None


class ActionExecuteRequest(BaseModel):
    """액션 실행 요청"""
    event_id: UUID
    processing_info: Optional[ProcessingInfoRequest] = None

