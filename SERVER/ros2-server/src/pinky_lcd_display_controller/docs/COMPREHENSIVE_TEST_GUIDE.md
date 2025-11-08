# LCD 디스플레이 시스템 종합 테스트 가이드

## 개요

이 문서는 현재 브랜치(`feat/SERVER/ros2-server__update_general_function_control__RP-50__update_pinky_lcd_display_control_func`)와 `base/ROS2/rfred` 브랜치의 모든 LCD 디스플레이 기능에 대한 종합 테스트 가이드를 제공합니다.

**작성 기준**: 실제 소스 코드를 직접 확인하여 작성되었습니다.

## 시스템 아키텍처

### 현재 브랜치 구조

```
[클라이언트]
    |
    | 서비스 호출
    v
[pinky_lcd_display_controller] (현재 브랜치)
    | - 서비스 서버: SetDisplay, SetStyle, ClearDisplay
    | - 토픽 발행: /lcd/status (std_msgs/String)
    |
    | 토픽 발행
    v
[pinky_lcd_display] (base/ROS2/rfred 브랜치)
    | - 토픽 구독: /lcd/status (std_msgs/String)
    | - 서비스 서버: SetDisplay, SetStyle, ClearDisplay, SetLayout
    | - 액션 서버: SetDisplayAction, ScrollTextAction
    | - 토픽 발행: /lcd_controller/status, /lcd_controller/events
    |
    | 하드웨어 제어
    v
[LCD 디스플레이]
```

### 통신 방식 요약

| 통신 방식 | 현재 브랜치 | base/ROS2/rfred 브랜치 |
|----------|------------|----------------------|
| **서비스** | ✅ 제공 (3개) | ✅ 제공 (4개) |
| **액션** | ❌ 없음 | ✅ 제공 (2개) |
| **토픽 (발행)** | ✅ /lcd/status | ✅ /lcd_controller/status, /lcd_controller/events |
| **토픽 (구독)** | ❌ 없음 | ✅ /lcd/status |

## 사전 준비

### 1. 빌드

#### 현재 브랜치 빌드

```bash
cd ~/ros-repo-1/SERVER/ros2-server
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display_controller
source install/setup.bash
```

#### base/ROS2/rfred 브랜치 빌드 (로봇 측)

```bash
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display
source install/setup.bash
```

### 2. 노드 실행

#### 현재 브랜치: 컨트롤러 서버 실행

```bash
# 터미널 1: 컨트롤러 서버
ros2 run pinky_lcd_display_controller lcd_controller_server
```

#### base/ROS2/rfred 브랜치: LCD 디스플레이 노드 실행 (로봇 측)

```bash
# 터미널 2: LCD 디스플레이 노드 (로봇에서 실행)
ros2 launch pinky_lcd_display lcd_display.launch.py
# 또는
ros2 run pinky_lcd_display lcd_node
```

### 3. 인터페이스 확인

```bash
# 서비스 목록 확인
ros2 service list | grep lcd_controller

# 액션 목록 확인 (base/ROS2/rfred 브랜치에서만)
ros2 action list | grep lcd_controller

# 토픽 목록 확인
ros2 topic list | grep lcd
```

## 테스트 1: 서비스 테스트 (현재 브랜치)

### 1.1 SetDisplay 서비스

**목적**: LCD에 표시할 내용을 설정합니다.

**서비스명**: `/lcd_controller/set_display`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetDisplay`

**요청 파라미터**:
- `title` (string): 타이틀 텍스트 (최대 20자 권장)
- `lines` (string[]): 본문 라인들
- `show_timestamp` (bool): 타임스탬프 표시 여부

**테스트 명령**:

```bash
# 기본 테스트
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING'], show_timestamp: true}"

# 여러 라인 테스트
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'System Info', lines: ['CPU: 45%', 'Memory: 2.1GB', 'Disk: 85%'], show_timestamp: true}"

# 타임스탬프 없이 표시
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Alert', lines: ['Low battery!'], show_timestamp: false}"

