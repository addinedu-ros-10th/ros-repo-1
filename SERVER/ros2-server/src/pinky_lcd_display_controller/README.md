# pinky_lcd_display_controller 패키지

Pinky 로봇의 LCD 디스플레이를 제어하기 위한 서비스 기반 컨트롤러 패키지입니다.

## 개요

이 패키지는 `pinky_lcd_display` 패키지를 서비스 인터페이스를 통해 제어할 수 있도록 하는 서버를 제공합니다. ROS2 서비스를 통해 LCD 표시 내용과 스타일을 동적으로 제어할 수 있습니다.

## 패키지 구조

```
pinky_lcd_display_controller/
├── package.xml
├── setup.py
├── setup.cfg
├── README.md
├── docs/                           # 문서 디렉토리
│   ├── DEVELOPMENT_REPORT.md      # 개발 현황 리포트
│   ├── FEATURES.md                  # 제어 가능한 기능
│   ├── INTEGRATION_GUIDE.md         # 연동 가이드
│   ├── INTERFACE_PROPOSAL.md        # 인터페이스 확장 제안서
│   ├── PINKY_LCD_DISPLAY_USAGE.md   # 사용 가이드
│   ├── QUICK_START.md               # 빠른 시작 가이드
│   └── SUMMARY.md                   # 개발 요약
├── resource/
│   └── pinky_lcd_display_controller
└── pinky_lcd_display_controller/
    ├── __init__.py
    └── lcd_controller_server.py    # 서비스 서버 노드
```

## 의존성

- `rclpy`: ROS2 Python 클라이언트
- `std_msgs`: 표준 메시지 타입
- `pinky_lcd_display_interfaces`: 서비스 인터페이스 정의

## 빌드 방법

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display_controller
source install/setup.bash
```

## 사용 방법

### 1. 서버 노드 실행

```bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

### 2. 서비스 호출 예시

#### LCD 내용 설정

```bash
ros2 service call /lcd_controller/set_display pinky_lcd_display_interfaces/srv/SetDisplay "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING', 'Waypoint: 2/4'], show_timestamp: true}"
```

#### LCD 스타일 설정

```bash
ros2 service call /lcd_controller/set_style pinky_lcd_display_interfaces/srv/SetStyle "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 0, title_color_g: 255, title_color_g: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 20, body_font_size: 18, font_path: ''}"
```

#### LCD 화면 지우기

```bash
ros2 service call /lcd_controller/clear_display pinky_lcd_display_interfaces/srv/ClearDisplay
```

## 제공 서비스

### 1. `lcd_controller/set_display`
LCD에 표시할 내용을 설정합니다.

**요청 (Request):**
- `title` (string): 타이틀 텍스트 (최대 20자)
- `lines` (string[]): 본문 라인들
- `show_timestamp` (bool): 타임스탬프 표시 여부

**응답 (Response):**
- `success` (bool): 성공 여부
- `message` (string): 응답 메시지

### 2. `lcd_controller/set_style`
LCD 표시 스타일을 설정합니다.

**요청 (Request):**
- `bg_color_r/g/b` (uint8): 배경 색상 (RGB, 0-255)
- `title_color_r/g/b` (uint8): 타이틀 색상 (RGB, 0-255)
- `body_color_r/g/b` (uint8): 본문 색상 (RGB, 0-255)
- `timestamp_color_r/g/b` (uint8): 타임스탬프 색상 (RGB, 0-255)
- `title_font_size` (uint8): 타이틀 폰트 크기
- `body_font_size` (uint8): 본문 폰트 크기
- `font_path` (string): 폰트 경로 (빈 문자열이면 기본값 사용)

**응답 (Response):**
- `success` (bool): 성공 여부
- `message` (string): 응답 메시지

**주의**: 현재 `pinky_lcd_display` 패키지는 스타일을 동적으로 변경하는 기능이 없습니다. 이 서비스는 스타일 설정을 저장만 하고, 실제 적용을 위해서는 `pinky_lcd_display` 패키지 수정이 필요합니다.

### 3. `lcd_controller/clear_display`
LCD 화면을 지웁니다.

**요청 (Request):** 없음

**응답 (Response):**
- `success` (bool): 성공 여부
- `message` (string): 응답 메시지

## pinky_lcd_display 패키지 연동

이 패키지는 `pinky_lcd_display` 패키지의 `/lcd/status` 토픽에 `std_msgs/String` 메시지를 발행하여 LCD를 제어합니다.

`pinky_lcd_display` 패키지가 실행 중이어야 합니다:

```bash
# 로봇 측에서 실행
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
# 또는
ros2 run pinky_lcd_display lcd_node
```

## 직접 토픽 발행 방법

`pinky_lcd_display` 패키지는 서비스나 액션을 제공하지 않으며, `/lcd/status` 토픽을 구독합니다.
서비스를 사용하지 않고 직접 토픽을 발행할 수도 있습니다:

```bash
# 기본 형식
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: '타이틀\n라인1\n라인2\n라인3'}"

# 예시 1: 상태 정보 표시
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"

# 예시 2: 배터리 정보만
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Battery Info\nLevel: 85%\nCharging: No'}"

# 예시 3: 네비게이션 정보
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Navigation\nGoal: (1.5, 2.0)\nDistance: 0.3m\nStatus: Moving'}"

# 주기적 발행 (1초마다, Ctrl+C로 중지)
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String "{data: 'Status\nTime: $(date +%H:%M:%S)'}"
```

**메시지 형식**:
- 첫 번째 줄은 타이틀로 표시됩니다 (최대 20자)
- `\n`으로 줄바꿈을 구분합니다
- 타임스탬프는 자동으로 하단에 표시됩니다

자세한 연동 방법은 [docs/INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md)를 참조하세요.

## 제어 가능한 피쳐

자세한 내용은 [docs/FEATURES.md](docs/FEATURES.md)를 참조하세요.

## 추가 문서

- [개발 현황 문서](docs/DEVELOPMENT_STATUS.md) - **LCD 기본 기능 호출 및 사용 중심의 개발 현황 문서**
- [개발 현황 리포트](docs/DEVELOPMENT_REPORT.md) - 프로젝트 개발 현황 및 통신 방식 분석
- [인터페이스 확장 제안서](docs/INTERFACE_PROPOSAL.md) - 향후 개발을 위한 인터페이스 제안
- [한글 폰트 패치 가이드](docs/KOREAN_FONT_PATCH_GUIDE.md) - 로봇에 한글 폰트 지원 추가 방법
- [빠른 시작 가이드](docs/QUICK_START.md) - 빠른 시작을 위한 가이드
- [사용 가이드](docs/PINKY_LCD_DISPLAY_USAGE.md) - 상세 사용 방법
- [개발 요약](docs/SUMMARY.md) - 개발 작업 요약
- [연동 에러 분석](docs/INTEGRATION_ERROR_ANALYSIS.md) - 패키지 간 연동 에러 분석 및 해결 가이드

## 한글 폰트 지원

이 패키지는 한글 폰트 파일을 포함하고 있지만, **실제 한글 표시를 위해서는 `pinky_lcd_display` 패키지에 패치가 필요합니다.**

자세한 패치 방법은 [한글 폰트 패치 가이드](docs/KOREAN_FONT_PATCH_GUIDE.md)를 참조하세요.

**중요**: `pinky_lcd_display_controller`는 단순히 토픽에 메시지를 발행하는 역할만 하며, 실제 폰트 렌더링은 로봇에 설치된 `pinky_lcd_display` 패키지에서 이루어집니다.

