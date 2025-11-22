# ROS2 연결 문제 해결 가이드

**작성일**: 2025-11-22  
**목적**: `ros2: false` 문제 원인 분석 및 해결 방법

---

## 문제 현상

Health Check 결과:
```json
{
    "status": "degraded",
    "services": {
        "ros2": false,  // ← 문제!
        "iot_data_server": true
    }
}
```

---

## 원인 분석

### 원인 1: Docker 컨테이너 내부에 ROS2가 없음 (가장 흔한 원인)

**증상**:
- Docker 컨테이너 내부에서 `rclpy` import 실패
- `ROS2_AVAILABLE = False`
- 로그: "ROS2가 설치되어 있지 않습니다. 모킹 모드로 동작합니다."

**확인 방법**:
```bash
docker exec ros2-api-server python3 -c "import rclpy"
# ImportError 발생
```

**해결 방법**:
1. **Python 직접 실행** (권장): `run_standalone.py` 사용
2. Dockerfile에 ROS2 설치 추가
3. 호스트 ROS2 볼륨 마운트

---

### 원인 2: ROS2 서비스를 찾을 수 없음

**증상**:
- `rclpy`는 import 가능
- `health_check()`에서 `wait_for_service()` 실패
- 로그: "ROS2 서비스 'lcd_controller/set_display'를 사용할 수 없습니다"

**확인 방법**:
```bash
# 호스트에서 ROS2 서비스 확인
source /opt/ros/humble/setup.bash
source SERVER/ros2-server/install/setup.bash
ros2 service list | grep lcd_controller
```

**예상 출력**:
```
/pinky/lcd_controller/set_display
/pinky/lcd_controller/clear_display
```

**해결 방법**:
1. LCD 컨트롤러 서버 실행 확인
2. 서비스 이름 확인 (네임스페이스 포함)
3. ROS2 도메인 ID 확인 (`ROS_DOMAIN_ID`)

---

### 원인 3: ROS2 도메인 ID 불일치

**증상**:
- 호스트와 컨테이너의 ROS2 도메인 ID가 다름
- 서비스는 실행 중이지만 접근 불가

**확인 방법**:
```bash
# 호스트
echo $ROS_DOMAIN_ID

# 컨테이너
docker exec ros2-api-server env | grep ROS_DOMAIN_ID
```

**해결 방법**:
- `.env.local`에 `ROS_DOMAIN_ID=0` 설정
- 호스트와 컨테이너 모두 동일한 도메인 ID 사용

---

### 원인 4: 네트워크 격리

**증상**:
- `network_mode: "host"`를 사용하지 않음
- Docker 네트워크에서 ROS2 DDS 접근 불가

**해결 방법**:
- `docker-compose.ros2.standalone.yml` 사용 (host 네트워크)
- 또는 Python 직접 실행

---

## 해결 방법

### 방법 1: Python 직접 실행 (권장)

**장점**:
- 호스트의 ROS2 환경 직접 사용
- Docker 설정 불필요
- 디버깅 용이

**사용 방법**:

```bash
cd SERVER/ros2-server/api-server

# 방법 A: Shell 스크립트 사용
./run_standalone.sh

# 방법 B: Python 스크립트 직접 실행
source /opt/ros/humble/setup.bash
source ../install/setup.bash
python3 run_standalone.py
```

**포트 설정**:
- 기본 포트: `8004` (`.env.local`의 `SERVER_PORT` 또는 환경 변수)
- 변경: `export SERVER_PORT=8004` 또는 `.env.local` 수정

---

### 방법 2: Dockerfile에 ROS2 설치

`Dockerfile` 수정:
```dockerfile
FROM python:3.11-slim

# ROS2 설치
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release \
    && curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - \
    && sh -c 'echo "deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list' \
    && apt-get update \
    && apt-get install -y \
    ros-humble-desktop \
    ros-humble-rclpy \
    && rm -rf /var/lib/apt/lists/*

# ... 나머지 설정 ...
```

---

### 방법 3: 호스트 ROS2 볼륨 마운트

`docker-compose.ros2.standalone.yml` 수정:
```yaml
services:
  ros2-api-server:
    volumes:
      - /opt/ros/humble:/opt/ros/humble:ro
      - ../install:/ros2_ws/install:ro
    environment:
      - ROS_DISTRO=humble
```

---

## 진단 스크립트

### ROS2 환경 진단

```bash
#!/bin/bash
echo "=== ROS2 환경 진단 ==="

# 1. ROS2 설치 확인
if [ -d "/opt/ros/humble" ]; then
    echo "✅ ROS2 설치됨: /opt/ros/humble"
else
    echo "❌ ROS2 미설치"
fi

# 2. ROS2 모듈 확인
python3 -c "import rclpy; print('✅ rclpy 사용 가능')" 2>/dev/null || echo "❌ rclpy 사용 불가"

# 3. ROS2 서비스 확인
source /opt/ros/humble/setup.bash 2>/dev/null
source SERVER/ros2-server/install/setup.bash 2>/dev/null
ros2 service list | grep lcd_controller && echo "✅ LCD 컨트롤러 서비스 발견" || echo "❌ LCD 컨트롤러 서비스 없음"

# 4. ROS2 도메인 ID 확인
echo "ROS_DOMAIN_ID: ${ROS_DOMAIN_ID:-0}"
```

---

## 단계별 문제 해결

### Step 1: ROS2 환경 확인

```bash
# 호스트에서
source /opt/ros/humble/setup.bash
source SERVER/ros2-server/install/setup.bash
ros2 service list | grep lcd_controller
```

**예상 출력**:
```
/pinky/lcd_controller/set_display
```

### Step 2: Python 직접 실행 테스트

```bash
cd SERVER/ros2-server/api-server
./run_standalone.sh
```

### Step 3: Health Check 확인

```bash
curl http://localhost:8004/health
```

**예상 결과**:
```json
{
    "status": "healthy",
    "services": {
        "ros2": true,  // ← 성공!
        "iot_data_server": true
    }
}
```

---

## 요약

### 문제 원인 우선순위

1. **Docker 컨테이너 내부에 ROS2 없음** (가장 흔함)
   - 해결: Python 직접 실행

2. **ROS2 서비스 미실행**
   - 해결: LCD 컨트롤러 서버 실행

3. **ROS2 도메인 ID 불일치**
   - 해결: `ROS_DOMAIN_ID` 환경 변수 설정

4. **네트워크 격리**
   - 해결: `network_mode: "host"` 사용

### 권장 해결 방법

**Python 직접 실행** (`run_standalone.sh`):
- ✅ 가장 간단하고 확실한 방법
- ✅ 호스트 ROS2 환경 직접 사용
- ✅ 디버깅 용이
- ✅ 포트 8004 사용

