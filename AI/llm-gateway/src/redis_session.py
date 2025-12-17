"""
Redis 기반 세션 관리 모듈

대화 히스토리를 Redis에 저장하여 분산 환경에서도 세션을 공유할 수 있습니다.
"""

import json
import asyncio
from typing import List, Dict, Optional
from datetime import timedelta
import redis.asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError, RedisError
import logging
from .config import settings

# 로깅 설정
logger = logging.getLogger(__name__)


class RedisSessionManager:
    """Redis를 사용한 세션 관리자"""
    
    def __init__(self):
        self.redis_client: Optional[aioredis.Redis] = None
        self.session_ttl = timedelta(days=30)  # 세션 만료 시간 (30일)
        self._connection_retries = 3  # 재연결 시도 횟수
        self._connection_timeout = 5.0  # 연결 타임아웃 (초)
    
    async def connect(self):
        """Redis 연결 (연결 풀 사용)"""
        if self.redis_client is not None:
            # 이미 연결되어 있고 연결이 살아있는지 확인
            try:
                await self.redis_client.ping()
                return
            except (ConnectionError, TimeoutError):
                # 연결이 끊어진 경우 재연결
                logger.warning("Redis connection lost, reconnecting...")
                await self.disconnect()
        
        try:
            if settings.redis_url:
                # URL을 통한 연결 (연결 풀 자동 생성)
                self.redis_client = await aioredis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=self._connection_timeout,
                    socket_timeout=self._connection_timeout,
                    retry_on_timeout=True,
                    health_check_interval=30  # 30초마다 연결 상태 확인
                )
                logger.debug(f"Redis connected via URL: {settings.redis_url.split('@')[1] if '@' in settings.redis_url else 'hidden'}")
            else:
                # 개별 설정을 통한 연결 (연결 풀 사용)
                self.redis_client = aioredis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    password=settings.redis_password,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=self._connection_timeout,
                    socket_timeout=self._connection_timeout,
                    retry_on_timeout=True,
                    health_check_interval=30  # 30초마다 연결 상태 확인
                )
                logger.debug(f"Redis connected: {settings.redis_host}:{settings.redis_port}")
            
            # 연결 테스트
            await self.redis_client.ping()
            logger.info("Redis connection established successfully")
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection failed: {e}")
            self.redis_client = None
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Redis connection: {e}", exc_info=True)
            self.redis_client = None
            raise
    
    async def disconnect(self):
        """Redis 연결 종료"""
        if self.redis_client:
            try:
                await self.redis_client.close()
                await self.redis_client.connection_pool.disconnect()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.warning(f"Error closing Redis connection: {e}")
            finally:
                self.redis_client = None
    
    def _get_session_key(self, session_id: str) -> str:
        """세션 키 생성"""
        return f"session:{session_id}"
    
    async def get_session(self, session_id: str) -> List[Dict[str, str]]:
        """세션 히스토리 조회"""
        try:
            await self.connect()
            key = self._get_session_key(session_id)
            
            data = await self.redis_client.get(key)
            if data:
                messages = json.loads(data)
                logger.debug(f"Loaded session: {session_id} ({len(messages)} messages)")
                return messages
            logger.debug(f"Session not found: {session_id}")
            return []
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection error while getting session: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode session data for {session_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting session {session_id}: {e}", exc_info=True)
            raise
    
    async def save_session(self, session_id: str, messages: List[Dict[str, str]]):
        """세션 히스토리 저장"""
        try:
            await self.connect()
            key = self._get_session_key(session_id)
            
            data = json.dumps(messages, ensure_ascii=False)
            await self.redis_client.setex(
                key,
                int(self.session_ttl.total_seconds()),
                data
            )
            logger.debug(f"Saved session: {session_id} ({len(messages)} messages, TTL: {self.session_ttl.days} days)")
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection error while saving session: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving session {session_id}: {e}", exc_info=True)
            raise
    
    async def append_message(self, session_id: str, role: str, content: str):
        """세션에 메시지 추가"""
        try:
            messages = await self.get_session(session_id)
            messages.append({"role": role, "content": content})
            await self.save_session(session_id, messages)
            logger.debug(f"Appended message to session: {session_id} (role: {role})")
        except Exception as e:
            logger.error(f"Failed to append message to session {session_id}: {e}", exc_info=True)
            raise
    
    async def initialize_session(self, session_id: str, system_prompt: str):
        """세션 초기화"""
        try:
            messages = [{"role": "system", "content": system_prompt}]
            await self.save_session(session_id, messages)
            logger.info(f"Initialized new session: {session_id}")
            return messages
        except Exception as e:
            logger.error(f"Failed to initialize session {session_id}: {e}", exc_info=True)
            raise
    
    async def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        try:
            await self.connect()
            key = self._get_session_key(session_id)
            result = await self.redis_client.delete(key)
            deleted = result > 0
            if deleted:
                logger.info(f"Deleted session: {session_id}")
            else:
                logger.debug(f"Session not found for deletion: {session_id}")
            return deleted
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection error while deleting session: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting session {session_id}: {e}", exc_info=True)
            return False
    
    async def session_exists(self, session_id: str) -> bool:
        """세션 존재 여부 확인"""
        try:
            await self.connect()
            key = self._get_session_key(session_id)
            exists = await self.redis_client.exists(key) > 0
            logger.debug(f"Session exists check: {session_id} = {exists}")
            return exists
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection error while checking session: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error checking session {session_id}: {e}", exc_info=True)
            return False
    
    async def get_all_sessions(self) -> List[str]:
        """모든 세션 ID 조회 (관리용)"""
        try:
            await self.connect()
            keys = await self.redis_client.keys("session:*")
            session_ids = [key.replace("session:", "") for key in keys]
            logger.debug(f"Found {len(session_ids)} sessions")
            return session_ids
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Redis connection error while getting all sessions: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting all sessions: {e}", exc_info=True)
            return []
    
    async def health_check(self) -> bool:
        """Redis 연결 상태 확인"""
        try:
            if self.redis_client is None:
                await self.connect()
            else:
                # 연결이 이미 있는 경우 ping으로 확인
                await self.redis_client.ping()
            logger.debug("Redis health check passed")
            return True
        except (ConnectionError, TimeoutError) as e:
            logger.warning(f"Redis health check failed (connection error): {e}")
            return False
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False


# 전역 세션 관리자 인스턴스
redis_session_manager = RedisSessionManager()


