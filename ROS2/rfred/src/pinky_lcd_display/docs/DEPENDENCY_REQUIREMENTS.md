# pinky_lcd_display 패키지 의존성 요구사항

## 개요

이 문서는 `pinky_lcd_display` 패키지가 정상 동작하기 위해 필요한 의존성과 설치 요구사항을 정리한 것입니다.

## pinky_lcd_display_interfaces 패키지에 대한 이해

### 1. 인터페이스 패키지의 역할

`pinky_lcd_display_interfaces`는 **인터페이스 정의 패키지**입니다. 이 패키지는:

- ✅ **서비스 타입 정의** (`.srv` 파일)
- ✅ **액션 타입 정의** (`.action` 파일)
- ✅ **메시지 타입 정의** (`.msg` 파일)

만 포함합니다.

### 2. 인터페이스 패키지는 노드를 실행하지 않습니다

**중요**: `pinky_lcd_display_interfaces`는 **별도의 노드를 실행할 필요가 없습니다**.

- 인터페이스 패키지는 타입 정의만 제공합니다
- 실행 가능한 노드나 launch 파일을 포함하지 않습니다
- Python에서 `import`할 때만 사용됩니다

### 3. 언제 필요한가?

#### 빌드 시 (Build Time)
- ✅ **필수**: `pinky_lcd_display` 패키지를 빌드할 때 반드시 필요합니다
- `package.xml`에 `<depend>pinky_lcd_display_interfaces</depend>`로 선언되어 있으므로, 빌드 시스템이 자동으로 빌드 순서를 결정합니다

#### 런타임 시 (Runtime)
- ✅ **필수**: `pinky_lcd_display` 노드를 실행할 때 Python에서 import하기 위해 필요합니다
- 인터페이스 패키지가 빌드되어 `install/` 디렉토리에 설치되어 있어야 합니다
- Python 경로에 인터페이스 패키지의 Python 모듈이 있어야 합니다

## 현재 코드의 동작 방식

현재 `lcd_node.py`는 다음과 같이 구현되어 있습니다:

```python
try:
    from pinky_lcd_display_interfaces.srv import SetDisplay, SetStyle, ClearDisplay, SetLayout
    from pinky_lcd_display_interfaces.msg import LCDStatus, LCDEvent
    from pinky_lcd_display_interfaces.action import SetDisplay as SetDisplayAction
    from pinky_lcd_display_interfaces.action import ScrollText
    from rclpy.action import ActionServer
    INTERFACES_AVAILABLE = True
except ImportError:
    INTERFACES_AVAILABLE = False
    print("Warning: pinky_lcd_display_interfaces not available. Service/action features will be disabled.")
```

### 동작 방식

1. **인터페이스가 있는 경우**:
   - 서비스 서버, 액션 서버, 토픽 Publisher가 모두 활성화됩니다
   - `pinky_lcd_display_controller`가 클라이언트로 동작할 수 있습니다

2. **인터페이스가 없는 경우**:
   - 기본 토픽 구독 기능(`/lcd/status`)만 동작합니다
   - 서비스/액션 기능은 비활성화됩니다
   - 경고 메시지가 출력되지만 노드는 정상 실행됩니다

## 로봇에 설치해야 할 패키지

### 필수 패키지

로봇에서 `pinky_lcd_display` 패키지가 **모든 기능**을 사용하려면 다음 패키지들이 **빌드되어 설치**되어 있어야 합니다:

1. **`pinky_lcd_display_interfaces`** (필수) ✅ **통합 완료**
   - 위치: `ROS2/rfred/src/pinky_lcd_display_interfaces` (현재 브랜치에 포함됨)
   - 역할: 인터페이스 타입 정의
   - 실행: 노드 실행 불필요 (타입 정의만 제공)
   - **참고**: base/SERVER/ros2-server 브랜치에서 복사하여 통합 완료

