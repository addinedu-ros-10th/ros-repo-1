#!/bin/bash
# ROS2 API Server 스탠드얼론 실행 스크립트
# 
# 사용 방법:
#   chmod +x run_standalone.sh
#   ./run_standalone.sh

set -e

# 스크립트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ROS2 환경 설정
# ROS2 버전 자동 감지 (jazzy 우선, 없으면 humble)
ROS_DISTRO=""
if [ -d "/opt/ros/jazzy" ]; then
    ROS_DISTRO="jazzy"
elif [ -d "/opt/ros/humble" ]; then
    ROS_DISTRO="humble"
else
    # 다른 버전 확인
    ROS_DISTRO=$(ls -1 /opt/ros/ 2>/dev/null | head -1)
fi

ROS_WORKSPACE="$(dirname "$SCRIPT_DIR")"  # SERVER/ros2-server

echo "============================================================"
echo "ROS2 API Server 스탠드얼론 실행"
echo "============================================================"
echo ""

# ROS2 설치 확인
if [ -z "$ROS_DISTRO" ] || [ ! -d "/opt/ros/$ROS_DISTRO" ]; then
    echo "❌ ROS2가 설치되어 있지 않습니다"
    echo "확인된 ROS2 버전: $ROS_DISTRO"
    echo "설치 방법: sudo apt install ros-jazzy-desktop 또는 ros-humble-desktop"
    exit 1
fi

# ROS2 환경 설정
echo "📦 ROS2 환경 설정 중... (버전: $ROS_DISTRO)"
source /opt/ros/$ROS_DISTRO/setup.bash

# ROS2 워크스페이스 환경 설정
if [ -f "$ROS_WORKSPACE/install/setup.bash" ]; then
    echo "📦 ROS2 워크스페이스 환경 설정 중..."
    source "$ROS_WORKSPACE/install/setup.bash"
else
    echo "⚠️  ROS2 워크스페이스가 빌드되지 않았습니다: $ROS_WORKSPACE/install"
    echo "빌드 방법: cd $ROS_WORKSPACE && colcon build"
fi

# Python 가상 환경 확인 (선택적)
if [ -d "venv" ]; then
    echo "🐍 가상 환경 활성화 중 (venv)..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🐍 가상 환경 활성화 중 (.venv)..."
    source .venv/bin/activate
elif [ -n "$VIRTUAL_ENV" ]; then
    echo "🐍 가상 환경이 이미 활성화되어 있습니다: $VIRTUAL_ENV"
else
    echo "ℹ️  가상 환경이 없습니다. 시스템 Python을 사용합니다."
fi

# Python 의존성 확인
echo "📋 Python 의존성 확인 중..."
python3 -c "import fastapi, uvicorn, httpx" 2>/dev/null || {
    echo "❌ 필수 Python 패키지가 설치되지 않았습니다"
    echo "설치 방법: pip install -r requirements.txt"
    exit 1
}

# ROS2 모듈 확인
echo "🤖 ROS2 모듈 확인 중..."
python3 -c "import rclpy" 2>/dev/null || {
    echo "❌ ROS2 Python 모듈 (rclpy)을 찾을 수 없습니다"
    echo "ROS2 버전: $ROS_DISTRO"
    echo "설치 방법: sudo apt install ros-$ROS_DISTRO-rclpy"
    echo ""
    echo "참고: ROS2 환경이 제대로 설정되었는지 확인하세요:"
    echo "  source /opt/ros/$ROS_DISTRO/setup.bash"
    exit 1
}

# ROS2 도메인 ID 설정 (환경 변수 또는 기본값 13)
# 사용 가능한 도메인 ID 목록 (환경 변수 또는 기본값 "11,12,13")
ROS2_DOMAIN_ID_ALLOWED="${ROS2_DOMAIN_ID_ALLOWED:-11,12,13}"
ROS2_DOMAIN_ID="${ROS2_DOMAIN_ID:-13}"

# 도메인 ID 검증 함수
validate_domain_id() {
    local domain_id=$1
    local allowed_list=$2
    
    # 범위 확인 (0~232)
    if [ "$domain_id" -lt 0 ] || [ "$domain_id" -gt 232 ]; then
        echo "❌ ROS2_DOMAIN_ID는 0~232 사이의 값이어야 합니다: $domain_id"
        return 1
    fi
    
    # 허용된 목록 확인 (설정된 경우)
    if [ -n "$allowed_list" ]; then
        IFS=',' read -ra ALLOWED <<< "$allowed_list"
        local found=0
        for allowed_id in "${ALLOWED[@]}"; do
            if [ "$domain_id" -eq "$allowed_id" ]; then
                found=1
                break
            fi
        done
        
        if [ $found -eq 0 ]; then
            echo "❌ ROS2_DOMAIN_ID $domain_id는 허용된 값이 아닙니다."
            echo "   허용된 값: $allowed_list"
            echo "   다른 값을 사용하려면 ROS2_DOMAIN_ID_ALLOWED 환경 변수를 설정하세요."
            return 1
        fi
    fi
    
    return 0
}

# 도메인 ID 검증
if ! validate_domain_id "$ROS2_DOMAIN_ID" "$ROS2_DOMAIN_ID_ALLOWED"; then
    exit 1
fi

# 환경 변수 설정
export ROS_DOMAIN_ID="$ROS2_DOMAIN_ID"
export RMW_IMPLEMENTATION="${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}"
# 포트 설정: 환경 변수 또는 기본값 8004 (포트 충돌 방지)
export SERVER_PORT="${SERVER_PORT:-8004}"

echo ""
echo "✅ 환경 설정 완료"
echo "============================================================"
echo "서버 포트: $SERVER_PORT"
echo "ROS2 도메인 ID: $ROS_DOMAIN_ID (허용된 값: $ROS2_DOMAIN_ID_ALLOWED)"
echo "============================================================"
echo ""

# 서버 실행
echo "🚀 서버 시작 중..."
python3 run_standalone.py

