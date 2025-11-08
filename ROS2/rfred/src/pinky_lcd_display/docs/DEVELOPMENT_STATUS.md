# pinky_lcd_display 개발 현황 리포트

## 프로젝트 개요

**패키지명**: `pinky_lcd_display`  
**목적**: Pinky 로봇의 LCD 디스플레이를 ROS2 토픽을 통해 제어하는 패키지  
**개발 상태**: ✅ 기본 기능 구현 완료, ✅ 한글 폰트 지원 추가 완료

## 구현된 기능

### 1. LCD 디스플레이 제어

Pinky 로봇의 LCD 디스플레이를 제어하여 텍스트 정보를 표시할 수 있습니다.

**주요 기능:**
- 타이틀 및 본문 라인 표시
- 타임스탬프 자동 표시
- 한글 폰트 지원 (MaruBuri)
- 실시간 텍스트 업데이트

### 2. ROS2 통신 방법

#### 2.1 토픽 (Topic) - 현재 주 통신 방식

**구독 토픽:**
- **`/lcd/status` (std_msgs/String)
  - LCD에 표시할 내용을 받는 토픽
  - 메시지 형식: 첫 번째 줄은 타이틀, 나머지는 본문 라인
  - 예: `"Pinky Status\nBattery: 78%\nMode: MOVING"`

**발행 토픽:**
- 없음 (읽기 전용)

#### 2.2 서비스 (Service)
- 현재 제공하지 않음

#### 2.3 액션 (Action)
- 현재 제공하지 않음

### 3. 한글 폰트 지원

**구현 기능:**
- MaruBuri 폰트 파일 포함 (5개 스타일)
- 폰트 경로 자동 탐색 (`_find_korean_font()` 메서드)
- 여러 경로에서 폰트 파일 검색 (소스 디렉토리, 설치 경로, 절대 경로)
- 폰트를 찾지 못하면 기본 폰트로 폴백

**포함된 폰트:**
- MaruBuri-Regular.ttf (기본)
- MaruBuri-Bold.ttf
- MaruBuri-SemiBold.ttf
- MaruBuri-Light.ttf
- MaruBuri-ExtraLight.ttf

## 패키지 구조

```
pinky_lcd_display/
├── package.xml
├── setup.py
├── setup.cfg
├── LICENSE
├── README.md (추가 예정)
├── docs/                          # 문서 디렉토리
│   └── DEVELOPMENT_STATUS.md      # 개발 현황 리포트 (이 문서)
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

## 주요 컴포넌트

### 1. LCDDisplayNode (`lcd_node.py`)

**역할**: `/lcd/status` 토픽을 구독하여 LCD에 내용을 표시

**주요 기능:**
- ROS2 토픽 구독 (`/lcd/status`)
- 메시지 파싱 (타이틀/본문 분리)
- LCDDisplayManager를 통한 화면 업데이트

**실행 명령**:
```bash
ros2 run pinky_lcd_display lcd_node
```

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

**실행 명령**:
```bash
ros2 run pinky_lcd_display test_pub
```

## 사용 방법

### 1. 빌드

```bash
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display
source install/setup.bash
```

### 2. 실행

#### 방법 1: Launch 파일 사용 (권장)

```bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

#### 방법 2: 직접 실행

```bash
ros2 run pinky_lcd_display lcd_node
```

### 3. LCD에 내용 표시

#### 방법 1: 토픽 직접 발행

```bash
# 기본 형식
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: '타이틀\n라인1\n라인2\n라인3'}"

# 예시 1: 상태 정보 표시
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"

# 예시 2: 한글 텍스트 표시
ros2 topic pub --once /lcd/status std_msgs/msg/String "{data: '안녕 핑키\n한글 테스트\n테스트 성공!'}"

# 예시 3: 주기적 업데이트 (1초마다)
ros2 topic pub --rate 1 /lcd/status std_msgs/msg/String "{data: 'Status\nTime: $(date +%H:%M:%S)'}"
```

#### 방법 2: 테스트 퍼블리셔 사용

```bash
# 다른 터미널에서
ros2 run pinky_lcd_display test_pub
```

#### 방법 3: 서비스를 통한 제어 (pinky_lcd_display_controller 사용)

