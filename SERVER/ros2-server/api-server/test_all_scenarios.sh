#!/bin/bash
# 시나리오 템플릿 전체 테스트 스크립트

BASE_URL="http://localhost:8004/api/templates/scenario"

echo "============================================================"
echo "시나리오 템플릿 테스트"
echo "============================================================"
echo ""

# 1. 아침인사
echo "1. 아침인사 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "morning_greeting",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "weather": "맑은"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# 2. 식사 지원
echo "2. 식사 지원 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "meal_assistance",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "menu": "된장찌개",
      "meal_time": "12:00"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# 3. 맞춤형 이동식 대화
echo "3. 맞춤형 이동식 대화 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "topic": "오늘 날씨 이야기",
      "destination": "3층 302호 생활실"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# 4. 배회 감지
echo "4. 배회 감지 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "wandering_detection",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "location": "1층 복도",
      "camera_id": "camera_001"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# 5. 면회객 안내
echo "5. 면회객 안내 시나리오 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "visitor_guidance",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "visitor_name": "정기우",
      "visitor_relationship": "아들",
      "meeting_room": "면회실"
    }
  }' | python3 -m json.tool
echo ""
echo ""

echo "============================================================"
echo "테스트 완료"
echo "============================================================"
