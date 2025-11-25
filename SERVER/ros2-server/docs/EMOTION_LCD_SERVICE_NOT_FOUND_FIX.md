# Emotion LCD 서비스 찾기 실패 해결 가이드

## 문제 증상

```bash
ros2 run pinky_emotion emotion_server_rfred

[INFO] [pinky_emotion]: Waiting for LCD display service...
[WARN] [pinky_emotion]: LCD display service not available. Emotion display will be disabled.
```

`emotion_server_rfred`가 `lcd_controller/display_image` 서비스를 찾지 못합니다.

## 원인 분석

### 가능한 원인

1. **LCD Display 노드가 실행되지 않음**
   - `lcd_controller/display_image` 서비스가 등록되지 않음

2. **ROS_DOMAIN_ID 불일치**
   - LCD Display 노드와 Emotion 서버가 다른 도메인에 있음

3. **서비스 이름 불일치**
   - 서비스 이름이 예상과 다름

4. **타임아웃**
   - 서비스가 등록되기 전에 확인 시도

## 해결 방법

### 1단계: LCD Display 노드 실행 확인

**터미널 1 - LCD Display 노드 실행**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 launch pinky_lcd_display lcd_display.launch.py
```

**확인 사항**:
- 노드가 정상적으로 시작되었는지 확인
- 로그에 "pinky_lcd_node started with service/action support" 메시지 확인

### 2단계: 서비스 목록 확인

**터미널 2 - 서비스 확인**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13

# 서비스 목록 확인
ros2 service list | grep lcd_controller

# 예상 출력:
# /lcd_controller/display_image
# /lcd_controller/set_display
# /lcd_controller/clear_display
# /lcd_controller/set_style
# /lcd_controller/set_layout
```

**중요**: `/lcd_controller/display_image` 서비스가 있어야 합니다.

### 3단계: 서비스 정보 확인

```bash
# 서비스 정보 확인
ros2 service info /lcd_controller/display_image

# 예상 출력:
# Type: pinky_lcd_display_interfaces/srv/DisplayImage
# Clients count: 0
# Services count: 1
```

### 4단계: Emotion 서버 실행

**터미널 3 - Emotion 서버 실행**:
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 run pinky_emotion emotion_server_rfred
```

**예상 로그**:
```
[INFO] [pinky_emotion]: Waiting for LCD display service...
[INFO] [pinky_emotion]: LCD display service connected.  ← 이 메시지가 나와야 함
[INFO] [pinky_emotion]: Pre-loading all emotion GIFs into memory...
```

## 문제 해결 체크리스트

### 문제 1: 서비스가 보이지 않음

**확인 사항**:
```bash
# 1. 노드 목록 확인
ros2 node list | grep lcd

# 예상 출력:
# /pinky_lcd_node

# 2. 서비스 목록 확인
ros2 service list | grep display_image

# 3. ROS_DOMAIN_ID 확인
echo $ROS_DOMAIN_ID
# 모든 터미널에서 동일한 값 (13)이어야 함
```

**해결 방법**:
1. LCD Display 노드가 실행 중인지 확인
2. `ROS_DOMAIN_ID`가 모든 터미널에서 동일한지 확인
3. 노드를 재시작

### 문제 2: 서비스 타입 불일치

**확인 사항**:
```bash
# 서비스 타입 확인
ros2 service type /lcd_controller/display_image

# 예상 출력:
# pinky_lcd_display_interfaces/srv/DisplayImage
```

**해결 방법**:
1. `pinky_lcd_display_interfaces` 패키지가 빌드되었는지 확인
2. 워크스페이스가 소스되었는지 확인

### 문제 3: 타임아웃

**원인**: 서비스가 등록되기 전에 확인 시도

**해결 방법**:
1. LCD Display 노드를 먼저 실행
2. 서비스가 등록될 때까지 대기 (약 2-3초)
3. 그 다음 Emotion 서버 실행

## 실행 순서 (중요)

### 올바른 실행 순서

1. **터미널 1**: LCD Display 노드 실행
   ```bash
   cd ~/ros-repo-1/ROS2/rfred
   source install/setup.bash
   export ROS_DOMAIN_ID=13
   ros2 launch pinky_lcd_display lcd_display.launch.py
   ```

2. **대기**: 서비스가 등록될 때까지 2-3초 대기

3. **터미널 2**: 서비스 확인 (선택사항)
   ```bash
   cd ~/ros-repo-1/ROS2/rfred
   source install/setup.bash
   export ROS_DOMAIN_ID=13
   ros2 service list | grep display_image
   ```

4. **터미널 3**: Emotion 서버 실행
   ```bash
   cd ~/ros-repo-1/ROS2/rfred
   source install/setup.bash
   export ROS_DOMAIN_ID=13
   ros2 run pinky_emotion emotion_server_rfred
   ```

## 디버깅 명령어

### 전체 상태 확인

```bash
# 환경 설정
export ROS_DOMAIN_ID=13
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash

# 노드 목록
ros2 node list

# 서비스 목록
ros2 service list

# 특정 서비스 정보
ros2 service info /lcd_controller/display_image

# 토픽 목록
ros2 topic list

# 로그 확인
ros2 topic echo /rosout | grep -E "lcd|emotion"
```

### 서비스 직접 호출 테스트

```bash
# DisplayImage 서비스 테스트 (이미지 파일 경로 필요)
ros2 service call /lcd_controller/display_image \
  pinky_lcd_display_interfaces/srv/DisplayImage \
  '{image_path: "/path/to/image.png", use_path: true, x: 0, y: 0, width: 0, height: 0, clear_before: false}'
```

## 예상 정상 동작

### LCD Display 노드 실행 시
```
[INFO] [pinky_lcd_node]: pinky_lcd_node started with service/action support
```

### Emotion 서버 실행 시
```
[INFO] [pinky_emotion]: Waiting for LCD display service...
[INFO] [pinky_emotion]: LCD display service connected.  ← 성공!
[INFO] [pinky_emotion]: Pre-loading all emotion GIFs into memory...
[INFO] [pinky_emotion]:   - Cached 'hello' (41 frames)
...
[INFO] [pinky_emotion]: Pinky's emotion server is ready!! All GIFs pre-loaded.
```

## 참고

- LCD Display 노드가 먼저 실행되어야 합니다
- 모든 터미널에서 `ROS_DOMAIN_ID=13`을 설정해야 합니다
- `pinky_lcd_display_interfaces` 패키지가 빌드되고 소스되어야 합니다
- 서비스 등록에는 약 2-3초가 소요될 수 있습니다

