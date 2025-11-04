"""
환경변수 및 설정 관리 모듈

.env 파일에서 환경변수를 로드하여 서버 설정을 관리합니다.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """서버 설정 클래스"""
    
    # OpenAI API 설정
    openai_api_key: str = Field(..., description="OpenAI API 키")
    
    # 서버 설정
    server_host: str = Field(default="0.0.0.0", description="서버 호스트")
    server_port: int = Field(default=8000, description="서버 포트")
    debug: bool = Field(default=False, description="디버그 모드")
    reload: bool = Field(default=False, description="자동 리로드 (개발 모드)")
    
    # CORS 설정
    cors_origins: str = Field(default="*", description="CORS 허용 오리진 (쉼표로 구분)")
    
    # ChatGPT 기본 설정
    default_chat_model: str = Field(default="gpt-4o-mini", description="기본 ChatGPT 모델")
    default_system_prompt: str = Field(
        default="당신은 친절한 한국어 AI 어시스턴트입니다.",
        description="기본 시스템 프롬프트"
    )
    
    # TTS 기본 설정
    default_tts_voice: str = Field(default="alloy", description="기본 TTS 음성")
    default_tts_model: str = Field(default="tts-1", description="기본 TTS 모델")
    
    # 데이터베이스 설정 (선택사항, 향후 확장용)
    db_url: Optional[str] = Field(default=None, description="데이터베이스 연결 URL")
    db_host: Optional[str] = Field(default=None, description="데이터베이스 호스트")
    db_port: Optional[int] = Field(default=None, description="데이터베이스 포트")
    db_name: Optional[str] = Field(default=None, description="데이터베이스 이름")
    db_user: Optional[str] = Field(default=None, description="데이터베이스 사용자")
    db_password: Optional[str] = Field(default=None, description="데이터베이스 비밀번호")
    
    # Redis 설정 (선택사항, 세션 관리용)
    redis_url: Optional[str] = Field(default=None, description="Redis 연결 URL")
    redis_host: Optional[str] = Field(default="localhost", description="Redis 호스트")
    redis_port: Optional[int] = Field(default=6379, description="Redis 포트")
    redis_password: Optional[str] = Field(default=None, description="Redis 비밀번호")
    
    class Config:
        env_file = ".env,local"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()


def get_cors_origins() -> list:
    """CORS 오리진 리스트 반환"""
    if settings.cors_origins == "*":
        return ["*"]
    return [origin.strip() for origin in settings.cors_origins.split(",")]


