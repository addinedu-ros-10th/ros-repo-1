#!/bin/bash
# update_env_vars_universal.sh
# IoT Care Backend System 환경변수 자동 업데이트 스크립트
# 모든 운영체제 (Linux, macOS, Windows)에서 실행 가능
# 작성일: 2025-08-27

set -e  # 오류 발생 시 스크립트 중단

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수들
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

# 메인 함수
main() {
    echo "🔍 IoT Care Backend System 환경변수 자동 업데이트 시작..."
    echo "📅 실행 시간: $(date)"
    echo ""

    # 현재 작업 디렉토리 확인
    log_info "현재 작업 디렉토리: $(pwd)"

    # 프로젝트 루트 디렉토리 찾기
    PROJECT_ROOT=$(find_project_root)
    log_info "프로젝트 루트 디렉토리: $PROJECT_ROOT"

    # .env.local 파일 확인
    ENV_FILE="$PROJECT_ROOT/.env.local"
    if [ ! -f "$ENV_FILE" ]; then
        log_error ".env.local 파일을 찾을 수 없습니다: $ENV_FILE"
        exit 1
    fi
    log_success ".env.local 파일 발견: $ENV_FILE"

    # 운영체제 감지
    OS=$(detect_os)
    log_info "운영체제: $OS"

    # IP 주소 조회
    CURRENT_IP=$(get_current_ip "$OS")
    if [ -z "$CURRENT_IP" ]; then
        log_error "IP 주소를 찾을 수 없습니다."
        show_ip_help "$OS"
        exit 1
    fi
    log_success "현재 IP 주소: $CURRENT_IP"

    # 현재 환경변수 확인
    show_current_env_vars "$ENV_FILE"

    # 백업 생성
    BACKUP_FILE=$(create_backup "$ENV_FILE" "$PROJECT_ROOT")
    log_success "백업 파일 생성: $BACKUP_FILE"

    # 환경변수 업데이트
    update_env_vars "$ENV_FILE" "$CURRENT_IP" "$OS"

    # 업데이트된 내용 확인
    show_updated_env_vars "$ENV_FILE"

    # 다음 단계 안내
    show_next_steps

    # Docker 재시작 옵션 처리
    if [ "$1" = "--restart" ]; then
        restart_docker
    fi

    log_success "환경변수 자동 업데이트 완료!"
    echo "📅 완료 시간: $(date)"
}

# 프로젝트 루트 찾기
find_project_root() {
    local current_dir=$(pwd)
    local max_depth=10
    local depth=0

    while [ "$depth" -lt "$max_depth" ] && [ "$current_dir" != "/" ]; do
        if [ -f "$current_dir/.env.local" ]; then
            echo "$current_dir"
            return 0
        fi
        current_dir=$(dirname "$current_dir")
        depth=$((depth + 1))
    done

    # fallback: 상대 경로로 시도
    local fallback_root="$(cd ../.. && pwd)"
    if [ -f "$fallback_root/.env.local" ]; then
        echo "$fallback_root"
        return 0
    fi

    log_error "프로젝트 루트를 찾을 수 없습니다."
    exit 1
}

# 운영체제 감지
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*|MINGW32*|MSYS*|MINGW*) echo "windows";;
        *)          echo "unknown";;
    esac
}

# IP 주소 조회
get_current_ip() {
    local os="$1"
    local ip=""

    case "$os" in
        "linux")
            ip=$(get_ip_linux)
            ;;
        "macos")
            ip=$(get_ip_macos)
            ;;
        "windows")
            ip=$(get_ip_windows)
            ;;
        *)
            ip=$(get_ip_fallback)
            ;;
    esac

    echo "$ip"
}

