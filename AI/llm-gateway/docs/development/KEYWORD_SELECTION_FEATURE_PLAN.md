# 키워드 선택 기능 개발 계획

**작성일**: 2025-11-18  
**요청사항**: `test_alfred_voice.html`에서 등록된 키워드를 선택할 수 있게 업데이트

---

## 📋 요청사항 이해 확인

### 현재 상태

1. **`test_alfred_voice.html`**
   - 키워드가 "alfred"로 하드코딩되어 있음
   - `loadKeywords()` 함수가 있지만 완전히 구현되지 않았을 수 있음
   - `keywordSelect` 드롭다운이 있지만 제한적임

2. **`test_voiceprint_management.html`**
   - 음성 지문 등록 기능 제공
   - 등록된 키워드 목록 조회 기능 제공
   - `/api/keyword/voiceprint` API를 통해 등록된 키워드 조회 가능

### 요청사항

**핵심 요청**:
- `test_alfred_voice.html`에서 대화 활성화 기준 키워드를 선택할 수 있게 업데이트
- `test_voiceprint_management.html`에서 등록한 키워드들을 불러와서 선택 가능하게 함
- 현재 "alfred"로 고정된 부분을 동적으로 변경 가능하게 함

**이해한 내용**:
1. ✅ `test_alfred_voice.html`에 키워드 선택 UI 추가/개선
2. ✅ 등록된 키워드 목록을 API로 불러오기
3. ✅ 선택한 키워드로 대화 활성화 기준 변경
4. ✅ 키워드 변경 시 관련 로직 업데이트

---

## 🔍 현재 코드 분석

### `test_alfred_voice.html` 현재 상태

#### 키워드 관련 변수
```javascript
let KEYWORD = 'alfred'; // 동적으로 변경 가능하도록 let으로 변경
```

#### 키워드 선택 UI (부분 구현됨)
```html
<select id="keywordSelect" onchange="onKeywordChange()">
    <option value="alfred" selected>alfred (기본)</option>
</select>
<button onclick="loadKeywords()">키워드 목록 새로고침</button>
```

#### 키워드 로드 함수 (부분 구현됨)
```javascript
async function loadKeywords() {
    // /api/keyword/voiceprint API 호출
    // 고유한 base_keyword 목록 추출
    // select 옵션 업데이트
}
```

#### 키워드 변경 함수
```javascript
function onKeywordChange() {
    const select = document.getElementById('keywordSelect');
    KEYWORD = select.value;
    console.log('키워드 변경:', KEYWORD);
    document.getElementById('debugBaseKeyword').textContent = KEYWORD;
}
```

### 문제점

1. **초기 로드 시 키워드 목록 불러오기 미완성**
   - 페이지 로드 시 자동으로 키워드 목록을 불러오지 않음
   - `loadKeywords()` 함수가 완전히 구현되지 않았을 수 있음

2. **키워드 변경 시 상태 초기화 미흡**
   - 키워드 변경 시 세션 상태 초기화 필요
   - 음성 인식 재시작 필요할 수 있음

3. **UI 피드백 부족**
   - 키워드 선택 UI가 눈에 잘 띄지 않음
   - 선택한 키워드가 명확히 표시되지 않음

---

## 🎯 개발 계획

### Phase 1: 키워드 선택 UI 개선

#### 1.1 키워드 선택 UI 위치 및 스타일 개선
- **위치**: 상단 상태 바 근처 또는 설정 영역에 배치
- **스타일**: 드롭다운 + 새로고침 버튼을 더 눈에 띄게
- **표시**: 현재 선택된 키워드를 명확히 표시

#### 1.2 키워드 목록 자동 로드
- **페이지 로드 시**: 자동으로 등록된 키워드 목록 불러오기
- **에러 처리**: API 호출 실패 시 기본값("alfred") 사용
- **로딩 상태**: 키워드 로드 중 표시

### Phase 2: 키워드 변경 로직 구현

#### 2.1 키워드 변경 핸들러 개선
- **상태 초기화**: 키워드 변경 시 세션 상태 초기화
- **음성 인식 재시작**: 필요 시 음성 인식 재시작
- **UI 업데이트**: 관련 UI 요소 업데이트

#### 2.2 키워드 관련 변수 업데이트
- **KEYWORD 변수**: 선택한 키워드로 업데이트
- **API 호출**: 선택한 키워드로 API 호출
- **디버그 정보**: 선택한 키워드 표시

### Phase 3: 통합 및 테스트

#### 3.1 통합 테스트
- 키워드 선택 → 대화 활성화 테스트
- 여러 키워드 전환 테스트
- 등록되지 않은 키워드 선택 테스트

