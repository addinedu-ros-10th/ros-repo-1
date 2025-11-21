# IoT Care Backend System 환경변수 자동 업데이트

이 디렉토리는 IoT Care Backend System의 환경변수를 자동으로 업데이트하는 스크립트들을 포함합니다.

## 📁 스크립트 목록

### 1. `update_env_vars_universal.sh` ⭐ **권장**
- **용도**: 모든 운영체제에서 사용 가능한 통합 스크립트
- **특징**: 
  - 자동 운영체제 감지
  - 스마트한 프로젝트 루트 찾기
  - 색상이 있는 로그 출력
  - 오류 처리 및 복구 기능
  - Docker 자동 재시작 옵션

### 2. `update_env_vars.sh`
- **용도**: Linux/Windows 환경용 스크립트
- **특징**: 
  - Linux, Windows, macOS 지원
  - 운영체제별 IP 주소 조회 최적화
  - sed 명령어 자동 조정

### 3. `update_env_vars_macos.sh`
- **용도**: macOS 환경에 최적화된 스크립트
- **특징**: 
  - macOS 전용 IP 주소 조회 방법
  - 모든 운영체제 지원
  - sed 명령어 자동 조정

## 🚀 사용법

### 기본 사용법
```bash
# 통합 스크립트 사용 (권장)
./update_env_vars_universal.sh

# 특정 운영체제용 스크립트 사용
./update_env_vars.sh          # Linux/Windows
./update_env_vars_macos.sh    # macOS
```

### Docker 자동 재시작과 함께 실행
```bash
# 환경변수 업데이트 후 Docker 자동 재시작
./update_env_vars_universal.sh --restart
```

### 실행 위치
스크립트는 다음 위치에서 실행할 수 있습니다:
- `services/was-server/environment/update/` (현재 디렉토리)
- `services/was-server/` (프로젝트 루트)
- 프로젝트 내의 어느 하위 디렉토리

## 🔧 지원 운영체제

| 운영체제 | 지원 상태 | IP 주소 조회 방법 |
|----------|-----------|-------------------|
| **Linux** | ✅ 완벽 지원 | `ip addr`, `hostname -I`, `ifconfig` |
| **macOS** | ✅ 완벽 지원 | `ifconfig`, `ipconfig getifaddr` |
| **Windows** | ✅ 완벽 지원 | `powershell`, `ipconfig` |
| **WSL** | ✅ 완벽 지원 | Linux 방식과 동일 |
| **Git Bash** | ✅ 완벽 지원 | Windows 방식과 동일 |

## 📋 업데이트되는 환경변수

- `DB_HOST`: 데이터베이스 호스트 IP 주소
- `CADDY_DOMAIN`: Caddy 웹서버 도메인 IP 주소

## 🛡️ 안전 기능

### 자동 백업
- 실행 전 `.env.local` 파일 자동 백업
- 백업 파일명: `.env.local.backup.YYYYMMDD_HHMMSS`

### 오류 처리
- 프로젝트 루트 자동 감지
- IP 주소 조회 실패 시 대체 방법 시도
- 운영체제별 최적화된 명령어 사용

### 검증
- 업데이트 전후 환경변수 값 확인
- 파일 존재 여부 검증
- 권한 확인

## 🔍 문제 해결

### IP 주소를 찾을 수 없는 경우
```bash
# Linux
ip addr
hostname -I

# macOS
ifconfig
ipconfig getifaddr en0

# Windows
ipconfig
powershell -Command "ipconfig"
```

### .env.local 파일을 찾을 수 없는 경우
1. 프로젝트 루트에 `.env.local` 파일이 있는지 확인
2. 파일 권한 확인: `ls -la .env.local`
3. 스크립트를 프로젝트 루트에서 실행

### 권한 오류가 발생하는 경우
```bash
chmod +x update_env_vars_universal.sh
```

## 📊 로그 레벨

| 로그 타입 | 색상 | 설명 |
|-----------|------|------|
| **INFO** | 🔵 파란색 | 일반 정보 |
| **SUCCESS** | 🟢 초록색 | 성공 메시지 |
| **WARNING** | 🟡 노란색 | 경고 메시지 |
| **ERROR** | 🔴 빨간색 | 오류 메시지 |
| **STEP** | 🔵 파란색 | 진행 단계 |

## 🔄 Docker 통합

### 자동 재시작 옵션
```bash
./update_env_vars_universal.sh --restart
```

이 옵션은 다음 작업을 순차적으로 수행합니다:
1. 환경변수 업데이트
2. Docker 컨테이너 중지
3. Docker 시스템 정리
4. 프로젝트 재시작
5. API 서버 상태 확인

### 수동 Docker 재시작
```bash
docker-compose down && docker-compose up -d
```

## 📝 예시 출력

```bash
🔍 IoT Care Backend System 환경변수 자동 업데이트 시작...
📅 실행 시간: Wed Aug 27 07:03:02 PM KST 2025

ℹ️  현재 작업 디렉토리: /path/to/project
ℹ️  프로젝트 루트 디렉토리: /path/to/project/services/was-server
✅ .env.local 파일 발견: /path/to/project/services/was-server/.env.local
ℹ️  운영체제: linux
✅ 현재 IP 주소: 192.168.0.26

🔍 현재 .env.local 파일의 IP 설정:
DB_HOST=192.168.0.2
CADDY_DOMAIN=192.168.0.2

✅ 백업 파일 생성: /path/to/project/services/was-server/.env.local.backup.20250827_190302

🔍 .env.local 파일 업데이트 중...
✅ DB_HOST 업데이트 완료: 192.168.0.26
✅ CADDY_DOMAIN 업데이트 완료: 192.168.0.26

🔍 업데이트된 환경변수:
DB_HOST=192.168.0.26
CADDY_DOMAIN=192.168.0.26

ℹ️  다음 단계: Docker 환경 재시작
💡 명령어: docker-compose down && docker-compose up -d
💡 또는 이 스크립트를 --restart 옵션과 함께 실행하세요.

✅ 환경변수 자동 업데이트 완료!
📅 완료 시간: Wed Aug 27 07:03:02 PM KST 2025
```

## 🎯 권장사항

1. **통합 스크립트 사용**: `update_env_vars_universal.sh`를 주로 사용
2. **자동화**: CI/CD 파이프라인에 통합하여 자동 실행
3. **모니터링**: 로그를 모니터링하여 업데이트 상태 추적
4. **백업**: 정기적으로 환경변수 파일 백업

## 📞 지원

문제가 발생하거나 개선 제안이 있는 경우:
1. 로그 출력 확인
2. README의 문제 해결 섹션 참조
3. 개발팀에 문의


