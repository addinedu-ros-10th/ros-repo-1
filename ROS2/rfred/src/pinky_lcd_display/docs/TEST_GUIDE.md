# pinky_lcd_display_controller 테스트 가이드

## 개요

이 문서는 `pinky_lcd_display_controller` 패키지의 모든 인터페이스를 테스트하는 방법을 설명합니다. 자동 테스트 코드와 수동 테스트 방법을 포함합니다.

## 테스트 환경 설정

### 1. 패키지 빌드

```bash
cd ~/ros-repo-1/SERVER/ros2-server
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display_controller
source install/setup.bash
```

### 2. 테스트 노드 실행

**터미널 1: LCD 노드 실행 (로봇 측)**
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

**터미널 2: 컨트롤러 서버 실행**
```bash
cd ~/ros-repo-1/SERVER/ros2-server
source install/setup.bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

## 자동 테스트 코드

### 테스트 스크립트 위치

테스트 스크립트는 `pinky_lcd_display_controller/test/` 디렉토리에 위치합니다.

### 1. 기본 서비스 테스트

**파일**: `test/test_services.py`

```python
#!/usr/bin/env python3
"""
pinky_lcd_display_controller 기본 서비스 테스트
"""
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.srv import SetDisplay, SetStyle, ClearDisplay
import time


