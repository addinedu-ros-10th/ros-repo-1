# Emotion Display 통신 구조 분석 및 개선 방안 리포트

## 실행 요약

### 현재 상황
- ✅ Emotion display는 정상 작동
- ❌ 타임아웃 에러 메시지 발생
- ❌ 애니메이션이 무한 반복되어 다른 디스플레이와 충돌
- ❌ 중지/일시중지 기능 없음

### 핵심 문제
1. **타임아웃 에러**: ROS_DOMAIN_ID 불일치 또는 네트워크 문제
2. **무한 반복**: 애니메이션이 끝나지 않아 다른 디스플레이와 충돌
3. **제어 부재**: 재생, 중지, 일시중지 기능 없음

## 현재 구조 상세 분석

### 1. 통신 흐름

```
[HTTP Client]
    |
    | POST /api/emotion/set
    v
[FastAPI Server]
    |
    | async def set_emotion()
    v
[EmotionClient.set_emotion()]
    |
    | ROS2 Service Call (동기, 타임아웃 3초)
    v
[emotion_controller_server]
    |
    | ROS2 Service Call (동기, 타임아웃 5초)
    v
[pinky_emotion.set_emotion_callback()]
    |
    | 즉시 응답 반환
    v
[응답 전달]
    |
    | (백그라운드)
    v
[timer_callback()] - 0.1초마다 실행, 무한 반복
    |
    | DisplayImage Service Call
    v
[lcd_controller/display_image]
    |
    | LCD 표시
    v
[LCD Display]
```

### 2. 코드 분석

#### pinky_emotion.set_emotion_callback()

```python
def set_emotion_callback(self, request, response):
    emo = request.emotion
    self.get_logger().info(f"Request to set emotion to '{emo}'")
    
    if emo in self.emotion_cache:
        with self.gif_lock:
            self.gif_frames = self.emotion_cache[emo]  # GIF 프레임 설정
            self.current_frame_index = 0
        response.response = f"Emotion set to {emo}"  # 즉시 응답
    else:
        response.response = "Wrong command or emotion not cached"
    
    return response  # 즉시 반환 (애니메이션 시작 확인만)
```

**특징**:
- ✅ 즉시 응답 반환 (1회성 응답 가능)
- ✅ 애니메이션 시작 확인만 반환
- ❌ 애니메이션 완료 시점은 알 수 없음

#### pinky_emotion.timer_callback()

```python
def timer_callback(self):
    # 0.1초마다 실행
    with self.gif_lock:
        if not self.gif_frames:
            return
        
        frame_to_show = self.gif_frames[self.current_frame_index]
        # DisplayImage 서비스 호출 (비동기)
        future = self.display_image_client.call_async(request)
        
        # 프레임 인덱스 증가 (모듈로 연산하여 무한 반복)
        self.current_frame_index = (self.current_frame_index + 1) % len(self.gif_frames)
```

**특징**:
- ✅ 0.1초마다 실행 (10 FPS)
- ❌ 무한 반복 (`% len(self.gif_frames)`)
- ❌ 중지 메커니즘 없음
- ❌ 다른 디스플레이와 충돌

### 3. 문제점 상세

#### 문제 1: 타임아웃 에러

**증상**:
```
[INFO] [emotion_controller_server]: Request to set emotion to 'hello'
[ERROR] [emotion_controller_server]: Service call timeout
```

**원인 분석**:
1. `pinky_emotion`은 즉시 응답을 반환함
2. 타임아웃이 발생한다면:
   - ROS_DOMAIN_ID 불일치 (가장 가능성 높음)
   - 네트워크 지연
   - 서비스 클라이언트 문제

**해결 방법**:
- ROS_DOMAIN_ID 확인 및 통일
- 서비스 직접 호출 테스트
- 타임아웃 시간 증가 (이미 5초로 증가)

#### 문제 2: 무한 반복 애니메이션

**증상**:
- 애니메이션이 끝나지 않음
- 다른 디스플레이 요청이 와도 계속 재생
- Clear API로 화면을 지워도 다시 표시

**원인**:
- `timer_callback`이 계속 실행됨
- `current_frame_index = (current_frame_index + 1) % len(self.gif_frames)`: 모듈로 연산하여 무한 반복
- 중지 메커니즘 없음

