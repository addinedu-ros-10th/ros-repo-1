# 환경별 Caddy 설정 자동 분리 시스템

## 🎯 **개요**

IoT Care Backend System은 환경별로 다른 Caddy 설정을 자동으로 적용하는 시스템을 제공합니다.

## 🌍 **지원 환경**

| 환경 | 감지 방법 | Caddy 설정 파일 | 용도 |
|------|-----------|----------------|------|
| **Local** | 기본값 | `Caddyfile` | 로컬 개발 환경 |
| **Development** | Docker 컨테이너 감지 | `Caddyfile.dev` | 개발 서버 환경 |
| **Production** | AWS EC2 메타데이터 감지 | `Caddyfile.prod` | 운영 서버 환경 |

## 📁 **파일 구조**

```
services/was-server/
├── Caddyfile              # 로컬 환경 기본 설정
├── Caddyfile.local        # 로컬 환경 전용 설정
├── Caddyfile.dev          # 개발 환경 전용 설정
├── Caddyfile.prod         # 프로덕션 환경 전용 설정
├── scripts/
│   ├── detect_environment.sh      # 환경 자동 감지 스크립트
│   └── setup_local_caddy.sh       # 로컬 환경 설정 스크립트
└── docker-compose*.yml    # 환경별 Docker Compose 설정
```

## 🚀 **사용 방법**

### **1. 로컬 환경**

```bash
# 로컬 환경 설정 확인
bash scripts/setup_local_caddy.sh

# Docker 컨테이너 시작
docker-compose up -d
```

### **2. 개발 환경**

```bash
# 개발 환경 시작
docker-compose -f docker-compose.dev.yml up -d
```

### **3. 프로덕션 환경**

```bash
# 프로덕션 환경 시작
docker-compose -f docker-compose.prod.yml up -d
```

## 🔧 **자동 감지 시스템**

### **환경 감지 로직**

1. **AWS EC2 환경**: `http://169.254.169.254/latest/meta-data/instance-id` 접근 가능 여부
2. **Docker 환경**: `/.dockerenv` 파일 존재 또는 `/proc/1/cgroup`에서 docker 확인
3. **로컬 환경**: 위 조건에 해당하지 않는 경우 (기본값)

### **자동 설정 적용**

- **Local**: `Caddyfile` → `/etc/caddy/Caddyfile`
- **Development**: `Caddyfile.dev` → `/etc/caddy/Caddyfile`
- **Production**: `Caddyfile.prod` → `/etc/caddy/Caddyfile`

## 📋 **환경별 설정 특징**

### **Local Environment**
- HTTP만 지원 (포트 80)
- CORS 허용
- 개발용 로깅
- 간단한 리버스 프록시

### **Development Environment**
- HTTP만 지원 (포트 8080)
- CORS 허용
- 개발용 로깅
- 상세한 에러 정보

### **Production Environment**
- HTTP/HTTPS 지원 (포트 80, 443)
- 보안 헤더 설정
- 성능 최적화 (Gzip 압축)
- 상세한 로깅
- Swagger UI 지원

## 🚨 **문제 해결**

### **1. 환경 감지 실패**

```bash
# 환경 감지 스크립트 수동 실행
bash scripts/detect_environment.sh

# 로그 확인
docker logs iot-care-caddy
```

### **2. Caddy 설정 적용 실패**

```bash
# 설정 파일 존재 확인
ls -la Caddyfile*

# Docker 컨테이너 재시작
docker-compose restart caddy
```

### **3. 네트워크 연결 문제**

```bash
# 컨테이너 네트워크 확인
docker network ls
docker network inspect was-server_iot-care-network

# 컨테이너 상태 확인
docker-compose ps
```

## 🔄 **설정 변경 시**

환경별 Caddy 설정을 변경한 후:

1. **설정 파일 수정**
2. **Docker 컨테이너 재시작**
   ```bash
   docker-compose restart caddy
   ```
3. **설정 적용 확인**
   ```bash
   docker logs iot-care-caddy
   ```

## 📝 **주의사항**

1. **환경 감지 스크립트**는 Docker 컨테이너 내부에서 실행되어야 합니다
2. **설정 파일 경로**는 컨테이너 내부 경로를 기준으로 합니다
3. **권한 문제**가 발생할 수 있으므로 스크립트 실행 권한을 확인하세요
4. **프로덕션 환경**에서는 보안 설정을 반드시 확인하세요

## 🎉 **장점**

- **자동화**: 환경별 설정 자동 감지 및 적용
- **일관성**: 동일한 코드베이스로 여러 환경 관리
- **유지보수성**: 환경별 설정 파일 분리로 관리 용이
- **확장성**: 새로운 환경 추가 시 스크립트만 수정
- **안정성**: 환경 감지 실패 시 기본값 사용
