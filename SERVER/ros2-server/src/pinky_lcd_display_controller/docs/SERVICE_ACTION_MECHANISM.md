# 서비스/액션 동작 메커니즘 상세 설명

## 서비스 (Service) 동작 메커니즘

### 1. 서비스가 언제 종료되는가?

#### ROS2 서비스의 생명주기

**서비스는 즉시 종료됩니다.** 서비스는 **요청-응답 패턴**을 따르는 **동기적 통신** 방식입니다.

```
[클라이언트]                    [서버]
    |                            |
    |---(1) 서비스 요청 전송)---->|
    |                            |---(2) 콜백 실행
    |                            |---(3) 응답 생성
    |<--(4) 응답 수신)------------|
    |                            |
    |---(5) 종료)----------------|
```

#### 서비스 종료 시점

1. **서비스 콜백이 `return response`를 실행하는 순간**
   - 서비스 콜백 함수가 응답 객체를 반환하면 즉시 종료
   - 예: `set_display_callback()`의 `return response` (line 207)

2. **클라이언트가 응답을 수신하는 순간**
   - `ros2 service call` 명령어는 응답을 받으면 즉시 종료
   - 서비스 연결이 해제됨

#### 현재 코드의 동작 흐름

```python
def set_display_callback(self, request, response):
    # 1. 서비스 클라이언트로 호출 시도
    if self.set_display_client.wait_for_service(timeout_sec=1.0):
        future = self.set_display_client.call_async(request)
        
        # 2. 폴링 루프 (최대 5초)
        while not future.done() and (time.time() - start_time) < timeout_sec:
            rclpy.spin_once(self, timeout_sec=0.1)
        
        # 3. 응답 처리
        if future.done():
            service_response = future.result()
            response.success = service_response.success
            response.message = service_response.message
        else:
            # 타임아웃 시 폴백
            self._fallback_to_topic_set_display(request, response)
    
    # 4. 서비스 종료 (즉시 반환)
    return response  # <-- 여기서 서비스 종료
```

### 2. "waiting for service to become available..." 메시지가 반복되는 이유

#### 문제 분석

로그를 보면:
```
waiting for service to become available...
requester: making request: ...
response: success=True, message='Display updated via topic (fallback): 4 lines'
```

이 메시지는 `ros2 service call` 명령어가 서비스를 찾는 과정에서 나타납니다.

#### 원인

1. **서비스 서버가 일시적으로 사용 불가능한 상태**
   - 서비스 콜백이 실행 중일 때는 새로운 요청을 받을 수 없음
   - ROS2 서비스는 **단일 요청만 동시에 처리** 가능

2. **서비스 콜백 내부에서 다른 서비스를 호출하는 구조**
   ```python
   def set_display_callback(self, request, response):
       # 이 콜백이 실행 중일 때는 다른 요청을 받을 수 없음
       if self.set_display_client.wait_for_service(timeout_sec=1.0):
           # 내부에서 또 다른 서비스를 호출
           future = self.set_display_client.call_async(request)
           # 폴링 루프 (최대 5초 대기)
           while not future.done() and ...:
               rclpy.spin_once(self, timeout_sec=0.1)
   ```

3. **서비스 가용성 확인 지연**
   - `wait_for_service(timeout_sec=1.0)`가 1초 동안 대기
   - 이 시간 동안 서비스가 사용 불가능한 것으로 표시될 수 있음

#### 해결 방법

**현재 구조는 정상 동작합니다.** "waiting for service to become available..." 메시지는:
- 서비스가 사용 가능해질 때까지 대기하는 정상적인 동작
- 서비스 콜백이 실행 중일 때 나타날 수 있음
- 응답을 받으면 즉시 종료되므로 문제 없음

### 3. 서비스 동작 흐름 상세

#### 단계별 동작

**1단계: 서비스 요청 수신**
```
[ros2 service call] 
    ↓
[pinky_lcd_display_controller 서비스 서버]
    ↓
[set_display_callback() 호출]
```

**2단계: 내부 서비스 호출**
```
[set_display_callback 내부]
    ↓
[pinky_lcd_display 서비스 클라이언트]
    ↓
[wait_for_service() - 서비스 가용성 확인]
    ↓
[call_async() - 비동기 호출]
    ↓
[폴링 루프 - 응답 대기 (최대 5초)]
```

