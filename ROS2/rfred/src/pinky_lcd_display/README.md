# pinky_lcd_display 패키지

Pinky 로봇의 LCD 디스플레이를 ROS2 토픽을 통해 제어하는 패키지입니다.

## 개요

이 패키지는 `/lcd/status` 토픽을 구독하여 LCD 디스플레이에 텍스트 정보를 표시합니다. 한글 폰트를 지원하여 한글 텍스트도 정상적으로 표시할 수 있습니다.

**인터페이스 통합**: `pinky_lcd_display_interfaces` 패키지를 통해 서비스, 액션, 토픽 인터페이스를 제공합니다. `pinky_lcd_display_controller`가 클라이언트로 동작하고, 이 패키지가 서버로 동작합니다.

## 패키지 구조

```
pinky_lcd_display/
├── package.xml
├── setup.py
├── setup.cfg
├── LICENSE
├── README.md
├── docs/                          # 문서 디렉토리
│   ├── DEVELOPMENT_STATUS.md      # 개발 현황 리포트
│   ├── IMPLEMENTATION_PLAN.md     # 인터페이스 구현 계획서
│   ├── IMPLEMENTATION_SUMMARY.md  # 구현 요약
│   ├── USER_GUIDE.md              # 사용자 가이드
│   └── TEST_GUIDE.md              # 테스트 가이드
├── fonts/                         # 한글 폰트 파일
│   └── maruburi/TTF/
│       ├── MaruBuri-Regular.ttf
│       ├── MaruBuri-Bold.ttf
│       ├── MaruBuri-SemiBold.ttf
│       ├── MaruBuri-Light.ttf
│       └── MaruBuri-ExtraLight.ttf
├── launch/
│   └── lcd_display.launch.py      # Launch 파일
├── resource/
│   └── pinky_lcd_display
├── pinky_lcd_display/
│   ├── __init__.py
│   ├── lcd_node.py                # 메인 LCD 노드
│   ├── lcd_manager.py             # LCD 관리 클래스 (한글 폰트 지원)
│   └── test_publisher_node.py     # 테스트용 퍼블리셔 노드
└── test/
    ├── test_copyright.py
    ├── test_flake8.py
    └── test_pep257.py
```

## 의존성

- `rclpy`: ROS2 Python 클라이언트
- `std_msgs`: 표준 메시지 타입
- `python3-pil`: PIL/Pillow 이미지 처리 라이브러리
- `ament_index_python`: 패키지 경로 탐색 (한글 폰트 경로 탐색용)
- `pinky_lcd_display_interfaces`: 인터페이스 패키지 (서비스, 액션, 메시지 정의)

### 의존성에 대한 중요 설명

**`pinky_lcd_display_interfaces` 패키지는**:
- ✅ **인터페이스 정의 패키지**입니다 (타입 정의만 포함)
- ✅ **별도의 노드를 실행할 필요가 없습니다**
- ✅ **빌드 시 필수**입니다 (타입 정의를 위해)
- ✅ **런타임 시 필수**입니다 (서비스/액션 사용 시 Python import를 위해)
- ⚠️ **없어도 기본 토픽 구독 기능은 동작합니다** (서비스/액션만 비활성화)

**로봇에 설치 방법**:
- ✅ **통합 완료**: `pinky_lcd_display_interfaces` 패키지가 현재 브랜치에 포함되어 있습니다.
- 같은 워크스페이스(`ROS2/rfred`)에서 한 번에 빌드 및 설치 가능합니다.

자세한 내용은 [의존성 요구사항 문서](docs/DEPENDENCY_REQUIREMENTS.md) 및 [패키지 통합 리포트](docs/PACKAGE_INTEGRATION_REPORT.md)를 참조하세요.

## 빌드 방법

```bash
cd ~/ros-repo-1/ROS2/rfred
# 인터페이스 패키지와 함께 빌드 (인터페이스 패키지가 자동으로 먼저 빌드됨)
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display
source install/setup.bash
```

**참고**: `pinky_lcd_display_interfaces` 패키지가 현재 브랜치에 포함되어 있어 함께 빌드해야 합니다.

## 사용 방법

### 1. 노드 실행

#### 방법 1: Launch 파일 사용 (권장)

```bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

#### 방법 2: 직접 실행

```bash
ros2 run pinky_lcd_display lcd_node
```

### 2. LCD에 내용 표시

#### 기본 사용법

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String \
  "{data: '타이틀\n라인1\n라인2\n라인3'}"
```

#### 예시 1: 상태 정보 표시

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String \
  "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"
```

#### 예시 2: 한글 텍스트 표시

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String \
  "{data: '안녕 핑키\n한글 테스트\n테스트 성공!'}"
```

#### 예시 3: 주기적 업데이트 (1초마다)

