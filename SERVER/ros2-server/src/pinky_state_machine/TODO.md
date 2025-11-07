# pinky_state_machine 자율 주행 센서 통합 TODO

**작성일**: 2025-01-30  
**목적**: 자율 주행을 위한 pinky_pro 센서 기능 통합

---

## 개요

현재 `pinky_state_machine`은 기본적인 목표 지향 주행 기능만 구현되어 있습니다. 자율 주행을 위해서는 장애물 회피, 경로 계획, 환경 인식 등의 기능이 필요하며, 이를 위해 `pinky_pro` 패키지의 다양한 센서들을 통합해야 합니다.

---

## pinky_pro 활용 가능 센서 및 기능

### 1. 센서 (Sensors)

#### 1.1 IMU 센서 (`pinky_imu_bno055`)
- **토픽**: `imu_raw` (sensor_msgs/msg/Imu)
- **발행 주기**: 100Hz (기본값)
- **프레임 ID**: `imu_link` (기본값)
- **제공 데이터**:
  - 가속도 (linear_acceleration)
  - 각속도 (angular_velocity)
  - 방향 (orientation, quaternion)
- **활용 방안**:
  - ✅ 자세 보정 (오도메트리 드리프트 보정)
  - ✅ 급격한 움직임 감지
  - ✅ 낙상 감지
  - ⏳ 자세 안정화 제어

#### 1.2 초음파 센서 (`pinky_sensor_adc`)
- **토픽**: `us_sensor/range` (sensor_msgs/msg/Range)
- **발행 주기**: 20Hz (기본값)
- **프레임 ID**: `ultrasonic_link`
- **측정 범위**: 0.02m ~ 3.0m
- **활용 방안**:
  - ⏳ 전방 장애물 감지
  - ⏳ 긴급 정지 기능
  - ⏳ 장애물 회피

#### 1.3 적외선 센서 (`pinky_sensor_adc`)
- **토픽**: `ir_sensor/range` (std_msgs/msg/UInt16MultiArray)
- **발행 주기**: 20Hz
- **센서 개수**: 3개 (배열 형태)
- **활용 방안**:
  - ⏳ 근거리 장애물 감지 (초음파 센서 보완)
  - ⏳ 다방향 장애물 감지
  - ⏳ 낮은 장애물 감지

#### 1.4 배터리 상태 (`pinky_sensor_adc`)
- **토픽**: `batt_state` (sensor_msgs/msg/BatteryState)
- **발행 주기**: 20Hz
- **프레임 ID**: `base_link`
- **활용 방안**:
  - ⏳ 배터리 잔량 모니터링
  - ⏳ 저전력 모드 전환
  - ⏳ 충전소 복귀 경로 계획

#### 1.5 라이다 센서 (Gazebo 시뮬레이션)
- **토픽**: `scan` (sensor_msgs/msg/LaserScan)
- **활용 방안**:
  - ⏳ 360도 장애물 감지
  - ⏳ SLAM (Simultaneous Localization and Mapping)
  - ⏳ 정밀한 경로 계획

#### 1.6 카메라 (Gazebo 시뮬레이션)
- **토픽**: `camera/image_raw` (sensor_msgs/msg/Image)
- **활용 방안**:
  - ⏳ 비주얼 SLAM
  - ⏳ 객체 인식
  - ⏳ 사람 추적

### 2. 제어 가능 기능 (Controllable Features)

#### 2.1 LED 제어 (`pinky_led`)
- **서비스**: `set_led` (pinky_interfaces/srv/SetLed)
- **기능**:
  - 픽셀 단위 LED 제어
  - 전체 LED 채우기
  - LED 초기화
- **활용 방안**:
  - ⏳ 상태 표시 (주행 중, 장애물 감지, 목표 도달 등)
  - ⏳ 디버깅 정보 표시

#### 2.2 LED 밝기 제어 (`pinky_led`)
- **서비스**: `set_brightness` (pinky_interfaces/srv/SetBrightness)
- **활용 방안**:
  - ⏳ 환경에 따른 밝기 조절

