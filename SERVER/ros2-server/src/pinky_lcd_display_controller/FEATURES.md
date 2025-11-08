# pinky_lcd_display 제어 가능한 피쳐

이 문서는 `pinky_lcd_display` 패키지에서 제어 가능한 피쳐들을 정리한 것입니다.

## 현재 구현된 제어 피쳐

### 1. 표시 내용 제어

#### 1.1 타이틀 (Title)
- **현재 상태**: ✅ 제어 가능
- **제어 방법**: `SetDisplay` 서비스의 `title` 파라미터
- **제한사항**: 최대 20자 (pinky_lcd_display 패키지에서 자동으로 잘림)
- **기본값**: "Pinky Status"

#### 1.2 본문 라인 (Body Lines)
- **현재 상태**: ✅ 제어 가능
- **제어 방법**: `SetDisplay` 서비스의 `lines` 파라미터 (string 배열)
- **제한사항**: 화면 크기에 따라 표시 가능한 라인 수 제한
- **예시**: `["Battery: 78%", "Mode: MOVING", "Waypoint: 2/4"]`

#### 1.3 타임스탬프 (Timestamp)
- **현재 상태**: ✅ 제어 가능
- **제어 방법**: `SetDisplay` 서비스의 `show_timestamp` 파라미터
- **형식**: "YYYY-MM-DD HH:MM:SS"
- **위치**: 화면 하단

### 2. 스타일 제어 (부분 지원)

#### 2.1 배경 색상 (Background Color)
- **현재 상태**: ⚠️ 서비스로 설정 가능하나 실제 적용은 pinky_lcd_display 패키지 수정 필요
- **제어 방법**: `SetStyle` 서비스의 `bg_color_r/g/b` 파라미터
- **기본값**: (0, 0, 0) - 검은색
- **형식**: RGB 값 (0-255)

#### 2.2 타이틀 색상 (Title Color)
- **현재 상태**: ⚠️ 서비스로 설정 가능하나 실제 적용은 pinky_lcd_display 패키지 수정 필요
- **제어 방법**: `SetStyle` 서비스의 `title_color_r/g/b` 파라미터
- **기본값**: (0, 255, 0) - 녹색
- **형식**: RGB 값 (0-255)

#### 2.3 본문 색상 (Body Color)
- **현재 상태**: ⚠️ 서비스로 설정 가능하나 실제 적용은 pinky_lcd_display 패키지 수정 필요
- **제어 방법**: `SetStyle` 서비스의 `body_color_r/g/b` 파라미터
- **기본값**: (255, 255, 255) - 흰색
- **형식**: RGB 값 (0-255)

#### 2.4 타임스탬프 색상 (Timestamp Color)
- **현재 상태**: ⚠️ 서비스로 설정 가능하나 실제 적용은 pinky_lcd_display 패키지 수정 필요
- **제어 방법**: `SetStyle` 서비스의 `timestamp_color_r/g/b` 파라미터
- **기본값**: (100, 100, 255) - 파란색
- **형식**: RGB 값 (0-255)

#### 2.5 폰트 크기 (Font Size)
- **현재 상태**: ⚠️ 서비스로 설정 가능하나 실제 적용은 pinky_lcd_display 패키지 수정 필요
- **제어 방법**: `SetStyle` 서비스의 `title_font_size`, `body_font_size` 파라미터
- **기본값**: 
  - 타이틀: 20
  - 본문: 18
- **형식**: 픽셀 단위 (uint8)

#### 2.6 폰트 경로 (Font Path)
- **현재 상태**: ⚠️ 서비스로 설정 가능하나 실제 적용은 pinky_lcd_display 패키지 수정 필요
- **제어 방법**: `SetStyle` 서비스의 `font_path` 파라미터
- **기본값**: `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`
- **형식**: 파일 시스템 경로 (string)

### 3. 화면 제어

#### 3.1 화면 지우기 (Clear Display)
- **현재 상태**: ✅ 제어 가능
- **제어 방법**: `ClearDisplay` 서비스 호출
- **동작**: LCD 화면을 지웁니다

## 추가 구현을 통해 제어 가능한 피쳐

### 1. 고급 스타일 제어

#### 1.1 텍스트 정렬 (Text Alignment)
- **제안 기능**: 왼쪽 정렬, 가운데 정렬, 오른쪽 정렬
- **구현 방법**: `LCDDisplayManager.render_status_frame()` 메서드 수정
- **필요한 변경**: `pinky_lcd_display` 패키지의 `lcd_manager.py` 수정

#### 1.2 텍스트 굵기 (Font Weight)
- **제안 기능**: 일반, 굵게, 얇게
- **구현 방법**: PIL의 `ImageFont.truetype()` 옵션 활용
- **필요한 변경**: 폰트 파일 경로 및 로드 방식 변경

#### 1.3 텍스트 스타일 (Text Style)
- **제안 기능**: 일반, 기울임, 밑줄
- **구현 방법**: PIL의 `ImageDraw.text()` 옵션 활용
- **필요한 변경**: `LCDDisplayManager.render_status_frame()` 메서드 수정

### 2. 레이아웃 제어

#### 2.1 레이아웃 모드 (Layout Mode)
- **제안 기능**: 
  - 단일 라인 모드
  - 다중 라인 모드
  - 그리드 모드 (2x2, 3x3 등)