class ServiceTester(Node):
    def __init__(self):
        super().__init__('service_tester')
        
        # 서비스 클라이언트 생성
        self.set_display_client = self.create_client(
            SetDisplay, 'lcd_controller/set_display'
        )
        self.set_style_client = self.create_client(
            SetStyle, 'lcd_controller/set_style'
        )
        self.clear_display_client = self.create_client(
            ClearDisplay, 'lcd_controller/clear_display'
        )
        
        # 서비스 대기
        self.wait_for_services()
    
    def wait_for_services(self):
        """모든 서비스가 준비될 때까지 대기"""
        self.get_logger().info('Waiting for services...')
        self.set_display_client.wait_for_service(timeout_sec=5.0)
        self.set_style_client.wait_for_service(timeout_sec=5.0)
        self.clear_display_client.wait_for_service(timeout_sec=5.0)
        self.get_logger().info('All services ready!')
    
    def test_set_display(self):
        """SetDisplay 서비스 테스트"""
        self.get_logger().info('=== Testing SetDisplay Service ===')
        
        request = SetDisplay.Request()
        request.title = 'Test Display'
        request.lines = ['Line 1', 'Line 2', 'Line 3']
        request.show_timestamp = True
        
        future = self.set_display_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'✅ SetDisplay SUCCESS: {response.message}')
                return True
            else:
                self.get_logger().error(f'❌ SetDisplay FAILED: {response.message}')
                return False
        else:
            self.get_logger().error('❌ SetDisplay: Service call timeout')
            return False
    
    def test_set_style(self):
        """SetStyle 서비스 테스트"""
        self.get_logger().info('=== Testing SetStyle Service ===')
        
        request = SetStyle.Request()
        request.bg_color_r = 0
        request.bg_color_g = 0
        request.bg_color_b = 0
        request.title_color_r = 0
        request.title_color_g = 255
        request.title_color_b = 0
        request.body_color_r = 255
        request.body_color_g = 255
        request.body_color_b = 255
        request.timestamp_color_r = 100
        request.timestamp_color_g = 100
        request.timestamp_color_b = 255
        request.title_font_size = 20
        request.body_font_size = 18
        request.font_path = ''
        
        future = self.set_style_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'✅ SetStyle SUCCESS: {response.message}')
                return True
            else:
                self.get_logger().error(f'❌ SetStyle FAILED: {response.message}')
                return False
        else:
            self.get_logger().error('❌ SetStyle: Service call timeout')
            return False
    
    def test_clear_display(self):
        """ClearDisplay 서비스 테스트"""
        self.get_logger().info('=== Testing ClearDisplay Service ===')
        
        request = ClearDisplay.Request()
        future = self.clear_display_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'✅ ClearDisplay SUCCESS: {response.message}')
                return True
            else:
                self.get_logger().error(f'❌ ClearDisplay FAILED: {response.message}')
                return False
        else:
            self.get_logger().error('❌ ClearDisplay: Service call timeout')
            return False
    
    def test_korean_text(self):
        """한글 텍스트 표시 테스트"""
        self.get_logger().info('=== Testing Korean Text Display ===')
        
        request = SetDisplay.Request()
        request.title = '안녕 핑키'
        request.lines = ['한글 테스트', '테스트 성공!']
        request.show_timestamp = True
        
        future = self.set_display_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() is not None:
            response = future.result()
            if response.success:
                self.get_logger().info(f'✅ Korean Text SUCCESS: {response.message}')
                return True
            else:
                self.get_logger().error(f'❌ Korean Text FAILED: {response.message}')
                return False
        else:
            self.get_logger().error('❌ Korean Text: Service call timeout')
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.get_logger().info('=' * 50)
        self.get_logger().info('Starting Service Tests')
        self.get_logger().info('=' * 50)
        
        results = []
        
        # 테스트 실행
        results.append(('SetDisplay', self.test_set_display()))
        time.sleep(1)
        
        results.append(('SetStyle', self.test_set_style()))
        time.sleep(1)
        
        results.append(('ClearDisplay', self.test_clear_display()))
        time.sleep(1)
        
        results.append(('Korean Text', self.test_korean_text()))
        time.sleep(1)
        
        # 결과 요약
        self.get_logger().info('=' * 50)
        self.get_logger().info('Test Results Summary')
        self.get_logger().info('=' * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = '✅ PASS' if result else '❌ FAIL'
            self.get_logger().info(f'{status}: {test_name}')
        
        self.get_logger().info('=' * 50)
        self.get_logger().info(f'Total: {passed}/{total} tests passed')
        self.get_logger().info('=' * 50)
        
        return passed == total


def main():
    rclpy.init()
    tester = ServiceTester()
    
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        tester.get_logger().error(f'Test failed with exception: {e}')
        exit_code = 1
    finally:
        tester.destroy_node()
        rclpy.shutdown()
    
    exit(exit_code)


if __name__ == '__main__':
    main()
```

---

### 2. 액션 테스트 (구현 예정)

**파일**: `test/test_actions.py`

```python
#!/usr/bin/env python3
"""
pinky_lcd_display_controller 액션 테스트
"""
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from pinky_lcd_display_interfaces.action import SetDisplay as SetDisplayAction
from pinky_lcd_display_interfaces.action import ScrollText
import time


class ActionTester(Node):
    def __init__(self):
        super().__init__('action_tester')
        
        # 액션 클라이언트 생성
        self.set_display_action_client = ActionClient(
            self, SetDisplayAction, 'lcd_controller/set_display_action'
        )
        self.scroll_text_action_client = ActionClient(
            self, ScrollText, 'lcd_controller/scroll_text_action'
        )
    
    def wait_for_action_servers(self):
        """액션 서버가 준비될 때까지 대기"""
        self.get_logger().info('Waiting for action servers...')
        self.set_display_action_client.wait_for_server(timeout_sec=5.0)
        self.scroll_text_action_client.wait_for_server(timeout_sec=5.0)
        self.get_logger().info('All action servers ready!')
    
    def test_set_display_action(self, duration_ms=3000, animation_type=0):
        """SetDisplayAction 테스트"""
        self.get_logger().info(f'=== Testing SetDisplayAction (duration={duration_ms}ms, animation={animation_type}) ===')
        
        goal_msg = SetDisplayAction.Goal()
        goal_msg.title = 'Action Test'
        goal_msg.lines = ['Testing action', 'Duration test']
        goal_msg.show_timestamp = True
        goal_msg.duration_ms = duration_ms
        goal_msg.animation_type = animation_type
        
        send_goal_future = self.set_display_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future, timeout_sec=5.0)
        
        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('❌ SetDisplayAction: Goal rejected')
            return False
        
        self.get_logger().info('✅ SetDisplayAction: Goal accepted')
        
        # Result 대기
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=(duration_ms/1000 + 5))
        
        result = result_future.result().result
        if result.success:
            self.get_logger().info(f'✅ SetDisplayAction SUCCESS: {result.message}')
            self.get_logger().info(f'   Actual duration: {result.actual_duration_ms}ms')
            return True
        else:
            self.get_logger().error(f'❌ SetDisplayAction FAILED: {result.message}')
            return False
    
    def test_scroll_text_action(self, direction=0, scroll_speed_ms=50, repeat_count=1):
        """ScrollTextAction 테스트"""
        self.get_logger().info(f'=== Testing ScrollTextAction (direction={direction}, speed={scroll_speed_ms}ms) ===')
        
        goal_msg = ScrollText.Goal()
        goal_msg.text = 'This is a very long text that needs to be scrolled to be displayed properly on the LCD screen'
        goal_msg.scroll_speed_ms = scroll_speed_ms
        goal_msg.direction = direction
        goal_msg.repeat_count = repeat_count
        
        send_goal_future = self.scroll_text_action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        rclpy.spin_until_future_complete(self, send_goal_future, timeout_sec=5.0)
        
        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('❌ ScrollTextAction: Goal rejected')
            return False
        
        self.get_logger().info('✅ ScrollTextAction: Goal accepted')
        
        # Result 대기 (스크롤 완료까지)
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=30.0)
        
        result = result_future.result().result
        if result.success:
            self.get_logger().info(f'✅ ScrollTextAction SUCCESS: {result.message}')
            self.get_logger().info(f'   Total scroll time: {result.total_scroll_time_ms}ms')
            return True
        else:
            self.get_logger().error(f'❌ ScrollTextAction FAILED: {result.message}')
            return False
    
    def feedback_callback(self, feedback_msg):
        """피드백 콜백"""
        feedback = feedback_msg.feedback
        if hasattr(feedback, 'progress_percent'):
            self.get_logger().info(
                f'   Progress: {feedback.progress_percent}% '
                f'({feedback.elapsed_ms}ms elapsed)'
            )
        if hasattr(feedback, 'status_message') and feedback.status_message:
            self.get_logger().info(f'   Status: {feedback.status_message}')
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.get_logger().info('=' * 50)
        self.get_logger().info('Starting Action Tests')
        self.get_logger().info('=' * 50)
        
        self.wait_for_action_servers()
        
        results = []
        
        # SetDisplayAction 테스트
        results.append(('SetDisplayAction (NONE)', 
                        self.test_set_display_action(duration_ms=3000, animation_type=0)))
        time.sleep(1)
        
        results.append(('SetDisplayAction (FADE_IN)', 
                        self.test_set_display_action(duration_ms=3000, animation_type=1)))
        time.sleep(1)
        
        results.append(('SetDisplayAction (SLIDE)', 
                        self.test_set_display_action(duration_ms=3000, animation_type=2)))
        time.sleep(1)
        
        # ScrollTextAction 테스트
        results.append(('ScrollTextAction (LEFT)', 
                        self.test_scroll_text_action(direction=0, scroll_speed_ms=50)))
        time.sleep(1)
        
        results.append(('ScrollTextAction (RIGHT)', 
                        self.test_scroll_text_action(direction=1, scroll_speed_ms=50)))
        time.sleep(1)
        
        # 결과 요약
        self.get_logger().info('=' * 50)
        self.get_logger().info('Test Results Summary')
        self.get_logger().info('=' * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = '✅ PASS' if result else '❌ FAIL'
            self.get_logger().info(f'{status}: {test_name}')
        
        self.get_logger().info('=' * 50)
        self.get_logger().info(f'Total: {passed}/{total} tests passed')
        self.get_logger().info('=' * 50)
        
        return passed == total


def main():
    rclpy.init()
    tester = ActionTester()
    
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        tester.get_logger().error(f'Test failed with exception: {e}')
        exit_code = 1
    finally:
        tester.destroy_node()
        rclpy.shutdown()
    
    exit(exit_code)


if __name__ == '__main__':
    main()
```

---

### 3. 토픽 테스트 (구현 예정)

**파일**: `test/test_topics.py`

```python
#!/usr/bin/env python3
"""
pinky_lcd_display_controller 토픽 테스트
"""
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.msg import LCDStatus, LCDEvent
from pinky_lcd_display_interfaces.srv import SetDisplay
import time


class TopicTester(Node):
    def __init__(self):
        super().__init__('topic_tester')
        
        # 토픽 구독
        self.status_subscription = self.create_subscription(
            LCDStatus,
            '/lcd_controller/status',
            self.status_callback,
            10
        )
        
        self.event_subscription = self.create_subscription(
            LCDEvent,
            '/lcd_controller/events',
            self.event_callback,
            10
        )
        
        # 서비스 클라이언트 (테스트용)
        self.set_display_client = self.create_client(
            SetDisplay, 'lcd_controller/set_display'
        )
        
        self.status_received = False
        self.event_received = False
        self.status_count = 0
        self.event_count = 0
    
    def wait_for_services(self):
        """서비스가 준비될 때까지 대기"""
        self.set_display_client.wait_for_service(timeout_sec=5.0)
    
    def status_callback(self, msg):
        """상태 토픽 콜백"""
        self.status_received = True
        self.status_count += 1
        self.get_logger().info(f'📊 Status received #{self.status_count}:')
        self.get_logger().info(f'   Active: {msg.is_active}')
        self.get_logger().info(f'   Title: {msg.current_title}')
        self.get_logger().info(f'   Lines: {msg.current_lines}')
        self.get_logger().info(f'   Display Mode: {msg.display_mode}')
    
    def event_callback(self, msg):
        """이벤트 토픽 콜백"""
        self.event_received = True
        self.event_count += 1
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
        self.get_logger().info(f'📢 Event received #{self.event_count}: {event_name} - {msg.message}')
    
    def test_status_topic(self):
        """LCDStatus 토픽 테스트"""
        self.get_logger().info('=== Testing LCDStatus Topic ===')
        
        self.status_received = False
        self.status_count = 0
        
        # 서비스 호출하여 상태 변경 유도
        request = SetDisplay.Request()
        request.title = 'Status Test'
        request.lines = ['Testing status topic']
        request.show_timestamp = True
        
        future = self.set_display_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        # 상태 토픽 수신 대기
        timeout = 5.0
        start_time = time.time()
        while not self.status_received and (time.time() - start_time) < timeout:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        if self.status_received:
            self.get_logger().info(f'✅ LCDStatus Topic: Received {self.status_count} messages')
            return True
        else:
            self.get_logger().error('❌ LCDStatus Topic: No messages received')
            return False
    
    def test_event_topic(self):
        """LCDEvent 토픽 테스트"""
        self.get_logger().info('=== Testing LCDEvent Topic ===')
        
        self.event_received = False
        self.event_count = 0
        
        # 서비스 호출하여 이벤트 발생 유도
        request = SetDisplay.Request()
        request.title = 'Event Test'
        request.lines = ['Testing event topic']
        request.show_timestamp = True
        
        future = self.set_display_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        # 이벤트 토픽 수신 대기
        timeout = 5.0
        start_time = time.time()
        while not self.event_received and (time.time() - start_time) < timeout:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        if self.event_received:
            self.get_logger().info(f'✅ LCDEvent Topic: Received {self.event_count} events')
            return True
        else:
            self.get_logger().error('❌ LCDEvent Topic: No events received')
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.get_logger().info('=' * 50)
        self.get_logger().info('Starting Topic Tests')
        self.get_logger().info('=' * 50)
        
        self.wait_for_services()
        
        results = []
        
        # 토픽 테스트
        results.append(('LCDStatus Topic', self.test_status_topic()))
        time.sleep(2)
        
        results.append(('LCDEvent Topic', self.test_event_topic()))
        time.sleep(2)
        
        # 결과 요약
        self.get_logger().info('=' * 50)
        self.get_logger().info('Test Results Summary')
        self.get_logger().info('=' * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = '✅ PASS' if result else '❌ FAIL'
            self.get_logger().info(f'{status}: {test_name}')
        
        self.get_logger().info('=' * 50)
        self.get_logger().info(f'Total: {passed}/{total} tests passed')
        self.get_logger().info('=' * 50)
        
        return passed == total


def main():
    rclpy.init()
    tester = TopicTester()
    
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        tester.get_logger().error(f'Test failed with exception: {e}')
        exit_code = 1
    finally:
        tester.destroy_node()
        rclpy.shutdown()
    
    exit(exit_code)


if __name__ == '__main__':
    main()
```

---

### 4. 통합 테스트

**파일**: `test/test_integration.py`

```python
#!/usr/bin/env python3
"""
pinky_lcd_display_controller 통합 테스트
모든 기능을 종합적으로 테스트합니다.
"""
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.srv import SetDisplay, ClearDisplay, SetLayout, SetParameter, GetParameter
from pinky_lcd_display_interfaces.action import SetDisplay as SetDisplayAction
from rclpy.action import ActionClient
import time


class IntegrationTester(Node):
    def __init__(self):
        super().__init__('integration_tester')
        
        # 서비스 클라이언트
        self.set_display_client = self.create_client(SetDisplay, 'lcd_controller/set_display')
        self.clear_display_client = self.create_client(ClearDisplay, 'lcd_controller/clear_display')
        self.set_layout_client = self.create_client(SetLayout, 'lcd_controller/set_layout')
        self.set_parameter_client = self.create_client(SetParameter, 'lcd_controller/set_parameter')
        self.get_parameter_client = self.create_client(GetParameter, 'lcd_controller/get_parameter')
        
        # 액션 클라이언트
        self.set_display_action_client = ActionClient(
            self, SetDisplayAction, 'lcd_controller/set_display_action'
        )
    
    def wait_for_services(self):
        """모든 서비스가 준비될 때까지 대기"""
        services = [
            self.set_display_client,
            self.clear_display_client,
            self.set_layout_client,
            self.set_parameter_client,
            self.get_parameter_client
        ]
        
        for service in services:
            service.wait_for_service(timeout_sec=5.0)
    
    def test_workflow_1_basic_display(self):
        """워크플로우 1: 기본 표시"""
        self.get_logger().info('=== Workflow 1: Basic Display ===')
        
        # 1. 화면 지우기
        request = ClearDisplay.Request()
        future = self.clear_display_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        # 2. 내용 표시
        request = SetDisplay.Request()
        request.title = 'Workflow Test'
        request.lines = ['Step 1: Clear', 'Step 2: Display']
        request.show_timestamp = True
        
        future = self.set_display_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() and future.result().success:
            self.get_logger().info('✅ Workflow 1: SUCCESS')
            return True
        else:
            self.get_logger().error('❌ Workflow 1: FAILED')
            return False
    
    def test_workflow_2_parameter_management(self):
        """워크플로우 2: 파라미터 관리"""
        self.get_logger().info('=== Workflow 2: Parameter Management ===')
        
        # 1. 파라미터 설정
        request = SetParameter.Request()
        request.parameter_name = 'update_rate'
        request.parameter_value = '20'
        
        future = self.set_parameter_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if not future.result() or not future.result().success:
            self.get_logger().error('❌ Workflow 2: SetParameter FAILED')
            return False
        
        # 2. 파라미터 조회
        request = GetParameter.Request()
        request.parameter_name = 'update_rate'
        
        future = self.get_parameter_client.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        
        if future.result() and future.result().success:
            value = future.result().parameter_value
            if value == '20':
                self.get_logger().info('✅ Workflow 2: SUCCESS')
                return True
            else:
                self.get_logger().error(f'❌ Workflow 2: Value mismatch ({value} != 20)')
                return False
        else:
            self.get_logger().error('❌ Workflow 2: GetParameter FAILED')
            return False
    
    def test_workflow_3_action_with_feedback(self):
        """워크플로우 3: 액션 피드백"""
        self.get_logger().info('=== Workflow 3: Action with Feedback ===')
        
        goal_msg = SetDisplayAction.Goal()
        goal_msg.title = 'Action Test'
        goal_msg.lines = ['Testing feedback']
        goal_msg.show_timestamp = True
        goal_msg.duration_ms = 3000
        goal_msg.animation_type = 1
        
        send_goal_future = self.set_display_action_client.send_goal_async(
            goal_msg,
            feedback_callback=lambda f: self.get_logger().info(f'Feedback: {f.feedback.progress_percent}%')
        )
        rclpy.spin_until_future_complete(self, send_goal_future, timeout_sec=5.0)
        
        goal_handle = send_goal_future.result()
        if not goal_handle.accepted:
            self.get_logger().error('❌ Workflow 3: Goal rejected')
            return False
        
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future, timeout_sec=10.0)
        
        if result_future.result().result.success:
            self.get_logger().info('✅ Workflow 3: SUCCESS')
            return True
        else:
            self.get_logger().error('❌ Workflow 3: FAILED')
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        self.get_logger().info('=' * 50)
        self.get_logger().info('Starting Integration Tests')
        self.get_logger().info('=' * 50)
        
        self.wait_for_services()
        
        results = []
        
        results.append(('Workflow 1: Basic Display', self.test_workflow_1_basic_display()))
        time.sleep(2)
        
        results.append(('Workflow 2: Parameter Management', self.test_workflow_2_parameter_management()))
        time.sleep(2)
        
        results.append(('Workflow 3: Action with Feedback', self.test_workflow_3_action_with_feedback()))
        time.sleep(2)
        
        # 결과 요약
        self.get_logger().info('=' * 50)
        self.get_logger().info('Integration Test Results')
        self.get_logger().info('=' * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = '✅ PASS' if result else '❌ FAIL'
            self.get_logger().info(f'{status}: {test_name}')
        
        self.get_logger().info('=' * 50)
        self.get_logger().info(f'Total: {passed}/{total} workflows passed')
        self.get_logger().info('=' * 50)
        
        return passed == total


def main():
    rclpy.init()
    tester = IntegrationTester()
    
    try:
        success = tester.run_all_tests()
        exit_code = 0 if success else 1
    except Exception as e:
        tester.get_logger().error(f'Test failed with exception: {e}')
        exit_code = 1
    finally:
        tester.destroy_node()
        rclpy.shutdown()
    
    exit(exit_code)


if __name__ == '__main__':
    main()
```

---

## 테스트 실행 방법

### 1. 개별 테스트 실행

```bash
# 서비스 테스트
python3 test/test_services.py

# 액션 테스트 (구현 예정)
python3 test/test_actions.py

# 토픽 테스트 (구현 예정)
python3 test/test_topics.py

# 통합 테스트
python3 test/test_integration.py
```

### 2. 모든 테스트 실행

```bash
# 테스트 스크립트 실행
./test/run_all_tests.sh
```

### 3. pytest를 사용한 테스트 (선택사항)

```bash
pytest test/ -v
```

## 테스트 결과 해석

### 성공적인 테스트

- 모든 서비스 호출이 성공적으로 완료됨
- 예상된 응답을 받음
- 에러 메시지 없음

### 실패한 테스트

- 서비스 호출 타임아웃
- 예상과 다른 응답
- 에러 메시지 출력

## 문제 해결

### 테스트가 실패하는 경우

1. **서버 노드가 실행 중인지 확인**
   ```bash
   ros2 node list | grep lcd_controller
   ```

2. **서비스가 등록되어 있는지 확인**
   ```bash
   ros2 service list | grep lcd_controller
   ```

3. **네트워크 연결 확인**
   ```bash
   ros2 topic list
   ```

4. **로그 확인**
   ```bash
   # 서버 로그 확인
   ros2 run pinky_lcd_display_controller lcd_controller_server
   ```

## 참고

- [사용자 가이드](USER_GUIDE.md) - 상세한 사용 방법
- [구현 계획서](IMPLEMENTATION_PLAN.md) - 구현 대상 목록 및 현황

