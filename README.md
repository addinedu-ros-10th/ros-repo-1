# ros-repo-1
파이널 프로젝트 1조 저장소. 요양원이 살아있다. (로봇 케어 요양원)

# 🧠 Multi-Domain Robotics-AI Monorepo

본 레포지토리는 IoT 센서, 딥러닝 서버, 로봇 경로계획, LLM 연동 서비스까지
포함한 **통합 AI·로보틱스 플랫폼**의 개발 환경을 제공합니다.

## 📖 발표자료

**상세 발표자료**: [`docs/[Korean]Smart Nursing Home AI Robot - R-Fred.pdf`](docs/[Korean]Smart%20Nursing%20Home%20AI%20Robot%20-%20R-Fred.pdf)

본 README는 발표자료의 주요 내용을 요약하여 제공합니다.

---

## 👥 팀 소개

**Team: R-FRED** - 기술과 인문학을 연결하는 팀

| 역할 | 담당자 | 주요 책임 |
|------|--------|----------|
| **TEAM LEAD** | Jeong Gyu-ho | • Service Planning<br>• ROS2 Emotion/UI<br>• LLM Interface<br>• Server & DB Architecture |
| **DRIVING & CONTROL** | Park Soo-hyun | • ROS2 Navigation<br>• Nav2 Tuning<br>• State Machine<br>• Set Construction |
| **PATH FINDING** | Park Jae-o | • A* Implementation<br>• Rectangular Tuning<br>• Algorithm Optimization<br>• Simulation-based Environment Modeling |
| **VISION AI** | Shin Dong-jin | • Deep Learning (YOLO)<br>• IbVS / IoU Tracking<br>• Feedback Control<br>• Precision Docking |
| **IOT & GUI** | Jeong Tae-min | • IoT Hardware Config<br>• REST API<br>• GUI<br>• System Prompt |

---

## 🎯 프로젝트 배경 및 필요성

### 사회적 배경

#### 고령화 현실
- **2025년**: 65세 이상 인구가 전체의 20% 이상 (초고령 사회 진입)
- **출처**: 통계청 (kostat.go.kr)

#### 요양원 현황
- **29.1%**: 요양원 거주자의 우울증 유병률
- **출처**: 보건복지부 (mohw.go.kr)

#### 시장 규모
- **글로벌 시장**: $4.4B (2024) → 2040년 4배 성장 예상
- **출처**: Fortune Business Insights

### 경쟁사 분석

#### 해외 경쟁사
- **일본**: PARO (감정 치료 로봇) - 정적, 감정 중심
- **유럽/글로벌**: Temi (텔레프레즌스 & 가이드) - 이동, 기능 중심
- **미국/이스라엘**: Elli Q (능동적 동반자) - 정적, 능동적

#### 국내 시장 (한국)
- **AI 케어 인형**: 효돌 등 - 감정 중심, 정적, 기능 부족
- **물류 로봇**: 이동, 기능 중심, 감정 부족
- **Missing Link**: 감정과 기능을 통합한 모바일 솔루션 부재

### 전략적 포지셔닝

R-Fred는 **감정과 기능을 통합한 모바일 스마트 케어 솔루션**으로, 기존 시장의 공백을 메웁니다.

**핵심 가치**: "More Than a Robot, A Partner in Care"
- 로보틱스는 물리적 노동과 감정적 연결 사이의 다리 역할을 할 수 있습니다.

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

---

## 🎯 주요 기능 시나리오

### Feature 1: 식사 및 식판 서비스 (Meal & Dish Service)

**서비스 플로우**:
1. **Kitchen Load Trays**: 주방에서 식판 적재
2. **Table Precision Docking**: 식탁 정밀 도킹 (10cm 이내 정밀도)
3. **Dish Return Auto Collection**: 식판 반납 자동 수집

**서비스 트리거**: 음성 명령 "식당으로 식판 가져다줘"

**핵심 기술**:
- **State Machine**: 정적 맵 기반 경로 계획
- **A* Tuning**: 90도 직각 회전 최적화
- **Cooperation**: 로봇과 요양원 직원 간 협업
- **360도 LiDAR**: 50cm 반경 장애물 감지
- **정밀 도킹**: YOLO BBOX 기반 PD 제어

---

### Feature 2: 야간 순찰 및 안전 (Night Patrol & Safety)

**서비스 트리거**: 
- 스케줄 기반: "밤에 순찰해줘"
- 음성 명령: "지금 순찰해줘"

