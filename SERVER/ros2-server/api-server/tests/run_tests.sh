#!/bin/bash

# ROS2 API Server 테스트 스크립트

BASE_URL="http://localhost:8003"

echo "=========================================="
echo "ROS2 API Server 테스트"
echo "=========================================="
echo "테스트 대상: $BASE_URL"
echo ""

# jq가 설치되어 있는지 확인
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq가 설치되어 있지 않습니다. JSON 출력이 보기 좋지 않을 수 있습니다."
    echo "   설치: sudo apt install jq (Ubuntu/Debian)"
    echo ""
    JQ_CMD="cat"
else
    JQ_CMD="jq ."
fi

# 헬스 체크
echo "1. 헬스 체크 테스트..."
HEALTH_RESPONSE=$(curl -s "$BASE_URL/health")
if [ $? -eq 0 ]; then
    echo "$HEALTH_RESPONSE" | $JQ_CMD
    echo "✅ 헬스 체크 성공"
else
    echo "❌ 헬스 체크 실패 (서버가 실행 중이지 않을 수 있습니다)"
    exit 1
fi
echo ""

# 어르신 탐지 API
echo "2. 어르신 탐지 API 테스트..."
DETECTION_RESPONSE=$(curl -s -X POST "$BASE_URL/api/detection/resident" \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "camera_001",
    "display_format": "basic"
  }')

if [ $? -eq 0 ]; then
    echo "$DETECTION_RESPONSE" | $JQ_CMD
    echo "✅ 어르신 탐지 API 성공"
else
    echo "❌ 어르신 탐지 API 실패"
fi
echo ""

# 아침인사 템플릿
echo "3. 아침인사 템플릿 테스트..."
MORNING_RESPONSE=$(curl -s -X POST "$BASE_URL/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "morning_greeting",
    "nickname": "Akaza",
    "additional_data": {"weather": "맑은"}
  }')

if [ $? -eq 0 ]; then
    echo "$MORNING_RESPONSE" | $JQ_CMD
    echo "✅ 아침인사 템플릿 성공"
else
    echo "❌ 아침인사 템플릿 실패"
fi
echo ""

# 식사 지원 템플릿
echo "4. 식사 지원 템플릿 테스트..."
MEAL_RESPONSE=$(curl -s -X POST "$BASE_URL/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "meal_assistance",
    "nickname": "Akaza",
    "additional_data": {"menu": "된장찌개", "meal_time": "12:00"}
  }')

if [ $? -eq 0 ]; then
    echo "$MEAL_RESPONSE" | $JQ_CMD
    echo "✅ 식사 지원 템플릿 성공"
else
    echo "❌ 식사 지원 템플릿 실패"
fi
echo ""

# 배회 감지 템플릿
echo "5. 배회 감지 템플릿 테스트..."
WANDERING_RESPONSE=$(curl -s -X POST "$BASE_URL/api/templates/scenario" \
  -H "Content-Type: application/json" \
  -d '{
    "scenario": "wandering_detection",
    "nickname": "Akaza",
    "additional_data": {"location": "1층 복도", "camera_id": "camera_001"}
  }')

if [ $? -eq 0 ]; then
    echo "$WANDERING_RESPONSE" | $JQ_CMD
    echo "✅ 배회 감지 템플릿 성공"
else
    echo "❌ 배회 감지 템플릿 실패"
fi
echo ""

echo "=========================================="
echo "테스트 완료"
echo "=========================================="

