# pinky_lcd_display_controller 사용자 가이드

## 개요

이 문서는 `pinky_lcd_display_controller` 패키지의 모든 인터페이스를 사용하는 방법을 설명합니다. 서비스, 액션, 토픽을 이용한 LCD 제어 방법과 옵셔널 파라미터 사용법을 포함합니다.

## 목차

1. [기본 사용법](#기본-사용법)
2. [서비스 사용법](#서비스-사용법)
3. [액션 사용법](#액션-사용법)
4. [토픽 사용법](#토픽-사용법)
5. [옵셔널 파라미터 가이드](#옵셔널-파라미터-가이드)
6. [테스트 방법](#테스트-방법)

## 기본 사용법

### 1. 패키지 빌드

```bash
cd ~/ros-repo-1/SERVER/ros2-server
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display_controller
source install/setup.bash
```

### 2. 서버 노드 실행

```bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

### 3. LCD 노드 실행 (로봇 측)

```bash
# 로봇에서 실행
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

## 서비스 사용법

### 1. SetDisplay 서비스

**서비스명**: `lcd_controller/set_display`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetDisplay`

#### 기본 사용법

```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING'], show_timestamp: true}"
```

#### 파라미터 설명

- **`title`** (string, 필수): 타이틀 텍스트 (최대 20자)
- **`lines`** (string[], 필수): 본문 라인들 (배열)
- **`show_timestamp`** (bool, 필수): 타임스탬프 표시 여부

#### 사용 예시

**예시 1: 기본 상태 표시**
```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING', 'Waypoint: 2/4'], show_timestamp: true}"
```

**예시 2: 한글 텍스트 표시**
```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: '안녕 핑키', lines: ['배터리: 78%', '모드: 이동 중'], show_timestamp: true}"
```

**예시 3: 타임스탬프 없이 표시**
```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Status', lines: ['Battery: 78%'], show_timestamp: false}"
```

---

### 2. SetStyle 서비스

**서비스명**: `lcd_controller/set_style`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetStyle`

#### 기본 사용법

```bash
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 0, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 20, body_font_size: 18, font_path: ''}"
```

#### 파라미터 설명

**색상 파라미터 (RGB, 0-255)**:
- `bg_color_r/g/b`: 배경 색상
- `title_color_r/g/b`: 타이틀 색상
- `body_color_r/g/b`: 본문 색상
- `timestamp_color_r/g/b`: 타임스탬프 색상

**폰트 파라미터**:
- `title_font_size` (uint8): 타이틀 폰트 크기 (기본값: 20)
- `body_font_size` (uint8): 본문 폰트 크기 (기본값: 18)
- `font_path` (string): 폰트 경로 (빈 문자열이면 기본값 사용)

**참고**: 현재는 스타일 설정을 저장만 하며, 실제 적용을 위해서는 `pinky_lcd_display` 패키지 수정이 필요합니다.

---

### 3. ClearDisplay 서비스

**서비스명**: `lcd_controller/clear_display`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/ClearDisplay`

#### 기본 사용법

```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

#### 파라미터

요청 파라미터 없음

---

### 4. SetLayout 서비스 (구현 예정)

**서비스명**: `lcd_controller/set_layout`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetLayout`

#### 기본 사용법

```bash
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 1, layout_mode: 1, margin_top: 10, margin_bottom: 10, margin_left: 10, margin_right: 10, line_spacing: 24, grid_columns: 1, grid_rows: 1}"
```

#### 파라미터 설명

**필수 파라미터**: 없음 (모두 옵셔널)

**옵셔널 파라미터**:
- `alignment` (uint8, 기본값: 0): 텍스트 정렬
  - 0: LEFT (왼쪽 정렬)
  - 1: CENTER (가운데 정렬)
  - 2: RIGHT (오른쪽 정렬)
- `layout_mode` (uint8, 기본값: 0): 레이아웃 모드
  - 0: SINGLE_LINE (단일 라인)
  - 1: MULTI_LINE (다중 라인)
  - 2: GRID (그리드 모드)
- `margin_top/bottom/left/right` (uint8, 기본값: 10): 여백 (픽셀)
- `line_spacing` (uint8, 기본값: 24): 라인 간격 (픽셀)
- `grid_columns/rows` (uint8, 기본값: 1): 그리드 모드 시 열/행 수

#### 사용 예시

**예시 1: 가운데 정렬 설정**
```bash
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 1}"
```

**예시 2: 여백 및 간격 조정**
```bash
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{margin_top: 20, margin_bottom: 20, margin_left: 15, margin_right: 15, line_spacing: 30}"
```

**예시 3: 그리드 모드 설정**
```bash
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{layout_mode: 2, grid_columns: 2, grid_rows: 2}"
```

---

### 5. SetParameter 서비스 (구현 예정)

**서비스명**: `lcd_controller/set_parameter`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetParameter`

#### 기본 사용법

```bash
ros2 service call /lcd_controller/set_parameter \
  pinky_lcd_display_interfaces/srv/SetParameter \
  "{parameter_name: 'update_rate', parameter_value: '20'}"
```

#### 지원 파라미터 목록

**1. `update_rate`**
- 타입: 숫자 (Hz)
- 기본값: 10
- 범위: 1-60
- 설명: 상태 토픽 발행 주기
- 사용 예시:
  ```bash
  ros2 service call /lcd_controller/set_parameter \
    pinky_lcd_display_interfaces/srv/SetParameter \
    "{parameter_name: 'update_rate', parameter_value: '20'}"
  ```

**2. `qos_depth`**
- 타입: 숫자
- 기본값: 10
- 범위: 1-100
- 설명: QoS 큐 깊이
- 사용 예시:
  ```bash
  ros2 service call /lcd_controller/set_parameter \
    pinky_lcd_display_interfaces/srv/SetParameter \
    "{parameter_name: 'qos_depth', parameter_value: '20'}"
  ```

**3. `debug_mode`**
- 타입: 불린
- 기본값: false
- 설명: 디버그 모드 활성화 (상세 로그 출력)
- 사용 예시:
  ```bash
  # 디버그 모드 활성화
  ros2 service call /lcd_controller/set_parameter \
    pinky_lcd_display_interfaces/srv/SetParameter \
    "{parameter_name: 'debug_mode', parameter_value: 'true'}"
  
  # 디버그 모드 비활성화
  ros2 service call /lcd_controller/set_parameter \
    pinky_lcd_display_interfaces/srv/SetParameter \
    "{parameter_name: 'debug_mode', parameter_value: 'false'}"
  ```

**4. `auto_clear_timeout`**
- 타입: 숫자 (초)
- 기본값: 0 (비활성화)
- 범위: 0-3600
- 설명: 자동 클리어 타임아웃 (지정 시간 후 자동으로 화면 지움)
- 사용 예시:
  ```bash
  # 30초 후 자동 클리어
  ros2 service call /lcd_controller/set_parameter \
    pinky_lcd_display_interfaces/srv/SetParameter \
    "{parameter_name: 'auto_clear_timeout', parameter_value: '30'}"
  
  # 자동 클리어 비활성화
  ros2 service call /lcd_controller/set_parameter \
    pinky_lcd_display_interfaces/srv/SetParameter \
    "{parameter_name: 'auto_clear_timeout', parameter_value: '0'}"
  ```

---

### 6. GetParameter 서비스 (구현 예정)

**서비스명**: `lcd_controller/get_parameter`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/GetParameter`

#### 기본 사용법

```bash
ros2 service call /lcd_controller/get_parameter \
  pinky_lcd_display_interfaces/srv/GetParameter \
  "{parameter_name: 'update_rate'}"
```

#### 사용 예시

**예시 1: update_rate 조회**
```bash
ros2 service call /lcd_controller/get_parameter \
  pinky_lcd_display_interfaces/srv/GetParameter \
  "{parameter_name: 'update_rate'}"
```

**예시 2: debug_mode 조회**
```bash
ros2 service call /lcd_controller/get_parameter \
  pinky_lcd_display_interfaces/srv/GetParameter \
  "{parameter_name: 'debug_mode'}"
```

---

## 액션 사용법

### 1. SetDisplayAction (구현 예정)

**액션명**: `lcd_controller/set_display_action`  
**인터페이스**: `pinky_lcd_display_interfaces/action/SetDisplay`

#### 기본 사용법 (명령줄)

```bash
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Processing', lines: ['Task: Data processing', 'Status: In progress'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"
```

#### 파라미터 설명

**필수 파라미터**:
- `title` (string): 타이틀 텍스트
- `lines` (string[]): 본문 라인들
- `show_timestamp` (bool): 타임스탬프 표시 여부

**옵셔널 파라미터**:
- `duration_ms` (uint32, 기본값: 0): 표시 지속 시간 (밀리초)
  - 0: 무한 (수동으로 취소하거나 다른 표시로 덮어쓸 때까지)
  - 1 이상: 지정된 시간(ms) 후 자동으로 화면 지움
- `animation_type` (uint8, 기본값: 0): 애니메이션 타입
  - 0: NONE - 애니메이션 없음, 즉시 표시
  - 1: FADE_IN - 페이드 인 효과로 표시
  - 2: SLIDE - 슬라이드 효과로 표시

#### 사용 예시

**예시 1: 5초간 표시 후 자동 사라짐**
```bash
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Alert', lines: ['Low battery!', 'Please charge'], show_timestamp: true, duration_ms: 5000, animation_type: 0}"
```

**예시 2: 페이드 인 효과로 표시**
```bash
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Welcome', lines: ['Pinky Robot', 'Ready to serve'], show_timestamp: true, duration_ms: 0, animation_type: 1}"
```

**예시 3: 슬라이드 효과로 표시**
```bash
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Status', lines: ['System OK'], show_timestamp: true, duration_ms: 3000, animation_type: 2}"
```

#### Python 코드 예시

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from pinky_lcd_display_interfaces.action import SetDisplay

class LCDActionClient(Node):
    def __init__(self):
        super().__init__('lcd_action_client')
        self.action_client = ActionClient(self, SetDisplay, 'lcd_controller/set_display_action')
        
    def send_display_goal(self, title, lines, duration_ms=0, animation_type=0):
        """LCD 표시 액션을 전송합니다."""
        # 액션 서버 대기
        self.action_client.wait_for_server()
        
        # Goal 생성
        goal_msg = SetDisplay.Goal()
        goal_msg.title = title
        goal_msg.lines = lines
        goal_msg.show_timestamp = True
        goal_msg.duration_ms = duration_ms
        goal_msg.animation_type = animation_type
        
        # Goal 전송
        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future)
        
        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return
        
        # Result 대기
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        
        result = result_future.result().result
        if result.success:
            self.get_logger().info(f'Action completed: {result.message}')
        else:
            self.get_logger().error(f'Action failed: {result.message}')
    
    def feedback_callback(self, feedback_msg):
        """피드백 콜백"""
        feedback = feedback_msg.feedback
        self.get_logger().info(
            f'Progress: {feedback.progress_percent}% '
            f'({feedback.elapsed_ms}ms elapsed) - {feedback.status_message}'
        )

def main():
    rclpy.init()
    client = LCDActionClient()
    
    # 5초간 알림 표시
    client.send_display_goal(
        title="Alert",
        lines=["Low battery!", "Please charge"],
        duration_ms=5000,
        animation_type=1  # FADE_IN
    )
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

### 2. ScrollTextAction (구현 예정)

**액션명**: `lcd_controller/scroll_text_action`  
**인터페이스**: `pinky_lcd_display_interfaces/action/ScrollText`

#### 기본 사용법

```bash
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'This is a very long text that needs to be scrolled to be displayed properly on the LCD screen', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
```

#### 파라미터 설명

**필수 파라미터**:
- `text` (string): 스크롤할 텍스트

**옵셔널 파라미터**:
- `scroll_speed_ms` (uint32, 기본값: 50): 스크롤 속도 (밀리초)
  - 기본값: 50ms (20 FPS)
  - 범위: 10ms ~ 1000ms
  - 값이 작을수록 빠른 스크롤
  - 권장값: 30-100ms
- `direction` (uint8, 기본값: 0): 스크롤 방향
  - 0: LEFT (왼쪽으로 스크롤)
  - 1: RIGHT (오른쪽으로 스크롤)
  - 2: UP (위로 스크롤)
  - 3: DOWN (아래로 스크롤)
- `repeat_count` (uint32, 기본값: 1): 반복 횟수
  - 기본값: 1 (1회 반복)
  - 0: 무한 반복
  - 1 이상: 지정된 횟수만큼 반복

#### 사용 예시

**예시 1: 왼쪽으로 빠르게 스크롤 (30ms)**
```bash
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text here', scroll_speed_ms: 30, direction: 0, repeat_count: 1}"
```

**예시 2: 오른쪽으로 느리게 스크롤 (100ms)**
```bash
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text here', scroll_speed_ms: 100, direction: 1, repeat_count: 1}"
```

**예시 3: 무한 반복 스크롤**
```bash
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text here', scroll_speed_ms: 50, direction: 0, repeat_count: 0}"
```

---

## 토픽 사용법

### 1. LCDStatus 토픽 (구현 예정)

**토픽명**: `/lcd_controller/status`  
**메시지 타입**: `pinky_lcd_display_interfaces/msg/LCDStatus`

#### 구독 방법

```bash
ros2 topic echo /lcd_controller/status
```

#### 메시지 구조

```python
std_msgs/Header header
bool is_active                  # LCD 활성 상태
string current_title            # 현재 타이틀
string[] current_lines         # 현재 라인들
bool show_timestamp             # 타임스탬프 표시 여부
uint64 last_update_time         # 마지막 업데이트 시간 (나노초)
uint8 display_mode             # 표시 모드 (옵션)
uint32 error_code               # 에러 코드 (0이면 정상)
string error_message             # 에러 메시지
```

#### 옵셔널 파라미터: `display_mode`
- **0: NORMAL** (기본값) - 일반 표시 모드
- **1: SCROLL** - 스크롤 표시 모드
- **2: ANIMATION** - 애니메이션 표시 모드

#### Python 코드 예시

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.msg import LCDStatus

class LCDStatusMonitor(Node):
    def __init__(self):
        super().__init__('lcd_status_monitor')
        self.subscription = self.create_subscription(
            LCDStatus,
            '/lcd_controller/status',
            self.status_callback,
            10
        )
    
    def status_callback(self, msg):
        """상태 메시지 콜백"""
        self.get_logger().info(f'LCD Status:')
        self.get_logger().info(f'  Active: {msg.is_active}')
        self.get_logger().info(f'  Title: {msg.current_title}')
        self.get_logger().info(f'  Lines: {msg.current_lines}')
        self.get_logger().info(f'  Display Mode: {msg.display_mode}')
        if msg.error_code != 0:
            self.get_logger().warn(f'  Error: {msg.error_code} - {msg.error_message}')

def main():
    rclpy.init()
    monitor = LCDStatusMonitor()
    rclpy.spin(monitor)
    monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

### 2. LCDEvent 토픽 (구현 예정)

**토픽명**: `/lcd_controller/events`  
**메시지 타입**: `pinky_lcd_display_interfaces/msg/LCDEvent`

#### 구독 방법

```bash
ros2 topic echo /lcd_controller/events
```

#### 메시지 구조

```python
std_msgs/Header header
uint8 event_type                # 이벤트 타입 (옵션)
uint64 timestamp                # 이벤트 발생 시간
string message                  # 이벤트 메시지
```

#### 옵셔널 파라미터: `event_type`
- **0: DISPLAY_STARTED** - 표시 시작
- **1: DISPLAY_ENDED** - 표시 종료
- **2: ERROR** - 에러 발생
- **3: CLEARED** - 화면 지워짐
- **4: PAGE_SWITCHED** - 페이지 전환
- **5: ANIMATION_STARTED** - 애니메이션 시작
- **6: ANIMATION_ENDED** - 애니메이션 종료

#### Python 코드 예시

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.msg import LCDEvent

class LCDEventMonitor(Node):
    def __init__(self):
        super().__init__('lcd_event_monitor')
        self.subscription = self.create_subscription(
            LCDEvent,
            '/lcd_controller/events',
            self.event_callback,
            10
        )
    
    def event_callback(self, msg):
        """이벤트 메시지 콜백"""
        event_types = {
            0: 'DISPLAY_STARTED',
            1: 'DISPLAY_ENDED',
            2: 'ERROR',
            3: 'CLEARED',
            4: 'PAGE_SWITCHED',
            5: 'ANIMATION_STARTED',
            6: 'ANIMATION_ENDED'
        }
        event_name = event_types.get(msg.event_type, 'UNKNOWN')
        self.get_logger().info(f'LCD Event: {event_name} - {msg.message}')

def main():
    rclpy.init()
    monitor = LCDEventMonitor()
    rclpy.spin(monitor)
    monitor.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

---

## 옵셔널 파라미터 가이드

### SetDisplayAction - animation_type

**설명**: LCD 표시 시 사용할 애니메이션 효과를 지정합니다.

**옵션**:
- **0: NONE** (기본값)
  - 특징: 애니메이션 없음, 즉시 표시
  - 사용 시나리오: 빠른 정보 업데이트가 필요한 경우
  - 성능: 가장 빠름, CPU 사용량 최소
  
- **1: FADE_IN**
  - 특징: 페이드 인 효과로 부드럽게 나타남
  - 사용 시나리오: 사용자 주의를 끌고 싶을 때, 알림 메시지
  - 성능: 중간, 약간의 CPU 사용
  - 지속 시간: 약 300-500ms

- **2: SLIDE**
  - 특징: 슬라이드 효과로 나타남
  - 사용 시나리오: 화면 전환 시, 동적인 느낌을 주고 싶을 때
  - 성능: 중간, 약간의 CPU 사용
  - 지속 시간: 약 400-600ms

**사용 예시**:
```bash
# 즉시 표시 (빠른 업데이트)
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Status', lines: ['Updating...'], show_timestamp: true, duration_ms: 0, animation_type: 0}"

# 페이드 인 효과 (알림)
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Alert', lines: ['Important!'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"

# 슬라이드 효과 (화면 전환)
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'New Page', lines: ['Content'], show_timestamp: true, duration_ms: 0, animation_type: 2}"
```

---

### SetLayout - alignment

**설명**: 텍스트의 수평 정렬 방식을 지정합니다.

**옵션**:
- **0: LEFT** (기본값)
  - 특징: 왼쪽 정렬
  - 사용 시나리오: 일반적인 텍스트 표시, 읽기 편함
  - 레이아웃: 텍스트가 왼쪽 여백부터 시작

- **1: CENTER**
  - 특징: 가운데 정렬
  - 사용 시나리오: 제목, 중요 메시지, 대칭적인 레이아웃
  - 레이아웃: 텍스트가 화면 중앙에 배치

- **2: RIGHT**
  - 특징: 오른쪽 정렬
  - 사용 시나리오: 숫자, 시간, 오른쪽 정렬이 자연스러운 경우
  - 레이아웃: 텍스트가 오른쪽 여백까지 정렬

**사용 예시**:
```bash
# 왼쪽 정렬 (기본)
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 0}"

# 가운데 정렬 (제목)
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 1}"

