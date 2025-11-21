from datetime import datetime
from typing import Optional
from uuid import UUID


class UserRelationship:
    """사용자 간의 관계(돌봄, 가족, 관리)를 정의하는 엔티티"""
    
    def __init__(
        self,
        relationship_id: UUID,
        subject_user_id: UUID,
        target_user_id: UUID,
        relationship_type: str,
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.relationship_id = relationship_id
        self.subject_user_id = subject_user_id
        self.target_user_id = target_user_id
        self.relationship_type = relationship_type
        self.status = status
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    def update_status(self, new_status: str) -> None:
        """관계 상태를 업데이트합니다."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def is_active(self) -> bool:
        """관계가 활성 상태인지 확인합니다."""
        return self.status == "active"
    
    def is_pending(self) -> bool:
        """관계가 대기 상태인지 확인합니다."""
        return self.status == "pending"

