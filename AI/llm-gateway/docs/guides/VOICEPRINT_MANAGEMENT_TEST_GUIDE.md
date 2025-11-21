# 음성 지문 관리 테스트 가이드

## 개요
음성 지문을 등록하고 관리할 수 있는 테스트 화면 사용 가이드입니다.

## 테스트 화면 접속

### URL
```
http://localhost:8000/tests/test_voiceprint_management.html
```

### 서버 실행
```bash
cd AI/llm-gateway
docker compose up -d
# 또는
python -m uvicorn src.main:app --reload
```

---

## 음성 지문 등록 테스트

### 시나리오: "alfred"를 "rarfredo"로 발음하는 사용자

#### 방법 1: 자동 등록 (녹음 + STT)

1. **기준 키워드 입력**
   - "기준 키워드" 필드에 `alfred` 입력 (또는 기본값 사용)

2. **키워드 녹음**
   - "🎤 키워드 녹음 시작" 버튼 클릭
   - 마이크 권한 허용
   - **"rarfredo"라고 말하기** (또는 원하는 발음)
   - "⏹️ 녹음 중지" 버튼 클릭

3. **STT 결과 확인**
   - "STT 결과 키워드" 필드에 자동으로 입력됨
   - Web Speech API로 인식된 결과
   - 필요시 수정 가능

4. **음성 지문 등록**
   - "💾 음성 지문 등록" 버튼 클릭
   - 등록 성공 메시지 확인

#### 방법 2: 수동 등록 (텍스트만)

1. **기준 키워드 입력**
   - "기준 키워드" 필드에 `alfred` 입력

2. **STT 결과 입력**
   - "STT 결과 키워드" 필드에 `rarfredo` 입력
   - 사용자가 실제로 발음한 키워드 입력

3. **음성 지문 등록**
   - "💾 음성 지문 등록" 버튼 클릭
   - 오디오 없이 텍스트만 저장됨

---

## 등록된 음성 지문 확인

### 목록 조회
- 페이지 로드 시 자동으로 목록 조회
- "🔄 목록 새로고침" 버튼으로 수동 조회
- "🔍 alfred만 조회" 버튼으로 필터링

### 표시 정보
- **ID**: 음성 지문 고유 ID
- **기준 키워드**: base_keyword (예: "alfred")
- **STT 키워드**: stt_keyword (예: "rarfredo")
- **세션 ID**: 등록 시 사용된 세션 ID
- **생성일**: 등록 일시
- **오디오 크기**: 저장된 오디오 데이터 크기

---

## 음성 지문 테스트

### 테스트 방법
1. 등록된 음성 지문 목록에서 "🧪 테스트" 버튼 클릭
2. 서버에서 키워드 확인 API 호출
3. 매칭 결과 확인:
   - ✅ 성공: 유사도 표시
   - ❌ 실패: 유사도 표시

### 테스트 예시

#### 시나리오 1: 정확한 매칭
```
등록된 음성 지문:
- base_keyword: "alfred"
- stt_keyword: "rarfredo"

테스트 입력: "rarfredo"
결과: ✅ 키워드 매칭 성공! 유사도: 100.0%
```

#### 시나리오 2: 유사도 매칭
```
등록된 음성 지문:
- base_keyword: "alfred"
- stt_keyword: "rarfredo"

테스트 입력: "alfred"
결과: ✅ 키워드 매칭 성공! 유사도: 71.4%
```

#### 시나리오 3: 매칭 실패
```
등록된 음성 지문:
- base_keyword: "alfred"
- stt_keyword: "rarfredo"

테스트 입력: "hello"
결과: ❌ 키워드 매칭 실패. 유사도: 0.0%
```

---

## 실제 사용 시나리오

### 시나리오: 사용자별 음성 지문 등록

#### 사용자 A: "alfred"를 "rarfredo"로 발음
1. 테스트 화면에서 음성 지문 등록
   - base_keyword: "alfred"
   - stt_keyword: "rarfredo"
   - 오디오: "rarfredo" 녹음

2. test_alfred_voice.html에서 테스트
   - "rarfredo"라고 말하기
   - ✅ 키워드 인식 성공 (등록된 voiceprint와 매칭)

#### 사용자 B: "alfred"를 "alfred"로 정확히 발음
1. 테스트 화면에서 음성 지문 등록
   - base_keyword: "alfred"
   - stt_keyword: "alfred"
   - 오디오: "alfred" 녹음

