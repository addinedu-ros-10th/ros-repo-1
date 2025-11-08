# pinky_lcd_display 인터페이스 통합 현황

## 개요

이 문서는 `pinky_lcd_display` 패키지가 `pinky_lcd_display_interfaces`를 통해 제공하는 인터페이스 통합 현황을 정리한 것입니다.

## 통신 구조

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

## 구현 현황

### ✅ 완료된 기능

#### 1. 서비스 인터페이스

**SetDisplay 서비스** (`lcd_controller/set_display`)
- ✅ 구현 완료
- LCD 내용 설정 (타이틀, 본문 라인, 타임스탬프)
- 이벤트 발행 (DISPLAY_STARTED)

**SetStyle 서비스** (`lcd_controller/set_style`)
- ✅ 구현 완료
- 스타일 동적 적용 (색상, 폰트 크기, 폰트 경로)
- 폰트 재로드 지원
- 즉시 적용

**ClearDisplay 서비스** (`lcd_controller/clear_display`)
- ✅ 구현 완료
- 화면 지우기
- 이벤트 발행 (CLEARED)

**SetLayout 서비스** (`lcd_controller/set_layout`)
- ✅ 구현 완료
- 레이아웃 제어 (정렬, 여백, 간격, 그리드 모드)
- 즉시 적용

#### 2. 액션 인터페이스

**SetDisplayAction** (`lcd_controller/set_display_action`)
- ✅ 구현 완료
- 시간 제한 표시
- 애니메이션 효과 (FADE_IN, SLIDE)
- 진행 상태 피드백
- 자동 전환

**ScrollTextAction** (`lcd_controller/scroll_text_action`)
- ✅ 구현 완료
- 스크롤 텍스트 표시
- 방향 제어 (LEFT, RIGHT)
- 스크롤 속도 조절
- 반복 횟수 설정
- 진행 상태 피드백

#### 3. 토픽 인터페이스

**LCDStatus 토픽** (`/lcd_controller/status`)
- ✅ 구현 완료
- 실시간 상태 발행 (1Hz)
- 현재 표시 내용, 스타일, 레이아웃 정보 포함

**LCDEvent 토픽** (`/lcd_controller/events`)
- ✅ 구현 완료
- 이벤트 발행 (DISPLAY_STARTED, DISPLAY_ENDED, ERROR, CLEARED, ANIMATION_STARTED, ANIMATION_ENDED)

#### 4. 기존 기능 유지

**토픽 구독** (`/lcd/status`)
- ✅ 유지
- 기존 토픽 기반 제어 방식 계속 지원

## 사용 방법

### 서비스 호출 예시

```bash
# SetDisplay 서비스
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Pinky Status', lines: ['Battery: 78%', 'Mode: MOVING'], show_timestamp: true}"

# SetStyle 서비스
ros2 service call /lcd_controller/set_style \
  pinky_lcd_display_interfaces/srv/SetStyle \
  "{bg_color_r: 0, bg_color_g: 0, bg_color_b: 0, title_color_r: 0, title_color_g: 255, title_color_b: 0, body_color_r: 255, body_color_g: 255, body_color_b: 255, timestamp_color_r: 100, timestamp_color_g: 100, timestamp_color_b: 255, title_font_size: 20, body_font_size: 18, font_path: ''}"

# SetLayout 서비스
ros2 service call /lcd_controller/set_layout \
  pinky_lcd_display_interfaces/srv/SetLayout \
  "{alignment: 1, layout_mode: 1, margin_top: 10, margin_bottom: 10, margin_left: 10, margin_right: 10, line_spacing: 24, grid_columns: 1, grid_rows: 1}"

# ClearDisplay 서비스
ros2 service call /lcd_controller/clear_display \
  pinky_lcd_display_interfaces/srv/ClearDisplay
```

### 액션 호출 예시

```bash
# SetDisplayAction (페이드 인 효과, 5초간 표시)
ros2 action send_goal /lcd_controller/set_display_action \
  pinky_lcd_display_interfaces/action/SetDisplay \
  "{title: 'Alert', lines: ['Low battery!', 'Please charge'], show_timestamp: true, duration_ms: 5000, animation_type: 1}"

# ScrollTextAction
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'This is a very long text that needs to be scrolled', scroll_speed_ms: 50, direction: 0, repeat_count: 1}"
```

### 토픽 구독 예시

```bash
# 상태 토픽 구독
ros2 topic echo /lcd_controller/status

# 이벤트 토픽 구독
ros2 topic echo /lcd_controller/events
```

## 구현 세부사항

### 스타일 동적 적용

- `LCDDisplayManager.set_style()` 메서드로 스타일 설정
- 폰트 재로드 지원
- 즉시 적용 (다음 렌더링 시 반영)

### 레이아웃 제어

- 텍스트 정렬 (LEFT, CENTER, RIGHT)
- 레이아웃 모드 (SINGLE_LINE, MULTI_LINE, GRID)
- 여백 및 라인 간격 설정
- 그리드 모드 지원

### 애니메이션 효과

- FADE_IN: 알파값을 점진적으로 증가 (10프레임)
- SLIDE: 왼쪽에서 오른쪽으로 슬라이드 (10프레임)

### 스크롤 텍스트

- 텍스트 너비 측정
- 스크롤 애니메이션 (10픽셀씩 이동)
- 반복 횟수 제어
- 피드백 발행

## 제한 사항

1. **스크롤 방향**: 현재 LEFT, RIGHT만 지원 (UP, DOWN 미구현)
2. **애니메이션 성능**: 프레임 생성 시간에 따라 성능 영향 가능
3. **액션 취소**: SetDisplayAction의 duration_ms 대기 중 취소 지원

## 향후 개선 사항

1. UP/DOWN 스크롤 방향 지원
2. 페이지 관리 기능 (CreatePage, SwitchPage 등)
3. 이미지 표시 기능 (DisplayImage)
4. 파라미터 관리 기능 (SetParameter, GetParameter)

## 참고

- [구현 계획서](IMPLEMENTATION_PLAN.md)
- [기능 상세 설명](FEATURE_DETAILS.md)
- [사용자 가이드](../USER_GUIDE.md)

