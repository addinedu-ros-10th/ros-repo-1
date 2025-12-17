# 서비스/액션 실행 흐름 상세 설명

## 개요

이 문서는 `pinky_lcd_display_controller` 패키지에서 서비스와 액션 커맨드가 실행될 때 수행되는 상세한 내용을 설명합니다.

---

## 서비스 커맨드 실행 흐름

### 1. SetDisplay 서비스

#### 사용자 커맨드
```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1', 'Line 2'], show_timestamp: true}"
```

#### 실행 흐름

1. **서비스 요청 수신** (`lcd_controller_server.py:167-198`)
   - `set_display_callback()` 함수가 호출됨
   - 요청 파라미터: `title`, `lines`, `show_timestamp`

2. **서비스 클라이언트 호출 시도** (`lcd_controller_server.py:177-192`)
   ```python
   if self.set_display_client.wait_for_service(timeout_sec=1.0):
       # pinky_lcd_display의 서비스를 직접 호출
       future = self.set_display_client.call_async(request)
       rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
   ```
   - `pinky_lcd_display` 패키지의 `/lcd_controller/set_display` 서비스가 사용 가능한지 확인
   - 사용 가능하면 서비스를 비동기로 호출
   - 최대 2초 대기

3. **pinky_lcd_display에서 처리** (base/ROS2/rfred 브랜치)
   - `lcd_node.py`의 `set_display_callback()` 실행
   - 내부 상태 업데이트:
     ```python
     self.current_title = request.title
     self.current_lines = list(request.lines)
     self.show_timestamp = request.show_timestamp
     ```
   - LCD 매니저를 통해 화면 표시:
     ```python
     self.lcd_manager.show_status(
         title=request.title,
         lines=list(request.lines),
         footer_timestamp=request.show_timestamp,
     )
     ```
   - 이벤트 발행: `DISPLAY_STARTED` 이벤트를 `/lcd_controller/events` 토픽에 발행

4. **응답 반환**
   - 서비스 성공 시: `success: true, message: "Display updated successfully"`
   - 서비스 실패 시: 폴백 로직 실행

5. **폴백 처리** (서비스 사용 불가능한 경우)
   - `_fallback_to_topic_set_display()` 함수 실행
   - `/lcd/status` 토픽에 `std_msgs/String` 메시지 발행
   - 메시지 형식: `"Title\nLine1\nLine2"`
   - `pinky_lcd_display`의 `status_callback()`이 토픽을 구독하여 처리

#### 최종 결과
- LCD 화면에 타이틀과 라인들이 표시됨
- 타임스탬프가 설정된 경우 하단에 시간 표시
- 이벤트 토픽에 `DISPLAY_STARTED` 이벤트 발행 (서비스 사용 시)

---

### 2. SetStyle 서비스

#### 사용자 커맨드
```bash
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 255, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 24, body_font_size: 20, font_path: ''}"
```

#### 실행 흐름

1. **서비스 요청 수신** (`lcd_controller_server.py:200-260`)
   - `set_style_callback()` 함수가 호출됨

2. **서비스 클라이언트 호출** (`lcd_controller_server.py:209-226`)
   ```python
   if self.set_style_client.wait_for_service(timeout_sec=1.0):
       future = self.set_style_client.call_async(request)
       rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
   ```
   - `pinky_lcd_display`의 `/lcd_controller/set_style` 서비스 호출

3. **pinky_lcd_display에서 처리** (base/ROS2/rfred 브랜치)
   - `lcd_node.py`의 `set_style_callback()` 실행
   - LCD 매니저의 스타일 설정:
     ```python
     self.lcd_manager.set_style(
         request.bg_color_r, request.bg_color_g, request.bg_color_b,
         request.title_color_r, request.title_color_g, request.title_color_b,
         request.body_color_r, request.body_color_g, request.body_color_b,
         request.timestamp_color_r, request.timestamp_color_g, request.timestamp_color_b,
         request.title_font_size, request.body_font_size, request.font_path
     )
     ```
   - 현재 표시 내용을 새 스타일로 다시 렌더링:
     ```python
     self.lcd_manager.show_status(
         title=self.current_title,
         lines=self.current_lines,
         footer_timestamp=self.show_timestamp,
     )
     ```

