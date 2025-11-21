"""
의존성 주입 컨테이너

애플리케이션의 모든 의존성을 관리하고 제공합니다.
"""

from typing import AsyncGenerator, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.infrastructure.database import get_db_session
from app.interfaces.repositories.user_repository import IUserRepository
from app.interfaces.repositories.device_repository import IDeviceRepository
from app.interfaces.repositories.user_relationship_repository import IUserRelationshipRepository
from app.interfaces.repositories.user_profile_repository import IUserProfileRepository
from app.interfaces.repositories.home_state_snapshot_repository import IHomeStateSnapshotRepository
from app.interfaces.repositories.sensor_event_button_repository import ISensorEventButtonRepository
from app.interfaces.repositories.sensor_raw_temperature_repository import ISensorRawTemperatureRepository
from app.interfaces.repositories.sensor_repository import (
    ILoadCellRepository,
    IMQ5Repository,
    IMQ7Repository,
    IRFIDRepository,
    ISoundRepository,
    ITCRT5000Repository,
    IUltrasonicRepository,
    IEdgeFlameRepository,
    IEdgePIRRepository,
    IEdgeReedRepository,
    IEdgeTiltRepository
)
from app.interfaces.repositories.actuator_repository import (
    IActuatorBuzzerRepository,
    IActuatorIRTXRepository,
    IActuatorRelayRepository,
    IActuatorServoRepository
)
from app.interfaces.repositories.device_rtc_repository import IDeviceRTCStatusRepository
from app.interfaces.services.user_service_interface import IUserService
from app.interfaces.services.user_relationship_service_interface import IUserRelationshipService
from app.interfaces.services.user_profile_service_interface import IUserProfileService
from app.interfaces.services.home_state_snapshot_service_interface import IHomeStateSnapshotService
from app.interfaces.services.sensor_event_button_service_interface import ISensorEventButtonService
from app.interfaces.services.sensor_raw_temperature_service_interface import ISensorRawTemperatureService
from app.interfaces.services.sensor_service_interface import (
    ILoadCellService,
    IMQ5Service,
    IMQ7Service,
    IRFIDService,
    ISoundService,
    ITCRT5000Service,
    IUltrasonicService,
    IEdgeFlameService,
    IEdgePIRService,
    IEdgeReedService,
    IEdgeTiltService
)
from app.interfaces.services.actuator_service_interface import (
    IActuatorBuzzerService,
    IActuatorIRTXService,
    IActuatorRelayService,
    IActuatorServoService
)
from app.interfaces.services.device_rtc_service_interface import IDeviceRTCStatusService


