-- ============================================================
-- 요양원 사용자 전체 목업 데이터 삽입
-- ============================================================
-- 
-- 이 스크립트는 users, user_profiles, user_relationships, residents 테이블에
-- 모든 사용자 데이터를 삽입합니다.
--
-- user_role 매핑:
-- - 입소자: 'care_target'
-- - 직원: 'caregiver'
-- - 면회객: 'family'
-- - 관리자: 'admin'
--
-- 캐릭터 매핑:
-- - 입소자 (care_target):
--   * Akaza (ID: 0) → 정도현 (user_id: 00000000-0000-0000-0000-000000000001)
--   * Gyomei Himejima (ID: 3) → 한기문 (user_id: 00000000-0000-0000-0000-000000000002)
--   * Kyojuro Rengoku (ID: 7) → 이강열 (user_id: 00000000-0000-0000-0000-000000000003)
--   * Zenitsu Agatsuma (ID: 17) → 김선우 (user_id: 00000000-0000-0000-0000-000000000004)
-- - 직원 (caregiver):
--   * Mitsuri Kanroji (ID: 8) → 박미소 (user_id: 00000000-0000-0000-0000-000000000005)
--   * Nezuko Kamado (ID: 11) → 최나래 (user_id: 00000000-0000-0000-0000-000000000006)
--   * Shinobu Kocho (ID: 14) → 유시은 (user_id: 00000000-0000-0000-0000-000000000007)
--   * Tanjiro Kamado (ID: 15) → 강탄호 (user_id: 00000000-0000-0000-0000-000000000008)
-- - 면회객 (family):
--   * Giyu Tomioka (ID: 2) → 정기우 (user_id: 00000000-0000-0000-0000-000000000009)
--   * Inosuke Hashibira (ID: 5) → 조인우 (user_id: 00000000-0000-0000-0000-000000000010)
--   * Obanai Iguro (ID: 12) → 오범준 (user_id: 00000000-0000-0000-0000-000000000011)
--   * Tengen Uzui (ID: 16) → 우태건 (user_id: 00000000-0000-0000-0000-000000000012)
-- ============================================================

-- ============================================================
-- 1. users 테이블 INSERT
-- ============================================================

INSERT INTO users (user_id, user_role, user_name, email, phone_number)
VALUES
-- 입소자 (care_target)
('00000000-0000-0000-0000-000000000001', 'care_target', '정도현', 'jdohyun@example.com', '010-3210-4801'),
('00000000-0000-0000-0000-000000000002', 'care_target', '한기문', 'hangimun@example.com', '010-5522-1934'),
('00000000-0000-0000-0000-000000000003', 'care_target', '이강열', 'leekangyeol@example.com', '010-8843-7721'),
('00000000-0000-0000-0000-000000000004', 'care_target', '김선우', 'kimsunwoo@example.com', '010-9972-3605'),

-- 직원 (caregiver)
('00000000-0000-0000-0000-000000000005', 'caregiver', '박미소', 'parkmiso@carehome.or.kr', '010-2311-8890'),
('00000000-0000-0000-0000-000000000006', 'caregiver', '최나래', 'choinare@carehome.or.kr', '010-4402-1138'),
('00000000-0000-0000-0000-000000000007', 'caregiver', '유시은', 'yusieun@carehome.or.kr', '010-7355-9042'),
('00000000-0000-0000-0000-000000000008', 'caregiver', '강탄호', 'kangtanho@carehome.or.kr', '010-5559-7150'),

-- 면회객 (family)
('00000000-0000-0000-0000-000000000009', 'family', '정기우', 'junggyiu@example.com', '010-9911-2670'),
('00000000-0000-0000-0000-000000000010', 'family', '조인우', 'choinwoo@example.com', '010-3874-9921'),
('00000000-0000-0000-0000-000000000011', 'family', '오범준', 'ohbeomjun@example.com', '010-6420-5531'),
('00000000-0000-0000-0000-000000000012', 'family', '우태건', 'wootaegun@example.com', '010-2841-7703')
ON CONFLICT (user_id) DO NOTHING;

-- ============================================================
-- 2. user_profiles 테이블 INSERT
-- ============================================================

INSERT INTO user_profiles
(user_id, date_of_birth, gender, address, address_detail,
medical_history, significant_notes, current_status)
VALUES
-- ===== 입소자 4명 =====

