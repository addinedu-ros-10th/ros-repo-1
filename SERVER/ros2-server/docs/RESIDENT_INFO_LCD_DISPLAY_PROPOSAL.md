# 어르신 정보 LCD 표시 형식 제안서

**작성일**: 2025-01-22  
**목적**: DL YOLO 탐지 후 어르신 정보를 로봇 LCD에 표시

---

## 개요

DL YOLO가 어르신을 탐지하고 API를 통해 정보를 받아와서 로봇 LCD에 요약 정보를 표시하는 시스템입니다.

---

## 정보 수집 API

### 1. 사용자 기본 정보
```
GET /api/users/{user_id}
```
- `user_name`: 이름
- `user_role`: 역할 (care_target)

### 2. 어르신 상세 정보 (중심)
```
GET /api/residents/{user_id}
```
- `user_name`: 이름
- `nickname`: 애칭
- `room_number`: 생활실 호수
- `floor_number`: 층수
- `bed_number`: 침대 번호
- `special_notes`: 특이사항 (health, emotional, behavioral, psychological)
- `current_status`: 현재 상태
- `adl_level`: 일상생활 활동 수준
- `mobility_level`: 이동 수준
- `cognitive_level`: 인지 수준

### 3. 프로필 정보 (보조)
```
GET /api/user-profiles/{user_id}
```
- `current_status`: 현재 상태
- `medical_history`: 병력
- `significant_notes`: 주요 참고사항

---

## LCD 표시 형식 제안

### 제약사항
- LCD 화면 크기: 일반적으로 128x64 또는 320x240 픽셀
- 타이틀: 최대 20자
- 본문 라인: 화면 크기에 따라 3-5줄 가능
- 한글 폰트 지원: ✅ (MaruBuri)

### 제안 형식 1: 기본 정보형 (권장)

```
타이틀: [애칭] 또는 [이름]
라인1: 생활실: 3층 302호 A번
라인2: 상태: 보행기 사용
라인3: 주의: 낙상 위험 높음
타임스탬프: 2025-01-22 14:30:15
```

**특징**:
- 간결하고 핵심 정보만 표시
- 3줄로 구성되어 작은 화면에도 적합
- 특이사항을 한 줄로 요약

### 제안 형식 2: 상세 정보형

```
타이틀: [애칭] 어르신 정보
라인1: 생활실: 3층 302호 A번 침대
라인2: 이동: 보행기 사용 필요
라인3: 건강: 고혈압, 당뇨 관리 중
라인4: 주의: 낙상 위험 높음
라인5: 약물: 다음 복용 20:00
타임스탬프: 2025-01-22 14:30:15
```

**특징**:
- 더 많은 정보 표시
- 약물 복용 시간 등 추가 정보
- 큰 화면(320x240 이상)에 적합

### 제안 형식 3: 긴급 정보 우선형

```
타이틀: ⚠️ [애칭] 어르신
라인1: 생활실: 3층 302호 A번
라인2: ⚠️ 낙상 위험 높음
라인3: 보행기 필수 사용
라인4: 야간 이동 주의
타임스탬프: 2025-01-22 14:30:15
```

**특징**:
- 긴급 정보를 강조
- 주의사항을 우선 표시
- 간결한 메시지

### 제안 형식 4: 스크롤 텍스트형 (긴 정보용)

```
타이틀: [애칭] 어르신 상세 정보
스크롤 텍스트:
"생활실: 3층 302호 A번 침대 | 이동: 보행기 사용 | 건강: 고혈압, 당뇨 관리 | 주의: 낙상 위험 높음, 야간 이동 주의 | 약물: 다음 복용 20:00"
```

**특징**:
- 긴 정보를 스크롤로 표시
- ScrollTextAction 활용
- 모든 정보를 한 번에 표시

---

## 정보 요약 로직 제안

### 1. 기본 정보 추출

```python
def extract_basic_info(resident_data):
    """기본 정보 추출"""
    return {
        "name": resident_data.get("nickname") or resident_data.get("user_name"),
        "room": f"{resident_data.get('floor_number')}층 {resident_data.get('room_number')}호",
        "bed": f"{resident_data.get('bed_number')}번 침대" if resident_data.get('bed_number') else None
    }
```