class DependencyContainer:
    """의존성 주입 컨테이너"""
    
    def __init__(self):
        self._db_session: AsyncSession = None
        self._repositories: Dict[str, Any] = {}
        self._services: Dict[str, Any] = {}
    
    async def get_db_session(self) -> AsyncSession:
        """데이터베이스 세션 제공"""
        if not self._db_session:
            from app.infrastructure.database import get_db_session
            async for session in get_db_session():
                self._db_session = session
                break
        return self._db_session
    
    def get_user_repository(self, db_session: AsyncSession) -> IUserRepository:
        """사용자 리포지토리 제공"""
        from app.infrastructure.repositories.postgresql_user_repository import PostgreSQLUserRepository
        return PostgreSQLUserRepository(db_session)
    
    def get_device_repository(self, db_session: AsyncSession) -> IDeviceRepository:
        """디바이스 리포지토리 제공"""
        from app.infrastructure.repositories.postgresql_device_repository import PostgreSQLDeviceRepository
        return PostgreSQLDeviceRepository(db_session)
    
    def get_loadcell_repository(self, db_session: AsyncSession) -> ILoadCellRepository:
        """LoadCell 센서 리포지토리 제공"""
        from app.infrastructure.repositories.loadcell_repository import LoadCellRepository
        return LoadCellRepository(db_session)
    
    def get_mq5_repository(self, db_session: AsyncSession) -> IMQ5Repository:
        """MQ5 센서 리포지토리 제공"""
        from app.infrastructure.repositories.mq5_repository import MQ5Repository
        return MQ5Repository(db_session)
    
    def get_mq7_repository(self, db_session: AsyncSession) -> IMQ7Repository:
        """MQ7 센서 리포지토리 제공"""
        from app.infrastructure.repositories.mq7_repository import MQ7Repository
        return MQ7Repository(db_session)
    
    def get_rfid_repository(self, db_session: AsyncSession) -> IRFIDRepository:
        """RFID 센서 리포지토리 제공"""
        from app.infrastructure.repositories.rfid_repository import RFIDRepository
        return RFIDRepository(db_session)
    
    def get_sound_repository(self, db_session: AsyncSession) -> ISoundRepository:
        """Sound 센서 리포지토리 제공"""
        from app.infrastructure.repositories.sound_repository import SoundRepository
        return SoundRepository(db_session)
    
    def get_tcrt5000_repository(self, db_session: AsyncSession) -> ITCRT5000Repository:
        """TCRT5000 센서 리포지토리 제공"""
        from app.infrastructure.repositories.tcrt5000_repository import TCRT5000Repository
        return TCRT5000Repository(db_session)
    
    def get_ultrasonic_repository(self, db_session: AsyncSession) -> IUltrasonicRepository:
        """Ultrasonic 센서 리포지토리 제공"""
        from app.infrastructure.repositories.ultrasonic_repository import UltrasonicRepository
        return UltrasonicRepository(db_session)
    
    def get_edge_flame_repository(self, db_session: AsyncSession) -> IEdgeFlameRepository:
        """Edge Flame 센서 리포지토리 제공"""
        from app.infrastructure.repositories.edge_flame_repository import EdgeFlameRepository
        return EdgeFlameRepository(db_session)
    
    def get_edge_pir_repository(self, db_session: AsyncSession) -> IEdgePIRRepository:
        """Edge PIR 센서 리포지토리 제공"""
        from app.infrastructure.repositories.edge_pir_repository import EdgePIRRepository
        return EdgePIRRepository(db_session)
    
    def get_edge_reed_repository(self, db_session: AsyncSession) -> IEdgeReedRepository:
        """Edge Reed 센서 리포지토리 제공"""
        from app.infrastructure.repositories.edge_reed_repository import EdgeReedRepository
        return EdgeReedRepository(db_session)
    
    def get_edge_tilt_repository(self, db_session: AsyncSession) -> IEdgeTiltRepository:
        """Edge Tilt 센서 리포지토리 제공"""
        from app.infrastructure.repositories.edge_tilt_repository import EdgeTiltRepository
        return EdgeTiltRepository(db_session)
    
    def get_actuator_buzzer_repository(self, db_session: AsyncSession) -> IActuatorBuzzerRepository:
        """Buzzer 액추에이터 리포지토리 제공"""
        from app.infrastructure.repositories.actuator_buzzer_repository import ActuatorBuzzerRepository
        return ActuatorBuzzerRepository(db_session)
    
    def get_actuator_irtx_repository(self, db_session: AsyncSession) -> IActuatorIRTXRepository:
        """IR TX 액추에이터 리포지토리 제공"""
        from app.infrastructure.repositories.actuator_irtx_repository import ActuatorIRTXRepository
        return ActuatorIRTXRepository(db_session)
    
    def get_actuator_relay_repository(self, db_session: AsyncSession) -> IActuatorRelayRepository:
        """Relay 액추에이터 리포지토리 제공"""
        from app.infrastructure.repositories.actuator_relay_repository import ActuatorRelayRepository
        return ActuatorRelayRepository(db_session)
    
    def get_actuator_servo_repository(self, db_session: AsyncSession) -> IActuatorServoRepository:
        """Servo 액추에이터 리포지토리 제공"""
        from app.infrastructure.repositories.actuator_servo_repository import ActuatorServoRepository
        return ActuatorServoRepository(db_session)
    
    def get_device_rtc_repository(self, db_session: AsyncSession) -> IDeviceRTCStatusRepository:
        """DeviceRTCStatus 리포지토리 제공"""
        from app.infrastructure.repositories.device_rtc_repository import DeviceRTCStatusRepository
        return DeviceRTCStatusRepository(db_session)
    
    def get_user_service(self, db_session: AsyncSession) -> IUserService:
        """사용자 서비스 제공"""
        from app.use_cases.user_service import UserService
        user_repository = self.get_user_repository(db_session)
        return UserService(user_repository)
    
    def get_loadcell_service(self, db_session: AsyncSession) -> ILoadCellService:
        """LoadCell 센서 서비스 제공"""
        from app.use_cases.loadcell_service import LoadCellService
        loadcell_repository = self.get_loadcell_repository(db_session)
        return LoadCellService(loadcell_repository)
    
    def get_mq5_service(self, db_session: AsyncSession) -> IMQ5Service:
        """MQ5 센서 서비스 제공"""
        from app.use_cases.mq5_service import MQ5Service
        mq5_repository = self.get_mq5_repository(db_session)
        return MQ5Service(mq5_repository)
    
    def get_mq7_service(self, db_session: AsyncSession) -> IMQ7Service:
        """MQ7 센서 서비스 제공"""
        from app.use_cases.mq7_service import MQ7Service
        mq7_repository = self.get_mq7_repository(db_session)
        return MQ7Service(mq7_repository)
    
    def get_rfid_service(self, db_session: AsyncSession) -> IRFIDService:
        """RFID 센서 서비스 제공"""
        from app.use_cases.rfid_service import RFIDService
        rfid_repository = self.get_rfid_repository(db_session)
        return RFIDService(rfid_repository)
    
    def get_sound_service(self, db_session: AsyncSession) -> ISoundService:
        """Sound 센서 서비스 제공"""
        from app.use_cases.sound_service import SoundService
        sound_repository = self.get_sound_repository(db_session)
        return SoundService(sound_repository)
    
    def get_tcrt5000_service(self, db_session: AsyncSession) -> ITCRT5000Service:
        """TCRT5000 센서 서비스 제공"""
        from app.use_cases.tcrt5000_service import TCRT5000Service
        tcrt5000_repository = self.get_tcrt5000_repository(db_session)
        return TCRT5000Service(tcrt5000_repository)
    
    def get_ultrasonic_service(self, db_session: AsyncSession) -> IUltrasonicService:
        """Ultrasonic 센서 서비스 제공"""
        from app.use_cases.ultrasonic_service import UltrasonicService
        ultrasonic_repository = self.get_ultrasonic_repository(db_session)
        return UltrasonicService(ultrasonic_repository)
    
    def get_edge_flame_service(self, db_session: AsyncSession) -> IEdgeFlameService:
        """Edge Flame 센서 서비스 제공"""
        from app.use_cases.edge_flame_service import EdgeFlameService
        edge_flame_repository = self.get_edge_flame_repository(db_session)
        return EdgeFlameService(edge_flame_repository)
    
    def get_edge_pir_service(self, db_session: AsyncSession) -> IEdgePIRService:
        """Edge PIR 센서 서비스 제공"""
        from app.use_cases.edge_pir_service import EdgePIRService
        edge_pir_repository = self.get_edge_pir_repository(db_session)
        return EdgePIRService(edge_pir_repository)
    
    def get_edge_reed_service(self, db_session: AsyncSession) -> IEdgeReedService:
        """Edge Reed 센서 서비스 제공"""
        from app.use_cases.edge_reed_service import EdgeReedService
        edge_reed_repository = self.get_edge_reed_repository(db_session)
        return EdgeReedService(edge_reed_repository)
    
    def get_edge_tilt_service(self, db_session: AsyncSession) -> IEdgeTiltService:
        """Edge Tilt 센서 서비스 제공"""
        from app.use_cases.edge_tilt_service import EdgeTiltService
        edge_tilt_repository = self.get_edge_tilt_repository(db_session)
        return EdgeTiltService(edge_tilt_repository)
    
    def get_actuator_buzzer_service(self, db_session: AsyncSession) -> IActuatorBuzzerService:
        """Buzzer 액추에이터 서비스 제공"""
        from app.use_cases.actuator_buzzer_service import ActuatorBuzzerService
        actuator_buzzer_repository = self.get_actuator_buzzer_repository(db_session)
        return ActuatorBuzzerService(actuator_buzzer_repository)
    
    def get_actuator_irtx_service(self, db_session: AsyncSession) -> IActuatorIRTXService:
        """IR TX 액추에이터 서비스 제공"""
        from app.use_cases.actuator_irtx_service import ActuatorIRTXService
        actuator_irtx_repository = self.get_actuator_irtx_repository(db_session)
        return ActuatorIRTXService(actuator_irtx_repository)
    
    def get_actuator_relay_service(self, db_session: AsyncSession) -> IActuatorRelayService:
        """Relay 액추에이터 서비스 제공"""
        from app.use_cases.actuator_relay_service import ActuatorRelayService
        actuator_relay_repository = self.get_actuator_relay_repository(db_session)
        return ActuatorRelayService(actuator_relay_repository)
    
    def get_actuator_servo_service(self, db_session: AsyncSession) -> IActuatorServoService:
        """Servo 액추에이터 서비스 제공"""
        from app.use_cases.actuator_servo_service import ActuatorServoService
        actuator_servo_repository = self.get_actuator_servo_repository(db_session)
        return ActuatorServoService(actuator_servo_repository)
    
    def get_device_rtc_service(self, db_session: AsyncSession) -> IDeviceRTCStatusService:
        """DeviceRTCStatus 서비스 제공"""
        from app.use_cases.device_rtc_service import DeviceRTCStatusService
        device_rtc_repository = self.get_device_rtc_repository(db_session)
        return DeviceRTCStatusService(device_rtc_repository)
    
    def get_user_relationship_repository(self, db_session: AsyncSession) -> IUserRelationshipRepository:
        """사용자 관계 리포지토리 제공"""
        from app.infrastructure.repositories.user_relationship_repository import UserRelationshipRepository
        return UserRelationshipRepository(db_session)
    
    def get_user_profile_repository(self, db_session: AsyncSession) -> IUserProfileRepository:
        """사용자 프로필 리포지토리 제공"""
        from app.infrastructure.repositories.user_profile_repository import UserProfileRepository
        return UserProfileRepository(db_session)
    
    def get_user_relationship_service(self, db_session: AsyncSession) -> IUserRelationshipService:
        """사용자 관계 서비스 제공"""
        from app.use_cases.user_relationship_service import UserRelationshipService
        user_relationship_repository = self.get_user_relationship_repository(db_session)
        return UserRelationshipService(user_relationship_repository)
    
    def get_user_profile_service(self, db_session: AsyncSession) -> IUserProfileService:
        """사용자 프로필 서비스 제공"""
        from app.use_cases.user_profile_service import UserProfileService
        user_profile_repository = self.get_user_profile_repository(db_session)
        return UserProfileService(user_profile_repository)

    def get_home_state_snapshot_repository(self) -> IHomeStateSnapshotRepository:
        """홈 상태 스냅샷 리포지토리 의존성 주입"""
        if "home_state_snapshot_repository" not in self._repositories:
            from app.infrastructure.repositories.home_state_snapshot_repository import HomeStateSnapshotRepository
            from app.infrastructure.database import get_db
            db = next(get_db())
            self._repositories["home_state_snapshot_repository"] = HomeStateSnapshotRepository(db)
        return self._repositories["home_state_snapshot_repository"]
    
    def get_sensor_event_button_repository(self) -> ISensorEventButtonRepository:
        """버튼 이벤트 센서 리포지토리 의존성 주입"""
        if "sensor_event_button_repository" not in self._repositories:
            from app.infrastructure.repositories.sensor_event_button_repository import SensorEventButtonRepository
            from app.infrastructure.database import get_db
            db = next(get_db())
            self._repositories["sensor_event_button_repository"] = SensorEventButtonRepository(db)
        return self._repositories["sensor_event_button_repository"]
    
    def get_home_state_snapshot_service(self) -> IHomeStateSnapshotService:
        """홈 상태 스냅샷 서비스 의존성 주입"""
        if "home_state_snapshot_service" not in self._services:
            from app.use_cases.home_state_snapshot_service import HomeStateSnapshotService
            repository = self.get_home_state_snapshot_repository()
            self._services["home_state_snapshot_service"] = HomeStateSnapshotService(repository)
        return self._services["home_state_snapshot_service"]
    
    def get_sensor_event_button_service(self) -> ISensorEventButtonService:
        """버튼 이벤트 센서 서비스 의존성 주입"""
        if "sensor_event_button_service" not in self._services:
            from app.use_cases.sensor_event_button_service import SensorEventButtonService
            repository = self.get_sensor_event_button_repository()
            self._services["sensor_event_button_service"] = SensorEventButtonService(repository)
        return self._services["sensor_event_button_service"]

    def get_sensor_raw_temperature_repository(self) -> ISensorRawTemperatureRepository:
        """온도 센서 원시 데이터 리포지토리 의존성 주입"""
        if "sensor_raw_temperature_repository" not in self._repositories:
            from app.infrastructure.repositories.sensor_raw_temperature_repository import SensorRawTemperatureRepository
            from app.infrastructure.database import get_db
            db = next(get_db())
            self._repositories["sensor_raw_temperature_repository"] = SensorRawTemperatureRepository(db)
        return self._repositories["sensor_raw_temperature_repository"]
    
    def get_sensor_raw_temperature_service(self) -> ISensorRawTemperatureService:
        """온도 센서 원시 데이터 서비스 의존성 주입"""
        if "sensor_raw_temperature_service" not in self._services:
            from app.use_cases.sensor_raw_temperature_service import SensorRawTemperatureService
            repository = self.get_sensor_raw_temperature_repository()
            self._services["sensor_raw_temperature_service"] = SensorRawTemperatureService(repository)
        return self._services["sensor_raw_temperature_service"]


