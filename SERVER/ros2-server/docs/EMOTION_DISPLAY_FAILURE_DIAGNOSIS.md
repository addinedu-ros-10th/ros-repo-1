# Emotion Display 실패 원인 진단

## 문제 증상

- ✅ 서비스 호출 성공: `Emotion set to interest`
- ✅ `pinky_emotion` 노드가 요청을 받음: `Request to set emotion to 'interest'`
- ❌ LCD에 emotion이 표시되지 않음
- ✅ 문자 display는 정상 작동

## 원인 분석

### 가능한 원인 1: 잘못된 emotion 서버 실행

**문제**: 원본 `emotion_server`가 실행 중일 수 있음
- 원본 `emotion_server`는 직접 LCD를 사용하려고 시도
- GPIO 충돌로 인해 LCD 표시 실패
- `emotion_server_rfred`가 실행되어야 함

**확인 방법**:
```bash
# 실행 중인 노드 확인
ros2 node list | grep emotion

# 예상 출력:
# /pinky_emotion  (노드 이름은 동일하지만 실행 파일이 다를 수 있음)

# 실행 중인 프로세스 확인
ps aux | grep emotion_server
```

**해결 방법**:
```bash
# 기존 emotion 서버 종료
pkill -f emotion_server
pkill -f pinky_emotion

# emotion_server_rfred 실행
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 run pinky_emotion emotion_server_rfred
```

### 가능한 원인 2: pinky_lcd_display_interfaces 미로드

**문제**: `emotion_server_rfred`가 `pinky_lcd_display_interfaces`를 찾지 못함
- LCD display 서비스를 사용할 수 없음
- 경고 메시지: `Warning: pinky_lcd_display_interfaces not available`

**확인 방법**:
```bash
# emotion_server_rfred 실행 시 로그 확인
# 다음 메시지가 있어야 함:
# - "LCD display service connected."
# - "Warning: pinky_lcd_display_interfaces not available" (없어야 함)
```

**해결 방법**:
```bash
# rfred 워크스페이스에서 빌드 및 소스
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display_interfaces
source install/setup.bash
```

### 가능한 원인 3: LCD Display 노드 미실행

**문제**: `lcd_controller/display_image` 서비스가 없음
- `emotion_server_rfred`가 LCD 서비스를 찾을 수 없음
- 서비스 호출 실패

**확인 방법**:
```bash
# LCD 서비스 확인
ros2 service list | grep lcd_controller

# 예상 출력:
# /lcd_controller/display_image
# /lcd_controller/set_display
# /lcd_controller/clear_display
```

**해결 방법**:
```bash
# LCD 디스플레이 노드 실행
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 launch pinky_lcd_display lcd_display.launch.py
```

### 가능한 원인 4: 서비스 연결 실패

**문제**: `emotion_server_rfred`가 LCD 서비스를 찾지 못함
- 서비스가 존재하지만 연결 실패
- 타임아웃 발생

**확인 방법**:
```bash
# 서비스 정보 확인
ros2 service info /lcd_controller/display_image

# 노드 목록 확인
ros2 node list | grep lcd
```

## 종합 해결 방법

### 1단계: 환경 확인

```bash
# 모든 터미널에서 ROS_DOMAIN_ID 설정
export ROS_DOMAIN_ID=13

# rfred 워크스페이스 소스
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
```

### 2단계: 기존 프로세스 종료

```bash
# 기존 emotion 서버 종료
pkill -f emotion_server
pkill -f pinky_emotion
pkill -f lcd_node

# GPIO 정리 (필요시)
sudo systemctl restart gpiod
```

### 3단계: LCD Display 노드 실행 (터미널 1)

```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 launch pinky_lcd_display lcd_display.launch.py
```

**확인 사항**:
- 노드가 정상적으로 시작되었는지 확인
- `lcd_controller/display_image` 서비스가 등록되었는지 확인

### 4단계: Emotion 서버 실행 (터미널 2)

```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
export ROS_DOMAIN_ID=13
ros2 run pinky_emotion emotion_server_rfred
```

**확인 사항**:
- `pinky_lcd_display_interfaces not available` 경고가 없어야 함
- `LCD display service connected.` 메시지가 있어야 함
- `Pinky's emotion server is ready!!` 메시지 확인

### 5단계: 서비스 호출 테스트

```bash
# 서비스 목록 확인
ros2 service list | grep -E "emotion|lcd"

# 서비스 호출
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'
```

## 디버깅 명령어

### 서비스 상태 확인

```bash
# 서비스 목록
ros2 service list | grep -E "emotion|lcd"

# 서비스 정보
ros2 service info /set_emotion
ros2 service info /lcd_controller/display_image

# 노드 목록
ros2 node list | grep -E "emotion|lcd"
```

### 로그 확인

```bash
# ROS2 로그 확인
ros2 topic echo /rosout | grep -E "emotion|lcd"

# 또는 직접 로그 파일 확인
ls -la ~/.ros/log/
```

### 프로세스 확인

```bash
# 실행 중인 프로세스 확인
ps aux | grep -E "emotion|lcd"

# GPIO 사용 확인
gpioinfo | grep -E "27|25|18"
```

## 예상 로그 (정상 동작)

### emotion_server_rfred 정상 실행 시

```
[INFO] [pinky_emotion]: Pre-loading all emotion GIFs into memory...
[INFO] [pinky_emotion]:   - Cached 'hello' (41 frames)
[INFO] [pinky_emotion]:   - Cached 'happy' (34 frames)
...
[INFO] [pinky_emotion]: Pinky's emotion server is ready!! All GIFs pre-loaded.
[INFO] [pinky_emotion]: LCD display service connected.
```

### 서비스 호출 시

```
[INFO] [pinky_emotion]: Request to set emotion to 'hello'
[INFO] [pinky_emotion]: Displaying frame 0/41
[INFO] [pinky_emotion]: Displaying frame 1/41
...
```

## 문제 해결 체크리스트

- [ ] `emotion_server_rfred`가 실행 중인가?
- [ ] `pinky_lcd_display_interfaces`가 로드되었는가?
- [ ] LCD Display 노드가 실행 중인가?
- [ ] `lcd_controller/display_image` 서비스가 등록되었는가?
- [ ] `ROS_DOMAIN_ID`가 모든 터미널에서 동일한가?
- [ ] GPIO 충돌이 없는가?

## 참고

- `emotion_server_rfred`는 `rfred` 워크스페이스에서 실행해야 합니다
- 원본 `emotion_server`는 직접 LCD를 사용하므로 GPIO 충돌이 발생할 수 있습니다
- LCD Display 노드가 먼저 실행되어야 `emotion_server_rfred`가 서비스를 찾을 수 있습니다

