# SERVER / ros2-server

Path: `SERVER/ros2-server`

## Purpose
- ROS2 ↔ HTTP / gRPC 브리지: ROS2 토픽/서비스를 외부 API로 노출

## Tech
- Python (rclpy), ROS2, FastAPI / gRPC

## Getting started (placeholder)
1. Ensure ROS2 environment is sourced
2. Run the bridge service

## Maintainer
- TBD

## Notes
- ROS2 노드 구성과 메시지/서비스 정의를 문서화하세요.

## 문서

프로젝트 관련 문서는 `docs/` 디렉토리에서 확인할 수 있습니다:
- [연동 에러 분석](docs/INTEGRATION_ERROR_ANALYSIS.md) - 패키지 간 연동 에러 분석 및 해결 가이드

## 패키지

### pinky_lcd_display_controller
LCD 디스플레이 제어를 위한 서비스 기반 컨트롤러 패키지
- [패키지 README](src/pinky_lcd_display_controller/README.md)
- [문서 디렉토리](src/pinky_lcd_display_controller/docs/)

### pinky_state_machine
State Machine 기반 제어 패키지
- [패키지 README](src/pinky_state_machine/README.md)
- [문서 디렉토리](src/pinky_state_machine/docs/)