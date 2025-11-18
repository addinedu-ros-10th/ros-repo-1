# 로봇 인식 데이터베이스 스키마 설계

## 개요

로봇 인식 시스템의 데이터베이스 스키마 설계 문서입니다. 4개 카테고리(ArUco 마커, OCR 텍스트, 얼굴, 전신)의 인식 이벤트와 레지스트리를 관리합니다.

## 데이터베이스 정보

- **DBMS**: PostgreSQL
- **스키마**: public (기본)
- **TimescaleDB**: detection_event 테이블은 하이퍼테이블로 변환 가능
- **마이그레이션**: Alembic 사용

---

## 공통 테이블

### detection_event

로봇 인식 이벤트 로그 테이블 (모든 카테고리 공통)

#### 테이블 구조

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| `detection_event_id` | UUID | PK, NOT NULL | 이벤트 고유 ID |
| `robot_id` | TEXT | NOT NULL | 로봇 ID |
| `category` | TEXT | NOT NULL | 인식 카테고리 ('aruco'\|'text'\|'face'\|'person') |
| `unique_key` | TEXT | NOT NULL | 고유 키 (마커/텍스트/얼굴해시/추적ID 등) |
| `meta` | JSONB | NOT NULL | 카테고리별 부가정보 |
| `detected_at` | TIMESTAMP(timezone) | NOT NULL | 인식 시간(로봇 기준 UTC 권장) |
| `processing_info` | JSONB | NOT NULL | 처리 정보 (intent/api_calls/cmds/scenario_state) |
| `processed_status` | TEXT | NOT NULL, DEFAULT 'accepted' | 처리 상태 ('accepted'\|'done'\|'failed') |
| `created_at` | TIMESTAMP(timezone) | NOT NULL, DEFAULT now() | 생성 시간 |

#### 인덱스

```sql
-- 시간 기반 조회 최적화
CREATE INDEX idx_detection_event_time ON detection_event (detected_at DESC);

-- 카테고리와 키 조합 조회 최적화
CREATE INDEX idx_detection_event_cat_key ON detection_event (category, unique_key);

-- 로봇별 조회 최적화
CREATE INDEX idx_detection_event_robot ON detection_event (robot_id);

-- 처리 상태 조회 최적화
CREATE INDEX idx_detection_event_status ON detection_event (processed_status);
```

#### TimescaleDB 하이퍼테이블

```sql
-- TimescaleDB 확장이 있는 경우 하이퍼테이블로 변환
SELECT create_hypertable('detection_event', 'detected_at', if_not_exists => TRUE);
```

#### ENUM 타입

```sql
-- detection_category ENUM
CREATE TYPE detection_category AS ENUM ('aruco', 'text', 'face', 'person');

-- intent_type ENUM
CREATE TYPE intent_type AS ENUM ('open_door', 'start_follow', 'stop_follow', 'announce', 'none');
```

---

## 카테고리별 레지스트리 테이블

### marker_registry

ArUco 마커 레지스트리 테이블

#### 테이블 구조

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| `marker_key` | TEXT | PK, NOT NULL | 마커 키 (예: 'ARUCO_23') |
| `entrance_id` | TEXT | NULL | 출입구/구역 식별 |
| `zone` | TEXT | NULL | 구역 |
| `pose` | JSONB | NULL | 고정 좌표/자세 |
| `description` | TEXT | NULL | 설명 |
| `action_plan` | JSONB | NULL | 기본 처리 계획 |
| `updated_at` | TIMESTAMP(timezone) | NOT NULL, DEFAULT now() | 수정 시간 |

#### 샘플 데이터

```json
{
  "marker_key": "ARUCO_23",
  "entrance_id": "E-1",
  "zone": "Hall-A",
  "pose": {
    "x": 5.0,
    "y": -1.0,
    "yaw": -80.0
  },
  "description": "1층 로비 출입구",
  "action_plan": {
    "intent": "open_door",
    "api_calls": [
      {
        "method": "POST",
        "url": "https://sec.local/door/open",
        "body": {
          "entrance_id": "E-1"
        }
      }
    ]
  }
}
```

---

### text_registry

OCR 텍스트 레지스트리 테이블

