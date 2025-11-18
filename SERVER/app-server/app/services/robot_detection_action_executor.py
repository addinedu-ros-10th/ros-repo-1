"""
로봇 인식 이벤트 액션 실행기
Redis Streams 기반 비동기 큐 발행
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from uuid import UUID
import httpx

try:
    import redis.asyncio as redis
except ImportError:
    redis = None

from app.domain.entities.robot_detection_event import ProcessingInfo, APICall, Cmd

logger = logging.getLogger(__name__)


class RobotDetectionActionExecutor:
    """로봇 인식 이벤트 액션 실행기"""

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.redis_enabled = os.getenv("REDIS_URL") is not None and redis is not None
        self.stream_name = os.getenv("ROBOT_DETECTION_STREAM", "detections:actions")

    async def initialize(self):
        """Redis 클라이언트 초기화"""
        if not self.redis_enabled:
            logger.warning("[action_executor] Redis not available, actions will be logged only")
            return

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # 연결 테스트
            await self.redis_client.ping()
            logger.info(f"[action_executor] Redis connected: {redis_url}")
        except Exception as e:
            logger.error(f"[action_executor] Redis connection failed: {e}")
            self.redis_client = None
            self.redis_enabled = False

    async def close(self):
        """Redis 클라이언트 종료"""
        if self.redis_client:
            await self.redis_client.close()

    async def execute_actions(
        self,
        event_id: UUID,
        processing_info: ProcessingInfo,
        robot_id: str,
        category: str,
        unique_key: str,
    ) -> Dict[str, Any]:
        """
        액션 실행 (Redis Streams에 발행)
        실제 실행은 워커에서 처리
        """
        result = {
            "status": "queued",
            "event_id": str(event_id),
            "actions": [],
        }

        # Redis Streams에 발행
        if self.redis_enabled and self.redis_client:
            try:
                message = {
                    "event_id": str(event_id),
                    "robot_id": robot_id,
                    "category": category,
                    "unique_key": unique_key,
                    "intent": processing_info.intent,
                    "api_calls": (
                        [
                            {
                                "method": call.method,
                                "url": call.url,
                                "headers": call.headers,
                                "body": call.body,
                            }
                            for call in processing_info.api_calls
                        ]
                        if processing_info.api_calls
                        else []
                    ),
                    "cmds": (
                        [
                            {"topic": cmd.topic, "payload": cmd.payload}
                            for cmd in processing_info.cmds
                        ]
                        if processing_info.cmds
                        else []
                    ),
                    "scenario_state": processing_info.scenario_state,
                }

                # Redis Streams에 추가
                stream_id = await self.redis_client.xadd(
                    self.stream_name,
                    message,
                    maxlen=10000,  # 최대 10000개 메시지 유지
                )
                result["stream_id"] = stream_id
                result["status"] = "queued"
                logger.info(
                    f"[action_executor] Action queued: event_id={event_id}, stream_id={stream_id}"
                )
            except Exception as e:
                logger.error(f"[action_executor] Failed to queue action: {e}")
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            # Redis가 없으면 로그만 출력 (개발/테스트 환경)
            logger.info(
                f"[action_executor] Action would be queued (Redis not available): event_id={event_id}, intent={processing_info.intent}"
            )
            result["status"] = "logged"

        return result

    async def execute_actions_sync(
        self, processing_info: ProcessingInfo
    ) -> Dict[str, Any]:
        """
        동기 액션 실행 (테스트/데모용)
        실제 운영에서는 워커 사용 권장
        """
        result = {"status": "done", "actions": []}

        # API 호출 실행
        if processing_info.api_calls:
            async with httpx.AsyncClient(timeout=5.0) as client:
                for call in processing_info.api_calls:
                    try:
                        headers = call.headers or {}
                        data = call.body or {}
                        resp = await client.request(
                            call.method, call.url, headers=headers, json=data
                        )
                        action_result = {
                            "type": "api_call",
                            "url": call.url,
                            "method": call.method,
                            "status_code": resp.status_code,
                            "success": resp.status_code < 400,
                        }
                        result["actions"].append(action_result)

                        if resp.status_code >= 400:
                            logger.warning(
                                f"[action_executor] API call failed: {call.url} {resp.status_code}"
                            )
                    except Exception as e:
                        logger.error(f"[action_executor] API call error: {e}")
                        action_result = {
                            "type": "api_call",
                            "url": call.url,
                            "method": call.method,
                            "success": False,
                            "error": str(e),
                        }
                        result["actions"].append(action_result)

        # ROS2/메시지 큐 명령 발행 (여기서는 로그만)
        if processing_info.cmds:
            for cmd in processing_info.cmds:
                logger.info(
                    f"[action_executor] [PUBLISH] topic={cmd.topic} payload={cmd.payload}"
                )
                action_result = {
                    "type": "cmd",
                    "topic": cmd.topic,
                    "success": True,
                }
                result["actions"].append(action_result)

        return result


# 전역 인스턴스
action_executor = RobotDetectionActionExecutor()

