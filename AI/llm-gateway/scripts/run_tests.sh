#!/bin/bash
# 테스트 실행 스크립트

set -e

echo "🧪 Running tests..."

# 단위 테스트
echo "📦 Running unit tests..."
pytest tests/unit -v -m unit

# 통합 테스트
echo "🔗 Running integration tests..."
pytest tests/integration -v -m integration

# E2E 테스트
echo "🌐 Running E2E tests..."
pytest tests/e2e -v -m e2e

# 전체 테스트
echo "✅ All tests completed!"

