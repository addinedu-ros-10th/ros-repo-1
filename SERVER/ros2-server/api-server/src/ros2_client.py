"""
ROS2 서비스 클라이언트
"""
from typing import List, Optional
import logging
import threading

# ROS2 모듈 선택적 import
try:
    import rclpy
    from rclpy.node import Node
    ROS2_AVAILABLE = True
except ImportError:
    rclpy = None
    Node = None
    ROS2_AVAILABLE = False

logger = logging.getLogger(__name__)


class ROS2Client:
    """ROS2 서비스 클라이언트"""
    
    def __init__(self, namespace: str = "/pinky", service_name: str = "lcd_controller/set_display"):
        self.namespace = namespace
        # 전체 서비스 이름 구성 (네임스페이스 포함)
        # service_name이 이미 절대 경로(/)로 시작하면 네임스페이스 추가 안 함
        if service_name.startswith("/"):
            # 이미 절대 경로이면 그대로 사용
            self.service_name = service_name
        elif namespace:
            # 네임스페이스와 서비스 이름 결합
            # namespace가 "/pinky", service_name이 "lcd_controller/set_display"인 경우
            # 결과: "/pinky/lcd_controller/set_display"
            self.service_name = f"{namespace}/{service_name.lstrip('/')}"
        else:
            self.service_name = service_name
        self.node: Optional[Node] = None
        self.client = None
        self.service_type = None  # 서비스 타입 저장
        self._initialized = False
        self._lock = threading.Lock()
        logger.info(f"ROS2Client 초기화: namespace={namespace}, service_name={self.service_name}")
    
    def _ensure_initialized(self):
        """ROS2 초기화 확인 및 수행"""
        if not ROS2_AVAILABLE:
            logger.warning("ROS2가 설치되어 있지 않습니다. 모킹 모드로 동작합니다.")
            return
        
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    try:
                        if not rclpy.ok():
                            rclpy.init()
                        self.node = Node('ros2_api_client')
                        # 서비스 타입 가져오기
                        self.service_type = type(self)._get_service_type()
                        if self.service_type is None:
                            raise ValueError("서비스 타입을 로드할 수 없습니다")
                        self.client = self.node.create_client(
                            self.service_type,
                            self.service_name
                        )
                        self._initialized = True
                        logger.info(f"ROS2 클라이언트 초기화 완료: {self.service_name}")
                    except Exception as e:
                        logger.error(f"ROS2 클라이언트 초기화 실패: {e}")
                        raise
    
    @staticmethod
    def _get_service_type():
        """서비스 타입 동적 로드"""
        try:
            # pinky_lcd_display_interfaces 패키지가 설치되어 있어야 함
            from pinky_lcd_display_interfaces.srv import SetDisplay
            return SetDisplay
        except ImportError:
            logger.warning("pinky_lcd_display_interfaces 패키지를 찾을 수 없습니다. 모킹 모드로 동작합니다.")
            return None
    
    def display_resident_info(self, title: str, lines: List[str], 
                             show_timestamp: bool = True, timeout: float = 2.0) -> bool:
        """
        LCD에 어르신 정보 표시
        
        Args:
            title: 타이틀 텍스트
            lines: 본문 라인들
            show_timestamp: 타임스탬프 표시 여부
            timeout: 타임아웃 (초)
        
        Returns:
            성공 여부
        """
        try:
            if not ROS2_AVAILABLE:
                logger.info(f"모킹 모드: LCD 표시 요청 (title: {title})")
                return False
            
            self._ensure_initialized()
            
            if self.client is None:
                logger.warning("ROS2 서비스 클라이언트가 초기화되지 않았습니다. 모킹 모드로 동작합니다.")
                return False
            
            # 서비스 사용 가능 확인
            if not self.client.wait_for_service(timeout_sec=1.0):
                logger.warning(f"ROS2 서비스 '{self.service_name}'를 사용할 수 없습니다")
                return False
            
            # 요청 생성 (서비스 타입에서 직접 생성)
            if self.service_type is None:
                logger.error("서비스 타입이 설정되지 않았습니다")
                return False
            
            request = self.service_type.Request()
            request.title = title
            request.lines = lines
            request.show_timestamp = show_timestamp
            
            # 비동기 호출
            future = self.client.call_async(request)
            
            # 응답 대기
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=timeout)
            
            if future.done():
                response = future.result()
                if response.success:
                    logger.info(f"LCD 표시 성공: {title}")
                    return True
                else:
                    logger.warning(f"LCD 표시 실패: {response.message}")
                    return False
            else:
                logger.warning(f"LCD 표시 타임아웃 ({timeout}초)")
                return False
                
        except Exception as e:
            logger.error(f"LCD 표시 중 오류: {e}")
            return False
    
    def health_check(self) -> bool:
        """ROS2 서비스 헬스 체크"""
        if not ROS2_AVAILABLE:
            return False
        try:
            self._ensure_initialized()
            if self.client is None:
                return False
            return self.client.wait_for_service(timeout_sec=1.0)
        except Exception:
            return False
    
    def shutdown(self):
        """ROS2 클라이언트 종료"""
        if not ROS2_AVAILABLE:
            return
        if self.node:
            self.node.destroy_node()
        if rclpy and rclpy.ok():
            rclpy.shutdown()
        self._initialized = False

