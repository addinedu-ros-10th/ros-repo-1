# pinky_state_machine 패키지

Pinky 로봇을 위한 State Machine 기반 제어 패키지입니다.

## 패키지 구조

```
pinky_state_machine/
├── package.xml              # ROS2 패키지 메타데이터
├── setup.py                 # Python 패키지 설정 및 entry points
├── setup.cfg                # 설치 설정
├── resource/
│   └── pinky_state_machine  # 리소스 마커 파일
└── pinky_state_machine/
    ├── __init__.py
    ├── control_apps.py                    # PID 컨트롤러 클래스
    ├── move_pinky_state_machine.py        # State machine 기반 제어 노드
    └── qmonitor_pinky_state_machine.py    # GUI 모니터링 노드
```

## 빌드 방법

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
colcon build --packages-select pinky_state_machine
source install/setup.bash
```

## 사용 방법

### 1. 제어 노드 실행

State machine 기반 제어 노드를 실행합니다:

```bash
ros2 run pinky_state_machine move_pinky_state_machine
```

**주요 파라미터:**
- `angle_tolerance` (기본값: 0.1): 각도 허용 오차
- `distance_tolerance` (기본값: 0.1): 거리 허용 오차
- `angular_P`, `angular_I`, `angular_D`: 각도 PID 게인
- `linear_P`, `linear_I`, `linear_D`: 선형 PID 게인
- `odom_topic` (기본값: 'odom'): Odometry 토픽 이름
- `cmd_vel_topic` (기본값: 'cmd_vel'): 속도 명령 토픽 이름
- `goal_pose_topic` (기본값: 'goal_pose'): 목표 위치 토픽 이름

**예시:**
```bash
ros2 run pinky_state_machine move_pinky_state_machine --ros-args \
  -p angle_tolerance:=0.05 \
  -p distance_tolerance:=0.05 \
  -p angular_P:=2.5
```

### 2. 모니터링 노드 실행

GUI 기반 모니터링 노드를 실행합니다:

```bash
ros2 run pinky_state_machine qmonitor_pinky_state_machine
```

**주요 파라미터:**
- `odom_topic` (기본값: 'odom'): Odometry 토픽 이름
- `goal_pose_topic` (기본값: 'goal_pose'): 목표 위치 토픽 이름
- `state_topic` (기본값: 'state'): 상태 토픽 이름
- `map_width` (기본값: 3.443): 맵 너비 (미터)
- `map_height` (기본값: 2.25): 맵 높이 (미터)

**GUI 기능:**
- 좌측: 로봇 위치 및 목표 위치 시각화
- 우측: State machine 상태 표시
- 마우스 드래그: 새로운 목표 위치 설정

**예시:**
```bash
ros2 run pinky_state_machine qmonitor_pinky_state_machine --ros-args \
  -p map_width:=5.0 \
  -p map_height:=3.0
```

## State Machine 동작

State machine은 다음 4가지 상태로 구성됩니다:

1. **RotateToGoal**: 목표 방향으로 회전
2. **MoveToGoal**: 목표 위치로 이동 (동시에 방향 보정)
3. **RotateToFinal**: 최종 방향으로 회전
4. **GoalReached**: 목표 도달 (종료 상태)

## 토픽

### 구독 토픽
- `odom` (nav_msgs/Odometry): 로봇의 현재 위치 및 자세
- `goal_pose` (geometry_msgs/Pose): 목표 위치 및 자세

### 발행 토픽
- `cmd_vel` (geometry_msgs/Twist): 속도 명령
- `angle_error` (std_msgs/Float64): 각도 오차
- `distance_error` (std_msgs/Float64): 거리 오차
- `state` (std_msgs/String): 현재 상태

## 의존성

### ROS2 패키지
- `rclpy`
- `nav_msgs`
- `geometry_msgs`
- `std_msgs`
- `tf_transformations`

### Python 패키지 (qmonitor_pinky_state_machine 사용 시)
- `PyQt5`
- `matplotlib`

**설치 방법:**
```bash
sudo apt-get install python3-pyqt5 python3-matplotlib
# 또는
pip3 install PyQt5 matplotlib
```

## 참고

이 패키지는 `/home/guehojung/dev_ws/ROS2/control_tutorials/src/controller_tutorials/controller_tutorials/`의 다음 파일들을 기반으로 작성되었습니다:
- `move_pinky_state_machine.py`
- `qmonitor_pinky_state_machine.py`
- `control_apps.py`

