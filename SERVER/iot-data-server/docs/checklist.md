# IoT Care Backend Service 개발 체크리스트

## 🎯 **전체 프로젝트 목표**
- [x] Clean Architecture 기반 백엔드 서비스 구축
- [x] 25개 ORM 모델에 대한 완전한 RESTful API 구현
- [x] 모든 API의 완벽한 작동 보장 ("완벽주의" 접근)
- [ ] 전체 API 통합 테스트 완료
- [ ] 사용자 수동 테스트 가이드 제공

## 🗄️ **데이터베이스 인프라**
- [x] PostgreSQL 데이터베이스 연결 설정
- [x] Docker 환경에서의 데이터베이스 연결 문제 해결
- [x] 데이터베이스 스키마 일관성 확보
- [x] 25개 ORM 모델에 대한 테이블 생성
- [x] Alembic 마이그레이션 설정 (수동 스크립트로 대체)

## 🔧 **ORM 모델 구현**
### **핵심 엔티티**
- [x] Users (사용자 관리)
- [x] Devices (디바이스 관리)
- [x] DeviceRTCStatus (디바이스 RTC 상태)

### **Raw 센서 모델**
- [x] SensorRawCDS (광센서)
- [x] SensorRawDHT (온습도 센서)
- [x] SensorRawFlame (화재 감지 센서)
- [x] SensorRawIMU (관성 측정 센서)
- [x] SensorRawLoadCell (무게 센서)
- [x] SensorRawMQ5 (가스 센서)
- [x] SensorRawMQ7 (일산화탄소 센서)
- [x] SensorRawRFID (RFID 리더)
- [x] SensorRawSound (소리 센서)
- [x] SensorRawTCRT5000 (적외선 센서)
- [x] SensorRawUltrasonic (초음파 센서)

### **Edge 센서 모델**
- [x] SensorEdgeFlame (Edge 화재 감지)
- [x] SensorEdgePIR (Edge 모션 감지)
- [x] SensorEdgeReed (Edge 자기장 감지)
- [x] SensorEdgeTilt (Edge 기울기 감지)

### **Actuator 로그 모델**
- [x] ActuatorLogBuzzer (부저 제어 로그)
- [x] ActuatorLogIRTX (적외선 송신 로그)
- [x] ActuatorLogRelay (릴레이 제어 로그)
- [x] ActuatorLogServo (서보 모터 제어 로그)

## 🌐 **RESTful API 구현**
### **핵심 API**
- [x] **User API** - 사용자 CRUD, 이메일 중복 검증
- [x] **Device API** - 디바이스 CRUD, 사용자 할당
- [ ] **DeviceRTCStatus API** - 디바이스 RTC 상태 관리

### **Raw 센서 API**
- [x] **CDS API** - 광센서 데이터 CRUD
- [x] **DHT API** - 온습도 센서 데이터 CRUD
- [x] **Flame API** - 화재 감지 센서 데이터 CRUD
- [x] **IMU API** - 관성 측정 센서 데이터 CRUD
- [x] **LoadCell API** - 무게 센서 데이터 CRUD
- [x] **MQ5 API** - 가스 센서 데이터 CRUD
- [x] **MQ7 API** - 일산화탄소 센서 데이터 CRUD
- [x] **RFID API** - RFID 리더 데이터 CRUD
- [x] **Sound API** - 소리 센서 데이터 CRUD
- [x] **TCRT5000 API** - 적외선 센서 데이터 CRUD
- [x] **Ultrasonic API** - 초음파 센서 데이터 CRUD

### **Edge 센서 API**
- [x] **Edge Flame API** - Edge 화재 감지 데이터 CRUD
- [x] **Edge PIR API** - Edge 모션 감지 데이터 CRUD
- [x] **Edge Reed API** - Edge 자기장 감지 데이터 CRUD
- [x] **Edge Tilt API** - Edge 기울기 감지 데이터 CRUD

### **Actuator API**
- [x] **Buzzer API** - 부저 제어 로그 CRUD
- [x] **IRTX API** - 적외선 송신 로그 CRUD
- [x] **Relay API** - 릴레이 제어 로그 CRUD
- [x] **Servo API** - 서보 모터 제어 로그 CRUD

## 🏗️ **아키텍처 구현**
### **Clean Architecture**
- [x] 인터페이스 계층 (API, Schemas)
- [x] 도메인 계층 (Entities, Services)
- [x] 인프라 계층 (Repositories, Database)

### **의존성 주입 (DI)**
- [x] DI 컨테이너 구현
- [x] FastAPI Depends 활용
- [x] 데이터베이스 세션 주입

### **패턴 구현**
- [x] Repository Pattern
- [x] Service Layer Pattern
- [x] Factory Pattern

## 🧪 **테스트 및 검증**
### **API 통합 테스트**
- [ ] User API 전체 시나리오 테스트
- [ ] Device API 전체 시나리오 테스트
- [ ] Raw 센서 API 전체 시나리오 테스트
- [ ] Edge 센서 API 전체 시나리오 테스트
- [ ] Actuator API 전체 시나리오 테스트

### **데이터 검증**
- [x] Pydantic 스키마 검증
- [x] 비즈니스 로직 검증
- [x] 데이터베이스 제약 조건 검증

### **성능 및 안정성**
- [ ] API 응답 시간 측정
- [ ] 동시 요청 처리 테스트
- [ ] 에러 상황 복구 테스트

## 📚 **문서화**
- [x] API 스키마 자동 생성 (OpenAPI)
- [x] 코드 주석 및 docstring
- [x] 개발 현황 문서
- [ ] API 사용 가이드
- [ ] 배포 가이드

## 🚀 **배포 및 운영**
- [x] Docker 컨테이너화
- [x] Docker Compose 설정
- [x] 환경별 설정 파일 (.env)
- [ ] CI/CD 파이프라인
- [ ] 모니터링 및 로깅

## 🔍 **품질 관리**
- [x] 타입 힌팅 적용
- [x] 에러 처리 구현
- [x] 로깅 구현
- [ ] 코드 커버리지 측정
- [ ] 정적 코드 분석

---
*마지막 업데이트: 2025-08-21*
*전체 진행률: 75%*
*완료된 항목: 45/60* 