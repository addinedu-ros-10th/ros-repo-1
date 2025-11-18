# pinky_lcd_display_controller 인터페이스 확장 제안서

## 1. 개요

이 문서는 `pinky_lcd_display_controller` 패키지의 향후 개발을 위한 인터페이스 확장 제안을 정리한 것입니다. 현재 서비스 기반 인터페이스를 기반으로, 액션, 토픽, 고급 기능 인터페이스를 제안합니다.

## 2. 현재 인터페이스 요약

### 2.1 서비스 (Service)
- ✅ `lcd_controller/set_display` - LCD 내용 설정
- ✅ `lcd_controller/set_style` - LCD 스타일 설정 (부분 지원)
- ✅ `lcd_controller/clear_display` - LCD 화면 지우기

### 2.2 토픽 (Topic)
- ✅ `/lcd/status` (std_msgs/String) - LCD 표시 내용 전달 (발행)

## 3. 제안 인터페이스 상세

### 3.1 액션 (Action) 인터페이스

#### 3.1.1 SetDisplayAction
**목적**: 시간 제한이 있는 LCD 표시 및 진행 상태 피드백 제공

**파일**: `pinky_lcd_display_interfaces/action/SetDisplay.action`

```python
# Goal
string title                    # 타이틀 텍스트
string[] lines                  # 본문 라인들
bool show_timestamp             # 타임스탬프 표시 여부
uint32 duration_ms              # 표시 지속 시간 (밀리초, 0이면 무한)
uint8 animation_type            # 0: NONE, 1: FADE_IN, 2: SLIDE
---
# Result
bool success                    # 성공 여부
string message                  # 결과 메시지
uint32 actual_duration_ms      # 실제 표시 시간
---
# Feedback
uint32 elapsed_ms               # 경과 시간 (밀리초)
uint8 progress_percent          # 진행률 (0-100)
string status_message           # 상태 메시지
```

**사용 사례**:
- 일정 시간 후 자동으로 화면 전환
- 애니메이션 효과가 있는 표시
- 진행률이 있는 작업 표시
- 사용자 알림 (일정 시간 후 자동 사라짐)

**예시 코드**:
```python
from pinky_lcd_display_interfaces.action import SetDisplayAction
import rclpy
from rclpy.action import ActionClient

# 액션 클라이언트 생성
action_client = ActionClient(node, SetDisplayAction, 'lcd_controller/set_display_action')

# Goal 전송
goal_msg = SetDisplayAction.Goal()
goal_msg.title = "Processing"
goal_msg.lines = ["Task: Data processing", "Status: In progress"]
goal_msg.duration_ms = 5000  # 5초간 표시
goal_msg.animation_type = 1  # FADE_IN

send_goal_future = action_client.send_goal_async(goal_msg)
```

#### 3.1.2 ScrollTextAction
**목적**: 긴 텍스트를 스크롤하여 표시

**파일**: `pinky_lcd_display_interfaces/action/ScrollText.action`

```python
# Goal
string text                     # 스크롤할 텍스트
uint32 scroll_speed_ms          # 스크롤 속도 (밀리초)
uint8 direction                 # 0: LEFT, 1: RIGHT, 2: UP, 3: DOWN
uint32 repeat_count             # 반복 횟수 (0이면 무한)
---
# Result
bool success
string message
uint32 total_scroll_time_ms
---
# Feedback
uint32 current_position         # 현재 스크롤 위치
uint8 progress_percent
```

### 3.2 토픽 (Topic) 인터페이스 확장

#### 3.2.1 LCD 상태 토픽
**목적**: LCD 현재 상태를 실시간으로 발행

**토픽명**: `/lcd_controller/status`

**메시지 타입**: `pinky_lcd_display_interfaces/msg/LCDStatus`

**파일**: `pinky_lcd_display_interfaces/msg/LCDStatus.msg`

```python
std_msgs/Header header
bool is_active                  # LCD 활성 상태
string current_title            # 현재 타이틀
string[] current_lines         # 현재 라인들
bool show_timestamp             # 타임스탬프 표시 여부
uint64 last_update_time         # 마지막 업데이트 시간 (나노초)
uint8 display_mode             # 0: NORMAL, 1: SCROLL, 2: ANIMATION
uint32 error_code               # 에러 코드 (0이면 정상)
string error_message             # 에러 메시지
```

**발행 주기**: 상태 변경 시 또는 1Hz

#### 3.2.2 LCD 이벤트 토픽
**목적**: LCD 이벤트 (표시 시작, 종료, 에러 등) 발행

**토픽명**: `/lcd_controller/events`

