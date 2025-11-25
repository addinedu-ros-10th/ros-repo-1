#!/bin/bash
# LCD 화면 지우기 테스트 스크립트

API_URL="http://localhost:8004"

echo "=========================================="
echo "LCD 화면 지우기 테스트"
echo "=========================================="
echo ""

echo "1. Health Check"
echo "----------------------------------------"
curl -s "${API_URL}/health" | jq '.services.ros2' 2>/dev/null || echo "ROS2 서비스 상태 확인"
echo ""

echo "2. LCD 화면 지우기"
echo "----------------------------------------"
response=$(curl -s -X POST "${API_URL}/api/lcd/clear" \
    -H "Content-Type: application/json")
echo "$response" | jq '.' 2>/dev/null || echo "$response"
echo ""

echo "=========================================="
echo "테스트 완료"
echo "=========================================="

