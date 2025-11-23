# Emotion 서비스 호출 오류 해결 가이드

## 문제 증상

```bash
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: 'hello'}"
# 오류: The passed service type is invalid
```

## 원인

ROS2 서비스 호출 시 서비스 타입 이름이 정확하지 않거나, 인터페이스가 제대로 로드되지 않았을 수 있습니다.

## 해결 방법

### 1단계: 서비스 타입 확인

```bash
# 서비스 타입 확인
ros2 service type /set_emotion

# 예상 출력:
# pinky_interfaces/srv/Emotion
```

### 2단계: 인터페이스 확인

```bash
# 인터페이스 구조 확인
ros2 interface show pinky_interfaces/srv/Emotion

# 예상 출력:
# string emotion
# ---
# string response
```

### 3단계: 올바른 형식으로 호출

#### 방법 1: 따옴표 이스케이프 사용

```bash
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: \"hello\"}"
```

#### 방법 2: 작은따옴표 사용

```bash
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'
```

#### 방법 3: YAML 파일 사용

`test_emotion.yaml` 파일 생성:
```yaml
emotion: "hello"
```

호출:
```bash
ros2 service call /set_emotion pinky_interfaces/srv/Emotion < test_emotion.yaml
```

### 4단계: 다른 감정 타입 테스트

```bash
# hello
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'

# happy
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "happy"}'

# sad
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "sad"}'

# angry
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "angry"}'

# fun
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "fun"}'

# bored
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "bored"}'

# interest
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "interest"}'

# basic
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "basic"}'
```

## 대안: emotion_controller 서비스 사용

`/emotion_controller/set_emotion` 서비스도 사용할 수 있습니다:

```bash
ros2 service call /emotion_controller/set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'
```

## 문제 해결 체크리스트

### 문제 1: "The passed service type is invalid"

**해결 방법**:
1. 서비스 타입 확인:
   ```bash
   ros2 service type /set_emotion
   ```

2. 인터페이스 확인:
   ```bash
   ros2 interface show pinky_interfaces/srv/Emotion
   ```

3. 따옴표 형식 변경:
   - 작은따옴표와 큰따옴표 조합 사용
   - 또는 이스케이프 문자 사용

### 문제 2: 인터페이스를 찾을 수 없음

**해결 방법**:
1. 패키지 확인:
   ```bash
   ros2 pkg list | grep pinky_interfaces
   ```

2. 워크스페이스 소스:
   ```bash
   # ros2-server 워크스페이스 소스
   source ~/ros-repo-1/SERVER/ros2-server/install/setup.bash
   
   # 또는 rfred 워크스페이스 소스
   source ~/ros-repo-1/ROS2/rfred/install/setup.bash
   ```

3. 빌드 확인:
   ```bash
   cd ~/ros-repo-1/SERVER/ros2-server
   colcon build --packages-select pinky_interfaces
   ```

## 테스트 스크립트

다음 스크립트를 사용하여 모든 감정 타입을 테스트할 수 있습니다:

```bash
#!/bin/bash
# test_all_emotions.sh

EMOTIONS=("hello" "basic" "angry" "bored" "fun" "happy" "interest" "sad")

for emotion in "${EMOTIONS[@]}"; do
    echo "Testing: $emotion"
    ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: \"$emotion\"}"
    sleep 2
done
```

## 참고

- ROS2 서비스 호출 시 따옴표 사용에 주의해야 합니다
- YAML 형식으로 호출하는 것이 더 안정적일 수 있습니다
- 서비스 타입 이름은 정확히 일치해야 합니다