```bash
# 서버 노드 실행 (다른 패키지)
ros2 run pinky_lcd_display_controller lcd_controller_server

# 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING'], show_timestamp: true}"
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

### 자동 탐색 경로

한글 폰트는 다음 경로에서 자동으로 탐색됩니다 (우선순위 순):

1. 패키지 소스 디렉토리: `fonts/maruburi/TTF/MaruBuri-Regular.ttf`
2. 로봇 절대 경로: `/home/pinky/ros-repo-1/ROS2/rfred/src/pinky_lcd_display/fonts/maruburi/TTF/MaruBuri-Regular.ttf`
3. 상대 경로: `./fonts/maruburi/TTF/MaruBuri-Regular.ttf`
4. 패키지 설치 경로: `share/pinky_lcd_display/fonts/maruburi/TTF/MaruBuri-Regular.ttf`

### 폰트 로드 확인

LCD 노드 실행 시 다음 메시지가 출력됩니다:
- 한글 폰트를 찾은 경우: `Korean font found: /path/to/MaruBuri-Regular.ttf`
- 한글 폰트를 찾지 못한 경우: `Korean font not found, using default font`

## 개발 완료 사항

### ✅ 완료된 기능

1. **토픽 기반 LCD 제어**
   - `/lcd/status` 토픽 구독
   - 메시지 파싱 및 표시

2. **LCDDisplayManager 클래스**
   - 이미지 렌더링
   - 텍스트 표시 (타이틀, 본문, 타임스탬프)
   - LCD 하드웨어 제어

3. **한글 폰트 지원**
   - MaruBuri 폰트 파일 포함
   - 폰트 경로 자동 탐색
   - 폴백 처리

4. **Launch 파일**
   - `lcd_display.launch.py` 제공

5. **테스트 노드**
   - `test_publisher_node` 제공

### ⚠️ 제한사항

1. **단방향 통신**: 토픽만 제공 (서비스/액션 없음)
2. **읽기 전용**: LCD 상태를 읽어올 수 없음
3. **하드웨어 의존성**: `pinky_lcd` 모듈 필요

## 통신 흐름

```
[발행 노드]
    |
    | (토픽 발행: /lcd/status)
    v
[/lcd/status 토픽]
    |
    | (토픽 구독)
    v
[LCDDisplayNode]
    |
    | (LCDDisplayManager 호출)
    v
[LCDDisplayManager]
    |
    | (하드웨어 제어)
    v
[LCD 디스플레이]
```

## 사용 예시

### 예시 1: 기본 상태 표시

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String \
  "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING\nWaypoint: 2/4'}"
```

### 예시 2: 한글 텍스트 표시

```bash
ros2 topic pub --once /lcd/status std_msgs/msg/String \
  "{data: '안녕 핑키\n한글 테스트\n테스트 성공!'}"
```

### 예시 3: 주기적 업데이트

```bash
ros2 topic pub --rate 2 /lcd/status std_msgs/msg/String \
  "{data: 'Status\nTime: $(date +%H:%M:%S)\nCounter: $(seq 1 100 | shuf | head -1)'}"
```

### 예시 4: Python 코드로 발행

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
    
    # 한글 텍스트 발행
    node.publish_status(
        title="안녕 핑키",
        lines=["한글 테스트", "테스트 성공!"]
    )
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 향후 개발 계획

### Phase 1 (단기)
- [ ] 서비스 인터페이스 추가 (스타일 동적 변경)
- [ ] 상태 토픽 발행 (LCD 현재 상태)
- [ ] 에러 처리 개선

### Phase 2 (중기)
- [ ] 액션 인터페이스 추가 (시간 제한 표시)
- [ ] 레이아웃 제어 기능
- [ ] 텍스트 정렬 기능

### Phase 3 (장기)
- [ ] 이미지 표시 기능
- [ ] 다중 페이지 관리
- [ ] 그래프 표시 기능

## 요약

`pinky_lcd_display` 패키지는 Pinky 로봇의 LCD 디스플레이를 제어하기 위한 기본 기능을 제공합니다.

**주요 특징:**
- ✅ 토픽 기반 통신 (`/lcd/status`)
- ✅ 한글 폰트 지원 (MaruBuri)
- ✅ 실시간 텍스트 업데이트
- ✅ 타임스탬프 자동 표시

**통신 방법:**
- **토픽**: `/lcd/status` (std_msgs/String) - 구독
- **서비스**: 없음
- **액션**: 없음

**한글 지원:**
- ✅ MaruBuri 폰트 파일 포함
- ✅ 자동 폰트 탐색 기능
- ✅ 폴백 처리

이 패키지는 다른 노드에서 토픽을 통해 LCD에 정보를 표시할 수 있는 간단하고 효율적인 인터페이스를 제공합니다.

