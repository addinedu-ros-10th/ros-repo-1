# Emotion 패키지 테스트 가이드

## 문제 진단

### 현재 문제점

1. **`pinky_lcd_display_interfaces`를 찾지 못함**
   - `emotion_server_rfred` 실행 시 경고: `Warning: pinky_lcd_display_interfaces not available`
   - 원인: 빌드가 제대로 되지 않았거나 소스가 제대로 되지 않음

2. **서비스 호출 타임아웃**
   - `emotion_controller_server`가 `pinky_emotion`의 `set_emotion` 서비스를 찾지 못함
   - 원인: 서비스 이름 불일치 또는 노드가 실행되지 않음

## 해결 방법

### 1단계: 빌드 확인 및 재빌드

```bash
cd ~/ros-repo-1/ROS2/rfred

# 모든 관련 패키지 빌드
colcon build --packages-select \
  pinky_lcd_display_interfaces \
  pinky_lcd_display \
  pinky_emotion

# 빌드 확인
source install/setup.bash

# 패키지가 제대로 설치되었는지 확인
ros2 pkg list | grep pinky
```

**예상 출력**:
```
pinky_emotion
pinky_lcd_display
pinky_lcd_display_interfaces
```

### 2단계: 서비스 확인

#### 2.1 LCD 디스플레이 노드 실행

**터미널 1**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 launch pinky_lcd_display lcd_display.launch.py
```

**확인 사항**:
- 노드가 정상적으로 시작되었는지 확인
- `lcd_controller/display_image` 서비스가 등록되었는지 확인

#### 2.2 Emotion 서버 실행 (rfred 버전)

**터미널 2**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 run pinky_emotion emotion_server_rfred
```

**확인 사항**:
- `pinky_lcd_display_interfaces not available` 경고가 없어야 함
- `LCD display service connected.` 메시지가 나와야 함
- `set_emotion` 서비스가 등록되었는지 확인

#### 2.3 서비스 목록 확인

**터미널 3**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13

# 서비스 목록 확인
ros2 service list | grep -E "emotion|lcd"

# 예상 출력:
# /lcd_controller/display_image
# /lcd_controller/set_display
# /lcd_controller/clear_display
# /set_emotion
```

**중요**: `emotion_server_rfred`는 `/set_emotion` 서비스를 제공합니다 (네임스페이스 없음).

### 3단계: 직접 서비스 호출 테스트

#### 3.1 Emotion 서비스 직접 호출

```bash
# 터미널 3에서
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: 'hello'}"

# 다른 감정 테스트
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: 'happy'}"
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: 'sad'}"
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: 'angry'}"
```

**예상 응답**:
```
waiting for service to become available...
requester: making request: pinky_interfaces.srv.Emotion_Request(emotion='hello')

response:
pinky_interfaces.srv.Emotion_Response(response='Emotion set to hello')
```

#### 3.2 LCD DisplayImage 서비스 직접 호출

```bash
# 이미지 파일 경로로 테스트 (임시)
ros2 service call /lcd_controller/display_image \
  pinky_lcd_display_interfaces/srv/DisplayImage \
  "{image_path: '/path/to/image.png', use_path: true, x: 0, y: 0, width: 0, height: 0, clear_before: false}"
```

### 4단계: emotion_controller_server 실행 (선택사항)

**참고**: `emotion_controller_server`는 `ros2-server` 워크스페이스에 있습니다. 
이것은 중간 서비스 서버로, API 서버에서 사용할 수 있습니다.

**터미널 4** (선택사항):
```bash
cd ~/ros-repo-1/SERVER/ros2-server
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 run pinky_emotion_controller emotion_controller_server
```

**확인 사항**:
- `emotion_controller/set_emotion` 서비스가 등록되었는지 확인
- `/set_emotion` 서비스를 찾을 수 있는지 확인

**서비스 호출 테스트**:
```bash
ros2 service call /emotion_controller/set_emotion \
  pinky_interfaces/srv/Emotion \
  "{emotion: 'hello'}"
