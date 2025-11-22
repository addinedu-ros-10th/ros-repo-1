#!/usr/bin/env python3
"""정적 파일 서빙 테스트"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# 정적 파일 서빙 테스트
docs_dir = project_root / "docs"
docs_dir_resolved = docs_dir.resolve()

print(f"프로젝트 루트: {project_root}")
print(f"docs 디렉토리: {docs_dir}")
print(f"docs 절대 경로: {docs_dir_resolved}")
print(f"docs 존재: {docs_dir_resolved.exists()}")

if docs_dir_resolved.exists():
    test_file = docs_dir_resolved / "CONVERSATION_SAMPLES.md"
    print(f"\n테스트 파일: {test_file}")
    print(f"테스트 파일 존재: {test_file.exists()}")
    
    try:
        app.mount("/docs-files", StaticFiles(directory=str(docs_dir_resolved)), name="docs")
        print("\n✅ 정적 파일 서빙 마운트 성공!")
    except Exception as e:
        print(f"\n❌ 정적 파일 서빙 마운트 실패: {e}")
else:
    print("\n❌ docs 디렉토리가 없습니다")