**감지 기능**:
1. **YOLO 전신 인식 + LSTM**: 낙상 위험 감지
   - **성능**: 80% Success Rate, 0.85 F1-Score (Fall Class)
   - **3가지 상태**: Normal / Warning / Fall
   - **0% Critical Failure**: 낙상 감지 누락 없음
2. **YOLO 얼굴 인식 + 추적**: 배회 위험 감지
3. **구역 모니터링**: 위험 구역 진입 감지 및 음성 알림

**배경 연구**: 배회 위험 연구 (ncbi.nlm.nih.gov 참조)

---

### Feature 3: 통합 케어 (Integrated Care)

**서비스 트리거**: 음성 명령 "대화하면서 따라다녀줘"

**서비스 플로우**:
1. **음성 트리거 (Voice Trigger)**: Wake-up Keyword 인식
2. **LLM 능동적 대화 (LLM Proactive)**: ChatGPT 기반 자연어 처리
3. **추종 및 대화 (Following & Talking)**: Target Tracking으로 사용자 추적
4. **감정 분석**: 대화 내용 기반 감정 분석 및 로깅
5. **감정 표현**: Happy 상태 표시 및 LCD 디스플레이 업데이트

**핵심 가치**: "More Than a Robot, A Partner in Care"
- 물리적 노동과 감정적 연결의 다리 역할
- 24/7 지속 가능한 케어 제공

---

## 🏗️ 시스템 아키텍처

### 계층 구조

```
┌─────────────────────────────────────────┐
│         Service Layer                   │
│  OpenAI GPT (LLM), STT/TTS, Web Dashboard │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         Perception Layer                 │
│  YOLO v8 (얼굴/전신), IoU Tracking, ArUco │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│          Control Layer                  │
│  ROS2 Jazzy, Nav2, A* (직각 튜닝), State Machine │
└─────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────┐
│         Hardware Layer                  │
│  mobility, Camera, IoT (ESP32), Postgres + TimescaleDB │
└─────────────────────────────────────────┘
```

### 통신 아키텍처

```
GUI
  ↕ HTTP/TCP
Main Server (Central Service)
  ↕ HTTP/TCP
AI Server
  ↕ HTTP
LLM Service
  ↕ WebRTC
Streaming Service
  ↕ TCP
IoT Living Room Controller
  ↕ ROS
Robot Controller Voice Processor
  ↕ HTTP
Robot
  ↕ UDP
Camera
```

### 요구사항 매핑 (UR → SR → Tech Solution)

| 사용자 요구사항 (UR) | 시스템 요구사항 (SR) | 기술 솔루션 |
|---------------------|---------------------|------------|
| UR-1: "식당으로 식판을 가져다줘" | SR-04: Nav2 Waypoint + Payload Mgmt | Nav2 경로 계획 + 페이로드 관리 |
| UR-9: "밤에 순찰해줘" | SR-15: State Machine + YOLO Detection | State Machine + YOLO 감지 |
| UR-12: "위험 구역에 들어가면 알려줘" | SR-12: Zone Check + Voice Alert | 구역 체크 + 음성 알림 |
| UR-4: "대화하면서 따라다녀줘" | SR-09: LLM Context + Emotion Log | LLM 컨텍스트 + 감정 로그 |

---

## 🔧 핵심 기술 스택 상세

### AI/ML 기술

#### 1. 낙상 감지 AI (Fall Detection AI)
- **기술**: LSTM 기반 시계열 분석
- **3가지 상태 분류**:
  - **Normal**: 정상 상태 (걷기, 서기, 앉기)
  - **Warning**: 경고 상태 (0.3 ~ 1.0초 이상 지속되는 비정상 자세)
  - **Fall**: 낙상 (0.5 ~ 1초 이상 지속되는 낙상 자세)
- **데이터**: 3,000+ 이미지, 다양한 자세/환경/각도
- **성능**: 80% Success Rate, 0.85 F1-Score (Fall Class), 0% Critical Failure

#### 2. 비전 AI 파이프라인
- **YOLO v8n 선택**: 5.36ms 추론 시간 (v11n 대비 1.74ms 빠름)
- **ArUco 마커**: 메타데이터 및 위치 인식
- **IoU Tracking**: 객체 추적 안정성 향상
- **정밀 도킹**: YOLO BBOX 기반 PD 제어

