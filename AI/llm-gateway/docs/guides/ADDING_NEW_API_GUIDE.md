# 새로운 API 추가 가이드

**작성일**: 2025-11-19  
**목적**: Function Calling에 새로운 외부 API를 추가하는 방법

---

## 📋 개요

이 가이드는 LLM이 호출할 수 있는 새로운 외부 API를 추가하는 방법을 설명합니다.

---

## 🎯 추가 단계

### Step 1: API 정보 수집

새로 추가할 API의 다음 정보를 확인합니다:

- **URL**: API 엔드포인트 URL
- **HTTP 메서드**: GET, POST, PUT, DELETE 등
- **파라미터**: 필수/선택 파라미터 목록
- **응답 형식**: JSON, XML 등
- **인증**: API 키, 토큰 등 필요 여부

---

### Step 2: 함수 정의 추가

**파일**: `src/tools.py`

`TOOLS` 리스트에 새로운 함수 정의를 추가합니다.

#### 예시: 새로운 API 추가

```python
TOOLS = [
    # ... 기존 함수들 ...
    
    {
        "type": "function",
        "function": {
            "name": "get_device_status",  # 함수 이름 (영문, snake_case)
            "description": "디바이스 상태를 조회합니다. 사용자가 '디바이스 상태', '기기 상태' 등을 요청할 때 사용합니다.",  # GPT가 이해할 수 있는 설명
            "parameters": {
                "type": "object",
                "properties": {
                    "device_id": {
                        "type": "string",
                        "description": "조회할 디바이스 ID"
                    },
                    "include_details": {
                        "type": "boolean",
                        "description": "상세 정보 포함 여부 (기본값: false)",
                        "default": false
                    }
                },
                "required": ["device_id"]  # 필수 파라미터
            }
        }
    }
]
```

#### 함수 정의 작성 가이드

1. **함수 이름 (`name`)**
   - 영문, snake_case 사용
   - 동사로 시작 (예: `get_`, `create_`, `update_`, `delete_`)
   - 명확하고 간결하게

2. **설명 (`description`)**
   - 한국어로 작성 (GPT가 한국어로 응답하므로)
   - 언제 이 함수를 사용하는지 명시
   - 사용자가 사용할 수 있는 표현 예시 포함

3. **파라미터 (`parameters`)**
   - JSON Schema 형식
   - 각 파라미터의 타입, 설명, 기본값 정의
   - 필수 파라미터는 `required` 배열에 명시

---

### Step 3: 함수 실행 로직 추가

**파일**: `src/tools.py`

`execute_function` 함수에 새로운 케이스를 추가합니다.

```python
async def execute_function(function_name: str, arguments: Dict[str, Any], db_manager=None) -> Dict[str, Any]:
    """함수를 실행하고 결과를 반환"""
    
    try:
        # ... 기존 함수들 ...
        
        elif function_name == "get_device_status":
            device_id = arguments.get("device_id")
            if not device_id:
                return {"error": "device_id is required"}
            include_details = arguments.get("include_details", False)
            return await _get_device_status(device_id, include_details)
        
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
```

---

### Step 4: 실제 API 호출 함수 구현

**파일**: `src/tools.py`

실제 API를 호출하는 함수를 구현합니다.

```python
async def _get_device_status(device_id: str, include_details: bool = False) -> Dict[str, Any]:
    """
    디바이스 상태 조회 API 호출
    
    Args:
        device_id: 디바이스 ID
        include_details: 상세 정보 포함 여부
    
    Returns:
        API 응답 결과
    """
    try:
        # API URL 구성
        url = f"{API_BASE_URL}/api/devices/{device_id}/status"
        
        # 파라미터 구성
        params = {}
        if include_details:
            params["include_details"] = "true"
        
        # HTTP 요청
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
        logger.error(f"Error calling get_device_status: {e}", exc_info=True)
        return {
            "error": str(e),
            "type": type(e).__name__
        }
```

---

## 📝 구현 예시

### 예시 1: GET 요청 (파라미터 없음)

```python
# 함수 정의
{
    "type": "function",
    "function": {
        "name": "get_health_status",
        "description": "서버 헬스 체크 상태를 조회합니다.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
}

# 함수 구현
async def _get_health_status() -> Dict[str, Any]:
    url = f"{API_BASE_URL}/health"
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers={"accept": "application/json"})
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
```

