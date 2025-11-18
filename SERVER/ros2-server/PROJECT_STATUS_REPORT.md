# ros2-server 프로젝트 상태 리포트

**작성일**: 2025-11-18  
**브랜치**: `feat/SERVER/ros2-server__build_state_management__RP-58__make_robot_state_manageable`

---

## 프로젝트 개요

`ros2-server`는 Pinky 로봇을 제어하기 위한 ROS2 서버 패키지 모음입니다.  
ROS2 토픽, 서비스, 액션을 통해 로봇을 원격으로 제어할 수 있습니다.

### 주요 목적
- ROS2 ↔ HTTP / gRPC 브리지: ROS2 토픽/서비스를 외부 API로 노출
- Pinky 로봇 제어를 위한 ROS2 서버 패키지 제공

### 기술 스택
- **언어**: Python 3
- **프레임워크**: ROS2 (rclpy)
- **통신**: ROS2 토픽, 서비스, 액션
- **GUI**: PyQt5, matplotlib (모니터링용)

---

## 패키지 구조

### 1. pinky_state_machine
**State Machine 기반 로봇 제어 패키지**

#### 주요 기능
- ✅ State Machine 기반 목표 위치 제어
- ✅ PID 제어기를 통한 각도 및 선형 속도 제어
- ✅ GUI 기반 모니터링 및 목표 위치 설정
- ✅ 동적 파라미터 조정 지원

#### 노드
- `move_pinky_state_machine`: State Machine 기반 제어 노드
- `qmonitor_pinky_state_machine`: GUI 모니터링 노드

#### State Machine 상태
1. **RotateToGoal**: 목표 방향으로 회전
2. **MoveToGoal**: 목표 위치로 이동
3. **RotateToFinal**: 최종 방향으로 회전
4. **GoalReached**: 목표 도달 (종료 상태)

#### 토픽
- **구독**: `/odom` (nav_msgs/Odometry), `/goal_pose` (geometry_msgs/Pose)
- **발행**: `/cmd_vel` (geometry_msgs/Twist), `/state` (std_msgs/String), `/angle_error`, `/distance_error`

#### 문서
- [README.md](src/pinky_state_machine/README.md)
- [State Diagram](src/pinky_state_machine/docs/STATE_DIAGRAM.md)
- [개발 현황 리포트](src/pinky_state_machine/docs/DEVELOPMENT_REPORT.md)
- [TODO](src/pinky_state_machine/docs/TODO.md)

---

### 2. pinky_lcd_display_controller
**LCD 디스플레이 제어를 위한 서비스 기반 컨트롤러 패키지**

#### 주요 기능
- ✅ LCD 표시 내용 제어 (서비스 기반)
- ✅ LCD 스타일 설정 (색상, 폰트)
- ✅ LCD 화면 지우기
- ✅ LCD 레이아웃 설정
- ✅ 애니메이션 지원 (액션)
- ✅ 텍스트 스크롤 (액션)
- ✅ 한글 폰트 지원 (MaruBuri)

#### 노드
- `lcd_controller_server`: LCD 제어 서비스 서버

#### 서비스
- `/lcd_controller/set_display`: LCD 표시 내용 설정
- `/lcd_controller/set_style`: LCD 스타일 설정
- `/lcd_controller/clear_display`: LCD 화면 지우기
- `/lcd_controller/set_layout`: LCD 레이아웃 설정

#### 액션
- `/lcd_controller/set_display_action`: LCD 표시 액션 (애니메이션 지원)
- `/lcd_controller/scroll_text_action`: 텍스트 스크롤 액션

#### 문서
- [README.md](src/pinky_lcd_display_controller/README.md)
- [종합 테스트 가이드](src/pinky_lcd_display_controller/docs/COMPREHENSIVE_TEST_GUIDE.md)
- [서비스/액션 실행 흐름](src/pinky_lcd_display_controller/docs/SERVICE_ACTION_EXECUTION_FLOW.md)
- [개발 현황 리포트](src/pinky_lcd_display_controller/docs/DEVELOPMENT_REPORT.md)

---

### 3. pinky_lcd_display_interfaces
**LCD 디스플레이 제어를 위한 인터페이스 정의 패키지**

#### 제공 인터페이스
- **서비스**: `SetDisplay`, `SetStyle`, `ClearDisplay`, `SetLayout`
- **액션**: `SetDisplay`, `ScrollText`
- **메시지**: `LCDEvent`, `LCDStatus`

