# 음성 지문 처리 STT 사용 분석

## 개요
음성 지문을 처리하는 데 사용되는 STT(Speech-to-Text) 엔진을 분석합니다.

---

## STT 사용 현황

### 1. 키워드 감지 시 STT

#### 사용 엔진: **브라우저 기반 Web Speech API**

**위치**: `test_alfred_voice.html`

```javascript
// 519-526줄
function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US'; // 영어로 키워드 감지
}
```

**특징**:
- ✅ 브라우저 내장 STT (Chrome, Edge 지원)
- ✅ 실시간 인식 (continuous mode)
- ✅ 인터넷 연결 필요 (Google 서비스 사용)
- ✅ 무료 사용 가능
- ⚠️ 브라우저별 성능 차이
- ⚠️ 오프라인 작동 불가

**사용 흐름**:
```
사용자: "alfred" 또는 "rarfredo"라고 말함
  ↓
Web Speech API: 실시간 STT 인식
  ↓
STT 결과: "alfred" 또는 "rarfredo"
  ↓
클라이언트: /api/keyword/check 호출
```

---

### 2. 음성 지문 등록 시 STT

#### 방법 1: 브라우저 기반 Web Speech API (기본)

**위치**: `test_voiceprint_management.html`

```javascript
// 401-416줄
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript.toLowerCase().trim();
        document.getElementById('sttKeyword').value = transcript;
    };
}
```

**특징**:
- ✅ 브라우저 내장 STT
- ✅ 실시간 인식
- ✅ 무료

#### 방법 2: OpenAI Whisper API (서버 기반, 선택적)

**위치**: `test_voiceprint_management.html`

```javascript
// 449-473줄
async function recognizeKeyword() {
    const formData = new FormData();
    formData.append('audio', recordedAudioBlob, 'keyword.webm');
    
    const response = await fetch(
        `${API_BASE_URL}/api/voice/process?response_format=json`,
        {
            method: 'POST',
            body: formData
        }
    );
    
    const data = await response.json();
    if (data.success && data.user_text) {
        const keyword = data.user_text.toLowerCase().trim();
        document.getElementById('sttKeyword').value = keyword;
    }
}
```

**서버 측 처리** (`main.py`):
```python
# 613-617줄
transcription = await client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ko"
)
```

**특징**:
- ✅ OpenAI Whisper-1 모델 사용
- ✅ 고정밀 인식
- ✅ 한국어 지원 우수
- ⚠️ API 비용 발생
- ⚠️ 서버 요청 필요

**현재 구현**: 
- 기본적으로 Web Speech API 사용
- 녹음된 오디오를 서버로 전송하여 Whisper로 인식하는 기능도 제공 (선택적)

---

### 3. 질문 처리 시 STT

#### 사용 엔진: **OpenAI Whisper API**

**위치**: `main.py`

```python
# 613-617줄
transcription = await client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ko"
)
```

**특징**:
- ✅ OpenAI Whisper-1 모델
- ✅ 한국어 인식 우수
- ✅ 고정밀 인식
- ⚠️ API 비용 발생

**사용 흐름**:
```
사용자: "안녕하세요"라고 질문
  ↓
클라이언트: 오디오 녹음
  ↓
서버: /api/voice/process 호출
  ↓
OpenAI Whisper API: STT 처리
  ↓
STT 결과: "안녕하세요"
```

---

## STT 사용 비교표

| 용도 | STT 엔진 | 위치 | 특징 |
|------|---------|------|------|
| **키워드 감지** | Web Speech API (브라우저) | test_alfred_voice.html | 실시간, 무료, 영어 |
| **음성 지문 등록** | Web Speech API (브라우저) | test_voiceprint_management.html | 실시간, 무료, 영어 |
| **음성 지문 등록 (선택)** | OpenAI Whisper (서버) | test_voiceprint_management.html | 고정밀, 유료, 다국어 |
| **질문 처리** | OpenAI Whisper (서버) | main.py | 고정밀, 유료, 한국어 |

---

## 상세 분석

