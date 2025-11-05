# WebSocket 실시간 채팅 테스트 가이드

이 가이드는 `/ws/voice` WebSocket 엔드포인트를 테스트하는 방법을 설명합니다.

## 📋 목차

- [WebSocket 기능 개요](#websocket-기능-개요)
- [테스트 방법](#테스트-방법)
  - [방법 1: HTML 웹 페이지 (가장 쉬움)](#방법-1-html-웹-페이지-가장-쉬움)
  - [방법 2: Python 클라이언트](#방법-2-python-클라이언트)
  - [방법 3: wscat CLI 도구](#방법-3-wscat-cli-도구)
  - [방법 4: 브라우저 개발자 도구](#방법-4-브라우저-개발자-도구)
- [메시지 형식](#메시지-형식)
- [문제 해결](#문제-해결)

---

## WebSocket 기능 개요

### 제공 기능

- ✅ **실시간 양방향 통신**: WebSocket을 통한 실시간 메시지 송수신
- ✅ **스트리밍 응답**: ChatGPT 응답을 실시간으로 스트리밍하여 전송
- ✅ **세션 관리**: 각 WebSocket 연결마다 고유한 세션 ID 생성 및 관리
- ✅ **대화 히스토리**: Redis 및 PostgreSQL에 대화 히스토리 자동 저장

### 엔드포인트

```
ws://localhost:8000/ws/voice
```

또는

```
wss://your-domain.com/ws/voice  (HTTPS 환경)
```

---

## 테스트 방법

### 방법 1: HTML 웹 페이지 (가장 쉬움)

#### 1. 서버 실행

```bash
# Docker Compose로 실행
docker-compose up -d

# 또는 로컬에서 실행
uvicorn main:app --reload
```

#### 2. 테스트 페이지 열기

`test_websocket.html` 파일을 브라우저에서 열기:

```bash
# 파일 경로 확인
cd AI/llm-gateway
ls -la test_websocket.html

# 브라우저에서 열기
# Linux: xdg-open test_websocket.html
# Mac: open test_websocket.html
# Windows: start test_websocket.html
```

또는 간단한 HTTP 서버 실행:

```bash
# Python 3
python -m http.server 8080

# 브라우저에서 접속
# http://localhost:8080/test_websocket.html
```

#### 3. 사용 방법

1. "연결" 버튼 클릭
2. 메시지 입력 후 "전송" 버튼 클릭 또는 Enter 키
3. AI 응답이 실시간으로 스트리밍되어 표시됨

#### 특징

- ✅ 직관적인 UI
- ✅ 실시간 스트리밍 응답 시각화
- ✅ 연결 상태 표시
- ✅ 채팅 히스토리 확인

---

### 방법 2: Python 클라이언트

#### 1. 의존성 설치

```bash
pip install websockets
```

#### 2. 인터랙티브 모드 실행

```bash
python test_websocket.py
```

또는 명시적으로:

```bash
python test_websocket.py --interactive
```

#### 3. 사용 방법

```
💬 메시지 입력: 안녕하세요
👤 사용자: 안녕하세요
🤖 AI: 안녕하세요! 무엇을 도와드릴까요?
💬 메시지 입력: 오늘 날씨는 어때?
👤 사용자: 오늘 날씨는 어때?
🤖 AI: 오늘 날씨에 대한 정보를 제공할 수 없습니다...
💬 메시지 입력: quit
```

#### 4. 단일 메시지 모드

```bash
python test_websocket.py --message "안녕하세요"
```

#### 5. 다른 서버 URI 사용

```bash
python test_websocket.py --uri ws://your-server:8000/ws/voice
```

#### 특징

- ✅ 스크립트로 자동화 가능
- ✅ 실시간 스트리밍 응답 표시
- ✅ 인터랙티브 및 단일 메시지 모드 지원

---

### 방법 3: wscat CLI 도구

#### 1. wscat 설치

```bash
# npm을 통한 설치
npm install -g wscat

# 또는 npx 사용 (설치 없이)
npx wscat -c ws://localhost:8000/ws/voice
```

#### 2. 연결 및 테스트

```bash
# 연결
wscat -c ws://localhost:8000/ws/voice

# 연결 후 메시지 전송
> {"type":"text","message":"안녕하세요"}
```

#### 응답 예시

```
< {"type":"text_chunk","content":"안녕"}
< {"type":"text_chunk","content":"하세요"}
< {"type":"text_chunk","content":"!"}
< {"type":"text_chunk","content":" 무엇을"}
< {"type":"text_chunk","content":" 도와드릴까요?"}
< {"type":"text_complete","full_response":"안녕하세요! 무엇을 도와드릴까요?"}
```

#### 특징

- ✅ CLI 환경에서 빠른 테스트
- ✅ JSON 형식으로 직접 메시지 전송
- ✅ 모든 응답 청크 확인 가능

---

### 방법 4: 브라우저 개발자 도구

#### 1. 브라우저 콘솔 열기

Chrome/Edge/Firefox에서 `F12` 또는 `Ctrl+Shift+I` (Mac: `Cmd+Option+I`)

#### 2. WebSocket 연결 생성

콘솔에 다음 코드 입력:

```javascript
// WebSocket 연결
const ws = new WebSocket('ws://localhost:8000/ws/voice');

// 연결 성공
ws.onopen = () => {
    console.log('✅ 연결됨');
    
    // 메시지 전송
    ws.send(JSON.stringify({
        type: 'text',
        message: '안녕하세요'
    }));
};

// 메시지 수신
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 수신:', data);
    
    if (data.type === 'text_chunk') {
        console.log('스트리밍:', data.content);
    } else if (data.type === 'text_complete') {
        console.log('완료:', data.full_response);
    }
};

// 오류 처리
ws.onerror = (error) => {
    console.error('❌ 오류:', error);
};

// 연결 종료
ws.onclose = () => {
    console.log('👋 연결 종료');
};

// 연결 종료 (필요시)
// ws.close();
```

#### 특징

- ✅ 브라우저에서 바로 테스트
- ✅ 개발자 도구로 디버깅 용이
- ✅ 네트워크 탭에서 WebSocket 트래픽 확인 가능

---

## 메시지 형식

### 클라이언트 → 서버

```json
{
  "type": "text",
  "message": "사용자 메시지 내용"
}
```

### 서버 → 클라이언트

#### 1. 스트리밍 응답 (부분)

```json
{
  "type": "text_chunk",
  "content": "응답의 일부"
}
```

#### 2. 완료 응답

```json
{
  "type": "text_complete",
  "full_response": "전체 응답 내용"
}
```

### 메시지 흐름 예시

```
클라이언트: {"type":"text","message":"안녕"}
서버:       {"type":"text_chunk","content":"안녕"}
서버:       {"type":"text_chunk","content":"하세요"}
서버:       {"type":"text_chunk","content":"!"}
서버:       {"type":"text_complete","full_response":"안녕하세요!"}
```

---

## 문제 해결

### 1. 연결 실패

**증상**: `Connection refused` 또는 `Failed to connect`

**해결 방법**:
- 서버가 실행 중인지 확인: `docker-compose ps` 또는 `curl http://localhost:8000/`
- 포트가 올바른지 확인 (기본값: 8000)
- 방화벽 설정 확인
- Docker Compose 사용 시 네트워크 설정 확인

### 2. CORS 오류 (브라우저에서)

**증상**: CORS 정책 오류

**해결 방법**:
- `.env` 파일에서 `CORS_ORIGINS` 설정 확인
- 서버 재시작

### 3. 메시지 형식 오류

**증상**: `Invalid message format` 또는 응답 없음

**해결 방법**:
- 메시지가 올바른 JSON 형식인지 확인
- `type` 필드가 `"text"`인지 확인
- `message` 필드가 문자열인지 확인

### 4. 응답이 없음

**증상**: 메시지를 보냈지만 응답이 없음

**해결 방법**:
- 서버 로그 확인: `docker-compose logs -f llm-gateway`
- OpenAI API 키가 올바르게 설정되었는지 확인
- 네트워크 연결 확인

### 5. 스트리밍이 보이지 않음

**증상**: 부분 응답(`text_chunk`)이 보이지 않고 완료 응답만 보임

**해결 방법**:
- 클라이언트가 `text_chunk` 메시지를 처리하는지 확인
- 네트워크 지연이 있을 수 있음 (정상 동작)
- Python 클라이언트는 자동으로 스트리밍 표시

---

## 고급 사용법

### 1. 커스텀 세션 ID

현재는 WebSocket 연결마다 자동으로 세션 ID가 생성됩니다. 
세션 ID를 지정하려면 서버 코드를 수정해야 합니다.

### 2. 여러 메시지 연속 전송

```javascript
// JavaScript 예시
const messages = ['안녕', '날씨는?', '고마워'];
for (const msg of messages) {
    ws.send(JSON.stringify({
        type: 'text',
        message: msg
    }));
    await new Promise(resolve => setTimeout(resolve, 1000)); // 1초 대기
}
```

### 3. 재연결 로직

```javascript
function connectWithRetry(maxRetries = 5) {
    let retries = 0;
    
    function connect() {
        const ws = new WebSocket('ws://localhost:8000/ws/voice');
        
        ws.onopen = () => {
            console.log('✅ 연결됨');
            retries = 0;
        };
        
        ws.onerror = (error) => {
            console.error('❌ 연결 오류:', error);
            retries++;
            
            if (retries < maxRetries) {
                console.log(`${retries}번째 재연결 시도...`);
                setTimeout(connect, 1000 * retries); // 지수 백오프
            } else {
                console.error('❌ 최대 재시도 횟수 초과');
            }
        };
        
        return ws;
    }
    
    return connect();
}
```

---

## 참고 자료

- [FastAPI WebSocket 문서](https://fastapi.tiangolo.com/advanced/websockets/)
- [MDN WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [websockets Python 라이브러리](https://websockets.readthedocs.io/)

---

## 테스트 체크리스트

- [ ] 서버가 실행 중인지 확인
- [ ] WebSocket 연결 성공
- [ ] 텍스트 메시지 전송 성공
- [ ] 스트리밍 응답 수신 확인 (`text_chunk`)
- [ ] 완료 응답 수신 확인 (`text_complete`)
- [ ] 여러 메시지 연속 전송 테스트
- [ ] 연결 종료 테스트
- [ ] 재연결 테스트

---

**테스트 중 문제가 발생하면 서버 로그를 확인하세요:**

```bash
docker-compose logs -f llm-gateway
```

