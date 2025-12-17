# 어르신 배회 탐지 시 생활관 복귀 안내 기능 구현 계획

**작성일**: 2024년  
**목적**: 순찰 중 어르신 배회 탐지 시 생활관 복귀 안내 기능 구현

---

## 📋 요구사항 분석

### 1. 기능 요구사항
- 순찰 중 어르신 배회 탐지 시 자동으로 생활관 복귀 안내
- 어르신 성함 또는 nickname 기반으로 정보 조회
- 안내 메시지를 최소 3회 친절하게 반복
- TOOLS API를 활용한 정보 조회 및 안내 메시지 전달

### 2. 비기능 요구사항
- 친절하고 명확한 안내 메시지
- 반복적인 안내로 어르신의 주의 환기
- 어르신 정보 기반 맞춤형 안내

---

## 🎯 구현 계획

### 1. 어르신 정보 조회 방법

#### 방법 A: 검색 API 활용 (권장) ⭐
- **API**: `/api/residents/search/{keyword}` (이미 존재)
- **장점**: 
  - nickname, user_name, resident_number 등으로 직접 검색 가능
  - 여러 결과 반환 가능 (중복 이름 처리 용이)
  - 서버 측 API 수정 불필요
- **사용법**: 
  - `nickname` 또는 `resident_name`을 keyword로 전달
  - 결과에서 첫 번째 항목 선택 (또는 가장 일치하는 항목)

#### 방법 B: 사용자 목록 조회 후 필터링
- **API**: `/api/users/list` + `/api/residents/{user_id}`
- **단점**: 
  - 2단계 API 호출 필요
  - 전체 사용자 목록을 조회해야 함 (비효율적)

**선택**: 방법 A (검색 API 활용) ⭐

---

### 2. 안내 메시지 구조

#### 메시지 구성 요소
1. **인사**: 어르신을 부르는 방식 (성함 또는 nickname)
2. **상황 설명**: 배회 탐지 상황 설명
3. **생활실 정보**: 생활실 번호, 층수, 침대 번호
4. **복귀 안내**: 생활관으로 복귀하도록 안내
5. **안전 강조**: 안전을 위한 복귀 필요성 강조

#### 메시지 예시
```
[1회차]
안녕하세요, {nickname} 어르신! 지금 복도에서 어르신을 발견했습니다. 
어르신의 생활실은 {floor_number}층 {room_number}호입니다. 
안전을 위해 생활실로 복귀해 주시겠어요?

[2회차]
{user_name} 어르신, 지금 복도에 계시는 것으로 보입니다. 
{floor_number}층 {room_number}호 생활실로 돌아가 주시면 감사하겠습니다. 
혼자 계시면 위험할 수 있으니 생활실로 복귀해 주세요.

[3회차]
어르신, {nickname} 어르신! 지금 복도에 계신 것으로 탐지되었습니다. 
생활실은 {floor_number}층 {room_number}호입니다. 
제가 함께 생활실로 안내해 드릴까요? 안전을 위해 생활실로 복귀해 주시기 바랍니다.
```

---

### 3. 함수 구현 계획

#### 함수명: `guide_wandering_resident_to_room`

**파라미터**:
- `resident_name` (string, optional): 어르신 성함
- `nickname` (string, optional): 어르신 nickname
- `detection_location` (string, optional): 탐지 위치 (예: "1층 복도", "2층 로비")

