"""
FastAPI 메인 애플리케이션

IoT Care 백엔드 서비스의 진입점입니다.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import api_router
from app.infrastructure.database import create_tables

# 모든 ORM 모델을 명시적으로 임포트하여 테이블 생성 시 포함되도록 함
from app.infrastructure.models import (
    User,
    Device,
    UserProfile,
    UserRelationship,
    ResidentInfo,  # residents 테이블 생성에 필요
    # 기타 모델들도 필요시 추가
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    print("🚀 IoT Care 백엔드 서비스 시작 중...")
    
    # 데이터베이스 테이블 생성
    try:
        create_tables()
        print("✅ 데이터베이스 테이블 생성 완료")
    except Exception as e:
        print(f"❌ 데이터베이스 테이블 생성 실패: {e}")
    
    yield
    
    # 종료 시 실행
    print("🛑 IoT Care 백엔드 서비스 종료 중...")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title="IoT Care Backend Service",
    description="독거노인 통합 돌봄 서비스를 위한 IoT 백엔드 시스템",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "defaultModelExpandDepth": 3,
        "docExpansion": "list",
        "syntaxHighlight.theme": "monokai"
    },
    lifespan=lifespan
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발/테스트 환경에서는 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 전역 예외 처리기
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 처리"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "path": str(request.url)
        }
    )


# 헬스체크 엔드포인트
@app.get("/health", tags=["health"])
async def health_check():
    """서비스 상태 확인"""
    return {
        "status": "healthy",
        "service": "IoT Care Backend",
        "version": "1.0.0",
        "timestamp": "2024-08-20T00:00:00Z"
    }


# 루트 엔드포인트
@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "IoT Care Backend Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# API 라우터 등록
app.include_router(api_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 