#### 테이블 구조

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| `text_key` | TEXT | PK, NOT NULL | 텍스트 키 (예: '식당') |
| `room_code` | TEXT | NULL | 방 코드 |
| `lang` | TEXT | NULL | 언어 (예: 'ko', 'en') |
| `synonyms` | TEXT[] | NULL | 유사 표현 배열 |
| `action_plan` | JSONB | NULL | 기본 처리 계획 |
| `updated_at` | TIMESTAMP(timezone) | NOT NULL, DEFAULT now() | 수정 시간 |

#### 샘플 데이터

```json
{
  "text_key": "식당",
  "room_code": "DINING-01",
  "lang": "ko",
  "synonyms": ["식당", "레스토랑", "다이닝"],
  "action_plan": {
    "intent": "announce",
    "cmds": [
      {
        "topic": "/robot/say",
        "payload": {
          "text": "식당에 도착했습니다."
        }
      }
    ]
  }
}
```

---

### face_registry

얼굴 레지스트리 테이블 (PII 보호)

#### 테이블 구조

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| `face_key` | TEXT | PK, NOT NULL | 얼굴 식별키 해시 |
| `role` | TEXT | NULL | 역할 ('elder'\|'caregiver'\|'visitor') |
| `consent` | BOOLEAN | NOT NULL, DEFAULT false | 동의 여부 |
| `pii_ref` | TEXT | NULL | 외부 금고/암호화 저장소 key(선택) |
| `policy` | JSONB | NULL | 보관기간/마스킹 등 |
| `action_plan` | JSONB | NULL | 기본 처리 계획 |
| `updated_at` | TIMESTAMP(timezone) | NOT NULL, DEFAULT now() | 수정 시간 |

#### 제약조건

```sql
-- role 제약조건
ALTER TABLE face_registry 
ADD CONSTRAINT ck_face_registry_role 
CHECK (role IN ('elder', 'caregiver', 'visitor'));
```

#### 샘플 데이터

```json
{
  "face_key": "facehash_abcd1234",
  "role": "visitor",
  "consent": true,
  "pii_ref": "pii_vault_key_xyz789",
  "policy": {
    "retention_days": 90,
    "masking": true
  },
  "action_plan": {
    "intent": "announce",
    "cmds": [
      {
        "topic": "/robot/notify",
        "payload": {
          "type": "VISITOR_ARRIVED"
        }
      }
    ]
  }
}
```

---

### person_registry

전신/개인 프로필 레지스트리 테이블

#### 테이블 구조

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| `person_key` | TEXT | PK, NOT NULL | 개인 논리 키 (예: 'track_006') |
| `preferred_follow_distance_m` | NUMERIC(4,2) | NULL, DEFAULT 1.5 | 선호 추종 거리(m) |
| `mobility_level` | TEXT | NULL | 보행속도/주의필요 등 |
| `action_plan` | JSONB | NULL | 기본 처리 계획 |
| `updated_at` | TIMESTAMP(timezone) | NOT NULL, DEFAULT now() | 수정 시간 |

#### 샘플 데이터

```json
{
  "person_key": "track_006",
  "preferred_follow_distance_m": 1.5,
  "mobility_level": "normal",
  "action_plan": {
    "intent": "start_follow",
    "cmds": [
      {
        "topic": "/robot/cmd",
        "payload": {
          "type": "FOLLOW",
          "target_id": "track_006",
          "distance": 1.5
        }
      }
    ]
  }
}
```

---

## 테이블 관계

```
detection_event (공통 이벤트 로그)
    │
    ├── marker_registry (ArUco 마커 레지스트리)
    │   └── unique_key → marker_key
    │
    ├── text_registry (OCR 텍스트 레지스트리)
    │   └── unique_key → text_key
    │
    ├── face_registry (얼굴 레지스트리)
    │   └── unique_key → face_key
    │
    └── person_registry (전신 레지스트리)
        └── unique_key → person_key
```

**참고**: 현재는 논리적 관계만 존재하며, 외래키 제약조건은 없습니다. `detection_event.unique_key`와 각 레지스트리 테이블의 키가 논리적으로 연결됩니다.

---

## 마이그레이션

### 마이그레이션 파일

- **파일 경로**: `app/infrastructure/db/migrations/versions/20251110_create_robot_detection_tables.py`
- **Revision ID**: `20251110_robot_detection`
- **Down Revision**: `aaf84b4b99c7`

### 마이그레이션 실행

```bash
# 마이그레이션 실행
alembic upgrade head

# 마이그레이션 롤백
alembic downgrade -1
```

---

## 데이터 타입 상세

### JSONB 필드 구조

#### detection_event.meta

