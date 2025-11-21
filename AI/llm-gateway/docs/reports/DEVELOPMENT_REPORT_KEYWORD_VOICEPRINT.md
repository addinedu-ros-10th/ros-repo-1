# 키워드 인식 및 음성 지문 기능 개발 리포트

## 개발 기간
2024년 11월

## 개발 목표
키워드 인식 및 사용자 음성 지문 저장/관리 기능 개발 및 검증

---

## 주요 개발 내용

### 1. 키워드 인식 기능 구현 ✅

#### 1.1 API 엔드포인트
- **`POST /api/keyword/check`**: 키워드 인식 및 활성화 확인
  - STT 결과를 받아 키워드 인식 확인
  - 정확한 매칭 우선 처리
  - 유사도 기반 Fuzzy Matching (70% 이상)
  - 등록된 voiceprint와 비교

#### 1.2 키워드 확인 로직
- DB에서 등록된 voiceprint 조회
- 정확한 매칭 확인 (`stt_keyword == stt_result`)
- 유사도 매칭 (`similarity >= 0.7`)
- 매칭 성공 시 `activate: True` 반환

---

### 2. 음성 지문 등록/관리 기능 구현 ✅

#### 2.1 API 엔드포인트
- **`POST /api/keyword/voiceprint/register`**: 음성 지문 등록
  - base_keyword와 stt_keyword 조합으로 저장
  - 기존 등록이 있으면 업데이트, 없으면 신규 등록
  - Base64 오디오 데이터 저장

- **`GET /api/keyword/voiceprint`**: 음성 지문 조회
  - base_keyword, session_id로 필터링 가능
  - 등록된 음성 지문 목록 반환

#### 2.2 데이터베이스 스키마
- **테이블**: `keyword_voiceprints`
- **필드**:
  - `base_keyword`: 기준 키워드 (예: "alfred")
  - `stt_keyword`: STT 결과 키워드 (예: "rarfredo")
  - `audio_data`: 음성 지문 오디오 (Base64)
  - `session_id`, `user_id`: 세션/사용자 ID
  - `is_active`: 활성화 여부

---

### 3. UI 개선 및 피드백 추가 ✅

#### 3.1 test_alfred_voice.html 개선
- **키워드 매칭 유사도 표시**: 키워드 감지 시 유사도 배지 표시
  - 90% 이상: 초록색
  - 70-90%: 노란색
  - 70% 미만: 빨간색

- **음성 지문 등록 상태 표시**: 성공/실패 메시지 표시
  - 성공: 초록색 배경
  - 실패: 빨간색 배경
  - 5초 후 자동 숨김

- **등록된 음성 지문 개수 표시**: 실시간 개수 표시 및 자동 업데이트

#### 3.2 test_voiceprint_management.html 신규 생성
- **음성 지문 등록 기능**:
  - 자동 등록: 녹음 + STT 자동 인식
  - 수동 등록: 텍스트만 입력하여 등록
  - STT 언어 선택 (영어/한국어)
  - OpenAI Whisper 사용 옵션

- **등록된 음성 지문 목록**:
  - 등록된 모든 음성 지문 조회
  - base_keyword로 필터링
  - 상세 정보 표시 (ID, 키워드, 생성일, 오디오 크기)
  - 테스트 기능 (키워드 확인)

- **실시간 음성 입력 및 STT 표시**:
  - 실시간 오디오 레벨 미터 (데시벨 표시)
  - 실시간 STT 텍스트 표시 (인식 중/최종 결과)
  - Web Speech API: 실시간 중간 결과 표시
  - OpenAI Whisper: 서버 인식 상태 표시

---

### 4. Docker 환경 개선 ✅

#### 4.1 Static 파일 업데이트 문제 해결
- **문제**: Docker 컨테이너 재시작해도 테스트 UI 변경사항이 반영되지 않음
- **해결**: `docker-compose.yml`에 tests 디렉토리 볼륨 마운트 추가
  ```yaml
  volumes:
    - ./tests:/app/tests
  ```
- **결과**: 호스트에서 파일 수정 시 컨테이너에 즉시 반영

---

### 5. 한국어 지원 추가 ✅

#### 5.1 STT 언어 선택
- 영어 (English) - 기본값
- 한국어 (Korean) - 추가

#### 5.2 STT 엔진 선택
- **Web Speech API** (기본값): 실시간, 무료, 선택한 언어로 인식
- **OpenAI Whisper** (선택): 한국어 인식 우수, 서버 요청 필요

#### 5.3 한국어 키워드 등록
- 한국어로 키워드를 말하면 한국어로 인식
- base_keyword는 영어로 유지, stt_keyword는 한국어로 저장 가능

---

### 6. 기능 검증 도구 제공 ✅

#### 6.1 API 테스트 스크립트
- **파일**: `tests/test_keyword_voiceprint_api.py`
- **기능**:
  - 키워드 확인 API 테스트
  - 음성 지문 등록 API 테스트
  - 음성 지문 조회 API 테스트

#### 6.2 문서화
- `docs/KEYWORD_VOICEPRINT_STATUS_REPORT.md`: 초기 상태 리포트
- `docs/KEYWORD_VOICEPRINT_VERIFICATION_GUIDE.md`: 검증 가이드
- `docs/KEYWORD_VOICEPRINT_DEVELOPMENT_COMPLETE.md`: 개발 완료 리포트
- `docs/VOICEPRINT_LOGIC_COMPARISON.md`: 로직 비교 분석
- `docs/VOICEPRINT_EXPLANATION.md`: 음성 지문 저장 관리 설명
- `docs/VOICEPRINT_REGISTRATION_TEST_GUIDE.md`: 등록 테스트 가이드
- `docs/VOICEPRINT_MANAGEMENT_TEST_GUIDE.md`: 관리 테스트 가이드
- `docs/STT_USAGE_ANALYSIS.md`: STT 사용 분석
- `docs/VOICEPRINT_KOREAN_SUPPORT.md`: 한국어 지원 가이드
- `docs/DOCKER_STATIC_FILES_FIX.md`: Docker static 파일 문제 해결
- `docs/DEVELOPMENT_REPORT_KEYWORD_VOICEPRINT.md`: 개발 리포트 (본 문서)

