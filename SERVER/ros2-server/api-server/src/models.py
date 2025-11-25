"""
Pydantic 모델 정의
"""
from typing import Optional, List, Literal
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class DetectionRequest(BaseModel):
    """어르신 탐지 요청"""
    user_id: Optional[str] = Field(None, description="사용자 ID (UUID)")
    nickname: Optional[str] = Field(None, description="어르신 애칭")
    detection_location: str = Field(..., description="탐지 위치 (예: '1층 복도')")
    detection_confidence: float = Field(..., ge=0.0, le=1.0, description="탐지 신뢰도 (0.0-1.0)")
    camera_id: str = Field(..., description="카메라 ID")
    timestamp: Optional[datetime] = Field(None, description="탐지 시간 (기본값: 현재 시간)")
    display_format: Literal["basic", "detailed", "urgent"] = Field(
        "basic", 
        description="LCD 표시 형식: basic(기본), detailed(상세), urgent(긴급)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "00000000-0000-0000-0000-000000000001",
                "nickname": "Akaza",
                "detection_location": "1층 복도",
                "detection_confidence": 0.95,
                "camera_id": "camera_001",
                "timestamp": "2025-01-22T10:30:00Z",
                "display_format": "basic"
            }
        }


class LCDDisplayData(BaseModel):
    """LCD 표시 데이터"""
    title: str = Field(..., description="타이틀 텍스트")
    lines: List[str] = Field(..., description="본문 라인들")
    show_timestamp: bool = Field(True, description="타임스탬프 표시 여부")


class DetectionResponse(BaseModel):
    """어르신 탐지 응답"""
    success: bool
    message: str
    data: Optional[dict] = None


class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    status: str
    services: dict
    timestamp: datetime


class ScenarioTemplateRequest(BaseModel):
    """시나리오 템플릿 요청"""
    scenario: Literal[
        "morning_greeting",
        "meal_assistance", 
        "conversation",
        "wandering_detection",
        "visitor_guidance"
    ] = Field(..., description="시나리오 타입")
    user_id: Optional[str] = Field(None, description="사용자 ID (UUID)")
    nickname: Optional[str] = Field(None, description="어르신 애칭")
    additional_data: Optional[dict] = Field(None, description="추가 데이터 (시나리오별 다름)")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "scenario": "morning_greeting",
                    "nickname": "Zenitsu Agatsuma",
                    "additional_data": {
                        "weather": "맑은"
                    }
                },
                {
                    "scenario": "meal_assistance",
                    "nickname": "Zenitsu Agatsuma",
                    "additional_data": {
                        "menu": "된장찌개",
                        "meal_time": "12:00"
                    }
                },
                {
                    "scenario": "visitor_guidance",
                    "nickname": "Zenitsu Agatsuma",
                    "additional_data": {
                        "visitor_name": "정기우",
                        "visitor_relationship": "아들",
                        "meeting_room": "면회실"
                    }
                },
                {
                    "scenario": "wandering_detection",
                    "nickname": "Zenitsu Agatsuma",
                    "additional_data": {
                        "location": "1층 복도",
                        "camera_id": "camera_001"
                    }
                },
                {
                    "scenario": "conversation",
                    "user_id": "00000000-0000-0000-0000-000000000001",
                    "additional_data": {
                        "topic": "건강 이야기",
                        "destination": "2층 복도"
                    }
                }
            ]
        }


class TemplateResponse(BaseModel):
    """템플릿 응답"""
    success: bool
    template: LCDDisplayData
    scenario: str
    description: str


class EmotionRequest(BaseModel):
    """감정 표현 요청"""
    emotion: Literal[
        "hello", "basic", "angry", "bored",
        "fun", "happy", "interest", "sad"
    ] = Field(..., description="감정 타입")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {"emotion": "hello"},
                {"emotion": "happy"},
                {"emotion": "sad"},
                {"emotion": "angry"},
                {"emotion": "fun"},
                {"emotion": "bored"},
                {"emotion": "interest"},
                {"emotion": "basic"}
            ]
        }


class EmotionResponse(BaseModel):
    """감정 표현 응답"""
    success: bool
    message: str
    emotion: Optional[str] = None


class ClearDisplayResponse(BaseModel):
    """LCD 화면 지우기 응답"""
    success: bool
    message: str