-- Akaza (입소자) → 정도현
('00000000-0000-0000-0000-000000000001',
'1943-02-11', 'male',
'서울특별시 성북구 정릉로 102',
'○○요양원 302호',
'고혈압, 제2형 당뇨병, 2년 전 낙상 후 대퇴골 수술 이력. 가벼운 보행 보조 필요.',
'애칭: Akaza (캐릭터 ID: 0). 평소 농담을 좋아하지만, 낙상 이후 야간 보행에 대한 불안감이 큼.',
'보행기 사용, 혼자서는 장거리 이동 어려움. 기본 일상생활 동작은 부분 도움 필요. 최근 야간 화장실 이동 시 두 차례 거의 넘어질 뻔한 이력 있음.'),

-- Gyomei Himejima (입소자) → 한기문
('00000000-0000-0000-0000-000000000002',
'1946-07-03', 'male',
'서울특별시 동대문구 이문로 45',
'○○요양원 205호',
'당뇨병, 고지혈증, 중증 시각 장애(시야 대부분 소실), 심부전 초기 진단.',
'애칭: Gyomei Himejima (캐릭터 ID: 3). 촉감과 소리에 민감하며, 익숙한 목소리와 발걸음 소리를 잘 구분함.',
'휠체어 병행 사용. 시각장애로 인해 실내 이동 시 동행이 필수적이며, 복도 구간에 대한 음성 안내 및 촉각 피드백 필요.'),

-- Kyojuro Rengoku (입소자) → 이강열
('00000000-0000-0000-0000-000000000003',
'1949-11-19', 'male',
'서울특별시 강서구 마곡중앙로 22',
'○○요양원 108호',
'고혈압, 협심증, 무릎 관절염. 과거 교사 경력으로 말수가 많고 리더십 있음.',
'애칭: Kyojuro Rengoku (캐릭터 ID: 7). 큰 목소리와 긍정적인 태도로 주변 어르신들을 자주 격려함.',
'대체로 활달하며 프로그램 참여율 높음. 갑작스러운 가슴 통증 호소 이력 있어, 계단·경사로 이용 시 관찰 필요.'),

-- Zenitsu Agatsuma (입소자) → 김선우
('00000000-0000-0000-0000-000000000004',
'1951-04-26', 'male',
'서울특별시 은평구 응암로 7',
'○○요양원 407호',
'불안장애, 불면증, 경도 치매(초기 단기 기억력 저하). 소음에 민감.',
'애칭: Zenitsu Agatsuma (캐릭터 ID: 17). 큰 소리와 갑작스러운 접촉을 매우 두려워하며, 친숙한 사람에게만 마음을 여는 경향.',
'낮 동안 졸림 호소 잦고, 밤에는 잠들기까지 시간이 오래 걸림. 새로운 환경에 대한 적응이 느려서, 변경 사항 안내 시 반복 설명 필요.'),

-- ===== 직원 4명 =====

-- Mitsuri Kanroji (직원) → 박미소 (주간 간호사)
('00000000-0000-0000-0000-000000000005',
'1991-03-15', 'female',
'서울특별시 중랑구 망우로 210',
'○○요양원 간호사실',
'알레르기 없음. 간호학 전공, 노인요양전문병원 5년 근무 경력.',
'애칭: Mitsuri Kanroji (캐릭터 ID: 8). 밝은 표정과 과한 리액션으로 어르신들에게 인기 많음.',
'주간 근무 담당. 입소자와 라포 형성이 잘 되어, 낙상 두려움이 큰 어르신 상담 시 우선 배치되는 편.'),

-- Nezuko Kamado (직원) → 최나래 (사회복지사)
('00000000-0000-0000-0000-000000000006',
'1993-09-02', 'female',
'서울특별시 마포구 월드컵북로 88',
'○○요양원 프로그램실',
'특이 병력 없음. 사회복지학 전공, 미술치료 자격증 보유.',
'애칭: Nezuko Kamado (캐릭터 ID: 11). 말수는 적지만 그림과 음악 프로그램에서 어르신 반응이 좋음.',
'사회성 증진·우울감 완화를 위한 소규모 그룹 프로그램 담당. 인지 자극 활동 및 생신 행사 진행에 강점이 있음.'),

-- Shinobu Kocho (직원) → 유시은 (야간 간호사)
('00000000-0000-0000-0000-000000000007',
'1988-12-28', 'female',
'서울특별시 용산구 한강대로 120',
'○○요양원 야간 당직실',
'천식 경미, 야간 근무 중심으로 생활 패턴이 맞춰져 있음.',
'애칭: Shinobu Kocho (캐릭터 ID: 14). 차분한 말투지만 위기 상황에서 빠르게 판단하는 편.',
'야간 투약 및 응급 대응 담당. 낙상·호흡곤란 등 센서 알림 발생 시 1차 대응자로 출동.'),