# 한글 텍스트 테스트 (한글 폰트가 설치된 경우)
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: '상태', lines: ['배터리: 78%', '모드: 이동'], show_timestamp: true}"
```

**예상 결과**:
- 서비스 응답: `success: true, message: "Display updated: N lines"`
- LCD 화면에 타이틀과 라인들이 표시됨
- 타임스탬프가 설정된 경우 하단에 시간 표시

**코드 확인**:
- 구현 위치: `pinky_lcd_display_controller/lcd_controller_server.py:126-156`
- 동작: 서비스 요청을 받아 `/lcd/status` 토픽에 `std_msgs/String` 메시지 발행

### 1.2 SetStyle 서비스

**목적**: LCD 표시 스타일을 설정합니다.

**서비스명**: `/lcd_controller/set_style`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetStyle`

**요청 파라미터**:
- `bg_color_r/g/b` (uint8): 배경 색상 (RGB, 0-255)
- `title_color_r/g/b` (uint8): 타이틀 색상 (RGB, 0-255)
- `body_color_r/g/b` (uint8): 본문 색상 (RGB, 0-255)
- `timestamp_color_r/g/b` (uint8): 타임스탬프 색상 (RGB, 0-255)
- `title_font_size` (uint8): 타이틀 폰트 크기
- `body_font_size` (uint8): 본문 폰트 크기
- `font_path` (string): 폰트 파일 경로 (빈 문자열이면 기본값 사용)

**테스트 명령**:

```bash
# 기본 스타일 설정 (검은 배경, 녹색 타이틀, 흰색 본문)
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 0, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 20, body_font_size: 18, font_path: ''}"

# 파란 배경, 노란 타이틀, 검은 본문
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 255, title_color_r: 255, title_color_g: 255, title_color_b: 0, body_color_r: 0, body_color_g: 0, body_color_b: 0, timestamp_color_r: 255, timestamp_color_g: 255, timestamp_color_b: 255, title_font_size: 24, body_font_size: 20, font_path: ''}"

# 한글 폰트 경로 지정
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 255, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 20, body_font_size: 18, font_path: '/home/pinky/ros-repo-1/SERVER/ros2-server/src/pinky_lcd_display_controller/fonts/maruburi/TTF/MaruBuri-Regular.ttf'}"
```

**예상 결과**:
- 서비스 응답: `success: true, message: "Style settings saved..."`
- **주의**: 현재 브랜치의 `pinky_lcd_display_controller`는 스타일을 저장만 하고, 실제 적용은 `base/ROS2/rfred` 브랜치의 `pinky_lcd_display` 패키지에서 이루어집니다.

**코드 확인**:
- 구현 위치: `pinky_lcd_display_controller/lcd_controller_server.py:158-203`
- 동작: 스타일 설정을 내부 변수에 저장 (실제 적용은 `pinky_lcd_display` 패키지 필요)

### 1.3 ClearDisplay 서비스

**목적**: LCD 화면을 지웁니다.

**서비스명**: `/lcd_controller/clear_display`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/ClearDisplay`

**테스트 명령**:

```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

**예상 결과**:
- 서비스 응답: `success: true, message: "Display cleared"`
- LCD 화면이 지워짐

**코드 확인**:
- 구현 위치: `pinky_lcd_display_controller/lcd_controller_server.py:205-225`
- 동작: 빈 문자열을 `/lcd/status` 토픽에 발행

## 테스트 2: 서비스 테스트 (base/ROS2/rfred 브랜치)

### 2.1 SetDisplay 서비스 (base/ROS2/rfred)

**차이점**: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display` 패키지는 직접 서비스를 제공합니다.

**테스트 명령**:

```bash
# base/ROS2/rfred 브랜치에서 직접 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Direct Call', lines: ['From base branch', 'Service test'], show_timestamp: true}"
```

**예상 결과**:
- LCD에 직접 표시됨
- 이벤트 토픽에 `DISPLAY_STARTED` 이벤트 발행

### 2.2 SetLayout 서비스 (base/ROS2/rfred 전용)

**목적**: 레이아웃을 설정합니다.

**서비스명**: `/lcd_controller/set_layout`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetLayout`

