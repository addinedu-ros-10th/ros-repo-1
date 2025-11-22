# Caddy SSL 적용 테스트 가이드

## 개요

Caddy를 통한 SSL/TLS 적용 후 음성 인터페이스가 정상 작동하는지 테스트하는 방법을 안내합니다.

## 사전 준비

### 1. 서버 시작

```bash
cd AI/llm-gateway
docker compose up -d
```

### 2. 컨테이너 상태 확인

```bash
# 모든 컨테이너가 실행 중인지 확인
docker compose ps

# 예상 출력:
# NAME                    STATUS
# llm-gateway             Up
# llm-gateway-caddy       Up
# llm-gateway-redis       Up
```

### 3. 포트 확인

```bash
# 포트가 열려있는지 확인
netstat -tuln | grep -E ':(80|443|8001)'

# 또는
ss -tuln | grep -E ':(80|443|8001)'
```

## 테스트 방법

### 방법 1: HTTPS 접속 테스트 (권장)

#### 1.1 IP 주소로 접속

1. **서버 IP 주소 확인**
   ```bash
   # 서버에서 실행
   hostname -I
   # 또는
   ip addr show
   ```

2. **HTTPS로 접속**
   - 브라우저에서 `https://your-server-ip` 접속
   - 예: `https://192.168.1.100`

3. **인증서 경고 처리**
   - 브라우저에서 "안전하지 않음" 경고가 표시됨 (자체 서명 인증서 사용)
   - **Chrome/Edge**: "고급" → "계속 진행 (your-server-ip)" 클릭
   - **Firefox**: "고급" → "위험을 감수하고 계속" 클릭
   - **Safari**: "상세 정보 표시" → "웹사이트 방문" 클릭

4. **테스트 페이지 접속**
   - `https://your-server-ip/tests/user_testing/test_chat_interface.html`
   - `https://your-server-ip/tests/user_testing/test_alfred_voice.html`

#### 1.2 도메인으로 접속 (운영 환경)

1. **Caddyfile 수정**
   ```bash
   # Caddyfile 열기
   nano Caddyfile
   ```
   
   도메인 설정 활성화:
   ```caddy
   your-domain.com {
       reverse_proxy llm-gateway:8000 {
           header_up X-Real-IP {remote_host}
           header_up X-Forwarded-For {remote_host}
           header_up X-Forwarded-Proto {scheme}
           header_up Connection {>Connection}
           header_up Upgrade {>Upgrade}
       }
   }
   
   http://your-domain.com {
       redir https://{host}{uri} permanent
   }
   ```

2. **DNS 설정**
   - 도메인의 A 레코드를 서버 IP로 설정
   - DNS 전파 대기 (보통 몇 분 소요)

3. **Caddy 재시작**
   ```bash
   docker compose restart caddy
   ```

4. **HTTPS 접속**
   - `https://your-domain.com` 접속
   - Let's Encrypt 인증서가 자동으로 발급됨 (경고 없음)

### 방법 2: HTTP 접속 테스트 (리다이렉트 확인)

1. **HTTP로 접속**
   - 브라우저에서 `http://your-server-ip` 접속
   - 자동으로 `https://your-server-ip`로 리다이렉트되는지 확인

2. **리다이렉트 확인**
   - 브라우저 주소창이 HTTPS로 변경되는지 확인
   - 개발자 도구(F12) → Network 탭에서 301/308 리다이렉트 확인

### 방법 3: 직접 포트 접속 테스트 (HTTP, 포트 8001)

1. **HTTP로 직접 접속**
   - `http://your-server-ip:8001` 접속
   - Caddy를 거치지 않고 직접 접속 (SSL 없음)

2. **음성 인터페이스 테스트**
   - 마이크 권한 요청이 정상 작동하는지 확인
   - HTTPS가 아닌 경우 브라우저에서 마이크 권한을 차단할 수 있음

## 음성 인터페이스 테스트

### 1. 마이크 권한 테스트

1. **테스트 페이지 접속**
   - `https://your-server-ip/tests/user_testing/test_alfred_voice.html`

2. **마이크 권한 확인**
   - 페이지 로드 시 브라우저에서 마이크 권한 요청
   - HTTPS인 경우 권한 요청이 정상 작동
   - HTTP인 경우 권한 요청이 차단될 수 있음

3. **음성 입력 테스트**
   - "🎤 음성 입력" 버튼 클릭
   - 마이크에 말하기
   - STT 결과가 표시되는지 확인

