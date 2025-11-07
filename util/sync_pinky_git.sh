#!/usr/bin/env bash
# Pinky 로봇 Git 상태 동기화 스크립트
# 
# 이 스크립트는 pinky 로봇의 git 저장소를 동기화합니다:
# 1. dev 브랜치로 switch
# 2. base/ROS2/* 브랜치들을 모두 pull
#
# Usage:
#   ./sync_pinky_git.sh

set -euo pipefail

# 설정
REPO_ROOT="/home/pinky/ros-repo-1"
GIT_REMOTE=${GIT_REMOTE:-origin}
REPO_URL="https://github.com/addinedu-ros-10th/ros-repo-1.git"

# 색상 출력 (선택적)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# 저장소 디렉토리 확인 및 생성
if [ ! -d "$REPO_ROOT" ]; then
    log_warn "저장소 디렉토리가 존재하지 않습니다: $REPO_ROOT"
    log_info "저장소를 클론합니다..."
    
    # 홈 디렉토리로 이동
    cd /home/pinky || {
        log_error "홈 디렉토리로 이동할 수 없습니다: /home/pinky"
        exit 1
    }
    
    # 저장소 클론
    git clone "$REPO_URL" "$REPO_ROOT" || {
        log_error "저장소 클론에 실패했습니다."
        exit 1
    }
    
    log_info "저장소 클론 완료: $REPO_ROOT"
fi

# 저장소 디렉토리로 이동
cd "$REPO_ROOT" || {
    log_error "저장소 디렉토리로 이동할 수 없습니다: $REPO_ROOT"
    exit 1
}

# Git 저장소인지 확인
if [ ! -d ".git" ]; then
    log_error "Git 저장소가 아닙니다: $REPO_ROOT"
    exit 1
fi

log_info "저장소 위치: $REPO_ROOT"

# 원격 저장소 정보 업데이트
log_info "원격 저장소 정보를 가져옵니다..."
git fetch --all --prune || {
    log_warn "git fetch에 실패했습니다. 계속 진행합니다..."
}

# dev 브랜치로 switch
log_info "dev 브랜치로 전환합니다..."

# dev 브랜치가 로컬에 없으면 원격에서 체크아웃
if ! git show-ref --verify --quiet refs/heads/dev; then
    log_info "로컬 dev 브랜치가 없습니다. 원격에서 체크아웃합니다..."
    git checkout -b dev origin/dev 2>/dev/null || {
        log_warn "원격 dev 브랜치를 찾을 수 없습니다. 기본 브랜치를 사용합니다."
        # 기본 브랜치 확인 (main 또는 master)
        if git show-ref --verify --quiet refs/heads/main; then
            git checkout main
        elif git show-ref --verify --quiet refs/heads/master; then
            git checkout master
        else
            log_error "기본 브랜치를 찾을 수 없습니다."
            exit 1
        fi
    }
else
    git checkout dev || {
        log_error "dev 브랜치로 전환할 수 없습니다."
        exit 1
    }
fi

# dev 브랜치 pull
log_info "dev 브랜치를 최신 상태로 업데이트합니다..."
git pull "$GIT_REMOTE" dev || {
    log_warn "dev 브랜치 pull에 실패했습니다. 계속 진행합니다..."
}

# base/ROS2/* 브랜치들 찾기 및 pull
log_info "base/ROS2/* 브랜치들을 찾는 중..."

# 배열로 브랜치 목록 저장
ROS2_BRANCHES_ARRAY=()

# 원격 브랜치 목록에서 base/ROS2/* 패턴 찾기
while IFS= read -r branch; do
    if [ -n "$branch" ]; then
        ROS2_BRANCHES_ARRAY+=("$branch")
    fi
done < <(git branch -r | grep -E "^\s*${GIT_REMOTE}/base/ROS2/" | sed "s|${GIT_REMOTE}/||" | sed 's/^[[:space:]]*//' || true)

# 원격에서 찾지 못했으면 로컬 브랜치에서 확인
if [ ${#ROS2_BRANCHES_ARRAY[@]} -eq 0 ]; then
    log_info "로컬 브랜치에서도 확인합니다..."
    while IFS= read -r branch; do
        if [ -n "$branch" ]; then
            ROS2_BRANCHES_ARRAY+=("$branch")
        fi
    done < <(git branch | grep -E "^\s*base/ROS2/" | sed 's/^\*\?[[:space:]]*//' || true)
fi

if [ ${#ROS2_BRANCHES_ARRAY[@]} -eq 0 ]; then
    log_warn "base/ROS2/* 브랜치를 찾을 수 없습니다. 스킵합니다."
else
    log_info "다음 브랜치들을 동기화합니다:"
    for branch in "${ROS2_BRANCHES_ARRAY[@]}"; do
        echo "  - $branch"
    done
    
    # 각 브랜치에 대해 pull 수행
    for branch in "${ROS2_BRANCHES_ARRAY[@]}"; do
        log_info "브랜치 동기화: $branch"
        
        # 로컬 브랜치가 있는지 확인
        if git show-ref --verify --quiet refs/heads/"$branch"; then
            # 로컬 브랜치가 있으면 체크아웃하고 pull
            git checkout "$branch" 2>/dev/null || {
                log_warn "브랜치 $branch로 전환할 수 없습니다. 스킵합니다."
                continue
            }
            git pull "$GIT_REMOTE" "$branch" 2>/dev/null || {
                log_warn "브랜치 $branch pull에 실패했습니다."
            }
        else
            # 로컬 브랜치가 없으면 원격에서 추적 브랜치 생성
            log_info "로컬 브랜치가 없습니다. 원격에서 추적 브랜치를 생성합니다: $branch"
            git checkout -b "$branch" "${GIT_REMOTE}/$branch" 2>/dev/null || {
                log_warn "브랜치 $branch를 생성할 수 없습니다. 스킵합니다."
                continue
            }
        fi
    done
    
    # 다시 dev 브랜치로 돌아가기
    log_info "dev 브랜치로 돌아갑니다..."
    git checkout dev || {
        log_warn "dev 브랜치로 돌아갈 수 없습니다."
    }
fi

log_info "동기화 완료!"

