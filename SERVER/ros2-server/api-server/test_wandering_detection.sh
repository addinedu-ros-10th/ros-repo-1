#!/bin/bash
# 배회 감지 시나리오 테스트 스크립트

BASE_URL="http://localhost:8004/api/templates/scenario"

echo "============================================================"
echo "배회 감지 시나리오 테스트"
echo "============================================================"
echo ""

# 샘플 1: 1층 복도
echo "1. 1층 복도 배회 감지 테스트..."
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

# 샘플 2: 2층 계단
echo "2. 2층 계단 배회 감지 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "wandering_detection",
    "nickname": "Akaza",
    "additional_data": {
      "location": "2층 계단",
      "camera_id": "camera_002"
    }
  }' | python3 -m json.tool
echo ""
echo ""

# 샘플 3: 1층 로비
echo "3. 1층 로비 배회 감지 테스트..."
curl -X 'POST' "$BASE_URL" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "scenario": "wandering_detection",
    "user_id": "00000000-0000-0000-0000-000000000001",
    "additional_data": {
      "location": "1층 로비",
      "camera_id": "camera_003"
    }
  }' | python3 -m json.tool
echo ""
echo ""

echo "============================================================"
echo "테스트 완료"
echo "============================================================"