2. **`pinky_lcd_display`** (필수)
   - 위치: `ROS2/rfred/src/pinky_lcd_display`
   - 역할: LCD 디스플레이 제어 노드
   - 실행: `ros2 run pinky_lcd_display lcd_node` 또는 launch 파일

### 선택적 패키지

3. **`pinky_lcd_display_controller`** (선택)
   - 위치: 다른 브랜치에 있음 (예: `SERVER/ros2-server/src/pinky_lcd_display_controller`)
   - 역할: 서비스/액션 클라이언트 (서버 측에서 사용)
   - 실행: 별도 노드로 실행 (로봇에는 필요 없을 수 있음)

## 설치 및 빌드 방법

### 방법 1: 단일 워크스페이스에서 빌드 (권장) ✅ **현재 상태**

`pinky_lcd_display_interfaces` 패키지가 `ROS2/rfred` 워크스페이스에 통합되어 있습니다:

```bash
# 로봇에서 실행
cd ~/ros-repo-1/ROS2/rfred

# 모든 패키지 빌드 (인터페이스 패키지가 자동으로 먼저 빌드됨)
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display
source install/setup.bash
```

**빌드 순서**: `pinky_lcd_display_interfaces`가 자동으로 먼저 빌드됩니다 (의존성 기반).

### 방법 2: 인터페이스 없이 빌드 (기본 기능만)

인터페이스 패키지가 없어도 빌드는 가능하지만, 서비스/액션 기능은 사용할 수 없습니다:

```bash
# 경고가 발생하지만 빌드는 됩니다
colcon build --packages-select pinky_lcd_display
```

**참고**: 현재 브랜치에는 `pinky_lcd_display_interfaces` 패키지가 포함되어 있으므로, 이 방법은 사용하지 않습니다.

## 실행 방법

### 기본 토픽 구독만 사용하는 경우

인터페이스 패키지가 없어도 동작합니다:

```bash
# 로봇에서 실행
ros2 run pinky_lcd_display lcd_node

# 또는 launch 파일 사용
ros2 launch pinky_lcd_display lcd_display.launch.py

# 토픽으로 내용 표시
ros2 topic pub --once /lcd/status std_msgs/msg/String \
  "{data: 'Pinky Status\nBattery: 78%'}"
```

### 서비스/액션 기능을 사용하는 경우

인터페이스 패키지가 **반드시 설치**되어 있어야 합니다:

```bash
# 1. 인터페이스 패키지가 빌드되어 있는지 확인
ros2 interface list | grep pinky_lcd_display_interfaces

# 2. 노드 실행
ros2 run pinky_lcd_display lcd_node

# 3. 서비스 호출 (다른 터미널에서)
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1'], show_timestamp: true}"
```

## 의존성 체크리스트

### 빌드 시 확인사항

- [ ] `pinky_lcd_display_interfaces` 패키지가 워크스페이스에 있거나 빌드되어 있음
- [ ] `package.xml`에 `<depend>pinky_lcd_display_interfaces</depend>` 선언됨
- [ ] `colcon build` 시 에러 없이 빌드됨

### 런타임 시 확인사항

- [ ] `install/` 디렉토리에 `pinky_lcd_display_interfaces` 패키지가 설치되어 있음
- [ ] `source install/setup.bash` 실행됨
- [ ] Python에서 import 가능: `python3 -c "from pinky_lcd_display_interfaces.srv import SetDisplay"`

### 기능 확인사항

- [ ] 기본 토픽 구독 기능 동작 (`/lcd/status`)
- [ ] 서비스 리스트에 `lcd_controller/set_display` 등이 보임 (`ros2 service list`)
- [ ] 액션 리스트에 `lcd_controller/set_display_action` 등이 보임 (`ros2 action list`)
- [ ] 상태 토픽 발행 확인 (`ros2 topic echo /lcd_controller/status`)

## 문제 해결

### 문제 1: ImportError 발생

