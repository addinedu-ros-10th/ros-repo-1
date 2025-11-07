#!/usr/bin/env python3
"""
Pinky 로봇용 State Machine 모니터링 노드

이 파일은 qmonitor_state_machine.py를 기반으로 하되,
pinky 로봇의 odom 토픽을 사용하도록 수정되었습니다.

주요 변경사항:
- 'turtle1/pose' -> 'odom' (nav_msgs/Odometry)
- turtlesim.msg.Pose -> nav_msgs/Odometry에서 변환
- 맵 크기 파라미터 추가 (실제 세트 크기 설정 가능)
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry  # Pinky 로봇의 odom 메시지 타입
from geometry_msgs.msg import Pose  # goal_pose용
from std_msgs.msg import String
from rcl_interfaces.msg import SetParametersResult
from tf_transformations import euler_from_quaternion  # 쿼터니언을 오일러 각으로 변환
import threading
import math
import sys

# PyQt5와 matplotlib 임포트
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout
from PyQt5.QtCore import QTimer
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import FancyBboxPatch  # 라운드 테두리 처리를 위해


def odom_to_pose(odom_msg):
    """
    nav_msgs/Odometry 메시지를 SimplePose 형식으로 변환
    
    Args:
        odom_msg: nav_msgs/Odometry 메시지
        
    Returns:
        SimplePose 객체 (x, y, theta 속성 포함)
    """
    class SimplePose:
        def __init__(self, x, y, theta):
            self.x = x
            self.y = y
            self.theta = theta
    
    # Odometry 메시지에서 위치 추출
    x = odom_msg.pose.pose.position.x
    y = odom_msg.pose.pose.position.y
    
    # 쿼터니언을 오일러 각으로 변환하여 theta 얻기
    orientation = odom_msg.pose.pose.orientation
    _, _, theta = euler_from_quaternion([
        orientation.x,
        orientation.y,
        orientation.z,
        orientation.w
    ])
    
    return SimplePose(x, y, theta)


# ROS 노드: Pinky 로봇의 현재 pose, goal_pose, state 구독 및 goal_pose 발행
class PinkyMonitor(Node):
    def __init__(self):
        super().__init__('pinky_monitor')
        self.turtle_pose = None      # 현재 로봇의 pose (SimplePose 형식)
        self.goal_pose = None        # 현재 goal_pose
        self.current_state = None    # 현재 상태 (문자열)
        self.guide_line_start = None # 가이드 선의 시작점 (로봇의 pose)

        # 토픽 이름 파라미터
        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('goal_pose_topic', 'goal_pose')
        self.declare_parameter('state_topic', 'state')

        odom_topic = self.get_parameter('odom_topic').value
        goal_pose_topic = self.get_parameter('goal_pose_topic').value
        state_topic = self.get_parameter('state_topic').value

        # 구독자 설정
        self.create_subscription(Odometry, odom_topic, self.odom_callback, 10)
        self.create_subscription(Pose, goal_pose_topic, self.goal_pose_callback, 10)
        self.create_subscription(String, state_topic, self.state_callback, 10)

        # 퍼블리셔: 마우스 드래그로 새 goal_pose 발행
        self.goal_pub = self.create_publisher(Pose, goal_pose_topic, 10)

    def odom_callback(self, msg):
        """odom 토픽에서 현재 위치 정보 수신"""
        self.turtle_pose = odom_to_pose(msg)

    def goal_pose_callback(self, msg):
        """goal_pose 토픽에서 목표 위치 수신"""
        # geometry_msgs/Pose를 SimplePose 형식으로 변환
        class SimplePose:
            def __init__(self, x, y, theta):
                self.x = x
                self.y = y
                self.theta = theta
        
        # 쿼터니언을 오일러 각으로 변환
        orientation = msg.orientation
        _, _, theta = euler_from_quaternion([
            orientation.x,
            orientation.y,
            orientation.z,
            orientation.w
        ])
        
        self.goal_pose = SimplePose(msg.position.x, msg.position.y, theta)
        if self.turtle_pose is not None:
            self.guide_line_start = (self.turtle_pose.x, self.turtle_pose.y)
            self.get_logger().info(
                f"Guide line set from ({self.turtle_pose.x:.2f}, {self.turtle_pose.y:.2f}) to ({msg.position.x:.2f}, {msg.position.y:.2f})"
            )

    def state_callback(self, msg):
        """state 토픽에서 현재 상태 수신"""
        self.current_state = msg.data


def ros_spin(node):
    """ROS 스핀을 별도 스레드에서 실행하기 위한 함수"""
    rclpy.spin(node)


class MainWindow(QMainWindow):
    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setWindowTitle("Pinky Monitor with Goal-Drag and State Display")

        # ============================================================
        # 실제 세트 크기 설정: 맵 크기 파라미터 선언 및 초기화
        # ============================================================
        # ROS2 파라미터를 통해 맵의 실제 크기를 설정할 수 있도록 함
        # 기본값은 3.443m x 2.25m (344.3cm x 225cm)
        self.node.declare_parameter('map_width', 3.443)   # 맵 너비 파라미터 선언
        self.node.declare_parameter('map_height', 2.25)    # 맵 높이 파라미터 선언
        
        # 선언된 파라미터 값을 가져와서 인스턴스 변수에 저장
        self.map_width = self.node.get_parameter('map_width').value
        self.map_height = self.node.get_parameter('map_height').value
        
        # 파라미터 변경 시 맵 크기를 동적으로 업데이트하기 위한 콜백 등록
        self.node.add_on_set_parameters_callback(self.parameter_callback)

        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # [좌측] 로봇 맵 영역
        self.figure_map = Figure()
        self.canvas_map = FigureCanvas(self.figure_map)
        self.ax_map = self.figure_map.add_subplot(111)
        main_layout.addWidget(self.canvas_map, stretch=3)

        # [우측] 상태 표시 영역 (세로 크기 3x6)
        self.figure_state = Figure(figsize=(3, 6))
        self.canvas_state = FigureCanvas(self.figure_state)
        self.ax_state = self.figure_state.add_subplot(111)
        main_layout.addWidget(self.canvas_state, stretch=1)

        self.drag_start = None
        self.drag_current = None

        self.canvas_map.mpl_connect('button_press_event', self.on_mouse_press)
        self.canvas_map.mpl_connect('motion_notify_event', self.on_mouse_move)
        self.canvas_map.mpl_connect('button_release_event', self.on_mouse_release)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all)
        self.timer.start(100)

        # 컨트롤러에서 발행하는 상태와 일치 (상태 목록)
        self.state_list = ["RotateToGoal", "MoveToGoal", "RotateToFinal", "GoalReached"]

    def parameter_callback(self, params):
        """
        파라미터 변경 시 호출되는 콜백 함수
        런타임에 'ros2 param set' 명령으로 map_width나 map_height를 변경하면
        이 함수가 호출되어 맵 크기를 동적으로 업데이트함
        
        Args:
            params: 변경된 파라미터들의 리스트
            
        Returns:
            SetParametersResult: 파라미터 설정 결과 (성공 여부)
        """
        for param in params:
            if param.name == 'map_width':
                self.map_width = param.value
                self.node.get_logger().info(f"맵 너비가 업데이트되었습니다: {param.value}")
            elif param.name == 'map_height':
                self.map_height = param.value
                self.node.get_logger().info(f"맵 높이가 업데이트되었습니다: {param.value}")
        return SetParametersResult(successful=True)

    def on_mouse_press(self, event):
        """마우스 버튼 누름 이벤트 처리"""
        if event.button == 1 and event.inaxes == self.ax_map:
            self.drag_start = (event.xdata, event.ydata)
            self.drag_current = (event.xdata, event.ydata)

    def on_mouse_move(self, event):
        """마우스 이동 이벤트 처리"""
        if self.drag_start is not None and event.inaxes == self.ax_map:
            self.drag_current = (event.xdata, event.ydata)

    def on_mouse_release(self, event):
        """마우스 버튼 놓음 이벤트 처리 - goal_pose 발행"""
        if event.button == 1 and self.drag_start is not None and event.inaxes == self.ax_map:
            if self.drag_current is not None:
                dx = self.drag_current[0] - self.drag_start[0]
                dy = self.drag_current[1] - self.drag_start[1]
                theta = math.atan2(dy, dx)
            else:
                theta = 0.0

            # geometry_msgs/Pose 메시지 생성
            goal_msg = Pose()
            goal_msg.position.x = self.drag_start[0]
            goal_msg.position.y = self.drag_start[1]
            goal_msg.position.z = 0.0
            
            # 오일러 각을 쿼터니언으로 변환
            from tf_transformations import quaternion_from_euler
            q = quaternion_from_euler(0, 0, theta)
            goal_msg.orientation.x = q[0]
            goal_msg.orientation.y = q[1]
            goal_msg.orientation.z = q[2]
            goal_msg.orientation.w = q[3]
            
            self.node.goal_pub.publish(goal_msg)
            self.node.get_logger().info(
                f"Published new goal: x={goal_msg.position.x:.2f}, y={goal_msg.position.y:.2f}, theta={theta:.2f}"
            )
            self.drag_start = None
            self.drag_current = None

    def update_all(self):
        """모든 화면 업데이트"""
        self.update_map()
        self.update_state_display()

    def update_map(self):
        """맵 화면 업데이트"""
        self.ax_map.clear()
        # 실제 세트 크기에 맞춰 맵 범위 설정
        self.ax_map.set_xlim(0, self.map_width)
        self.ax_map.set_ylim(0, self.map_height)
        self.ax_map.set_aspect('equal')
        self.ax_map.grid(True)
        self.ax_map.set_title("Pinky Robot Map")

        # 현재 로봇 pose 표시 (파란 화살표 및 점)
        if self.node.turtle_pose is not None:
            x = self.node.turtle_pose.x
            y = self.node.turtle_pose.y
            theta = self.node.turtle_pose.theta
            arrow_len = 0.1  # 로봇 크기에 맞게 조정
            dx = arrow_len * math.cos(theta)
            dy = arrow_len * math.sin(theta)
            self.ax_map.arrow(x, y, dx, dy, head_width=0.05, head_length=0.05, fc='blue', ec='blue')
            self.ax_map.plot(x, y, 'bo', markersize=8)

        # 목표 pose 표시 (빨간 점 및 화살표)
        if self.node.goal_pose is not None:
            gx = self.node.goal_pose.x
            gy = self.node.goal_pose.y
            gtheta = self.node.goal_pose.theta
            self.ax_map.plot(gx, gy, 'ro', markersize=8)
            arrow_len = 0.1
            dx = arrow_len * math.cos(gtheta)
            dy = arrow_len * math.sin(gtheta)
            self.ax_map.arrow(gx, gy, dx, dy, head_width=0.05, head_length=0.05, fc='red', ec='red')

        # 드래그 중인 경우 녹색 점선 화살표 표시
        if self.drag_start is not None and self.drag_current is not None:
            sx, sy = self.drag_start
            cx, cy = self.drag_current
            self.ax_map.arrow(sx, sy, cx - sx, cy - sy, head_width=0.05, head_length=0.05,
                                fc='green', ec='green', linestyle='--')
            
        # 가이드 선: 목표 수신 시 기록된 시작점에서 목표까지 빨간 점선
        if self.node.guide_line_start is not None and self.node.goal_pose is not None:
            start_x, start_y = self.node.guide_line_start
            goal_x = self.node.goal_pose.x
            goal_y = self.node.goal_pose.y
            self.ax_map.plot([start_x, goal_x], [start_y, goal_y], 'r--')
            if self.node.turtle_pose is not None:
                dist = math.sqrt((self.node.turtle_pose.x - goal_x)**2 +
                                    (self.node.turtle_pose.y - goal_y)**2)
                if dist < 0.1:
                    self.node.guide_line_start = None

        self.canvas_map.draw()

    def update_state_display(self):
        """상태 표시 영역 업데이트"""
        self.ax_state.clear()
        # 오른쪽 영역: x축 0 ~ 1.5, y축 0 ~ 1
        self.ax_state.set_xlim(0, 1.5)
        self.ax_state.set_ylim(0, 1)
        self.ax_state.axis('off')

        block_width = 0.8 * 1.2      # 0.96
        block_height = 0.06 * 1.1    # 약 0.066
        spacing = 0.12             # 블록 간 간격 (화살표 길이)
        
        # 오른쪽 영역의 폭은 1.5이므로, 가로 중앙에 배치: start_x = (1.5 - block_width) / 2
        start_x = (1.5 - block_width) / 2  # 약 0.27

        # 블록 전체 그룹을 수직 중앙 정렬하기 위해 총 높이를 계산
        n = len(self.state_list)
        total_height = n * block_height + (n - 1) * spacing
        group_bottom = 0.5 - total_height / 2
        group_top = group_bottom + total_height

        boundaries = []
        active_color = '#A2D2FF'    # 파스텔 블루
        inactive_color = '#E9ECEF'  # 연한 파스텔 그레이

        # 블록들을 그룹 중앙 기준으로 위에서부터 차례로 배치
        for i, state in enumerate(self.state_list):
            # i=0: 최상단 블록, 각 블록의 바닥 y 좌표
            y = group_top - (i + 1) * block_height - i * spacing
            face_color = active_color if self.node.current_state == state else inactive_color
            rect = FancyBboxPatch((start_x, y), block_width, block_height,
                                    boxstyle="round,pad=0.02",
                                    fc=face_color, ec="black", lw=1.5)
            self.ax_state.add_patch(rect)
            self.ax_state.text(start_x + block_width/2, y + block_height/2,
                                state, horizontalalignment='center',
                                verticalalignment='center',
                                color='black', fontsize=10)
            top_center = (start_x + block_width/2, y + block_height)
            bottom_center = (start_x + block_width/2, y)
            boundaries.append((top_center, bottom_center))
        
        for i in range(len(boundaries) - 1):
            start_point = boundaries[i][1]
            end_point = boundaries[i+1][0]
            self.ax_state.annotate("",
                                    xy=end_point, xycoords='data',
                                    xytext=start_point, textcoords='data',
                                    arrowprops=dict(arrowstyle="->", color='black'))
        self.canvas_state.draw()


def main(args=None):
    rclpy.init(args=args)
    node = PinkyMonitor()
    spin_thread = threading.Thread(target=ros_spin, args=(node,), daemon=True)
    spin_thread.start()

    app = QApplication(sys.argv)
    window = MainWindow(node)
    window.show()
    ret = app.exec_()

    node.destroy_node()
    rclpy.shutdown()
    sys.exit(ret)


if __name__ == '__main__':
    main()