**영향**:
- 다른 디스플레이와 충돌
- 사용자가 제어할 수 없음
- 리소스 낭비

#### 문제 3: HTTP 요청-응답 모델과의 불일치

**현재 구조**:
- HTTP 요청 → 즉시 응답 (애니메이션 시작 확인)
- 애니메이션은 백그라운드에서 계속 실행

**문제**:
- 애니메이션 완료 시점을 알 수 없음
- 중지/일시중지 기능 없음
- 다른 디스플레이와 충돌

**고려사항**:
- HTTP는 1회성 요청-응답 모델
- 애니메이션은 지속적 실행
- 두 모델이 맞지 않음

## 해결 방안

### 방안 1: 즉시 해결 - 타임아웃 문제

#### 1.1 ROS_DOMAIN_ID 확인 및 통일

```bash
# 모든 터미널에서
export ROS_DOMAIN_ID=13

# 확인
echo $ROS_DOMAIN_ID
```

#### 1.2 서비스 직접 호출 테스트

```bash
# 서버 측에서
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'

# 즉시 응답이 오는지 확인
```

#### 1.3 emotion_controller_server 재시작

```bash
pkill -f emotion_controller_server
ros2 run pinky_emotion_controller emotion_controller_server
```

### 방안 2: 애니메이션 제어 기능 추가

#### 2.1 서비스 인터페이스 확장

**새로운 서비스 추가** (`pinky_interfaces/srv/`):
- `StopEmotion.srv`: 애니메이션 중지
- `PauseEmotion.srv`: 애니메이션 일시중지
- `ResumeEmotion.srv`: 애니메이션 재개

**기존 서비스 수정**:
- `Emotion.srv`에 재생 옵션 추가:
  ```srv
  string emotion
  int32 repeat_count  # -1: 무한, 0 이상: 재생 횟수
  bool play_once      # true: 1회만 재생
  ---
  string response
  ```

#### 2.2 상태 관리 추가

```python
class PinkyEmotion(Node):
    def __init__(self):
        self.animation_state = "stopped"  # stopped, playing, paused
        self.repeat_count = -1  # -1: 무한, 0 이상: 재생 횟수
        self.current_repeat = 0
        self.is_paused = False
        self.should_stop = False
```

#### 2.3 타이머 콜백 수정

```python
def timer_callback(self):
    with self.gif_lock:
        # 중지 확인
        if self.should_stop or self.animation_state == "stopped":
            self.gif_frames = []
            self.current_frame_index = 0
            return
        
        # 일시중지 확인
        if self.is_paused or self.animation_state == "paused":
            return
        
        # 재생 횟수 확인
        if self.repeat_count > 0 and self.current_repeat >= self.repeat_count:
            self.animation_state = "stopped"
            self.gif_frames = []
            return
        
        # 프레임 표시
        if not self.gif_frames:
            return
        
        frame_to_show = self.gif_frames[self.current_frame_index]
        # ... DisplayImage 서비스 호출 ...
        
        # 프레임 인덱스 증가
        self.current_frame_index += 1
        
        # 한 사이클 완료 확인
        if self.current_frame_index >= len(self.gif_frames):
            self.current_frame_index = 0
            if self.repeat_count > 0:
                self.current_repeat += 1
```

### 방안 3: 우선순위 기반 디스플레이 관리

#### 3.1 우선순위 시스템

```python
class DisplayPriority:
    HIGH = 3      # 안내 메시지, 알림
    MEDIUM = 2    # 감정 표현
    LOW = 1       # 기본 상태

class PinkyEmotion(Node):
    def __init__(self):
        self.current_priority = DisplayPriority.LOW
        self.paused_for_priority = False
    
    def pause_for_priority_display(self, priority):
        if priority > self.current_priority:
            self.paused_for_priority = True
            self.is_paused = True
    
    def resume_after_priority_display(self):
        if self.paused_for_priority:
            self.paused_for_priority = False
            self.is_paused = False
```

### 방안 4: 비동기 처리 개선

#### 4.1 현재 구조

```
[HTTP Request] 
    → [FastAPI] (동기 대기)
    → [EmotionClient] (동기 대기, 타임아웃 3초)
    → [emotion_controller_server] (동기 대기, 타임아웃 5초)
    → [pinky_emotion] (즉시 응답)
```