**요청 파라미터**:
- `alignment` (uint8): 텍스트 정렬 (0: LEFT, 1: CENTER, 2: RIGHT)
- `layout_mode` (uint8): 레이아웃 모드 (0: SINGLE_LINE, 1: MULTI_LINE, 2: GRID)
- `margin_top/bottom/left/right` (uint8): 여백 (픽셀)
- `line_spacing` (uint8): 라인 간격 (픽셀)
- `grid_columns/rows` (uint8): 그리드 모드 시 열/행 수

**테스트 명령**:

```bash
# 가운데 정렬, 다중 라인 모드
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 1, layout_mode: 1, margin_top: 10, margin_bottom: 10, margin_left: 10, margin_right: 10, line_spacing: 24, grid_columns: 1, grid_rows: 1}"

# 왼쪽 정렬, 그리드 모드
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 0, layout_mode: 2, margin_top: 5, margin_bottom: 5, margin_left: 5, margin_right: 5, line_spacing: 20, grid_columns: 2, grid_rows: 2}"
```

**예상 결과**:
- 레이아웃 설정이 적용됨
- 이후 표시되는 내용이 새 레이아웃으로 렌더링됨

**코드 확인**:
- 구현 위치: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display/lcd_node.py`
- `lcd_manager.set_layout()` 호출

## 테스트 3: 액션 테스트 (base/ROS2/rfred 브랜치 전용)

### 3.1 SetDisplayAction

**목적**: 시간 제한이 있는 LCD 표시 및 애니메이션 효과를 제공합니다.

**액션명**: `/lcd_controller/set_display_action`  
**인터페이스**: `pinky_lcd_display_interfaces/action/SetDisplay`

**Goal 파라미터**:
- `title` (string): 타이틀 텍스트
- `lines` (string[]): 본문 라인들
- `show_timestamp` (bool): 타임스탬프 표시 여부
- `duration_ms` (uint32): 표시 지속 시간 (밀리초, 0이면 무한)
- `animation_type` (uint8): 0: NONE, 1: FADE_IN, 2: SLIDE

**Feedback**:
- `elapsed_ms` (uint32): 경과 시간 (밀리초)
- `progress_percent` (uint8): 진행률 (0-100)
- `status_message` (string): 상태 메시지

**Result**:
- `success` (bool): 성공 여부
- `message` (string): 결과 메시지
- `actual_duration_ms` (uint32): 실제 표시 시간

**테스트 명령**:

```bash
# 페이드 인 효과, 5초간 표시
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Processing', lines: ['Task: Data processing', 'Status: In progress'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"

# 슬라이드 효과, 3초간 표시
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Alert', lines: ['Warning message', 'Please check'], show_timestamp: true, duration_ms: 3000, animation_type: 2}"

# 애니메이션 없이 10초간 표시
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Info', lines: ['Displaying for 10 seconds'], show_timestamp: true, duration_ms: 10000, animation_type: 0}"

# 무한 표시 (duration_ms: 0)
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Continuous', lines: ['This will stay'], show_timestamp: true, duration_ms: 0, animation_type: 1}"
```

**피드백 확인**:

```bash
# 피드백을 받으면서 실행
ros2 action send_goal --feedback /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Progress', lines: ['Task running'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"
```

**예상 결과**:
- 애니메이션 효과가 적용되어 표시됨
- 지정된 시간 후 자동으로 화면이 지워짐 (duration_ms > 0인 경우)
- 피드백으로 진행 상황 확인 가능
- 이벤트 토픽에 `ANIMATION_STARTED`, `ANIMATION_ENDED` 이벤트 발행

**코드 확인**:
- 구현 위치: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display/lcd_node.py`
- `lcd_manager.show_status_with_animation()` 호출
- 애니메이션 타입: 'fade_in', 'slide'

### 3.2 ScrollTextAction

**목적**: 긴 텍스트를 스크롤하여 표시합니다.

**액션명**: `/lcd_controller/scroll_text_action`  
**인터페이스**: `pinky_lcd_display_interfaces/action/ScrollText`

**Goal 파라미터**:
- `text` (string): 스크롤할 텍스트
- `scroll_speed_ms` (uint32): 스크롤 속도 (밀리초)
- `direction` (uint8): 0: LEFT, 1: RIGHT, 2: UP, 3: DOWN
- `repeat_count` (uint32): 반복 횟수 (0이면 무한)

