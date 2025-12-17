# PowerShell 가상환경 활성화 및 패키지 설치 스크립트

Write-Host "========================================" -ForegroundColor Green
Write-Host "IoT Care Backend 패키지 설치 시작" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "1단계: 가상환경 활성화 중..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "2단계: pip 업그레이드 중..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "3단계: 기본 패키지들 설치 중..." -ForegroundColor Yellow
pip install fastapi uvicorn pydantic==1.10.13 python-dotenv==1.0.0

Write-Host "4단계: 데이터베이스 핵심 패키지들 설치 중..." -ForegroundColor Yellow
pip install sqlalchemy alembic

Write-Host "5단계: psycopg2-binary 설치 중..." -ForegroundColor Yellow
pip install psycopg2-binary==2.9.9

Write-Host "6단계: Redis 패키지들 설치 중..." -ForegroundColor Yellow
pip install redis aioredis

Write-Host "7단계: 테스트 패키지들 설치 중..." -ForegroundColor Yellow
pip install pytest httpx pytest-html

Write-Host "8단계: 기타 유틸리티 설치 중..." -ForegroundColor Yellow
pip install python-dotenv python-dateutil pytz

Write-Host "========================================" -ForegroundColor Green
Write-Host "패키지 설치 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "설치된 패키지 확인:" -ForegroundColor Cyan
pip list | Select-String "psycopg2"
pip list | Select-String "sqlalchemy"
pip list | Select-String "redis"

Write-Host ""
Write-Host "가상환경을 활성화하려면: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "연결 테스트를 실행하려면: python test_connection.py" -ForegroundColor Cyan

Read-Host "계속하려면 Enter를 누르세요"

