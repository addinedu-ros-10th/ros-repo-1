"""
User 도메인 서비스

사용자 관련 비즈니스 로직을 처리합니다.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from app.domain.entities.user import User


class UserService:
    """사용자 도메인 서비스"""
    
    def __init__(self, user_repository: "IUserRepository"):
        self.user_repository = user_repository
    
    async def create_user(self, user: User) -> User:
        """새로운 사용자 생성"""
        # 비즈니스 로직 검증
        if not self.validate_user_data(user.user_name, user.email, user.phone_number):
            raise ValueError("사용자 데이터가 유효하지 않습니다")
        
        # 리포지토리를 통한 사용자 생성
        return await self.user_repository.create(user)
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID로 사용자 조회"""
        return await self.user_repository.get_by_id(user_id)
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return await self.user_repository.get_by_email(email)
    
    async def get_all_users(self) -> List[User]:
        """모든 사용자 조회"""
        return await self.user_repository.get_all()
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """역할별 사용자 조회"""
        return await self.user_repository.get_by_role(role)
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> User:
        """사용자 정보 업데이트"""
        # 기존 사용자 조회
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("사용자를 찾을 수 없습니다")
        
        # 업데이트할 필드 검증
        if "user_name" in update_data and not update_data["user_name"].strip():
            raise ValueError("사용자 이름은 비어있을 수 없습니다")
        
        if "email" in update_data and update_data["email"]:
            if not self._is_valid_email(update_data["email"]):
                raise ValueError("유효하지 않은 이메일 형식입니다")
        
        if "phone_number" in update_data and update_data["phone_number"]:
            if not self._is_valid_phone(update_data["phone_number"]):
                raise ValueError("유효하지 않은 전화번호 형식입니다")
        
        # 사용자 정보 업데이트
        for field, value in update_data.items():
            if hasattr(existing_user, field):
                setattr(existing_user, field, value)
        
        # 리포지토리를 통한 업데이트
        return await self.user_repository.update(user_id, update_data)
    
    async def delete_user(self, user_id: str) -> bool:
        """사용자 삭제"""
        # 사용자 존재 여부 확인
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("사용자를 찾을 수 없습니다")
        
        # 리포지토리를 통한 삭제
        await self.user_repository.delete(user_id)
        return True
    
    def update_user_profile(self, user: User, name: str = None, email: str = None, phone: str = None) -> User:
        """사용자 프로필 업데이트 (도메인 로직)"""
        if name:
            user.user_name = name
        if email:
            if not self._is_valid_email(email):
                raise ValueError("유효하지 않은 이메일 형식입니다")
            user.email = email
        if phone:
            if not self._is_valid_phone(phone):
                raise ValueError("유효하지 않은 전화번호 형식입니다")
            user.phone_number = phone
        
        return user
    
    def change_user_role(self, user: User, new_role: str) -> User:
        """사용자 역할 변경"""
        if new_role not in ["admin", "caregiver", "user", "family"]:
            raise ValueError("유효하지 않은 사용자 역할입니다.")
        
        user.user_role = new_role
        return user
    
    def validate_user_permissions(self, user: User, required_role: str) -> bool:
        """사용자 권한 검증"""
        role_hierarchy = {
            "user": 1,
            "family": 2,
            "caregiver": 3,
            "admin": 4
        }
        
        user_level = role_hierarchy.get(user.user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def can_manage_user(self, admin_user: User, target_user: User) -> bool:
        """사용자 관리 권한 확인"""
        if not admin_user.is_admin():
            return False
        
        # 관리자는 다른 관리자를 관리할 수 없음
        if target_user.is_admin() and admin_user.user_id != target_user.user_id:
            return False
        
        return True
    
    def get_active_users(self, users: List[User]) -> List[User]:
        """활성 사용자 목록 조회 (가상의 활성 상태 체크)"""
        # 실제로는 사용자 상태 필드가 필요할 수 있음
        return users
    
    def validate_user_data(self, name: str, email: str = None, phone: str = None) -> bool:
        """사용자 데이터 유효성 검사"""
        if not name or not name.strip():
            return False
        
        if email and not self._is_valid_email(email):
            return False
        
        if phone and not self._is_valid_phone(phone):
            return False
        
        return True
    
    def _is_valid_email(self, email: str) -> bool:
        """이메일 형식 검증"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone(self, phone: str) -> bool:
        """전화번호 형식 검증"""
        import re
        pattern = r'^(\d{2,3})-?(\d{3,4})-?(\d{4})$'
        return bool(re.match(pattern, phone)) 