#### 3. LLM 물리적 AI 통합
- **음성 인터페이스**: Wake-up Word + STT Pipeline
- **함수 호출**: 자연어 → 구조화된 JSON 명령 변환
- **하이브리드 프로토콜**: ROS2 로봇 (gRPC-web) + 소프트웨어 (REST API)
- **시스템 프롬프트**: 케어 페르소나 AI, GDS (Geriatric Depression Scale) 기반 심리 분석

### 로보틱스 기술

#### 1. 네비게이션 로직
- **A* 90도 각도 튜닝**: 요양원 복도의 직각 구조에 최적화
- **State Machine (RTR)**: Rotate-Translate-Rotate
  - **RotateToGoal**: 목표 방향으로 회전 (IMU Angle Control)
  - **MoveToGoal**: 목표 위치로 이동 (Linear Distance Control)
  - **RotateToFinal**: 최종 방향 정렬 (Heading Alignment)
  - **GoalReached**: 목표 도달

#### 2. 제어 로직 및 센서
- **회전 제어**: IMU 기반 P-Control Loop
- **이동 제어**: Odometry 기반 거리 누적
- **P-Control 핵심 로직**: 오차에 비례한 제어 (큰 오차 → 빠른 속도, 작은 오차 → 느린 속도)
- **엔지니어링 결정**: Integral (I) 제외 (Min Velocity로 해결), Derivative (D) 제외 (마찰로 인해 불필요)

#### 3. 정밀 도킹 및 벽 추종
- **정밀 도킹**: YOLO BBOX 기반 PD 제어 (식탁 10cm 이내 정밀도)
- **벽 추종**: LiDAR 기반 Hybrid PD 제어
  - **각도 오차**: PD 제어 (안정성)
  - **거리 오차**: P 제어 (위치 제어)
  - **진화 과정**: v1 (P-only, 진동) → v2 (Full PD, 복잡) → v3 (Hybrid, 최종)

### IoT 기술

#### IoT 제어 및 REST API
- **플로우**: User (Voice/Remote) → LLM (Intent Analysis) → RestAPI (FastAPI Proxy) → ESP32 (Arduino Server) → Smart Device Control
- **이중 인터페이스**: 원격 제어 + LLM 통합
- **도어 & 전원 제어**: 자동 문 제어, 조명 제어
- **REST API 선택 이유**: Function Call과의 통합 용이, ESP32 WebServer + ArduinoJson 구조
- **네트워크**: 2.4GHz Wi-Fi

### 데이터베이스

#### TimescaleDB 로그 스키마
- **목적**: 고빈도 쓰기 및 시계열 분석을 위한 환자 건강 트렌드 분석
- **필드**: time (TIMESTAMPTZ), event_type (VARCHAR), value_json (JSONB), robot_id (INT)
- **이벤트 타입**: FALL, EMOTION 등

#### LLM 제어 파이프라인
- **구현**: Python을 사용하여 비구조화된 음성 입력을 구조화된 ROS2 액션으로 연결
- **데이터 흐름**: Voice Input → STT → LLM (Function Calling) → JSON CMD → ROS2 Actions

---

## 🔬 기술적 철학 및 선택 이유

### 기술 선택 철학

**"안정성 우선" (Stability Over Speed)**
- 요양원 환경은 정적(Static) 환경
- 안정적인 기술(Stable Tech) 선택을 우선시
- 속도보다는 신뢰성과 안정성 중시

### 기술 선택 상세

#### 비전 및 인식
- **YOLO v8 선택**: Faster R-CNN 대비 빠른 속도, 실시간 처리 가능
- **ArUco + YOLO**: 메타데이터 및 위치 인식, 정밀 제어
- **IoU 로직**: P-Control과 함께 안정적인 객체 추적

#### 네비게이션
- **Nav2 Stack (ROS2 표준)**: ROS2 생태계, SLAM/Nav 통합
- **A* + 직각 튜닝**: 요양원 복도에 최적화
- **State Machine**: 정밀 제어 및 예측 가능한 동작
- **Dijkstra / D* Lite**: 시나리오별 제외 (복잡도 대비 효과 낮음)

#### 인텔리전스 (LLM)
- **OpenAI GPT + FC (현재)**: Function Calling으로 안정적인 JSON 출력, PoC 완료
- **Chain of Thought (CoT) (향후)**: 추론 능력 향상, 복잡한 의사결정 지원

