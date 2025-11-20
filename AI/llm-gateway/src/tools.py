"""
LLM이 호출할 수 있는 함수 정의
외부 API 호출 및 내부 기능을 제공합니다.
"""
from typing import Dict, Any, Optional, List
import json
import httpx
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

# API 베이스 URL
API_BASE_URL = "http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com"
IOT_BASE_URL = "http://192.168.0.59:8000"

# 함수 정의 리스트
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_users_list",
            "description": "사용자 목록을 조회합니다. 사용자가 '사용자 목록', '사용자 리스트', '사용자 목록 보여줘', '사용자 조회', '사용자들', 'care_target 사용자', 'caregiver 사용자' 등을 요청할 때 반드시 이 함수를 호출하세요. 페이지네이션과 역할 필터링을 지원합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "page": {
                        "type": "integer",
                        "description": "페이지 번호 (기본값: 1)",
                        "default": 1
                    },
                    "size": {
                        "type": "integer",
                        "description": "페이지당 항목 수 (기본값: 100)",
                        "default": 100
                    },
                    "role": {
                        "type": "string",
                        "description": "사용자 역할 필터 (예: 'care_target', 'caregiver' 등). 선택사항입니다.",
                        "enum": ["care_target", "caregiver"]
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "특정 사용자의 프로필 정보를 조회합니다. 사용자가 '사용자 프로필', '사용자 정보', '사용자 상세', '프로필 조회' 등을 요청할 때 반드시 이 함수를 호출하세요. user_id 파라미터가 필요합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "조회할 사용자의 UUID (예: '10fa45f2-f375-41c9-a62a-093efcd01bd3')"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_relationships",
            "description": "사용자의 관계 정보를 조회합니다. 사용자가 '사용자 관계', '관계 정보', '관계 조회' 등을 요청할 때 반드시 이 함수를 호출하세요. user_id와 relationship_type 파라미터가 필요합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "조회할 사용자의 UUID (예: '10fa45f2-f375-41c9-a62a-093efcd01bd3')"
                    },
                    "relationship_type": {
                        "type": "string",
                        "description": "관계 타입 (기본값: 'as-target')",
                        "enum": ["as-target", "as-caregiver"],
                        "default": "as-target"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_door",
            "description": "문을 열거나 닫습니다. 사용자가 '문 열어줘', '문 열기', '문 열림', '문 닫아줘', '문 닫기', '문 닫힘', '문을 열어주세요', '문을 닫아주세요' 등을 요청할 때 반드시 이 함수를 호출하세요. 두 개의 서보 모터를 동시에 제어하여 문을 열거나 닫습니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["open", "close"],
                        "description": "문 동작: 'open' (열기) 또는 'close' (닫기)"
                    }
                },
                "required": ["action"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "start_customized_mobile_conversation",
            "description": "맞춤형 이동식 대화를 시작합니다. 사용자가 '대화를 하고 싶어', '맞춤 대화를 시작해줘', '대화 좀 나눌 수 있을까', '함께 이야기 하자', '산책 하면서 같이 이야기 할래' 등을 요청할 때 반드시 이 함수를 호출하세요. YOLO 객체 인식 프로그램을 시작하여 맞춤형 이동식 대화 기능을 활성화합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "대화 세션 ID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "사용자 ID (어르신 ID)"
                    }
                },
                "required": ["session_id", "user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "activate_tracking",
            "description": "추종 기능을 활성화합니다. 사용자가 '함께 걸으며 대화 할까요?'에 대해 긍정적으로 응답('그래', '응', '좋아' 등)했을 때 반드시 이 함수를 호출하세요. 추종 스위치를 토글하여 추종 기능을 활성화합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "대화 세션 ID"
                    }
                },
                "required": ["session_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "end_customized_mobile_conversation",
            "description": "맞춤형 이동식 대화를 종료합니다. 사용자가 '그래 즐거웠어. 이제 대화를 종료하자', '대화 종료', '이제 그만하자' 등 대화 종료 의사를 밝힐 때 반드시 이 함수를 호출하세요. 추종 기능을 비활성화하고 YOLO 객체 인식 프로그램을 종료합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "대화 세션 ID"
                    }
                },
                "required": ["session_id"]
            }
        }
    }
]


