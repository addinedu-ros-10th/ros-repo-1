#!/bin/bash
# 빠른 테스트 스크립트

cd "$(dirname "$0")"

# 가상 환경 활성화
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# ROS2 환경 설정
source /opt/ros/humble/setup.bash 2>/dev/null || echo "ROS2 환경 설정 실패"
source ../install/setup.bash 2>/dev/null || echo "워크스페이스 환경 설정 실패"

# 환경 변수
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export SERVER_PORT=8004

# Python 의존성 확인
echo "Python 의존성 확인 중..."
python3 -c "import fastapi, uvicorn, httpx; print('✅ 필수 패키지 확인')" || {
    echo "❌ 필수 패키지 설치 필요: pip install -r requirements.txt"
    exit 1
}

# ROS2 모듈 확인
echo "ROS2 모듈 확인 중..."
python3 -c "import rclpy; print('✅ ROS2 모듈 확인')" || {
    echo "❌ ROS2 모듈 없음 (ROS2 환경 설정 필요)"
    exit 1
}

echo ""
echo "✅ 모든 확인 완료!"
echo "서버 실행: python3 run_standalone.py"
