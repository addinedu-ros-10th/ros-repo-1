# API Voice Process 업데이트 리포트

## 개요
`/api/voice/process` 엔드포인트의 오디오 스트리밍 문제를 해결하고, 더 안정적이고 사용하기 쉬운 응답 형식으로 개선했습니다.

## 발생한 문제

### 1. 오디오 스트리밍 손상 문제
- **증상**: `/api/voice/process` 엔드포인트에서 반환되는 `multipart/mixed` 응답의 오디오 데이터가 손상되거나 깨짐
- **원인**: 
  - OpenAI TTS 응답 처리 방식이 불안정 (`response.content` 접근 방식)
  - Multipart 형식의 복잡한 바운더리 처리
  - JSON 메타데이터와 오디오 데이터의 구분 문제

### 2. HTTP 헤더 인코딩 에러
- **증상**: `response_format=audio` 요청 시 `UnicodeEncodeError: 'latin-1' codec can't encode characters`
- **원인**: HTTP 헤더는 `latin-1` 인코딩만 지원하는데, 한글 텍스트를 직접 헤더에 포함시킴
  ```python
  headers={
      "X-User-Text": user_text[:200],  # 한글 포함으로 인한 에러
      "X-Assistant-Text": assistant_text[:200]
  }
  ```

## 해결 방법

### 1. 응답 형식 개선
Multipart 형식을 제거하고 더 간단하고 안정적인 JSON 응답 방식으로 변경:

#### 변경 전 (Multipart)
- 복잡한 바운더리 처리
- 오디오 데이터 손상 가능성
- 클라이언트 파싱 복잡

#### 변경 후 (JSON + Base64)
- **기본값**: JSON 응답 (텍스트 + Base64 인코딩된 오디오)
- **선택적**: 오디오만 반환 (`response_format=audio`)
- 파싱 용이, 디버깅 쉬움
- CORS 문제 없음

### 2. OpenAI TTS 응답 처리 개선
```python
# 변경 전: 복잡한 조건 분기
if hasattr(tts_response, 'content'):
    content = tts_response.content
    # ... 복잡한 처리

# 변경 후: 직접적인 read() 사용
audio_bytes = tts_response.read()
```

### 3. HTTP 헤더 인코딩 문제 해결
- 헤더에서 한글 텍스트 제거
- 텍스트 정보가 필요한 경우 JSON 응답 사용 권장

## 주요 변경사항

### 코드 변경

#### 1. Import 추가
```python
from fastapi.responses import JSONResponse
import base64
```

#### 2. 파라미터 추가
```python
response_format: Optional[str] = Query(
    default="json",
    description="응답 형식: 'json' (텍스트+Base64 오디오) 또는 'audio' (오디오만)"
)
```

#### 3. 응답 형식 분기
```python
if response_format == "audio":
    # 오디오만 반환
    return StreamingResponse(
        iter([audio_bytes]),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": "attachment; filename=response.mp3"
        }
    )
else:
    # JSON 응답 (기본값)
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    return JSONResponse(content={
        "success": True,
        "user_text": user_text,
        "assistant_text": assistant_text,
        "audio_base64": audio_base64,
        "audio_format": "mp3",
        "session_id": session_id
    })
```

## API 사용 예시

### JSON 응답 (기본값, 권장)
```bash
curl -X POST "http://localhost:8000/api/voice/process?response_format=json" \
  -F "audio=@speech.mp3"
```

**응답:**
```json
{
    "success": true,
    "user_text": "사용자 입력 텍스트",
    "assistant_text": "AI 응답 텍스트",
    "audio_base64": "Base64 인코딩된 오디오 데이터",
    "audio_format": "mp3",
    "session_id": "session_id"
}
```

### 오디오만 받기
```bash
curl -X POST "http://localhost:8000/api/voice/process?response_format=audio" \
  -F "audio=@speech.mp3" \
  -o response.mp3
```

**응답:**
- Content-Type: `audio/mpeg`
- 오디오 파일만 반환 (텍스트 정보 없음)

## 장점

### JSON 응답 방식 (기본값)
- ✅ 간단한 파싱
- ✅ 디버깅 쉬움
- ✅ CORS 문제 없음
- ✅ 텍스트와 오디오 정보 모두 포함
- ⚠️ Base64 인코딩 오버헤드 (~33% 증가)

### 오디오만 응답
- ✅ 작은 데이터 크기
- ✅ 직접 재생 가능
- ⚠️ 텍스트 정보 헤더로만 전달 불가 (한글 인코딩 문제)

## 테스트 결과

### JSON 응답
- ✅ 정상 동작 확인
- ✅ 오디오 데이터 손상 없음
- ✅ 텍스트 정보 정상 반환

### 오디오 응답
- ✅ 정상 동작 확인
- ✅ HTTP 헤더 인코딩 에러 해결
- ✅ 오디오 파일 정상 재생 가능

## 향후 개선 사항

1. **스트리밍 지원**: 대용량 오디오를 위한 스트리밍 응답
2. **압축 옵션**: Base64 오버헤드 감소를 위한 압축 옵션
3. **메타데이터 헤더**: 오디오 응답에 메타데이터를 포함할 수 있는 방법 (예: 별도 엔드포인트)

## 참고

- HTTP 헤더는 `latin-1` 인코딩만 지원하므로 한글 텍스트는 직접 포함할 수 없음
- 텍스트 정보가 필요한 경우 JSON 응답 형식 사용 권장
- OpenAI SDK v1.0+ 에서는 `response.read()` 방식 사용 권장

