#!/usr/bin/env python3
"""
실제적인 어르신 데이터 100명 및 관계자 데이터 생성 스크립트

이 스크립트는 사실적인 목업 데이터를 생성합니다:
- 100명의 어르신 (care_target)
- 각 어르신당 1-2명의 담당 직원 (caregiver)
- 각 어르신당 1-3명의 가족 (family)
- 관리자 관계 (admin)
"""

import uuid
import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Tuple
import json

# 한국 이름 데이터 (실제 사용되는 이름)
KOREAN_FIRST_NAMES_MALE = [
    '기준', '민수', '영수', '성호', '정호', '영호', '상호', '동호', '태호', '준호',
    '민호', '지훈', '현우', '준영', '성민', '민준', '지우', '서준', '도윤', '예준',
    '건우', '현준', '윤서', '지원', '준서', '유준', '시우', '하준', '지후', '준혁',
    '도현', '시현', '준호', '민재', '지안', '서진', '준수', '승현', '민석', '준희'
]

KOREAN_FIRST_NAMES_FEMALE = [
    '영희', '순자', '옥자', '미영', '정자', '숙자', '영자', '옥순', '미숙', '정숙',
    '영숙', '미경', '정희', '영미', '순희', '옥희', '미희', '정미', '영경', '순경',
    '지은', '서연', '서윤', '지우', '서현', '민서', '하은', '예은', '윤서', '채원',
    '지원', '예원', '지유', '서아', '수아', '지안', '예린', '채은', '은서', '다은'
]

KOREAN_LAST_NAMES = [
    '김', '이', '박', '최', '정', '강', '조', '윤', '장', '임',
    '한', '오', '서', '신', '권', '황', '안', '송', '류', '전',
    '홍', '고', '문', '양', '손', '배', '조', '백', '허', '유',
    '남', '심', '노', '정', '하', '곽', '성', '차', '주', '우'
]

# 서울 지역구
SEOUL_DISTRICTS = [
    '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
    '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
    '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
]

# 병력 데이터 (실제 요양원에서 흔한 병력)
MEDICAL_CONDITIONS = [
    '고혈압', '당뇨병', '치매', '파킨슨병', '뇌졸중', '골다공증', '관절염',
    '심부전', '만성폐쇄성폐질환', '신부전', '간경화', '위암', '폐암', '대장암',
    '알츠하이머병', '우울증', '불안장애', '불면증', '요실금', '난청', '시력저하'
]

# 생활실 번호 생성 (1-5층, 각 층당 20-30개 방)
def generate_room_number(floor: int) -> str:
    """생활실 번호 생성"""
    room = random.randint(1, 30)
    return f"{floor}{room:02d}"

# 입소일 생성 (2018년부터 현재까지)
def generate_admission_date() -> date:
    """입소일 생성 (2018-01-01 ~ 현재)"""
    start_date = date(2018, 1, 1)
    end_date = date.today()
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)

# 생년월일 생성 (1920년대 ~ 1950년대)
def generate_birth_date(gender: str) -> date:
    """생년월일 생성"""
    birth_year = random.randint(1920, 1955)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    return date(birth_year, birth_month, birth_day)

# 전화번호 생성
def generate_phone_number() -> str:
    """전화번호 생성 (010-XXXX-XXXX)"""
    middle = random.randint(1000, 9999)
    last = random.randint(1000, 9999)
    return f"010-{middle}-{last}"

# 이메일 생성
def generate_email(name: str) -> str:
    """이메일 생성"""
    domains = ['gmail.com', 'naver.com', 'daum.net', 'hanmail.net', 'kakao.com']
    name_clean = name.replace(' ', '').lower()
    return f"{name_clean}{random.randint(10, 99)}@{random.choice(domains)}"

# 복약 일정 생성
def generate_medication_schedule() -> List[Dict]:
    """복약 일정 생성"""
    medications = [
        {'name': '고혈압약', 'times': ['08:00', '20:00']},
        {'name': '당뇨약', 'times': ['08:00', '12:00', '18:00']},
        {'name': '치매약', 'times': ['08:00']},
        {'name': '우울증약', 'times': ['20:00']},
        {'name': '불면증약', 'times': ['21:00']},
        {'name': '관절염약', 'times': ['08:00', '20:00']},
        {'name': '비타민', 'times': ['08:00']},
    ]
    
    selected = random.sample(medications, random.randint(1, 4))
    schedule = []
    
    for med in selected:
        for time in med['times']:
            schedule.append({
                'medication_name': med['name'],
                'time': time,
                'dose': f"{random.randint(1, 2)}알",
                'route': '경구',
                'with_food': random.choice([True, False])
            })
    
    return schedule

