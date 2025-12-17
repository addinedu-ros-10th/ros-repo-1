# 현재 상태에서 HTTPS 접속 가이드

## 현재 상황

- **HTTP 접속**: ✅ 정상 작동 (`http://192.168.0.9:8001/docs`)
- **HTTPS 접속**: ⚠️ SSL 핸드셰이크 오류 발생 (`https://192.168.0.9/docs`)

## 문제 원인

Caddy가 IP 주소로 접속할 때 자체 서명 인증서를 제대로 처리하지 못하고 있습니다. 이는 Caddy의 알려진 제한사항입니다.

## 해결 방법

### 방법 1: HTTP 직접 접속 사용 (현재 작동 중)

**장점**: 즉시 사용 가능, 설정 불필요  
**단점**: SSL 없음, 브라우저 마이크 권한 제한 가능

```
http://192.168.0.9:8001/docs
```

**음성 인터페이스 사용 시**:
- 일부 브라우저에서 마이크 권한이 제한될 수 있습니다
- Chrome/Edge: 사이트 설정에서 마이크 권한을 수동으로 허용해야 할 수 있습니다

### 방법 2: 브라우저에서 인증서 신뢰 추가

1. **인증서 다운로드**
   ```bash
   # Caddy 컨테이너에서 인증서 위치 확인
   docker compose exec caddy ls -la /data/caddy/certificates/
   ```

2. **인증서 추출** (필요시)
   ```bash
   # 인증서 파일 복사
   docker compose cp caddy:/data/caddy/certificates/authorities/local/root.crt ./caddy-root.crt
   ```

3. **브라우저에 인증서 추가**
   - **Chrome/Edge**: 설정 → 개인정보 및 보안 → 인증서 관리 → 신뢰할 수 있는 루트 인증 기관 → 가져오기
   - **Firefox**: 설정 → 개인정보 및 보안 → 인증서 → 인증서 보기 → 인증 기관 → 가져오기

### 방법 3: hosts 파일에 도메인 추가 (임시 해결)

로컬에서 도메인처럼 사용:

1. **호스트 파일 수정** (관리자 권한 필요)
   ```bash
   # Linux/Mac
   sudo nano /etc/hosts
   
   # Windows
   # C:\Windows\System32\drivers\etc\hosts
   ```

2. **도메인 추가**
   ```
   192.168.0.9    llm-gateway.local
   ```

3. **Caddyfile 수정**
   ```caddy
   llm-gateway.local {
       tls internal
       reverse_proxy llm-gateway:8000 {
           header_up X-Real-IP {remote_host}
           header_up X-Forwarded-For {remote_host}
           header_up X-Forwarded-Proto {scheme}
           header_up Connection {>Connection}
           header_up Upgrade {>Upgrade}
       }
   }
   ```

4. **접속**
   ```
   https://llm-gateway.local/docs
   ```

### 방법 4: Caddy 재설정 (권장)

Caddyfile을 더 명확하게 설정:

```caddy
# 전역 설정
{
    email your-email@example.com
}

# IP 주소 접속용 (자체 서명 인증서)
:443 {
    tls internal {
        # 모든 호스트 허용
        protocols tls1.2 tls1.3
    }
    
    reverse_proxy llm-gateway:8000 {
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto {scheme}
        header_up Connection {>Connection}
        header_up Upgrade {>Upgrade}
    }
}

:80 {
    redir https://{host}{uri} permanent
}
```

## 현재 권장 방법

### 즉시 사용 가능: HTTP 직접 접속

```
http://192.168.0.9:8001/docs
http://192.168.0.9:8001/tests/user_testing/test_chat_interface.html
```

**음성 인터페이스 사용 시**:
1. 브라우저 주소창 왼쪽의 자물쇠/정보 아이콘 클릭
2. "사이트 설정" 또는 "권한" 선택
3. 마이크 권한을 "허용"으로 변경
4. 페이지 새로고침

### 향후 개선: 도메인 설정 후 Let's Encrypt 사용

도메인을 설정하면 Let's Encrypt 인증서를 사용할 수 있습니다:
- 브라우저 경고 없음
- 마이크 권한 정상 작동
- 자동 인증서 갱신

## 테스트 방법

### HTTP 접속 테스트
```bash
curl http://192.168.0.9:8001/docs
```

### HTTPS 접속 테스트 (인증서 검증 무시)
```bash
curl -k https://192.168.0.9/docs
```

### 브라우저 접속 테스트
1. `http://192.168.0.9:8001/docs` 접속
2. 정상 작동 확인
3. 마이크 권한 설정 확인

## 문제 해결

### HTTPS 접속이 계속 실패하는 경우

1. **Caddy 로그 확인**
   ```bash
   docker compose logs -f caddy
   ```

2. **Caddy 재시작**
   ```bash
   docker compose restart caddy
   ```

3. **포트 확인**
   ```bash
   sudo netstat -tuln | grep -E ':80|:443'
   ```

4. **방화벽 확인**
   ```bash
   sudo ufw status
   # 또는
   sudo iptables -L -n | grep -E '80|443'
   ```

## 요약

**현재 사용 가능한 접속 방법:**
- ✅ HTTP: `http://192.168.0.9:8001` (즉시 사용 가능)
- ⚠️ HTTPS: `https://192.168.0.9` (SSL 오류 발생, 수정 필요)

**권장 사항:**
- 현재는 HTTP 직접 접속 사용
- 향후 도메인 설정 후 Let's Encrypt 적용