4. **로컬 스타일 저장** (`lcd_controller_server.py:228-253`)
   - `self.current_style` 딕셔너리에 스타일 정보 저장 (참고용)

5. **응답 반환**
   - 성공: `success: true, message: "Style updated successfully"`

#### 최종 결과
- LCD 표시 스타일이 변경됨 (색상, 폰트 크기 등)
- 현재 표시 중인 내용이 새 스타일로 다시 렌더링됨

---

### 3. ClearDisplay 서비스

#### 사용자 커맨드
```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

#### 실행 흐름

1. **서비스 요청 수신** (`lcd_controller_server.py:262-293`)
   - `clear_display_callback()` 함수가 호출됨

2. **서비스 클라이언트 호출** (`lcd_controller_server.py:272-287`)
   ```python
   if self.clear_display_client.wait_for_service(timeout_sec=1.0):
       future = self.clear_display_client.call_async(request)
   ```

3. **pinky_lcd_display에서 처리** (base/ROS2/rfred 브랜치)
   - `lcd_node.py`의 `clear_display_callback()` 실행
   - 내부 상태 초기화:
     ```python
     self.current_title = ""
     self.current_lines = []
     self.show_timestamp = False
     ```
   - 빈 화면 표시:
     ```python
     self.lcd_manager.show_status(
         title="",
         lines=[],
         footer_timestamp=False,
     )
     ```
   - 이벤트 발행: `CLEARED` 이벤트를 `/lcd_controller/events` 토픽에 발행

4. **폴백 처리** (서비스 사용 불가능한 경우)
   - `_fallback_to_topic_clear_display()` 함수 실행
   - `/lcd/status` 토픽에 빈 문자열 발행

#### 최종 결과
- LCD 화면이 지워짐
- 이벤트 토픽에 `CLEARED` 이벤트 발행 (서비스 사용 시)

---

### 4. SetLayout 서비스

#### 사용자 커맨드
```bash
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 1, layout_mode: 1, margin_top: 10, margin_bottom: 10, margin_left: 10, margin_right: 10, line_spacing: 24, grid_columns: 1, grid_rows: 1}"
```

#### 실행 흐름

1. **헬퍼 메서드 호출** (`lcd_controller_server.py:338-385`)
   - `call_set_layout()` 함수 사용
   - Python 코드에서 직접 호출:
     ```python
     node.call_set_layout(alignment=1, layout_mode=1, ...)
     ```

2. **서비스 클라이언트 호출**
   ```python
   if self.set_layout_client.wait_for_service(timeout_sec=1.0):
       request = SetLayout.Request()
       # 파라미터 설정
       future = self.set_layout_client.call_async(request)
   ```

3. **pinky_lcd_display에서 처리** (base/ROS2/rfred 브랜치)
   - `lcd_node.py`의 `set_layout_callback()` 실행
   - LCD 매니저의 레이아웃 설정:
     ```python
     self.lcd_manager.set_layout(
         alignment, layout_mode, margin_top, margin_bottom,
         margin_left, margin_right, line_spacing, grid_columns, grid_rows
     )
     ```
   - 현재 표시 내용을 새 레이아웃으로 다시 렌더링

#### 최종 결과
- 레이아웃 설정이 변경됨 (정렬, 여백, 간격 등)
- 이후 표시되는 내용이 새 레이아웃으로 렌더링됨

---

## 액션 커맨드 실행 흐름

### 1. SetDisplayAction

#### 사용자 커맨드
```bash
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Processing', lines: ['Task: Data processing', 'Status: In progress'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"
```

#### 실행 흐름

1. **액션 Goal 전송** (`lcd_controller_server.py:387-437`)
   - `call_set_display_action()` 메서드 또는 직접 액션 클라이언트 사용
   - Goal 메시지 생성:
     ```python
     goal_msg = SetDisplayAction.Goal()
     goal_msg.title = title
     goal_msg.lines = lines
     goal_msg.show_timestamp = show_timestamp
     goal_msg.duration_ms = duration_ms
     goal_msg.animation_type = animation_type
     ```

2. **액션 서버로 전송**
   ```python
   future = self.set_display_action_client.send_goal_async(goal_msg)
   rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
   ```

3. **pinky_lcd_display에서 처리** (base/ROS2/rfred 브랜치)
   - `lcd_node.py`의 `set_display_action_execute_callback()` 실행
   - 시작 시간 기록:
     ```python
     start_time = self.get_clock().now()
     ```

4. **애니메이션 효과 적용** (base/ROS2/rfred 브랜치)
   - `animation_type`에 따라 다른 효과:
     - `1 (FADE_IN)`: 페이드 인 효과
       ```python
       self.lcd_manager.show_status_with_animation(
           title=goal.title,
           lines=list(goal.lines),
           footer_timestamp=goal.show_timestamp,
           animation_type='fade_in'
       )
       ```
     - `2 (SLIDE)`: 슬라이드 효과
       ```python
       self.lcd_manager.show_status_with_animation(
           animation_type='slide'
       )
       ```
     - `0 (NONE)`: 애니메이션 없음
       ```python
       self.lcd_manager.show_status(
           title=goal.title,
           lines=list(goal.lines),
           footer_timestamp=goal.show_timestamp,
       )
       ```

5. **상태 업데이트**
   ```python
   self.current_title = goal.title
   self.current_lines = list(goal.lines)
   self.show_timestamp = goal.show_timestamp
   self.current_display_mode = 2 if goal.animation_type > 0 else 0
   ```

6. **이벤트 발행**
   - `ANIMATION_STARTED` 이벤트를 `/lcd_controller/events` 토픽에 발행

7. **지속 시간 처리** (`duration_ms > 0`인 경우)
   - 피드백 루프 시작:
     ```python
     while elapsed_ms < goal.duration_ms:
         # 피드백 발행
         feedback_msg = SetDisplayAction.Feedback()
         feedback_msg.elapsed_ms = elapsed_ms
         feedback_msg.progress_percent = int((elapsed_ms / goal.duration_ms) * 100)
         feedback_msg.status_message = "Displaying..."
         goal_handle.publish_feedback(feedback_msg)
         
         # 100ms 대기
         time.sleep(0.1)
         elapsed_ms = (current_time - start_time).nanoseconds / 1_000_000
     ```
   - 지정된 시간 후 자동으로 화면 지움:
     ```python
     self.lcd_manager.show_status(
         title="",
         lines=[],
         footer_timestamp=False,
     )
     ```

8. **결과 반환**
   - `ANIMATION_ENDED` 이벤트 발행
   - Result 메시지:
     ```python
     result = SetDisplayAction.Result()
     result.success = True
     result.message = "Display completed successfully"
     result.actual_duration_ms = int(total_duration)
     ```

#### 최종 결과
- 애니메이션 효과와 함께 LCD에 표시됨
- 지정된 시간 후 자동으로 화면이 지워짐 (duration_ms > 0인 경우)
- 피드백으로 진행 상황 확인 가능
- 이벤트 토픽에 `ANIMATION_STARTED`, `ANIMATION_ENDED` 이벤트 발행

---

### 2. ScrollTextAction

#### 사용자 커맨드
```bash
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'This is a very long text that needs to be scrolled', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
```

#### 실행 흐름

1. **액션 Goal 전송** (`lcd_controller_server.py:439-487`)
   - `call_scroll_text_action()` 메서드 사용
   - Goal 메시지 생성:
     ```python
     goal_msg = ScrollText.Goal()
     goal_msg.text = text
     goal_msg.scroll_speed_ms = scroll_speed_ms
     goal_msg.direction = direction
     goal_msg.repeat_count = repeat_count
     ```

2. **액션 서버로 전송**
   ```python
   future = self.scroll_text_action_client.send_goal_async(goal_msg)
   ```

3. **pinky_lcd_display에서 처리** (base/ROS2/rfred 브랜치)
   - `lcd_node.py`의 `scroll_text_action_execute_callback()` 실행
   - 시작 시간 기록

4. **스크롤 텍스트 표시**
   ```python
   self.lcd_manager.show_scroll_text(
       text=goal.text,
       direction=goal.direction,
       scroll_speed_ms=goal.scroll_speed_ms,
       repeat_count=goal.repeat_count,
       callback=lambda pos, progress: self._scroll_feedback(goal_handle, pos, progress)
   )
   ```

5. **스크롤 애니메이션** (lcd_manager.py)
   - 텍스트 너비 측정
   - 스크롤이 필요한지 확인
   - 스크롤 방향에 따라 프레임 생성:
     - `LEFT (0)`: 왼쪽에서 오른쪽으로 스크롤
     - `RIGHT (1)`: 오른쪽에서 왼쪽으로 스크롤
   - 각 프레임을 `scroll_speed_ms` 간격으로 표시
   - 피드백 콜백 호출:
     ```python
     feedback_msg = ScrollText.Feedback()
     feedback_msg.current_position = current_position
     feedback_msg.progress_percent = progress_percent
     goal_handle.publish_feedback(feedback_msg)
     ```

6. **반복 처리**
   - `repeat_count`만큼 반복 (0이면 무한 반복)

7. **결과 반환**
   ```python
   result = ScrollText.Result()
   result.success = True
   result.message = "Scroll text completed successfully"
   result.total_scroll_time_ms = int(total_duration)
   ```

#### 최종 결과
- 텍스트가 지정된 방향으로 스크롤되어 표시됨
- 피드백으로 현재 위치와 진행률 확인 가능
- 반복 횟수만큼 반복 (0이면 무한)

---

## 액션 사용자 사용 테스트 예시

### 테스트 1: SetDisplayAction - 페이드 인 효과

#### 테스트 목적
페이드 인 애니메이션 효과와 함께 5초간 표시 후 자동으로 화면이 지워지는지 확인

#### 테스트 커맨드

```bash
# 터미널 1: pinky_lcd_display 노드 실행 (로봇에서)
ros2 run pinky_lcd_display lcd_node

