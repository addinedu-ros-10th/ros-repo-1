# IOT 문 제어 기능 구현 계획

## 📋 요청 사항 정리

### 이해한 내용

1. **IOT 제어 API**
   - ESP32 서보 모터 제어 API
   - Base URL: `http://192.168.0.30:8010`
   - Endpoint: `/control/esp_32/servo1`, `/control/esp_32/servo2`

2. **서보 모터 동작**
   - **servo1**: 문 한 짝 담당
     - 열림: 0도
     - 닫힘: 180도
   - **servo2**: 문 한 짝 담당
     - 열림: 170도
     - 닫힘: 0도

3. **요구사항**
   - 두 서보를 동시에 제어하여 문을 열고 닫기
   - GPT에게 TOOLS로 제공하여 자연어로 제어 가능

### API 스펙

```bash
# servo1 제어
POST http://192.168.0.30:8010/control/esp_32/servo1
Content-Type: application/json
{
  "angle": 0  # 열림: 0도, 닫힘: 180도
}

# servo2 제어
POST http://192.168.0.30:8010/control/esp_32/servo2
Content-Type: application/json
{
  "angle": 170  # 열림: 170도, 닫힘: 0도
}
```

---

## 🎯 구현 계획

### 1. 함수 설계

#### 함수명: `control_door`

**파라미터:**
- `action` (required): "open" 또는 "close"
  - "open": 문 열기 (servo1: 0도, servo2: 170도)
  - "close": 문 닫기 (servo1: 180도, servo2: 0도)

**동작:**
- 두 서보를 동시에 제어 (비동기 병렬 호출)
- 각 서보의 성공/실패 상태를 개별적으로 확인
- 결과를 통합하여 반환

**반환값:**
```json
{
  "success": true,
  "action": "open",
  "servo1": {
    "success": true,
    "angle": 0,
    "status_code": 200
  },
  "servo2": {
    "success": true,
    "angle": 170,
    "status_code": 200
  }
}
```

### 2. 구현 단계

#### Step 1: tools.py에 함수 정의 추가
- `TOOLS` 리스트에 `control_door` 함수 정의 추가
- description에 자연어 예시 포함 (예: "문 열어줘", "문 닫아줘" 등)

#### Step 2: execute_function에 처리 로직 추가
- `control_door` 함수 처리 분기 추가
- `_control_door` 내부 함수 구현

#### Step 3: _control_door 함수 구현
- action에 따라 각 서보의 각도 결정
- `httpx.AsyncClient`로 두 API 동시 호출
- 에러 처리 및 로깅

### 3. 코드 구조

```python
# TOOLS 리스트에 추가
{
    "type": "function",
    "function": {
        "name": "control_door",
        "description": "문을 열거나 닫습니다. 사용자가 '문 열어줘', '문 열기', '문 닫아줘', '문 닫기', '문 열림', '문 닫힘' 등을 요청할 때 반드시 이 함수를 호출하세요.",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["open", "close"],
                    "description": "문 동작: 'open' (열기) 또는 'close' (닫기)"
                }
            },
            "required": ["action"]
        }
    }
}

# execute_function에 추가
elif function_name == "control_door":
    action = arguments.get("action")
    if not action:
        return {"error": "action is required (open or close)"}
    return await _control_door(action)

# _control_door 함수 구현
async def _control_door(action: str) -> Dict[str, Any]:
    IOT_BASE_URL = "http://192.168.0.30:8010"
    
    # action에 따라 각도 결정
    if action == "open":
        servo1_angle = 0
        servo2_angle = 170
    elif action == "close":
        servo1_angle = 180
        servo2_angle = 0
    else:
        return {"error": f"Invalid action: {action}. Must be 'open' or 'close'"}
    
    # 두 API 동시 호출
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = [
            client.post(
                f"{IOT_BASE_URL}/control/esp_32/servo1",
                json={"angle": servo1_angle},
                headers={"accept": "application/json", "Content-Type": "application/json"}
            ),
            client.post(
                f"{IOT_BASE_URL}/control/esp_32/servo2",
                json={"angle": servo2_angle},
                headers={"accept": "application/json", "Content-Type": "application/json"}
            )
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 처리
        servo1_result = _process_servo_response(results[0], "servo1", servo1_angle)
        servo2_result = _process_servo_response(results[1], "servo2", servo2_angle)
        
        return {
            "success": servo1_result["success"] and servo2_result["success"],
            "action": action,
            "servo1": servo1_result,
            "servo2": servo2_result
        }
```

### 4. 에러 처리

- 타임아웃: 5초
- 연결 오류: 명확한 에러 메시지
- HTTP 오류: 상태 코드 및 응답 내용 포함
- 부분 실패: 하나의 서보만 실패해도 결과에 반영

### 5. 로깅

- 함수 호출 시 로그
- 각 서보 제어 결과 로그
- 에러 발생 시 상세 로그

---

## ✅ 확인 사항

### 요청 사항 확인

1. ✅ **servo1**: 열림 0도, 닫힘 180도
2. ✅ **servo2**: 열림 170도, 닫힘 0도
3. ✅ **동시 제어**: 두 서보를 동시에 제어
4. ✅ **GPT TOOLS**: Function Calling으로 제공

### 추가 고려 사항

1. **개별 서보 제어**: 필요시 `control_servo1`, `control_servo2` 함수 추가 가능
2. **각도 직접 지정**: 필요시 `set_door_angle` 함수 추가 가능
3. **상태 확인**: 필요시 `get_door_status` 함수 추가 가능

---

## 🚀 구현 시작 여부

위 계획으로 구현을 진행할까요?

**예상 작업 시간**: 약 30분
**영향 범위**: `src/tools.py` 파일 수정

