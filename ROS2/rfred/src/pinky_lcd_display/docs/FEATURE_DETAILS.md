# pinky_lcd_display 패키지 기능 상세 설명

## 개요

이 문서는 `pinky_lcd_display` 패키지에 구현될 각 기능에 대한 상세한 설명을 제공합니다. `pinky_lcd_display_controller`가 서비스/액션 클라이언트로 동작하고, `pinky_lcd_display`가 서비스/액션 서버로 동작하는 구조를 기반으로 합니다.

## 아키텍처 개요

```
[pinky_lcd_display_controller] (클라이언트)
    |
    | 서비스/액션 호출
    v
[pinky_lcd_display] (서버)
    |
    | 하드웨어 제어
    v
[LCD 디스플레이]
```

**통신 방식**:
- 서비스: 동기식 요청/응답
- 액션: 비동기식 요청/피드백/응답
- 토픽: 상태 및 이벤트 발행 (단방향)

---

## 1. 스타일 동적 적용 (SetStyle 서비스)

### 1.1 목적

LCD 표시 스타일(색상, 폰트 크기, 폰트 경로)을 런타임에 동적으로 변경할 수 있도록 합니다. 현재는 스타일이 초기화 시에만 설정되지만, 서비스를 통해 언제든지 변경 가능하도록 합니다.

### 1.2 구현 방법

**서비스 인터페이스**: `pinky_lcd_display_interfaces/srv/SetStyle.srv`

**요청 파라미터**:
- `bg_color_r/g/b`: 배경 색상 (RGB, 0-255)
- `title_color_r/g/b`: 타이틀 색상 (RGB, 0-255)
- `body_color_r/g/b`: 본문 색상 (RGB, 0-255)
- `timestamp_color_r/g/b`: 타임스탬프 색상 (RGB, 0-255)
- `title_font_size`: 타이틀 폰트 크기 (픽셀)
- `body_font_size`: 본문 폰트 크기 (픽셀)
- `font_path`: 폰트 파일 경로 (빈 문자열이면 기본값 사용)

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 서비스 서버 생성 및 요청 처리
- `pinky_lcd_display/lcd_manager.py`: 스타일 저장 및 적용

**기술적 세부사항**:

1. **스타일 저장소**:
   ```python
   class LCDDisplayManager:
       def __init__(self):
           # 현재 스타일 저장
           self.current_style = {
               'bg_color': (0, 0, 0),
               'title_color': (0, 255, 0),
               'body_color': (255, 255, 255),
               'timestamp_color': (100, 100, 255),
               'title_font_size': 20,
               'body_font_size': 18,
               'font_path': None  # None이면 자동 탐색
           }
   ```

2. **폰트 재로드**:
   - `font_path`가 변경되면 폰트 파일을 다시 로드
   - 폰트 로드 실패 시 기본 폰트로 폴백
   - 한글 폰트 자동 탐색 로직 유지

3. **렌더링 적용**:
   - `render_status_frame()` 메서드에서 저장된 스타일 사용
   - 즉시 적용 (다음 렌더링 시 반영)

**구현 복잡도**: 중간
- 기존 코드 수정 필요
- 폰트 재로드 로직 추가
- 에러 처리 필요

**의존성**: 없음 (기존 기능 확장)

**사용 시나리오**:
- 다크 모드/라이트 모드 전환
- 폰트 크기 조절 (가독성 향상)
- 테마 변경

**예상 구현 시간**: 2-3시간

---

## 2. 레이아웃 제어 (SetLayout 서비스)

### 2.1 목적

텍스트 정렬, 여백, 라인 간격 등을 제어하여 다양한 레이아웃을 지원합니다. 현재는 고정된 레이아웃(왼쪽 정렬, 고정 여백)만 지원하지만, 동적으로 변경 가능하도록 합니다.

### 2.2 구현 방법

**서비스 인터페이스**: `pinky_lcd_display_interfaces/srv/SetLayout.srv`

