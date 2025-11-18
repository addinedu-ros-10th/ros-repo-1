# pinky_lcd_display/test_publisher_node.py
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time


class LCDTestPublisher(Node):
    def __init__(self):
        super().__init__('lcd_test_publisher')
        self.pub = self.create_publisher(String, '/lcd/status', 10)

        # 타이머로 주기 발행 (1초마다)
        self.timer = self.create_timer(1.0, self.timer_cb)
        self._tick = 0

    def timer_cb(self):
        self._tick += 1
        battery = 80 - self._tick
        mode = "MOVING" if self._tick % 2 == 0 else "IDLE"
        wp = f"{(self._tick % 4)+1}/4"

        msg_text = (
            "Pinky Status\n"
            f"Battery: {battery}%\n"
            f"Mode: {mode}\n"
            f"WP: {wp}"
        )
        msg = String()
        msg.data = msg_text
        self.get_logger().info(f"Publishing:\n{msg.data}")
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = LCDTestPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
