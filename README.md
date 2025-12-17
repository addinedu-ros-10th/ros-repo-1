# ros-repo-1
파이널 프로젝트 1조 저장소. 요양원이 살아있다. (로봇 케어 요양원)

# 🧠 Multi-Domain Robotics-AI Monorepo

본 레포지토리는 IoT 센서, 딥러닝 서버, 로봇 경로계획, LLM 연동 서비스까지
포함한 **통합 AI·로보틱스 플랫폼**의 개발 환경을 제공합니다.

---

## 📂 프로젝트 구성

| 구분 | 위치 | 주요 기술 | 역할 |
|------|------|------------|------|
| IOT | `IOT/arduino` | C++, Arduino | 센서/액추에이터 제어 펌웨어 |
| DEEP_LEARNING | `DEEP_LEARNING/deep-learning-server` | PyTorch, FastAPI | 모델 추론/학습 서버 |
| AI | `AI/llm-gateway`, `AI/mcp-server` | Python, FastAPI | LLM 호출 및 내부 API 노출 |
| APP | `APP/web-app`, `APP/web-page` | Flutter, HTML/JS | 사용자용 웹 인터페이스 |
| SERVER | `SERVER/*` | FastAPI, ROS2, MQTT, vLLM | 백엔드 서비스 그룹 |

## 📁 상세 디렉토리 구조

```
repo-root/
├─ IOT/
│  └─ arduino/                # Arduino 기반 IoT 디바이스 코드
│
├─ DEEP_LEARNING/
│  └─ deep-learning-server/   # 딥러닝 모델 학습 및 추론 서버
│
├─ AI/
│  ├─ llm-gateway/           # OpenAI 프록시 및 제어 (요청·로그·비용 관리)
│  └─ mcp-server/            # LLM용 MCP 브리지 (LLM → 내부 API 호출)
│
├─ APP/
│  ├─ web-app/               # Flutter Web 기반 서비스 UI
│  └─ web-page/              # HTML/JS 정적 페이지
│
└─ SERVER/
   ├─ app-server/            # FastAPI 기반 BFF / 메인 API 게이트웨이
   ├─ iot-data-server/       # IoT 데이터 수집 / 조회 서버
   ├─ local-hub/             # MQTT / RTSP / WS 엣지 허브
   ├─ ros2-server/           # ROS2 ↔ HTTP/gRPC 브리지 서버
   ├─ vllm-server/           # OpenAI + vLLM 모델 서빙 서버
   ├─ path-planning-server/  # A* / D* Lite 기반 경로계획 서버
   └─ sim-resource-server/   # RViz / Gazebo 맵·월드 자산 관리 서버
```

## 🔍 컴포넌트 상세 설명

### IOT
- `arduino/`: Arduino 기반 IoT 디바이스 펌웨어 및 제어 코드

### DEEP_LEARNING
- `deep-learning-server/`: 딥러닝 모델 학습 및 추론을 위한 서버

### AI
- `llm-gateway/`: OpenAI API 프록시 서버. 요청, 로그, 비용 관리 기능 제공
- `mcp-server/`: LLM Model Context Protocol 브리지. LLM과 내부 API 연동

### APP
- `web-app/`: Flutter Web 기반의 메인 서비스 UI
- `web-page/`: HTML/JS 기반 정적 웹페이지

### SERVER
- `app-server/`: FastAPI 기반 Backend-for-Frontend (BFF) 및 메인 API 게이트웨이
- `iot-data-server/`: IoT 디바이스 데이터 수집 및 조회 서비스
- `local-hub/`: MQTT, RTSP, WebSocket 기반 엣지 컴퓨팅 허브
- `ros2-server/`: ROS2와 HTTP/gRPC 간의 브리지 서버
- `vllm-server/`: OpenAI 호환 vLLM 기반 모델 서빙 서버
- `path-planning-server/`: A* 및 D* Lite 알고리즘 기반 경로 계획
- `sim-resource-server/`: RViz 및 Gazebo 시뮬레이션 자원 관리 서버