# 오른쪽 정렬 (시간)
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 2}"
```

---

### SetLayout - layout_mode

**설명**: 텍스트 레이아웃 모드를 지정합니다.

**옵션**:
- **0: SINGLE_LINE** (기본값)
  - 특징: 단일 라인 모드, 모든 텍스트를 한 줄로 표시
  - 사용 시나리오: 짧은 메시지, 상태 표시
  - 제한: 긴 텍스트는 잘림

- **1: MULTI_LINE**
  - 특징: 다중 라인 모드, 여러 줄로 표시
  - 사용 시나리오: 일반적인 텍스트 표시, 여러 정보 표시
  - 장점: 많은 정보를 표시 가능

- **2: GRID**
  - 특징: 그리드 모드, 격자 형태로 배치
  - 사용 시나리오: 구조화된 정보, 표 형태 데이터
  - 파라미터: `grid_columns`, `grid_rows` 필요

**사용 예시**:
```bash
# 단일 라인 모드
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{layout_mode: 0}"

# 다중 라인 모드
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{layout_mode: 1}"

# 그리드 모드 (2x2)
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{layout_mode: 2, grid_columns: 2, grid_rows: 2}"
```

---

### ScrollTextAction - direction

**설명**: 스크롤 방향을 지정합니다.

**옵션**:
- **0: LEFT** (기본값)
  - 특징: 왼쪽으로 스크롤 (텍스트가 오른쪽에서 왼쪽으로 이동)
  - 사용 시나리오: 일반적인 텍스트 스크롤
  - 시각적 효과: 자연스러운 읽기 방향

- **1: RIGHT**
  - 특징: 오른쪽으로 스크롤 (텍스트가 왼쪽에서 오른쪽으로 이동)
  - 사용 시나리오: 역방향 스크롤이 필요한 경우
  - 시각적 효과: 역방향 이동

- **2: UP**
  - 특징: 위로 스크롤 (텍스트가 아래에서 위로 이동)
  - 사용 시나리오: 세로 스크롤이 필요한 경우
  - 시각적 효과: 위로 올라가는 효과

- **3: DOWN**
  - 특징: 아래로 스크롤 (텍스트가 위에서 아래로 이동)
  - 사용 시나리오: 세로 스크롤이 필요한 경우
  - 시각적 효과: 아래로 내려가는 효과

**사용 예시**:
```bash
# 왼쪽 스크롤
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"

