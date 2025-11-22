#!/bin/bash
# 빠른 테스트: 서버가 정상 실행되는지 확인

cd "$(dirname "$0")"

# 가상 환경 활성화
if [ -d "venv" ] && [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# ROS2 환경 설정
source /opt/ros/humble/setup.bash 2>/dev/null
source ../install/setup.bash 2>/dev/null

# 환경 변수
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export SERVER_PORT=8004

# 서버를 백그라운드로 실행
echo "서버 시작 중..."
python3 run_standalone.py &
SERVER_PID=$!

# 서버 시작 대기
sleep 3

# Health Check
echo ""
echo "Health Check 테스트..."
curl -s http://localhost:8004/health | python3 -m json.tool || echo "서버 응답 없음"

# 서버 종료
echo ""
echo "서버 종료 중..."
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

echo "테스트 완료"
