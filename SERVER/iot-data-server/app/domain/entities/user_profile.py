from datetime import date, datetime
from typing import Optional
from uuid import UUID


class UserProfile:
    """사용자의 상세 프로필 및 돌봄 서비스 관련 정보를 정의하는 엔티티"""
    
    def __init__(
        self,
        user_id: UUID,
        date_of_birth: date,
        gender: str,
        address: Optional[str] = None,
        address_detail: Optional[str] = None,
        medical_history: Optional[str] = None,
        significant_notes: Optional[str] = None,
        current_status: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.user_id = user_id
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.address = address
        self.address_detail = address_detail
        self.medical_history = medical_history
        self.significant_notes = significant_notes
        self.current_status = current_status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_profile(
        self,
        address: Optional[str] = None,
        address_detail: Optional[str] = None,
        medical_history: Optional[str] = None,
        significant_notes: Optional[str] = None,
        current_status: Optional[str] = None
    ) -> None:
        """프로필 정보를 업데이트합니다."""
        if address is not None:
            self.address = address
        if address_detail is not None:
            self.address_detail = address_detail
        if medical_history is not None:
            self.medical_history = medical_history
        if significant_notes is not None:
            self.significant_notes = significant_notes
        if current_status is not None:
            self.current_status = current_status
        
        self.updated_at = datetime.utcnow()
    
    def get_age(self) -> int:
        """현재 나이를 계산합니다."""
        today = date.today()
        age = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
            today.month == self.date_of_birth.month and today.day < self.date_of_birth.day
        ):
            age -= 1
        return age

