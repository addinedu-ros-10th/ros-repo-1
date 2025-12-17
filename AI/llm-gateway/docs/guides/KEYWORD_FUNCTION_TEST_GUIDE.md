# 키워드 기능 테스트 가이드

**작성일**: 2025-11-18  
**프로젝트**: LLM Gateway  
**기능**: Keyword Voiceprint (키워드 인식 및 음성 지문)

---

## 📋 개요

이 가이드는 LLM Gateway의 키워드 인식 및 음성 지문 기능을 테스트하는 방법을 안내합니다.

### 키워드 기능이란?

- **키워드 인식**: 사용자가 말한 키워드(예: "alfred")를 정확하게 또는 유사도 기반으로 인식
- **음성 지문 등록**: 사용자별 발음 특성을 저장하여 향후 정확한 인식 지원
- **Fuzzy Matching**: 오타나 발음 차이를 고려한 유사도 기반 매칭 (70% 이상)

---

## 🗂️ 테스트에 사용할 파일들

### 1. 테스트 UI 파일 (HTML)

#### `tests/user_testing/test_alfred_voice.html`
**용도**: ALFRED 음성 인터페이스 통합 테스트  
**기능**:
- 키워드 인식 테스트
- 음성 지문 자동 등록 테스트
- 연속 대화 테스트
- 유사도 표시 확인

**접속 URL**: `http://localhost:8000/tests/test_alfred_voice.html`

#### `tests/user_testing/test_voiceprint_management.html`
**용도**: 음성 지문 관리 전용 테스트  
**기능**:
- 음성 지문 수동 등록
- 등록된 음성 지문 목록 조회
- 음성 지문 테스트 (키워드 확인)
- 필터링 및 관리

**접속 URL**: `http://localhost:8000/tests/test_voiceprint_management.html`

### 2. API 테스트 스크립트 (Python)

#### `tests/test_keyword_voiceprint_api.py`
**용도**: API 엔드포인트 직접 테스트  
**기능**:
- 키워드 확인 API 테스트
- 음성 지문 등록 API 테스트
- 음성 지문 조회 API 테스트
- 자동화된 테스트 케이스 실행

**실행 방법**:
```bash
cd AI/llm-gateway
python tests/test_keyword_voiceprint_api.py
```

### 3. 관련 문서

#### `docs/guides/KEYWORD_VOICEPRINT_VERIFICATION_GUIDE.md`
- 키워드 인식 및 음성 지문 기능 검증 가이드
- UI 개선 사항 및 기능 개선 사항 설명
- 검증 방법 및 체크리스트

#### `docs/guides/VOICEPRINT_REGISTRATION_TEST_GUIDE.md`
- 음성 지문 등록 기능 테스트 가이드
- 자동/수동 등록 방법
- 테스트 시나리오

#### `docs/guides/VOICEPRINT_MANAGEMENT_TEST_GUIDE.md`
- 음성 지문 관리 테스트 가이드
- 등록, 조회, 테스트 방법
- 실제 사용 시나리오

---

## 🚀 빠른 시작 가이드

### Step 1: 서버 실행

#### 방법 A: Docker Compose (권장)
```bash
cd AI/llm-gateway
docker compose up -d
```

#### 방법 B: 로컬 개발 환경
```bash
cd AI/llm-gateway
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: 서버 상태 확인

브라우저에서 접속:
- Health Check: `http://localhost:8000/`
- API 문서: `http://localhost:8000/docs`

### Step 3: 테스트 시작

아래 테스트 방법 중 하나를 선택하여 진행하세요.

---

## 🧪 테스트 방법

### 방법 1: 통합 테스트 UI (권장)

**파일**: `tests/user_testing/test_alfred_voice.html`

#### 테스트 절차

1. **브라우저에서 접속**
   ```
   http://localhost:8000/tests/test_alfred_voice.html
   ```

2. **기본 테스트**
   - "시작" 버튼 클릭
   - 마이크 권한 허용
   - "alfred"라고 말하기
   - **확인 사항**:
     - ✅ 키워드 감지 시 "유사도 XX%" 배지 표시
     - ✅ "등록된 음성 지문: N개" 표시
     - ✅ 키워드 인식 후 음성 인터페이스 활성화

