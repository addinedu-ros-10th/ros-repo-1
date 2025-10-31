# ROS2 pinky_pro Final Project - 커스텀 패키지 개발 브랜치

이 브랜치는 ROS2 pinky_pro Final project의 커스텀 패키지 개발을 위한 브랜치입니다.

## 개요

Pinky 로봇을 위한 ROS2 커스텀 패키지들을 개발하고 관리합니다.
각 패키지는 독립적으로 개발되며, 표준 ROS2 패키지 구조와 패턴을 따릅니다.

## 개발 가이드

새로운 패키지를 개발할 때는 `pinky_lcd_display` 패키지를 샘플로 참고하여 동일한 구조와 패턴을 따르세요.

### 샘플 패키지 참고사항
- 패키지 구조: `src/<package_name>/`
- launch 파일 위치: `src/<package_name>/launch/`
- setup.py에서 launch 파일을 data_files에 등록 필수
- 표준 ROS2 패키지 메타데이터 설정 (package.xml)

## 패키지 및 통신 인터페이스 관리

### Topics

| 패키지 | 토픽 이름 | 메시지 타입 | Publisher | Subscriber | 설명 |
|--------|---------|------------|-----------|------------|------|
| pinky_lcd_display | `/lcd/status` | `std_msgs/String` | - | `pinky_lcd_node` | LCD 상태 표시용 메시지. 첫 줄은 타이틀, 이후 줄은 본문으로 표시됨 |

### Services

현재 등록된 서비스가 없습니다.

### Actions

현재 등록된 액션이 없습니다.

## 패키지 목록

### pinky_lcd_display
- **설명**: Pinky 로봇의 LCD 디스플레이를 제어하는 패키지
- **노드**: `lcd_node` (LCD 상태 표시), `test_pub` (테스트용 퍼블리셔)
- **구독 토픽**: `/lcd/status` (std_msgs/String)
- **Launch 파일**: `lcd_display.launch.py`

## 빌드 및 실행

```bash
# 워크스페이스 빌드
cd ~/ros-repo-1/ROS2/rfred
colcon build

# 환경 소스
source install/setup.bash

# 패키지 실행 예시
ros2 launch pinky_lcd_display lcd_display.launch.py
```

## 개발 규칙

1. **Launch 파일 배포**: 모든 launch 파일은 `setup.py`의 `data_files`에 반드시 등록
2. **패키지 구조**: 표준 ROS2 패키지 구조 준수
3. **의존성 관리**: `package.xml`에 필요한 의존성 명시
4. **통신 인터페이스 문서화**: 새로운 topic/service/action 추가 시 본 README 업데이트 필수

