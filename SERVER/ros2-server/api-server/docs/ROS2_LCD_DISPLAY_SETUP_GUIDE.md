# 실제 로봇 LCD 표시 설정 가이드

**작성일**: 2025-11-22  
**목적**: 모킹 모드가 아닌 실제 로봇 LCD에 표시하기 위한 ROS2 환경 설정

---

## 개요

현재 서버는 ROS2 환경이 없어서 모킹 모드로 동작합니다. 실제 로봇 LCD에 표시하려면 ROS2 환경을 설정해야 합니다.

---

## 현재 상태 확인

### Health Check로 확인

```bash
curl http://localhost:8003/health
```

**현재 상태 (모킹 모드)**:
```json
{
    "status": "degraded",
    "services": {
        "ros2": false,  // ← ROS2 없음
        "iot_data_server": true
    }
}
```

**목표 상태 (실제 LCD 표시)**:
```json
{
    "status": "healthy",
    "services": {
        "ros2": true,  // ← ROS2 연결 성공
        "iot_data_server": true
    }
}
```

---

## ROS2 환경 설정 방법

### 방법 1: 호스트 시스템에 ROS2 설치 (권장)

#### 1.1 ROS2 설치

```bash
# Ubuntu 22.04 (ROS2 Humble) 예시
sudo apt update
sudo apt install -y \
    software-properties-common \
    curl \
    gnupg \
    lsb-release

# ROS2 저장소 추가
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -
sudo sh -c 'echo "deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'

# ROS2 Humble 설치
sudo apt update
sudo apt install -y \
    ros-humble-desktop \
    ros-humble-rclpy \
    python3-colcon-common-extensions

# 환경 설정
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

#### 1.2 ROS2 패키지 빌드

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server

# ROS2 패키지 빌드
colcon build --packages-select \
    pinky_lcd_display_interfaces \
    pinky_lcd_display_controller

# 환경 설정
source install/setup.bash
```

#### 1.3 ROS2 서비스 실행

```bash
# 터미널 1: LCD 컨트롤러 서버 실행
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
source install/setup.bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

#### 1.4 Docker 컨테이너에서 호스트 ROS2 접근

**옵션 A: 네트워크 모드 host 사용**

`docker-compose.yml` 수정:
```yaml
services:
  ros2-api-server:
    # ... 기존 설정 ...
    network_mode: "host"  # 호스트 네트워크 사용
    # 또는
    # extra_hosts:
    #   - "host.docker.internal:host-gateway"
```

**옵션 B: ROS2 DDS 네트워크 설정**

`.env.local`에 추가:
```bash
# ROS2 DDS 설정
ROS_DOMAIN_ID=0
RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

**옵션 C: 볼륨 마운트로 ROS2 설치 경로 공유**

`docker-compose.yml` 수정:
```yaml
services:
  ros2-api-server:
    # ... 기존 설정 ...
    volumes:
      - ./logs:/app/logs
      - ./src:/app/src
      - /opt/ros/humble:/opt/ros/humble:ro  # ROS2 설치 경로
      - /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/install:/ros2_ws/install:ro  # 빌드된 패키지
    environment:
      - ROS_DISTRO=humble
      - ROS_DOMAIN_ID=0
      - RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

---

### 방법 2: Docker 컨테이너 내부에 ROS2 설치

#### 2.1 Dockerfile 수정

`Dockerfile`에 ROS2 설치 추가:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

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
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# ROS2 환경 설정
ENV ROS_DISTRO=humble
ENV ROS_DOMAIN_ID=0
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ ./src/

# 환경 변수
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8000

# 서버 실행 (ROS2 환경 포함)
CMD ["bash", "-c", "source /opt/ros/humble/setup.bash && uvicorn src.main:app --host 0.0.0.0 --port 8000"]
```

#### 2.2 ROS2 패키지 빌드 및 복사

```bash
# 호스트에서 ROS2 패키지 빌드
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
colcon build --packages-select \
    pinky_lcd_display_interfaces \
    pinky_lcd_display_controller

# Dockerfile에서 빌드된 패키지 복사하도록 수정
# 또는 docker-compose.yml에서 볼륨 마운트
```

---

## ROS2 서비스 확인

### 1. ROS2 서비스 목록 확인

```bash
# 호스트에서 실행
ros2 service list | grep lcd_controller
```

**예상 출력**:
```
/pinky/lcd_controller/set_display
/pinky/lcd_controller/clear_display
```

### 2. ROS2 서비스 타입 확인

```bash
ros2 service type /pinky/lcd_controller/set_display
```

**예상 출력**:
```
pinky_lcd_display_interfaces/srv/SetDisplay
```

### 3. ROS2 서비스 테스트

```bash
# 서비스 호출 테스트
ros2 service call /pinky/lcd_controller/set_display \
  pinky_lcd_display_interfaces/srv/SetDisplay \
  "{title: 'Test', lines: ['Line 1', 'Line 2'], show_timestamp: true}"
```

---

## Docker 컨테이너 설정

### 권장 설정: 네트워크 모드 host

`docker-compose.yml` 수정:

```yaml
services:
  ros2-api-server:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ros2-api-server
    network_mode: "host"  # 호스트 네트워크 사용
    env_file:
      - .env.local
    volumes:
      - ./logs:/app/logs
      - ./src:/app/src
    environment:
      - ROS_DOMAIN_ID=0
      - RMW_IMPLEMENTATION=rmw_fastrtps_cpp
    restart: unless-stopped
    # depends_on 제거 (host 네트워크 사용 시)
```

