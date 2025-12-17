# 마이그레이션 안전성 검증 리포트

**검증 일시**: 2025-11-10  
**검증자**: 시스템 자동 검증

## 검증 결과 요약

### ✅ 마이그레이션 안전성 확인

**기존 테이블에 영향을 주지 않습니다.**

1. **마이그레이션 파일 분석**
   - `upgrade()` 함수: `CREATE TABLE`만 사용 (5개 테이블)
   - 기존 테이블 수정/삭제 명령 없음
   - ENUM 타입 안전 생성 (`IF NOT EXISTS`)

2. **기존 테이블 상태**
   - 기존 테이블 개수: **35개**
   - 신규 테이블 존재 여부: **없음** (모두 생성 가능)
   - 현재 Alembic 버전: `20250912_create_scheduled_jobs`

3. **Alembic 설정 보호**
   - `include_object` 함수: 관리 대상 테이블만 포함 (화이트리스트)
   - 기존 테이블 자동 변경 방지

## 기존 테이블 목록 (35개)

다음 테이블들은 **영향을 받지 않습니다**:

- `scheduled_jobs` (기존 관리 테이블)
- `actuator_log_*` (4개)
- `sensor_*` (다수)
- `devices`, `users`, `user_profiles`, `user_relationships`
- `home_state_snapshots`
- `conversation_*`, `api_request_logs`, `cost_logs`
- 기타 레거시 테이블들

## 생성될 신규 테이블 (5개)

다음 테이블만 생성됩니다:

1. `detection_event` - 로봇 인식 이벤트 로그
2. `marker_registry` - ArUco 마커 레지스트리
3. `text_registry` - OCR 텍스트 레지스트리
4. `face_registry` - 얼굴 레지스트리 (PII 보호)
5. `person_registry` - 전신/개인 프로필 레지스트리

## 생성될 ENUM 타입 (2개)

1. `detection_category` - 인식 카테고리 (aruco, text, face, person)
2. `intent_type` - 처리 의도 (open_door, start_follow, stop_follow, announce, none)

## 안전성 보장 메커니즘

### 1. 마이그레이션 파일 수동 작성
- `CREATE TABLE`만 사용
- `DROP TABLE`, `ALTER TABLE` 없음 (upgrade 함수)
- 기존 테이블 참조 없음

### 2. Alembic include_object 함수
```python
managed_tables = {
    "scheduled_jobs",      # 기존 관리 테이블
    "detection_event",     # 신규
    "marker_registry",     # 신규
    "text_registry",       # 신규
    "face_registry",      # 신규
    "person_registry",     # 신규
}
```
- 관리 대상 테이블만 포함
- 기타 테이블은 자동 변경되지 않음

### 3. 트랜잭션 보호
- 마이그레이션은 트랜잭션으로 실행
- 오류 시 자동 롤백
- 기존 데이터 보존

## 마이그레이션 실행 절차

### 1. 사전 확인 (완료)
```bash
# 기존 테이블 확인
python3 scripts/check_existing_tables.py

# 마이그레이션 파일 검증
bash scripts/verify_migration_safety.sh
```

### 2. 마이그레이션 실행
```bash
# 방법 1: Docker 컨테이너 내에서
docker compose exec api alembic upgrade head

# 방법 2: 호스트에서 직접 (환경 변수 설정 필요)
cd SERVER/app-server
alembic upgrade head
```

### 3. 사후 확인
```bash
# 신규 테이블 생성 확인
python3 scripts/check_existing_tables.py

# 또는 직접 확인
psql $DB_APP_URL -c "\dt public.detection_event"
psql $DB_APP_URL -c "\dt public.marker_registry"
```

## 롤백 절차 (필요 시)

```bash
# 이전 버전으로 롤백
alembic downgrade -1

# 또는 특정 버전으로
alembic downgrade 20250912_create_scheduled_jobs
```

**주의**: 롤백 시 신규 테이블이 삭제됩니다. 데이터가 있다면 먼저 백업하세요.

## 결론

✅ **마이그레이션을 안전하게 실행할 수 있습니다.**

- 기존 테이블: 영향 없음
- 기존 데이터: 보존됨
- 신규 테이블: 5개만 생성
- 롤백: 가능