**Feedback**:
- `current_position` (uint32): 현재 스크롤 위치
- `progress_percent` (uint8): 진행률

**Result**:
- `success` (bool): 성공 여부
- `message` (string): 결과 메시지
- `total_scroll_time_ms` (uint32): 전체 스크롤 시간

**테스트 명령**:

```bash
# 왼쪽으로 스크롤, 1회 반복
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'This is a very long text that needs to be scrolled across the screen', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"

# 오른쪽으로 스크롤, 3회 반복
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Scrolling text from right to left', scroll_speed_ms: 30, direction: 1, repeat_count: 3}"

# 빠른 스크롤, 무한 반복
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Infinite scroll test', scroll_speed_ms: 20, direction: 0, repeat_count: 0}"
```

**피드백 확인**:

```bash
ros2 action send_goal --feedback /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long scrolling text with feedback', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
```

**예상 결과**:
- 텍스트가 지정된 방향으로 스크롤됨
- 피드백으로 현재 위치와 진행률 확인 가능
- 반복 횟수만큼 반복 (0이면 무한)

**코드 확인**:
- 구현 위치: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display/lcd_node.py`
- `lcd_manager.show_scroll_text()` 호출
- 스크롤 방향: LEFT(0), RIGHT(1) 지원 (UP/DOWN은 미구현 가능성)

## 테스트 4: 토픽 테스트

### 4.1 /lcd/status 토픽 (std_msgs/String)

**목적**: 기본 토픽 기반 LCD 제어

**토픽명**: `/lcd/status`  
**타입**: `std_msgs/msg/String`

**테스트 명령**:

```bash
# 한 번 발행
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"

# 주기적 발행 (1초마다)
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String "{data: 'Status\nTime: $(date +%H:%M:%S)'}"

# 여러 라인 예시
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'System Info\nCPU: 45%\nMemory: 2.1GB\nDisk: 85%'}"
```

**예상 결과**:
- LCD에 텍스트가 표시됨
- 첫 번째 줄은 타이틀로 표시
- `\n`으로 줄바꿈 구분

**코드 확인**:
- 구독 위치: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display/lcd_node.py`
- `status_callback()` 함수에서 처리

### 4.2 /lcd_controller/status 토픽 (LCDStatus) - base/ROS2/rfred 전용

**목적**: LCD 상태 정보를 실시간으로 발행

**토픽명**: `/lcd_controller/status`  
**타입**: `pinky_lcd_display_interfaces/msg/LCDStatus`

**메시지 필드**:
- `header` (std_msgs/Header): 헤더 정보
- `is_active` (bool): LCD 활성 상태
- `current_title` (string): 현재 타이틀
- `current_lines` (string[]): 현재 라인들
- `show_timestamp` (bool): 타임스탬프 표시 여부
- `last_update_time` (uint64): 마지막 업데이트 시간
- `display_mode` (uint8): 0: NORMAL, 1: SCROLL, 2: ANIMATION
- `error_code` (uint32): 에러 코드
- `error_message` (string): 에러 메시지

**테스트 명령**:

```bash
# 토픽 구독
ros2 topic echo /lcd_controller/status

# 토픽 정보 확인
ros2 topic info /lcd_controller/status

# 토픽 타입 확인
ros2 topic type /lcd_controller/status
```

**예상 결과**:
- 1Hz 주기로 상태 정보 발행
- 현재 표시 중인 내용과 상태 정보 확인 가능

**코드 확인**:
- 발행 위치: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display/lcd_node.py`
- `publish_status()` 함수에서 1초마다 발행

### 4.3 /lcd_controller/events 토픽 (LCDEvent) - base/ROS2/rfred 전용

**목적**: LCD 이벤트 정보를 발행

**토픽명**: `/lcd_controller/events`  
**타입**: `pinky_lcd_display_interfaces/msg/LCDEvent`

**메시지 필드**:
- `header` (std_msgs/Header): 헤더 정보
- `event_type` (uint8): 이벤트 타입
  - 0: DISPLAY_STARTED
  - 1: DISPLAY_ENDED
  - 2: ERROR
  - 3: CLEARED
  - 4: PAGE_SWITCHED
  - 5: ANIMATION_STARTED
  - 6: ANIMATION_ENDED
- `timestamp` (uint64): 이벤트 발생 시간
- `message` (string): 이벤트 메시지

**테스트 명령**:

```bash
# 이벤트 구독
ros2 topic echo /lcd_controller/events