---

### 예시 2: POST 요청 (본문 포함)

```python
# 함수 정의
{
    "type": "function",
    "function": {
        "name": "create_notification",
        "description": "새로운 알림을 생성합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "description": "알림을 받을 사용자 ID"
                },
                "message": {
                    "type": "string",
                    "description": "알림 메시지"
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "알림 우선순위"
                }
            },
            "required": ["user_id", "message"]
        }
    }
}

# 함수 구현
async def _create_notification(user_id: str, message: str, priority: str = "medium") -> Dict[str, Any]:
    url = f"{API_BASE_URL}/api/notifications"
    
    body = {
        "user_id": user_id,
        "message": message,
        "priority": priority
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url,
            json=body,
            headers={"accept": "application/json", "Content-Type": "application/json"}
        )
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
```

---

### 예시 3: 인증이 필요한 API

```python
# 함수 구현
async def _get_authenticated_data(api_key: str) -> Dict[str, Any]:
    url = f"{API_BASE_URL}/api/secure-data"
    
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {api_key}"  # API 키를 헤더에 추가
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return {
            "success": True,
            "status_code": response.status_code,
            "data": response.json()
        }
```

---

## 🔧 고급 기능

### 1. API 베이스 URL 변경

여러 API 서버를 사용하는 경우:

```python
# src/tools.py 상단
API_BASE_URLS = {
    "default": "http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com",
    "device": "http://device-api.example.com",
    "notification": "http://notification-api.example.com"
}

# 함수에서 사용
async def _get_device_status(device_id: str):
    url = f"{API_BASE_URLS['device']}/api/devices/{device_id}/status"
    # ...
```

---

### 2. 에러 처리 개선

```python
async def _call_api_with_retry(url: str, max_retries: int = 3):
    """재시도 로직이 있는 API 호출"""
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500 and attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # 지수 백오프
                continue
            raise
```

---

### 3. 응답 캐싱

```python
from functools import lru_cache
import hashlib

# 간단한 메모리 캐시 (프로덕션에서는 Redis 사용 권장)
_cache = {}

async def _get_cached_data(url: str, cache_ttl: int = 60):
    """캐시된 API 호출"""
    cache_key = hashlib.md5(url.encode()).hexdigest()
    
    # 캐시 확인
    if cache_key in _cache:
        cached_data, timestamp = _cache[cache_key]
        if time.time() - timestamp < cache_ttl:
            return cached_data
    
    # API 호출
    result = await _call_api(url)
    
    # 캐시 저장
    _cache[cache_key] = (result, time.time())
    
    return result
```

---

## ✅ 체크리스트

새로운 API를 추가할 때 확인할 사항:

- [ ] 함수 정의가 `TOOLS` 리스트에 추가됨
- [ ] `execute_function`에 케이스 추가됨
- [ ] 실제 API 호출 함수 구현됨
- [ ] 에러 처리 구현됨
- [ ] 타임아웃 설정됨 (기본 10초)
- [ ] 로깅 추가됨
- [ ] 테스트 완료됨
- [ ] 문서 업데이트됨

---

## 🧪 테스트 방법

### 1. 단위 테스트

```python
# tests/test_tools.py
import pytest
from src.tools import execute_function

@pytest.mark.asyncio
async def test_get_device_status():
    result = await execute_function(
        "get_device_status",
        {"device_id": "test-device-123"}
    )
    assert result["success"] == True
    assert "data" in result
```

### 2. 통합 테스트

```bash
# 채팅 인터페이스에서 테스트
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "디바이스 test-device-123의 상태를 조회해줘",
    "session_id": "test-session"
  }'
```

---

## 📚 참고 자료

### 관련 파일
- `src/tools.py`: 함수 정의 및 구현
- `src/main.py`: Function Calling 통합
- `docs/guides/API_CALLING_USAGE_GUIDE.md`: 사용 가이드

### 외부 문서
- [OpenAI Function Calling 문서](https://platform.openai.com/docs/guides/function-calling)
- [httpx 문서](https://www.python-httpx.org/)

---

## 🔄 업데이트 이력

| 날짜 | 변경 내용 | 작성자 |
|------|----------|--------|
| 2025-11-19 | 초기 문서 작성 | Development Team |

---

**문의**: 개발팀에 문의하시면 추가 지원을 받을 수 있습니다.