```bash
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String \
  "{data: 'Status\nTime: $(date +%H:%M:%S)'}"
```

### 3. 테스트 퍼블리셔 사용

```bash
# 다른 터미널에서
ros2 run pinky_lcd_display test_pub
```

## 제공하는 ROS2 통신 방법

### 토픽 (Topic)

**구독 토픽:**
- **`/lcd/status`** (std_msgs/String)
  - LCD에 표시할 내용을 받는 토픽 (기존 방식 유지)
  - 메시지 형식: 첫 번째 줄은 타이틀, 나머지는 본문 라인
  - 예: `"Pinky Status\nBattery: 78%\nMode: MOVING"`

**발행 토픽:**
- **`/lcd_controller/status`** (pinky_lcd_display_interfaces/msg/LCDStatus)
  - LCD 현재 상태를 실시간으로 발행 (1Hz)
  - 현재 표시 내용, 스타일, 레이아웃 정보 포함

- **`/lcd_controller/events`** (pinky_lcd_display_interfaces/msg/LCDEvent)
  - LCD 이벤트 발행 (표시 시작, 종료, 에러 등)

### 서비스 (Service)

**제공 서비스:**
- **`lcd_controller/set_display`** (pinky_lcd_display_interfaces/srv/SetDisplay)
  - LCD 내용 설정 (타이틀, 본문 라인, 타임스탬프)

- **`lcd_controller/set_style`** (pinky_lcd_display_interfaces/srv/SetStyle)
  - LCD 스타일 설정 (색상, 폰트 크기, 폰트 경로) - 동적 적용 지원

- **`lcd_controller/clear_display`** (pinky_lcd_display_interfaces/srv/ClearDisplay)
  - LCD 화면 지우기

- **`lcd_controller/set_layout`** (pinky_lcd_display_interfaces/srv/SetLayout)
  - 레이아웃 설정 (정렬, 여백, 간격, 그리드 모드)

### 액션 (Action)

**제공 액션:**
- **`lcd_controller/set_display_action`** (pinky_lcd_display_interfaces/action/SetDisplay)
  - 시간 제한이 있는 LCD 표시
  - 애니메이션 효과 (FADE_IN, SLIDE)
  - 진행 상태 피드백

- **`lcd_controller/scroll_text_action`** (pinky_lcd_display_interfaces/action/ScrollText)
  - 긴 텍스트를 스크롤하여 표시
  - 방향 제어 (LEFT, RIGHT)
  - 스크롤 속도 조절
  - 반복 횟수 설정

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

**한글 예시**:
```
안녕 핑키
한글 테스트
테스트 성공!
```

**주의사항**:
- 첫 번째 줄은 타이틀로 표시됩니다 (최대 20자로 자동 잘림)
- `\n`으로 줄바꿈을 구분합니다
- 타임스탬프는 자동으로 하단에 표시됩니다
- 한글 텍스트는 MaruBuri 폰트로 표시됩니다 (폰트가 있는 경우)

## 한글 폰트 지원

이 패키지는 한글 폰트(MaruBuri)를 포함하고 있으며, 자동으로 폰트 경로를 탐색합니다.

**포함된 폰트:**
- MaruBuri-Regular.ttf (기본)
- MaruBuri-Bold.ttf
- MaruBuri-SemiBold.ttf
- MaruBuri-Light.ttf
- MaruBuri-ExtraLight.ttf

**자동 탐색 경로:**
1. 패키지 소스 디렉토리: `fonts/maruburi/TTF/MaruBuri-Regular.ttf`
2. 로봇 절대 경로: `/home/pinky/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/fonts/maruburi/TTF/MaruBuri-Regular.ttf`
3. 상대 경로: `./fonts/maruburi/TTF/MaruBuri-Regular.ttf`
4. 패키지 설치 경로: `share/pinky_lcd_display/fonts/maruburi/TTF/MaruBuri-Regular.ttf`

**폰트 로드 확인:**
LCD 노드 실행 시 다음 메시지가 출력됩니다:
- 한글 폰트를 찾은 경우: `Korean font found: /path/to/MaruBuri-Regular.ttf`
- 한글 폰트를 찾지 못한 경우: `Korean font not found, using default font`

## 주요 컴포넌트

### 1. LCDDisplayNode (`lcd_node.py`)

**역할**: `/lcd/status` 토픽을 구독하여 LCD에 내용을 표시

**주요 기능:**
- ROS2 토픽 구독 (`/lcd/status`)
- 메시지 파싱 (타이틀/본문 분리)
- LCDDisplayManager를 통한 화면 업데이트

### 2. LCDDisplayManager (`lcd_manager.py`)

**역할**: LCD 하드웨어 제어 및 이미지 렌더링

