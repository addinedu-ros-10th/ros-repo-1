# 테스트 피드백 및 해결 방안

## 개요

이 문서는 실제 테스트 중 발견된 문제점과 해결 방안을 정리한 것입니다.

**작성일**: 2025년 11월 8일  
**작성 기준**: 실제 코드 분석 결과

---

## 문제 1: 타임스탬프 제어 불가

### 문제 설명

**현상**: 타임스탬프가 `show_timestamp: false`로 설정해도 사라지지 않습니다.

**재현 단계**:
```bash
# 타임스탬프를 false로 설정
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1'], show_timestamp: false}"

# 결과: 타임스탬프가 여전히 표시됨
```

### 원인 분석

#### 현재 브랜치 (`pinky_lcd_display_controller`)

**코드 위치**: `SERVER/ros2-server/src/pinky_lcd_display_controller/pinky_lcd_display_controller/lcd_controller_server.py:126-156`

```python
def set_display_callback(self, request, response):
    # ...
    msg_text = '\n'.join(lines)
    msg = String()
    msg.data = msg_text
    self.lcd_status_publisher.publish(msg)  # show_timestamp 정보가 전달되지 않음
```

**문제점**:
- `std_msgs/String` 타입은 `show_timestamp` 정보를 포함할 수 없음
- `request.show_timestamp` 값을 사용하지 않음
- 토픽 메시지에 타임스탬프 제어 정보가 없음

#### base/ROS2/rfred 브랜치 (`pinky_lcd_display`)

**코드 위치**: `base/ROS2/rfred` 브랜치의 `pinky_lcd_display/lcd_node.py`

```python
def status_callback(self, msg: String):
    # ...
    self.show_timestamp = True  # 하드코딩됨
    # ...
    self.lcd_manager.show_status(
        title=title,
        lines=body_lines,
        footer_timestamp=True,  # 하드코딩됨
    )
```

**문제점**:
- `status_callback`에서 `show_timestamp`가 `True`로 하드코딩됨
- `footer_timestamp` 파라미터가 `True`로 하드코딩됨
- 토픽 메시지에서 타임스탬프 제어 정보를 받을 수 없음

### 해결 방안

#### 방안 1: 토픽 메시지에 타임스탬프 정보 포함 (권장)

**수정 브랜치**: `base/ROS2/rfred` 브랜치

**수정 파일**: `ROS2/rfred/src/pinky_lcd_display/pinky_lcd_display/lcd_node.py`

**수정 내용**:

1. **토픽 메시지 형식 확장**:
   - 현재: `"Title\nLine1\nLine2"`
   - 변경: `"Title\nLine1\nLine2\n__TIMESTAMP__:true"` 또는 `"Title\nLine1\nLine2\n__TIMESTAMP__:false"`

2. **status_callback 수정**:
   ```python
   def status_callback(self, msg: String):
       lines = msg.data.split("\n")
       
       # 타임스탬프 플래그 추출
       show_timestamp = True  # 기본값
       if len(lines) > 0 and lines[-1].startswith("__TIMESTAMP__:"):
           timestamp_flag = lines[-1].split(":")[1].strip().lower()
           show_timestamp = timestamp_flag == "true"
           lines = lines[:-1]  # 플래그 라인 제거
       
       # 나머지 로직
       if len(lines) > 0:
           title = lines[0][:20]
           body_lines = lines[1:]
       else:
           title = "Status"
           body_lines = []
       
       self.show_timestamp = show_timestamp
       
       self.lcd_manager.show_status(
           title=title,
           lines=body_lines,
           footer_timestamp=show_timestamp,  # 동적으로 설정
       )
   ```

3. **pinky_lcd_display_controller 수정**:
   ```python
   def set_display_callback(self, request, response):
       lines = [request.title]
       lines.extend(request.lines)
       
       # 타임스탬프 플래그 추가
       timestamp_flag = "true" if request.show_timestamp else "false"
       lines.append(f"__TIMESTAMP__:{timestamp_flag}")
       
       msg_text = '\n'.join(lines)
       msg = String()
       msg.data = msg_text
       self.lcd_status_publisher.publish(msg)
   ```

**장점**:
- 기존 토픽 구조 유지
- 하위 호환성 유지 (플래그가 없으면 기본값 사용)
- 간단한 구현

**단점**:
- 메시지 형식이 약간 복잡해짐

#### 방안 2: 별도 토픽으로 타임스탬프 제어

**수정 브랜치**: `base/ROS2/rfred` 브랜치