# 응급 연락처 생성
def generate_emergency_contacts(family_members: List[Dict]) -> List[Dict]:
    """응급 연락처 생성"""
    contacts = []
    for i, member in enumerate(family_members[:3], 1):  # 최대 3명
        contacts.append({
            'name': member['name'],
            'phone': member['phone'],
            'relationship': member['relationship'],
            'priority': i,
            'available_hours': random.choice([
                '평일 18:00 이후, 주말 가능',
                '24시간 가능',
                '평일 19:00 이후',
                '주말 가능'
            ])
        })
    return contacts

# 특이사항 생성
def generate_special_notes(medical_history: str) -> Dict:
    """특이사항 생성"""
    notes = {
        'health': {},
        'emotional': {},
        'behavioral': {},
        'psychological': {}
    }
    
    if '고혈압' in medical_history:
        notes['health']['blood_pressure'] = '고혈압 주의 (140/90 이상 시 알림)'
    if '당뇨' in medical_history:
        notes['health']['diabetes'] = '혈당 모니터링 필요 (공복 100-120 유지 목표)'
    if '치매' in medical_history or '알츠하이머' in medical_history:
        notes['psychological']['dementia'] = '경도~중등도 치매 (단기 기억력 저하)'
        notes['behavioral']['wandering'] = random.choice(['없음', '경미', '중등도'])
    if '우울' in medical_history:
        notes['emotional']['mood'] = '경도 우울감 (격려 및 관심 필요)'
    if '불면' in medical_history:
        notes['behavioral']['sleep'] = '불면증 (야간 각성 빈번)'
    
    return notes

# 사건/사고 기록 생성
def generate_incidents(admission_date: date) -> List[Dict]:
    """사건/사고 기록 생성 (30% 확률로 1-2건)"""
    if random.random() > 0.3:
        return []
    
    incidents = []
    num_incidents = random.randint(1, 2)
    
    for _ in range(num_incidents):
        days_ago = random.randint(30, (date.today() - admission_date).days)
        incident_date = date.today() - timedelta(days=days_ago)
        
        incident_types = ['낙상', '압박궤양', '호흡곤란', '식사곤란', '배뇨장애']
        locations = ['화장실', '침대', '복도', '식당', '거실']
        severities = ['경미', '중등도', '중증']
        
        incidents.append({
            'incident_date': incident_date.isoformat(),
            'incident_type': random.choice(incident_types),
            'location': random.choice(locations),
            'severity': random.choice(severities),
            'description': f"{random.choice(locations)}에서 {random.choice(incident_types)} 발생",
            'action_taken': '응급실 방문, 검사 완료, 상태 안정',
            'preventive_measures': '재발 방지를 위한 주의사항 적용'
        })
    
    return incidents

# ADL 수준 결정
def determine_adl_level(age: int, medical_history: str) -> str:
    """ADL 수준 결정"""
    if age >= 90 or '치매' in medical_history or '뇌졸중' in medical_history:
        return random.choice(['partial_assistance', 'full_assistance'])
    elif age >= 85:
        return random.choice(['independent', 'partial_assistance'])
    else:
        return random.choice(['independent', 'partial_assistance'])

# 이동 수준 결정
def determine_mobility_level(adl_level: str) -> str:
    """이동 수준 결정"""
    if adl_level == 'full_assistance':
        return random.choice(['wheelchair', 'bedridden'])
    elif adl_level == 'partial_assistance':
        return random.choice(['walker', 'wheelchair'])
    else:
        return random.choice(['independent', 'walker'])

# 인지 수준 결정
def determine_cognitive_level(medical_history: str) -> str:
    """인지 수준 결정"""
    if '치매' in medical_history or '알츠하이머' in medical_history:
        return random.choice(['mild_impairment', 'moderate_impairment', 'severe_impairment'])
    elif '뇌졸중' in medical_history:
        return random.choice(['normal', 'mild_impairment', 'moderate_impairment'])
    else:
        return random.choice(['normal', 'mild_impairment'])

