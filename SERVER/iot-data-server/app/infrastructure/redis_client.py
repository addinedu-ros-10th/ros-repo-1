"""
Redis 클라이언트 모듈

Redis 연결 및 세션 관리를 담당합니다.
캐시, 세션, 태스크 큐 등의 기능을 제공합니다.
"""

import redis
import json
import logging
from typing import Optional, Any, Union
from datetime import timedelta

from app.core.config import get_settings

# 로거 설정
logger = logging.getLogger(__name__)

# 설정 가져오기
settings = get_settings()


class RedisClient:
    """Redis 클라이언트 클래스"""
    
    def __init__(self):
        """Redis 클라이언트를 초기화합니다."""
        self.redis_client = None
        self._connect()
    
    def _connect(self):
        """Redis 서버에 연결합니다."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,  # 문자열 자동 디코딩
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # 연결 테스트
            self.redis_client.ping()
            logger.info(f"Redis 연결 성공: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
            
        except Exception as e:
            logger.error(f"Redis 연결 실패: {e}")
            self.redis_client = None
            raise
    
    def is_connected(self) -> bool:
        """Redis 연결 상태를 확인합니다."""
        try:
            if self.redis_client:
                self.redis_client.ping()
                return True
            return False
        except Exception:
            return False
    
    def get(self, key: str) -> Optional[str]:
        """키에 해당하는 값을 가져옵니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            value = self.redis_client.get(key)
            logger.debug(f"Redis GET: {key} = {value}")
            return value
            
        except Exception as e:
            logger.error(f"Redis GET 오류 ({key}): {e}")
            return None
    
    def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """키-값을 설정합니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            if expire:
                result = self.redis_client.setex(key, expire, value)
            else:
                result = self.redis_client.set(key, value)
            
            logger.debug(f"Redis SET: {key} = {value} (expire: {expire})")
            return result
            
        except Exception as e:
            logger.error(f"Redis SET 오류 ({key}): {e}")
            return False
    
    def set_json(self, key: str, value: dict, expire: Optional[int] = None) -> bool:
        """JSON 값을 설정합니다."""
        try:
            json_value = json.dumps(value, ensure_ascii=False)
            return self.set(key, json_value, expire)
        except Exception as e:
            logger.error(f"Redis SET JSON 오류 ({key}): {e}")
            return False
    
    def get_json(self, key: str) -> Optional[dict]:
        """JSON 값을 가져옵니다."""
        try:
            value = self.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET JSON 오류 ({key}): {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """키를 삭제합니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.delete(key)
            logger.debug(f"Redis DELETE: {key}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis DELETE 오류 ({key}): {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """키가 존재하는지 확인합니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis EXISTS 오류 ({key}): {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """키의 만료 시간을 설정합니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.expire(key, seconds)
            logger.debug(f"Redis EXPIRE: {key} = {seconds}초")
            return result
            
        except Exception as e:
            logger.error(f"Redis EXPIRE 오류 ({key}): {e}")
            return False
    
    def ttl(self, key: str) -> int:
        """키의 남은 만료 시간을 반환합니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.ttl(key)
            logger.debug(f"Redis TTL: {key} = {result}초")
            return result
            
        except Exception as e:
            logger.error(f"Redis TTL 오류 ({key}): {e}")
            return -1
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """키의 값을 증가시킵니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.incrby(key, amount)
            logger.debug(f"Redis INCR: {key} += {amount} = {result}")
            return result
            
        except Exception as e:
            logger.error(f"Redis INCR 오류 ({key}): {e}")
            return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """키의 값을 감소시킵니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.decrby(key, amount)
            logger.debug(f"Redis DECR: {key} -= {amount} = {result}")
            return result
            
        except Exception as e:
            logger.error(f"Redis DECR 오류 ({key}): {e}")
            return None
    
    def list_push(self, key: str, value: str) -> bool:
        """리스트에 값을 추가합니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.lpush(key, value)
            logger.debug(f"Redis LPUSH: {key} = {value}")
            return result > 0
            
        except Exception as e:
            logger.error(f"Redis LPUSH 오류 ({key}): {e}")
            return False
    
    def list_pop(self, key: str) -> Optional[str]:
        """리스트에서 값을 꺼냅니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            value = self.redis_client.rpop(key)
            logger.debug(f"Redis RPOP: {key} = {value}")
            return value
            
        except Exception as e:
            logger.error(f"Redis RPOP 오류 ({key}): {e}")
            return None
    
    def list_range(self, key: str, start: int = 0, end: int = -1) -> list:
        """리스트의 범위를 가져옵니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.lrange(key, start, end)
            logger.debug(f"Redis LRANGE: {key} [{start}:{end}] = {len(result)}개")
            return result
            
        except Exception as e:
            logger.error(f"Redis LRANGE 오류 ({key}): {e}")
            return []
    
    def hash_set(self, key: str, field: str, value: str) -> bool:
        """해시에 필드-값을 설정합니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.hset(key, field, value)
            logger.debug(f"Redis HSET: {key}.{field} = {value}")
            return result >= 0
            
        except Exception as e:
            logger.error(f"Redis HSET 오류 ({key}.{field}): {e}")
            return False
    
    def hash_get(self, key: str, field: str) -> Optional[str]:
        """해시에서 필드 값을 가져옵니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            value = self.redis_client.hget(key, field)
            logger.debug(f"Redis HGET: {key}.{field} = {value}")
            return value
            
        except Exception as e:
            logger.error(f"Redis HGET 오류 ({key}.{field}): {e}")
            return None
    
    def hash_get_all(self, key: str) -> dict:
        """해시의 모든 필드-값을 가져옵니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.hgetall(key)
            logger.debug(f"Redis HGETALL: {key} = {len(result)}개 필드")
            return result
            
        except Exception as e:
            logger.error(f"Redis HGETALL 오류 ({key}): {e}")
            return {}
    
    def flush_db(self) -> bool:
        """현재 데이터베이스를 비웁니다. (주의: 개발 환경에서만 사용)"""
        if settings.ENVIRONMENT == "production":
            logger.warning("프로덕션 환경에서는 데이터베이스 비우기가 금지됩니다.")
            return False
        
        try:
            if not self.is_connected():
                self._connect()
            
            result = self.redis_client.flushdb()
            logger.warning(f"Redis FLUSHDB 실행: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Redis FLUSHDB 오류: {e}")
            return False
    
    def get_info(self) -> dict:
        """Redis 서버 정보를 가져옵니다."""
        try:
            if not self.is_connected():
                self._connect()
            
            info = self.redis_client.info()
            logger.debug("Redis INFO 조회 성공")
            return info
            
        except Exception as e:
            logger.error(f"Redis INFO 오류: {e}")
            return {}
    
    def close(self):
        """Redis 연결을 종료합니다."""
        try:
            if self.redis_client:
                self.redis_client.close()
                logger.info("Redis 연결 종료")
        except Exception as e:
            logger.error(f"Redis 연결 종료 오류: {e}")


# 전역 Redis 클라이언트 인스턴스
redis_client = RedisClient()


def get_redis_client() -> RedisClient:
    """Redis 클라이언트를 반환합니다."""
    return redis_client


def test_redis_connection() -> bool:
    """Redis 연결을 테스트합니다."""
    try:
        return redis_client.is_connected()
    except Exception as e:
        logger.error(f"Redis 연결 테스트 실패: {e}")
        return False


def init_redis():
    """Redis를 초기화합니다."""
    try:
        if test_redis_connection():
            info = redis_client.get_info()
            logger.info(f"Redis 초기화 완료: {info.get('redis_version', 'unknown')}")
        else:
            raise Exception("Redis 연결 실패")
    except Exception as e:
        logger.error(f"Redis 초기화 실패: {e}")
        raise

