# IoT Care Backend System - 환경변수 자동 업데이트 가이드

**작성일**: 2025-08-23  
**프로젝트**: IoT Repository 4 - WAS Server

## 🎯 **개요**

이 시스템은 IoT Care Backend System의 환경변수(특히 IP 주소)를 자동으로 감지하고 업데이트하여, 개발자가 매번 수동으로 IP 주소를 변경할 필요 없이 프로젝트를 시작할 수 있도록 합니다.

## 🚀 **주요 기능**

- **자동 IP 감지**: 현재 개발 머신의 IP 주소를 운영체제별로 자동 감지
- **환경변수 자동 업데이트**: `.env.local` 파일의 `DB_HOST`와 `CADDY_DOMAIN` 자동 수정
- **백업 생성**: 업데이트 전 기존 환경변수 파일 자동 백업
- **Docker 자동 재시작**: 환경변수 변경 후 Docker Compose 자동 재시작 (선택사항)
- **크로스 플랫폼 지원**: Linux, macOS, Windows 모든 환경에서 사용 가능

## 🖥️ **지원 운영체제**

| 운영체제 | 지원 스크립트 | IP 감지 방법 |
|---------|---------------|-------------|
| **Linux** | `auto_env_update.sh` | `ip addr`, `hostname -I`, `ifconfig` |
| **macOS** | `auto_env_update.sh` | `ifconfig`, `ipconfig getifaddr` |
| **Windows** | `auto_env_update.bat` | PowerShell `Get-NetIPAddress`, `ipconfig` |

## 📁 **파일 구조**

```
services/was-server/
├── scripts/
│   ├── auto_env_update.py          # Python 기반 통합 스크립트
│   ├── auto_env_update.sh          # Linux/macOS용 Bash 스크립트
│   └── auto_env_update.bat         # Windows용 배치 파일
├── start_project.sh                 # Linux/macOS용 프로젝트 시작 스크립트
├── start_project.bat                # Windows용 프로젝트 시작 스크립트
├── docker-compose.auto.yml          # 자동 업데이트 포함 Docker Compose 설정
├── .env.local                       # 환경변수 파일 (자동 업데이트 대상)
└── env_backups/                     # 백업 파일 저장 디렉토리
```

## 🔧 **사용법**

### 1. **환경변수만 업데이트 (Docker 재시작 없음)**

#### Linux/macOS
```bash
cd services/was-server
./scripts/auto_env_update.sh
```

#### Windows (Git Bash)
```bash
cd services/was-server
./scripts/auto_env_update.sh
```

#### Windows (Command Prompt/PowerShell)
```cmd
cd services\was-server
scripts\auto_env_update.bat
```

### 2. **환경변수 업데이트 + Docker 자동 재시작**

#### Linux/macOS
```bash
cd services/was-server
./scripts/auto_env_update.sh --restart
```

#### Windows (Git Bash)
```bash
cd services/was-server
./scripts/auto_env_update.sh --restart
```

#### Windows (Command Prompt/PowerShell)
```cmd
cd services\was-server
scripts\auto_env_update.bat --restart
```

### 3. **프로젝트 전체 시작 (권장)**

#### Linux/macOS
```bash
cd services/was-server
./start_project.sh
```

#### Windows (Git Bash)
```bash
cd services/was-server
./start_project.sh
```

#### Windows (Command Prompt/PowerShell)
```cmd
cd services\was-server
start_project.bat
```

### 4. **Python 스크립트 사용**

```bash
cd services/was-server
python3 scripts/auto_env_update.py --restart
```

## 📋 **업데이트되는 환경변수**

| 환경변수 | 설명 | 예시 |
|---------|------|------|
| `DB_HOST` | 데이터베이스 호스트 IP 주소 | `192.168.0.9` |
| `CADDY_DOMAIN` | Caddy 웹서버 도메인/IP | `192.168.0.9` |

## 🔄 **작동 원리**