async def execute_function(function_name: str, arguments: Dict[str, Any], db_manager=None) -> Dict[str, Any]:
    """
    함수를 실행하고 결과를 반환합니다.
    
    Args:
        function_name: 실행할 함수 이름
        arguments: 함수 인자
        db_manager: 데이터베이스 관리자 (내부 함수용, 선택사항)
    
    Returns:
        함수 실행 결과
    """
    try:
        if function_name == "get_users_list":
            return await _get_users_list(
                page=arguments.get("page", 1),
                size=arguments.get("size", 100),
                role=arguments.get("role")
            )
        
        elif function_name == "get_user_profile":
            user_id = arguments.get("user_id")
            if not user_id:
                return {"error": "user_id is required"}
            return await _get_user_profile(user_id)
        
        elif function_name == "get_user_relationships":
            user_id = arguments.get("user_id")
            if not user_id:
                return {"error": "user_id is required"}
            relationship_type = arguments.get("relationship_type", "as-target")
            return await _get_user_relationships(user_id, relationship_type)
        
        elif function_name == "control_door":
            action = arguments.get("action")
            if not action:
                return {"error": "action is required (open or close)"}
            return await _control_door(action)
        
        elif function_name == "start_customized_mobile_conversation":
            session_id = arguments.get("session_id")
            user_id = arguments.get("user_id")
            if not session_id or not user_id:
                return {"error": "session_id and user_id are required"}
            return await _start_customized_mobile_conversation(session_id, user_id, db_manager)
        
        elif function_name == "activate_tracking":
            session_id = arguments.get("session_id")
            if not session_id:
                return {"error": "session_id is required"}
            return await _activate_tracking(session_id, db_manager)
        
        elif function_name == "end_customized_mobile_conversation":
            session_id = arguments.get("session_id")
            if not session_id:
                return {"error": "session_id is required"}
            return await _end_customized_mobile_conversation(session_id, db_manager)
        
        else:
            return {
                "error": f"Unknown function: {function_name}",
                "available_functions": [tool["function"]["name"] for tool in TOOLS]
            }
    
    except Exception as e:
        logger.error(f"Function execution error: {e}", exc_info=True)
        return {
            "error": str(e),
            "function": function_name
        }


async def _get_users_list(page: int = 1, size: int = 100, role: Optional[str] = None) -> Dict[str, Any]:
    """
    사용자 목록 조회 API 호출
    
    Args:
        page: 페이지 번호
        size: 페이지당 항목 수
        role: 사용자 역할 필터
    
    Returns:
        API 응답 결과
    """
    try:
        url = f"{API_BASE_URL}/api/users/list"
        params = {
            "page": page,
            "size": size
        }
        
        if role:
            params["role"] = role
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                params=params,
                headers={"accept": "application/json"}
            )
            
            response.raise_for_status()
            
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
                "url": str(response.url)
            }
    
    except httpx.TimeoutException:
        return {
            "error": "Request timeout",
            "url": url,
            "timeout": "10 seconds"
        }
    
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error: {e.response.status_code}",
            "status_code": e.response.status_code,
            "response": e.response.text[:500] if e.response.text else None
        }
    
    except httpx.ConnectError:
        return {
            "error": "Connection error",
            "url": url,
            "message": "Could not connect to the server"
        }
    
    except Exception as e:
        logger.error(f"Error calling get_users_list: {e}", exc_info=True)
        return {
            "error": str(e),
            "type": type(e).__name__
        }


async def _get_user_profile(user_id: str) -> Dict[str, Any]:
    """
    사용자 프로필 조회 API 호출
    
    Args:
        user_id: 사용자 UUID
    
    Returns:
        API 응답 결과
    """
    try:
        url = f"{API_BASE_URL}/api/user-profiles/{user_id}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers={"accept": "application/json"}
            )
            
            response.raise_for_status()
            
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
                "url": str(response.url)
            }
    
    except httpx.TimeoutException:
        return {
            "error": "Request timeout",
            "url": url,
            "timeout": "10 seconds"
        }
    
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error: {e.response.status_code}",
            "status_code": e.response.status_code,
            "response": e.response.text[:500] if e.response.text else None
        }
    
    except httpx.ConnectError:
        return {
            "error": "Connection error",
            "url": url,
            "message": "Could not connect to the server"
        }
    
    except Exception as e:
        logger.error(f"Error calling get_user_profile: {e}", exc_info=True)
        return {
            "error": str(e),
            "type": type(e).__name__
        }