---

## 기술적 세부사항

### STT 사용 현황
- **키워드 감지**: 브라우저 기반 Web Speech API (기본)
- **음성 지문 등록**: Web Speech API (기본) 또는 OpenAI Whisper (선택)
- **질문 처리**: OpenAI Whisper API (항상)

### 음성 지문 저장 로직
- **stt_keyword**: 키워드 감지 시점의 STT 결과 텍스트 저장 ✅
- **audio_data**: 현재는 질문 오디오 저장 (향후 키워드 오디오 저장으로 개선 필요)

### 키워드 매칭 로직
- 정확한 매칭 우선
- 유사도 기반 Fuzzy Matching (70% 이상)
- 등록된 voiceprint와 비교
- 매칭 성공 시 음성 인터페이스 활성화

---

## 변경된 파일

### 신규 파일
1. `tests/user_testing/test_voiceprint_management.html` - 음성 지문 관리 테스트 UI
2. `tests/test_keyword_voiceprint_api.py` - API 테스트 스크립트
3. `docs/KEYWORD_VOICEPRINT_STATUS_REPORT.md` - 상태 리포트
4. `docs/KEYWORD_VOICEPRINT_VERIFICATION_GUIDE.md` - 검증 가이드
5. `docs/KEYWORD_VOICEPRINT_DEVELOPMENT_COMPLETE.md` - 개발 완료 리포트
6. `docs/VOICEPRINT_LOGIC_COMPARISON.md` - 로직 비교 분석
7. `docs/VOICEPRINT_EXPLANATION.md` - 음성 지문 설명
8. `docs/VOICEPRINT_REGISTRATION_TEST_GUIDE.md` - 등록 테스트 가이드
9. `docs/VOICEPRINT_MANAGEMENT_TEST_GUIDE.md` - 관리 테스트 가이드
10. `docs/STT_USAGE_ANALYSIS.md` - STT 사용 분석
11. `docs/VOICEPRINT_KOREAN_SUPPORT.md` - 한국어 지원 가이드
12. `docs/DOCKER_STATIC_FILES_FIX.md` - Docker 문제 해결
13. `docs/DEVELOPMENT_REPORT_KEYWORD_VOICEPRINT.md` - 개발 리포트

### 수정된 파일
1. `src/main.py` - 키워드 인식 및 음성 지문 API 엔드포인트 추가
2. `src/database.py` - KeywordVoiceprint 테이블 스키마 추가
3. `tests/user_testing/test_alfred_voice.html` - UI 피드백 추가
4. `docker-compose.yml` - tests 디렉토리 볼륨 마운트 추가

---

## 테스트 방법

### 1. 음성 지문 등록 테스트
```
URL: http://localhost:8000/tests/test_voiceprint_management.html
1. STT 언어 선택
2. 키워드 녹음 시작
3. 키워드 말하기
4. 녹음 중지
5. STT 결과 확인
6. 음성 지문 등록
```

### 2. 키워드 인식 테스트
```
URL: http://localhost:8000/tests/test_alfred_voice.html
1. 시작 버튼 클릭
2. "alfred" 또는 등록된 키워드 말하기
3. 키워드 인식 확인 (유사도 표시)
4. 질문하기
5. 음성 지문 자동 등록 확인
```

### 3. API 테스트
```bash
cd AI/llm-gateway
python tests/test_keyword_voiceprint_api.py
```

---

## 주요 성과

### ✅ 완료된 기능
- [x] 키워드 인식 API 구현
- [x] 음성 지문 등록/조회 API 구현
- [x] 데이터베이스 스키마 구현
- [x] UI 피드백 추가 (유사도, 등록 상태, 개수)
- [x] 음성 지문 관리 테스트 UI 생성
- [x] 실시간 음성 입력 및 STT 표시
- [x] 한국어 지원
- [x] Docker 환경 개선
- [x] 검증 도구 및 문서화

### ⚠️ 향후 개선 사항
- [ ] 키워드 감지 시점의 오디오 저장 (현재는 질문 오디오 저장)
- [ ] 음성 지문 삭제 기능
- [ ] 음성 지문 목록 상세 조회 UI
- [ ] 오디오 데이터 기반 음성 인식 (향후 확장)

---

## 결론

키워드 인식 및 음성 지문 기능이 성공적으로 개발되었습니다. 사용자는 자신의 발음 특성에 맞는 음성 지문을 등록하고, 향후 키워드 인식 시 더 정확하게 매칭될 수 있습니다.

### 핵심 기능
1. **텍스트 기반 키워드 매칭**: STT 결과 텍스트를 DB에 저장하고 비교
2. **유사도 기반 매칭**: 70% 이상 유사도로 키워드 인식
3. **사용자별 음성 지문**: 사용자의 발음 특성에 맞는 키워드 저장
4. **실시간 피드백**: 오디오 레벨, STT 텍스트 실시간 표시

### 사용자 경험 개선
- 시각적 피드백으로 기능 동작 확인 가능
- 실시간 상태 표시로 진행 상황 파악
- 한국어 지원으로 다양한 사용자 지원