**증상**:
```
Warning: pinky_lcd_display_interfaces not available. Service/action features will be disabled.
```

**원인**:
- `pinky_lcd_display_interfaces` 패키지가 빌드되지 않았거나 설치되지 않음
- `source install/setup.bash`가 실행되지 않음

**해결 방법**:
```bash
# 1. 인터페이스 패키지 빌드
cd ~/ros-repo-1/SERVER/ros2-server  # 또는 인터페이스 패키지가 있는 위치
colcon build --packages-select pinky_lcd_display_interfaces
source install/setup.bash

# 2. pinky_lcd_display 빌드
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display
source install/setup.bash

# 3. 확인
ros2 interface list | grep pinky_lcd_display_interfaces
```

### 문제 2: 서비스가 보이지 않음

**증상**:
```bash
ros2 service list | grep lcd_controller
# 아무것도 출력되지 않음
```

**원인**:
- 인터페이스 패키지가 없어서 서비스 서버가 생성되지 않음
- 노드가 실행되지 않음

**해결 방법**:
1. 인터페이스 패키지가 설치되어 있는지 확인
2. 노드가 실행 중인지 확인: `ros2 node list | grep pinky_lcd_node`
3. 노드 로그 확인: 경고 메시지가 있는지 확인

### 문제 3: 빌드 에러

**증상**:
```
ERROR: Could not find a package configuration file provided by "pinky_lcd_display_interfaces"
```

**원인**:
- `pinky_lcd_display_interfaces` 패키지가 빌드되지 않음
- 워크스페이스에 패키지가 없음

**해결 방법**:
1. 인터페이스 패키지를 먼저 빌드
2. 또는 `package.xml`에서 의존성을 `<exec_depend>`로 변경 (빌드 시에는 필요 없고 런타임에만 필요)

## 권장 설치 구조

### 로봇에 설치할 패키지 ✅ **현재 구조**

```
/home/pinky/ros-repo-1/ROS2/rfred/
└── src/
    ├── pinky_lcd_display_interfaces/  # 인터페이스 정의 (필수) ✅ 통합 완료
    └── pinky_lcd_display/              # LCD 제어 노드 (필수)
```

### 빌드 순서

1. **먼저 빌드**: `pinky_lcd_display_interfaces` (자동으로 먼저 빌드됨)
2. **나중에 빌드**: `pinky_lcd_display` (의존성 기반 자동 처리)

### 실행

```bash
# 로봇에서
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display
source install/setup.bash
ros2 run pinky_lcd_display lcd_node

# 또는 launch 파일 사용
ros2 launch pinky_lcd_display lcd_display.launch.py
```

## 요약

### 핵심 포인트

1. **`pinky_lcd_display_interfaces`는 인터페이스 정의 패키지입니다**
   - 노드를 실행할 필요가 없습니다
   - 타입 정의만 제공합니다

2. **빌드 시 필수입니다**
   - `pinky_lcd_display` 패키지를 빌드하려면 인터페이스 패키지가 먼저 빌드되어 있어야 합니다

3. **런타임 시 필수입니다 (서비스/액션 사용 시)**
   - Python에서 import하기 위해 설치되어 있어야 합니다
   - 없어도 기본 토픽 구독 기능은 동작합니다

4. **로봇에 설치해야 합니다** ✅ **통합 완료**
   - 인터페이스 패키지가 현재 브랜치에 통합되어 있음
   - 로봇에 한 번에 설치 가능
   - 빌드 시 자동으로 인터페이스 패키지 먼저 빌드됨

### 최소 요구사항

- ✅ **기본 기능만 사용**: 인터페이스 패키지 불필요
- ✅ **서비스/액션 사용**: 인터페이스 패키지 필수 (빌드 + 설치)

## 참고

- [인터페이스 통합 현황](INTEGRATION_STATUS.md)
- [구현 계획서](IMPLEMENTATION_PLAN.md)
- [README](../README.md)

