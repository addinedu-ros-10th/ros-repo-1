"""
User 서비스 구현체

Clean Architecture 원칙에 따라 사용자 관련 비즈니스 로직을 담당합니다.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import HTTPException

from app.interfaces.services.user_service_interface import IUserService
from app.interfaces.repositories.user_repository import IUserRepository
from app.domain.entities.user import User


class UserService(IUserService):
    """사용자 서비스 구현체"""
    
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
    
    async def create_user(self, name: str, role: str = "user", email: str = None, phone: str = None) -> User:
        """새로운 사용자 생성"""
        # 비즈니스 로직 검증
        if not self.validate_user_data(name, email, phone):
            raise ValueError("사용자 데이터가 유효하지 않습니다")
        
        # 이메일 중복 검증
        if email:
            existing_user = await self.user_repository.get_by_email(email)
            if existing_user:
                raise ValueError(f"이메일 '{email}'이 이미 사용 중입니다")
        
        # User 엔티티 생성
        user = User(
            user_name=name,
            user_role=role,
            email=email,
            phone_number=phone
        )
        
        # 리포지토리를 통한 사용자 생성
        return await self.user_repository.create(user)
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        return await self.user_repository.get_by_id(str(user_id))
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        return await self.user_repository.get_by_email(email)
    
    async def get_all_users(self) -> List[User]:
        """모든 사용자 조회"""
        return await self.user_repository.get_all()
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """역할별 사용자 조회"""
        return await self.user_repository.get_by_role(role)
    
    async def update_user_profile(self, user_id: UUID, name: str = None, email: str = None, phone: str = None) -> User:
        """사용자 프로필 업데이트"""
        # 기존 사용자 조회
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("사용자를 찾을 수 없습니다")
        
        # 업데이트할 필드 검증
        if name and not name.strip():
            raise ValueError("사용자 이름은 비어있을 수 없습니다")
        
        if email and not self._is_valid_email(email):
            raise ValueError("유효하지 않은 이메일 형식입니다")
        
        if phone and not self._is_valid_phone(phone):
            raise ValueError("유효하지 않은 전화번호 형식입니다")
        
        # 사용자 정보 업데이트
        if name:
            existing_user.user_name = name
        if email:
            existing_user.email = email
        if phone:
            existing_user.phone_number = phone
        
        # 리포지토리를 통한 업데이트
        update_data = {}
        if name:
            update_data["user_name"] = name
        if email:
            update_data["email"] = email
        if phone:
            update_data["phone_number"] = phone
        
        return await self.user_repository.update(str(user_id), update_data)
    
    async def change_user_role(self, user_id: UUID, new_role: str) -> User:
        """사용자 역할 변경"""
        if new_role not in ["admin", "caregiver", "user", "family"]:
            raise ValueError("유효하지 않은 사용자 역할입니다.")
        
        # 기존 사용자 조회
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("사용자를 찾을 수 없습니다")
        
        # 역할 변경
        existing_user.user_role = new_role
        
        # 리포지토리를 통한 업데이트
        return await self.user_repository.update(str(user_id), {"user_role": new_role})
    
    async def delete_user(self, user_id: UUID) -> bool:
        """사용자 삭제"""
        # 사용자 존재 여부 확인
        existing_user = await self.get_user_by_id(user_id)
        if not existing_user:
            raise ValueError("사용자를 찾을 수 없습니다")
        
        # 리포지토리를 통한 삭제
        await self.user_repository.delete(str(user_id))
        return True
    
    async def validate_user_permissions(self, user: User, required_role: str) -> bool:
        """사용자 권한을 검증합니다."""
        role_hierarchy = {
            "admin": 4,
            "caregiver": 3,
            "family": 2,
            "user": 1
        }
        
        user_level = role_hierarchy.get(user.user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    async def can_manage_user(self, admin_user: User, target_user: User) -> bool:
        """사용자 관리 권한을 확인합니다."""
        # admin은 모든 사용자를 관리할 수 있음
        if admin_user.user_role == "admin":
            return True
        
        # caregiver는 user와 family만 관리할 수 있음
        if admin_user.user_role == "caregiver":
            return target_user.user_role in ["user", "family"]
        
        # family는 user만 관리할 수 있음
        if admin_user.user_role == "family":
            return target_user.user_role == "user"
        
        # user는 다른 사용자를 관리할 수 없음
        return False
    
    def validate_user_data(self, user_name: str, email: Optional[str] = None, phone: Optional[str] = None) -> bool:
        """사용자 데이터 유효성 검증"""
        if not user_name or not user_name.strip():
            return False
        
        if email and not self._is_valid_email(email):
            return False
        
        if phone and not self._is_valid_phone(phone):
            return False
        
        return True
    
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