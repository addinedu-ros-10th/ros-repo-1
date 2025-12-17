#!/bin/bash

# 로컬 환경 Caddy 설정 스크립트
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
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 메인 실행
main() {
    log_info "IoT Care Backend - 로컬 환경 Caddy 설정"
    log_info "====================================="
    
    # 현재 Caddy 설정 확인
    if [ -f "./Caddyfile" ]; then
        log_success "로컬 환경 Caddy 설정 파일 확인됨"
        
        log_info "현재 Caddy 설정:"
        echo "----------------------------------------"
        cat ./Caddyfile
        echo "----------------------------------------"
        
        # Docker 컨테이너 상태 확인
        log_info "Docker 컨테이너 상태 확인 중..."
        if command -v docker-compose &> /dev/null; then
            docker-compose ps
        else
            log_warning "docker-compose 명령어를 찾을 수 없습니다"
        fi
        
        log_success "로컬 환경 Caddy 설정이 준비되었습니다"
        log_info "Docker 컨테이너를 시작하려면: docker-compose up -d"
        
    else
        log_error "Caddyfile을 찾을 수 없습니다"
        exit 1
    fi
}

# 스크립트 실행
main "$@"
