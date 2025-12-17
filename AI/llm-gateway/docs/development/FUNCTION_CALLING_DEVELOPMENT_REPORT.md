# Function Calling 기능 개발 리포트

## 개발 기간
2025년 11월 19일

## 개발 목표
LLM이 채팅을 통해 외부 API를 호출할 수 있도록 OpenAI Function Calling 기능 구현

## 주요 개발 내용

### 1. Function Calling 기능 구현

#### 1.1 외부 API 호출 함수 정의 (`src/tools.py`)
- **구현된 함수:**
  - `get_users_list`: 사용자 목록 조회 (페이지네이션, 역할 필터링 지원)
  - `get_user_profile`: 특정 사용자 프로필 조회
  - `get_user_relationships`: 사용자 관계 정보 조회

- **기술 스택:**
  - `httpx`: 비동기 HTTP 클라이언트
  - JSON Schema: OpenAI Function Calling 형식

- **API 베이스 URL:**
  - `http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com`

#### 1.2 채팅 API 엔드포인트 수정 (`src/main.py`)
- `/api/chat` 엔드포인트에 Function Calling 로직 통합
- 최대 5회 반복 호출 지원 (함수 체이닝)
- `tool_calls` 처리 및 함수 실행 로직 구현
- 함수 실행 결과를 메시지에 추가하여 LLM이 최종 응답 생성

#### 1.3 System Prompt 자동 감싸기
- 사용자가 선택한 System Prompt에 Function Calling 안내 자동 추가
- 서버와 클라이언트 양쪽에서 처리하여 이중 보호
- Function Calling 사용 규칙 명시

### 2. 테스트 인터페이스 개선 (`tests/user_testing/test_chat_interface.html`)

#### 2.1 API 엔드포인트 변경
- `/api/chat/stream` → `/api/chat` 변경 (Function Calling 지원)
- 스트리밍은 Function Calling과 호환되지 않으므로 일반 응답으로 변경

#### 2.2 프롬프트 엔지니어링 로깅
- 브라우저 콘솔에서 프롬프트 내용 확인 가능
- 원본 System Prompt, Function Calling 안내 포함 여부, 최종 System Prompt 등 로깅
- API 응답 상태 로깅

#### 2.3 System Prompt 자동 감싸기
- `wrapSystemPromptWithToolInstructions()` 함수 추가
- 클라이언트에서 System Prompt를 Function Calling 안내로 감싸기

### 3. 버그 수정

#### 3.1 API 응답 필드명 불일치 수정
- **문제:** 서버는 `response` 필드 반환, 프론트엔드는 `message` 필드 확인
- **해결:** 프론트엔드에서 `response` 또는 `message` 모두 확인하도록 수정

#### 3.2 tool_choice 에러 수정
- **문제:** `tool_choice`는 `tools`가 제공될 때만 사용 가능한데, 항상 전달하고 있었음
- **해결:** `TOOLS`가 비어있지 않을 때만 `tools`와 `tool_choice` 전달하도록 수정

#### 3.3 DB 저장 시 content None 처리
- **문제:** Function Calling 시 assistant 메시지의 `content`가 `None`일 수 있는데, DB의 `content` 컬럼은 NOT NULL 제약이 있음
- **해결:** `save_conversation_to_db` 함수에서 `content`가 `None`인 경우 처리
  - `tool_calls`가 있으면 JSON 문자열로 변환하여 저장
  - `tool_calls`도 없으면 빈 문자열로 저장

### 4. 문서화

#### 4.1 사용 가이드
- `docs/guides/API_CALLING_USAGE_GUIDE.md`: API 호출 사용 가이드
- `docs/guides/ADDING_NEW_API_GUIDE.md`: 새 API 추가 가이드
- `docs/guides/FUNCTION_CALLING_TEST_GUIDE.md`: 테스트 가이드

## 기술적 세부사항

### Function Calling 흐름
1. 사용자 메시지 수신
2. System Prompt에 Function Calling 안내 추가
3. OpenAI API 호출 (tools 전달)
4. LLM이 적절한 함수 선택
5. 함수 실행 (외부 API 호출)
6. 함수 결과를 메시지에 추가
7. LLM이 최종 응답 생성

### 보안 고려사항
- 외부 API 호출은 `httpx`를 사용하여 타임아웃 설정 (10초)
- 에러 처리 및 로깅 구현
- 함수 실행 결과는 JSON으로 직렬화하여 전달

## 테스트 시나리오

### 성공 케이스
1. ✅ 사용자 목록 조회: "사용자 목록을 보여줘"
2. ✅ 사용자 프로필 조회: "사용자 ID xxx의 프로필을 보여줘"
3. ✅ 사용자 관계 정보 조회: "사용자 ID xxx의 관계 정보를 알려줘"

### 에러 처리
- ✅ 외부 API 호출 실패 시 에러 메시지 반환
- ✅ 함수 파라미터 파싱 실패 시 기본값 사용
- ✅ DB 저장 실패 시 로깅만 하고 계속 진행

## 성능 개선
- 비동기 HTTP 클라이언트 사용 (`httpx`)
- 함수 실행 결과 캐싱 없음 (실시간 데이터 조회)
- 최대 반복 횟수 제한 (5회)으로 무한 루프 방지

## 향후 개선 사항
1. 더 많은 외부 API 함수 추가
2. 함수 실행 결과 캐싱 (선택적)
3. 스트리밍과 Function Calling 통합 (복잡도 고려 필요)
4. 함수 실행 권한 관리
5. 함수 실행 로그 및 모니터링 강화

## 변경된 파일 목록
- `src/tools.py`: Function Calling 함수 정의 및 구현
- `src/main.py`: Function Calling 로직 통합
- `src/database.py`: content None 처리 로직 추가
- `tests/user_testing/test_chat_interface.html`: 테스트 인터페이스 개선
- `requirements.txt`: httpx 추가
- `docs/guides/API_CALLING_USAGE_GUIDE.md`: 사용 가이드
- `docs/guides/ADDING_NEW_API_GUIDE.md`: API 추가 가이드
- `docs/guides/FUNCTION_CALLING_TEST_GUIDE.md`: 테스트 가이드

## 결론
OpenAI Function Calling 기능을 성공적으로 구현하여 LLM이 외부 API를 호출할 수 있게 되었습니다. 이를 통해 사용자는 자연어로 데이터를 조회하고, LLM이 자동으로 적절한 API를 호출하여 결과를 제공할 수 있습니다.

