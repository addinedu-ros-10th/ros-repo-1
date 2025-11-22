#!/bin/bash
# 맞춤형 이동식 대화 시나리오 테스트 스크립트

BASE_URL="http://localhost:8004/api/templates/scenario"

echo "============================================================"
echo "맞춤형 이동식 대화 시나리오 테스트"
echo "============================================================"
echo ""

# 샘플 1: 생활실로 이동하며 날씨 이야기
echo "1. 생활실로 이동하며 날씨 이야기 테스트..."
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

# 샘플 2: 식당으로 이동하며 식사 메뉴 이야기
echo "2. 식당으로 이동하며 식사 메뉴 이야기 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Akaza",
    "additional_data": {
      "topic": "오늘 식사 메뉴",
      "destination": "1층 식당"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# 샘플 3: 복도 산책하며 건강 이야기
echo "3. 복도 산책하며 건강 이야기 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "user_id": "00000000-0000-0000-0000-000000000001",
    "additional_data": {
      "topic": "건강 이야기",
      "destination": "2층 복도"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# 샘플 4: 휴게실로 이동하며 가족 이야기
echo "4. 휴게실로 이동하며 가족 이야기 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "conversation",
    "nickname": "Zenitsu Agatsuma",
    "additional_data": {
      "topic": "가족 이야기",
      "destination": "2층 휴게실"
    }
  }' | python3 -m json.tool
echo ""
echo ""

echo "============================================================"
echo "테스트 완료"
echo "============================================================"
