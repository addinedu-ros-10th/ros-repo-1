# Emotion Controller 타임아웃 문제 해결

## 문제 증상

`emotion_controller_server`가 `pinky_emotion`의 `/set_emotion` 서비스를 호출할 때 타임아웃이 발생합니다.

**로그**:
```
[INFO] [emotion_controller_server]: Request to set emotion to 'hello'
[ERROR] [emotion_controller_server]: Service call timeout
```

하지만 `pinky_emotion` 노드는 요청을 받고 있습니다:
```
[INFO] [pinky_emotion]: Request to set emotion to 'hello'
```

## 원인 분석

### 문제 1: `rclpy.spin_until_future_complete` 동작 문제

`rclpy.spin_until_future_complete`가 제대로 동작하지 않을 수 있습니다. 특히:
- Executor가 제대로 설정되지 않음
- 노드가 spin 중이 아닐 때 응답을 받지 못함

### 문제 2: ROS_DOMAIN_ID 불일치

서버와 로봇이 다른 ROS_DOMAIN_ID를 사용하고 있을 수 있습니다.

## 해결 방법

### 수정 내용

`emotion_controller_server.py`의 서비스 호출 방식을 개선했습니다:

**변경 전**:
```python
future = self.emotion_service_client.call_async(emotion_request)
rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
```

**변경 후**:
```python
future = self.emotion_service_client.call_async(emotion_request)

# Executor를 사용하여 응답 대기
executor = rclpy.executors.SingleThreadedExecutor()
executor.add_node(self)

# 응답 대기 (최대 5초)
timeout_sec = 5.0
start_time = self.get_clock().now()

while not future.done():
    executor.spin_once(timeout_sec=0.1)
    elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
    if elapsed > timeout_sec:
        break
```

### 추가 확인 사항

1. **ROS_DOMAIN_ID 확인**
   ```bash
   # 서버 측
   echo $ROS_DOMAIN_ID
   
   # 로봇 측
   echo $ROS_DOMAIN_ID
   
   # 둘 다 13이어야 함
   ```

2. **서비스 확인**
   ```bash
   # 서버 측에서
   ros2 service list | grep set_emotion
   
   # 로봇 측에서
   ros2 service list | grep set_emotion
   
   # 둘 다 /set_emotion이 보여야 함
   ```

3. **직접 서비스 호출 테스트**
   ```bash
   # 서버 측에서 직접 호출
   ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'
   ```

## 재빌드 및 테스트

### 1단계: 재빌드

```bash
cd ~/ros-repo-1/SERVER/ros2-server
colcon build --packages-select pinky_emotion_controller
source install/setup.bash
```

### 2단계: 테스트

```bash
# emotion_controller_server 실행
ros2 run pinky_emotion_controller emotion_controller_server

# 다른 터미널에서 서비스 호출
ros2 service call /emotion_controller/set_emotion \
  pinky_interfaces/srv/Emotion \
  '{emotion: "hello"}'
```

## 예상 결과

### 수정 전
```
[INFO] [emotion_controller_server]: Request to set emotion to 'hello'
[ERROR] [emotion_controller_server]: Service call timeout
```

### 수정 후
```
[INFO] [emotion_controller_server]: Request to set emotion to 'hello'
[INFO] [emotion_controller_server]: Emotion set successfully: Emotion set to hello
```

## 참고

- 타임아웃 시간을 3초에서 5초로 증가
- Executor를 명시적으로 사용하여 응답 대기
- 더 나은 에러 처리 및 로깅

