# 음성 지문 등록 기능 테스트 가이드

## 개요
키워드 기능에 대한 사용자 음성 지문을 등록하는 기능을 테스트하는 방법을 안내합니다.

## 음성 지문 등록 방식

### 자동 등록 (현재 구현)
키워드 감지 후 첫 질문 시 **자동으로** 음성 지문이 등록됩니다.

### 수동 등록
API를 직접 호출하여 음성 지문을 등록할 수 있습니다.

---

## 테스트 방법

### 방법 1: 테스트 UI를 통한 자동 등록 테스트 (권장)

#### 테스트 절차
1. **서버 실행**
   ```bash
   cd AI/llm-gateway
   docker compose up -d
   # 또는
   python -m uvicorn src.main:app --reload
   ```

2. **테스트 UI 접속**
   - 브라우저에서 `http://localhost:8000/tests/test_alfred_voice.html` 접속

3. **음성 지문 등록 테스트**
   - "시작" 버튼 클릭
   - "alfred"라고 말하기 (키워드 감지)
   - **확인 사항**:
     - ✅ "유사도 XX%" 배지 표시
     - ✅ "등록된 음성 지문: 0개" 표시 (처음에는 0개)
   - 한국어로 질문하기 (예: "안녕하세요")
   - **확인 사항**:
     - ✅ "✅ 새로운 음성 지문이 등록되었습니다 (ID: X)" 메시지 표시
     - ✅ "등록된 음성 지문: 1개"로 자동 업데이트

4. **추가 테스트**
   - 다시 "alfred"라고 말하기
   - 다른 질문하기 (예: "오늘 날씨는?")
   - **확인 사항**:
     - ✅ 음성 지문이 추가로 등록되거나 업데이트됨
     - ✅ 개수가 증가하거나 업데이트 메시지 표시

#### 예상 결과
- 첫 번째 질문: "✅ 새로운 음성 지문이 등록되었습니다 (ID: 1)"
- 두 번째 질문 (같은 STT 결과): "🔄 음성 지문이 업데이트되었습니다 (ID: 1)"
- 두 번째 질문 (다른 STT 결과): "✅ 새로운 음성 지문이 등록되었습니다 (ID: 2)"

---

### 방법 2: API 테스트 스크립트 사용

#### 테스트 스크립트 실행
```bash
cd AI/llm-gateway
python tests/test_keyword_voiceprint_api.py
```

#### 예상 출력
```
============================================================
2. 음성 지문 등록 API 테스트
============================================================
✅ 신규 음성 지문 등록
   성공: True
   음성 지문 ID: 1
   신규 등록: True
   메시지: 새로운 음성 지문이 등록되었습니다

✅ 오타 키워드 음성 지문 등록
   성공: True
   음성 지문 ID: 2
   신규 등록: True
   메시지: 새로운 음성 지문이 등록되었습니다
```

---

### 방법 3: API 직접 호출 (cURL 또는 Postman)

#### 요청 예시
```bash
curl -X POST "http://localhost:8000/api/keyword/voiceprint/register" \
  -H "Content-Type: application/json" \
  -d '{
    "base_keyword": "alfred",
    "stt_keyword": "alfred",
    "audio_data": "BASE64_ENCODED_AUDIO_DATA",
    "session_id": "test_session_123"
  }'
```

#### 성공 응답
```json
{
  "success": true,
  "voiceprint_id": 1,
  "is_new": true,
  "message": "새로운 음성 지문이 등록되었습니다"
}
```

#### 실패 응답 (DB 미초기화)
```json
{
  "detail": "데이터베이스가 초기화되지 않았습니다"
}
```

---

### 방법 4: 등록된 음성 지문 확인

#### UI에서 확인
- 테스트 UI에서 "등록된 음성 지문: N개" 표시 확인

#### API로 조회
```bash
curl "http://localhost:8000/api/keyword/voiceprint?base_keyword=alfred"
```