#### 문서
- [인터페이스 동기화 리포트](src/pinky_lcd_display_interfaces/INTERFACE_SYNC_REPORT.md)

---

## 최근 개발 내용

### 2025-11-18: 사용 가이드 작성

#### 추가된 문서
1. **USAGE_GUIDE.md** (18KB, 722줄)
   - 전체 사용 가이드 문서
   - 빌드 및 실행 방법
   - 패키지별 상세 사용법
   - 네트워크 설정
   - 문제 해결 가이드
   - 통합 사용 시나리오
   - 고급 사용법

2. **README.md 업데이트**
   - 빠른 시작 가이드 추가
   - 사용 가이드 링크 추가
   - 패키지별 기능 및 실행 방법 정리
   - 주요 토픽 및 서비스 요약

3. **STATE_DIAGRAM.md** (이전에 생성됨)
   - State Machine 상태 다이어그램
   - 상태 전이 설명

---

## 프로젝트 통계

### 코드 규모
- **Python 파일**: 4개 (주요 노드)
  - `move_pinky_state_machine.py`
  - `qmonitor_pinky_state_machine.py`
  - `control_apps.py`
  - `lcd_controller_server.py`

### 문서 규모
- **README 파일**: 3개
- **상세 문서**: 20개 이상
- **사용 가이드**: 1개 (USAGE_GUIDE.md)

### 패키지 수
- **ROS2 패키지**: 3개
  - `pinky_state_machine`
  - `pinky_lcd_display_controller`
  - `pinky_lcd_display_interfaces`

---

## 빌드 및 실행 상태

### 빌드 환경
- **빌드 시스템**: colcon
- **빌드 상태**: ✅ 정상
- **의존성**: ROS2 Humble/Foxy, Python 3, PyQt5, matplotlib

### 실행 가능한 노드
1. `ros2 run pinky_state_machine move_pinky_state_machine`
2. `ros2 run pinky_state_machine qmonitor_pinky_state_machine`
3. `ros2 run pinky_lcd_display_controller lcd_controller_server`

---

## 개발 현황

### 완료된 기능 ✅
- [x] State Machine 기반 로봇 제어
- [x] PID 제어기 구현
- [x] GUI 모니터링 도구
- [x] LCD 디스플레이 제어 서비스
- [x] LCD 스타일 및 레이아웃 제어
- [x] LCD 애니메이션 및 스크롤 기능
- [x] 한글 폰트 지원
- [x] 사용 가이드 문서화

### 진행 중 ⏳
- [ ] 센서 통합 (IMU, 초음파, 적외선)
- [ ] 장애물 회피 기능
- [ ] SLAM 통합

### 예정 🔜
- [ ] HTTP/gRPC 브리지 구현
- [ ] 외부 API 연동
- [ ] 다중 로봇 제어 지원

---

## 네트워크 및 통신

### ROS2 도메인
- **기본 도메인 ID**: 0
- **통신 방식**: DDS (멀티캐스트)
- **포트**: UDP 7400-7500

### 필수 토픽
- `/odom`: 로봇 위치 및 자세 (30Hz)
- `/cmd_vel`: 속도 명령
- `/goal_pose`: 목표 위치
- `/state`: 현재 상태

---

## 문제 해결

### 알려진 이슈
- 없음

### 해결된 이슈
- ✅ 사용 가이드 부재 → USAGE_GUIDE.md 작성 완료
- ✅ README 간소화 → 빠른 시작 가이드 추가

---

## 다음 단계

### 단기 계획
1. 센서 통합 (IMU, 초음파, 적외선)
2. 장애물 회피 기능 구현
3. HTTP/gRPC 브리지 프로토타입

### 중기 계획
1. SLAM 통합
2. 다중 로봇 제어 지원
3. 외부 API 연동

### 장기 계획
1. 자율 주행 기능 완성
2. 클라우드 연동
3. 대규모 배포 지원

---

## 참고 문서

### 프로젝트 문서
- [전체 사용 가이드](USAGE_GUIDE.md)
- [프로젝트 README](README.md)

### 패키지별 문서
- [pinky_state_machine README](src/pinky_state_machine/README.md)
- [pinky_lcd_display_controller README](src/pinky_lcd_display_controller/README.md)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| 2025-11-18 | 1.0.0 | 사용 가이드 작성 및 README 업데이트 | Development Team |

---

**마지막 업데이트**: 2025-11-18