3. **음성 지문 자동 등록 테스트**
   - 키워드 인식 후 한국어로 질문하기 (예: "안녕하세요")
   - **확인 사항**:
     - ✅ "✅ 새로운 음성 지문이 등록되었습니다 (ID: X)" 메시지 표시
     - ✅ "등록된 음성 지문: 1개"로 자동 업데이트

4. **연속 대화 테스트**
   - 여러 번 질문하기
   - **확인 사항**:
     - ✅ 키워드 인식이 정상 작동
     - ✅ 음성 지문이 적절히 관리됨

#### 예상 결과

```
✅ 키워드 감지: "alfred" → 유사도 100%
✅ 음성 지문 등록: "✅ 새로운 음성 지문이 등록되었습니다 (ID: 1)"
✅ 음성 지문 개수: "등록된 음성 지문: 1개"
```

---

### 방법 2: 음성 지문 관리 테스트 UI

**파일**: `tests/user_testing/test_voiceprint_management.html`

#### 테스트 절차

1. **브라우저에서 접속**
   ```
   http://localhost:8000/tests/test_voiceprint_management.html
   ```

2. **음성 지문 등록 (자동 - 녹음 + STT)**
   - "기준 키워드" 필드에 `alfred` 입력
   - "🎤 키워드 녹음 시작" 버튼 클릭
   - 마이크 권한 허용
   - **"rarfredo"라고 말하기** (또는 원하는 발음)
   - "⏹️ 녹음 중지" 버튼 클릭
   - "STT 결과 키워드" 필드에 자동 입력 확인
   - "💾 음성 지문 등록" 버튼 클릭
   - 등록 성공 메시지 확인

3. **음성 지문 등록 (수동 - 텍스트만)**
   - "기준 키워드" 필드에 `alfred` 입력
   - "STT 결과 키워드" 필드에 `rarfredo` 입력
   - "💾 음성 지문 등록" 버튼 클릭

4. **등록된 음성 지문 확인**
   - 페이지 로드 시 자동으로 목록 조회
   - "🔄 목록 새로고침" 버튼으로 수동 조회
   - "🔍 alfred만 조회" 버튼으로 필터링

5. **음성 지문 테스트**
   - 등록된 음성 지문 목록에서 "🧪 테스트" 버튼 클릭
   - 매칭 결과 확인:
     - ✅ 성공: 유사도 표시
     - ❌ 실패: 유사도 표시

#### 예상 결과

```
✅ 등록 성공: "✅ 새로운 음성 지문이 등록되었습니다"
✅ 목록 조회: 등록된 음성 지문 목록 표시
✅ 테스트 성공: "✅ 키워드 매칭 성공! 유사도: 100.0%"
```

---

### 방법 3: API 테스트 스크립트

**파일**: `tests/test_keyword_voiceprint_api.py`

#### 테스트 절차

1. **서버 실행 확인**
   ```bash
   # 서버가 실행 중인지 확인
   curl http://localhost:8000/
   ```

2. **테스트 스크립트 실행**
   ```bash
   cd AI/llm-gateway
   python tests/test_keyword_voiceprint_api.py
   ```

3. **테스트 결과 확인**
   - 키워드 확인 API 테스트 결과
   - 음성 지문 등록 API 테스트 결과
   - 음성 지문 조회 API 테스트 결과

#### 예상 출력

```
============================================================
키워드 인식 및 음성 지문 API 테스트
============================================================
API 서버: http://localhost:8000
✅ 서버 연결 확인됨

============================================================
1. 키워드 확인 API 테스트
============================================================
✅ 정확한 키워드 매칭
   STT 결과: 'alfred'
   키워드 인식: True (기대: True)
   유사도: 100.00%
   매칭된 키워드: alfred

✅ 키워드 포함
   STT 결과: 'hello alfred'
   키워드 인식: True (기대: True)
   유사도: 100.00%

✅ 유사한 키워드 (오타)
   STT 결과: 'rarpred'
   키워드 인식: True (기대: True)
   유사도: 71.43%

❌ 완전히 다른 단어
   STT 결과: 'hello'
   키워드 인식: False (기대: False)
   유사도: 0.00%

============================================================
2. 음성 지문 등록 API 테스트
============================================================
✅ 신규 음성 지문 등록
   성공: True
   음성 지문 ID: 1
   신규 등록: True

============================================================
3. 음성 지문 조회 API 테스트
============================================================
✅ 조회 성공
   등록된 음성 지문 개수: 1

============================================================
테스트 결과 요약
============================================================
키워드 확인: 4/4 성공
음성 지문 등록: 2/2 성공
음성 지문 조회: ✅ 성공 (1개 등록됨)
```