#### 3.2 사용자 경험 개선
- 키워드 선택 시 피드백 제공
- 키워드 목록이 비어있을 때 안내 메시지
- 키워드 로드 실패 시 안내 메시지

---

## 📝 상세 구현 계획

### 1. HTML 구조 개선

#### 현재 구조
```html
<select id="keywordSelect" onchange="onKeywordChange()">
    <option value="alfred" selected>alfred (기본)</option>
</select>
<button onclick="loadKeywords()">키워드 목록 새로고침</button>
```

#### 개선된 구조
```html
<div class="keyword-selector">
    <label for="keywordSelect">활성화 키워드:</label>
    <select id="keywordSelect" onchange="onKeywordChange()">
        <option value="alfred" selected>alfred (기본)</option>
        <!-- 동적으로 추가됨 -->
    </select>
    <button onclick="loadKeywords()" class="btn-refresh">🔄 새로고침</button>
    <span id="keywordCount" class="keyword-count">(0개 등록됨)</span>
</div>
```

### 2. JavaScript 함수 개선

#### `loadKeywords()` 함수 개선
```javascript
async function loadKeywords() {
    try {
        // 로딩 상태 표시
        showLoadingState();
        
        // API 호출
        const response = await fetch(`${API_BASE_URL}/api/keyword/voiceprint`);
        const data = await response.json();
        
        if (data.success && data.voiceprints) {
            // 고유한 base_keyword 목록 추출
            const uniqueKeywords = [...new Set(
                data.voiceprints.map(vp => vp.base_keyword)
            )];
            
            // select 옵션 업데이트
            updateKeywordSelect(uniqueKeywords);
            
            // 키워드 개수 표시
            updateKeywordCount(uniqueKeywords.length);
            
            console.log('키워드 목록 로드 완료:', uniqueKeywords);
        }
    } catch (error) {
        console.error('키워드 목록 로드 실패:', error);
        showErrorMessage('키워드 목록을 불러올 수 없습니다.');
    }
}
```

#### `onKeywordChange()` 함수 개선
```javascript
function onKeywordChange() {
    const select = document.getElementById('keywordSelect');
    const newKeyword = select.value;
    
    // 키워드 변경
    KEYWORD = newKeyword;
    
    // 세션 상태 초기화
    resetSessionState();
    
    // UI 업데이트
    updateUIForKeyword(newKeyword);
    
    // 디버그 정보 업데이트
    document.getElementById('debugBaseKeyword').textContent = KEYWORD;
    
    console.log('키워드 변경:', KEYWORD);
}
```

#### `resetSessionState()` 함수 추가
```javascript
function resetSessionState() {
    // 세션 비활성화
    sessionActive = false;
    
    // 키워드 관련 상태 초기화
    lastDetectedKeyword = null;
    keywordAudioBuffer = null;
    
    // UI 상태 초기화
    document.getElementById('keywordStatus').textContent = '대기 중';
    document.getElementById('keywordIndicator').classList.remove('active');
    updateStatus('waiting', `대기 중... "${KEYWORD}"라고 말해주세요`);
    
    // 활성화 타이머 초기화
    if (activationTimer) {
        clearTimeout(activationTimer);
        activationTimer = null;
    }
}
```

### 3. CSS 스타일 추가

```css
.keyword-selector {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 10px;
    margin-bottom: 20px;
}

.keyword-selector label {
    font-weight: bold;
    color: #333;
}

.keyword-selector select {
    flex: 1;
    padding: 8px 12px;
    border: 2px solid #007bff;
    border-radius: 5px;
    font-size: 14px;
}

.keyword-count {
    font-size: 12px;
    color: #666;
}

.btn-refresh {
    padding: 8px 15px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 14px;
}
```

---

## ✅ 구현 체크리스트

### Phase 1: UI 개선
- [ ] 키워드 선택 UI 위치 및 스타일 개선
- [ ] 키워드 개수 표시 추가
- [ ] 로딩 상태 표시 추가
- [ ] 에러 메시지 표시 추가

### Phase 2: 기능 구현
- [ ] `loadKeywords()` 함수 완전 구현
- [ ] `onKeywordChange()` 함수 개선
- [ ] `resetSessionState()` 함수 추가
- [ ] 페이지 로드 시 자동 키워드 로드

### Phase 3: 통합 및 테스트
- [ ] 키워드 선택 → 대화 활성화 테스트
- [ ] 여러 키워드 전환 테스트
- [ ] 등록되지 않은 키워드 선택 테스트
- [ ] 키워드 목록이 비어있을 때 테스트

---

## 🎨 UI 개선 사항

