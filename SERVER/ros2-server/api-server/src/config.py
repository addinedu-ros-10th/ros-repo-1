"""
환경 변수 및 설정 관리
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator, Field, model_validator


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버 설정
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    DEBUG: bool = False
    
    # iot-data-server API 설정
    IOT_DATA_SERVER_URL: str = os.getenv(
        "IOT_DATA_SERVER_URL",
        "http://iot-data-server:8000"
    )
    
    # ROS2 설정
    ROS2_NAMESPACE: str = os.getenv("ROS2_NAMESPACE", "/pinky")
    ROS2_SERVICE_TIMEOUT: float = float(os.getenv("ROS2_SERVICE_TIMEOUT", "2.0"))
    ROS2_SERVICE_NAME: str = "lcd_controller/set_display"
    
    # ROS2 감정 표현 설정
    ROS2_EMOTION_SERVICE_NAME: str = os.getenv("ROS2_EMOTION_SERVICE_NAME", "emotion_controller/set_emotion")
    ROS2_EMOTION_SERVICE_TIMEOUT: float = float(os.getenv("ROS2_EMOTION_SERVICE_TIMEOUT", "3.0"))
    
    # ROS2 도메인 ID 설정
    # 사용 가능한 도메인 ID 목록 (쉼표로 구분, 예: "11,12,13")
    ROS2_DOMAIN_ID_ALLOWED: str = os.getenv("ROS2_DOMAIN_ID_ALLOWED", "11,12,13")
    # 실제 사용할 도메인 ID (기본값: 13)
    ROS2_DOMAIN_ID: int = int(os.getenv("ROS2_DOMAIN_ID", "13"))
    
    @field_validator("ROS2_DOMAIN_ID", mode="before")
    @classmethod
    def validate_ros2_domain_id(cls, v):
        """ROS2 도메인 ID 검증 및 변환"""
        if v is None:
            return 13  # 기본값
        
        try:
            domain_id = int(v)
        except (ValueError, TypeError):
            raise ValueError(f"ROS2_DOMAIN_ID는 정수여야 합니다: {v}")
        
        # ROS2 도메인 ID 범위 확인 (0~232)
        if domain_id < 0 or domain_id > 232:
            raise ValueError(f"ROS2_DOMAIN_ID는 0~232 사이의 값이어야 합니다: {domain_id}")
        
        return domain_id
    
    @model_validator(mode="after")
    def validate_ros2_domain_id_allowed(self):
        """ROS2 도메인 ID 허용 목록 검증"""
        # 허용된 도메인 ID 목록 확인 (설정된 경우)
        if self.ROS2_DOMAIN_ID_ALLOWED:
            try:
                allowed_list = [int(x.strip()) for x in self.ROS2_DOMAIN_ID_ALLOWED.split(',') if x.strip()]
                if allowed_list and self.ROS2_DOMAIN_ID not in allowed_list:
                    raise ValueError(
                        f"ROS2_DOMAIN_ID {self.ROS2_DOMAIN_ID}는 허용된 값이 아닙니다. "
                        f"허용된 값: {allowed_list}. "
                        f"다른 값을 사용하려면 ROS2_DOMAIN_ID_ALLOWED 환경 변수를 설정하세요."
                    )
            except (ValueError, AttributeError):
                # 허용된 목록 파싱 실패는 무시 (환경 변수 형식 오류일 수 있음)
                pass
        
        return self
    
    # Redis 설정 (선택적)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
    
    # CORS 설정 (문자열로 받아서 리스트로 변환)
    CORS_ORIGINS_STR: str = Field(default="*", alias="CORS_ORIGINS")
    
    @field_validator("CORS_ORIGINS_STR", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """CORS_ORIGINS를 문자열로 받음"""
        if v is None:
            return "*"
        return str(v)
    
    @property
    def CORS_ORIGINS(self) -> list[str]:
        """CORS 허용 오리진 리스트"""
        if self.CORS_ORIGINS_STR == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS_STR.split(",") if origin.strip()]
    
    # 로깅
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env.local"
        case_sensitive = True
        populate_by_name = True  # alias와 필드명 모두 허용
        extra = "ignore"  # 추가 필드 무시 (CADDY_HTTP_PORT, CADDY_HTTPS_PORT 등)
        validate_assignment = True  # 할당 시 검증


# 전역 설정 인스턴스
settings = Settings()

