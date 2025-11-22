# 접속 가능한 URL 목록

## 서버 IP 주소

### 로컬 네트워크 (WiFi)
- **IP**: `192.168.0.9`
- **인터페이스**: wlo1

### Tailscale VPN
- **IP**: `100.69.86.72`
- **인터페이스**: tailscale0

---

## HTTPS 접속 (Caddy SSL 적용) - 권장

### 로컬 네트워크
- **메인**: https://192.168.0.9
- **API 문서**: https://192.168.0.9/docs
- **Health Check**: https://192.168.0.9/

### Tailscale VPN
- **메인**: https://100.69.86.72
- **API 문서**: https://100.69.86.72/docs
- **Health Check**: https://100.69.86.72/

### 테스트 페이지 (로컬 네트워크)
- **채팅 인터페이스**: https://192.168.0.9/tests/user_testing/test_chat_interface.html
- **Alfred 음성 인터페이스**: https://192.168.0.9/tests/user_testing/test_alfred_voice.html
- **음성 인터페이스**: https://192.168.0.9/tests/user_testing/test_voice.html
- **WebSocket 테스트**: https://192.168.0.9/tests/user_testing/test_websocket.html
- **음성 지문 관리**: https://192.168.0.9/tests/user_testing/test_voiceprint_management.html

### 테스트 페이지 (Tailscale VPN)
- **채팅 인터페이스**: https://100.69.86.72/tests/user_testing/test_chat_interface.html
- **Alfred 음성 인터페이스**: https://100.69.86.72/tests/user_testing/test_alfred_voice.html
- **음성 인터페이스**: https://100.69.86.72/tests/user_testing/test_voice.html
- **WebSocket 테스트**: https://100.69.86.72/tests/user_testing/test_websocket.html
- **음성 지문 관리**: https://100.69.86.72/tests/user_testing/test_voiceprint_management.html

---

## HTTP 직접 접속 (포트 8001)

### 로컬 네트워크
- **메인**: http://192.168.0.9:8001
- **API 문서**: http://192.168.0.9:8001/docs
- **Health Check**: http://192.168.0.9:8001/

### Tailscale VPN
- **메인**: http://100.69.86.72:8001
- **API 문서**: http://100.69.86.72:8001/docs
- **Health Check**: http://100.69.86.72:8001/

### 테스트 페이지 (로컬 네트워크)
- **채팅 인터페이스**: http://192.168.0.9:8001/tests/user_testing/test_chat_interface.html
- **Alfred 음성 인터페이스**: http://192.168.0.9:8001/tests/user_testing/test_alfred_voice.html
- **음성 인터페이스**: http://192.168.0.9:8001/tests/user_testing/test_voice.html

### 테스트 페이지 (Tailscale VPN)
- **채팅 인터페이스**: http://100.69.86.72:8001/tests/user_testing/test_chat_interface.html
- **Alfred 음성 인터페이스**: http://100.69.86.72:8001/tests/user_testing/test_alfred_voice.html
- **음성 인터페이스**: http://100.69.86.72:8001/tests/user_testing/test_voice.html

---

## API 엔드포인트

### HTTPS (Caddy)
- **채팅**: POST https://192.168.0.9/api/chat
- **STT**: POST https://192.168.0.9/api/stt
- **TTS**: POST https://192.168.0.9/api/tts
- **통합 음성 처리**: POST https://192.168.0.9/api/voice/process
- **배회 탐지**: POST https://192.168.0.9/api/wandering/detection
- **WebSocket**: wss://192.168.0.9/ws/wandering-detection

### HTTP (직접 접속, 포트 8001)
- **채팅**: POST http://192.168.0.9:8001/api/chat
- **STT**: POST http://192.168.0.9:8001/api/stt
- **TTS**: POST http://192.168.0.9:8001/api/tts
- **통합 음성 처리**: POST http://192.168.0.9:8001/api/voice/process
- **배회 탐지**: POST http://192.168.0.9:8001/api/wandering/detection
- **WebSocket**: ws://192.168.0.9:8001/ws/wandering-detection

---

## 빠른 테스트

### 1. Health Check
```bash
# HTTPS
curl https://192.168.0.9/

# HTTP
curl http://192.168.0.9:8001/
```

### 2. 배회 탐지 테스트
```bash
# HTTPS
curl -X POST https://192.168.0.9/api/wandering/detection \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "pinky_013"
  }'

# HTTP
curl -X POST http://192.168.0.9:8001/api/wandering/detection \
  -H "Content-Type: application/json" \
  -d '{
    "nickname": "Akaza",
    "detection_location": "1층 복도",
    "detection_confidence": 0.95,
    "camera_id": "pinky_013"
  }'
```

---

## 접속 방법별 특징

### HTTPS (권장)
- ✅ SSL/TLS 암호화
- ✅ 브라우저 마이크 권한 정상 작동
- ✅ WebSocket 정상 작동
- ⚠️ 자체 서명 인증서 사용 시 브라우저 경고 발생

### HTTP (포트 8001)
- ❌ SSL 없음
- ⚠️ 브라우저 마이크 권한 제한 가능
- ✅ 직접 접속 가능
- ✅ 개발/테스트용으로 유용

---

## 주의사항

1. **방화벽 설정**: 80, 443, 8001 포트가 열려있어야 합니다.
2. **인증서 경고**: IP 주소로 접속 시 자체 서명 인증서 경고가 표시됩니다.
   - "고급" → "계속 진행" 클릭하여 접속
3. **Tailscale VPN**: Tailscale 네트워크에 연결된 기기에서만 접속 가능합니다.
4. **로컬 네트워크**: 같은 WiFi 네트워크에 연결된 기기에서만 접속 가능합니다.

