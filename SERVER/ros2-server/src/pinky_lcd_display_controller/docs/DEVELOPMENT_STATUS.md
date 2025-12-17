# pinky_lcd_display_controller 개발 현황 문서

## 프로젝트 개요

**브랜치**: `feat/SERVER/ros2-server__pinky_lcd_display_controller__RP-50__lcd_display_function`  
**목적**: Pinky 로봇의 LCD 디스플레이를 ROS2 서비스를 통해 제어할 수 있는 컨트롤러 패키지 개발  
**개발 기간**: 2024년 11월  
**상태**: ✅ 개발 완료

## 개발 목표

1. **서비스 기반 LCD 제어 인터페이스 제공**
   - 기존 토픽 기반 제어를 서비스 기반으로 확장
   - 다른 ROS2 노드에서 쉽게 LCD를 제어할 수 있는 API 제공

2. **표준화된 인터페이스 정의**
   - 명확한 서비스 인터페이스 정의
   - 확장 가능한 아키텍처 설계

3. **한글 폰트 지원 준비**
   - 한글 폰트 파일 포함
   - 폰트 경로 자동 탐색 기능

## 구현된 기능

### 1. 서비스 인터페이스 패키지 (`pinky_lcd_display_interfaces`)

#### 1.1 SetDisplay 서비스
LCD에 표시할 내용을 설정하는 서비스입니다.

**서비스명**: `lcd_controller/set_display`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetDisplay`

**요청 (Request)**:
```python
string title                    # 타이틀 텍스트 (최대 20자)
string[] lines                  # 본문 라인들
bool show_timestamp             # 타임스탬프 표시 여부
```

**응답 (Response)**:
```python
bool success                    # 성공 여부
string message                  # 응답 메시지
```

**사용 예시**:
```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING', 'Waypoint: 2/4'], show_timestamp: true}"
```

#### 1.2 SetStyle 서비스
LCD 표시 스타일을 설정하는 서비스입니다.

**서비스명**: `lcd_controller/set_style`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetStyle`

**요청 (Request)**:
```python
uint8 bg_color_r/g/b            # 배경 색상 (RGB, 0-255)
uint8 title_color_r/g/b         # 타이틀 색상 (RGB, 0-255)
uint8 body_color_r/g/b          # 본문 색상 (RGB, 0-255)
uint8 timestamp_color_r/g/b     # 타임스탬프 색상 (RGB, 0-255)
uint8 title_font_size           # 타이틀 폰트 크기
uint8 body_font_size            # 본문 폰트 크기
string font_path                # 폰트 경로 (선택사항)
```

**응답 (Response)**:
```python
bool success
string message
```

**참고**: 현재는 스타일 설정을 저장만 하며, 실제 적용을 위해서는 `pinky_lcd_display` 패키지 수정이 필요합니다.

#### 1.3 ClearDisplay 서비스
LCD 화면을 지우는 서비스입니다.

**서비스명**: `lcd_controller/clear_display`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/ClearDisplay`

**요청 (Request)**: 없음

**응답 (Response)**:
```python
bool success
string message
```

**사용 예시**:
```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

### 2. 컨트롤러 서버 패키지 (`pinky_lcd_display_controller`)

#### 2.1 LCDControllerServer 노드

**노드명**: `lcd_controller_server`  
**실행 명령**: `ros2 run pinky_lcd_display_controller lcd_controller_server`

**주요 기능**:
- 서비스 요청을 받아 `/lcd/status` 토픽에 메시지 발행
- 한글 폰트 경로 자동 탐색
- 스타일 설정 관리

**아키텍처**:
```
[클라이언트 노드]
    |
    | (서비스 호출)
    v
[lcd_controller_server]
    |
    | (토픽 발행: /lcd/status)
    v
[pinky_lcd_display/lcd_node]
    |
    | (하드웨어 제어)
    v
[LCD 디스플레이]
```

#### 2.2 한글 폰트 지원

**구현 기능**:
- `_find_korean_font()` 메서드로 한글 폰트 자동 탐색
- 여러 경로에서 폰트 파일 검색 (패키지 설치 경로, 로컬 경로, 상대 경로)
- 폰트를 찾지 못하면 기본 폰트로 폴백

**포함된 폰트**:
- MaruBuri-Regular.ttf (기본)
- MaruBuri-Bold.ttf
- MaruBuri-SemiBold.ttf
- MaruBuri-Light.ttf
- MaruBuri-ExtraLight.ttf

**참고**: 실제 한글 표시를 위해서는 `pinky_lcd_display` 패키지에 패치가 필요합니다. 자세한 내용은 [한글 폰트 패치 가이드](KOREAN_FONT_PATCH_GUIDE.md)를 참조하세요.

## 패키지 구조