async def _get_user_relationships(user_id: str, relationship_type: str = "as-target") -> Dict[str, Any]:
    """
    사용자 관계 정보 조회 API 호출
    
    Args:
        user_id: 사용자 UUID
        relationship_type: 관계 타입 ('as-target' 또는 'as-caregiver')
    
    Returns:
        API 응답 결과
    """
    try:
        url = f"{API_BASE_URL}/api/user-relationships/user/{user_id}/{relationship_type}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                headers={"accept": "application/json"}
            )
            
            response.raise_for_status()
            
            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
                "url": str(response.url)
            }
    
    except httpx.TimeoutException:
        return {
            "error": "Request timeout",
            "url": url,
            "timeout": "10 seconds"
        }
    
    except httpx.HTTPStatusError as e:
        return {
            "error": f"HTTP error: {e.response.status_code}",
            "status_code": e.response.status_code,
            "response": e.response.text[:500] if e.response.text else None
        }
    
    except httpx.ConnectError:
        return {
            "error": "Connection error",
            "url": url,
            "message": "Could not connect to the server"
        }
    
    except Exception as e:
        logger.error(f"Error calling get_user_relationships: {e}", exc_info=True)
        return {
            "error": str(e),
            "type": type(e).__name__
        }


async def _control_door(action: str) -> Dict[str, Any]:
    """
    IOT 문 제어 API 호출 (두 서보 모터 동시 제어)
    
    Args:
        action: "open" (열기) 또는 "close" (닫기)
    
    Returns:
        API 응답 결과
    """
    IOT_BASE_URL = "http://192.168.0.30:8010"
    
    # action에 따라 각도 결정
    if action == "open":
        servo1_angle = 0
        servo2_angle = 170
    elif action == "close":
        servo1_angle = 180
        servo2_angle = 0
    else:
        return {
            "error": f"Invalid action: {action}. Must be 'open' or 'close'",
            "action": action
        }
    
    logger.info(f"Controlling door: action={action}, servo1={servo1_angle}°, servo2={servo2_angle}°")
    
    try:
        # 두 API 동시 호출 (비동기 병렬 처리)
        async with httpx.AsyncClient(timeout=5.0) as client:
            tasks = [
                client.post(
                    f"{IOT_BASE_URL}/control/esp_32/servo1",
                    json={"angle": servo1_angle},
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json"
                    }
                ),
                client.post(
                    f"{IOT_BASE_URL}/control/esp_32/servo2",
                    json={"angle": servo2_angle},
                    headers={
                        "accept": "application/json",
                        "Content-Type": "application/json"
                    }
                )
            ]
            
            # 두 요청을 동시에 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 처리
            servo1_result = _process_servo_response(results[0], "servo1", servo1_angle)
            servo2_result = _process_servo_response(results[1], "servo2", servo2_angle)
            
            # 전체 성공 여부 확인
            overall_success = servo1_result["success"] and servo2_result["success"]
            
            result = {
                "success": overall_success,
                "action": action,
                "servo1": servo1_result,
                "servo2": servo2_result
            }
            
            if overall_success:
                logger.info(f"Door control successful: action={action}")
            else:
                logger.warning(f"Door control partial failure: action={action}, servo1={servo1_result['success']}, servo2={servo2_result['success']}")
            
            return result
    
    except Exception as e:
        logger.error(f"Error controlling door: {e}", exc_info=True)
        return {
            "error": str(e),
            "action": action,
            "type": type(e).__name__
        }


