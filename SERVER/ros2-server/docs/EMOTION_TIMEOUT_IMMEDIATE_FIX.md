# Emotion Controller 타임아웃 즉시 해결 방법

## 문제 증상

```
[INFO] [emotion_controller_server]: Request to set emotion to 'hello'
[ERROR] [emotion_controller_server]: Service call timeout
```

하지만 `pinky_emotion`은 요청을 받고 있습니다:
```
[INFO] [pinky_emotion]: Request to set emotion to 'hello'
```

## 원인 분석

### 핵심 문제

`pinky_emotion`의 `set_emotion_callback`은 **즉시 응답을 반환**합니다:
```python
def set_emotion_callback(self, request, response):
    # ... 감정 설정 ...
    response.response = f"Emotion set to {emo}"
    return response  # 즉시 반환
```

하지만 `emotion_controller_server`가 응답을 받지 못하고 있습니다.

### 가능한 원인

1. **ROS_DOMAIN_ID 불일치** (가장 가능성 높음)
   - 서버와 로봇이 다른 도메인에 있음
   - 서비스 호출은 되지만 응답이 다른 도메인으로 전달됨

2. **네트워크 지연**
   - 원격 호출 시 네트워크 지연
   - 타임아웃 시간 부족

3. **서비스 클라이언트 문제**
   - `rclpy.spin_until_future_complete`가 제대로 동작하지 않음

## 즉시 해결 방법

### 방법 1: ROS_DOMAIN_ID 확인 및 통일 (가장 중요)

**서버 측**:
```bash
echo $ROS_DOMAIN_ID
# 13이어야 함

# 설정
export ROS_DOMAIN_ID=13
```

**로봇 측**:
```bash
echo $ROS_DOMAIN_ID
# 13이어야 함

# 설정
export ROS_DOMAIN_ID=13
```

**확인**:
```bash
# 서버 측에서
ros2 service list | grep set_emotion
# /set_emotion이 보여야 함

# 로봇 측에서
ros2 service list | grep set_emotion
# /set_emotion이 보여야 함
```

### 방법 2: 직접 서비스 호출 테스트

**서버 측에서 직접 호출**:
```bash
cd ~/ros-repo-1/SERVER/ros2-server
source install/setup.bash
export ROS_DOMAIN_ID=13

ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'
```

**응답이 즉시 오는지 확인**:
- 즉시 오면: `emotion_controller_server`의 문제
- 타임아웃이면: ROS_DOMAIN_ID 또는 네트워크 문제

### 방법 3: emotion_controller_server 재시작

```bash
# 기존 프로세스 종료
pkill -f emotion_controller_server

# 재시작
cd ~/ros-repo-1/SERVER/ros2-server
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 run pinky_emotion_controller emotion_controller_server
```

### 방법 4: 타임아웃 시간 증가 (이미 적용됨)

코드에서 타임아웃을 3초에서 5초로 증가했습니다.

## 디버깅 단계

### 1단계: 환경 확인

```bash
# 모든 터미널에서
export ROS_DOMAIN_ID=13
echo $ROS_DOMAIN_ID
```

### 2단계: 서비스 확인

```bash
# 서버 측
ros2 service list | grep emotion

# 로봇 측
ros2 service list | grep emotion

# 둘 다 /set_emotion이 보여야 함
```

### 3단계: 직접 호출 테스트

```bash
# 서버 측에서
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'

# 즉시 응답이 오는지 확인
```

### 4단계: emotion_controller_server 로그 확인

```bash
# emotion_controller_server 실행 시 로그 확인
# "Service call timeout" 메시지가 나오는 시점 확인
```

## 예상 결과

### 정상 동작 시

```
[INFO] [emotion_controller_server]: Request to set emotion to 'hello'
[INFO] [emotion_controller_server]: Emotion set successfully: Emotion set to hello
```

### 여전히 타임아웃 발생 시

1. ROS_DOMAIN_ID 재확인
2. 네트워크 연결 확인
3. 서비스 직접 호출 테스트
4. 로그 상세 확인

## 참고

- `pinky_emotion`은 즉시 응답을 반환하므로 타임아웃이 발생하지 않아야 함
- 타임아웃이 발생한다면 ROS_DOMAIN_ID 불일치 또는 네트워크 문제일 가능성이 높음
- 코드 수정으로는 해결되지 않을 수 있음 (환경 설정 문제)

