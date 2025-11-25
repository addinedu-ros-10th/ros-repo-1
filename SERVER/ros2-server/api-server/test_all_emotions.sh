#!/bin/bash
# 모든 감정 표현 테스트 스크립트

API_URL="http://localhost:8004"

echo "=========================================="
echo "감정 표현 전체 테스트"
echo "=========================================="
echo ""

# 지원하는 모든 감정 타입
emotions=("hello" "basic" "angry" "bored" "fun" "happy" "interest" "sad")

echo "📋 지원하는 감정 타입:"
for emotion in "${emotions[@]}"; do
    echo "  - $emotion"
done
echo ""

echo "1. Health Check"
echo "----------------------------------------"
curl -s "${API_URL}/health" | jq '.services.emotion' 2>/dev/null || echo "emotion 서비스 상태 확인"
echo ""

echo "2. 감정 표현 테스트 (API 서버)"
echo "----------------------------------------"
for emotion in "${emotions[@]}"; do
    echo "테스트: $emotion"
    response=$(curl -s -X POST "${API_URL}/api/emotion/set" \
        -H "Content-Type: application/json" \
        -d "{\"emotion\": \"${emotion}\"}")
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
    sleep 2  # 각 감정 표현 사이에 2초 대기
done

echo "=========================================="
echo "테스트 완료"
echo "=========================================="

