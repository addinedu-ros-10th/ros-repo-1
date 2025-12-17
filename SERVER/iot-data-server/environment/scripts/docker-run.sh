#!/bin/bash

# Docker Compose 실행 스크립트
# Usage: ./docker-run.sh [local|dev|prod]

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

# 환경 변수 파일 확인
check_env_file() {
    local env_file=".env"
    if [ ! -f "$env_file" ]; then
        log_warning "환경 변수 파일이 없습니다. env.example을 복사하여 .env 파일을 생성하세요."
        log_info "cp env.example .env"
        return 1
    fi
    log_success "환경 변수 파일 확인 완료"
    return 0
}

# Docker Compose 실행
run_docker_compose() {
    local environment=$1
    local compose_file="docker-compose.yml"
    
    case $environment in
        "local")
            compose_file="docker-compose.yml"
            log_info "로컬 환경으로 실행합니다..."
            ;;
        "dev")
            compose_file="docker-compose.dev.yml"
            log_info "개발 환경으로 실행합니다..."
            ;;
        "prod")
            compose_file="docker-compose.prod.yml"
            log_info "운영 환경으로 실행합니다..."
            ;;
        *)
            log_error "잘못된 환경입니다. local, dev, prod 중 선택하세요."
            exit 1
            ;;
    esac
    
    if [ ! -f "$compose_file" ]; then
        log_error "Docker Compose 파일을 찾을 수 없습니다: $compose_file"
        exit 1
    fi
    
    log_info "Docker Compose 실행: $compose_file"
    docker-compose -f "$compose_file" up -d
    
    log_success "컨테이너가 성공적으로 시작되었습니다!"
    log_info "컨테이너 상태 확인: docker-compose -f $compose_file ps"
    log_info "로그 확인: docker-compose -f $compose_file logs -f"
}

# 메인 실행
main() {
    local environment=${1:-"local"}
    
    log_info "IoT Care Backend Docker Compose 실행 스크립트"
    log_info "환경: $environment"
    
    # 환경 변수 파일 확인
    check_env_file
    
    # Docker Compose 실행
    run_docker_compose "$environment"
}

# 스크립트 실행
main "$@"

