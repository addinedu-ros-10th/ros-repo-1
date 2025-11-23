# ROS2-Server FastAPI 서버 구축 계획서

**작성일**: 2025-01-22  
**목적**: Deep Learning 컴포넌트가 호출할 수 있는 FastAPI 서버 구축

---

## 개요

ROS2-Server 프로젝트에 FastAPI 기반 API 서버를 구축하여, Deep Learning 컴포넌트(YOLO 등)가 어르신 탐지 시 로봇 LCD에 정보를 표시할 수 있도록 합니다.

---

## 요구사항

### 기능 요구사항
1. **어르신 탐지 API**: DL 컴포넌트가 어르신을 탐지했을 때 호출
2. **어르신 정보 조회**: iot-data-server의 API를 통해 어르신 정보 조회
3. **LCD 표시**: ROS2 서비스를 통해 로봇 LCD에 정보 표시
4. **세션 관리**: Redis를 통한 탐지 이벤트 관리 (필요시)

### 기술 요구사항
- ✅ Docker Compose 기반
- ✅ FastAPI
- ✅ Redis (선택적, 캐싱 및 세션 관리용)
- ✅ Caddy (SSL/TLS 자동 적용)

---

## 프로젝트 구조

### 디렉토리 구조

```
SERVER/ros2-server/
├── api-server/                    # FastAPI 서버 (신규)
│   ├── src/                      # 소스 코드
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 애플리케이션 메인
│   │   ├── config.py             # 환경변수 및 설정 관리
│   │   ├── ros2_client.py        # ROS2 서비스 클라이언트
│   │   ├── iot_data_client.py    # iot-data-server API 클라이언트
│   │   └── models.py             # Pydantic 모델
│   │
│   ├── tests/                    # 테스트 코드
│   │   ├── __init__.py
│   │   ├── conftest.py           # pytest 설정
│   │   └── test_detection.py    # 탐지 API 테스트
│   │
│   ├── docs/                     # 문서
│   │   └── API_DOCUMENTATION.md  # API 문서
│   │
│   ├── docker-compose.yml        # Docker Compose 설정
│   ├── Dockerfile                # Docker 이미지 정의
│   ├── Caddyfile                 # Caddy 설정
│   ├── requirements.txt          # Python 의존성
│   ├── .env.example              # 환경변수 예시
│   └── README.md                 # 프로젝트 README
│
└── ... (기존 ROS2 패키지들)
```

---

## API 엔드포인트 설계

### 1. 어르신 탐지 API (핵심)

#### `POST /api/detection/resident`

**목적**: DL 컴포넌트가 어르신을 탐지했을 때 호출하여 LCD에 정보 표시

**Request Body**:
```json
{
  "user_id": "00000000-0000-0000-0000-000000000001",
  "nickname": "Akaza",  // user_id 또는 nickname 중 하나 필수
  "detection_location": "1층 복도",
  "detection_confidence": 0.95,
  "camera_id": "camera_001",
  "timestamp": "2025-01-22T10:30:00Z",
  "display_format": "basic"  // "basic" | "detailed" | "urgent"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Resident information displayed on LCD",
  "data": {
    "user_id": "00000000-0000-0000-0000-000000000001",
    "name": "정도현",
    "nickname": "Akaza",
    "room": "3층 302호 A번",
    "display_sent": true,
    "lcd_display_data": {
      "title": "Akaza 어르신",
      "lines": [
        "생활실: 3층 302호 A번",
        "상태: 보행기 사용 / 당뇨 관리",
        "주의: 낙상 위험 높음"
      ]
    }
  }
}
```

**동작 흐름**:
1. `user_id` 또는 `nickname`으로 어르신 정보 조회 (iot-data-server API)
2. 어르신 정보 요약 (이름, 생활실, 특이사항)
3. ROS2 서비스를 통해 LCD에 표시
4. 응답 반환

### 2. 건강 체크 API

#### `GET /api/health`

