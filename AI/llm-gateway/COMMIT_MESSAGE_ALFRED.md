feat(ui): Alfred 키워드 기반 음성 인터페이스 테스트 프로그램 개발

## 주요 기능 추가

### 1. 키워드 기반 음성 인터페이스 테스트 프로그램
- Web Speech API를 사용한 영어 "alfred" 키워드 감지
- STT → ChatGPT → TTS 전체 프로세스 통합
- JSON 응답 처리 (Base64 오디오 디코딩 및 재생)
- 텍스트-음성 재생 동기화
- 실시간 오디오 레벨 미터 (데시벨 표시)
- 설정 패널 (파라미터 조절 기능)

### 2. 정적 파일 서빙 구성 (404 에러 해결)
- FastAPI에 StaticFiles 추가
- /tests 경로에 tests/user_testing 디렉토리 마운트
- Dockerfile에 tests 디렉토리 복사 추가
- .dockerignore에서 tests 디렉토리 제외 주석 처리

### 3. 키워드 감지 개선
- 유연한 키워드 매칭 (정규식 + 단순 포함)
- interim/final 결과 모두 확인
- 중복 트리거 방지 로직 추가
- 자동 재시작 및 재시도 로직 개선

### 4. 연속 대화 지원
- 오디오 재생 완료 후 자동 키워드 감지 재시작
- 오디오 레벨 측정 지속 (연속 대화 중에도 활성화)
- API 응답 처리 후 recognition 상태 확인 및 재시작
- autoWaitMode로 자동 대기 모드 지원

### 5. 실시간 오디오 레벨 미터
- Web Audio API 기반 RMS 계산
- 데시벨(dB) 실시간 표시
- 시각적 피드백 (레벨 바 + 색상 변경)
- 마이크 입력 상태 시각적 확인 가능

## 변경된 파일

### 신규 파일
- tests/user_testing/test_alfred_voice.html: 키워드 기반 음성 인터페이스 테스트 프로그램
- docs/ALFRED_VOICE_INTERFACE_UPDATE.md: 개발 리포트

### 수정된 파일
- src/main.py: 정적 파일 서빙 추가 (StaticFiles)
- Dockerfile: tests 디렉토리 복사 추가
- .dockerignore: tests 디렉토리 제외 주석 처리

## 테스트 방법
- URL: http://localhost:8000/tests/test_alfred_voice.html
- "시작" 버튼 클릭 → "alfred" 키워드 감지 → 한국어 질문 → 연속 대화 진행

## 참고 문서
- docs/ALFRED_VOICE_INTERFACE_UPDATE.md: 상세 개발 리포트