**수정 내용**:
- 새로운 토픽 `/lcd/timestamp_control` (std_msgs/Bool) 추가
- `pinky_lcd_display_controller`에서 이 토픽에 타임스탬프 제어 메시지 발행

**장점**:
- 메시지 형식이 깔끔함
- 타임스탬프만 독립적으로 제어 가능

**단점**:
- 추가 토픽 필요
- 두 토픽의 동기화 문제 가능성

#### 방안 3: 서비스 직접 호출 (방안 2와 함께)

**수정 브랜치**: 현재 브랜치 (`pinky_lcd_display_controller`)

**수정 내용**:
- `pinky_lcd_display_controller`에서 `base/ROS2/rfred` 브랜치의 `pinky_lcd_display` 서비스를 직접 호출
- 토픽 대신 서비스 사용

**장점**:
- 타임스탬프 제어가 명확함
- 모든 서비스 기능 활용 가능

**단점**:
- 네트워크 연결 필요
- 서비스 클라이언트 구현 필요

### 권장 해결 방안

**방안 1 (토픽 메시지에 타임스탬프 정보 포함)**을 권장합니다.

**이유**:
1. 기존 토픽 구조를 최대한 유지
2. 하위 호환성 보장
3. 구현이 간단함
4. 추가 토픽 불필요

### 구현 체크리스트

#### base/ROS2/rfred 브랜치 수정

- [ ] `lcd_node.py`의 `status_callback` 수정
  - 타임스탬프 플래그 파싱 로직 추가
  - `show_timestamp` 변수를 동적으로 설정
  - `footer_timestamp` 파라미터를 동적으로 전달

#### 현재 브랜치 수정

- [ ] `lcd_controller_server.py`의 `set_display_callback` 수정
  - `request.show_timestamp` 값을 메시지에 포함
  - 타임스탬프 플래그를 메시지 끝에 추가

---

## 문제 2: pinky_lcd_display_controller에서 모든 기능 호출 필요

### 문제 설명

**요구사항**: `pinky_lcd_display_controller`에서 `pinky_lcd_display`의 모든 토픽, 서비스, 액션을 호출하고 싶습니다. 매번 로봇에 접속해서 명령할 수는 없습니다.

**현재 상황**:
- `pinky_lcd_display_controller`는 토픽(`/lcd/status`)만 사용
- `base/ROS2/rfred` 브랜치의 `pinky_lcd_display`는 서비스, 액션, 토픽 모두 제공
- 하지만 `pinky_lcd_display_controller`에서 직접 호출 불가

### 현재 아키텍처 분석

#### 현재 브랜치 (`pinky_lcd_display_controller`)

**제공 기능**:
- 서비스 서버: SetDisplay, SetStyle, ClearDisplay
- 토픽 발행: `/lcd/status` (std_msgs/String)

**제한사항**:
- 토픽만 사용하여 제한된 기능만 제공
- `base/ROS2/rfred` 브랜치의 서비스/액션을 직접 호출 불가

#### base/ROS2/rfred 브랜치 (`pinky_lcd_display`)

**제공 기능**:
- 서비스 서버: SetDisplay, SetStyle, ClearDisplay, SetLayout
- 액션 서버: SetDisplayAction, ScrollTextAction
- 토픽 발행: `/lcd_controller/status`, `/lcd_controller/events`
- 토픽 구독: `/lcd/status`

### 해결 방안

#### 방안 1: 서비스/액션 클라이언트 추가 (권장)

**수정 브랜치**: 현재 브랜치 (`pinky_lcd_display_controller`)

**구현 내용**:

1. **서비스 클라이언트 추가**:
   - SetLayout 서비스 클라이언트
   - SetStyle 서비스 클라이언트 (실제 적용용)

2. **액션 클라이언트 추가**:
   - SetDisplayAction 클라이언트
   - ScrollTextAction 클라이언트

3. **기존 서비스 콜백 수정**:
   - SetDisplay: 토픽 발행 대신 서비스 직접 호출
   - SetStyle: 서비스 직접 호출
   - ClearDisplay: 서비스 직접 호출

**구현 예시**:

```python
class LCDControllerServer(Node):
    def __init__(self):
        super().__init__('lcd_controller_server')
        
        # 서비스 클라이언트 생성
        self.set_display_client = self.create_client(
            SetDisplay,
            'lcd_controller/set_display'
        )
        
        self.set_style_client = self.create_client(
            SetStyle,
            'lcd_controller/set_style'
        )
        
        self.clear_display_client = self.create_client(
            ClearDisplay,
            'lcd_controller/clear_display'
        )
        
        self.set_layout_client = self.create_client(
            SetLayout,
            'lcd_controller/set_layout'
        )
        
        # 액션 클라이언트 생성
        self.set_display_action_client = ActionClient(
            self,
            SetDisplayAction,
            'lcd_controller/set_display_action'
        )
        
        self.scroll_text_action_client = ActionClient(
            self,
            ScrollText,
            'lcd_controller/scroll_text_action'
        )
        
        # 서비스 서버도 유지 (외부에서 호출 가능)
        self.set_display_srv = self.create_service(
            SetDisplay,
            'lcd_controller/set_display',
            self.set_display_callback
        )
        # ... (다른 서비스 서버들)
    
    def set_display_callback(self, request, response):
        """서비스 서버 콜백: 내부적으로 서비스 클라이언트로 전달"""
        if self.set_display_client.wait_for_service(timeout_sec=1.0):
            future = self.set_display_client.call_async(request)
            rclpy.spin_until_future_complete(self, future)
            service_response = future.result()
            response.success = service_response.success
            response.message = service_response.message
        else:
            # 서비스가 없으면 토픽으로 폴백
            self._fallback_to_topic(request, response)
        return response
    
    def call_set_layout(self, alignment, layout_mode, margin_top, margin_bottom,
                       margin_left, margin_right, line_spacing, grid_columns, grid_rows):
        """SetLayout 서비스 호출 메서드"""
        if not self.set_layout_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().warn("SetLayout service not available")
            return False
        
        request = SetLayout.Request()
        request.alignment = alignment
        request.layout_mode = layout_mode
        request.margin_top = margin_top
        request.margin_bottom = margin_bottom
        request.margin_left = margin_left
        request.margin_right = margin_right
        request.line_spacing = line_spacing
        request.grid_columns = grid_columns
        request.grid_rows = grid_rows
        
        future = self.set_layout_client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        return response.success
    
    def call_set_display_action(self, title, lines, show_timestamp, duration_ms, animation_type):
        """SetDisplayAction 액션 호출 메서드"""
        if not self.set_display_action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn("SetDisplayAction server not available")
            return None
        
        goal_msg = SetDisplayAction.Goal()
        goal_msg.title = title
        goal_msg.lines = lines
        goal_msg.show_timestamp = show_timestamp
        goal_msg.duration_ms = duration_ms
        goal_msg.animation_type = animation_type
        
        future = self.set_display_action_client.send_goal_async(goal_msg)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()
        return goal_handle
```

**장점**:
- 모든 기능을 직접 호출 가능
- 네트워크를 통해 원격 제어 가능
- 서비스/액션의 모든 기능 활용
- 타임스탬프 제어 문제도 함께 해결

**단점**:
- 네트워크 연결 필요
- 서비스가 없을 때 폴백 로직 필요
- 코드 복잡도 증가

#### 방안 2: 하이브리드 접근 (토픽 + 서비스/액션)

**수정 브랜치**: 현재 브랜치 (`pinky_lcd_display_controller`)

**구현 내용**:
- 기본 기능은 토픽 사용 (하위 호환성)
- 고급 기능은 서비스/액션 클라이언트 사용
- 서비스/액션이 없으면 토픽으로 폴백

**장점**:
- 하위 호환성 유지
- 점진적 마이그레이션 가능
- 네트워크 문제 시 폴백 가능

**단점**:
- 두 가지 통신 방식 관리 필요

#### 방안 3: 프록시 패턴

**수정 브랜치**: 현재 브랜치 (`pinky_lcd_display_controller`)

**구현 내용**:
- `pinky_lcd_display_controller`가 완전한 프록시 역할
- 모든 요청을 `pinky_lcd_display`로 전달
- 로컬 서비스 서버는 유지하되, 내부적으로 원격 서비스 호출

**장점**:
- 완전한 기능 제공
- 클라이언트는 로컬 서비스만 호출
- 구현 세부사항 숨김

**단점**:
- 네트워크 의존성
- 지연 시간 증가 가능

### 권장 해결 방안

**방안 1 (서비스/액션 클라이언트 추가)**을 권장합니다.

**이유**:
1. 모든 기능을 직접 호출 가능
2. 타임스탬프 제어 문제도 함께 해결
3. 네트워크를 통한 원격 제어 가능
4. 확장성 좋음

