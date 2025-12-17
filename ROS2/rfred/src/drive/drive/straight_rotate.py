import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, Point
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from sensor_msgs.msg import Imu
from rcl_interfaces.msg import ParameterDescriptor
import math
import json

class StraightAndRotate(Node):

  def __init__(self):
    super().__init__('straight_rotate')

    self.drive_scenario =  []
    self.extract_drive_scenario()

    # 상태 관리 (IDLE, ROTATING, MOVING)
    self.state = 'IDLE'

    # 회전 관련 설정 변수
    self.target_angle_deg = -90.0  # 목표 회전 각도 (도)
    self.kp = 0.5                 # P-gain: 클수록 빨리 돌지만 오버슈트 위험 (조절 필요)
    self.min_vel = 0.2            # 모터가 움직일 수 있는 최소 속도 (너무 작으면 안 움직임)
    self.max_vel = 1.0            # 최대 회전 속도 제한
    self.angle_tolerance = 1.0          # 허용 오차 범위 (도) - 1도 이내면 멈춤

    # 회전 관련 상태 변수
    self.initial_yaw = None
    self.current_yaw = None
    self.target_yaw = None

    # 직진 관련 설정 변수
    self.target_distance = 0.765  # 목표 이동 거리 (미터) - 예: 95cm
    self.kp_dist = 1.0          # 거리 제어 P게인 (속도 조절용)
    self.kp_angle = 1.5         # 각도 보정 P게인 (직진 유지용)
    
    self.max_speed = 0.2        # 최대 전진 속도 (m/s)
    self.min_speed = 0.05       # 최소 전진 속도 (m/s)
    
    self.dist_tolerance = 0.01  # 거리 허용 오차 (1cm 이내면 정지)

    # 직진 관련 상태 변수
    self.start_x = None
    self.start_y = None
    self.current_x = 0.0
    self.current_y = 0.0

    self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
    self.odom_sub = self.create_subscription(Odometry, '/odom', self.odom_callback, 10)
    self.imu_subscriber = self.create_subscription(Imu, '/imu_raw', self.imu_callback, 10)
    self.command_sub = self.create_subscription(String, '/command', self.command_callback, 10)
    self.timer = self.create_timer(0.1, self.timer_callback)

  def extract_drive_scenario(self):

    param_move = f"dining.move"
    param_value = f"dining.value"

    my_descriptor = ParameterDescriptor(dynamic_typing=True)

    self.declare_parameter(param_move, [], my_descriptor)
    self.declare_parameter(param_value, [], my_descriptor)

    move_list = self.get_parameter(param_move).value
    value_list = self.get_parameter(param_value).value

    if not (len(move_list) == len(value_list)):
        self.get_logger().error("파라미터 길이 불일치!")
        return []

    if len(move_list) == 0:
        self.get_logger().warn("순찰 경로가 비어있음!")
        return []
    
    for move, value in zip(move_list, value_list):
        self.drive_scenario.append({'move': move, 'value': value})

    self.get_logger().info(f"도착까지 {len(self.drive_scenario)}번의 움직임 로드 완료")

  def imu_callback(self, msg):
    # Extract the yaw angle from the IMU message
    self.current_yaw = self.euler_from_quaternion(
        msg.orientation.x, 
        msg.orientation.y, 
        msg.orientation.z, 
        msg.orientation.w
    )

    # 2. 초기화: 첫 IMU 데이터가 들어왔을 때 목표 설정
    if self.initial_yaw is None:
      self.initial_yaw = self.current_yaw

  def odom_callback(self, msg):
    # 현재 위치(x, y) 업데이트
    self.current_x = msg.pose.pose.position.x
    self.current_y = msg.pose.pose.position.y

    # 시작 위치 설정
    # if self.start_x is None:
    #   self.start_x = self.current_x
    #   self.start_y = self.current_y
    #   self.get_logger().info(f"Start Position: ({self.start_x:.2f}, {self.start_y:.2f})")

  def command_callback(self, msg):
    data = json.loads(msg.data)
    command = data.get('move')
    value = float(data.get('value', 0.0))
    if command == "rotate":
      self.target_angle_deg = value
      # 목표 Yaw 설정
      if self.initial_yaw is not None:
          target_rad = self.initial_yaw + math.radians(self.target_angle_deg)
          self.target_yaw = self.normalize_angle(target_rad)
          self.state = 'ROTATING'
          self.get_logger().info(f"Command: Rotate {value} deg")
      else:
          self.get_logger().warn("IMU not ready yet.")
      self.target_angle_deg = value
      self.control_rotation()
    elif command == 'move':
      self.target_distance = value
      # 직진을 시작하기 전에, '현재 바라보는 각도'를 '유지해야 할 기준 각도'로 업데이트합니다.
      self.initial_yaw = self.current_yaw
      # 시작 위치 초기화
      self.start_x = self.current_x
      self.start_y = self.current_y
      self.state = 'MOVING'
      self.get_logger().info(f"Command: Move {value} m")
    else:
      self.get_logger().info("잘못된 주행 명령입니다.")

  def timer_callback(self):
    """타이머가 계속 돌면서 현재 상태에 맞는 제어 함수를 호출합니다."""
    if self.state == 'IDLE':
        self.process_next_command()
        
    elif self.state == 'ROTATING':
        self.control_rotation()
        
    elif self.state == 'MOVING':
        self.control_drive()
        
    elif self.state == 'WAITING':
        self.control_wait()

  def process_next_command(self):
    """큐에서 명령을 꺼내 상태를 설정합니다."""
    if not self.drive_scenario:
        # 모든 명령 완료
        self.stop_robot()
        return

    cmd_data = self.drive_scenario.pop(0)
    cmd_type = cmd_data.get('move')
    value = float(cmd_data.get('value', 0.0))

    self.get_logger().info(f"Executing: 움직임: {cmd_type}, 값: {value}")

    if cmd_type == 'rotate':
        self.target_angle_deg = value
        # 현재 각도 기준 상대 회전
        target_rad = self.current_yaw + math.radians(self.target_angle_deg)
        self.target_yaw = self.normalize_angle(target_rad)
        self.initial_yaw = self.current_yaw # 회전 시작 전 각도 저장
        self.state = 'ROTATING'

    elif cmd_type == 'move':
        self.target_distance = value
        self.start_x = self.current_x
        self.start_y = self.current_y
        self.initial_yaw = self.current_yaw # 직진 유지를 위한 기준 각도
        self.state = 'MOVING'

    elif cmd_type == 'wait':
        # JSON에 명시된 대기 시간
        self.wait_duration = value
        self.wait_start_time = self.get_clock().now().nanoseconds / 1e9
        self.state = 'WAITING'

  def switch_to_wait(self):
    """동작 완료 후 자동으로 대기 상태로 전환"""
    self.stop_robot()
    self.wait_duration = self.default_wait_time
    self.wait_start_time = self.get_clock().now().nanoseconds / 1e9
    self.state = 'WAITING'
    self.get_logger().info(f"Action done. Waiting for {self.wait_duration}s...")

  def control_wait(self):
    """정해진 시간만큼 대기"""
    current_time = self.get_clock().now().nanoseconds / 1e9
    elapsed = current_time - self.wait_start_time
    
    # 로봇이 밀리지 않게 정지 명령 지속 전송
    self.stop_robot()

    if elapsed >= self.wait_duration:
        self.state = 'IDLE'
    
  def control_rotation(self):
    self.get_logger().info(f"Initial Yaw: {math.degrees(self.initial_yaw):.2f}, Target Yaw: {math.degrees(self.target_yaw):.2f}")

    # 현재 각도와 목표 각도의 차이 계산 (Error)
    error = self.normalize_angle(self.target_yaw - self.current_yaw)
    error_deg = math.degrees(error)

    cmd = Twist()

    # 허용 오차 이내에 들어오면 정지
    if abs(error_deg) < self.angle_tolerance:
        self.get_logger().info(f"Target Reached! Error: {error_deg:.2f} deg")
        cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd)
        self.state = 'IDLE'
        # 노드 종료를 원하면 아래 주석 해제
        # rclpy.shutdown() 
        return

    # P-Controller: 오차에 비례하여 속도 결정
    angular_z = error * self.kp

    # 속도 제한 (Clamp)
    if angular_z > 0:
        angular_z = max(self.min_vel, min(self.max_vel, angular_z))
    else:
        angular_z = min(-self.min_vel, max(-self.max_vel, angular_z))

    # 명령 발행
    cmd.angular.z = angular_z
    self.cmd_vel_pub.publish(cmd)
    
    # 디버깅용 로그 (너무 자주 찍히면 주석 처리)
    # self.get_logger().info(f"Error: {error_deg:.2f}, Cmd: {angular_z:.2f}")

  def control_drive(self):
    # 1. 이동한 거리 계산 (유클리드 거리)
    dx = self.current_x - self.start_x
    dy = self.current_y - self.start_y
    distance_moved = math.sqrt(dx*dx + dy*dy)
    
    # 남은 거리 (에러)
    error_dist = self.target_distance - distance_moved
    
    cmd = Twist()

    # 목표 도달 체크
    if error_dist <= self.dist_tolerance:
        self.get_logger().info(f"Arrived! Moved: {distance_moved:.3f}m")
        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd)
        self.state = 'IDLE'
        # rclpy.shutdown() # 종료하고 싶으면 주석 해제
        return

    # 2. 직진 속도 제어 (거리가 멀면 빠르고, 가까우면 느리게)
    linear_x = error_dist * self.kp_dist
    linear_x = max(self.min_speed, min(self.max_speed, linear_x))

    # 3. 각도 보정 (직진 유지)
    # 목표 각도는 '처음 시작했을 때의 각도(initial_yaw)'로 고정
    if self.initial_yaw is not None:
        angle_error = self.normalize_angle(self.initial_yaw - self.current_yaw)
        angular_z = angle_error * self.kp_angle
    else:
        angular_z = 0.0

    # 명령 발행
    cmd.linear.x = linear_x
    cmd.angular.z = angular_z
    self.cmd_vel_pub.publish(cmd)
    
    # 디버깅 (필요시 주석 해제)
    # self.get_logger().info(f"Dist Error: {error_dist:.3f}, Angle Correction: {angular_z:.3f}")
  
  def stop_robot(self):
    cmd = Twist()
    self.cmd_vel_pub.publish(cmd)

  def euler_from_quaternion(self, x, y, z, w):
    """쿼터니언 -> Yaw 변환"""
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    return math.atan2(t3, t4)
  
  def normalize_angle(self, angle):
    """
    각도를 -PI ~ +PI 범위로 정규화
    (예: 190도는 -170도로 변환)
    """
    while angle > math.pi:
        angle -= 2.0 * math.pi
    while angle < -math.pi:
        angle += 2.0 * math.pi
    return angle
    
def main(args=None):
    rclpy.init(args=args)
    node = StraightAndRotate()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
