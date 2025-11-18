"""create_robot_detection_tables

Revision ID: create_robot_detection_001
Revises: aaf84b4b99c7
Create Date: 2025-11-10 12:00:00.000000+09:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20251110_robot_detection'
down_revision: Union[str, Sequence[str], None] = 'aaf84b4b99c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ENUM 타입 생성 (이미 존재하면 무시)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE detection_category AS ENUM ('aruco', 'text', 'face', 'person');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE intent_type AS ENUM ('open_door', 'start_follow', 'stop_follow', 'announce', 'none');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # detection_event 테이블 생성
    op.create_table('detection_event',
        sa.Column('detection_event_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()'), nullable=False, comment='이벤트 고유 ID'),
        sa.Column('robot_id', sa.Text(), nullable=False, comment='로봇 ID'),
        sa.Column('category', postgresql.ENUM('aruco', 'text', 'face', 'person', name='detection_category', create_type=False), nullable=False, comment='인식 카테고리'),
        sa.Column('unique_key', sa.Text(), nullable=False, comment='고유 키 (마커/텍스트/얼굴해시/추적ID 등)'),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='카테고리별 부가정보'),
        sa.Column('detected_at', sa.TIMESTAMP(timezone=True), nullable=False, comment='인식 시간(로봇 기준 UTC 권장)'),
        sa.Column('processing_info', postgresql.JSONB(astext_type=sa.Text()), nullable=False, comment='처리 정보 (intent/api_calls/cmds/scenario_state)'),
        sa.Column('processed_status', sa.Text(), nullable=False, server_default=sa.text("'accepted'"), comment='처리 상태 (accepted|done|failed)'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='생성 시간'),
        comment='로봇 인식 이벤트 로그 (공통)'
    )
    
    # detection_event 인덱스 생성
    op.create_index('idx_detection_event_time', 'detection_event', ['detected_at'], postgresql_ops={'detected_at': 'DESC'}, unique=False)
    op.create_index('idx_detection_event_cat_key', 'detection_event', ['category', 'unique_key'], unique=False)
    op.create_index('idx_detection_event_robot', 'detection_event', ['robot_id'], unique=False)
    op.create_index('idx_detection_event_status', 'detection_event', ['processed_status'], unique=False)
    
    # TimescaleDB 하이퍼테이블 변환 (조건부)
    op.execute("""
        DO $$ 
        BEGIN
            -- TimescaleDB 확장이 있는지 확인
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                -- 하이퍼테이블로 변환 (이미 존재하면 무시)
                PERFORM create_hypertable('detection_event', 'detected_at', if_not_exists => TRUE);
                RAISE NOTICE 'TimescaleDB hypertable created for detection_event';
            ELSE
                RAISE NOTICE 'TimescaleDB extension not found, using regular table';
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                RAISE NOTICE 'Could not create hypertable: %', SQLERRM;
        END $$;
    """)
    
    # marker_registry 테이블 생성 (ArUco)
    op.create_table('marker_registry',
        sa.Column('marker_key', sa.Text(), primary_key=True, nullable=False, comment='마커 키 (예: ARUCO_23)'),
        sa.Column('entrance_id', sa.Text(), nullable=True, comment='출입구/구역 식별'),
        sa.Column('zone', sa.Text(), nullable=True, comment='구역'),
        sa.Column('pose', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='고정 좌표/자세'),
        sa.Column('description', sa.Text(), nullable=True, comment='설명'),
        sa.Column('action_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='기본 처리 계획'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='수정 시간'),
        comment='ArUco 마커 레지스트리'
    )
    
    # text_registry 테이블 생성 (OCR)
    op.create_table('text_registry',
        sa.Column('text_key', sa.Text(), primary_key=True, nullable=False, comment='텍스트 키 (예: 식당, 응접실)'),
        sa.Column('room_code', sa.Text(), nullable=True, comment='방 코드'),
        sa.Column('lang', sa.Text(), nullable=True, comment='언어'),
        sa.Column('synonyms', postgresql.ARRAY(sa.Text()), nullable=True, comment='유사 표현'),
        sa.Column('action_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='기본 처리 계획'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='수정 시간'),
        comment='OCR 텍스트 레지스트리'
    )
    
    # face_registry 테이블 생성 (얼굴, PII 보호)
    op.create_table('face_registry',
        sa.Column('face_key', sa.Text(), primary_key=True, nullable=False, comment='얼굴 식별키 해시'),
        sa.Column('role', sa.Text(), nullable=True, comment='역할 (elder|caregiver|visitor)'),
        sa.Column('consent', sa.Boolean(), nullable=False, server_default=sa.text('false'), comment='동의 여부'),
        sa.Column('pii_ref', sa.Text(), nullable=True, comment='외부 금고/암호화 저장소 key(선택)'),
        sa.Column('policy', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='보관기간/마스킹 등'),
        sa.Column('action_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='기본 처리 계획'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='수정 시간'),
        sa.CheckConstraint("role IN ('elder', 'caregiver', 'visitor')", name='ck_face_registry_role'),
        comment='얼굴 레지스트리 (PII 보호)'
    )
    
    # person_registry 테이블 생성 (전신/개인 프로필)
    op.create_table('person_registry',
        sa.Column('person_key', sa.Text(), primary_key=True, nullable=False, comment='개인 논리 키'),
        sa.Column('preferred_follow_distance_m', sa.Numeric(4, 2), nullable=True, server_default=sa.text('1.5'), comment='선호 추종 거리(m)'),
        sa.Column('mobility_level', sa.Text(), nullable=True, comment='보행속도/주의필요 등'),
        sa.Column('action_plan', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment='기본 처리 계획'),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False, comment='수정 시간'),
        comment='전신/개인 프로필 레지스트리'
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 테이블 삭제 (역순)
    op.drop_table('person_registry')
    op.drop_table('face_registry')
    op.drop_table('text_registry')
    op.drop_table('marker_registry')
    
    # TimescaleDB 하이퍼테이블 해제 (조건부)
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
                -- 하이퍼테이블이면 일반 테이블로 변환 후 삭제
                PERFORM * FROM timescaledb_information.hypertables WHERE hypertable_name = 'detection_event';
                IF FOUND THEN
                    PERFORM * FROM _timescaledb_internal.drop_chunk(chunk_id) 
                    FROM timescaledb_information.chunks 
                    WHERE hypertable_name = 'detection_event';
                END IF;
            END IF;
        EXCEPTION
            WHEN OTHERS THEN
                NULL;
        END $$;
    """)
    
    op.drop_table('detection_event')
    
    # 인덱스 삭제는 테이블 삭제 시 자동 삭제됨
    
    # ENUM 타입 삭제
    op.execute("DROP TYPE IF EXISTS intent_type")
    op.execute("DROP TYPE IF EXISTS detection_category")

