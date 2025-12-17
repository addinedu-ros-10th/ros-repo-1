#!/bin/bash

# 환경 자동 감지 및 Caddy 설정 선택 스크립트
# IoT Care Backend System

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" >&2
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# 환경 감지 함수
detect_environment() {
    # AWS EC2 환경 감지
    if curl -s --connect-timeout 3 http://169.254.169.254/latest/meta-data/instance-id > /dev/null 2>&1; then
        echo "production"
        return 0
    fi
    
    # Docker 환경 감지
    if [ -f /.dockerenv ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
        echo "development"
        return 0
    fi
    
    # 로컬 환경 (기본값)
    echo "local"
    return 0
}

# 환경별 Caddy 설정 파일 선택
select_caddy_config() {
    local env=$1
    local caddy_dir="/etc/caddy"
    
    log_info "환경: '$env'에 대한 Caddy 설정 선택 중..."
    
    case $env in
        "production")
            log_info "프로덕션 환경 감지됨 - Caddyfile.prod 사용"
            if [ -f "/app/Caddyfile.prod" ]; then
                cp /app/Caddyfile.prod $caddy_dir/Caddyfile
                log_success "프로덕션 Caddy 설정 적용됨"
            else
                log_error "Caddyfile.prod를 찾을 수 없습니다"
                return 1
            fi
            ;;
        "development")
            log_info "개발 환경 감지됨 - Caddyfile.dev 사용"
            if [ -f "/app/Caddyfile.dev" ]; then
                cp /app/Caddyfile.dev $caddy_dir/Caddyfile
                log_success "개발 환경 Caddy 설정 적용됨"
            else
                log_error "Caddyfile.dev를 찾을 수 없습니다"
                return 1
            fi
            ;;
        "local")
            log_info "로컬 환경 감지됨 - Caddyfile 사용"
            if [ -f "/app/Caddyfile" ]; then
                cp /app/Caddyfile $caddy_dir/Caddyfile
                log_success "로컬 환경 Caddy 설정 적용됨"
            elif [ -f "./Caddyfile" ]; then
                # 로컬 환경에서는 현재 디렉토리의 Caddyfile 사용
                cp ./Caddyfile $caddy_dir/Caddyfile
                log_success "로컬 환경 Caddy 설정 적용됨 (현재 디렉토리)"
            else
                log_error "Caddyfile을 찾을 수 없습니다"
                return 1
            fi
            ;;
        *)
            log_error "알 수 없는 환경: '$env'"
            return 1
            ;;
    esac
}

# 메인 실행
main() {
    log_info "IoT Care Backend - 환경별 Caddy 설정 자동 분리 시스템"
    log_info "=================================================="
    
    # 환경 감지
    local detected_env
    detected_env=$(detect_environment)
    log_success "감지된 환경: '$detected_env'"
    
    # Caddy 설정 선택 및 적용
    if select_caddy_config "$detected_env"; then
        log_success "환경별 Caddy 설정이 성공적으로 적용되었습니다"
        
        # 설정 파일 내용 확인
        log_info "적용된 Caddy 설정:"
        echo "----------------------------------------"
        cat /etc/caddy/Caddyfile
        echo "----------------------------------------"
        
        # Caddy 재시작
        log_info "Caddy 서비스 재시작 중..."
        if pgrep caddy > /dev/null; then
            pkill caddy
            sleep 2
        fi
        
        # Caddy 백그라운드에서 시작
        caddy run --config /etc/caddy/Caddyfile &
        log_success "Caddy가 새로운 설정으로 시작되었습니다"
        
    else
        log_error "Caddy 설정 적용에 실패했습니다"
        exit 1
    fi
}

# 스크립트 실행
main "$@"
