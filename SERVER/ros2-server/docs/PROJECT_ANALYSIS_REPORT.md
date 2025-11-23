# ROS2-Server 프로젝트 분석 리포트

**작성일**: 2025-01-22  
**프로젝트 경로**: `SERVER/ros2-server`

---

## 목차

1. [프로젝트 개요](#프로젝트-개요)
2. [프로젝트 구조](#프로젝트-구조)
3. [주요 패키지 분석](#주요-패키지-분석)
4. [기능 및 스펙](#기능-및-스펙)
5. [사용 방법](#사용-방법)
6. [FastAPI 적용 확장 가능성](#fastapi-적용-확장-가능성)
7. [LCD 정보 표시 확장 가능성](#lcd-정보-표시-확장-가능성)

---

## 프로젝트 개요

### 목적
ROS2 ↔ HTTP/gRPC 브리지 역할을 수행하는 서버 프로젝트로, ROS2 토픽/서비스를 외부 API로 노출하여 웹 애플리케이션 및 외부 시스템과 통신할 수 있도록 합니다.

### 기술 스택
- **언어**: Python 3
- **프레임워크**: ROS2 (rclpy)
- **통신**: ROS2 Topics, Services, Actions
- **GUI**: PyQt5 (모니터링용)
- **시각화**: matplotlib

### 주요 기능
1. **LCD 디스플레이 제어**: Pinky 로봇의 LCD 화면을 원격으로 제어
2. **로봇 주행 제어**: State Machine 기반 목표 지점 제어
3. **실시간 모니터링**: GUI 기반 로봇 상태 모니터링

---

## 프로젝트 구조

```
SERVER/ros2-server/
├── src/
│   ├── pinky_lcd_display_controller/    # LCD 제어 패키지
│   │   ├── pinky_lcd_display_controller/
│   │   │   └── lcd_controller_server.py # LCD 제어 서버 노드
│   │   ├── fonts/                        # 한글 폰트 (MaruBuri)
│   │   └── docs/                         # 상세 문서
│   │
│   ├── pinky_lcd_display_interfaces/    # LCD 인터페이스 정의
│   │   ├── srv/                          # 서비스 정의
│   │   │   ├── SetDisplay.srv
│   │   │   ├── SetStyle.srv
│   │   │   ├── ClearDisplay.srv
│   │   │   └── SetLayout.srv
│   │   ├── action/                       # 액션 정의
│   │   │   ├── SetDisplay.action
│   │   │   └── ScrollText.action
│   │   └── msg/                          # 메시지 정의
│   │       ├── LCDStatus.msg
│   │       └── LCDEvent.msg
│   │
│   └── pinky_state_machine/              # State Machine 제어 패키지
│       ├── pinky_state_machine/
│       │   ├── move_pinky_state_machine.py    # 주행 제어 노드
│       │   ├── qmonitor_pinky_state_machine.py # GUI 모니터링 노드
│       │   └── control_apps.py                 # PID 제어기
│       └── docs/
│
├── build/                                # 빌드 결과물
├── install/                              # 설치 결과물
└── log/                                  # 빌드 로그
```

---

## 주요 패키지 분석

### 1. pinky_lcd_display_controller

#### 기능
Pinky 로봇의 LCD 디스플레이를 원격으로 제어하는 서비스 서버입니다.

#### 제공 서비스
1. **`/lcd_controller/set_display`** (SetDisplay)
   - LCD에 표시할 내용 설정
   - 파라미터: `title`, `lines[]`, `show_timestamp`
   - 폴백: 서비스 실패 시 `/lcd/status` 토픽으로 전송

2. **`/lcd_controller/set_style`** (SetStyle)
   - LCD 표시 스타일 설정
   - 파라미터: 색상(RGB), 폰트 크기, 폰트 경로
   - 타임아웃: 5초

3. **`/lcd_controller/clear_display`** (ClearDisplay)
   - LCD 화면 지우기
   - 폴백: 서비스 실패 시 빈 메시지를 토픽으로 전송

#### 제공 액션 (클라이언트)
1. **`/lcd_controller/set_display_action`** (SetDisplayAction)
   - 애니메이션 효과가 있는 표시
   - 파라미터: `duration_ms`, `animation_type` (FADE_IN, SLIDE)

2. **`/lcd_controller/scroll_text_action`** (ScrollTextAction)
   - 텍스트 스크롤 표시
   - 파라미터: `scroll_speed_ms`, `direction`, `repeat_count`

#### 토픽
- **발행**: `/lcd/status` (std_msgs/String) - 폴백용

#### 특징
- 한글 폰트 지원 (MaruBuri)
- 서비스 실패 시 토픽으로 자동 폴백
- 비동기 서비스 호출로 데드락 방지

---

### 2. pinky_state_machine

#### 기능
State Machine 기반으로 Pinky 로봇을 목표 지점까지 자동으로 이동시키는 제어 시스템입니다.

#### 노드

##### 2.1 move_pinky_state_machine (제어 노드)
- **구독 토픽**:
  - `/odom` (nav_msgs/Odometry): 로봇의 현재 위치 및 자세
  - `/goal_pose` (geometry_msgs/Pose): 목표 위치

- **발행 토픽**:
  - `/cmd_vel` (geometry_msgs/Twist): 속도 명령
  - `/angle_error` (std_msgs/Float64): 각도 오차
  - `/distance_error` (std_msgs/Float64): 거리 오차
  - `/state` (std_msgs/String): 현재 상태

- **State Machine 흐름**:
  ```
  1. RotateToGoal: 목표 방향으로 회전
  2. MoveToGoal: 목표 위치로 직진 이동
  3. RotateToFinal: 최종 방향으로 회전
  4. GoalReached: 목표 도달 완료
  ```

- **제어 방식**:
  - PID 제어기를 통한 각도 및 선형 속도 제어
  - 동적 파라미터 조정 지원 (런타임 변경 가능)

##### 2.2 qmonitor_pinky_state_machine (GUI 모니터링 노드)
- **기능**: PyQt5 기반 GUI로 로봇 상태를 실시간 모니터링
- **구독 토픽**: `/odom`, `/goal_pose`, `/state`
- **발행 토픽**: `/goal_pose` (마우스 드래그로 목표 설정)
- **특징**:
  - 실시간 로봇 위치 시각화
  - State Machine 상태 표시
  - 마우스 드래그로 목표 위치 설정
  - 맵 크기 파라미터 설정 가능

##### 2.3 control_apps (PID 제어기)
- **기능**: PID 제어 알고리즘 구현
- **파라미터**: P, I, D 게인, 최대/최소 출력 제한

---

## 기능 및 스펙

### LCD 제어 스펙

#### 서비스 인터페이스

**SetDisplay.srv**
```yaml
# Request
string title                    # 타이틀 (최대 20자)
string[] lines                  # 본문 라인들
bool show_timestamp             # 타임스탬프 표시 여부

# Response
bool success
string message
```

**SetStyle.srv**
```yaml
# Request
uint8 bg_color_r/g/b            # 배경 색상 (RGB)
uint8 title_color_r/g/b         # 타이틀 색상 (RGB)
uint8 body_color_r/g/b          # 본문 색상 (RGB)
uint8 timestamp_color_r/g/b     # 타임스탬프 색상 (RGB)
uint8 title_font_size           # 타이틀 폰트 크기
uint8 body_font_size            # 본문 폰트 크기
string font_path                # 폰트 파일 경로

# Response
bool success
string message
```

**ClearDisplay.srv**
```yaml
# Request
(empty)

# Response
bool success
string message
```

#### 액션 인터페이스

**SetDisplay.action**
```yaml
# Goal
string title
string[] lines
bool show_timestamp
uint32 duration_ms              # 표시 지속 시간 (0=무한)
uint8 animation_type            # 0: NONE, 1: FADE_IN, 2: SLIDE

# Result
bool success
string message
uint32 actual_duration_ms

# Feedback
uint32 elapsed_ms
uint8 progress_percent
string status_message
```

**ScrollText.action**
```yaml
# Goal
string text
uint32 scroll_speed_ms
uint8 direction                 # 0: LEFT, 1: RIGHT, 2: UP, 3: DOWN
uint32 repeat_count            # 0=무한

# Result
bool success
string message

# Feedback
uint32 elapsed_ms
uint8 progress_percent
string status_message
```

### State Machine 스펙

#### 토픽 스펙

**입력 토픽**
- `/odom` (nav_msgs/Odometry): 30Hz 오도메트리 정보
- `/goal_pose` (geometry_msgs/Pose): 목표 위치

**출력 토픽**
- `/cmd_vel` (geometry_msgs/Twist): 속도 명령
- `/angle_error` (std_msgs/Float64): 각도 오차
- `/distance_error` (std_msgs/Float64): 거리 오차
- `/state` (std_msgs/String): 현재 상태

#### PID 파라미터
- **각도 제어**: `angular_p`, `angular_i`, `angular_d`
- **선형 제어**: `linear_p`, `linear_i`, `linear_d`
- **허용 오차**: `angle_tolerance`, `distance_tolerance`

---

## 사용 방법

### 빌드

```bash
cd SERVER/ros2-server

# 전체 빌드
colcon build

# 특정 패키지만 빌드
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display_controller
colcon build --packages-select pinky_state_machine

# 환경 설정
source install/setup.bash
```

### LCD 제어 서버 실행

```bash
# 서버 노드 실행
ros2 run pinky_lcd_display_controller lcd_controller_server
```

### LCD 제어 예시

#### 서비스 호출
```bash
# 표시 내용 설정
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING'], show_timestamp: true}"

# 스타일 설정
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, \
    title_color_r: 0, title_color_g: 255, title_color_b: 0, \
    body_color_r: 255, body_color_g: 255, body_color_b: 255, \
    title_font_size: 20, body_font_size: 18}"

# 화면 지우기
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

#### 토픽 발행 (폴백)
```bash
# 직접 토픽 발행
ros2 topic pub --once /lcd/status std_msgs/msg/String \
  "{data: 'Pinky Status\nBattery: 78%\nMode: MOVING'}"
```

### State Machine 제어

#### 제어 노드 실행
```bash
# 로봇 측 준비 (pinky_bringup 실행 필요)
ros2 launch pinky_bringup bringup_robot.launch.xml

# 제어 노드 실행
ros2 run pinky_state_machine move_pinky_state_machine

# GUI 모니터링 노드 실행
ros2 run pinky_state_machine qmonitor_pinky_state_machine
```

#### 목표 위치 설정
```bash
# 목표 위치 발행
ros2 topic pub --once /goal_pose geometry_msgs/msg/Pose \
  "{position: {x: 1.5, y: 2.0, z: 0.0}, \
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}"
```

---

## FastAPI 적용 확장 가능성

### 현재 상태
- ❌ FastAPI가 아직 적용되지 않음
- ✅ ROS2 서비스/액션을 통한 제어 가능
- ✅ 토픽 기반 통신 가능

### 확장 제안

#### 1. FastAPI 브리지 서버 구조

```
[외부 클라이언트]
    |
    | HTTP/WebSocket
    v
[FastAPI 서버] (새로 추가)
    |
    | ROS2 Service/Action/Topic
    v
[ROS2 노드] (기존)
    |
    v
[로봇 하드웨어]
```

#### 2. 구현 제안

##### 2.1 FastAPI 서버 패키지 생성
```
src/pinky_ros2_bridge/
├── package.xml
├── setup.py
├── pinky_ros2_bridge/
│   ├── __init__.py
│   ├── fastapi_server.py      # FastAPI 서버
│   ├── ros2_client.py          # ROS2 클라이언트 래퍼
│   └── models.py               # Pydantic 모델
└── docs/
```

##### 2.2 주요 API 엔드포인트 제안

**LCD 제어 API**
```python
# POST /api/lcd/display
# LCD 표시 내용 설정
{
  "title": "Pinky Status",
  "lines": ["Battery: 78%", "Mode: MOVING"],
  "show_timestamp": true
}

# POST /api/lcd/style
# LCD 스타일 설정
{
  "bg_color": {"r": 0, "g": 0, "b": 0},
  "title_color": {"r": 0, "g": 255, "b": 0},
  "body_color": {"r": 255, "g": 255, "b": 255},
  "title_font_size": 20,
  "body_font_size": 18
}

# POST /api/lcd/clear
# LCD 화면 지우기

# GET /api/lcd/status
# LCD 현재 상태 조회

# POST /api/lcd/display/action
# 애니메이션 효과가 있는 표시
{
  "title": "Alert",
  "lines": ["Low Battery!"],
  "duration_ms": 5000,
  "animation_type": "fade_in"
}

# POST /api/lcd/scroll
# 텍스트 스크롤
{
  "text": "긴 텍스트를 스크롤하여 표시합니다...",
  "scroll_speed_ms": 50,
  "direction": "left",
  "repeat_count": 3
}
```

**로봇 제어 API**
```python
# POST /api/robot/goal
# 목표 위치 설정
{
  "x": 1.5,
  "y": 2.0,
  "theta": 0.0
}

# GET /api/robot/status
# 로봇 현재 상태 조회
{
  "position": {"x": 0.5, "y": 1.2, "theta": 0.3},
  "state": "MoveToGoal",
  "angle_error": 0.05,
  "distance_error": 0.3
}

# POST /api/robot/stop
# 로봇 정지

# GET /api/robot/odom
# 오도메트리 정보 조회
```

**WebSocket 스트리밍**
```python
# WebSocket /ws/robot/status
# 실시간 로봇 상태 스트리밍
{
  "position": {...},
  "state": "...",
  "errors": {...},
  "timestamp": "..."
}

# WebSocket /ws/lcd/events
# LCD 이벤트 스트리밍
{
  "event_type": "display_updated",
  "data": {...}
}
```

##### 2.3 구현 예시 코드

```python
# fastapi_server.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import rclpy
from rclpy.node import Node
from pinky_ros2_bridge.ros2_client import ROS2LCDClient, ROS2RobotClient

app = FastAPI(title="Pinky ROS2 Bridge API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROS2 노드 초기화
rclpy.init()
ros2_node = Node('pinky_bridge')
lcd_client = ROS2LCDClient(ros2_node)
robot_client = ROS2RobotClient(ros2_node)

@app.post("/api/lcd/display")
async def set_lcd_display(request: LCDDisplayRequest):
    """LCD 표시 내용 설정"""
    result = await lcd_client.set_display(
        title=request.title,
        lines=request.lines,
        show_timestamp=request.show_timestamp
    )
    return result

@app.get("/api/robot/status")
async def get_robot_status():
    """로봇 현재 상태 조회"""
    status = await robot_client.get_status()
    return status

@app.websocket("/ws/robot/status")
async def websocket_robot_status(websocket: WebSocket):
    """실시간 로봇 상태 스트리밍"""
    await websocket.accept()
    try:
        while True:
            status = await robot_client.get_status_stream()
            await websocket.send_json(status)
            await asyncio.sleep(0.1)  # 10Hz
    except:
        await websocket.close()
```

#### 3. 장점

1. **표준화된 API**: RESTful API로 외부 시스템과 쉽게 통합
2. **자동 문서화**: FastAPI의 Swagger UI로 API 문서 자동 생성
3. **비동기 처리**: asyncio 기반으로 높은 성능
4. **WebSocket 지원**: 실시간 데이터 스트리밍
5. **타입 안정성**: Pydantic 모델로 요청/응답 검증
6. **인증/권한**: JWT, OAuth 등 표준 인증 방식 적용 가능

#### 4. 구현 단계

**Phase 1: 기본 브리지**
- FastAPI 서버 기본 구조
- LCD 제어 API (서비스 기반)
- 로봇 상태 조회 API

**Phase 2: 고급 기능**
- 액션 기반 API (애니메이션, 스크롤)
- WebSocket 스트리밍
- 에러 처리 및 재시도 로직

**Phase 3: 최적화**
- 연결 풀링
- 캐싱
- 로깅 및 모니터링

---

## LCD 정보 표시 확장 가능성

### 현재 기능

#### ✅ 구현됨
1. **기본 표시**: 타이틀, 본문 라인, 타임스탬프
2. **스타일 제어**: 색상, 폰트 크기 (서비스는 구현, 실제 적용은 pinky_lcd_display 패키지 수정 필요)
3. **화면 지우기**: ClearDisplay 서비스
4. **애니메이션**: SetDisplayAction (FADE_IN, SLIDE)
5. **스크롤**: ScrollTextAction

### 확장 제안

#### 1. 실시간 정보 표시

##### 1.1 로봇 상태 정보
```python
# 제안: 주기적으로 로봇 상태를 LCD에 표시
POST /api/lcd/display/robot-status
{
  "update_interval_ms": 1000,  # 1초마다 업데이트
  "fields": [
    "battery_level",
    "current_state",
    "position",
    "goal_distance"
  ]
}
```

**구현 방법**:
- ROS2 토픽 구독 (`/odom`, `/state`, `/battery` 등)
- 주기적으로 LCD 업데이트
- FastAPI 엔드포인트로 제어

##### 1.2 시스템 정보
```python
# 제안: 시스템 리소스 정보 표시
POST /api/lcd/display/system-info
{
  "show_cpu": true,
  "show_memory": true,
  "show_temperature": true,
  "update_interval_ms": 2000
}
```

#### 2. 다중 페이지/화면 전환

##### 2.1 페이지 관리 시스템
```python
# 제안: 여러 페이지를 순환 표시
POST /api/lcd/pages/create
{
  "pages": [
    {
      "id": "status",
      "title": "Status",
      "lines": ["Battery: 78%", "Mode: MOVING"],
      "duration_ms": 3000
    },
    {
      "id": "navigation",
      "title": "Navigation",
      "lines": ["Goal: (1.5, 2.0)", "Distance: 0.3m"],
      "duration_ms": 3000
    }
  ],
  "auto_rotate": true,
  "rotation_interval_ms": 5000
}

# 페이지 전환
POST /api/lcd/pages/switch
{
  "page_id": "status"
}
```

**구현 방법**:
- 페이지 관리자 클래스 생성
- 타이머 기반 자동 전환
- 수동 전환 API 제공

#### 3. 조건부 표시 및 알림

##### 3.1 알림 시스템
```python
# 제안: 우선순위 기반 알림 표시
POST /api/lcd/notify
{
  "priority": "high",  # low, normal, high, urgent
  "title": "Alert",
  "message": "Low Battery!",
  "duration_ms": 5000,
  "interrupt_current": true  # 현재 표시 중단하고 알림 표시
}
```

**구현 방법**:
- 알림 큐 관리
- 우선순위에 따른 표시 순서 결정
- 알림 표시 후 이전 화면 복원

##### 3.2 조건부 표시
```python
# 제안: 조건에 따라 다른 내용 표시
POST /api/lcd/display/conditional
{
  "conditions": [
    {
      "field": "battery_level",
      "operator": "<",
      "value": 20,
      "display": {
        "title": "Warning",
        "lines": ["Low Battery!", "Please charge"]
      }
    },
    {
      "field": "state",
      "operator": "==",
      "value": "GoalReached",
      "display": {
        "title": "Success",
        "lines": ["Goal reached!"]
      }
    }
  ],
  "default": {
    "title": "Status",
    "lines": ["Normal operation"]
  }
}
```

#### 4. 그래픽 및 차트 표시

##### 4.1 간단한 그래프
```python
# 제안: 막대 그래프, 선 그래프 표시
POST /api/lcd/display/graph
{
  "type": "bar",  # bar, line
  "title": "Battery History",
  "data": [78, 75, 72, 70, 68],
  "labels": ["5m", "4m", "3m", "2m", "1m"],
  "height": 40  # 픽셀
}
```

**구현 방법**:
- PIL ImageDraw를 사용한 그래프 렌더링
- 간단한 데이터 시각화 라이브러리 활용

##### 4.2 아이콘 표시
```python
# 제안: 아이콘 이미지 표시
POST /api/lcd/display/icon
{
  "icon_type": "battery",  # battery, warning, success, error
  "position": "top_left",  # top_left, top_right, bottom_left, bottom_right
  "size": 32
}
```

#### 5. 템플릿 시스템

##### 5.1 미리 정의된 템플릿
```python
# 제안: 자주 사용하는 레이아웃을 템플릿으로 제공
POST /api/lcd/display/template
{
  "template_id": "robot_status",
  "variables": {
    "battery": 78,
    "mode": "MOVING",
    "waypoint": "2/4"
  }
}
```

**템플릿 예시**:
- `robot_status`: 로봇 상태 정보
- `navigation_info`: 네비게이션 정보
- `system_info`: 시스템 정보
- `alert`: 알림 메시지

#### 6. 다국어 지원

##### 6.1 다국어 메시지
```python
# 제안: 언어별 메시지 표시
POST /api/lcd/display
{
  "title": {"ko": "상태", "en": "Status"},
  "lines": [
    {"ko": "배터리: 78%", "en": "Battery: 78%"},
    {"ko": "모드: 이동 중", "en": "Mode: MOVING"}
  ],
  "language": "ko"
}
```

#### 7. 통합 제안: LCD 정보 대시보드

##### 7.1 대시보드 개념
여러 정보 소스를 통합하여 하나의 대시보드로 표시:

```python
# 대시보드 설정
POST /api/lcd/dashboard/create
{
  "layout": "grid_2x2",  # single, multi_line, grid_2x2, grid_3x3
  "widgets": [
    {
      "type": "battery",
      "position": {"row": 0, "col": 0},
      "update_interval_ms": 1000
    },
    {
      "type": "robot_state",
      "position": {"row": 0, "col": 1},
      "update_interval_ms": 500
    },
    {
      "type": "navigation",
      "position": {"row": 1, "col": 0},
      "update_interval_ms": 2000
    },
    {
      "type": "system_info",
      "position": {"row": 1, "col": 1},
      "update_interval_ms": 5000
    }
  ],
  "auto_refresh": true
}
```

##### 7.2 위젯 타입
- **battery**: 배터리 레벨 (막대 그래프)
- **robot_state**: 로봇 상태 (텍스트)
- **navigation**: 네비게이션 정보 (거리, 방향)
- **system_info**: 시스템 정보 (CPU, 메모리)
- **custom**: 사용자 정의 위젯

### 구현 우선순위

#### High Priority
1. ✅ 실시간 로봇 상태 정보 표시
2. ✅ 알림 시스템 (우선순위 기반)
3. ✅ 페이지 관리 시스템

#### Medium Priority
4. ⏳ 조건부 표시
5. ⏳ 템플릿 시스템
6. ⏳ 간단한 그래프 표시

#### Low Priority
7. ⏳ 아이콘 표시
8. ⏳ 다국어 지원
9. ⏳ 대시보드 시스템

---

## 결론

### 현재 상태
- ✅ ROS2 기반 LCD 제어 시스템 완성
- ✅ State Machine 기반 로봇 제어 시스템 완성
- ✅ GUI 모니터링 도구 제공
- ❌ FastAPI 브리지 미구현

### 확장 가능성
1. **FastAPI 브리지**: 외부 시스템과의 통합 용이
2. **LCD 정보 표시**: 실시간 정보, 알림, 대시보드 등 다양한 확장 가능
3. **WebSocket 스트리밍**: 실시간 데이터 전송
4. **템플릿 시스템**: 재사용 가능한 표시 레이아웃

### 권장 사항
1. **즉시 구현**: FastAPI 기본 브리지 (LCD 제어, 로봇 상태 조회)
2. **단기 구현**: 실시간 정보 표시, 알림 시스템
3. **중기 구현**: 페이지 관리, 템플릿 시스템
4. **장기 구현**: 대시보드, 그래프, 다국어 지원

---

## 참고 문서

- [LCD 제어 패키지 README](src/pinky_lcd_display_controller/README.md)
- [State Machine 개발 리포트](src/pinky_state_machine/docs/DEVELOPMENT_REPORT.md)
- [LCD 기능 문서](src/pinky_lcd_display_controller/docs/FEATURES.md)
- [빠른 시작 가이드](src/pinky_lcd_display_controller/docs/QUICK_START.md)

