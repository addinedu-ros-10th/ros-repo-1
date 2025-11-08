# pinky_lcd_display 패키지 사용 방법

**패키지 경로**: `/home/guehojung/Documents/Project/FINAL/development/tmp/ros-repo-1/ROS2/rfred/src/pinky_lcd_display`

## 패키지 개요

`pinky_lcd_display`는 Pinky 로봇의 LCD 디스플레이를 제어하는 ROS2 패키지입니다. 이 패키지는 토픽 기반 통신을 사용하며, 서비스나 액션을 제공하지 않습니다.

## 패키지 구조

```
pinky_lcd_display/
├── package.xml
├── setup.py
├── setup.cfg
├── launch/
│   └── lcd_display.launch.py      # Launch 파일
├── pinky_lcd_display/
│   ├── __init__.py
│   ├── lcd_node.py                 # 메인 LCD 노드
│   ├── lcd_manager.py              # LCD 관리 클래스
│   └── test_publisher_node.py      # 테스트용 퍼블리셔 노드
└── resource/
    └── pinky_lcd_display
```

## 주요 컴포넌트

### 1. LCDDisplayNode (`lcd_node.py`)
- **역할**: `/lcd/status` 토픽을 구독하여 LCD에 내용을 표시
- **토픽**: `/lcd/status` (std_msgs/String) - 구독
- **실행 명령**: `ros2 run pinky_lcd_display lcd_node`

### 2. LCDDisplayManager (`lcd_manager.py`)
- **역할**: LCD 하드웨어 제어 및 이미지 렌더링
- **기능**:
  - PIL(Pillow)을 사용한 이미지 생성
  - 텍스트 렌더링 (타이틀, 본문, 타임스탬프)
  - LCD 하드웨어 제어 (`pinky_lcd` 모듈 사용)

### 3. LCDTestPublisher (`test_publisher_node.py`)
- **역할**: 테스트용 메시지 발행 노드
- **실행 명령**: `ros2 run pinky_lcd_display test_pub`

## 빌드 방법

```bash
cd /home/guehojung/Documents/Project/FINAL/development/tmp/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display
source install/setup.bash
```

## 실행 방법

### 방법 1: Launch 파일 사용 (권장)

```bash
cd /home/guehojung/Documents/Project/FINAL/development/tmp/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

### 방법 2: 직접 노드 실행

```bash
cd /home/guehojung/Documents/Project/FINAL/development/tmp/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 run pinky_lcd_display lcd_node
```

## 토픽 사용법

### 토픽 정보

- **토픽 이름**: `/lcd/status`
- **메시지 타입**: `std_msgs/String`
- **방향**: 구독 (Subscriber)
- **QoS**: 10

### 메시지 형식

메시지는 여러 줄 텍스트 형식입니다:

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

### 토픽 발행 명령어

#### 기본 발행
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: '타이틀\n라인1\n라인2\n라인3'}"
```

#### 실용적인 예시

**1. 로봇 상태 표시**
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"
```

**2. 배터리 정보**
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Battery Info\nLevel: 85%\nCharging: No\nTime left: 2h 30m'}"
```

**3. 네비게이션 정보**
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Navigation\nGoal: (1.5, 2.0)\nDistance: 0.3m\nETA: 15s'}"
```

**4. 시스템 정보**
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'System Status\nCPU: 45%\nRAM: 60%\nTemp: 42°C'}"
```

**5. 에러 메시지**
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'ERROR\nLow Battery!\nPlease charge'}"
```

**6. 주기적 업데이트 (1초마다)**
```bash
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String "{data: 'Status\nTime: $(date +%H:%M:%S)'}"
```

**7. 화면 지우기**
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: ''}"
```

## 테스트

### 테스트 퍼블리셔 실행

```bash
# 터미널 1: LCD 노드 실행
ros2 run pinky_lcd_display lcd_node

# 터미널 2: 테스트 퍼블리셔 실행
ros2 run pinky_lcd_display test_pub
```

테스트 퍼블리셔는 1초마다 다음 정보를 자동으로 발행합니다:
- 타이틀: "Pinky Status"
- 배터리: 80%에서 시작하여 1씩 감소
- 모드: MOVING/IDLE 번갈아가며 표시
- 웨이포인트: 1/4 ~ 4/4 순환

