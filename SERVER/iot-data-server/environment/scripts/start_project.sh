#!/bin/bash
# start_project.sh
# IoT Care Backend System 프로젝트 시작 스크립트
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
PROJECT_ROOT="$SCRIPT_DIR"

log_info "🚀 IoT Care Backend System 프로젝트 시작..."
log_info "📅 시작 시간: $(date)"
log_info "📍 프로젝트 루트: $PROJECT_ROOT"
echo ""

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

# 필수 도구 확인
check_requirements() {
    log_step "필수 도구 확인 중..."
    
    # Docker 확인
    if ! command -v docker >/dev/null 2>&1; then
        log_error "Docker가 설치되지 않았습니다"
        log_info "Docker를 설치한 후 다시 시도하세요: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # Docker 실행 상태 확인
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker가 실행되지 않았습니다"
        log_info "Docker Desktop을 시작한 후 다시 시도하세요"
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose >/dev/null 2>&1; then
        log_error "Docker Compose가 설치되지 않았습니다"
        log_info "Docker Compose를 설치한 후 다시 시도하세요"
        exit 1
    fi
    
    log_success "필수 도구 확인 완료"
}

# 환경변수 자동 업데이트
update_environment() {
    log_step "환경변수 자동 업데이트 시작..."
    
    # 운영체제별 스크립트 실행
    case "$OS" in
        "linux"|"macos")
            if [ -f "scripts/auto_env_update.sh" ]; then
                chmod +x scripts/auto_env_update.sh
                ./scripts/auto_env_update.sh
            else
                log_warning "auto_env_update.sh 스크립트를 찾을 수 없습니다"
            fi
            ;;
        "windows")
            if [ -f "scripts/auto_env_update.bat" ]; then
                # Git Bash에서 실행 중인 경우
                ./scripts/auto_env_update.bat
            else
                log_warning "auto_env_update.bat 스크립트를 찾을 수 없습니다"
            fi
            ;;
        *)
            log_warning "지원하지 않는 운영체제: $OS"
            ;;
    esac
    
    log_success "환경변수 업데이트 완료"
}

# Docker Compose 시작
start_docker_compose() {
    log_step "Docker Compose 시작 중..."
    
    # 기존 컨테이너 정리
    log_info "기존 컨테이너 정리 중..."
    docker-compose down --volumes --remove-orphans 2>/dev/null || true
    
    # Docker 시스템 정리
    log_info "Docker 시스템 정리 중..."
    docker system prune -f
    
    # 프로젝트 시작
    log_info "프로젝트 시작 중..."
    docker-compose up -d
    
    log_success "Docker Compose 시작 완료"
}

# 서비스 상태 확인
check_services() {
    log_step "서비스 상태 확인 중..."
    
    # 컨테이너 상태 확인
    echo ""
    log_info "Docker 컨테이너 상태:"
    docker-compose ps
    
    # API 서버 상태 확인
    echo ""
    log_step "API 서버 상태 확인 중..."
    log_info "서버 시작 대기 중... (10초)"
    
    for i in {1..10}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            log_success "API 서버 정상 동작"
            break
        else
            if [ $i -eq 10 ]; then
                log_warning "API 서버 응답 없음"
                log_info "docker logs iot-care-app 명령으로 로그를 확인하세요"
            else
                echo -n "."
                sleep 1
            fi
        fi
    done
    
    # Redis 상태 확인
    echo ""
    log_step "Redis 상태 확인 중..."
    if docker exec iot-care-redis redis-cli ping >/dev/null 2>&1; then
        log_success "Redis 정상 동작"
    else
        log_warning "Redis 응답 없음"
    fi
    
    # Caddy 상태 확인
    echo ""
    log_step "Caddy 상태 확인 중..."
    if curl -s http://localhost:80 >/dev/null 2>&1; then
        log_success "Caddy 정상 동작"
    else
        log_warning "Caddy 응답 없음"
    fi
}

# 프로젝트 정보 표시
show_project_info() {
    echo ""
    log_success "🎉 프로젝트 시작 완료!"
    echo ""
    log_info "📋 프로젝트 정보:"
    echo "   • API 서버: http://localhost:8000"
    echo "   • API 문서: http://localhost:8000/docs"
    echo "   • Caddy 웹서버: http://localhost:80"
    echo "   • Redis: localhost:16379"
    echo ""
    log_info "🔧 유용한 명령어:"
    echo "   • 컨테이너 상태 확인: docker-compose ps"
    echo "   • 로그 확인: docker-compose logs -f"
    echo "   • 서비스 중지: docker-compose down"
    echo "   • 환경변수 업데이트: ./scripts/auto_env_update.sh"
    echo ""
    log_info "📅 시작 완료 시간: $(date)"
}

# 메인 실행 함수
main() {
    # 1. 필수 도구 확인
    check_requirements
    
    # 2. 환경변수 자동 업데이트
    update_environment
    
    # 3. Docker Compose 시작
    start_docker_compose
    
    # 4. 서비스 상태 확인
    check_services
    
    # 5. 프로젝트 정보 표시
    show_project_info
}

# 스크립트 실행
main "$@"