-- Tanjiro Kamado (직원) → 강탄호 (시설장)
('00000000-0000-0000-0000-000000000008',
'1985-05-09', 'male',
'서울특별시 광진구 능동로 55',
'○○요양원 원장실',
'허리디스크 초기 진단, 오래 서 있는 자세에 주의 필요.',
'애칭: Tanjiro Kamado (캐릭터 ID: 15). 직원·입소자·가족 사이의 갈등을 조율하는 역할을 잘 수행.',
'시설 운영 총괄. 보호자 상담 및 신규 입소 상담, 외부 기관 연계를 담당하며, 위기 상황 시 최종 책임자.'),

-- ===== 면회객 4명 =====

-- Giyu Tomioka (면회객) → 정기우 (정도현의 아들)
('00000000-0000-0000-0000-000000000009',
'1974-08-20', 'male',
'경기도 고양시 일산동구 중앙로 777',
'○○아파트 1203동 804호',
'고혈압 경계선. IT 회사 팀장으로 장시간 앉아서 근무.',
'애칭: Giyu Tomioka (캐릭터 ID: 2). 표현은 적지만 아버지의 안전에 대한 걱정이 큼.',
'월 1~2회 방문. 바쁜 일정으로 자주 오지 못하지만, 영상통화로 상태를 확인하려는 의지가 있음.'),

-- Inosuke Hashibira (면회객) → 조인우 (한기문의 손자)
('00000000-0000-0000-0000-000000000010',
'2001-01-13', 'male',
'서울특별시 관악구 관악로 99',
'○○대학교 기숙사 3동 215호',
'특이 병력 없음. 대학생, 운동을 좋아하며 활동적.',
'애칭: Inosuke Hashibira (캐릭터 ID: 5). 할아버지에게 크게 인사하며 주변 분위기를 띄우는 편.',
'방학·시험 종료 기간에 집중 방문. 로봇·스마트폰 사용에 능숙해, 디지털 기기를 활용한 소통을 선호.'),

-- Obanai Iguro (면회객) → 오범준 (이강열의 사위)
('00000000-0000-0000-0000-000000000011',
'1979-06-01', 'male',
'경기도 성남시 분당구 수내로 14',
'○○빌라 B동 301호',
'위염, 과거 스트레스성 공황발작 이력.',
'애칭: Obanai Iguro (캐릭터 ID: 12). 말투는 직설적이지만 책임감이 강함.',
'주로 배우자(이강열의 딸)와 함께 방문. 의료 정보 설명을 이해·정리하여 가족에게 공유하는 역할.'),

-- Tengen Uzui (면회객) → 우태건 (김선우의 아들)
('00000000-0000-0000-0000-000000000012',
'1969-10-30', 'male',
'해외(일본, 도쿄 시나가와구)',
'출장·파견 근무 잦음',
'과거 허리 부상 외 특이 병력 없음. 해외 근무로 인한 장거리 이동 피로 있음.',
'애칭: Tengen Uzui (캐릭터 ID: 16). 화려한 말투와 유머 감각이 있으나, 실제로는 가족에게 미안함을 많이 느낌.',
'연 1~2회 장기 면회. 평소에는 영상통화 및 간헐적 전화로 안부 확인. 방문 시 주변 어르신들에게 간식을 나누며 인상 좋음.')
ON CONFLICT (user_id) DO UPDATE SET
    date_of_birth = EXCLUDED.date_of_birth,
    gender = EXCLUDED.gender,
    address = EXCLUDED.address,
    address_detail = EXCLUDED.address_detail,
    medical_history = EXCLUDED.medical_history,
    significant_notes = EXCLUDED.significant_notes,
    current_status = EXCLUDED.current_status,
    updated_at = NOW();

-- ============================================================
-- 3. user_relationships 테이블 INSERT
-- ============================================================

-- caregiver 관계: 직원 → 입소자
INSERT INTO user_relationships
(subject_user_id, target_user_id, relationship_type, status)
VALUES
-- 박미소(간호사) → 정도현
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000001', 'caregiver', 'active'),
-- 유시은(야간 간호사) → 한기문
('00000000-0000-0000-0000-000000000007', '00000000-0000-0000-0000-000000000002', 'caregiver', 'active'),
-- 최나래(사회복지사) → 이강열
('00000000-0000-0000-0000-000000000006', '00000000-0000-0000-0000-000000000003', 'caregiver', 'active'),
-- 박미소(간호사) → 김선우
('00000000-0000-0000-0000-000000000005', '00000000-0000-0000-0000-000000000004', 'caregiver', 'active')
ON CONFLICT (subject_user_id, target_user_id, relationship_type) DO NOTHING;

