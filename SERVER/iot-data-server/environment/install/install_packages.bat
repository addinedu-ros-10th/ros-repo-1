@echo off
REM 가상환경 활성화 및 패키지 설치 스크립트

echo ========================================
echo IoT Care Backend 패키지 설치 시작
echo ========================================

echo 1단계: 가상환경 활성화 중...
call .venv\Scripts\activate.bat

echo 2단계: pip 업그레이드 중...
python -m pip install --upgrade pip

echo 3단계: 기본 패키지들 설치 중...
pip install fastapi uvicorn pydantic==1.10.13 python-dotenv==1.0.0

echo 4단계: 데이터베이스 핵심 패키지들 설치 중...
pip install sqlalchemy alembic

echo 5단계: psycopg2-binary 설치 중...
pip install psycopg2-binary==2.9.9

echo 6단계: Redis 패키지들 설치 중...
pip install redis aioredis

echo 7단계: 테스트 패키지들 설치 중...
pip install pytest httpx pytest-html

echo 8단계: 기타 유틸리티 설치 중...
pip install python-dotenv python-dateutil pytz

echo ========================================
echo 패키지 설치 완료!
echo ========================================

echo 설치된 패키지 확인:
pip list | findstr psycopg2
pip list | findstr sqlalchemy
pip list | findstr redis

echo.
echo 가상환경을 활성화하려면: .venv\Scripts\activate.bat
echo 연결 테스트를 실행하려면: python test_connection.py

pause

