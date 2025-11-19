# 키워드 기능 동작 문제 진단 리포트

## 문제 상황

### 사용자 보고
- **STT 인식 결과**: "my friend"
- **등록된 키워드**: ID: 6 | STT 키워드: "my friend" | 오디오: 있음 | 생성일: 2025. 11. 6. 오후 12:33:28
- **문제**: 키워드가 등록되어 있지만 키워드 기능이 동작하지 않음

### 기대 동작
1. 사용자가 "my friend"라고 발음
2. STT가 "my friend"로 인식
3. 등록된 키워드와 매칭
4. 음성 인터페이스 활성화

---

## 진단 결과

### 1. 키워드 기능 구조

#### 서버 측 (`/api/keyword/check`)
```python
@app.post("/api/keyword/check")
async def check_keyword(request: KeywordCheckRequest):
    # base_keyword 기준으로 등록된 voiceprint 조회
    voiceprints = session.query(KeywordVoiceprint)\
        .filter_by(base_keyword=request.base_keyword)\
        .filter_by(is_active=True)\
        .all()
    
    # stt_result와 stt_keyword 비교
    for vp in voiceprints:
        if vp.stt_keyword.lower() == stt_result_lower:
            return {"is_keyword": True, "activate": True, ...}
```

**요구사항**:
- `base_keyword`: 기준 키워드 (예: "alfred")
- `stt_result`: 현재 STT 인식 결과 (예: "my friend")
- DB에서 `base_keyword`로 등록된 voiceprint 조회
- `stt_keyword`와 `stt_result` 비교

#### 클라이언트 측
- **`test_alfred_voice.html`**: ✅ 키워드 체크 로직 있음
- **`test_chat_interface.html`**: ❌ 키워드 체크 로직 없음

---

### 2. 문제 원인

#### `test_chat_interface.html`의 문제점

**현재 동작**:
```javascript
async function sendVoiceMessage(audioBlob) {
    // 1. FormData 생성
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');
    
    // 2. 바로 /api/voice/process 호출
    const response = await fetch(`${API_BASE}/api/voice/process`, {
        method: 'POST',
        body: formData
    });
    
    // 3. 응답 처리
    const data = await response.json();
    // ...
}
```

**문제**:
- ❌ STT 결과를 받기 전에 키워드 체크를 하지 않음
- ❌ `/api/keyword/check`를 호출하지 않음
- ❌ 등록된 키워드와 매칭하지 않음

#### `test_alfred_voice.html`의 올바른 동작

```javascript
// 1. STT 결과 받기
recognition.onresult = (event) => {
    const sttResult = event.results[0][0].transcript;
    
    // 2. 키워드 체크
    checkKeywordWithServer(sttResult);
};

// 3. 키워드 체크 API 호출
async function checkKeywordWithServer(sttResult) {
    const response = await fetch(`${API_BASE_URL}/api/keyword/check`, {
        method: 'POST',
        body: JSON.stringify({
            stt_result: sttResult,
            base_keyword: KEYWORD,  // 예: "alfred"
            session_id: sessionId
        })
    });
    
    const data = await response.json();
    if (data.is_keyword && data.activate) {
        // 키워드 활성화
        activateKeyword(data.matched_keyword, sttResult);
    }
}
```

---

### 3. 추가 확인 사항

#### `base_keyword` 확인 필요

**질문**: "my friend"의 `base_keyword`가 무엇인가?

**가능한 시나리오**:
1. `base_keyword = "my friend"`인 경우
   - `/api/keyword/check` 호출 시 `base_keyword: "my friend"` 전달
   - DB에서 `base_keyword = "my friend"`인 voiceprint 조회
   - `stt_keyword = "my friend"`와 `stt_result = "my friend"` 비교
   - ✅ 정확한 매칭 성공

2. `base_keyword = "alfred"`인 경우 (또는 다른 값)
   - `/api/keyword/check` 호출 시 `base_keyword: "alfred"` 전달
   - DB에서 `base_keyword = "alfred"`인 voiceprint 조회
   - `stt_keyword = "my friend"`와 `stt_result = "my friend"` 비교
   - ✅ 정확한 매칭 성공 (단, base_keyword가 올바르게 전달되어야 함)

**확인 방법**:
```sql
SELECT id, base_keyword, stt_keyword, is_active 
FROM keyword_voiceprints 
WHERE id = 6;
```

---

## 해결 방안

### 방안 1: `test_chat_interface.html`에 키워드 체크 로직 추가 (권장)

#### 구현 단계

