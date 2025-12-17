# ROS2 서버 실행 절차 가이드

**작성일**: 2025-11-23  
**목적**: ROS2 서비스를 사용할 수 있도록 정확한 실행 절차 제공

---

## 문제 원인

`ros2: false`가 리턴되는 주요 원인:

1. **ROS_DOMAIN_ID 불일치**: 서버와 ROS2 서비스가 다른 도메인 ID 사용
2. **ROS2 서비스 미실행**: LCD 컨트롤러 서버가 실행되지 않음
3. **ROS2 환경 미설정**: ROS2 환경이 제대로 source되지 않음

---

## 정확한 실행 절차

### Step 1: ROS2 환경 확인

```bash
# 1. ROS2 설치 확인
ls /opt/ros/jazzy  # 또는 /opt/ros/humble

# 2. ROS2 환경 설정
source /opt/ros/jazzy/setup.bash  # 또는 source /opt/ros/humble/setup.bash

# 3. 워크스페이스 환경 설정
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1
source SERVER/ros2-server/install/setup.bash
```

### Step 2: ROS2 도메인 ID 설정 (중요!)

**모든 터미널에서 동일한 ROS_DOMAIN_ID 사용 필수**

```bash
# ROS2 도메인 ID 설정 (0~232 사이의 숫자)
export ROS_DOMAIN_ID=0  # 또는 원하는 숫자 (예: 13)

# 확인
echo $ROS_DOMAIN_ID
```

### Step 3: LCD 컨트롤러 서버 실행

**새 터미널에서 실행** (ROS2 환경이 설정된 상태)

```bash
# 터미널 1: LCD 컨트롤러 서버 실행
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1

# ROS2 환경 설정
source /opt/ros/jazzy/setup.bash
source SERVER/ros2-server/install/setup.bash

# ROS2 도메인 ID 설정 (Step 2와 동일한 값!)
export ROS_DOMAIN_ID=0

# LCD 컨트롤러 서버 실행
ros2 run pinky_lcd_display_controller lcd_controller_server
```

**예상 출력**:
```
[INFO] [lcd_controller_server]: LCD Controller Server 시작...
[INFO] [lcd_controller_server]: 서비스 대기 중: /lcd_controller/set_display
```

### Step 4: ROS2 서비스 확인

**새 터미널에서 확인** (ROS2 환경이 설정된 상태)

```bash
# 터미널 2: ROS2 서비스 확인
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1

# ROS2 환경 설정
source /opt/ros/jazzy/setup.bash
source SERVER/ros2-server/install/setup.bash

# ROS2 도메인 ID 설정 (Step 2와 동일한 값!)
export ROS_DOMAIN_ID=0

# 서비스 목록 확인
ros2 service list | grep lcd_controller
```

**예상 출력**:
```
/lcd_controller/clear_display
/lcd_controller/set_display
/lcd_controller/set_layout
/lcd_controller/set_style
```

### Step 5: API 서버 실행

**새 터미널에서 실행** (ROS2 환경이 설정된 상태)

```bash
# 터미널 3: API 서버 실행
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server

# ROS2 환경 설정 (run_standalone.sh가 자동으로 처리하지만, 명시적으로 설정)
source /opt/ros/jazzy/setup.bash
source ../../install/setup.bash

# ROS2 도메인 ID 설정 (Step 2와 동일한 값!)
export ROS_DOMAIN_ID=0

# 서버 실행
./run_standalone.sh
```

**또는 환경 변수를 설정하여 실행**:

```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server

# .env.local에 ROS_DOMAIN_ID 설정 (선택적)
# 또는 환경 변수로 직접 설정
ROS_DOMAIN_ID=0 ./run_standalone.sh
```

### Step 6: Health Check 확인

```bash
# 터미널 4: Health Check
curl http://localhost:8004/health
```

**예상 결과**:
```json
{
    "status": "healthy",
    "services": {
        "ros2": true,  // ← 성공!
        "iot_data_server": true
    },
    "timestamp": "2025-11-23T04:33:37.305000"
}
```

---

## 전체 실행 스크립트

### 방법 1: 수동 실행 (권장)