#### 응답 예시
```json
{
  "success": true,
  "voiceprints": [
    {
      "id": 1,
      "base_keyword": "alfred",
      "stt_keyword": "alfred",
      "session_id": "test_session_123",
      "is_active": true,
      "created_at": "2024-11-06T06:47:00",
      "updated_at": "2024-11-06T06:47:00"
    }
  ],
  "count": 1
}
```

---

## 테스트 시나리오

### 시나리오 1: 첫 번째 음성 지문 등록
1. 테스트 UI 접속
2. "시작" 버튼 클릭
3. "alfred"라고 말하기
4. "안녕하세요"라고 질문하기
5. **예상 결과**: "✅ 새로운 음성 지문이 등록되었습니다 (ID: 1)"

### 시나리오 2: 동일 키워드 재등록 (업데이트)
1. 위 시나리오 완료 후
2. 다시 "alfred"라고 말하기
3. "안녕하세요"라고 동일하게 질문하기
4. **예상 결과**: "🔄 음성 지문이 업데이트되었습니다 (ID: 1)"

### 시나리오 3: 다른 키워드 등록
1. "alfred"라고 말하기
2. "오늘 날씨는?"이라고 질문하기
3. **예상 결과**: "✅ 새로운 음성 지문이 등록되었습니다 (ID: 2)"

### 시나리오 4: 오타 키워드 등록
1. "alfred"라고 말했는데 STT가 "rarpred"로 인식
2. 질문하기
3. **예상 결과**: 
   - 키워드 인식 성공 (유사도 기반)
   - "✅ 새로운 음성 지문이 등록되었습니다 (ID: X)"
   - stt_keyword: "rarpred"로 저장됨

---

## 문제 해결

### 문제: 음성 지문이 등록되지 않음

#### 확인 사항
1. **데이터베이스 초기화 확인**
   ```bash
   # 서버 로그 확인
   docker compose logs llm-gateway | grep -i database
   ```

2. **브라우저 콘솔 확인**
   - F12 → Console 탭
   - 에러 메시지 확인

3. **서버 로그 확인**
   ```bash
   docker compose logs llm-gateway | tail -50
   ```

#### 해결 방법
- DB가 초기화되지 않았다면 서버 재시작
- API 호출 실패 시 네트워크 연결 확인
- 브라우저 콘솔의 에러 메시지 확인

### 문제: 등록 메시지가 표시되지 않음

#### 확인 사항
1. **UI 요소 확인**
   - `voiceprintStatus` div가 존재하는지 확인
   - CSS가 제대로 로드되었는지 확인

2. **JavaScript 콘솔 확인**
   - `registerVoiceprint` 함수가 호출되는지 확인
   - API 응답이 정상인지 확인

---

## 음성 지문 등록 로직 상세

### 자동 등록 조건
```javascript
if (lastDetectedKeyword) {
    // voiceprint_id가 null이거나, 새로운 STT 결과면 등록
    if (lastDetectedKeyword.voiceprint_id === null || 
        lastDetectedKeyword.stt_result !== data.user_text) {
        // 질문 오디오를 음성 지문으로 등록
        registerVoiceprint(lastDetectedKeyword.stt_result, audioBlob);
    }
}
```

### 등록되는 데이터
- `base_keyword`: "alfred" (기준 키워드)
- `stt_keyword`: STT 결과 (예: "alfred", "rarpred" 등)
- `audio_data`: Base64 인코딩된 오디오 데이터
- `session_id`: 현재 세션 ID

---

## 추가 정보

### 관련 API 엔드포인트
- `POST /api/keyword/voiceprint/register`: 음성 지문 등록
- `GET /api/keyword/voiceprint`: 음성 지문 조회
- `POST /api/keyword/check`: 키워드 확인 (등록된 voiceprint와 매칭)

### 관련 파일
- `tests/user_testing/test_alfred_voice.html`: 테스트 UI
- `tests/test_keyword_voiceprint_api.py`: API 테스트 스크립트
- `src/main.py`: API 엔드포인트 구현

