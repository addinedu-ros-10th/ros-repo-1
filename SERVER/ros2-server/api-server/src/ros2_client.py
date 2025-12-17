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
    
    def clear_display(self, timeout: float = 2.0) -> tuple[bool, str]:
        """
        LCD 화면 지우기 (검은 화면으로 초기화)
        
        Args:
            timeout: 타임아웃 (초)
        
        Returns:
            (성공 여부, 응답 메시지)
        """
        try:
            if not ROS2_AVAILABLE:
                logger.info("모킹 모드: LCD 화면 지우기 요청")
                return False, "ROS2 not available (mocking mode)"
            
            self._ensure_initialized()
            
            if self.node is None:
                logger.warning("ROS2 노드가 초기화되지 않았습니다. 모킹 모드로 동작합니다.")
                return False, "Node not initialized"
            
            # ClearDisplay 서비스 타입 가져오기
            try:
                from pinky_lcd_display_interfaces.srv import ClearDisplay
                clear_service_type = ClearDisplay
            except ImportError:
                logger.warning("pinky_lcd_display_interfaces 패키지를 찾을 수 없습니다.")
                return False, "ClearDisplay service type not available"
            
            # ClearDisplay 서비스 이름 구성
            if self.service_name.startswith("/"):
                clear_service_name = self.service_name.replace("set_display", "clear_display")
            elif self.namespace:
                clear_service_name = f"{self.namespace}/lcd_controller/clear_display"
            else:
                clear_service_name = "lcd_controller/clear_display"
            
            # ClearDisplay 서비스 클라이언트 생성
            clear_client = self.node.create_client(
                clear_service_type,
                clear_service_name
            )
            
            # 서비스 사용 가능 확인
            if not clear_client.wait_for_service(timeout_sec=1.0):
                error_msg = f"ClearDisplay 서비스 '{clear_service_name}'를 사용할 수 없습니다"
                logger.warning(error_msg)
                return False, error_msg
            
            # 요청 생성 (ClearDisplay는 요청 파라미터가 없음)
            request = clear_service_type.Request()
            
            # 비동기 호출
            future = clear_client.call_async(request)
            
            # 응답 대기
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=timeout)
            
            if future.done():
                response = future.result()
                if response.success:
                    logger.info(f"LCD 화면 지우기 성공")
                    return True, response.message
                else:
                    logger.warning(f"LCD 화면 지우기 실패: {response.message}")
                    return False, response.message
            else:
                error_msg = f"LCD 화면 지우기 타임아웃 ({timeout}초)"
                logger.warning(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"LCD 화면 지우기 중 오류: {e}"
            logger.error(error_msg)
            return False, error_msg
    
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


class EmotionClient:
    """ROS2 감정 표현 서비스 클라이언트"""
    
    # 지원하는 감정 타입
    SUPPORTED_EMOTIONS = [
        "hello", "basic", "angry", "bored", 
        "fun", "happy", "interest", "sad"
    ]
    
    def __init__(self, namespace: str = "", service_name: str = "emotion_controller/set_emotion"):
        self.namespace = namespace
        # 전체 서비스 이름 구성 (네임스페이스 포함)
        if service_name.startswith("/"):
            self.service_name = service_name
        elif namespace:
            self.service_name = f"{namespace}/{service_name.lstrip('/')}"
        else:
            self.service_name = service_name
        self.node: Optional[Node] = None
        self.client = None
        self.service_type = None
        self._initialized = False
        self._lock = threading.Lock()
        logger.info(f"EmotionClient 초기화: namespace={namespace}, service_name={self.service_name}")
    
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
                        self.node = Node('ros2_emotion_client')
                        # 서비스 타입 가져오기
                        self.service_type = type(self)._get_service_type()
                        if self.service_type is None:
                            raise ValueError("서비스 타입을 로드할 수 없습니다")
                        self.client = self.node.create_client(
                            self.service_type,
                            self.service_name
                        )
                        self._initialized = True
                        logger.info(f"EmotionClient 초기화 완료: {self.service_name}")
                    except Exception as e:
                        logger.error(f"EmotionClient 초기화 실패: {e}")
                        raise
    
    @staticmethod
    def _get_service_type():
        """서비스 타입 동적 로드"""
        try:
            from pinky_interfaces.srv import Emotion
            return Emotion
        except ImportError:
            logger.warning("pinky_interfaces 패키지를 찾을 수 없습니다. 모킹 모드로 동작합니다.")
            return None
    
    def set_emotion(self, emotion: str, timeout: float = 3.0) -> tuple[bool, str]:
        """
        감정 표현 설정
        
        Args:
            emotion: 감정 타입 (hello, basic, angry, bored, fun, happy, interest, sad)
            timeout: 타임아웃 (초)
        
        Returns:
            (성공 여부, 응답 메시지)
        """
        try:
            if not ROS2_AVAILABLE:
                logger.info(f"모킹 모드: 감정 표현 요청 (emotion: {emotion})")
                return False, "ROS2 not available (mocking mode)"
            
            # 감정 타입 검증
            if emotion not in self.SUPPORTED_EMOTIONS:
                error_msg = f"Unsupported emotion: {emotion}. Supported: {', '.join(self.SUPPORTED_EMOTIONS)}"
                logger.warning(error_msg)
                return False, error_msg
            
            self._ensure_initialized()
            
            if self.client is None:
                logger.warning("ROS2 서비스 클라이언트가 초기화되지 않았습니다. 모킹 모드로 동작합니다.")
                return False, "Client not initialized"
            
            # 서비스 사용 가능 확인
            if not self.client.wait_for_service(timeout_sec=1.0):
                error_msg = f"ROS2 서비스 '{self.service_name}'를 사용할 수 없습니다"
                logger.warning(error_msg)
                return False, error_msg
            
            # 요청 생성
            if self.service_type is None:
                logger.error("서비스 타입이 설정되지 않았습니다")
                return False, "Service type not set"
            
            request = self.service_type.Request()
            request.emotion = emotion
            
            # 비동기 호출
            future = self.client.call_async(request)
            
            # 응답 대기
            rclpy.spin_until_future_complete(self.node, future, timeout_sec=timeout)
            
            if future.done():
                response = future.result()
                logger.info(f"감정 표현 설정 성공: {emotion} - {response.response}")
                return True, response.response
            else:
                error_msg = f"감정 표현 설정 타임아웃 ({timeout}초)"
                logger.warning(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"감정 표현 설정 중 오류: {e}"
            logger.error(error_msg)
            return False, error_msg
    
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

