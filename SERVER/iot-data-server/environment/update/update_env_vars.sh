#!/bin/bash
# update_env_vars.sh
# IoT Care Backend System 환경변수 자동 업데이트 스크립트
# 모든 운영체제 (Linux, macOS, Windows)에서 실행 가능

echo "🔍 IoT Care Backend System 환경변수 자동 업데이트 시작..."
echo "📅 실행 시간: $(date)"
echo ""

# 현재 작업 디렉토리 확인
echo "📍 현재 작업 디렉토리: $(pwd)"

# 프로젝트 루트 디렉토리로 이동 (.env.local이 있는 위치)
PROJECT_ROOT="$(cd ../.. && pwd)"
echo "📍 프로젝트 루트 디렉토리: $PROJECT_ROOT"

# .env.local 파일 존재 확인 (프로젝트 루트 기준)
ENV_FILE="$PROJECT_ROOT/.env.local"
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ .env.local 파일을 찾을 수 없습니다: $ENV_FILE"
    echo "💡 프로젝트 루트에 .env.local 파일이 있는지 확인하세요."
    exit 1
fi

echo "✅ .env.local 파일 발견: $ENV_FILE"

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
echo "📍 운영체제: $OS"

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
        ip=$(powershell -Command "Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*'} | Select-Object -First 1 -ExpandProperty IPAddress" 2>/dev/null | tr -d '\r')
    fi
    
    # ipconfig 사용
    if [ -z "$ip" ]; then
        ip=$(ipconfig 2>/dev/null | grep "IPv4" | head -1 | sed 's/.*: //' | tr -d '\r')
    fi
    
    echo "$ip"
}

# 현재 IP 주소 조회
echo "🔍 현재 개발 머신 IP 주소 조사 중..."

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
        echo "⚠️  지원하지 않는 운영체제: $OS"
        echo "💡 fallback 방법으로 IP 주소 조회 시도..."
        # 소켓을 사용한 fallback
        if command -v python3 >/dev/null 2>&1; then
            CURRENT_IP=$(python3 -c "
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
        ;;
esac

if [ -z "$CURRENT_IP" ]; then
    echo "❌ IP 주소를 찾을 수 없습니다."
    echo "💡 수동으로 IP 주소를 확인하고 환경변수를 업데이트하세요."
    echo "💡 Linux/macOS: ip addr 또는 ifconfig"
    echo "💡 Windows: ipconfig 또는 powershell -Command 'ipconfig'"
    exit 1
fi

echo "✅ 현재 IP 주소: $CURRENT_IP"

# 현재 .env.local 파일의 IP 설정 확인
echo ""
echo "📋 현재 .env.local 파일의 IP 설정:"
grep -E "^(DB_HOST|CADDY_DOMAIN)=" "$ENV_FILE" || echo "⚠️  IP 관련 환경변수를 찾을 수 없습니다."

# 백업 파일 생성
BACKUP_FILE="$PROJECT_ROOT/.env.local.backup.$(date +%Y%m%d_%H%M%S)"
cp "$ENV_FILE" "$BACKUP_FILE"
echo "💾 백업 파일 생성: $BACKUP_FILE"

# 환경변수 업데이트
echo ""
echo "📝 .env.local 파일 업데이트 중..."

# 운영체제별 sed 명령어 결정
if [ "$OS" = "macos" ]; then
    SED_CMD="sed -i ''"
else
    SED_CMD="sed -i"
fi

# DB_HOST 업데이트
if grep -q "DB_HOST=" "$ENV_FILE"; then
    $SED_CMD "s/DB_HOST=.*/DB_HOST=$CURRENT_IP/g" "$ENV_FILE"
    echo "✅ DB_HOST 업데이트 완료: $CURRENT_IP"
else
    echo "⚠️  DB_HOST 환경변수가 .env.local 파일에 없습니다."
fi

# CADDY_DOMAIN 업데이트
if grep -q "CADDY_DOMAIN=" "$ENV_FILE"; then
    $SED_CMD "s/CADDY_DOMAIN=.*/CADDY_DOMAIN=$CURRENT_IP/g" "$ENV_FILE"
    echo "✅ CADDY_DOMAIN 업데이트 완료: $CURRENT_IP"
else
    echo "⚠️  CADDY_DOMAIN 환경변수가 .env.local 파일에 없습니다."
fi

# 업데이트된 내용 확인
echo ""
echo "📋 업데이트된 환경변수:"
grep -E "^(DB_HOST|CADDY_DOMAIN)=" "$ENV_FILE" || echo "⚠️  업데이트된 환경변수를 찾을 수 없습니다."

echo ""
echo "🎯 다음 단계: Docker 환경 재시작"
echo "💡 명령어: docker-compose down && docker-compose up -d"
echo "💡 또는 이 스크립트를 --restart 옵션과 함께 실행하세요."

# --restart 옵션이 있는 경우 Docker 재시작
if [ "$1" = "--restart" ]; then
    echo ""
    echo "🚀 Docker 환경 자동 재시작 시작..."
    
    # Docker 컨테이너 중지
    echo "⏹️  Docker 컨테이너 중지 중..."
    docker-compose down --volumes --remove-orphans
    
    # Docker 시스템 정리
    echo "🧹 Docker 시스템 정리 중..."
    docker system prune -f
    
    # 프로젝트 재시작
    echo "🔄 프로젝트 재시작 중..."
    docker-compose up -d
    
    # 상태 확인
    echo ""
    echo "📊 Docker 컨테이너 상태:"
    docker-compose ps
    
    # API 서버 상태 확인
    echo ""
    echo "🔍 API 서버 상태 확인 중..."
    sleep 10  # 서버 시작 대기
    
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API 서버 정상 동작"
    else
        echo "❌ API 서버 응답 없음"
        echo "💡 docker logs iot-care-app 명령으로 로그를 확인하세요."
    fi
    
    echo ""
    echo "🎉 환경변수 업데이트 및 Docker 재시작 완료!"
fi

echo ""
echo "✅ 환경변수 자동 업데이트 완료!"
echo "📅 완료 시간: $(date)"