#### 4.2 개선된 구조

```
[HTTP Request] 
    → [FastAPI] (비동기, 즉시 응답)
    → [Background Task] (백그라운드에서 서비스 호출)
    → [pinky_emotion] (즉시 응답)
```

**구현**:
```python
@app.post("/api/emotion/set")
async def set_emotion(request: EmotionRequest):
    # 즉시 응답 반환
    response = EmotionResponse(
        success=True,
        message="Emotion request accepted",
        emotion=request.emotion
    )
    
    # 백그라운드에서 서비스 호출
    background_tasks.add_task(
        emotion_client.set_emotion_async,
        request.emotion
    )
    
    return response
```

## 권장 구현 순서

### 1단계: 타임아웃 문제 해결 (즉시)

1. ROS_DOMAIN_ID 확인 및 통일
2. 서비스 직접 호출 테스트
3. emotion_controller_server 재시작

### 2단계: 애니메이션 중지 기능 (단기)

1. `StopEmotion` 서비스 추가
2. API 엔드포인트 추가: `POST /api/emotion/stop`
3. 상태 관리 추가

### 3단계: 1회 재생 옵션 (단기)

1. `Emotion.srv`에 재생 옵션 추가
2. 재생 횟수 관리 로직 추가
3. API에 재생 옵션 추가

### 4단계: 우선순위 관리 (중기)

1. 우선순위 시스템 구현
2. 자동 일시중지/재개
3. 디스플레이 충돌 해결

## HTTP 요청-응답 모델 적합성 평가

### 현재 구조 평가

**적합성**: ⚠️ 부분적

**장점**:
- ✅ 즉시 응답 가능 (애니메이션 시작 확인)
- ✅ HTTP 요청-응답 모델 유지
- ✅ 간단한 구조

**단점**:
- ❌ 애니메이션 완료 시점을 알 수 없음
- ❌ 중지/일시중지 기능 없음
- ❌ 다른 디스플레이와 충돌

### 개선된 구조 평가

**방안 A: 즉시 응답 + 백그라운드 실행** (권장)
- ✅ HTTP 요청-응답 모델 유지
- ✅ 빠른 응답 시간
- ✅ 애니메이션은 백그라운드에서 실행
- ⚠️ 완료 시점을 알 수 없음 (WebSocket 또는 폴링 필요)

**방안 B: 액션 기반 제어**
- ✅ 진행 상황 피드백 가능
- ✅ 취소 기능 제공
- ❌ HTTP 요청-응답 모델과 다름
- ❌ 구현 복잡도 증가

**방안 C: 이벤트 기반 통신**
- ✅ 실시간 상태 업데이트
- ✅ 유연한 제어
- ❌ HTTP 요청-응답 모델과 다름
- ❌ WebSocket 또는 SSE 필요

## 최종 권장 사항

### 즉시 적용 (타임아웃 해결)

1. **ROS_DOMAIN_ID 확인 및 통일**
   - 모든 터미널에서 `export ROS_DOMAIN_ID=13`
   - 서비스 직접 호출 테스트

2. **에러 처리 개선**
   - 더 상세한 로그
   - 재시도 로직

### 단기 개선 (1-2주)

1. **애니메이션 중지 기능**
   - `POST /api/emotion/stop` 추가
   - `POST /api/emotion/pause` 추가
   - `POST /api/emotion/resume` 추가

2. **1회 재생 옵션**
   - API에 `play_once` 옵션 추가
   - 재생 횟수 관리

### 중기 개선 (1-2개월)

1. **우선순위 기반 디스플레이 관리**
   - 디스플레이 우선순위 시스템
   - 자동 일시중지/재개

2. **상태 모니터링**
   - WebSocket 또는 SSE로 상태 전송
   - 실시간 애니메이션 상태 확인

## 참고

- 현재 구조는 HTTP 요청-응답 모델과 부분적으로만 맞음
- 애니메이션은 백그라운드에서 계속 실행됨
- 제어 기능이 없어 다른 디스플레이와 충돌함
- 개선이 필요하지만, 현재 구조에서도 기본 동작은 함

