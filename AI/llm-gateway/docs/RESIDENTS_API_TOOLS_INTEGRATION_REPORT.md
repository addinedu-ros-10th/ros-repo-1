# residents API TOOLS 통합 리포트

**작성일**: 2024년  
**목적**: `/api/residents/` API를 LLM TOOLS에 추가

---

## ✅ 완료 사항

### 1. TOOLS 리스트에 함수 정의 추가

**파일**: `src/tools.py`

**추가된 함수**:
- `get_resident_info`: 요양원 입소자(어르신)의 상세 정보를 조회하는 함수

**함수 설명**:
- 입소자 정보, 복약 일정, 특이사항, 응급 연락처, 보험 정보, 의료 기관 정보 등을 포함
- 사용자가 '입소자 정보', '어르신 정보', '요양원 정보', '복약 일정', '응급 연락처' 등을 요청할 때 호출

**파라미터**:
- `user_id` (필수): 입소자(어르신)의 UUID

---

### 2. execute_function에 케이스 추가

**파일**: `src/tools.py`

**추가된 케이스**:
```python
elif function_name == "get_resident_info":
    user_id = arguments.get("user_id")
    if not user_id:
        return {"error": "user_id is required"}
    return await _get_resident_info(user_id)
```

---

### 3. 실제 API 호출 함수 구현

**파일**: `src/tools.py`

**구현된 함수**: `_get_resident_info(user_id: str)`

**기능**:
- `/api/residents/{user_id}` API 호출
- 타임아웃: 10초
- 에러 처리: TimeoutException, HTTPStatusError, ConnectError 등

**응답 형식**:
```python
{
    "success": True,
    "status_code": 200,
    "data": {
        # residents API 응답 데이터
        "user_name": "정도현",
        "resident_number": "R-2024-001",
        "nickname": "Akaza",
        "medication_schedule": [...],
        "special_notes": {...},
        "emergency_contacts": [...],
        # ... 기타 모든 필드
    },
    "url": "http://..."
}
```

---

## 📊 통합 결과

### TOOLS 목록 (총 8개)

1. `get_users_list` - 사용자 목록 조회
2. `get_user_profile` - 사용자 프로필 조회
3. `get_user_relationships` - 사용자 관계 정보 조회
4. **`get_resident_info`** - 입소자(어르신) 상세 정보 조회 ⭐ **신규 추가**
5. `control_door` - 문 제어
6. `start_customized_mobile_conversation` - 맞춤형 이동식 대화 시작
7. `activate_tracking` - 추종 기능 활성화
8. `end_customized_mobile_conversation` - 맞춤형 이동식 대화 종료

---

## 🔍 API 엔드포인트

**URL**: `http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com/api/residents/{user_id}`

**Method**: `GET`

**Headers**: 
- `accept: application/json`

**Response**: 입소자 상세 정보 (JSON)

---

## 📋 응답 데이터 구조

### 주요 필드

- **기본 정보**: `user_name`, `email`, `phone_number`, `resident_number`, `nickname`
- **입소 정보**: `admission_date`, `discharge_date`, `room_number`, `floor_number`, `bed_number`
- **ADL 수준**: `adl_level`, `mobility_level`, `cognitive_level`
- **복약 관리**: `medication_schedule`, `medication_notes`
- **특이사항**: `special_notes` (건강, 정서, 행동, 심리)
- **사건/사고**: `incidents`
- **식이 제한**: `dietary_restrictions`
- **응급 연락처**: `emergency_contacts`
- **보험 정보**: `insurance_info`
- **의료 기관**: `medical_facility_info`
- **요양 등급**: `care_level`
- **보호자 정보**: `guardian_name`, `guardian_relationship`, `guardian_phone`

---

## 🚀 사용 방법

### LLM이 자동으로 호출하는 경우

사용자가 다음과 같은 요청을 할 때 LLM이 자동으로 `get_resident_info` 함수를 호출합니다:

- "입소자 정보 보여줘"
- "어르신 정보 조회"
- "요양원 정보 확인"
- "복약 일정 알려줘"
- "응급 연락처 보여줘"
- "의료 정보 확인"
- "보험 정보 조회"
- "생활실 정보"
- "ADL 수준 확인"
- "특이사항 알려줘"
- "사건/사고 기록 보여줘"
- "식이 제한 확인"

### 함수 호출 예시

```python
# LLM이 자동으로 호출
{
    "function_name": "get_resident_info",
    "arguments": {
        "user_id": "00000000-0000-0000-0000-000000000001"
    }
}
```

---

## ✅ 검증 완료

- ✅ TOOLS 리스트에 함수 정의 추가됨
- ✅ execute_function에 케이스 추가됨
- ✅ 실제 API 호출 함수 구현됨
- ✅ 에러 처리 구현됨
- ✅ 로깅 구현됨
- ✅ 린터 오류 없음
- ✅ 통합 테스트 완료 (TOOLS 개수: 8개)

---

## 📝 관련 파일

- `src/tools.py` - TOOLS 정의 및 구현
- `src/system_prompt_builder.py` - System Prompt 빌더 (TOOLS 목록 포함)
- `src/main.py` - LLM API 엔드포인트 (TOOLS 사용)

---

**작성자**: AI Assistant  
**작성일**: 2024년  
**상태**: ✅ **완료**

