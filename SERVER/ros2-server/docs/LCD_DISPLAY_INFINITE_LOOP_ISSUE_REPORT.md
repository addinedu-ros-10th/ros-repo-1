# LCD Display 무한 루프 문제 분석 및 해결 방안

**작성일**: 2025-01-22  
**문제**: SetDisplay 서비스 호출 시 무한 루프 발생

---

## 문제 현상

### 로그 분석

```
[INFO] [1763832957.882012021] [lcd_controller_server]: SetDisplay service call sent (async)
[INFO] [1763832957.882679387] [lcd_controller_server]: SetDisplay service call sent (async)
[INFO] [1763832957.883317270] [lcd_controller_server]: SetDisplay service call sent (async)
...
```

- `SetDisplay service call sent (async)` 메시지가 약 **0.5ms 간격**으로 무한 반복
- 서비스 호출이 1회성으로 완료되어야 하는데 계속 반복됨
- 두 메시지(기본 형식, 상세 형식)가 번갈아 표시됨

---

## 원인 분석

### 1. 문제의 핵심: 자기 자신의 서비스 호출

**`lcd_controller_server.py` 코드 분석**:

```python
# Line 109-112: 서비스 클라이언트 생성
self.set_display_client = self.create_client(
    SetDisplay,
    'lcd_controller/set_display'  # ⚠️ 자기 자신의 서비스 이름!
)

# Line 143-147: 서비스 서버 생성
self.set_display_srv = self.create_service(
    SetDisplay,
    'lcd_controller/set_display',  # ⚠️ 같은 이름!
    self.set_display_callback
)

# Line 168-195: 서비스 콜백
def set_display_callback(self, request, response):
    if self.set_display_client.wait_for_service(timeout_sec=0.5):
        # ⚠️ 자기 자신의 서비스를 호출!
        self.set_display_client.call_async(request)
```

### 2. 무한 루프 발생 메커니즘

```
1. 외부에서 서비스 호출
   ros2 service call /lcd_controller/set_display ...

2. lcd_controller_server의 set_display_callback() 실행
   ↓
3. set_display_callback 내부에서
   self.set_display_client.call_async(request) 호출
   ↓
4. 자기 자신의 서비스 'lcd_controller/set_display' 호출
   ↓
5. 다시 set_display_callback() 실행
   ↓
6. 무한 반복... 🔄
```

### 3. 왜 두 메시지가 번갈아 표시되는가?

- 기본 형식과 상세 형식 두 개의 서비스 호출이 있었을 가능성
- 각 호출이 무한 루프를 일으키면서 번갈아 실행됨

---

## 해결 방안

### 방안 1: 서비스 클라이언트 제거, 토픽만 사용 (권장) ⭐

**이유**:
- `pinky_lcd_display` 패키지는 이미 `/lcd/status` 토픽을 구독하고 있음
- 서비스 콜백 내부에서 다른 서비스를 호출하는 것은 복잡하고 위험함
- 토픽 발행은 비동기적이고 안전함

**구현**:
```python
def set_display_callback(self, request, response):
    """
    SetDisplay 서비스 콜백
    토픽을 통해 직접 LCD에 표시 내용 전달
    """
    try:
        # 토픽으로 직접 발행 (서비스 호출 제거)
        self._fallback_to_topic_set_display(request, response)
    except Exception as e:
        response.success = False
        response.message = f"Error: {str(e)}"
        self.get_logger().error(f"Failed to set display: {e}")
    
    return response
```

**장점**:
- ✅ 무한 루프 완전 제거
- ✅ 간단하고 안전한 구조
- ✅ 기존 토픽 기반 구조와 일치
- ✅ 성능 향상 (서비스 호출 오버헤드 제거)

### 방안 2: 서비스 이름 분리