# Linux IP 주소 조회
get_ip_linux() {
    local ip=""
    
    # 방법 1: ip addr 사용
    ip=$(ip addr show 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}' | cut -d'/' -f1)
    
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

# macOS IP 주소 조회
get_ip_macos() {
    local ip=""
    
    # 방법 1: ifconfig 사용
    ip=$(ifconfig 2>/dev/null | grep "inet " | grep -v "127.0.0.1" | head -1 | awk '{print $2}')
    
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

# Windows IP 주소 조회
get_ip_windows() {
    local ip=""
    
    # Git Bash에서 실행 중인 경우
    if command -v powershell >/dev/null 2>&1; then
        ip=$(powershell -Command "Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*'} | Select-Object -First 1 -ExpandProperty IPAddress" 2>/dev/null | tr -d '\r')
    fi
    
    # ipconfig 사용
    if [ -z "$ip" ]; then
        ip=$(ipconfig 2>/dev/null | grep "IPv4" | head -1 | sed 's/.*: //' | tr -d '\r')
    fi
    
    echo "$ip"
}

# Fallback IP 주소 조회
get_ip_fallback() {
    local ip=""
    
    if command -v python3 >/dev/null 2>&1; then
        ip=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
except:
    print('')
" 2>/dev/null)
    fi
    
    echo "$ip"
}

# IP 주소 도움말 표시
show_ip_help() {
    local os="$1"
    
    case "$os" in
        "linux")
            log_info "Linux에서 IP 주소 확인 방법:"
            echo "  💡 ip addr"
            echo "  💡 hostname -I"
            echo "  💡 ifconfig"
            ;;
        "macos")
            log_info "macOS에서 IP 주소 확인 방법:"
            echo "  💡 ifconfig"
            echo "  💡 ipconfig getifaddr en0"
            ;;
        "windows")
            log_info "Windows에서 IP 주소 확인 방법:"
            echo "  💡 ipconfig"
            echo "  💡 powershell -Command 'ipconfig'"
            ;;
        *)
            log_info "IP 주소 확인 방법:"
            echo "  💡 네트워크 설정 확인"
            ;;
    esac
}

# 현재 환경변수 표시
show_current_env_vars() {
    local env_file="$1"
    
    echo ""
    log_step "현재 .env.local 파일의 IP 설정:"
    grep -E "^(DB_HOST|CADDY_DOMAIN)=" "$env_file" || log_warning "IP 관련 환경변수를 찾을 수 없습니다."
}

# 백업 파일 생성
create_backup() {
    local env_file="$1"
    local project_root="$2"
    local backup_file="$project_root/.env.local.backup.$(date +%Y%m%d_%H%M%S)"
    
    cp "$env_file" "$backup_file"
    echo "$backup_file"
}

# 환경변수 업데이트
update_env_vars() {
    local env_file="$1"
    local current_ip="$2"
    local os="$3"
    
    echo ""
    log_step ".env.local 파일 업데이트 중..."
    
    # 운영체제별 sed 명령어 결정
    local sed_cmd
    if [ "$os" = "macos" ]; then
        sed_cmd="sed -i ''"
    else
        sed_cmd="sed -i"
    fi
    
    # DB_HOST 업데이트
    if grep -q "DB_HOST=" "$env_file"; then
        $sed_cmd "s/DB_HOST=.*/DB_HOST=$current_ip/g" "$env_file"
        log_success "DB_HOST 업데이트 완료: $current_ip"
    else
        log_warning "DB_HOST 환경변수가 .env.local 파일에 없습니다."
    fi
    
    # CADDY_DOMAIN 업데이트
    if grep -q "CADDY_DOMAIN=" "$env_file"; then
        $sed_cmd "s/CADDY_DOMAIN=.*/CADDY_DOMAIN=$current_ip/g" "$env_file"
        log_success "CADDY_DOMAIN 업데이트 완료: $current_ip"
    else
        log_warning "CADDY_DOMAIN 환경변수가 .env.local 파일에 없습니다."
    fi
}

# 업데이트된 환경변수 표시
show_updated_env_vars() {
    local env_file="$1"
    
    echo ""
    log_step "업데이트된 환경변수:"
    grep -E "^(DB_HOST|CADDY_DOMAIN)=" "$env_file" || log_warning "업데이트된 환경변수를 찾을 수 없습니다."
}

# 다음 단계 안내
show_next_steps() {
    echo ""
    log_info "다음 단계: Docker 환경 재시작"
    echo "💡 명령어: docker-compose down && docker-compose up -d"
    echo "💡 또는 이 스크립트를 --restart 옵션과 함께 실행하세요."
}

# Docker 재시작
restart_docker() {
    echo ""
    log_step "Docker 환경 자동 재시작 시작..."
    
    # Docker 컨테이너 중지
    log_info "Docker 컨테이너 중지 중..."
    docker-compose down --volumes --remove-orphans
    
    # Docker 시스템 정리
    log_info "Docker 시스템 정리 중..."
    docker system prune -f
    
    # 프로젝트 재시작
    log_info "프로젝트 재시작 중..."
    docker-compose up -d
    
    # 상태 확인
    echo ""
    log_step "Docker 컨테이너 상태:"
    docker-compose ps
    
    # API 서버 상태 확인
    echo ""
    log_step "API 서버 상태 확인 중..."
    sleep 10  # 서버 시작 대기
    
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "API 서버 정상 동작"
    else
        log_warning "API 서버 응답 없음"
        echo "💡 docker logs iot-care-app 명령으로 로그를 확인하세요."
    fi
    
    echo ""
    log_success "환경변수 업데이트 및 Docker 재시작 완료!"
}

# 스크립트 실행
main "$@"


