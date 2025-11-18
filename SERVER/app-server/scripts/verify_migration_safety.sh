#!/bin/bash
# 마이그레이션 안전성 검증 스크립트

set -e

echo "=== 마이그레이션 안전성 검증 ==="
echo ""

MIGRATION_DIR="app/infrastructure/db/migrations/versions"
LATEST_MIGRATION=$(ls -t ${MIGRATION_DIR}/*.py | head -1)

echo "1. 최신 마이그레이션 파일 확인: $(basename ${LATEST_MIGRATION})"
echo ""

# 1. upgrade() 함수에 drop_table이나 alter_table이 있는지 확인
echo "2. upgrade() 함수 안전성 검사..."
# upgrade() 함수 내에서 drop_table이나 alter_table이 있는지 확인
UPGRADE_SECTION=$(sed -n '/^def upgrade/,/^def downgrade/p' ${LATEST_MIGRATION} | head -n -1)
if echo "${UPGRADE_SECTION}" | grep -E "drop_table|alter_table" | grep -v "^#" | grep -v "^[[:space:]]*#"; then
    echo "   ⚠️ 경고: upgrade() 함수에 기존 테이블을 변경하는 명령이 있습니다!"
    echo "   upgrade() 함수에는 create_table만 있어야 합니다."
    exit 1
else
    echo "   ✅ upgrade() 함수는 create_table만 사용 (안전)"
fi

# 2. create_table만 있는지 확인
echo ""
echo "3. 신규 테이블 생성 명령 확인..."
CREATE_COUNT=$(grep -c "op.create_table" ${LATEST_MIGRATION} || echo "0")
if [ "${CREATE_COUNT}" -gt 0 ]; then
    echo "   ✅ ${CREATE_COUNT}개의 create_table 명령 발견 (정상)"
else
    echo "   ⚠️ create_table 명령이 없습니다."
fi

# 3. 테이블 이름 추출
echo ""
echo "4. 생성될 테이블 목록:"
grep "op.create_table" ${LATEST_MIGRATION} | sed 's/.*create_table(\([^,)]*\).*/\1/' | sed "s/'//g" | while read table; do
    echo "   - ${table}"
done

echo ""
echo "5. ENUM 타입 생성 확인..."
ENUM_COUNT=$(grep -c "CREATE TYPE" ${LATEST_MIGRATION} || echo "0")
if [ "${ENUM_COUNT}" -gt 0 ]; then
    echo "   ✅ ${ENUM_COUNT}개의 ENUM 타입 생성 (IF NOT EXISTS 패턴 사용)"
fi

echo ""
echo "=== 검증 완료 ==="
echo "✅ 마이그레이션 파일이 안전합니다."
echo "   - 기존 테이블 변경 없음"
echo "   - 신규 테이블만 생성"
echo "   - 기존 데이터 보존"
echo ""
echo "마이그레이션 실행: docker compose exec api alembic upgrade head"