### 2. WebSocket 연결 테스트

1. **배회 탐지 WebSocket 테스트**
   - `https://your-server-ip/tests/user_testing/test_chat_interface.html` 접속
   - 브라우저 콘솔(F12)에서 다음 메시지 확인:
     ```
     ✅ 배회 탐지 WebSocket 연결 성공
     ```

2. **WebSocket 연결 확인**
   ```bash
   # Caddy 로그에서 WebSocket 업그레이드 확인
   docker compose logs caddy | grep -i websocket
   ```

### 3. TTS 음성 출력 테스트

1. **채팅 인터페이스에서 테스트**
   - 메시지 전송 후 TTS 음성이 재생되는지 확인
   - 브라우저 콘솔에서 오디오 재생 로그 확인

2. **배회 탐지 음성 안내 테스트**
   - "🚨 배회 탐지 테스트" 버튼 클릭
   - 음성 안내가 자동으로 재생되는지 확인

## 문제 해결

### 문제 1: 인증서 경고가 계속 표시됨

**원인**: 자체 서명 인증서 사용 (IP 주소 접속 시)

**해결 방법**:
- 운영 환경에서는 도메인을 사용하여 Let's Encrypt 인증서 사용
- 개발 환경에서는 브라우저에서 인증서를 신뢰하도록 설정

### 문제 2: WebSocket 연결 실패

**증상**: 브라우저 콘솔에 WebSocket 연결 오류

**해결 방법**:
1. Caddyfile에 WebSocket 헤더가 포함되어 있는지 확인
2. Caddy 재시작:
   ```bash
   docker compose restart caddy
   ```
3. Caddy 로그 확인:
   ```bash
   docker compose logs -f caddy
   ```

### 문제 3: 마이크 권한이 요청되지 않음

**증상**: HTTPS로 접속했는데도 마이크 권한 요청이 없음

**해결 방법**:
1. 브라우저 주소창에서 자물쇠 아이콘 클릭
2. 사이트 설정 → 마이크 권한 확인
3. 브라우저 재시작 후 다시 시도

### 문제 4: HTTP로 접속 시 리다이렉트되지 않음

**증상**: `http://your-server-ip` 접속 시 HTTPS로 리다이렉트되지 않음

**해결 방법**:
1. Caddyfile에 HTTP 리다이렉트 설정이 있는지 확인
2. Caddy 재시작:
   ```bash
   docker compose restart caddy
   ```

### 문제 5: Let's Encrypt 인증서 발급 실패

**증상**: 도메인 사용 시 인증서 발급 실패

**해결 방법**:
1. DNS 설정 확인 (A 레코드가 올바른 IP로 설정되어 있는지)
2. 80, 443 포트가 열려있는지 확인
3. 방화벽 설정 확인
4. Caddy 로그 확인:
   ```bash
   docker compose logs caddy | grep -i "certificate\|acme\|letsencrypt"
   ```

## 로그 확인

### Caddy 로그

```bash
# 실시간 로그 확인
docker compose logs -f caddy

# 최근 로그만 확인
docker compose logs --tail=100 caddy
```

### LLM Gateway 로그

```bash
# 실시간 로그 확인
docker compose logs -f llm-gateway

# 최근 로그만 확인
docker compose logs --tail=100 llm-gateway
```

## 성공 기준

✅ **HTTPS 접속 성공**
- `https://your-server-ip` 접속 시 페이지가 정상 로드됨

✅ **마이크 권한 요청**
- HTTPS 접속 시 브라우저에서 마이크 권한 요청이 정상 작동

✅ **WebSocket 연결 성공**
- 브라우저 콘솔에 "✅ 배회 탐지 WebSocket 연결 성공" 메시지 표시

✅ **음성 입력/출력 정상**
- STT, TTS가 정상 작동
- 배회 탐지 음성 안내가 자동 재생됨

✅ **HTTP → HTTPS 리다이렉트**
- HTTP 접속 시 자동으로 HTTPS로 리다이렉트됨

## 참고 사항

- **개발 환경**: IP 주소 + 자체 서명 인증서 사용 (브라우저 경고 발생)
- **운영 환경**: 도메인 + Let's Encrypt 인증서 사용 (경고 없음)
- **직접 접속**: `http://your-server-ip:8001`로 직접 접속 가능 (SSL 없음, 마이크 권한 제한 가능)

