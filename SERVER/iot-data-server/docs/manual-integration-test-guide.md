# IoT Care Backend System 수동 통합 테스트 가이드

## 📋 개요

이 가이드는 IoT Care Backend System의 모든 API를 수동으로 테스트하는 방법을 설명합니다. 총 25개의 테이블 API가 모두 구현되어 있으며, Clean Architecture를 준수하여 개발되었습니다.

## 🚀 테스트 환경 준비

### 1. 시스템 시작
```bash
# 프로젝트 디렉토리로 이동
cd services/was-server

# Docker Compose로 시스템 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 2. 서비스 상태 확인
```bash
# 컨테이너 상태 확인
docker-compose ps

# 네트워크 상태 확인
docker network ls
```

### 3. API 문서 접근
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **API Base URL**: http://localhost:8080/api/v1

## 🧪 API 테스트 순서

### Phase 1: 기본 연결 테스트

#### 1.1 헬스체크
```bash
curl -X GET "http://localhost:8080/health" \
  -H "accept: application/json"
```

**예상 응답:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-19T10:00:00Z",
  "version": "1.0.0"
}
```

### Phase 2: User API 테스트

#### 2.1 사용자 생성
```bash
curl -X POST "http://localhost:8080/api/v1/users/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": true
  }'
```

#### 2.2 사용자 목록 조회
```bash
curl -X GET "http://localhost:8080/api/v1/users/" \
  -H "accept: application/json"
```

#### 2.3 사용자 통계 조회
```bash
curl -X GET "http://localhost:8080/api/v1/users/statistics" \
  -H "accept: application/json"
```

### Phase 3: 센서 API 테스트

#### 3.1 LoadCell API 테스트
```bash
# LoadCell 데이터 생성
curl -X POST "http://localhost:8080/api/v1/loadcell/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "time": "2024-12-19T10:00:00Z",
    "device_id": "loadcell_001",
    "weight_g": 1500.5,
    "calibration_factor": 1.02,
    "temperature_c": 25.0,
    "raw_adc_value": 2048,
    "status": "stable"
  }'

# LoadCell 데이터 목록 조회
curl -X GET "http://localhost:8080/api/v1/loadcell/" \
  -H "accept: application/json"

# LoadCell 통계 조회
curl -X GET "http://localhost:8080/api/v1/loadcell/loadcell_001/statistics" \
  -H "accept: application/json"
```

#### 3.2 MQ5 API 테스트
```bash
# MQ5 데이터 생성
curl -X POST "http://localhost:8080/api/v1/mq5/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "time": "2024-12-19T10:00:00Z",
    "device_id": "mq5_001",
    "gas_concentration_ppm": 45.2,
    "raw_adc_value": 512,
    "temperature_c": 25.0,
    "humidity_percent": 60.0,
    "status": "normal"
  }'

# MQ5 통계 조회
curl -X GET "http://localhost:8080/api/v1/mq5/mq5_001/statistics" \
  -H "accept: application/json"
```

#### 3.3 RFID API 테스트
```bash
# RFID 데이터 생성
curl -X POST "http://localhost:8080/api/v1/rfid/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "time": "2024-12-19T10:00:00Z",
    "device_id": "rfid_001",
    "tag_id": "1234567890ABCDEF",
    "tag_type": "MIFARE",
    "rssi": -45,
    "antenna_id": 1,
    "read_count": 1
  }'

# RFID 통계 조회
curl -X GET "http://localhost:8080/api/v1/rfid/rfid_001/statistics" \
  -H "accept: application/json"
```

### Phase 4: Actuator API 테스트

#### 4.1 ActuatorBuzzer API 테스트
```bash
# Buzzer 데이터 생성
curl -X POST "http://localhost:8080/api/v1/actuator-buzzer/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "time": "2024-12-19T10:00:00Z",
    "device_id": "buzzer_001",
    "buzzer_type": "piezo",
    "state": "on",
    "freq_hz": 1000,
    "duration_ms": 500,
    "reason": "alert"
  }'

# Buzzer 통계 조회
curl -X GET "http://localhost:8080/api/v1/actuator-buzzer/buzzer_001/statistics" \
  -H "accept: application/json"
```

#### 4.2 ActuatorRelay API 테스트
```bash
# Relay 데이터 생성
curl -X POST "http://localhost:8080/api/v1/actuator-relay/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "time": "2024-12-19T10:00:00Z",
    "device_id": "relay_001",
    "channel": 1,
    "state": "on",
    "voltage_v": 12.0,
    "current_ma": 100,
    "reason": "manual_control"
  }'

# Relay 통계 조회
curl -X GET "http://localhost:8080/api/v1/actuator-relay/relay_001/statistics" \
  -H "accept: application/json"
```

#### 4.3 ActuatorServo API 테스트
```bash
# Servo 데이터 생성
curl -X POST "http://localhost:8080/api/v1/actuator-servo/" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "time": "2024-12-19T10:00:00Z",
    "device_id": "servo_001",
    "channel": 1,
    "angle_deg": 90,
    "pwm_us": 1500,
    "speed_rpm": 60,
    "reason": "position_control"
  }'

# Servo 통계 조회
curl -X GET "http://localhost:8080/api/v1/actuator-servo/servo_001/statistics" \
  -H "accept: application/json"
```