#### 2.3 램프 제어 (`pinky_lamp_control`)
- **서비스**: `set_lamp` (pinky_interfaces/srv/SetLamp)
- **모드**:
  - 0: 꺼짐
  - 1: 켜짐
  - 2: 깜빡임
  - 3: 어둡게/밝게 조절
- **활용 방안**:
  - ⏳ 주행 상태 표시
  - ⏳ 경고 신호

#### 2.4 감정 표시 (`pinky_emotion`)
- **서비스**: `set_emotion` (pinky_interfaces/srv/Emotion)
- **지원 감정**: hello, basic, angry, bored, fun, happy, interest, sad
- **활용 방안**:
  - ⏳ 사용자 인터랙션
  - ⏳ 상태 피드백

### 3. 네비게이션 기능 (`pinky_navigation`)

#### 3.1 SLAM (Simultaneous Localization and Mapping)
- **Launch**: `map_building.launch.xml`
- **활용 방안**:
  - ⏳ 실시간 맵 생성
  - ⏳ 위치 추적

#### 3.2 Navigation2
- **Launch**: `bringup_launch.xml`
- **활용 방안**:
  - ⏳ 글로벌 경로 계획
  - ⏳ 로컬 경로 계획
  - ⏳ 동적 장애물 회피

---

## 통합 우선순위

### Phase 1: 기본 장애물 회피 (High Priority)
1. ⏳ 초음파 센서 통합 (`us_sensor/range`)
   - 전방 장애물 감지
   - 긴급 정지 기능
   - 기본 장애물 회피 로직

2. ⏳ 적외선 센서 통합 (`ir_sensor/range`)
   - 다방향 장애물 감지
   - 근거리 장애물 감지

3. ⏳ State Machine에 장애물 회피 상태 추가
   - `AvoidObstacle` 상태 추가
   - 장애물 감지 시 회피 경로 생성

### Phase 2: 자세 보정 및 안정화 (Medium Priority)
1. ⏳ IMU 센서 통합 (`imu_raw`)
   - 오도메트리 드리프트 보정
   - 자세 안정화 제어
   - 급격한 움직임 감지

### Phase 3: 고급 기능 (Low Priority)
1. ⏳ 배터리 모니터링 (`batt_state`)
   - 저전력 모드
   - 충전소 복귀

2. ⏳ LED/램프 제어 통합
   - 상태 표시
   - 사용자 피드백

3. ⏳ 감정 표시 통합
   - 사용자 인터랙션

### Phase 4: SLAM 및 Navigation2 통합 (Future)
1. ⏳ 라이다 센서 통합
2. ⏳ SLAM 통합
3. ⏳ Navigation2 통합

---

## 구현 가이드

### 센서 통합 패턴

각 센서는 다음 패턴으로 통합할 수 있습니다:

```python
# 1. 센서 토픽 구독
self.create_subscription(
    SensorMsgType,
    'sensor_topic',
    self.sensor_callback,
    10
)

# 2. 센서 데이터 저장
def sensor_callback(self, msg):
    self.sensor_data = msg
    # State Machine에 영향 주기

# 3. State Machine에서 센서 데이터 활용
class MoveToGoalState(ControllerState):
    def update(self, current_pose):
        # 장애물 감지 확인
        if self.controller.has_obstacle():
            return self.avoid_obstacle()
        # 일반 주행 로직
        ...
```

### 장애물 회피 State 추가

```python
class AvoidObstacleState(ControllerState):
    def update(self, current_pose):
        # 장애물 회피 로직
        # 회피 완료 후 원래 상태로 복귀
        ...
```

---

## 참고 자료

- pinky_pro 인터페이스 리포트: `/home/guehojung/Documents/Project/FINAL/development/pinky_pro/ROS2_INTERFACES_REPORT.md`
- pinky_pro README: `/home/guehojung/Documents/Project/FINAL/development/pinky_pro/src/pinky_pro/README.md`

---

## 상태 표기

- ✅ 완료
- ⏳ 진행 중 / 예정
- ❌ 취소됨