# 터미널 2: pinky_lcd_display_controller 노드 실행 (서버에서)
ros2 run pinky_lcd_display_controller lcd_controller_server

# 터미널 3: 액션 호출
ros2 action send_goal --feedback /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Processing', lines: ['Task: Data processing', 'Status: In progress'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"
```

#### 예상 결과

1. **즉시 반응**:
   ```
   Waiting for an action server to become available...
   Sending goal:
      title: 'Processing'
      lines:
        - 'Task: Data processing'
        - 'Status: In progress'
      show_timestamp: True
      duration_ms: 5000
      animation_type: 1
   Goal accepted with ID: <goal_id>
   ```

2. **피드백 수신** (100ms마다):
   ```
   Feedback:
      elapsed_ms: 100
      progress_percent: 2
      status_message: 'Displaying...'
   Feedback:
      elapsed_ms: 200
      progress_percent: 4
      status_message: 'Displaying...'
   ...
   Feedback:
      elapsed_ms: 5000
      progress_percent: 100
      status_message: 'Displaying...'
   ```

3. **결과 수신**:
   ```
   Result:
      success: True
      message: 'Display completed successfully'
      actual_duration_ms: 5000
   Goal finished with status: SUCCEEDED
   ```

4. **LCD 화면**:
   - 페이드 인 효과로 "Processing" 타이틀과 라인들이 나타남
   - 5초 후 자동으로 화면이 지워짐

#### 검증 포인트
- [ ] 페이드 인 애니메이션이 부드럽게 표시됨
- [ ] 피드백이 100ms마다 수신됨
- [ ] 진행률이 0%에서 100%로 증가함
- [ ] 5초 후 자동으로 화면이 지워짐
- [ ] 결과가 성공으로 반환됨

---

### 테스트 2: SetDisplayAction - 슬라이드 효과

#### 테스트 커맨드

```bash
ros2 action send_goal --feedback /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Alert', lines: ['Warning message', 'Please check'], show_timestamp: true, duration_ms: 3000, animation_type: 2}"
```

#### 예상 결과

1. **LCD 화면**:
   - 왼쪽에서 오른쪽으로 슬라이드 효과로 표시됨
   - 3초 후 자동으로 화면이 지워짐

2. **피드백**:
   - 3초 동안 진행률 피드백 수신

#### 검증 포인트
- [ ] 슬라이드 애니메이션이 부드럽게 표시됨
- [ ] 3초 후 자동으로 화면이 지워짐

---

### 테스트 3: SetDisplayAction - 무한 표시

#### 테스트 커맨드

```bash
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Continuous', lines: ['This will stay'], show_timestamp: true, duration_ms: 0, animation_type: 1}"
```

#### 예상 결과

1. **LCD 화면**:
   - 페이드 인 효과로 표시됨
   - 화면이 계속 표시됨 (자동으로 지워지지 않음)

2. **피드백**:
   - 피드백이 발행되지 않음 (duration_ms=0이므로)

#### 검증 포인트
- [ ] 화면이 계속 표시됨
- [ ] 자동으로 지워지지 않음

---

### 테스트 4: ScrollTextAction - 왼쪽 스크롤

#### 테스트 커맨드

```bash
ros2 action send_goal --feedback /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'This is a very long text that needs to be scrolled across the LCD display screen to show all content', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
```

#### 예상 결과

1. **즉시 반응**:
   ```
   Goal accepted with ID: <goal_id>
   ```

2. **피드백 수신** (스크롤 중):
   ```
   Feedback:
      current_position: 0
      progress_percent: 0
   Feedback:
      current_position: 10
      progress_percent: 5
   ...
   Feedback:
      current_position: 200
      progress_percent: 100
   ```

3. **결과 수신**:
   ```
   Result:
      success: True
      message: 'Scroll text completed successfully'
      total_scroll_time_ms: <실제 스크롤 시간>
   Goal finished with status: SUCCEEDED
   ```

4. **LCD 화면**:
   - 텍스트가 왼쪽에서 오른쪽으로 스크롤됨
   - 1회 반복 후 종료

#### 검증 포인트
- [ ] 텍스트가 부드럽게 스크롤됨
- [ ] 피드백으로 현재 위치 확인 가능
- [ ] 1회 반복 후 종료됨

---

### 테스트 5: ScrollTextAction - 오른쪽 스크롤, 3회 반복

#### 테스트 커맨드

```bash
ros2 action send_goal --feedback /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Scrolling from right to left', scroll_speed_ms: 30, direction: 1, repeat_count: 3}"
```

#### 예상 결과

1. **LCD 화면**:
   - 텍스트가 오른쪽에서 왼쪽으로 스크롤됨
   - 3회 반복 후 종료

2. **피드백**:
   - 각 반복마다 피드백 수신

#### 검증 포인트
- [ ] 오른쪽에서 왼쪽으로 스크롤됨
- [ ] 3회 반복됨
- [ ] 각 반복마다 피드백 수신

---

### 테스트 6: ScrollTextAction - 무한 반복

#### 테스트 커맨드

```bash
# Ctrl+C로 중단 가능
ros2 action send_goal --feedback /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Infinite scroll test', scroll_speed_ms: 20, direction: 0, repeat_count: 0}"
```

#### 예상 결과

1. **LCD 화면**:
   - 텍스트가 계속 스크롤됨 (무한 반복)

2. **중단 방법**:
   ```bash
   # 다른 터미널에서 액션 취소
   ros2 action send_goal --cancel /lcd_controller/scroll_text_action \
     pinky_lcd_display_interfaces/action/ScrollText \
     "{text: '', scroll_speed_ms: 0, direction: 0, repeat_count: 0}"
   ```

#### 검증 포인트
- [ ] 무한 반복됨
- [ ] Ctrl+C 또는 취소 명령으로 중단 가능

---

### 테스트 7: 통합 테스트 - 여러 액션 연속 호출

#### 테스트 시나리오

```bash
# 1. 페이드 인 효과, 3초간 표시
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Step 1', lines: ['Fade in test'], show_timestamp: true, duration_ms: 3000, animation_type: 1}"

