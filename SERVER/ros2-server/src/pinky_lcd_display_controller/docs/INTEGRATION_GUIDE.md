# pinky_lcd_display 연동 가이드

## 개요

`pinky_lcd_display` 패키지는 서비스나 액션을 제공하지 않으며, `/lcd/status` 토픽(`std_msgs/String`)을 구독하여 LCD에 내용을 표시합니다.

## 통신 구조

```
[pinky_lcd_display_controller]  --(서비스)-->  [lcd_controller_server]
                                                      |
                                                      | (토픽 발행)
                                                      v
                                            [/lcd/status 토픽]
                                                      |
                                                      | (토픽 구독)
                                                      v
                                            [pinky_lcd_display]
                                                 (lcd_node)
```

## 연동 방법

### 방법 1: 서비스를 통한 제어 (권장)

`pinky_lcd_display_controller` 패키지의 서비스를 사용하여 LCD를 제어합니다.

#### 1.1 서버 노드 실행

**서버 측 (ros2-server)**:
```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
source install/setup.bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

#### 1.2 LCD 노드 실행

**로봇 측 (pinky_pro)**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
# 또는
ros2 run pinky_lcd_display lcd_node
```

#### 1.3 서비스 호출

**서버 측에서**:
```bash
# LCD 내용 설정
ros2 service call /lcd_controller/set_display pinky_lcd_display_interfaces/srv/SetDisplay "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING', 'Waypoint: 2/4'], show_timestamp: true}"

# LCD 화면 지우기
ros2 service call /lcd_controller/clear_display pinky_lcd_display_interfaces/srv/ClearDisplay
```

### 방법 2: 직접 토픽 발행 (간단한 방법)

서비스를 사용하지 않고 직접 토픽을 발행할 수 있습니다.

#### 2.1 LCD 노드 실행

**로봇 측 (pinky_pro)**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

#### 2.2 토픽 발행 명령어

**서버 측 또는 다른 터미널에서**:
```bash
# 기본 형식
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: '타이틀\n라인1\n라인2\n라인3'}"

# 예시 1: 상태 정보 표시
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"

# 예시 2: 배터리 정보만
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Battery Info\nLevel: 85%\nCharging: No'}"

# 예시 3: 네비게이션 정보
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Navigation\nGoal: (1.5, 2.0)\nDistance: 0.3m\nStatus: Moving'}"

# 예시 4: 시스템 정보
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'System Status\nCPU: 45%\nRAM: 60%\nTemp: 42°C'}"
```

#### 2.3 주기적 발행 (테스트용)

```bash
# 1초마다 발행 (Ctrl+C로 중지)
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String "{data: 'Test\nCounter: $(date +%s)'}"
```

### 방법 3: Python 스크립트로 토픽 발행

간단한 Python 스크립트를 만들어 사용할 수 있습니다:

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class LCDPublisher(Node):
    def __init__(self):
        super().__init__('lcd_publisher')
        self.pub = self.create_publisher(String, '/lcd/status', 10)
        
    def publish_status(self, title, lines):
        """LCD 상태를 발행합니다."""
        msg_text = title
        if lines:
            msg_text += '\n' + '\n'.join(lines)
        
        msg = String()
        msg.data = msg_text
        self.pub.publish(msg)
        self.get_logger().info(f"Published:\n{msg_text}")

def main():
    rclpy.init()
    node = LCDPublisher()
    
    # 예시: 상태 정보 발행
    node.publish_status(
        title="Pinky Status",
        lines=["Battery: 78%", "Mode: MOVING", "Waypoint: 2/4"]
    )
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 메시지 형식

### 토픽: `/lcd/status` (std_msgs/String)

**형식**:
```
타이틀 텍스트 (첫 번째 줄, 최대 20자)
본문 라인 1
본문 라인 2
본문 라인 3
...
```

**예시**:
```
Pinky Status
Battery: 78%
Mode: MOVING
Waypoint: 2/4
```

**주의사항**:
- 첫 번째 줄은 타이틀로 표시됩니다
- `\n`으로 줄바꿈을 구분합니다
- 타이틀은 최대 20자로 자동 잘림 (pinky_lcd_display 패키지에서 처리)
- 타임스탬프는 pinky_lcd_display 패키지에서 자동으로 하단에 표시됩니다

## 사용 시나리오

### 시나리오 1: 로봇 상태 모니터링

```bash
# 주기적으로 상태 업데이트 (다른 노드에서)
ros2 topic pub --rate 2 /lcd/status std_msgs/msg/String "{data: 'Robot Status\nBattery: 85%\nMode: IDLE\nTime: $(date +%H:%M:%S)'}"
```

### 시나리오 2: 네비게이션 정보 표시

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Navigation\nGoal: (2.5, 3.0)\nDistance: 1.2m\nETA: 30s'}"
```

### 시나리오 3: 에러 메시지 표시

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'ERROR\nLow Battery!\nPlease charge'}"
```

## 네트워크 설정

서버와 로봇이 다른 머신에서 실행되는 경우:

1. **ROS2 도메인 ID 설정**:
   ```bash
   export ROS_DOMAIN_ID=0  # 서버와 로봇 모두 동일한 ID 사용
   ```

2. **네트워크 확인**:
   ```bash
   # 서버에서
   ros2 topic list
   
   # 로봇에서
   ros2 topic list
   ```

3. **토픽 확인**:
   ```bash
   # 서버에서 로봇의 토픽 확인
   ros2 topic echo /lcd/status
   ```

## 테스트

### 테스트 1: 기본 발행 테스트

```bash
# 터미널 1: LCD 노드 실행 (로봇)
ros2 run pinky_lcd_display lcd_node

# 터미널 2: 토픽 발행 (서버)
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Test\nHello World\nThis is a test'}"

# 터미널 3: 토픽 확인
ros2 topic echo /lcd/status
```

### 테스트 2: 주기적 업데이트 테스트

```bash
# 터미널 1: LCD 노드 실행 (로봇)
ros2 run pinky_lcd_display lcd_node

# 터미널 2: 1초마다 업데이트
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String "{data: 'Status\nTime: $(date +%H:%M:%S)\nCounter: $(seq 1 100 | shuf | head -1)'}"
```

## 문제 해결

### 문제 1: 토픽이 전달되지 않음

**확인 사항**:
```bash
# 토픽이 존재하는지 확인
ros2 topic list | grep lcd

# 토픽 정보 확인
ros2 topic info /lcd/status

# 토픽 발행자 확인
ros2 topic info /lcd/status --verbose
```

**해결 방법**:
- ROS2 도메인 ID가 동일한지 확인
- 네트워크 연결 확인
- 방화벽 설정 확인

### 문제 2: LCD에 표시되지 않음

**확인 사항**:
```bash
# 토픽이 발행되는지 확인
ros2 topic echo /lcd/status

# LCD 노드가 실행 중인지 확인
ros2 node list | grep lcd
```

**해결 방법**:
- LCD 노드가 정상 실행 중인지 확인
- 하드웨어 연결 확인
- 로봇 측 로그 확인

## 참고

- `pinky_lcd_display` 패키지 경로: `~/ros-repo-1/ROS2/rfred/src/pinky_lcd_display`
- 토픽 이름: `/lcd/status`
- 메시지 타입: `std_msgs/String`
- LCD 노드: `pinky_lcd_node`

