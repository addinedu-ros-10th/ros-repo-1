#!/bin/bash

# IoT Care API 엔드포인트 테스트 스크립트
# 서버가 정상적으로 실행되고 있는지 확인

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔧 IoT Care API 엔드포인트 테스트 시작"
echo "📍 테스트 대상: $BASE_URL"
echo "=" * 60

# 헬스 체크
echo "🔍 헬스 체크 테스트..."
if curl -s "$BASE_URL/health" > /dev/null; then
    echo -e "${GREEN}✅ 헬스 체크 성공${NC}"
else
    echo -e "${RED}❌ 헬스 체크 실패${NC}"
    exit 1
fi

# Swagger UI 접근 테스트
echo "🔍 Swagger UI 접근 테스트..."
if curl -s "$BASE_URL/docs" > /dev/null; then
    echo -e "${GREEN}✅ Swagger UI 접근 성공${NC}"
else
    echo -e "${RED}❌ Swagger UI 접근 실패${NC}"
fi

# OpenAPI 스키마 접근 테스트
echo "🔍 OpenAPI 스키마 접근 테스트..."
if curl -s "$BASE_URL/openapi.json" > /dev/null; then
    echo -e "${GREEN}✅ OpenAPI 스키마 접근 성공${NC}"
    
    # API 엔드포인트 수 확인
    ENDPOINT_COUNT=$(curl -s "$BASE_URL/openapi.json" | jq '.paths | keys | length' 2>/dev/null)
    if [ "$ENDPOINT_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ API 엔드포인트 수: $ENDPOINT_COUNT${NC}"
    else
        echo -e "${YELLOW}⚠️ API 엔드포인트 수를 확인할 수 없습니다${NC}"
    fi
else
    echo -e "${RED}❌ OpenAPI 스키마 접근 실패${NC}"
fi

# 주요 API 엔드포인트 테스트
echo ""
echo "🔍 주요 API 엔드포인트 테스트..."

APIS=(
    "/api/v1/users/"
    "/api/v1/devices/"
    "/api/v1/loadcell/"
    "/api/v1/mq5/"
    "/api/v1/mq7/"
    "/api/v1/rfid/"
    "/api/v1/sound/"
    "/api/v1/tcrt5000/"
    "/api/v1/ultrasonic/"
    "/api/v1/edge-flame/"
    "/api/v1/edge-pir/"
    "/api/v1/edge-reed/"
    "/api/v1/edge-tilt/"
    "/api/v1/actuator-buzzer/"
    "/api/v1/actuator-irtx/"
    "/api/v1/actuator-relay/"
    "/api/v1/actuator-servo/"
)

SUCCESS_COUNT=0
TOTAL_COUNT=${#APIS[@]}

for api in "${APIS[@]}"; do
    if curl -s "$BASE_URL$api" > /dev/null; then
        echo -e "${GREEN}✅ $api${NC}"
        ((SUCCESS_COUNT++))
    else
        echo -e "${RED}❌ $api${NC}"
    fi
done

echo ""
echo "=" * 60
echo "📊 테스트 결과 요약"
echo "=" * 60
echo "총 API 엔드포인트: $TOTAL_COUNT"
echo "성공한 API: $SUCCESS_COUNT"
echo "실패한 API: $((TOTAL_COUNT - SUCCESS_COUNT))"

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}🎉 모든 API 엔드포인트가 정상적으로 작동합니다!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️ 일부 API 엔드포인트에 문제가 있습니다.${NC}"
    exit 1
fi 