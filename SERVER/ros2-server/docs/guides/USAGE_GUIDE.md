# ros2-server 사용 가이드

**작성일**: 2025-11-10  
**프로젝트 경로**: `SERVER/ros2-server`

## 개요

`ros2-server`는 Pinky 로봇을 제어하기 위한 ROS2 서버 패키지 모음입니다.  
ROS2 토픽, 서비스, 액션을 통해 로봇을 원격으로 제어할 수 있습니다.

---

## 프로젝트 구조

```
ros2-server/
├── src/
│   ├── pinky_state_machine/          # State Machine 기반 제어 패키지
│   ├── pinky_lcd_display_controller/ # LCD 디스플레이 제어 패키지
│   └── pinky_lcd_display_interfaces/ # 인터페이스 정의 패키지
├── build/                            # 빌드 결과물
├── install/                          # 설치 결과물
└── log/                              # 빌드 로그
```

---

## 사전 준비

### 1. ROS2 환경 설정

```bash
# ROS2 환경 소스 (예: ROS2 Humble)
source /opt/ros/humble/setup.bash

# 또는 ROS2 Foxy
source /opt/ros/foxy/setup.bash
```

### 2. Python 의존성 설치

```bash
# 기본 의존성
sudo apt-get update
sudo apt-get install -y \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep

# GUI 모니터링용 (선택사항)
sudo apt-get install -y python3-pyqt5 python3-matplotlib
# 또는
pip3 install PyQt5 matplotlib

# ROS2 Python 패키지
sudo apt-get install -y \
    ros-humble-rclpy \
    ros-humble-nav-msgs \
    ros-humble-geometry-msgs \
    ros-humble-std-msgs \
    ros-humble-tf-transformations
```

### 3. 네트워크 설정

서버와 로봇이 같은 ROS2 도메인에서 통신할 수 있도록 설정:

```bash
# ROS2 도메인 ID 설정 (서버와 로봇 동일하게)
export ROS_DOMAIN_ID=0

# 네트워크 연결 확인
ping <로봇_IP주소>
```

---

## 빌드 방법

### 전체 빌드

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server

# 전체 패키지 빌드
colcon build

# 빌드 결과 소스
source install/setup.bash
```

### 개별 패키지 빌드

```bash
# State Machine 패키지만 빌드
colcon build --packages-select pinky_state_machine

# LCD Controller 패키지만 빌드
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display_controller

# 특정 패키지 제외
colcon build --packages-skip pinky_lcd_display_controller
```

### 빌드 옵션

```bash
# 디버그 모드
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Debug

# 릴리즈 모드
colcon build --cmake-args -DCMAKE_BUILD_TYPE=Release

# 병렬 빌드 (빠른 빌드)
colcon build --parallel-workers 4

# 의존성 자동 설치
rosdep install --from-paths src --ignore-src -r -y
```

---

## 패키지별 사용법

### 1. pinky_state_machine

State Machine 기반 로봇 제어 패키지

#### 1.1 로봇 측 준비사항

**로봇에서 실행해야 할 사항:**

```bash
# 로봇에서 실행
ros2 launch pinky_bringup bringup_robot.launch.xml
```

이 launch 파일은 다음을 제공합니다:
- `odom` 토픽: `nav_msgs/msg/Odometry` (30Hz)
- `cmd_vel` 토픽: `geometry_msgs/msg/Twist` (속도 명령 수신)
- `joint_states` 토픽: 조인트 상태 정보
- TF 변환: `odom` → `base_footprint`

#### 1.2 제어 노드 실행

**기본 실행:**
```bash
ros2 run pinky_state_machine move_pinky_state_machine
```

**파라미터 설정:**
```bash
ros2 run pinky_state_machine move_pinky_state_machine --ros-args \
  -p angle_tolerance:=0.05 \
  -p distance_tolerance:=0.05 \
  -p angular_P:=2.5 \
  -p linear_P:=1.5 \
  -p odom_topic:=odom \
  -p cmd_vel_topic:=cmd_vel \
  -p goal_pose_topic:=goal_pose
