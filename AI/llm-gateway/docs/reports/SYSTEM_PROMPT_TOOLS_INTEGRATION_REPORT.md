# System Prompt 및 TOOLS 통합 적용 현황 리포트

**작성일:** 2025-11-20  
**검사 대상:** 모든 LLM API 엔드포인트

---

## 📋 검사 결과 요약

### ✅ 통합 완료된 엔드포인트

1. **`/api/chat`** (텍스트 채팅)
   - ✅ `build_system_prompt()` 사용
   - ✅ `get_tools_for_api()` 사용
   - ⚠️ 최종 응답 생성 시 tools 미전달 (수정 필요)

2. **`/api/chat/stream`** (스트리밍 텍스트 채팅)
   - ✅ `build_system_prompt()` 사용
   - ✅ `get_tools_for_api()` 사용
   - ⚠️ 최종 응답 생성 시 tools 미전달 (수정 필요)

3. **`/api/voice/process`** (음성 입력 → 채팅 → 음성 응답)
   - ✅ `build_system_prompt()` 사용
   - ✅ `get_tools_for_api()` 사용
   - ⚠️ 최종 응답 생성 시 tools 미전달 (수정 필요)

### ❌ 통합되지 않은 엔드포인트

1. **`/api/chat/update-system-prompt`** (세션 System Prompt 업데이트)
   - ❌ 하드코딩된 System Prompt 사용
   - ❌ `build_system_prompt()` 미사용
   - ❌ TOOLS 안내가 하드코딩되어 있음

### 🔍 LLM 호출이 없는 엔드포인트 (검사 불필요)

- `/api/stt` - STT만 사용
- `/api/tts` - TTS만 사용
- `/api/keyword/*` - 키워드 관련 기능
- `/api/session/*` - 세션 관리
- `/api/system-prompts/*` - System Prompt 관리

---

## 🔧 발견된 문제점

### 1. 최종 응답 생성 시 TOOLS 미전달

**위치:**
- `/api/chat` (492-495줄)
- `/api/chat/stream` (773-776줄)
- `/api/voice/process` (1087-1090줄)

**문제:**
최종 응답을 생성할 때 `tools`를 전달하지 않아, 함수 호출이 필요한 경우에도 함수를 호출할 수 없습니다.

**현재 코드:**
```python
# /api/chat
final_response_message = await client.chat.completions.create(
    model=model,
    messages=messages
)

# /api/chat/stream
final_stream = await client.chat.completions.create(
    model=model,
    messages=messages,
    stream=True
)

# /api/voice/process
final_response_message = await client.chat.completions.create(
    model=chat_model,
    messages=messages
)
```

**수정 필요:**
```python
# tools를 전달해야 함
api_params = {
    "model": model,
    "messages": messages
}
if tools and len(tools) > 0:
    api_params["tools"] = tools
    api_params["tool_choice"] = "auto"
```

### 2. `/api/chat/update-system-prompt` 하드코딩

**위치:** 1883-1895줄

**문제:**
- `build_system_prompt()`를 사용하지 않음
- TOOLS 안내가 하드코딩되어 있음
- TOOLS 목록이 업데이트되어도 반영되지 않음

**현재 코드:**
```python
prompt_content = f"""{base_prompt_content}

중요: 사용자가 데이터 조회나 API 호출을 요청하면 반드시 제공된 함수를 사용해야 합니다. 일반적인 응답으로 대체하지 마세요.

사용 가능한 함수:
1. get_users_list: ...
2. get_user_profile: ...
3. get_user_relationships: ...

규칙:
- ...
"""
```

**수정 필요:**
```python
prompt_content = build_system_prompt(base_prompt_content)
```

---

## ✅ 수정 계획

### 1. 최종 응답 생성 시 TOOLS 전달

**수정 대상:**
- `/api/chat` 엔드포인트 (492-495줄)
- `/api/chat/stream` 엔드포인트 (773-776줄)
- `/api/voice/process` 엔드포인트 (1087-1090줄)

**수정 내용:**
각 엔드포인트의 최종 응답 생성 부분에서 `tools`를 전달하도록 수정

### 2. `/api/chat/update-system-prompt` 통합

**수정 대상:**
- `/api/chat/update-system-prompt` 엔드포인트 (1883-1895줄)

**수정 내용:**
- 하드코딩된 System Prompt 제거
- `build_system_prompt()` 사용

---

## 📊 통합 상태

| 엔드포인트 | System Prompt 통합 | TOOLS 통합 | 최종 응답 TOOLS 전달 | 상태 |
|-----------|-------------------|-----------|---------------------|------|
| `/api/chat` | ✅ | ✅ | ❌ | 수정 필요 |
| `/api/chat/stream` | ✅ | ✅ | ❌ | 수정 필요 |
| `/api/voice/process` | ✅ | ✅ | ❌ | 수정 필요 |
| `/api/chat/update-system-prompt` | ❌ | ❌ | N/A | 수정 필요 |

---

## 🎯 수정 후 예상 효과

1. **일관성 향상**
   - 모든 엔드포인트에서 동일한 System Prompt 사용
   - TOOLS 목록 자동 반영

2. **기능 완성도 향상**
   - 최종 응답 생성 시에도 함수 호출 가능
   - 사용자 요청에 대한 완전한 응답 제공

3. **유지보수성 향상**
   - System Prompt 및 TOOLS 변경 시 모든 엔드포인트에 자동 반영
   - 하드코딩 제거로 버그 발생 가능성 감소

---

**작성자:** AI Assistant  
**검토 필요:** 코드 리뷰 및 테스트