**터미널 1: LCD 컨트롤러 서버**
```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1
source /opt/ros/jazzy/setup.bash
source SERVER/ros2-server/install/setup.bash
export ROS_DOMAIN_ID=0
ros2 run pinky_lcd_display_controller lcd_controller_server
```

**터미널 2: API 서버**
```bash
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server
source /opt/ros/jazzy/setup.bash
source ../../install/setup.bash
export ROS_DOMAIN_ID=0
./run_standalone.sh
```

**터미널 3: 테스트**
```bash
# 서비스 확인
source /opt/ros/jazzy/setup.bash
source /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/install/setup.bash
export ROS_DOMAIN_ID=0
ros2 service list | grep lcd_controller

# Health Check
curl http://localhost:8004/health
```

### 방법 2: 자동화 스크립트

```bash
#!/bin/bash
# start_ros2_services.sh

set -e

# ROS2 환경 설정
source /opt/ros/jazzy/setup.bash
source /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/install/setup.bash

# ROS2 도메인 ID 설정
export ROS_DOMAIN_ID=0

# LCD 컨트롤러 서버 실행 (백그라운드)
ros2 run pinky_lcd_display_controller lcd_controller_server &
LCD_PID=$!

# 잠시 대기 (서버 시작 시간)
sleep 2

# 서비스 확인
echo "ROS2 서비스 확인 중..."
ros2 service list | grep lcd_controller || {
    echo "❌ LCD 컨트롤러 서비스가 시작되지 않았습니다"
    kill $LCD_PID 2>/dev/null
    exit 1
}

echo "✅ LCD 컨트롤러 서버 실행 중 (PID: $LCD_PID)"
echo "종료하려면: kill $LCD_PID"

# API 서버 실행
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/api-server
./run_standalone.sh
```

---

## 문제 해결

### 문제 1: `ros2: false`가 계속 리턴됨

**확인 사항**:
1. **ROS_DOMAIN_ID 일치 확인**
   ```bash
   # 모든 터미널에서 동일한 값인지 확인
   echo $ROS_DOMAIN_ID
   ```

2. **ROS2 서비스 실행 확인**
   ```bash
   source /opt/ros/jazzy/setup.bash
   source SERVER/ros2-server/install/setup.bash
   export ROS_DOMAIN_ID=0  # 서버와 동일한 값
   ros2 service list | grep lcd_controller
   ```

3. **서비스 타입 확인**
   ```bash
   ros2 service type /lcd_controller/set_display
   # 예상: pinky_lcd_display_interfaces/srv/SetDisplay
   ```

**해결 방법**:
- 모든 터미널에서 동일한 `ROS_DOMAIN_ID` 사용
- LCD 컨트롤러 서버가 실행 중인지 확인
- 서버 재시작

### 문제 2: 서비스 목록에 없음

**원인**: LCD 컨트롤러 서버가 실행되지 않음

**해결**:
```bash
# LCD 컨트롤러 서버 실행
source /opt/ros/jazzy/setup.bash
source SERVER/ros2-server/install/setup.bash
export ROS_DOMAIN_ID=0
ros2 run pinky_lcd_display_controller lcd_controller_server
```

### 문제 3: 서비스 타입 오류

**원인**: 워크스페이스가 빌드되지 않음

**해결**:
```bash
cd SERVER/ros2-server
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
```

---

## 요약

### 필수 조건

1. ✅ **모든 터미널에서 동일한 ROS_DOMAIN_ID 사용**
2. ✅ **LCD 컨트롤러 서버 실행 중**
3. ✅ **ROS2 환경이 모든 터미널에서 source됨**
4. ✅ **워크스페이스가 빌드됨**

### 실행 순서

1. **터미널 1**: LCD 컨트롤러 서버 실행
2. **터미널 2**: API 서버 실행
3. **터미널 3**: Health Check 확인

### 확인 명령어

```bash
# 1. ROS2 도메인 ID 확인
echo $ROS_DOMAIN_ID

# 2. 서비스 목록 확인
ros2 service list | grep lcd_controller

# 3. Health Check
curl http://localhost:8004/health
```

---

## 참고

- ROS2 도메인 ID는 0~232 사이의 숫자
- 기본값은 0
- 서버와 ROS2 서비스가 같은 도메인 ID를 사용해야 통신 가능
- `.env.local`에 `ROS_DOMAIN_ID=0` 설정 가능