---

## 📝 테스트 시나리오

### 시나리오 1: 기본 키워드 인식 테스트

**목적**: 키워드가 정확하게 인식되는지 확인

**절차**:
1. `test_alfred_voice.html` 접속
2. "시작" 버튼 클릭
3. "alfred"라고 정확히 말하기

**예상 결과**:
- ✅ 키워드 인식 성공
- ✅ 유사도 100% 표시
- ✅ 음성 인터페이스 활성화

---

### 시나리오 2: 유사도 기반 매칭 테스트

**목적**: 오타나 발음 차이를 고려한 유사도 매칭 확인

**절차**:
1. `test_alfred_voice.html` 접속
2. "시작" 버튼 클릭
3. "rarpred"라고 말하기 (오타 시뮬레이션)

**예상 결과**:
- ✅ 키워드 인식 성공 (유사도 70% 이상)
- ✅ 유사도 배지 표시 (노란색 또는 초록색)
- ✅ 음성 인터페이스 활성화

---

### 시나리오 3: 음성 지문 자동 등록 테스트

**목적**: 키워드 인식 후 자동으로 음성 지문이 등록되는지 확인

**절차**:
1. `test_alfred_voice.html` 접속
2. "시작" 버튼 클릭
3. "alfred"라고 말하기 (키워드 인식)
4. "안녕하세요"라고 질문하기

**예상 결과**:
- ✅ 키워드 인식 성공
- ✅ "✅ 새로운 음성 지문이 등록되었습니다 (ID: 1)" 메시지 표시
- ✅ "등록된 음성 지문: 1개"로 업데이트

---

### 시나리오 4: 사용자별 음성 지문 등록

**목적**: 사용자별 발음 특성을 저장하고 활용하는지 확인

**절차**:
1. `test_voiceprint_management.html` 접속
2. 기준 키워드: "alfred" 입력
3. "rarfredo"라고 녹음 (사용자 A의 발음)
4. 음성 지문 등록
5. `test_alfred_voice.html`에서 "rarfredo"라고 말하기

**예상 결과**:
- ✅ 등록된 음성 지문과 정확히 매칭
- ✅ 유사도 100% 표시
- ✅ 키워드 인식 성공

---

### 시나리오 5: 다중 음성 지문 테스트

**목적**: 여러 사용자의 음성 지문이 모두 작동하는지 확인

**절차**:
1. `test_voiceprint_management.html`에서 여러 음성 지문 등록
   - "alfred" → "alfred" (정확한 발음)
   - "alfred" → "rarfredo" (오타 발음)
   - "alfred" → "alpred" (다른 오타 발음)
2. 각각 테스트

**예상 결과**:
- ✅ 모든 음성 지문이 정상 작동
- ✅ 각각의 발음이 정확히 인식됨

---

## ✅ 테스트 체크리스트

### 기본 기능
- [ ] 키워드 "alfred" 정확히 말하면 인식됨
- [ ] 키워드 포함된 문장에서도 인식됨 (예: "hello alfred")
- [ ] 유사한 키워드도 인식됨 (예: "rarpred", 유사도 70% 이상)
- [ ] 완전히 다른 단어는 인식되지 않음

### UI 피드백
- [ ] 키워드 감지 시 유사도 배지 표시
- [ ] 유사도에 따른 색상 변경 확인
  - 90% 이상: 초록색
  - 70-90%: 노란색
  - 70% 미만: 빨간색
- [ ] 음성 지문 등록 성공 시 초록색 메시지 표시
- [ ] 음성 지문 등록 실패 시 빨간색 메시지 표시
- [ ] 등록된 음성 지문 개수 표시

### 음성 지문 기능
- [ ] 키워드 감지 후 첫 질문 시 음성 지문 자동 등록
- [ ] 등록된 음성 지문이 DB에 저장됨
- [ ] 동일한 키워드로 다시 말하면 등록된 voiceprint와 매칭
- [ ] 음성 지문 조회 API로 등록된 데이터 확인 가능
- [ ] 음성 지문 관리 UI에서 등록/조회/테스트 가능

