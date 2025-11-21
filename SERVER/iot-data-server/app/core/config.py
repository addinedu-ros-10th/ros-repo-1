"""
Core 설정 모듈

애플리케이션의 핵심 설정을 관리합니다.
환경 변수, 데이터베이스 연결, Redis 설정 등을 포함합니다.
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv


class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 기본 설정
    ENVIRONMENT: str = Field(default="local", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    
    # 데이터베이스 설정
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASSWORD: str = Field(..., env="DB_PASSWORD")
    DB_HOST: str = Field(..., env="DB_HOST")
    DB_PORT: int = Field(..., env="DB_PORT")
    DB_NAME: str = Field(..., env="DB_NAME")
    
    @property
    def DATABASE_URL(self) -> str:
        """데이터베이스 URL을 동적으로 생성합니다."""
        from urllib.parse import quote_plus
        
        # 비밀번호에 포함된 특수문자를 URL 인코딩
        encoded_password = quote_plus(self.DB_PASSWORD)
        return f"postgresql://{self.DB_USER}:{encoded_password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis 설정
    REDIS_URL: str = Field(..., env="REDIS_URL")
    REDIS_HOST: str = Field(..., env="REDIS_HOST")
    REDIS_PORT: int = Field(..., env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    
    # Caddy 설정
    CADDY_DOMAIN: str = Field(..., env="CADDY_DOMAIN")
    CADDY_EMAIL: str = Field(..., env="CADDY_EMAIL")
    
    # 보안 설정
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # API 설정
    API_V1_STR: str = Field(default="/api/v1", env="API_V1_STR")
    PROJECT_NAME: str = Field(default="IoT Care Backend", env="PROJECT_NAME")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    
    # CORS 설정
    ALLOWED_HOSTS: list = Field(default=["*"], env="ALLOWED_HOSTS")
    
    # 로깅 설정
    LOG_FILE_PATH: str = Field(default="./logs/app.log", env="LOG_FILE_PATH")
    LOG_MAX_SIZE: str = Field(default="100MB", env="LOG_MAX_SIZE")
    LOG_BACKUP_COUNT: int = Field(default=5, env="LOG_BACKUP_COUNT")
    
    class Config:
        env_file = ".env.local"
        case_sensitive = True


def get_settings() -> Settings:
    """설정 인스턴스를 반환합니다."""
    # .env 파일 로드
    load_dotenv()
    return Settings()


def get_database_url() -> str:
    """데이터베이스 URL을 반환합니다."""
    settings = get_settings()
    return settings.DATABASE_URL


def get_redis_url() -> str:
    """Redis URL을 반환합니다."""
    settings = get_settings()
    return settings.REDIS_URL


# 전역 설정 인스턴스
settings = get_settings()