-- family 관계: 면회객 → 입소자
INSERT INTO user_relationships
(subject_user_id, target_user_id, relationship_type, status)
VALUES
-- 정기우(아들) → 정도현
('00000000-0000-0000-0000-000000000009', '00000000-0000-0000-0000-000000000001', 'family', 'active'),
-- 조인우(손자) → 한기문
('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000002', 'family', 'active'),
-- 오범준(사위) → 이강열
('00000000-0000-0000-0000-000000000011', '00000000-0000-0000-0000-000000000003', 'family', 'active'),
-- 우태건(아들) → 김선우
('00000000-0000-0000-0000-000000000012', '00000000-0000-0000-0000-000000000004', 'family', 'active')
ON CONFLICT (subject_user_id, target_user_id, relationship_type) DO NOTHING;

-- admin 관계: 시설장(강탄호) → 모든 입소자
INSERT INTO user_relationships
(subject_user_id, target_user_id, relationship_type, status)
VALUES
('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000001', 'admin', 'active'),
('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000002', 'admin', 'active'),
('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000003', 'admin', 'active'),
('00000000-0000-0000-0000-000000000008', '00000000-0000-0000-0000-000000000004', 'admin', 'active')
ON CONFLICT (subject_user_id, target_user_id, relationship_type) DO NOTHING;

-- ============================================================
-- 4. residents 테이블 INSERT (입소자 정보)
-- ============================================================

-- 정도현 (Akaza) - 입소자 정보
INSERT INTO residents (
    user_id,
    resident_number,
    nickname,
    admission_date,
    discharge_date,
    room_number,
    floor_number,
    bed_number,
    adl_level,
    mobility_level,
    cognitive_level,
    medication_schedule,
    medication_notes,
    special_notes,
    incidents,
    dietary_restrictions,
    emergency_contacts,
    insurance_info,
    medical_facility_info,
    care_level,
    guardian_name,
    guardian_relationship,
    guardian_phone
) VALUES (
    '00000000-0000-0000-0000-000000000001',
    'R-2024-001',
    'Akaza',
    '2022-03-15',
    NULL,
    '302',
    3,
    'A',
    'partial_assistance',
    'walker',
    'mild_impairment',
    '[
        {
            "medication_name": "고혈압약",
            "time": "08:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        },
        {
            "medication_name": "당뇨약",
            "time": "12:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        },
        {
            "medication_name": "고혈압약",
            "time": "20:00",
            "dose": "1알",
            "route": "경구",
            "with_food": false
        }
    ]'::jsonb,
    '식후 30분 복용. 혈압 모니터링 필요. 야간 복용 시 졸음 주의.',
    '{
        "health": {
            "blood_pressure": "고혈압 주의 (140/90 이상 시 알림)",
            "diabetes": "혈당 모니터링 필요 (공복 100-120 유지 목표)",
            "fall_risk": "높음 (낙상 이력 있음)"
        },
        "emotional": {
            "anxiety": "야간 보행에 대한 불안감",
            "mood": "평소 밝지만, 낙상 후 우울감 증가"
        },
        "psychological": {
            "memory": "단기 기억력 저하 (약물 복용 시간 확인 필요)",
            "orientation": "정상"
        },
        "behavioral": {
            "wandering": "야간 화장실 이동 시 주의 필요",
            "agitation": "큰 소리에 민감하지 않음"
        }
    }'::jsonb,
    '[
        {
            "incident_date": "2024-01-15",
            "incident_type": "낙상",
            "location": "화장실",
            "severity": "경미",
            "description": "야간 화장실 이동 중 미끄러짐. 넘어지지는 않았으나 거의 넘어질 뻔함.",
            "action_taken": "응급실 방문, X-ray 촬영, 골절 없음 확인. 보행기 사용 강화.",
            "preventive_measures": "화장실 바닥 미끄럼 방지 매트 설치, 야간 이동 시 동행 권장"
        },
        {
            "incident_date": "2023-11-20",
            "incident_type": "낙상",
            "location": "복도",
            "severity": "중등도",
            "description": "보행기 없이 이동 중 넘어짐. 대퇴골 골절 의심으로 병원 이송.",
            "action_taken": "응급실 방문, 대퇴골 골절 확인, 수술 및 재활 치료",
            "preventive_measures": "보행기 사용 의무화, 장거리 이동 시 동행 필수"
        }
    ]'::jsonb,
    '{
        "allergies": [],
        "restrictions": ["저염식", "당뇨식"],
        "preferences": ["부드러운 음식", "따뜻한 음식"],
        "feeding_assistance": "부분 도움 필요",
        "swallowing": "정상"
    }'::jsonb,
    '[
        {
            "name": "정기우",
            "relationship": "아들",
            "phone": "010-9911-2670",
            "priority": 1,
            "available_hours": "평일 18:00 이후, 주말 가능"
        },
        {
            "name": "정기우 부인",
            "relationship": "며느리",
            "phone": "010-1234-5678",
            "priority": 2,
            "available_hours": "평일 19:00 이후"
        }
    ]'::jsonb,
    '{
        "health_insurance": {
            "number": "1234567890",
            "type": "건강보험"
        },
        "long_term_care_insurance": {
            "number": "0987654321",
            "grade": "등급 2",
            "start_date": "2022-03-15"
        },
        "medical_aid": false
    }'::jsonb,
    '{
        "primary_hospital": {
            "name": "서울대학교병원",
            "department": "내과",
            "doctor": "홍길동",
            "phone": "02-2072-2114"
        },
        "pharmacy": {
            "name": "○○약국",
            "phone": "02-1234-5678",
            "address": "서울특별시 성북구 정릉로 102"
        },
        "emergency_hospital": {
            "name": "응급의료센터",
            "phone": "119"
        }
    }'::jsonb,
    '2등급',
    '정기우',
    '아들',
    '010-9911-2670'
) ON CONFLICT (user_id) DO UPDATE SET
    resident_number = EXCLUDED.resident_number,
    nickname = EXCLUDED.nickname,
    admission_date = EXCLUDED.admission_date,
    discharge_date = EXCLUDED.discharge_date,
    room_number = EXCLUDED.room_number,
    floor_number = EXCLUDED.floor_number,
    bed_number = EXCLUDED.bed_number,
    adl_level = EXCLUDED.adl_level,
    mobility_level = EXCLUDED.mobility_level,
    cognitive_level = EXCLUDED.cognitive_level,
    medication_schedule = EXCLUDED.medication_schedule,
    medication_notes = EXCLUDED.medication_notes,
    special_notes = EXCLUDED.special_notes,
    incidents = EXCLUDED.incidents,
    dietary_restrictions = EXCLUDED.dietary_restrictions,
    emergency_contacts = EXCLUDED.emergency_contacts,
    insurance_info = EXCLUDED.insurance_info,
    medical_facility_info = EXCLUDED.medical_facility_info,
    care_level = EXCLUDED.care_level,
    guardian_name = EXCLUDED.guardian_name,
    guardian_relationship = EXCLUDED.guardian_relationship,
    guardian_phone = EXCLUDED.guardian_phone,
    updated_at = NOW();

