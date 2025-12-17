# 지난 커밋 개발 내용 리포트

## 커밋 정보

- **커밋 해시**: `7f04782550e5e51eb44f004ff04292b1edb7a985`
- **브랜치**: `feat/SERVER/app-server__DL_model_interface__RP-57__app-server_init`
- **커밋 메시지**: `feat: 로봇 인식 이벤트 수집 API 구현 (ArUco, OCR, Face, Person)`
- **작성일**: 2025-11-10

---

## 개발 개요

로봇 인식 이벤트 수집 API를 구현하여 4개 카테고리(ArUco 마커, OCR 텍스트, 얼굴, 전신)의 인식 결과를 수집하고 처리하는 시스템을 구축했습니다.

---

## 주요 변경사항

### 1. 도메인 레이어

#### 엔티티 (Domain Entities)
- **파일**: `app/domain/entities/robot_detection_event.py`
- **내용**:
  - `RobotDetectionEvent`: 로봇 인식 이벤트 엔티티
  - `ProcessingInfo`: 처리 정보 (intent, api_calls, cmds, scenario_state)
  - `APICall`: API 호출 정보
  - `Cmd`: ROS2/메시지 큐 명령

#### 포트 인터페이스 (Domain Ports)
- **파일**: `app/domain/ports/robot_detection_repository.py`
- **내용**:
  - `RobotDetectionRepository`: 인식 이벤트 리포지토리 인터페이스
  - `MarkerRegistryRepository`: ArUco 마커 레지스트리 인터페이스
  - `TextRegistryRepository`: OCR 텍스트 레지스트리 인터페이스
  - `FaceRegistryRepository`: 얼굴 레지스트리 인터페이스
  - `PersonRegistryRepository`: 전신 레지스트리 인터페이스

### 2. 애플리케이션 레이어

#### DTO (Data Transfer Objects)
- **파일**: `app/application/dto/robot_detection_dto.py`
- **내용**:
  - `RobotDetectionCreateRequest`: 인식 이벤트 생성 요청
  - `RobotDetectionResponse`: 인식 이벤트 응답
  - `RegistryResponse`: 레지스트리 응답
  - `ProcessingInfoRequest/Response`: 처리 정보 요청/응답

#### 유즈케이스 (Use Cases)
- **파일**: `app/application/use_cases/robot_detection_use_cases.py`
- **내용**:
  - `CreateRobotDetectionUseCase`: 인식 이벤트 생성 및 레지스트리 업데이트
  - `GetRobotDetectionUseCase`: 인식 이벤트 단건 조회
  - `ListRobotDetectionsUseCase`: 인식 이벤트 목록 조회
  - `GetRegistryUseCase`: 레지스트리 조회

### 3. 인프라 레이어

#### 데이터베이스 모델
- **파일**: `app/infrastructure/db/models/robot_detection_models.py`
- **내용**:
  - `RobotDetectionEventModel`: 인식 이벤트 모델
  - `MarkerRegistryModel`: ArUco 마커 레지스트리 모델
  - `TextRegistryModel`: OCR 텍스트 레지스트리 모델
  - `FaceRegistryModel`: 얼굴 레지스트리 모델 (PII 보호)
  - `PersonRegistryModel`: 전신 레지스트리 모델

#### 리포지토리 구현
- **파일**: `app/adapters/repositories/robot_detection_repository_impl.py`
- **내용**:
  - `RobotDetectionRepositoryImpl`: 인식 이벤트 리포지토리 구현
  - `MarkerRegistryRepositoryImpl`: ArUco 마커 레지스트리 구현
  - `TextRegistryRepositoryImpl`: OCR 텍스트 레지스트리 구현
  - `FaceRegistryRepositoryImpl`: 얼굴 레지스트리 구현
  - `PersonRegistryRepositoryImpl`: 전신 레지스트리 구현

#### 마이그레이션
- **파일**: `app/infrastructure/db/migrations/versions/20251110_create_robot_detection_tables.py`
- **내용**:
  - `detection_event` 테이블 생성
  - `marker_registry` 테이블 생성
  - `text_registry` 테이블 생성
  - `face_registry` 테이블 생성
  - `person_registry` 테이블 생성
  - TimescaleDB 하이퍼테이블 변환 (조건부)
  - 인덱스 생성

### 4. 어댑터 레이어

#### HTTP 라우터
- **파일**: `app/adapters/http/robot_detection_router.py`
- **내용**:
  - `POST /api/v1/detections`: 인식 이벤트 수집
  - `GET /api/v1/detections`: 인식 이벤트 목록 조회
  - `GET /api/v1/detections/{event_id}`: 인식 이벤트 단건 조회
  - `GET /api/v1/detections/registry/{category}/{unique_key}`: 레지스트리 조회
  - `POST /api/v1/detections/actions/execute`: 액션 수동 실행

### 5. 서비스 레이어

#### 액션 실행기
- **파일**: `app/services/robot_detection_action_executor.py`
- **내용**:
  - `RobotDetectionActionExecutor`: 로봇 인식 이벤트 액션 실행기
  - Redis Streams를 통한 비동기 액션 처리
  - API 호출 및 ROS2 명령 실행

### 6. 테스트

