# 환경 변수 설정 가이드

**작성일**: 2025-01-22  
**목적**: ROS2 API Server 환경 변수 설정 방법 및 각 값 설명

---

## 개요

ROS2 API Server는 `.env.local` 파일을 통해 환경 변수를 설정합니다. 이 문서는 각 환경 변수의 의미와 설정 방법을 설명합니다.

---

## 환경 변수 설정 방법

### 1. .env.local 파일 생성

```bash
cd SERVER/ros2-server/api-server
cp .env.example .env.local
```

### 2. .env.local 파일 편집

필요한 값들을 실제 환경에 맞게 수정합니다.

---

## 환경 변수 상세 설명

### 서버 설정

#### `SERVER_HOST`
- **설명**: 서버가 바인딩할 호스트 주소
- **기본값**: `0.0.0.0`
- **설정 값**: 
  - `0.0.0.0`: 모든 네트워크 인터페이스에서 접근 가능 (Docker 권장)
  - `127.0.0.1`: 로컬호스트만 접근 가능
- **변경 필요**: ❌ 일반적으로 변경 불필요

#### `SERVER_PORT`
- **설명**: 서버 내부 포트 (Docker 컨테이너 내부)
- **기본값**: `8000`
- **설정 값**: 
  - `8000`: 기본값 (권장)
  - 다른 포트: 다른 서비스와 충돌 시 변경
- **변경 필요**: ❌ 일반적으로 변경 불필요
- **참고**: 외부 포트는 `docker-compose.yml`에서 `8003`으로 설정됨

#### `DEBUG`
- **설명**: 디버그 모드 활성화 여부
- **기본값**: `false`
- **설정 값**:
  - `false`: 프로덕션 모드 (권장)
  - `true`: 개발 모드 (자동 리로드, 상세 로그)
- **변경 필요**: 개발 중에만 `true`로 설정

---

### iot-data-server API 설정

#### `IOT_DATA_SERVER_URL`
- **설명**: iot-data-server API 서버의 URL
- **기본값**: `http://iot-data-server:8000`
- **설정 값**:
  - **Docker Compose 환경**: `http://iot-data-server:8000` (같은 Docker 네트워크 내)
  - **외부 서버**: `http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com`
  - **로컬 개발**: `http://localhost:8000` (iot-data-server가 로컬에서 실행 중인 경우)
- **변경 필요**: ✅ **반드시 설정 필요**
- **확인 방법**:
  ```bash
  # 외부 서버 확인
  curl http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com/health
  
  # 로컬 서버 확인
  curl http://localhost:8000/health
  ```

**권장 설정**:
```bash
# 운영 환경 (외부 서버 사용)
IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com

# 또는 Docker Compose로 iot-data-server도 함께 실행하는 경우
IOT_DATA_SERVER_URL=http://iot-data-server:8000
```

---

### ROS2 설정

#### `ROS2_NAMESPACE`
- **설명**: ROS2 네임스페이스
- **기본값**: `/pinky`
- **설정 값**:
  - `/pinky`: 기본값 (Pinky 로봇)
  - 다른 네임스페이스: 다른 로봇 사용 시
- **변경 필요**: ❌ 일반적으로 변경 불필요

#### `ROS2_SERVICE_TIMEOUT`
- **설명**: ROS2 서비스 호출 타임아웃 (초)
- **기본값**: `2.0`
- **설정 값**:
  - `2.0`: 기본값 (권장)
  - 더 큰 값: 네트워크 지연이 큰 경우
- **변경 필요**: ❌ 일반적으로 변경 불필요

#### `ROS2_SERVICE_NAME`
- **설명**: LCD 제어를 위한 ROS2 서비스 이름
- **기본값**: `lcd_controller/set_display`
- **설정 값**:
  - `lcd_controller/set_display`: 기본값 (권장)
  - 다른 서비스: 커스텀 서비스 사용 시
- **변경 필요**: ❌ 일반적으로 변경 불필요

**참고**: ROS2 환경이 없는 경우, API 서버는 모킹 모드로 동작하며 `display_sent: false`로 응답합니다.

---

### Redis 설정 (선택적)

