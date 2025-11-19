# 외부 API 호출 기능 구현 가이드

**작성일**: 2025-11-19  
**목표**: Function Calling을 통해 외부 API 호출

---

## ✅ 답변: Function Calling이 외부 API를 호출할 수 있나요?

**네, 가능합니다!** Function Calling은 외부 API를 호출하는 함수를 정의하고, GPT가 그 함수를 호출하도록 할 수 있습니다.

---

## 🎯 동작 원리

### 1. 함수 정의
외부 API를 호출하는 함수를 정의합니다.

### 2. GPT가 함수 선택
사용자 요청에 따라 GPT가 적절한 함수를 선택합니다.

### 3. 함수 실행
선택된 함수가 외부 API를 호출합니다.

### 4. 결과 반환
API 응답을 GPT에 전달하고, GPT가 사용자에게 설명합니다.

---

## 📋 구현 예시

### 예시: Health Check API 호출 함수

```python
import httpx
from typing import Dict, Any

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "call_external_api",
            "description": "외부 API를 호출합니다. URL과 HTTP 메서드를 지정할 수 있습니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "호출할 API의 전체 URL (예: http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/health)"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                        "description": "HTTP 메서드 (기본값: GET)",
                        "default": "GET"
                    },
                    "headers": {
                        "type": "object",
                        "description": "HTTP 헤더 (선택사항)",
                        "additionalProperties": {"type": "string"}
                    },
                    "body": {
                        "type": "object",
                        "description": "요청 본문 (POST, PUT 등에서 사용, 선택사항)"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

async def execute_function(function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """함수를 실행하고 결과를 반환"""
    
    if function_name == "call_external_api":
        return await _call_external_api(
            url=arguments.get("url"),
            method=arguments.get("method", "GET"),
            headers=arguments.get("headers"),
            body=arguments.get("body")
        )
    
    return {"error": f"Unknown function: {function_name}"}


async def _call_external_api(
    url: str,
    method: str = "GET",
    headers: Dict[str, str] = None,
    body: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    외부 API를 호출합니다.
    
    Args:
        url: API URL
        method: HTTP 메서드
        headers: HTTP 헤더
        body: 요청 본문
    
    Returns:
        API 응답 결과
    """
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 기본 헤더 설정
            request_headers = {
                "Content-Type": "application/json",
                "User-Agent": "LLM-Gateway/1.0"
            }
            if headers:
                request_headers.update(headers)
            
            # HTTP 메서드에 따라 요청
            if method.upper() == "GET":
                response = await client.get(url, headers=request_headers)
            elif method.upper() == "POST":
                response = await client.post(url, headers=request_headers, json=body)
            elif method.upper() == "PUT":
                response = await client.put(url, headers=request_headers, json=body)
            elif method.upper() == "DELETE":
                response = await client.delete(url, headers=request_headers)
            elif method.upper() == "PATCH":
                response = await client.patch(url, headers=request_headers, json=body)
            else:
                return {
                    "error": f"Unsupported HTTP method: {method}",
                    "supported_methods": ["GET", "POST", "PUT", "DELETE", "PATCH"]
                }
            
            # 응답 처리
            try:
                response_data = response.json()
            except Exception:
                response_data = response.text
            
            return {
                "success": True,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "data": response_data,
                "url": str(response.url)
            }
    
    except httpx.TimeoutException:
        return {
            "error": "Request timeout",
            "url": url,
            "timeout": "10 seconds"
        }
    
    except httpx.ConnectError:
        return {
            "error": "Connection error",
            "url": url,
            "message": "Could not connect to the server"
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "url": url,
            "type": type(e).__name__
        }
```

---

## 🚀 사용 예시

### 예시 1: Health Check API 호출

**사용자 요청:**
```
"http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/health API를 호출해줘"
```

**GPT 동작:**
1. GPT가 `call_external_api` 함수 호출 결정
2. 함수 실행:
   ```python
   await _call_external_api(
       url="http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/health",
       method="GET"
   )
   ```
3. API 응답을 GPT에 전달
4. GPT가 사용자에게 결과 설명:
   ```
   "Health Check API를 호출했습니다. 응답 상태 코드는 200이고, 
   서버가 정상적으로 동작 중입니다."
   ```

---

### 예시 2: POST 요청

**사용자 요청:**
```
"http://api.example.com/users에 이름이 '홍길동'인 사용자를 생성해줘"
```

**GPT 동작:**
1. GPT가 `call_external_api` 함수 호출 결정
2. 함수 실행:
   ```python
   await _call_external_api(
       url="http://api.example.com/users",
       method="POST",
       body={"name": "홍길동"}
   )
   ```
3. API 응답을 GPT에 전달
4. GPT가 사용자에게 결과 설명

---