```
SERVER/ros2-server/src/
├── pinky_lcd_display_interfaces/          # 서비스 인터페이스 정의
│   ├── package.xml
│   ├── CMakeLists.txt
│   └── srv/
│       ├── SetDisplay.srv                 # LCD 내용 설정
│       ├── SetStyle.srv                    # LCD 스타일 설정
│       └── ClearDisplay.srv               # LCD 화면 지우기
│
└── pinky_lcd_display_controller/          # 컨트롤러 서버
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    ├── README.md
    ├── docs/                              # 문서 디렉토리
    │   ├── DEVELOPMENT_REPORT.md          # 개발 현황 리포트
    │   ├── DEVELOPMENT_STATUS.md          # 개발 현황 문서 (이 문서)
    │   ├── FEATURES.md                     # 제어 가능한 기능
    │   ├── INTEGRATION_GUIDE.md            # 연동 가이드
    │   ├── INTERFACE_PROPOSAL.md           # 인터페이스 확장 제안서
    │   ├── KOREAN_FONT_PATCH_GUIDE.md     # 한글 폰트 패치 가이드
    │   ├── PINKY_LCD_DISPLAY_USAGE.md     # 사용 가이드
    │   ├── QUICK_START.md                  # 빠른 시작 가이드
    │   └── SUMMARY.md                      # 개발 요약
    ├── fonts/                              # 한글 폰트 파일
    │   └── maruburi/TTF/
    │       ├── MaruBuri-Regular.ttf
    │       ├── MaruBuri-Bold.ttf
    │       ├── MaruBuri-SemiBold.ttf
    │       ├── MaruBuri-Light.ttf
    │       └── MaruBuri-ExtraLight.ttf
    ├── resource/
    │   └── pinky_lcd_display_controller
    └── pinky_lcd_display_controller/
        ├── __init__.py
        └── lcd_controller_server.py       # 메인 서버 노드
```

## 기본 사용 방법

### 1. 빌드

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
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

### 4. 서비스 호출

#### 4.1 LCD 내용 설정

```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING', 'Waypoint: 2/4'], show_timestamp: true}"
```

#### 4.2 LCD 화면 지우기

```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

#### 4.3 LCD 스타일 설정 (참고용)

```bash
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 0, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 20, body_font_size: 18, font_path: ''}"
```

**참고**: 스타일 설정은 현재 저장만 되며, 실제 적용을 위해서는 `pinky_lcd_display` 패키지 수정이 필요합니다.

## Python 코드 예제

### 예제 1: 기본 LCD 내용 설정

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.srv import SetDisplay

class LCDClient(Node):
    def __init__(self):
        super().__init__('lcd_client')
        self.client = self.create_client(SetDisplay, 'lcd_controller/set_display')
        
    def set_display(self, title, lines, show_timestamp=True):
        """LCD에 내용을 표시합니다."""
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not available, waiting again...')
        
        request = SetDisplay.Request()
        request.title = title
        request.lines = lines
        request.show_timestamp = show_timestamp
        
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'Display updated: {response.message}')
            else:
                self.get_logger().error(f'Failed: {response.message}')
        else:
            self.get_logger().error('Service call failed')

def main():
    rclpy.init()
    client = LCDClient()
    
    # LCD에 상태 정보 표시
    client.set_display(
        title='Pinky Status',
        lines=['Battery: 78%', 'Mode: MOVING', 'Waypoint: 2/4'],
        show_timestamp=True
    )
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 예제 2: 주기적 상태 업데이트

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.srv import SetDisplay
import time

class StatusMonitor(Node):
    def __init__(self):
        super().__init__('status_monitor')
        self.client = self.create_client(SetDisplay, 'lcd_controller/set_display')
        self.timer = self.create_timer(2.0, self.update_status)
        self.counter = 0
        
    def update_status(self):
        """주기적으로 상태를 업데이트합니다."""
        if not self.client.wait_for_service(timeout_sec=0.5):
            return
        
        request = SetDisplay.Request()
        request.title = 'Status Monitor'
        request.lines = [
            f'Counter: {self.counter}',
            f'Time: {time.strftime("%H:%M:%S")}',
            'Running...'
        ]
        request.show_timestamp = True
        
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=0.5)
        
        self.counter += 1

def main():
    rclpy.init()
    monitor = StatusMonitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

### 예제 3: 화면 지우기

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.srv import ClearDisplay

def clear_lcd():
    rclpy.init()
    node = Node('clear_lcd_client')
    client = node.create_client(ClearDisplay, 'lcd_controller/clear_display')
    
    while not client.wait_for_service(timeout_sec=1.0):
        node.get_logger().info('Service not available, waiting...')
    
    request = ClearDisplay.Request()
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    
    if future.result() is not None:
        response = future.result()
        if response.success:
            node.get_logger().info('LCD cleared successfully')
        else:
            node.get_logger().error(f'Failed: {response.message}')
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    clear_lcd()
```

