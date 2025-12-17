# pinky_lcd_display_controller 인터페이스 구현 계획서

## 개요

이 문서는 `pinky_lcd_display_controller` 패키지의 인터페이스 확장 구현 계획을 정리한 것입니다. `/home/guehojung/Downloads/lcd_ws/INTERFACE_PROPOSAL.md` 문서를 기반으로 서비스, 액션 등을 이용한 LCD 표준 기능을 제공합니다.

## 구현 현황

### ✅ 완료된 기능 (pinky_lcd_display 패키지)

1. **서비스 인터페이스**
   - ✅ `lcd_controller/set_display` - LCD 내용 설정 (서버 구현 완료)
   - ✅ `lcd_controller/set_style` - LCD 스타일 설정 (동적 적용 완료)
   - ✅ `lcd_controller/clear_display` - LCD 화면 지우기 (서버 구현 완료)
   - ✅ `lcd_controller/set_layout` - 레이아웃 제어 (서버 구현 완료)

2. **액션 인터페이스**
   - ✅ `lcd_controller/set_display_action` - 시간 제한 표시 및 애니메이션 (서버 구현 완료)
   - ✅ `lcd_controller/scroll_text_action` - 스크롤 텍스트 (서버 구현 완료)

3. **토픽 인터페이스**
   - ✅ `/lcd_controller/status` - LCD 상태 발행 (구현 완료)
   - ✅ `/lcd_controller/events` - LCD 이벤트 발행 (구현 완료)
   - ✅ `/lcd/status` (std_msgs/String) - 기존 토픽 구독 유지

### ⏳ 구현 예정 기능

다음 섹션에서 각 기능의 구현 계획을 상세히 설명합니다.

## 구현 대상 목록

### Priority 1 (필수) - 단기 구현

#### 1. SetDisplayAction (액션)
**상태**: ✅ 구현 완료 (pinky_lcd_display 패키지)  
**우선순위**: 높음

**목적**: 시간 제한이 있는 LCD 표시 및 진행 상태 피드백 제공

**인터페이스**: `pinky_lcd_display_interfaces/action/SetDisplay.action`

**요청 (Goal)**:
```python
string title                    # 타이틀 텍스트
string[] lines                  # 본문 라인들
bool show_timestamp             # 타임스탬프 표시 여부
uint32 duration_ms              # 표시 지속 시간 (밀리초, 0이면 무한)
uint8 animation_type            # 애니메이션 타입 (옵션)
```

**옵셔널 파라미터: `animation_type`**
- **0: NONE** (기본값) - 애니메이션 없음, 즉시 표시
- **1: FADE_IN** - 페이드 인 효과로 표시
- **2: SLIDE** - 슬라이드 효과로 표시

**응답 (Result)**:
```python
bool success                    # 성공 여부
string message                  # 결과 메시지
uint32 actual_duration_ms      # 실제 표시 시간
```

**피드백 (Feedback)**:
```python
uint32 elapsed_ms               # 경과 시간 (밀리초)
uint8 progress_percent          # 진행률 (0-100)
string status_message           # 상태 메시지
```

**사용 사례**:
- 일정 시간 후 자동으로 화면 전환
- 애니메이션 효과가 있는 표시
- 진행률이 있는 작업 표시
- 사용자 알림 (일정 시간 후 자동 사라짐)

**구현 방법**:
1. 액션 인터페이스 파일 생성
2. 액션 서버 구현 (타이머 기반 피드백)
3. 애니메이션 효과 구현 (FADE_IN, SLIDE)
4. 자동 전환 로직 구현

---

#### 2. LCDStatus 토픽 (메시지)
**상태**: ✅ 구현 완료 (pinky_lcd_display 패키지)  
**우선순위**: 높음

**목적**: LCD 현재 상태를 실시간으로 발행

**토픽명**: `/lcd_controller/status`  
**메시지 타입**: `pinky_lcd_display_interfaces/msg/LCDStatus`

