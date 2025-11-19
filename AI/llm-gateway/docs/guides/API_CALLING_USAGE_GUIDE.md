# API 호출 기능 사용 가이드

**작성일**: 2025-11-19  
**버전**: 1.0.0

---

## 📋 개요

채팅 인터페이스를 통해 자연어로 API를 호출할 수 있습니다. GPT가 사용자의 요청을 이해하고 적절한 API를 자동으로 호출합니다.

---

## 🎯 사용 가능한 API

### 1. 사용자 목록 조회

**API 엔드포인트**: `GET /api/users/list`

**기능**: 사용자 목록을 페이지네이션과 역할 필터링으로 조회합니다.

**채팅 명령어 예시:**
```
"사용자 목록을 보여줘"
"care_target 역할 사용자 목록 조회해줘"
"사용자 리스트를 1페이지부터 100개씩 가져와줘"
"사용자 목록을 페이지 2, 크기 50으로 조회해줘"
```

**파라미터:**
- `page` (선택): 페이지 번호 (기본값: 1)
- `size` (선택): 페이지당 항목 수 (기본값: 100)
- `role` (선택): 사용자 역할 필터 (`care_target`, `caregiver`)

---

### 2. 사용자 프로필 조회

**API 엔드포인트**: `GET /api/user-profiles/{user_id}`

**기능**: 특정 사용자의 상세 프로필 정보를 조회합니다.

**채팅 명령어 예시:**
```
"사용자 10fa45f2-f375-41c9-a62a-093efcd01bd3의 프로필을 보여줘"
"10fa45f2-f375-41c9-a62a-093efcd01bd3 사용자 정보 조회해줘"
"사용자 프로필을 가져와줘 (ID: 10fa45f2-f375-41c9-a62a-093efcd01bd3)"
```

**파라미터:**
- `user_id` (필수): 사용자 UUID

---

### 3. 사용자 관계 정보 조회

**API 엔드포인트**: `GET /api/user-relationships/user/{user_id}/{relationship_type}`

**기능**: 특정 사용자의 관계 정보를 조회합니다.

**채팅 명령어 예시:**
```
"사용자 10fa45f2-f375-41c9-a62a-093efcd01bd3의 관계 정보를 보여줘"
"10fa45f2-f375-41c9-a62a-093efcd01bd3 사용자의 caregiver 관계 조회해줘"
"사용자 관계 정보를 가져와줘 (ID: 10fa45f2-f375-41c9-a62a-093efcd01bd3, 타입: as-target)"
```

**파라미터:**
- `user_id` (필수): 사용자 UUID
- `relationship_type` (선택): 관계 타입 (`as-target`, `as-caregiver`, 기본값: `as-target`)

---

## 💬 채팅 명령어 가이드

### 기본 사용법

1. **채팅 인터페이스 접속**
   - URL: `http://localhost:8001/tests/user_testing/test_chat_interface.html`

2. **자연어로 요청**
   - 예: "사용자 목록을 보여줘"
   - 예: "10fa45f2-f375-41c9-a62a-093efcd01bd3 사용자 프로필 조회해줘"

3. **GPT가 자동으로 API 호출**
   - GPT가 요청을 분석하여 적절한 함수를 선택
   - 함수가 실제 API를 호출
   - 결과를 GPT가 사용자에게 설명

---

### 명령어 예시 모음

#### 사용자 목록 조회

```
✅ "사용자 목록을 보여줘"
✅ "care_target 역할 사용자 목록 조회해줘"
✅ "사용자 리스트를 가져와줘"
✅ "사용자 목록을 페이지 1, 크기 50으로 조회해줘"
✅ "caregiver 역할 사용자를 2페이지부터 20개씩 보여줘"
```

#### 사용자 프로필 조회