### 2. 생활실 정보 포맷팅

```python
def format_room_info(resident_data):
    """생활실 정보 포맷팅"""
    floor = resident_data.get('floor_number', '')
    room = resident_data.get('room_number', '')
    bed = resident_data.get('bed_number', '')
    
    if bed:
        return f"{floor}층 {room}호 {bed}번"
    else:
        return f"{floor}층 {room}호"
```

### 3. 특이사항 요약

```python
def summarize_special_notes(resident_data):
    """특이사항 요약"""
    special_notes = resident_data.get('special_notes', {})
    notes = []
    
    # 건강 관련
    health = special_notes.get('health', {})
    if health.get('fall_risk') == '높음':
        notes.append("낙상 위험 높음")
    if health.get('diabetes'):
        notes.append("당뇨 관리")
    if health.get('blood_pressure'):
        notes.append("고혈압 주의")
    
    # 행동 관련
    behavioral = special_notes.get('behavioral', {})
    if behavioral.get('wandering'):
        notes.append("야간 이동 주의")
    
    # 이동 수준
    mobility = resident_data.get('mobility_level', '')
    if mobility == 'walker':
        notes.append("보행기 사용")
    
    return notes[:3]  # 최대 3개
```

### 4. 현재 상태 요약

```python
def summarize_current_status(resident_data, profile_data):
    """현재 상태 요약"""
    # residents의 current_status 또는 user-profiles의 current_status 사용
    status = resident_data.get('current_status') or profile_data.get('current_status', '')
    
    # 긴 텍스트를 요약
    if len(status) > 30:
        # 핵심 키워드 추출
        keywords = ['보행기', '낙상', '야간', '도움 필요']
        summary = []
        for keyword in keywords:
            if keyword in status:
                summary.append(keyword)
        return ', '.join(summary[:2])
    
    return status[:30]  # 최대 30자
```

### 5. 약물 정보 추출

```python
def get_next_medication(resident_data):
    """다음 약물 복용 시간"""
    schedule = resident_data.get('medication_schedule', [])
    if not schedule:
        return None
    
    from datetime import datetime, time
    now = datetime.now()
    current_time = now.time()
    
    # 다음 복용 시간 찾기
    for med in schedule:
        med_time = datetime.strptime(med['time'], '%H:%M').time()
        if med_time > current_time:
            return f"약물: {med['medication_name']} {med['time']}"
    
    # 오늘 남은 약이 없으면 내일 첫 약
    if schedule:
        first_med = schedule[0]
        return f"약물: {first_med['medication_name']} 내일 {first_med['time']}"
    
    return None
```

---

## LCD 표시 명령어 제안

### 형식 1: 기본 정보형 (권장)

```bash
# ROS2 서비스 호출
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Akaza 어르신', \
   lines: ['생활실: 3층 302호 A번', '상태: 보행기 사용', '주의: 낙상 위험 높음'], \
   show_timestamp: true}"
```

**Python 코드 예시**:
```python
from pinky_lcd_display_interfaces.srv import SetDisplay

def display_resident_info_basic(resident_data, profile_data):
    """기본 정보형 표시"""
    # 정보 추출
    name = resident_data.get("nickname") or resident_data.get("user_name")
    room_info = format_room_info(resident_data)
    special_notes = summarize_special_notes(resident_data)
    status = summarize_current_status(resident_data, profile_data)
    
    # 라인 구성
    lines = [
        f"생활실: {room_info}",
        f"상태: {status}" if status else "상태: 정상",
        f"주의: {special_notes[0]}" if special_notes else ""
    ]
    
    # 서비스 요청
    request = SetDisplay.Request()
    request.title = f"{name} 어르신"
    request.lines = [line for line in lines if line]  # 빈 라인 제거
    request.show_timestamp = True
    
    return request
```

### 형식 2: 상세 정보형

