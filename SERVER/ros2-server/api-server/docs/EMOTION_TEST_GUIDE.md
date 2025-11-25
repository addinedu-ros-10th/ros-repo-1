# 감정 표현 및 LCD 제어 테스트 가이드

## 개요

이 문서는 Pinky 로봇의 감정 표현 기능과 LCD 제어 기능을 테스트하는 방법을 설명합니다.

## 지원하는 감정 타입

다음 8가지 감정 타입을 지원합니다:

1. **hello** - 인사
2. **basic** - 기본 상태
3. **angry** - 화남
4. **bored** - 지루함
5. **fun** - 재미있음
6. **happy** - 행복함
7. **interest** - 관심
8. **sad** - 슬픔

## 호출 방식

### 1. 서비스 (Service) - 권장

감정 표현은 **서비스**를 통해 호출됩니다. 토픽이나 액션은 사용하지 않습니다.

#### 통신 구조

```
[API Server / emotion_controller_server]
    |
    | ROS2 Service Call
    v
[pinky_emotion 노드]
    |
    | LCD 제어
    v
[LCD Display (GIF 표시)]
```

#### 서비스 정보

- **서비스 이름**: 
  - `/emotion_controller/set_emotion` (emotion_controller_server 제공)
  - `/set_emotion` (pinky_emotion 노드 직접 호출)

- **서비스 타입**: `pinky_interfaces/srv/Emotion`

### 2. 인터페이스 내용

#### Emotion.srv

```python
# 요청 (Request)
string emotion  # 감정 타입: "hello", "basic", "angry", "bored", "fun", "happy", "interest", "sad"

---

# 응답 (Response)
string response  # 응답 메시지
```

#### 요청 예시

```python
emotion: "happy"
```

#### 응답 예시

```python
response: "Emotion set to happy"
```

## 테스트 방법

### 방법 1: API 서버를 통한 테스트 (권장)

#### 1.1 서버 실행

**터미널 1**: emotion_controller_server 실행
```bash
cd SERVER/ros2-server
source install/setup.bash
ros2 run pinky_emotion_controller emotion_controller_server
```

**터미널 2**: API 서버 실행
```bash
cd SERVER/ros2-server/api-server
./run_standalone.sh
```

#### 1.2 전체 감정 테스트

```bash
cd SERVER/ros2-server/api-server
./test_all_emotions.sh
```

#### 1.3 개별 감정 테스트

```bash
# 행복한 감정
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy"}'

# 인사 감정
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "hello"}'
```

### 방법 2: ROS2 서비스를 직접 호출

#### 2.1 서버 실행

```bash
cd SERVER/ros2-server
source install/setup.bash

# emotion_controller_server 실행
ros2 run pinky_emotion_controller emotion_controller_server
```

**또는** pinky_emotion 노드 직접 실행:
```bash
cd ROS2/pinky_pro
source install/setup.bash
ros2 run pinky_emotion emotion_server
```

#### 2.2 전체 감정 테스트

```bash
cd SERVER/ros2-server
source install/setup.bash
./test_emotions_ros2.sh
```

#### 2.3 개별 감정 테스트

```bash
# emotion_controller_server를 통한 호출
ros2 service call /emotion_controller/set_emotion \
  pinky_interfaces/srv/Emotion \
  "{emotion: 'happy'}"

# pinky_emotion 노드 직접 호출
ros2 service call /set_emotion \
  pinky_interfaces/srv/Emotion \
  "{emotion: 'hello'}"
```

## 상세 테스트 가이드

### 1. Health Check

서비스가 사용 가능한지 확인:

```bash
# API 서버
curl http://localhost:8004/health | jq '.services.emotion'

# ROS2 서비스
ros2 service list | grep emotion
ros2 service type /emotion_controller/set_emotion
```

### 2. 각 감정 타입 테스트

#### hello (인사)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "hello"}'
```

#### basic (기본 상태)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "basic"}'
```

#### angry (화남)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "angry"}'
```

#### bored (지루함)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "bored"}'
```

#### fun (재미있음)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "fun"}'
```

#### happy (행복함)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy"}'
```

#### interest (관심)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "interest"}'
```

#### sad (슬픔)
```bash
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "sad"}'
```

## Python으로 테스트

### API 서버 사용

```python
import requests

url = "http://localhost:8004/api/emotion/set"
emotions = ["hello", "basic", "angry", "bored", "fun", "happy", "interest", "sad"]

for emotion in emotions:
    response = requests.post(url, json={"emotion": emotion})
    print(f"{emotion}: {response.json()}")
```

### ROS2 서비스 직접 사용

```python
import rclpy
from rclpy.node import Node
from pinky_interfaces.srv import Emotion

rclpy.init()
node = Node('emotion_test_client')
client = node.create_client(Emotion, '/emotion_controller/set_emotion')

emotions = ["hello", "basic", "angry", "bored", "fun", "happy", "interest", "sad"]

for emotion in emotions:
    request = Emotion.Request()
    request.emotion = emotion
    
    if client.wait_for_service(timeout_sec=1.0):
        future = client.call_async(request)
        rclpy.spin_until_future_complete(node, future)
        response = future.result()
        print(f"{emotion}: {response.response}")
    else:
        print(f"Service not available for {emotion}")

node.destroy_node()
rclpy.shutdown()
```

## 문제 해결

### 서비스가 사용 불가능함

**증상**: `Service not available` 오류

**해결 방법**:
1. emotion_controller_server가 실행 중인지 확인
2. ROS2 도메인 ID가 일치하는지 확인
3. 서비스 목록 확인: `ros2 service list | grep emotion`

### 잘못된 감정 타입

**증상**: `Unsupported emotion` 오류

**해결 방법**:
- 지원하는 감정 타입만 사용: hello, basic, angry, bored, fun, happy, interest, sad

### LCD에 표시되지 않음

**증상**: 서비스 호출은 성공하지만 LCD에 표시되지 않음

**해결 방법**:
1. pinky_emotion 노드가 실행 중인지 확인
2. LCD 하드웨어 연결 확인
3. GIF 파일이 존재하는지 확인: `ROS2/pinky_pro/src/pinky_pro/pinky_emotion/emotion/`

## LCD 화면 지우기

### API 엔드포인트

**POST /api/lcd/clear**

LCD 화면을 검은 화면으로 초기화합니다.

**요청**: 없음 (요청 본문 없음)

**응답**:
```json
{
  "success": true,
  "message": "LCD display cleared successfully"
}
```

### 사용 예시

#### cURL
```bash
curl -X POST http://localhost:8004/api/lcd/clear
```

#### Python
```python
import requests

url = "http://localhost:8004/api/lcd/clear"
response = requests.post(url)
print(response.json())
```

#### JavaScript
```javascript
fetch('http://localhost:8004/api/lcd/clear', {
  method: 'POST'
})
.then(response => response.json())
.then(data => console.log(data));
```

### ROS2 서비스 직접 호출

```bash
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

## 참고

- 감정 표현은 GIF 파일을 LCD에 표시하는 방식으로 동작합니다
- 각 감정 타입에 해당하는 GIF 파일이 `pinky_emotion` 패키지에 포함되어 있습니다
- GIF 파일 경로: `ROS2/pinky_pro/src/pinky_pro/pinky_emotion/emotion/*.gif`
- LCD 화면 지우기는 모든 표시 내용을 제거하고 검은 화면으로 초기화합니다

