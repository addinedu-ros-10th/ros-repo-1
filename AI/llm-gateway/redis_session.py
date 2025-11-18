"""
Redis 기반 세션 관리 모듈

대화 히스토리를 Redis에 저장하여 분산 환경에서도 세션을 공유할 수 있습니다.
"""

import json
import asyncio
from typing import List, Dict, Optional
from datetime import timedelta
import redis.asyncio as aioredis
from config import settings


class RedisSessionManager:
    """Redis를 사용한 세션 관리자"""
    
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.session_ttl = timedelta(days=30)  # 세션 만료 시간 (30일)
    
    async def connect(self):
        """Redis 연결"""
        if self.redis_client is None:
            if settings.redis_url:
                # URL을 통한 연결
                self.redis_client = await aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
            else:
                # 개별 설정을 통한 연결
                self.redis_client = await aioredis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    password=settings.redis_password,
                    encoding="utf-8",
                    decode_responses=True
                )
    
    async def disconnect(self):
        """Redis 연결 종료"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
    
    def _get_session_key(self, session_id: str) -> str:
        """세션 키 생성"""
        return f"session:{session_id}"
    
    async def get_session(self, session_id: str) -> List[Dict[str, str]]:
        """세션 히스토리 조회"""
        await self.connect()
        key = self._get_session_key(session_id)
        
        data = await self.redis_client.get(key)
        if data:
            messages = json.loads(data)
            return messages
        return []
    
    async def save_session(self, session_id: str, messages: List[Dict[str, str]]):
        """세션 히스토리 저장"""
        await self.connect()
        key = self._get_session_key(session_id)
        
        data = json.dumps(messages, ensure_ascii=False)
        await self.redis_client.setex(
            key,
            int(self.session_ttl.total_seconds()),
            data
        )
    
    async def append_message(self, session_id: str, role: str, content: str):
        """세션에 메시지 추가"""
        messages = await self.get_session(session_id)
        messages.append({"role": role, "content": content})
        await self.save_session(session_id, messages)
    
    async def initialize_session(self, session_id: str, system_prompt: str):
        """세션 초기화"""
        messages = [{"role": "system", "content": system_prompt}]
        await self.save_session(session_id, messages)
        return messages
    
    async def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        await self.connect()
        key = self._get_session_key(session_id)
        result = await self.redis_client.delete(key)
        return result > 0
    
    async def session_exists(self, session_id: str) -> bool:
        """세션 존재 여부 확인"""
        await self.connect()
        key = self._get_session_key(session_id)
        return await self.redis_client.exists(key) > 0
    
    async def get_all_sessions(self) -> List[str]:
        """모든 세션 ID 조회 (관리용)"""
        await self.connect()
        keys = await self.redis_client.keys("session:*")
        return [key.replace("session:", "") for key in keys]
    
    async def health_check(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            await self.connect()
            await self.redis_client.ping()
            return True
        except Exception as e:
            print(f"Redis health check failed: {e}")
            return False


# 전역 세션 관리자 인스턴스
redis_session_manager = RedisSessionManager()


