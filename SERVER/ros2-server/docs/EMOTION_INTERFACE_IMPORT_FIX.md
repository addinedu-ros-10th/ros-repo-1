# Emotion Interface Import 오류 해결

## 문제 증상

```bash
ros2 run pinky_emotion emotion_server_rfred
Warning: pinky_lcd_display_interfaces not available. Emotion display will be disabled.
```

빌드와 소스는 성공했지만 Python에서 인터페이스를 import할 수 없습니다.

## 원인

**`DisplayImage.srv`가 `CMakeLists.txt`에 포함되지 않음**

`pinky_lcd_display_interfaces` 패키지의 `CMakeLists.txt`를 보면:

```cmake
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/SetDisplay.srv"
  "srv/SetStyle.srv"
  "srv/ClearDisplay.srv"
  "srv/SetLayout.srv"
  # "srv/DisplayImage.srv"  ← 이 줄이 없음!
  ...
)
```

`DisplayImage.srv` 파일은 존재하지만, `rosidl_generate_interfaces()` 함수에 포함되지 않아서:
- Python 바인딩이 생성되지 않음
- `from pinky_lcd_display_interfaces.srv import DisplayImage` 실패
- `emotion_server_rfred`가 인터페이스를 찾을 수 없음

## 해결 방법

### 1단계: CMakeLists.txt 수정

`ROS2/rfred/src/pinky_lcd_display_interfaces/CMakeLists.txt` 파일에 `DisplayImage.srv` 추가:

```cmake
rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/SetDisplay.srv"
  "srv/SetStyle.srv"
  "srv/ClearDisplay.srv"
  "srv/SetLayout.srv"
  "srv/DisplayImage.srv"  # ← 추가
  "msg/LCDStatus.msg"
  "msg/LCDEvent.msg"
  "action/SetDisplay.action"
  "action/ScrollText.action"
  DEPENDENCIES std_msgs
)
```

### 2단계: 재빌드

```bash
cd ~/ros-repo-1/ROS2/rfred

# pinky_lcd_display_interfaces만 재빌드
colcon build --packages-select pinky_lcd_display_interfaces

# 또는 전체 재빌드
colcon build
```

### 3단계: 워크스페이스 소스

```bash
source install/setup.bash
```

### 4단계: 확인

```bash
# Python에서 import 테스트
python3 -c "from pinky_lcd_display_interfaces.srv import DisplayImage; print('✅ OK')"

# ROS2 인터페이스 확인
ros2 interface show pinky_lcd_display_interfaces/srv/DisplayImage

# emotion_server_rfred 실행
ros2 run pinky_emotion emotion_server_rfred
# 경고 메시지가 없어야 함
```

## 예상 결과

### 수정 전
```
Warning: pinky_lcd_display_interfaces not available. Emotion display will be disabled.
```

### 수정 후
```
[INFO] [pinky_emotion]: Waiting for LCD display service...
[INFO] [pinky_emotion]: LCD display service connected.
[INFO] [pinky_emotion]: Pinky's emotion server is ready!! All GIFs pre-loaded.
```

## 추가 확인 사항

### Python 패키지 확인

```bash
# Python 경로 확인
python3 -c "import sys; print('\n'.join(sys.path))" | grep pinky_lcd_display_interfaces

# 패키지 위치 확인
find ~/ros-repo-1/ROS2/rfred/install -name "*pinky_lcd_display_interfaces*" -type d
```

### 빌드 출력 확인

빌드 시 다음과 같은 출력이 있어야 합니다:

```
Starting >>> pinky_lcd_display_interfaces
Finished <<< pinky_lcd_display_interfaces [X.XXs]
```

### 설치 확인

```bash
# install 디렉토리 확인
ls -la ~/ros-repo-1/ROS2/rfred/install/pinky_lcd_display_interfaces/

# Python 패키지 확인
ls -la ~/ros-repo-1/ROS2/rfred/install/pinky_lcd_display_interfaces/lib/python3.*/site-packages/pinky_lcd_display_interfaces/
```

## 문제 해결 체크리스트

- [ ] `DisplayImage.srv` 파일이 `srv/` 디렉토리에 있는가?
- [ ] `CMakeLists.txt`에 `"srv/DisplayImage.srv"`가 포함되어 있는가?
- [ ] 패키지를 재빌드했는가?
- [ ] 워크스페이스를 소스했는가?
- [ ] Python에서 import가 성공하는가?
- [ ] `emotion_server_rfred` 실행 시 경고가 없는가?

## 참고

- ROS2 인터페이스 패키지는 `rosidl_generate_interfaces()` 함수에 명시적으로 포함해야 Python 바인딩이 생성됩니다
- 파일만 존재한다고 해서 자동으로 포함되지 않습니다
- 빌드 후 반드시 `source install/setup.bash`를 실행해야 Python 경로에 추가됩니다