def _process_servo_response(response_or_exception: Any, servo_name: str, angle: int) -> Dict[str, Any]:
    """
    서보 모터 API 응답 처리
    
    Args:
        response_or_exception: httpx.Response 또는 Exception
        servo_name: 서보 이름 ("servo1" 또는 "servo2")
        angle: 설정한 각도
    
    Returns:
        처리된 결과 딕셔너리
    """
    if isinstance(response_or_exception, Exception):
        # 예외 처리
        if isinstance(response_or_exception, httpx.TimeoutException):
            return {
                "success": False,
                "error": "Request timeout",
                "servo": servo_name,
                "angle": angle,
                "timeout": "5 seconds"
            }
        elif isinstance(response_or_exception, httpx.HTTPStatusError):
            return {
                "success": False,
                "error": f"HTTP error: {response_or_exception.response.status_code}",
                "servo": servo_name,
                "angle": angle,
                "status_code": response_or_exception.response.status_code,
                "response": response_or_exception.response.text[:500] if response_or_exception.response.text else None
            }
        elif isinstance(response_or_exception, httpx.ConnectError):
            return {
                "success": False,
                "error": "Connection error",
                "servo": servo_name,
                "angle": angle,
                "message": "Could not connect to the server"
            }
        else:
            return {
                "success": False,
                "error": str(response_or_exception),
                "servo": servo_name,
                "angle": angle,
                "type": type(response_or_exception).__name__
            }
    
    # 정상 응답 처리
    try:
        response_or_exception.raise_for_status()
        response_data = response_or_exception.json() if response_or_exception.content else {}
        
        return {
            "success": True,
            "servo": servo_name,
            "angle": angle,
            "status_code": response_or_exception.status_code,
            "response": response_data
        }
    except httpx.HTTPStatusError as e:
        return {
            "success": False,
            "error": f"HTTP error: {e.response.status_code}",
            "servo": servo_name,
            "angle": angle,
            "status_code": e.response.status_code,
            "response": e.response.text[:500] if e.response.text else None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "servo": servo_name,
            "angle": angle,
            "type": type(e).__name__
        }


async def _start_customized_mobile_conversation(session_id: str, user_id: str, db_manager) -> Dict[str, Any]:
    """
    맞춤형 이동식 대화 시작 (YOLO 객체 인식 프로그램 시작)
    
    Args:
        session_id: 대화 세션 ID
        user_id: 사용자 ID
        db_manager: 데이터베이스 관리자
    
    Returns:
        API 응답 결과
    """
    try:
        logger.info(f"Starting customized mobile conversation: session_id={session_id}, user_id={user_id}")
        
        # 1. DB에 세션 생성
        if db_manager and db_manager._initialized:
            try:
                from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                with db_manager.get_session() as session:
                    # 세션 생성
                    cmc_session = CustomizedMobileConversationSession(
                        session_id=session_id,
                        user_id=user_id,
                        started_at=datetime.utcnow(),
                        status='yolo_starting'
                    )
                    session.add(cmc_session)
                    
                    # YOLO 상태 저장
                    yolo_status = DeepLearningFunctionStatus(
                        function_type='yolo',
                        session_id=session_id,
                        status='starting',
                        metadata={'user_id': user_id}
                    )
                    session.add(yolo_status)
                    session.commit()
                    logger.info(f"Created CMC session and YOLO status in DB: session_id={session_id}")
            except Exception as db_error:
                logger.warning(f"Failed to save session to DB: {db_error}, continuing with API call")
        
        # 2. YOLO 시작 API 호출 (비동기)
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{IOT_BASE_URL}/send-signal_run_yolo",
                    headers={"accept": "application/json"},
                    content=""
                )
                response.raise_for_status()
                response_data = response.json()
                
                # 3. DB 상태 업데이트
                if db_manager and db_manager._initialized:
                    try:
                        from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                        with db_manager.get_session() as session:
                            # 세션 상태 업데이트
                            cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
                            if cmc_session:
                                cmc_session.yolo_started_at = datetime.utcnow()
                                cmc_session.status = 'yolo_running'
                            
                            # YOLO 상태 업데이트
                            yolo_status = session.query(DeepLearningFunctionStatus).filter_by(function_type='yolo', session_id=session_id).first()
                            if yolo_status:
                                yolo_status.status = 'active'
                                yolo_status.last_updated = datetime.utcnow()
                            
                            session.commit()
                    except Exception as db_error:
                        logger.warning(f"Failed to update session status in DB: {db_error}")
                
                logger.info(f"YOLO started successfully: session_id={session_id}")
                return {
                    "success": True,
                    "status": "yolo_started",
                    "message": "YOLO 객체 인식 프로그램이 시작되었습니다. 맞춤형 이동식 대화를 시작할 수 있습니다.",
                    "response": response_data,
                    "next_action": "ask_walking_together"
                }
            
            except httpx.TimeoutException:
                logger.error(f"YOLO start timeout: session_id={session_id}")
                return {
                    "success": False,
                    "error": "YOLO 시작 요청 타임아웃 (30초 초과)",
                    "session_id": session_id
                }
            
            except httpx.HTTPStatusError as e:
                logger.error(f"YOLO start HTTP error: {e.response.status_code}, session_id={session_id}")
                return {
                    "success": False,
                    "error": f"HTTP error: {e.response.status_code}",
                    "status_code": e.response.status_code,
                    "response": e.response.text[:500] if e.response.text else None,
                    "session_id": session_id
                }
            
            except httpx.ConnectError:
                logger.error(f"YOLO start connection error: session_id={session_id}")
                return {
                    "success": False,
                    "error": "IOT 서버 연결 오류",
                    "session_id": session_id
                }
    
    except Exception as e:
        logger.error(f"Error starting customized mobile conversation: {e}", exc_info=True)
        return {
            "error": str(e),
            "session_id": session_id,
            "type": type(e).__name__
        }