#### `REDIS_HOST`
- **설명**: Redis 서버 호스트
- **기본값**: `redis`
- **설정 값**:
  - `redis`: Docker Compose 환경 (권장)
  - `localhost`: 로컬 개발
  - 다른 호스트: 외부 Redis 서버
- **변경 필요**: ❌ Docker Compose 사용 시 변경 불필요

#### `REDIS_PORT`
- **설명**: Redis 서버 포트 (내부 포트)
- **기본값**: `6379`
- **설정 값**:
  - `6379`: 기본값 (권장)
  - 다른 포트: 커스텀 설정 시
- **변경 필요**: ❌ 일반적으로 변경 불필요
- **참고**: 외부 포트는 `docker-compose.yml`에서 `16381`로 설정됨

#### `REDIS_PASSWORD`
- **설명**: Redis 비밀번호
- **기본값**: (비어있음)
- **설정 값**:
  - (비어있음): 비밀번호 없음 (개발 환경)
  - 비밀번호: 프로덕션 환경
- **변경 필요**: ⚠️ 프로덕션 환경에서는 설정 권장

#### `REDIS_ENABLED`
- **설명**: Redis 사용 여부
- **기본값**: `false`
- **설정 값**:
  - `false`: Redis 사용 안 함 (기본값)
  - `true`: Redis 사용 (캐싱, 세션 관리)
- **변경 필요**: ⚠️ Redis 기능이 필요한 경우에만 `true`로 설정

**참고**: 현재 버전에서는 Redis가 선택적 기능입니다. 기본적으로는 사용하지 않아도 됩니다.

---

### CORS 설정

#### `CORS_ORIGINS`
- **설명**: CORS 허용 오리진 목록 (쉼표로 구분)
- **기본값**: `*`
- **설정 값**:
  - `*`: 모든 오리진 허용 (개발 환경)
  - 특정 도메인: `http://localhost:3000,https://example.com` (프로덕션)
- **변경 필요**: ⚠️ 프로덕션 환경에서는 특정 도메인만 허용 권장

**예시**:
```bash
# 개발 환경
CORS_ORIGINS=*

# 프로덕션 환경
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

### Caddy 설정

#### `CADDY_HTTP_PORT`
- **설명**: Caddy HTTP 외부 포트
- **기본값**: `8080`
- **설정 값**:
  - `8080`: 기본값 (80 포트와 충돌 방지)
  - `80`: 표준 HTTP 포트 (다른 서비스와 충돌 없을 경우)
- **변경 필요**: ❌ 일반적으로 변경 불필요

#### `CADDY_HTTPS_PORT`
- **설명**: Caddy HTTPS 외부 포트
- **기본값**: `8443`
- **설정 값**:
  - `8443`: 기본값 (443 포트와 충돌 방지)
  - `443`: 표준 HTTPS 포트 (다른 서비스와 충돌 없을 경우)
- **변경 필요**: ❌ 일반적으로 변경 불필요

**참고**: Caddy는 SSL/TLS 자동 적용을 위한 리버스 프록시입니다. 직접 FastAPI 서버에 접근할 경우 `8003` 포트를 사용하세요.

---

### 로깅 설정

#### `LOG_LEVEL`
- **설명**: 로그 레벨
- **기본값**: `INFO`
- **설정 값**:
  - `DEBUG`: 상세한 디버그 정보
  - `INFO`: 일반 정보 (권장)
  - `WARNING`: 경고만 표시
  - `ERROR`: 오류만 표시
- **변경 필요**: ❌ 일반적으로 변경 불필요

---

## 최소 필수 설정

가장 기본적인 설정만으로도 서버를 실행할 수 있습니다:

```bash
# .env.local 파일 최소 설정

# iot-data-server URL (필수)
IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com

# 나머지는 기본값 사용
```

---

## 환경별 설정 예시

### 개발 환경

```bash
# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=true

# iot-data-server (로컬 또는 외부)
IOT_DATA_SERVER_URL=http://localhost:8000
# 또는
# IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com

# ROS2 (로컬 개발 시 모킹 모드)
ROS2_NAMESPACE=/pinky
ROS2_SERVICE_TIMEOUT=2.0

# Redis (선택적)
REDIS_ENABLED=false

# CORS (개발 환경)
CORS_ORIGINS=*

