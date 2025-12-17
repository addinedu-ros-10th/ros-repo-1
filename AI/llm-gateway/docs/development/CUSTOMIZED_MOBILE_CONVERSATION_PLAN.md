# 맞춤형 이동식 대화 기능 구현 계획

## 📋 요청 사항 정리

### 이해한 내용

#### 1. YOLO 객체 인식 및 추종 기능 API

**API 1: YOLO 객체 인식 프로그램 시작**
- Endpoint: `POST http://192.168.0.59:8000/send-signal_run_yolo`
- Response: `{"status": "test message: yolo terminated"}`
- 특이사항:
  - terminated 되기 전까지 계속 호출 상태가 지속됨
  - 맞춤형 이동식 대화 기능이라서 러닝 타임이 김
  - 비동기식 호출로 처리 필요
  - 상태를 지속적으로 체크하여 running 중인지 확인 필요
  - 'YOLO 객체 인식 프로그램 종료' API 호출 시 종료

**API 2: YOLO 객체 인식 프로그램 종료**
- Endpoint: `POST http://192.168.0.59:8000/send-signal_stop_yolo`
- Response: `{"status": "updated"}`
- 특이사항: 'YOLO 객체 인식 프로그램 시작' API 호출 종료 역할

**API 3: 추종 활성화 스위치**
- Endpoint: `POST http://192.168.0.59:8000/send-signal_tracking_switch`
- Response: 
  ```json
  {
    "status": "updated",
    "tracking_switch": "Tracking activated" // 또는 "Tracking deactivated"
  }
  ```
- 특이사항:
  - 추종 기능을 켜고 끄는 토글 스위치
  - 처음 호출 시 activate, 그 다음 호출 시 deactivate
  - response로 동작 여부 확인 가능

#### 2. 사용자 시나리오

**시나리오 흐름:**

1. **대화 기능 요청**
   - 사용자: "대화를 하고 싶어.", "맞춤 대화를 시작해줘." 등
   - AI: 확인 메시지 및 대화 시작 확인

2. **YOLO 시작**
   - 사용자: "그래", "응", "좋아." 등 대화 시작 응답
   - AI: YOLO 객체 인식 프로그램 시작 API 호출
   - AI: "네, 이제 맞춤 대화를 시작합니다."

3. **추종 활성화**
   - AI: "함께 걸으며 대화 할 까요?"
   - 사용자: "그래", "응", "좋아." 등 이동 시작 응답
   - AI: 추종 활성화 스위치 API 호출
   - AI: "네, 이제 맞춤 이동식 대화도 가능합니다."

4. **대화 진행**
   - 맞춤형 이동식 대화 진행

5. **대화 종료**
   - 사용자: "그래 즐거웠어. 이제 대화를 종료하자." 등 종료 의사
   - AI: 추종 비활성화 스위치 API 호출
   - AI: YOLO 객체 인식 프로그램 종료 API 호출
   - AI: "네, 맞춤형 대화를 종료하겠습니다."

#### 3. 데이터베이스 요구사항

**목적:**
- 심리 상담 세션 기반 준의료적 행위 기록
- 사용자(어르신)의 심리, 정서, 건강 상태 분석 및 관리
- 개인화된 대화 경험 제공
- 개인화된 어르신 관리
- 대화 기반 심리 상담 리포트 생성 (직원, 요양사, 사회복지사, 가족 등)

**필요한 테이블:**
1. **맞춤형 이동식 대화 세션 테이블**
   - 세션 ID, 사용자 ID, 시작/종료 시간
   - YOLO 시작/종료 시간
   - 추종 활성화/비활성화 시간
   - 세션 상태 (대기, 진행 중, 종료)

2. **대화 내용 테이블**
   - 세션 ID, 메시지 순서, 역할 (user/assistant)
   - 메시지 내용, 타임스탬프
   - 감정 분석 결과 (선택사항)

3. **심리 상담 분석 테이블**
   - 세션 ID, 분석 항목 (심리, 정서, 건강 상태)
   - 분석 결과, 점수/등급
   - 분석 일시

4. **리포트 테이블**
   - 리포트 ID, 세션 ID, 리포트 타입
   - 리포트 내용, 생성 일시
   - 공유 대상 (직원, 요양사, 사회복지사, 가족 등)

---

## 🎯 구현 계획

### Phase 1: API 함수 구현

#### 1.1 YOLO 객체 인식 프로그램 시작 함수
- 함수명: `start_yolo_detection`
- 비동기 처리
- 상태 체크 로직 (선택사항)
- GPT가 "맞춤 대화 시작" 요청 시 호출

#### 1.2 YOLO 객체 인식 프로그램 종료 함수
- 함수명: `stop_yolo_detection`
- GPT가 "대화 종료" 요청 시 호출