async def _activate_tracking(session_id: str, db_manager) -> Dict[str, Any]:
    """
    추종 기능 활성화 (토글 스위치)
    
    Args:
        session_id: 대화 세션 ID
        db_manager: 데이터베이스 관리자
    
    Returns:
        API 응답 결과
    """
    try:
        logger.info(f"Activating tracking: session_id={session_id}")
        
        # 1. DB에서 현재 추종 상태 확인
        current_tracking_status = None
        if db_manager and db_manager._initialized:
            try:
                from .database import DeepLearningFunctionStatus
                with db_manager.get_session() as session:
                    tracking_status = session.query(DeepLearningFunctionStatus).filter_by(
                        function_type='tracking',
                        session_id=session_id
                    ).first()
                    if tracking_status:
                        current_tracking_status = tracking_status.status
            except Exception as db_error:
                logger.warning(f"Failed to check tracking status in DB: {db_error}")
        
        # 2. 추종 스위치 API 호출
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{IOT_BASE_URL}/send-signal_tracking_switch",
                    headers={"accept": "application/json"},
                    content=""
                )
                response.raise_for_status()
                response_data = response.json()
                
                # 3. response에서 상태 확인
                tracking_switch = response_data.get("tracking_switch", "")
                is_activated = "activated" in tracking_switch.lower()
                
                # 4. DB 상태 업데이트
                if db_manager and db_manager._initialized:
                    try:
                        from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                        with db_manager.get_session() as session:
                            # 세션 상태 업데이트
                            cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
                            if cmc_session:
                                if is_activated:
                                    cmc_session.tracking_activated_at = datetime.utcnow()
                                    cmc_session.status = 'tracking_active'
                                else:
                                    cmc_session.tracking_deactivated_at = datetime.utcnow()
                            
                            # 추종 상태 저장/업데이트
                            tracking_status = session.query(DeepLearningFunctionStatus).filter_by(
                                function_type='tracking',
                                session_id=session_id
                            ).first()
                            
                            if tracking_status:
                                tracking_status.status = 'active' if is_activated else 'inactive'
                                tracking_status.last_updated = datetime.utcnow()
                                tracking_status.metadata = {'tracking_switch': tracking_switch}
                            else:
                                tracking_status = DeepLearningFunctionStatus(
                                    function_type='tracking',
                                    session_id=session_id,
                                    status='active' if is_activated else 'inactive',
                                    metadata={'tracking_switch': tracking_switch}
                                )
                                session.add(tracking_status)
                            
                            session.commit()
                    except Exception as db_error:
                        logger.warning(f"Failed to update tracking status in DB: {db_error}")
                
                logger.info(f"Tracking {'activated' if is_activated else 'deactivated'}: session_id={session_id}")
                return {
                    "success": True,
                    "status": "tracking_activated" if is_activated else "tracking_deactivated",
                    "message": f"추종 기능이 {'활성화' if is_activated else '비활성화'}되었습니다.",
                    "tracking_switch": tracking_switch,
                    "response": response_data
                }
            
            except httpx.TimeoutException:
                return {
                    "success": False,
                    "error": "추종 활성화 요청 타임아웃",
                    "session_id": session_id
                }
            
            except httpx.HTTPStatusError as e:
                return {
                    "success": False,
                    "error": f"HTTP error: {e.response.status_code}",
                    "status_code": e.response.status_code,
                    "response": e.response.text[:500] if e.response.text else None,
                    "session_id": session_id
                }
            
            except httpx.ConnectError:
                return {
                    "success": False,
                    "error": "IOT 서버 연결 오류",
                    "session_id": session_id
                }
    
    except Exception as e:
        logger.error(f"Error activating tracking: {e}", exc_info=True)
        return {
            "error": str(e),
            "session_id": session_id,
            "type": type(e).__name__
        }


