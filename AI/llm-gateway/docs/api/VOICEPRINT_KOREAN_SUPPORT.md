# 음성 지문 한국어 지원

## 개요
`test_voiceprint_management.html`에서 한국어 키워드 음성 지문을 등록할 수 있도록 개선되었습니다.

## 한국어 인식 방법

### 방법 1: OpenAI Whisper 사용 (권장)

#### 설정
1. **STT 언어 선택**: "한국어 (Korean)" 선택 (선택사항, Whisper는 자동 인식)
2. **OpenAI Whisper 사용**: ✅ 체크
3. **키워드 녹음 시작** 클릭
4. 한국어로 키워드 말하기 (예: "알프레드", "알프레드야" 등)
5. **녹음 중지** 클릭
6. STT 결과 확인 (한국어로 인식됨)

#### 특징
- ✅ 한국어 인식 정확도 높음
- ✅ 자연스러운 한국어 발음 인식
- ✅ 서버 요청 필요 (약간의 지연)
- ⚠️ API 비용 발생

### 방법 2: 브라우저 Web Speech API 사용

#### 설정
1. **STT 언어 선택**: "한국어 (Korean)" 선택
2. **OpenAI Whisper 사용**: ❌ 체크 해제
3. **키워드 녹음 시작** 클릭
4. 한국어로 키워드 말하기
5. **녹음 중지** 클릭
6. STT 결과 확인

#### 특징
- ✅ 실시간 인식
- ✅ 무료
- ⚠️ 한국어 인식 정확도가 Whisper보다 낮을 수 있음
- ⚠️ 브라우저별 성능 차이

---

## 사용 예시

### 시나리오 1: 한국어 키워드 등록

```
1. STT 언어: "한국어 (Korean)" 선택
2. OpenAI Whisper: ✅ 체크
3. 키워드 녹음: "알프레드"라고 말하기
4. STT 결과: "알프레드" (자동 입력)
5. 음성 지문 등록
```

### 시나리오 2: 영어 키워드 등록 (기존 방식)

```
1. STT 언어: "영어 (English)" 선택
2. OpenAI Whisper: ❌ 체크 해제 (또는 체크)
3. 키워드 녹음: "alfred"라고 말하기
4. STT 결과: "alfred" (자동 입력)
5. 음성 지문 등록
```

### 시나리오 3: 혼합 (영어 키워드, 한국어 발음)

```
1. STT 언어: "한국어 (Korean)" 선택
2. OpenAI Whisper: ✅ 체크
3. 키워드 녹음: "알프레드"라고 말하기 (영어 "alfred"를 한국어로 발음)
4. STT 결과: "알프레드" (자동 입력)
5. base_keyword: "alfred" (기준 키워드는 영어)
6. stt_keyword: "알프레드" (STT 결과는 한국어)
7. 음성 지문 등록
```

---

## 한국어 키워드 인식 테스트

### 테스트 절차

1. **음성 지문 등록**
   - 한국어로 키워드 등록 (예: "알프레드")
   - base_keyword: "alfred"
   - stt_keyword: "알프레드"

2. **키워드 인식 테스트**
   - test_alfred_voice.html에서 테스트
   - "알프레드"라고 말하기
   - 등록된 voiceprint와 매칭 확인

### 주의사항

- **base_keyword**: 기준 키워드는 영어로 유지하는 것을 권장
- **stt_keyword**: STT 결과는 한국어로 저장 가능
- **매칭**: `/api/keyword/check`에서 텍스트 매칭 사용 (한국어도 매칭 가능)

---

## 기술적 세부사항

### Web Speech API 한국어 설정

```javascript
recognition.lang = 'ko-KR'; // 한국어 설정
```

### OpenAI Whisper 한국어 인식

```python
# main.py:616
transcription = await client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file,
    language="ko"  # 한국어 명시
)
```

### 텍스트 매칭

```python
# main.py:812
if vp.stt_keyword.lower() == stt_result_lower:
    # 정확한 매칭 (한국어도 매칭 가능)
    return {"activate": True, ...}
```

---

## FAQ

### Q: 한국어 키워드도 인식되나요?
**A**: 네, OpenAI Whisper를 사용하면 한국어 키워드도 정확하게 인식됩니다.

### Q: 브라우저 STT로도 한국어 인식이 가능한가요?
**A**: 가능하지만, 정확도가 Whisper보다 낮을 수 있습니다. 한국어 키워드 등록 시 Whisper 사용을 권장합니다.

### Q: 영어와 한국어를 혼합해서 사용할 수 있나요?
**A**: 네, base_keyword는 영어로, stt_keyword는 한국어로 저장할 수 있습니다.

### Q: 한국어 키워드로 음성 인터페이스를 활성화할 수 있나요?
**A**: 네, 등록된 한국어 stt_keyword와 매칭되면 활성화됩니다.

---

## 참고사항

- 한국어 키워드 등록 시 OpenAI Whisper 사용을 권장합니다
- 브라우저 STT는 한국어 인식 정확도가 낮을 수 있습니다
- base_keyword는 영어로 유지하는 것을 권장합니다 (시스템 일관성)

