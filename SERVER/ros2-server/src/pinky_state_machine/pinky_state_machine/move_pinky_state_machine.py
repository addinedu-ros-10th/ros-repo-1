#!/usr/bin/env python3
"""
Pinky 로봇용 State Machine 기반 목표 제어 노드

이 파일은 move_turtle_state_machine.py를 기반으로 하되,
pinky 로봇의 odom 토픽과 cmd_vel 토픽을 사용하도록 수정되었습니다.

주요 변경사항:
- 'turtle1/pose' -> 'odom' (nav_msgs/Odometry)
- 'turtle1/cmd_vel' -> 'cmd_vel'
- turtlesim.msg.Pose -> nav_msgs/Odometry에서 변환
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry  # Pinky 로봇의 odom 메시지 타입
from geometry_msgs.msg import Twist, Pose  # Pose는 goal_pose용으로 사용
from std_msgs.msg import Float64, String
from rcl_interfaces.msg import SetParametersResult
import math
from tf_transformations import euler_from_quaternion  # 쿼터니언을 오일러 각으로 변환

from pinky_state_machine.control_apps import PID


def normalize_angle(angle):
    """각도를 -π ~ π 범위로 정규화"""
    return math.atan2(math.sin(angle), math.cos(angle))


def odom_to_pose(odom_msg):
    """
    nav_msgs/Odometry 메시지를 turtlesim.msg.Pose 형식으로 변환
    
    Args:
        odom_msg: nav_msgs/Odometry 메시지
        
    Returns:
        turtlesim.msg.Pose 형식의 pose 객체 (x, y, theta 속성 포함)
    """
    # 간단한 클래스로 pose 객체 생성
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


# Define possible state results (IDLE removed)
class StateResult:
    CONTINUE = 0
    COMPLETE = 1


# Abstract state class that returns a (Twist, status) tuple
class ControllerState:
    def __init__(self, controller):
        self.controller = controller

    def update(self, current_pose):
        raise NotImplementedError("update() must be implemented by subclasses")


# RotateToGoalState: turn to face the goal
class RotateToGoalState(ControllerState):
    def update(self, current_pose):
        twist_msg = Twist()
        desired_heading = math.atan2(
            self.controller.goal_pose.y - current_pose.y,
            self.controller.goal_pose.x - current_pose.x)
        error_angle = normalize_angle(desired_heading - current_pose.theta)
        error_msg = Float64()
        error_msg.data = error_angle
        # Publish angle error and state
        self.controller.angle_error_publisher.publish(error_msg)
        self.controller.state_publisher.publish(String(data="RotateToGoal"))
        self.controller.get_logger().info(f"[RotateToGoal] Heading error: {error_angle:.2f}")

        if abs(error_angle) > self.controller.angle_tolerance:
            angular_correction = self.controller.angular_pid.update(error_angle)
            twist_msg.angular.z = angular_correction
            twist_msg.linear.x = 0.0
            return twist_msg, StateResult.CONTINUE
        else:
            twist_msg.angular.z = 0.0
            twist_msg.linear.x = 0.0
            self.controller.get_logger().info("Heading aligned. RotateToGoal complete.")
            return twist_msg, StateResult.COMPLETE


# MoveToGoalState: move forward toward the goal while correcting heading
class MoveToGoalState(ControllerState):
    def update(self, current_pose):
        twist_msg = Twist()
        dx = self.controller.goal_pose.x - current_pose.x
        dy = self.controller.goal_pose.y - current_pose.y
        distance_error = dx * math.cos(current_pose.theta) + dy * math.sin(current_pose.theta)
        error_msg = Float64()
        error_msg.data = distance_error
        # Publish distance error and state
        self.controller.distance_error_publisher.publish(error_msg)
        self.controller.state_publisher.publish(String(data="MoveToGoal"))
        self.controller.get_logger().info(f"[MoveToGoal] Distance error: {distance_error:.2f}")

        if abs(distance_error) > self.controller.distance_tolerance:
            linear_correction = self.controller.linear_pid.update(distance_error)
            twist_msg.linear.x = linear_correction
            desired_heading = math.atan2(
                self.controller.goal_pose.y - current_pose.y,
                self.controller.goal_pose.x - current_pose.x)
            angle_error = normalize_angle(desired_heading - current_pose.theta)
            angular_correction = self.controller.angular_pid.update(angle_error)
            twist_msg.angular.z = angular_correction
            return twist_msg, StateResult.CONTINUE
        else:
            twist_msg.linear.x = 0.0
            twist_msg.angular.z = 0.0
            self.controller.get_logger().info("Position reached. MoveToGoal complete.")
            return twist_msg, StateResult.COMPLETE


# RotateToFinalState: rotate in place to match final orientation
class RotateToFinalState(ControllerState):
    def update(self, current_pose):
        twist_msg = Twist()
        final_error = normalize_angle(self.controller.goal_pose.theta - current_pose.theta)
        error_msg = Float64()
        error_msg.data = final_error
        # Publish final orientation error and state
        self.controller.angle_error_publisher.publish(error_msg)
        self.controller.state_publisher.publish(String(data="RotateToFinal"))
        self.controller.get_logger().info(f"[RotateToFinal] Orientation error: {final_error:.2f}")

        if abs(final_error) > self.controller.angle_tolerance:
            angular_correction = self.controller.angular_pid.update(final_error)
            twist_msg.angular.z = angular_correction
            twist_msg.linear.x = 0.0
            return twist_msg, StateResult.CONTINUE
        else:
            twist_msg.angular.z = 0.0
            twist_msg.linear.x = 0.0
            self.controller.get_logger().info("Final orientation reached. RotateToFinal complete.")
            return twist_msg, StateResult.COMPLETE


# GoalReachedState: the terminal state when the goal has been achieved
class GoalReachedState(ControllerState):
    def update(self, current_pose):
        twist_msg = Twist()
        twist_msg.linear.x = 0.0
        twist_msg.angular.z = 0.0
        self.controller.state_publisher.publish(String(data="GoalReached"))
        self.controller.get_logger().info("Goal reached!")
        return twist_msg, StateResult.COMPLETE


# StateTransitionManager encapsulates state transition rules
class StateTransitionManager:
    def __init__(self, controller):
        self.controller = controller

    def get_next_state(self, current_state, state_result):
        if state_result == StateResult.COMPLETE:
            if isinstance(current_state, RotateToGoalState):
                return MoveToGoalState(self.controller)
            elif isinstance(current_state, MoveToGoalState):
                return RotateToFinalState(self.controller)
            elif isinstance(current_state, RotateToFinalState):
                return GoalReachedState(self.controller)
            elif isinstance(current_state, GoalReachedState):
                # Terminal state, remain here
                return GoalReachedState(self.controller)
        elif state_result == StateResult.CONTINUE:
            return current_state
        return current_state


# Main controller node that manages state transitions
class PinkyGoalController(Node):
    def __init__(self):
        super().__init__('pinky_goal_controller')
        
        # Declare parameters for tolerances and PID
        self.declare_parameter('angle_tolerance', 0.1)
        self.declare_parameter('distance_tolerance', 0.1)

        self.declare_parameter('angular_P', 2.0)
        self.declare_parameter('angular_I', 0.0)
        self.declare_parameter('angular_D', 0.0)
        self.declare_parameter('angular_max_state', 2.0)
        self.declare_parameter('angular_min_state', -2.0)

        self.declare_parameter('linear_P', 1.0)
        self.declare_parameter('linear_I', 0.0)
        self.declare_parameter('linear_D', 0.0)
        self.declare_parameter('linear_max_state', 2.0)
        self.declare_parameter('linear_min_state', -2.0)

        # 토픽 이름 파라미터 (기본값은 pinky 로봇용)
        self.declare_parameter('odom_topic', 'odom')
        self.declare_parameter('cmd_vel_topic', 'cmd_vel')
        self.declare_parameter('goal_pose_topic', 'goal_pose')

        self.angle_tolerance = self.get_parameter('angle_tolerance').value
        self.distance_tolerance = self.get_parameter('distance_tolerance').value

        # Initialize Angular PID
        angular_P = self.get_parameter('angular_P').value
        angular_I = self.get_parameter('angular_I').value
        angular_D = self.get_parameter('angular_D').value
        angular_max_state = self.get_parameter('angular_max_state').value
        angular_min_state = self.get_parameter('angular_min_state').value
        self.angular_pid = PID()
        self.angular_pid.P = angular_P
        self.angular_pid.I = angular_I
        self.angular_pid.D = angular_D
        self.angular_pid.max_state = angular_max_state
        self.angular_pid.min_state = angular_min_state

        # Initialize Linear PID
        linear_P = self.get_parameter('linear_P').value
        linear_I = self.get_parameter('linear_I').value
        linear_D = self.get_parameter('linear_D').value
        linear_max_state = self.get_parameter('linear_max_state').value
        linear_min_state = self.get_parameter('linear_min_state').value
        self.linear_pid = PID()
        self.linear_pid.P = linear_P
        self.linear_pid.I = linear_I
        self.linear_pid.D = linear_D
        self.linear_pid.max_state = linear_max_state
        self.linear_pid.min_state = linear_min_state

        self.state_instance = None
        self.goal_pose = None
        
        self.state_transition_manager = StateTransitionManager(self)
        
        # Pinky 로봇의 odom 토픽 구독 (nav_msgs/Odometry)
        odom_topic = self.get_parameter('odom_topic').value
        self.odom_subscriber = self.create_subscription(
            Odometry,
            odom_topic,
            self.odom_callback,
            10)
        
        # goal_pose 토픽 구독 (geometry_msgs/Pose)
        goal_pose_topic = self.get_parameter('goal_pose_topic').value
        self.goal_pose_subscriber = self.create_subscription(
            Pose,
            goal_pose_topic,
            self.goal_pose_callback,
            10)
        
        # Pinky 로봇의 cmd_vel 토픽 발행
        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.cmd_vel_publisher = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.angle_error_publisher = self.create_publisher(Float64, 'angle_error', 10)
        self.distance_error_publisher = self.create_publisher(Float64, 'distance_error', 10)
        self.state_publisher = self.create_publisher(String, 'state', 10)
        
        self.add_on_set_parameters_callback(self.parameter_callback)
    
    def parameter_callback(self, params):
        for param in params:
            if param.name == 'angle_tolerance':
                self.angle_tolerance = param.value
                self.get_logger().info(f"Updated angle_tolerance: {param.value}")
            elif param.name == 'distance_tolerance':
                self.distance_tolerance = param.value
                self.get_logger().info(f"Updated distance_tolerance: {param.value}")
            elif param.name == 'angular_P':
                self.angular_pid.P = param.value
                self.get_logger().info(f"Updated angular_PID P: {param.value}")
            elif param.name == 'angular_I':
                self.angular_pid.I = param.value
                self.get_logger().info(f"Updated angular_PID I: {param.value}")
            elif param.name == 'angular_D':
                self.angular_pid.D = param.value
                self.get_logger().info(f"Updated angular_PID D: {param.value}")
            elif param.name == 'angular_max_state':
                self.angular_pid.max_state = param.value
                self.get_logger().info(f"Updated angular_PID max_state: {param.value}")
            elif param.name == 'angular_min_state':
                self.angular_pid.min_state = param.value
                self.get_logger().info(f"Updated angular_PID min_state: {param.value}")
            elif param.name == 'linear_P':
                self.linear_pid.P = param.value
                self.get_logger().info(f"Updated linear_PID P: {param.value}")
            elif param.name == 'linear_I':
                self.linear_pid.I = param.value
                self.get_logger().info(f"Updated linear_PID I: {param.value}")
            elif param.name == 'linear_D':
                self.linear_pid.D = param.value
                self.get_logger().info(f"Updated linear_PID D: {param.value}")
            elif param.name == 'linear_max_state':
                self.linear_pid.max_state = param.value
                self.get_logger().info(f"Updated linear_PID max_state: {param.value}")
            elif param.name == 'linear_min_state':
                self.linear_pid.min_state = param.value
                self.get_logger().info(f"Updated linear_PID min_state: {param.value}")
        return SetParametersResult(successful=True)
    
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
        self.state_instance = RotateToGoalState(self)
        self.get_logger().info(
            f"Received new goal pose: x={msg.position.x:.2f}, y={msg.position.y:.2f}, theta={theta:.2f}"
        )
    
    def odom_callback(self, msg):
        """odom 토픽에서 현재 위치 정보 수신 및 제어 실행"""
        if self.goal_pose is None or self.state_instance is None:
            return
        
        # Odometry 메시지를 SimplePose 형식으로 변환
        current_pose = odom_to_pose(msg)
        
        # State machine 업데이트 및 제어 명령 발행
        twist_msg, status = self.state_instance.update(current_pose)
        self.state_instance = self.state_transition_manager.get_next_state(self.state_instance, status)
        self.cmd_vel_publisher.publish(twist_msg)

def main(args=None):
    rclpy.init(args=args)
    node = PinkyGoalController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Node interrupted")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