**3단계: 응답 처리**
```
[응답 수신 또는 타임아웃]
    ↓
[response 객체 설정]
    ↓
[return response - 서비스 종료]
```

**4단계: 클라이언트 종료**
```
[ros2 service call이 응답 수신]
    ↓
[명령어 종료]
```

#### 타임라인 예시

```
시간    동작
----    ----
0.0s    ros2 service call 실행
0.1s    서비스 요청 전송
0.2s    set_display_callback() 시작
0.3s    wait_for_service() 호출
0.4s    call_async() 호출
0.5s    폴링 루프 시작
...     폴링 (0.1초 간격)
2.0s    응답 수신 또는 타임아웃
2.1s    return response (서비스 종료)
2.2s    ros2 service call 종료
```

### 4. 서비스의 특징

#### 동기적 통신
- **요청-응답 패턴**: 하나의 요청에 대해 하나의 응답
- **즉시 종료**: 응답을 받으면 즉시 종료
- **단일 요청 처리**: 동시에 하나의 요청만 처리 가능

#### 서비스 콜백의 제약
- **동기적 실행**: 콜백이 완료되어야 응답 반환
- **블로킹**: 콜백이 실행 중이면 다른 요청 대기
- **타임아웃**: 클라이언트는 응답을 기다리는 시간 제한

---

## 액션 (Action) 동작 메커니즘

### 1. 액션이 언제 종료되는가?

#### ROS2 액션의 생명주기

**액션은 비동기적으로 실행되며, Goal이 완료되면 종료됩니다.** 액션은 **Goal-Feedback-Result 패턴**을 따르는 **비동기적 통신** 방식입니다.

```
[클라이언트]                    [서버]
    |                            |
    |---(1) Goal 전송)----------->|
    |                            |---(2) Goal 수락/거부
    |<--(3) Goal 수락)-----------|
    |                            |
    |<--(4) Feedback (반복)------|
    |                            |---(5) 실행 중...
    |                            |
    |<--(6) Result)--------------|
    |                            |---(7) 액션 종료
    |                            |
```

#### 액션 종료 시점

1. **Goal이 완료되는 순간**
   - 액션 서버가 `goal_handle.succeed()` 또는 `goal_handle.abort()` 호출
   - Result가 클라이언트에 전송됨

2. **Goal이 취소되는 순간**
   - 클라이언트가 `goal_handle.cancel()` 호출
   - 액션 서버가 `goal_handle.canceled()` 호출

3. **Goal이 거부되는 순간**
   - 액션 서버가 Goal을 수락하지 않으면 즉시 종료

#### 현재 코드의 동작 흐름

```python
def call_set_display_action(self, title, lines, ...):
    # 1. 액션 서버 대기
    if not self.set_display_action_client.wait_for_server(timeout_sec=1.0):
        return None
    
    # 2. Goal 전송
    goal_msg = SetDisplayAction.Goal()
    # ... Goal 설정 ...
    future = self.set_display_action_client.send_goal_async(goal_msg)
    
    # 3. Goal 수락 대기
    rclpy.spin_until_future_complete(self, future, timeout_sec=2.0)
    
    if future.done():
        goal_handle = future.result()
        if goal_handle.accepted:
            # 4. Goal 수락됨 (액션은 백그라운드에서 실행)
            return goal_handle  # <-- 여기서 함수는 종료되지만 액션은 계속 실행
        else:
            return None  # Goal 거부
```

**중요**: `call_set_display_action()` 함수는 Goal을 전송하고 수락되면 즉시 반환합니다. 하지만 **액션 자체는 백그라운드에서 계속 실행**됩니다.

### 2. 액션의 비동기 실행

#### 액션 서버에서의 실행

```python
# pinky_lcd_display의 lcd_node.py
def set_display_action_execute_callback(self, goal_handle):
    goal = goal_handle.goal
    
    # 1. 애니메이션 효과 적용
    if goal.animation_type == 1:  # FADE_IN
        self.lcd_manager.show_status_with_animation(...)
    
    # 2. duration_ms가 0이 아니면 지정된 시간 후 자동 종료
    if goal.duration_ms > 0:
        # 피드백 발행 루프
        while elapsed_ms < goal.duration_ms:
            # 피드백 발행
            goal_handle.publish_feedback(feedback_msg)
            time.sleep(0.1)
        
        # 자동으로 화면 지우기
        self.lcd_manager.show_status(title="", lines=[], ...)
    
    # 3. Result 반환 (액션 종료)
    result = SetDisplayAction.Result()
    result.success = True
    result.message = "Display completed successfully"
    return result  # <-- 여기서 액션 종료
```