#### 인프라 및 데이터
- **TCP / HTTP 프로토콜**: MQTT 대신 선택 (안정성 및 통합 용이성)
- **ESP32 / Arduino 디바이스**: 저비용, 다양한 센서 지원, MCU 기반
- **TimescaleDB 저장소**: 시계열 데이터, 장기 건강 트렌드 분석에 최적화

---

## ✅ 프로토타입 검증

### 검증 내용

**시뮬레이션뿐만 아니라 실제 검증**:
- ✅ **순찰 (Patrol)**: 야간 순찰 기능 검증
- ✅ **배달 (Delivery)**: 식판 배달 기능 검증
- ✅ **대화 (Dialogue)**: 음성 대화 기능 검증

### 검증 결과
- **물리적 요양원 세트**: 실제 환경에서 검증 완료
- **다중 도메인 작업**: 단일 로봇으로 여러 작업 수행 가능 입증
- **필드 테스트 준비**: 자동화 시스템의 실용성 입증

---

## 🖥️ GUI 및 대시보드

### 실시간 비디오 모니터링 GUI

**기술 스택**: PyQt + OpenCV

**다중 패널 통합 제어**:
- 실시간 비디오 스트리밍 (OpenCV)
- 로봇 상태 모니터링
- 제어 인터페이스

---

## 🚀 향후 로드맵

### 도전 과제 및 해결책

| 도전 과제 | 기술적 해결책 |
|----------|--------------|
| 좁고 정적인 복도 | A* 직각 튜닝으로 부드러운 90도 회전 |
| 정밀 도킹 | IbVS + ArUco로 픽셀 단위 정렬 |
| 복잡한 명령 | LLM Function Calling으로 구조화된 제어 |
| 장기 데이터 | TimescaleDB로 건강 트렌드 분석 |

### 향후 계획

#### Phase 2: MAPF (Multi-Agent Path Finding)
- **목적**: 다중 로봇 조정
- **기술**: Conflict-Based Search (CBS)로 3대 이상 로봇 조정
- **참고**: arXiv:1901.09824

#### Phase 3: Edge AI
- **목적**: 온디바이스 추론 (NVIDIA Jetson Orin Nano)
- **이점**: 프라이버시 및 오프라인 안전성
- **기술**: YOLO, LSTM을 Orin Nano에서 실행

#### O&M 플랫폼 통합
- **Step 1**: 초기 프로토타입
- **Step 2**: 플릿 관리 (Fleet Management)
- **Step 3**: HVAC, 조명, IoT 통합

### 기술 전략: 진화 로드맵

#### System Prompting (현재)
- **속도**: 즉각적인 반복
- **유연성**: 로직 수정 용이
- **제한**: 토큰 비용 및 지연 시간
- **용도**: "로직 검증에 최적"

#### LLM Fine-Tuning (향후)
- **정확도**: 도메인 특화 지식 (의료/케어)
- **프라이버시**: 온프레미스 SLM (Llama 3)
- **효율성**: 낮은 지연 시간
- **용도**: "실제 배포에 최적화"

### LLM: Chain of Thought (CoT)

**현재**: OpenAI Function Calling으로 안정적인 JSON 출력

**향후**: 온프레미스 LLM으로 CoT 마이그레이션 계획

**예시**:
- 사용자: "어지러워요, 간병인을 불러주세요"
- LLM 추론:
  1. 키워드: "어지러움" → 응급 상황
  2. 액션: 간병인 호출
  3. 보조: 간병인실로 이동

---

## 📊 프로젝트 성과

### 구현 완료 기능

1. ✅ **음성 인터페이스**: STT + ChatGPT + TTS 통합
2. ✅ **딥러닝 인식**: 4가지 카테고리 인식 시스템 (ArUco, OCR, Face, Person Tracking)
3. ✅ **IoT 통합**: 25개 이상의 센서 타입 지원
4. ✅ **로봇 제어**: ROS2 기반 자율 주행 및 제어
5. ✅ **백엔드 시스템**: 113개 이상의 API 엔드포인트
6. ✅ **실시간 통신**: WebSocket 기반 알림 시스템
7. ✅ **관리자 패널**: SQLAdmin 기반 웹 인터페이스

### 개발 현황

- **총 파일 수**: 450개 이상
- **API 엔드포인트**: 113개 이상
- **데이터베이스 테이블**: 25개 이상
- **ROS2 패키지**: 10개 이상

