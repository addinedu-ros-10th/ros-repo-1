# 개발 현황 리포트

**작성일:** 2025-11-20  
**프로젝트:** 맞춤형 이동식 대화 기능 개선 및 TOOLS 통합 관리

---

## 📋 주요 개발 내용

### 1. TOOLS 통합 관리 시스템 구축

#### 문제점
- TOOLS 관리가 각 엔드포인트마다 분산되어 있었음
- `/api/chat`, `/api/chat/stream`, `/api/voice/process`에서 각각 다른 방식으로 TOOLS 전달
- TOOLS 업데이트 시 모든 엔드포인트를 수정해야 했음
- System Prompt도 각 엔드포인트마다 다르게 구성

#### 해결 방법
- **`system_prompt_builder.py` 모듈 생성**
  - `build_system_prompt()`: 통합 System Prompt 생성
  - `get_tools_for_api()`: 통합 TOOLS 목록 반환
  - 모든 엔드포인트에서 동일한 System Prompt 사용
  - TOOLS 목록 자동 포함

- **모든 LLM API 엔드포인트 통합**
  - `/api/chat`: 통합 System Prompt 및 TOOLS 사용
  - `/api/chat/stream`: 통합 System Prompt 및 TOOLS 사용
  - `/api/voice/process`: 통합 System Prompt 및 TOOLS 사용

#### 효과
- TOOLS 업데이트 시 모든 엔드포인트에 자동 반영
- System Prompt 일관성 보장
- 유지보수성 향상

---

### 2. 상세 로깅 시스템 추가

#### 구현 내용
- **TOOLS 호출 로깅 (🔧 이모지로 구분)**
  - `🔧 TOOL CALL START`: 함수 호출 시작 (함수명, 인자)
  - `🔧 TOOL CALL SUCCESS`: 함수 호출 성공
  - `🔧 TOOL CALL FAILED`: 함수 호출 실패
  - `🔧 TOOL CALLS DETECTED`: LLM이 함수 호출 감지

- **TOOLS 정보 로깅**
  - TOOLS 개수 및 함수 목록 로깅
  - 각 엔드포인트별 TOOLS 사용 현황

#### 효과
- 함수 호출 여부를 쉽게 확인 가능
- 디버깅 시간 단축
- 문제 발생 시 빠른 원인 파악

---

### 3. 맞춤형 이동식 대화 기능 개선

#### 문제점
1. **세션 중복 생성 오류 (UniqueViolation)**
   - 같은 `session_id`로 재시도 시 기존 세션을 확인하지 않고 새로 생성
   - `duplicate key value violates unique constraint` 발생

2. **YOLO API 타임아웃**
   - 30초 타임아웃으로 응답 없음
   - 맞춤형 이동식 대화는 러닝 타임이 길어 타임아웃 발생 가능

3. **에러 발생 시 세션 상태 미업데이트**
   - 타임아웃/HTTP 에러/연결 오류 발생 시 DB 상태가 업데이트되지 않음
   - 재시도 시 이전 상태가 남아 문제 발생

4. **블로킹 문제**
   - `await`로 YOLO API 응답을 기다려 사용자 응답 지연
   - YOLO API는 "terminated 되기 전까지 계속 호출 상태가 지속"됨

#### 해결 방법

**1. 세션 관리 개선**
- 세션 생성 전 기존 세션 확인
- 기존 세션이 있으면 업데이트, 없으면 생성
- 재시작 시 상태 초기화 (`ended_at`, `yolo_started_at` 등)
- YOLO 상태도 업데이트 또는 생성

**2. YOLO API 호출 개선 (Fire-and-Forget)**
- `asyncio.create_task()`로 백그라운드 태스크 실행
- API 호출 시작 후 즉시 반환 (비블로킹)
- 타임아웃 60초 → 120초로 증가
- 타임아웃 발생 시에도 YOLO 실행 중일 수 있으므로 `'yolo_running'` 상태로 설정

**3. 에러 처리 개선**
- 모든 에러 케이스에서 세션 상태를 `'error'`로 업데이트
- 타임아웃, HTTP 에러, 연결 오류 모두 처리
- 에러 정보를 `meta_data`에 저장
- 사용자 친화적인 에러 메시지 제공

**4. 함수 description 개선**
- `user_id` 추출 방법 명확화
- '맞춤형 이동식 대화를 하고 싶어' 패턴 추가
- 사용자가 말한 이름을 그대로 사용하도록 안내

