# 서비스 타임아웃 문제 분석 및 해결 방안

## 문제 현상

서비스 호출 시 타임아웃이 발생하여 토픽으로 폴백되는 문제가 발생합니다.

### 로그 분석

**pinky_lcd_display_controller 로그**:
```
[WARN] SetDisplay service call timeout, falling back to topic
[INFO] Display updated via topic: Test\nLine 1...
```

**pinky_lcd_display 로그**:
```
[INFO] SetDisplay service called: Test
[INFO] LCD update request:
Test
Line 1
Line 2
```

### 문제 요약

1. 서비스가 호출되고 있음 (`pinky_lcd_display`에서 "SetDisplay service called" 로그 확인)
2. 하지만 `pinky_lcd_display_controller`에서는 2초 내에 응답을 받지 못함
3. 타임아웃 발생 후 토픽으로 폴백

---

## 원인 분석

### 1. 주요 원인: 서비스 콜백 내부에서 `spin_until_future_complete` 사용

**문제 코드** (`lcd_controller_server.py:180`):
```python
def set_display_callback(self, request, response):
    # ...
    future = self.set_display_client.call_async(request)
    rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)  # 문제!
```

**문제점**:
- `set_display_callback`은 이미 `rclpy.spin()`으로 실행 중인 노드의 서비스 콜백입니다
- 서비스 콜백 내부에서 `spin_until_future_complete`를 호출하면 **데드락**이 발생할 수 있습니다
- 노드가 이미 스핀 중이므로 추가로 스핀할 수 없어 타임아웃이 발생합니다

### 2. 부차적 원인: LCD 렌더링 시간

`pinky_lcd_display`의 `set_display_callback`에서:
```python
self.lcd_manager.show_status(...)  # 동기적 렌더링
```

- LCD 렌더링이 시간이 오래 걸릴 수 있음
- 하지만 이것만으로는 2초 타임아웃을 설명하기 어려움

### 3. 네트워크 지연

- 서버와 로봇 간 네트워크 지연
- 하지만 로그상 서비스는 호출되고 있으므로 네트워크 문제는 아님

---

## 해결 방안

### 방안 1: 콜백 체인 사용 (권장)

서비스 콜백 내부에서 `spin_until_future_complete`를 사용하지 않고, 콜백 체인을 사용합니다.

**수정 브랜치**: 현재 브랜치 (`feat/SERVER/ros2-server__update_general_function_control__RP-50__update_pinky_lcd_display_control_func`)

**수정 파일**: `SERVER/ros2-server/src/pinky_lcd_display_controller/pinky_lcd_display_controller/lcd_controller_server.py`

**수정 내용**:

```python
def set_display_callback(self, request, response):
    """
    SetDisplay 서비스 콜백
    LCD에 표시할 내용을 설정합니다.
    
    우선 서비스 클라이언트를 통해 pinky_lcd_display의 서비스를 호출하고,
    서비스가 사용 불가능한 경우 토픽으로 폴백합니다.
    """
    try:
        # 서비스 클라이언트로 호출 시도
        if self.set_display_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().debug('Calling SetDisplay service on pinky_lcd_display')
            
            # 콜백 체인 사용
            future = self.set_display_client.call_async(request)
            future.add_done_callback(
                lambda f: self._set_display_service_response_callback(f, request, response)
            )
            
            # 즉시 반환 (비동기 처리)
            # 응답은 콜백에서 설정됨
            return response
        else:
            self.get_logger().warn("SetDisplay service not available, falling back to topic")
            self._fallback_to_topic_set_display(request, response)
            return response
    
    except Exception as e:
        self.get_logger().error(f"SetDisplay service call failed: {e}, falling back to topic")
        self._fallback_to_topic_set_display(request, response)
        return response

def _set_display_service_response_callback(self, future, original_request, response):
    """SetDisplay 서비스 응답 콜백"""
    try:
        if future.done():
            service_response = future.result()
            response.success = service_response.success
            response.message = service_response.message
            self.get_logger().info(f"SetDisplay service call successful: {response.message}")
        else:
            self.get_logger().warn("SetDisplay service call timeout, falling back to topic")
            self._fallback_to_topic_set_display(original_request, response)
    except Exception as e:
        self.get_logger().error(f"SetDisplay service response error: {e}, falling back to topic")
        self._fallback_to_topic_set_display(original_request, response)
```

**문제점**: 이 방법은 서비스 응답을 즉시 반환할 수 없습니다. 서비스 콜백은 동기적으로 응답을 반환해야 하는데, 비동기 콜백에서는 응답을 설정할 수 없습니다.

### 방안 2: 타임아웃 시간 증가 및 폴링 방식 (권장)

서비스 콜백 내부에서 짧은 시간 동안 폴링하여 응답을 기다립니다.

**수정 내용**:

```python
def set_display_callback(self, request, response):
    """
    SetDisplay 서비스 콜백
    LCD에 표시할 내용을 설정합니다.
    
    우선 서비스 클라이언트를 통해 pinky_lcd_display의 서비스를 호출하고,
    서비스가 사용 불가능한 경우 토픽으로 폴백합니다.
    """
    try:
        # 서비스 클라이언트로 호출 시도
        if self.set_display_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().debug('Calling SetDisplay service on pinky_lcd_display')
            future = self.set_display_client.call_async(request)
            
            # 짧은 시간 동안 폴링 (데드락 방지)
            timeout_sec = 3.0  # 타임아웃 증가
            start_time = time.time()
            while not future.done() and (time.time() - start_time) < timeout_sec:
                rclpy.spin_once(self, timeout_sec=0.1)  # 짧은 시간만 스핀
            
            if future.done():
                service_response = future.result()
                response.success = service_response.success
                response.message = service_response.message
                self.get_logger().info(f"SetDisplay service call successful: {response.message}")
            else:
                self.get_logger().warn("SetDisplay service call timeout, falling back to topic")
                self._fallback_to_topic_set_display(request, response)
        else:
            self.get_logger().warn("SetDisplay service not available, falling back to topic")
            self._fallback_to_topic_set_display(request, response)
    
    except Exception as e:
        self.get_logger().error(f"SetDisplay service call failed: {e}, falling back to topic")
        self._fallback_to_topic_set_display(request, response)
    
    return response
```

**필요한 import 추가**:
```python
import time
```

### 방안 3: 서비스 호출을 별도 스레드에서 처리 (복잡함)

서비스 호출을 별도 스레드에서 처리하고 결과를 기다립니다. 하지만 ROS2 노드는 단일 스레드에서 실행되어야 하므로 권장하지 않습니다.

---

## 권장 해결 방안

**방안 2 (타임아웃 증가 및 폴링)**를 권장합니다:

1. **장점**:
   - 서비스 콜백이 동기적으로 응답을 반환할 수 있음
   - 데드락 방지 (짧은 시간만 스핀)
   - 타임아웃 시간을 충분히 설정하여 LCD 렌더링 시간 고려

2. **단점**:
   - 서비스 콜백이 약간 지연될 수 있음 (하지만 허용 가능한 수준)

---

## 수정이 필요한 브랜치 및 파일

### 수정 브랜치
- **현재 브랜치**: `feat/SERVER/ros2-server__update_general_function_control__RP-50__update_pinky_lcd_display_control_func`

### 수정 파일
- `SERVER/ros2-server/src/pinky_lcd_display_controller/pinky_lcd_display_controller/lcd_controller_server.py`
  - `set_display_callback()` 메서드
  - `clear_display_callback()` 메서드 (동일한 문제)

### 수정이 필요하지 않은 브랜치
- `base/ROS2/rfred` 브랜치의 `pinky_lcd_display`는 정상 동작 중
- 문제는 클라이언트 측의 비동기 호출 방식에 있음

---

## 추가 개선 사항

### 1. 타임아웃 시간 조정

LCD 렌더링 시간을 고려하여 타임아웃을 3-5초로 증가:
```python
timeout_sec = 5.0  # LCD 렌더링 시간 고려
```

### 2. 로깅 개선

디버그 로그 추가:
```python
self.get_logger().debug(f"Waiting for service response, elapsed: {elapsed:.2f}s")
```

### 3. 에러 처리 강화

서비스 응답 에러 처리:
```python
try:
    service_response = future.result()
except Exception as e:
    self.get_logger().error(f"Service response error: {e}")
    self._fallback_to_topic_set_display(request, response)
```

---

## 테스트 방법

### 1. 서비스 호출 테스트

```bash
# 터미널 1: pinky_lcd_display 노드 실행 (로봇)
ros2 run pinky_lcd_display lcd_node

# 터미널 2: pinky_lcd_display_controller 노드 실행 (서버)
ros2 run pinky_lcd_display_controller lcd_controller_server

# 터미널 3: 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1', 'Line 2'], show_timestamp: true}"
```

### 2. 예상 결과

**수정 전**:
```
[WARN] SetDisplay service call timeout, falling back to topic
[INFO] Display updated via topic: Test\nLine 1...
```

**수정 후**:
```
[INFO] SetDisplay service call successful: Display updated successfully
```

---

## 참고 자료

- [ROS2 Service Client Documentation](https://docs.ros.org/en/humble/Tutorials/Beginner-Client-Libraries/Writing-A-Simple-Py-Service-And-Client.html)
- [rclpy.spin_once() Documentation](https://docs.ros2.org/humble/api/rclpy/api/node.html#rclpy.node.Node.spin_once)

---

**작성일**: 2025년 11월 8일  
**문제 발견일**: 2025년 11월 8일