# 2. 슬라이드 효과, 3초간 표시
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Step 2', lines: ['Slide test'], show_timestamp: true, duration_ms: 3000, animation_type: 2}"

# 3. 스크롤 텍스트
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Final step: Scrolling text', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
```

#### 예상 결과

1. **순차적 실행**:
   - 각 액션이 순차적으로 실행됨
   - 이전 액션이 완료되면 다음 액션이 시작됨

2. **LCD 화면**:
   - Step 1: 페이드 인 → 3초 후 지워짐
   - Step 2: 슬라이드 → 3초 후 지워짐
   - Step 3: 스크롤 텍스트 → 완료 후 종료

#### 검증 포인트
- [ ] 각 액션이 순차적으로 실행됨
- [ ] 이전 액션 완료 후 다음 액션 시작

---

### 테스트 8: Python 코드에서 액션 호출

#### 테스트 스크립트

```python
#!/usr/bin/env python3
"""
액션 호출 테스트 스크립트
"""
import rclpy
from pinky_lcd_display_controller.lcd_controller_server import LCDControllerServer
import time

def main():
    rclpy.init()
    node = LCDControllerServer()
    
    # 서비스/액션이 준비될 때까지 대기
    print("Waiting for services/actions to be available...")
    time.sleep(3.0)
    
    # 1. SetDisplayAction 호출
    print("\n=== Test 1: SetDisplayAction (FADE_IN) ===")
    goal_handle = node.call_set_display_action(
        title='Python Test',
        lines=['Action call from Python', 'Fade in effect'],
        show_timestamp=True,
        duration_ms=5000,
        animation_type=1  # FADE_IN
    )
    
    if goal_handle:
        print("Goal accepted, waiting for result...")
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(node, result_future, timeout_sec=6.0)
        
        if result_future.done():
            result = result_future.result().result
            print(f"Result: success={result.success}, duration={result.actual_duration_ms}ms")
    else:
        print("Failed to send goal")
    
    time.sleep(1.0)
    
    # 2. ScrollTextAction 호출
    print("\n=== Test 2: ScrollTextAction ===")
    goal_handle = node.call_scroll_text_action(
        text='This is a scrolling text test from Python code',
        scroll_speed_ms=50,
        direction=0,  # LEFT
        repeat_count=1
    )
    
    if goal_handle:
        print("Goal accepted, waiting for result...")
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(node, result_future, timeout_sec=10.0)
        
        if result_future.done():
            result = result_future.result().result
            print(f"Result: success={result.success}, total_time={result.total_scroll_time_ms}ms")
    else:
        print("Failed to send goal")
    
    print("\nTests completed")
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

