#!/bin/bash
# 네임스페이스 불일치 빠른 수정 스크립트

echo "============================================================"
echo "ROS2 네임스페이스 설정 확인 및 수정"
echo "============================================================"
echo ""

# .env.local 확인
if [ -f ".env.local" ]; then
    echo "현재 .env.local 설정:"
    grep -E "(ROS2_NAMESPACE|ROS2_SERVICE_NAME)" .env.local || echo "설정 없음"
    echo ""
    
    # 네임스페이스가 /pinky로 설정되어 있으면 빈 문자열로 변경
    if grep -q "ROS2_NAMESPACE=/pinky" .env.local; then
        echo "⚠️  네임스페이스가 /pinky로 설정되어 있습니다"
        echo "서비스는 루트 네임스페이스(/)에 있으므로 빈 문자열로 변경합니다"
        sed -i 's/ROS2_NAMESPACE=\/pinky/ROS2_NAMESPACE=/' .env.local
        echo "✅ .env.local 업데이트 완료"
    else
        echo "✅ 네임스페이스 설정 확인됨"
    fi
else
    echo "⚠️  .env.local 파일이 없습니다"
    echo "생성 중..."
    cat > .env.local << ENVEOF
# ROS2 설정
ROS2_NAMESPACE=
ROS2_SERVICE_NAME=lcd_controller/set_display

# 서버 설정
SERVER_PORT=8004

# IoT Data Server
IOT_DATA_SERVER_URL=http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com
ENVEOF
    echo "✅ .env.local 생성 완료"
fi

echo ""
echo "현재 설정:"
grep -E "(ROS2_NAMESPACE|ROS2_SERVICE_NAME)" .env.local
echo ""
echo "============================================================"