# 가족 관계 생성
def generate_family_relationships(resident_id: str, resident_name: str, resident_birth_date: date) -> List[Dict]:
    """가족 관계 생성"""
    relationships = []
    num_family = random.randint(1, 3)
    
    family_types = ['아들', '딸', '배우자', '손자', '손녀', '며느리', '사위']
    selected_types = random.sample(family_types, min(num_family, len(family_types)))
    
    for rel_type in selected_types:
        # 가족의 생년월일 추정
        if rel_type in ['아들', '딸']:
            family_birth_year = resident_birth_date.year + random.randint(25, 40)
        elif rel_type == '배우자':
            family_birth_year = resident_birth_date.year + random.randint(-5, 5)
        elif rel_type in ['손자', '손녀']:
            family_birth_year = resident_birth_date.year + random.randint(50, 65)
        else:
            family_birth_year = resident_birth_date.year + random.randint(20, 35)
        
        family_birth_date = date(family_birth_year, random.randint(1, 12), random.randint(1, 28))
        gender = 'male' if rel_type in ['아들', '손자', '사위'] else 'female'
        
        family_name = generate_korean_name(gender)
        
        relationships.append({
            'name': family_name,
            'relationship': rel_type,
            'birth_date': family_birth_date,
            'gender': gender,
            'phone': generate_phone_number(),
            'email': generate_email(family_name)
        })
    
    return relationships

# 한국 이름 생성
def generate_korean_name(gender: str) -> str:
    """한국 이름 생성"""
    last_name = random.choice(KOREAN_LAST_NAMES)
    if gender == 'male':
        first_name = random.choice(KOREAN_FIRST_NAMES_MALE)
    else:
        first_name = random.choice(KOREAN_FIRST_NAMES_FEMALE)
    return f"{last_name}{first_name}"

# 직원 데이터 생성 (100명의 어르신을 위해 약 20-30명의 직원 필요)
def generate_staff_members(num_staff: int = 25) -> List[Dict]:
    """직원 데이터 생성"""
    staff = []
    roles = ['간호사', '사회복지사', '요양보호사', '물리치료사', '작업치료사']
    
    for i in range(num_staff):
        gender = random.choice(['male', 'female'])
        name = generate_korean_name(gender)
        birth_year = random.randint(1970, 1995)
        birth_date = date(birth_year, random.randint(1, 12), random.randint(1, 28))
        
        staff.append({
            'name': name,
            'gender': gender,
            'birth_date': birth_date,
            'role': random.choice(roles),
            'phone': generate_phone_number(),
            'email': generate_email(name)
        })
    
    return staff

