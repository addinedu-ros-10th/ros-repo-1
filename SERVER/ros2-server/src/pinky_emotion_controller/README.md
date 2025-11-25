# pinky_emotion_controller

Pinky 로봇의 감정 표현을 제어하기 위한 ROS2 서비스 컨트롤러 패키지입니다.

## 개요

이 패키지는 `pinky_emotion` 패키지의 서비스를 원격에서 호출할 수 있도록 중간 서비스 서버를 제공합니다. 
`pinky_lcd_display_controller`와 유사한 구조로 설계되어 있습니다.

## 기능

- **서비스 기반 감정 표현 제어**: ROS2 서비스를 통해 로봇의 감정 표현을 제어
- **원격 호출 지원**: 다른 ROS2 노드에서 감정 표현을 제어할 수 있음
- **감정 타입 검증**: 지원하는 감정 타입만 허용

## 지원 감정 타입

- `hello`: 인사
- `basic`: 기본 상태
- `angry`: 화남
- `bored`: 지루함
- `fun`: 재미있음
- `happy`: 행복함
- `interest`: 관심
- `sad`: 슬픔

## 서비스

### emotion_controller/set_emotion

로봇의 감정 표현을 설정하는 서비스입니다.

**서비스 타입**: `pinky_interfaces/srv/Emotion`

**요청 (Request)**:
```python
string emotion  # 감정 타입
```

**응답 (Response)**:
```python
string response  # 응답 메시지
```

**사용 예시**:
```bash
ros2 service call /emotion_controller/set_emotion \
  pinky_interfaces/srv/Emotion \
  "{emotion: 'happy'}"
```

## 빌드 및 설치

```bash
cd SERVER/ros2-server
colcon build --packages-select pinky_emotion_controller
source install/setup.bash
```

## 의존성

이 패키지는 `pinky_interfaces` 패키지에 의존합니다. `pinky_interfaces`는 `ros2-server` 워크스페이스에 포함되어 있어 별도로 소스할 필요가 없습니다.

## 실행

```bash
# 서비스 서버 실행
ros2 run pinky_emotion_controller emotion_controller_server
```

**참고**: `pinky_interfaces` 패키지가 없으면 `ModuleNotFoundError: No module named 'pinky_interfaces'` 오류가 발생합니다. 
이 경우 위의 의존성 섹션을 참조하여 `pinky_pro` 워크스페이스를 소스하세요.

## 의존성

- `rclpy`: ROS2 Python 클라이언트 라이브러리
- `pinky_interfaces`: 감정 표현 서비스 인터페이스
- `std_msgs`: 표준 메시지 타입

## 통신 구조

```
[emotion_controller_server]
    |
    | ROS2 Service Call
    v
[pinky_emotion] (원격 노드)
    |
    | LCD 제어
    v
[LCD Display]
```

## API 서버 통합

이 패키지는 FastAPI 서버(`api-server`)에서도 사용할 수 있습니다.

**API 엔드포인트**: `POST /api/emotion/set`

**요청 예시**:
```json
{
  "emotion": "happy"
}
```

**응답 예시**:
```json
{
  "success": true,
  "message": "Emotion set to happy",
  "emotion": "happy"
}
```

자세한 내용은 `api-server` 문서를 참조하세요.