### 성능 지표

- **낙상 감지**: 80% Success Rate, 0.85 F1-Score
- **YOLO 추론**: 5.36ms (v8n)
- **정밀 도킹**: 10cm 이내 정밀도
- **벽 추종**: PD 제어로 안정성 확보

---

## 💡 프로젝트 제안 및 시사점

### 1. 실용적 타당성 (Practical Feasibility)

**PoC (Proof of Concept)**:
- 단일 로봇이 다중 도메인 작업 (순찰 + 배달 + 케어) 수행 가능 입증
- 물리적 요양원 세트에서 검증 완료
- **제안**: 자동화 시스템의 필드 테스트 준비 완료

### 2. 표준화된 아키텍처 (Standardized Architecture)

**ROS2 모듈러 설계**:
- Vision Node, Control Node, LLM Service 분리
- 하드웨어 업그레이드 용이 (로봇 베이스, 카메라 교체 시 코어 로직 재작성 불필요)
- **제안**: 모듈러 설계로 유지보수성 및 확장성 확보

### 3. 케어 중심 혁신 (Care-Centric Innovation)

**노동 절감을 넘어서**:
- "인간 대체"가 아닌 "케어 보강"
- 감정 로깅 및 낙상 예방 기능으로 24/7 가치 제공
- **제안**: 케어 중심 설계로 요양원 거주자의 삶의 질 향상

---

## 📚 참고 자료

### 발표자료
- **상세 발표자료**: [`docs/[Korean]Smart Nursing Home AI Robot - R-Fred.pdf`](docs/[Korean]Smart%20Nursing%20Home%20AI%20Robot%20-%20R-Fred.pdf)
- **상세 분석 리포트**: [`docs/RFRED_PDF_DETAILED_ANALYSIS.md`](docs/RFRED_PDF_DETAILED_ANALYSIS.md)

### 외부 참고 자료
- **배회 위험 연구**: ncbi.nlm.nih.gov
- **Path Planning**: https://aieros.atlassian.net/wiki/x/H4Ck
- **A* 알고리즘**: https://sofee.tistory.com/33
- **LiDAR Tracking**: https://wiki.ros.org/lidar_tracking
- **Path Planning**: https://github.com/zhm-real/PathPlanning
- **MAPF**: arXiv:1901.09824

---

## 💡 개발 로그 (Dev Log)

### 문제 해결 사례

#### 비전 AI 팀
**"YOLO 얼굴 인식, 왜 안 돼?"**
- 모델 최적화 및 데이터 증강 과정
- YOLO v8n vs v11n 성능 비교 및 선택

#### 네비게이션 팀
**"Nav2가 너무 느려... IMU+Odom으로 직접 구현"**
- Nav2의 복잡한 튜닝 문제
- IMU + Odometry 기반 직접 구현으로 전환
- State Machine (RTR) 방식으로 정밀도 향상

#### ROS2 팀
**"이제 됐어. Lifecycle 'Active' 확인!"**
- ROS2 생명주기 관리 문제 해결
- 노드 상태 관리 및 안정성 확보

#### LLM 인터페이스 팀
**"음성 인식... 이제 완벽해"**
- STT 파이프라인 최적화
- Wake-up Word 효율성 개선

#### 시스템 통합 팀
**"SW API와 ROS OS... REST와 gRPC 하이브리드!"**
- ROS2 로봇: gRPC-web 사용
- 소프트웨어: REST API 사용
- 하이브리드 프로토콜로 통합

### 근거리 주행 문제 해결

**문제**: 벽 추종 시 비대칭성 (Asymmetry in Wall Following Control)

**Issue 1: Right Wall Collision**
- 오른쪽 벽 충돌 문제
- 센서 오프셋 및 캘리브레이션 문제

**Issue 2: The Drift (Divergence)**
- 발산 문제
- 오차 0에서의 바이어스(Bias) 발생

**해결책: Heuristic Offset**
- 휴리스틱 오프셋 적용
- 비대칭성 보정

**기술 스택**: ROS2 Control, P-Controller, Heuristic Tuning

---

## 🎯 핵심 메시지

**"More Than a Robot, A Partner in Care"**

로보틱스는 물리적 노동과 감정적 연결 사이의 다리 역할을 할 수 있습니다.

R-Fred는 단순한 로봇이 아닌, 요양원 거주자와 직원을 위한 **케어 파트너**입니다.