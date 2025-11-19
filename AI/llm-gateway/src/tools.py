"""
LLM이 호출할 수 있는 함수 정의
외부 API 호출 및 내부 기능을 제공합니다.
"""
from typing import Dict, Any, Optional, List
import json
import httpx
import logging

logger = logging.getLogger(__name__)

# API 베이스 URL
API_BASE_URL = "http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com"

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