```

### 5단계: API 서버를 통한 테스트

#### 5.1 API 서버 실행

**터미널 5**:
```bash
cd ~/ros-repo-1/SERVER/ros2-server/api-server
source ../install/setup.bash  # ros2-server 워크스페이스 소스
source venv/bin/activate
export ROS_DOMAIN_ID=13
./run_standalone.sh
```

#### 5.2 API 호출 테스트

**터미널 6**:
```bash
# 감정 표현 설정
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "hello"}'

# 다른 감정 테스트
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy"}'

curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "sad"}'
```

**예상 응답**:
```json
{
  "success": true,
  "message": "Emotion set to hello",
  "emotion": "hello"
}
```

## 문제 해결 체크리스트

### 문제 1: `pinky_lcd_display_interfaces not available`

**해결 방법**:
1. 빌드 확인:
   ```bash
   cd ~/ros-repo-1/ROS2/rfred
   colcon build --packages-select pinky_lcd_display_interfaces
   source install/setup.bash
   ```

2. Python 경로 확인:
   ```bash
   python3 -c "from pinky_lcd_display_interfaces.srv import DisplayImage; print('OK')"
   ```

3. 패키지 설치 확인:
   ```bash
   ros2 pkg list | grep pinky_lcd_display_interfaces
   ```

### 문제 2: 서비스 호출 타임아웃

**해결 방법**:
1. 서비스 목록 확인:
   ```bash
   ros2 service list | grep emotion
   ```

2. 노드 목록 확인:
   ```bash
   ros2 node list | grep emotion
   ```

3. ROS_DOMAIN_ID 확인:
   ```bash
   echo $ROS_DOMAIN_ID
   # 모든 터미널에서 동일한 값 (13)이어야 함
   ```

4. 서비스 정보 확인:
   ```bash
   ros2 service info /set_emotion
   ```

### 문제 3: LCD 디스플레이가 작동하지 않음

**해결 방법**:
1. LCD 노드가 실행 중인지 확인:
   ```bash
   ros2 node list | grep lcd
   ```

2. LCD 서비스 확인:
   ```bash
   ros2 service list | grep lcd_controller
   ```

3. GPIO 충돌 확인:
   ```bash
   # 기존 프로세스 종료
   pkill -f lcd_node
   pkill -f pinky_emotion
   ```

## 전체 테스트 시나리오

### 시나리오 1: 기본 테스트 (명령어 기반)

1. **LCD 디스플레이 노드 실행** (터미널 1)
2. **Emotion 서버 실행** (터미널 2)
3. **서비스 직접 호출** (터미널 3):
   ```bash
   ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: 'hello'}"
   ```

### 시나리오 2: API 서버 통합 테스트

1. **LCD 디스플레이 노드 실행** (터미널 1)
2. **Emotion 서버 실행** (터미널 2)
3. **API 서버 실행** (터미널 3)
4. **API 호출** (터미널 4):
   ```bash
   curl -X POST http://localhost:8004/api/emotion/set \
     -H "Content-Type: application/json" \
     -d '{"emotion": "hello"}'
   ```

### 시나리오 3: emotion_controller_server 사용 (선택사항)

1. **LCD 디스플레이 노드 실행** (터미널 1)
2. **Emotion 서버 실행** (터미널 2)
3. **emotion_controller_server 실행** (터미널 3)
4. **API 서버 실행** (터미널 4)
5. **API 호출** (터미널 5)

## 지원 감정 타입

- `hello`: 인사
- `basic`: 기본 상태
- `angry`: 화남
- `bored`: 지루함
- `fun`: 재미있음
- `happy`: 행복함
- `interest`: 관심
- `sad`: 슬픔

## 디버깅 명령어

```bash
# 서비스 목록
ros2 service list

# 노드 목록
ros2 node list

# 서비스 정보
ros2 service info /set_emotion
ros2 service info /lcd_controller/display_image

# 서비스 타입 확인
ros2 service type /set_emotion
ros2 service type /lcd_controller/display_image

# 토픽 목록
ros2 topic list

# 로그 확인
ros2 topic echo /rosout
```

## 참고

- 모든 터미널에서 `ROS_DOMAIN_ID=13`을 설정해야 합니다
- `pinky_lcd_display` 노드가 먼저 실행되어야 `emotion_server_rfred`가 LCD 서비스를 사용할 수 있습니다
- `emotion_server_rfred`는 `/set_emotion` 서비스를 제공합니다 (네임스페이스 없음)