### 3. 액션 동작 흐름 상세

#### 단계별 동작

**1단계: Goal 전송**
```
[call_set_display_action() 호출]
    ↓
[액션 서버 대기]
    ↓
[Goal 메시지 생성]
    ↓
[send_goal_async() - Goal 전송]
```

**2단계: Goal 수락/거부**
```
[액션 서버가 Goal 수신]
    ↓
[Goal 수락 또는 거부]
    ↓
[goal_handle 반환]
```

**3단계: 액션 실행 (백그라운드)**
```
[액션 서버의 execute 콜백 실행]
    ↓
[애니메이션 효과 적용]
    ↓
[피드백 발행 (반복)]
    ↓
[지속 시간 처리]
    ↓
[Result 생성 및 반환]
```

**4단계: Result 수신 (선택적)**
```
[클라이언트가 Result 대기]
    ↓
[Result 수신]
    ↓
[액션 완전 종료]
```

#### 타임라인 예시 (SetDisplayAction, duration_ms=5000)

```
시간    동작
----    ----
0.0s    call_set_display_action() 호출
0.1s    Goal 전송
0.2s    Goal 수락
0.3s    함수 반환 (goal_handle 반환)
        ↓ (백그라운드 실행)
0.4s    액션 서버 execute 콜백 시작
0.5s    애니메이션 효과 적용
0.6s    피드백 발행 (elapsed_ms: 100)
1.0s    피드백 발행 (elapsed_ms: 500)
...     피드백 발행 (0.1초 간격)
5.0s    피드백 발행 (elapsed_ms: 5000)
5.1s    화면 자동 지우기
5.2s    Result 반환 (액션 종료)
```

### 4. 액션의 특징

#### 비동기적 통신
- **Goal-Feedback-Result 패턴**: Goal 전송 후 백그라운드에서 실행
- **장시간 실행 가능**: 몇 초에서 몇 분까지 실행 가능
- **피드백 제공**: 실행 중 진행 상황을 피드백으로 전달

#### 액션의 장점
- **취소 가능**: 실행 중 Goal을 취소할 수 있음
- **진행 상황 확인**: 피드백을 통해 진행률 확인 가능
- **비동기 실행**: Goal 전송 후 즉시 다른 작업 가능

#### 액션 vs 서비스

| 특징 | 서비스 | 액션 |
|------|--------|------|
| 통신 방식 | 동기적 | 비동기적 |
| 실행 시간 | 짧음 (보통 < 1초) | 길 수 있음 (초~분) |
| 피드백 | 없음 | 있음 |
| 취소 가능 | 없음 | 있음 |
| 종료 시점 | 응답 반환 시 | Goal 완료 시 |

---

## 실제 사용 예시

### 서비스 사용 예시

```bash
# 서비스 호출 (동기적)
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1'], show_timestamp: true}"

# 동작:
# 1. 서비스 요청 전송
# 2. 서비스 콜백 실행 (최대 5초)
# 3. 응답 수신
# 4. 명령어 종료 (즉시)
```

### 액션 사용 예시

```bash
# 액션 호출 (비동기적)
ros2 action send_goal --feedback /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Processing', lines: ['Task: Data processing'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"

# 동작:
# 1. Goal 전송
# 2. Goal 수락
# 3. 피드백 수신 (반복)
# 4. Result 수신 (5초 후)
# 5. 명령어 종료
```

---

## 요약

### 서비스
- **종료 시점**: 서비스 콜백이 `return response`를 실행하는 순간
- **특징**: 동기적, 즉시 종료, 단일 요청 처리
- **"waiting for service..." 메시지**: 서비스 콜백이 실행 중일 때 나타날 수 있음 (정상)

### 액션
- **종료 시점**: Goal이 완료되어 Result가 반환되는 순간
- **특징**: 비동기적, 백그라운드 실행, 피드백 제공
- **실행 시간**: Goal에 지정된 duration_ms에 따라 결정

---

**작성일**: 2025년 11월 8일  
**기준**: 실제 코드 분석 결과