### 현재 UI
- 키워드 선택 드롭다운이 작고 눈에 잘 띄지 않음
- 키워드 개수 정보 없음
- 키워드 로드 상태 표시 없음

### 개선된 UI
- 키워드 선택 영역을 더 눈에 띄게 배치
- 현재 선택된 키워드 강조 표시
- 등록된 키워드 개수 표시
- 키워드 로드 중 로딩 인디케이터
- 키워드 로드 실패 시 에러 메시지

---

## 🔄 워크플로우

### 사용자 시나리오

1. **페이지 로드**
   - 자동으로 등록된 키워드 목록 불러오기
   - 기본값 "alfred" 선택 (또는 마지막 선택한 키워드)

2. **키워드 선택**
   - 드롭다운에서 키워드 선택
   - 세션 상태 자동 초기화
   - UI 업데이트

3. **키워드 목록 새로고침**
   - "🔄 새로고침" 버튼 클릭
   - 최신 등록된 키워드 목록 불러오기
   - select 옵션 업데이트

4. **대화 시작**
   - 선택한 키워드를 말하면 대화 활성화
   - 키워드 인식 및 음성 인터페이스 시작

---

## 📊 예상 변경사항

### 파일 변경
- `tests/user_testing/test_alfred_voice.html`
  - HTML 구조 수정 (키워드 선택 UI)
  - JavaScript 함수 개선/추가
  - CSS 스타일 추가

### 추가 기능
- 키워드 목록 자동 로드
- 키워드 변경 시 상태 초기화
- 키워드 개수 표시
- 로딩/에러 상태 표시

---

## ⚠️ 주의사항

1. **하위 호환성**
   - 기존 "alfred" 키워드는 기본값으로 유지
   - 기존 기능이 정상 작동해야 함

2. **에러 처리**
   - API 호출 실패 시 기본값 사용
   - 네트워크 오류 처리
   - 빈 키워드 목록 처리

3. **성능**
   - 키워드 목록 로드는 필요 시에만 실행
   - 캐싱 고려 (선택사항)

---

## 🧪 테스트 시나리오

### 시나리오 1: 기본 동작
1. 페이지 로드
2. 등록된 키워드 목록 자동 로드 확인
3. 기본값 "alfred" 선택 확인
4. 키워드 선택 드롭다운에 등록된 키워드 표시 확인

### 시나리오 2: 키워드 변경
1. 드롭다운에서 다른 키워드 선택
2. 세션 상태 초기화 확인
3. UI 업데이트 확인
4. 선택한 키워드로 대화 활성화 테스트

### 시나리오 3: 키워드 목록 새로고침
1. "🔄 새로고침" 버튼 클릭
2. 최신 키워드 목록 불러오기 확인
3. select 옵션 업데이트 확인

### 시나리오 4: 등록되지 않은 키워드
1. 등록되지 않은 키워드 선택
2. 키워드 인식 실패 확인
3. 적절한 피드백 제공 확인

---

## 📅 예상 작업 시간

- Phase 1 (UI 개선): 30분
- Phase 2 (기능 구현): 1시간
- Phase 3 (통합 및 테스트): 30분

**총 예상 시간**: 약 2시간

---

## ✅ 요청사항 확인 질문

1. **키워드 선택 UI 위치**
   - 상단 상태 바 근처에 배치할까요?
   - 설정 영역에 배치할까요?
   - → **제안**: 상단 상태 바 근처 (눈에 잘 띄게)

2. **기본 키워드**
   - 페이지 로드 시 기본값은 "alfred"로 유지할까요?
   - 마지막 선택한 키워드를 기억할까요? (localStorage)
   - → **제안**: "alfred" 기본값 유지 + localStorage로 마지막 선택 기억

3. **키워드 목록 자동 로드**
   - 페이지 로드 시 자동으로 불러올까요?
   - 사용자가 버튼을 클릭할 때만 불러올까요?
   - → **제안**: 페이지 로드 시 자동 로드 + 수동 새로고침 버튼 제공

4. **키워드 변경 시 동작**
   - 키워드 변경 시 즉시 세션 초기화할까요?
   - 사용자 확인 후 초기화할까요?
   - → **제안**: 즉시 초기화 (사용자 경험 향상)

---

**피드백 요청**

위 계획이 요청사항을 정확히 반영했는지 확인 부탁드립니다.
특히 다음 사항에 대한 피드백을 요청합니다:

1. 키워드 선택 UI 위치 선호도
2. 기본 키워드 처리 방식
3. 키워드 목록 자동 로드 여부
4. 키워드 변경 시 동작 방식
5. 추가 요구사항

피드백 주시면 즉시 개발을 시작하겠습니다.