## 개발 완료 사항

### ✅ 완료된 기능

1. **서비스 인터페이스 정의**
   - SetDisplay.srv
   - SetStyle.srv
   - ClearDisplay.srv

2. **컨트롤러 서버 구현**
   - LCDControllerServer 노드
   - 서비스 콜백 구현
   - 토픽 발행 기능

3. **한글 폰트 지원 준비**
   - 한글 폰트 파일 포함
   - 폰트 경로 자동 탐색 기능

4. **문서화**
   - README.md
   - 개발 현황 리포트
   - 사용 가이드
   - 한글 폰트 패치 가이드
   - 인터페이스 확장 제안서

5. **패키지 구조 정리**
   - 문서 파일을 docs/ 디렉토리로 정리
   - 폰트 파일을 fonts/ 디렉토리로 정리

### ⚠️ 제한사항

1. **스타일 동적 적용 불가**
   - SetStyle 서비스는 설정을 저장만 함
   - 실제 적용을 위해서는 `pinky_lcd_display` 패키지 수정 필요

2. **한글 표시 제한**
   - 한글 폰트 파일은 포함되어 있음
   - 실제 한글 표시를 위해서는 `pinky_lcd_display` 패키지에 패치 필요

3. **단방향 통신**
   - LCD 상태를 읽어올 수 없음 (읽기 전용)

## 통신 흐름

```
┌─────────────────┐
│  클라이언트 노드 │
└────────┬────────┘
         │
         │ 서비스 호출
         │ (lcd_controller/set_display)
         │
         v
┌─────────────────────────┐
│ lcd_controller_server   │
│ (LCDControllerServer)    │
└────────┬─────────────────┘
         │
         │ 토픽 발행
         │ (/lcd/status)
         │
         v
┌─────────────────────────┐
│ /lcd/status 토픽        │
│ (std_msgs/String)       │
└────────┬─────────────────┘
         │
         │ 토픽 구독
         │
         v
┌─────────────────────────┐
│ pinky_lcd_display       │
│ (lcd_node)              │
└────────┬─────────────────┘
         │
         │ 하드웨어 제어
         │
         v
┌─────────────────────────┐
│ LCD 디스플레이          │
│ (하드웨어)              │
└─────────────────────────┘
```

## 주요 커밋 내역

1. **9200fc1** - 개발 현황 리포트 및 인터페이스 제안서 추가
2. **37dc504** - 한글 폰트 지원 기능 추가 및 패키지 구조 정리
3. **5bbc6b3** - 한글 폰트 패치 가이드 문서 추가

## 향후 개발 계획

### Phase 1 (단기)
- [ ] 스타일 동적 적용 기능 (`pinky_lcd_display` 패키지 수정)
- [ ] 에러 처리 개선
- [ ] 상태 토픽 발행 (LCD 현재 상태)

### Phase 2 (중기)
- [ ] 액션 인터페이스 추가 (시간 제한 표시)
- [ ] 레이아웃 제어 기능
- [ ] 텍스트 정렬 기능

### Phase 3 (장기)
- [ ] 이미지 표시 기능
- [ ] 다중 페이지 관리
- [ ] 그래프 표시 기능

## 참고 문서

- [README.md](../README.md) - 패키지 개요 및 기본 사용법
- [QUICK_START.md](QUICK_START.md) - 빠른 시작 가이드
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - 연동 가이드
- [KOREAN_FONT_PATCH_GUIDE.md](KOREAN_FONT_PATCH_GUIDE.md) - 한글 폰트 패치 가이드
- [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md) - 상세 개발 현황 리포트
- [INTERFACE_PROPOSAL.md](INTERFACE_PROPOSAL.md) - 인터페이스 확장 제안서

## 요약

이 브랜치에서는 Pinky 로봇의 LCD 디스플레이를 제어하기 위한 서비스 기반 컨트롤러 패키지를 개발했습니다. 주요 성과는 다음과 같습니다:

1. ✅ **서비스 인터페이스 정의**: 3개의 서비스 인터페이스 (SetDisplay, SetStyle, ClearDisplay)
2. ✅ **컨트롤러 서버 구현**: 서비스 요청을 토픽 메시지로 변환하는 서버 노드
3. ✅ **한글 폰트 지원 준비**: 한글 폰트 파일 포함 및 자동 탐색 기능
4. ✅ **문서화**: 상세한 사용 가이드 및 개발 문서

LCD 기본 기능 호출 및 사용이 가능하며, 다른 ROS2 노드에서 쉽게 LCD를 제어할 수 있는 인터페이스를 제공합니다.

