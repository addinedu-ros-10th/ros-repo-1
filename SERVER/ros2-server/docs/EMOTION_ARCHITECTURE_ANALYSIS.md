# Emotion Display 아키텍처 분석 및 개선 방안

## 현재 구조 분석

### 1. 동작 방식

#### emotion_server_rfred.py 구조

```python
class PinkyEmotion(Node):
    def __init__(self):
        # 서비스 서버 생성
        self.emotion_service = self.create_service(Emotion, 'set_emotion', self.set_emotion_callback)
        
        # 타이머 생성 (0.1초마다 실행)
        self.animation_timer = self.create_timer(0.1, self.timer_callback)
        
        # GIF 프레임 캐시
        self.emotion_cache = {}
        self.gif_frames = []
        self.current_frame_index = 0
    
    def set_emotion_callback(self, request, response):
        # 요청을 받으면 즉시 응답 반환
        # GIF 프레임만 변경
        response.response = f"Emotion set to {emo}"
        return response  # 즉시 반환
    
    def timer_callback(self):
        # 0.1초마다 실행
        # GIF 프레임을 계속 표시 (무한 반복)
        self.current_frame_index = (self.current_frame_index + 1) % len(self.gif_frames)
```

### 2. 문제점 분석

#### 문제 1: 무한 반복 애니메이션

**현재 동작**:
- `timer_callback`이 0.1초마다 실행
- `current_frame_index = (current_frame_index + 1) % len(self.gif_frames)`: 모듈로 연산하여 무한 반복
- 애니메이션이 끝나지 않음

**영향**:
- 다른 디스플레이 요청이 와도 계속 재생됨
- Clear API로 화면을 지워도 다시 표시됨
- 안내 메시지가 표시되어도 이어서 재생됨

#### 문제 2: 1회성 응답 vs 지속적 실행

**현재 구조**:
- `set_emotion_callback`: 즉시 응답 반환 (1회성)
- `timer_callback`: 계속 실행 (지속적)

**문제**:
- 서비스 콜백은 즉시 응답하지만, 실제 애니메이션은 계속 실행됨
- HTTP 요청-응답 모델과 맞지 않음
- 애니메이션이 완료되었는지 알 수 없음

#### 문제 3: 제어 기능 부재

**현재 기능**:
- ✅ 재생: `set_emotion` 호출
- ❌ 중지: 없음
- ❌ 일시중지: 없음
- ❌ 1회 재생: 없음

#### 문제 4: 타임아웃 발생 원인

**가능한 원인**:
1. **ROS_DOMAIN_ID 불일치**: 서버와 로봇이 다른 도메인
2. **서비스 응답 지연**: 애니메이션 시작 후 응답이 지연될 수 있음
3. **네트워크 지연**: 원격 호출 시 네트워크 지연

## 해결 방안

### 방안 1: 즉시 응답 + 비동기 처리 (권장)

**구조**:
```
[HTTP Request] 
    → [FastAPI] 
    → [EmotionClient] 
    → [emotion_controller_server] 
    → [pinky_emotion] 
        → 즉시 응답 반환 (애니메이션 시작 확인)
        → 타이머로 애니메이션 재생 (백그라운드)
```

**장점**:
- HTTP 요청-응답 모델 유지
- 빠른 응답 시간
- 애니메이션은 백그라운드에서 실행

**단점**:
- 애니메이션 완료 시점을 알 수 없음
- 제어 기능 추가 필요

### 방안 2: 애니메이션 제어 기능 추가

#### 2.1 서비스 인터페이스 확장

**새로운 서비스 추가**:
- `StopEmotion`: 애니메이션 중지
- `PauseEmotion`: 애니메이션 일시중지
- `ResumeEmotion`: 애니메이션 재개

**기존 서비스 수정**:
- `SetEmotion`: 재생 횟수 옵션 추가 (1회, 무한 반복)

#### 2.2 상태 관리

```python
class PinkyEmotion(Node):
    def __init__(self):
        self.animation_state = "stopped"  # stopped, playing, paused
        self.repeat_count = -1  # -1: 무한, 0 이상: 재생 횟수
        self.current_repeat = 0
        self.is_paused = False
```

### 방안 3: 우선순위 기반 디스플레이 관리