```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Akaza 어르신 정보', \
   lines: ['생활실: 3층 302호 A번 침대', '이동: 보행기 사용 필요', '건강: 고혈압, 당뇨 관리', '주의: 낙상 위험 높음', '약물: 다음 복용 20:00'], \
   show_timestamp: true}"
```

**Python 코드 예시**:
```python
def display_resident_info_detailed(resident_data, profile_data):
    """상세 정보형 표시"""
    name = resident_data.get("nickname") or resident_data.get("user_name")
    room_info = format_room_info(resident_data)
    special_notes = summarize_special_notes(resident_data)
    next_med = get_next_medication(resident_data)
    
    # 건강 정보
    health_info = []
    if resident_data.get('special_notes', {}).get('health', {}).get('diabetes'):
        health_info.append("당뇨")
    if resident_data.get('special_notes', {}).get('health', {}).get('blood_pressure'):
        health_info.append("고혈압")
    health_str = ', '.join(health_info) if health_info else "정상"
    
    # 라인 구성
    lines = [
        f"생활실: {room_info}",
        f"이동: {resident_data.get('mobility_level', '정상')}",
        f"건강: {health_str}",
        f"주의: {special_notes[0]}" if special_notes else "주의사항 없음"
    ]
    
    if next_med:
        lines.append(next_med)
    
    request = SetDisplay.Request()
    request.title = f"{name} 어르신 정보"
    request.lines = lines[:5]  # 최대 5줄
    request.show_timestamp = True
    
    return request
```

### 형식 3: 긴급 정보 우선형

```bash
ros2 service call /lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: '⚠️ Akaza 어르신', \
   lines: ['생활실: 3층 302호 A번', '⚠️ 낙상 위험 높음', '보행기 필수 사용', '야간 이동 주의'], \
   show_timestamp: true}"
```

**Python 코드 예시**:
```python
def display_resident_info_urgent(resident_data, profile_data):
    """긴급 정보 우선형 표시"""
    name = resident_data.get("nickname") or resident_data.get("user_name")
    room_info = format_room_info(resident_data)
    special_notes = summarize_special_notes(resident_data)
    
    # 긴급 정보 우선
    urgent_notes = []
    normal_notes = []
    
    for note in special_notes:
        if '낙상' in note or '위험' in note or '주의' in note:
            urgent_notes.append(f"⚠️ {note}")
        else:
            normal_notes.append(note)
    
    lines = [f"생활실: {room_info}"]
    lines.extend(urgent_notes[:2])  # 긴급 정보 최대 2개
    lines.extend(normal_notes[:2])  # 일반 정보 최대 2개
    
    request = SetDisplay.Request()
    request.title = f"⚠️ {name} 어르신" if urgent_notes else f"{name} 어르신"
    request.lines = lines[:4]  # 최대 4줄
    request.show_timestamp = True
    
    return request
```

### 형식 4: 스크롤 텍스트형

```bash
# 액션 호출
ros2 action send_goal /lcd_controller/scroll_text_action \
  pinky_lcd_display_interfaces/action/ScrollText \
  "{text: 'Akaza 어르신 | 생활실: 3층 302호 A번 | 이동: 보행기 사용 | 건강: 고혈압, 당뇨 | 주의: 낙상 위험 높음 | 약물: 다음 복용 20:00', \
   scroll_speed_ms: 50, \
   direction: 0, \
   repeat_count: 3}"
```

**Python 코드 예시**:
```python
from pinky_lcd_display_interfaces.action import ScrollText

def display_resident_info_scroll(resident_data, profile_data):
    """스크롤 텍스트형 표시"""
    name = resident_data.get("nickname") or resident_data.get("user_name")
    room_info = format_room_info(resident_data)
    special_notes = summarize_special_notes(resident_data)
    next_med = get_next_medication(resident_data)
    
    # 모든 정보를 하나의 텍스트로 구성
    info_parts = [
        f"{name} 어르신",
        f"생활실: {room_info}",
        f"이동: {resident_data.get('mobility_level', '정상')}",
    ]
    
    if special_notes:
        info_parts.append(f"주의: {', '.join(special_notes)}")
    
    if next_med:
        info_parts.append(next_med)
    
    scroll_text = " | ".join(info_parts)
    
    goal = ScrollText.Goal()
    goal.text = scroll_text
    goal.scroll_speed_ms = 50
    goal.direction = 0  # LEFT
    goal.repeat_count = 3
    
    return goal
```

