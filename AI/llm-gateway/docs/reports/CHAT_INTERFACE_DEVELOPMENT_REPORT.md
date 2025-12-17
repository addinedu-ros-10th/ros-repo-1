# 채팅 인터페이스 및 System Prompt 관리 기능 개발 리포트

**작성일**: 2025-11-19  
**개발 기간**: 2025-11-19  
**버전**: 1.0.0

---

## 📋 개발 개요

채팅 기반 대화 인터페이스와 System Prompt 관리 기능을 개발하여, 사용자가 다양한 톤과 매너로 AI와 대화할 수 있는 기능을 제공합니다.

---

## 🎯 주요 개발 내용

### 1. 채팅 인터페이스 개발 (ChatGPT 스타일)

#### 1.1 UI/UX 구현
- **다크 테마 적용**: ChatGPT와 유사한 다크 테마 디자인
- **메시지 스타일링**: 사용자/AI 메시지 구분 및 아바타 표시
- **실시간 스트리밍**: 스트리밍 응답 표시 기능
- **자동 스크롤**: 새 메시지 자동 스크롤
- **반응형 디자인**: 다양한 화면 크기 지원

#### 1.2 기능 구현
- 텍스트 메시지 입력 및 전송
- 대화 히스토리 표시 및 관리
- 실시간 스트리밍 응답 처리
- 세션별 대화 히스토리 관리

**파일**: `tests/user_testing/test_chat_interface.html`

---

### 2. System Prompt 관리 기능

#### 2.1 데이터베이스 설계
- **`system_prompts` 테이블**: System Prompt 저장
  - `id`: 프롬프트 ID (Primary Key)
  - `name`: 프롬프트 이름
  - `content`: 프롬프트 내용
  - `description`: 프롬프트 설명 (선택사항)
  - `is_default`: 기본 프롬프트 여부 (여러 개 선택 가능)
  - `created_at`, `updated_at`: 생성/수정 시간

- **`system_prompt_usage` 테이블**: 마지막 사용 프롬프트 추적
  - `id`: 사용 기록 ID (Primary Key)
  - `user_id`: 사용자 ID (향후 확장용)
  - `session_id`: 세션 ID
  - `system_prompt_id`: 사용한 System Prompt ID
  - `created_at`, `updated_at`: 생성/수정 시간

**파일**: `src/database.py`

#### 2.2 API 엔드포인트 구현
- `GET /api/system-prompts`: System Prompt 목록 조회
- `GET /api/system-prompts/{id}`: 특정 System Prompt 조회
- `POST /api/system-prompts`: System Prompt 생성
- `PUT /api/system-prompts/{id}`: System Prompt 수정
- `DELETE /api/system-prompts/{id}`: System Prompt 삭제
- `GET /api/system-prompts/last-used/{session_id}`: 마지막 사용 프롬프트 조회
- `POST /api/system-prompts/usage`: System Prompt 사용 기록 저장
- `PUT /api/chat/update-system-prompt`: 기존 세션의 System Prompt 업데이트

**파일**: `src/main.py`

#### 2.3 System Prompt 관리 UI
- 프롬프트 목록 표시
- 프롬프트 작성/편집 폼
- 프롬프트 삭제 기능
- 프롬프트 선택 드롭다운
- 마지막 사용 프롬프트 자동 선택

**파일**: `tests/user_testing/test_chat_interface.html`

---

### 3. 음성 인터페이스 통합

#### 3.1 새로운 음성 인터페이스
- 키워드 인식 기능 제거
- 체크박스로 음성 인터페이스 토글
- 토글 활성화 시 바로 음성 입력 사용 가능
- 음성 녹음 및 전송 기능
- 음성 응답 재생 기능

**파일**: `tests/user_testing/test_chat_interface.html`

---

### 4. 세션 관리 개선

#### 4.1 기존 세션 업데이트 기능
- System Prompt 변경 시 기존 세션의 system 메시지 업데이트
- Redis 세션 업데이트
- DB 세션 업데이트
- Fallback store 업데이트

