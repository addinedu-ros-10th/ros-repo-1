"""
메모리 기반 User 리포지토리

테스트와 개발 단계에서 사용하는 인메모리 리포지토리입니다.
실제 데이터베이스 대신 메모리에 데이터를 저장합니다.
"""

from typing import List, Optional, Dict
from uuid import UUID
from app.domain.entities.user import User
from app.interfaces.repositories.user_repository import IUserRepository


class MemoryUserRepository(IUserRepository):
    """메모리 기반 사용자 리포지토리"""
    
    def __init__(self):
        self._users: Dict[UUID, User] = {}
        self._email_index: Dict[str, UUID] = {}
    
    async def create(self, user: User) -> User:
        """새로운 사용자를 생성합니다."""
        if user.user_id in self._users:
            raise ValueError(f"사용자가 이미 존재합니다: {user.user_id}")
        
        if user.email and user.email in self._email_index:
            raise ValueError(f"이메일이 이미 사용 중입니다: {user.email}")
        
        self._users[user.user_id] = user
        if user.email:
            self._email_index[user.email] = user.user_id
        
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자를 조회합니다."""
        return self._users.get(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자를 조회합니다."""
        user_id = self._email_index.get(email)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def get_all(self) -> List[User]:
        """모든 사용자를 조회합니다."""
        return list(self._users.values())
    
    async def get_by_role(self, role: str) -> List[User]:
        """역할별 사용자를 조회합니다."""
        return [user for user in self._users.values() if user.user_role == role]
    
    async def update(self, user: User) -> User:
        """사용자 정보를 업데이트합니다."""
        if user.user_id not in self._users:
            raise ValueError(f"사용자가 존재하지 않습니다: {user.user_id}")
        
        old_user = self._users[user.user_id]
        
        # 이메일이 변경된 경우 인덱스 업데이트
        if old_user.email != user.email:
            if old_user.email:
                del self._email_index[old_user.email]
            if user.email:
                if user.email in self._email_index:
                    raise ValueError(f"이메일이 이미 사용 중입니다: {user.email}")
                self._email_index[user.email] = user.user_id
        
        self._users[user.user_id] = user
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """사용자를 삭제합니다."""
        if user_id not in self._users:
            return False
        
        user = self._users[user_id]
        if user.email:
            del self._email_index[user.email]
        
        del self._users[user_id]
        return True
    
    async def exists(self, user_id: UUID) -> bool:
        """사용자 존재 여부를 확인합니다."""
        return user_id in self._users
    
    def clear(self) -> None:
        """모든 데이터를 제거합니다 (테스트용)."""
        self._users.clear()
        self._email_index.clear() 