**요청 파라미터**:
- `alignment`: 텍스트 정렬 (0: LEFT, 1: CENTER, 2: RIGHT)
- `layout_mode`: 레이아웃 모드 (0: SINGLE_LINE, 1: MULTI_LINE, 2: GRID)
- `margin_top/bottom/left/right`: 여백 (픽셀)
- `line_spacing`: 라인 간격 (픽셀)
- `grid_columns/rows`: 그리드 모드 시 열/행 수

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 서비스 서버 생성 및 요청 처리
- `pinky_lcd_display/lcd_manager.py`: 레이아웃 저장 및 텍스트 위치 계산

**기술적 세부사항**:

1. **레이아웃 저장소**:
   ```python
   class LCDDisplayManager:
       def __init__(self):
           self.current_layout = {
               'alignment': 0,  # LEFT
               'layout_mode': 1,  # MULTI_LINE
               'margin_top': 10,
               'margin_bottom': 10,
               'margin_left': 10,
               'margin_right': 10,
               'line_spacing': 24,
               'grid_columns': 1,
               'grid_rows': 1
           }
   ```

2. **텍스트 위치 계산**:
   - **LEFT 정렬**: `x = margin_left`
   - **CENTER 정렬**: 텍스트 너비 측정 후 중앙 계산
     ```python
     text_width = draw.textlength(text, font=self.font_title)
     x = (self.width - text_width) // 2
     ```
   - **RIGHT 정렬**: 텍스트 너비 측정 후 오른쪽 정렬
     ```python
     text_width = draw.textlength(text, font=self.font_title)
     x = self.width - margin_right - text_width
     ```

3. **그리드 모드**:
   - 화면을 그리드로 분할
   - 각 셀에 텍스트 배치
   - 셀 크기 계산: `cell_width = (width - margin_left - margin_right) / grid_columns`

**구현 복잡도**: 높음
- 텍스트 위치 계산 로직 복잡
- 그리드 모드 구현 필요
- 텍스트 너비 측정 필요 (PIL의 `textlength` 사용)

**의존성**: PIL/Pillow (텍스트 너비 측정)

**사용 시나리오**:
- 가운데 정렬 제목
- 오른쪽 정렬 숫자/시간
- 그리드 레이아웃 (표 형태 데이터)

**예상 구현 시간**: 4-5시간

---

## 3. 애니메이션 효과 (SetDisplayAction)

### 3.1 목적

LCD 표시 시 애니메이션 효과(FADE_IN, SLIDE)를 제공하여 시각적 피드백을 향상시킵니다. 액션 인터페이스를 사용하여 시간 제한 표시 및 진행 상태 피드백도 제공합니다.

### 3.2 구현 방법

**액션 인터페이스**: `pinky_lcd_display_interfaces/action/SetDisplay.action`

**Goal 파라미터**:
- `title`, `lines`, `show_timestamp`: 기본 표시 내용
- `duration_ms`: 표시 지속 시간 (0이면 무한)
- `animation_type`: 애니메이션 타입 (0: NONE, 1: FADE_IN, 2: SLIDE)

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 액션 서버 생성 및 Goal 처리
- `pinky_lcd_display/lcd_manager.py`: 애니메이션 렌더링 로직

**기술적 세부사항**:

1. **FADE_IN 효과**:
   - 알파값을 0에서 255로 점진적으로 증가
   - 중간 프레임 생성 (예: 10프레임, 각 25ms 간격)
   ```python
   def render_fade_in(self, base_image, frame_count, total_frames):
       alpha = int(255 * (frame_count / total_frames))
       # PIL의 Image.blend 사용
       fade_image = Image.blend(
           Image.new('RGB', base_image.size, (0, 0, 0)),
           base_image,
           alpha / 255.0
       )
       return fade_image
   ```

2. **SLIDE 효과**:
   - 이미지를 왼쪽에서 오른쪽으로 슬라이드
   - 중간 프레임 생성 (위치를 점진적으로 이동)
   ```python
   def render_slide(self, base_image, frame_count, total_frames):
       slide_distance = base_image.width
       current_x = int(slide_distance * (1 - frame_count / total_frames))
       # 새 이미지에 base_image를 current_x 위치에 배치
       slide_image = Image.new('RGB', base_image.size, (0, 0, 0))
       slide_image.paste(base_image, (current_x, 0))
       return slide_image
   ```