#### 통합 테스트
- **파일**: `tests/integration/test_robot_detection_api.py`
- **내용**:
  - ArUco 마커 인식 이벤트 생성 테스트
  - OCR 텍스트 인식 이벤트 생성 테스트
  - 인식 이벤트 목록 조회 테스트

### 7. 문서

#### API 문서
- **파일**: `docs/apis/robot_detections_api.md`
- **내용**:
  - API 엔드포인트 상세 설명
  - 카테고리별 샘플 페이로드
  - 에러 응답 예시

---

## 추가된 파일 목록

### 도메인 레이어
- `app/domain/entities/robot_detection_event.py`
- `app/domain/ports/robot_detection_repository.py`

### 애플리케이션 레이어
- `app/application/dto/robot_detection_dto.py`
- `app/application/use_cases/robot_detection_use_cases.py`

### 인프라 레이어
- `app/infrastructure/db/models/robot_detection_models.py`
- `app/infrastructure/db/migrations/versions/20251110_create_robot_detection_tables.py`
- `app/adapters/repositories/robot_detection_repository_impl.py`

### 어댑터 레이어
- `app/adapters/http/robot_detection_router.py`

### 서비스 레이어
- `app/services/robot_detection_action_executor.py`

### 테스트
- `tests/integration/test_robot_detection_api.py`

### 문서
- `docs/apis/robot_detections_api.md`

---

## 주요 기능

### 1. 인식 이벤트 수집
- 4개 카테고리(ArUco, OCR, Face, Person)의 인식 결과 수집
- 카테고리별 메타 데이터 저장
- 처리 정보(intent, api_calls, cmds) 포함

### 2. 레지스트리 관리
- 카테고리별 레지스트리 자동 생성/업데이트
- ArUco 마커: 출입구, 구역, 좌표 정보
- OCR 텍스트: 방 코드, 언어, 유사 표현
- 얼굴: 역할, 동의 여부, PII 보호 정책
- 전신: 선호 추종 거리, 보행 속도

### 3. 액션 실행
- Redis Streams를 통한 비동기 액션 처리
- API 호출 실행
- ROS2/메시지 큐 명령 발행

### 4. 조회 기능
- 필터링 조건으로 인식 이벤트 목록 조회
- 카테고리별 레지스트리 조회
- 단건 조회

---

## 아키텍처 패턴

### 헥사고날 아키텍처
- **도메인 레이어**: 비즈니스 로직 및 엔티티
- **애플리케이션 레이어**: 유즈케이스 및 DTO
- **인프라 레이어**: 데이터베이스 모델 및 리포지토리 구현
- **어댑터 레이어**: HTTP 라우터

### Repository Pattern
- 인터페이스와 구현 분리
- 테스트 용이성 향상
- 의존성 역전 원칙 적용

### Dependency Injection
- FastAPI의 Depends를 통한 의존성 주입
- 리포지토리 및 레지스트리 주입

---

## 데이터베이스 설계

### 공통 테이블
- `detection_event`: 인식 이벤트 로그 (모든 카테고리 공통)

### 카테고리별 레지스트리 테이블
- `marker_registry`: ArUco 마커 레지스트리
- `text_registry`: OCR 텍스트 레지스트리
- `face_registry`: 얼굴 레지스트리 (PII 보호)
- `person_registry`: 전신 레지스트리

### 인덱스
- 시간 기반 조회 최적화
- 카테고리와 키 조합 조회 최적화
- 로봇별 조회 최적화
- 처리 상태 조회 최적화

### TimescaleDB 지원
- `detection_event` 테이블을 하이퍼테이블로 변환 가능
- 시계열 데이터 최적화

---

## 보안 및 PII 보호

### 얼굴 데이터 보호
- 얼굴 식별키는 해시만 저장
- 원본 얼굴 이미지는 저장하지 않음
- 외부 금고 연동 지원 (`pii_ref`)
- 보관 정책 관리 (`policy`)

### 접근 제어
- `X-Robot-ID` 헤더 필수
- 향후 JWT 인증 지원 예정

---

## 성능 최적화

### 인덱스 전략
- 시간 기반 인덱스 (DESC)
- 카테고리와 키 조합 인덱스
- 로봇별 인덱스
- 처리 상태 인덱스

### 비동기 처리
- Redis Streams를 통한 비동기 액션 처리
- 워커를 통한 실제 액션 실행

---

## 향후 개선 사항

### 1. AI 서버 연동
- ArUco 마커 인식 요청
- OCR 텍스트 인식 요청
- 얼굴 인식 요청
- 전신 추적 시작/중단 명령

### 2. 인증 및 권한
- JWT 토큰 기반 인증
- 역할 기반 접근 제어

### 3. 모니터링 및 로깅
- 구조화된 로깅
- 메트릭 수집
- 알림 시스템 연동

### 4. 성능 최적화
- 캐싱 전략
- 배치 처리
- 쿼리 최적화

---

## 관련 문서

- [인터페이스 명세서](../interfaces/README.md)
- [DB 설계 문서](../database/robot_detection_schema.md)
- [API 문서](../apis/robot_detections_api.md)

---

## 결론

이번 커밋에서는 로봇 인식 이벤트 수집 API를 완전히 구현하여 4개 카테고리의 인식 결과를 수집하고 처리할 수 있는 시스템을 구축했습니다. 헥사고날 아키텍처 패턴을 따르며, 확장 가능하고 테스트 가능한 구조로 설계되었습니다.