- **구현 방법**: 레이아웃 엔진 추가
- **필요한 변경**: `LCDDisplayManager` 클래스에 레이아웃 관리 기능 추가

#### 2.2 여백 제어 (Margin Control)
- **제안 기능**: 상하좌우 여백 설정
- **구현 방법**: 텍스트 위치 계산 시 여백 값 적용
- **필요한 변경**: `LCDDisplayManager.render_status_frame()` 메서드 수정

#### 2.3 라인 간격 (Line Spacing)
- **제안 기능**: 라인 간 간격 조절
- **구현 방법**: 텍스트 위치 계산 시 간격 값 적용
- **필요한 변경**: `LCDDisplayManager.render_status_frame()` 메서드 수정

### 3. 애니메이션 및 효과

#### 3.1 스크롤 텍스트 (Scrolling Text)
- **제안 기능**: 긴 텍스트를 스크롤하여 표시
- **구현 방법**: 타이머를 사용하여 텍스트 위치를 이동
- **필요한 변경**: `LCDDisplayNode`에 타이머 및 애니메이션 로직 추가

#### 3.2 페이드 인/아웃 (Fade In/Out)
- **제안 기능**: 화면 전환 시 페이드 효과
- **구현 방법**: 알파 블렌딩을 사용한 이미지 합성
- **필요한 변경**: `LCDDisplayManager`에 페이드 효과 메서드 추가

#### 3.3 깜빡임 효과 (Blink Effect)
- **제안 기능**: 특정 텍스트나 라인을 깜빡이게 표시
- **구현 방법**: 타이머를 사용하여 표시/숨김 전환
- **필요한 변경**: `LCDDisplayManager`에 깜빡임 효과 메서드 추가

### 4. 이미지 및 그래픽

#### 4.1 이미지 표시 (Image Display)
- **제안 기능**: PNG, JPEG 등 이미지 파일 표시
- **구현 방법**: PIL의 `Image.open()` 및 리사이즈 기능 활용
- **필요한 변경**: `LCDDisplayManager`에 이미지 로드 및 표시 메서드 추가

#### 4.2 아이콘 표시 (Icon Display)
- **제안 기능**: 작은 아이콘 이미지 표시
- **구현 방법**: 이미지 표시 기능 활용
- **필요한 변경**: 아이콘 라이브러리 및 관리 기능 추가

#### 4.3 그래프 표시 (Graph Display)
- **제안 기능**: 간단한 막대 그래프, 선 그래프 표시
- **구현 방법**: PIL의 `ImageDraw`를 사용한 그래프 그리기
- **필요한 변경**: 그래프 렌더링 모듈 추가

### 5. 다중 페이지/화면

#### 5.1 페이지 전환 (Page Navigation)
- **제안 기능**: 여러 페이지 간 전환
- **구현 방법**: 페이지 관리 시스템 추가
- **필요한 변경**: `LCDDisplayManager`에 페이지 관리 기능 추가

#### 5.2 화면 분할 (Screen Split)
- **제안 기능**: 화면을 여러 영역으로 분할하여 표시
- **구현 방법**: 레이아웃 엔진 활용
- **필요한 변경**: 레이아웃 관리 기능 추가

### 6. 동적 업데이트

#### 6.1 실시간 데이터 업데이트 (Real-time Data Update)
- **제안 기능**: 특정 데이터를 주기적으로 업데이트
- **구현 방법**: 타이머를 사용한 주기적 업데이트
- **필요한 변경**: `LCDDisplayNode`에 데이터 구독 및 업데이트 로직 추가

#### 6.2 조건부 표시 (Conditional Display)
- **제안 기능**: 특정 조건에 따라 다른 내용 표시
- **구현 방법**: 조건 체크 로직 추가
- **필요한 변경**: 표시 로직에 조건부 처리 추가

### 7. 설정 저장 및 복원

#### 7.1 스타일 프리셋 (Style Presets)
- **제안 기능**: 미리 정의된 스타일 프리셋 저장 및 적용
- **구현 방법**: YAML 또는 JSON 파일로 프리셋 저장
- **필요한 변경**: 프리셋 관리 시스템 추가

#### 7.2 설정 파일 로드 (Configuration File Load)
- **제안 기능**: 설정 파일에서 스타일 및 레이아웃 로드
- **구현 방법**: YAML 또는 JSON 파서 활용
- **필요한 변경**: 설정 파일 파싱 기능 추가

## 구현 우선순위

### High Priority
1. ✅ 표시 내용 제어 (현재 구현됨)
2. ⚠️ 스타일 제어 (서비스는 구현됨, pinky_lcd_display 패키지 수정 필요)
3. ⏳ 텍스트 정렬 기능
4. ⏳ 레이아웃 모드

### Medium Priority
1. ⏳ 스크롤 텍스트
2. ⏳ 이미지 표시
3. ⏳ 실시간 데이터 업데이트

### Low Priority
1. ⏳ 애니메이션 효과
2. ⏳ 그래프 표시
3. ⏳ 페이지 전환

## 참고

- `pinky_lcd_display` 패키지 경로: `/home/guehojung/Documents/Project/FINAL/development/ros-repo-1/ROS2/rfred/src/pinky_lcd_display`
- 현재 `pinky_lcd_display` 패키지는 하드코딩된 색상과 폰트 설정을 사용합니다.
- 동적 스타일 변경을 위해서는 `LCDDisplayManager` 클래스를 수정해야 합니다.

