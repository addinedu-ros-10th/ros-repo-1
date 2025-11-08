#!/usr/bin/env python3
"""
pinky_lcd_display_controller 서버 노드

이 노드는 pinky_lcd_display 패키지를 제어하기 위한 서비스 서버를 제공합니다.
서비스를 통해 LCD 표시 내용과 스타일을 제어할 수 있습니다.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from pinky_lcd_display_interfaces.srv import SetDisplay, SetStyle, ClearDisplay


class LCDControllerServer(Node):
    """
    LCD 디스플레이 제어 서버
    
    제공하는 서비스:
    - SetDisplay: LCD에 표시할 내용 설정
    - SetStyle: LCD 표시 스타일 설정 (색상, 폰트 등)
    - ClearDisplay: LCD 화면 지우기
    """
    
    def __init__(self):
        super().__init__('lcd_controller_server')
        
        # pinky_lcd_display 패키지의 /lcd/status 토픽에 발행
        self.lcd_status_publisher = self.create_publisher(
            String,
            '/lcd/status',
            10
        )
        
        # 현재 스타일 설정 저장
        self.current_style = {
            'bg_color': (0, 0, 0),
            'title_color': (0, 255, 0),
            'body_color': (255, 255, 255),
            'timestamp_color': (100, 100, 255),
            'title_font_size': 20,
            'body_font_size': 18,
            'font_path': '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        }
        
        # 서비스 서버 생성
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
    
    def set_display_callback(self, request, response):
        """
        SetDisplay 서비스 콜백
        LCD에 표시할 내용을 설정합니다.
        """
        try:
            # 타이틀과 라인들을 조합하여 메시지 생성
            lines = [request.title]
            lines.extend(request.lines)
            
            # 타임스탬프 표시 여부에 따라 처리
            # (현재 pinky_lcd_display는 footer_timestamp 파라미터로 제어)
            # 여기서는 단순히 텍스트만 전송
            
            msg_text = '\n'.join(lines)
            
            # String 메시지 생성 및 발행
            msg = String()
            msg.data = msg_text
            self.lcd_status_publisher.publish(msg)
            
            response.success = True
            response.message = f"Display updated: {len(lines)} lines"
            self.get_logger().info(f"Display updated: {msg_text[:50]}...")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"Failed to set display: {e}")
        
        return response
    
    def set_style_callback(self, request, response):
        """
        SetStyle 서비스 콜백
        LCD 표시 스타일을 설정합니다.
        
        주의: 현재 pinky_lcd_display 패키지는 스타일을 동적으로 변경하는 기능이 없습니다.
        이 서비스는 스타일 설정을 저장만 하고, 실제 적용은 pinky_lcd_display 패키지 수정이 필요합니다.
        """
        try:
            # 스타일 설정 저장
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
            
            response.success = True
            response.message = "Style settings saved (Note: requires pinky_lcd_display package modification for full support)"
            self.get_logger().info(f"Style updated: {self.current_style}")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"Failed to set style: {e}")
        
        return response
    
    def clear_display_callback(self, request, response):
        """
        ClearDisplay 서비스 콜백
        LCD 화면을 지웁니다.
        """
        try:
            # 빈 메시지 발행하여 화면 지우기
            msg = String()
            msg.data = ""
            self.lcd_status_publisher.publish(msg)
            
            response.success = True
            response.message = "Display cleared"
            self.get_logger().info("Display cleared")
            
        except Exception as e:
            response.success = False
            response.message = f"Error: {str(e)}"
            self.get_logger().error(f"Failed to clear display: {e}")
        
        return response


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