### API 동작
- [ ] `/api/keyword/check` 엔드포인트 정상 작동
- [ ] `/api/keyword/voiceprint/register` 엔드포인트 정상 작동
- [ ] `/api/keyword/voiceprint` 엔드포인트 정상 작동
- [ ] 에러 처리 정상 작동 (DB 미초기화 시 등)

---

## 🔧 문제 해결

### 문제: 서버에 연결할 수 없음

**증상**: 브라우저에서 404 또는 연결 오류

**해결**:
```bash
# 서버 실행 확인
cd AI/llm-gateway
docker compose ps
# 또는
ps aux | grep uvicorn

# 서버 재시작
docker compose up -d
# 또는
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### 문제: 데이터베이스가 초기화되지 않음

**증상**: 음성 지문 등록 시 "데이터베이스가 초기화되지 않았습니다" 오류

**해결**:
1. 서버 로그 확인
   ```bash
   docker compose logs llm-gateway | grep -i database
   ```

2. 환경 변수 확인
   ```bash
   # .env.local 파일 확인
   cat AI/llm-gateway/.env.local | grep DB
   ```

3. 서버 재시작
   ```bash
   docker compose restart llm-gateway
   ```

---

### 문제: 음성 지문이 등록되지 않음

**증상**: 등록 버튼 클릭 후 메시지가 표시되지 않음

**해결**:
1. 브라우저 콘솔 확인 (F12 → Console)
   - 에러 메시지 확인
   - API 호출 실패 여부 확인

2. 서버 로그 확인
   ```bash
   docker compose logs llm-gateway | tail -50
   ```

3. 데이터베이스 직접 확인
   ```sql
   SELECT * FROM keyword_voiceprints 
   WHERE base_keyword = 'alfred';
   ```

---

### 문제: 키워드가 인식되지 않음

**증상**: "alfred"라고 말해도 키워드 인식이 안 됨

**해결**:
1. 마이크 권한 확인
   - 브라우저에서 마이크 권한 허용 확인
   - 다른 앱에서 마이크 사용 중인지 확인

2. Web Speech API 확인
   - 브라우저 콘솔에서 STT 결과 확인
   - 다른 브라우저에서 테스트

3. 키워드 확인 API 직접 테스트
   ```bash
   python tests/test_keyword_voiceprint_api.py
   ```

---

### 문제: UI에 변경사항이 보이지 않음

**증상**: 코드 변경 후 UI가 업데이트되지 않음

**해결**:
1. 브라우저 캐시 삭제
   - Ctrl+Shift+R (강력 새로고침)
   - 또는 개발자 도구에서 캐시 비활성화

2. 서버가 최신 파일을 서빙하는지 확인
   - Docker Compose 사용 시 볼륨 마운트 확인
   - 로컬 실행 시 파일 경로 확인

---

## 📚 관련 문서

### 가이드 문서
- [키워드 인식 및 음성 지문 기능 검증 가이드](KEYWORD_VOICEPRINT_VERIFICATION_GUIDE.md)
- [음성 지문 등록 기능 테스트 가이드](VOICEPRINT_REGISTRATION_TEST_GUIDE.md)
- [음성 지문 관리 테스트 가이드](VOICEPRINT_MANAGEMENT_TEST_GUIDE.md)

### API 문서
- [키워드 Voiceprint 개발 완료](../api/KEYWORD_VOICEPRINT_DEVELOPMENT_COMPLETE.md)
- [Voiceprint 한국어 지원](../api/VOICEPRINT_KOREAN_SUPPORT.md)
- [Voiceprint 로직 비교](../api/VOICEPRINT_LOGIC_COMPARISON.md)

### 리포트 문서
- [키워드 Voiceprint 상태 리포트](../reports/KEYWORD_VOICEPRINT_STATUS_REPORT.md)
- [키워드 Voiceprint 개발 리포트](../reports/DEVELOPMENT_REPORT_KEYWORD_VOICEPRINT.md)

---

## 🎯 다음 단계

테스트 완료 후:
1. 테스트 결과 문서화
2. 발견된 이슈 리포트 작성
3. 개선 사항 제안

---

**작성일**: 2025-11-18  
**최종 업데이트**: 2025-11-18