**메시지 타입**: `pinky_lcd_display_interfaces/msg/LCDEvent`

**파일**: `pinky_lcd_display_interfaces/msg/LCDEvent.msg`

```python
std_msgs/Header header
uint8 event_type                # 0: DISPLAY_STARTED, 1: DISPLAY_ENDED, 2: ERROR, 3: CLEARED
uint64 timestamp                # 이벤트 발생 시간
string message                  # 이벤트 메시지
```

### 3.3 고급 서비스 인터페이스

#### 3.3.1 SetLayout 서비스
**목적**: 레이아웃 설정 (정렬, 여백, 간격 등)

**서비스명**: `lcd_controller/set_layout`

**파일**: `pinky_lcd_display_interfaces/srv/SetLayout.srv`

```python
# Request
uint8 alignment                 # 0: LEFT, 1: CENTER, 2: RIGHT
uint8 layout_mode               # 0: SINGLE_LINE, 1: MULTI_LINE, 2: GRID
uint8 margin_top                 # 상단 여백 (픽셀)
uint8 margin_bottom             # 하단 여백 (픽셀)
uint8 margin_left               # 좌측 여백 (픽셀)
uint8 margin_right              # 우측 여백 (픽셀)
uint8 line_spacing              # 라인 간격 (픽셀)
uint8 grid_columns              # 그리드 모드: 열 수
uint8 grid_rows                 # 그리드 모드: 행 수
---
# Response
bool success
string message
```

#### 3.3.2 DisplayImage 서비스
**목적**: 이미지 파일 표시

**서비스명**: `lcd_controller/display_image`

**파일**: `pinky_lcd_display_interfaces/srv/DisplayImage.srv`

```python
# Request
string image_path               # 이미지 파일 경로 (PNG, JPEG)
uint16 x                        # X 좌표 (픽셀)
uint16 y                        # Y 좌표 (픽셀)
uint16 width                    # 너비 (0이면 원본 크기)
uint16 height                   # 높이 (0이면 원본 크기)
bool overlay_text               # 텍스트 오버레이 여부
string overlay_text_content     # 오버레이 텍스트
---
# Response
bool success
string message
```

#### 3.3.3 CreatePage 서비스
**목적**: 다중 페이지 생성

**서비스명**: `lcd_controller/create_page`

**파일**: `pinky_lcd_display_interfaces/srv/CreatePage.srv`

```python
# Request
string page_id                  # 페이지 ID (고유 식별자)
string title                    # 페이지 타이틀
string[] lines                  # 페이지 내용
uint32 display_duration_ms      # 표시 지속 시간 (0이면 수동 전환)
uint8 priority                  # 우선순위 (높을수록 우선)
---
# Response
bool success
string page_id                  # 생성된 페이지 ID
string message
```

#### 3.3.4 SwitchPage 서비스
**목적**: 페이지 전환

**서비스명**: `lcd_controller/switch_page`

**파일**: `pinky_lcd_display_interfaces/srv/SwitchPage.srv`

```python
# Request
string page_id                  # 전환할 페이지 ID
uint8 transition_type           # 0: INSTANT, 1: FADE, 2: SLIDE_LEFT, 3: SLIDE_RIGHT
uint32 transition_duration_ms  # 전환 시간 (밀리초)
---
# Response
bool success
string message
string previous_page_id         # 이전 페이지 ID
string current_page_id          # 현재 페이지 ID
```

#### 3.3.5 ListPages 서비스
**목적**: 페이지 목록 조회

**서비스명**: `lcd_controller/list_pages`

**파일**: `pinky_lcd_display_interfaces/srv/ListPages.srv`

```python
# Request
---
# Response
string[] page_ids               # 페이지 ID 목록
string current_page_id          # 현재 표시 중인 페이지 ID
uint8 page_count                # 총 페이지 수
```

#### 3.3.6 DeletePage 서비스
**목적**: 페이지 삭제

**서비스명**: `lcd_controller/delete_page`

**파일**: `pinky_lcd_display_interfaces/srv/DeletePage.srv`

```python
# Request
string page_id                  # 삭제할 페이지 ID
---
# Response
bool success
string message
```

### 3.4 파라미터 서비스

#### 3.4.1 SetParameter 서비스
**목적**: 런타임 파라미터 설정

**서비스명**: `lcd_controller/set_parameter`

**파일**: `pinky_lcd_display_interfaces/srv/SetParameter.srv`

```python
# Request
string parameter_name           # 파라미터 이름
string parameter_value          # 파라미터 값 (JSON 문자열)
---
# Response
bool success
string message
string old_value                # 이전 값
```

