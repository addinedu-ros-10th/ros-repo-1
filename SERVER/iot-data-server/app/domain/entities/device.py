"""
Device 도메인 엔티티

IoT 디바이스 정보를 관리합니다.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from dataclasses import dataclass, field


@dataclass
class Device:
    """IoT 디바이스 엔티티"""
    
    device_id: str = field(default="")
    user_id: Optional[UUID] = field(default=None)
    location_label: Optional[str] = field(default=None)
    installed_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """유효성 검사"""
        if not self.device_id:
            raise ValueError("디바이스 ID는 필수입니다.")
    
    def assign_to_user(self, user_id: UUID) -> None:
        """사용자에게 디바이스 할당"""
        self.user_id = user_id
    
    def unassign_from_user(self) -> None:
        """사용자로부터 디바이스 할당 해제"""
        self.user_id = None
    
    def update_location(self, location: str) -> None:
        """설치 위치 업데이트"""
        if location and not location.strip():
            raise ValueError("위치 라벨은 비어있을 수 없습니다.")
        self.location_label = location.strip() if location else None
    
    def is_assigned(self) -> bool:
        """사용자에게 할당되었는지 확인"""
        return self.user_id is not None
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "device_id": self.device_id,
            "user_id": str(self.user_id) if self.user_id else None,
            "location_label": self.location_label,
            "installed_at": self.installed_at.isoformat() if self.installed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Device':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            device_id=data["device_id"],
            user_id=UUID(data["user_id"]) if data.get("user_id") else None,
            location_label=data.get("location_label"),
            installed_at=datetime.fromisoformat(data["installed_at"]) if data.get("installed_at") else datetime.utcnow()
        ) 