#!/usr/bin/env python3
"""
pinky_lcd_display_controller 서버 노드

이 노드는 pinky_lcd_display 패키지를 제어하기 위한 서비스 서버를 제공합니다.
서비스를 통해 LCD 표시 내용과 스타일을 제어할 수 있습니다.
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from std_msgs.msg import String
from pinky_lcd_display_interfaces.srv import SetDisplay, SetStyle, ClearDisplay, SetLayout
from pinky_lcd_display_interfaces.action import SetDisplay as SetDisplayAction
from pinky_lcd_display_interfaces.action import ScrollText
import os
import time
from ament_index_python.packages import get_package_share_directory


class LCDControllerServer(Node):
    """
    LCD 디스플레이 제어 서버
    
    제공하는 서비스:
    - SetDisplay: LCD에 표시할 내용 설정
    - SetStyle: LCD 표시 스타일 설정 (색상, 폰트 등)
    - ClearDisplay: LCD 화면 지우기
    
    내부적으로 pinky_lcd_display 패키지의 서비스/액션을 호출합니다.
    서비스가 사용 불가능한 경우 토픽으로 폴백합니다.
    """
    
    def _find_korean_font(self):
        """
        한글 폰트 파일 경로를 찾습니다.
        
        우선순위:
        1. 패키지 설치 경로의 fonts/maruburi/TTF/MaruBuri-Regular.ttf
        2. 현재 작업 디렉토리의 fonts/maruburi/TTF/MaruBuri-Regular.ttf
        3. 상대 경로 ./fonts/maruburi/TTF/MaruBuri-Regular.ttf
        
        Returns:
            str: 폰트 파일 경로, 찾지 못하면 None
        """
        font_filename = 'MaruBuri-Regular.ttf'
        possible_paths = []
        
        # 1. 패키지 설치 경로에서 찾기
        try:
            package_share_dir = get_package_share_directory('pinky_lcd_display_controller')
            installed_font_path = os.path.join(
                package_share_dir, 'fonts', 'maruburi', 'TTF', font_filename
            )
            possible_paths.append(installed_font_path)
        except Exception as e:
            self.get_logger().debug(f'Could not get package share directory: {e}')
        
        # 2. 현재 작업 디렉토리 기준
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_font_path = os.path.join(current_dir, 'fonts', 'maruburi', 'TTF', font_filename)
        possible_paths.append(local_font_path)
        
        # 3. 상대 경로 (개발 환경)
        relative_font_path = os.path.join('fonts', 'maruburi', 'TTF', font_filename)
        possible_paths.append(relative_font_path)
        
        # 4. 절대 경로 (로봇 환경)
        robot_font_path = os.path.join('/home/pinky/ros-repo-1/SERVER/ros2-server/src/pinky_lcd_display_controller', 'fonts', 'maruburi', 'TTF', font_filename)
        possible_paths.append(robot_font_path)
        
        # 경로 확인
        for font_path in possible_paths:
            if os.path.exists(font_path) and os.path.isfile(font_path):
                return os.path.abspath(font_path)
        
        # 기본 폰트 경로 반환
        return '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    
    def __init__(self):
        super().__init__('lcd_controller_server')
        
        # pinky_lcd_display 패키지의 /lcd/status 토픽에 발행 (폴백용)
        self.lcd_status_publisher = self.create_publisher(
            String,
            '/lcd/status',
            10
        )
        
        # 한글 폰트 경로 찾기
        korean_font_path = self._find_korean_font()
        
        # 현재 스타일 설정 저장
        self.current_style = {
            'bg_color': (0, 0, 0),
            'title_color': (0, 255, 0),
            'body_color': (255, 255, 255),
            'timestamp_color': (100, 100, 255),
            'title_font_size': 20,
            'body_font_size': 18,
            'font_path': korean_font_path,
        }
        
        if korean_font_path and 'MaruBuri' in korean_font_path:
            self.get_logger().info(f'Korean font found: {korean_font_path}')
        else:
            self.get_logger().warn('Korean font not found, using default font')
        
        # 서비스 클라이언트 생성 (pinky_lcd_display 패키지의 서비스 호출용)
        self.set_display_client = self.create_client(
            SetDisplay,
            'lcd_controller/set_display'
        )
        
        self.set_style_client = self.create_client(
            SetStyle,
            'lcd_controller/set_style'
        )
        
        self.clear_display_client = self.create_client(
            ClearDisplay,
            'lcd_controller/clear_display'
        )
        
        self.set_layout_client = self.create_client(
            SetLayout,
            'lcd_controller/set_layout'
        )
        
        # 액션 클라이언트 생성
        self.set_display_action_client = ActionClient(
            self,
            SetDisplayAction,
            'lcd_controller/set_display_action'
        )
        
        self.scroll_text_action_client = ActionClient(
            self,
            ScrollText,
            'lcd_controller/scroll_text_action'
        )
        
        # 서비스 서버 생성 (외부에서 호출 가능)
        self.set_display_srv = self.create_service(
            SetDisplay,
            'lcd_controller/set_display',
            self.set_display_callback
        )
        
        self.set_style_srv = self.create_service(
            SetStyle,
            'lcd_controller/set_style',
            self.set_style_callback
        )
        
        self.clear_display_srv = self.create_service(
            ClearDisplay,
            'lcd_controller/clear_display',
            self.clear_display_callback
        )
        
        self.get_logger().info('LCD Controller Server started')
        self.get_logger().info('Available services:')
        self.get_logger().info('  - lcd_controller/set_display')
        self.get_logger().info('  - lcd_controller/set_style')
        self.get_logger().info('  - lcd_controller/clear_display')
        self.get_logger().info('Service/Action clients created for remote control')
    
    def set_display_callback(self, request, response):
        """
        SetDisplay 서비스 콜백
        LCD에 표시할 내용을 설정합니다.
        
        우선 서비스 클라이언트를 통해 pinky_lcd_display의 서비스를 호출하고,
        서비스가 사용 불가능한 경우 토픽으로 폴백합니다.
        """
        try:
            # 서비스 클라이언트로 호출 시도
            if self.set_display_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().debug('Calling SetDisplay service on pinky_lcd_display')
                future = self.set_display_client.call_async(request)
                
                # 짧은 시간 동안 폴링 (데드락 방지)
                # spin_until_future_complete는 서비스 콜백 내부에서 데드락을 일으킬 수 있음
                timeout_sec = 5.0  # 타임아웃 증가 (LCD 렌더링 시간 고려)
                start_time = time.time()
                
                while not future.done() and (time.time() - start_time) < timeout_sec:
                    rclpy.spin_once(self, timeout_sec=0.1)  # 짧은 시간만 스핀
                
                if future.done():
                    service_response = future.result()
                    response.success = service_response.success
                    response.message = service_response.message
                    self.get_logger().info(f"SetDisplay service call successful: {response.message}")
                else:
                    elapsed = time.time() - start_time
                    self.get_logger().warn(f"SetDisplay service call timeout after {elapsed:.2f}s, falling back to topic")
                    self._fallback_to_topic_set_display(request, response)
            else:
                self.get_logger().warn("SetDisplay service not available, falling back to topic")
                self._fallback_to_topic_set_display(request, response)
            
        except Exception as e:
            self.get_logger().error(f"SetDisplay service call failed: {e}, falling back to topic")
            self._fallback_to_topic_set_display(request, response)
        
        return response
    
    def set_style_callback(self, request, response):
        """
        SetStyle 서비스 콜백
        LCD 표시 스타일을 설정합니다.
        
        서비스 클라이언트를 통해 pinky_lcd_display의 서비스를 호출합니다.
        """
        try:
            # 서비스 클라이언트로 호출 시도
            if self.set_style_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().debug('Calling SetStyle service on pinky_lcd_display')
                future = self.set_style_client.call_async(request)
                
                # 짧은 시간 동안 폴링 (데드락 방지)
                timeout_sec = 5.0  # 타임아웃 증가
                start_time = time.time()
                
                while not future.done() and (time.time() - start_time) < timeout_sec:
                    rclpy.spin_once(self, timeout_sec=0.1)
                
                if future.done():
                    service_response = future.result()
                    response.success = service_response.success
                    response.message = service_response.message
                    self.get_logger().info(f"SetStyle service call successful: {response.message}")
                else:
                    elapsed = time.time() - start_time
                    response.success = False
                    response.message = f"SetStyle service call timeout after {elapsed:.2f}s"
                    self.get_logger().warn(response.message)
            else:
                response.success = False
                response.message = "SetStyle service not available"
                self.get_logger().warn("SetStyle service not available")
            
            # 로컬 스타일도 저장 (참고용)
            self.current_style['bg_color'] = (
                request.bg_color_r,
                request.bg_color_g,
                request.bg_color_b
            )
            self.current_style['title_color'] = (
                request.title_color_r,
                request.title_color_g,
                request.title_color_b
            )
            self.current_style['body_color'] = (
                request.body_color_r,
                request.body_color_g,
                request.body_color_b
            )
            self.current_style['timestamp_color'] = (
                request.timestamp_color_r,
                request.timestamp_color_g,
                request.timestamp_color_b
            )
            self.current_style['title_font_size'] = request.title_font_size
            self.current_style['body_font_size'] = request.body_font_size
            
            if request.font_path:
                self.current_style['font_path'] = request.font_path
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"Failed to set style: {e}")
        
        return response
    
    def clear_display_callback(self, request, response):
        """
        ClearDisplay 서비스 콜백
        LCD 화면을 지웁니다.
        
        우선 서비스 클라이언트를 통해 pinky_lcd_display의 서비스를 호출하고,
        서비스가 사용 불가능한 경우 토픽으로 폴백합니다.
        """
        try:
            # 서비스 클라이언트로 호출 시도
            if self.clear_display_client.wait_for_service(timeout_sec=1.0):
                self.get_logger().debug('Calling ClearDisplay service on pinky_lcd_display')
                future = self.clear_display_client.call_async(request)
                
                # 짧은 시간 동안 폴링 (데드락 방지)
                timeout_sec = 5.0  # 타임아웃 증가
                start_time = time.time()
                
                while not future.done() and (time.time() - start_time) < timeout_sec:
                    rclpy.spin_once(self, timeout_sec=0.1)
                
                if future.done():
                    service_response = future.result()
                    response.success = service_response.success
                    response.message = service_response.message
                    self.get_logger().info(f"ClearDisplay service call successful: {response.message}")
                else:
                    elapsed = time.time() - start_time
                    self.get_logger().warn(f"ClearDisplay service call timeout after {elapsed:.2f}s, falling back to topic")
                    self._fallback_to_topic_clear_display(request, response)
            else:
                self.get_logger().warn("ClearDisplay service not available, falling back to topic")
                self._fallback_to_topic_clear_display(request, response)
            
        except Exception as e:
            self.get_logger().error(f"ClearDisplay service call failed: {e}, falling back to topic")
            self._fallback_to_topic_clear_display(request, response)
        
        return response
    
    def _fallback_to_topic_set_display(self, request, response):
        """
        SetDisplay 서비스가 사용 불가능할 때 토픽으로 폴백
        """
        try:
            # 타이틀과 라인들을 조합하여 메시지 생성
            lines = [request.title]
            lines.extend(request.lines)
            msg_text = '\n'.join(lines)
            
            # String 메시지 생성 및 발행
            msg = String()
            msg.data = msg_text
            self.lcd_status_publisher.publish(msg)
            
            response.success = True
            response.message = f"Display updated via topic (fallback): {len(lines)} lines"
            self.get_logger().info(f"Display updated via topic: {msg_text[:50]}...")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"Failed to set display via topic: {e}")
    
    def _fallback_to_topic_clear_display(self, request, response):
        """
        ClearDisplay 서비스가 사용 불가능할 때 토픽으로 폴백
        """
        try:
            # 빈 메시지 발행하여 화면 지우기
            msg = String()
            msg.data = ""
            self.lcd_status_publisher.publish(msg)
            
            response.success = True
            response.message = "Display cleared via topic (fallback)"
            self.get_logger().info("Display cleared via topic")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"Failed to clear display via topic: {e}")
    
    def call_set_layout(self, alignment, layout_mode, margin_top, margin_bottom,
                       margin_left, margin_right, line_spacing, grid_columns, grid_rows):
        """
        SetLayout 서비스를 호출합니다.
        
        Args:
            alignment: 텍스트 정렬 (0: LEFT, 1: CENTER, 2: RIGHT)
            layout_mode: 레이아웃 모드 (0: SINGLE_LINE, 1: MULTI_LINE, 2: GRID)
            margin_top/bottom/left/right: 여백 (픽셀)
            line_spacing: 라인 간격 (픽셀)
            grid_columns/rows: 그리드 모드 시 열/행 수
        
        Returns:
            bool: 성공 여부
        """
        if not self.set_layout_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("SetLayout service not available")
            return False
        
        try:
            request = SetLayout.Request()
            request.alignment = alignment
            request.layout_mode = layout_mode
            request.margin_top = margin_top
            request.margin_bottom = margin_bottom
            request.margin_left = margin_left
            request.margin_right = margin_right
            request.line_spacing = line_spacing
            request.grid_columns = grid_columns
            request.grid_rows = grid_rows
            
            future = self.set_layout_client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
            
            if future.done():
                response = future.result()
                if response.success:
                    self.get_logger().info(f"SetLayout service call successful: {response.message}")
                else:
                    self.get_logger().warn(f"SetLayout service call failed: {response.message}")
                return response.success
            else:
                self.get_logger().warn("SetLayout service call timeout")
                return False
                
        except Exception as e:
            self.get_logger().error(f"Failed to call SetLayout service: {e}")
            return False
    
    def call_set_display_action(self, title, lines, show_timestamp=True, 
                                duration_ms=0, animation_type=0, feedback_callback=None):
        """
        SetDisplayAction 액션을 호출합니다.
        
        Args:
            title: 타이틀 텍스트
            lines: 본문 라인들 (list)
            show_timestamp: 타임스탬프 표시 여부
            duration_ms: 표시 지속 시간 (밀리초, 0이면 무한)
            animation_type: 0: NONE, 1: FADE_IN, 2: SLIDE
            feedback_callback: 피드백 수신 시 호출할 콜백 함수 (optional)
        
        Returns:
            goal_handle 또는 None (실패 시)
        """
        if not self.set_display_action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("SetDisplayAction server not available")
            return None
        
        try:
            goal_msg = SetDisplayAction.Goal()
            goal_msg.title = title
            goal_msg.lines = list(lines) if isinstance(lines, list) else [lines]
            goal_msg.show_timestamp = show_timestamp
            goal_msg.duration_ms = duration_ms
            goal_msg.animation_type = animation_type
            
            self.get_logger().info(f"Sending SetDisplayAction goal: {title}")
            future = self.set_display_action_client.send_goal_async(goal_msg)
            rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
            
            if future.done():
                goal_handle = future.result()
                if goal_handle.accepted:
                    self.get_logger().info("SetDisplayAction goal accepted")
                    
                    # 피드백 수신은 별도로 처리 (비동기)
                    # feedback_callback은 향후 구현 예정
                    
                    return goal_handle
                else:
                    self.get_logger().warn("SetDisplayAction goal rejected")
                    return None
            else:
                self.get_logger().warn("SetDisplayAction send goal timeout")
                return None
                
        except Exception as e:
            self.get_logger().error(f"Failed to send SetDisplayAction goal: {e}")
            return None
    
    def call_scroll_text_action(self, text, scroll_speed_ms=50, direction=0, 
                                repeat_count=1, feedback_callback=None):
        """
        ScrollTextAction 액션을 호출합니다.
        
        Args:
            text: 스크롤할 텍스트
            scroll_speed_ms: 스크롤 속도 (밀리초)
            direction: 0: LEFT, 1: RIGHT, 2: UP, 3: DOWN
            repeat_count: 반복 횟수 (0이면 무한)
            feedback_callback: 피드백 수신 시 호출할 콜백 함수 (optional)
        
        Returns:
            goal_handle 또는 None (실패 시)
        """
        if not self.scroll_text_action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("ScrollTextAction server not available")
            return None
        
        try:
            goal_msg = ScrollText.Goal()
            goal_msg.text = text
            goal_msg.scroll_speed_ms = scroll_speed_ms
            goal_msg.direction = direction
            goal_msg.repeat_count = repeat_count
            
            self.get_logger().info(f"Sending ScrollTextAction goal: {text[:30]}...")
            future = self.scroll_text_action_client.send_goal_async(goal_msg)
            rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
            
            if future.done():
                goal_handle = future.result()
                if goal_handle.accepted:
                    self.get_logger().info("ScrollTextAction goal accepted")
                    
                    # 피드백 수신은 별도로 처리 (비동기)
                    # feedback_callback은 향후 구현 예정
                    
                    return goal_handle
                else:
                    self.get_logger().warn("ScrollTextAction goal rejected")
                    return None
            else:
                self.get_logger().warn("ScrollTextAction send goal timeout")
                return None
                
        except Exception as e:
            self.get_logger().error(f"Failed to send ScrollTextAction goal: {e}")
            return None


def main(args=None):
    rclpy.init(args=args)
    node = LCDControllerServer()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

