"""
User 도메인 엔티티

독거노인 통합 돌봄 서비스의 사용자 정보를 관리합니다.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from dataclasses import dataclass, field


@dataclass
class User:
    """사용자 엔티티"""
    
    user_name: str
    user_role: str = field(default="user")
    user_id: UUID = field(default_factory=uuid4)
    email: Optional[str] = field(default=None)
    phone_number: Optional[str] = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """유효성 검사"""
        if not self.user_name:
            raise ValueError("사용자 이름은 필수입니다.")
        
        if self.user_role not in ["admin", "caregiver", "care_target", "family"]:
            raise ValueError(f"유효하지 않은 사용자 역할입니다. {self.user_role}")
    
    def is_admin(self) -> bool:
        """관리자 여부 확인"""
        return self.user_role == "admin"
    
    def is_caregiver(self) -> bool:
        """돌봄 제공자 여부 확인"""
        return self.user_role == "caregiver"
    
    def is_family_member(self) -> bool:
        """가족 구성원 여부 확인"""
        return self.user_role == "family"
    
    def update_profile(self, name: str = None, email: str = None, phone: str = None) -> None:
        """프로필 정보 업데이트"""
        if name is not None:
            if not name.strip():
                raise ValueError("사용자 이름은 비어있을 수 없습니다.")
            self.user_name = name.strip()
        
        if email is not None:
            if email and not self._is_valid_email(email):
                raise ValueError("유효하지 않은 이메일 형식입니다.")
            self.email = email
        
        if phone is not None:
            if phone and not self._is_valid_phone(phone):
                raise ValueError("유효하지 않은 전화번호 형식입니다.")
            self.phone_number = phone
    
    def _is_valid_email(self, email: str) -> bool:
        """이메일 형식 검증"""
        import re
        # 더 엄격한 이메일 검증: 연속된 점, 시작/끝 점 제한
        # 연속된 점(..)이 있으면 안됨
        if '..' in email:
            return False
        pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """전화번호 형식 검증"""
        import re
        # 한국 전화번호 형식 (010-1234-5678, 02-123-4567 등)
        pattern = r'^(\d{2,3})-?(\d{3,4})-?(\d{4})$'
        return bool(re.match(pattern, phone))
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "user_id": str(self.user_id),
            "user_role": self.user_role,
            "user_name": self.user_name,
            "email": self.email,
            "phone_number": self.phone_number,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """딕셔너리에서 엔티티 생성"""
        return cls(
            user_id=UUID(data["user_id"]) if data.get("user_id") else uuid4(),
            user_role=data.get("user_role", "user"),
            user_name=data["user_name"],
            email=data.get("email"),
            phone_number=data.get("phone_number"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow()
        ) 