## 🔍 테스트 시나리오

### 시나리오 1: 기본 CRUD 작업
1. **Create**: 각 API에서 데이터 생성
2. **Read**: 생성된 데이터 조회 및 목록 확인
3. **Update**: 데이터 수정 및 변경사항 확인
4. **Delete**: 데이터 삭제 및 삭제 확인

### 시나리오 2: 통계 기능 테스트
1. **기본 통계**: 각 센서/액추에이터별 기본 통계 확인
2. **시간별 통계**: 시간 범위별 통계 데이터 확인
3. **상태별 통계**: 상태값별 분포 및 통계 확인

### 시나리오 3: 에러 처리 테스트
1. **잘못된 데이터**: 유효하지 않은 데이터로 API 호출
2. **존재하지 않는 리소스**: 존재하지 않는 ID로 조회/수정/삭제
3. **잘못된 형식**: 잘못된 JSON 형식으로 API 호출

### 시나리오 4: 성능 테스트
1. **대량 데이터**: 많은 수의 데이터 생성 및 조회
2. **동시 요청**: 여러 API를 동시에 호출
3. **응답 시간**: 각 API의 응답 시간 측정

## 📊 테스트 결과 기록

### 테스트 체크리스트
- [ ] User API: CRUD + 통계
- [ ] LoadCell API: CRUD + 통계
- [ ] MQ5 API: CRUD + 통계
- [ ] MQ7 API: CRUD + 통계
- [ ] RFID API: CRUD + 통계
- [ ] Sound API: CRUD + 통계
- [ ] TCRT5000 API: CRUD + 통계
- [ ] Ultrasonic API: CRUD + 통계
- [ ] EdgeFlame API: CRUD + 통계
- [ ] EdgePIR API: CRUD + 통계
- [ ] EdgeReed API: CRUD + 통계
- [ ] EdgeTilt API: CRUD + 통계
- [ ] DHT11 API: CRUD + 통계
- [ ] DHT22 API: CRUD + 통계
- [ ] DS18B20 API: CRUD + 통계
- [ ] HC-SR04 API: CRUD + 통계
- [ ] LDR API: CRUD + 통계
- [ ] PIR API: CRUD + 통계
- [ ] ActuatorBuzzer API: CRUD + 통계
- [ ] ActuatorIRTX API: CRUD + 통계
- [ ] ActuatorRelay API: CRUD + 통계
- [ ] ActuatorServo API: CRUD + 통계

### 성능 메트릭
| API | 응답시간(ms) | 처리량(req/s) | 에러율(%) |
|-----|-------------|---------------|-----------|
| User API | | | |
| LoadCell API | | | |
| MQ5 API | | | |
| ... | | | |

## 🚨 문제 해결

### 일반적인 문제들

#### 1. 연결 오류
```bash
# 컨테이너 상태 확인
docker-compose ps

# 컨테이너 재시작
docker-compose restart

# 로그 확인
docker-compose logs [service_name]
```

#### 2. 데이터베이스 연결 오류
```bash
# 데이터베이스 컨테이너 상태 확인
docker-compose ps postgres

# 데이터베이스 연결 테스트
docker-compose exec postgres psql -U svc_dev -d iot_care -c "SELECT 1;"
```

#### 3. API 응답 오류
- HTTP 상태 코드 확인
- 응답 본문의 에러 메시지 확인
- Swagger UI에서 API 스키마 검증

### 디버깅 도구

#### 1. 로그 확인
```bash
# 전체 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs fastapi

# 실시간 로그
docker-compose logs -f fastapi
```

#### 2. 데이터베이스 직접 접근
```bash
# PostgreSQL 컨테이너 접속
docker-compose exec postgres psql -U svc_dev -d iot_care

# 테이블 목록 확인
\dt

# 데이터 확인
SELECT * FROM users LIMIT 5;
```

## 📝 테스트 완료 후

### 1. 결과 요약 작성
- 테스트된 API 목록
- 발견된 문제점
- 성능 메트릭
- 개선 제안사항

### 2. 문제점 보고
- 버그 리포트 작성
- 성능 이슈 문서화
- 사용자 경험 개선 제안

### 3. 다음 단계 계획
- Phase 5: 고급 기능 구현
- Phase 6: 프로덕션 환경 준비
- 추가 테스트 시나리오 계획

## 🎯 성공 기준

### 기능적 요구사항
- [ ] 모든 25개 API가 정상 동작
- [ ] CRUD 작업이 모든 API에서 정상 수행
- [ ] 통계 기능이 모든 API에서 정상 작동
- [ ] 에러 처리가 일관되게 동작

### 비기능적 요구사항
- [ ] API 응답 시간 < 500ms (95%ile)
- [ ] 에러율 < 1%
- [ ] 시스템 안정성 (24시간 연속 운영)
- [ ] Clean Architecture 준수 검증

---

## 📞 지원 및 문의

테스트 과정에서 문제가 발생하거나 질문이 있으시면:
1. 로그 파일 확인
2. Swagger UI 문서 참조
3. 개발팀에 이슈 리포트 제출

**테스트 완료 후 결과를 공유해 주시면 다음 단계 진행을 도와드리겠습니다!**
