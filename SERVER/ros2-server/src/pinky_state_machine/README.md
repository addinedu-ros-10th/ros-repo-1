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

### 로봇 측 준비사항

`pinky_state_machine`을 사용하기 전에 로봇 측에서 다음 사항을 준비해야 합니다:

#### 1. pinky_pro 패키지 실행

로봇에서 `pinky_bringup` 패키지를 실행하여 오도메트리(`odom`) 토픽과 속도 제어(`cmd_vel`) 토픽을 활성화해야 합니다:

```bash
# 로봇에서 실행
ros2 launch pinky_bringup bringup_robot.launch.xml
```

이 launch 파일은 다음을 제공합니다:
- `odom` 토픽: `nav_msgs/msg/Odometry` 타입의 오도메트리 정보 (30Hz)
- `cmd_vel` 토픽: `geometry_msgs/msg/Twist` 타입의 속도 명령 수신
- `joint_states` 토픽: 조인트 상태 정보
- TF 변환: `odom` → `base_footprint` 변환 발행

#### 2. 네트워크 설정

서버와 로봇이 같은 ROS2 도메인에서 통신할 수 있도록 설정:
- ROS2 도메인 ID 확인: `export ROS_DOMAIN_ID=<동일한_ID>`
- 네트워크 연결 확인: 서버와 로봇 간 네트워크 연결 상태 확인

#### 3. 토픽 확인

로봇이 정상적으로 실행 중인지 확인:

```bash
# odom 토픽 확인
ros2 topic echo /odom

# cmd_vel 토픽 확인 (발행 가능 여부)
ros2 topic info /cmd_vel
```

### 서버 측 실행

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

## 통합 테스트 시나리오

### 전체 시스템 실행 순서

1. **로봇 측 실행** (로봇에서):
   ```bash
   ros2 launch pinky_bringup bringup_robot.launch.xml
   ```

2. **서버 측 제어 노드 실행** (서버에서):
   ```bash
   ros2 run pinky_state_machine move_pinky_state_machine
   ```

3. **서버 측 모니터링 노드 실행** (서버에서, 선택사항):
   ```bash
   ros2 run pinky_state_machine qmonitor_pinky_state_machine
   ```

4. **목표 위치 설정** (다른 터미널에서):
   ```bash
   ros2 topic pub --once /goal_pose geometry_msgs/msg/Pose "{position: {x: 1.0, y: 1.0, z: 0.0}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"
   ```

### 문제 해결

- **odom 토픽이 수신되지 않는 경우**: 로봇의 `pinky_bringup`이 정상 실행 중인지 확인
- **cmd_vel이 전달되지 않는 경우**: 네트워크 연결 및 ROS2 도메인 ID 확인
- **로봇이 움직이지 않는 경우**: 로봇의 모터 드라이버 및 Dynamixel 통신 상태 확인

## pinky_pro 센서 및 기능 통합 현황

### 활용 가능한 센서

#### 센서 (Sensors)
1. **IMU 센서** (`pinky_imu_bno055`)
   - 토픽: `imu_raw` (sensor_msgs/msg/Imu)
   - 주기: 100Hz
   - 데이터: 가속도, 각속도, 방향 (쿼터니언)
   - 통합 상태: ⏳ 예정

2. **초음파 센서** (`pinky_sensor_adc`)
   - 토픽: `us_sensor/range` (sensor_msgs/msg/Range)
   - 주기: 20Hz
   - 범위: 0.02m ~ 3.0m
   - 통합 상태: ⏳ 예정

3. **적외선 센서** (`pinky_sensor_adc`)
   - 토픽: `ir_sensor/range` (std_msgs/msg/UInt16MultiArray)
   - 주기: 20Hz
   - 센서 개수: 3개
   - 통합 상태: ⏳ 예정

4. **배터리 상태** (`pinky_sensor_adc`)
   - 토픽: `batt_state` (sensor_msgs/msg/BatteryState)
   - 주기: 20Hz
   - 통합 상태: ⏳ 예정

5. **라이다 센서** (Gazebo 시뮬레이션)
   - 토픽: `scan` (sensor_msgs/msg/LaserScan)
   - 통합 상태: ⏳ 예정

6. **카메라** (Gazebo 시뮬레이션)
   - 토픽: `camera/image_raw` (sensor_msgs/msg/Image)
   - 통합 상태: ⏳ 예정

#### 제어 가능 기능 (Controllable Features)
1. **LED 제어** (`pinky_led`)
   - 서비스: `set_led` (pinky_interfaces/srv/SetLed)
   - 기능: 픽셀 제어, 전체 채우기, 초기화
   - 통합 상태: ⏳ 예정

2. **LED 밝기 제어** (`pinky_led`)
   - 서비스: `set_brightness` (pinky_interfaces/srv/SetBrightness)
   - 통합 상태: ⏳ 예정

3. **램프 제어** (`pinky_lamp_control`)
   - 서비스: `set_lamp` (pinky_interfaces/srv/SetLamp)
   - 모드: 꺼짐, 켜짐, 깜빡임, 밝기 조절
   - 통합 상태: ⏳ 예정

4. **감정 표시** (`pinky_emotion`)
   - 서비스: `set_emotion` (pinky_interfaces/srv/Emotion)
   - 감정: hello, basic, angry, bored, fun, happy, interest, sad
   - 통합 상태: ⏳ 예정

### 통합 현황 요약

| 센서/기능 | 패키지 | 토픽/서비스 | 통합 상태 | 우선순위 |
|----------|--------|------------|----------|---------|
| IMU | pinky_imu_bno055 | `imu_raw` | ⏳ 예정 | Medium |
| 초음파 센서 | pinky_sensor_adc | `us_sensor/range` | ⏳ 예정 | High |
| 적외선 센서 | pinky_sensor_adc | `ir_sensor/range` | ⏳ 예정 | High |
| 배터리 상태 | pinky_sensor_adc | `batt_state` | ⏳ 예정 | Low |
| 라이다 | Gazebo | `scan` | ⏳ 예정 | Future |
| 카메라 | Gazebo | `camera/image_raw` | ⏳ 예정 | Future |
| LED 제어 | pinky_led | `set_led` | ⏳ 예정 | Low |
| LED 밝기 | pinky_led | `set_brightness` | ⏳ 예정 | Low |
| 램프 제어 | pinky_lamp_control | `set_lamp` | ⏳ 예정 | Low |
| 감정 표시 | pinky_emotion | `set_emotion` | ⏳ 예정 | Low |

**통합 상태 표기:**
- ✅ 완료
- ⏳ 예정
- ❌ 취소됨

### 자율 주행을 위한 센서 통합 계획

자세한 통합 계획은 [TODO.md](TODO.md)를 참조하세요.

**주요 통합 계획:**
1. **Phase 1**: 초음파/적외선 센서를 통한 기본 장애물 회피
2. **Phase 2**: IMU 센서를 통한 자세 보정 및 안정화
3. **Phase 3**: 배터리 모니터링 및 LED/램프 제어
4. **Phase 4**: 라이다 및 SLAM 통합

## 참고

이 패키지는 `/home/guehojung/dev_ws/ROS2/control_tutorials/src/controller_tutorials/controller_tutorials/`의 다음 파일들을 기반으로 작성되었습니다:
- `move_pinky_state_machine.py`
- `qmonitor_pinky_state_machine.py`
- `control_apps.py`

**관련 문서:**
- [개발 현황 리포트](DEVELOPMENT_REPORT.md)
- [센서 통합 TODO](TODO.md)
- [pinky_pro 인터페이스 리포트](../../../../../pinky_pro/ROS2_INTERFACES_REPORT.md)

