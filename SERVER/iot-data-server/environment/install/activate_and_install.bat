@echo off
REM 가상환경 활성화 및 패키지 설치 스크립트

echo 가상환경 활성화 중...
call .venv\Scripts\activate.bat

echo pip 업그레이드 중...
python -m pip install --upgrade pip

echo 필요한 패키지 설치 중...
pip install -r requirements.txt

echo 설치 완료!
echo 가상환경을 활성화하려면: .venv\Scripts\activate.bat
echo 연결 테스트를 실행하려면: python test_connection.py

pause