def generate_residents_data(num_residents: int = 100) -> Tuple[List[Dict], List[Dict], List[Dict], List[Dict]]:
    """어르신 데이터 생성"""
    residents = []
    users = []
    profiles = []
    relationships = []
    
    # 직원 생성
    staff_members = generate_staff_members(25)
    staff_users = []
    staff_profiles = []
    
    for staff in staff_members:
        user_id = str(uuid.uuid4())
        staff_users.append({
            'user_id': user_id,
            'user_role': 'caregiver',
            'user_name': staff['name'],
            'email': staff['email'],
            'phone_number': staff['phone']
        })
        staff_profiles.append({
            'user_id': user_id,
            'date_of_birth': staff['birth_date'],
            'gender': staff['gender'],
            'address': f"서울특별시 {random.choice(SEOUL_DISTRICTS)}",
            'address_detail': f"{random.randint(1, 500)}-{random.randint(1, 50)}",
            'medical_history': '특이 병력 없음',
            'significant_notes': f"직원 역할: {staff['role']}",
            'current_status': f"{staff['role']}로 근무 중"
        })
    
    users.extend(staff_users)
    profiles.extend(staff_profiles)
    
    # 어르신 데이터 생성
    for i in range(num_residents):
        # 기본 정보
        gender = random.choice(['male', 'female'])
        name = generate_korean_name(gender)
        birth_date = generate_birth_date(gender)
        age = (date.today() - birth_date).days // 365
        
        user_id = str(uuid.uuid4())
        admission_date = generate_admission_date()
        floor = random.randint(1, 5)
        room_number = generate_room_number(floor)
        
        # 병력 생성
        num_conditions = random.randint(1, 4)
        medical_conditions = random.sample(MEDICAL_CONDITIONS, num_conditions)
        medical_history = ', '.join(medical_conditions)
        
        # ADL 수준 결정
        adl_level = determine_adl_level(age, medical_history)
        mobility_level = determine_mobility_level(adl_level)
        cognitive_level = determine_cognitive_level(medical_history)
        
        # 가족 관계 생성
        family_members = generate_family_relationships(user_id, name, birth_date)
        
        # users 테이블
        users.append({
            'user_id': user_id,
            'user_role': 'care_target',
            'user_name': name,
            'email': generate_email(name),
            'phone_number': generate_phone_number()
        })
        
        # user_profiles 테이블
        profiles.append({
            'user_id': user_id,
            'date_of_birth': birth_date,
            'gender': gender,
            'address': f"서울특별시 {random.choice(SEOUL_DISTRICTS)} {random.choice(['로', '길'])} {random.randint(1, 500)}",
            'address_detail': f"○○요양원 {room_number}호",
            'medical_history': medical_history,
            'significant_notes': f"입소 전 거주지: 서울특별시 {random.choice(SEOUL_DISTRICTS)}",
            'current_status': f"입소 중. {adl_level} 수준. {mobility_level} 사용."
        })
        
        # residents 테이블
        medication_schedule = generate_medication_schedule()
        special_notes = generate_special_notes(medical_history)
        incidents = generate_incidents(admission_date)
        emergency_contacts = generate_emergency_contacts(family_members)
        
        residents.append({
            'user_id': user_id,
            'user_name': name,
            'email': generate_email(name),
            'phone_number': generate_phone_number(),
            'resident_number': f"R-{admission_date.year}-{i+1:03d}",
            'nickname': None,
            'admission_date': admission_date,
            'discharge_date': None,
            'room_number': room_number,
            'floor_number': floor,
            'bed_number': random.choice(['A', 'B', 'C']),
            'adl_level': adl_level,
            'mobility_level': mobility_level,
            'cognitive_level': cognitive_level,
            'medication_schedule': medication_schedule,
            'medication_notes': '식후 30분 복용. 혈압 모니터링 필요.',
            'special_notes': special_notes,
            'incidents': incidents if incidents else {},
            'dietary_restrictions': {
                'allergies': random.sample(['견과류', '해산물', '우유', '계란'], random.randint(0, 2)),
                'swallowing': random.choice(['정상', '경미한 어려움', '부분 도움 필요']),
                'preferences': random.sample(['부드러운 음식', '따뜻한 음식', '단 음식'], random.randint(0, 2)),
                'restrictions': random.sample(['저염식', '당뇨식', '연식'], random.randint(0, 2)),
                'feeding_assistance': random.choice(['없음', '부분 도움 필요', '전체 도움 필요'])
            },
            'emergency_contacts': emergency_contacts,
            'insurance_info': {
                'medical_aid': random.choice([True, False]),
                'health_insurance': {
                    'type': '건강보험',
                    'number': f"{random.randint(1000000000, 9999999999)}"
                },
                'long_term_care_insurance': {
                    'grade': random.choice(['등급 1', '등급 2', '등급 3']),
                    'number': f"{random.randint(1000000000, 9999999999)}",
                    'start_date': admission_date.isoformat()
                }
            },
            'medical_facility_info': {
                'pharmacy': {
                    'name': f"○○약국",
                    'phone': generate_phone_number(),
                    'address': f"서울특별시 {random.choice(SEOUL_DISTRICTS)}"
                },
                'primary_hospital': {
                    'name': random.choice(['서울대학교병원', '세브란스병원', '삼성서울병원', '아산병원']),
                    'phone': generate_phone_number(),
                    'doctor': generate_korean_name('male'),
                    'department': random.choice(['내과', '정형외과', '신경과', '정신건강의학과'])
                },
                'emergency_hospital': {
                    'name': '응급의료센터',
                    'phone': '119'
                }
            },
            'care_level': random.choice(['1등급', '2등급', '3등급']),
            'guardian_name': family_members[0]['name'] if family_members else None,
            'guardian_relationship': family_members[0]['relationship'] if family_members else None,
            'guardian_phone': family_members[0]['phone'] if family_members else None
        })
        
        # 가족 users 및 profiles 생성
        for family in family_members:
            family_user_id = str(uuid.uuid4())
            users.append({
                'user_id': family_user_id,
                'user_role': 'family',
                'user_name': family['name'],
                'email': family['email'],
                'phone_number': family['phone']
            })
            profiles.append({
                'user_id': family_user_id,
                'date_of_birth': family['birth_date'],
                'gender': family['gender'],
                'address': f"서울특별시 {random.choice(SEOUL_DISTRICTS)}",
                'address_detail': f"{random.randint(1, 500)}-{random.randint(1, 50)}",
                'medical_history': '특이 병력 없음',
                'significant_notes': f"{name} 어르신의 {family['relationship']}",
                'current_status': f"월 {random.randint(1, 4)}회 방문"
            })
            
            # family 관계 추가
            relationships.append({
                'subject_user_id': family_user_id,
                'target_user_id': user_id,
                'relationship_type': 'family',
                'status': 'active'
            })
        
        # 담당 직원 관계 생성 (1-2명)
        num_caregivers = random.randint(1, 2)
        assigned_staff = random.sample(staff_users, min(num_caregivers, len(staff_users)))
        for staff_user in assigned_staff:
            relationships.append({
                'subject_user_id': staff_user['user_id'],
                'target_user_id': user_id,
                'relationship_type': 'caregiver',
                'status': 'active'
            })
        
        # 관리자 관계 생성 (모든 어르신에게)
        # 관리자는 별도로 생성하거나 기존 관리자 사용
        # 여기서는 첫 번째 직원을 관리자로 가정
        if staff_users:
            relationships.append({
                'subject_user_id': staff_users[0]['user_id'],  # 첫 번째 직원을 관리자로
                'target_user_id': user_id,
                'relationship_type': 'admin',
                'status': 'active'
            })
    
    return users, profiles, residents, relationships

