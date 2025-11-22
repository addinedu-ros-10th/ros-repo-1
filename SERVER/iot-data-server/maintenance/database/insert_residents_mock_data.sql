-- ============================================================
-- 요양원 내부 입소자 관리 정보 목업 데이터 삽입
-- ============================================================
-- 
-- 이 스크립트는 users, user_profiles, user_relationships 테이블에
-- 이미 데이터가 있다고 가정하고, residents 테이블에 입소자 정보를 삽입합니다.
--
-- 캐릭터 매핑:
-- - 입소자 (user_role = 'resident'):
--   * Akaza (ID: 0) → 정도현 (user_id: 00000000-0000-0000-0000-000000000001)
--   * Gyomei Himejima (ID: 3) → 한기문 (user_id: 00000000-0000-0000-0000-000000000002)
--   * Kyojuro Rengoku (ID: 7) → 이강열 (user_id: 00000000-0000-0000-0000-000000000003)
--   * Zenitsu Agatsuma (ID: 17) → 김선우 (user_id: 00000000-0000-0000-0000-000000000004)
-- ============================================================

-- ============================================================
-- 1. 정도현 (Akaza) - 입소자 정보
-- ============================================================
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
    '00000000-0000-0000-0000-000000000001',  -- 정도현
    'R-2024-001',
    'Akaza',
    '2022-03-15',  -- 입소일: 2년 전
    NULL,  -- 현재 입소 중
    '302',
    3,
    'A',
    'partial_assistance',  -- 부분 도움 필요
    'walker',  -- 보행기 사용
    'mild_impairment',  -- 경도 인지 저하
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
);

-- ============================================================
-- 2. 한기문 (Gyomei Himejima) - 입소자 정보
-- ============================================================
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
    '00000000-0000-0000-0000-000000000002',  -- 한기문
    'R-2024-002',
    'Gyomei Himejima',
    '2021-08-20',  -- 입소일: 약 3년 전
    NULL,  -- 현재 입소 중
    '205',
    2,
    'B',
    'full_assistance',  -- 전면 도움 필요
    'wheelchair',  -- 휠체어 사용
    'normal',  -- 인지 정상
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
    '[]'::jsonb,  -- 사건/사고 없음
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
);

-- ============================================================
-- 3. 이강열 (Kyojuro Rengoku) - 입소자 정보
-- ============================================================
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
    '00000000-0000-0000-0000-000000000003',  -- 이강열
    'R-2024-003',
    'Kyojuro Rengoku',
    '2023-01-10',  -- 입소일: 약 1년 전
    NULL,  -- 현재 입소 중
    '108',
    1,
    'A',
    'independent',  -- 독립적
    'independent',  -- 독립 이동 가능
    'normal',  -- 인지 정상
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
);

-- ============================================================
-- 4. 김선우 (Zenitsu Agatsuma) - 입소자 정보
-- ============================================================
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
    '00000000-0000-0000-0000-000000000004',  -- 김선우
    'R-2024-004',
    'Zenitsu Agatsuma',
    '2023-05-20',  -- 입소일: 약 1년 전
    NULL,  -- 현재 입소 중
    '407',
    4,
    'B',
    'partial_assistance',  -- 부분 도움 필요
    'independent',  -- 독립 이동 가능
    'mild_impairment',  -- 경도 치매
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
    '[]'::jsonb,  -- 사건/사고 없음
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
);

-- ============================================================
-- 완료 메시지
-- ============================================================
SELECT '요양원 내부 입소자 관리 정보 목업 데이터 삽입 완료!' AS message;

