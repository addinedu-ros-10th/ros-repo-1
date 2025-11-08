# pinky_state_machine 개발 현황 리포트

**작성일**: 2025-01-30  
**패키지 경로**: `/home/guehojung/Documents/Project/FINAL/development/ros-repo-1/SERVER/ros2-server/src/pinky_state_machine`

---

## 개발 완료 사항

### 1. GUI 기반 기본 주행 기능 서버 개발 완료 ✅

#### 1.1 State Machine 기반 제어 노드 (`move_pinky_state_machine.py`)
- **기능**: Pinky 로봇을 위한 State Machine 기반 목표 제어 시스템
- **주요 특징**:
  - 4단계 State Machine 구현 (RotateToGoal → MoveToGoal → RotateToFinal → GoalReached)
  - PID 제어기를 통한 각도 및 선형 속도 제어
  - 동적 파라미터 조정 지원 (런타임 파라미터 변경 가능)
  - Pinky 로봇의 `odom` 및 `cmd_vel` 토픽과 통합

- **구현된 기능**:
  - ✅ `nav_msgs/Odometry` 메시지 구독 및 파싱
  - ✅ `geometry_msgs/Pose` 목표 위치 수신
  - ✅ `geometry_msgs/Twist` 속도 명령 발행
  - ✅ PID 기반 각도 제어 (RotateToGoal, RotateToFinal)
  - ✅ PID 기반 선형 제어 (MoveToGoal)
  - ✅ 상태 전이 관리 (StateTransitionManager)
  - ✅ 오차 정보 발행 (angle_error, distance_error)
  - ✅ 현재 상태 발행 (state)

#### 1.2 GUI 모니터링 노드 (`qmonitor_pinky_state_machine.py`)
- **기능**: PyQt5 기반 GUI 모니터링 및 목표 위치 설정 도구
- **주요 특징**:
  - 실시간 로봇 위치 및 목표 위치 시각화
  - State Machine 상태 표시
  - 마우스 드래그를 통한 목표 위치 설정
  - 실제 세트 크기에 맞춘 맵 크기 설정 가능

- **구현된 기능**:
  - ✅ PyQt5 기반 GUI 인터페이스
  - ✅ matplotlib을 통한 로봇 위치 시각화
  - ✅ State Machine 상태 시각화 (4단계 상태 표시)
  - ✅ 마우스 드래그를 통한 목표 위치 설정
  - ✅ 가이드 라인 표시 (로봇 위치에서 목표까지)
  - ✅ 맵 크기 파라미터 설정 (map_width, map_height)
  - ✅ 실시간 업데이트 (100ms 주기)

#### 1.3 PID 제어기 (`control_apps.py`)
- **기능**: PID 제어 알고리즘 구현
- **구현된 기능**:
  - ✅ P, I, D 게인 설정
  - ✅ 최대/최소 출력 제한
  - ✅ 적분 및 미분 항 계산
  - ✅ 시간 기반 제어

---

## 현재 개발 상태

### 완료된 기능 ✅
1. ✅ State Machine 기반 제어 로직
2. ✅ GUI 모니터링 인터페이스
3. ✅ PID 제어기
4. ✅ Pinky 로봇 토픽 통합 (odom, cmd_vel)
5. ✅ 동적 파라미터 조정
6. ✅ 목표 위치 설정 기능
7. ✅ 상태 모니터링 및 오차 추적

### 테스트 완료 항목 ✅
- ✅ State Machine 상태 전이 테스트
- ✅ PID 제어 동작 테스트
- ✅ GUI 인터페이스 동작 테스트
- ✅ 토픽 통신 테스트

---

## 기술 스택

### ROS2 패키지
- `rclpy`: ROS2 Python 클라이언트 라이브러리
- `nav_msgs`: 네비게이션 메시지 타입
- `geometry_msgs`: 기하학적 메시지 타입
- `std_msgs`: 표준 메시지 타입
- `tf_transformations`: 변환 유틸리티

### Python 패키지
- `PyQt5`: GUI 프레임워크
- `matplotlib`: 그래픽 시각화

---

## 아키텍처

### 노드 구조
```
move_pinky_state_machine (제어 노드)
├── 구독: /odom, /goal_pose
├── 발행: /cmd_vel, /angle_error, /distance_error, /state
└── State Machine: RotateToGoal → MoveToGoal → RotateToFinal → GoalReached

qmonitor_pinky_state_machine (모니터링 노드)
├── 구독: /odom, /goal_pose, /state
├── 발행: /goal_pose (마우스 드래그 시)
└── GUI: PyQt5 + matplotlib
```

### State Machine 흐름
```
[시작]
  ↓
RotateToGoal (목표 방향으로 회전)
  ↓ (각도 오차 < tolerance)
MoveToGoal (목표 위치로 이동)
  ↓ (거리 오차 < tolerance)
RotateToFinal (최종 방향으로 회전)
  ↓ (각도 오차 < tolerance)
GoalReached (목표 도달)
  ↓
[종료]
```

---

## 향후 개발 계획

### 자율 주행을 위한 센서 통합 필요 사항
자세한 내용은 `TODO.md` 참조

---

## 참고 자료

- 원본 코드: `/home/guehojung/dev_ws/ROS2/control_tutorials/src/controller_tutorials/controller_tutorials/`
- Pinky Pro 패키지: `/home/guehojung/Documents/Project/FINAL/development/pinky_pro`