**지원 파라미터**:
- `update_rate`: 업데이트 주기 (Hz)
- `qos_depth`: QoS 큐 깊이
- `debug_mode`: 디버그 모드 (true/false)
- `auto_clear_timeout`: 자동 클리어 타임아웃 (초)

#### 3.4.2 GetParameter 서비스
**목적**: 파라미터 값 조회

**서비스명**: `lcd_controller/get_parameter`

**파일**: `pinky_lcd_display_interfaces/srv/GetParameter.srv`

```python
# Request
string parameter_name
---
# Response
bool success
string parameter_value
string message
```

## 4. 인터페이스 사용 시나리오

### 4.1 시나리오 1: 시간 제한 알림
```python
# 액션을 사용하여 5초간 알림 표시
goal = SetDisplayAction.Goal()
goal.title = "Alert"
goal.lines = ["Low battery!", "Please charge"]
goal.duration_ms = 5000
goal.animation_type = 1  # FADE_IN

action_client.send_goal_async(goal)
```

### 4.2 시나리오 2: 실시간 상태 모니터링
```python
# 상태 토픽 구독
def status_callback(msg):
    if not msg.is_active:
        logger.warn("LCD is not active")
    logger.info(f"Current title: {msg.current_title}")

status_sub = node.create_subscription(
    LCDStatus, '/lcd_controller/status', status_callback, 10
)
```

### 4.3 시나리오 3: 다중 페이지 관리
```python
# 페이지 생성
create_page_req = CreatePage.Request()
create_page_req.page_id = "status_page"
create_page_req.title = "Status"
create_page_req.lines = ["Battery: 85%", "Mode: IDLE"]
create_page_req.display_duration_ms = 10000

create_page_client.call_async(create_page_req)

# 페이지 전환
switch_page_req = SwitchPage.Request()
switch_page_req.page_id = "status_page"
switch_page_req.transition_type = 1  # FADE
switch_page_req.transition_duration_ms = 500

switch_page_client.call_async(switch_page_req)
```

### 4.4 시나리오 4: 이미지 표시
```python
# 이미지 표시
display_image_req = DisplayImage.Request()
display_image_req.image_path = "/path/to/icon.png"
display_image_req.x = 10
display_image_req.y = 10
display_image_req.width = 64
display_image_req.height = 64
display_image_req.overlay_text = True
display_image_req.overlay_text_content = "Icon"

display_image_client.call_async(display_image_req)
```

## 5. 구현 우선순위

### Priority 1 (필수)
1. ✅ 기본 서비스 인터페이스 (완료)
2. ⏳ SetDisplayAction - 시간 제한 표시
3. ⏳ LCDStatus 토픽 - 상태 모니터링
4. ⏳ SetLayout 서비스 - 레이아웃 제어

### Priority 2 (중요)
1. ⏳ ScrollTextAction - 스크롤 텍스트
2. ⏳ LCDEvent 토픽 - 이벤트 알림
3. ⏳ CreatePage/SwitchPage 서비스 - 다중 페이지
4. ⏳ SetParameter/GetParameter 서비스 - 파라미터 관리

### Priority 3 (선택)
1. ⏳ DisplayImage 서비스 - 이미지 표시
2. ⏳ ListPages/DeletePage 서비스 - 페이지 관리
3. ⏳ 고급 애니메이션 액션

## 6. 확장성 고려사항

### 6.1 하위 호환성
- 기존 서비스 인터페이스는 유지
- 새로운 인터페이스는 선택적 사용
- 점진적 마이그레이션 지원

### 6.2 성능
- 토픽 발행 주기 최적화
- 액션 피드백 주기 조절 가능
- 메시지 크기 최소화

### 6.3 안정성
- 에러 처리 및 복구 메커니즘
- 타임아웃 처리
- 리소스 관리

### 6.4 확장성
- 플러그인 아키텍처 고려
- 커스텀 레이아웃 엔진 지원
- 외부 렌더링 엔진 연동 가능

## 7. 결론

제안된 인터페이스들은 현재 서비스 기반 아키텍처를 확장하여 더욱 강력하고 유연한 LCD 제어 시스템을 구축할 수 있게 합니다. 특히 액션 인터페이스는 장시간 실행 작업에 적합하고, 토픽 인터페이스는 실시간 모니터링을 가능하게 하며, 고급 서비스들은 복잡한 UI 요구사항을 충족시킬 수 있습니다.

단계적 구현을 통해 기존 시스템의 안정성을 유지하면서 새로운 기능을 추가할 수 있습니다.