```

**주요 파라미터:**
- `angle_tolerance` (기본값: 0.1): 각도 허용 오차 (라디안)
- `distance_tolerance` (기본값: 0.1): 거리 허용 오차 (미터)
- `angular_P`, `angular_I`, `angular_D`: 각도 PID 게인
- `angular_max_state`, `angular_min_state`: 각도 출력 제한
- `linear_P`, `linear_I`, `linear_D`: 선형 PID 게인
- `linear_max_state`, `linear_min_state`: 선형 출력 제한
- `odom_topic` (기본값: 'odom'): Odometry 토픽 이름
- `cmd_vel_topic` (기본값: 'cmd_vel'): 속도 명령 토픽 이름
- `goal_pose_topic` (기본값: 'goal_pose'): 목표 위치 토픽 이름

**런타임 파라미터 변경:**
```bash
ros2 param set /pinky_goal_controller angle_tolerance 0.05
ros2 param set /pinky_goal_controller angular_P 3.0
```

#### 1.3 GUI 모니터링 노드 실행

**기본 실행:**
```bash
ros2 run pinky_state_machine qmonitor_pinky_state_machine
```

**파라미터 설정:**
```bash
ros2 run pinky_state_machine qmonitor_pinky_state_machine --ros-args \
  -p map_width:=5.0 \
  -p map_height:=3.0 \
  -p odom_topic:=odom \
  -p goal_pose_topic:=goal_pose \
  -p state_topic:=state
```

**GUI 기능:**
- 좌측: 로봇 위치 및 목표 위치 시각화
- 우측: State machine 상태 표시
- 마우스 드래그: 새로운 목표 위치 설정
- 실시간 업데이트: 로봇 위치 및 상태 실시간 표시

#### 1.4 목표 위치 설정

**토픽으로 목표 위치 발행:**
```bash
# 기본 목표 위치
ros2 topic pub --once /goal_pose geometry_msgs/msg/Pose \
  "{position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"

# 특정 방향으로 목표 설정
ros2 topic pub --once /goal_pose geometry_msgs/msg/Pose \
  "{position: {x: 2.0, y: 0.5, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.707, w: 0.707}}"
```

**GUI에서 목표 위치 설정:**
- GUI 창의 좌측 맵 영역에서 마우스로 클릭 및 드래그
- 목표 위치가 자동으로 `/goal_pose` 토픽으로 발행됨

#### 1.5 토픽 모니터링

**현재 위치 확인:**
```bash
ros2 topic echo /odom
```

**속도 명령 확인:**
```bash
ros2 topic echo /cmd_vel
```

**상태 확인:**
```bash
ros2 topic echo /state
```

**오차 정보 확인:**
```bash
ros2 topic echo /angle_error
ros2 topic echo /distance_error
```

**토픽 정보 확인:**
```bash
ros2 topic list
ros2 topic info /odom
ros2 topic info /cmd_vel
ros2 topic info /goal_pose
```

#### 1.6 State Machine 동작

State machine은 다음 4가지 상태로 구성됩니다:

1. **RotateToGoal**: 목표 방향으로 회전
   - PID 각도 제어
   - 완료 조건: 각도 오차 < `angle_tolerance`

2. **MoveToGoal**: 목표 위치로 이동
   - PID 선형 및 각도 제어
   - 완료 조건: 거리 오차 < `distance_tolerance`

3. **RotateToFinal**: 최종 방향으로 회전
   - PID 각도 제어
   - 완료 조건: 각도 오차 < `angle_tolerance`

4. **GoalReached**: 목표 도달 (종료 상태)
   - 정지 (linear=0, angular=0)

**상태 전이:**
```
RotateToGoal → MoveToGoal → RotateToFinal → GoalReached
```

---

### 2. pinky_lcd_display_controller

LCD 디스플레이 제어 패키지

#### 2.1 서버 노드 실행

**기본 실행:**
```bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

#### 2.2 서비스 사용

**SetDisplay 서비스:**
```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Hello', lines: ['Line 1', 'Line 2'], show_timestamp: true}"
```

**SetStyle 서비스:**
```bash
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{title_color: {r: 255, g: 0, b: 0}, line_color: {r: 0, g: 255, b: 0}}"
```

**ClearDisplay 서비스:**
```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay \
  "{}"
```

**SetLayout 서비스:**
```bash
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{layout_type: 1, title_position: 'top', line_spacing: 1.2}"
```

#### 2.3 액션 사용

**SetDisplayAction:**
```bash
ros2 action send_goal --feedback /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Processing', lines: ['Task: Data processing'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"
```

**ScrollTextAction:**
```bash
ros2 action send_goal --feedback /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'This is a long scrolling text message', speed: 2, direction: 1}"
```

#### 2.4 서비스/액션 목록 확인

```bash
# 서비스 목록
ros2 service list | grep lcd_controller

# 액션 목록
ros2 action list | grep lcd_controller

# 서비스 타입 확인
ros2 service type /lcd_controller/set_display

# 액션 타입 확인
ros2 action info /lcd_controller/set_display_action
```

---

## 통합 사용 시나리오

### 시나리오 1: 기본 로봇 제어

**1단계: 로봇 측 실행**
```bash
# 로봇에서 실행
ros2 launch pinky_bringup bringup_robot.launch.xml
```

**2단계: 서버 측 제어 노드 실행**
```bash
# 서버에서 실행
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
source install/setup.bash
ros2 run pinky_state_machine move_pinky_state_machine
```