**로직 흐름**:
1. `nickname` 우선으로 `/api/residents/search/{keyword}` API 호출
2. 결과가 없으면 `resident_name`으로 재시도
3. 일치하는 입소자 정보 찾기 (첫 번째 결과 또는 가장 일치하는 결과)
4. 생활실 정보 추출 (floor_number, room_number, bed_number)
5. 안내 메시지 생성 (3회 반복)
6. 메시지 반환

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
    "detection_location": "..."
}
```

---

### 4. TOOLS 함수 정의

```python
{
    "type": "function",
    "function": {
        "name": "guide_wandering_resident_to_room",
        "description": "순찰 중 어르신 배회가 탐지된 경우 생활관 복귀를 안내합니다. 어르신의 성함 또는 nickname을 기반으로 정보를 조회하고, 친절한 안내 메시지를 최소 3회 반복하여 전달합니다. 사용자가 '배회 탐지', '어르신 복도에 있음', '생활실로 안내', '복귀 안내' 등을 언급할 때 반드시 이 함수를 호출하세요.",
        "parameters": {
            "type": "object",
            "properties": {
                "resident_name": {
                    "type": "string",
                    "description": "어르신의 성함 (예: '정도현', '한기문')"
                },
                "nickname": {
                    "type": "string",
                    "description": "어르신의 nickname (예: 'Akaza', 'Gyomei Himejima')"
                },
                "detection_location": {
                    "type": "string",
                    "description": "배회 탐지 위치 (예: '1층 복도', '2층 로비', '3층 계단')"
                }
            },
            "required": []
        }
    }
}
```

---

### 5. 테스트용 모킹 API

#### 엔드포인트: `/api/test/wandering-detection`

**Method**: `POST`

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
    }
}
```

**기능**:
- 배회 탐지 시뮬레이션
- 실제 안내 함수 호출 트리거
- 테스트 및 디버깅 용도

---

## 🔄 구현 순서

1. **어르신 정보 조회 헬퍼 함수 구현**
   - `_find_resident_by_name_or_nickname(name: str, nickname: str) -> Optional[str]`
   - 사용자 목록 조회 및 필터링

2. **안내 메시지 생성 함수 구현**
   - `_generate_guidance_messages(resident_info: dict, detection_location: str) -> List[str]`
   - 3회 반복 메시지 생성

3. **메인 함수 구현**
   - `guide_wandering_resident_to_room(resident_name: str, nickname: str, detection_location: str) -> Dict[str, Any]`
   - 전체 로직 통합

4. **TOOLS에 함수 추가**
   - TOOLS 리스트에 함수 정의 추가
   - execute_function에 케이스 추가

5. **테스트용 모킹 API 구현**
   - `/api/test/wandering-detection` 엔드포인트 추가
   - FastAPI 라우터에 등록

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

## ⚠️ 고려사항

### 1. 이름 매칭
- 정확한 일치 우선
- 부분 일치도 고려 (예: "정도현" → "정도현 어르신")
- nickname 우선 매칭 (더 친근함)

### 2. 중복 이름 처리
- 동일한 이름이 여러 명인 경우
- user_id를 명시하거나 추가 정보 요청

### 3. 정보 없음 처리
- 어르신 정보를 찾을 수 없는 경우
- 일반적인 안내 메시지 제공

### 4. 메시지 톤
- 친절하고 존중하는 톤
- 명확하고 간결한 표현
- 반복을 통한 주의 환기

---

## 🧪 테스트 시나리오

### 시나리오 1: nickname으로 조회
- Input: `nickname="Akaza"`
- Expected: 정도현 어르신 정보 조회 및 안내 메시지 생성

### 시나리오 2: 성함으로 조회
- Input: `resident_name="정도현"`
- Expected: 정도현 어르신 정보 조회 및 안내 메시지 생성

### 시나리오 3: 탐지 위치 포함
- Input: `nickname="Akaza"`, `detection_location="1층 복도"`
- Expected: 위치 정보가 포함된 안내 메시지

### 시나리오 4: 정보 없음
- Input: `nickname="존재하지않는닉네임"`
- Expected: 에러 메시지 및 일반 안내

---

## 📝 구현 피드백 요청 사항

1. **안내 메시지 톤**: 현재 제안한 톤이 적절한가요? 더 친절하거나 더 명확해야 할까요?

2. **반복 횟수**: 최소 3회 반복이 적절한가요? 더 많거나 적어야 할까요?

3. **정보 조회 방법**: 기존 API 활용(방법 A)이 적절한가요? 새로운 API 엔드포인트가 필요한가요?

4. **탐지 위치**: detection_location 파라미터가 필요한가요? 자동으로 감지할 수 있나요?

5. **에러 처리**: 어르신 정보를 찾을 수 없는 경우 어떻게 처리해야 할까요?

6. **추가 기능**: 생활실로 안내하는 것 외에 추가로 필요한 기능이 있나요? (예: 가족 연락, 직원 호출 등)

---

**작성자**: AI Assistant  
**작성일**: 2024년  
**상태**: ⏳ **피드백 대기 중**