#### 4.2 마지막 사용 프롬프트 추적
- DB에 사용 기록 저장
- 페이지 로드 시 마지막 사용 프롬프트 자동 선택
- localStorage와 DB 동기화

---

### 5. 포트 변경

#### 5.1 Docker Compose 포트 변경
- **llm-gateway**: `8000:8000` → `8001:8000` (외부:8001, 내부:8000)
- **redis**: `6379:6379` → `16379:6379` (외부:16379, 내부:6379)

**파일**: `docker-compose.yml`

#### 5.2 테스트 파일 포트 업데이트
다음 파일들의 `localhost:8000`을 `localhost:8001`로 변경:
- `tests/user_testing/test_ui_ux_improvements.html`
- `tests/user_testing/test_alfred_voice.html`
- `tests/user_testing/test_voice.html`
- `tests/user_testing/test_voiceprint_management.html`
- `tests/user_testing/test_websocket.html`
- `tests/user_testing/test_websocket.py`
- `tests/user_testing/test_ui_ux_improvements.js`
- `tests/test_keyword_voiceprint_api.py`

---

### 6. 정적 파일 마운트 경로 수정

#### 6.1 문제 해결
- **문제**: `/tests`에 `tests/user_testing` 디렉토리 마운트로 인해 `/tests/user_testing/test_chat_interface.html` 접근 시 404 발생
- **해결**: `/tests/user_testing`에 `tests/user_testing` 디렉토리 마운트로 변경

**파일**: `src/main.py`

---

## 📁 변경된 파일 목록

### 데이터베이스
- `src/database.py`
  - `SystemPrompt` 모델 추가
  - `SystemPromptUsage` 모델 추가
  - 테이블 생성 SQL 추가

### API
- `src/main.py`
  - System Prompt CRUD API 엔드포인트 추가
  - 세션 System Prompt 업데이트 API 추가
  - 정적 파일 마운트 경로 수정

### 프론트엔드
- `tests/user_testing/test_chat_interface.html` (신규)
  - 채팅 인터페이스 UI
  - System Prompt 관리 UI
  - 음성 인터페이스 통합

### 설정 파일
- `docker-compose.yml`
  - 포트 변경 (8000→8001, 6379→16379)

### 테스트 파일
- `tests/user_testing/test_ui_ux_improvements.html`
- `tests/user_testing/test_alfred_voice.html`
- `tests/user_testing/test_voice.html`
- `tests/user_testing/test_voiceprint_management.html`
- `tests/user_testing/test_websocket.html`
- `tests/user_testing/test_websocket.py`
- `tests/user_testing/test_ui_ux_improvements.js`
- `tests/test_keyword_voiceprint_api.py`

### 문서
- `docs/development/CHAT_INTERFACE_WITH_SYSTEM_PROMPT_PLAN.md` (신규)
- `docs/development/PORT_CHANGE_VERIFICATION_PLAN.md` (신규)
- `docs/reports/CHAT_INTERFACE_DEVELOPMENT_REPORT.md` (본 문서)

---

## 🔧 기술 스택

### 백엔드
- **FastAPI**: 웹 프레임워크
- **PostgreSQL**: System Prompt 저장
- **Redis**: 세션 관리
- **SQLAlchemy**: ORM

### 프론트엔드
- **HTML5/CSS3**: UI 구현
- **JavaScript (Vanilla)**: 기능 구현
- **WebSocket API**: 실시간 통신
- **MediaRecorder API**: 음성 녹음

---

## 📊 주요 기능 상세

### 1. 채팅 인터페이스
- ✅ 텍스트 메시지 입력 및 전송
- ✅ 실시간 스트리밍 응답 표시
- ✅ 대화 히스토리 표시
- ✅ 세션별 히스토리 관리

### 2. System Prompt 관리
- ✅ 프롬프트 작성/편집/삭제
- ✅ 프롬프트 목록 조회
- ✅ 기본 프롬프트 설정 (여러 개 가능)
- ✅ 프롬프트 선택 드롭다운
- ✅ 마지막 사용 프롬프트 자동 선택

