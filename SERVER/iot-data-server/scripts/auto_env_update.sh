#!/bin/bash
# auto_env_update.sh
# IoT Care Backend System 환경변수 자동 업데이트 스크립트
# 모든 운영체제 (Linux, macOS, Windows)에서 사용 가능
# 작성일: 2025-08-23

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_step() {
    echo -e "${BLUE}🔍 $1${NC}"
}

# 현재 작업 디렉토리 확인
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info "IoT Care Backend System 환경변수 자동 업데이트 시작..."
log_info "📅 실행 시간: $(date)"
log_info "📍 프로젝트 루트: $PROJECT_ROOT"
echo ""

# .env.local 파일 존재 확인
ENV_FILE="$PROJECT_ROOT/.env.local"
if [ ! -f "$ENV_FILE" ]; then
    log_error ".env.local 파일을 찾을 수 없습니다: $ENV_FILE"
    exit 1
fi

log_success ".env.local 파일 발견"

# 운영체제 감지
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW32*|MSYS*|MINGW*) echo "windows";;
        *)          echo "unknown";;
    esac
}

OS=$(detect_os)
log_info "운영체제 감지: $OS"

# IP 주소 조회 함수들
get_ip_linux() {
    # 방법 1: ip addr 사용
    local ip=$(ip addr show 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}' | cut -d'/' -f1)
    
    # 방법 2: hostname -I 사용
    if [ -z "$ip" ]; then
        ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    fi
    
    # 방법 3: ifconfig 사용 (레거시)
    if [ -z "$ip" ]; then
        ip=$(ifconfig 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')
    fi
    
    echo "$ip"
}

get_ip_macos() {
    # 방법 1: ifconfig 사용
    local ip=$(ifconfig 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')
    
    # 방법 2: ipconfig getifaddr en0 사용
    if [ -z "$ip" ]; then
        ip=$(ipconfig getifaddr en0 2>/dev/null)
    fi
    
    # 방법 3: ipconfig getifaddr en1 사용
    if [ -z "$ip" ]; then
        ip=$(ipconfig getifaddr en1 2>/dev/null)
    fi
    
    echo "$ip"
}

get_ip_windows() {
    local ip=""
    
    # Git Bash에서 실행 중인 경우
    if command -v powershell >/dev/null 2>&1; then
        # PowerShell 사용
        ip=$(powershell -Command "Get-NetIPAddress | Where-Object {\$_.AddressFamily -eq 'IPv4' -and \$_.IPAddress -notlike '127.*' -and \$_.IPAddress -notlike '169.*'} | Select-Object -First 1 -ExpandProperty IPAddress" 2>/dev/null | tr -d '\r')
    fi
    
    # ipconfig 사용
    if [ -z "$ip" ]; then
        ip=$(ipconfig 2>/dev/null | grep "IPv4" | head -1 | sed 's/.*: //' | tr -d '\r')
    fi
    
    echo "$ip"
}

# 현재 IP 주소 조회
log_step "현재 개발 머신 IP 주소 조사 중..."

CURRENT_IP=""
case "$OS" in
    "linux")
        CURRENT_IP=$(get_ip_linux)
        ;;
    "macos")
        CURRENT_IP=$(get_ip_macos)
        ;;
    "windows")
        CURRENT_IP=$(get_ip_windows)
        ;;
    *)
        log_warning "지원하지 않는 운영체제: $OS"
        log_info "fallback 방법으로 IP 주소 조회 시도..."
        # 소켓을 사용한 fallback
        CURRENT_IP=$(python3 -c "
import socket
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        print(s.getsockname()[0])
except:
    pass
" 2>/dev/null)
        ;;
esac

if [ -z "$CURRENT_IP" ]; then
    log_error "IP 주소를 찾을 수 없습니다."
    log_info "수동으로 IP 주소를 확인하고 환경변수를 업데이트하세요."
    case "$OS" in
        "linux")
            log_info "명령어: ip addr show 또는 hostname -I"
            ;;
        "macos")
            log_info "명령어: ifconfig 또는 ipconfig getifaddr en0"
            ;;
        "windows")
            log_info "명령어: ipconfig 또는 PowerShell Get-NetIPAddress"
            ;;
    esac
    exit 1