#### 효과
- 재시도 시 세션 중복 생성 오류 해결
- 사용자 응답 즉시 반환 (비블로킹)
- YOLO API 타임아웃 발생률 감소
- 에러 발생 시 세션 상태가 정확히 업데이트되어 재시도 가능

---

### 4. SQLAlchemy 예약어 충돌 해결

#### 문제점
- `metadata`는 SQLAlchemy Declarative API의 예약어
- `DeepLearningFunctionStatus` 클래스에서 `metadata` 컬럼 사용 시 에러 발생

#### 해결 방법
- `metadata` → `meta_data`로 컬럼명 변경
- 모든 참조 업데이트 (database.py, tools.py)
- 테이블 생성 SQL도 업데이트

---

### 5. 문서화

#### 추가된 문서
- **`CUSTOMIZED_MOBILE_CONVERSATION_ISSUES.md`**
  - 문제 해결 가이드
  - 음성 인터페이스 사용 가이드
  - 문제 해결 체크리스트
  - 향후 개선 방안

---

## 📊 통계

### 변경된 파일
- `src/system_prompt_builder.py` (신규)
- `src/main.py` (통합 System Prompt 및 TOOLS 사용)
- `src/tools.py` (세션 관리, 에러 처리, fire-and-forget 개선)
- `src/database.py` (meta_data 변경)
- `docs/troubleshooting/CUSTOMIZED_MOBILE_CONVERSATION_ISSUES.md` (신규)

### 커밋 수
- 총 10개 이상의 커밋

---

## 🔧 기술 스택

- **비동기 처리**: `asyncio.create_task()`, `httpx.AsyncClient`
- **데이터베이스**: PostgreSQL, SQLAlchemy ORM
- **로깅**: Python logging with emoji markers
- **API 통합**: FastAPI, OpenAI Function Calling

---

## ✅ 완료된 작업

1. ✅ TOOLS 통합 관리 시스템 구축
2. ✅ System Prompt 통합 관리
3. ✅ 상세 로깅 시스템 추가
4. ✅ 맞춤형 이동식 대화 세션 관리 개선
5. ✅ YOLO API fire-and-forget 방식 구현
6. ✅ 에러 처리 개선
7. ✅ SQLAlchemy 예약어 충돌 해결
8. ✅ 문서화

---

## 🚀 향후 개선 방안

### 단기
1. **비동기 처리 개선**
   - YOLO 상태를 주기적으로 확인하는 API 추가
   - WebSocket을 통한 실시간 상태 업데이트

2. **재시도 로직**
   - 타임아웃 발생 시 자동 재시도
   - 최대 재시도 횟수 제한

3. **user_id 매핑**
   - 사용자 이름 → 실제 user_id 매핑 테이블
   - 세션 정보에서 user_id 자동 추출

### 장기
1. **상태 모니터링 대시보드**
   - YOLO 실행 상태 실시간 모니터링
   - 상태 변경 시 알림 기능

2. **성능 최적화**
   - 캐싱 전략 도입
   - 데이터베이스 쿼리 최적화

---

## 📝 주요 커밋

1. `6b72f45`: YOLO API 호출을 fire-and-forget 방식으로 변경
2. `20787b1`: 맞춤형 이동식 대화 세션 관리 및 에러 처리 개선
3. `16bebd2`: TOOLS 통합 관리 및 상세 로깅 추가
4. `c032ee8`: `/api/voice/process`에서도 통합 System Prompt 사용
5. `2c4e513`: start_customized_mobile_conversation 함수 description 개선
6. `ba6e222`: 테이블 생성 SQL에서도 metadata를 meta_data로 변경
7. `32aaffc`: SQLAlchemy 예약어 충돌 해결 - metadata를 meta_data로 변경

---

## 🎯 성과

1. **개발 생산성 향상**
   - TOOLS 업데이트 시 모든 엔드포인트에 자동 반영
   - 유지보수 시간 단축

2. **사용자 경험 개선**
   - 즉시 응답 반환 (비블로킹)
   - 명확한 에러 메시지 제공

3. **안정성 향상**
   - 세션 중복 생성 오류 해결
   - 에러 처리 개선
   - 상태 관리 정확도 향상

4. **디버깅 효율성 향상**
   - 상세 로깅으로 문제 파악 시간 단축
   - 이모지 마커로 로그 가독성 향상

---

**작성자:** AI Assistant  
**검토 필요:** 코드 리뷰 및 테스트