### 3. 음성 인터페이스
- ✅ 체크박스 토글
- ✅ 음성 녹음 및 전송
- ✅ 음성 응답 재생
- ✅ 키워드 인식 제거 (바로 사용 가능)

### 4. 세션 관리
- ✅ System Prompt 변경 시 기존 세션 업데이트
- ✅ 마지막 사용 프롬프트 DB 저장
- ✅ 세션별 히스토리 관리

---

## 🎨 UI/UX 특징

### 디자인
- **다크 테마**: ChatGPT 스타일의 다크 테마
- **깔끔한 레이아웃**: 메시지 중심의 간결한 디자인
- **반응형**: 다양한 화면 크기 지원

### 사용자 경험
- **직관적인 인터페이스**: 쉬운 사용법
- **실시간 피드백**: 스트리밍 응답으로 즉각적인 피드백
- **자동 저장**: 마지막 사용 프롬프트 자동 저장 및 선택

---

## 🔍 테스트 및 검증

### 테스트 항목
- ✅ 채팅 메시지 전송 및 응답
- ✅ System Prompt 생성/수정/삭제
- ✅ System Prompt 선택 및 적용
- ✅ 음성 인터페이스 토글
- ✅ 음성 입력 및 출력
- ✅ 세션 업데이트 기능
- ✅ 마지막 사용 프롬프트 저장 및 로드

### 접근 URL
- **채팅 인터페이스**: `http://localhost:8001/tests/user_testing/test_chat_interface.html`
- **API 문서**: `http://localhost:8001/docs`
- **Health Check**: `http://localhost:8001/`

---

## 📝 사용 방법

### 1. System Prompt 관리
1. 채팅 인터페이스에서 "프롬프트 관리" 버튼 클릭
2. "새 프롬프트 작성" 버튼으로 새 프롬프트 생성
3. 프롬프트 목록에서 "편집" 또는 "삭제" 버튼으로 관리
4. 드롭다운에서 프롬프트 선택

### 2. 채팅 사용
1. System Prompt 선택 (선택사항)
2. 메시지 입력 후 전송
3. AI 응답 확인

### 3. 음성 인터페이스 사용
1. "음성 인터페이스 사용" 체크박스 활성화
2. "🎤 음성 입력" 버튼 클릭
3. 말하기
4. AI 음성 응답 자동 재생

---

## 🚀 향후 개선 사항

### 기능 개선
- [ ] 프롬프트 카테고리 분류
- [ ] 프롬프트 템플릿 제공
- [ ] 프롬프트 공유 기능
- [ ] 대화 내보내기/가져오기
- [ ] 대화 검색 기능

### 성능 개선
- [ ] 프롬프트 목록 캐싱
- [ ] 대화 히스토리 페이지네이션
- [ ] 스트리밍 응답 최적화

### UI/UX 개선
- [ ] 다크/라이트 테마 전환
- [ ] 폰트 크기 조절
- [ ] 키보드 단축키 지원

---

## 📚 관련 문서

- [개발 계획서](./CHAT_INTERFACE_WITH_SYSTEM_PROMPT_PLAN.md)
- [포트 변경 검증 계획](./PORT_CHANGE_VERIFICATION_PLAN.md)
- [API 문서](http://localhost:8001/docs)

---

## ✅ 완료 체크리스트

- [x] 채팅 인터페이스 UI 개발
- [x] System Prompt 데이터베이스 설계
- [x] System Prompt CRUD API 구현
- [x] System Prompt 관리 UI 구현
- [x] 음성 인터페이스 통합
- [x] 세션 업데이트 기능 구현
- [x] 마지막 사용 프롬프트 저장 기능
- [x] 포트 변경 (8000→8001, 6379→16379)
- [x] 정적 파일 마운트 경로 수정
- [x] 테스트 파일 포트 업데이트
- [x] 문서 작성

---

**개발 완료일**: 2025-11-19  
**담당자**: Development Team  
**버전**: 1.0.0

