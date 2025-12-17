# 실제 LCD 표시 빠른 시작 가이드

**작성일**: 2025-11-22  
**전제 조건**: 호스트 머신에 ROS2가 설치되어 있고, colcon build가 완료된 상태

---

## 단계별 설정

### Step 1: ROS2 환경 확인

```bash
# ROS2 설치 확인
source /opt/ros/humble/setup.bash  # 또는 설치된 ROS2 버전
ros2 --version

# ROS2 워크스페이스 환경 설정
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
source install/setup.bash

# 빌드된 패키지 확인
ros2 pkg list | grep pinky_lcd
```

**예상 출력**:
```
pinky_lcd_display_controller
pinky_lcd_display_interfaces
```

---

### Step 2: LCD 컨트롤러 서버 실행

**터미널 1**에서 실행 (백그라운드로 실행 가능):

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
source install/setup.bash
ros2 run pinky_lcd_display_controller lcd_controller_server
```

**서버가 정상 실행되면**:
- 서비스가 생성됨: `/pinky/lcd_controller/set_display`
- 서비스 확인: `ros2 service list | grep lcd_controller`

---

### Step 3: Docker 컨테이너 설정 (호스트 ROS2 접근)

#### 방법 A: 네트워크 모드 host 사용 (권장)

`docker-compose.yml`을 수정하거나 `docker-compose.ros2.yml`을 사용:

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server

# ROS2 환경용 설정으로 실행
docker-compose -f docker-compose.yml -f docker-compose.ros2.yml up -d --build
```

**주의**: `network_mode: "host"`를 사용하면 포트 매핑이 필요 없습니다. 서버는 호스트의 포트를 직접 사용합니다.

#### 방법 B: ROS2 볼륨 마운트 (네트워크 격리 유지)

`docker-compose.yml`에 ROS2 경로 마운트 추가:

```yaml
services:
  ros2-api-server:
    volumes:
      - ./logs:/app/logs
      - ./src:/app/src
      # ROS2 설치 경로 마운트
      - /opt/ros/humble:/opt/ros/humble:ro
      # ROS2 워크스페이스 마운트
      - /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/install:/ros2_ws/install:ro
    environment:
      - ROS_DISTRO=humble
      - ROS_DOMAIN_ID=0
      - RMW_IMPLEMENTATION=rmw_fastrtps_cpp
```

그리고 `Dockerfile`에 ROS2 환경 설정 추가 필요.

---

### Step 4: Docker 컨테이너에서 ROS2 접근 확인

```bash
# 컨테이너 내부 접속
docker exec -it ros2-api-server bash

# 컨테이너 내부에서 ROS2 환경 설정 (방법 B 사용 시)
source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash

# ROS2 서비스 확인
ros2 service list | grep lcd_controller
```

**예상 출력**:
```
/pinky/lcd_controller/set_display
/pinky/lcd_controller/clear_display
```

---

### Step 5: Health Check 확인

```bash
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

---

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
1. LCD 컨트롤러 서버가 실행 중인지 확인
   ```bash
   ros2 node list | grep lcd_controller
   ```

2. ROS2 서비스 확인
   ```bash
   ros2 service list | grep lcd_controller
   ```

3. Docker 컨테이너에서 ROS2 접근 확인
   ```bash
   docker exec -it ros2-api-server bash
   # 컨테이너 내부에서
   ros2 service list
   ```

**해결 방법**:
- `network_mode: "host"` 사용 (방법 A)
- ROS2 DDS 도메인 ID 확인 (`ROS_DOMAIN_ID=0`)
- 호스트와 컨테이너의 ROS2 도메인 ID가 동일한지 확인

### 문제 2: ROS2 서비스를 찾을 수 없음

**에러 메시지**:
```
ROS2 서비스 'lcd_controller/set_display'를 사용할 수 없습니다
```

**해결 방법**:
1. 서비스 이름 확인
   ```bash
   ros2 service list
   # /pinky/lcd_controller/set_display 확인
   ```

2. 네임스페이스 확인
   - `.env.local`의 `ROS2_NAMESPACE` 확인
   - 기본값: `/pinky`
   - 서비스 이름: `{ROS2_NAMESPACE}/lcd_controller/set_display`

3. LCD 컨트롤러 서버 재시작
   ```bash
   # 터미널에서 Ctrl+C로 중지 후 재시작
   ros2 run pinky_lcd_display_controller lcd_controller_server
   ```

### 문제 3: Docker 컨테이너에서 ROS2 접근 불가

**해결 방법**:
1. 네트워크 모드 확인
   ```bash
   docker inspect ros2-api-server | grep NetworkMode
   ```

2. ROS2 환경 변수 확인
   ```bash
   docker exec -it ros2-api-server env | grep ROS
   ```

3. 호스트 네트워크 사용
   ```yaml
   network_mode: "host"
   ```

---

## 자동 실행 스크립트

### LCD 컨트롤러 서버 자동 실행 (systemd 서비스)

`/etc/systemd/system/lcd-controller.service` 생성:

```ini
[Unit]
Description=ROS2 LCD Controller Server
After=network.target

[Service]
Type=simple
User=guehojung
WorkingDirectory=/home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/bin/bash -c 'source /opt/ros/humble/setup.bash && source install/setup.bash && ros2 run pinky_lcd_display_controller lcd_controller_server'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**활성화**:
```bash
sudo systemctl enable lcd-controller.service
sudo systemctl start lcd-controller.service
sudo systemctl status lcd-controller.service
```

---

## 요약

### 필수 단계

1. ✅ **LCD 컨트롤러 서버 실행** (터미널 1)
   ```bash
   cd SERVER/ros2-server
   source install/setup.bash
   ros2 run pinky_lcd_display_controller lcd_controller_server
   ```

2. ✅ **Docker 컨테이너 설정** (호스트 ROS2 접근)
   ```bash
   cd api-server
   docker-compose -f docker-compose.yml -f docker-compose.ros2.yml up -d
   ```

3. ✅ **Health Check 확인**
   ```bash
   curl http://localhost:8003/health
   # ros2: true 확인
   ```

4. ✅ **API 테스트**
   ```bash
   curl -X POST http://localhost:8003/api/detection/resident ...
   # display_sent: true 확인
   ```

### 확인 체크리스트

- [ ] LCD 컨트롤러 서버 실행 중
- [ ] ROS2 서비스 확인: `ros2 service list | grep lcd_controller`
- [ ] Docker 컨테이너가 호스트 ROS2에 접근 가능
- [ ] Health Check: `ros2: true`
- [ ] API 테스트: `display_sent: true`

---

## 참고

- ROS2 네임스페이스: `/pinky` (기본값, `.env.local`에서 변경 가능)
- 서비스 이름: `lcd_controller/set_display`
- 서비스 타입: `pinky_lcd_display_interfaces/srv/SetDisplay`
- 로봇 측 LCD 노드: 별도로 실행 필요 (로봇에서)

