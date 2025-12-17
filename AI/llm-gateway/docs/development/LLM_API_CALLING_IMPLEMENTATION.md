# LLM API 호출 기능 구현 가이드

**작성일**: 2025-11-19  
**방법**: OpenAI Function Calling

---

## 🎯 구현 개요

OpenAI Function Calling을 사용하여 GPT가 API를 호출할 수 있도록 구현합니다.

---

## 📋 구현 단계

### Step 1: 함수 정의 모듈 생성

**파일**: `src/tools.py` (신규)

```python
"""
LLM이 호출할 수 있는 함수 정의
"""
from typing import Dict, Any, List
import json

# 함수 정의 리스트
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_system_prompts",
            "description": "등록된 System Prompt 목록을 조회합니다. 사용자가 프롬프트 목록을 요청할 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_system_prompt",
            "description": "새로운 System Prompt를 생성합니다. 사용자가 새 프롬프트를 만들고 싶을 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "프롬프트 이름"
                    },
                    "content": {
                        "type": "string",
                        "description": "프롬프트 내용"
                    },
                    "description": {
                        "type": "string",
                        "description": "프롬프트 설명 (선택사항)"
                    },
                    "is_default": {
                        "type": "boolean",
                        "description": "기본 프롬프트로 설정할지 여부"
                    }
                },
                "required": ["name", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_system_prompt",
            "description": "기존 System Prompt를 수정합니다. 사용자가 프롬프트를 수정하고 싶을 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt_id": {
                        "type": "integer",
                        "description": "수정할 프롬프트 ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "새 프롬프트 이름 (선택사항)"
                    },
                    "content": {
                        "type": "string",
                        "description": "새 프롬프트 내용 (선택사항)"
                    },
                    "description": {
                        "type": "string",
                        "description": "새 프롬프트 설명 (선택사항)"
                    }
                },
                "required": ["prompt_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_system_prompt",
            "description": "System Prompt를 삭제합니다. 사용자가 프롬프트를 삭제하고 싶을 때 사용합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt_id": {
                        "type": "integer",
                        "description": "삭제할 프롬프트 ID"
                    }
                },
                "required": ["prompt_id"]
            }
        }
    }
]


async def execute_function(function_name: str, arguments: Dict[str, Any], db_manager) -> Dict[str, Any]:
    """
    함수를 실행하고 결과를 반환합니다.
    
    Args:
        function_name: 실행할 함수 이름
        arguments: 함수 인자
        db_manager: 데이터베이스 관리자
    
    Returns:
        함수 실행 결과
    """
    try:
        if function_name == "get_system_prompts":
            return await _get_system_prompts(db_manager)
        
        elif function_name == "create_system_prompt":
            return await _create_system_prompt(
                name=arguments.get("name"),
                content=arguments.get("content"),
                description=arguments.get("description"),
                is_default=arguments.get("is_default", False),
                db_manager=db_manager
            )
        
        elif function_name == "update_system_prompt":
            return await _update_system_prompt(
                prompt_id=arguments.get("prompt_id"),
                name=arguments.get("name"),
                content=arguments.get("content"),
                description=arguments.get("description"),
                db_manager=db_manager
            )
        
        elif function_name == "delete_system_prompt":
            return await _delete_system_prompt(
                prompt_id=arguments.get("prompt_id"),
                db_manager=db_manager
            )
        
        else:
            return {
                "error": f"Unknown function: {function_name}",
                "available_functions": [tool["function"]["name"] for tool in TOOLS]
            }
    
    except Exception as e:
        return {
            "error": str(e),
            "function": function_name
        }


async def _get_system_prompts(db_manager):
    """System Prompt 목록 조회"""
    if not db_manager._initialized:
        return {"error": "Database not initialized"}
    
    from .database import SystemPrompt
    
    with db_manager.get_session() as session:
        prompts = session.query(SystemPrompt).order_by(SystemPrompt.created_at.desc()).all()
        return {
            "success": True,
            "prompts": [
                {
                    "id": p.id,
                    "name": p.name,
                    "content": p.content[:100] + "..." if len(p.content) > 100 else p.content,
                    "description": p.description,
                    "is_default": p.is_default
                }
                for p in prompts
            ]
        }


async def _create_system_prompt(name: str, content: str, description: str = None, is_default: bool = False, db_manager=None):
    """System Prompt 생성"""
    if not db_manager._initialized:
        return {"error": "Database not initialized"}
    
    from .database import SystemPrompt
    
    with db_manager.get_session() as session:
        prompt = SystemPrompt(
            name=name,
            content=content,
            description=description,
            is_default=is_default
        )
        session.add(prompt)
        session.flush()
        
        return {
            "success": True,
            "message": f"System Prompt '{name}' created successfully",
            "prompt_id": prompt.id
        }


async def _update_system_prompt(prompt_id: int, name: str = None, content: str = None, description: str = None, db_manager=None):
    """System Prompt 수정"""
    if not db_manager._initialized:
        return {"error": "Database not initialized"}
    
    from .database import SystemPrompt
    from datetime import datetime
    
    with db_manager.get_session() as session:
        prompt = session.query(SystemPrompt).filter_by(id=prompt_id).first()
        if not prompt:
            return {"error": f"System Prompt {prompt_id} not found"}
        
        if name is not None:
            prompt.name = name
        if content is not None:
            prompt.content = content
        if description is not None:
            prompt.description = description
        
        prompt.updated_at = datetime.utcnow()
        
        return {
            "success": True,
            "message": f"System Prompt {prompt_id} updated successfully"
        }


async def _delete_system_prompt(prompt_id: int, db_manager=None):
    """System Prompt 삭제"""
    if not db_manager._initialized:
        return {"error": "Database not initialized"}
    
    from .database import SystemPrompt
    
    with db_manager.get_session() as session:
        prompt = session.query(SystemPrompt).filter_by(id=prompt_id).first()
        if not prompt:
            return {"error": f"System Prompt {prompt_id} not found"}
        
        session.delete(prompt)
        
        return {
            "success": True,
            "message": f"System Prompt {prompt_id} deleted successfully"
        }
```