**메시지 구조**:
```python
std_msgs/Header header
bool is_active                  # LCD 활성 상태
string current_title            # 현재 타이틀
string[] current_lines         # 현재 라인들
bool show_timestamp             # 타임스탬프 표시 여부
uint64 last_update_time         # 마지막 업데이트 시간 (나노초)
uint8 display_mode             # 표시 모드 (옵션)
uint32 error_code               # 에러 코드 (0이면 정상)
string error_message             # 에러 메시지
```

**옵셔널 파라미터: `display_mode`**
- **0: NORMAL** (기본값) - 일반 표시 모드
- **1: SCROLL** - 스크롤 표시 모드
- **2: ANIMATION** - 애니메이션 표시 모드

**발행 주기**: 상태 변경 시 또는 1Hz

**구현 방법**:
1. 메시지 인터페이스 파일 생성
2. 상태 관리 로직 추가
3. 주기적 상태 발행 (타이머 사용)
4. 상태 변경 이벤트 감지

---

#### 3. SetLayout 서비스
**상태**: ✅ 구현 완료 (pinky_lcd_display 패키지)  
**우선순위**: 높음

**목적**: 레이아웃 설정 (정렬, 여백, 간격 등)

**서비스명**: `lcd_controller/set_layout`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetLayout.srv`

**요청 (Request)**:
```python
uint8 alignment                 # 텍스트 정렬 (옵션)
uint8 layout_mode               # 레이아웃 모드 (옵션)
uint8 margin_top                 # 상단 여백 (픽셀, 기본값: 10)
uint8 margin_bottom             # 하단 여백 (픽셀, 기본값: 10)
uint8 margin_left               # 좌측 여백 (픽셀, 기본값: 10)
uint8 margin_right              # 우측 여백 (픽셀, 기본값: 10)
uint8 line_spacing              # 라인 간격 (픽셀, 기본값: 24)
uint8 grid_columns              # 그리드 모드: 열 수 (기본값: 1)
uint8 grid_rows                 # 그리드 모드: 행 수 (기본값: 1)
```

**옵셔널 파라미터: `alignment`**
- **0: LEFT** (기본값) - 왼쪽 정렬
- **1: CENTER** - 가운데 정렬
- **2: RIGHT** - 오른쪽 정렬

**옵셔널 파라미터: `layout_mode`**
- **0: SINGLE_LINE** (기본값) - 단일 라인 모드
- **1: MULTI_LINE** - 다중 라인 모드
- **2: GRID** - 그리드 모드 (grid_columns, grid_rows 사용)

**응답 (Response)**:
```python
bool success
string message
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 레이아웃 설정 저장 로직
3. 텍스트 렌더링 위치 계산 로직 수정
4. pinky_lcd_display 패키지에 레이아웃 적용 기능 추가

---

### Priority 2 (중요) - 중기 구현

#### 4. ScrollTextAction (액션)
**상태**: ✅ 구현 완료 (pinky_lcd_display 패키지)  
**우선순위**: 중간

**목적**: 긴 텍스트를 스크롤하여 표시

**인터페이스**: `pinky_lcd_display_interfaces/action/ScrollText.action`

**요청 (Goal)**:
```python
string text                     # 스크롤할 텍스트
uint32 scroll_speed_ms          # 스크롤 속도 (밀리초, 기본값: 50)
uint8 direction                 # 스크롤 방향 (옵션)
uint32 repeat_count             # 반복 횟수 (0이면 무한, 기본값: 1)
```

**옵셔널 파라미터: `direction`**
- **0: LEFT** (기본값) - 왼쪽으로 스크롤
- **1: RIGHT** - 오른쪽으로 스크롤
- **2: UP** - 위로 스크롤
- **3: DOWN** - 아래로 스크롤