**주요 기능:**
- PIL(Pillow)을 사용한 이미지 생성
- 텍스트 렌더링 (타이틀, 본문, 타임스탬프)
- 한글 폰트 자동 탐색 및 로드
- LCD 하드웨어 제어 (`pinky_lcd` 모듈 사용)

**주요 메서드:**
- `_find_korean_font()`: 한글 폰트 경로 자동 탐색
- `render_status_frame()`: 상태 프레임 렌더링
- `show_status()`: LCD에 상태 표시
- `ensure_lcd_ready()`: LCD 하드웨어 초기화

### 3. LCDTestPublisher (`test_publisher_node.py`)

**역할**: 테스트용 메시지 발행 노드

**주요 기능:**
- 주기적으로 테스트 메시지 발행 (1초마다)
- 배터리, 모드, 웨이포인트 정보 시뮬레이션

## Python 코드 예제

### 예시 1: 기본 상태 표시

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
    
    # 상태 정보 발행
    node.publish_status(
        title="Pinky Status",
        lines=["Battery: 78%", "Mode: MOVING", "Waypoint: 2/4"]
    )
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 예시 2: 한글 텍스트 표시

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

def main():
    rclpy.init()
    node = Node('korean_test')
    pub = node.create_publisher(String, '/lcd/status', 10)
    
    # 한글 텍스트 발행
    msg = String()
    msg.data = "안녕 핑키\n한글 테스트\n테스트 성공!"
    pub.publish(msg)
    node.get_logger().info("Published Korean text")
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 인터페이스 사용 예시

### 서비스 호출

```bash
# SetDisplay 서비스
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING'], show_timestamp: true}"

# SetStyle 서비스
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 0, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 20, body_font_size: 18, font_path: ''}"

# SetLayout 서비스
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 1, layout_mode: 1, margin_top: 10, margin_bottom: 10, margin_left: 10, margin_right: 10, line_spacing: 24, grid_columns: 1, grid_rows: 1}"
```

### 액션 호출

```bash
# SetDisplayAction (페이드 인 효과, 5초간 표시)
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Alert', lines: ['Low battery!', 'Please charge'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"

# ScrollTextAction
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'This is a very long text that needs to be scrolled', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
```

### 토픽 구독

```bash
# 상태 토픽 구독
ros2 topic echo /lcd_controller/status

# 이벤트 토픽 구독
ros2 topic echo /lcd_controller/events
```

## 추가 문서

- [패키지 통합 리포트](docs/PACKAGE_INTEGRATION_REPORT.md) - **필수 읽기**: 인터페이스 패키지 통합 및 정상화 리포트
- [의존성 요구사항](docs/DEPENDENCY_REQUIREMENTS.md) - **필수 읽기**: 패키지 의존성 및 설치 요구사항
- [개발 현황 리포트](docs/DEVELOPMENT_STATUS.md) - 개발 현황 및 사용 방법 상세 설명
- [구현 계획서](docs/IMPLEMENTATION_PLAN.md) - 인터페이스 구현 대상 목록 및 구현 현황
- [인터페이스 통합 현황](docs/INTEGRATION_STATUS.md) - 인터페이스 통합 현황 및 사용 방법
- [기능 상세 설명](docs/FEATURE_DETAILS.md) - 각 기능의 상세한 설명
- [구현 요약](docs/IMPLEMENTATION_SUMMARY.md) - 구현 계획 및 가이드 문서 요약
- [사용자 가이드](docs/USER_GUIDE.md) - 서비스, 액션, 토픽 사용 방법 및 옵셔널 파라미터 가이드
- [테스트 가이드](docs/TEST_GUIDE.md) - 자동 테스트 코드 및 테스트 방법

## 문제 해결

### 한글이 깨져서 표시되는 경우

1. 폰트 파일 확인:
   ```bash
   ls -la fonts/maruburi/TTF/MaruBuri-Regular.ttf
   ```

2. 노드 실행 시 로그 확인:
   - `Korean font found: ...` 메시지가 출력되는지 확인
   - 폰트 경로가 올바른지 확인

3. 폰트 파일 권한 확인:
   ```bash
   chmod 644 fonts/maruburi/TTF/*.ttf
   ```

### LCD에 표시되지 않는 경우

1. 토픽 확인:
   ```bash
   ros2 topic list | grep lcd
   ros2 topic echo /lcd/status
   ```

2. 노드 실행 확인:
   ```bash
   ros2 node list | grep lcd
   ```

3. 하드웨어 연결 확인:
   - LCD 하드웨어가 올바르게 연결되어 있는지 확인
   - `pinky_lcd` 모듈이 설치되어 있는지 확인

## 라이선스

Apache-2.0

## 참고

- 한글 폰트 라이선스: MaruBuri 폰트는 SIL Open Font License 1.1을 따릅니다.