## LCD 표시 형식

### 레이아웃

```
┌─────────────────────────────┐
│ 타이틀 (녹색, 20px)          │  ← 첫 번째 줄
│                             │
│ 본문 라인 1 (흰색, 18px)     │  ← 두 번째 줄 이후
│ 본문 라인 2 (흰색, 18px)     │
│ 본문 라인 3 (흰색, 18px)     │
│ ...                         │
│                             │
│ 2025-01-30 14:30:00 (파란색)│  ← 타임스탬프 (자동)
└─────────────────────────────┘
```

### 색상 설정 (현재 하드코딩)

- **배경**: 검은색 (0, 0, 0)
- **타이틀**: 녹색 (0, 255, 0)
- **본문**: 흰색 (255, 255, 255)
- **타임스탬프**: 파란색 (100, 100, 255)

### 폰트 설정 (현재 하드코딩)

- **타이틀 폰트 크기**: 20px
- **본문 폰트 크기**: 18px
- **폰트 경로**: `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`

### 화면 크기

- **너비**: 320px
- **높이**: 240px

## 동작 원리

1. **토픽 구독**: `LCDDisplayNode`가 `/lcd/status` 토픽을 구독
2. **메시지 파싱**: 받은 문자열을 `\n`으로 분리하여 타이틀과 본문으로 구분
3. **이미지 생성**: `LCDDisplayManager`가 PIL을 사용하여 이미지 생성
4. **LCD 표시**: `pinky_lcd` 모듈을 통해 하드웨어 LCD에 이미지 표시

## 의존성

### ROS2 패키지
- `rclpy`: ROS2 Python 클라이언트
- `std_msgs`: 표준 메시지 타입

### Python 패키지
- `PIL` (Pillow): 이미지 생성 및 처리
- `pinky_lcd`: LCD 하드웨어 제어 모듈 (로봇에 설치되어 있어야 함)

## 제한사항

1. **서비스/액션 없음**: 이 패키지는 토픽만 사용하며 서비스나 액션을 제공하지 않습니다.
2. **스타일 하드코딩**: 색상, 폰트 크기 등이 하드코딩되어 있어 동적 변경이 불가능합니다.
3. **타이틀 길이 제한**: 타이틀은 최대 20자로 자동 잘림
4. **하드웨어 의존성**: `pinky_lcd` 모듈이 설치되어 있어야 하며, 실제 로봇 하드웨어가 필요합니다.

## 문제 해결

### 문제 1: LCD가 표시되지 않음

**확인 사항**:
```bash
# 노드가 실행 중인지 확인
ros2 node list | grep lcd

# 토픽이 발행되는지 확인
ros2 topic echo /lcd/status

# 하드웨어 연결 확인
# pinky_lcd 모듈이 설치되어 있는지 확인
```

**해결 방법**:
- `pinky_lcd` 모듈이 설치되어 있는지 확인
- LCD 하드웨어 연결 확인
- 로봇 측 로그 확인

### 문제 2: 토픽이 전달되지 않음

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
- ROS2 도메인 ID가 동일한지 확인 (`export ROS_DOMAIN_ID=0`)
- 네트워크 연결 확인
- 방화벽 설정 확인

### 문제 3: PIL/Pillow 오류

**해결 방법**:
```bash
sudo apt-get install python3-pil
# 또는
pip3 install Pillow
```

## Python 코드 예시

### 다른 노드에서 토픽 발행

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class MyLCDPublisher(Node):
    def __init__(self):
        super().__init__('my_lcd_publisher')
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
    node = MyLCDPublisher()
    
    # 상태 정보 발행
    node.publish_status(
        title="Pinky Status",
        lines=["Battery: 78%", "Mode: MOVING", "Waypoint: 2/4"]
    )
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 참고

- 패키지 경로: `/home/guehojung/Documents/Project/FINAL/development/tmp/ros-repo-1/ROS2/rfred/src/pinky_lcd_display`
- 토픽 이름: `/lcd/status`
- 메시지 타입: `std_msgs/String`
- LCD 노드: `pinky_lcd_node`
- 테스트 퍼블리셔: `lcd_test_publisher`

