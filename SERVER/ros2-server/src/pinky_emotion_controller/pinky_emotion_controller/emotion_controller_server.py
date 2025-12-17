#!/usr/bin/env python3
"""
pinky_emotion_controller 서버 노드

이 노드는 pinky_emotion 패키지를 제어하기 위한 서비스 서버를 제공합니다.
서비스를 통해 로봇의 감정 표현을 제어할 수 있습니다.
"""
import rclpy
from rclpy.node import Node
from pinky_interfaces.srv import Emotion


class EmotionControllerServer(Node):
    """
    감정 표현 제어 서버
    
    제공하는 서비스:
    - SetEmotion: 로봇의 감정 표현 설정
    
    내부적으로 pinky_emotion 패키지의 서비스를 호출합니다.
    """
    
    # 지원하는 감정 타입
    SUPPORTED_EMOTIONS = [
        "hello", "basic", "angry", "bored", 
        "fun", "happy", "interest", "sad"
    ]
    
    def __init__(self):
        super().__init__('emotion_controller_server')
        
        # pinky_emotion 패키지의 서비스 클라이언트 생성
        # 원격 노드의 서비스를 호출하기 위해 클라이언트 사용
        self.emotion_service_client = self.create_client(
            Emotion,
            'set_emotion'  # pinky_emotion 노드의 서비스 이름
        )
        
        # 서비스 서버 생성 (외부에서 호출 가능)
        self.set_emotion_srv = self.create_service(
            Emotion,
            'emotion_controller/set_emotion',
            self.set_emotion_callback
        )
        
        self.get_logger().info('Emotion Controller Server started')
        self.get_logger().info('Available services:')
        self.get_logger().info('  - emotion_controller/set_emotion')
        self.get_logger().info('Service client created for remote control')
    
    def set_emotion_callback(self, request, response):
        """
        SetEmotion 서비스 콜백
        로봇의 감정 표현을 설정합니다.
        
        Args:
            request: Emotion 서비스 요청
            response: Emotion 서비스 응답
        
        Returns:
            response: 서비스 응답
        """
        emotion = request.emotion
        
        # 감정 타입 검증
        if emotion not in self.SUPPORTED_EMOTIONS:
            response.response = f"Unsupported emotion: {emotion}. Supported emotions: {', '.join(self.SUPPORTED_EMOTIONS)}"
            self.get_logger().warn(f"Unsupported emotion requested: {emotion}")
            return response
        
        self.get_logger().info(f"Request to set emotion to '{emotion}'")
        
        try:
            # pinky_emotion 노드의 서비스가 사용 가능한지 확인
            if not self.emotion_service_client.wait_for_service(timeout_sec=2.0):
                response.response = "pinky_emotion service is not available"
                self.get_logger().error("pinky_emotion service is not available")
                return response
            
            # 서비스 요청 생성
            emotion_request = Emotion.Request()
            emotion_request.emotion = emotion
            
            # 서비스 호출 (동기)
            future = self.emotion_service_client.call_async(emotion_request)
            
            # 응답 대기 (최대 5초)
            # rclpy.spin_until_future_complete는 이미 spin 중인 노드에서도 동작함
            try:
                rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            except Exception as e:
                self.get_logger().error(f"Error during spin_until_future_complete: {e}")
            
            if future.done():
                try:
                    emotion_response = future.result()
                    response.response = emotion_response.response
                    self.get_logger().info(f"Emotion set successfully: {emotion_response.response}")
                except Exception as e:
                    response.response = f"Error getting response: {str(e)}"
                    self.get_logger().error(f"Error getting response: {e}")
            else:
                response.response = "Service call timeout"
                self.get_logger().error("Service call timeout")
                
        except Exception as e:
            response.response = f"Error: {str(e)}"
            self.get_logger().error(f"Failed to set emotion: {e}")
        
        return response


def main(args=None):
    rclpy.init(args=args)
    emotion_controller_server = EmotionControllerServer()
    
    try:
        rclpy.spin(emotion_controller_server)
    except KeyboardInterrupt:
        emotion_controller_server.get_logger().info("KeyboardInterrupt, shutting down.")
    except Exception as e:
        emotion_controller_server.get_logger().error(f"Error: {e}")
    finally:
        try:
            emotion_controller_server.destroy_node()
        except Exception:
            pass
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()

