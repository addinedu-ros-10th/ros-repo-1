"""
User 엔티티 테스트

TDD 방식으로 User 도메인 엔티티를 테스트합니다.
"""

import pytest
from datetime import datetime
from uuid import UUID
from app.domain.entities.user import User


class TestUser:
    """User 엔티티 테스트 클래스"""
    
    def test_create_user_with_valid_data(self):
        """유효한 데이터로 사용자 생성 테스트"""
        # Given
        name = "홍길동"
        role = "user"
        email = "hong@example.com"
        phone = "010-1234-5678"
        
        # When
        user = User(
            user_name=name,
            user_role=role,
            email=email,
            phone_number=phone
        )
        
        # Then
        assert user.user_name == name
        assert user.user_role == role
        assert user.email == email
        assert user.phone_number == phone
        assert isinstance(user.user_id, UUID)
        assert isinstance(user.created_at, datetime)
    
    def test_create_user_with_minimal_data(self):
        """최소 데이터로 사용자 생성 테스트"""
        # Given & When
        user = User(user_name="김철수")
        
        # Then
        assert user.user_name == "김철수"
        assert user.user_role == "user"  # 기본값
        assert user.email is None
        assert user.phone_number is None
    
    def test_create_user_without_name_raises_error(self):
        """이름 없이 사용자 생성 시 에러 발생 테스트"""
        # Given & When & Then
        with pytest.raises(ValueError, match="사용자 이름은 필수입니다"):
            User(user_name="")
    
    def test_create_user_with_invalid_role_raises_error(self):
        """유효하지 않은 역할로 사용자 생성 시 에러 발생 테스트"""
        # Given & When & Then
        with pytest.raises(ValueError, match="유효하지 않은 사용자 역할입니다"):
            User(user_name="테스트", user_role="invalid_role")
    
    def test_user_role_validation(self):
        """사용자 역할 검증 테스트"""
        # Given
        valid_roles = ["admin", "caregiver", "user", "family"]
        
        # When & Then
        for role in valid_roles:
            user = User(user_name="테스트", user_role=role)
            assert user.user_role == role
    
    def test_is_admin_method(self):
        """관리자 여부 확인 메서드 테스트"""
        # Given
        admin_user = User(user_name="관리자", user_role="admin")
        regular_user = User(user_name="일반사용자", user_role="user")
        
        # When & Then
        assert admin_user.is_admin() is True
        assert regular_user.is_admin() is False
    
    def test_is_caregiver_method(self):
        """돌봄 제공자 여부 확인 메서드 테스트"""
        # Given
        caregiver = User(user_name="돌봄제공자", user_role="caregiver")
        regular_user = User(user_name="일반사용자", user_role="user")
        
        # When & Then
        assert caregiver.is_caregiver() is True
        assert regular_user.is_caregiver() is False
    
    def test_is_family_member_method(self):
        """가족 구성원 여부 확인 메서드 테스트"""
        # Given
        family_member = User(user_name="가족", user_role="family")
        regular_user = User(user_name="일반사용자", user_role="user")
        
        # When & Then
        assert family_member.is_family_member() is True
        assert regular_user.is_family_member() is False
    
    def test_update_profile_with_valid_data(self):
        """유효한 데이터로 프로필 업데이트 테스트"""
        # Given
        user = User(user_name="원래이름")
        
        # When
        user.update_profile(name="새이름", email="new@example.com")
        
        # Then
        assert user.user_name == "새이름"
        assert user.email == "new@example.com"
    
    def test_update_profile_with_empty_name_raises_error(self):
        """빈 이름으로 프로필 업데이트 시 에러 발생 테스트"""
        # Given
        user = User(user_name="원래이름")
        
        # When & Then
        with pytest.raises(ValueError, match="사용자 이름은 비어있을 수 없습니다"):
            user.update_profile(name="")
    
    def test_update_profile_with_invalid_email_raises_error(self):
        """유효하지 않은 이메일로 프로필 업데이트 시 에러 발생 테스트"""
        # Given
        user = User(user_name="테스트")
        
        # When & Then
        with pytest.raises(ValueError, match="유효하지 않은 이메일 형식입니다"):
            user.update_profile(email="invalid-email")
    
    def test_update_profile_with_invalid_phone_raises_error(self):
        """유효하지 않은 전화번호로 프로필 업데이트 시 에러 발생 테스트"""
        # Given
        user = User(user_name="테스트")
        
        # When & Then
        with pytest.raises(ValueError, match="유효하지 않은 전화번호 형식입니다"):
            user.update_profile(phone="12345")
    
    def test_email_validation(self):
        """이메일 형식 검증 테스트"""
        # Given
        user = User(user_name="테스트")
        
        # When & Then
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.kr",
            "test+tag@example.org"
        ]
        
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com"
        ]
        
        for email in valid_emails:
            assert user._is_valid_email(email) is True
        
        for email in invalid_emails:
            assert user._is_valid_email(email) is False
    
    def test_phone_validation(self):
        """전화번호 형식 검증 테스트"""
        # Given
        user = User(user_name="테스트")
        
        # When & Then
        valid_phones = [
            "010-1234-5678",
            "02-123-4567",
            "031-123-4567",
            "01012345678"
        ]
        
        invalid_phones = [
            "12345",
            "010-123-456",
            "02-1234-56789"
        ]
        
        for phone in valid_phones:
            assert user._is_valid_phone(phone) is True
        
        for phone in invalid_phones:
            assert user._is_valid_phone(phone) is False
    
    def test_to_dict_method(self):
        """딕셔너리 변환 메서드 테스트"""
        # Given
        user = User(
            user_name="테스트",
            user_role="admin",
            email="test@example.com",
            phone_number="010-1234-5678"
        )
        
        # When
        user_dict = user.to_dict()
        
        # Then
        assert user_dict["user_name"] == "테스트"
        assert user_dict["user_role"] == "admin"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["phone_number"] == "010-1234-5678"
        assert "user_id" in user_dict
        assert "created_at" in user_dict
    
    def test_from_dict_method(self):
        """딕셔너리에서 엔티티 생성 메서드 테스트"""
        # Given
        user_data = {
            "user_name": "테스트",
            "user_role": "user",
            "email": "test@example.com",
            "phone_number": "010-1234-5678"
        }
        
        # When
        user = User.from_dict(user_data)
        
        # Then
        assert user.user_name == "테스트"
        assert user.user_role == "user"
        assert user.email == "test@example.com"
        assert user.phone_number == "010-1234-5678"
        assert isinstance(user.user_id, UUID)
        assert isinstance(user.created_at, datetime) 