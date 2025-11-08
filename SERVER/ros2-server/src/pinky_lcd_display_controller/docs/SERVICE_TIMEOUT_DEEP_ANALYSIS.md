# 서비스 타임아웃 심층 분석 및 해결 방안

## 문제 현상

```
[WARN] SetDisplay service call timeout after 5.01s, falling back to topic
```

서비스 호출이 5초 타임아웃 후에도 응답을 받지 못하여 계속 토픽으로 폴백되고 있습니다.

## 문제 분석

### 1. 현재 구조

```
[pinky_lcd_display_controller]
    ├── 서비스 서버: 'lcd_controller/set_display' (line 143-146)
    └── 서비스 클라이언트: 'lcd_controller/set_display' (line 109-112)
            ↓ (네트워크를 통해 호출)
[pinky_lcd_display]
    └── 서비스 서버: 'lcd_controller/set_display'
```

### 2. 문제의 핵심

**서비스 콜백 내부에서 `spin_once`를 사용한 폴링 방식의 한계**

```python
def set_display_callback(self, request, response):
    # 서비스 클라이언트로 호출
    future = self.set_display_client.call_async(request)
    
    # 폴링 루프
    while not future.done() and (time.time() - start_time) < timeout_sec:
        rclpy.spin_once(self, timeout_sec=0.1)  # 문제!
```

#### 문제점

1. **`spin_once`의 제한**
   - `spin_once`는 **한 번의 콜백만 처리**합니다
   - 서비스 응답을 받기 위해서는 **여러 번의 콜백 처리**가 필요합니다
   - 네트워크를 통한 서비스 호출은 여러 메시지 교환이 필요하지만, `spin_once`는 이를 제대로 처리하지 못할 수 있습니다

2. **서비스 콜백 내부에서 다른 서비스 호출**
   - 서비스 콜백이 실행 중일 때는 노드의 메인 스핀 루프가 블로킹됨
   - 네트워크를 통한 서비스 응답을 받기 위해서는 **노드가 계속 스핀**되어야 함
   - 하지만 서비스 콜백 내부에서는 제한적으로만 스핀할 수 있음

3. **네트워크 지연**
   - 서버와 로봇 간 네트워크 지연
   - 서비스 응답이 도착하기 전에 타임아웃 발생

### 3. `future.done()`이 `False`로 남는 이유

#### 가능한 원인

1. **`spin_once`가 서비스 응답을 처리하지 못함**
   - 서비스 응답은 여러 단계의 메시지 교환을 필요로 함
   - `spin_once`는 한 번의 콜백만 처리하므로 응답을 완전히 처리하지 못할 수 있음

2. **네트워크 메시지가 도착하지 않음**
   - 네트워크 지연 또는 연결 문제
   - 서비스 서버가 응답을 보내지 않음

3. **서비스 서버가 실제로 응답하지 않음**
   - `pinky_lcd_display`의 서비스 콜백이 실행되지 않음
   - `INTERFACES_AVAILABLE`이 `False`일 수 있음

## 해결 방안

### 방안 1: 서비스 호출을 비동기로 처리 (권장)

서비스 콜백 내부에서 다른 서비스를 동기적으로 호출하는 대신, **비동기적으로 처리**하고 즉시 응답을 반환합니다.

**장점**:
- 서비스 콜백이 즉시 종료되어 다른 요청을 받을 수 있음
- 네트워크 지연에 영향받지 않음
- 데드락 방지

**단점**:
- 서비스 응답을 기다릴 수 없음
- 항상 성공으로 응답해야 함

**구현**:

```python
def set_display_callback(self, request, response):
    """
    SetDisplay 서비스 콜백
    비동기적으로 pinky_lcd_display의 서비스를 호출합니다.
    """
    try:
        # 서비스 클라이언트로 비동기 호출
        if self.set_display_client.wait_for_service(timeout_sec=0.5):
            self.get_logger().debug('Calling SetDisplay service on pinky_lcd_display (async)')
            future = self.set_display_client.call_async(request)
            
            # 콜백 등록 (응답 처리)
            future.add_done_callback(
                lambda f: self._set_display_service_response_handler(f, request)
            )
            
            # 즉시 성공 응답 반환
            response.success = True
            response.message = "Display update request sent (async)"
            return response
        else:
            # 서비스가 없으면 토픽으로 폴백
            self.get_logger().warn("SetDisplay service not available, falling back to topic")
            self._fallback_to_topic_set_display(request, response)
            return response
    
    except Exception as e:
        self.get_logger().error(f"SetDisplay service call failed: {e}, falling back to topic")
        self._fallback_to_topic_set_display(request, response)
        return response

def _set_display_service_response_handler(self, future, original_request):
    """서비스 응답 핸들러 (비동기)"""
    try:
        if future.done():
            service_response = future.result()
            if service_response.success:
                self.get_logger().info(f"SetDisplay service call successful: {service_response.message}")
            else:
                self.get_logger().warn(f"SetDisplay service call failed: {service_response.message}")
                # 실패 시 토픽으로 폴백
                self._fallback_to_topic_set_display_async(original_request)
    except Exception as e:
        self.get_logger().error(f"SetDisplay service response error: {e}")
        # 에러 시 토픽으로 폴백
        self._fallback_to_topic_set_display_async(original_request)
```

**문제점**: 서비스 콜백은 동기적으로 응답을 반환해야 하므로, 비동기 콜백에서 응답을 설정할 수 없습니다.

### 방안 2: 타임아웃 증가 및 더 긴 스핀 시간 (간단한 해결)

현재 폴링 방식을 유지하되, 타임아웃을 증가시키고 스핀 시간을 늘립니다.

**구현**:

```python
def set_display_callback(self, request, response):
    try:
        if self.set_display_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().debug('Calling SetDisplay service on pinky_lcd_display')
            future = self.set_display_client.call_async(request)
            
            # 타임아웃 증가 및 스핀 시간 증가
            timeout_sec = 10.0  # 5초 → 10초로 증가
            start_time = time.time()
            
            # 더 긴 시간 동안 스핀
            while not future.done() and (time.time() - start_time) < timeout_sec:
                rclpy.spin_once(self, timeout_sec=0.5)  # 0.1초 → 0.5초로 증가
            
            if future.done():
                service_response = future.result()
                response.success = service_response.success
                response.message = service_response.message
                self.get_logger().info(f"SetDisplay service call successful: {response.message}")
            else:
                elapsed = time.time() - start_time
                self.get_logger().warn(f"SetDisplay service call timeout after {elapsed:.2f}s, falling back to topic")
                self._fallback_to_topic_set_display(request, response)
        else:
            self.get_logger().warn("SetDisplay service not available, falling back to topic")
            self._fallback_to_topic_set_display(request, response)
    
    except Exception as e:
        self.get_logger().error(f"SetDisplay service call failed: {e}, falling back to topic")
        self._fallback_to_topic_set_display(request, response)
    
    return response
```

**문제점**: 여전히 서비스 콜백이 블로킹되며, 근본적인 문제를 해결하지 못합니다.

### 방안 3: 서비스 호출 제거, 토픽만 사용 (가장 간단)

서비스 콜백 내부에서 다른 서비스를 호출하지 않고, **항상 토픽으로 폴백**합니다.

**구현**:

```python
def set_display_callback(self, request, response):
    """
    SetDisplay 서비스 콜백
    토픽을 통해 LCD 내용을 업데이트합니다.
    """
    try:
        # 항상 토픽으로 전송 (서비스 호출 제거)
        self._fallback_to_topic_set_display(request, response)
        return response
    except Exception as e:
        response.success = False
        response.message = f"Error: {str(e)}"
        self.get_logger().error(f"Failed to set display: {e}")
        return response
```

**장점**:
- 간단하고 안정적
- 데드락 없음
- 네트워크 지연에 영향받지 않음