**목적**: 서버 상태 확인

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "ros2": "connected",
    "iot_data_server": "connected",
    "redis": "connected"
  }
}
```

### 3. LCD 표시 상태 조회

#### `GET /api/lcd/status`

**목적**: 현재 LCD에 표시 중인 정보 조회

**Response**:
```json
{
  "current_display": {
    "title": "Akaza 어르신",
    "lines": ["생활실: 3층 302호 A번", "상태: 보행기 사용"],
    "updated_at": "2025-01-22T10:30:00Z"
  }
}
```

---

## 기술 스택

### 1. FastAPI
- **버전**: 최신 안정 버전
- **주요 기능**:
  - 자동 API 문서 생성 (Swagger UI)
  - Pydantic 모델 검증
  - 비동기 처리 지원

### 2. ROS2 통신
- **라이브러리**: `rclpy` (ROS2 Python 클라이언트)
- **서비스 호출**: `pinky_lcd_display_interfaces/srv/SetDisplay`
- **연결 방식**: 
  - 같은 네트워크에서 ROS2 서비스 호출
  - 또는 ROS2 브리지 서버를 통해 통신

### 3. Redis (선택적)
- **용도**:
  - 탐지 이벤트 캐싱 (중복 방지)
  - LCD 표시 상태 저장
  - 세션 관리
- **설정**: llm-gateway와 동일한 구조

### 4. Caddy
- **역할**: SSL/TLS 자동 적용, 리버스 프록시
- **설정**: llm-gateway와 유사한 구조

---

## Docker Compose 구성

### 서비스 구성

```yaml
services:
  # FastAPI 서버
  ros2-api-server:
    build:
      context: ./api-server
      dockerfile: Dockerfile
    container_name: ros2-api-server
    ports:
      - "${SERVER_PORT:-8003}:8000"  # 외부 포트 8003 (llm-gateway:8001, iot-data-server:8000과 충돌 방지)
    expose:
      - "8000"  # Caddy가 내부 네트워크로 접근
    env_file:
      - .env.local
    volumes:
      - ./api-server/logs:/app/logs
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped
    networks:
      - ros2-api-network
    # ROS2 통신을 위한 설정
    # 네트워크 모드: host 또는 ROS2 브리지 서버 사용

  # Redis 컨테이너 (선택적)
  redis:
    image: redis:7-alpine
    container_name: ros2-api-redis
    ports:
      - "${REDIS_EXTERNAL_PORT:-16381}:6379"  # 외부 포트 16381 (llm-gateway:16379와 충돌 방지)
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD-SHELL", "redis-cli ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    networks:
      - ros2-api-network

  # Caddy 리버스 프록시
  # 주의: 80, 443 포트는 다른 프로젝트와 충돌할 수 있음
  # 필요시 다른 포트 사용 (예: 8080:80, 8443:443)
  caddy:
    image: caddy:2-alpine
    container_name: ros2-api-caddy
    ports:
      - "${CADDY_HTTP_PORT:-8080}:80"      # HTTP 포트 (기본 8080)
      - "${CADDY_HTTPS_PORT:-8443}:443"    # HTTPS 포트 (기본 8443)
    volumes:
      - ./api-server/Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config
    depends_on:
      - ros2-api-server
    restart: unless-stopped
    networks:
      - ros2-api-network

volumes:
  caddy-data:
  caddy-config:
  redis-data:

networks:
  ros2-api-network:
    driver: bridge
```

---

## ROS2 통신 방식

### 옵션 1: 직접 ROS2 서비스 호출 (권장)

**전제 조건**:
- FastAPI 서버가 ROS2 환경에 접근 가능
- ROS2 네임스페이스가 설정되어 있음

**구현**:
```python
# ros2_client.py
import rclpy
from rclpy.node import Node
from pinky_lcd_display_interfaces.srv import SetDisplay

