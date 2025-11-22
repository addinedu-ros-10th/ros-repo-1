"""
User API 전용 라우터

사용자 관련 모든 API를 그룹화하여 관리합니다.
"""

from fastapi import APIRouter
from app.api.v1 import users

# User 전용 라우터 생성
user_router = APIRouter(tags=["users"])

# User API 엔드포인트들을 User 전용 라우터에 포함
user_router.include_router(users.router) 