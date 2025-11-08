# LLM Gateway 프로젝트 DB 사용 현황 리포트

**작성일**: 2025-11-05  
**프로젝트**: AI/llm-gateway  
**브랜치**: `feat/AI/llm-gateway__voice_interface__RP-22`

---

## 📊 사용 중인 데이터베이스 목록

프로젝트에서는 **2개의 데이터베이스**를 사용하고 있습니다:

### 1. PostgreSQL (영구 저장용)
- **용도**: 대화 히스토리, API 로그, 비용 추적 등 영구 저장
- **타입**: 관계형 데이터베이스 (RDBMS)
- **위치**: 외부 DB (Docker 컨테이너 외부)
- **접근 방식**: SQLAlchemy ORM 사용

### 2. Redis (캐시/세션 관리용)
- **용도**: 세션 히스토리 캐싱, 빠른 읽기/쓰기
- **타입**: 인메모리 데이터 스토어
- **위치**: Docker Compose 컨테이너 (`llm-gateway-redis`)
- **접근 방식**: aioredis 라이브러리 사용

---

## 🗄️ PostgreSQL 데이터베이스 상세

### 데이터베이스 연결 설정

**환경변수 설정 방법**:
```env
# 방법 1: URL 사용 (권장)
DB_URL=postgresql://user:password@host:port/dbname

# 방법 2: 개별 설정
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=llm_gateway
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

### 테이블 구조

PostgreSQL에는 **4개의 테이블**이 있습니다:

#### 1. `conversation_sessions` (대화 세션)
**목적**: 대화 세션의 메타데이터 저장

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| session_id | VARCHAR(255) | PRIMARY KEY | 세션 고유 ID |
| user_id | VARCHAR(255) | NULL, INDEX | 사용자 ID (향후 확장용) |
| system_prompt | TEXT | NULL | 시스템 프롬프트 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 수정 시간 |

**인덱스**: `idx_user_created` (user_id, created_at)

#### 2. `conversation_messages` (대화 메시지)
**목적**: 각 세션의 대화 메시지 히스토리 저장

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | 메시지 고유 ID |
| session_id | VARCHAR(255) | NOT NULL, INDEX | 세션 ID |
| role | VARCHAR(50) | NOT NULL | 메시지 역할 (system, user, assistant) |
| content | TEXT | NOT NULL | 메시지 내용 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |

**인덱스**: `idx_session_created` (session_id, created_at)

#### 3. `api_request_logs` (API 요청 로그)
**목적**: 모든 API 요청을 로깅 (분석 및 디버깅용)

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | 로그 고유 ID |
| session_id | VARCHAR(255) | NULL, INDEX | 세션 ID |
| endpoint | VARCHAR(255) | NOT NULL | API 엔드포인트 |
| method | VARCHAR(10) | NOT NULL | HTTP 메서드 |
| request_data | JSON | NULL | 요청 데이터 (일부만 저장) |
| response_data | JSON | NULL | 응답 데이터 (요약 정보) |
| status_code | INTEGER | NOT NULL | HTTP 상태 코드 |
| processing_time_ms | FLOAT | NULL | 처리 시간 (밀리초) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |

**인덱스**: 
- `idx_session_created` (session_id, created_at)
- `idx_endpoint_created` (endpoint, created_at)

#### 4. `cost_logs` (비용 로그)
**목적**: OpenAI API 사용 비용 추적

| 컬럼명 | 타입 | 제약조건 | 설명 |
|--------|------|----------|------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | 로그 고유 ID |
| session_id | VARCHAR(255) | NULL, INDEX | 세션 ID |
| service_type | VARCHAR(50) | NOT NULL | 서비스 타입 (stt, chat, tts) |
| model | VARCHAR(100) | NOT NULL | 사용된 모델 |
| input_tokens | INTEGER | NULL | 입력 토큰 수 |
| output_tokens | INTEGER | NULL | 출력 토큰 수 |
| cost_usd | FLOAT | NOT NULL | 비용 (USD) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | 생성 시간 |

**인덱스**: 
- `idx_session_created` (session_id, created_at)
- `idx_service_created` (service_type, created_at)

---

## 🔴 Redis 데이터베이스 상세

### Redis 연결 설정

**환경변수 설정 방법**:
```env
# 방법 1: URL 사용
REDIS_URL=redis://:password@host:port