**장점**:
- 호스트의 ROS2 환경에 직접 접근 가능
- DDS 네트워크 설정 간단
- 추가 네트워크 설정 불필요

**단점**:
- 포트 매핑 불가 (호스트 포트 직접 사용)
- 다른 컨테이너와 네트워크 격리 불가

---

## 환경 변수 설정

`.env.local`에 ROS2 관련 설정 추가:

```bash
# ROS2 설정
ROS2_NAMESPACE=/pinky
ROS2_SERVICE_TIMEOUT=2.0
ROS2_SERVICE_NAME=lcd_controller/set_display

# ROS2 DDS 설정 (필요한 경우)
ROS_DOMAIN_ID=0
RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

---

## 단계별 설정 가이드

### Step 1: ROS2 설치 확인

```bash
# 호스트에서 ROS2 확인
ros2 --help
source /opt/ros/humble/setup.bash
ros2 run demo_nodes_cpp talker  # 테스트
```

### Step 2: ROS2 패키지 빌드

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
colcon build --packages-select \
    pinky_lcd_display_interfaces \
    pinky_lcd_display_controller
source install/setup.bash
```

### Step 3: LCD 컨트롤러 서버 실행

```bash
# 터미널 1: LCD 컨트롤러 서버
ros2 run pinky_lcd_display_controller lcd_controller_server
```

### Step 4: Docker 컨테이너 설정

`docker-compose.yml`에서 네트워크 모드 설정:

```yaml
ros2-api-server:
  network_mode: "host"
```

또는 볼륨 마운트:

```yaml
ros2-api-server:
  volumes:
    - /opt/ros/humble:/opt/ros/humble:ro
    - ./install:/ros2_ws/install:ro
  environment:
    - ROS_DISTRO=humble
    - ROS_DOMAIN_ID=0
```

### Step 5: 서버 재시작 및 확인

```bash
cd SERVER/ros2-server/api-server
docker-compose down
docker-compose up -d --build

# Health Check 확인
curl http://localhost:8003/health
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

### Step 6: API 테스트

```bash
curl -X POST http://localhost:8003/api/detection/resident \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "00000000-0000-0000-0000-000000000001",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001",
    "display_format": "basic"
  }'
```

**예상 응답**:
```json
{
    "success": true,
    "message": "Resident information displayed on LCD",
    "data": {
        "display_sent": true  // ← 실제 LCD에 표시됨!
    }
}
```

---

## 문제 해결

### 문제 1: `ros2: false` 상태 유지

**확인 사항**:
1. ROS2 서비스 실행 확인
   ```bash
   ros2 service list | grep lcd_controller
   ```

2. ROS2 네트워크 확인
   ```bash
   ros2 node list
   ros2 topic list
   ```

3. Docker 컨테이너에서 ROS2 접근 확인
   ```bash
   docker exec -it ros2-api-server bash
   # 컨테이너 내부에서
   source /opt/ros/humble/setup.bash
   ros2 service list
   ```

**해결 방법**:
- 네트워크 모드 `host` 사용
- ROS2 DDS 도메인 ID 확인 (`ROS_DOMAIN_ID`)
- ROS2 서비스가 실행 중인지 확인

### 문제 2: ROS2 서비스를 찾을 수 없음

**에러 메시지**:
```
ROS2 서비스 'lcd_controller/set_display'를 사용할 수 없습니다
```

**해결 방법**:
1. LCD 컨트롤러 서버 실행 확인
   ```bash
   ros2 run pinky_lcd_display_controller lcd_controller_server
   ```

2. 서비스 이름 확인
   ```bash
   ros2 service list
   # /pinky/lcd_controller/set_display 확인
   ```

3. 네임스페이스 확인
   - `.env.local`의 `ROS2_NAMESPACE` 확인
   - 서비스 이름: `{ROS2_NAMESPACE}/lcd_controller/set_display`

### 문제 3: Docker 컨테이너에서 ROS2 접근 불가

**해결 방법**:
1. 네트워크 모드 `host` 사용
2. ROS2 볼륨 마운트 확인
3. 환경 변수 설정 확인 (`ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`)

---

## 요약

### 모킹 모드 → 실제 LCD 표시 전환

1. ✅ ROS2 설치 (호스트 또는 Docker)
2. ✅ ROS2 패키지 빌드
3. ✅ LCD 컨트롤러 서버 실행
4. ✅ Docker 컨테이너에서 ROS2 접근 설정
5. ✅ Health Check로 `ros2: true` 확인
6. ✅ API 테스트로 `display_sent: true` 확인

### 권장 방법

**로컬 개발 환경**:
- 호스트에 ROS2 설치
- Docker 컨테이너는 `network_mode: "host"` 사용

**프로덕션 환경**:
- Docker 컨테이너 내부에 ROS2 설치
- ROS2 네트워크 설정 (DDS 도메인 ID)

---

## 참고

- ROS2 네임스페이스: `/pinky` (기본값)
- 서비스 이름: `lcd_controller/set_display`
- 서비스 타입: `pinky_lcd_display_interfaces/srv/SetDisplay`
- 로봇 측 LCD 노드: `pinky_lcd_display` 패키지의 `lcd_node`