## 🔧 구현 단계

### Step 1: httpx 설치

```bash
pip install httpx
```

또는 `requirements.txt`에 추가:
```
httpx>=0.25.0
```

---

### Step 2: 함수 정의 모듈 생성

**파일**: `src/tools.py` (또는 기존 파일에 추가)

위의 예시 코드를 참고하여 함수를 정의합니다.

---

### Step 3: Chat API에 통합

**파일**: `src/main.py`

```python
from .tools import TOOLS, execute_function

@app.post("/api/chat")
async def text_chat(request: TextChatRequest):
    # ... 기존 코드 ...
    
    # ChatGPT API 호출 (Function Calling 활성화)
    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,  # 함수 정의 추가
        tool_choice="auto"
    )
    
    # 함수 호출 처리
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            # 함수 실행 (외부 API 호출)
            result = await execute_function(function_name, arguments)
            
            # 결과를 GPT에 전달
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })
        
        # 최종 응답 생성
        final_response = await client.chat.completions.create(
            model=model,
            messages=messages
        )
```

---

## 🛡️ 보안 고려사항

### 1. URL 화이트리스트 (권장)

특정 도메인만 허용:

```python
ALLOWED_DOMAINS = [
    "ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com",
    "api.example.com"
]

def is_url_allowed(url: str) -> bool:
    """URL이 허용된 도메인인지 확인"""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc
    
    return any(allowed in domain for allowed in ALLOWED_DOMAINS)

async def _call_external_api(url: str, ...):
    # URL 검증
    if not is_url_allowed(url):
        return {
            "error": "URL not allowed",
            "url": url,
            "allowed_domains": ALLOWED_DOMAINS
        }
    
    # ... API 호출 ...
```

---

### 2. 타임아웃 설정

```python
async with httpx.AsyncClient(timeout=10.0) as client:
    # 타임아웃 10초
    response = await client.get(url)
```

---

### 3. 요청 크기 제한

```python
MAX_REQUEST_SIZE = 1024 * 1024  # 1MB

if body and len(json.dumps(body)) > MAX_REQUEST_SIZE:
    return {"error": "Request body too large"}
```

---

### 4. 인증 정보 관리

```python
# 환경변수에서 API 키 가져오기
API_KEYS = {
    "api.example.com": os.getenv("EXAMPLE_API_KEY")
}

async def _call_external_api(url: str, ...):
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    
    # API 키가 있으면 헤더에 추가
    if domain in API_KEYS:
        headers["Authorization"] = f"Bearer {API_KEYS[domain]}"
```

---

## 📊 고급 기능

### 1. 여러 API 호출

```python
{
    "type": "function",
    "function": {
        "name": "call_multiple_apis",
        "description": "여러 API를 동시에 호출합니다",
        "parameters": {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "호출할 API URL 목록"
                }
            },
            "required": ["urls"]
        }
    }
}
```

---

### 2. API 응답 캐싱

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
async def _call_external_api_cached(url: str, ...):
    """캐시된 API 호출"""
    cache_key = hashlib.md5(f"{url}:{method}".encode()).hexdigest()
    # Redis에 캐시 저장
    # ...
```

---

### 3. 재시도 로직

```python
async def _call_external_api_with_retry(url: str, max_retries: int = 3):
    """재시도 로직이 있는 API 호출"""
    for attempt in range(max_retries):
        try:
            return await _call_external_api(url)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # 지수 백오프
```

---

## 🧪 테스트 예시

### 테스트 1: Health Check

```bash
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/health API를 호출해줘",
    "session_id": "test-session"
  }'
```

---

### 테스트 2: POST 요청

```bash
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "http://api.example.com/users에 POST 요청으로 {\"name\": \"홍길동\"} 데이터를 보내줘",
    "session_id": "test-session"
  }'
```

---

## 📝 요약

### ✅ Function Calling으로 외부 API 호출 가능

1. **함수 정의**: 외부 API를 호출하는 함수를 정의
2. **GPT 선택**: GPT가 사용자 요청에 맞는 함수를 자동 선택
3. **함수 실행**: 함수 내부에서 외부 API 호출
4. **결과 반환**: API 응답을 GPT에 전달하여 사용자에게 설명

### 🔑 핵심 포인트

- ✅ **가능합니다**: Function Calling은 외부 API를 호출할 수 있습니다
- ✅ **유연함**: GET, POST, PUT, DELETE 등 모든 HTTP 메서드 지원
- ✅ **안전함**: URL 화이트리스트, 타임아웃, 인증 등 보안 기능 추가 가능
- ✅ **확장 가능**: 여러 API 호출, 캐싱, 재시도 등 고급 기능 추가 가능

---

**구현 예상 시간**: 1-2시간  
**난이도**: ⭐⭐ (쉬움)

