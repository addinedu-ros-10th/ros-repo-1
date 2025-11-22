# Python 직접 실행 가이드 (스탠드얼론)

**작성일**: 2025-11-22  
**목적**: Docker 없이 Python으로 직접 실행하여 ROS2 서비스에 접근

---

## 개요

Docker 컨테이너 내부에 ROS2가 설치되어 있지 않아 `ros2: false`가 발생하는 경우, Python으로 직접 실행하여 호스트의 ROS2 환경을 사용할 수 있습니다.

---

## 전제 조건

1. ✅ 호스트에 ROS2 설치됨
2. ✅ colcon build 완료됨
3. ✅ LCD 컨트롤러 서버 실행 중

---

## 실행 방법

### 방법 1: Shell 스크립트 사용 (권장)

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server

# 실행 권한 부여 (최초 1회)
chmod +x run_standalone.sh

# 서버 실행
./run_standalone.sh
```

**스크립트가 자동으로 수행하는 작업**:
1. ROS2 환경 설정 (`/opt/ros/humble/setup.bash`)
2. ROS2 워크스페이스 환경 설정 (`install/setup.bash`)
3. Python 의존성 확인
4. ROS2 모듈 확인
5. 환경 변수 설정 (`ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, `SERVER_PORT`)
6. 서버 실행

---

### 방법 2: Python 스크립트 직접 실행

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server

# ROS2 환경 설정
source /opt/ros/humble/setup.bash
source ../install/setup.bash

# 환경 변수 설정
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export SERVER_PORT=8004

# 서버 실행
python3 run_standalone.py
```

---

## 포트 설정

### 기본 포트: 8004

포트는 다음 순서로 결정됩니다:

1. 환경 변수 `SERVER_PORT`
2. `.env.local` 파일의 `SERVER_PORT`
3. 기본값: `8004`

**포트 변경 방법**:

```bash
# 방법 1: 환경 변수
export SERVER_PORT=8005
./run_standalone.sh

# 방법 2: .env.local 파일
echo "SERVER_PORT=8005" >> .env.local
./run_standalone.sh
```

---

## 서버 접속

서버 실행 후:

- **HTTP**: `http://localhost:8004`
- **API 문서**: `http://localhost:8004/docs`
- **Health Check**: `http://localhost:8004/health`

---

## Health Check 확인

```bash
curl http://localhost:8004/health
```

**예상 결과** (ROS2 연결 성공 시):
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

## 문제 해결

### 문제 1: ROS2 모듈을 찾을 수 없음

**에러**:
```
❌ ROS2 Python 모듈 (rclpy)을 찾을 수 없습니다
```

**해결**:
```bash
# ROS2 환경 설정 확인
source /opt/ros/humble/setup.bash
python3 -c "import rclpy; print('OK')"
```

### 문제 2: ROS2 워크스페이스가 빌드되지 않음

**에러**:
```
⚠️  ROS2 워크스페이스가 빌드되지 않았습니다
```

**해결**:
```bash
cd SERVER/ros2-server
colcon build --packages-select \
    pinky_lcd_display_interfaces \
    pinky_lcd_display_controller
source install/setup.bash
```

### 문제 3: Python 의존성이 없음

**에러**:
```
❌ 필수 Python 패키지가 설치되지 않았습니다
```

**해결**:
```bash
cd SERVER/ros2-server/api-server
pip install -r requirements.txt
```

### 문제 4: 포트 충돌

**에러**:
```
Address already in use
```

**해결**:
```bash
# 다른 포트 사용
export SERVER_PORT=8005
./run_standalone.sh

# 또는 사용 중인 프로세스 확인
sudo lsof -i :8004
```

---

## 백그라운드 실행

### systemd 서비스로 등록

`/etc/systemd/system/ros2-api-server.service` 생성:

```ini
[Unit]
Description=ROS2 API Server (Standalone)
After=network.target

[Service]
Type=simple
User=guehojung
WorkingDirectory=/home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server
Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="ROS_DOMAIN_ID=0"
Environment="RMW_IMPLEMENTATION=rmw_fastrtps_cpp"
Environment="SERVER_PORT=8004"
ExecStart=/bin/bash -c 'source /opt/ros/humble/setup.bash && source /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/install/setup.bash && cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server && python3 run_standalone.py'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**활성화**:
```bash
sudo systemctl enable ros2-api-server.service
sudo systemctl start ros2-api-server.service
sudo systemctl status ros2-api-server.service
```

---

## Docker vs Python 직접 실행 비교

| 항목 | Docker 실행 | Python 직접 실행 |
|------|------------|-----------------|
| ROS2 접근 | ❌ 컨테이너 내부에 ROS2 없음 | ✅ 호스트 ROS2 직접 사용 |
| 설정 복잡도 | 높음 | 낮음 |
| 디버깅 | 어려움 | 쉬움 |
| 포트 | 8003 (매핑) | 8004 (직접) |
| 권장 | 모킹 모드 | 실제 LCD 표시 |

---

## 요약

### 실행 순서

1. ✅ LCD 컨트롤러 서버 실행 (터미널 1)
   ```bash
   cd SERVER/ros2-server
   source install/setup.bash
   ros2 run pinky_lcd_display_controller lcd_controller_server
   ```

2. ✅ Python 직접 실행 (터미널 2)
   ```bash
   cd api-server
   ./run_standalone.sh
   ```

3. ✅ Health Check 확인
   ```bash
   curl http://localhost:8004/health
   # ros2: true 확인
   ```

4. ✅ API 테스트
   ```bash
   curl -X POST http://localhost:8004/api/detection/resident ...
   ```

---

## 참고

- 포트: `8004` (기본값)
- ROS2 도메인 ID: `0` (기본값)
- 서비스 이름: `/pinky/lcd_controller/set_display` (네임스페이스 포함)