카테고리별로 다른 구조를 가집니다:

**ArUco 마커 (aruco)**
```json
{
  "entrance_id": "E-1",
  "zone": "Hall-A",
  "bbox": [120, 80, 64, 64],
  "confidence": 0.95,
  "pose": {
    "x": 5.0,
    "y": -1.0,
    "yaw": -80.0
  }
}
```

**OCR 텍스트 (text)**
```json
{
  "lang": "ko",
  "room_code": "DINING-01",
  "synonyms": ["식당", "레스토랑"],
  "bbox": [200, 60, 120, 45],
  "confidence": 0.88,
  "raw_text": "식당"
}
```

**얼굴 (face)**
```json
{
  "role": "visitor",
  "consent": "Y",
  "last_verified_at": "2025-11-10T10:21:50Z",
  "confidence": 0.92,
  "bbox": [150, 100, 80, 100]
}
```

**전신 (person)**
```json
{
  "distance_m": 1.8,
  "pose": {
    "x": 2.5,
    "y": -0.5,
    "yaw": 0.12
  },
  "velocity": {
    "vx": 0.3,
    "vy": 0.0,
    "vz": 0.0
  },
  "lost": false,
  "mobility_level": "normal",
  "confidence": 0.90
}
```

#### detection_event.processing_info

```json
{
  "intent": "open_door|start_follow|stop_follow|announce|none",
  "api_calls": [
    {
      "method": "POST",
      "url": "https://sec.local/door/open",
      "headers": {},
      "body": {
        "entrance_id": "E-1"
      }
    }
  ],
  "cmds": [
    {
      "topic": "/robot/cmd",
      "payload": {
        "type": "FOLLOW",
        "target_id": "track_006",
        "distance": 1.5
      }
    }
  ],
  "scenario_state": "INIT|RUN|END"
}
```

---

## 성능 최적화

### 인덱스 전략

1. **시간 기반 조회**: `idx_detection_event_time` (detected_at DESC)
2. **카테고리별 조회**: `idx_detection_event_cat_key` (category, unique_key)
3. **로봇별 조회**: `idx_detection_event_robot` (robot_id)
4. **상태별 조회**: `idx_detection_event_status` (processed_status)

### TimescaleDB 활용

- `detection_event` 테이블을 하이퍼테이블로 변환
- 시계열 데이터 최적화
- 자동 파티셔닝 및 데이터 보관 정책 적용 가능

### 쿼리 최적화 팁

```sql
-- 카테고리별 최근 이벤트 조회
SELECT * FROM detection_event
WHERE category = 'aruco'
  AND detected_at >= NOW() - INTERVAL '1 day'
ORDER BY detected_at DESC
LIMIT 100;

-- 특정 마커의 이벤트 조회
SELECT * FROM detection_event
WHERE category = 'aruco'
  AND unique_key = 'ARUCO_23'
ORDER BY detected_at DESC;

-- 레지스트리와 조인 (논리적)
SELECT de.*, mr.entrance_id, mr.zone
FROM detection_event de
LEFT JOIN marker_registry mr ON de.unique_key = mr.marker_key
WHERE de.category = 'aruco'
  AND de.detected_at >= NOW() - INTERVAL '1 day';
```

---

## 보안 및 PII 보호

### 얼굴 데이터 보호

1. **해시만 저장**: 원본 얼굴 이미지는 저장하지 않음
2. **외부 금고**: `pii_ref` 필드로 별도 암호화 저장소 참조
3. **보관 정책**: `policy` 필드로 보관기간 및 마스킹 정책 관리
4. **동의 관리**: `consent` 필드로 동의 여부 필수 확인

### 접근 제어

- 레지스트리 조회는 인증된 사용자만 가능
- 얼굴 데이터는 역할 기반 접근 제어 적용

---

## 백업 및 복구

### 백업 전략

1. **일일 백업**: 전체 데이터베이스 백업
2. **증분 백업**: 변경된 데이터만 백업
3. **레지스트리 백업**: 레지스트리 테이블은 별도 백업

### 복구 절차

1. 마이그레이션 롤백: `alembic downgrade -1`
2. 데이터 복구: PostgreSQL 백업 파일 복원
3. 마이그레이션 재실행: `alembic upgrade head`

---

## 관련 문서

- [인터페이스 명세서](../interfaces/README.md)
- [API 문서](../apis/robot_detections_api.md)
- [개발 리포트](../development/commit_report_20251110.md)