#### 실행 방법

```bash
# 스크립트 저장
cat > test_actions.py << 'EOF'
# 위의 Python 코드
EOF

# 실행
python3 test_actions.py
```

#### 예상 결과

```
Waiting for services/actions to be available...

=== Test 1: SetDisplayAction (FADE_IN) ===
Goal accepted, waiting for result...
Result: success=True, duration=5000ms

=== Test 2: ScrollTextAction ===
Goal accepted, waiting for result...
Result: success=True, total_time=<실제 시간>ms

Tests completed
```

---

## 문제 해결

### 액션이 실행되지 않는 경우

1. **액션 서버 확인**:
   ```bash
   ros2 action list | grep lcd_controller
   ```

2. **액션 타입 확인**:
   ```bash
   ros2 interface show pinky_lcd_display_interfaces/action/SetDisplay
   ```

3. **네트워크 연결 확인**:
   ```bash
   # ROS2 도메인 ID 확인
   echo $ROS_DOMAIN_ID
   
   # 서버와 로봇이 같은 도메인에 있어야 함
   ```

### 피드백이 수신되지 않는 경우

- `--feedback` 플래그를 사용했는지 확인
- 액션 서버가 피드백을 발행하는지 확인
- 네트워크 지연 가능성 고려

---

## 참고 자료

- [종합 테스트 가이드](COMPREHENSIVE_TEST_GUIDE.md)
- [클라이언트 사용 예시](CLIENT_USAGE_EXAMPLES.md)
- [테스트 피드백 및 해결 방안](TEST_FEEDBACK_AND_SOLUTIONS.md)

---

**작성일**: 2025년 11월 8일  
**작성 기준**: 실제 코드 분석 결과

