"""
의존성 주입 컨테이너 테스트

TDD 방식으로 의존성 주입 시스템을 테스트합니다.
"""

import pytest
from app.core.container import DependencyContainer, get_container
from app.interfaces.repositories.user_repository import IUserRepository
from app.interfaces.repositories.device_repository import IDeviceRepository
from app.interfaces.services.user_service_interface import IUserService
from app.infrastructure.repositories.memory_user_repository import MemoryUserRepository
from app.infrastructure.repositories.memory_device_repository import MemoryDeviceRepository


class TestDependencyContainer:
    """의존성 주입 컨테이너 테스트 클래스"""
    
    def test_create_container(self):
        """컨테이너 생성 테스트"""
        # Given & When
        container = DependencyContainer()
        
        # Then
        assert container is not None
        assert hasattr(container, '_services')
        assert hasattr(container, '_repositories')
    
    def test_register_and_get_service(self):
        """서비스 등록 및 조회 테스트"""
        # Given
        container = DependencyContainer()
        mock_service = object()
        
        # When
        container.register_service(IUserService, mock_service)
        retrieved_service = container.get_service(IUserService)
        
        # Then
        assert retrieved_service == mock_service
        assert container.has_service(IUserService) is True
    
    def test_register_and_get_repository(self):
        """리포지토리 등록 및 조회 테스트"""
        # Given
        container = DependencyContainer()
        mock_repository = object()
        
        # When
        container.register_repository(IUserRepository, mock_repository)
        retrieved_repository = container.get_repository(IUserRepository)
        
        # Then
        assert retrieved_repository == mock_repository
        assert container.has_repository(IUserRepository) is True
    
    def test_get_unregistered_service_raises_error(self):
        """등록되지 않은 서비스 조회 시 에러 발생 테스트"""
        # Given
        container = DependencyContainer()
        
        # When & Then
        with pytest.raises(KeyError, match="서비스가 등록되지 않았습니다"):
            container.get_service(IUserService)
    
    def test_get_unregistered_repository_raises_error(self):
        """등록되지 않은 리포지토리 조회 시 에러 발생 테스트"""
        # Given
        container = DependencyContainer()
        
        # When & Then
        with pytest.raises(KeyError, match="리포지토리가 등록되지 않았습니다"):
            container.get_repository(IUserRepository)
    
    def test_clear_container(self):
        """컨테이너 초기화 테스트"""
        # Given
        container = DependencyContainer()
        container.register_service(IUserService, object())
        container.register_repository(IUserRepository, object())
        
        # When
        container.clear()
        
        # Then
        assert container.has_service(IUserService) is False
        assert container.has_repository(IUserRepository) is False
    
    def test_global_container_singleton(self):
        """전역 컨테이너 싱글톤 패턴 테스트"""
        # Given & When
        container1 = get_container()
        container2 = get_container()
        
        # Then
        assert container1 is container2
    
    def test_register_multiple_services(self):
        """여러 서비스 등록 테스트"""
        # Given
        container = DependencyContainer()
        service1 = object()
        service2 = object()
        
        # When
        container.register_service(IUserService, service1)
        container.register_service(IDeviceRepository, service2)
        
        # Then
        assert container.get_service(IUserService) == service1
        assert container.get_service(IDeviceRepository) == service2
        assert container.has_service(IUserService) is True
        assert container.has_service(IDeviceRepository) is True


class TestMemoryRepositories:
    """메모리 리포지토리 테스트 클래스"""
    
    def test_memory_user_repository_implements_interface(self):
        """메모리 User 리포지토리가 인터페이스를 구현하는지 테스트"""
        # Given & When
        repository = MemoryUserRepository()
        
        # Then
        assert isinstance(repository, IUserRepository)
    
    def test_memory_device_repository_implements_interface(self):
        """메모리 Device 리포지토리가 인터페이스를 구현하는지 테스트"""
        # Given & When
        repository = MemoryDeviceRepository()
        
        # Then
        assert isinstance(repository, IDeviceRepository) 