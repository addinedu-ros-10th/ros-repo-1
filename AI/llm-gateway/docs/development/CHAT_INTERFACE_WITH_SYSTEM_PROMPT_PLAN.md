# 채팅 인터페이스 및 System Prompt 관리 기능 개발 계획

**작성일**: 2025-11-18  
**요청사항**: 채팅 기반 대화 UI + System Prompt 관리 기능

---

## 📋 요청사항 이해 확인

### 요청사항 정리

#### 1. 채팅 기반 인터페이스 화면 생성
- **목적**: 텍스트 기반 대화 인터페이스 제공
- **기능**:
  - 채팅 메시지 입력 및 전송
  - 대화 히스토리 표시
  - 실시간 응답 표시 (스트리밍 지원)

#### 2. System Prompt 관리/사용 기능
- **System Prompt 작성/편집/저장**
  - System Prompt 작성 UI
  - System Prompt 편집 기능
  - System Prompt 저장 기능
- **DB 테이블 생성**
  - System Prompt를 저장할 테이블 생성
  - 프롬프트 ID, 이름, 내용, 생성/수정 시간 등 저장
- **대화 시작 시 System Prompt 선택**
  - 등록된 System Prompt 목록 표시
  - 드롭다운 또는 리스트에서 선택
  - 선택한 System Prompt로 대화 시작
- **마지막 사용 프롬프트 기본 선택**
  - localStorage 또는 DB에 마지막 사용 프롬프트 저장
  - 페이지 로드 시 마지막 사용 프롬프트 자동 선택

#### 3. 음성 인터페이스 토글 기능
- **체크박스 선택**
  - 체크박스로 음성 인터페이스 활성화/비활성화
  - 체크 시: 음성 입력/출력 기능 활성화
  - 체크 해제 시: 텍스트 채팅만 사용

### 이해한 내용 ✅

1. ✅ **채팅 UI**: 텍스트 기반 대화 인터페이스 (메시지 입력, 히스토리 표시)
2. ✅ **System Prompt 관리**: 작성/편집/저장 기능 + DB 테이블
3. ✅ **System Prompt 선택**: 대화 시작 시 선택 가능 + 마지막 사용 프롬프트 기본 선택
4. ✅ **음성 인터페이스 토글**: 체크박스로 음성 기능 활성화/비활성화

---

## 🔍 현재 코드 상태 분석

### 기존 기능

#### 1. Chat API
- ✅ `POST /api/chat`: 텍스트 채팅 API
- ✅ `POST /api/chat/stream`: 스트리밍 채팅 API
- ✅ `system_prompt` 파라미터 지원 (TextChatRequest)
- ✅ 세션별 대화 히스토리 관리 (Redis)

#### 2. 데이터베이스
- ✅ `conversation_sessions` 테이블에 `system_prompt` 컬럼 존재
- ❌ System Prompt 전용 관리 테이블 없음

#### 3. 기존 테스트 UI
- ✅ `test_websocket.html`: WebSocket 채팅 테스트 UI (참고 가능)
- ✅ `test_voice.html`: 음성 인터페이스 테스트 UI (참고 가능)

### 필요한 작업

1. **DB 테이블 생성**: `system_prompts` 테이블
2. **API 엔드포인트 추가**: System Prompt CRUD API
3. **채팅 UI 생성**: 새로운 HTML 파일
4. **System Prompt 관리 UI**: 프롬프트 작성/편집/저장
5. **음성 인터페이스 통합**: 체크박스 토글 기능

---

## 🎯 개발 계획

### Phase 1: 데이터베이스 및 API 개발

#### 1.1 System Prompt 테이블 생성

**테이블명**: `system_prompts`

**스키마 설계**:
```sql
CREATE TABLE system_prompts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,              -- 프롬프트 이름
    content TEXT NOT NULL,                    -- 프롬프트 내용
    description TEXT,                         -- 프롬프트 설명 (선택사항)
    is_default BOOLEAN DEFAULT FALSE,         -- 기본 프롬프트 여부
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_system_prompts_name ON system_prompts(name);
CREATE INDEX idx_system_prompts_created ON system_prompts(created_at);
```

**마이그레이션 파일**: `src/database.py`에 모델 추가

