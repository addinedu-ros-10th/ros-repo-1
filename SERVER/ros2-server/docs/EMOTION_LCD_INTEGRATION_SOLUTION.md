# Emotion LCD 통합 해결 방안

## 문제 상황

`pinky_lcd_display` (rfred)와 `pinky_emotion` (pinky_pro) 두 노드가 동시에 LCD를 사용하려고 할 때 GPIO 핀 충돌이 발생합니다:

```
lgpio.error: 'GPIO not allocated'
```

**원인**: 두 노드가 모두 직접 LCD 하드웨어를 사용하여 같은 GPIO 핀 (27, 25, 18)을 점유하려고 함

## 해결 방안

### 1. emotion 패키지를 rfred로 통합

- `pinky_emotion` 패키지를 `ROS2/rfred/src/`로 복사
- rfred 워크스페이스에서 빌드 및 관리

### 2. LCD 리소스 공유

- `pinky_lcd_display`만 LCD 하드웨어를 직접 사용
- `pinky_emotion`은 `pinky_lcd_display`의 서비스를 통해 LCD를 제어

### 3. 구현 내용

#### 3.1 DisplayImage 서비스 추가

**서비스 인터페이스**: `pinky_lcd_display_interfaces/srv/DisplayImage.srv`

```srv
string image_path          # 이미지 파일 경로
bool use_path             # true: image_path 사용
uint8[] image_data        # 이미지 데이터 (향후 구현)
uint16 x                  # X 좌표
uint16 y                  # Y 좌표
uint16 width              # 너비 (0이면 원본)
uint16 height             # 높이 (0이면 원본)
bool clear_before         # 표시 전 화면 지우기
---
bool success
string message
```

#### 3.2 pinky_lcd_display에 이미지 표시 기능 추가

**파일**: `ROS2/rfred/src/pinky_lcd_display/pinky_lcd_display/lcd_manager.py`

- `show_image()` 메서드 추가
- GIF, PNG, JPEG 이미지 지원
- 이미지 리사이즈 및 배치 기능

**파일**: `ROS2/rfred/src/pinky_lcd_display/pinky_lcd_display/lcd_node.py`

- `display_image_callback()` 추가
- `lcd_controller/display_image` 서비스 서버 등록

#### 3.3 emotion 노드 수정

**파일**: `ROS2/rfred/src/pinky_emotion/pinky_emotion/emotion_server_rfred.py`

- 직접 LCD 사용 제거 (`LCD()` 인스턴스 생성 제거)
- `DisplayImage` 서비스 클라이언트 사용
- GIF 프레임을 임시 파일로 저장하여 서비스에 전달

## 사용 방법

### 1. 빌드

```bash
cd ~/ros-repo-1/ROS2/rfred
colcon build --packages-select pinky_lcd_display_interfaces pinky_lcd_display pinky_emotion
source install/setup.bash
```

### 2. 실행

**터미널 1**: LCD 디스플레이 노드 실행
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 launch pinky_lcd_display lcd_display.launch.py
```

**터미널 2**: Emotion 서버 실행 (rfred 버전)
```bash
cd ~/ros-repo-1/ROS2/rfred
source install/setup.bash
ros2 run pinky_emotion emotion_server_rfred
```

### 3. 테스트

```bash
# 감정 표현 설정
ros2 service call /set_emotion pinky_interfaces/srv/Emotion "{emotion: 'happy'}"

# 또는 API 서버를 통해
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy"}'
```

## 장점

1. **GPIO 충돌 해결**: 단일 노드만 LCD 하드웨어 사용
2. **리소스 관리**: LCD 리소스를 중앙에서 관리
3. **유지보수성**: LCD 관련 코드가 한 곳에 집중
4. **확장성**: 다른 노드도 동일한 방식으로 LCD 사용 가능

## 향후 개선 사항

1. **이미지 데이터 직접 전송**: 임시 파일 대신 이미지 데이터를 직접 전송하여 성능 향상
2. **GIF 애니메이션 최적화**: 프레임 전송 최적화
3. **우선순위 관리**: 여러 노드가 동시에 LCD를 요청할 때 우선순위 처리

## 참고

- `emotion_server_rfred.py`: rfred 환경용 emotion 서버 (LCD 서비스 사용)
- `emotion_server.py`: 원본 emotion 서버 (직접 LCD 사용, pinky_pro 환경용)