# 이벤트 정보 확인
ros2 topic info /lcd_controller/events
```

**예상 결과**:
- 서비스/액션 호출 시 해당 이벤트가 발행됨
- 이벤트 타입과 메시지로 상태 추적 가능

**코드 확인**:
- 발행 위치: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display/lcd_node.py`
- `publish_event()` 함수에서 이벤트 발생 시 발행

## 테스트 5: 통합 테스트 시나리오

### 5.1 기본 워크플로우 테스트

**목적**: 전체 시스템이 정상 동작하는지 확인

**단계**:

1. **노드 실행**
   ```bash
   # 터미널 1: 컨트롤러 서버 (현재 브랜치)
   ros2 run pinky_lcd_display_controller lcd_controller_server
   
   # 터미널 2: LCD 디스플레이 노드 (base/ROS2/rfred 브랜치, 로봇에서)
   ros2 run pinky_lcd_display lcd_node
   ```

2. **기본 표시 테스트**
   ```bash
   ros2 service call /lcd_controller/set_display \
     pinky_lcd_display_interfaces/srv/SetDisplay \
     "{title: 'Test', lines: ['Line 1', 'Line 2'], show_timestamp: true}"
   ```

3. **상태 확인**
   ```bash
   ros2 topic echo /lcd_controller/status --once
   ```

4. **화면 지우기**
   ```bash
   ros2 service call /lcd_controller/clear_display \
     pinky_lcd_display_interfaces/srv/ClearDisplay
   ```

### 5.2 스타일 변경 테스트 (base/ROS2/rfred 브랜치)

**단계**:

1. **스타일 설정**
   ```bash
   ros2 service call /lcd_controller/set_style \
     pinky_lcd_display_interfaces/srv/SetStyle \
     "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 255, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 24, body_font_size: 20, font_path: ''}"
   ```

2. **내용 표시**
   ```bash
   ros2 service call /lcd_controller/set_display \
     pinky_lcd_display_interfaces/srv/SetDisplay \
     "{title: 'Styled', lines: ['New style applied'], show_timestamp: true}"
   ```

3. **결과 확인**: LCD에 새 스타일이 적용되어 표시됨

### 5.3 애니메이션 테스트 (base/ROS2/rfred 브랜치)

**단계**:

1. **페이드 인 효과**
   ```bash
   ros2 action send_goal /lcd_controller/set_display_action \
     pinky_lcd_display_interfaces/action/SetDisplay \
     "{title: 'Fade In', lines: ['Animation test'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"
   ```

2. **슬라이드 효과**
   ```bash
   ros2 action send_goal /lcd_controller/set_display_action \
     pinky_lcd_display_interfaces/action/SetDisplay \
     "{title: 'Slide', lines: ['Slide animation'], show_timestamp: true, duration_ms: 3000, animation_type: 2}"
   ```

3. **결과 확인**: 각 애니메이션 효과가 적용되어 표시됨

### 5.4 스크롤 텍스트 테스트 (base/ROS2/rfred 브랜치)

**단계**:

1. **스크롤 실행**
   ```bash
   ros2 action send_goal --feedback /lcd_controller/scroll_text_action \
     pinky_lcd_display_interfaces/action/ScrollText \
     "{text: 'This is a very long text that needs to be scrolled across the LCD display screen', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
   ```

2. **피드백 확인**: 진행 상황이 실시간으로 표시됨

3. **결과 확인**: 텍스트가 스크롤되어 표시됨

## 테스트 6: 에러 케이스 테스트

### 6.1 잘못된 서비스 호출

```bash
# 존재하지 않는 서비스
ros2 service call /lcd_controller/invalid_service \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: [], show_timestamp: true}"

# 잘못된 파라미터 타입 (예: 문자열을 숫자로)
# 이 경우 ROS2가 자동으로 검증
```

### 6.2 빈 내용 테스트

