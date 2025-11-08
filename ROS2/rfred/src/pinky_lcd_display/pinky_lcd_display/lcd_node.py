# pinky_lcd_display/lcd_node.py
import rclpy
import time
from rclpy.node import Node
from std_msgs.msg import String

from .lcd_manager import LCDDisplayManager

# 인터페이스 import
try:
    from pinky_lcd_display_interfaces.srv import SetDisplay, SetStyle, ClearDisplay, SetLayout
    from pinky_lcd_display_interfaces.msg import LCDStatus, LCDEvent
    from pinky_lcd_display_interfaces.action import SetDisplay as SetDisplayAction
    from pinky_lcd_display_interfaces.action import ScrollText
    from rclpy.action import ActionServer
    INTERFACES_AVAILABLE = True
except ImportError:
    INTERFACES_AVAILABLE = False
    print("Warning: pinky_lcd_display_interfaces not available. Service/action features will be disabled.")


class LCDDisplayNode(Node):
    """
    이 노드는 /lcd/status 토픽(String) 을 구독해서
    그 내용을 LCD에 표시한다.
    메시지는 예를 들면:
    "Battery:78%\nMode:MOVING\nWaypoint:2/4"
    이런 식으로 여러 줄 가능.
    """

    def __init__(self):
        super().__init__('pinky_lcd_node')

        # LCD 매니저 준비
        self.lcd_manager = LCDDisplayManager()

        # 현재 상태 추적
        self.current_title = "Status"
        self.current_lines = []
        self.show_timestamp = True
        self.current_display_mode = 0  # 0: NORMAL, 1: SCROLL, 2: ANIMATION

        # Subscriber 등록 (기존 토픽 구독 유지)
        self.sub = self.create_subscription(
            String,
            '/lcd/status',   # 토픽 이름
            self.status_callback,
            10
        )

        # 서비스 서버 등록 (인터페이스가 사용 가능한 경우)
        if INTERFACES_AVAILABLE:
            # SetDisplay 서비스
            self.set_display_srv = self.create_service(
                SetDisplay,
                'lcd_controller/set_display',
                self.set_display_callback
            )
            
            # SetStyle 서비스
            self.set_style_srv = self.create_service(
                SetStyle,
                'lcd_controller/set_style',
                self.set_style_callback
            )
            
            # ClearDisplay 서비스
            self.clear_display_srv = self.create_service(
                ClearDisplay,
                'lcd_controller/clear_display',
                self.clear_display_callback
            )
            
            # SetLayout 서비스
            self.set_layout_srv = self.create_service(
                SetLayout,
                'lcd_controller/set_layout',
                self.set_layout_callback
            )
            
            # 상태 토픽 Publisher
            self.status_pub = self.create_publisher(
                LCDStatus,
                '/lcd_controller/status',
                10
            )
            
            # 이벤트 토픽 Publisher
            self.event_pub = self.create_publisher(
                LCDEvent,
                '/lcd_controller/events',
                10
            )
            
            # 상태 발행 타이머 (1Hz)
            self.status_timer = self.create_timer(1.0, self.publish_status)
            
            # 액션 서버 등록
            self.set_display_action_server = ActionServer(
                self,
                SetDisplayAction,
                'lcd_controller/set_display_action',
                self.set_display_action_execute_callback
            )
            
            self.scroll_text_action_server = ActionServer(
                self,
                ScrollText,
                'lcd_controller/scroll_text_action',
                self.scroll_text_action_execute_callback
            )
            
            self.get_logger().info("pinky_lcd_node started with service/action support")
        else:
            self.get_logger().info("pinky_lcd_node started, listening on /lcd/status (service/action disabled)")

    def status_callback(self, msg: String):
        """
        토픽으로 들어온 문자열을 LCD에 반영한다.
        """
        self.get_logger().info(f"LCD update request:\n{msg.data}")

        # LCD에 넣을 lines 구성
        # 예: "Battery:78%\nMode:MOVING\nWaypoint:2/4"
        lines = msg.data.split("\n")

        # 1행(타이틀)은 따로 빼고 싶다면 여기서 가공할 수 있음.
        # 지금은 첫 줄을 타이틀로 쓰고 나머지를 body로 쓰자.
        if len(lines) > 0:
            title = lines[0][:20]  # 너무 길면 잘라
            body_lines = lines[1:]
        else:
            title = "Status"
            body_lines = []

        # 상태 업데이트
        self.current_title = title
        self.current_lines = body_lines
        self.show_timestamp = True
        self.current_display_mode = 0  # NORMAL

        # LCD 업데이트
        self.lcd_manager.show_status(
            title=title,
            lines=body_lines,
            footer_timestamp=True,
        )
        
        # 이벤트 발행
        if INTERFACES_AVAILABLE:
            self.publish_event(0, "Display started via topic")  # DISPLAY_STARTED

    def set_display_callback(self, request, response):
        """SetDisplay 서비스 콜백"""
        try:
            self.current_title = request.title
            self.current_lines = list(request.lines)
            self.show_timestamp = request.show_timestamp
            self.current_display_mode = 0  # NORMAL
            
            self.lcd_manager.show_status(
                title=request.title,
                lines=list(request.lines),
                footer_timestamp=request.show_timestamp,
            )
            
            response.success = True
            response.message = "Display updated successfully"
            
            # 이벤트 발행
            if INTERFACES_AVAILABLE:
                self.publish_event(0, f"Display started: {request.title}")  # DISPLAY_STARTED
            
            self.get_logger().info(f"SetDisplay service called: {request.title}")
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"SetDisplay service error: {e}")
            if INTERFACES_AVAILABLE:
                self.publish_event(2, f"Error: {str(e)}")  # ERROR
        
        return response
    
    def set_style_callback(self, request, response):
        """SetStyle 서비스 콜백"""
        try:
            self.lcd_manager.set_style(
                request.bg_color_r, request.bg_color_g, request.bg_color_b,
                request.title_color_r, request.title_color_g, request.title_color_b,
                request.body_color_r, request.body_color_g, request.body_color_b,
                request.timestamp_color_r, request.timestamp_color_g, request.timestamp_color_b,
                request.title_font_size, request.body_font_size, request.font_path
            )
            
            # 현재 표시 내용을 새 스타일로 다시 렌더링
            self.lcd_manager.show_status(
                title=self.current_title,
                lines=self.current_lines,
                footer_timestamp=self.show_timestamp,
            )
            
            response.success = True
            response.message = "Style updated successfully"
            
            self.get_logger().info("SetStyle service called")
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"SetStyle service error: {e}")
            if INTERFACES_AVAILABLE:
                self.publish_event(2, f"Error: {str(e)}")  # ERROR
        
        return response
    
    def clear_display_callback(self, request, response):
        """ClearDisplay 서비스 콜백"""
        try:
            # 빈 화면 표시
            self.current_title = ""
            self.current_lines = []
            self.show_timestamp = False
            
            self.lcd_manager.show_status(
                title="",
                lines=[],
                footer_timestamp=False,
            )
            
            response.success = True
            response.message = "Display cleared successfully"
            
            # 이벤트 발행
            if INTERFACES_AVAILABLE:
                self.publish_event(3, "Display cleared")  # CLEARED
            
            self.get_logger().info("ClearDisplay service called")
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"ClearDisplay service error: {e}")
            if INTERFACES_AVAILABLE:
                self.publish_event(2, f"Error: {str(e)}")  # ERROR
        
        return response
    
    def set_layout_callback(self, request, response):
        """SetLayout 서비스 콜백"""
        try:
            self.lcd_manager.set_layout(
                request.alignment,
                request.layout_mode,
                request.margin_top,
                request.margin_bottom,
                request.margin_left,
                request.margin_right,
                request.line_spacing,
                request.grid_columns,
                request.grid_rows
            )
            
            # 현재 표시 내용을 새 레이아웃으로 다시 렌더링
            self.lcd_manager.show_status(
                title=self.current_title,
                lines=self.current_lines,
                footer_timestamp=self.show_timestamp,
            )
            
            response.success = True
            response.message = "Layout updated successfully"
            
            self.get_logger().info("SetLayout service called")
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"SetLayout service error: {e}")
            if INTERFACES_AVAILABLE:
                self.publish_event(2, f"Error: {str(e)}")  # ERROR
        
        return response
    
    def publish_status(self):
        """상태 토픽 발행"""
        if not INTERFACES_AVAILABLE:
            return
        
        try:
            msg = LCDStatus()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.is_active = self.lcd_manager.lcd is not None
            msg.current_title = self.current_title
            msg.current_lines = list(self.current_lines)
            msg.show_timestamp = self.show_timestamp
            msg.last_update_time = self.get_clock().now().nanoseconds
            msg.display_mode = self.current_display_mode
            msg.error_code = 0
            msg.error_message = ""
            
            self.status_pub.publish(msg)
        except Exception as e:
            self.get_logger().error(f"Error publishing status: {e}")
    
    def publish_event(self, event_type, message):
        """이벤트 토픽 발행"""
        if not INTERFACES_AVAILABLE:
            return
        
        try:
            msg = LCDEvent()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.event_type = event_type
            msg.timestamp = self.get_clock().now().nanoseconds
            msg.message = message
            
            self.event_pub.publish(msg)
        except Exception as e:
            self.get_logger().error(f"Error publishing event: {e}")
    
    def set_display_action_execute_callback(self, goal_handle):
        """SetDisplayAction 액션 execute 콜백"""
        if not INTERFACES_AVAILABLE:
            goal_handle.abort()
            result = SetDisplayAction.Result()
            result.success = False
            result.message = "Interfaces not available"
            return result
        
        try:
            goal = goal_handle.goal
            start_time = self.get_clock().now()
            
            # 애니메이션 효과 적용
            if goal.animation_type == 1:  # FADE_IN
                self.lcd_manager.show_status_with_animation(
                    title=goal.title,
                    lines=list(goal.lines),
                    footer_timestamp=goal.show_timestamp,
                    animation_type='fade_in'
                )
            elif goal.animation_type == 2:  # SLIDE
                self.lcd_manager.show_status_with_animation(
                    title=goal.title,
                    lines=list(goal.lines),
                    footer_timestamp=goal.show_timestamp,
                    animation_type='slide'
                )
            else:  # NONE
                self.lcd_manager.show_status(
                    title=goal.title,
                    lines=list(goal.lines),
                    footer_timestamp=goal.show_timestamp,
                )
            
            # 상태 업데이트
            self.current_title = goal.title
            self.current_lines = list(goal.lines)
            self.show_timestamp = goal.show_timestamp
            self.current_display_mode = 2 if goal.animation_type > 0 else 0
            
            # 이벤트 발행
            self.publish_event(5, f"Animation started: {goal.title}")  # ANIMATION_STARTED
            
            # duration_ms가 0이 아니면 지정된 시간 후 자동으로 화면 지움
            if goal.duration_ms > 0:
                # 피드백 발행
                feedback_msg = SetDisplayAction.Feedback()
                feedback_msg.elapsed_ms = 0
                feedback_msg.progress_percent = 0
                feedback_msg.status_message = "Displaying..."
                goal_handle.publish_feedback(feedback_msg)
                
                # 타이머를 사용하여 피드백 발행 및 자동 종료
                elapsed_ms = 0
                feedback_interval = 100  # 100ms마다 피드백 발행
                
                while elapsed_ms < goal.duration_ms:
                    # 취소 요청 확인
                    if goal_handle.is_cancel_requested:
                        goal_handle.canceled()
                        result = SetDisplayAction.Result()
                        result.success = False
                        result.message = "Action canceled"
                        return result
                    
                    # 피드백 발행
                    feedback_msg.elapsed_ms = elapsed_ms
                    feedback_msg.progress_percent = int((elapsed_ms / goal.duration_ms) * 100)
                    feedback_msg.status_message = f"Displaying... {feedback_msg.progress_percent}%"
                    goal_handle.publish_feedback(feedback_msg)
                    
                    # 대기
                    time.sleep(feedback_interval / 1000.0)
                    elapsed_ms += feedback_interval
                
                # 자동으로 화면 지우기
                self.lcd_manager.show_status(
                    title="",
                    lines=[],
                    footer_timestamp=False,
                )
                self.current_title = ""
                self.current_lines = []
                self.publish_event(6, "Animation ended")  # ANIMATION_ENDED
                self.publish_event(1, "Display ended")  # DISPLAY_ENDED
            
            # Result 설정
            result = SetDisplayAction.Result()
            result.success = True
            result.message = "Display action completed successfully"
            end_time = self.get_clock().now()
            actual_duration = (end_time - start_time).nanoseconds / 1_000_000  # 밀리초로 변환
            result.actual_duration_ms = int(actual_duration)
            
            return result
            
        except Exception as e:
            self.get_logger().error(f"SetDisplayAction error: {e}")
            self.publish_event(2, f"Error: {str(e)}")  # ERROR
            result = SetDisplayAction.Result()
            result.success = False
            result.message = f"Error: {str(e)}"
            return result
    
    def scroll_text_action_execute_callback(self, goal_handle):
        """ScrollTextAction 액션 execute 콜백"""
        if not INTERFACES_AVAILABLE:
            goal_handle.abort()
            result = ScrollText.Result()
            result.success = False
            result.message = "Interfaces not available"
            return result
        
        try:
            goal = goal_handle.goal
            start_time = self.get_clock().now()
            
            # 스크롤 텍스트 표시
            self.lcd_manager.show_scroll_text(
                text=goal.text,
                direction=goal.direction,
                scroll_speed_ms=goal.scroll_speed_ms,
                repeat_count=goal.repeat_count,
                callback=lambda pos, progress: self._scroll_feedback(goal_handle, pos, progress)
            )
            
            # Result 설정
            result = ScrollText.Result()
            result.success = True
            result.message = "Scroll text completed successfully"
            end_time = self.get_clock().now()
            total_duration = (end_time - start_time).nanoseconds / 1_000_000  # 밀리초로 변환
            result.total_scroll_time_ms = int(total_duration)
            
            return result
            
        except Exception as e:
            self.get_logger().error(f"ScrollTextAction error: {e}")
            self.publish_event(2, f"Error: {str(e)}")  # ERROR
            result = ScrollText.Result()
            result.success = False
            result.message = f"Error: {str(e)}"
            return result
    
    def _scroll_feedback(self, goal_handle, current_position, progress_percent):
        """스크롤 피드백 발행"""
        if not INTERFACES_AVAILABLE:
            return
        
        try:
            feedback_msg = ScrollText.Feedback()
            feedback_msg.current_position = current_position
            feedback_msg.progress_percent = progress_percent
            goal_handle.publish_feedback(feedback_msg)
        except Exception as e:
            self.get_logger().error(f"Error publishing scroll feedback: {e}")

    def destroy_node(self):
        # 노드 종료 시 LCD close
        try:
            self.lcd_manager.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = LCDDisplayNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