### 1. **IP 주소 감지**
- **Linux**: `ip addr show` → `hostname -I` → `ifconfig` 순서로 시도
- **macOS**: `ifconfig` → `ipconfig getifaddr en0` → `ipconfig getifaddr en1` 순서로 시도
- **Windows**: PowerShell `Get-NetIPAddress` → `ipconfig` 순서로 시도

### 2. **환경변수 업데이트**
- 현재 IP 주소와 `.env.local` 파일의 기존 IP 주소 비교
- 변경이 필요한 경우에만 업데이트 수행
- 업데이트 전 자동 백업 생성

### 3. **Docker 재시작 (선택사항)**
- `--restart` 옵션 사용 시 자동으로 Docker Compose 재시작
- 컨테이너 상태 및 서비스 동작 확인

## 🛠️ **문제 해결**

### **IP 주소를 찾을 수 없는 경우**

#### Linux
```bash
# 방법 1
ip addr show | grep "inet " | grep -v "127.0.0.1"

# 방법 2
hostname -I

# 방법 3
ifconfig | grep "inet " | grep -v "127.0.0.1"
```

#### macOS
```bash
# 방법 1
ifconfig | grep "inet " | grep -v "127.0.0.1"

# 방법 2
ipconfig getifaddr en0

# 방법 3
ipconfig getifaddr en1
```

#### Windows
```cmd
# 방법 1 (PowerShell)
powershell -Command "Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*'} | Select-Object -First 1 -ExpandProperty IPAddress"

# 방법 2
ipconfig | findstr "IPv4"
```

### **환경변수 파일이 없는 경우**
```bash
# .env.local 파일이 있는지 확인
ls -la .env.local

# 파일이 없다면 .env.local.example을 복사
cp .env.local.example .env.local
```

### **Docker 관련 오류**
```bash
# Docker 상태 확인
docker info

# Docker Compose 버전 확인
docker-compose --version

# 컨테이너 로그 확인
docker-compose logs
```

## 📚 **고급 사용법**

### **특정 프로젝트 루트 지정**
```bash
python3 scripts/auto_env_update.py --project-root /path/to/project
```

### **백업 디렉토리 변경**
```bash
# scripts/auto_env_update.sh 파일에서 수정
BACKUP_DIR="/custom/backup/path"
```

### **추가 IP 관련 환경변수 업데이트**
```bash
# scripts/auto_env_update.sh 파일에서 수정
ip_fields=('DB_HOST' 'CADDY_DOMAIN' 'CUSTOM_IP_FIELD')
```

## 🔒 **보안 고려사항**

- 환경변수 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않음
- 백업 파일은 `env_backups/` 디렉토리에 저장되며, 필요시 수동으로 정리 가능
- 민감한 정보(비밀번호, API 키 등)는 환경변수 파일에 직접 저장하지 말고 Docker secrets 사용 권장

## 📝 **로그 및 모니터링**

### **로그 확인**
```bash
# Docker 컨테이너 로그
docker-compose logs -f

# 특정 서비스 로그
docker-compose logs -f app
docker-compose logs -f redis
docker-compose logs -f caddy
```

### **상태 확인**
```bash
# 컨테이너 상태
docker-compose ps

# 서비스 상태 확인
curl http://localhost:8000/health
curl http://localhost:80
```

## 🚨 **주의사항**

1. **백업 확인**: 자동 백업이 생성되지만, 중요한 변경사항이 있다면 수동으로도 백업
2. **네트워크 변경**: VPN 연결/해제, 네트워크 변경 시 환경변수 재업데이트 필요
3. **권한 문제**: 스크립트 실행 권한이 없는 경우 `chmod +x` 명령으로 권한 부여
4. **방화벽**: 외부 데이터베이스 연결 시 방화벽 설정 확인

## 📞 **지원 및 문의**

문제가 발생하거나 개선 사항이 있는 경우:
1. 프로젝트 이슈 트래커에 등록
2. 개발팀에 직접 문의
3. 로그 파일과 함께 상세한 오류 내용 전달

---

**마지막 업데이트**: 2025-08-23  
**버전**: 1.0.0