# 로깅
LOG_LEVEL=DEBUG
```

### 프로덕션 환경

```bash
# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# iot-data-server (외부 서버)
IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com

# ROS2
ROS2_NAMESPACE=/pinky
ROS2_SERVICE_TIMEOUT=2.0

# Redis (필요한 경우)
REDIS_ENABLED=true
REDIS_PASSWORD=your_secure_password

# CORS (특정 도메인만 허용)
CORS_ORIGINS=https://yourdomain.com

# 로깅
LOG_LEVEL=INFO
```

### Docker Compose 환경

```bash
# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=false

# iot-data-server (Docker 네트워크 내)
IOT_DATA_SERVER_URL=http://iot-data-server:8000
# 또는 외부 서버
# IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com

# ROS2
ROS2_NAMESPACE=/pinky
ROS2_SERVICE_TIMEOUT=2.0

# Redis
REDIS_ENABLED=false
REDIS_HOST=redis
REDIS_PORT=6379

# CORS
CORS_ORIGINS=*

# 로깅
LOG_LEVEL=INFO
```

---

## 설정 확인 방법

### 1. 환경 변수 로드 확인

서버 실행 후 로그에서 환경 변수가 올바르게 로드되었는지 확인:

```bash
docker-compose logs ros2-api-server | grep -i "config\|setting"
```

### 2. 헬스 체크로 연결 확인

```bash
curl http://localhost:8003/health
```

응답에서 `iot_data_server` 상태를 확인할 수 있습니다.

### 3. iot-data-server 연결 테스트

```bash
# .env.local에 설정한 URL 확인
curl http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com/health
```

---

## 문제 해결

### 문제 1: iot-data-server 연결 실패

**증상**: 헬스 체크에서 `iot_data_server: false`

**해결**:
1. `.env.local`에서 `IOT_DATA_SERVER_URL` 확인
2. URL이 올바른지 확인:
   ```bash
   curl $IOT_DATA_SERVER_URL/health
   ```
3. Docker 네트워크 확인 (Docker Compose 사용 시)

### 문제 2: ROS2 서비스 연결 실패

**증상**: `ros2: false` (헬스 체크)

**해결**:
- ROS2 환경이 없는 경우: 정상 동작 (모킹 모드)
- ROS2 환경이 있는 경우:
  1. ROS2 서비스 확인: `ros2 service list | grep lcd_controller`
  2. 네트워크 설정 확인 (Docker 컨테이너에서 ROS2 접근)

### 문제 3: 포트 충돌

**증상**: `Bind for 0.0.0.0:8003 failed: port is already allocated`

**해결**:
1. 포트 사용 중인 프로세스 확인:
   ```bash
   sudo lsof -i :8003
   ```
2. 다른 포트 사용:
   - `docker-compose.yml`에서 포트 매핑 변경
   - 또는 사용 중인 프로세스 종료

---

## 빠른 시작

### 1. .env.local 파일 생성

```bash
cd SERVER/ros2-server/api-server
cat > .env.local << 'EOF'
# 최소 필수 설정
IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com

# 나머지는 기본값 사용
EOF
```

### 2. 서버 실행

```bash
docker-compose up -d --build
```

### 3. 확인

```bash
# 헬스 체크
curl http://localhost:8003/health

# API 문서
# 브라우저에서 http://localhost:8003/docs 접속
```

---

## 요약

### 반드시 설정해야 하는 값
- ✅ `IOT_DATA_SERVER_URL`: iot-data-server API URL

### 선택적으로 설정하는 값
- ⚠️ `DEBUG`: 개발 중에만 `true`
- ⚠️ `REDIS_ENABLED`: Redis 기능이 필요한 경우 `true`
- ⚠️ `CORS_ORIGINS`: 프로덕션 환경에서는 특정 도메인만 허용
- ⚠️ `REDIS_PASSWORD`: 프로덕션 환경에서 Redis 사용 시

### 기본값 사용 권장
- ❌ 나머지 모든 값: 기본값 사용 권장

---

## 참고

- 환경 변수는 `.env.local` 파일에 저장되며, Git에 커밋되지 않습니다 (`.gitignore`에 포함)
- `.env.example`은 예시 파일이며, 실제로는 사용되지 않습니다
- Docker Compose는 `.env.local` 파일을 자동으로 로드합니다