**단점**:
- 서비스의 장점(응답 확인)을 활용하지 못함
- 토픽만 사용하므로 서비스 클라이언트가 불필요

### 방안 4: Executor를 사용한 비동기 처리 (복잡하지만 가장 정확)

별도의 Executor를 사용하여 서비스 호출을 비동기로 처리합니다.

**구현**:

```python
from rclpy.executors import SingleThreadedExecutor
import threading

class LCDControllerServer(Node):
    def __init__(self):
        # ... 기존 코드 ...
        
        # 별도 Executor를 위한 스레드
        self.executor_thread = None
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self)
    
    def set_display_callback(self, request, response):
        try:
            if self.set_display_client.wait_for_service(timeout_sec=1.0):
                future = self.set_display_client.call_async(request)
                
                # 별도 스레드에서 Executor 실행
                def run_executor():
                    self.executor.spin_until_future_complete(future, timeout_sec=5.0)
                
                thread = threading.Thread(target=run_executor)
                thread.start()
                thread.join(timeout=5.0)
                
                if future.done():
                    service_response = future.result()
                    response.success = service_response.success
                    response.message = service_response.message
                else:
                    self._fallback_to_topic_set_display(request, response)
            else:
                self._fallback_to_topic_set_display(request, response)
        except Exception as e:
            self._fallback_to_topic_set_display(request, response)
        
        return response
```

**문제점**: ROS2 노드는 단일 스레드에서 실행되어야 하므로, 별도 스레드에서 Executor를 실행하는 것은 권장되지 않습니다.

## 권장 해결 방안

**방안 3 (토픽만 사용)**을 권장합니다.

### 이유

1. **현재 구조의 문제**
   - 서비스 콜백 내부에서 다른 서비스를 호출하는 것은 ROS2의 권장 패턴이 아님
   - 네트워크를 통한 서비스 호출은 지연이 발생할 수 있음
   - 서비스 콜백이 블로킹되어 다른 요청을 받을 수 없음

2. **토픽의 장점**
   - 비동기적 통신으로 블로킹 없음
   - 네트워크 지연에 영향받지 않음
   - 간단하고 안정적

3. **실제 사용 패턴**
   - 현재도 토픽으로 폴백되어 정상 동작 중
   - 서비스 응답을 기다릴 필요가 없음

### 구현

서비스 콜백에서 서비스 호출을 제거하고, 항상 토픽으로 전송하도록 수정합니다.

---

## 추가 확인 사항

### 1. `pinky_lcd_display`의 서비스 가용성 확인

다음 명령어로 서비스가 실제로 제공되는지 확인:

```bash
# 로봇에서 실행
ros2 service list | grep lcd_controller

# 서비스 타입 확인
ros2 service type /lcd_controller/set_display

# 서비스 호출 테스트
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1'], show_timestamp: true}"
```

### 2. 네트워크 연결 확인

```bash
# ROS2 도메인 ID 확인
echo $ROS_DOMAIN_ID

# 서버와 로봇이 같은 도메인에 있어야 함
```

### 3. `INTERFACES_AVAILABLE` 확인

`pinky_lcd_display` 노드의 로그에서 다음 메시지 확인:

```
[INFO] pinky_lcd_node started with service/action support
```

또는

```
[INFO] pinky_lcd_node started, listening on /lcd/status (service/action disabled)
```

---

## 결론

**문제의 근본 원인**: 서비스 콜백 내부에서 `spin_once`를 사용한 폴링 방식이 네트워크를 통한 서비스 응답을 제대로 처리하지 못함

**권장 해결책**: 서비스 콜백에서 서비스 호출을 제거하고, 항상 토픽으로 전송

**대안**: 타임아웃을 증가시키고 스핀 시간을 늘리지만, 근본적인 문제는 해결되지 않음

---

**작성일**: 2025년 11월 8일  
**문제 발견일**: 2025년 11월 8일

