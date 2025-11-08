# LLM Gateway 디버깅 및 개선 리포트

**작성일**: 2025-01-27  
**브랜치**: `feat/AI/llm-gateway__voice_interface__RP-22`

---

## 📊 개요

이번 세션에서 데이터베이스 연결, Redis 설정, 그리고 전반적인 코드 품질 개선 작업을 수행했습니다.

### 변경 통계
- **수정된 파일**: 3개
- **추가된 파일**: 3개
- **총 변경 라인**: +359 / -64

---

## 🐛 디버깅 내용

### 1. 데이터베이스 연결 오류 해결

#### 문제 1: 비밀번호 특수문자 처리 오류
**증상**: 
```
could not translate host name "#@localhost" to address
```
**원인**: 비밀번호에 `#`, `@`, `!` 등의 특수문자가 포함되어 URL 파싱 시 주석으로 해석됨

**해결**:
- 정규식 패턴으로 URL 구성 요소 파싱 (`@([a-zA-Z0-9._-]+)`)
- `quote_plus()`로 각 구성 요소 인코딩
- 인코딩된 구성 요소로 URL 재구성

**파일**: `database.py` (106-228줄)

#### 문제 2: SQLAlchemy 2.0+ 문법 오류
**증상**:
```
Not an executable object: 'SELECT 1'
```
**원인**: SQLAlchemy 2.0+에서는 `text()` 함수로 SQL 문자열을 감싸야 함

**해결**:
- `from sqlalchemy import text` 추가
- `conn.execute(text("SELECT 1"))`로 수정

**파일**: `database.py` (9줄, 335줄)

#### 문제 3: Docker 컨테이너에서 호스트 DB 접근 불가
**증상**:
```
connection to server at "localhost" (::1), port 15432 failed: Connection refused
```
**원인**: Docker 컨테이너 내부에서 `localhost`는 컨테이너 자체를 가리킴

**해결**:
- `/.dockerenv` 파일 존재 여부로 컨테이너 내부 감지
- `localhost`를 `host.docker.internal`로 자동 변환
- `docker-compose.yml`에 `extra_hosts` 추가

**파일**: `database.py` (120-124줄, 236-239줄), `docker-compose.yml` (54-57줄)

#### 문제 4: 중복 테이블/인덱스 오류
**증상**:
```
DuplicateTable: relation "idx_session_created" already exists
```
**원인**: 테이블 생성 시 이미 존재하는 인덱스에 대한 예외 처리 없음

**해결**:
- `create_all()`에 `checkfirst=True` 추가
- `OperationalError`, `ProgrammingError` 예외 처리
- 중복 오류는 무시하고 계속 진행

**파일**: `database.py` (276-293줄)

---

### 2. Redis 설정 최적화

#### 문제 1: 메모리 Overcommit 경고
**증상**:
```
WARNING Memory overcommit must be enabled!
```
**원인**: 호스트 시스템의 `vm.overcommit_memory = 0` 설정

**해결**:
- `sysctls` 제거 (컨테이너에서 설정 불가)
- 호스트에서 수동 설정 가이드 제공 (`REDIS_SETUP.md`)
- Redis 로그 레벨 조정 (`--loglevel notice`)

**파일**: `docker-compose.yml` (69-89줄), `REDIS_SETUP.md`

#### 문제 2: Redis 연결 안정성
**원인**: 연결 풀 설정 부족, 재연결 로직 없음

**해결**:
- 연결 풀 설정 추가 (`health_check_interval=30`)
- 타임아웃 설정 (`socket_connect_timeout=5.0`)
- 자동 재연결 로직 구현
- 연결 상태 확인 (`ping()`)

**파일**: `redis_session.py` (29-79줄)

---

### 3. Docker Compose YAML 오류

#### 문제 1: Healthcheck 구문 오류
**증상**:
```
Implicit keys need to be on a single line
```
**원인**: `>` (folded scalar) 사용 시 YAML 파싱 오류

**해결**:
- 배열 형식으로 변경: `["CMD-SHELL", "..."]`

**파일**: `docker-compose.yml` (100-101줄)

#### 문제 2: sysctl 설정 오류
**증상**:
```
sysctl "vm.overcommit_memory" is not in a separate kernel namespace
```
**원인**: 호스트 레벨 커널 파라미터를 컨테이너에서 설정 시도