#### 1.2 System Prompt API 엔드포인트 구현

**엔드포인트**:
- `GET /api/system-prompts`: System Prompt 목록 조회
- `GET /api/system-prompts/{id}`: 특정 System Prompt 조회
- `POST /api/system-prompts`: System Prompt 생성
- `PUT /api/system-prompts/{id}`: System Prompt 수정
- `DELETE /api/system-prompts/{id}`: System Prompt 삭제

**Pydantic 모델**:
```python
class SystemPromptCreate(BaseModel):
    name: str
    content: str
    description: Optional[str] = None
    is_default: bool = False

class SystemPromptUpdate(BaseModel):
    name: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None

class SystemPromptResponse(BaseModel):
    id: int
    name: str
    content: str
    description: Optional[str]
    is_default: bool
    created_at: datetime
    updated_at: datetime
```

#### 1.3 마지막 사용 프롬프트 추적

**방법 1: localStorage 사용 (클라이언트)**
- 브라우저 localStorage에 마지막 사용 프롬프트 ID 저장
- 페이지 로드 시 localStorage에서 읽어서 기본 선택

**방법 2: DB에 사용 이력 저장 (서버)**
- `system_prompt_usage` 테이블 생성 (선택사항)
- 사용자별/세션별 마지막 사용 프롬프트 추적

**제안**: localStorage 사용 (간단하고 빠름)

---

### Phase 2: 채팅 UI 개발

#### 2.1 새로운 HTML 파일 생성

**파일명**: `tests/user_testing/test_chat_interface.html`

**주요 구성 요소**:
1. **상단 영역**
   - System Prompt 선택 드롭다운
   - System Prompt 관리 버튼 (모달 열기)
   - 음성 인터페이스 토글 체크박스

2. **채팅 영역**
   - 대화 히스토리 표시 영역
   - 메시지 입력 영역
   - 전송 버튼

3. **음성 인터페이스 영역** (체크박스 활성화 시)
   - 음성 입력 버튼
   - 음성 출력 재생

#### 2.2 채팅 기능 구현

**기능**:
- 텍스트 메시지 입력 및 전송
- `/api/chat` 또는 `/api/chat/stream` API 호출
- 대화 히스토리 표시 (사용자/어시스턴트 메시지 구분)
- 스트리밍 응답 표시 (선택사항)

**JavaScript 함수**:
```javascript
// 메시지 전송
async function sendMessage(message, systemPromptId) {
    // API 호출
    // 응답 표시
    // 히스토리 업데이트
}

// System Prompt 적용
function applySystemPrompt(promptId) {
    // 선택한 프롬프트 저장 (localStorage)
    // 대화 시작
}
```

#### 2.3 System Prompt 선택 UI

**구현**:
- 드롭다운에 등록된 System Prompt 목록 표시
- 선택 시 해당 프롬프트로 대화 시작
- 마지막 사용 프롬프트 기본 선택

---

### Phase 3: System Prompt 관리 UI

#### 3.1 System Prompt 관리 모달

**기능**:
- System Prompt 목록 표시
- 새 프롬프트 작성
- 기존 프롬프트 편집
- 프롬프트 삭제
- 프롬프트 미리보기

**UI 구성**:
```
┌─────────────────────────────────────┐
│ System Prompt 관리                  │
├─────────────────────────────────────┤
│ [새 프롬프트 작성]                   │
│                                     │
│ 프롬프트 목록:                      │
│ ┌─────────────────────────────────┐│
│ │ 📝 친절한 어시스턴트 [편집][삭제]││
│ │ 📝 기술 지원 전문가 [편집][삭제]││
│ │ 📝 번역 전문가 [편집][삭제]     ││
│ └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

#### 3.2 프롬프트 작성/편집 폼

**필드**:
- 이름 (name): 프롬프트 이름
- 내용 (content): 프롬프트 내용 (텍스트 영역)
- 설명 (description): 프롬프트 설명 (선택사항)
- 기본 프롬프트 여부 (is_default): 체크박스

---

### Phase 4: 음성 인터페이스 통합

#### 4.1 음성 인터페이스 토글

**구현**:
- 체크박스: "음성 인터페이스 사용"
- 체크 시: 음성 입력/출력 UI 표시
- 체크 해제 시: 텍스트 채팅만 사용

**기능**:
- 음성 입력: STT API 호출
- 음성 출력: TTS API 호출
- 통합 음성 처리: `/api/voice/process` API 사용

---

## 📝 상세 구현 계획

### 1. 데이터베이스 모델 추가

**파일**: `src/database.py`

```python
class SystemPrompt(Base):
    """System Prompt 테이블"""
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_system_prompts_name', 'name'),
        Index('idx_system_prompts_created', 'created_at'),
    )