3. **타이머 기반 피드백**:
   - 액션 실행 중 주기적으로 피드백 발행 (예: 100ms마다)
   - 경과 시간 및 진행률 계산
   ```python
   elapsed_ms = (current_time - start_time) * 1000
   progress_percent = int((elapsed_ms / duration_ms) * 100) if duration_ms > 0 else 0
   ```

4. **자동 전환**:
   - `duration_ms`가 0이 아니면 지정된 시간 후 자동으로 화면 지움
   - 타이머를 사용하여 시간 경과 감지

**구현 복잡도**: 높음
- 애니메이션 프레임 생성 로직 복잡
- 타이머 및 스레드 관리 필요
- 성능 최적화 필요 (프레임 생성 시간)

**의존성**: 
- PIL/Pillow (이미지 블렌딩)
- threading 또는 asyncio (타이머 관리)

**사용 시나리오**:
- 알림 메시지 (페이드 인 효과)
- 화면 전환 (슬라이드 효과)
- 시간 제한 표시 (5초 후 자동 사라짐)

**예상 구현 시간**: 5-6시간

---

## 4. 상태/이벤트 토픽 발행

### 4.1 목적

LCD의 현재 상태와 이벤트를 실시간으로 발행하여 다른 노드에서 모니터링할 수 있도록 합니다.

### 4.2 구현 방법

**토픽 인터페이스**:
- `/lcd_controller/status`: `pinky_lcd_display_interfaces/msg/LCDStatus`
- `/lcd_controller/events`: `pinky_lcd_display_interfaces/msg/LCDEvent`

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 토픽 Publisher 생성 및 발행

**기술적 세부사항**:

1. **상태 토픽 발행**:
   - 상태 변경 시 즉시 발행
   - 주기적 발행 (예: 1Hz) - 상태가 변경되지 않아도 주기적으로 발행
   ```python
   def __init__(self):
       self.status_pub = self.create_publisher(LCDStatus, '/lcd_controller/status', 10)
       # 1Hz 타이머
       self.status_timer = self.create_timer(1.0, self.publish_status)
   
   def publish_status(self):
       msg = LCDStatus()
       msg.is_active = self.lcd_manager.lcd is not None
       msg.current_title = self.current_title
       msg.current_lines = self.current_lines
       msg.show_timestamp = self.show_timestamp
       msg.last_update_time = self.get_clock().now().nanoseconds
       msg.display_mode = self.current_display_mode
       self.status_pub.publish(msg)
   ```

2. **이벤트 토픽 발행**:
   - 이벤트 발생 시 즉시 발행
   - 이벤트 타입: DISPLAY_STARTED, DISPLAY_ENDED, ERROR, CLEARED, PAGE_SWITCHED, ANIMATION_STARTED, ANIMATION_ENDED
   ```python
   def publish_event(self, event_type, message):
       msg = LCDEvent()
       msg.header.stamp = self.get_clock().now().to_msg()
       msg.event_type = event_type
       msg.timestamp = self.get_clock().now().nanoseconds
       msg.message = message
       self.event_pub.publish(msg)
   ```

3. **상태 추적**:
   - 현재 표시 중인 내용 저장
   - 표시 모드 추적 (NORMAL, SCROLL, ANIMATION)
   - 에러 상태 추적

**구현 복잡도**: 낮음-중간
- Publisher 생성 및 메시지 발행
- 상태 추적 로직 추가
- 타이머 관리

**의존성**: `pinky_lcd_display_interfaces` 패키지

**사용 시나리오**:
- LCD 상태 모니터링
- 에러 감지 및 알림
- 디버깅

**예상 구현 시간**: 2-3시간

---

## 5. 스크롤 텍스트 (ScrollTextAction)

### 5.1 목적

긴 텍스트를 스크롤하여 표시하여 화면 크기 제한을 극복합니다.

### 5.2 구현 방법

**액션 인터페이스**: `pinky_lcd_display_interfaces/action/ScrollText.action`

