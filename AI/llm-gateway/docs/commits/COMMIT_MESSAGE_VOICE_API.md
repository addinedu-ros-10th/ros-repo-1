fix(api): /api/voice/process 엔드포인트 오디오 스트리밍 문제 해결 및 응답 형식 개선

## 문제 해결
- OpenAI TTS 응답 처리 오류 수정
  - response.read() 방식으로 변경하여 안정적인 오디오 데이터 읽기
  - 복잡한 multipart 형식 제거

- HTTP 헤더 인코딩 에러 해결
  - 한글 텍스트를 헤더에 포함 시도로 인한 UnicodeEncodeError 해결
  - 헤더에서 텍스트 정보 제거 (latin-1 인코딩 제약)

## 주요 변경사항

### 1. 응답 형식 개선
- Multipart 형식에서 JSON 응답 방식으로 변경 (기본값)
- response_format 파라미터 추가 (json/audio 선택 가능)
- JSON 응답: 텍스트 + Base64 인코딩된 오디오
- Audio 응답: 오디오 파일만 반환

### 2. 코드 개선
- base64, JSONResponse import 추가
- OpenAI TTS 응답을 response.read()로 직접 읽기
- 간결하고 안정적인 응답 처리 로직

### 3. API 문서화
- response_format 파라미터 문서화
- 사용 예시 및 장단점 설명 추가

## 테스트 결과
- ✅ JSON 응답: 정상 동작, 오디오 데이터 손상 없음
- ✅ Audio 응답: HTTP 헤더 인코딩 에러 해결, 오디오 파일 정상 재생

## 참고 문서
- docs/API_VOICE_PROCESS_UPDATE.md: 상세 업데이트 리포트

