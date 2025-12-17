# SSL/TLS 설정 가이드 (Caddy 사용)

## 개요

외부에서 서버에 접속할 때 음성 인터페이스(마이크 권한 등)를 사용하기 위해서는 HTTPS가 필요합니다. Caddy를 사용하여 자동으로 SSL/TLS 인증서를 발급받고 HTTPS를 제공합니다.

## 설정 방법

### 1. 도메인을 사용하는 경우 (운영 환경)

#### Caddyfile 수정

`Caddyfile`을 열어서 도메인을 설정합니다:

```caddy
your-domain.com {
    reverse_proxy llm-gateway:8000 {
        # WebSocket 지원
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
    }
}

# HTTP를 HTTPS로 리다이렉트
http://your-domain.com {
    redir https://{host}{uri} permanent
}
```

#### DNS 설정

도메인의 A 레코드를 서버의 IP 주소로 설정합니다.

#### 포트 포워딩

서버의 80, 443 포트가 열려있어야 합니다.

### 2. IP 주소로 접속하는 경우 (개발/테스트 환경)

현재 설정은 IP 주소로 접속하는 경우를 위한 자체 서명 인증서를 사용합니다.

#### 브라우저에서 인증서 경고 처리

1. HTTPS로 접속 시 브라우저에서 "안전하지 않음" 경고가 표시됩니다.
2. "고급" → "계속 진행"을 클릭하여 접속합니다.
3. 또는 인증서를 브라우저에 신뢰할 수 있는 인증 기관으로 추가합니다.

## 사용 방법

### 서버 시작

```bash
cd AI/llm-gateway
docker compose up -d
```

### 서버 중지

```bash
docker compose down
```

### 로그 확인

```bash
# Caddy 로그
docker compose logs -f caddy

# LLM Gateway 로그
docker compose logs -f llm-gateway
```

## 접속 방법

### HTTPS 접속

- **도메인 사용 시**: `https://your-domain.com`
- **IP 주소 사용 시**: `https://your-server-ip`

### 테스트 페이지

- `https://your-domain.com/tests/user_testing/test_chat_interface.html`
- `https://your-domain.com/tests/user_testing/test_alfred_voice.html`

## 문제 해결

### 1. 인증서 발급 실패

**증상**: Caddy 로그에 인증서 발급 실패 메시지

**해결 방법**:
- 도메인이 올바르게 DNS에 설정되어 있는지 확인
- 80, 443 포트가 열려있는지 확인
- 방화벽 설정 확인

### 2. WebSocket 연결 실패

**증상**: WebSocket 연결이 403 또는 연결 실패

**해결 방법**:
- Caddyfile에 WebSocket 지원 설정이 포함되어 있는지 확인
- Caddy 컨테이너 재시작: `docker compose restart caddy`

### 3. 자체 서명 인증서 경고

**증상**: 브라우저에서 "안전하지 않음" 경고

**해결 방법**:
- 운영 환경에서는 도메인을 사용하여 Let's Encrypt 인증서 사용
- 개발 환경에서는 브라우저에서 인증서를 신뢰하도록 설정

## 보안 고려사항

1. **운영 환경**: 반드시 도메인을 사용하여 Let's Encrypt 인증서를 사용하세요.
2. **개발 환경**: 자체 서명 인증서는 보안 경고가 표시되지만, 개발 목적으로는 사용 가능합니다.
3. **방화벽**: 필요한 포트(80, 443)만 열어두고, 불필요한 포트는 차단하세요.

## 참고 자료

- [Caddy 공식 문서](https://caddyserver.com/docs/)
- [Let's Encrypt](https://letsencrypt.org/)

