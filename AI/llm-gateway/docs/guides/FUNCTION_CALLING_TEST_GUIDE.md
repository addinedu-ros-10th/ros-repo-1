# Function Calling 테스트 가이드

## 개요

이 가이드는 LLM Gateway의 Function Calling 기능을 테스트하는 방법을 설명합니다.

## 주요 변경 사항

### 1. API 엔드포인트 변경
- **이전**: `/api/chat/stream` (스트리밍, Function Calling 미지원)
- **현재**: `/api/chat` (일반 응답, Function Calling 지원)

### 2. System Prompt 자동 감싸기
- 사용자가 선택한 System Prompt에 Function Calling 안내가 자동으로 추가됩니다
- 서버와 클라이언트 모두에서 처리됩니다

### 3. 프롬프트 엔지니어링 로깅
- 브라우저 콘솔에서 프롬프트 내용을 확인할 수 있습니다
- 개발자 도구(F12) → Console 탭에서 확인

## 테스트 방법

### 1. 테스트 환경 준비

```bash
# 서버 시작
cd AI/llm-gateway
docker-compose up -d

# 또는 직접 실행
python -m uvicorn src.main:app --reload --port 8001
```

### 2. 테스트 페이지 접속

```
http://localhost:8001/tests/user_testing/test_chat_interface.html
```

### 3. 브라우저 개발자 도구 열기

- **Chrome/Edge**: F12 또는 Ctrl+Shift+I
- **Firefox**: F12 또는 Ctrl+Shift+K
- **Safari**: Cmd+Option+I

### 4. 콘솔 로그 확인

메시지를 전송하면 다음과 같은 로그가 출력됩니다:

```
🔧 프롬프트 엔지니어링 정보
  📝 원본 System Prompt: 당신은 친절한 한국어 AI 어시스턴트입니다.
  🛠️ Function Calling 안내 포함: 예
  📋 최종 System Prompt (일부): 당신은 친절한 한국어 AI 어시스턴트입니다.

중요: 사용자가 데이터 조회나 API 호출을 요청하면 반드시 제공된 함수를 사용해야 합니다...
  💬 사용자 메시지: 사용자 목록을 보여줘
  🆔 Session ID: chat-1234567890
✅ API 응답: {success: true, message_length: 150, has_tool_calls: "예"}
```

## 테스트 시나리오

### 시나리오 1: 사용자 목록 조회

**입력:**
```
사용자 목록을 보여줘
```

**예상 동작:**
1. LLM이 `get_users_list` 함수를 호출
2. API에서 사용자 목록 데이터를 가져옴
3. 사용자에게 포맷된 목록을 표시

**확인 사항:**
- 콘솔에서 "Tool calls detected" 로그 확인
- "Executing function: get_users_list" 로그 확인
- 실제 사용자 목록이 응답에 포함되는지 확인

### 시나리오 2: 특정 사용자 프로필 조회

**입력:**
```
사용자 ID 10fa45f2-f375-41c9-a62a-093efcd01bd3의 프로필을 보여줘
```

**예상 동작:**
1. LLM이 `get_user_profile` 함수를 호출
2. user_id 파라미터로 전달
3. 프로필 정보를 가져와서 표시

### 시나리오 3: 사용자 관계 정보 조회

**입력:**
```
사용자 10fa45f2-f375-41c9-a62a-093efcd01bd3의 관계 정보를 알려줘
```

**예상 동작:**
1. LLM이 `get_user_relationships` 함수를 호출
2. 관계 정보를 가져와서 표시

## 문제 해결

### 문제 1: 함수가 호출되지 않음

**원인:**
- System Prompt가 제대로 업데이트되지 않음
- 세션에 이전 프롬프트가 남아있음

**해결:**
1. 브라우저 콘솔에서 프롬프트 로그 확인
2. 새로운 세션 ID 사용 (페이지 새로고침)
3. System Prompt를 다시 선택

### 문제 2: API 호출 실패

**확인 사항:**
- 외부 API 서버가 실행 중인지 확인
- 네트워크 연결 확인
- API_BASE_URL이 올바른지 확인 (`src/tools.py`)

### 문제 3: 스트리밍이 작동하지 않음

**참고:**
- Function Calling은 `/api/chat` 엔드포인트에서만 지원됩니다
- 스트리밍(`/api/chat/stream`)은 Function Calling을 지원하지 않습니다
- 일반 응답으로 변경되었습니다

## 개발자 팁

### 프롬프트 디버깅

콘솔에서 다음 정보를 확인할 수 있습니다:
- 원본 System Prompt
- Function Calling 안내 포함 여부
- 최종 System Prompt (일부)
- 사용자 메시지
- Session ID
- API 응답 상태

### 새로운 함수 추가

새로운 API 함수를 추가하려면:
1. `src/tools.py`에 함수 정의 추가
2. `TOOLS` 리스트에 추가
3. 서버 재시작
4. 테스트

자세한 내용은 `docs/guides/ADDING_NEW_API_GUIDE.md`를 참조하세요.

## 참고 문서

- [API 호출 사용 가이드](./API_CALLING_USAGE_GUIDE.md)
- [새 API 추가 가이드](./ADDING_NEW_API_GUIDE.md)