**옵셔널 파라미터: `scroll_speed_ms`**
- 기본값: 50ms (20 FPS)
- 범위: 10ms ~ 1000ms
- 값이 작을수록 빠른 스크롤

**옵셔널 파라미터: `repeat_count`**
- 기본값: 1 (1회 반복)
- 0: 무한 반복
- 1 이상: 지정된 횟수만큼 반복

**응답 (Result)**:
```python
bool success
string message
uint32 total_scroll_time_ms
```

**피드백 (Feedback)**:
```python
uint32 current_position         # 현재 스크롤 위치
uint8 progress_percent          # 진행률 (0-100)
```

**구현 방법**:
1. 액션 인터페이스 파일 생성
2. 스크롤 로직 구현 (타이머 기반)
3. 텍스트 위치 계산 로직
4. 피드백 발행 로직

---

#### 5. LCDEvent 토픽 (메시지)
**상태**: ✅ 구현 완료 (pinky_lcd_display 패키지)  
**우선순위**: 중간

**목적**: LCD 이벤트 (표시 시작, 종료, 에러 등) 발행

**토픽명**: `/lcd_controller/events`  
**메시지 타입**: `pinky_lcd_display_interfaces/msg/LCDEvent`

**메시지 구조**:
```python
std_msgs/Header header
uint8 event_type                # 이벤트 타입 (옵션)
uint64 timestamp                # 이벤트 발생 시간
string message                  # 이벤트 메시지
```

**옵셔널 파라미터: `event_type`**
- **0: DISPLAY_STARTED** - 표시 시작
- **1: DISPLAY_ENDED** - 표시 종료
- **2: ERROR** - 에러 발생
- **3: CLEARED** - 화면 지워짐
- **4: PAGE_SWITCHED** - 페이지 전환
- **5: ANIMATION_STARTED** - 애니메이션 시작
- **6: ANIMATION_ENDED** - 애니메이션 종료

**발행 시점**: 이벤트 발생 시 즉시 발행

**구현 방법**:
1. 메시지 인터페이스 파일 생성
2. 이벤트 감지 로직 추가
3. 이벤트 발행 로직 구현

---

#### 6. CreatePage 서비스
**상태**: ⏳ 구현 예정  
**우선순위**: 중간

**목적**: 다중 페이지 생성

**서비스명**: `lcd_controller/create_page`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/CreatePage.srv`

**요청 (Request)**:
```python
string page_id                  # 페이지 ID (고유 식별자, 필수)
string title                    # 페이지 타이틀
string[] lines                  # 페이지 내용
uint32 display_duration_ms      # 표시 지속 시간 (0이면 수동 전환, 기본값: 0)
uint8 priority                  # 우선순위 (높을수록 우선, 기본값: 0)
```

**옵셔널 파라미터: `display_duration_ms`**
- 기본값: 0 (수동 전환)
- 0: 수동 전환만 가능
- 1 이상: 지정된 시간(ms) 후 자동으로 다음 페이지로 전환

**옵셔널 파라미터: `priority`**
- 기본값: 0
- 범위: 0-255
- 높은 우선순위 페이지가 자동 전환 시 먼저 표시됨

**응답 (Response)**:
```python
bool success
string page_id                  # 생성된 페이지 ID
string message
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 페이지 관리 시스템 구현
3. 페이지 저장소 (딕셔너리 또는 데이터베이스)
4. 우선순위 기반 페이지 선택 로직

---

#### 7. SwitchPage 서비스
**상태**: ⏳ 구현 예정  
**우선순위**: 중간

**목적**: 페이지 전환

