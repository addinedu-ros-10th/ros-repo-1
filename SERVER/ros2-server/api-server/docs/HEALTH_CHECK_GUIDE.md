# Health Check 결과 해석 가이드

**작성일**: 2025-11-22  
**목적**: ROS2 API Server의 Health Check 결과 해석 방법

---

## Health Check 엔드포인트

```bash
curl http://localhost:8003/health
```

---

## 응답 형식

```json
{
    "status": "degraded",
    "services": {
        "ros2": false,
        "iot_data_server": true
    },
    "timestamp": "2025-11-22T18:33:54.876226"
}
```

---

## Status 값 해석

### `status: "healthy"`
- **의미**: 모든 서비스가 정상 동작 중
- **조건**: `services`의 모든 값이 `true`

### `status: "degraded"`
- **의미**: 일부 서비스가 사용 불가능하지만 서버는 동작 중
- **조건**: `services`의 일부 값이 `false`
- **동작**: 서버는 정상 동작하지만, 일부 기능이 제한될 수 있음

---

## Services 상태 해석

### `ros2: false`
- **의미**: ROS2 환경이 없거나 ROS2 서비스에 연결할 수 없음
- **원인**:
  1. ROS2가 설치되어 있지 않음 (정상, 모킹 모드)
  2. ROS2 서비스(`lcd_controller/set_display`)가 실행되지 않음
  3. ROS2 네트워크 연결 문제
- **영향**:
  - LCD 표시 기능이 동작하지 않음
  - API는 정상 응답하지만 `display_sent: false` 반환
  - 모킹 모드로 동작 (에러 없이 처리)
- **해결 방법**:
  - ROS2 환경이 필요한 경우: ROS2 설치 및 서비스 실행
  - ROS2 환경이 불필요한 경우: 무시해도 됨 (모킹 모드)

### `ros2: true`
- **의미**: ROS2 환경이 정상적으로 연결됨
- **조건**: ROS2 서비스(`lcd_controller/set_display`)가 사용 가능
- **영향**: LCD 표시 기능이 정상 동작

### `iot_data_server: false`
- **의미**: iot-data-server에 연결할 수 없음
- **원인**:
  1. iot-data-server가 실행되지 않음
  2. 네트워크 연결 문제
  3. URL 설정 오류 (`.env.local`의 `IOT_DATA_SERVER_URL` 확인)
- **영향**:
  - 어르신 정보 조회 불가
  - 대부분의 API 기능이 동작하지 않음
- **해결 방법**:
  1. iot-data-server 상태 확인: `curl http://<IOT_DATA_SERVER_URL>/health`
  2. `.env.local`의 `IOT_DATA_SERVER_URL` 확인
  3. 네트워크 연결 확인

### `iot_data_server: true`
- **의미**: iot-data-server에 정상적으로 연결됨
- **조건**: iot-data-server의 `/health` 엔드포인트가 200 응답
- **영향**: 어르신 정보 조회 및 모든 API 기능 정상 동작

---

## 일반적인 상태 조합

### 1. 정상 동작 (ROS2 환경 있음)
```json
{
    "status": "healthy",
    "services": {
        "ros2": true,
        "iot_data_server": true
    }
}
```
- **의미**: 모든 기능 정상 동작
- **LCD 표시**: ✅ 정상 동작
- **어르신 정보 조회**: ✅ 정상 동작

### 2. 정상 동작 (ROS2 환경 없음, 모킹 모드)
```json
{
    "status": "degraded",
    "services": {
        "ros2": false,
        "iot_data_server": true
    }
}
```
- **의미**: iot-data-server는 정상, ROS2는 없음 (모킹 모드)
- **LCD 표시**: ⚠️ 모킹 모드 (실제 LCD 표시 안 됨)
- **어르신 정보 조회**: ✅ 정상 동작
- **API 응답**: 정상 (단, `display_sent: false`)

### 3. iot-data-server 연결 실패
```json
{
    "status": "degraded",
    "services": {
        "ros2": false,
        "iot_data_server": false
    }
}
```
- **의미**: iot-data-server에 연결할 수 없음
- **LCD 표시**: ⚠️ 모킹 모드
- **어르신 정보 조회**: ❌ 실패
- **API 응답**: 500 에러 또는 404 에러

### 4. ROS2만 연결 실패
```json
{
    "status": "degraded",
    "services": {
        "ros2": false,
        "iot_data_server": true
    }
}
```
- **의미**: iot-data-server는 정상, ROS2만 연결 실패
- **LCD 표시**: ⚠️ 모킹 모드
- **어르신 정보 조회**: ✅ 정상 동작
- **API 응답**: 정상 (단, `display_sent: false`)

---

## 문제 해결

### 문제 1: `iot_data_server: false`

**확인 사항**:
1. iot-data-server 실행 상태
   ```bash
   curl http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com/health
   ```

2. `.env.local` 설정 확인
   ```bash
   cat SERVER/ros2-server/api-server/.env.local | grep IOT_DATA_SERVER_URL
   ```

3. 네트워크 연결 확인
   ```bash
   ping ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com
   ```

**해결 방법**:
- iot-data-server가 실행 중인지 확인
- `.env.local`의 `IOT_DATA_SERVER_URL`이 올바른지 확인
- 방화벽/네트워크 설정 확인

### 문제 2: `ros2: false` (ROS2 환경이 필요한 경우)

**확인 사항**:
1. ROS2 설치 확인
   ```bash
   ros2 --help
   ```

2. ROS2 서비스 확인
   ```bash
   ros2 service list | grep lcd_controller
   ```

3. ROS2 서비스 타입 확인
   ```bash
   ros2 service type /pinky/lcd_controller/set_display
   ```

**해결 방법**:
- ROS2 설치: `sudo apt install ros-<distro>-rclpy`
- ROS2 서비스 실행 확인
- 네임스페이스 확인 (`.env.local`의 `ROS2_NAMESPACE`)

---

## 참고

- `status: "degraded"`는 서버가 동작 중이라는 의미입니다
- `ros2: false`는 ROS2 환경이 없을 때 정상적인 상태입니다 (모킹 모드)
- `iot_data_server: false`는 심각한 문제이며 즉시 해결해야 합니다

