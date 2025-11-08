#!/usr/bin/env bash
# Pinky 로봇 SSH 접속 시 자동 Git 동기화 설정 스크립트
#
# 이 스크립트는 ~/.bashrc에 sync_pinky_git.sh 자동 실행을 추가합니다.
#
# Usage:
#   ./setup_pinky_auto_sync.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SYNC_SCRIPT="$SCRIPT_DIR/sync_pinky_git.sh"
BASHRC_FILE="$HOME/.bashrc"
MARKER="# Pinky Git Auto Sync"

# 색상 출력
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# 동기화 스크립트 존재 확인
if [ ! -f "$SYNC_SCRIPT" ]; then
    log_error "동기화 스크립트를 찾을 수 없습니다: $SYNC_SCRIPT"
    exit 1
fi

# 실행 권한 부여
chmod +x "$SYNC_SCRIPT"
log_info "동기화 스크립트에 실행 권한을 부여했습니다: $SYNC_SCRIPT"

# .bashrc 파일 확인
if [ ! -f "$BASHRC_FILE" ]; then
    log_warn ".bashrc 파일이 없습니다. 생성합니다..."
    touch "$BASHRC_FILE"
fi

# 이미 설정되어 있는지 확인
if grep -q "$MARKER" "$BASHRC_FILE" 2>/dev/null; then
    log_warn "이미 자동 동기화가 설정되어 있습니다."
    log_info "기존 설정을 제거하고 다시 추가합니다..."
    
    # 기존 설정 제거 (마커부터 다음 빈 줄까지)
    sed -i "/$MARKER/,/^$/d" "$BASHRC_FILE" 2>/dev/null || true
fi

# .bashrc에 추가할 내용
AUTO_SYNC_CONFIG=$(cat <<EOF

$MARKER
# SSH 접속 시 자동으로 Git 저장소 동기화
if [ -f "$SYNC_SCRIPT" ]; then
    # 비대화형 모드가 아니고 (SSH 세션인 경우) 실행
    if [ -n "\$SSH_CLIENT" ] || [ -n "\$SSH_TTY" ]; then
        # 백그라운드에서 실행하여 로그인 지연 방지
        bash "$SYNC_SCRIPT" > /tmp/pinky_git_sync.log 2>&1 &
    fi
fi
EOF
)

# .bashrc에 추가
echo "$AUTO_SYNC_CONFIG" >> "$BASHRC_FILE"
log_info ".bashrc에 자동 동기화 설정을 추가했습니다."

log_info "설정 완료!"
log_info ""
log_info "다음 SSH 접속 시부터 자동으로 Git 동기화가 실행됩니다."
log_info "로그는 /tmp/pinky_git_sync.log 파일에서 확인할 수 있습니다."
log_info ""
log_info "즉시 적용하려면 다음 명령을 실행하세요:"
log_info "  source ~/.bashrc"
log_info ""
log_info "또는 수동으로 동기화를 실행하려면:"
log_info "  $SYNC_SCRIPT"