# 오른쪽 스크롤
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text', scroll_speed_ms: 50, direction: 1, repeat_count: 1}"
```

---

### ScrollTextAction - scroll_speed_ms

**설명**: 스크롤 속도를 밀리초 단위로 지정합니다.

**옵션 범위**: 10ms ~ 1000ms

**권장값**:
- **10-30ms**: 매우 빠른 스크롤
  - 특징: 빠른 정보 전달
  - 사용 시나리오: 긴급 알림, 빠른 업데이트
  - 주의: 너무 빠르면 읽기 어려움

- **30-50ms** (기본값: 50ms): 적당한 속도
  - 특징: 읽기 가능한 속도
  - 사용 시나리오: 일반적인 스크롤 텍스트
  - 권장: 대부분의 경우

- **50-100ms**: 느린 스크롤
  - 특징: 천천히 스크롤
  - 사용 시나리오: 강조하고 싶은 메시지, 읽기 쉬운 속도
  - 주의: 너무 느리면 지루할 수 있음

- **100-1000ms**: 매우 느린 스크롤
  - 특징: 매우 천천히 스크롤
  - 사용 시나리오: 특별한 효과, 장시간 표시
  - 주의: 사용자 경험 저하 가능

**사용 예시**:
```bash
# 빠른 스크롤 (30ms)
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text', scroll_speed_ms: 30, direction: 0, repeat_count: 1}"