### 브라우저 기반 Web Speech API

#### 장점
- ✅ 무료 사용
- ✅ 실시간 인식
- ✅ 클라이언트 측 처리 (서버 부하 없음)
- ✅ 즉시 사용 가능 (별도 설정 불필요)

#### 단점
- ⚠️ 인터넷 연결 필수
- ⚠️ 브라우저별 성능 차이
- ⚠️ 영어 인식에 최적화 (다른 언어는 성능 저하)
- ⚠️ 정확도가 OpenAI Whisper보다 낮음

#### 사용 사례
- 키워드 감지 (실시간, 영어)
- 음성 지문 등록 시 키워드 인식 (실시간, 영어)

---

### OpenAI Whisper API

#### 장점
- ✅ 높은 정확도
- ✅ 다국어 지원 (한국어 포함)
- ✅ 오프라인 모델 사용 가능 (로컬 배포 시)
- ✅ 일관된 성능

#### 단점
- ⚠️ API 비용 발생
- ⚠️ 서버 요청 필요 (지연 시간)
- ⚠️ 실시간 인식 어려움

#### 사용 사례
- 질문 처리 (한국어, 고정밀)
- 음성 지문 등록 시 키워드 인식 (선택적, 고정밀)

---

## 현재 구현의 특징

### 하이브리드 접근

1. **키워드 감지**: 브라우저 STT (빠른 응답, 무료)
2. **질문 처리**: OpenAI Whisper (고정밀, 한국어)
3. **음성 지문 등록**: 브라우저 STT (기본) 또는 OpenAI Whisper (선택)

### 이유

#### 키워드 감지에 브라우저 STT 사용
- 키워드는 단순하고 반복적
- 실시간 인식이 중요
- 영어 키워드 ("alfred") 인식에 충분
- 비용 절감

#### 질문 처리에 OpenAI Whisper 사용
- 한국어 질문 처리 필요
- 높은 정확도 필요
- 복잡한 문장 처리

---

## 음성 지문 저장 시 STT 결과

### 현재 저장되는 데이터

```sql
INSERT INTO keyword_voiceprints (
    base_keyword,      -- "alfred" (수동 입력 또는 기본값)
    stt_keyword,       -- "rarfredo" (브라우저 STT 또는 OpenAI Whisper 결과)
    audio_data,        -- 오디오 (Base64)
    ...
);
```

### STT 결과 출처

1. **test_alfred_voice.html (자동 등록)**:
   - `stt_keyword`: Web Speech API 결과
   - 예: "alfred", "rarfredo", "alpred" 등

2. **test_voiceprint_management.html (수동 등록)**:
   - 방법 1: Web Speech API 결과 (기본)
   - 방법 2: OpenAI Whisper 결과 (선택)
   - 방법 3: 수동 입력 (STT 없이)

---

## 결론

### 음성 지문 처리에 사용되는 STT

**주로 사용**: **브라우저 기반 Web Speech API**
- 키워드 감지: Web Speech API
- 음성 지문 등록: Web Speech API (기본)

**선택적 사용**: **OpenAI Whisper API**
- 음성 지문 등록: OpenAI Whisper (고정밀 인식 필요 시)
- 질문 처리: OpenAI Whisper (항상)

### 권장 사항

1. **키워드 감지**: Web Speech API 유지 (실시간, 무료)
2. **음성 지문 등록**: 
   - 기본: Web Speech API
   - 고정밀 필요 시: OpenAI Whisper API
3. **질문 처리**: OpenAI Whisper API 유지 (한국어, 고정밀)

---

## 참고 사항

### Web Speech API 제한사항
- Chrome, Edge에서만 최적 성능
- 인터넷 연결 필수
- 영어 인식에 최적화

### OpenAI Whisper API 비용
- 사용량에 따라 비용 발생
- 정확도와 비용의 트레이드오프

### 향후 개선 방안
- 로컬 Whisper 모델 배포 (비용 절감)
- 하이브리드 접근 유지 (키워드: 브라우저, 질문: Whisper)

