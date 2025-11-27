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
DL_BASE_URL = "http://192.168.10.11:8000"

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
            "name": "get_resident_info",
            "description": "요양원 입소자(어르신)의 상세 정보를 조회합니다. 사용자가 '입소자 정보', '어르신 정보', '요양원 정보', '입소자 상세', '어르신 상세', '복약 일정', '응급 연락처', '의료 정보', '보험 정보', '생활실 정보', 'ADL 수준', '이동 수준', '인지 수준', '특이사항', '사건/사고 기록', '식이 제한' 등을 요청할 때 반드시 이 함수를 호출하세요. user_id 파라미터가 필요합니다. 이 함수는 입소자의 모든 정보(입소 정보, 생활실, 복약 일정, 특이사항, 응급 연락처, 보험 정보, 의료 기관 정보 등)를 포함합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "조회할 입소자(어르신)의 UUID (예: '00000000-0000-0000-0000-000000000001')"
                    }
                },
                "required": ["user_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "guide_wandering_resident_to_room",
            "description": "순찰 중 어르신 배회가 탐지된 경우 생활관 복귀를 안내합니다. 어르신의 성함 또는 nickname을 기반으로 정보를 조회하고, 친절한 안내 메시지를 최소 3회 반복하여 전달합니다. 사용자가 '배회 탐지', '어르신 복도에 있음', '생활실로 안내', '복귀 안내', '어르신이 복도에 계심', '배회 중인 어르신 발견' 등을 언급할 때 반드시 이 함수를 호출하세요. resident_name 또는 nickname 중 하나는 반드시 제공되어야 합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "resident_name": {
                        "type": "string",
                        "description": "어르신의 성함 (예: '정도현', '한기문'). nickname이 없을 때 사용합니다."
                    },
                    "nickname": {
                        "type": "string",
                        "description": "어르신의 nickname (예: 'Akaza', 'Gyomei Himejima'). nickname이 있으면 우선적으로 사용합니다."
                    },
                    "detection_location": {
                        "type": "string",
                        "description": "배회 탐지 위치 (예: '1층 복도', '2층 로비', '3층 계단'). 선택사항입니다."
                    }
                },
                "required": []
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
            "description": "맞춤형 이동식 대화를 시작합니다. 사용자가 '대화를 하고 싶어', '맞춤 대화를 시작해줘', '맞춤형 이동식 대화를 하고 싶어', '대화 좀 나눌 수 있을까', '함께 이야기 하자', '산책 하면서 같이 이야기 할래' 등을 요청할 때 반드시 이 함수를 호출하세요. YOLO 객체 인식 프로그램을 시작하여 맞춤형 이동식 대화 기능을 활성화합니다. 함수 호출 성공 후 반드시 사용자에게 '함께 걸으며 대화 할까요?'라고 물어봐야 합니다. user_id는 사용자가 말한 이름(예: '서보리', '보리')을 그대로 사용하거나, 이전 대화에서 언급된 이름을 사용하세요. 정확한 user_id를 모르는 경우 사용자가 말한 이름을 그대로 사용해도 됩니다.",
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
    # 상세 로깅: 함수 호출 시작
    logger.info(f"🔧 TOOL CALL START: function_name='{function_name}', arguments={arguments}")
    
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
        
        elif function_name == "get_resident_info":
            user_id = arguments.get("user_id")
            if not user_id:
                return {"error": "user_id is required"}
            return await _get_resident_info(user_id)
        
        elif function_name == "guide_wandering_resident_to_room":
            resident_name = arguments.get("resident_name")
            nickname = arguments.get("nickname")
            detection_location = arguments.get("detection_location", "복도")
            if not resident_name and not nickname:
                return {"error": "resident_name 또는 nickname 중 하나는 필수입니다."}
            return await _guide_wandering_resident_to_room(resident_name, nickname, detection_location)
        
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
                logger.warning(f"🔧 TOOL CALL FAILED: activate_tracking - missing session_id")
                return {"error": "session_id is required"}
            logger.info(f"🔧 TOOL CALL: activate_tracking - session_id={session_id}")
            result = await _activate_tracking(session_id, db_manager)
            logger.info(f"🔧 TOOL CALL SUCCESS: activate_tracking - success={result.get('success', False)}")
            return result
        
        elif function_name == "end_customized_mobile_conversation":
            session_id = arguments.get("session_id")
            if not session_id:
                logger.warning(f"🔧 TOOL CALL FAILED: end_customized_mobile_conversation - missing session_id")
                return {"error": "session_id is required"}
            logger.info(f"🔧 TOOL CALL: end_customized_mobile_conversation - session_id={session_id}")
            result = await _end_customized_mobile_conversation(session_id, db_manager)
            logger.info(f"🔧 TOOL CALL SUCCESS: end_customized_mobile_conversation - success={result.get('success', False)}")
            return result
        
        else:
            logger.warning(f"🔧 TOOL CALL FAILED: Unknown function '{function_name}'. Available: {[tool['function']['name'] for tool in TOOLS]}")
            return {
                "error": f"Unknown function: {function_name}",
                "available_functions": [tool["function"]["name"] for tool in TOOLS]
            }
    
    except Exception as e:
        logger.error(f"🔧 TOOL CALL ERROR: function_name='{function_name}', error={str(e)}", exc_info=True)
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