# 방법 2: 개별 설정
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_password
```

### Redis 사용 용도

#### 1. 세션 히스토리 캐싱
- **키 형식**: `session:{session_id}`
- **값 형식**: JSON 문자열 (메시지 배열)
- **TTL**: 30일 (자동 만료)
- **용도**: 빠른 세션 히스토리 읽기/쓰기

#### 2. 세션 관리
- 세션 존재 여부 확인
- 세션 목록 조회
- 세션 삭제

### Redis 최적화 설정

```yaml
# docker-compose.yml에서 설정
command: >
  redis-server 
    --requirepass $REDIS_PASSWORD
    --appendonly yes              # AOF 활성화 (데이터 영구성)
    --maxmemory 256mb             # 메모리 제한
    --maxmemory-policy allkeys-lru # LRU 정책
    --save 60 1000                # 자동 저장 설정
    --loglevel notice             # 로그 레벨
```

---

## 📋 LLM Chat Session 관리 현황

### ✅ 네, LLM Chat Session은 DB에서 관리하고 있습니다!

프로젝트는 **이중 저장 전략**을 사용합니다:

#### 1. Redis (캐시/세션 관리)
- **역할**: 빠른 읽기/쓰기를 위한 캐시
- **저장 내용**: 현재 활성 세션의 메시지 히스토리
- **TTL**: 30일
- **사용 위치**: 
  - `/api/chat`: 세션 히스토리 읽기/쓰기
  - `/api/chat/stream`: 스트리밍 채팅
  - `/api/voice/process`: 통합 음성 처리
  - `/ws/voice`: WebSocket 실시간 채팅

#### 2. PostgreSQL (영구 저장)
- **역할**: 영구 저장 및 백업
- **저장 내용**: 
  - 세션 메타데이터 (`conversation_sessions`)
  - 모든 메시지 히스토리 (`conversation_messages`)
- **저장 시점**: Redis 저장과 동시에 비동기로 저장
- **복구 기능**: Redis 장애 시 PostgreSQL에서 로드 가능

### 데이터 흐름

```
1. 클라이언트 요청
   ↓
2. Redis에서 세션 히스토리 읽기 (빠른 읽기)
   ↓
3. ChatGPT API 호출
   ↓
4. Redis에 새 메시지 추가 (빠른 쓰기)
   ↓
5. PostgreSQL에 동시 저장 (영구 저장)
   ↓
6. 응답 반환
```

### 세션 관리 코드 위치

**Redis 세션 관리**: `src/redis_session.py`
- `get_session()`: 세션 히스토리 조회
- `save_session()`: 세션 히스토리 저장
- `initialize_session()`: 새 세션 초기화
- `delete_session()`: 세션 삭제

**PostgreSQL 세션 관리**: `src/database.py`
- `save_conversation_to_db()`: 대화 히스토리 저장
- `load_conversation_from_db()`: 대화 히스토리 로드

**사용 위치**: `src/main.py`
- `/api/chat`: `save_conversation_to_db()` 호출
- `/api/chat/stream`: `save_conversation_to_db()` 호출
- `/api/voice/process`: `save_conversation_to_db()` 호출
- `/ws/voice`: `save_conversation_to_db()` 호출

---

## 📊 데이터 관리 전략

### 1. 세션 히스토리 관리

**Redis (캐시)**:
- 빠른 읽기/쓰기
- 30일 TTL로 자동 만료
- 분산 환경 지원

**PostgreSQL (영구 저장)**:
- 장기 보관
- 백업 및 복구
- 분석 쿼리 가능

### 2. API 요청 로깅

- 모든 API 요청을 `api_request_logs` 테이블에 기록
- 요청/응답 데이터, 처리 시간, 상태 코드 저장
- 분석 및 디버깅용

### 3. 비용 추적

- OpenAI API 호출마다 토큰 사용량과 비용 기록
- `cost_logs` 테이블에 저장
- 일별/월별 비용 집계 가능

### 4. Fallback 메커니즘

**우선순위**:
1. Redis (최우선)
2. PostgreSQL (Redis 장애 시)
3. 메모리 기반 fallback_store (모든 DB 장애 시)

---

## 🔍 데이터베이스 사용 현황 요약

### PostgreSQL 사용 현황

| 항목 | 내용 |
|------|------|
| **데이터베이스 타입** | PostgreSQL (RDBMS) |
| **용도** | 영구 저장, 백업, 분석 |
| **테이블 수** | 4개 |
| **주요 데이터** | 세션 메타데이터, 메시지 히스토리, API 로그, 비용 로그 |
| **인덱스 수** | 7개 |
| **연결 방식** | SQLAlchemy ORM |
| **위치** | 외부 DB (Docker 컨테이너 외부) |

### Redis 사용 현황

| 항목 | 내용 |
|------|------|
| **데이터베이스 타입** | Redis (인메모리) |
| **용도** | 캐시, 세션 관리 |
| **주요 데이터** | 세션 히스토리 (30일 TTL) |
| **연결 방식** | aioredis (비동기) |
| **위치** | Docker Compose 컨테이너 (`llm-gateway-redis`) |
| **메모리 제한** | 256MB |
| **정책** | LRU (Least Recently Used) |

---

## 📈 데이터베이스 통계 쿼리 예시

### 일별 비용 집계
```sql
SELECT 
    DATE(created_at) as date,
    SUM(cost_usd) as total_cost,
    COUNT(*) as request_count
