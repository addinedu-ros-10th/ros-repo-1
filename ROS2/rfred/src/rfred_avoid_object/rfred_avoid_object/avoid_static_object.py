#!/usr/bin/env python3
import time
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class AvoidStaticObject(Node):
    def __init__(self):
        super().__init__("avoid_static_object")

        # 라이다
        self.sub_scan = self.create_subscription(
            LaserScan, "/scan", self.cb_scan_input, 10
        )

        # 제어 입력값 - (SUB topic /cmd_vel_raw)
        self.cmd_vel_raw = self.create_subscription(
            Twist, "/cmd_vel_raw", self.cmd_vel_raw_mask, 10
        )

        # 제어 출력값 - (PUB topic /cmd_vel)
        self.pub_cmd = self.create_publisher(
            Twist, "/cmd_vel_static", 10
        )

        # 라이다 임계값
        self.threshold = 0.10  # 10cm 이하 위험 감지

        # 정지 유지 로직
        self.stop_duration = 10.0  # 10초 정지
        self.stop_until = 0.0      # 정지 유지 종료 시각

        # teleop 명령 저장
        self.mask_cmd = Twist()

        self.get_logger().info("정적 장애물 중돌 방지 : 10cm 이하 감지 → 10초 정지")

    # ----------------------------------------
    # ① 라이다 콜백
    # ----------------------------------------
    def cb_scan_input(self, msg):
        now = time.time()

        arr = np.array(msg.ranges, dtype=float)
        valid = arr[
            (arr != np.inf) &
            (arr >= msg.range_min) &
            (arr <= msg.range_max)
        ]

        if valid.size == 0:
            return

        min_val = valid.min()

        # 10cm 이하 → 즉시 10초 정지 예약
        if min_val <= self.threshold:
            self.stop_until = now + self.stop_duration
            self.get_logger().warn(
                f"근접 감지: {min_val:.3f} m → 10초 정지 유지"
            )

        # 상태 반영
        self.publish_cmd(now)

    # 제어 입력값 - (SUB topic /cmd_vel_raw)
    def cmd_vel_raw_mask(self, msg):
        self.mask_cmd = msg
        self.publish_cmd(time.time())

    # 제어 출력값 - (PUB topic /cmd_vel)
    def publish_cmd(self, now):
        out = Twist()

        if now < self.stop_until:
            # 정지 유지 모드
            out.linear.x = 0.0
            out.angular.z = 0.0
        else:
            # 정상 주행 (pass-through)
            out = self.mask_cmd

        self.pub_cmd.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = AvoidStaticObject()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