2. test_alfred_voice.html에서 테스트
   - "alfred"라고 말하기
   - ✅ 키워드 인식 성공

#### 사용자 C: "alfred"를 "alpred"로 발음
1. 테스트 화면에서 음성 지문 등록
   - base_keyword: "alfred"
   - stt_keyword: "alpred"
   - 오디오: "alpred" 녹음

2. test_alfred_voice.html에서 테스트
   - "alpred"라고 말하기
   - ✅ 키워드 인식 성공 (정확한 매칭)
   - "alfred"라고 말하기
   - ✅ 키워드 인식 성공 (유사도 매칭, 70% 이상)

---

## 음성 지문 저장 관리 과정 상세

### 1단계: 음성 지문 등록

```
[사용자 행동]
사용자: "rarfredo"라고 발음

[시스템 처리]
1. 녹음 시작 → 오디오 저장
2. STT 인식 → "rarfredo" 텍스트 추출
3. 음성 지문 등록 API 호출
   - base_keyword: "alfred"
   - stt_keyword: "rarfredo"
   - audio_data: "rarfredo" 오디오 (Base64)
4. DB 저장
```

### 2단계: DB 저장

```sql
INSERT INTO keyword_voiceprints (
    base_keyword,      -- "alfred"
    stt_keyword,       -- "rarfredo"
    audio_data,        -- "rarfredo" 오디오 (Base64)
    session_id,        -- "voiceprint_test_1234567890"
    is_active          -- true
);
```

### 3단계: 키워드 인식 시 활용

```
[사용자 행동]
사용자: "rarfredo"라고 말함

[시스템 처리]
1. Web Speech API: "rarfredo" STT 인식
2. /api/keyword/check 호출
   - stt_result: "rarfredo"
   - base_keyword: "alfred"
3. 서버: DB에서 voiceprint 조회
   - SELECT * FROM keyword_voiceprints 
     WHERE base_keyword = 'alfred' AND is_active = true
4. 서버: 정확한 매칭 확인
   - vp.stt_keyword("rarfredo") == stt_result("rarfredo")
   - ✅ 매칭 성공!
5. 서버: activate: True 반환
6. 클라이언트: 음성 인터페이스 활성화
```

---

## 테스트 체크리스트

### 기본 기능
- [ ] 음성 지문 등록 (자동 - 녹음 + STT)
- [ ] 음성 지문 등록 (수동 - 텍스트만)
- [ ] 등록된 음성 지문 목록 조회
- [ ] 음성 지문 테스트 (키워드 확인)
- [ ] 필터링 (base_keyword로 조회)

### 시나리오 테스트
- [ ] "alfred"를 "rarfredo"로 발음하는 사용자 등록
- [ ] "alfred"를 "alfred"로 정확히 발음하는 사용자 등록
- [ ] "alfred"를 "alpred"로 발음하는 사용자 등록
- [ ] 등록된 음성 지문으로 키워드 인식 테스트

### 통합 테스트
- [ ] test_voiceprint_management.html에서 등록
- [ ] test_alfred_voice.html에서 키워드 인식 테스트
- [ ] 등록된 voiceprint와 매칭 확인

---

## 문제 해결

### 문제: 녹음이 시작되지 않음
**해결**: 브라우저 마이크 권한 확인

### 문제: STT 결과가 입력되지 않음
**해결**: 
- Web Speech API 지원 브라우저 사용 (Chrome, Edge)
- 수동으로 STT 결과 입력

### 문제: 음성 지문 등록 실패
**해결**:
- 서버 로그 확인
- 데이터베이스 초기화 확인
- API 엔드포인트 확인

### 문제: 목록이 표시되지 않음
**해결**:
- 서버 연결 확인
- API 응답 확인 (브라우저 개발자 도구)
- 데이터베이스에 실제로 저장되었는지 확인

---

## 추가 정보

### 관련 파일
- `tests/user_testing/test_voiceprint_management.html`: 테스트 UI
- `tests/user_testing/test_alfred_voice.html`: 키워드 인식 테스트 UI
- `src/main.py`: API 엔드포인트
- `src/database.py`: 데이터베이스 스키마

### 관련 API
- `POST /api/keyword/voiceprint/register`: 음성 지문 등록
- `GET /api/keyword/voiceprint`: 음성 지문 조회
- `POST /api/keyword/check`: 키워드 확인

