# 맞춤형 이동식 대화 기능 문제 해결 가이드

## 문제점 분석

### 1. 세션 중복 생성 오류

**증상:**
```
duplicate key value violates unique constraint "ix_customized_mobile_conversation_sessions_session_id"
```

**원인:**
- 같은 `session_id`로 여러 번 함수를 호출할 때 기존 세션을 확인하지 않고 새로 생성하려고 함
- 세션이 이미 존재하는데 `INSERT`를 시도하여 UniqueViolation 발생

**해결:**
- 세션 생성 전에 기존 세션 확인
- 기존 세션이 있으면 업데이트, 없으면 생성
- 재시작 시 상태 초기화 (ended_at, yolo_started_at 등)

### 2. YOLO API 타임아웃

**증상:**
```
YOLO start timeout: session_id=session1
```

**원인:**
- YOLO API가 30초 내에 응답하지 않음
- 맞춤형 이동식 대화 기능이라서 러닝 타임이 김
- IOT 서버가 응답하지 않거나 네트워크 문제

**해결:**
- 타임아웃을 30초 → 60초로 증가
- 타임아웃 발생 시 세션 상태를 'error'로 업데이트
- 사용자에게 명확한 에러 메시지 제공

### 3. 에러 발생 시 세션 상태 미업데이트

**원인:**
- 타임아웃, HTTP 에러, 연결 오류 발생 시 DB 상태가 업데이트되지 않음
- 다음 시도 시 이전 상태가 남아있어 문제 발생

**해결:**
- 모든 에러 케이스에서 세션 상태를 'error'로 업데이트
- YOLO 상태도 함께 업데이트
- 에러 정보를 meta_data에 저장

## 음성 인터페이스 사용 가이드

### user_id 추출 방법

현재 구현에서는 사용자가 말한 이름을 `user_id`로 사용합니다.

**예시:**
- 사용자: "내 이름은 보리야" → `user_id = "보리"`
- 사용자: "서보리야" → `user_id = "서보리"`

**향후 개선 방안:**
1. 사용자 이름을 실제 user_id로 매핑하는 테이블 생성
2. 세션 정보에서 이전에 사용한 user_id 추출
3. 사용자 인증 정보에서 user_id 가져오기

### 사용 시나리오

1. **첫 번째 요청:**
   ```
   사용자: "맞춤형 이동식 대화를 하고 싶어"
   AI: "어르신 성함을 알려주실 수 있을까요?"
   사용자: "내 이름은 보리야"
   AI: start_customized_mobile_conversation(session_id="session1", user_id="보리")
   ```

2. **재시도:**
   ```
   사용자: "맞춤형 대화를 다시 시작해줘"
   AI: start_customized_mobile_conversation(session_id="session1", user_id="보리")
   → 기존 세션 업데이트 (중복 생성 오류 방지)
   ```

## 문제 해결 체크리스트

### YOLO API 타임아웃 발생 시

1. **IOT 서버 상태 확인**
   ```bash
   curl http://192.168.0.59:8000/send-signal_run_yolo
   ```

2. **네트워크 연결 확인**
   - llm-gateway에서 IOT 서버로의 네트워크 연결 확인
   - 방화벽 설정 확인

3. **로그 확인**
   - `🔧 TOOL CALL START` 로그 확인
   - 타임아웃 메시지 확인
   - 세션 상태가 'error'로 업데이트되었는지 확인

### 세션 중복 생성 오류 발생 시

1. **기존 세션 확인**
   ```sql
   SELECT * FROM customized_mobile_conversation_sessions 
   WHERE session_id = 'session1';
   ```

2. **세션 상태 확인**
   - `status`가 'error'인 경우 재시도 가능
   - `status`가 'ended'인 경우 새로 시작 가능

3. **세션 정리 (필요시)**
   ```sql
   DELETE FROM customized_mobile_conversation_sessions 
   WHERE session_id = 'session1';
   ```

## 개선 사항

### 완료된 개선

1. ✅ 세션 중복 생성 방지 (기존 세션 업데이트)
2. ✅ 타임아웃 증가 (30초 → 60초)
3. ✅ 에러 발생 시 세션 상태 업데이트
4. ✅ 사용자 친화적인 에러 메시지

### 향후 개선 방안

1. **비동기 처리 개선**
   - YOLO API 호출을 완전 비동기로 처리
   - 백그라운드에서 상태를 주기적으로 확인
   - WebSocket을 통한 실시간 상태 업데이트

2. **재시도 로직**
   - 타임아웃 발생 시 자동 재시도
   - 최대 재시도 횟수 제한
   - 재시도 간격 설정

3. **상태 모니터링**
   - YOLO 실행 상태를 주기적으로 확인하는 API 추가
   - 상태 변경 시 알림 기능

4. **user_id 매핑**
   - 사용자 이름 → 실제 user_id 매핑 테이블
   - 세션 정보에서 user_id 자동 추출

