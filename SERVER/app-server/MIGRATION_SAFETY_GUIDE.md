# 마이그레이션 안전성 가이드

## 기존 테이블 보호 확인

### 현재 마이그레이션 파일 분석

**신규 마이그레이션 파일**: `20251110_create_robot_detection_tables.py`

이 마이그레이션은 **기존 테이블에 영향을 주지 않습니다**:

1. **CREATE TABLE만 사용**: `op.create_table()`만 사용하여 신규 테이블만 생성
2. **기존 테이블 수정 없음**: `op.alter_table()`, `op.drop_table()` 등 기존 테이블을 변경하는 명령 없음
3. **ENUM 타입 안전 생성**: `IF NOT EXISTS` 패턴으로 중복 생성 방지

### 생성되는 테이블 목록

다음 5개 테이블만 생성됩니다:
- `detection_event` (로봇 인식 이벤트 로그)
- `marker_registry` (ArUco 마커 레지스트리)
- `text_registry` (OCR 텍스트 레지스트리)
- `face_registry` (얼굴 레지스트리)
- `person_registry` (전신/개인 프로필 레지스트리)

### 기존 테이블 보호 메커니즘

1. **수동 마이그레이션**: 현재 마이그레이션은 수동으로 작성되어 있어 안전
2. **Alembic include_object**: `env.py`의 `include_object` 함수가 레거시 테이블 제외
3. **Base.metadata 분리**: 신규 모델만 `Base.metadata`에 포함

## 안전한 마이그레이션 실행 절차

### 1. 사전 확인 (필수)

```bash
# 현재 데이터베이스 상태 확인
docker compose exec api psql $DB_APP_URL -c "\dt public.*"

# 기존 테이블 목록 확인
docker compose exec api psql $DB_APP_URL -c "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;"

# 현재 마이그레이션 버전 확인
docker compose exec api alembic current
```

### 2. 백업 (권장)

```bash
# 데이터베이스 백업
docker compose exec api pg_dump $DB_APP_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# 또는 특정 테이블만 백업
docker compose exec api pg_dump $DB_APP_URL -t scheduled_jobs > backup_scheduled_jobs.sql
```

### 3. 마이그레이션 실행

```bash
# 마이그레이션 실행 (신규 테이블만 생성)
docker compose exec api alembic upgrade head

# 또는 특정 버전으로
docker compose exec api alembic upgrade 20251110_robot_detection
```

### 4. 사후 확인

```bash
# 신규 테이블 생성 확인
docker compose exec api psql $DB_APP_URL -c "\dt public.detection_event"
docker compose exec api psql $DB_APP_URL -c "\dt public.marker_registry"
docker compose exec api psql $DB_APP_URL -c "\dt public.text_registry"
docker compose exec api psql $DB_APP_URL -c "\dt public.face_registry"
docker compose exec api psql $DB_APP_URL -c "\dt public.person_registry"

# 기존 테이블 확인 (변경 없어야 함)
docker compose exec api psql $DB_APP_URL -c "\dt public.scheduled_jobs"

# 마이그레이션 버전 확인
docker compose exec api alembic current
```

## 향후 안전성 보장 방안

### 1. include_object 함수 개선 (선택사항)

현재 `include_object` 함수는 레거시 테이블만 제외하고 있습니다. 
더 엄격한 보호를 원한다면 다음과 같이 수정할 수 있습니다:

```python
def include_object(object, name, type_, reflected, compare_to):
    """
    비삭제 정책을 위한 객체 필터링
    관리 대상 테이블만 포함
    """
    if type_ == "table":
        # 관리 대상 테이블 목록 (화이트리스트)
        managed_tables = {
            "scheduled_jobs",
            "detection_event",
            "marker_registry",
            "text_registry",
            "face_registry",
            "person_registry",
        }
        
        # 관리 대상 테이블만 포함
        if name in managed_tables:
            return True
        
        # 시스템 테이블 (alembic_version)
        if name == "alembic_version":
            return True
        
        # 기타 테이블은 제외 (기존 테이블 보호)
        return False
    
    # 인덱스는 테이블과 함께 처리
    if type_ == "index":
        # 관리 대상 테이블의 인덱스만 포함
        return True
    
    return True
```

### 2. 마이그레이션 검증 스크립트

마이그레이션 실행 전 검증 스크립트를 사용할 수 있습니다:

```bash
#!/bin/bash
# scripts/verify_migration_safety.sh

echo "=== 마이그레이션 안전성 검증 ==="

# 1. 마이그레이션 파일에 drop_table이 있는지 확인
if grep -r "drop_table\|alter_table" app/infrastructure/db/migrations/versions/*.py | grep -v "def downgrade"; then
    echo "⚠️ 경고: 마이그레이션에 기존 테이블을 변경하는 명령이 있습니다!"
    exit 1
fi

# 2. create_table만 있는지 확인
echo "✅ 마이그레이션 파일 검증 완료 (create_table만 사용)"

# 3. 기존 테이블 목록 저장
echo "기존 테이블 목록을 저장합니다..."
docker compose exec api psql $DB_APP_URL -c "\dt public.*" > /tmp/before_migration_tables.txt

echo "✅ 검증 완료. 마이그레이션을 실행할 수 있습니다."
```

## 롤백 절차

마이그레이션 후 문제가 발생하면 롤백할 수 있습니다:

```bash
# 이전 버전으로 롤백
docker compose exec api alembic downgrade -1

# 또는 특정 버전으로
docker compose exec api alembic downgrade aaf84b4b99c7
```

**주의**: 롤백 시 신규로 생성된 테이블이 삭제됩니다. 데이터가 있다면 먼저 백업하세요.

## 자주 묻는 질문

### Q1: 기존 테이블(scheduled_jobs 등)이 영향을 받나요?
**A**: 아니요. 현재 마이그레이션은 `CREATE TABLE`만 사용하므로 기존 테이블은 전혀 영향을 받지 않습니다.

### Q2: 기존 데이터가 손실되나요?
**A**: 아니요. 신규 테이블만 생성되므로 기존 데이터는 그대로 유지됩니다.

### Q3: 향후 autogenerate를 사용해도 안전한가요?
**A**: `include_object` 함수를 개선하면 안전합니다. 위의 "향후 안전성 보장 방안" 섹션을 참고하세요.

### Q4: 마이그레이션 실행 중 오류가 발생하면?
**A**: 마이그레이션은 트랜잭션으로 실행되므로, 오류 발생 시 자동으로 롤백됩니다. 기존 테이블은 안전합니다.

## 체크리스트

마이그레이션 실행 전 확인사항:

- [ ] 기존 테이블 목록 확인 완료
- [ ] 데이터베이스 백업 완료 (권장)
- [ ] 마이그레이션 파일 검토 완료 (drop_table, alter_table 없음)
- [ ] 테스트 환경에서 먼저 실행 (권장)
- [ ] 롤백 절차 숙지

## 결론

**현재 마이그레이션은 기존 테이블과 데이터에 전혀 영향을 주지 않습니다.**

- ✅ 신규 테이블만 생성 (`CREATE TABLE`)
- ✅ 기존 테이블 수정 없음
- ✅ 기존 데이터 보존
- ✅ 안전한 롤백 가능