```

### 2. API 엔드포인트 구현

**파일**: `src/main.py`

```python
# System Prompt 엔드포인트
@app.get("/api/system-prompts")
async def list_system_prompts():
    """System Prompt 목록 조회"""
    pass

@app.get("/api/system-prompts/{prompt_id}")
async def get_system_prompt(prompt_id: int):
    """특정 System Prompt 조회"""
    pass

@app.post("/api/system-prompts")
async def create_system_prompt(request: SystemPromptCreate):
    """System Prompt 생성"""
    pass

@app.put("/api/system-prompts/{prompt_id}")
async def update_system_prompt(prompt_id: int, request: SystemPromptUpdate):
    """System Prompt 수정"""
    pass

@app.delete("/api/system-prompts/{prompt_id}")
async def delete_system_prompt(prompt_id: int):
    """System Prompt 삭제"""
    pass
```

### 3. 채팅 UI HTML 구조

**파일**: `tests/user_testing/test_chat_interface.html`

```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>채팅 인터페이스</title>
    <style>
        /* 채팅 UI 스타일 */
    </style>
</head>
<body>
    <div class="container">
        <!-- 상단: System Prompt 선택 및 설정 -->
        <div class="header">
            <select id="systemPromptSelect">
                <option value="">기본 프롬프트</option>
            </select>
            <button onclick="openPromptManager()">프롬프트 관리</button>
            <label>
                <input type="checkbox" id="voiceInterfaceToggle">
                음성 인터페이스 사용
            </label>
        </div>
        
        <!-- 채팅 영역 -->
        <div class="chat-area">
            <div class="messages" id="messages">
                <!-- 대화 히스토리 -->
            </div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="메시지를 입력하세요...">
                <button onclick="sendMessage()">전송</button>
            </div>
        </div>
        
        <!-- 음성 인터페이스 영역 (체크박스 활성화 시 표시) -->
        <div class="voice-area" id="voiceArea" style="display: none;">
            <button onclick="startVoiceInput()">🎤 음성 입력</button>
            <div id="voiceStatus">대기 중...</div>
        </div>
    </div>
    
    <!-- System Prompt 관리 모달 -->
    <div class="modal" id="promptManagerModal">
        <!-- 모달 내용 -->
    </div>
    
    <script>
        // JavaScript 코드
    </script>