```bash
# 빈 타이틀
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: '', lines: ['Line 1'], show_timestamp: true}"

# 빈 라인 배열
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Title', lines: [], show_timestamp: true}"
```

### 6.3 긴 텍스트 테스트

```bash
# 매우 긴 타이틀 (20자 초과)
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'This is a very long title that exceeds the recommended 20 characters', lines: ['Line 1'], show_timestamp: true}"

# 많은 라인
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Many Lines', lines: ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5', 'Line 6', 'Line 7', 'Line 8'], show_timestamp: true}"
```

## 테스트 7: 성능 테스트

### 7.1 빠른 연속 호출

```bash
# 여러 서비스를 빠르게 연속 호출
for i in {1..10}; do
  ros2 service call /lcd_controller/set_display \
    pinky_lcd_display_interfaces/srv/SetDisplay \
    "{title: 'Test $i', lines: ['Rapid call test'], show_timestamp: true}"
  sleep 0.1
done
```

### 7.2 토픽 발행 속도 테스트

```bash
# 높은 주기로 토픽 발행
ros2 topic pub --rate 10 /lcd/status std_msgs/msg/String "{data: 'High rate test'}"
```

## 테스트 체크리스트

### 현재 브랜치 (pinky_lcd_display_controller)

- [ ] SetDisplay 서비스 호출 성공
- [ ] SetStyle 서비스 호출 성공 (스타일 저장 확인)
- [ ] ClearDisplay 서비스 호출 성공
- [ ] /lcd/status 토픽 발행 확인
- [ ] 한글 텍스트 표시 (한글 폰트 설치 시)
- [ ] 여러 라인 표시
- [ ] 타임스탬프 표시/숨김

### base/ROS2/rfred 브랜치 (pinky_lcd_display)

- [ ] SetDisplay 서비스 직접 호출
- [ ] SetStyle 서비스로 스타일 적용 확인
- [ ] SetLayout 서비스로 레이아웃 변경 확인
- [ ] ClearDisplay 서비스로 화면 지우기
- [ ] SetDisplayAction (FADE_IN) 실행
- [ ] SetDisplayAction (SLIDE) 실행
- [ ] SetDisplayAction (NONE) 실행
- [ ] SetDisplayAction duration_ms 동작 확인
- [ ] ScrollTextAction (LEFT) 실행
- [ ] ScrollTextAction (RIGHT) 실행
- [ ] ScrollTextAction 반복 동작 확인
- [ ] /lcd_controller/status 토픽 구독
- [ ] /lcd_controller/events 토픽 구독
- [ ] 이벤트 타입 확인 (DISPLAY_STARTED, ANIMATION_STARTED 등)

## 문제 해결

### 서비스 타입 인식 실패

**에러**: `The passed service type is invalid`

**해결**:
```bash
# 인터페이스 패키지 빌드 확인
cd ~/ros-repo-1/SERVER/ros2-server
colcon build --packages-select pinky_lcd_display_interfaces
source install/setup.bash

# 인터페이스 확인
ros2 interface show pinky_lcd_display_interfaces/srv/SetDisplay
```

### 액션 타입 인식 실패

**에러**: `The passed action type is invalid`

**해결**:
```bash
# base/ROS2/rfred 브랜치에서 인터페이스 빌드 확인
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display_interfaces
source install/setup.bash

# 액션 타입 확인
ros2 interface show pinky_lcd_display_interfaces/action/SetDisplay
```

### LCD에 표시되지 않음

**확인 사항**:
1. `pinky_lcd_display` 노드가 실행 중인지 확인
2. `/lcd/status` 토픽이 발행되는지 확인: `ros2 topic echo /lcd/status`
3. 로봇의 LCD 하드웨어 연결 확인
4. 로그 확인: `ros2 topic echo /rosout`

## 참고 자료

- [pinky_lcd_display_controller README](../README.md)
- [개발 현황 문서](DEVELOPMENT_STATUS.md)
- [인터페이스 동기화 리포트](../../pinky_lcd_display_interfaces/INTERFACE_SYNC_REPORT.md)

---

**작성일**: 2025년 11월 8일  
**작성 기준**: 실제 소스 코드 직접 확인  
**검증 상태**: 코드 기반 작성 완료

