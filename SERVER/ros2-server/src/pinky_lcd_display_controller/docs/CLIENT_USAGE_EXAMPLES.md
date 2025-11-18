# 서비스/액션 클라이언트 사용 예시

## 개요

`pinky_lcd_display_controller` 패키지가 이제 `pinky_lcd_display` 패키지의 모든 서비스와 액션을 직접 호출할 수 있습니다. 이 문서는 Python 코드에서 이러한 기능을 사용하는 방법을 설명합니다.

## 서비스 클라이언트 사용

### SetDisplay 서비스

서비스를 통해 호출하면 자동으로 `pinky_lcd_display`의 서비스를 호출합니다:

```python
import rclpy
from pinky_lcd_display_interfaces.srv import SetDisplay

rclpy.init()
node = rclpy.create_node('test_client')

# 서비스 클라이언트 생성
client = node.create_client(SetDisplay, 'lcd_controller/set_display')

# 서비스 대기
if client.wait_for_service(timeout_sec=1.0):
    request = SetDisplay.Request()
    request.title = 'Test'
    request.lines = ['Line 1', 'Line 2']
    request.show_timestamp = True
    
    future = client.call_async(request)
    rclpy.spin_until_future_complete(node, future)
    
    if future.done():
        response = future.result()
        print(f"Success: {response.success}, Message: {response.message}")
```

### SetLayout 서비스

`LCDControllerServer` 인스턴스의 헬퍼 메서드를 사용:

```python
from pinky_lcd_display_controller.lcd_controller_server import LCDControllerServer
import rclpy

rclpy.init()
node = LCDControllerServer()

# SetLayout 호출
success = node.call_set_layout(
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

if success:
    print("Layout updated successfully")
```

## 액션 클라이언트 사용

### SetDisplayAction

```python
from pinky_lcd_display_controller.lcd_controller_server import LCDControllerServer
import rclpy

rclpy.init()
node = LCDControllerServer()

# SetDisplayAction 호출 (페이드 인 효과, 5초간 표시)
goal_handle = node.call_set_display_action(
    title='Processing',
    lines=['Task: Data processing', 'Status: In progress'],
    show_timestamp=True,
    duration_ms=5000,
    animation_type=1  # FADE_IN
)

if goal_handle:
    print("Action goal accepted")
    # 결과 대기 (선택적)
    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future)
    if result_future.done():
        result = result_future.result().result
        print(f"Action completed: {result.success}, Duration: {result.actual_duration_ms}ms")
```

### ScrollTextAction

```python
from pinky_lcd_display_controller.lcd_controller_server import LCDControllerServer
import rclpy

rclpy.init()
node = LCDControllerServer()

# ScrollTextAction 호출
goal_handle = node.call_scroll_text_action(
    text='This is a very long text that needs to be scrolled across the screen',
    scroll_speed_ms=50,
    direction=0,  # LEFT
    repeat_count=1
)

if goal_handle:
    print("Scroll action goal accepted")
    # 결과 대기
    result_future = goal_handle.get_result_async()
    rclpy.spin_until_future_complete(node, result_future)
    if result_future.done():
        result = result_future.result().result
        print(f"Scroll completed: {result.success}, Total time: {result.total_scroll_time_ms}ms")
```

## 통합 예시

```python
#!/usr/bin/env python3
"""
LCD 디스플레이 제어 예시
"""
import rclpy
from pinky_lcd_display_controller.lcd_controller_server import LCDControllerServer
import time

def main():
    rclpy.init()
    node = LCDControllerServer()
    
    # 서비스가 준비될 때까지 대기
    time.sleep(2.0)
    
    # 1. 레이아웃 설정
    print("Setting layout...")
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
    
    # 2. 기본 표시
    print("Setting display...")
    from pinky_lcd_display_interfaces.srv import SetDisplay
    request = SetDisplay.Request()
    request.title = 'System Status'
    request.lines = ['Battery: 85%', 'Mode: IDLE']
    request.show_timestamp = True
    # 서비스는 자동으로 호출됨 (서비스 콜백에서)
    
    # 3. 애니메이션 효과
    print("Sending action with animation...")
    goal_handle = node.call_set_display_action(
        title='Alert',
        lines=['Low battery!', 'Please charge'],
        show_timestamp=True,
        duration_ms=5000,
        animation_type=1  # FADE_IN
    )
    
    if goal_handle:
        # 결과 대기
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(node, result_future, timeout_sec=6.0)
    
    # 4. 스크롤 텍스트
    print("Sending scroll action...")
    goal_handle = node.call_scroll_text_action(
        text='This is a scrolling text example',
        scroll_speed_ms=50,
        direction=0,  # LEFT
        repeat_count=1
    )
    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## 폴백 동작

서비스가 사용 불가능한 경우 자동으로 토픽으로 폴백합니다:

- `SetDisplay`: 토픽 `/lcd/status`로 폴백
- `ClearDisplay`: 토픽 `/lcd/status`로 폴백
- `SetStyle`: 폴백 없음 (서비스 필수)
- `SetLayout`: 폴백 없음 (서비스 필수)
- 액션: 폴백 없음 (액션 필수)

## 네트워크 설정

서버와 로봇이 같은 ROS2 도메인에 있어야 합니다:

```bash
# 서버 측
export ROS_DOMAIN_ID=0

# 로봇 측
export ROS_DOMAIN_ID=0
```

## 주의사항

1. **네트워크 연결**: 서비스/액션은 네트워크를 통해 호출되므로 지연이 발생할 수 있습니다.
2. **서비스 가용성**: `pinky_lcd_display` 노드가 실행 중이어야 합니다.
3. **타임아웃**: 서비스가 1초 내에 응답하지 않으면 폴백 또는 실패 처리됩니다.

