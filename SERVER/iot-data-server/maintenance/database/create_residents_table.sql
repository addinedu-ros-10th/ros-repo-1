-- ============================================================
-- 요양원 내부 사용자 정보 관리 테이블 생성
-- ============================================================
-- 
-- 이 테이블은 users 테이블과 1:1 관계로,
-- 입소자(resident) 역할을 가진 사용자의 요양원 내부 관리 정보를 저장합니다.
--
-- 요양원에서 일반적으로 관리하는 정보:
-- - 입소 관리: 입소일, 퇴소일, 생활실 정보
-- - 복약 관리: 복약 일정, 복약 특이사항
-- - 건강 관리: 건강 상태, 정서 상태, 심리 상태 (JSONB)
-- - 사건/사고: 사건/사고 기록 (JSONB)
-- - ADL 수준: 일상생활 활동 수준
-- - 식이 제한: 식이 제한 사항 (JSONB)
-- - 응급 연락처: 응급 연락처 정보 (JSONB)
-- - 보험 정보: 보험 정보 (JSONB)
-- - 의료 기관 연계: 의료 기관 정보 (JSONB)
-- ============================================================

CREATE TABLE IF NOT EXISTS residents (
    -- 기본 키: users 테이블의 user_id를 참조 (1:1 관계)
    user_id UUID NOT NULL PRIMARY KEY
        CONSTRAINT fk_resident_user
            REFERENCES users(user_id)
            ON DELETE CASCADE,
    
    -- 입소 관리 정보
    resident_number VARCHAR(20) UNIQUE,  -- 요양원 내부 관리 번호 (예: R-2024-001)
    nickname VARCHAR(50),                -- 애칭 (일본어 이름 등)
    admission_date DATE NOT NULL,        -- 입소일
    discharge_date DATE,                  -- 퇴소일 (NULL이면 현재 입소 중)
    
    -- 생활실 정보
    room_number VARCHAR(20),             -- 생활실 번호 (예: 302호, 205호)
    floor_number INTEGER,                 -- 층수
    bed_number VARCHAR(10),               -- 침대 번호 (같은 방에 여러 침대가 있는 경우)
    
    -- ADL (일상생활 활동) 수준
    adl_level VARCHAR(20) DEFAULT 'independent',  -- independent, partial_assistance, full_assistance
    mobility_level VARCHAR(20),                   -- independent, walker, wheelchair, bedridden
    cognitive_level VARCHAR(20),                 -- normal, mild_impairment, moderate_impairment, severe_impairment
    
    -- 복약 관리
    medication_schedule JSONB,           -- 복약 일정 (JSON 형식)
    -- 예시: [
    --   {"medication_name": "고혈압약", "time": "08:00", "dose": "1알", "route": "경구"},
    --   {"medication_name": "당뇨약", "time": "12:00", "dose": "1알", "route": "경구"}
    -- ]
    medication_notes TEXT,               -- 복약 특이사항 (예: 식후 30분, 알레르기 주의 등)
    
    -- 특이사항 (건강, 정서, 심리 등) - JSONB로 유연하게 관리
    special_notes JSONB,                 -- 특이사항 (JSON 형식)
    -- 예시: {
    --   "health": {"blood_pressure": "고혈압 주의", "diabetes": "혈당 모니터링 필요"},
    --   "emotional": {"anxiety": "야간 불안감", "depression": "경도 우울"},
    --   "psychological": {"dementia": "경도 치매", "memory": "단기 기억력 저하"},
    --   "behavioral": {"wandering": "야간 배회 경향", "agitation": "소음에 민감"}
    -- }
    
    -- 사건/사고 기록 - JSONB로 유연하게 관리
    incidents JSONB,                     -- 사건/사고 기록 (JSON 형식)
    -- 예시: [
    --   {
    --     "incident_date": "2024-01-15",
    --     "incident_type": "낙상",
    --     "location": "화장실",
    --     "severity": "경미",
    --     "description": "야간 화장실 이동 중 미끄러짐",
    --     "action_taken": "응급실 방문, X-ray 촬영, 골절 없음 확인",
    --     "preventive_measures": "화장실 바닥 미끄럼 방지 매트 설치"
    --   }
    -- ]
    
    -- 식이 제한 - JSONB로 유연하게 관리
    dietary_restrictions JSONB,         -- 식이 제한 (JSON 형식)
    -- 예시: {
    --   "allergies": ["견과류", "해산물"],
    --   "restrictions": ["저염식", "당뇨식"],
    --   "preferences": ["부드러운 음식", "따뜻한 음식"],
    --   "feeding_assistance": "부분 도움 필요"
    -- }
    
    -- 응급 연락처 - JSONB로 유연하게 관리
    emergency_contacts JSONB,            -- 응급 연락처 (JSON 형식)
    -- 예시: [
    --   {"name": "정기우", "relationship": "아들", "phone": "010-9911-2670", "priority": 1},
    --   {"name": "정기우 부인", "relationship": "며느리", "phone": "010-1234-5678", "priority": 2}
    -- ]
    
    -- 보험 정보 - JSONB로 유연하게 관리
    insurance_info JSONB,                 -- 보험 정보 (JSON 형식)
    -- 예시: {
    --   "health_insurance": {"number": "1234567890", "type": "건강보험"},
    --   "long_term_care_insurance": {"number": "0987654321", "grade": "등급 2"},
    --   "medical_aid": false
    -- }
    
    -- 의료 기관 연계 정보 - JSONB로 유연하게 관리
    medical_facility_info JSONB,         -- 의료 기관 정보 (JSON 형식)
    -- 예시: {
    --   "primary_hospital": {"name": "서울대학교병원", "department": "내과", "doctor": "홍길동"},
    --   "pharmacy": {"name": "○○약국", "phone": "02-1234-5678"},
    --   "emergency_hospital": {"name": "응급의료센터", "phone": "119"}
    -- }
    
    -- 기타 관리 정보
    care_level VARCHAR(20),              -- 요양 등급 (1등급, 2등급, 3등급 등)
    guardian_name VARCHAR(100),          -- 보호자 이름
    guardian_relationship VARCHAR(50),  -- 보호자 관계 (아들, 딸, 배우자 등)
    guardian_phone VARCHAR(20),         -- 보호자 전화번호
    
    -- 메타데이터
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- 제약조건
    CONSTRAINT check_adl_level CHECK (adl_level IN ('independent', 'partial_assistance', 'full_assistance')),
    CONSTRAINT check_mobility_level CHECK (mobility_level IN ('independent', 'walker', 'wheelchair', 'bedridden')),
    CONSTRAINT check_cognitive_level CHECK (cognitive_level IN ('normal', 'mild_impairment', 'moderate_impairment', 'severe_impairment')),
    CONSTRAINT check_discharge_date CHECK (discharge_date IS NULL OR discharge_date >= admission_date)
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_residents_resident_number ON residents(resident_number);
CREATE INDEX IF NOT EXISTS idx_residents_room_number ON residents(room_number);
CREATE INDEX IF NOT EXISTS idx_residents_admission_date ON residents(admission_date);
CREATE INDEX IF NOT EXISTS idx_residents_discharge_date ON residents(discharge_date);
CREATE INDEX IF NOT EXISTS idx_residents_user_id ON residents(user_id);

-- 코멘트 추가
COMMENT ON TABLE residents IS '요양원 내부 입소자 관리 정보 테이블';
COMMENT ON COLUMN residents.user_id IS 'users 테이블의 user_id (FK, 1:1 관계)';
COMMENT ON COLUMN residents.resident_number IS '요양원 내부 관리 번호 (예: R-2024-001)';
COMMENT ON COLUMN residents.nickname IS '애칭 (일본어 이름 등)';
COMMENT ON COLUMN residents.admission_date IS '입소일';
COMMENT ON COLUMN residents.discharge_date IS '퇴소일 (NULL이면 현재 입소 중)';
COMMENT ON COLUMN residents.room_number IS '생활실 번호 (예: 302호, 205호)';
COMMENT ON COLUMN residents.floor_number IS '층수';
COMMENT ON COLUMN residents.bed_number IS '침대 번호';
COMMENT ON COLUMN residents.adl_level IS '일상생활 활동 수준 (independent, partial_assistance, full_assistance)';
COMMENT ON COLUMN residents.mobility_level IS '이동 수준 (independent, walker, wheelchair, bedridden)';
COMMENT ON COLUMN residents.cognitive_level IS '인지 수준 (normal, mild_impairment, moderate_impairment, severe_impairment)';
COMMENT ON COLUMN residents.medication_schedule IS '복약 일정 (JSON 형식)';
COMMENT ON COLUMN residents.medication_notes IS '복약 특이사항';
COMMENT ON COLUMN residents.special_notes IS '특이사항 (건강, 정서, 심리 등, JSON 형식)';
COMMENT ON COLUMN residents.incidents IS '사건/사고 기록 (JSON 형식)';
COMMENT ON COLUMN residents.dietary_restrictions IS '식이 제한 (JSON 형식)';
COMMENT ON COLUMN residents.emergency_contacts IS '응급 연락처 (JSON 형식)';
COMMENT ON COLUMN residents.insurance_info IS '보험 정보 (JSON 형식)';
COMMENT ON COLUMN residents.medical_facility_info IS '의료 기관 정보 (JSON 형식)';
COMMENT ON COLUMN residents.care_level IS '요양 등급 (1등급, 2등급, 3등급 등)';
COMMENT ON COLUMN residents.guardian_name IS '보호자 이름';
COMMENT ON COLUMN residents.guardian_relationship IS '보호자 관계 (아들, 딸, 배우자 등)';
COMMENT ON COLUMN residents.guardian_phone IS '보호자 전화번호';

-- 테이블 소유권 설정
ALTER TABLE residents OWNER TO svc_dev;

