# ROS2 가상 환경 전략 리포트

**작성일**: 2025-11-23  
**목적**: 프로젝트 독립성을 위한 최적 venv 전략 수립

---

## 현재 상황 분석

### 시스템 환경
- **ROS2 버전**: Jazzy (humble 아님!)
- **ROS2 경로**: `/opt/ros/jazzy`
- **전역 ROS2 venv**: `~/venv/ros` (ros_venv alias에서 사용)
- **프로젝트 venv**: `SERVER/ros2-server/api-server/venv` (현재 사용 중)

### .bashrc 설정
```bash
alias ros_venv="source ~/venv/ros/bin/activate; echo \"ros venv activated\""
alias ros_domain="export ROS_DOMAIN_ID=17"
alias jazzy="source /opt/ros/jazzy/setup.bash; ros_domain; ros_venv; ..."
```

---

## 옵션 분석

### 옵션 1: 전역 ROS2 venv 사용 (~/venv/ros)

**장점**:
- ✅ 이미 설정된 환경 활용
- ✅ ROS2 관련 패키지 재사용
- ✅ 시스템 리소스 절약

**단점**:
- ❌ 외부 자원 의존 (프로젝트 독립성 저하)
- ❌ 다른 프로젝트와 충돌 가능
- ❌ 배포 시 일관성 문제

**평가**: 프로젝트 독립성 요구사항과 맞지 않음

---

### 옵션 2: 프로젝트 독립 venv + 시스템 ROS2 (권장)

**장점**:
- ✅ 프로젝트 독립성 높음
- ✅ 다른 프로젝트와 충돌 없음
- ✅ 배포 시 일관성
- ✅ ROS2는 시스템 패키지이므로 source로 로드 (표준 방식)

**단점**:
- ⚠️ 시스템 ROS2 환경 source 필요 (스크립트에서 처리)

**평가**: 프로젝트 독립성과 실용성의 균형

---

### 옵션 3: 프로젝트 내부 독립 venv + ROS2 Python 패키지 직접 설치

**장점**:
- ✅ 완전한 독립성

**단점**:
- ❌ ROS2 전체 설치 복잡 (수백 MB)
- ❌ 시스템 ROS2와 호환성 문제 가능
- ❌ 유지보수 어려움

**평가**: 과도한 복잡성, 비권장

---

## 권장 방안: 옵션 2

### 전략
1. **프로젝트 독립 venv 유지**: `api-server/venv`
2. **시스템 ROS2 사용**: `/opt/ros/jazzy` (source로 로드)
3. **Python 패키지만 venv에 설치**: FastAPI, httpx 등
4. **ROS2 Python 모듈**: 시스템 ROS2에서 제공 (rclpy 등)

### 구현 방법

#### 1. 기존 venv 정리
```bash
# 프로젝트 내부 venv 제거 (선택적)
rm -rf venv
```

#### 2. 새로운 독립 venv 생성
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. ROS2 환경 설정 (스크립트에서)
```bash
# run_standalone.sh에서
source /opt/ros/jazzy/setup.bash  # 시스템 ROS2
source ../install/setup.bash      # 워크스페이스
```

---

## 실행 계획

### Step 1: 현재 venv 상태 확인
- [x] 프로젝트 venv 존재 확인
- [x] 전역 ROS2 venv 확인

### Step 2: venv 정리 및 재구성
- [ ] 기존 venv 제거 (선택적)
- [ ] 새로운 독립 venv 생성
- [ ] requirements.txt 설치

### Step 3: 스크립트 업데이트
- [ ] run_standalone.sh: ROS2 환경 설정 (jazzy)
- [ ] run_standalone.py: ROS2 환경 확인

### Step 4: 테스트
- [ ] 서버 실행 테스트
- [ ] ROS2 연결 확인
- [ ] Health Check 확인

---

## 최종 권장 사항

**프로젝트 독립 venv 유지 + 시스템 ROS2 사용**

이유:
1. ✅ 프로젝트 독립성 확보
2. ✅ ROS2는 시스템 패키지이므로 source로 로드 (표준 방식)
3. ✅ Python 패키지만 venv에 설치 (일반적인 방식)
4. ✅ 배포 시 일관성
5. ✅ 유지보수 용이

**구현**:
- 프로젝트 내부 `venv` 유지
- `run_standalone.sh`에서 시스템 ROS2 (jazzy) source
- Python 패키지는 venv에 설치