# 기본 속도 (50ms)
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"

# 느린 스크롤 (100ms)
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Long text', scroll_speed_ms: 100, direction: 0, repeat_count: 1}"
```

---

### SwitchPage - transition_type

**설명**: 페이지 전환 시 사용할 전환 효과를 지정합니다.

**옵션**:
- **0: INSTANT** (기본값)
  - 특징: 즉시 전환, 효과 없음
  - 사용 시나리오: 빠른 페이지 전환, 성능이 중요한 경우
  - 성능: 가장 빠름

- **1: FADE**
  - 특징: 페이드 효과 (이전 페이지가 사라지고 새 페이지가 나타남)
  - 사용 시나리오: 부드러운 전환, 사용자 경험 개선
  - 지속 시간: 권장 300-500ms

- **2: SLIDE_LEFT**
  - 특징: 왼쪽으로 슬라이드 (새 페이지가 왼쪽에서 나타남)
  - 사용 시나리오: 왼쪽 방향 페이지 전환
  - 지속 시간: 권장 400-600ms

- **3: SLIDE_RIGHT**
  - 특징: 오른쪽으로 슬라이드 (새 페이지가 오른쪽에서 나타남)
  - 사용 시나리오: 오른쪽 방향 페이지 전환
  - 지속 시간: 권장 400-600ms

- **4: SLIDE_UP**
  - 특징: 위로 슬라이드 (새 페이지가 아래에서 나타남)
  - 사용 시나리오: 위 방향 페이지 전환
  - 지속 시간: 권장 400-600ms

- **5: SLIDE_DOWN**
  - 특징: 아래로 슬라이드 (새 페이지가 위에서 나타남)
  - 사용 시나리오: 아래 방향 페이지 전환
  - 지속 시간: 권장 400-600ms

**사용 예시**:
```bash
# 즉시 전환
ros2 service call /lcd_controller/switch_page \
  pinky_lcd_display_interfaces/srv/SwitchPage \
  "{page_id: 'page1', transition_type: 0, transition_duration_ms: 0}"