**서비스명**: `lcd_controller/switch_page`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SwitchPage.srv`

**요청 (Request)**:
```python
string page_id                  # 전환할 페이지 ID
uint8 transition_type           # 전환 효과 타입 (옵션)
uint32 transition_duration_ms  # 전환 시간 (밀리초, 기본값: 0)
```

**옵셔널 파라미터: `transition_type`**
- **0: INSTANT** (기본값) - 즉시 전환
- **1: FADE** - 페이드 효과
- **2: SLIDE_LEFT** - 왼쪽으로 슬라이드
- **3: SLIDE_RIGHT** - 오른쪽으로 슬라이드
- **4: SLIDE_UP** - 위로 슬라이드
- **5: SLIDE_DOWN** - 아래로 슬라이드

**옵셔널 파라미터: `transition_duration_ms`**
- 기본값: 0 (즉시 전환)
- 범위: 0ms ~ 5000ms
- 전환 효과의 지속 시간

**응답 (Response)**:
```python
bool success
string message
string previous_page_id         # 이전 페이지 ID
string current_page_id          # 현재 페이지 ID
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 페이지 전환 로직 구현
3. 전환 효과 애니메이션 구현
4. 이전/현재 페이지 추적

---

#### 8. SetParameter 서비스
**상태**: ⏳ 구현 예정  
**우선순위**: 중간

**목적**: 런타임 파라미터 설정

**서비스명**: `lcd_controller/set_parameter`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/SetParameter.srv`

**요청 (Request)**:
```python
string parameter_name           # 파라미터 이름 (필수)
string parameter_value          # 파라미터 값 (JSON 문자열, 필수)
```

**지원 파라미터 목록**:

1. **`update_rate`** (옵션)
   - 타입: 숫자 (Hz)
   - 기본값: 10
   - 범위: 1-60
   - 설명: 상태 토픽 발행 주기
   - 예시: `"10"` (10Hz)

2. **`qos_depth`** (옵션)
   - 타입: 숫자
   - 기본값: 10
   - 범위: 1-100
   - 설명: QoS 큐 깊이
   - 예시: `"10"`

3. **`debug_mode`** (옵션)
   - 타입: 불린
   - 기본값: false
   - 설명: 디버그 모드 활성화 (상세 로그 출력)
   - 예시: `"true"` 또는 `"false"`

4. **`auto_clear_timeout`** (옵션)
   - 타입: 숫자 (초)
   - 기본값: 0 (비활성화)
   - 범위: 0-3600
   - 설명: 자동 클리어 타임아웃 (지정 시간 후 자동으로 화면 지움)
   - 예시: `"30"` (30초 후 자동 클리어)

**응답 (Response)**:
```python
bool success
string message
string old_value                # 이전 값
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 파라미터 저장소 구현
3. 파라미터 검증 로직
4. JSON 파싱 로직

---

#### 9. GetParameter 서비스
**상태**: ⏳ 구현 예정  
**우선순위**: 중간

**목적**: 파라미터 값 조회

**서비스명**: `lcd_controller/get_parameter`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/GetParameter.srv`

**요청 (Request)**:
```python
string parameter_name           # 파라미터 이름
```

**응답 (Response)**:
```python
bool success
string parameter_value          # 파라미터 값 (JSON 문자열)
string message
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 파라미터 조회 로직
3. JSON 직렬화 로직

---

### Priority 3 (선택) - 장기 구현

#### 10. DisplayImage 서비스
**상태**: ⏳ 구현 예정  
**우선순위**: 낮음

**목적**: 이미지 파일 표시

**서비스명**: `lcd_controller/display_image`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/DisplayImage.srv`

**요청 (Request)**:
```python
string image_path               # 이미지 파일 경로 (PNG, JPEG, 필수)
uint16 x                        # X 좌표 (픽셀, 기본값: 0)
uint16 y                        # Y 좌표 (픽셀, 기본값: 0)
uint16 width                    # 너비 (0이면 원본 크기, 기본값: 0)
uint16 height                   # 높이 (0이면 원본 크기, 기본값: 0)
bool overlay_text               # 텍스트 오버레이 여부 (기본값: false)
string overlay_text_content     # 오버레이 텍스트 (overlay_text가 true일 때)
```

**옵셔널 파라미터: `width`, `height`**
- 기본값: 0 (원본 크기 유지)
- 0: 원본 크기 사용
- 1 이상: 지정된 크기로 리사이즈

**옵셔널 파라미터: `overlay_text`**
- 기본값: false
- true: 이미지 위에 텍스트 오버레이
- false: 이미지만 표시

**응답 (Response)**:
```python
bool success
string message
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 이미지 로드 및 리사이즈 로직
3. 텍스트 오버레이 로직
4. pinky_lcd_display 패키지에 이미지 표시 기능 추가

