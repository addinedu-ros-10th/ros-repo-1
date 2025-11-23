# Pinky Emotion 통합 계획서

## 📋 요청 사항 이해 및 정리

### 1. 조사 대상
- **패키지**: `ROS2/pinky_pro/src/pinky_pro/pinky_emotion`
- **목적**: 감정 표현 관련 패키지 조사 및 API 서버 통합

### 2. 조사 항목
- ✅ 사용법 (토픽, 서비스, 액션)
- ✅ 기능 범위
- ✅ 인터페이스 구조

### 3. 개발 요구사항
- ✅ `ros2-server`에 원격 호출 패키지 설치
- ✅ `pinky_emotion_controller` 패키지 생성
- ✅ 필요시 인터페이스 패키지 생성
- ✅ `pinky_lcd_display_controller`와 유사한 구조로 API 서버 통합

---

## 🔍 Pinky Emotion 패키지 분석 결과

### 패키지 구조
```
ROS2/pinky_pro/src/pinky_pro/pinky_emotion/
├── pinky_emotion/
│   ├── pinky_emotion.py          # 기본 구현
│   ├── emotion_server.py          # 최적화된 구현 (GIF 프리로딩)
│   └── pinky_lcd.py               # LCD 제어 모듈
├── emotion/                       # GIF 파일들
│   ├── hello.gif
│   ├── basic.gif
│   ├── angry.gif
│   ├── bored.gif
│   ├── fun.gif
│   ├── happy.gif
│   ├── interest.gif
│   └── sad.gif
├── package.xml
└── setup.py
```

### 서비스 인터페이스
**서비스명**: `set_emotion`  
**인터페이스**: `pinky_interfaces/srv/Emotion`

**Request**:
```python
string emotion  # 감정 타입: "hello", "basic", "angry", "bored", "fun", "happy", "interest", "sad"
```

**Response**:
```python
string response  # 응답 메시지
```

### 지원 감정 타입
1. `hello` - 인사
2. `basic` - 기본 상태
3. `angry` - 화남
4. `bored` - 지루함
5. `fun` - 재미있음
6. `happy` - 행복함
7. `interest` - 관심
8. `sad` - 슬픔

### 기능 범위
- ✅ GIF 파일을 LCD에 표시
- ✅ 감정별 GIF 프리로딩 (emotion_server.py)
- ✅ 애니메이션 재생 (타이머 기반)
- ✅ 서비스 기반 제어

### 통신 방식
- **서비스**: `set_emotion` (pinky_interfaces/srv/Emotion)
- **토픽**: 없음
- **액션**: 없음

---

## 📝 개발 계획

### Phase 1: 인터페이스 패키지 확인/생성
**목표**: `pinky_interfaces` 패키지 확인 및 필요시 생성

**작업 내용**:
1. `pinky_interfaces` 패키지 존재 여부 확인
2. `Emotion.srv` 인터페이스 확인
3. 필요시 `ros2-server`에 인터페이스 패키지 생성

**예상 결과**:
- `pinky_interfaces` 패키지가 `ros2-server`에서 사용 가능

### Phase 2: pinky_emotion_controller 패키지 생성
**목표**: `pinky_lcd_display_controller`와 유사한 구조로 컨트롤러 패키지 생성

**작업 내용**:
1. 패키지 구조 생성
   ```
   SERVER/ros2-server/src/pinky_emotion_controller/
   ├── package.xml
   ├── setup.py
   ├── setup.cfg
   ├── resource/
   ├── pinky_emotion_controller/
   │   ├── __init__.py
   │   └── emotion_controller_server.py
   └── README.md
   ```

2. `emotion_controller_server.py` 구현
   - `pinky_interfaces.srv.Emotion` 서비스 클라이언트 생성
   - 원격 `pinky_emotion` 노드의 `set_emotion` 서비스 호출
   - 에러 처리 및 폴백 메커니즘

3. 패키지 빌드 및 설치

**예상 결과**:
- `pinky_emotion_controller` 패키지 빌드 완료
- `emotion_controller_server` 노드 실행 가능

### Phase 3: API 서버 통합
**목표**: FastAPI 서버에서 감정 표현 제어 가능

**작업 내용**:
1. `ros2_client.py` 확장 또는 새로운 클라이언트 생성
   - `EmotionClient` 클래스 생성
   - `set_emotion()` 메서드 구현

2. `main.py`에 API 엔드포인트 추가
   - `POST /api/emotion/set` 엔드포인트
   - 요청 모델: `EmotionRequest`
   - 응답 모델: `EmotionResponse`

3. 설정 파일 업데이트
   - `config.py`에 감정 관련 설정 추가
   - `.env.example` 업데이트

**예상 결과**:
- API 서버에서 감정 표현 제어 가능
- HTTP 요청으로 감정 변경 가능

### Phase 4: 테스트 및 검증
**목표**: 기능 검증 및 문서화

**작업 내용**:
1. 단위 테스트
   - 서비스 클라이언트 테스트
   - API 엔드포인트 테스트

2. 통합 테스트
   - API 서버 → emotion_controller_server → pinky_emotion 통신 테스트
   - 실제 LCD에 GIF 표시 확인

3. 문서화
   - API 사용 가이드 작성
   - 통합 가이드 작성

**예상 결과**:
- 모든 기능 정상 동작 확인
- 문서 완성

---

## 🏗️ 아키텍처 설계

### 통신 구조
```
[FastAPI Server]
    |
    | HTTP POST /api/emotion/set
    v
[ROS2Client/EmotionClient]
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

### 패키지 의존성
```
pinky_emotion_controller
├── rclpy
├── pinky_interfaces
└── std_msgs

api-server (src/ros2_client.py 확장)
├── rclpy
└── pinky_interfaces
```

---

## ✅ 확인 사항 (피드백 요청)

### 1. 인터페이스 패키지
- **질문**: `pinky_interfaces` 패키지를 `ros2-server`에 복사/생성할까요, 아니면 원격에서 사용할까요?
- **제안**: 원격 사용 (ROS2 도메인 ID로 통신)

### 2. 서비스 이름
- **질문**: 서비스 이름을 `/emotion_controller/set_emotion`으로 할까요, 아니면 `/set_emotion`으로 할까요?
- **제안**: `/emotion_controller/set_emotion` (명확성)

### 3. API 엔드포인트
- **질문**: API 엔드포인트를 `/api/emotion/set`로 할까요, 아니면 다른 이름으로 할까요?
- **제안**: `/api/emotion/set` (RESTful)

### 4. 에러 처리
- **질문**: `pinky_emotion` 서비스가 사용 불가능할 때 어떻게 처리할까요?
- **제안**: 에러 응답 반환, Health Check에 포함

### 5. 감정 타입 검증
- **질문**: API에서 감정 타입을 Enum으로 제한할까요, 아니면 문자열로 받을까요?
- **제안**: Enum으로 제한 (타입 안정성)

---

## 📅 예상 일정

1. **인터페이스 확인**: 30분
2. **컨트롤러 패키지 생성**: 1시간
3. **API 서버 통합**: 1시간
4. **테스트 및 검증**: 1시간

**총 예상 시간**: 약 3.5시간

---

## 🚀 다음 단계

1. 피드백 확인
2. 개발 계획 수정 (필요시)
3. 개발 시작
4. 테스트 및 검증
5. 문서화