</body>
</html>
```

---

## ✅ 구현 체크리스트

### Phase 1: 데이터베이스 및 API
- [ ] `system_prompts` 테이블 생성 (마이그레이션)
- [ ] `SystemPrompt` 모델 추가
- [ ] System Prompt CRUD API 구현
- [ ] API 테스트

### Phase 2: 채팅 UI
- [ ] `test_chat_interface.html` 파일 생성
- [ ] 채팅 메시지 입력/전송 기능
- [ ] 대화 히스토리 표시
- [ ] System Prompt 선택 드롭다운
- [ ] 마지막 사용 프롬프트 기본 선택 (localStorage)

### Phase 3: System Prompt 관리
- [ ] System Prompt 관리 모달 UI
- [ ] 프롬프트 목록 조회 및 표시
- [ ] 프롬프트 작성 폼
- [ ] 프롬프트 편집 폼
- [ ] 프롬프트 삭제 기능

### Phase 4: 음성 인터페이스 통합
- [ ] 음성 인터페이스 토글 체크박스
- [ ] 체크박스 활성화 시 음성 UI 표시
- [ ] 음성 입력 기능 (STT)
- [ ] 음성 출력 기능 (TTS)
- [ ] 통합 음성 처리

---

## 🎨 UI 디자인 제안

### 레이아웃 구조

```
┌─────────────────────────────────────────────┐
│ [System Prompt 선택 ▼] [관리] [✓ 음성 사용] │
├─────────────────────────────────────────────┤
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 대화 히스토리 영역                    │   │
│  │                                     │   │
│  │ 👤 사용자: 안녕하세요                │   │
│  │ 🤖 AI: 안녕하세요! 무엇을 도와드릴까요?│   │
│  │                                     │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  [메시지 입력...] [전송]                    │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 🎤 음성 입력 [녹음 중지]              │   │
│  │ 🔊 음성 출력 [재생]                  │   │
│  └─────────────────────────────────────┘   │
│                                             │
└─────────────────────────────────────────────┘
```

### System Prompt 관리 모달

```
┌─────────────────────────────────────────────┐
│ System Prompt 관리                    [X]   │
├─────────────────────────────────────────────┤
│ [새 프롬프트 작성]                           │
│                                             │
│ 프롬프트 목록:                               │
│ ┌───────────────────────────────────────┐ │
│ │ 📝 친절한 어시스턴트                    │ │
│ │    당신은 친절한 한국어 AI 어시스턴트입니다│ │
│ │    [편집] [삭제] [선택]                │ │
│ ├───────────────────────────────────────┤ │
│ │ 📝 기술 지원 전문가                    │ │
│ │    당신은 기술 지원 전문가입니다...    │ │
│ │    [편집] [삭제] [선택]                │ │
│ └───────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## 🔄 사용자 워크플로우

### 시나리오 1: 기본 채팅

1. 페이지 로드
   - 마지막 사용 System Prompt 자동 선택 (localStorage)
   - 채팅 인터페이스 표시

2. 메시지 입력 및 전송
   - 텍스트 입력
   - 전송 버튼 클릭
   - AI 응답 표시

3. 대화 계속
   - 여러 메시지 주고받기
   - 대화 히스토리 유지

### 시나리오 2: System Prompt 변경

1. System Prompt 선택
   - 드롭다운에서 다른 프롬프트 선택
   - localStorage에 저장
   - 새 세션으로 대화 시작 (또는 기존 세션에 적용)

2. 대화 시작
   - 선택한 System Prompt로 대화 시작
   - AI 응답 톤/매너 변경 확인

### 시나리오 3: System Prompt 관리

1. 프롬프트 관리 모달 열기
   - "프롬프트 관리" 버튼 클릭

2. 새 프롬프트 작성
   - "새 프롬프트 작성" 버튼 클릭
   - 이름, 내용, 설명 입력
   - 저장

3. 프롬프트 편집
   - 목록에서 "편집" 버튼 클릭
   - 내용 수정
   - 저장

4. 프롬프트 삭제
   - 목록에서 "삭제" 버튼 클릭
   - 확인 후 삭제

### 시나리오 4: 음성 인터페이스 사용

1. 음성 인터페이스 활성화
   - "음성 인터페이스 사용" 체크박스 체크
   - 음성 입력/출력 UI 표시

2. 음성 대화
   - "🎤 음성 입력" 버튼 클릭
   - 말하기
   - AI 음성 응답 재생

3. 텍스트와 음성 혼합 사용
   - 텍스트 입력 또는 음성 입력 선택 가능
   - 음성 출력은 체크박스 상태에 따라 자동 재생

---

## 📊 예상 변경사항

### 새로 생성할 파일

1. **HTML 파일**
   - `tests/user_testing/test_chat_interface.html` (채팅 UI)

2. **데이터베이스 마이그레이션**
   - `src/database.py` (SystemPrompt 모델 추가)
   - 마이그레이션 스크립트 (선택사항)

3. **문서**
   - `docs/development/CHAT_INTERFACE_WITH_SYSTEM_PROMPT_PLAN.md` (본 문서)
   - `docs/guides/CHAT_INTERFACE_USAGE_GUIDE.md` (사용 가이드, 추후 작성)

### 수정할 파일

1. **API 파일**
   - `src/main.py` (System Prompt API 엔드포인트 추가)

2. **데이터베이스 파일**
   - `src/database.py` (SystemPrompt 모델 추가, 테이블 생성 로직)

