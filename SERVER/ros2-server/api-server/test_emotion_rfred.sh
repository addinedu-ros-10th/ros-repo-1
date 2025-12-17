#!/bin/bash
# Emotion 패키지 테스트 스크립트 (rfred 버전)

echo "=========================================="
echo "Emotion 패키지 테스트 (rfred 버전)"
echo "=========================================="

API_URL="http://localhost:8004/api/emotion/set"

# 지원하는 감정 타입
EMOTIONS=("hello" "basic" "angry" "bored" "fun" "happy" "interest" "sad")

echo ""
echo "테스트할 감정 타입: ${EMOTIONS[@]}"
echo ""

for emotion in "${EMOTIONS[@]}"; do
    echo "----------------------------------------"
    echo "테스트: $emotion"
    echo "----------------------------------------"
    
    response=$(curl -s -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{\"emotion\": \"$emotion\"}")
    
    echo "응답: $response"
    echo ""
    
    # 성공 여부 확인
    if echo "$response" | grep -q '"success":true'; then
        echo "✅ 성공: $emotion"
    else
        echo "❌ 실패: $emotion"
        echo "   응답: $response"
    fi
    
    echo ""
    sleep 1
done

echo "=========================================="
echo "테스트 완료"
echo "=========================================="