async def _end_customized_mobile_conversation(session_id: str, db_manager) -> Dict[str, Any]:
    """
    맞춤형 이동식 대화 종료 (추종 비활성화 + YOLO 종료)
    
    Args:
        session_id: 대화 세션 ID
        db_manager: 데이터베이스 관리자
    
    Returns:
        API 응답 결과
    """
    try:
        logger.info(f"Ending customized mobile conversation: session_id={session_id}")
        
        results = {
            "success": True,
            "session_id": session_id,
            "tracking_deactivated": False,
            "yolo_stopped": False,
            "errors": []
        }
        
        # 1. 추종 비활성화
        tracking_result = await _activate_tracking(session_id, db_manager)
        if tracking_result.get("success") and "deactivated" in tracking_result.get("status", ""):
            results["tracking_deactivated"] = True
        else:
            results["errors"].append(f"추종 비활성화 실패: {tracking_result.get('error', 'Unknown error')}")
        
        # 2. YOLO 종료
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                response = await client.post(
                    f"{IOT_BASE_URL}/send-signal_stop_yolo",
                    headers={"accept": "application/json"},
                    content=""
                )
                response.raise_for_status()
                response_data = response.json()
                results["yolo_stopped"] = True
                results["yolo_response"] = response_data
                
            except Exception as yolo_error:
                results["errors"].append(f"YOLO 종료 실패: {str(yolo_error)}")
        
        # 3. DB 상태 업데이트
        if db_manager and db_manager._initialized:
            try:
                from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                with db_manager.get_session() as session:
                    # 세션 종료 처리
                    cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
                    if cmc_session:
                        cmc_session.ended_at = datetime.utcnow()
                        cmc_session.yolo_ended_at = datetime.utcnow()
                        if results["tracking_deactivated"]:
                            cmc_session.tracking_deactivated_at = datetime.utcnow()
                        cmc_session.status = 'ended'
                    
                    # YOLO 상태 업데이트
                    yolo_status = session.query(DeepLearningFunctionStatus).filter_by(function_type='yolo', session_id=session_id).first()
                    if yolo_status:
                        yolo_status.status = 'inactive'
                        yolo_status.last_updated = datetime.utcnow()
                    
                    session.commit()
                    
                    # 리포트 자동 생성
                    await _generate_counseling_report(session_id, db_manager)
                    
            except Exception as db_error:
                logger.warning(f"Failed to update session end status in DB: {db_error}")
                results["errors"].append(f"DB 업데이트 실패: {str(db_error)}")
        
        if results["errors"]:
            results["success"] = False
        
        logger.info(f"Customized mobile conversation ended: session_id={session_id}, success={results['success']}")
        return results
    
    except Exception as e:
        logger.error(f"Error ending customized mobile conversation: {e}", exc_info=True)
        return {
            "error": str(e),
            "session_id": session_id,
            "type": type(e).__name__
        }