#### 1.3 추종 활성화 스위치 함수
- 함수명: `toggle_tracking`
- 토글 기능 (activate/deactivate)
- 현재 상태 확인 (response 기반)

### Phase 2: 데이터베이스 스키마 설계

#### 2.1 맞춤형 이동식 대화 세션 테이블
```sql
CREATE TABLE customized_mobile_conversation_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    yolo_started_at TIMESTAMP,
    yolo_ended_at TIMESTAMP,
    tracking_activated_at TIMESTAMP,
    tracking_deactivated_at TIMESTAMP,
    status VARCHAR(50) NOT NULL, -- 'waiting', 'yolo_starting', 'yolo_running', 'tracking_active', 'conversation_active', 'ending', 'ended'
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

#### 2.2 대화 내용 테이블
```sql
CREATE TABLE customized_mobile_conversation_messages (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    message_order INTEGER NOT NULL,
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant'
    content TEXT NOT NULL,
    emotion_analysis JSONB, -- 감정 분석 결과 (선택사항)
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES customized_mobile_conversation_sessions(session_id)
);
```

#### 2.3 심리 상담 분석 테이블
```sql
CREATE TABLE psychological_counseling_analysis (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(100) NOT NULL, -- 'psychological', 'emotional', 'health'
    analysis_result JSONB NOT NULL,
    score INTEGER, -- 0-100 점수
    grade VARCHAR(50), -- 'excellent', 'good', 'normal', 'concern', 'warning'
    analyzed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES customized_mobile_conversation_sessions(session_id)
);
```

#### 2.4 리포트 테이블
```sql
CREATE TABLE counseling_reports (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    report_type VARCHAR(100) NOT NULL, -- 'daily', 'weekly', 'monthly', 'session'
    report_content JSONB NOT NULL,
    shared_with JSONB, -- ['staff', 'caregiver', 'social_worker', 'family']
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255), -- 리포트 생성자
    FOREIGN KEY (session_id) REFERENCES customized_mobile_conversation_sessions(session_id)
);
```

### Phase 3: GPT Function Calling 통합

#### 3.1 함수 정의
- `start_customized_mobile_conversation`: 맞춤형 이동식 대화 시작
- `activate_tracking`: 추종 활성화
- `end_customized_mobile_conversation`: 맞춤형 이동식 대화 종료

#### 3.2 System Prompt 업데이트
- 맞춤형 이동식 대화 시나리오 안내
- 단계별 API 호출 가이드

### Phase 4: 데이터베이스 모델 및 API 구현

#### 4.1 데이터베이스 모델 클래스
- `CustomizedMobileConversationSession`
- `CustomizedMobileConversationMessage`
- `PsychologicalCounselingAnalysis`
- `CounselingReport`

#### 4.2 API 엔드포인트
- 세션 생성/조회/종료
- 메시지 저장/조회
- 분석 결과 저장/조회
- 리포트 생성/조회

---

## ✅ 확인 사항

### 요청 사항 확인

1. ✅ **YOLO API 3개**: 시작, 종료, 추종 스위치
2. ✅ **사용자 시나리오**: 5단계 흐름 (요청 → YOLO 시작 → 추종 활성화 → 대화 → 종료)
3. ✅ **비동기 처리**: YOLO 시작은 비동기로 처리
4. ✅ **DB 테이블**: 4개 테이블 (세션, 메시지, 분석, 리포트)
5. ✅ **심리 상담 목적**: 준의료적 행위 기록 및 분석
6. ✅ **리포트 기능**: 직원, 요양사, 사회복지사, 가족 등 공유

### 추가 고려 사항 (피드백 반영)

1. **YOLO 상태 체크**: 상태 체크 방안이 있다면 적용, 없으면 비동기 호출 후 종료 API 호출 시까지 대기
2. **상태 관리 DB**: 각 기능별(YOLO, 추종) 상태를 DB에 저장하여 관리
3. **자동 분석**: 대화 내용을 자동으로 분석하여 심리 상담 분석 테이블에 저장
4. **자동 리포트 생성**: 세션 종료 시 자동으로 리포트 생성
5. **에러 처리**: API 호출 실패 시 재시도 로직
6. **타임아웃**: YOLO 시작 후 일정 시간 내 종료되지 않으면 타임아웃 처리

---

## 🚀 구현 시작 여부

위 계획으로 구현을 진행할까요?

**예상 작업 시간**: 약 2-3시간
**영향 범위**: 
- `src/tools.py`: API 함수 추가
- `src/database.py`: DB 모델 추가
- `src/main.py`: API 엔드포인트 추가 (선택사항)