1. **STT 결과를 먼저 받기**
   ```javascript
   // 옵션 1: Web Speech API 사용 (클라이언트 측 STT)
   const recognition = new webkitSpeechRecognition();
   recognition.onresult = (event) => {
       const sttResult = event.results[0][0].transcript;
       checkKeywordAndProcess(sttResult, audioBlob);
   };
   
   // 옵션 2: 서버 측 STT 후 키워드 체크
   // /api/stt로 먼저 STT 수행
   // 그 다음 /api/keyword/check 호출
   // 마지막으로 /api/voice/process 호출
   ```

2. **키워드 체크 API 호출**
   ```javascript
   async function checkKeywordAndProcess(sttResult, audioBlob) {
       // 1. 키워드 체크
       const keywordResponse = await fetch(`${API_BASE}/api/keyword/check`, {
           method: 'POST',
           headers: {'Content-Type': 'application/json'},
           body: JSON.stringify({
               stt_result: sttResult,
               base_keyword: "my friend",  // 또는 설정 가능한 키워드
               session_id: currentSessionId
           })
       });
       
       const keywordData = await keywordResponse.json();
       
       // 2. 키워드가 매칭되면 음성 인터페이스 활성화
       if (keywordData.is_keyword && keywordData.activate) {
           console.log('✅ 키워드 감지:', keywordData.matched_keyword);
           // 음성 처리 진행
           await processVoiceMessage(audioBlob);
       } else {
           console.log('❌ 키워드 미매칭');
           // 키워드가 아니면 처리하지 않음 (또는 일반 응답)
       }
   }
   ```

3. **키워드 선택 UI 추가**
   - 등록된 키워드 목록을 불러와서 선택 가능하게
   - 선택한 키워드를 `base_keyword`로 사용

### 방안 2: 서버 측에서 자동 키워드 체크

#### `/api/voice/process` 수정

```python
@app.post("/api/voice/process")
async def process_voice(...):
    # 1. STT 수행
    user_text = transcription.text
    
    # 2. 키워드 체크 (자동)
    # 등록된 모든 키워드와 비교
    with db_manager.get_session() as session:
        voiceprints = session.query(KeywordVoiceprint)\
            .filter_by(is_active=True)\
            .all()
        
        for vp in voiceprints:
            if vp.stt_keyword.lower() == user_text.lower().strip():
                # 키워드 매칭 성공
                # 음성 인터페이스 활성화 플래그 반환
                return {
                    "success": True,
                    "is_keyword": True,
                    "activate": True,
                    "matched_keyword": vp.stt_keyword,
                    "message": "키워드가 감지되었습니다. 질문을 말하세요."
                }
    
    # 3. 키워드가 아니면 일반 채팅 처리
    # ... 기존 로직
```

**장점**: 클라이언트 수정 최소화
**단점**: 모든 키워드와 비교해야 함 (성능 이슈 가능)

---

## 권장 해결 방안

### 단기 해결책
1. **`test_chat_interface.html`에 키워드 체크 로직 추가**
   - STT 결과를 받은 후 `/api/keyword/check` 호출
   - 키워드 매칭 시에만 음성 처리 진행

2. **키워드 선택 UI 추가**
   - 등록된 키워드 목록 표시
   - 사용자가 키워드 선택 가능

### 장기 해결책
1. **키워드 자동 감지 기능**
   - 서버 측에서 자동으로 키워드 체크
   - 클라이언트는 키워드 선택 없이 사용 가능

2. **키워드 관리 개선**
   - 키워드별 활성화/비활성화
   - 키워드 우선순위 설정

---

## 테스트 방법

### 1. 키워드 체크 API 직접 테스트

```bash
curl -X POST 'http://localhost:8001/api/keyword/check' \
  -H 'Content-Type: application/json' \
  -d '{
    "stt_result": "my friend",
    "base_keyword": "my friend",
    "session_id": "test123"
  }'
```

**예상 응답**:
```json
{
  "is_keyword": true,
  "activate": true,
  "matched_keyword": "my friend",
  "similarity": 1.0,
  "voiceprint_id": 6
}
```

### 2. DB 확인

```sql
-- ID: 6의 base_keyword 확인
SELECT id, base_keyword, stt_keyword, is_active 
FROM keyword_voiceprints 
WHERE id = 6;

-- base_keyword로 등록된 모든 키워드 확인
SELECT id, base_keyword, stt_keyword, is_active 
FROM keyword_voiceprints 
WHERE base_keyword = 'my friend' AND is_active = true;
```

---

## 결론

**현재 문제**: `test_chat_interface.html`에서 키워드 체크를 하지 않아 등록된 키워드와 매칭하지 않음

**해결 방법**: 
1. STT 결과를 받은 후 `/api/keyword/check` 호출 추가
2. 키워드 매칭 시에만 음성 처리 진행
3. 키워드 선택 UI 추가 (선택사항)

**다음 단계**: `test_chat_interface.html`에 키워드 체크 로직 구현

