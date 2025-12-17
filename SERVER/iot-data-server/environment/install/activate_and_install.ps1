# PowerShell 가상환경 활성화 및 패키지 설치 스크립트

Write-Host "가상환경 활성화 중..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

Write-Host "pip 업그레이드 중..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host "필요한 패키지 설치 중..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "설치 완료!" -ForegroundColor Green
Write-Host "가상환경을 활성화하려면: .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "연결 테스트를 실행하려면: python test_connection.py" -ForegroundColor Cyan

Read-Host "계속하려면 Enter를 누르세요"