**Goal 파라미터**:
- `text`: 스크롤할 텍스트
- `scroll_speed_ms`: 스크롤 속도 (밀리초)
- `direction`: 스크롤 방향 (0: LEFT, 1: RIGHT, 2: UP, 3: DOWN)
- `repeat_count`: 반복 횟수 (0이면 무한)

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 액션 서버 생성 및 Goal 처리
- `pinky_lcd_display/lcd_manager.py`: 스크롤 렌더링 로직

**기술적 세부사항**:

1. **텍스트 너비 측정**:
   - 텍스트가 화면 너비보다 긴지 확인
   - 폰트를 사용하여 정확한 너비 측정
   ```python
   text_width = draw.textlength(text, font=self.font_body)
   if text_width <= self.width:
       # 스크롤 불필요
       return
   ```

2. **스크롤 애니메이션**:
   - 텍스트를 화면 밖에서 시작하여 화면 안으로 이동
   - LEFT 방향: 텍스트를 오른쪽에서 왼쪽으로 이동
   ```python
   def render_scroll_left(self, text, current_position, font):
       img, draw = self._new_canvas()
       # 텍스트를 current_position 위치에 그리기
       # current_position은 음수에서 시작하여 text_width까지 증가
       x = self.width - current_position
       draw.text((x, y), text, fill=self.current_style['body_color'], font=font)
       return img
   ```

3. **타이머 기반 업데이트**:
   - `scroll_speed_ms` 간격으로 화면 업데이트
   - 각 업데이트마다 `current_position` 증가
   - 피드백 발행 (현재 위치, 진행률)

4. **반복 처리**:
   - 텍스트가 완전히 화면 밖으로 나가면 한 사이클 완료
   - `repeat_count`만큼 반복
   - 무한 반복 (`repeat_count = 0`) 지원

**구현 복잡도**: 중간-높음
- 텍스트 위치 계산 복잡
- 타이머 및 스레드 관리
- 성능 최적화 (빠른 스크롤 시)

**의존성**: 
- PIL/Pillow (텍스트 너비 측정)
- threading 또는 asyncio (타이머 관리)

**사용 시나리오**:
- 긴 상태 메시지 표시
- 로그 메시지 스크롤
- 알림 메시지 (스크롤 효과)

**예상 구현 시간**: 4-5시간

---

## 6. 페이지 관리 (CreatePage, SwitchPage, ListPages, DeletePage 서비스)

### 6.1 목적

다중 페이지를 생성하고 관리하여 복잡한 UI를 구성할 수 있도록 합니다.

### 6.2 구현 방법

**서비스 인터페이스**:
- `pinky_lcd_display_interfaces/srv/CreatePage.srv`
- `pinky_lcd_display_interfaces/srv/SwitchPage.srv`
- `pinky_lcd_display_interfaces/srv/ListPages.srv`
- `pinky_lcd_display_interfaces/srv/DeletePage.srv`

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 서비스 서버 생성 및 요청 처리
- `pinky_lcd_display/lcd_manager.py`: 페이지 저장소 및 렌더링

**기술적 세부사항**:

1. **페이지 저장소**:
   ```python
   class LCDDisplayManager:
       def __init__(self):
           self.pages = {}  # {page_id: PageInfo}
           self.current_page_id = None
   
   class PageInfo:
       def __init__(self, page_id, title, lines, display_duration_ms, priority):
           self.page_id = page_id
           self.title = title
           self.lines = lines
           self.display_duration_ms = display_duration_ms
           self.priority = priority
   ```

2. **페이지 생성**:
   - `page_id`로 고유 식별
   - 중복 `page_id` 검사
   - 우선순위 저장 (자동 전환 시 사용)

3. **페이지 전환**:
   - 전환 효과 지원 (INSTANT, FADE, SLIDE_LEFT, SLIDE_RIGHT, SLIDE_UP, SLIDE_DOWN)
   - 전환 효과는 애니메이션 효과 재사용
   - 이전/현재 페이지 ID 추적

4. **자동 전환**:
   - `display_duration_ms`가 0이 아니면 지정된 시간 후 자동으로 다음 페이지로 전환
   - 우선순위 기반 페이지 선택
   - 타이머를 사용하여 시간 경과 감지

5. **페이지 목록 조회**:
   - 저장된 모든 페이지 ID 반환
   - 현재 표시 중인 페이지 ID 반환
   - 총 페이지 수 반환