```
✅ "사용자 10fa45f2-f375-41c9-a62a-093efcd01bd3의 프로필을 보여줘"
✅ "10fa45f2-f375-41c9-a62a-093efcd01bd3 사용자 정보 조회해줘"
✅ "사용자 프로필을 가져와줘 (ID: 10fa45f2-f375-41c9-a62a-093efcd01bd3)"
✅ "이 사용자의 상세 정보를 보여줘: 10fa45f2-f375-41c9-a62a-093efcd01bd3"
```

#### 사용자 관계 정보 조회

```
✅ "사용자 10fa45f2-f375-41c9-a62a-093efcd01bd3의 관계 정보를 보여줘"
✅ "10fa45f2-f375-41c9-a62a-093efcd01bd3 사용자의 caregiver 관계 조회해줘"
✅ "사용자 관계 정보를 가져와줘 (ID: 10fa45f2-f375-41c9-a62a-093efcd01bd3)"
✅ "이 사용자를 대상으로 하는 관계 정보를 보여줘: 10fa45f2-f375-41c9-a62a-093efcd01bd3"
```

---

## 🔄 동작 흐름

### 예시: 사용자 목록 조회

```
1. 사용자: "사용자 목록을 보여줘"
   ↓
2. GPT 분석: "get_users_list 함수를 호출해야겠다"
   ↓
3. 함수 실행: GET /api/users/list?page=1&size=100
   ↓
4. API 응답: {"users": [...], "total": 100, ...}
   ↓
5. GPT 응답: "사용자 목록을 조회했습니다. 총 100명의 사용자가 있습니다..."
```

---

## 📊 응답 형식

### 성공 응답

```json
{
  "success": true,
  "status_code": 200,
  "data": {
    "users": [...],
    "total": 100,
    "page": 1,
    "size": 100
  },
  "url": "http://ec2-54-180-206-205.ap-northeast-2.compute.amazonaws.com/api/users/list?page=1&size=100"
}
```

### 에러 응답

```json
{
  "error": "Connection error",
  "url": "http://...",
  "message": "Could not connect to the server"
}
```

---

## 🧪 테스트 방법

### 1. 채팅 인터페이스에서 테스트

1. `http://localhost:8001/tests/user_testing/test_chat_interface.html` 접속
2. 채팅창에 명령어 입력
3. GPT 응답 확인

### 2. API 직접 호출 테스트

```bash
# 사용자 목록 조회
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "사용자 목록을 보여줘",
    "session_id": "test-session"
  }'

# 사용자 프로필 조회
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "사용자 10fa45f2-f375-41c9-a62a-093efcd01bd3의 프로필을 보여줘",
    "session_id": "test-session"
  }'
```

---

## ⚠️ 주의사항

### 1. 사용자 ID 형식
- UUID 형식이어야 합니다 (예: `10fa45f2-f375-41c9-a62a-093efcd01bd3`)
- 잘못된 형식이면 API 호출이 실패할 수 있습니다

### 2. 네트워크 연결
- 외부 API 서버에 접근 가능해야 합니다
- 방화벽 설정을 확인하세요

### 3. 타임아웃
- API 호출 타임아웃은 10초입니다
- 응답이 느린 경우 타임아웃이 발생할 수 있습니다

---

## 🔧 문제 해결

### API 호출 실패 시

1. **연결 오류**
   - 외부 API 서버가 실행 중인지 확인
   - 네트워크 연결 확인

2. **인증 오류**
   - API 키가 필요한 경우 설정 확인
   - 헤더에 인증 정보 추가 필요

3. **잘못된 파라미터**
   - 사용자 ID 형식 확인
   - 필수 파라미터 확인

---

## 📚 관련 문서

- [Function Calling 구현 가이드](../development/LLM_API_CALLING_IMPLEMENTATION.md)
- [외부 API 호출 가이드](../development/EXTERNAL_API_CALLING_GUIDE.md)
- [API 추가 방법 가이드](./ADDING_NEW_API_GUIDE.md)

---

**업데이트**: 2025-11-19

