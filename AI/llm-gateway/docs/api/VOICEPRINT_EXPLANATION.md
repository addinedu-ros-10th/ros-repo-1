# 음성 지문 저장 관리 설명

## "질문 오디오"란?

### 현재 구현에서의 "질문 오디오"

**질문 오디오**는 키워드("alfred")를 감지한 **후**에 사용자가 말한 **질문 내용의 오디오**입니다.

#### 예시 흐름:
```
1. 사용자: "alfred"라고 말함 (키워드 감지)
   ↓
2. 키워드 활성화 → 녹음 시작
   ↓
3. 사용자: "안녕하세요"라고 질문함
   ↓
4. 이 "안녕하세요" 오디오가 "질문 오디오"
   ↓
5. 현재 코드: 이 질문 오디오를 음성 지문으로 저장 ❌
```

#### 코드 위치:
```javascript
// test_alfred_voice.html:1015-1017
// 키워드 감지 후 질문을 말한 오디오
const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
// audioChunks에는 "안녕하세요" 오디오가 들어있음
registerVoiceprint(lastDetectedKeyword.stt_result, audioBlob);
```

### 문제점

- **저장되는 것**: 질문 오디오 ("안녕하세요")
- **저장되어야 할 것**: 키워드 오디오 ("alfred" 또는 "rarfredo")

---

## 음성 지문 저장 관리 예시

### 시나리오: "alfred"를 "rarfredo"로 발음하는 사용자

#### 1단계: 첫 번째 키워드 감지 및 등록

```
[사용자 행동]
사용자: "rarfredo"라고 발음 (실제로는 "alfred"를 말하려고 함)

[시스템 처리]
1. Web Speech API: "rarfredo"로 STT 인식
2. 클라이언트: /api/keyword/check 호출
   - stt_result: "rarfredo"
   - base_keyword: "alfred"
3. 서버: DB에 등록된 voiceprint 없음
   - base_keyword("alfred")와 유사도 계산
   - similarity = calculate_similarity("rarfredo", "alfred")
   - similarity >= 0.7 → activate: True
4. 클라이언트: 키워드 활성화
5. 사용자: "오늘 날씨는?"이라고 질문
6. 클라이언트: 음성 지문 등록
   - stt_keyword: "rarfredo" ✅ (키워드 STT 결과)
   - audio_data: "오늘 날씨는?" 오디오 ❌ (질문 오디오)
```

#### 2단계: DB에 저장된 데이터

```sql
INSERT INTO keyword_voiceprints (
    base_keyword,      -- "alfred"
    stt_keyword,       -- "rarfredo" ✅
    audio_data,        -- "오늘 날씨는?" 오디오 (Base64) ❌
    session_id,        -- "alfred_1234567890"
    is_active          -- true
);
```

#### 3단계: 두 번째 키워드 감지 (등록된 voiceprint 활용)

```
[사용자 행동]
사용자: 다시 "rarfredo"라고 발음

[시스템 처리]
1. Web Speech API: "rarfredo"로 STT 인식
2. 클라이언트: /api/keyword/check 호출
   - stt_result: "rarfredo"
   - base_keyword: "alfred"
3. 서버: DB에서 voiceprint 조회
   - SELECT * FROM keyword_voiceprints 
     WHERE base_keyword = 'alfred' AND is_active = true
   - 조회 결과: stt_keyword = "rarfredo"
4. 서버: 정확한 매칭 확인
   - vp.stt_keyword("rarfredo") == stt_result("rarfredo")
   - 매칭 성공! ✅
5. 서버: activate: True, voiceprint_id: 1 반환
6. 클라이언트: 키워드 활성화 (더 빠르고 정확함)
```

#### 4단계: 다른 발음으로 시도

```
[사용자 행동]
사용자: "alfred"라고 정확히 발음

[시스템 처리]
1. Web Speech API: "alfred"로 STT 인식
2. 클라이언트: /api/keyword/check 호출
   - stt_result: "alfred"
   - base_keyword: "alfred"
3. 서버: DB에서 voiceprint 조회
   - 조회 결과: stt_keyword = "rarfredo"
4. 서버: 정확한 매칭 실패
   - "alfred" != "rarfredo"
5. 서버: 유사도 매칭 시도
   - similarity = calculate_similarity("alfred", "rarfredo")
   - similarity >= 0.7 → activate: True ✅
6. 클라이언트: 키워드 활성화
7. 클라이언트: 새로운 음성 지문 등록
   - stt_keyword: "alfred" ✅
   - audio_data: 질문 오디오 ❌
```

#### 5단계: 최종 DB 상태

```sql
-- 등록된 음성 지문들
id | base_keyword | stt_keyword | session_id        | is_active
---|--------------|-------------|-------------------|----------
1  | alfred       | rarfredo    | alfred_1234567890 | true
2  | alfred       | alfred      | alfred_1234567890 | true
```

---

## 올바른 음성 지문 저장 흐름 (개선안)

### 개선된 로직

```
[사용자 행동]
사용자: "rarfredo"라고 발음

[시스템 처리]
1. Web Speech API: "rarfredo"로 STT 인식
2. 클라이언트: 키워드 감지 시점의 오디오 버퍼링 시작
3. 클라이언트: /api/keyword/check 호출
   - stt_result: "rarfredo"
   - base_keyword: "alfred"
4. 서버: 키워드 확인 및 활성화
5. 클라이언트: 키워드 감지 시점의 오디오 저장
   - stt_keyword: "rarfredo" ✅
   - audio_data: "rarfredo" 오디오 ✅ (키워드 오디오)
6. 클라이언트: 음성 지문 등록
```

### 개선된 DB 저장

```sql
INSERT INTO keyword_voiceprints (
    base_keyword,      -- "alfred"
    stt_keyword,       -- "rarfredo" ✅
    audio_data,        -- "rarfredo" 오디오 (Base64) ✅
    session_id,        -- "alfred_1234567890"
    is_active          -- true
);
```

---

## 요약

### 현재 구현의 문제
- ✅ `stt_keyword`: 키워드 STT 결과 저장 (올바름)
- ❌ `audio_data`: 질문 오디오 저장 (잘못됨)

### 올바른 구현
- ✅ `stt_keyword`: 키워드 STT 결과 저장
- ✅ `audio_data`: 키워드 오디오 저장

### 음성 지문 활용
- 텍스트 매칭: `stt_keyword`로 정확한/유사도 매칭 ✅
- 오디오 매칭: `audio_data`로 향후 음성 특징 비교 가능 (현재 미사용)