# 페이드 효과 (500ms)
ros2 service call /lcd_controller/switch_page \
  pinky_lcd_display_interfaces/srv/SwitchPage \
  "{page_id: 'page1', transition_type: 1, transition_duration_ms: 500}"

# 왼쪽 슬라이드 (600ms)
ros2 service call /lcd_controller/switch_page \
  pinky_lcd_display_interfaces/srv/SwitchPage \
  "{page_id: 'page1', transition_type: 2, transition_duration_ms: 600}"
```

---

## 테스트 방법

### 자동 테스트

자동 테스트 스크립트는 다음 섹션을 참조하세요: [자동 테스트 코드](#자동-테스트-코드)

### 수동 테스트

#### 1. 기본 서비스 테스트

**테스트 1: SetDisplay 서비스**
```bash
# 터미널 1: 서버 실행
ros2 run pinky_lcd_display_controller lcd_controller_server

# 터미널 2: 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1', 'Line 2'], show_timestamp: true}"

# 예상 결과: LCD에 "Test" 타이틀과 "Line 1", "Line 2"가 표시됨
```

**테스트 2: ClearDisplay 서비스**
```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay

# 예상 결과: LCD 화면이 지워짐
```

#### 2. 액션 테스트 (구현 예정)

**테스트 3: SetDisplayAction**
```bash
# 5초간 표시 후 자동 사라짐
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Alert', lines: ['Test message'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"

