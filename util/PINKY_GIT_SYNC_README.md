# Pinky 로봇 Git 동기화 스크립트

이 디렉토리에는 pinky 로봇의 git 저장소를 자동으로 동기화하는 스크립트가 포함되어 있습니다.

## 파일 설명

### 1. `sync_pinky_git.sh`
Pinky 로봇의 git 저장소를 동기화하는 메인 스크립트입니다.

**기능:**
- `/home/pinky/ros-repo-1` 디렉토리 확인 및 자동 클론 (없는 경우)
- `dev` 브랜치로 전환
- `base/ROS2/*` 패턴의 모든 브랜치를 찾아서 pull

**사용법:**
```bash
./sync_pinky_git.sh
```

### 2. `setup_pinky_auto_sync.sh`
SSH 접속 시 자동으로 `sync_pinky_git.sh`를 실행하도록 설정하는 스크립트입니다.

**기능:**
- `~/.bashrc`에 자동 실행 설정 추가
- SSH 세션에서만 실행되도록 설정 (비대화형 모드 제외)
- 백그라운드 실행으로 로그인 지연 방지

**사용법:**
```bash
./setup_pinky_auto_sync.sh
```

## 설치 및 설정 방법

### 1단계: 스크립트를 pinky 로봇에 복사

로컬 개발 환경에서 pinky 로봇으로 스크립트를 복사합니다:

```bash
# SSH를 통해 pinky 로봇에 접속
ssh pinky@<pinky-ip-address>

# 또는 직접 복사
scp util/sync_pinky_git.sh util/setup_pinky_auto_sync.sh pinky@<pinky-ip>:/home/pinky/
```

### 2단계: 자동 동기화 설정

pinky 로봇에 SSH 접속 후:

```bash
# 스크립트 디렉토리로 이동 (또는 복사한 위치로)
cd /home/pinky/ros-repo-1/util

# 실행 권한 부여
chmod +x sync_pinky_git.sh setup_pinky_auto_sync.sh

# 자동 동기화 설정
./setup_pinky_auto_sync.sh
```

### 3단계: 설정 적용

```bash
# 즉시 적용
source ~/.bashrc

# 또는 다음 SSH 접속부터 자동 적용됨
```

## 동작 방식

1. **SSH 접속 시**: `~/.bashrc`가 로드되면서 `sync_pinky_git.sh`가 백그라운드에서 실행됩니다.
2. **동기화 과정**:
   - 저장소가 없으면 자동으로 클론
   - `dev` 브랜치로 전환 및 pull
   - `base/ROS2/*` 브랜치들을 찾아서 각각 pull
   - 작업 완료 후 다시 `dev` 브랜치로 복귀

## 로그 확인

동기화 로그는 다음 파일에서 확인할 수 있습니다:

```bash
cat /tmp/pinky_git_sync.log
```

## 수동 실행

자동 동기화가 설정되어 있어도 수동으로 실행할 수 있습니다:

```bash
/home/pinky/ros-repo-1/util/sync_pinky_git.sh
```

## 문제 해결

### 저장소가 클론되지 않는 경우
- GitHub 접근 권한 확인
- 네트워크 연결 확인
- `/home/pinky` 디렉토리 권한 확인

### 브랜치를 찾을 수 없는 경우
- `git fetch --all` 실행 후 다시 시도
- 원격 저장소에 해당 브랜치가 존재하는지 확인

### 자동 실행이 되지 않는 경우
- `~/.bashrc`에 설정이 추가되었는지 확인:
  ```bash
  grep "Pinky Git Auto Sync" ~/.bashrc
  ```
- SSH 세션인지 확인 (로컬 터미널에서는 실행되지 않음)
- 로그 파일 확인: `/tmp/pinky_git_sync.log`

## 주의사항

- 스크립트는 SSH 세션에서만 자동 실행됩니다 (로컬 터미널에서는 실행되지 않음)
- 백그라운드에서 실행되므로 로그인 지연이 없습니다
- 동기화 중에는 git 작업을 피하는 것이 좋습니다
- 충돌이 발생하면 수동으로 해결해야 합니다

