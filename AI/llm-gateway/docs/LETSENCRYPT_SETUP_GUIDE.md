# Let's Encrypt 인증서 설정 가이드

## 개요

Let's Encrypt를 사용하여 무료 SSL/TLS 인증서를 자동으로 발급받고 적용하는 방법을 안내합니다.

## 사전 요구사항

1. **도메인 이름**: 공개 도메인이 필요합니다 (예: `example.com`)
2. **DNS 설정**: 도메인의 A 레코드가 서버 IP로 설정되어 있어야 합니다
3. **포트 80, 443 열림**: Let's Encrypt 인증서 발급을 위해 포트 80이 열려있어야 합니다

## 설정 방법

### 1. 도메인 DNS 설정

도메인 관리 패널에서 A 레코드를 설정합니다:

```
Type: A
Name: @ (또는 서브도메인 이름)
Value: 192.168.0.9 (또는 서버의 공개 IP)
TTL: 3600 (또는 기본값)
```

**예시:**
- `llm-gateway.example.com` → `192.168.0.9`
- `api.example.com` → `192.168.0.9`

### 2. Caddyfile 수정

`Caddyfile`을 열어서 도메인을 설정합니다:

```bash
cd AI/llm-gateway
nano Caddyfile
```

#### 2.1 이메일 설정

전역 설정 블록에서 이메일을 설정합니다:

```caddy
{
    # Let's Encrypt 인증서 갱신 알림용 이메일
    email your-email@example.com
}
```

#### 2.2 도메인 설정

IP 주소 블록을 주석 처리하고 도메인 블록을 활성화합니다:

```caddy
# 도메인 설정 (주석 해제 및 도메인 입력)
llm-gateway.example.com {
    reverse_proxy llm-gateway:8000 {
        # WebSocket 지원
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        
        # WebSocket 업그레이드 헤더
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
}

# HTTP를 HTTPS로 리다이렉트
http://llm-gateway.example.com {
    redir https://{host}{uri} permanent
}

# IP 주소 블록 주석 처리
# :443 {
#     tls internal
#     ...
# }
```

### 3. Caddy 재시작

```bash
docker compose restart caddy
```

### 4. 인증서 발급 확인

```bash
# Caddy 로그 확인
docker compose logs -f caddy

# 인증서 발급 성공 메시지 확인:
# "certificate obtained successfully"
# "serving certificates"
```

### 5. 접속 테스트

브라우저에서 `https://your-domain.com` 접속:
- 인증서 경고 없이 접속 가능
- 자물쇠 아이콘 표시 확인

## 설정 예시

### 예시 1: 단일 도메인

```caddy
{
    email admin@example.com
}

llm-gateway.example.com {
    reverse_proxy llm-gateway:8000 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
}

http://llm-gateway.example.com {
    redir https://{host}{uri} permanent
}
```

### 예시 2: 여러 도메인

```caddy
{
    email admin@example.com
}

# 메인 도메인
llm-gateway.example.com {
    reverse_proxy llm-gateway:8000 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
}

# API 서브도메인
api.example.com {
    reverse_proxy llm-gateway:8000 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
}

# HTTP 리다이렉트
http://llm-gateway.example.com {
    redir https://{host}{uri} permanent
}

http://api.example.com {
    redir https://{host}{uri} permanent
}
```

## 문제 해결

### 문제 1: 인증서 발급 실패

**증상**: Caddy 로그에 인증서 발급 실패 메시지

**원인 및 해결**:
1. **DNS 설정 확인**
   ```bash
   # DNS 전파 확인
   dig your-domain.com
   # 또는
   nslookup your-domain.com
   ```
   - A 레코드가 올바른 IP로 설정되어 있는지 확인
   - DNS 전파 대기 (보통 몇 분~몇 시간 소요)

2. **포트 80 확인**
   ```bash
   # 포트 80이 열려있는지 확인
   sudo netstat -tuln | grep :80
   ```
   - 포트 80이 다른 서비스에서 사용 중이면 중지 필요

3. **방화벽 확인**
   ```bash
   # UFW 방화벽
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   
   # iptables
   sudo iptables -A INPUT -p tcp --dport 80 -j ACCEPT
   sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT
   ```

### 문제 2: 인증서 갱신 실패

**증상**: 인증서 갱신 시 오류 발생

**해결 방법**:
- Caddy가 자동으로 인증서를 갱신합니다 (만료 30일 전)
- 수동 갱신:
  ```bash
  docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
  ```

### 문제 3: 도메인 접속 불가

**증상**: 도메인으로 접속이 안 됨

**확인 사항**:
1. DNS 전파 확인
2. 도메인 설정이 올바른지 확인
3. Caddy 로그 확인

## 인증서 저장 위치

Caddy의 인증서는 Docker 볼륨에 저장됩니다:

```bash
# 인증서 확인
docker compose exec caddy ls -la /data/caddy/certificates/

# 볼륨 위치 확인
docker volume inspect llm-gateway_caddy-data
```

## 자동 갱신

Let's Encrypt 인증서는 90일마다 만료되지만, Caddy가 자동으로 갱신합니다:
- 만료 30일 전부터 자동 갱신 시도
- 갱신 실패 시 로그에 기록
- 이메일로 알림 (설정한 경우)

## 참고 사항

1. **Rate Limit**: Let's Encrypt는 주간 인증서 발급 제한이 있습니다 (도메인당 50개/주)
2. **테스트 환경**: 스테이징 환경 사용 시 `https://acme-staging-v02.api.letsencrypt.org/directory` 사용 가능
3. **IP 주소**: Let's Encrypt는 IP 주소에 대해 인증서를 발급하지 않습니다 (도메인 필요)

## 빠른 설정 체크리스트

- [ ] 도메인 DNS A 레코드 설정
- [ ] DNS 전파 확인 (`dig` 또는 `nslookup`)
- [ ] Caddyfile에 도메인 및 이메일 설정
- [ ] 포트 80, 443 열림 확인
- [ ] Caddy 재시작
- [ ] 인증서 발급 확인 (로그)
- [ ] HTTPS 접속 테스트

