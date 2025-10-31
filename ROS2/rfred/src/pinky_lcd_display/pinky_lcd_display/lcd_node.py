# pinky_lcd_display/lcd_node.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from .lcd_manager import LCDDisplayManager


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

        # Subscriber 등록
        self.sub = self.create_subscription(
            String,
            '/lcd/status',   # 토픽 이름
            self.status_callback,
            10
        )

        self.get_logger().info("pinky_lcd_node started, listening on /lcd/status")

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

        # LCD 업데이트
        self.lcd_manager.show_status(
            title=title,
            lines=body_lines,
            footer_timestamp=True,
        )

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