# 전역 컨테이너 인스턴스
container = DependencyContainer()

# 의존성 주입 함수들
def get_user_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUserRepository:
    """사용자 리포지토리 의존성 주입"""
    return container.get_user_repository(db_session)

def get_device_repository(db_session: AsyncSession = Depends(get_db_session)) -> IDeviceRepository:
    """디바이스 리포지토리 의존성 주입"""
    return container.get_device_repository(db_session)

def get_loadcell_repository(db_session: AsyncSession = Depends(get_db_session)) -> ILoadCellRepository:
    """LoadCell 센서 리포지토리 의존성 주입"""
    return container.get_loadcell_repository(db_session)

def get_mq5_repository(db_session: AsyncSession = Depends(get_db_session)) -> IMQ5Repository:
    """MQ5 센서 리포지토리 의존성 주입"""
    return container.get_mq5_repository(db_session)

def get_mq7_repository(db_session: AsyncSession = Depends(get_db_session)) -> IMQ7Repository:
    """MQ7 센서 리포지토리 의존성 주입"""
    return container.get_mq7_repository(db_session)

def get_rfid_repository(db_session: AsyncSession = Depends(get_db_session)) -> IRFIDRepository:
    """RFID 센서 리포지토리 의존성 주입"""
    return container.get_rfid_repository(db_session)

