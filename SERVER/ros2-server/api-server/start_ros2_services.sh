#!/bin/bash
# ROS2 서비스 자동 시작 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# ROS2 환경 설정
if [ -d "/opt/ros/jazzy" ]; then
    ROS_DISTRO="jazzy"
elif [ -d "/opt/ros/humble" ]; then
    ROS_DISTRO="humble"
else
    echo "❌ ROS2가 설치되어 있지 않습니다"
    exit 1
fi

source /opt/ros/$ROS_DISTRO/setup.bash
source "$WORKSPACE_ROOT/SERVER/ros2-server/install/setup.bash"

# ROS2 도메인 ID 설정
export ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}"

echo "============================================================"
echo "ROS2 서비스 자동 시작"
echo "============================================================"
echo "ROS2 버전: $ROS_DISTRO"
echo "ROS_DOMAIN_ID: $ROS_DOMAIN_ID"
echo ""

# LCD 컨트롤러 서버 실행 (백그라운드)
echo "🚀 LCD 컨트롤러 서버 시작 중..."
ros2 run pinky_lcd_display_controller lcd_controller_server &
LCD_PID=$!

# 서버 시작 대기
sleep 3

# 서비스 확인
echo "📋 ROS2 서비스 확인 중..."
if ros2 service list | grep -q lcd_controller; then
    echo "✅ LCD 컨트롤러 서비스 확인됨"
    ros2 service list | grep lcd_controller
else
    echo "❌ LCD 컨트롤러 서비스가 시작되지 않았습니다"
    kill $LCD_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ LCD 컨트롤러 서버 실행 중 (PID: $LCD_PID)"
echo "종료하려면: kill $LCD_PID"
echo ""

# API 서버 실행
echo "🚀 API 서버 시작 중..."
cd "$SCRIPT_DIR"
./run_standalone.sh

# 정리
kill $LCD_PID 2>/dev/null