# 예상 결과: 
# - 페이드 인 효과로 표시
# - 5초 후 자동으로 화면 지워짐
# - 피드백 메시지가 주기적으로 출력됨
```

#### 3. 토픽 테스트 (구현 예정)

**테스트 4: LCDStatus 토픽 구독**
```bash
# 터미널 1: 상태 모니터링
ros2 topic echo /lcd_controller/status

# 터미널 2: 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Status test'], show_timestamp: true}"

# 예상 결과: 상태 토픽에 현재 LCD 상태가 발행됨
```

**테스트 5: LCDEvent 토픽 구독**
```bash
# 터미널 1: 이벤트 모니터링
ros2 topic echo /lcd_controller/events

# 터미널 2: 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Event test'], show_timestamp: true}"

# 예상 결과: DISPLAY_STARTED 이벤트가 발행됨
```

---

## 자동 테스트 코드

자동 테스트 코드는 별도 파일로 제공됩니다. [TEST_GUIDE.md](TEST_GUIDE.md)를 참조하세요.

---

## 문제 해결

### 서비스가 응답하지 않는 경우

1. 서버 노드가 실행 중인지 확인:
   ```bash
   ros2 node list | grep lcd_controller
   ```

2. 서비스가 등록되어 있는지 확인:
   ```bash
   ros2 service list | grep lcd_controller
   ```

3. 네트워크 연결 확인:
   ```bash
   ros2 topic list
   ```

### 액션이 완료되지 않는 경우

1. 액션 서버가 실행 중인지 확인:
   ```bash
   ros2 action list | grep lcd_controller
   ```

2. Goal이 수락되었는지 확인:
   ```bash
   ros2 action info /lcd_controller/set_display_action
   ```

### 토픽이 발행되지 않는 경우

1. 토픽이 존재하는지 확인:
   ```bash
   ros2 topic list | grep lcd_controller
   ```

2. 토픽 정보 확인:
   ```bash
   ros2 topic info /lcd_controller/status
   ```

3. 발행자 확인:
   ```bash
   ros2 topic info /lcd_controller/status --verbose
   ```

---

## 참고 문서

- [구현 계획서](IMPLEMENTATION_PLAN.md) - 구현 대상 목록 및 구현 현황
- [테스트 가이드](TEST_GUIDE.md) - 자동 테스트 코드 및 테스트 방법
- [개발 현황 리포트](DEVELOPMENT_STATUS.md) - 개발 현황 및 통신 방법