**3단계: 목표 위치 설정**
```bash
# 다른 터미널에서
ros2 topic pub --once /goal_pose geometry_msgs/msg/Pose \
  "{position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"
```

**4단계: 모니터링 (선택사항)**
```bash
# GUI 모니터링
ros2 run pinky_state_machine qmonitor_pinky_state_machine

# 또는 토픽 모니터링
ros2 topic echo /state
ros2 topic echo /cmd_vel
```

### 시나리오 2: LCD 디스플레이 제어

**1단계: 서버 노드 실행**
```bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

**2단계: LCD 표시**
```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Robot Status', lines: ['State: Moving', 'Battery: 80%'], show_timestamp: true}"
```

**3단계: 애니메이션 표시**
```bash
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Processing', lines: ['Task: Navigation'], duration_ms: 3000, animation_type: 1}"
```

### 시나리오 3: 통합 제어 (State Machine + LCD)

**1단계: 모든 노드 실행**
```bash
# 터미널 1: State Machine 제어 노드
ros2 run pinky_state_machine move_pinky_state_machine

# 터미널 2: LCD 제어 서버
ros2 run pinky_lcd_display_controller lcd_controller_server

# 터미널 3: GUI 모니터링 (선택사항)
ros2 run pinky_state_machine qmonitor_pinky_state_machine
```

**2단계: 목표 위치 설정 및 LCD 업데이트**
```bash
# 목표 위치 설정
ros2 topic pub --once /goal_pose geometry_msgs/msg/Pose \
  "{position: {x: 2.0, y: 1.5, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"

# LCD에 상태 표시
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Navigation', lines: ['Goal: (2.0, 1.5)', 'Status: Moving'], show_timestamp: true}"
```

---

## 네트워크 설정 상세

### ROS2 도메인 설정

**같은 네트워크에서:**
```bash
# 서버와 로봇 모두 동일한 도메인 ID 설정
export ROS_DOMAIN_ID=0
```

**다른 네트워크에서 (멀티캐스트):**
```bash
# ROS2 멀티캐스트 설정 확인
export ROS_DISCOVERY_SERVER=192.168.1.100:11811
```

### 방화벽 설정

**필요한 포트:**
- ROS2 DDS 통신: UDP 7400-7500 (멀티캐스트)
- ROS2 Discovery Server: TCP 11811 (선택사항)

**방화벽 해제 (Ubuntu):**
```bash
sudo ufw allow 7400:7500/udp
sudo ufw allow 11811/tcp
```

### 네트워크 연결 확인

```bash
# 로봇 IP 확인
ros2 node list

# 토픽 확인
ros2 topic list

# 서비스 확인
ros2 service list

# 네트워크 상태 확인
ros2 node info /pinky_goal_controller
```

---

## 문제 해결

### 1. 빌드 오류

**문제: 패키지를 찾을 수 없음**
```bash
# 해결: 의존성 설치
rosdep update
rosdep install --from-paths src --ignore-src -r -y
```

**문제: Python 패키지 import 오류**
```bash
# 해결: 빌드 후 소스
source install/setup.bash
```

### 2. 실행 오류

**문제: 노드를 찾을 수 없음**
```bash
# 해결: 빌드 확인
colcon build --packages-select <package_name>
source install/setup.bash

# 실행 파일 확인
ros2 pkg executables <package_name>
```

**문제: 토픽이 수신되지 않음**
```bash
# 해결: ROS2 도메인 ID 확인
echo $ROS_DOMAIN_ID

# 네트워크 연결 확인
ros2 topic list
ros2 topic echo /odom --once
```

### 3. 로봇 제어 오류

**문제: 로봇이 움직이지 않음**
```bash
# 해결: 로봇 측 bringup 확인
ros2 topic echo /odom  # 로봇에서 실행

# cmd_vel 토픽 확인
ros2 topic echo /cmd_vel  # 서버에서 실행

# 로봇 모터 드라이버 확인
ros2 topic list  # 로봇에서 실행
```

**문제: 목표 위치가 업데이트되지 않음**
```bash
# 해결: goal_pose 토픽 확인
ros2 topic echo /goal_pose

# 노드 상태 확인
ros2 node info /pinky_goal_controller
```

### 4. GUI 모니터링 오류

**문제: GUI가 표시되지 않음**
```bash
# 해결: PyQt5 설치 확인
python3 -c "import PyQt5; print('PyQt5 OK')"

# X11 포워딩 확인 (원격 접속 시)
echo $DISPLAY
```

---

## 고급 사용법

### 1. Launch 파일 생성

**예시: `launch/pinky_control.launch.py`**
```python
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='pinky_state_machine',
            executable='move_pinky_state_machine',
            name='pinky_controller',
            parameters=[{
                'angle_tolerance': 0.05,
                'distance_tolerance': 0.05,
            }]
        ),
        Node(
            package='pinky_lcd_display_controller',
            executable='lcd_controller_server',
            name='lcd_controller',
        ),
    ])