---

## 최종 권장 형식

### 기본 형식 (권장)

**구조**:
```
타이틀: [애칭] 어르신 (최대 20자)
라인1: 생활실: [층수]층 [호수]호 [침대번호]번
라인2: 상태: [이동수준] / [주요 건강 상태]
라인3: 주의: [가장 중요한 특이사항 1개]
타임스탬프: [시간]
```

**예시**:
```
타이틀: Akaza 어르신
라인1: 생활실: 3층 302호 A번
라인2: 상태: 보행기 사용 / 당뇨 관리
라인3: 주의: 낙상 위험 높음
타임스탬프: 2025-01-22 14:30:15
```

**특징**:
- ✅ 간결하고 핵심 정보만 표시
- ✅ 작은 LCD 화면에도 적합
- ✅ 빠른 정보 파악 가능
- ✅ 3줄로 구성되어 가독성 좋음

---

## API 엔드포인트 제안

### 1. 어르신 정보 요약 API

```python
POST /api/ros2/lcd/display/resident-info
```

**Request**:
```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "display_format": "basic",  // basic, detailed, urgent, scroll
  "show_timestamp": true
}
```

**Response**:
```json
{
  "success": true,
  "message": "LCD display updated",
  "display_data": {
    "title": "Akaza 어르신",
    "lines": [
      "생활실: 3층 302호 A번",
      "상태: 보행기 사용 / 당뇨 관리",
      "주의: 낙상 위험 높음"
    ],
    "timestamp": "2025-01-22 14:30:15"
  }
}
```

### 2. 어르신 정보 조회 API

```python
GET /api/ros2/resident/{user_id}/summary
```

**Response**:
```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "name": "정도현",
  "nickname": "Akaza",
  "room": "3층 302호 A번",
  "mobility": "보행기 사용",
  "health_status": "고혈압, 당뇨 관리 중",
  "special_notes": [
    "낙상 위험 높음",
    "야간 이동 주의"
  ],
  "next_medication": {
    "name": "고혈압약",
    "time": "20:00"
  }
}
```

---

## 구현 단계

### Phase 1: 기본 정보 표시
1. ✅ 기본 정보 추출 로직
2. ✅ 생활실 정보 포맷팅
3. ✅ 특이사항 요약 (최상위 1개)
4. ✅ LCD 표시 API 구현

### Phase 2: 상세 정보 표시
1. ⏳ 건강 정보 통합
2. ⏳ 약물 정보 표시
3. ⏳ 여러 형식 지원

### Phase 3: 고급 기능
1. ⏳ 스크롤 텍스트 지원
2. ⏳ 애니메이션 효과
3. ⏳ 우선순위 기반 표시

---

## 정보 요약 우선순위

### 1순위 (항상 표시)
- 이름/애칭
- 생활실 정보 (층수, 호수, 침대)

### 2순위 (가능하면 표시)
- 이동 수준 (보행기 사용 등)
- 낙상 위험도

### 3순위 (공간이 있으면 표시)
- 건강 상태 (고혈압, 당뇨 등)
- 다음 약물 복용 시간
- 기타 특이사항

---

## 참고사항

1. **LCD 화면 크기 확인 필요**: 실제 LCD 화면 크기에 따라 라인 수 조정
2. **폰트 크기**: 한글 표시를 위해 적절한 폰트 크기 설정
3. **타임스탬프**: 탐지 시간 표시로 최신 정보임을 명시
4. **에러 처리**: API 호출 실패 시 기본 정보라도 표시

---

## 다음 단계

1. ✅ LCD 표시 형식 결정 (기본 형식 권장)
2. ⏳ 정보 요약 로직 구현
3. ⏳ FastAPI 엔드포인트 구현
4. ⏳ ROS2 서비스 호출 통합
5. ⏳ 테스트 및 최적화

