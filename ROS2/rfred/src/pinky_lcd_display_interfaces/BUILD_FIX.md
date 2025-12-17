# 빌드 에러 해결 가이드

## 문제점

### 에러 메시지
```
CMake Error at /opt/ros/jazzy/share/rosidl_cmake/cmake/rosidl_generate_interfaces.cmake:192 (message):
rosidl_generate_interfaces() the passed dependency 'std_msgs' has not been
found before using find_package()
```

### 원인 분석

1. **문제 상황**:
   - `CMakeLists.txt`의 `rosidl_generate_interfaces()` 함수에서 `DEPENDENCIES std_msgs`를 지정했습니다.
   - 하지만 `find_package(std_msgs REQUIRED)`를 호출하지 않았습니다.

2. **왜 필요한가?**:
   - `LCDStatus.msg`와 `LCDEvent.msg` 파일에서 `std_msgs/Header header`를 사용하고 있습니다.
   - ROS2에서는 메시지 타입을 사용하기 전에 해당 패키지를 `find_package()`로 먼저 찾아야 합니다.

3. **CMake 동작 방식**:
   - `rosidl_generate_interfaces()`의 `DEPENDENCIES`는 이미 `find_package()`로 찾은 패키지를 참조합니다.
   - 따라서 `DEPENDENCIES`에 추가하기 전에 반드시 `find_package()`를 먼저 호출해야 합니다.

## 해결 방법

### 수정 내용

`CMakeLists.txt` 파일에 `find_package(std_msgs REQUIRED)`를 추가했습니다:

```cmake
# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(std_msgs REQUIRED)  # ← 추가됨

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/SetDisplay.srv"
  "srv/SetStyle.srv"
  "srv/ClearDisplay.srv"
  "srv/SetLayout.srv"
  "msg/LCDStatus.msg"
  "msg/LCDEvent.msg"
  "action/SetDisplay.action"
  "action/ScrollText.action"
  DEPENDENCIES std_msgs
)
```

### 확인 사항

- ✅ `package.xml`에는 이미 `<depend>std_msgs</depend>`가 포함되어 있습니다.
- ✅ `CMakeLists.txt`에 `find_package(std_msgs REQUIRED)`가 추가되었습니다.
- ✅ `rosidl_generate_interfaces()`의 `DEPENDENCIES std_msgs`는 그대로 유지됩니다.

## 빌드 테스트

다음 명령으로 빌드를 다시 시도하세요:

```bash
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display_interfaces
```

성공하면 전체 빌드를 진행하세요:

```bash
colcon build
```

## 참고 사항

### ROS2 CMake 패턴

ROS2 인터페이스 패키지에서 다른 메시지 타입을 사용할 때는 다음 순서를 따라야 합니다:

1. `package.xml`에 의존성 추가: `<depend>std_msgs</depend>`
2. `CMakeLists.txt`에 `find_package()` 추가: `find_package(std_msgs REQUIRED)`
3. `rosidl_generate_interfaces()`의 `DEPENDENCIES`에 추가: `DEPENDENCIES std_msgs`

### std_msgs 사용 이유

`LCDStatus.msg`와 `LCDEvent.msg`에서 `std_msgs/Header`를 사용하는 이유:
- **표준화**: ROS2 표준 메시지 형식
- **타임스탬프**: `header.stamp`로 메시지 생성 시간 기록
- **프레임 ID**: `header.frame_id`로 메시지 소스 식별 (선택적)
- **호환성**: 다른 ROS2 패키지와의 호환성 향상

## 추가 문제 해결

만약 여전히 빌드가 실패한다면:

1. **워크스페이스 소스 확인**:
   ```bash
   source /opt/ros/jazzy/setup.bash
   ```

2. **의존성 설치 확인**:
   ```bash
   sudo apt update
   sudo apt install ros-jazzy-std-msgs
   ```

3. **빌드 디렉토리 정리 후 재빌드**:
   ```bash
   cd ~/ros-repo-1/ROS2/rfred
   rm -rf build install log
   colcon build
   ```