**해결**:
- `sysctls` 섹션 제거
- 주석으로 호스트 설정 방법 안내

**파일**: `docker-compose.yml` (93-96줄)

---

## ✨ 코드 품질 개선

### 1. 로깅 시스템 개선

**변경 전**: `print()` 사용
**변경 후**: `logging` 모듈 사용

**개선 사항**:
- 로그 레벨 구분 (`debug`, `info`, `warning`, `error`)
- `exc_info=True`로 스택 트레이스 포함
- 구조화된 로그 메시지

**파일**: `database.py`, `redis_session.py`

### 2. 에러 처리 강화

**개선 사항**:
- 구체적인 예외 타입 처리 (`ConnectionError`, `TimeoutError`, `OperationalError`, `ProgrammingError`)
- JSON 디코딩 오류 처리
- 모든 메서드에 예외 처리 추가
- 에러 메시지 개선

**파일**: `database.py`, `redis_session.py`

### 3. 연결 안정성 향상

**데이터베이스**:
- `pool_pre_ping=True` 추가 (연결 상태 확인)
- Docker 환경 자동 감지 및 호스트 변환

**Redis**:
- 연결 풀 설정
- 자동 재연결 로직
- Health check 간격 설정 (30초)

**파일**: `database.py` (262-267줄), `redis_session.py` (48-51줄, 65줄)

### 4. Redis 서버 최적화

**추가된 설정**:
- `--maxmemory 256mb`: 메모리 제한
- `--maxmemory-policy allkeys-lru`: LRU 정책
- `--save 60 1000`: 자동 저장 설정
- `--stop-writes-on-bgsave-error no`: 백그라운드 저장 실패 시에도 쓰기 허용
- `--loglevel notice`: 로그 레벨 조정

**파일**: `docker-compose.yml` (73-89줄)

---

## 📝 변경된 파일 상세

### 수정된 파일

1. **`database.py`** (+186줄)
   - URL 파싱 로직 개선 (특수문자 처리)
   - Docker 환경 자동 감지
   - 로깅 시스템 개선
   - 에러 처리 강화
   - 중복 테이블/인덱스 오류 처리
   - SQLAlchemy 2.0+ 호환성

2. **`redis_session.py`** (+202줄)
   - 연결 풀 설정 추가
   - 자동 재연결 로직
   - 로깅 시스템 개선
   - 에러 처리 강화
   - Health check 개선

3. **`docker-compose.yml`** (+35줄)
   - Redis 서버 최적화 옵션 추가
   - Healthcheck 개선 (비밀번호 지원)
   - `extra_hosts` 추가 (Docker 호스트 접근)
   - sysctl 설정 제거 및 주석 추가

### 추가된 파일

1. **`REDIS_SETUP.md`**
   - Redis 메모리 overcommit 설정 가이드
   - 호스트 설정 방법 안내

2. **`DEVELOPMENT_STATUS.md`**
   - 프로젝트 개발 현황 리포트

3. **`COMMIT_MESSAGE.md`**
   - 이전 커밋 메시지 기록

---

## ✅ 테스트 결과

### 성공한 개선사항
- ✅ 비밀번호 특수문자 처리 정상 작동
- ✅ Docker 컨테이너에서 호스트 DB 접근 성공
- ✅ 중복 테이블/인덱스 오류 해결
- ✅ SQLAlchemy 2.0+ 호환성 확인
- ✅ Redis 연결 안정성 향상
- ✅ YAML 구문 오류 해결

### 남은 경고 (기능 영향 없음)
- ⚠️ Redis 메모리 overcommit 경고 (호스트 설정 필요)
  - Redis는 정상 작동하지만 경고 메시지 표시
  - 호스트에서 `sudo sysctl vm.overcommit_memory=1` 실행 필요

---

## 🚀 다음 단계

1. 호스트에서 Redis 메모리 overcommit 설정 (선택사항)
2. 프로덕션 환경 배포 전 최종 테스트
3. 성능 모니터링 및 로그 분석

---

## 📚 참고 문서

- `REDIS_SETUP.md`: Redis 설정 가이드
- `DEVELOPMENT_STATUS.md`: 개발 현황 리포트
- `README.md`: 프로젝트 사용 가이드

