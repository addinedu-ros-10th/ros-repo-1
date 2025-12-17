# Emotion Controller 사용 방안 분석 및 문제 해결

## 문제 진단

### 증상

```bash
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'
# 오류: The passed service type is invalid
```

### 원인 분석

1. **`pinky_interfaces` 패키지가 로드되지 않음**
   - `ros2 interface list` 출력에 `pinky_interfaces`가 없음
   - 이는 `pinky_interfaces` 패키지가 현재 ROS2 환경에 소스되지 않았음을 의미

2. **서비스 타입 인식 실패**
   - ROS2가 `pinky_interfaces/srv/Emotion` 타입을 인식하지 못함
   - 서비스는 존재하지만 타입 정보가 없어 호출 실패

3. **워크스페이스 소스 누락**
   - `pinky_interfaces`가 포함된 워크스페이스가 소스되지 않음
   - `ros2-server` 또는 `pinky_pro` 워크스페이스 소스 필요

## 해결 방법

### 1단계: pinky_interfaces 패키지 위치 확인

```bash
# ros2-server 워크스페이스 확인
ls -la ~/ros-repo-1/SERVER/ros2-server/src/pinky_interfaces/

# pinky_pro 워크스페이스 확인
ls -la ~/ros-repo-1/ROS2/pinky_pro/src/pinky_pro/pinky_interfaces/
```

### 2단계: 워크스페이스 빌드 및 소스

#### 방법 1: ros2-server 워크스페이스 사용 (권장)

```bash
cd ~/ros-repo-1/SERVER/ros2-server

# 빌드
colcon build --packages-select pinky_interfaces

# 소스
source install/setup.bash

# 확인
ros2 interface list | grep pinky_interfaces
ros2 interface show pinky_interfaces/srv/Emotion
```

#### 방법 2: pinky_pro 워크스페이스 사용

```bash
cd ~/ros-repo-1/ROS2/pinky_pro

# 빌드
colcon build --packages-select pinky_interfaces

# 소스
source install/setup.bash

# 확인
ros2 interface list | grep pinky_interfaces
ros2 interface show pinky_interfaces/srv/Emotion
```

### 3단계: 서비스 타입 확인

```bash
# 서비스 타입 확인
ros2 service type /set_emotion

# 예상 출력:
# pinky_interfaces/srv/Emotion

# 인터페이스 구조 확인
ros2 interface show pinky_interfaces/srv/Emotion

# 예상 출력:
# string emotion
# ---
# string response
```

### 4단계: 서비스 호출

#### 올바른 호출 형식

```bash
# 방법 1: 작은따옴표 사용 (권장)
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'

# 방법 2: 이스케이프 사용
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: \"hello\"}"
```

#### 모든 감정 타입 테스트

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

## Emotion Controller 사용 방안

### 현재 구조

```
[API Server] 
    |
    | HTTP POST /api/emotion/set
    v
[EmotionClient (ros2_client.py)]
    |
    | ROS2 Service Call
    v
[emotion_controller/set_emotion]
    |
    | ROS2 Service Call
    v
[emotion_controller_server]
    |
    | ROS2 Service Call
    v
[/set_emotion]
    |
    | ROS2 Service Call
    v
[pinky_emotion 노드]
    |
    | DisplayImage Service Call
    v
[lcd_controller/display_image]
    |
    | LCD 제어
    v
[LCD Display]
```

### 사용 방안 1: emotion_controller_server 사용 (현재 구조)

**장점**:
- 중간 서비스 레이어 제공
- API 서버와 emotion 노드 간 분리
- 감정 타입 검증 제공

**단점**:
- 추가 노드 필요
- 서비스 호출 체인이 길어짐

**사용 방법**:
```bash
# 1. emotion_controller_server 실행
ros2 run pinky_emotion_controller emotion_controller_server

# 2. API 서버에서 호출
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "hello"}'
```

### 사용 방안 2: 직접 /set_emotion 호출

**장점**:
- 서비스 호출 체인 단순화
- 중간 레이어 제거

**단점**:
- API 서버 코드 수정 필요
- 감정 타입 검증을 API 서버에서 수행해야 함

**사용 방법**:
```bash
# API 서버의 EmotionClient 수정 필요
# service_name을 "set_emotion"으로 변경
```

### 사용 방안 3: emotion_controller_server 제거 (권장)

**현재 상황**:
- `emotion_controller_server`는 `/set_emotion` 서비스를 호출하는 중간 레이어
- `pinky_emotion` 노드가 이미 `/set_emotion` 서비스를 제공
- 중복 레이어로 인한 복잡성 증가