async def _get_resident_info(user_id: str) -> Dict[str, Any]:
    """
    요양원 입소자(어르신) 상세 정보 조회 API 호출
    
    Args:
        user_id: 입소자(어르신) UUID
    
    Returns:
        API 응답 결과 (입소자 정보, 복약 일정, 특이사항, 응급 연락처, 보험 정보 등 포함)
    """
    try:
        url = f"{API_BASE_URL}/api/residents/{user_id}"
        
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
        logger.error(f"Error calling get_resident_info: {e}", exc_info=True)
        return {
            "error": str(e),
            "type": type(e).__name__
        }


async def _search_residents(keyword: str) -> Dict[str, Any]:
    """
    키워드로 입소자 정보 검색 API 호출
    
    Args:
        keyword: 검색 키워드 (nickname, user_name, resident_number 등)
    
    Returns:
        API 응답 결과 (입소자 목록)
    """
    try:
        url = f"{API_BASE_URL}/api/residents/search/{keyword}"
        
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
        logger.error(f"Error calling search_residents: {e}", exc_info=True)
        return {
            "error": str(e),
            "type": type(e).__name__
        }


async def _guide_wandering_resident_to_room(
    resident_name: Optional[str] = None,
    nickname: Optional[str] = None,
    detection_location: str = "복도"
) -> Dict[str, Any]:
    """
    배회 탐지된 어르신을 생활실로 안내하는 함수
    
    Args:
        resident_name: 어르신 성함
        nickname: 어르신 nickname
        detection_location: 탐지 위치
    
    Returns:
        안내 메시지 및 어르신 정보
    """
    try:
        # 1. nickname 우선으로 검색
        search_keyword = None
        if nickname:
            search_keyword = nickname
            logger.info(f"Searching resident by nickname: {nickname}")
        elif resident_name:
            search_keyword = resident_name
            logger.info(f"Searching resident by name: {resident_name}")
        else:
            return {
                "success": False,
                "error": "resident_name 또는 nickname 중 하나는 필수입니다."
            }
        
        # 2. 입소자 검색
        search_result = await _search_residents(search_keyword)
        
        if not search_result.get("success") or not search_result.get("data"):
            return {
                "success": False,
                "error": f"어르신 정보를 찾을 수 없습니다. (검색어: {search_keyword})",
                "search_keyword": search_keyword
            }
        
        residents = search_result["data"]
        if not residents or len(residents) == 0:
            return {
                "success": False,
                "error": f"어르신 정보를 찾을 수 없습니다. (검색어: {search_keyword})",
                "search_keyword": search_keyword
            }
        
        # 3. 첫 번째 결과 선택 (또는 가장 일치하는 결과)
        resident = residents[0]
        
        # 4. 생활실 정보 추출
        user_name = resident.get("user_name", "어르신")
        resident_nickname = resident.get("nickname") or user_name
        room_number = resident.get("room_number", "알 수 없음")
        floor_number = resident.get("floor_number", "알 수 없음")
        bed_number = resident.get("bed_number", "")
        
        # 5. 안내 메시지 생성 (3회 반복)
        guidance_messages = []
        
        # 1회차: 친절한 인사와 상황 설명
        message1 = f"안녕하세요, {resident_nickname} 어르신! 지금 {detection_location}에서 어르신을 발견했습니다. 어르신의 생활실은 {floor_number}층 {room_number}호"
        if bed_number:
            message1 += f" {bed_number}번 침대"
        message1 += "입니다. 안전을 위해 생활실로 복귀해 주시겠어요?"
        guidance_messages.append(message1)
        
        # 2회차: 상황 재확인 및 복귀 안내
        message2 = f"{user_name} 어르신, 지금 {detection_location}에 계시는 것으로 보입니다. {floor_number}층 {room_number}호 생활실로 돌아가 주시면 감사하겠습니다. 혼자 계시면 위험할 수 있으니 생활실로 복귀해 주세요."
        guidance_messages.append(message2)
        
        # 3회차: 함께 안내 제안
        message3 = f"어르신, {resident_nickname} 어르신! 지금 {detection_location}에 계신 것으로 탐지되었습니다. 생활실은 {floor_number}층 {room_number}호입니다. 제가 함께 생활실로 안내해 드릴까요? 안전을 위해 생활실로 복귀해 주시기 바랍니다."
        guidance_messages.append(message3)
        
        return {
            "success": True,
            "resident_info": {
                "user_id": resident.get("user_id"),
                "user_name": user_name,
                "nickname": resident_nickname,
                "room_number": room_number,
                "floor_number": floor_number,
                "bed_number": bed_number,
                "resident_number": resident.get("resident_number")
            },
            "guidance_messages": guidance_messages,
            "detection_location": detection_location,
            "message": f"{resident_nickname} 어르신의 생활실 복귀 안내 메시지가 생성되었습니다."
        }
    
    except Exception as e:
        logger.error(f"Error in guide_wandering_resident_to_room: {e}", exc_info=True)
        return {
            "success": False,
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
        
        # 1. DB에 세션 생성 또는 업데이트
        if db_manager and db_manager._initialized:
            try:
                from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                with db_manager.get_session() as session:
                    # 기존 세션 확인
                    cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
                    
                    if cmc_session:
                        # 기존 세션이 있으면 업데이트
                        logger.info(f"Updating existing CMC session: session_id={session_id}")
                        cmc_session.user_id = user_id
                        cmc_session.started_at = datetime.utcnow()
                        cmc_session.status = 'yolo_starting'
                        cmc_session.ended_at = None  # 재시작 시 종료 시간 초기화
                        cmc_session.yolo_started_at = None
                        cmc_session.yolo_ended_at = None
                        cmc_session.tracking_activated_at = None
                        cmc_session.tracking_deactivated_at = None
                    else:
                        # 새 세션 생성
                        logger.info(f"Creating new CMC session: session_id={session_id}")
                        cmc_session = CustomizedMobileConversationSession(
                            session_id=session_id,
                            user_id=user_id,
                            started_at=datetime.utcnow(),
                            status='yolo_starting'
                        )
                        session.add(cmc_session)
                    
                    # YOLO 상태 확인 및 업데이트
                    yolo_status = session.query(DeepLearningFunctionStatus).filter_by(
                        function_type='yolo',
                        session_id=session_id
                    ).first()
                    
                    if yolo_status:
                        # 기존 상태 업데이트
                        yolo_status.status = 'starting'
                        yolo_status.last_updated = datetime.utcnow()
                        yolo_status.meta_data = {'user_id': user_id}
                    else:
                        # 새 상태 생성
                        yolo_status = DeepLearningFunctionStatus(
                            function_type='yolo',
                            session_id=session_id,
                            status='starting',
                            meta_data={'user_id': user_id}
                        )
                        session.add(yolo_status)
                    
                    session.commit()
                    logger.info(f"CMC session and YOLO status saved/updated in DB: session_id={session_id}")
            except Exception as db_error:
                logger.error(f"Failed to save/update session to DB: {db_error}", exc_info=True)
                # DB 오류가 있어도 API 호출은 계속 진행
        
        # 2. YOLO 시작 API 호출 (비동기, fire-and-forget)
        # YOLO API는 'terminated 되기 전까지 계속 호출 상태가 지속'되므로
        # API 호출을 시작하고 즉시 반환 (응답을 기다리지 않음)
        import asyncio
        
        async def _call_yolo_api():
            """YOLO API를 백그라운드에서 호출하고 상태를 업데이트"""
            try:
                async with httpx.AsyncClient(timeout=120.0) as client:  # 타임아웃을 120초로 증가
                    try:
                        response = await client.post(
                            f"{DL_BASE_URL}/send-signal_run_yolo",
                            headers={"accept": "application/json"},
                            content=""
                        )
                        response.raise_for_status()
                        response_data = response.json()
                        
                        # DB 상태 업데이트 (성공)
                        if db_manager and db_manager._initialized:
                            try:
                                from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                                with db_manager.get_session() as session:
                                    cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
                                    if cmc_session:
                                        cmc_session.yolo_started_at = datetime.utcnow()
                                        cmc_session.status = 'yolo_running'
                                    
                                    yolo_status = session.query(DeepLearningFunctionStatus).filter_by(function_type='yolo', session_id=session_id).first()
                                    if yolo_status:
                                        yolo_status.status = 'active'
                                        yolo_status.last_updated = datetime.utcnow()
                                    
                                    session.commit()
                                logger.info(f"YOLO started successfully (background): session_id={session_id}")
                            except Exception as db_error:
                                logger.warning(f"Failed to update YOLO success status in DB: {db_error}")
                    except httpx.TimeoutException:
                        logger.warning(f"YOLO API timeout (background): session_id={session_id} - API may still be running")
                        # 타임아웃이 발생해도 YOLO는 백그라운드에서 실행 중일 수 있음
                        if db_manager and db_manager._initialized:
                            try:
                                from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                                with db_manager.get_session() as session:
                                    cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
                                    if cmc_session:
                                        # 타임아웃이지만 YOLO는 실행 중일 수 있으므로 상태를 'yolo_running'으로 설정
                                        cmc_session.status = 'yolo_running'
                                        cmc_session.yolo_started_at = datetime.utcnow()
                                    
                                    yolo_status = session.query(DeepLearningFunctionStatus).filter_by(function_type='yolo', session_id=session_id).first()
                                    if yolo_status:
                                        yolo_status.status = 'active'
                                        yolo_status.last_updated = datetime.utcnow()
                                        yolo_status.meta_data = yolo_status.meta_data or {}
                                        yolo_status.meta_data['timeout_but_running'] = True
                                    
                                    session.commit()
                            except Exception as db_error:
                                logger.warning(f"Failed to update YOLO timeout status in DB: {db_error}")
                    except Exception as e:
                        logger.error(f"YOLO API call error (background): {e}, session_id={session_id}", exc_info=True)
                        # 에러 발생 시 DB 상태 업데이트
                        if db_manager and db_manager._initialized:
                            try:
                                from .database import CustomizedMobileConversationSession, DeepLearningFunctionStatus
                                with db_manager.get_session() as session:
                                    cmc_session = session.query(CustomizedMobileConversationSession).filter_by(session_id=session_id).first()
                                    if cmc_session:
                                        cmc_session.status = 'error'
                                        cmc_session.updated_at = datetime.utcnow()
                                    
                                    yolo_status = session.query(DeepLearningFunctionStatus).filter_by(function_type='yolo', session_id=session_id).first()
                                    if yolo_status:
                                        yolo_status.status = 'error'
                                        yolo_status.last_updated = datetime.utcnow()
                                        yolo_status.meta_data = yolo_status.meta_data or {}
                                        yolo_status.meta_data['error'] = str(e)
                                    
                                    session.commit()
                            except Exception as db_error:
                                logger.warning(f"Failed to update YOLO error status in DB: {db_error}")
            except Exception as e:
                logger.error(f"YOLO background task error: {e}, session_id={session_id}", exc_info=True)
        
        # 백그라운드 태스크로 실행 (응답을 기다리지 않음)
        asyncio.create_task(_call_yolo_api())
        logger.info(f"YOLO API call initiated (fire-and-forget): session_id={session_id}")
        
        # 즉시 반환 (API 호출 완료를 기다리지 않음)
        return {
            "success": True,
            "status": "yolo_starting",
            "message": "YOLO 객체 인식 프로그램을 시작했습니다. 맞춤형 이동식 대화를 시작할 수 있습니다.",
            "next_action": "ask_walking_together",
            "note": "YOLO는 백그라운드에서 실행 중입니다."
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
                    f"{DL_BASE_URL}/send-signal_tracking_switch",
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
                                tracking_status.meta_data = {'tracking_switch': tracking_switch}
                            else:
                                tracking_status = DeepLearningFunctionStatus(
                                    function_type='tracking',
                                    session_id=session_id,
                                    status='active' if is_activated else 'inactive',
                                    meta_data={'tracking_switch': tracking_switch}
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
                    f"{DL_BASE_URL}/send-signal_stop_yolo",
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

