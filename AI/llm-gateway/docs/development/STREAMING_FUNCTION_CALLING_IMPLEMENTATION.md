# Streaming + Function Calling 구현 리포트

## 개요
OpenAI 공식 스펙에 따라 스트리밍과 Function Calling을 동시에 지원하도록 구현했습니다.

## 구현 날짜
2025년 11월 19일

## 참고 자료
OpenAI 공식 답변: stream=True와 tools를 동시에 사용 가능

## 구현 내용

### 1. 핵심 흐름

#### 1단계: 스트리밍으로 tool_calls 수신
- `stream=True`, `tools=[...]`, `tool_choice="auto"`로 요청
- 스트림 chunk에서 `delta.tool_calls` 수집
- `finish_reason == "tool_calls"`가 오면 함수 실행 단계로 진행

#### 2단계: 함수 실행
- 수집된 `arguments`를 JSON으로 파싱
- 로컬 Python 함수 실행 (또는 외부 API 호출)
- 결과를 `role="tool"` 메시지로 추가

#### 3단계: 최종 응답 스트리밍
- tool 결과를 포함한 메시지로 두 번째 스트리밍 호출
- 최종 답변을 스트리밍으로 받아서 클라이언트에 전송

### 2. 코드 구조

```python
# 1단계: 스트리밍으로 tool_calls 수신
stream = await client.chat.completions.create(
    model=model,
    messages=messages,
    tools=TOOLS,
    tool_choice="auto",
    stream=True
)

tool_call_id = None
tool_name = None
tool_arguments_str = ""

async for chunk in stream:
    # delta.tool_calls 수집
    if delta.tool_calls:
        tool_call_id = tc.id
        tool_name = tc.function.name
        tool_arguments_str += tc.function.arguments
    
    if choice.finish_reason == "tool_calls":
        break

# 2단계: 함수 실행
tool_args = json.loads(tool_arguments_str)
tool_result = await execute_function(tool_name, tool_args, db_manager)

# 3단계: 최종 응답 스트리밍
final_stream = await client.chat.completions.create(
    model=model,
    messages=messages_with_tool_result,
    stream=True
)
```

### 3. 주요 변경사항

#### `/api/chat/stream` 엔드포인트
- Function Calling 지원 추가
- 스트리밍 중 tool_calls 처리
- 함수 실행 후 최종 응답 스트리밍

#### 이벤트 형식
- `{"content": "텍스트"}`: 일반 텍스트 청크
- `{"tool_call": {...}}`: 함수 호출 감지
- `{"done": true}`: 스트리밍 완료
- `{"error": "..."}`: 에러 발생

### 4. 테스트 인터페이스 업데이트

`test_chat_interface.html`에서 스트리밍 모드 사용 가능:
- `useStream = true`: 스트리밍 모드
- `useStream = false`: 일반 응답 모드

## 기술적 세부사항

### tool_calls 수집
- `delta.tool_calls`는 여러 chunk로 나뉘어 전송됨
- `arguments` 문자열을 누적하여 수집
- `finish_reason == "tool_calls"`로 완료 확인

### 함수 실행
- 수집된 `arguments`를 JSON으로 파싱
- `execute_function()`으로 실제 함수 실행
- 결과를 JSON으로 직렬화하여 메시지에 추가

### 최종 응답
- tool 결과를 포함한 메시지로 재요청
- 스트리밍으로 최종 답변 수신
- 클라이언트에 실시간 전송

## 장점

1. **실시간 피드백**: 사용자가 함수 호출 과정을 실시간으로 확인 가능
2. **성능**: 스트리밍으로 응답 지연 최소화
3. **유연성**: 일반 응답과 스트리밍 응답 선택 가능

## 제한사항

1. **복잡도**: 일반 응답보다 구현이 복잡함
2. **에러 처리**: 스트리밍 중 에러 처리가 더 복잡함
3. **반복 호출**: 최대 5회 반복 제한

## 향후 개선

1. 여러 tool_calls 동시 처리
2. tool_calls 진행 상황 표시
3. 에러 복구 메커니즘 강화

