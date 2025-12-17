# 포트 변경 검증 계획

**작성일**: 2025-11-19  
**변경 내용**: 
- llm-gateway 외부 포트: 8000 → 8001
- redis 외부 포트: 6379 → 16379

---

## 📋 변경 사항 요약

### Docker Compose 포트 매핑
- **llm-gateway**: `${SERVER_PORT:-8001}:8000` (외부:8001, 내부:8000)
- **redis**: `${REDIS_EXTERNAL_PORT:-16379}:6379` (외부:16379, 내부:6379)

### 코드 변경 사항
1. **테스트 HTML 파일들** (localhost:8000 → localhost:8001)
   - `test_ui_ux_improvements.html`
   - `test_alfred_voice.html`
   - `test_voice.html`
   - `test_voiceprint_management.html`
   - `test_websocket.html`
   - `test_chat_interface.html` (window.location.origin 사용, 자동 대응)

2. **테스트 Python 파일들**
   - `test_websocket.py` (ws://localhost:8001)
   - `test_keyword_voiceprint_api.py` (http://localhost:8001)

3. **JavaScript 파일들**
   - `test_ui_ux_improvements.js`

---

## ✅ 검증 계획

### Phase 1: 컨테이너 및 포트 확인

#### 1.1 Docker Compose 포트 매핑 확인
```bash
# 컨테이너 시작
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/AI/llm-gateway
docker-compose up -d

# 포트 매핑 확인
docker-compose ps
# 또는
docker ps --format "table {{.Names}}\t{{.Ports}}"

# 예상 결과:
# llm-gateway        0.0.0.0:8001->8000/tcp
# llm-gateway-redis  0.0.0.0:16379->6379/tcp
```

#### 1.2 포트 리스닝 확인
```bash
# llm-gateway 포트 확인
netstat -tuln | grep 8001
# 또는
ss -tuln | grep 8001
# 또는
lsof -i :8001

# redis 포트 확인
netstat -tuln | grep 16379
# 또는
ss -tuln | grep 16379
# 또는
lsof -i :16379
```

---

### Phase 2: API 엔드포인트 검증

#### 2.1 Health Check API
```bash
# 기본 Health Check
curl http://localhost:8001/

# 예상 응답:
# {
#   "status": "running",
#   "service": "Voice Interface API",
#   "version": "1.0.0",
#   ...
# }
```

#### 2.2 Swagger UI 접근
```bash
# 브라우저에서 접속
open http://localhost:8001/docs
# 또는
curl http://localhost:8001/docs
```

#### 2.3 주요 API 엔드포인트 테스트
```bash
# STT API 테스트 (파일 필요)
# curl -X POST "http://localhost:8001/api/stt" -F "audio=@test.wav"

# Chat API 테스트
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕하세요",
    "session_id": "test-session"
  }'

# System Prompt 목록 조회
curl http://localhost:8001/api/system-prompts

# Health Check 상세
curl http://localhost:8001/ | jq '.services'
```

---

### Phase 3: WebSocket 연결 검증

#### 3.1 WebSocket 연결 테스트
```bash
# Python 테스트 스크립트 실행
cd /home/guehojung/Documents/Project/FINAL/development/ros-repo-1/AI/llm-gateway/tests/user_testing
python test_websocket.py

# 또는 wscat 사용 (설치 필요: npm install -g wscat)
wscat -c ws://localhost:8001/ws/voice
```

#### 3.2 WebSocket 수동 테스트
```javascript
// 브라우저 콘솔에서 실행
const ws = new WebSocket('ws://localhost:8001/ws/voice?session_id=test');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.send(JSON.stringify({type: 'text', message: '안녕하세요'}));
```

---

### Phase 4: 테스트 HTML 파일 검증

#### 4.1 각 테스트 페이지 접속 확인
```bash
# 브라우저에서 다음 URL들 접속하여 정상 동작 확인:

# 1. 채팅 인터페이스
http://localhost:8001/tests/user_testing/test_chat_interface.html

# 2. WebSocket 테스트
http://localhost:8001/tests/user_testing/test_websocket.html

# 3. 음성 인터페이스
http://localhost:8001/tests/user_testing/test_voice.html

# 4. Alfred 음성 인터페이스
http://localhost:8001/tests/user_testing/test_alfred_voice.html

# 5. Voiceprint 관리
http://localhost:8001/tests/user_testing/test_voiceprint_management.html

# 6. UI/UX 개선 테스트
http://localhost:8001/tests/user_testing/test_ui_ux_improvements.html
```

#### 4.2 각 페이지 기능 테스트
- **채팅 인터페이스**: 메시지 전송, System Prompt 선택, 음성 인터페이스 토글
- **WebSocket**: 실시간 메시지 송수신
- **음성 인터페이스**: 음성 입력/출력
- **Alfred 음성**: 키워드 인식 및 음성 대화
- **Voiceprint 관리**: 키워드 등록/조회

---

### Phase 5: Redis 연결 검증

#### 5.1 컨테이너 내부 Redis 연결 확인
```bash
# llm-gateway 컨테이너 내부에서 Redis 연결 테스트
docker exec -it llm-gateway python -c "
import redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)
print('Redis 연결 성공:', r.ping())
"
```

#### 5.2 외부에서 Redis 접근 확인 (포트 16379)
```bash
# Redis CLI로 외부 포트 접근
redis-cli -h localhost -p 16379 ping
# 또는 (비밀번호 있는 경우)
redis-cli -h localhost -p 16379 -a $REDIS_PASSWORD ping
```

---

### Phase 6: 통합 테스트

#### 6.1 전체 파이프라인 테스트
```bash
# 1. STT → Chat → TTS 통합 테스트
curl -X POST "http://localhost:8001/api/voice/process" \
  -F "audio=@test_audio.wav" \
  -F "session_id=test-session"

# 2. 채팅 세션 관리 테스트
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "테스트", "session_id": "test-session"}'

curl http://localhost:8001/api/session/test-session
```

#### 6.2 System Prompt 기능 테스트
```bash
# 1. 프롬프트 생성
curl -X POST "http://localhost:8001/api/system-prompts" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "테스트 프롬프트",
    "content": "당신은 테스트 어시스턴트입니다.",
    "description": "테스트용"
  }'

# 2. 프롬프트 목록 조회
curl http://localhost:8001/api/system-prompts

# 3. 프롬프트로 채팅
curl -X POST "http://localhost:8001/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕",
    "session_id": "test-session",
    "system_prompt": "당신은 테스트 어시스턴트입니다."
  }'
```

---

## 🔍 검증 체크리스트

### 기본 검증
- [ ] Docker Compose 포트 매핑 확인 (8001, 16379)
- [ ] 컨테이너 정상 실행 확인
- [ ] Health Check API 응답 확인
- [ ] Swagger UI 접근 확인

### API 검증
- [ ] STT API 동작 확인
- [ ] Chat API 동작 확인
- [ ] TTS API 동작 확인
- [ ] System Prompt API 동작 확인
- [ ] WebSocket 연결 확인

### 테스트 페이지 검증
- [ ] test_chat_interface.html 정상 동작
- [ ] test_websocket.html 정상 동작
- [ ] test_voice.html 정상 동작
- [ ] test_alfred_voice.html 정상 동작
- [ ] test_voiceprint_management.html 정상 동작
- [ ] test_ui_ux_improvements.html 정상 동작

### Redis 검증
- [ ] 컨테이너 내부 Redis 연결 확인
- [ ] 외부 포트(16379) 접근 확인
- [ ] 세션 저장/조회 동작 확인

### 통합 검증
- [ ] 전체 음성 파이프라인 동작 확인
- [ ] 세션 관리 동작 확인
- [ ] System Prompt 기능 동작 확인

---

## 🚨 문제 발생 시 대응 방안

### 포트 충돌
```bash
# 포트 사용 중인 프로세스 확인
lsof -i :8001
lsof -i :16379

# 프로세스 종료
kill -9 <PID>
```

### 컨테이너 재시작
```bash
docker-compose down
docker-compose up -d
```

### 로그 확인
```bash
# llm-gateway 로그
docker-compose logs -f llm-gateway

# redis 로그
docker-compose logs -f redis
```

### 환경변수 확인
```bash
# .env.local 파일 확인
cat .env.local | grep -E "SERVER_PORT|REDIS_EXTERNAL_PORT"
```

---

## 📝 검증 결과 기록

검증 완료 후 다음 정보를 기록:

1. **검증 일시**: YYYY-MM-DD HH:MM:SS
2. **검증자**: 이름
3. **검증 환경**: 
   - OS: 
   - Docker 버전: 
   - Docker Compose 버전:
4. **검증 결과**: 
   - 성공 항목:
   - 실패 항목:
   - 문제점 및 해결 방법:
5. **최종 판정**: ✅ 통과 / ❌ 실패

---

## 🎯 빠른 검증 스크립트

다음 스크립트를 실행하여 빠르게 검증:

```bash
#!/bin/bash
# quick_verification.sh

echo "=== 포트 변경 검증 ==="
echo ""

echo "1. 포트 리스닝 확인..."
netstat -tuln | grep -E "8001|16379" && echo "✓ 포트 정상" || echo "✗ 포트 미사용"

echo ""
echo "2. Health Check..."
curl -s http://localhost:8001/ | jq -r '.status' && echo "✓ API 정상" || echo "✗ API 오류"

echo ""
echo "3. Redis 연결 확인..."
docker exec llm-gateway-redis redis-cli ping 2>/dev/null && echo "✓ Redis 정상" || echo "✗ Redis 오류"

echo ""
echo "4. 컨테이너 상태 확인..."
docker-compose ps

echo ""
echo "=== 검증 완료 ==="
```