async def _generate_counseling_report(session_id: str, db_manager) -> Optional[Dict[str, Any]]:
    """
    심리 상담 리포트 자동 생성 (세션 종료 시)
    대화 내용을 자동으로 분석하여 리포트에 포함합니다.
    
    Args:
        session_id: 대화 세션 ID
        db_manager: 데이터베이스 관리자
    
    Returns:
        리포트 생성 결과
    """
    try:
        if not db_manager or not db_manager._initialized:
            return None
        
        from .database import (
            CustomizedMobileConversationSession,
            CustomizedMobileConversationMessage,
            PsychologicalCounselingAnalysis,
            CounselingReport
        )
        from .psychological_analysis import analyze_conversation_messages, save_psychological_analysis
        
        with db_manager.get_session() as session:
            # 세션 정보 조회
            cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
            if not cmc_session:
                logger.warning(f"Session not found for report generation: session_id={session_id}")
                return None
            
            # 대화 메시지 조회
            db_messages = session.query(CustomizedMobileConversationMessage).filter_by(
                session_id=session_id
            ).order_by(CustomizedMobileConversationMessage.message_order).all()
            
            # 메시지를 분석용 형식으로 변환
            messages_for_analysis = [
                {"role": msg.role, "content": msg.content}
                for msg in db_messages
            ]
            
            # 자동 분석 수행
            analysis_result = analyze_conversation_messages(messages_for_analysis)
            
            # 분석 결과 저장
            analysis_id = save_psychological_analysis(session_id, analysis_result, db_manager)
            
            # 기존 분석 결과 조회 (저장된 것 포함)
            analyses = session.query(PsychologicalCounselingAnalysis).filter_by(
                session_id=session_id
            ).all()
            
            # 리포트 내용 구성
            report_content = {
                "session_id": session_id,
                "user_id": cmc_session.user_id,
                "started_at": cmc_session.started_at.isoformat() if cmc_session.started_at else None,
                "ended_at": cmc_session.ended_at.isoformat() if cmc_session.ended_at else None,
                "duration_minutes": None,
                "message_count": len(db_messages),
                "psychological_analysis": {
                    "overall_score": analysis_result.get("overall_score", 0),
                    "overall_grade": analysis_result.get("overall_grade", "unknown"),
                    "indicators": analysis_result.get("indicators", {}),
                    "analyzed_at": analysis_result.get("analyzed_at")
                },
                "analyses": [
                    {
                        "type": a.analysis_type,
                        "score": a.score,
                        "grade": a.grade,
                        "result": a.analysis_result
                    } for a in analyses
                ],
                "summary": f"맞춤형 이동식 대화 세션이 완료되었습니다. 총 {len(db_messages)}개의 메시지가 교환되었습니다. "
                          f"심리 상담 분석 결과: 전체 점수 {analysis_result.get('overall_score', 0):.1f}점 ({analysis_result.get('overall_grade', 'unknown')} 등급)."
            }
            
            # 세션 지속 시간 계산
            if cmc_session.started_at and cmc_session.ended_at:
                duration = cmc_session.ended_at - cmc_session.started_at
                report_content["duration_minutes"] = int(duration.total_seconds() / 60)
            
            # 리포트 저장
            report = CounselingReport(
                session_id=session_id,
                report_type='session',
                report_content=report_content,
                shared_with=['staff', 'caregiver', 'social_worker', 'family'],  # 기본 공유 대상
                created_by='system'
            )
            session.add(report)
            session.commit()
            
            logger.info(f"Generated counseling report with analysis: session_id={session_id}, report_id={report.id}, analysis_id={analysis_id}")
            return {
                "success": True,
                "report_id": report.id,
                "analysis_id": analysis_id,
                "session_id": session_id,
                "overall_score": analysis_result.get("overall_score", 0),
                "overall_grade": analysis_result.get("overall_grade", "unknown")
            }
    
    except Exception as e:
        logger.error(f"Error generating counseling report: {e}", exc_info=True)
        return None