def get_sound_repository(db_session: AsyncSession = Depends(get_db_session)) -> ISoundRepository:
    """Sound 센서 리포지토리 의존성 주입"""
    return container.get_sound_repository(db_session)

def get_tcrt5000_repository(db_session: AsyncSession = Depends(get_db_session)) -> ITCRT5000Repository:
    """TCRT5000 센서 리포지토리 의존성 주입"""
    return container.get_tcrt5000_repository(db_session)

def get_ultrasonic_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUltrasonicRepository:
    """Ultrasonic 센서 리포지토리 의존성 주입"""
    return container.get_ultrasonic_repository(db_session)

def get_edge_flame_repository(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeFlameRepository:
    """Edge Flame 센서 리포지토리 의존성 주입"""
    return container.get_edge_flame_repository(db_session)

def get_edge_pir_repository(db_session: AsyncSession = Depends(get_db_session)) -> IEdgePIRRepository:
    """Edge PIR 센서 리포지토리 의존성 주입"""
    return container.get_edge_pir_repository(db_session)

def get_edge_reed_repository(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeReedRepository:
    """Edge Reed 센서 리포지토리 의존성 주입"""
    return container.get_edge_reed_repository(db_session)

def get_edge_tilt_repository(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeTiltRepository:
    """Edge Tilt 센서 리포지토리 의존성 주입"""
    return container.get_edge_tilt_repository(db_session)

def get_actuator_buzzer_repository(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorBuzzerRepository:
    """Buzzer 액추에이터 리포지토리 의존성 주입"""
    return container.get_actuator_buzzer_repository(db_session)

def get_actuator_irtx_repository(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorIRTXRepository:
    """IR TX 액추에이터 리포지토리 의존성 주입"""
    return container.get_actuator_irtx_repository(db_session)

def get_actuator_relay_repository(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorRelayRepository:
    """Relay 액추에이터 리포지토리 의존성 주입"""
    return container.get_actuator_relay_repository(db_session)

def get_actuator_servo_repository(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorServoRepository:
    """Servo 액추에이터 리포지토리 의존성 주입"""
    return container.get_actuator_servo_repository(db_session)

def get_device_rtc_repository(db_session: AsyncSession = Depends(get_db_session)) -> IDeviceRTCStatusRepository:
    """DeviceRTCStatus 리포지토리 의존성 주입"""
    return container.get_device_rtc_repository(db_session)

def get_device_rtc_service(db_session: AsyncSession = Depends(get_db_session)) -> IDeviceRTCStatusService:
    """DeviceRTCStatus 서비스 의존성 주입"""
    return container.get_device_rtc_service(db_session)

def get_user_service(db_session: AsyncSession = Depends(get_db_session)) -> IUserService:
    """사용자 서비스 의존성 주입"""
    return container.get_user_service(db_session)

def get_loadcell_service(db_session: AsyncSession = Depends(get_db_session)) -> ILoadCellService:
    """LoadCell 센서 서비스 의존성 주입"""
    return container.get_loadcell_service(db_session)

def get_mq5_service(db_session: AsyncSession = Depends(get_db_session)) -> IMQ5Service:
    """MQ5 센서 서비스 의존성 주입"""
    return container.get_mq5_service(db_session)

def get_mq7_service(db_session: AsyncSession = Depends(get_db_session)) -> IMQ7Service:
    """MQ7 센서 서비스 의존성 주입"""
    return container.get_mq7_service(db_session)

def get_rfid_service(db_session: AsyncSession = Depends(get_db_session)) -> IRFIDService:
    """RFID 센서 서비스 의존성 주입"""
    return container.get_rfid_service(db_session)

def get_sound_service(db_session: AsyncSession = Depends(get_db_session)) -> ISoundService:
    """Sound 센서 서비스 의존성 주입"""
    return container.get_sound_service(db_session)

def get_tcrt5000_service(db_session: AsyncSession = Depends(get_db_session)) -> ITCRT5000Service:
    """TCRT5000 센서 서비스 의존성 주입"""
    return container.get_tcrt5000_service(db_session)

def get_ultrasonic_service(db_session: AsyncSession = Depends(get_db_session)) -> IUltrasonicService:
    """Ultrasonic 센서 서비스 의존성 주입"""
    return container.get_ultrasonic_service(db_session)

def get_edge_flame_service(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeFlameService:
    """Edge Flame 센서 서비스 의존성 주입"""
    return container.get_edge_flame_service(db_session)

def get_edge_pir_service(db_session: AsyncSession = Depends(get_db_session)) -> IEdgePIRService:
    """Edge PIR 센서 서비스 제공"""
    return container.get_edge_pir_service(db_session)

def get_edge_reed_service(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeReedService:
    """Edge Reed 센서 서비스 제공"""
    return container.get_edge_reed_service(db_session)

def get_edge_tilt_service(db_session: AsyncSession = Depends(get_db_session)) -> IEdgeTiltService:
    """Edge Tilt 센서 서비스 제공"""
    return container.get_edge_tilt_service(db_session)

def get_actuator_buzzer_service(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorBuzzerService:
    """Buzzer 액추에이터 서비스 제공"""
    return container.get_actuator_buzzer_service(db_session)

def get_actuator_irtx_service(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorIRTXService:
    """IR TX 액추에이터 서비스 제공"""
    return container.get_actuator_irtx_service(db_session)

def get_actuator_relay_service(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorRelayService:
    """Relay 액추에이터 서비스 제공"""
    return container.get_actuator_relay_service(db_session)

def get_actuator_servo_service(db_session: AsyncSession = Depends(get_db_session)) -> IActuatorServoService:
    """Servo 액추에이터 서비스 제공"""
    return container.get_actuator_servo_service(db_session)

def get_user_relationship_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUserRelationshipRepository:
    """사용자 관계 리포지토리 의존성 주입"""
    return container.get_user_relationship_repository(db_session)

def get_user_profile_repository(db_session: AsyncSession = Depends(get_db_session)) -> IUserProfileRepository:
    """사용자 프로필 리포지토리 의존성 주입"""
    return container.get_user_profile_repository(db_session)

def get_user_relationship_service(db_session: AsyncSession = Depends(get_db_session)) -> IUserRelationshipService:
    """사용자 관계 서비스 의존성 주입"""
    return container.get_user_relationship_service(db_session)

def get_user_profile_service(db_session: AsyncSession = Depends(get_db_session)) -> IUserProfileService:
    """사용자 프로필 서비스 의존성 주입"""
    return container.get_user_profile_service(db_session) 

# 홈 상태 스냅샷 의존성 주입 함수
def get_home_state_snapshot_repository() -> IHomeStateSnapshotRepository:
    """홈 상태 스냅샷 리포지토리 의존성 주입"""
    container = DependencyContainer()
    return container.get_home_state_snapshot_repository()

def get_home_state_snapshot_service() -> IHomeStateSnapshotService:
    """홈 상태 스냅샷 서비스 의존성 주입"""
    container = DependencyContainer()
    return container.get_home_state_snapshot_service()

# 버튼 이벤트 센서 의존성 주입 함수
def get_sensor_event_button_repository() -> ISensorEventButtonRepository:
    """버튼 이벤트 센서 리포지토리 의존성 주입"""
    container = DependencyContainer()
    return container.get_sensor_event_button_repository()

def get_sensor_event_button_service() -> ISensorEventButtonService:
    """버튼 이벤트 센서 서비스 의존성 주입"""
    container = DependencyContainer()
    return container.get_sensor_event_button_service() 

# 온도 센서 원시 데이터 의존성 주입 함수
def get_sensor_raw_temperature_repository() -> ISensorRawTemperatureRepository:
    """온도 센서 원시 데이터 리포지토리 의존성 주입"""
    container = DependencyContainer()
    return container.get_sensor_raw_temperature_repository()

def get_sensor_raw_temperature_service() -> ISensorRawTemperatureService:
    """온도 센서 원시 데이터 서비스 의존성 주입"""
    container = DependencyContainer()
    return container.get_sensor_raw_temperature_service() 