-- 한기문 (Gyomei Himejima) - 입소자 정보
INSERT INTO residents (
    user_id,
    resident_number,
    nickname,
    admission_date,
    discharge_date,
    room_number,
    floor_number,
    bed_number,
    adl_level,
    mobility_level,
    cognitive_level,
    medication_schedule,
    medication_notes,
    special_notes,
    incidents,
    dietary_restrictions,
    emergency_contacts,
    insurance_info,
    medical_facility_info,
    care_level,
    guardian_name,
    guardian_relationship,
    guardian_phone
) VALUES (
    '00000000-0000-0000-0000-000000000002',
    'R-2024-002',
    'Gyomei Himejima',
    '2021-08-20',
    NULL,
    '205',
    2,
    'B',
    'full_assistance',
    'wheelchair',
    'normal',
    '[
        {
            "medication_name": "당뇨약",
            "time": "08:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        },
        {
            "medication_name": "고지혈증약",
            "time": "20:00",
            "dose": "1알",
            "route": "경구",
            "with_food": false
        },
        {
            "medication_name": "심부전약",
            "time": "08:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        }
    ]'::jsonb,
    '식후 30분 복용. 혈당 모니터링 필요. 심부전 약물은 염분 제한과 함께 복용.',
    '{
        "health": {
            "diabetes": "혈당 모니터링 필요 (공복 100-120 유지 목표)",
            "hyperlipidemia": "고지혈증 관리 필요",
            "heart_failure": "심부전 초기 진단, 염분 제한 필수",
            "vision": "중증 시각 장애 (시야 대부분 소실)"
        },
        "emotional": {
            "anxiety": "없음",
            "mood": "안정적, 촉감과 소리에 민감"
        },
        "psychological": {
            "memory": "정상",
            "orientation": "정상 (음성 안내로 공간 인지 가능)"
        },
        "behavioral": {
            "wandering": "없음",
            "agitation": "없음",
            "communication": "익숙한 목소리와 발걸음 소리를 잘 구분함"
        }
    }'::jsonb,
    '[]'::jsonb,
    '{
        "allergies": [],
        "restrictions": ["저염식", "당뇨식"],
        "preferences": ["부드러운 음식", "따뜻한 음식"],
        "feeding_assistance": "전면 도움 필요 (시각 장애로 인해)",
        "swallowing": "정상"
    }'::jsonb,
    '[
        {
            "name": "조인우",
            "relationship": "손자",
            "phone": "010-3874-9921",
            "priority": 1,
            "available_hours": "방학 및 시험 종료 기간 집중 방문"
        },
        {
            "name": "조인우 아버지",
            "relationship": "아들",
            "phone": "010-5555-1234",
            "priority": 2,
            "available_hours": "주말 가능"
        }
    ]'::jsonb,
    '{
        "health_insurance": {
            "number": "2345678901",
            "type": "건강보험"
        },
        "long_term_care_insurance": {
            "number": "1098765432",
            "grade": "등급 1",
            "start_date": "2021-08-20"
        },
        "medical_aid": false
    }'::jsonb,
    '{
        "primary_hospital": {
            "name": "서울대학교병원",
            "department": "내과",
            "doctor": "김철수",
            "phone": "02-2072-2114"
        },
        "pharmacy": {
            "name": "○○약국",
            "phone": "02-2345-6789",
            "address": "서울특별시 동대문구 이문로 45"
        },
        "emergency_hospital": {
            "name": "응급의료센터",
            "phone": "119"
        }
    }'::jsonb,
    '1등급',
    '조인우',
    '손자',
    '010-3874-9921'
) ON CONFLICT (user_id) DO UPDATE SET
    resident_number = EXCLUDED.resident_number,
    nickname = EXCLUDED.nickname,
    admission_date = EXCLUDED.admission_date,
    discharge_date = EXCLUDED.discharge_date,
    room_number = EXCLUDED.room_number,
    floor_number = EXCLUDED.floor_number,
    bed_number = EXCLUDED.bed_number,
    adl_level = EXCLUDED.adl_level,
    mobility_level = EXCLUDED.mobility_level,
    cognitive_level = EXCLUDED.cognitive_level,
    medication_schedule = EXCLUDED.medication_schedule,
    medication_notes = EXCLUDED.medication_notes,
    special_notes = EXCLUDED.special_notes,
    incidents = EXCLUDED.incidents,
    dietary_restrictions = EXCLUDED.dietary_restrictions,
    emergency_contacts = EXCLUDED.emergency_contacts,
    insurance_info = EXCLUDED.insurance_info,
    medical_facility_info = EXCLUDED.medical_facility_info,
    care_level = EXCLUDED.care_level,
    guardian_name = EXCLUDED.guardian_name,
    guardian_relationship = EXCLUDED.guardian_relationship,
    guardian_phone = EXCLUDED.guardian_phone,
    updated_at = NOW();

