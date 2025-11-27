import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import numpy as np
from geometry_msgs.msg import Twist
import time


class AvoidMovingObject(Node):
    def __init__(self):
        super().__init__("avoid_moving_object")

        self.sub = self.create_subscription(
            LaserScan, "/scan", self.cb_scan_input, 10
        )

        # 제어 입력값 - (SUB topic /cmd_vel_raw)
        self.cmd_vel_raw = self.create_subscription(
            Twist, "/cmd_vel_static", self.cmd_vel_raw_mask, 10
        )

        self.pub_cmd_vel = self.create_publisher(
            Twist, "/cmd_vel", 10
        )

        # 이전 전체 스캔 저장
        self.prev_ranges = None          # full length
        self.prev_xy_x = None            # full length
        self.prev_xy_y = None            # full length
        self.prev_time = None

        # 설정값
        self.move_threshold = 0.03       # 5cm 이상 변화 → 움직임
        self.cluster_distance = 0.15     # 15cm 이하 거리 차이면 같은 클러스터
        self.min_cluster_size = 5        # 클러스터 최소 크기
        self.print_interval = 1.0
        self.last_print = 0.0
        self.stop_until = 0.0           # 처음에는 항상 주행 허용
        self.stop_duration = 10.0       # 동적 장애물 근접 시 정지 유지 시간(초)

        # 마스킹한 Twist 자료 저장
        self.mask_cmd = Twist()

        self.get_logger().info("동적 장애물 감지 및 트래킹 시작")

    # 제어 입력값 - (SUB topic /cmd_vel_raw)
    def cmd_vel_raw_mask(self, msg):
        self.mask_cmd = msg
        self.publish_cmd(time.time()) # 현재 시간 기준으로 토픽 발행

    # 제어 출력값 - (PUB topic /cmd_vel)
    def publish_cmd(self, now: float):
        out = Twist()

        if now < self.stop_until:
            # 정지 유지 모드
            out.linear.x = 0.0
            out.angular.z = 0.0
        else:
            # 정상 주행 (상위 /cmd_vel_raw를 그대로 통과)
            out = self.mask_cmd

        self.pub_cmd_vel.publish(out)

    # 라이다 콜백
    def cb_scan_input(self, msg):
        now = time.time()
        ranges = np.array(msg.ranges, dtype=float)
        N = len(ranges)

        # 유효 빔 필터링
        valid_mask = (
            (ranges != np.inf) &
            (ranges >= msg.range_min) &
            (ranges <= msg.range_max)
        )

        # ranges 전처리 (inf → nan)
        ranges = np.array(msg.ranges, dtype=float)
        ranges[~np.isfinite(ranges)] = np.nan

        if self.prev_ranges is None:
            # prev 배열 전체 초기화
            self.prev_ranges = ranges.copy()
            self.prev_xy_x = (ranges * np.cos(np.linspace(msg.angle_min, msg.angle_max, N))).copy()
            self.prev_xy_y = (ranges * np.sin(np.linspace(msg.angle_min, msg.angle_max, N))).copy()
            self.prev_time = now
            return

        # 변화량(diff), 전체 빔 기준 계산
        diff = np.abs(ranges - self.prev_ranges)
        moving_mask = valid_mask & (diff > self.move_threshold)
        moving_idx = np.where(moving_mask)[0]

        if len(moving_idx) == 0:
            # 다음 프레임 대비 저장
            self.save_prev(msg, ranges, N)
            return

        # 각도
        angles = msg.angle_min + moving_idx * msg.angle_increment


        # 현재 xy
        # angles = np.linspace(msg.angle_min, msg.angle_max, N) # inf
        curr_x = ranges[moving_idx] * np.cos(angles)
        curr_y = ranges[moving_idx] * np.sin(angles)

        # 이전 xy (full array 기준)
        prev_x = self.prev_xy_x[moving_idx]
        prev_y = self.prev_xy_y[moving_idx]

        dt = now - self.prev_time if self.prev_time else 0.1
        vx = (curr_x - prev_x) / dt
        vy = (curr_y - prev_y) / dt
        speed = np.sqrt(vx**2 + vy**2)

        # 클러스터링
        clusters = []
        current_cluster = [0]

        for i in range(1, len(moving_idx)):
            # 인접 빔이고 거리 값이 비슷할 때 같은 클러스터의 픽셀
            if (moving_idx[i] == moving_idx[i - 1] + 1) and \
               (abs(ranges[moving_idx[i]] - ranges[moving_idx[i - 1]]) < self.cluster_distance):
                current_cluster.append(i)
            else:
                clusters.append(current_cluster.copy())
                current_cluster = [i]

        clusters.append(current_cluster)


        # 최소 크기 이상 클러스터만 추출
        big_clusters = [c for c in clusters if len(c) >= self.min_cluster_size]

        # print(f"{big_clusters} : {now - self.last_print >= self.print_interval}")

        # Notebook 출력
        if len(big_clusters) > 0 and (now - self.last_print >= self.print_interval):
            for idx, cluster in enumerate(big_clusters):
                ids = cluster

                cx = curr_x[ids]
                cy = curr_y[ids]
                cspeed = speed[ids]

                centroid_x = np.mean(cx)
                centroid_y = np.mean(cy)
                mean_speed = np.mean(cspeed)

                # 클러스터 중심점의 로봇 기준 거리
                cluster_dist = np.sqrt(centroid_x**2 + centroid_y**2)

                # 20cm 이하 접근 → 정지 명령
                if cluster_dist < 0.30:
                    self.emergency_stop()

                log = (
                    f"다른 로봇 감지: {cluster_dist:.3f} m → 10초 정지 유지\n"
                    f"[Cluster {idx}]\n"
                    f" - beam count : {len(ids)}\n"
                    f" - centroid : ({centroid_x:.2f}, {centroid_y:.2f}) m\n"
                    f" - mean speed : {mean_speed:.2f} m/s\n"
                    f" - cluster_dist : {cluster_dist:.2f} m\n"
                )
                self.get_logger().warn(log)
            self.last_print = now

        # 현재 프레임 저장
        self.save_prev(msg, ranges, N)

    # 이전 프레임 저장 (full array로 저장)
    def save_prev(self, msg, ranges, N):
        angles = np.linspace(msg.angle_min, msg.angle_max, N)
        self.prev_ranges = ranges.copy()
        self.prev_xy_x = (ranges * np.cos(angles)).copy()
        self.prev_xy_y = (ranges * np.sin(angles)).copy()
        self.prev_time = time.time()
    
    # def emergency_stop(self):
    #     from geometry_msgs.msg import Twist
    #     stop = Twist()
    #     stop.linear.x = 0.0
    #     stop.angular.z = 0.0
    #     self.pub_cmd_vel.publish(stop)

    def emergency_stop(self):
        # 10초 정지 유지 예약
        now = time.time()
        self.stop_until = now + self.stop_duration

        self.get_logger().warn(
            f"동적 장애물 근접 감지 → {self.stop_duration:.1f}초 정지 유지 예약"
        )

        # 바로 한 번 상태를 반영해 현재 속도도 0으로 보냄
        self.publish_cmd(now)

def main():
    rclpy.init()
    node = AvoidMovingObject()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
