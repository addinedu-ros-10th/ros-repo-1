# LLM API 호출 기능 개발 계획

**작성일**: 2025-11-19  
**목표**: 채팅으로 요청하면 GPT가 API를 호출할 수 있도록 구현

---

## 📋 LLM이 API를 호출하는 방법

### 1. OpenAI Function Calling (Tools) ⭐ **추천**

**장점:**
- ✅ OpenAI 공식 지원, 안정적
- ✅ 빠른 구현 (기존 코드에 바로 통합 가능)
- ✅ gpt-4o, gpt-4o-mini 등 모든 최신 모델 지원
- ✅ 자동 함수 선택 및 호출
- ✅ 타입 안전성 (JSON Schema)

**단점:**
- ❌ OpenAI 모델에 종속적
- ❌ 복잡한 워크플로우 처리 제한적

**구현 난이도**: ⭐⭐ (쉬움)

---

### 2. MCP (Model Context Protocol)

**장점:**
- ✅ 표준화된 프로토콜
- ✅ 다양한 LLM 지원 (OpenAI, Anthropic, 등)
- ✅ 확장 가능한 아키텍처
- ✅ 서버-클라이언트 분리

**단점:**
- ❌ 상대적으로 복잡한 구현
- ❌ 추가 인프라 필요 (MCP 서버)
- ❌ 학습 곡선 존재

**구현 난이도**: ⭐⭐⭐⭐ (어려움)

---

### 3. ReAct 패턴 (Reasoning + Acting)

**장점:**
- ✅ LLM 독립적
- ✅ 복잡한 워크플로우 처리 가능
- ✅ 자체 제어 가능

**단점:**
- ❌ 직접 구현 필요
- ❌ 에러 처리 복잡
- ❌ 토큰 소비 증가

**구현 난이도**: ⭐⭐⭐⭐⭐ (매우 어려움)

---

## 🎯 추천 방안: OpenAI Function Calling

현재 프로젝트 상황:
- ✅ FastAPI 기반
- ✅ OpenAI API 사용 중
- ✅ gpt-4o-mini, gpt-4o 등 최신 모델 사용
- ✅ 빠른 개발 필요

**결론**: OpenAI Function Calling이 가장 빠르고 효과적입니다.

---

## 🚀 개발 계획

### Phase 1: 기본 Function Calling 구현 (1-2시간)

#### 1.1 Tools 정의
- API 호출을 위한 함수 정의
- JSON Schema로 파라미터 정의
- 함수 설명 작성

#### 1.2 함수 실행 로직
- GPT가 선택한 함수 실행
- 결과를 GPT에 전달
- 최종 응답 생성

#### 1.3 API 통합
- 기존 `/api/chat` 엔드포인트에 tools 추가
- 스트리밍 지원 고려

---

### Phase 2: API 함수 등록 시스템 (2-3시간)

#### 2.1 함수 레지스트리
- 동적 함수 등록
- 함수 메타데이터 관리
- 권한 관리

#### 2.2 API 함수 정의
- 내부 API 함수 (예: System Prompt 관리)
- 외부 API 함수 (예: 날씨, 뉴스)
- 커스텀 함수

---

### Phase 3: 고급 기능 (선택사항, 3-4시간)

#### 3.1 MCP 서버 통합
- MCP 프로토콜 구현
- MCP 서버와 통신
- 다양한 LLM 지원

#### 3.2 함수 체이닝
- 여러 함수 순차 호출
- 조건부 함수 호출
- 에러 처리 및 재시도

---

## 💡 구현 예시

### 예시 1: 기본 Function Calling

```python
# 함수 정의
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "특정 도시의 날씨 정보를 가져옵니다",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "도시 이름 (예: 서울, 부산)"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# 함수 실행 함수
async def execute_function(function_name: str, arguments: dict):
    if function_name == "get_weather":
        city = arguments.get("city")
        # 실제 API 호출
        weather = await fetch_weather_api(city)
        return weather
    return None

# ChatGPT API 호출
response = await client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    tools=tools,
    tool_choice="auto"  # 자동으로 함수 선택
)

# 함수 호출 처리
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        result = await execute_function(function_name, arguments)
        
        # 결과를 GPT에 전달
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })
        
        # 최종 응답 생성
        final_response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
```

---

### 예시 2: 내부 API 호출 함수

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_system_prompts",
            "description": "등록된 System Prompt 목록을 조회합니다",
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
            "description": "새로운 System Prompt를 생성합니다",
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
                    }
                },
                "required": ["name", "content"]
            }
        }
    }
]
```

---

## 📊 비교표

| 방법 | 구현 시간 | 복잡도 | 확장성 | 유지보수 | 추천도 |
|------|----------|--------|--------|----------|--------|
| **Function Calling** | 1-2시간 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **MCP** | 1-2일 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **ReAct** | 3-5일 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |

---

## 🎯 단계별 구현 계획

### Step 1: 기본 구조 (30분)
1. 함수 정의 구조 생성
2. 함수 실행 로직 구현
3. 기본 테스트 함수 추가

### Step 2: API 통합 (1시간)
1. `/api/chat` 엔드포인트에 tools 추가
2. 함수 호출 처리 로직 추가
3. 에러 처리 추가

### Step 3: 함수 확장 (1시간)
1. 내부 API 함수 추가
2. 외부 API 함수 추가 (선택사항)
3. 함수 레지스트리 구현

### Step 4: 테스트 및 문서화 (30분)
1. 테스트 케이스 작성
2. API 문서 업데이트
3. 사용 예시 작성

---

## 🔧 기술 스택

### 필수
- **OpenAI Python SDK**: Function Calling 지원
- **FastAPI**: API 엔드포인트
- **Pydantic**: 타입 검증

### 선택사항
- **httpx**: 외부 API 호출
- **aiohttp**: 비동기 HTTP 클라이언트

---

## 📝 구현 우선순위

### 높은 우선순위
1. ✅ 기본 Function Calling 구조
2. ✅ 내부 API 함수 (System Prompt 관리 등)
3. ✅ 에러 처리

### 중간 우선순위
4. ⚠️ 함수 레지스트리 시스템
5. ⚠️ 외부 API 함수 (날씨, 뉴스 등)

### 낮은 우선순위
6. ⚠️ MCP 서버 통합
7. ⚠️ 함수 체이닝
8. ⚠️ 권한 관리

---

## 🚨 주의사항

### 보안
- 함수 호출 권한 검증
- 입력 값 검증 및 sanitization
- API 키 관리

### 성능
- 함수 호출 비용 고려
- 캐싱 전략
- 타임아웃 설정

### 에러 처리
- 함수 실행 실패 처리
- 네트워크 오류 처리
- 잘못된 파라미터 처리

---

## 📚 참고 자료

- [OpenAI Function Calling 문서](https://platform.openai.com/docs/guides/function-calling)
- [MCP 공식 문서](https://modelcontextprotocol.io/)
- [ReAct 패턴 논문](https://arxiv.org/abs/2210.03629)

---

## ✅ 다음 단계

1. **즉시 시작 가능**: OpenAI Function Calling 구현
2. **향후 확장**: MCP 서버 통합 고려
3. **복잡한 워크플로우**: ReAct 패턴 고려

**추천**: 먼저 Function Calling으로 빠르게 구현하고, 필요시 MCP로 확장