FROM cost_logs
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### 세션별 비용 집계
```sql
SELECT 
    session_id,
    SUM(cost_usd) as total_cost,
    COUNT(*) as request_count
FROM cost_logs
GROUP BY session_id
ORDER BY total_cost DESC
LIMIT 10;
```

### API 엔드포인트별 요청 통계
```sql
SELECT 
    endpoint,
    COUNT(*) as request_count,
    AVG(processing_time_ms) as avg_processing_time,
    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
FROM api_request_logs
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY endpoint
ORDER BY request_count DESC;
```

### 활성 세션 수
```sql
SELECT COUNT(DISTINCT session_id) as active_sessions
FROM conversation_sessions
WHERE updated_at >= NOW() - INTERVAL '1 day';
```

---

## ✅ 확인 사항

### LLM Chat Session 관리

**질문**: LLM chat session 등 관련 정보를 DB에서 관리하고 있어?

**답변**: ✅ **네, 관리하고 있습니다!**

1. **Redis에서 관리**:
   - 세션 히스토리를 캐시로 저장
   - 빠른 읽기/쓰기 제공
   - 30일 TTL로 자동 만료

2. **PostgreSQL에서 관리**:
   - 세션 메타데이터 (`conversation_sessions`)
   - 모든 메시지 히스토리 (`conversation_messages`)
   - 영구 저장 및 백업

3. **이중 저장 전략**:
   - Redis: 빠른 접근 (캐시)
   - PostgreSQL: 영구 저장 (백업)

### 사용 중인 DB 목록

**답변**: **2개의 데이터베이스**를 사용 중입니다.

1. **PostgreSQL**
   - 타입: 관계형 데이터베이스 (RDBMS)
   - 용도: 영구 저장, 백업, 분석
   - 테이블: 4개 (conversation_sessions, conversation_messages, api_request_logs, cost_logs)

2. **Redis**
   - 타입: 인메모리 데이터 스토어
   - 용도: 캐시, 세션 관리
   - 데이터: 세션 히스토리 (30일 TTL)

---

## 📚 참고 문서

- `docs/database_schema.md`: 데이터베이스 스키마 상세 설명
- `src/database.py`: PostgreSQL 데이터베이스 관리 코드
- `src/redis_session.py`: Redis 세션 관리 코드
- `src/main.py`: API 엔드포인트에서 DB 사용 예시

---

## 📝 SQL 쿼리 모음

영구 DB에서 테이블을 직접 조회하기 위한 SQL 쿼리 모음이 `docs/database_queries.sql` 파일에 포함되어 있습니다.

### 주요 쿼리 카테고리

1. **대화 세션 관련 쿼리**
   - 모든 세션 조회
   - 최근 활성 세션
   - 사용자별 세션 통계

2. **대화 메시지 관련 쿼리**
   - 특정 세션의 메시지 조회
   - 세션별 메시지 수 집계
   - 최근 메시지 조회

3. **API 요청 로그 관련 쿼리**
   - 최근 요청 로그
   - 엔드포인트별 통계
   - 에러 로그 조회
   - 느린 요청 조회

4. **비용 로그 관련 쿼리**
   - 일별/월별 비용 집계
   - 서비스 타입별 통계
   - 모델별 비용 분석
   - 세션별 비용 집계

5. **통합 분석 쿼리**
   - 세션별 전체 통계
   - 일별 종합 통계
   - 활성 세션 조회

6. **데이터 정리 및 관리 쿼리**
   - 오래된 세션 조회
   - 테이블별 데이터 수 확인
   - 테이블 크기 확인

### 사용 방법

```bash
# PostgreSQL 클라이언트에 연결
psql -h your_host -U your_user -d your_database

# 쿼리 파일 실행
\i docs/database_queries.sql

# 또는 특정 쿼리만 복사하여 실행
```

자세한 내용은 `docs/database_queries.sql` 파일을 참고하세요.

---

**리포트 작성자**: AI Assistant  
**최종 업데이트**: 2025-11-05