class ROS2Client:
    def __init__(self):
        rclpy.init()
        self.node = Node('ros2_api_client')
        self.set_display_client = self.node.create_client(
            SetDisplay,
            'lcd_controller/set_display'
        )
    
    def display_resident_info(self, title, lines, show_timestamp=True):
        request = SetDisplay.Request()
        request.title = title
        request.lines = lines
        request.show_timestamp = show_timestamp
        
        future = self.set_display_client.call_async(request)
        rclpy.spin_until_future_complete(self.node, future, timeout_sec=2.0)
        
        if future.done():
            return future.result()
        return None
```

### 옵션 2: ROS2 브리지 서버 (대안)

**전제 조건**:
- 별도의 ROS2 브리지 서버가 HTTP API를 제공
- FastAPI 서버는 HTTP로 브리지 서버 호출

**구현**:
```python
# ros2_client.py
import httpx

class ROS2BridgeClient:
    def __init__(self, bridge_url: str):
        self.bridge_url = bridge_url
    
    async def display_resident_info(self, title, lines, show_timestamp=True):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.bridge_url}/api/ros2/lcd/display",
                json={
                    "title": title,
                    "lines": lines,
                    "show_timestamp": show_timestamp
                }
            )
            return response.json()
```

**권장**: 옵션 1 (직접 ROS2 서비스 호출)

---

## iot-data-server API 클라이언트

```python
# iot_data_client.py
import httpx
from typing import Optional

class IoTDataClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
    
    async def get_resident_info(self, user_id: Optional[str] = None, 
                               nickname: Optional[str] = None):
        """어르신 정보 조회"""
        if user_id:
            url = f"{self.base_url}/api/residents/{user_id}"
        elif nickname:
            # nickname으로 검색하는 API가 있다면
            url = f"{self.base_url}/api/residents/search?nickname={nickname}"
        else:
            raise ValueError("user_id or nickname required")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, user_id: str):
        """사용자 기본 정보 조회"""
        url = f"{self.base_url}/api/users/{user_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
```

---

## 정보 요약 로직

```python
# resident_info_formatter.py
def format_room_info(resident_data: dict) -> str:
    """생활실 정보 포맷팅"""
    floor = resident_data.get('floor_number', '')
    room = resident_data.get('room_number', '')
    bed = resident_data.get('bed_number', '')
    
    if bed:
        return f"{floor}층 {room}호 {bed}번"
    return f"{floor}층 {room}호"

def summarize_special_notes(resident_data: dict) -> list:
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
    
    # 이동 수준
    mobility = resident_data.get('mobility_level', '')
    if mobility == 'walker':
        notes.append("보행기 사용")
    
    return notes[:3]  # 최대 3개

def format_display_data(resident_data: dict, display_format: str = "basic") -> dict:
    """LCD 표시 데이터 포맷팅"""
    name = resident_data.get("nickname") or resident_data.get("user_name")
    room_info = format_room_info(resident_data)
    special_notes = summarize_special_notes(resident_data)
    
    if display_format == "basic":
        lines = [
            f"생활실: {room_info}",
            f"상태: {resident_data.get('mobility_level', '정상')}",
            f"주의: {special_notes[0]}" if special_notes else ""
        ]
    elif display_format == "detailed":
        # 상세 형식 (5줄)
        lines = [
            f"생활실: {room_info}",
            f"이동: {resident_data.get('mobility_level', '정상')}",
            f"건강: {', '.join(special_notes[:2])}" if special_notes else "정상",
            f"주의: {special_notes[0]}" if special_notes else "주의사항 없음"
        ]
    else:  # urgent
        lines = [
            f"생활실: {room_info}",
            f"⚠️ {special_notes[0]}" if special_notes else "",
            f"보행기 필수 사용" if resident_data.get('mobility_level') == 'walker' else ""
        ]
    
    return {
        "title": f"{name} 어르신",
        "lines": [line for line in lines if line],  # 빈 라인 제거
        "show_timestamp": True
    }