6. **페이지 삭제**:
   - 현재 표시 중인 페이지 삭제 시 처리 (기본 페이지로 전환 또는 빈 화면)
   - 페이지 존재 여부 확인

**구현 복잡도**: 높음
- 페이지 저장소 관리
- 전환 효과 구현
- 자동 전환 로직
- 우선순위 처리

**의존성**: 
- 애니메이션 효과 (전환 효과용)
- 타이머 관리

**사용 시나리오**:
- 다중 정보 표시 (상태, 배터리, 센서 데이터 등)
- 메뉴 시스템
- 슬라이드쇼

**예상 구현 시간**: 6-8시간

---

## 7. 이미지 표시 (DisplayImage 서비스)

### 7.1 목적

이미지 파일을 LCD에 표시하여 아이콘이나 그래픽을 표시할 수 있도록 합니다.

### 7.2 구현 방법

**서비스 인터페이스**: `pinky_lcd_display_interfaces/srv/DisplayImage.srv`

**요청 파라미터**:
- `image_path`: 이미지 파일 경로 (PNG, JPEG)
- `x`, `y`: 이미지 위치 (픽셀)
- `width`, `height`: 이미지 크기 (0이면 원본 크기)
- `overlay_text`: 텍스트 오버레이 여부
- `overlay_text_content`: 오버레이 텍스트

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 서비스 서버 생성 및 요청 처리
- `pinky_lcd_display/lcd_manager.py`: 이미지 로드 및 표시

**기술적 세부사항**:

1. **이미지 로드**:
   ```python
   def load_image(self, image_path):
       try:
           img = Image.open(image_path)
           return img
       except Exception as e:
           raise RuntimeError(f"Failed to load image: {e}")
   ```

2. **이미지 리사이즈**:
   - `width` 또는 `height`가 0이면 원본 크기 유지
   - 비율 유지 또는 강제 리사이즈 선택
   ```python
   if width > 0 and height > 0:
       img = img.resize((width, height), Image.Resampling.LANCZOS)
   elif width > 0:
       # 비율 유지하며 너비만 조정
       ratio = width / img.width
       height = int(img.height * ratio)
       img = img.resize((width, height), Image.Resampling.LANCZOS)
   ```

3. **이미지 배치**:
   - 배경 이미지에 이미지 붙여넣기
   - 위치 지정 (x, y)
   ```python
   def display_image(self, image_path, x, y, width, height, overlay_text, overlay_text_content):
       img, draw = self._new_canvas()
       # 이미지 로드 및 리사이즈
       overlay_img = self.load_image(image_path)
       if width > 0 and height > 0:
           overlay_img = overlay_img.resize((width, height), Image.Resampling.LANCZOS)
       # 배경 이미지에 붙여넣기
       img.paste(overlay_img, (x, y))
       # 텍스트 오버레이
       if overlay_text:
           draw.text((x, y - 20), overlay_text_content, fill=(255, 255, 255), font=self.font_body)
       return img
   ```

4. **에러 처리**:
   - 이미지 파일 존재 여부 확인
   - 지원 형식 확인 (PNG, JPEG)
   - 메모리 부족 처리

**구현 복잡도**: 중간
- 이미지 로드 및 리사이즈
- 이미지 배치
- 에러 처리

**의존성**: 
- PIL/Pillow (이미지 처리)

**사용 시나리오**:
- 아이콘 표시
- 로고 표시
- 그래프/차트 표시 (이미지로 변환 후)

**예상 구현 시간**: 3-4시간

---

## 8. 파라미터 관리 (SetParameter, GetParameter 서비스)

### 8.1 목적

런타임에 패키지 동작을 제어하는 파라미터를 설정하고 조회할 수 있도록 합니다.

### 8.2 구현 방법

**서비스 인터페이스**:
- `pinky_lcd_display_interfaces/srv/SetParameter.srv`
- `pinky_lcd_display_interfaces/srv/GetParameter.srv`

