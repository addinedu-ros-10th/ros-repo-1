# HTTPS 접속 가이드

## 개요

Caddy를 통해 HTTPS로 접속하는 방법을 안내합니다.

## 사전 확인

### 1. 서버가 실행 중인지 확인

```bash
cd AI/llm-gateway
docker compose ps
```

다음 컨테이너들이 실행 중이어야 합니다:
- `llm-gateway-caddy` (Caddy 리버스 프록시)
- `llm-gateway` (FastAPI 서버)

### 2. 포트 확인

```bash
# 80, 443 포트가 열려있는지 확인
sudo netstat -tuln | grep -E ':(80|443)'
# 또는
sudo ss -tuln | grep -E ':(80|443)'
```

## HTTPS 접속 방법

### 방법 1: 브라우저에서 직접 접속

#### 1.1 로컬 네트워크 (192.168.0.9)

1. **브라우저 주소창에 입력**
   ```
   https://192.168.0.9
   ```

2. **인증서 경고 처리**
   - 브라우저에서 "안전하지 않음" 또는 "NET::ERR_CERT_AUTHORITY_INVALID" 경고가 표시됩니다.
   - 이는 자체 서명 인증서를 사용하기 때문입니다 (정상 동작).

3. **경고 우회 방법**
   - **Chrome/Edge**: 
     - "고급" 버튼 클릭
     - "192.168.0.9(안전하지 않음)로 이동" 클릭
   - **Firefox**:
     - "고급" 버튼 클릭
     - "위험을 감수하고 계속" 클릭
   - **Safari**:
     - "상세 정보 표시" 클릭
     - "웹사이트 방문" 클릭

4. **접속 확인**
   - Health Check 페이지가 표시되면 성공입니다.

#### 1.2 Tailscale VPN (100.69.86.72)

1. **브라우저 주소창에 입력**
   ```
   https://100.69.86.72
   ```

2. **인증서 경고 처리** (위와 동일)

### 방법 2: 테스트 페이지 접속

#### 채팅 인터페이스
```
https://192.168.0.9/tests/user_testing/test_chat_interface.html
```

#### Alfred 음성 인터페이스
```
https://192.168.0.9/tests/user_testing/test_alfred_voice.html
```

#### 음성 인터페이스
```
https://192.168.0.9/tests/user_testing/test_voice.html
```

### 방법 3: curl로 테스트

```bash
# 인증서 검증 무시 (자체 서명 인증서 사용 시)
curl -k https://192.168.0.9/

# 또는
curl --insecure https://192.168.0.9/
```

## 문제 해결

### 문제 1: "연결할 수 없음" 오류

**원인**: 서버가 실행되지 않았거나 포트가 열려있지 않음

**해결 방법**:
```bash
# 서버 시작
cd AI/llm-gateway
docker compose up -d

# 포트 확인
docker compose ps
```

### 문제 2: 인증서 경고가 계속 표시됨

**원인**: 자체 서명 인증서 사용 (IP 주소 접속 시 정상)

**해결 방법**:
- 운영 환경에서는 도메인을 사용하여 Let's Encrypt 인증서 사용
- 개발 환경에서는 브라우저에서 경고를 무시하고 접속

### 문제 3: HTTP로 리다이렉트되지 않음

**원인**: Caddy 설정 문제

**해결 방법**:
```bash
# Caddy 재시작
docker compose restart caddy

# Caddy 로그 확인
docker compose logs caddy
```

### 문제 4: WebSocket 연결 실패

**원인**: Caddyfile에 WebSocket 설정이 누락됨

**해결 방법**:
1. `Caddyfile` 확인
2. WebSocket 헤더가 포함되어 있는지 확인
3. Caddy 재시작:
   ```bash
   docker compose restart caddy
   ```

## 인증서 경고를 영구적으로 해결하는 방법

### 방법 1: 도메인 사용 (운영 환경 권장)

1. **Caddyfile 수정**
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
   ```

2. **DNS 설정**
   - 도메인의 A 레코드를 서버 IP로 설정

3. **Caddy 재시작**
   ```bash
   docker compose restart caddy
   ```

4. **Let's Encrypt 인증서 자동 발급**
   - Caddy가 자동으로 인증서를 발급받습니다.
   - 브라우저 경고 없이 접속 가능합니다.

### 방법 2: 브라우저에 인증서 추가 (개발 환경)

자체 서명 인증서를 브라우저에 신뢰할 수 있는 인증 기관으로 추가할 수 있습니다. (고급 사용자용)

## 빠른 테스트 체크리스트

- [ ] 서버 실행 중: `docker compose ps`
- [ ] 포트 열림: `netstat -tuln | grep 443`
- [ ] HTTPS 접속: `https://192.168.0.9`
- [ ] 인증서 경고 처리: "고급" → "계속 진행"
- [ ] Health Check 응답 확인
- [ ] 테스트 페이지 접속 확인
- [ ] 마이크 권한 요청 확인 (HTTPS에서 정상 작동)

## 참고

- **HTTPS 접속**: `https://192.168.0.9` (포트 443, Caddy 프록시)
- **HTTP 직접 접속**: `http://192.168.0.9:8001` (포트 8001, 직접 접속)
- **인증서 경고**: IP 주소 접속 시 정상 (도메인 사용 시 해결)

