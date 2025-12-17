# 키워드 음성 지문 기능 전면 분석 리포트

## 📋 목차
1. [문제 요약](#문제-요약)
2. [데이터베이스 분석](#데이터베이스-분석)
3. [서버 코드 분석](#서버-코드-분석)
4. [클라이언트 코드 분석](#클라이언트-코드-분석)
5. [핵심 문제점](#핵심-문제점)
6. [해결 방안](#해결-방안)

---

## 문제 요약

### 발견된 문제들
1. **voiceprint 20개 제한 문제**
   - `test_alfred_voice.html`과 `test_voiceprint_management.html`에서 항상 20개만 표시
   - 새로 등록해도 20개로 유지됨

2. **키워드 매칭 실패**
   - 등록된 음성 지문을 기준으로 키워드 발화 인식이 안 됨
   - 음성 인터페이스 활성화가 안 됨

3. **세션/ID 필터링 불일치**
   - 등록 시에는 `session_id`로 구분
   - 조회/매칭 시에는 `session_id` 필터링이 없거나 불일치

---

## 데이터베이스 분석

### 테이블 구조
```sql
CREATE TABLE keyword_voiceprints (
    id SERIAL PRIMARY KEY,
    base_keyword VARCHAR(255) NOT NULL,      -- 기준 키워드 (예: "alfred")
    stt_keyword VARCHAR(255) NOT NULL,        -- STT 결과 키워드 (예: "my friend")
    audio_data TEXT,                          -- 음성 지문 오디오 (Base64)
    session_id VARCHAR(255),                  -- 세션 ID (nullable)
    user_id VARCHAR(255),                     -- 사용자 ID (nullable)
    is_active BOOLEAN NOT NULL DEFAULT TRUE, -- 활성화 여부
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
)
```

### 인덱스
- `idx_base_keyword`: base_keyword 인덱스
- `idx_session_id`: session_id 인덱스
- `idx_user_id`: user_id 인덱스
- `idx_base_stt_keyword`: (base_keyword, stt_keyword) 복합 인덱스

### 실제 데이터 현황
- **전체 voiceprint 개수**: 20개 (확인됨)
- **활성화된 voiceprint**: 20개 (is_active=True)
- **base_keyword별 분포**: 확인 필요

---

## 서버 코드 분석

### 1. 음성 지문 등록 API (`/api/keyword/voiceprint/register`)

**위치**: `src/main.py:1296-1363`

**현재 로직**:
```python
# 기존 등록 확인
existing = session.query(KeywordVoiceprint)\
    .filter_by(base_keyword=request.base_keyword)\
    .filter_by(stt_keyword=request.stt_keyword)\
    .filter_by(session_id=request.session_id)\  # ⚠️ 문제: session_id 필터링
    .first()
```

**문제점**:
- `session_id`를 필터링 조건에 포함
- 같은 `base_keyword`와 `stt_keyword`라도 `session_id`가 다르면 새로 등록됨
- 이로 인해 같은 키워드가 여러 세션에 중복 등록될 수 있음

**의도된 동작**:
- 음성 지문은 `base_keyword`와 `stt_keyword` 조합으로 고유해야 함
- `session_id`는 메타데이터일 뿐, 중복 체크 조건이 아님

### 2. 키워드 체크 API (`/api/keyword/check`)

**위치**: `src/main.py:1190-1293`

**현재 로직**:
```python
# base_keyword 기준으로 등록된 모든 keyword 조회
voiceprints = session.query(KeywordVoiceprint)\
    .filter_by(base_keyword=request.base_keyword)\
    .filter_by(is_active=True)\
    .all()  # ⚠️ session_id 필터링 없음
```

**문제점**:
- 등록 시에는 `session_id`로 구분하지만, 체크 시에는 모든 세션의 voiceprint를 확인
- 이로 인해 다른 세션에서 등록한 voiceprint도 매칭될 수 있음
- 하지만 의도된 동작일 수도 있음 (모든 사용자가 등록한 키워드를 사용 가능)

**매칭 로직**:
1. 정확한 매칭: `stt_keyword`와 `stt_result`가 정확히 일치
2. Fuzzy matching: 유사도 70% 이상
3. base_keyword 자체와도 비교

### 3. 음성 지문 조회 API (`/api/keyword/voiceprint`)

**위치**: `src/main.py:1366-1428`

**현재 로직**:
```python
query = session.query(KeywordVoiceprint).filter_by(is_active=True)

if base_keyword:
    query = query.filter_by(base_keyword=base_keyword)
if session_id:
    query = query.filter_by(session_id=session_id)  # 선택적 필터
```

**문제점**:
- `session_id`는 선택적 필터
- 클라이언트에서 `session_id`를 전달하지 않으면 모든 세션의 voiceprint를 조회
- 하지만 등록 시에는 `session_id`로 구분하므로 불일치

---

## 클라이언트 코드 분석

### 1. test_alfred_voice.html

**음성 지문 조회** (`loadVoiceprints`):
```javascript
const response = await fetch(`${API_BASE_URL}/api/keyword/voiceprint?base_keyword=${selectedKeyword}`);
// ⚠️ session_id를 전달하지 않음
```

**키워드 체크** (`checkKeywordWithServer`):
```javascript
body: JSON.stringify({
    stt_result: sttResult,
    base_keyword: KEYWORD,
    session_id: sessionId  // ✅ session_id 전달
})
```

**문제점**:
- 조회 시에는 `session_id`를 전달하지 않아 모든 세션의 voiceprint를 조회
- 체크 시에는 `session_id`를 전달하지만, 서버에서 무시됨

### 2. test_voiceprint_management.html

**음성 지문 조회** (`loadVoiceprints`):
```javascript
let url = `${API_BASE_URL}/api/keyword/voiceprint`;
if (baseKeyword) {
    url += `?base_keyword=${encodeURIComponent(baseKeyword)}`;
}
// ⚠️ session_id를 전달하지 않음
```

**음성 지문 등록** (`registerVoiceprint`):
```javascript
body: JSON.stringify({
    base_keyword: baseKeyword,
    stt_keyword: sttKeyword,
    audio_data: base64Audio,
    session_id: sessionId  // ✅ session_id 전달
})
```

**문제점**:
- 등록 시에는 `session_id`를 전달
- 조회 시에는 `session_id`를 전달하지 않음
- 이로 인해 등록한 voiceprint가 조회되지 않을 수 있음

---

## 핵심 문제점

### 1. session_id 필터링 불일치

**문제**:
- 등록 시: `session_id`를 필터링 조건에 포함하여 중복 체크
- 조회 시: `session_id`를 전달하지 않아 모든 세션의 voiceprint 조회
- 체크 시: `session_id`를 전달하지만 서버에서 무시

**영향**:
- 같은 키워드가 여러 세션에 중복 등록됨
- 조회 시 모든 세션의 voiceprint가 표시되어 혼란
- 체크 시 다른 세션의 voiceprint도 매칭될 수 있음

### 2. 음성 지문 등록 로직 문제

**현재 로직**:
```python
existing = session.query(KeywordVoiceprint)\
    .filter_by(base_keyword=request.base_keyword)\
    .filter_by(stt_keyword=request.stt_keyword)\
    .filter_by(session_id=request.session_id)\  # ⚠️ 문제
    .first()
```

**문제점**:
- `session_id`를 중복 체크 조건에 포함
- 같은 키워드라도 세션마다 별도로 등록됨
- 이로 인해 voiceprint 개수가 불필요하게 증가

**올바른 로직**:
```python
existing = session.query(KeywordVoiceprint)\
    .filter_by(base_keyword=request.base_keyword)\
    .filter_by(stt_keyword=request.stt_keyword)\
    .first()  # session_id 제외
```

### 3. 키워드 매칭 실패 원인

**가능한 원인**:
1. 등록된 voiceprint가 다른 세션에 있어서 매칭되지 않음
2. `session_id` 필터링으로 인해 등록이 실패했을 수 있음
3. 클라이언트에서 전달한 `base_keyword`와 등록 시 사용한 `base_keyword`가 다름
4. STT 결과와 등록된 `stt_keyword`가 정확히 일치하지 않음

### 4. 20개 제한 문제

**원인 분석**:
- 실제로 DB에 20개만 있는 것으로 확인됨
- 새로 등록해도 20개로 유지되는 이유:
  1. 등록이 실패했거나
  2. 같은 조건으로 업데이트되어 개수가 증가하지 않거나
  3. `session_id` 필터링으로 인해 기존 레코드가 업데이트됨

---

## 해결 방안

### 1. 음성 지문 등록 로직 수정

**변경사항**:
- `session_id`를 중복 체크 조건에서 제외
- `base_keyword`와 `stt_keyword` 조합으로만 중복 체크
- `session_id`는 메타데이터로만 사용

**수정 코드**:
```python
# 기존 등록 확인 (session_id 제외)
existing = session.query(KeywordVoiceprint)\
    .filter_by(base_keyword=request.base_keyword)\
    .filter_by(stt_keyword=request.stt_keyword)\
    .first()  # session_id 필터링 제거

if existing:
    # 기존 등록 업데이트
    existing.audio_data = request.audio_data
    existing.updated_at = datetime.utcnow()
    existing.is_active = True
    # session_id는 업데이트하지 않음 (원래 등록한 세션 유지)
    if request.user_id:
        existing.user_id = request.user_id
```

### 2. 키워드 체크 로직 개선

**현재 로직 유지** (모든 세션의 voiceprint 확인):
- 의도된 동작일 수 있음 (모든 사용자가 등록한 키워드를 사용 가능)
- 하지만 필요시 `session_id` 필터링 옵션 추가 가능

**옵션 1: 모든 세션의 voiceprint 확인 (현재)**
```python
voiceprints = session.query(KeywordVoiceprint)\
    .filter_by(base_keyword=request.base_keyword)\
    .filter_by(is_active=True)\
    .all()
```

**옵션 2: 특정 세션의 voiceprint만 확인**
```python
query = session.query(KeywordVoiceprint)\
    .filter_by(base_keyword=request.base_keyword)\
    .filter_by(is_active=True)

if request.session_id:
    query = query.filter_by(session_id=request.session_id)

voiceprints = query.all()
```

### 3. 클라이언트 코드 개선

**test_alfred_voice.html**:
- `loadVoiceprints`에서 `session_id` 전달 옵션 추가
- 필요시 현재 세션의 voiceprint만 조회

**test_voiceprint_management.html**:
- `loadVoiceprints`에서 `session_id` 전달 옵션 추가
- 등록한 voiceprint가 조회되는지 확인

### 4. 디버깅 로그 추가

**서버 로그**:
- voiceprint 등록/조회/체크 시 상세 로그
- `session_id`, `base_keyword`, `stt_keyword` 정보 포함

**클라이언트 로그**:
- voiceprint 조회/등록/체크 시 상세 로그
- 매칭 성공/실패 원인 표시

---

## 권장 사항

### 1. 음성 지문 등록 정책 결정

**옵션 A: 전역 공유 (권장)**
- `base_keyword`와 `stt_keyword` 조합으로만 중복 체크
- 모든 세션에서 등록된 키워드를 사용 가능
- `session_id`는 메타데이터로만 사용

**옵션 B: 세션별 분리**
- `session_id`를 중복 체크 조건에 포함
- 각 세션마다 별도로 등록
- 다른 세션의 voiceprint는 사용 불가

### 2. 키워드 체크 정책 결정

**옵션 A: 모든 세션의 voiceprint 확인 (현재)**
- 모든 사용자가 등록한 키워드를 사용 가능
- 더 나은 사용자 경험

**옵션 B: 현재 세션의 voiceprint만 확인**
- 자신이 등록한 키워드만 사용 가능
- 더 안전하지만 사용자 경험 저하

### 3. 즉시 수정 사항

1. ✅ 음성 지문 등록 시 `session_id` 필터링 제거
2. ✅ 키워드 체크 로직 검토 및 개선
3. ✅ 클라이언트에서 `session_id` 전달 일관성 확보
4. ✅ 디버깅 로그 추가

---

## 결론

**핵심 문제**:
1. `session_id` 필터링 불일치로 인한 중복 등록 및 조회 문제
2. 음성 지문 등록 로직의 `session_id` 필터링 문제
3. 키워드 매칭 실패 원인 불명확

**해결 방향**:
1. 음성 지문 등록 시 `session_id` 필터링 제거
2. 키워드 체크 로직 개선
3. 클라이언트 코드 일관성 확보
4. 디버깅 로그 추가

**예상 효과**:
- voiceprint 중복 등록 문제 해결
- 키워드 매칭 정상화
- 디버깅 용이성 향상