```

**실행:**
```bash
ros2 launch <package_name> pinky_control.launch.py
```

### 2. 파라미터 파일 사용

**예시: `config/pinky_params.yaml`**
```yaml
/pinky_goal_controller:
  ros__parameters:
    angle_tolerance: 0.05
    distance_tolerance: 0.05
    angular_P: 2.5
    linear_P: 1.5
```

**사용:**
```bash
ros2 run pinky_state_machine move_pinky_state_machine \
  --ros-args --params-file config/pinky_params.yaml
```

### 3. 로깅 설정

```bash
# 로그 레벨 설정
ros2 run pinky_state_machine move_pinky_state_machine \
  --ros-args --log-level debug

# 로그 파일 저장
ros2 run pinky_state_machine move_pinky_state_machine \
  --ros-args --log-level info 2>&1 | tee robot_control.log
```

### 4. 네임스페이스 사용

```bash
# 네임스페이스로 여러 로봇 제어
ros2 run pinky_state_machine move_pinky_state_machine \
  --ros-args -r __ns:=/robot1

ros2 run pinky_state_machine move_pinky_state_machine \
  --ros-args -r __ns:=/robot2
```

---

## 패키지별 상세 문서

### pinky_state_machine
- [패키지 README](src/pinky_state_machine/README.md)
- [State Diagram](src/pinky_state_machine/docs/STATE_DIAGRAM.md)
- [개발 현황 리포트](src/pinky_state_machine/docs/DEVELOPMENT_REPORT.md)
- [TODO](src/pinky_state_machine/docs/TODO.md)

### pinky_lcd_display_controller
- [패키지 README](src/pinky_lcd_display_controller/README.md)
- [종합 테스트 가이드](src/pinky_lcd_display_controller/docs/COMPREHENSIVE_TEST_GUIDE.md)
- [서비스/액션 실행 흐름](src/pinky_lcd_display_controller/docs/SERVICE_ACTION_EXECUTION_FLOW.md)
- [개발 현황 리포트](src/pinky_lcd_display_controller/docs/DEVELOPMENT_REPORT.md)

---

## 주요 토픽 및 서비스 요약

### pinky_state_machine 토픽

| 토픽 이름 | 타입 | 방향 | 설명 |
|----------|------|------|------|
| `/odom` | `nav_msgs/Odometry` | 구독 | 로봇의 현재 위치 및 자세 |
| `/goal_pose` | `geometry_msgs/Pose` | 구독 | 목표 위치 및 자세 |
| `/cmd_vel` | `geometry_msgs/Twist` | 발행 | 속도 명령 |
| `/angle_error` | `std_msgs/Float64` | 발행 | 각도 오차 |
| `/distance_error` | `std_msgs/Float64` | 발행 | 거리 오차 |
| `/state` | `std_msgs/String` | 발행 | 현재 상태 |

### pinky_lcd_display_controller 서비스

| 서비스 이름 | 타입 | 설명 |
|------------|------|------|
| `/lcd_controller/set_display` | `SetDisplay` | LCD 표시 내용 설정 |
| `/lcd_controller/set_style` | `SetStyle` | LCD 스타일 설정 |
| `/lcd_controller/clear_display` | `ClearDisplay` | LCD 화면 지우기 |
| `/lcd_controller/set_layout` | `SetLayout` | LCD 레이아웃 설정 |

### pinky_lcd_display_controller 액션

| 액션 이름 | 타입 | 설명 |
|----------|------|------|
| `/lcd_controller/set_display_action` | `SetDisplay` | LCD 표시 액션 (애니메이션 지원) |
| `/lcd_controller/scroll_text_action` | `ScrollText` | 텍스트 스크롤 액션 |

---

## 빠른 참조

### 빌드
```bash
cd SERVER/ros2-server
colcon build
source install/setup.bash
```

### 실행
```bash
# State Machine 제어
ros2 run pinky_state_machine move_pinky_state_machine

# GUI 모니터링
ros2 run pinky_state_machine qmonitor_pinky_state_machine

# LCD 제어 서버
ros2 run pinky_lcd_display_controller lcd_controller_server
```

### 목표 위치 설정
```bash
ros2 topic pub --once /goal_pose geometry_msgs/msg/Pose \
  "{position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"
```

### 상태 확인
```bash
ros2 topic echo /state
ros2 topic echo /cmd_vel
ros2 node list
ros2 topic list
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 1.0.0 | 2025-11-10 | 초기 버전 작성 | Development Team |