### 구현 체크리스트

#### 현재 브랜치 수정 (`pinky_lcd_display_controller`)

- [ ] 서비스 클라이언트 추가
  - [ ] SetDisplay 클라이언트
  - [ ] SetStyle 클라이언트
  - [ ] ClearDisplay 클라이언트
  - [ ] SetLayout 클라이언트

- [ ] 액션 클라이언트 추가
  - [ ] SetDisplayAction 클라이언트
  - [ ] ScrollTextAction 클라이언트

- [ ] 서비스 콜백 수정
  - [ ] `set_display_callback`: 서비스 클라이언트로 전달
  - [ ] `set_style_callback`: 서비스 클라이언트로 전달
  - [ ] `clear_display_callback`: 서비스 클라이언트로 전달

- [ ] 헬퍼 메서드 추가
  - [ ] `call_set_layout()`: SetLayout 서비스 호출
  - [ ] `call_set_display_action()`: SetDisplayAction 호출
  - [ ] `call_scroll_text_action()`: ScrollTextAction 호출
  - [ ] `_fallback_to_topic()`: 서비스 없을 때 토픽으로 폴백

- [ ] 의존성 추가
  - [ ] `package.xml`에 `rclpy.action` 확인
  - [ ] import 문 추가

### 네트워크 설정

**요구사항**:
- 서버와 로봇이 같은 ROS2 도메인에 있어야 함
- 네트워크 연결 필요

**설정 방법**:
```bash
# 서버 측
export ROS_DOMAIN_ID=0

# 로봇 측
export ROS_DOMAIN_ID=0
```

### 사용 예시

**구현 후 사용 방법**:

```python
# Python 코드에서 사용
from pinky_lcd_display_controller.lcd_controller_server import LCDControllerServer

# 노드 생성
node = LCDControllerServer()

# SetLayout 호출
node.call_set_layout(
    alignment=1,  # CENTER
    layout_mode=1,  # MULTI_LINE
    margin_top=10,
    margin_bottom=10,
    margin_left=10,
    margin_right=10,
    line_spacing=24,
    grid_columns=1,
    grid_rows=1
)

# SetDisplayAction 호출
goal_handle = node.call_set_display_action(
    title="Processing",
    lines=["Task: Data processing", "Status: In progress"],
    show_timestamp=True,
    duration_ms=5000,
    animation_type=1  # FADE_IN
)
```

---

## 수정 브랜치 요약

### 문제 1: 타임스탬프 제어

| 수정 항목 | 브랜치 | 파일 |
|----------|--------|------|
| 토픽 메시지에 타임스탬프 정보 포함 | 현재 브랜치 | `pinky_lcd_display_controller/lcd_controller_server.py` |
| 타임스탬프 플래그 파싱 및 적용 | `base/ROS2/rfred` | `pinky_lcd_display/lcd_node.py` |

### 문제 2: 모든 기능 호출

| 수정 항목 | 브랜치 | 파일 |
|----------|--------|------|
| 서비스/액션 클라이언트 추가 | 현재 브랜치 | `pinky_lcd_display_controller/lcd_controller_server.py` |
| 서비스 콜백 수정 | 현재 브랜치 | `pinky_lcd_display_controller/lcd_controller_server.py` |
| 헬퍼 메서드 추가 | 현재 브랜치 | `pinky_lcd_display_controller/lcd_controller_server.py` |

---

## 우선순위

### 높은 우선순위

1. **문제 1 해결** (타임스탬프 제어)
   - 사용자 요구사항 충족
   - 기본 기능 완성

2. **문제 2 해결** (모든 기능 호출)
   - 확장성 및 편의성 향상
   - 원격 제어 가능

### 구현 순서

1. **1단계**: 문제 1 해결 (타임스탬프 제어)
   - `base/ROS2/rfred` 브랜치 수정
   - 현재 브랜치 수정

2. **2단계**: 문제 2 해결 (서비스/액션 클라이언트)
   - 현재 브랜치에 클라이언트 추가
   - 서비스 콜백 수정

---

## 참고 자료

- [종합 테스트 가이드](COMPREHENSIVE_TEST_GUIDE.md)
- [개발 현황 문서](DEVELOPMENT_STATUS.md)
- [인터페이스 동기화 리포트](../../pinky_lcd_display_interfaces/INTERFACE_SYNC_REPORT.md)

---

**작성일**: 2025년 11월 8일  
**상태**: 해결 방안 제시 완료, 구현 대기