**구조**:
- 높은 우선순위: 안내 메시지, 알림
- 중간 우선순위: 감정 표현
- 낮은 우선순위: 기본 상태

**동작**:
- 높은 우선순위 요청이 오면 현재 애니메이션 일시중지
- 높은 우선순위 표시 완료 후 이전 애니메이션 재개

### 방안 4: 1회 재생 옵션

**구현**:
```python
def set_emotion_callback(self, request, response):
    emo = request.emotion
    repeat = request.repeat  # -1: 무한, 0 이상: 재생 횟수
    
    if repeat == 1:
        # 1회만 재생
        self.repeat_count = 1
        self.current_repeat = 0
    else:
        # 무한 반복
        self.repeat_count = -1
```

## 즉시 해결: 타임아웃 문제

### 원인 분석

1. **ROS_DOMAIN_ID 불일치** (가장 가능성 높음)
2. **서비스 응답 지연**: 애니메이션 시작 후 응답 지연
3. **네트워크 문제**: 원격 호출 시 네트워크 지연

### 해결 방법

#### 1. ROS_DOMAIN_ID 확인

```bash
# 서버 측
echo $ROS_DOMAIN_ID

# 로봇 측
echo $ROS_DOMAIN_ID

# 둘 다 13이어야 함
```

#### 2. 서비스 직접 호출 테스트

```bash
# 서버 측에서 직접 호출
ros2 service call /set_emotion pinky_interfaces/srv/Emotion '{emotion: "hello"}'

# 응답이 즉시 오는지 확인
```

#### 3. 비동기 처리 개선

현재 `emotion_controller_server`는 동기적으로 응답을 기다립니다. 
`pinky_emotion`은 즉시 응답을 반환하므로 타임아웃이 발생하지 않아야 합니다.

**확인 사항**:
- `pinky_emotion`의 `set_emotion_callback`이 즉시 응답하는지
- 네트워크 지연이 있는지
- ROS_DOMAIN_ID가 일치하는지

## 권장 개선 방안

### 단기 개선 (즉시 적용 가능)

1. **애니메이션 중지 기능 추가**
   ```python
   def stop_emotion_callback(self, request, response):
       with self.gif_lock:
           self.gif_frames = []
           self.current_frame_index = 0
       response.response = "Emotion stopped"
       return response
   ```

2. **1회 재생 옵션 추가**
   ```python
   def set_emotion_callback(self, request, response):
       emo = request.emotion
       repeat_once = request.repeat_once  # 새 필드
       
       if repeat_once:
           self.repeat_count = 1
       else:
           self.repeat_count = -1  # 무한 반복
   ```

3. **우선순위 기반 일시중지**
   ```python
   def pause_for_priority_display(self):
       self.is_paused = True
       # 현재 프레임 저장
       self.paused_frame_index = self.current_frame_index
   ```

### 중기 개선 (구조 개선)

1. **서비스 인터페이스 확장**
   - `StopEmotion` 서비스 추가
   - `PauseEmotion` 서비스 추가
   - `SetEmotion`에 재생 옵션 추가

2. **상태 관리 개선**
   - 애니메이션 상태 추적
   - 재생 횟수 관리
   - 우선순위 관리

### 장기 개선 (아키텍처 개선)

1. **액션 기반 제어**
   - ROS2 Action 사용
   - 진행 상황 피드백
   - 취소 기능

2. **이벤트 기반 통신**
   - 토픽으로 상태 발행
   - 이벤트 구독으로 제어

## 구현 우선순위

### 1순위: 타임아웃 문제 해결
- ROS_DOMAIN_ID 확인 및 통일
- 서비스 호출 방식 개선
- 에러 처리 강화

### 2순위: 애니메이션 중지 기능
- `stop_emotion` 서비스 추가
- API 엔드포인트 추가

### 3순위: 1회 재생 옵션
- 서비스 인터페이스 확장
- 재생 횟수 관리

### 4순위: 우선순위 관리
- 디스플레이 우선순위 시스템
- 자동 일시중지/재개

## 참고

- 현재 구조는 HTTP 요청-응답 모델과 맞지 않음
- 애니메이션은 백그라운드에서 계속 실행됨
- 제어 기능이 없어 다른 디스플레이와 충돌함
- 개선이 필요하지만, 현재 구조에서도 동작은 함

