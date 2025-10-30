#!/bin/bash
# ==============================================
# Git Commit Message Template Setup Script
# ==============================================

set -e

TEMPLATE_PATH="$(pwd)/.gitmessage.txt"

if [ ! -f "$TEMPLATE_PATH" ]; then
  echo "⚠️  템플릿 파일이 존재하지 않습니다: $TEMPLATE_PATH"
  echo "⏳ 템플릿을 새로 생성합니다..."
  cat <<'EOF' > "$TEMPLATE_PATH"
# ==============================================
# 📝 Git Commit Message Template
# Company: ConAI
# Author: IT 총괄 정규호
# Version: v1.0
# Date: $(date +"%Y-%m-%d")
# ==============================================

# [Type] [Category/Project]: [Summary]
# ----------------------------------------------
# Type: feat | fix | refactor | chore | docs | test | style | perf | ci
# Category: IOT | SERVER | AI | DEEP_LEARNING | APP
# Project: app-server | ros2-server | mcp-server | deep-learning-server | web-app 등
# Summary: 간결하게 현재 변경 요약 (50자 이내)
EOF
fi

echo "🔧 Git commit message template 설정 중..."
git config commit.template "$TEMPLATE_PATH"

echo "✅ 설정 완료!"
echo "📄 현재 템플릿 경로: $(git config commit.template)"
echo "✍️  커밋 메시지 작성 시 자동으로 템플릿이 로드됩니다."
