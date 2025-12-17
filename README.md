# ros-repo-1
파이널 프로젝트 1조 저장소. 요양원이 살아있다. (로봇 케어 요양원)

# 🧠 Multi-Domain Robotics-AI Monorepo

본 레포지토리는 IoT 센서, 딥러닝 서버, 로봇 경로계획, LLM 연동 서비스까지
포함한 **통합 AI·로보틱스 플랫폼**의 개발 환경을 제공합니다.

---

## 📂 프로젝트 구성

| 구분 | 위치 | 주요 기술 | 역할 | 상태 |
|------|------|------------|------|------|
| IOT | `IOT/arduino` | C++, Arduino | 센서/액추에이터 제어 펌웨어 | ✅ 구현됨 |
| DEEP_LEARNING | `DEEP_LEARNING/deep-learning-server` | PyTorch, FastAPI | 모델 추론/학습 서버 | ✅ 구현됨 |
| AI | `AI/llm-gateway` | Python, FastAPI | LLM 호출 및 음성 인터페이스 | ✅ 구현됨 |
| APP | `APP/gui` | PyQt | 로봇 제어 GUI | ⚠️ 부분 구현 |
| SERVER | `SERVER/app-server`, `SERVER/iot-data-server`, `SERVER/ros2-server` | FastAPI, ROS2 | 백엔드 서비스 그룹 | ✅ 구현됨 |
| ROS2 | `ROS2/pinky_pro`, `ROS2/rfred` | ROS2 | 로봇 제어 시스템 | ✅ 구현됨 |

## 📁 상세 디렉토리 구조

```
repo-root/
├─ IOT/
│  └─ arduino/                # ✅ Arduino 기반 IoT 디바이스 코드
│
├─ DEEP_LEARNING/
│  └─ deep-learning-server/   # ✅ 딥러닝 모델 학습 및 추론 서버
│
├─ AI/
│  └─ llm-gateway/           # ✅ OpenAI 프록시 및 음성 인터페이스 서버
│
├─ APP/
│  └─ gui/                   # ⚠️ PyQt 기반 로봇 제어 GUI (부분 구현)
│
├─ ROS2/
│  ├─ pinky_pro/             # ✅ Pinky 로봇 ROS2 패키지
│  ├─ rfred/                 # ✅ RFred 로봇 ROS2 패키지
│  └─ util/                  # ✅ 카메라 유틸리티
│
└─ SERVER/
   ├─ app-server/            # ✅ FastAPI 기반 BFF / 메인 API 게이트웨이
   ├─ iot-data-server/       # ✅ IoT 데이터 수집 / 조회 서버
   ├─ ros2-server/           # ✅ ROS2 ↔ HTTP/gRPC 브리지 서버
   └─ path-planning-server/  # ⚠️ 경로계획 서버 (데모 코드만 존재)
```

**상태 표시**: ✅ 구현됨 | ⚠️ 부분 구현 | ❌ 계획됨

## 🔍 컴포넌트 상세 설명

### IOT ✅
- `arduino/`: Arduino 기반 IoT 디바이스 펌웨어 및 제어 코드

### DEEP_LEARNING ✅
- `deep-learning-server/`: 딥러닝 모델 학습 및 추론을 위한 서버
  - ArUco 마커 감지
  - 얼굴 인식 (YOLO 기반)
  - OCR 감지 및 인식

### AI ✅
- `llm-gateway/`: OpenAI API 프록시 서버 및 음성 인터페이스
  - STT (Speech-to-Text): OpenAI Whisper
  - ChatGPT 통합
  - TTS (Text-to-Speech): OpenAI TTS
  - WebSocket 기반 실시간 통신
  - Redis 세션 관리

### APP ⚠️
- `gui/`: PyQt 기반 로봇 제어 GUI (부분 구현)

### ROS2 ✅
- `pinky_pro/`: Pinky 로봇 ROS2 패키지 모음
- `rfred/`: RFred 로봇 ROS2 패키지 모음
- `util/`: 카메라 수신/송신 유틸리티

### SERVER ✅
- `app-server/`: FastAPI 기반 Backend-for-Frontend (BFF) 및 메인 API 게이트웨이
  - ML 레지스트리 API
  - 스케줄러 시스템
  - 알림 시스템 (WebSocket)
  - 관리자 패널 (SQLAdmin)
  - 로봇 감지 이벤트 API
- `iot-data-server/`: IoT 디바이스 데이터 수집 및 조회 서비스
  - 57개 이상의 API 엔드포인트
  - 센서 데이터 수집 및 관리
  - 사용자 및 디바이스 관리
- `ros2-server/`: ROS2와 HTTP/gRPC 간의 브리지 서버
  - Pinky 로봇 제어 패키지
  - LCD 디스플레이 제어
  - 감정 표현 제어

### SERVER ⚠️
- `path-planning-server/`: 경로계획 서버 (데모 코드만 존재)
  - extract_corner 폴더에 데모 코드 3개 파일
  - A* / D* Lite 알고리즘 구현 예정