-- 이강열 (Kyojuro Rengoku) - 입소자 정보
INSERT INTO residents (
    user_id,
    resident_number,
    nickname,
    admission_date,
    discharge_date,
    room_number,
    floor_number,
    bed_number,
    adl_level,
    mobility_level,
    cognitive_level,
    medication_schedule,
    medication_notes,
    special_notes,
    incidents,
    dietary_restrictions,
    emergency_contacts,
    insurance_info,
    medical_facility_info,
    care_level,
    guardian_name,
    guardian_relationship,
    guardian_phone
) VALUES (
    '00000000-0000-0000-0000-000000000003',
    'R-2024-003',
    'Kyojuro Rengoku',
    '2023-01-10',
    NULL,
    '108',
    1,
    'A',
    'independent',
    'independent',
    'normal',
    '[
        {
            "medication_name": "고혈압약",
            "time": "08:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        },
        {
            "medication_name": "협심증약",
            "time": "08:00",
            "dose": "1알",
            "route": "설하",
            "with_food": false,
            "note": "가슴 통증 시 추가 복용 가능"
        },
        {
            "medication_name": "관절염약",
            "time": "20:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        }
    ]'::jsonb,
    '식후 30분 복용. 협심증 약물은 가슴 통증 시 즉시 복용 가능. 계단·경사로 이용 시 관찰 필요.',
    '{
        "health": {
            "blood_pressure": "고혈압 관리 필요",
            "angina": "협심증 주의 (갑작스러운 가슴 통증 호소 이력)",
            "arthritis": "무릎 관절염 (계단 이용 시 주의)"
        },
        "emotional": {
            "anxiety": "없음",
            "mood": "활달하고 긍정적, 주변 어르신들을 자주 격려함"
        },
        "psychological": {
            "memory": "정상",
            "orientation": "정상"
        },
        "behavioral": {
            "wandering": "없음",
            "agitation": "없음",
            "social": "프로그램 참여율 높음, 리더십 있음"
        }
    }'::jsonb,
    '[
        {
            "incident_date": "2023-06-15",
            "incident_type": "건강 이상",
            "location": "복도",
            "severity": "경미",
            "description": "계단 이용 중 갑작스러운 가슴 통증 호소",
            "action_taken": "즉시 휴식, 협심증 약물 복용, 상태 안정화 확인",
            "preventive_measures": "계단·경사로 이용 시 동행 권장, 협심증 약물 휴대 필수"
        }
    ]'::jsonb,
    '{
        "allergies": [],
        "restrictions": ["저염식"],
        "preferences": ["다양한 음식 선호"],
        "feeding_assistance": "독립적",
        "swallowing": "정상"
    }'::jsonb,
    '[
        {
            "name": "오범준",
            "relationship": "사위",
            "phone": "010-6420-5531",
            "priority": 1,
            "available_hours": "주로 배우자와 함께 방문"
        },
        {
            "name": "이강열의 딸",
            "relationship": "딸",
            "phone": "010-7777-8888",
            "priority": 2,
            "available_hours": "주말 가능"
        }
    ]'::jsonb,
    '{
        "health_insurance": {
            "number": "3456789012",
            "type": "건강보험"
        },
        "long_term_care_insurance": {
            "number": "2109876543",
            "grade": "등급 3",
            "start_date": "2023-01-10"
        },
        "medical_aid": false
    }'::jsonb,
    '{
        "primary_hospital": {
            "name": "서울대학교병원",
            "department": "내과",
            "doctor": "이영희",
            "phone": "02-2072-2114"
        },
        "pharmacy": {
            "name": "○○약국",
            "phone": "02-3456-7890",
            "address": "서울특별시 강서구 마곡중앙로 22"
        },
        "emergency_hospital": {
            "name": "응급의료센터",
            "phone": "119"
        }
    }'::jsonb,
    '3등급',
    '오범준',
    '사위',
    '010-6420-5531'
) ON CONFLICT (user_id) DO UPDATE SET
    resident_number = EXCLUDED.resident_number,
    nickname = EXCLUDED.nickname,
    admission_date = EXCLUDED.admission_date,
    discharge_date = EXCLUDED.discharge_date,
    room_number = EXCLUDED.room_number,
    floor_number = EXCLUDED.floor_number,
    bed_number = EXCLUDED.bed_number,
    adl_level = EXCLUDED.adl_level,
    mobility_level = EXCLUDED.mobility_level,
    cognitive_level = EXCLUDED.cognitive_level,
    medication_schedule = EXCLUDED.medication_schedule,
    medication_notes = EXCLUDED.medication_notes,
    special_notes = EXCLUDED.special_notes,
    incidents = EXCLUDED.incidents,
    dietary_restrictions = EXCLUDED.dietary_restrictions,
    emergency_contacts = EXCLUDED.emergency_contacts,
    insurance_info = EXCLUDED.insurance_info,
    medical_facility_info = EXCLUDED.medical_facility_info,
    care_level = EXCLUDED.care_level,
    guardian_name = EXCLUDED.guardian_name,
    guardian_relationship = EXCLUDED.guardian_relationship,
    guardian_phone = EXCLUDED.guardian_phone,
    updated_at = NOW();