**구현**:
```python
# 서비스 클라이언트는 다른 이름의 서비스를 호출
self.set_display_client = self.create_client(
    SetDisplay,
    'pinky_lcd_display/set_display'  # 다른 이름 사용
)

# 서비스 서버는 기존 이름 유지
self.set_display_srv = self.create_service(
    SetDisplay,
    'lcd_controller/set_display',  # 기존 이름 유지
    self.set_display_callback
)
```

**단점**:
- ⚠️ `pinky_lcd_display` 패키지도 `'lcd_controller/set_display'`를 사용 중
- ⚠️ 서비스 이름 충돌 가능성
- ⚠️ 구조가 복잡해짐

### 방안 3: 서비스 호출 체크 추가

**구현**:
```python
def __init__(self):
    # ...
    self._processing_request = False  # 플래그 추가

def set_display_callback(self, request, response):
    # 무한 루프 방지
    if self._processing_request:
        response.success = False
        response.message = "Request already processing"
        return response
    
    self._processing_request = True
    try:
        # 토픽으로 직접 발행
        self._fallback_to_topic_set_display(request, response)
    finally:
        self._processing_request = False
    
    return response
```

**단점**:
- ⚠️ 근본적인 해결책이 아님
- ⚠️ 동시 요청 처리 불가능

---

## 권장 해결책: 방안 1 (토픽만 사용)

### 수정 사항

1. **서비스 클라이언트 제거 또는 사용 안 함**
   - `set_display_callback`에서 서비스 클라이언트 호출 제거
   - 항상 토픽으로 직접 발행

2. **코드 수정**:

```python
def set_display_callback(self, request, response):
    """
    SetDisplay 서비스 콜백
    LCD에 표시할 내용을 설정합니다.
    
    토픽을 통해 직접 전송하여 무한 루프 방지
    """
    try:
        # 토픽으로 직접 발행 (서비스 호출 제거)
        self._fallback_to_topic_set_display(request, response)
    except Exception as e:
        response.success = False
        response.message = f"Error: {str(e)}"
        self.get_logger().error(f"Failed to set display: {e}")
    
    return response
```

3. **동일한 수정을 `clear_display_callback`에도 적용**

---

## 테스트 방법

### 수정 전 테스트 (문제 재현)

```bash
# 터미널 1: 서버 실행
ros2 run pinky_lcd_display_controller lcd_controller_server

# 터미널 2: 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1'], show_timestamp: true}"
```

**예상 결과**: 무한 루프 발생

### 수정 후 테스트

```bash
# 터미널 1: 서버 실행
ros2 run pinky_lcd_display_controller lcd_controller_server

# 터미널 2: 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1'], show_timestamp: true}"
```

**예상 결과**:
- ✅ 서비스 호출 1회만 실행
- ✅ 로그에 "Display updated via topic" 메시지 1회만 출력
- ✅ LCD에 정상적으로 표시

---

## 추가 고려사항

### 1. 서비스 클라이언트는 유지하되 사용 안 함

서비스 클라이언트를 완전히 제거하지 않고, 향후 필요할 때를 대비해 유지할 수 있습니다:

```python
# 서비스 클라이언트는 유지 (향후 사용 가능)
# 하지만 set_display_callback에서는 사용 안 함
```

### 2. 다른 서비스 콜백도 확인

`set_style_callback`도 동일한 문제가 있을 수 있으므로 확인 필요:

```python
def set_style_callback(self, request, response):
    # 현재는 폴링 루프를 사용하고 있어 문제 없음
    # 하지만 동일한 패턴이면 수정 필요
```

---

## 결론

**문제**: `lcd_controller_server`가 자기 자신의 서비스를 호출하여 무한 루프 발생

**해결**: 서비스 콜백 내부에서 서비스 클라이언트 호출을 제거하고, 토픽으로 직접 발행

**장점**:
- ✅ 무한 루프 완전 제거
- ✅ 간단하고 안전한 구조
- ✅ 성능 향상

**다음 단계**: 코드 수정 및 테스트

