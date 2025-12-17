# 어르신 배회 탐지 시 생활관 복귀 안내 기능 구현 완료 리포트

**작성일**: 2024년  
**상태**: ✅ **구현 완료**

---

## ✅ 구현 완료 사항

### 1. TOOLS 함수 추가

**함수명**: `guide_wandering_resident_to_room`

**기능**:
- 순찰 중 어르신 배회 탐지 시 생활관 복귀 안내
- 어르신 성함 또는 nickname 기반 정보 조회
- 친절한 안내 메시지 최소 3회 반복 생성

**파라미터**:
- `resident_name` (optional): 어르신 성함
- `nickname` (optional): 어르신 nickname
- `detection_location` (optional): 탐지 위치 (기본값: "복도")

**반환 형식**:
```json
{
    "success": true,
    "resident_info": {
        "user_id": "...",
        "user_name": "...",
        "nickname": "...",
        "room_number": "...",
        "floor_number": ...,
        "bed_number": "..."
    },
    "guidance_messages": [
        "안내 메시지 1",
        "안내 메시지 2",
        "안내 메시지 3"
    ],
    "detection_location": "...",
    "message": "..."
}
```

---

### 2. 구현된 함수

#### `_search_residents(keyword: str)`
- 키워드로 입소자 정보 검색 API 호출
- `/api/residents/search/{keyword}` 엔드포인트 사용

#### `_guide_wandering_resident_to_room(resident_name, nickname, detection_location)`
- 메인 안내 함수
- nickname 우선 검색, 없으면 resident_name으로 검색
- 생활실 정보 추출 및 안내 메시지 생성

---

### 3. 안내 메시지 구조

#### 1회차 메시지
```
안녕하세요, {nickname} 어르신! 지금 {detection_location}에서 어르신을 발견했습니다. 
어르신의 생활실은 {floor_number}층 {room_number}호 {bed_number}번 침대입니다. 
안전을 위해 생활실로 복귀해 주시겠어요?
```

#### 2회차 메시지
```
{user_name} 어르신, 지금 {detection_location}에 계시는 것으로 보입니다. 
{floor_number}층 {room_number}호 생활실로 돌아가 주시면 감사하겠습니다. 
혼자 계시면 위험할 수 있으니 생활실로 복귀해 주세요.
```

#### 3회차 메시지
```
어르신, {nickname} 어르신! 지금 {detection_location}에 계신 것으로 탐지되었습니다. 
생활실은 {floor_number}층 {room_number}호입니다. 
제가 함께 생활실로 안내해 드릴까요? 안전을 위해 생활실로 복귀해 주시기 바랍니다.
```

---

### 4. 테스트용 모킹 API

**엔드포인트**: `POST /api/test/wandering-detection`

**Request Body**:
```json
{
    "resident_name": "정도현",
    "nickname": "Akaza",
    "detection_location": "1층 복도"
}
```

**Response**:
```json
{
    "success": true,
    "message": "배회 탐지 시뮬레이션 완료",
    "detection_info": {
        "resident_name": "정도현",
        "nickname": "Akaza",
        "detection_location": "1층 복도",
        "detected_at": "2024-11-22T10:30:00Z"
    },
    "guidance_result": {
        "success": true,
        "resident_info": {...},
        "guidance_messages": [...]
    }
}
```

---

## 📊 데이터 흐름

```
배회 탐지
    ↓
nickname 또는 resident_name 입력
    ↓
/api/residents/search/{keyword} API 호출
    ↓
검색 결과에서 일치하는 입소자 선택
    ↓
생활실 정보 추출 (floor_number, room_number, bed_number)
    ↓
안내 메시지 생성 (3회 반복)
    ↓
LLM에게 메시지 전달
```

---

## 🔍 사용 방법

### LLM이 자동으로 호출하는 경우

사용자가 다음과 같은 요청을 할 때 LLM이 자동으로 `guide_wandering_resident_to_room` 함수를 호출합니다:

- "배회 탐지"
- "어르신 복도에 있음"
- "생활실로 안내"
- "복귀 안내"
- "어르신이 복도에 계심"
- "배회 중인 어르신 발견"

### 함수 호출 예시

```python
# LLM이 자동으로 호출
{
    "function_name": "guide_wandering_resident_to_room",
    "arguments": {
        "nickname": "Akaza",
        "detection_location": "1층 복도"
    }
}
```

---

## 🧪 테스트 방법

### 1. 모킹 API로 테스트

```bash
curl -X POST 'http://localhost:8000/api/test/wandering-detection' \
  -H 'Content-Type: application/json' \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도"
  }'
```

### 2. LLM 채팅으로 테스트

```
사용자: "Akaza 어르신이 1층 복도에서 배회 중이에요. 생활실로 안내해주세요."
→ LLM이 자동으로 guide_wandering_resident_to_room 함수 호출
```

---

## ✅ 검증 완료

- ✅ TOOLS 리스트에 함수 정의 추가됨
- ✅ execute_function에 케이스 추가됨
- ✅ 실제 API 호출 함수 구현됨
- ✅ 안내 메시지 생성 함수 구현됨 (3회 반복)
- ✅ 에러 처리 구현됨
- ✅ 로깅 구현됨
- ✅ 테스트용 모킹 API 구현됨
- ✅ 린터 오류 없음
- ✅ 통합 테스트 완료 (TOOLS 개수: 9개)

---

## 📝 변경된 파일

1. **`src/tools.py`**
   - `guide_wandering_resident_to_room` 함수 정의 추가
   - `_search_residents` 함수 구현
   - `_guide_wandering_resident_to_room` 함수 구현
   - `execute_function`에 케이스 추가

2. **`src/main.py`**
   - `/api/test/wandering-detection` 엔드포인트 추가
   - `WanderingDetectionRequest` 모델 추가

3. **`docs/WANDERING_DETECTION_GUIDANCE_IMPLEMENTATION_PLAN.md`**
   - 구현 계획 문서 작성

4. **`docs/WANDERING_DETECTION_GUIDANCE_IMPLEMENTATION_REPORT.md`**
   - 구현 완료 리포트 작성

---

## 🎯 구현 특징

### 1. 효율적인 정보 조회
- `/api/residents/search/{keyword}` API 활용
- nickname 우선 검색, 없으면 resident_name으로 재시도
- 단일 API 호출로 정보 조회

### 2. 친절한 안내 메시지
- 3회 반복으로 주의 환기
- 각 메시지마다 다른 톤과 내용
- 생활실 정보를 명확히 포함

### 3. 에러 처리
- 어르신 정보를 찾을 수 없는 경우
- API 호출 실패 시
- 네트워크 오류 시

### 4. 테스트 지원
- 모킹 API로 쉽게 테스트 가능
- 실제 배회 탐지 시스템과 동일한 로직 사용

---

## 📚 관련 문서

- `docs/WANDERING_DETECTION_GUIDANCE_IMPLEMENTATION_PLAN.md` - 구현 계획
- `docs/RESIDENTS_API_TOOLS_INTEGRATION_REPORT.md` - residents API TOOLS 통합 리포트

---

**작성자**: AI Assistant  
**작성일**: 2024년  
**상태**: ✅ **구현 완료**

