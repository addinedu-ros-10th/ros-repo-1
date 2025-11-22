# 자체 서명 인증서 설정 완료

## 현재 상태

✅ **인증서 생성 완료**
- 자체 서명 인증서가 `/data/caddy/pki/authorities/local/`에 생성되었습니다
- 루트 인증서: `root.crt`
- 중간 인증서: `intermediate.crt`

⚠️ **IP 주소 직접 접속 제한**
- Caddy는 IP 주소로 직접 접속할 때 SNI(Server Name Indication)가 없어 인증서를 제대로 제공하지 못할 수 있습니다
- 이는 Caddy의 알려진 제한사항입니다

## 해결 방법

### 방법 1: hosts 파일에 도메인 추가 (권장)

로컬에서 도메인처럼 사용:

#### 1.1 hosts 파일 수정

**Linux/Mac:**
```bash
sudo nano /etc/hosts
```

**Windows:**
```
C:\Windows\System32\drivers\etc\hosts
```

#### 1.2 도메인 추가
```
192.168.0.9    llm-gateway.local
```

#### 1.3 Caddyfile 수정
```caddy
# 도메인 블록 활성화
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

http://llm-gateway.local {
    redir https://{host}{uri} permanent
}
```

#### 1.4 Caddy 재시작
```bash
docker compose restart caddy
```

#### 1.5 접속
```
https://llm-gateway.local/docs
```

### 방법 2: HTTP 직접 접속 사용 (현재 작동 중)

```
http://192.168.0.9:8001/docs
```

**장점:**
- 즉시 사용 가능
- SSL 문제 없음

**단점:**
- 마이크 권한이 브라우저에서 제한될 수 있음
- 브라우저 설정에서 수동으로 허용 필요

### 방법 3: 브라우저에서 인증서 신뢰 추가

#### 3.1 인증서 추출
```bash
# 루트 인증서 추출
docker compose cp caddy:/data/caddy/pki/authorities/local/root.crt ./caddy-root.crt
```

#### 3.2 브라우저에 추가

**Chrome/Edge:**
1. 설정 → 개인정보 및 보안 → 보안
2. 인증서 관리 클릭
3. "신뢰할 수 있는 루트 인증 기관" 탭
4. "가져오기" 클릭
5. `caddy-root.crt` 파일 선택

**Firefox:**
1. 설정 → 개인정보 및 보안
2. 인증서 → "인증서 보기" 클릭
3. "인증 기관" 탭
4. "가져오기" 클릭
5. `caddy-root.crt` 파일 선택

**주의:** 이 방법만으로는 IP 주소 접속 문제가 해결되지 않을 수 있습니다.

## 현재 권장 방법

### 즉시 사용: HTTP 직접 접속
```
http://192.168.0.9:8001/docs
http://192.168.0.9:8001/tests/user_testing/test_chat_interface.html
```

### HTTPS 사용: hosts 파일에 도메인 추가
1. hosts 파일에 `192.168.0.9    llm-gateway.local` 추가
2. Caddyfile에 도메인 블록 활성화
3. `https://llm-gateway.local/docs` 접속

## 인증서 정보

**인증서 위치:**
- 컨테이너 내부: `/data/caddy/pki/authorities/local/`
- 볼륨: `llm-gateway_caddy-data`

**인증서 파일:**
- `root.crt`: 루트 인증서
- `root.key`: 루트 키
- `intermediate.crt`: 중간 인증서
- `intermediate.key`: 중간 키

**인증서 확인:**
```bash
# 인증서 내용 확인
docker compose exec caddy cat /data/caddy/pki/authorities/local/root.crt

# 인증서 정보 확인
docker compose exec caddy openssl x509 -in /data/caddy/pki/authorities/local/root.crt -text -noout
```

## 향후 개선

도메인을 설정하면 Let's Encrypt 인증서를 사용할 수 있습니다:
- 브라우저 경고 없음
- 자동 인증서 갱신
- IP 주소 접속 문제 해결

자세한 내용은 `docs/LETSENCRYPT_SETUP_GUIDE.md`를 참고하세요.

