@echo off
REM start_project.bat
REM IoT Care Backend System 프로젝트 시작 스크립트 (Windows 환경)
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
set "PROJECT_ROOT=%SCRIPT_DIR%"

call :log_info "🚀 IoT Care Backend System 프로젝트 시작 (Windows)..."
call :log_info "📅 시작 시간: %date% %time%"
call :log_info "📍 프로젝트 루트: %PROJECT_ROOT%"
echo.

REM 필수 도구 확인
call :log_step "필수 도구 확인 중..."

REM Docker 확인
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker가 설치되지 않았습니다"
    call :log_info "Docker를 설치한 후 다시 시도하세요: https://docs.docker.com/get-docker/"
    pause
    exit /b 1
)

REM Docker 실행 상태 확인
docker info >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker가 실행되지 않았습니다"
    call :log_info "Docker Desktop을 시작한 후 다시 시도하세요"
    pause
    exit /b 1
)

REM Docker Compose 확인
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    call :log_error "Docker Compose가 설치되지 않았습니다"
    call :log_info "Docker Compose를 설치한 후 다시 시도하세요"
    pause
    exit /b 1
)

call :log_success "필수 도구 확인 완료"

REM 환경변수 자동 업데이트
call :log_step "환경변수 자동 업데이트 시작..."

if exist "scripts\auto_env_update.bat" (
    call scripts\auto_env_update.bat
) else (
    call :log_warning "auto_env_update.bat 스크립트를 찾을 수 없습니다"
)

call :log_success "환경변수 업데이트 완료"

REM Docker Compose 시작
call :log_step "Docker Compose 시작 중..."

REM 기존 컨테이너 정리
call :log_info "기존 컨테이너 정리 중..."
cd /d "%PROJECT_ROOT%"
docker-compose down --volumes --remove-orphans 2>nul

REM Docker 시스템 정리
call :log_info "Docker 시스템 정리 중..."
docker system prune -f

REM 프로젝트 시작
call :log_info "프로젝트 시작 중..."
docker-compose up -d

call :log_success "Docker Compose 시작 완료"

REM 서비스 상태 확인
call :log_step "서비스 상태 확인 중..."

REM 컨테이너 상태 확인
echo.
call :log_info "Docker 컨테이너 상태:"
docker-compose ps

REM API 서버 상태 확인
echo.
call :log_step "API 서버 상태 확인 중..."
call :log_info "서버 시작 대기 중... (10초)"

for /l %%i in (1,1,10) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if !errorlevel! equ 0 (
        call :log_success "API 서버 정상 동작"
        goto :api_ready
    ) else (
        if %%i equ 10 (
            call :log_warning "API 서버 응답 없음"
            call :log_info "docker logs iot-care-app 명령으로 로그를 확인하세요"
        ) else (
            echo -n "."
            timeout /t 1 /nobreak >nul
        )
    )
)

:api_ready

REM Redis 상태 확인
echo.
call :log_step "Redis 상태 확인 중..."
docker exec iot-care-redis redis-cli ping >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Redis 정상 동작"
) else (
    call :log_warning "Redis 응답 없음"
)

REM Caddy 상태 확인
echo.
call :log_step "Caddy 상태 확인 중..."
curl -s http://localhost:80 >nul 2>&1
if %errorlevel% equ 0 (
    call :log_success "Caddy 정상 동작"
) else (
    call :log_warning "Caddy 응답 없음"
)

REM 프로젝트 정보 표시
echo.
call :log_success "🎉 프로젝트 시작 완료!"
echo.
call :log_info "📋 프로젝트 정보:"
echo    • API 서버: http://localhost:8000
echo    • API 문서: http://localhost:8000/docs
echo    • Caddy 웹서버: http://localhost:80
echo    • Redis: localhost:16379
echo.
call :log_info "🔧 유용한 명령어:"
echo    • 컨테이너 상태 확인: docker-compose ps
echo    • 로그 확인: docker-compose logs -f
echo    • 서비스 중지: docker-compose down
echo    • 환경변수 업데이트: scripts\auto_env_update.bat
echo.
call :log_info "📅 시작 완료 시간: %date% %time%"

pause
endlocal

