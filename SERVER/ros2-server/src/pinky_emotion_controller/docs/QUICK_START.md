# Pinky Emotion Controller 빠른 시작 가이드

## 사전 요구사항

1. ROS2 설치 (Jazzy 또는 Humble)
2. `pinky_interfaces` 패키지 (ROS2/pinky_pro 워크스페이스에 있음)
3. `pinky_emotion` 패키지 (ROS2/pinky_pro 워크스페이스에 있음)

## 실행 방법

### 1. 워크스페이스 소스

```bash
# ros2-server 워크스페이스 소스 (pinky_interfaces 포함)
cd SERVER/ros2-server
source install/setup.bash
```

### 2. emotion_controller_server 실행

```bash
ros2 run pinky_emotion_controller emotion_controller_server
```

서버가 시작되면 다음과 같은 메시지가 표시됩니다:

```
[INFO] [emotion_controller_server]: Emotion Controller Server started
[INFO] [emotion_controller_server]: Available services:
[INFO] [emotion_controller_server]:   - emotion_controller/set_emotion
[INFO] [emotion_controller_server]: Service client created for remote control
```

### 3. 서비스 호출 테스트

다른 터미널에서:

```bash
# 워크스페이스 소스
cd SERVER/ros2-server
source install/setup.bash
source ../../ROS2/pinky_pro/install/setup.bash

# 감정 표현 설정
ros2 service call /emotion_controller/set_emotion \
  pinky_interfaces/srv/Emotion \
  "{emotion: 'happy'}"
```

## 문제 해결

### ModuleNotFoundError: No module named 'pinky_interfaces'

**원인**: `pinky_interfaces` 패키지를 찾을 수 없음

**해결 방법**:
```bash
# ros2-server 워크스페이스를 다시 빌드하세요
cd SERVER/ros2-server
colcon build --packages-select pinky_interfaces
source install/setup.bash
```

### 서비스가 사용 불가능함

**원인**: `pinky_emotion` 노드가 실행되지 않음

**해결 방법**:
```bash
# pinky_emotion 노드를 실행해야 합니다
cd ROS2/pinky_pro
source install/setup.bash
ros2 run pinky_emotion emotion_server
```

## API 서버와 함께 사용

API 서버를 통해 감정 표현을 제어할 수도 있습니다:

```bash
# API 서버 실행 (다른 터미널)
cd SERVER/ros2-server/api-server
./run_standalone.sh

# API 호출
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy"}'
```

자세한 내용은 `api-server/docs/EMOTION_API_GUIDE.md`를 참조하세요.