```

---

## 환경 변수 설정

### `.env.example`

```bash
# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000  # 내부 포트 (외부 포트는 8003)
DEBUG=false

# iot-data-server API
IOT_DATA_SERVER_URL=http://iot-data-server:8000
# 또는 외부 URL
# IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com

# ROS2 설정
ROS2_NAMESPACE=/pinky
ROS2_SERVICE_TIMEOUT=2.0

# Redis 설정 (선택적)
REDIS_HOST=redis
REDIS_PORT=6379  # 내부 포트 (외부 포트는 16381)
REDIS_PASSWORD=

# Caddy 설정
CADDY_HTTP_PORT=8080   # HTTP 외부 포트 (기본 80과 충돌 방지)
CADDY_HTTPS_PORT=8443  # HTTPS 외부 포트 (기본 443과 충돌 방지)

# CORS 설정
CORS_ORIGINS=*

# 로깅
LOG_LEVEL=INFO
```

---

## 구현 단계

### Phase 1: 기본 구조 구축 (1일)
1. ✅ 프로젝트 디렉토리 생성
2. ✅ FastAPI 기본 구조 생성
3. ✅ Docker Compose 설정
4. ✅ 기본 헬스 체크 API 구현

### Phase 2: ROS2 통신 구현 (1일)
1. ⏳ ROS2 클라이언트 구현
2. ⏳ LCD 표시 서비스 호출 테스트
3. ⏳ 에러 처리 및 재시도 로직

### Phase 3: iot-data-server 연동 (1일)
1. ⏳ iot-data-server API 클라이언트 구현
2. ⏳ 어르신 정보 조회 및 파싱
3. ⏳ 정보 요약 로직 구현

### Phase 4: 탐지 API 구현 (1일)
1. ⏳ POST /api/detection/resident 구현
2. ⏳ 전체 플로우 통합 테스트
3. ⏳ 에러 처리 및 로깅

### Phase 5: Redis 및 Caddy 설정 (0.5일)
1. ⏳ Redis 통합 (캐싱, 세션 관리)
2. ⏳ Caddy 설정 및 SSL 적용
3. ⏳ 최종 테스트

---

## 테스트 계획

### 단위 테스트
- 정보 요약 로직 테스트
- ROS2 클라이언트 모킹 테스트
- iot-data-server 클라이언트 모킹 테스트

### 통합 테스트
- 전체 플로우 테스트 (탐지 → 정보 조회 → LCD 표시)
- 에러 케이스 테스트

### E2E 테스트
- 실제 ROS2 환경에서 테스트
- 실제 iot-data-server와 연동 테스트

---

## 배포 및 운영

### 배포 방법
1. Docker Compose로 배포
2. 환경 변수 설정 (.env.local)
3. Caddy SSL 인증서 자동 발급

### 모니터링
- 로그 수집 (파일 또는 로그 서비스)
- 헬스 체크 엔드포인트 모니터링
- ROS2 서비스 연결 상태 모니터링

---

## 보안 고려사항

1. **API 인증**: 필요시 API 키 또는 JWT 토큰 인증 추가
2. **CORS 설정**: 프로덕션 환경에서는 특정 도메인만 허용
3. **Rate Limiting**: API 호출 제한 설정
4. **입력 검증**: Pydantic 모델을 통한 엄격한 입력 검증

---

## 다음 단계

1. ✅ 구축 계획 검토 및 승인
2. ⏳ 프로젝트 구조 생성
3. ⏳ 기본 FastAPI 애플리케이션 구현
4. ⏳ ROS2 통신 구현
5. ⏳ iot-data-server 연동
6. ⏳ 탐지 API 구현
7. ⏳ 테스트 및 배포

---

## 참고 자료

- [llm-gateway 프로젝트 구조](AI/llm-gateway/)
- [어르신 정보 LCD 표시 제안서](RESIDENT_INFO_LCD_DISPLAY_PROPOSAL.md)
- [ROS2 서비스 인터페이스](../src/pinky_lcd_display_interfaces/)

