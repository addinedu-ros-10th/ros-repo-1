@echo off
REM auto_env_update.bat
REM IoT Care Backend System 환경변수 자동 업데이트 스크립트 (Windows 환경)
REM 작성일: 2025-08-23

setlocal enabledelayedexpansion

REM 색상 정의 (Windows 10 이상)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM 로그 함수
:log_info
echo %BLUE%ℹ️  %~1%NC%
goto :eof

:log_success
echo %GREEN%✅ %~1%NC%
goto :eof

:log_warning
echo %YELLOW%⚠️  %~1%NC%
goto :eof

:log_error
echo %RED%❌ %~1%NC%
goto :eof

:log_step
echo %BLUE%🔍 %~1%NC%
goto :eof

REM 현재 작업 디렉토리 확인
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%.."

call :log_info "IoT Care Backend System 환경변수 자동 업데이트 시작 (Windows)..."
call :log_info "📅 실행 시간: %date% %time%"
call :log_info "📍 프로젝트 루트: %PROJECT_ROOT%"
echo.

REM .env.local 파일 존재 확인
set "ENV_FILE=%PROJECT_ROOT%\.env.local"
if not exist "%ENV_FILE%" (
    call :log_error ".env.local 파일을 찾을 수 없습니다: %ENV_FILE%"
    exit /b 1
)

call :log_success ".env.local 파일 발견"

REM 현재 IP 주소 조회
call :log_step "현재 개발 머신 IP 주소 조사 중..."

REM PowerShell을 사용한 IP 주소 추출
for /f "tokens=*" %%i in ('powershell -Command "Get-NetIPAddress | Where-Object {$_.AddressFamily -eq 'IPv4' -and $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.*'} | Select-Object -First 1 -ExpandProperty IPAddress"') do (
    set "CURRENT_IP=%%i"
    goto :ip_found
)

REM PowerShell이 실패한 경우 ipconfig 사용
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr "IPv4"') do (
    set "CURRENT_IP=%%i"
    set "CURRENT_IP=!CURRENT_IP: =!"
    goto :ip_found
)

:ip_found
if "%CURRENT_IP%"=="" (
    call :log_error "IP 주소를 찾을 수 없습니다."
    call :log_info "수동으로 IP 주소를 확인하고 환경변수를 업데이트하세요."
    call :log_info "명령어: ipconfig 또는 PowerShell Get-NetIPAddress"
    exit /b 1
)

call :log_success "현재 IP 주소: %CURRENT_IP%"

REM 현재 .env.local 파일의 IP 설정 확인
echo.
call :log_step "현재 .env.local 파일의 IP 설정:"
findstr /R "^DB_HOST= ^CADDY_DOMAIN=" "%ENV_FILE%" 2>nul || call :log_warning "IP 관련 환경변수를 찾을 수 없습니다."

REM 백업 디렉토리 생성
set "BACKUP_DIR=%PROJECT_ROOT%\env_backups"
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"

REM 백업 파일 생성
set "BACKUP_FILE=%BACKUP_DIR%\.env.local.backup.%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%"
set "BACKUP_FILE=%BACKUP_FILE: =0%"
copy "%ENV_FILE%" "%BACKUP_FILE%" >nul
call :log_success "백업 파일 생성: %BACKUP_FILE%"

REM 환경변수 업데이트
echo.
call :log_step ".env.local 파일 업데이트 중..."

REM 임시 파일 생성
set "TEMP_FILE=%TEMP%\env_temp_%random%.txt"

REM DB_HOST 업데이트
findstr /R "^DB_HOST=" "%ENV_FILE%" >nul
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content '%ENV_FILE%') -replace '^DB_HOST=.*', 'DB_HOST=%CURRENT_IP%' | Set-Content '%ENV_FILE%'"
    call :log_success "DB_HOST 업데이트 완료: %CURRENT_IP%"
) else (
    call :log_warning "DB_HOST 환경변수가 .env.local 파일에 없습니다."
)

REM CADDY_DOMAIN 업데이트
findstr /R "^CADDY_DOMAIN=" "%ENV_FILE%" >nul
if %errorlevel% equ 0 (
    powershell -Command "(Get-Content '%ENV_FILE%') -replace '^CADDY_DOMAIN=.*', 'CADDY_DOMAIN=%CURRENT_IP%' | Set-Content '%ENV_FILE%'"
    call :log_success "CADDY_DOMAIN 업데이트 완료: %CURRENT_IP%"
) else (
    call :log_warning "CADDY_DOMAIN 환경변수가 .env.local 파일에 없습니다."
)

REM 업데이트된 내용 확인
echo.
call :log_step "업데이트된 환경변수:"
findstr /R "^DB_HOST= ^CADDY_DOMAIN=" "%ENV_FILE%" 2>nul || call :log_warning "업데이트된 환경변수를 찾을 수 없습니다."

echo.
call :log_info "🎯 다음 단계: Docker 환경 재시작"
call :log_info "💡 명령어: docker-compose down && docker-compose up -d"
call :log_info "💡 또는 이 스크립트를 --restart 옵션과 함께 실행하세요."

REM --restart 옵션이 있는 경우 Docker 재시작
if "%1"=="--restart" (
    echo.
    call :log_info "🚀 Docker 환경 자동 재시작 시작..."
    
    REM Docker 상태 확인
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        call :log_error "Docker가 실행되지 않았습니다"
        exit /b 1
    )
    
    REM Docker Compose 상태 확인
    docker-compose --version >nul 2>&1
    if %errorlevel% neq 0 (
        call :log_error "Docker Compose가 설치되지 않았습니다"
        exit /b 1
    )
    
    REM Docker 컨테이너 중지
    call :log_step "Docker 컨테이너 중지 중..."
    cd /d "%PROJECT_ROOT%"
    docker-compose down --volumes --remove-orphans
    
    REM Docker 시스템 정리
    call :log_step "Docker 시스템 정리 중..."
    docker system prune -f
    
    REM 프로젝트 재시작
    call :log_step "프로젝트 재시작 중..."
    docker-compose up -d
    
    REM 상태 확인
    echo.
    call :log_step "Docker 컨테이너 상태:"
    docker-compose ps
    
    REM API 서버 상태 확인
    echo.
    call :log_step "API 서버 상태 확인 중..."
    timeout /t 10 /nobreak >nul
    
    curl -s http://localhost:8000/health >nul 2>&1
    if %errorlevel% equ 0 (
        call :log_success "API 서버 정상 동작"
    ) else (
        call :log_warning "API 서버 응답 없음"
        call :log_info "docker logs iot-care-app 명령으로 로그를 확인하세요."
    )
    
    echo.
    call :log_success "🎉 환경변수 업데이트 및 Docker 재시작 완료!"
)

echo.
call :log_success "✅ 환경변수 자동 업데이트 완료!"
call :log_info "📅 완료 시간: %date% %time%"

endlocal