-- 김선우 (Zenitsu Agatsuma) - 입소자 정보
INSERT INTO residents (
    user_id,
    resident_number,
    nickname,
    admission_date,
    discharge_date,
    room_number,
    floor_number,
    bed_number,
    adl_level,
    mobility_level,
    cognitive_level,
    medication_schedule,
    medication_notes,
    special_notes,
    incidents,
    dietary_restrictions,
    emergency_contacts,
    insurance_info,
    medical_facility_info,
    care_level,
    guardian_name,
    guardian_relationship,
    guardian_phone
) VALUES (
    '00000000-0000-0000-0000-000000000004',
    'R-2024-004',
    'Zenitsu Agatsuma',
    '2023-05-20',
    NULL,
    '407',
    4,
    'B',
    'partial_assistance',
    'independent',
    'mild_impairment',
    '[
        {
            "medication_name": "불안장애약",
            "time": "08:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        },
        {
            "medication_name": "불면증약",
            "time": "21:00",
            "dose": "1알",
            "route": "경구",
            "with_food": false,
            "note": "취침 30분 전 복용"
        },
        {
            "medication_name": "치매약",
            "time": "08:00",
            "dose": "1알",
            "route": "경구",
            "with_food": true
        }
    ]'::jsonb,
    '식후 30분 복용. 불면증 약물은 취침 30분 전 복용. 낮 동안 졸림 호소 시 주의.',
    '{
        "health": {
            "anxiety": "불안장애 관리 필요",
            "insomnia": "불면증 (낮 졸림, 밤 잠들기 어려움)",
            "dementia": "경도 치매 (초기 단기 기억력 저하)"
        },
        "emotional": {
            "anxiety": "큰 소리와 갑작스러운 접촉에 대한 두려움",
            "mood": "친숙한 사람에게만 마음을 여는 경향"
        },
        "psychological": {
            "memory": "단기 기억력 저하 (약물 복용 시간 확인 필요)",
            "orientation": "정상 (새로운 환경 적응 느림)"
        },
        "behavioral": {
            "wandering": "없음",
            "agitation": "큰 소리와 갑작스러운 접촉에 매우 민감",
            "sleep": "낮 졸림 호소 잦음, 밤 잠들기까지 시간 오래 걸림"
        }
    }'::jsonb,
    '[]'::jsonb,
    '{
        "allergies": [],
        "restrictions": [],
        "preferences": ["부드러운 음식", "따뜻한 음식"],
        "feeding_assistance": "부분 도움 필요",
        "swallowing": "정상"
    }'::jsonb,
    '[
        {
            "name": "우태건",
            "relationship": "아들",
            "phone": "010-2841-7703",
            "priority": 1,
            "available_hours": "연 1~2회 장기 면회, 평소 영상통화"
        },
        {
            "name": "우태건 부인",
            "relationship": "며느리",
            "phone": "010-9999-8888",
            "priority": 2,
            "available_hours": "연 1~2회 장기 면회"
        }
    ]'::jsonb,
    '{
        "health_insurance": {
            "number": "4567890123",
            "type": "건강보험"
        },
        "long_term_care_insurance": {
            "number": "3210987654",
            "grade": "등급 2",
            "start_date": "2023-05-20"
        },
        "medical_aid": false
    }'::jsonb,
    '{
        "primary_hospital": {
            "name": "서울대학교병원",
            "department": "정신건강의학과",
            "doctor": "박민수",
            "phone": "02-2072-2114"
        },
        "pharmacy": {
            "name": "○○약국",
            "phone": "02-4567-8901",
            "address": "서울특별시 은평구 응암로 7"
        },
        "emergency_hospital": {
            "name": "응급의료센터",
            "phone": "119"
        }
    }'::jsonb,
    '2등급',
    '우태건',
    '아들',
    '010-2841-7703'
) ON CONFLICT (user_id) DO UPDATE SET
    resident_number = EXCLUDED.resident_number,
    nickname = EXCLUDED.nickname,
    admission_date = EXCLUDED.admission_date,
    discharge_date = EXCLUDED.discharge_date,
    room_number = EXCLUDED.room_number,
    floor_number = EXCLUDED.floor_number,
    bed_number = EXCLUDED.bed_number,
    adl_level = EXCLUDED.adl_level,
    mobility_level = EXCLUDED.mobility_level,
    cognitive_level = EXCLUDED.cognitive_level,
    medication_schedule = EXCLUDED.medication_schedule,
    medication_notes = EXCLUDED.medication_notes,
    special_notes = EXCLUDED.special_notes,
    incidents = EXCLUDED.incidents,
    dietary_restrictions = EXCLUDED.dietary_restrictions,
    emergency_contacts = EXCLUDED.emergency_contacts,
    insurance_info = EXCLUDED.insurance_info,
    medical_facility_info = EXCLUDED.medical_facility_info,
    care_level = EXCLUDED.care_level,
    guardian_name = EXCLUDED.guardian_name,
    guardian_relationship = EXCLUDED.guardian_relationship,
    guardian_phone = EXCLUDED.guardian_phone,
    updated_at = NOW();

-- ============================================================
-- 완료 메시지
-- ============================================================
SELECT '요양원 사용자 전체 목업 데이터 삽입 완료!' AS message;

