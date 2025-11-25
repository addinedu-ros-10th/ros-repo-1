#!/bin/bash
# 감정 표현 API 테스트 스크립트

API_URL="http://localhost:8004"

echo "=========================================="
echo "감정 표현 API 테스트"
echo "=========================================="
echo ""

# 지원하는 감정 타입들
emotions=("hello" "basic" "angry" "bored" "fun" "happy" "interest" "sad")

echo "1. Health Check"
echo "----------------------------------------"
curl -s "${API_URL}/health" | jq '.'
echo ""
echo ""

echo "2. 감정 표현 테스트"
echo "----------------------------------------"
for emotion in "${emotions[@]}"; do
    echo "테스트: ${emotion}"
    response=$(curl -s -X POST "${API_URL}/api/emotion/set" \
        -H "Content-Type: application/json" \
        -d "{\"emotion\": \"${emotion}\"}")
    echo "$response" | jq '.'
    echo ""
    sleep 1
done

echo "3. 잘못된 감정 타입 테스트"
echo "----------------------------------------"
curl -s -X POST "${API_URL}/api/emotion/set" \
    -H "Content-Type: application/json" \
    -d '{"emotion": "invalid"}' | jq '.'
echo ""

echo "=========================================="
echo "테스트 완료"
echo "=========================================="