---

#### 11. ListPages 서비스
**상태**: ⏳ 구현 예정  
**우선순위**: 낮음

**목적**: 페이지 목록 조회

**서비스명**: `lcd_controller/list_pages`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/ListPages.srv`

**요청 (Request)**: 없음

**응답 (Response)**:
```python
string[] page_ids               # 페이지 ID 목록
string current_page_id          # 현재 표시 중인 페이지 ID
uint8 page_count                # 총 페이지 수
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 페이지 목록 조회 로직

---

#### 12. DeletePage 서비스
**상태**: ⏳ 구현 예정  
**우선순위**: 낮음

**목적**: 페이지 삭제

**서비스명**: `lcd_controller/delete_page`  
**인터페이스**: `pinky_lcd_display_interfaces/srv/DeletePage.srv`

**요청 (Request)**:
```python
string page_id                  # 삭제할 페이지 ID
```

**응답 (Response)**:
```python
bool success
string message
```

**구현 방법**:
1. 서비스 인터페이스 파일 생성
2. 페이지 삭제 로직
3. 현재 표시 중인 페이지 삭제 시 처리

---

## 구현 우선순위 요약

### Phase 1 (단기 - 1-2주)
1. ⏳ SetDisplayAction - 시간 제한 표시
2. ⏳ LCDStatus 토픽 - 상태 모니터링
3. ⏳ SetLayout 서비스 - 레이아웃 제어

### Phase 2 (중기 - 1개월)
1. ⏳ ScrollTextAction - 스크롤 텍스트
2. ⏳ LCDEvent 토픽 - 이벤트 알림
3. ⏳ CreatePage/SwitchPage 서비스 - 다중 페이지
4. ⏳ SetParameter/GetParameter 서비스 - 파라미터 관리

### Phase 3 (장기 - 2-3개월)
1. ⏳ DisplayImage 서비스 - 이미지 표시
2. ⏳ ListPages/DeletePage 서비스 - 페이지 관리
3. ⏳ 고급 애니메이션 액션

## 구현 체크리스트

### Priority 1
- [ ] SetDisplayAction 인터페이스 파일 생성
- [ ] SetDisplayAction 서버 구현
- [ ] LCDStatus 메시지 인터페이스 파일 생성
- [ ] LCDStatus 토픽 발행 로직 구현
- [ ] SetLayout 서비스 인터페이스 파일 생성
- [ ] SetLayout 서비스 구현

### Priority 2
- [ ] ScrollTextAction 인터페이스 파일 생성
- [ ] ScrollTextAction 서버 구현
- [ ] LCDEvent 메시지 인터페이스 파일 생성
- [ ] LCDEvent 토픽 발행 로직 구현
- [ ] CreatePage/SwitchPage 서비스 인터페이스 파일 생성
- [ ] 페이지 관리 시스템 구현
- [ ] SetParameter/GetParameter 서비스 인터페이스 파일 생성
- [ ] 파라미터 관리 시스템 구현

### Priority 3
- [ ] DisplayImage 서비스 인터페이스 파일 생성
- [ ] 이미지 표시 기능 구현
- [ ] ListPages/DeletePage 서비스 인터페이스 파일 생성
- [ ] 페이지 관리 기능 확장

## 참고

이 문서는 `/home/guehojung/Downloads/lcd_ws/INTERFACE_PROPOSAL.md`를 기반으로 작성되었습니다.