def generate_sql_insert_statements(users: List[Dict], profiles: List[Dict], 
                                   residents: List[Dict], relationships: List[Dict]) -> str:
    """SQL INSERT 문 생성"""
    sql = "-- ============================================================\n"
    sql += "-- 실제적인 어르신 데이터 100명 및 관계자 데이터\n"
    sql += "-- 생성일: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
    sql += "-- ============================================================\n\n"
    
    # users 테이블
    sql += "-- ============================================================\n"
    sql += "-- 1. users 테이블 INSERT\n"
    sql += "-- ============================================================\n"
    sql += "INSERT INTO users (user_id, user_role, user_name, email, phone_number) VALUES\n"
    
    user_values = []
    for user in users:
        user_values.append(
            f"('{user['user_id']}', '{user['user_role']}', '{user['user_name']}', "
            f"'{user['email']}', '{user['phone_number']}')"
        )
    sql += ",\n".join(user_values) + "\n"
    sql += "ON CONFLICT (user_id) DO NOTHING;\n\n"
    
    # user_profiles 테이블
    sql += "-- ============================================================\n"
    sql += "-- 2. user_profiles 테이블 INSERT\n"
    sql += "-- ============================================================\n"
    sql += "INSERT INTO user_profiles (user_id, date_of_birth, gender, address, address_detail, medical_history, significant_notes, current_status) VALUES\n"
    
    profile_values = []
    for profile in profiles:
        profile_values.append(
            f"('{profile['user_id']}', '{profile['date_of_birth']}', '{profile['gender']}', "
            f"'{profile['address']}', '{profile['address_detail']}', "
            f"'{profile['medical_history']}', '{profile['significant_notes']}', "
            f"'{profile['current_status']}')"
        )
    sql += ",\n".join(profile_values) + "\n"
    sql += "ON CONFLICT (user_id) DO NOTHING;\n\n"
    
    # residents 테이블
    sql += "-- ============================================================\n"
    sql += "-- 3. residents 테이블 INSERT\n"
    sql += "-- ============================================================\n"
    sql += "INSERT INTO residents (\n"
    sql += "    user_id, user_name, email, phone_number, resident_number, nickname, admission_date, discharge_date,\n"
    sql += "    room_number, floor_number, bed_number, adl_level, mobility_level, cognitive_level,\n"
    sql += "    medication_schedule, medication_notes, special_notes, incidents, dietary_restrictions,\n"
    sql += "    emergency_contacts, insurance_info, medical_facility_info, care_level,\n"
    sql += "    guardian_name, guardian_relationship, guardian_phone\n"
    sql += ") VALUES\n"
    
    resident_values = []
    for resident in residents:
        medication_schedule_json = json.dumps(resident['medication_schedule'], ensure_ascii=False)
        special_notes_json = json.dumps(resident['special_notes'], ensure_ascii=False)
        incidents_json = json.dumps(resident['incidents'] if resident['incidents'] else {}, ensure_ascii=False)
        dietary_json = json.dumps(resident['dietary_restrictions'], ensure_ascii=False)
        emergency_json = json.dumps(resident['emergency_contacts'], ensure_ascii=False)
        insurance_json = json.dumps(resident['insurance_info'], ensure_ascii=False)
        medical_facility_json = json.dumps(resident['medical_facility_info'], ensure_ascii=False)
        
        discharge_date = 'NULL' if resident['discharge_date'] is None else f"'{resident['discharge_date']}'"
        nickname = 'NULL' if resident['nickname'] is None else f"'{resident['nickname']}'"
        guardian_name = 'NULL' if resident['guardian_name'] is None else f"'{resident['guardian_name']}'"
        guardian_relationship = 'NULL' if resident['guardian_relationship'] is None else f"'{resident['guardian_relationship']}'"
        guardian_phone = 'NULL' if resident['guardian_phone'] is None else f"'{resident['guardian_phone']}'"
        
        resident_values.append(
            f"('{resident['user_id']}', '{resident['user_name']}', '{resident['email']}', "
            f"'{resident['phone_number']}', '{resident['resident_number']}', {nickname}, "
            f"'{resident['admission_date']}', {discharge_date}, "
            f"'{resident['room_number']}', {resident['floor_number']}, '{resident['bed_number']}', "
            f"'{resident['adl_level']}', '{resident['mobility_level']}', '{resident['cognitive_level']}', "
            f"'{medication_schedule_json}'::jsonb, '{resident['medication_notes']}', "
            f"'{special_notes_json}'::jsonb, '{incidents_json}'::jsonb, '{dietary_json}'::jsonb, "
            f"'{emergency_json}'::jsonb, '{insurance_json}'::jsonb, '{medical_facility_json}'::jsonb, "
            f"'{resident['care_level']}', {guardian_name}, {guardian_relationship}, {guardian_phone})"
        )
    sql += ",\n".join(resident_values) + "\n"
    sql += "ON CONFLICT (user_id) DO NOTHING;\n\n"
    
    # user_relationships 테이블
    sql += "-- ============================================================\n"
    sql += "-- 4. user_relationships 테이블 INSERT\n"
    sql += "-- ============================================================\n"
    sql += "INSERT INTO user_relationships (subject_user_id, target_user_id, relationship_type, status) VALUES\n"
    
    relationship_values = []
    for rel in relationships:
        relationship_values.append(
            f"('{rel['subject_user_id']}', '{rel['target_user_id']}', "
            f"'{rel['relationship_type']}', '{rel['status']}')"
        )
    sql += ",\n".join(relationship_values) + "\n"
    sql += "ON CONFLICT (subject_user_id, target_user_id, relationship_type) DO NOTHING;\n\n"
    
    sql += "-- ============================================================\n"
    sql += "-- 데이터 생성 완료\n"
    sql += f"-- 총 users: {len(users)}개\n"
    sql += f"-- 총 user_profiles: {len(profiles)}개\n"
    sql += f"-- 총 residents: {len(residents)}개\n"
    sql += f"-- 총 user_relationships: {len(relationships)}개\n"
    sql += "-- ============================================================\n"
    
    return sql

def main():
    """메인 함수"""
    print("=" * 80)
    print("실제적인 어르신 데이터 100명 생성")
    print("=" * 80)
    print()
    
    # 데이터 생성
    print("데이터 생성 중...")
    users, profiles, residents, relationships = generate_residents_data(100)
    
    print(f"✅ 생성 완료:")
    print(f"   - users: {len(users)}개")
    print(f"   - user_profiles: {len(profiles)}개")
    print(f"   - residents: {len(residents)}개")
    print(f"   - user_relationships: {len(relationships)}개")
    print()
    
    # SQL 생성
    print("SQL 파일 생성 중...")
    sql = generate_sql_insert_statements(users, profiles, residents, relationships)
    
    # 파일 저장
    output_file = 'maintenance/database/insert_100_residents_realistic_data.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(sql)
    
    print(f"✅ SQL 파일 생성 완료: {output_file}")
    print()
    print("=" * 80)
    print("생성 완료!")
    print("=" * 80)

if __name__ == '__main__':
    main()

