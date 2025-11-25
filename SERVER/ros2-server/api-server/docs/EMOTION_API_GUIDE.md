# 감정 표현 API 가이드

## 개요

이 문서는 ROS2 API Server의 감정 표현 제어 기능을 설명합니다.

## API 엔드포인트

### POST /api/emotion/set

로봇의 감정 표현을 설정합니다.

**요청 본문**:
```json
{
  "emotion": "happy"
}
```

**응답**:
```json
{
  "success": true,
  "message": "Emotion set to happy",
  "emotion": "happy"
}
```

## 지원 감정 타입

- `hello`: 인사
- `basic`: 기본 상태
- `angry`: 화남
- `bored`: 지루함
- `fun`: 재미있음
- `happy`: 행복함
- `interest`: 관심
- `sad`: 슬픔

## 사용 예시

### cURL

```bash
# 행복한 감정 표현
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "happy"}'

# 인사 감정 표현
curl -X POST http://localhost:8004/api/emotion/set \
  -H "Content-Type: application/json" \
  -d '{"emotion": "hello"}'
```

### Python

```python
import requests

url = "http://localhost:8004/api/emotion/set"
data = {"emotion": "happy"}

response = requests.post(url, json=data)
print(response.json())
```

### JavaScript

```javascript
fetch('http://localhost:8004/api/emotion/set', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ emotion: 'happy' })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 에러 처리

### 서비스 사용 불가능

```json
{
  "detail": "감정 표현 서비스가 사용 불가능합니다"
}
```

**HTTP 상태 코드**: 503

### 잘못된 감정 타입

```json
{
  "detail": "Unsupported emotion: invalid. Supported: hello, basic, angry, bored, fun, happy, interest, sad"
}
```

**HTTP 상태 코드**: 422 (Validation Error)

### 서비스 호출 실패

```json
{
  "detail": "ROS2 서비스 'emotion_controller/set_emotion'를 사용할 수 없습니다"
}
```

**HTTP 상태 코드**: 500

## Health Check

감정 표현 서비스의 상태는 `/health` 엔드포인트에서 확인할 수 있습니다.

```bash
curl http://localhost:8004/health
```

**응답 예시**:
```json
{
  "status": "healthy",
  "services": {
    "ros2": true,
    "emotion": true,
    "iot_data_server": true
  },
  "timestamp": "2025-11-23T10:30:00"
}
```

## 설정

환경 변수를 통해 감정 표현 서비스 설정을 변경할 수 있습니다.

```bash
# 서비스 이름 (기본값: emotion_controller/set_emotion)
ROS2_EMOTION_SERVICE_NAME=emotion_controller/set_emotion

# 서비스 타임아웃 (기본값: 3.0초)
ROS2_EMOTION_SERVICE_TIMEOUT=3.0
```

## 통신 구조

```
[FastAPI Server]
    |
    | HTTP POST /api/emotion/set
    v
[EmotionClient]
    |
    | ROS2 Service Call
    v
[emotion_controller_server]
    |
    | ROS2 Service Call (원격)
    v
[pinky_emotion] (ROS2/pinky_pro)
    |
    | LCD 제어
    v
[LCD Display]
```

## 참고

- `pinky_emotion` 패키지는 `ROS2/pinky_pro` 프로젝트에 있습니다.
- 감정 표현은 GIF 파일을 LCD에 표시하는 방식으로 동작합니다.
- 각 감정 타입에 해당하는 GIF 파일이 `pinky_emotion` 패키지에 포함되어 있습니다.