---

## ⚠️ 주의사항

### 1. 세션 관리
- System Prompt 변경 시 기존 세션 처리 방법 결정 필요
  - 옵션 A: 새 세션 생성
  - 옵션 B: 기존 세션의 system 메시지 업데이트
  - **제안**: 새 세션 생성 (명확한 히스토리 관리)

### 2. 기본 프롬프트
- `is_default` 플래그로 기본 프롬프트 지정
- 여러 개의 기본 프롬프트가 있을 경우 처리 방법
  - **제안**: 하나만 기본으로 설정 가능하게 제한

### 3. 프롬프트 삭제 시
- 사용 중인 프롬프트 삭제 시 처리 방법
  - **제안**: 경고 메시지 표시 후 삭제

### 4. 음성 인터페이스 통합
- 기존 `test_alfred_voice.html`의 음성 기능 재사용 가능
- 코드 중복 최소화를 위한 공통 함수 모듈화 고려

---

## 📅 예상 작업 시간

### Phase 1: 데이터베이스 및 API (2시간)
- 테이블 생성 및 모델 추가: 30분
- API 엔드포인트 구현: 1시간
- API 테스트: 30분

### Phase 2: 채팅 UI (3시간)
- HTML 구조 및 스타일: 1시간
- 채팅 기능 구현: 1.5시간
- System Prompt 선택 기능: 30분

### Phase 3: System Prompt 관리 (2시간)
- 관리 모달 UI: 1시간
- CRUD 기능 구현: 1시간

### Phase 4: 음성 인터페이스 통합 (2시간)
- 토글 기능: 30분
- 음성 입력/출력 통합: 1.5시간

**총 예상 시간**: 약 9시간

---

## ✅ 요청사항 확인 질문

1. **채팅 UI 스타일**
   - 모던한 채팅 앱 스타일 (예: WhatsApp, Telegram)?
   - 심플한 메시지 리스트 스타일?
   - → **제안**: 모던한 채팅 앱 스타일

2. **System Prompt 변경 시 세션 처리**
   - System Prompt 변경 시 새 세션 생성할까요?
   - 기존 세션의 system 메시지를 업데이트할까요?
   - → **제안**: 새 세션 생성 (명확한 히스토리 관리)

3. **음성 인터페이스 통합 방식**
   - 기존 `test_alfred_voice.html`의 기능을 그대로 통합할까요?
   - 새로운 간소화된 음성 인터페이스를 만들까요?
   - → **제안**: 기존 기능 재사용 + 간소화

4. **마지막 사용 프롬프트 저장 위치**
   - localStorage만 사용할까요?
   - DB에도 저장할까요? (사용자별 추적)
   - → **제안**: localStorage (간단하고 빠름)

5. **기본 프롬프트 처리**
   - 여러 개의 기본 프롬프트를 허용할까요?
   - 하나만 기본으로 설정 가능하게 할까요?
   - → **제안**: 하나만 기본 설정 가능

---

## 🎯 개발 우선순위

### 높은 우선순위
1. ✅ System Prompt 테이블 생성
2. ✅ System Prompt CRUD API
3. ✅ 채팅 UI 기본 구조
4. ✅ System Prompt 선택 기능

### 중간 우선순위
5. ✅ System Prompt 관리 UI
6. ✅ 마지막 사용 프롬프트 기본 선택
7. ✅ 음성 인터페이스 토글

### 낮은 우선순위
8. ⚠️ 스트리밍 응답 표시 (선택사항)
9. ⚠️ 프롬프트 미리보기 기능 (선택사항)
10. ⚠️ 프롬프트 카테고리 분류 (선택사항)

---

**피드백 요청**

위 계획이 요청사항을 정확히 반영했는지 확인 부탁드립니다.
특히 다음 사항에 대한 피드백을 요청합니다:

1. 채팅 UI 스타일 선호도
2. System Prompt 변경 시 세션 처리 방식
3. 음성 인터페이스 통합 방식
4. 마지막 사용 프롬프트 저장 위치
5. 기본 프롬프트 처리 방식
6. 추가 요구사항

피드백 주시면 즉시 개발을 시작하겠습니다.