fi

log_success "현재 IP 주소: $CURRENT_IP"

# 현재 .env.local 파일의 IP 설정 확인
echo ""
log_step "현재 .env.local 파일의 IP 설정:"
grep -E "^(DB_HOST|CADDY_DOMAIN)=" "$ENV_FILE" || log_warning "IP 관련 환경변수를 찾을 수 없습니다."

# 백업 디렉토리 생성
BACKUP_DIR="$PROJECT_ROOT/env_backups"
mkdir -p "$BACKUP_DIR"

# 백업 파일 생성
BACKUP_FILE="$BACKUP_DIR/.env.local.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$BACKUP_FILE"
log_success "백업 파일 생성: $BACKUP_FILE"

# 환경변수 업데이트
echo ""
log_step ".env.local 파일 업데이트 중..."

# sed 명령어를 운영체제별로 조정
SED_CMD="sed"
case "$OS" in
    "macos")
        SED_CMD="sed -i ''"
        ;;
    *)
        SED_CMD="sed -i"
        ;;
esac

# DB_HOST 업데이트
if grep -q "DB_HOST=" "$ENV_FILE"; then
    $SED_CMD "s/DB_HOST=.*/DB_HOST=$CURRENT_IP/g" "$ENV_FILE"
    log_success "DB_HOST 업데이트 완료: $CURRENT_IP"
else
    log_warning "DB_HOST 환경변수가 .env.local 파일에 없습니다."
fi

# CADDY_DOMAIN 업데이트
if grep -q "CADDY_DOMAIN=" "$ENV_FILE"; then
    $SED_CMD "s/CADDY_DOMAIN=.*/CADDY_DOMAIN=$CURRENT_IP/g" "$ENV_FILE"
    log_success "CADDY_DOMAIN 업데이트 완료: $CURRENT_IP"
else
    log_warning "CADDY_DOMAIN 환경변수가 .env.local 파일에 없습니다."
fi

# 업데이트된 내용 확인
echo ""
log_step "업데이트된 환경변수:"
grep -E "^(DB_HOST|CADDY_DOMAIN)=" "$ENV_FILE" || log_warning "업데이트된 환경변수를 찾을 수 없습니다."

echo ""
log_info "🎯 다음 단계: Docker 환경 재시작"
log_info "💡 명령어: docker-compose down && docker-compose up -d"
log_info "💡 또는 이 스크립트를 --restart 옵션과 함께 실행하세요."

# --restart 옵션이 있는 경우 Docker 재시작
if [[ "$1" == "--restart" ]]; then
    echo ""
    log_info "🚀 Docker 환경 자동 재시작 시작..."
    
    # Docker 상태 확인
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker가 설치되지 않았습니다"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker가 실행되지 않았습니다"
        exit 1
    fi
    
    # Docker Compose 상태 확인
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose가 설치되지 않았습니다"
        exit 1
    fi
    
    # Docker 컨테이너 중지
    log_step "Docker 컨테이너 중지 중..."
    cd "$PROJECT_ROOT"
    docker-compose down --volumes --remove-orphans
    
    # Docker 시스템 정리
    log_step "Docker 시스템 정리 중..."
    docker system prune -f
    
    # 프로젝트 재시작
    log_step "프로젝트 재시작 중..."
    docker-compose up -d
    
    # 상태 확인
    echo ""
    log_step "Docker 컨테이너 상태:"
    docker-compose ps
    
    # API 서버 상태 확인
    echo ""
    log_step "API 서버 상태 확인 중..."
    sleep 10  # 서버 시작 대기
    
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        log_success "API 서버 정상 동작"
    else
        log_warning "API 서버 응답 없음"
        log_info "docker logs iot-care-app 명령으로 로그를 확인하세요."
    fi
    
    echo ""
    log_success "🎉 환경변수 업데이트 및 Docker 재시작 완료!"
fi

echo ""
log_success "✅ 환경변수 자동 업데이트 완료!"
log_info "📅 완료 시간: $(date)"

