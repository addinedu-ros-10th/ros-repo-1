#!/bin/bash
# 커스텀 텍스트 LCD 표시 테스트 스크립트

set -e

# 기본 설정
SERVER_URL="${SERVER_URL:-http://localhost:8004}"
ENDPOINT="${SERVER_URL}/api/lcd/display"

echo "============================================================"
echo "커스텀 텍스트 LCD 표시 테스트"
echo "============================================================"
echo "서버 URL: $SERVER_URL"
echo ""

# 테스트 케이스 1: 기본 커스텀 표시
echo "📋 테스트 1: 기본 커스텀 표시"
curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "안내사항",
    "lines": [
      "오늘은 휴진일입니다",
      "필요하시면 간병인을",
      "호출해주세요"
    ],
    "show_timestamp": true,
    "template_style": "custom"
  }' | jq '.'

echo ""
echo "⏳ 3초 대기..."
sleep 3
echo ""

# 테스트 케이스 2: 긴급 공지
echo "📋 테스트 2: 긴급 공지"
curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "긴급 공지",
    "lines": [
      "화재 대피 훈련",
      "오후 2시에 진행됩니다",
      "참여 부탁드립니다"
    ],
    "show_timestamp": true,
    "template_style": "custom"
  }' | jq '.'

echo ""
echo "⏳ 3초 대기..."
sleep 3
echo ""

# 테스트 케이스 3: 아침인사 스타일
echo "📋 테스트 3: 아침인사 스타일"
curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "안녕하세요! 어르신",
    "lines": [
      "오늘은 2025년 1월 22일",
      "수요일, 맑은 날씨입니다",
      "좋은 하루 되세요!"
    ],
    "show_timestamp": true,
    "template_style": "morning_greeting"
  }' | jq '.'

echo ""
echo "⏳ 3초 대기..."
sleep 3
echo ""

# 테스트 케이스 4: 식사 지원 스타일
echo "📋 테스트 4: 식사 지원 스타일"
curl -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "식사 시간입니다",
    "lines": [
      "오늘의 메뉴: 된장찌개",
      "저염식 준비",
      "천천히 드세요"
    ],
    "show_timestamp": true,
    "template_style": "meal_assistance"
  }' | jq '.'

echo ""
echo "============================================================"
echo "✅ 모든 테스트 완료"
echo "============================================================"