---

### Step 2: Chat API에 Function Calling 통합

**파일**: `src/main.py` 수정

```python
from .tools import TOOLS, execute_function

@app.post("/api/chat", summary="텍스트 채팅 (Function Calling 지원)")
async def text_chat(request: TextChatRequest):
    """
    텍스트 메시지를 ChatGPT에 전송하고 응답을 받습니다.
    Function Calling을 지원하여 GPT가 API를 호출할 수 있습니다.
    """
    start_time = time.time()
    try:
        # 기본값 설정
        system_prompt = request.system_prompt or settings.default_system_prompt
        model = request.model.value if request.model else settings.default_chat_model
        
        # 세션 히스토리 가져오기 또는 생성
        try:
            messages = await redis_session_manager.get_session(request.session_id)
            if not messages:
                messages = await redis_session_manager.initialize_session(request.session_id, system_prompt)
        except Exception:
            if request.session_id not in fallback_store:
                fallback_store[request.session_id] = [
                    {"role": "system", "content": system_prompt}
                ]
            messages = fallback_store[request.session_id]

        # 사용자 메시지 추가
        messages.append({"role": "user", "content": request.message})

        # ChatGPT API 호출 (Function Calling 활성화)
        max_iterations = 5  # 최대 함수 호출 반복 횟수
        iteration = 0
        
        while iteration < max_iterations:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS if iteration == 0 else None,  # 첫 번째 호출에만 tools 전달
                tool_choice="auto"  # 자동으로 함수 선택
            )
            
            message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ] if message.tool_calls else None
            })
            
            # 함수 호출이 없으면 종료
            if not message.tool_calls:
                break
            
            # 함수 실행
            for tool_call in message.tool_calls:
                function_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                # 함수 실행
                result = await execute_function(function_name, arguments, db_manager)
                
                # 결과를 메시지에 추가
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })
            
            iteration += 1
        
        # 최종 응답
        assistant_message = messages[-1].get("content") or "함수 호출이 완료되었습니다."
        
        # 어시스턴트 응답 저장
        messages.append({"role": "assistant", "content": assistant_message})
        
        # Redis에 저장
        try:
            await redis_session_manager.save_session(request.session_id, messages)
            save_conversation_to_db(request.session_id, messages, system_prompt)
        except Exception:
            fallback_store[request.session_id] = messages

        # 비용 로깅
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            input_cost = (usage.prompt_tokens / 1_000_000) * 0.15 if usage.prompt_tokens else 0
            output_cost = (usage.completion_tokens / 1_000_000) * 0.60 if usage.completion_tokens else 0
            total_cost = input_cost + output_cost
            
            log_cost(
                session_id=request.session_id,
                service_type="chat",
                model=model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cost_usd=total_cost
            )

        processing_time = (time.time() - start_time) * 1000
        log_api_request(
            session_id=request.session_id,
            endpoint="/api/chat",
            method="POST",
            request_data={"message": request.message[:100]},
            response_data={"response_length": len(assistant_message)},
            status_code=200,
            processing_time_ms=processing_time
        )

        return {
            "success": True,
            "message": assistant_message,
            "session_id": request.session_id,
            "processing_time_ms": round(processing_time, 2),
            "iterations": iteration
        }

    except Exception as e:
        logger.error(f"Chat processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"채팅 처리 실패: {str(e)}")
```

---

### Step 3: 스트리밍 지원 (선택사항)

스트리밍 응답에서도 Function Calling을 지원하려면 추가 구현이 필요합니다.

---

## 🧪 테스트 예시

### 테스트 1: System Prompt 목록 조회

```bash
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "등록된 System Prompt 목록을 보여줘",
    "session_id": "test-session"
  }'
```

**예상 동작:**
1. GPT가 `get_system_prompts` 함수 호출 결정
2. 함수 실행하여 프롬프트 목록 조회
3. 결과를 GPT에 전달
4. GPT가 사용자에게 친절하게 설명

---

### 테스트 2: System Prompt 생성

```bash
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "번역 전문가 프롬프트를 만들어줘. 이름은 번역 전문가이고, 내용은 당신은 전문 번역가입니다.",
    "session_id": "test-session"
  }'
```

**예상 동작:**
1. GPT가 `create_system_prompt` 함수 호출 결정
2. 함수 실행하여 프롬프트 생성
3. 결과를 GPT에 전달
4. GPT가 생성 완료 메시지 전달

---

## 📊 성능 고려사항

### 토큰 사용량
- Function Calling은 추가 토큰을 사용합니다
- 함수 정의: ~100-200 tokens
- 함수 호출: ~50-100 tokens
- 결과 처리: 결과 크기에 비례

### 비용 최적화
- 필요한 함수만 등록
- 함수 설명을 간결하게 작성
- 결과를 요약하여 전달

---

## 🔒 보안 고려사항

### 입력 검증
- 함수 인자 타입 검증
- 필수 파라미터 확인
- 값 범위 검증

### 권한 관리
- 함수 호출 권한 확인
- 세션별 권한 관리
- 민감한 함수 보호

---

## 🚀 다음 단계

1. **기본 구현 완료 후**:
   - 더 많은 함수 추가
   - 외부 API 통합
   - 함수 레지스트리 시스템

2. **향후 확장**:
   - MCP 서버 통합
   - 함수 체이닝
   - 워크플로우 자동화

---

**구현 예상 시간**: 2-3시간  
**난이도**: ⭐⭐ (중간)

