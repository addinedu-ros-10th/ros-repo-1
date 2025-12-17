# SERVER / ros2-server

Path: `SERVER/ros2-server`

## Purpose
- ROS2 ↔ HTTP / gRPC 브리지: ROS2 토픽/서비스를 외부 API로 노출
- Pinky 로봇 제어를 위한 ROS2 서버 패키지 모음

## Tech
- Python (rclpy), ROS2, FastAPI / gRPC

## 빠른 시작

### 1. 환경 설정
```bash
# ROS2 환경 소스
source /opt/ros/humble/setup.bash

# 프로젝트 디렉토리로 이동
cd SERVER/ros2-server
```

### 2. 빌드
```bash
# 전체 빌드
colcon build

# 빌드 결과 소스
source install/setup.bash
```

### 3. 실행
```bash
# State Machine 제어 노드
ros2 run pinky_state_machine move_pinky_state_machine

# GUI 모니터링 노드
ros2 run pinky_state_machine qmonitor_pinky_state_machine

# LCD 제어 서버
ros2 run pinky_lcd_display_controller lcd_controller_server
```

## 상세 사용 가이드

**📖 [전체 사용 가이드](docs/guides/USAGE_GUIDE.md)** - 빌드, 실행, 네트워크 설정, 문제 해결 등 모든 내용을 포함합니다.

## 패키지

### pinky_state_machine
State Machine 기반 로봇 제어 패키지
- **기능**: 목표 위치로 이동, PID 제어, State Machine 기반 제어
- **실행**: `ros2 run pinky_state_machine move_pinky_state_machine`
- [패키지 README](src/pinky_state_machine/README.md)
- [State Diagram](src/pinky_state_machine/docs/STATE_DIAGRAM.md)
- [문서 디렉토리](src/pinky_state_machine/docs/)

### pinky_lcd_display_controller
LCD 디스플레이 제어를 위한 서비스 기반 컨트롤러 패키지
- **기능**: LCD 표시 제어, 스타일 설정, 애니메이션 지원
- **실행**: `ros2 run pinky_lcd_display_controller lcd_controller_server`
- [패키지 README](src/pinky_lcd_display_controller/README.md)
- [문서 디렉토리](src/pinky_lcd_display_controller/docs/)

### pinky_lcd_display_interfaces
LCD 디스플레이 제어를 위한 인터페이스 정의 패키지
- **내용**: 서비스, 액션, 메시지 타입 정의
- [인터페이스 동기화 리포트](src/pinky_lcd_display_interfaces/INTERFACE_SYNC_REPORT.md)

## 주요 토픽 및 서비스

### State Machine 토픽
- `/odom` (구독): 로봇의 현재 위치 및 자세
- `/goal_pose` (구독): 목표 위치 및 자세
- `/cmd_vel` (발행): 속도 명령
- `/state` (발행): 현재 상태

### LCD Controller 서비스
- `/lcd_controller/set_display`: LCD 표시 내용 설정
- `/lcd_controller/set_style`: LCD 스타일 설정
- `/lcd_controller/clear_display`: LCD 화면 지우기
- `/lcd_controller/set_layout`: LCD 레이아웃 설정

## Maintainer
- TBD

## Notes
- ROS2 노드 구성과 메시지/서비스 정의를 문서화하세요.
- 각 패키지의 상세 문서는 해당 패키지의 `docs/` 디렉토리에서 확인할 수 있습니다.