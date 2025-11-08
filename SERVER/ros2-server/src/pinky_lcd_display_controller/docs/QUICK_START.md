# pinky_lcd_display 빠른 시작 가이드

## 토픽 발행 명령어 모음

### 기본 사용법

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: '타이틀\n라인1\n라인2'}"
```

### 실용적인 예시

#### 1. 로봇 상태 표시
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"
```

#### 2. 배터리 정보
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Battery Info\nLevel: 85%\nCharging: No\nTime left: 2h 30m'}"
```

#### 3. 네비게이션 정보
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Navigation\nGoal: (1.5, 2.0)\nDistance: 0.3m\nETA: 15s'}"
```

#### 4. 시스템 정보
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'System Status\nCPU: 45%\nRAM: 60%\nTemp: 42°C'}"
```

#### 5. 에러 메시지
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'ERROR\nLow Battery!\nPlease charge'}"
```

#### 6. 주기적 업데이트 (1초마다)
```bash
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String "{data: 'Status\nTime: $(date +%H:%M:%S)'}"
```

#### 7. 화면 지우기
```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: ''}"
```

## 실행 순서

### 1. 로봇 측 (pinky_pro)
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

### 2. 서버 측 (ros2-server)
```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
source install/setup.bash

# 방법 1: 직접 토픽 발행
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING'}"

# 방법 2: 서비스 사용 (컨트롤러 서버 실행 필요)
ros2 run pinky_lcd_display_controller lcd_controller_server
# 다른 터미널에서
ros2 service call /lcd_controller/set_display pinky_lcd_display_interfaces/srv/SetDisplay "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING'], show_timestamp: true}"
```

## 네트워크 설정

서버와 로봇이 다른 머신인 경우:

```bash
# 양쪽 모두 동일한 도메인 ID 설정
export ROS_DOMAIN_ID=0

# 토픽 확인
ros2 topic list | grep lcd
ros2 topic echo /lcd/status
```

## 테스트

```bash
# 터미널 1: LCD 노드 실행 (로봇)
ros2 run pinky_lcd_display lcd_node

# 터미널 2: 토픽 발행 (서버)
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Test\nHello World'}"

# 터미널 3: 토픽 확인
ros2 topic echo /lcd/status
```

