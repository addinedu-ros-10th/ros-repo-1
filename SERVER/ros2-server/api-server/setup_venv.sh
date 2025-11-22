#!/bin/bash
# 프로젝트 독립 venv 설정 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "프로젝트 독립 venv 설정"
echo "============================================================"
echo ""

# 기존 venv 제거 여부 확인
if [ -d "venv" ]; then
    echo "⚠️  기존 venv 발견: $(du -sh venv 2>/dev/null | cut -f1 || echo '크기 확인 불가')"
    if [ "$1" = "--force" ] || [ "$1" = "-f" ]; then
        echo "🗑️  기존 venv 제거 중... (--force 옵션)"
        rm -rf venv
    else
        read -p "기존 venv를 제거하고 새로 생성하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🗑️  기존 venv 제거 중..."
            rm -rf venv
        else
            echo "ℹ️  기존 venv 유지"
        fi
    fi
fi

# venv 생성
if [ ! -d "venv" ]; then
    echo "🐍 새로운 venv 생성 중..."
    python3 -m venv venv
    echo "✅ venv 생성 완료"
else
    echo "ℹ️  기존 venv 사용"
fi

# venv 활성화
echo "🐍 venv 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "📦 pip 업그레이드 중..."
pip install --upgrade pip setuptools wheel

# requirements.txt 설치
echo "📦 Python 패키지 설치 중..."
pip install -r requirements.txt

echo ""
echo "✅ venv 설정 완료!"
echo "============================================================"
echo "활성화 방법:"
echo "  source venv/bin/activate"
echo ""
echo "서버 실행:"
echo "  ./run_standalone.sh"
echo ""
echo "참고:"
echo "  - ROS2는 시스템 패키지이므로 run_standalone.sh에서 자동으로 설정됩니다"
echo "  - ROS2 버전은 자동 감지됩니다 (jazzy 우선)"
echo "============================================================"