**권장 구조**:
```
[API Server] 
    |
    | HTTP POST /api/emotion/set
    v
[EmotionClient (ros2_client.py)]
    |
    | ROS2 Service Call (직접 호출)
    v
[/set_emotion]
    |
    | ROS2 Service Call
    v
[pinky_emotion 노드]
    |
    | DisplayImage Service Call
    v
[lcd_controller/display_image]
    |
    | LCD 제어
    v
[LCD Display]
```

**수정 사항**:
1. API 서버의 `EmotionClient`가 `/set_emotion`을 직접 호출하도록 수정
2. `emotion_controller_server` 제거 또는 선택적 사용

## 문제 해결 체크리스트

### 문제 1: "The passed service type is invalid"

**해결 방법**:
1. `pinky_interfaces` 패키지 빌드 및 소스:
   ```bash
   cd ~/ros-repo-1/SERVER/ros2-server
   colcon build --packages-select pinky_interfaces
   source install/setup.bash
   ```

2. 인터페이스 확인:
   ```bash
   ros2 interface list | grep pinky_interfaces
   ros2 interface show pinky_interfaces/srv/Emotion
   ```

3. 서비스 타입 확인:
   ```bash
   ros2 service type /set_emotion
   ```

### 문제 2: emotion_controller_server가 서비스를 찾지 못함

**해결 방법**:
1. `pinky_emotion` 노드가 실행 중인지 확인:
   ```bash
   ros2 node list | grep pinky_emotion
   ```

2. 서비스 목록 확인:
   ```bash
   ros2 service list | grep emotion
   ```

3. ROS_DOMAIN_ID 확인:
   ```bash
   echo $ROS_DOMAIN_ID
   # 모든 터미널에서 동일한 값 (13)이어야 함
   ```

### 문제 3: API 서버에서 타임아웃 발생

**해결 방법**:
1. `emotion_controller_server`가 실행 중인지 확인
2. `/set_emotion` 서비스가 사용 가능한지 확인
3. 직접 `/set_emotion` 호출로 변경 고려

## 권장 사용 방안

### 최종 권장 구조

1. **API 서버에서 직접 `/set_emotion` 호출**
   - `emotion_controller_server` 제거
   - 서비스 호출 체인 단순화
   - 성능 향상

2. **pinky_interfaces 패키지 관리**
   - `ros2-server` 워크스페이스에 포함
   - 모든 노드에서 동일한 인터페이스 사용

3. **환경 설정**
   - 모든 터미널에서 `ROS_DOMAIN_ID=13` 설정
   - `ros2-server` 워크스페이스 소스

## 테스트 스크립트

```bash
#!/bin/bash
# test_emotion_complete.sh

echo "=========================================="
echo "Emotion 패키지 완전 테스트"
echo "=========================================="

# 환경 설정
export ROS_DOMAIN_ID=13

# 1. pinky_interfaces 확인
echo ""
echo "1. pinky_interfaces 확인"
echo "----------------------------------------"
if ros2 interface list | grep -q pinky_interfaces; then
    echo "✅ pinky_interfaces 로드됨"
    ros2 interface show pinky_interfaces/srv/Emotion
else
    echo "❌ pinky_interfaces 로드되지 않음"
    echo "   해결: ros2-server 워크스페이스 소스 필요"
    exit 1
fi

# 2. 서비스 확인
echo ""
echo "2. 서비스 확인"
echo "----------------------------------------"
ros2 service list | grep emotion

# 3. 서비스 타입 확인
echo ""
echo "3. 서비스 타입 확인"
echo "----------------------------------------"
ros2 service type /set_emotion

# 4. 서비스 호출 테스트
echo ""
echo "4. 서비스 호출 테스트"
echo "----------------------------------------"
EMOTIONS=("hello" "happy" "sad" "angry" "fun" "bored" "interest" "basic")

for emotion in "${EMOTIONS[@]}"; do
    echo "Testing: $emotion"
    ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: \"$emotion\"}" 2>&1 | head -5
    sleep 1
done

echo ""
echo "=========================================="
echo "테스트 완료"
echo "=========================================="
```

## 참고

- `pinky_interfaces` 패키지는 `ros2-server` 워크스페이스에 포함되어 있습니다
- 모든 ROS2 노드는 `pinky_interfaces`를 사용하기 전에 해당 워크스페이스를 소스해야 합니다
- `emotion_controller_server`는 선택적이며, 직접 `/set_emotion` 호출도 가능합니다

