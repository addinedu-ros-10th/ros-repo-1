import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from PIL import Image, ImageSequence
import os
import threading

from pinky_interfaces.srv import Emotion

# pinky_lcd_display의 DisplayImage 서비스 사용
try:
    from pinky_lcd_display_interfaces.srv import DisplayImage
    DISPLAY_SERVICE_AVAILABLE = True
except ImportError:
    DISPLAY_SERVICE_AVAILABLE = False
    print("Warning: pinky_lcd_display_interfaces not available. Emotion display will be disabled.")


class PinkyEmotion(Node):
    def __init__(self):
        super().__init__('pinky_emotion')

        self.emotion_path = os.path.join(get_package_share_directory('pinky_emotion'), 'emotion')
        self.emotion_service = self.create_service(Emotion, 'set_emotion', self.set_emotion_callback)
        
        # LCD 직접 사용 대신 pinky_lcd_display 서비스 클라이언트 사용
        if DISPLAY_SERVICE_AVAILABLE:
            self.display_image_client = self.create_client(
                DisplayImage,
                'lcd_controller/display_image'
            )
            self.get_logger().info("Waiting for LCD display service...")
            if not self.display_image_client.wait_for_service(timeout_sec=5.0):
                self.get_logger().warn("LCD display service not available. Emotion display will be disabled.")
                self.display_image_client = None
            else:
                self.get_logger().info("LCD display service connected.")
        else:
            self.display_image_client = None
        
        self.gif_frames = []
        self.current_frame_index = 0
        self.gif_lock = threading.Lock() 
        
        self.emotion_cache = {}  
        self._preload_gifs()

        self.animation_timer = self.create_timer(0.1, self.timer_callback)

        self.get_logger().info("Pinky's emotion server is ready!! All GIFs pre-loaded.")

        with self.gif_lock:
            self.gif_frames = self.emotion_cache.get("basic", [])

    def _preload_gifs(self):
        self.get_logger().info("Pre-loading all emotion GIFs into memory...")
        try:
            gif_files = [f for f in os.listdir(self.emotion_path) if f.endswith('.gif')]
            for gif_file in gif_files:
                emotion_name = os.path.splitext(gif_file)[0]
                file_path = os.path.join(self.emotion_path, gif_file)
                
                img = Image.open(file_path)
                frames = []
                for i, frame in enumerate(ImageSequence.Iterator(img)):
                    if i % 2 == 0: 
                        frames.append(frame.copy().convert("RGB"))
                
                self.emotion_cache[emotion_name] = frames
                self.get_logger().info(f"  - Cached '{emotion_name}' ({len(frames)} frames)")
        except Exception as e:
            self.get_logger().error(f"Failed during GIF pre-loading: {e}")

    def set_emotion_callback(self, request, response):
        emo = request.emotion
        self.get_logger().info(f"Request to set emotion to '{emo}'")

        if emo in self.emotion_cache:
            with self.gif_lock:
                self.gif_frames = self.emotion_cache[emo]
                self.current_frame_index = 0
            response.response = f"Emotion set to {emo}"
        else:
            response.response = "Wrong command or emotion not cached"
            self.get_logger().warn(f"Emotion '{emo}' not found in cache.")

        return response

    def timer_callback(self):
        with self.gif_lock:
            if not self.gif_frames:
                return
            
            if self.display_image_client is None:
                return
            
            frame_to_show = self.gif_frames[self.current_frame_index]
            
            # 임시 파일로 저장하여 서비스에 전달
            # TODO: 더 효율적인 방법 (이미지 데이터 직접 전송) 구현 가능
            try:
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                    frame_to_show.save(tmp_file.name, 'PNG')
                    tmp_path = tmp_file.name
                
                # DisplayImage 서비스 호출
                request = DisplayImage.Request()
                request.image_path = tmp_path
                request.use_path = True
                request.x = 0
                request.y = 0
                request.width = 0  # 원본 크기
                request.height = 0  # 원본 크기
                request.clear_before = False  # 애니메이션이므로 이전 프레임 유지
                
                future = self.display_image_client.call_async(request)
                # 비동기 호출이므로 결과를 기다리지 않음 (성능 향상)
                # rclpy.spin_until_future_complete(self, future, timeout_sec=0.1)
                
                # 임시 파일 삭제 (나중에)
                # os.unlink(tmp_path)  # 서비스가 완료될 때까지 유지
                
            except Exception as e:
                self.get_logger().error(f"Error displaying frame: {e}")

            self.current_frame_index = (self.current_frame_index + 1) % len(self.gif_frames)


def main(args=None):
    rclpy.init(args=args)
    pinky_emotion_node = PinkyEmotion()
     
    try:
        rclpy.spin(pinky_emotion_node)
    except KeyboardInterrupt:
        pinky_emotion_node.get_logger().info("KeyboardInterrupt, shutting down.")
    finally:
        pinky_emotion_node.destroy_node()
        rclpy.shutdown()
 
if __name__ == '__main__':
    main()