**지원 파라미터**:
- `update_rate`: 상태 토픽 발행 주기 (Hz, 기본값: 10)
- `qos_depth`: QoS 큐 깊이 (기본값: 10)
- `debug_mode`: 디버그 모드 (true/false, 기본값: false)
- `auto_clear_timeout`: 자동 클리어 타임아웃 (초, 기본값: 0)

**구현 위치**:
- `pinky_lcd_display/lcd_node.py`: 서비스 서버 생성 및 요청 처리
- 파라미터 저장소 및 적용

**기술적 세부사항**:

1. **파라미터 저장소**:
   ```python
   class LCDDisplayNode:
       def __init__(self):
           self.parameters = {
               'update_rate': 10,
               'qos_depth': 10,
               'debug_mode': False,
               'auto_clear_timeout': 0
           }
   ```

2. **파라미터 설정**:
   - JSON 문자열로 파라미터 값 전달
   - 파라미터 검증 (범위, 타입)
   - 이전 값 저장 및 반환
   ```python
   def set_parameter(self, parameter_name, parameter_value):
       # JSON 파싱
       try:
           value = json.loads(parameter_value)
       except:
           raise ValueError("Invalid JSON format")
       
       # 파라미터 검증
       if parameter_name == 'update_rate':
           if not (1 <= value <= 60):
               raise ValueError("update_rate must be between 1 and 60")
       
       # 이전 값 저장
       old_value = self.parameters.get(parameter_name)
       
       # 파라미터 설정
       self.parameters[parameter_name] = value
       
       # 즉시 적용
       self.apply_parameter(parameter_name, value)
       
       return old_value
   ```

3. **파라미터 적용**:
   - `update_rate`: 상태 토픽 발행 타이머 주기 변경
   - `debug_mode`: 로그 레벨 변경
   - `auto_clear_timeout`: 자동 클리어 타이머 설정

4. **파라미터 조회**:
   - 파라미터 이름으로 값 조회
   - JSON 문자열로 직렬화하여 반환
   - 존재하지 않는 파라미터 처리

**구현 복잡도**: 낮음-중간
- 파라미터 저장소 관리
- JSON 파싱 및 검증
- 즉시 적용 로직

**의존성**: 
- json (JSON 파싱)

**사용 시나리오**:
- 동적 설정 변경
- 디버깅 모드 활성화
- 성능 튜닝

**예상 구현 시간**: 2-3시간

---

## 구현 우선순위 요약

### Priority 1 (필수) - 단기 구현
1. **스타일 동적 적용** (2-3시간)
   - 복잡도: 중간
   - 의존성: 없음
   - 즉시 사용 가능한 기능

2. **레이아웃 제어** (4-5시간)
   - 복잡도: 높음
   - 의존성: PIL/Pillow
   - 사용자 경험 향상

3. **상태/이벤트 토픽 발행** (2-3시간)
   - 복잡도: 낮음-중간
   - 의존성: pinky_lcd_display_interfaces
   - 모니터링 필수

### Priority 2 (중요) - 중기 구현
4. **애니메이션 효과** (5-6시간)
   - 복잡도: 높음
   - 의존성: PIL/Pillow, threading
   - 시각적 효과 향상

5. **스크롤 텍스트** (4-5시간)
   - 복잡도: 중간-높음
   - 의존성: PIL/Pillow, threading
   - 긴 텍스트 표시 필수

6. **파라미터 관리** (2-3시간)
   - 복잡도: 낮음-중간
   - 의존성: json
   - 동적 설정 필수

### Priority 3 (선택) - 장기 구현
7. **페이지 관리** (6-8시간)
   - 복잡도: 높음
   - 의존성: 애니메이션 효과
   - 복잡한 UI 구성

8. **이미지 표시** (3-4시간)
   - 복잡도: 중간
   - 의존성: PIL/Pillow
   - 그래픽 표시

---

## 총 예상 구현 시간

- **Priority 1**: 8-11시간
- **Priority 2**: 11-14시간
- **Priority 3**: 9-12시간
- **총계**: 28-37시간

---

## 참고

- 인터페이스 제안서: `/home/guehojung/Downloads/lcd_ws/INTERFACE_PROPOSAL.md`
- 구현 계획서: [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- 사용자 가이드: [USER_GUIDE.md](USER_GUIDE.md)

