"""
ResidentInfo 도메인 엔티티

요양원 내부 입소자 관리 정보를 관리합니다.
"""

from datetime import date, datetime
from typing import Optional, Dict, Any
from uuid import UUID
from dataclasses import dataclass, field


@dataclass
class ResidentInfo:
    """요양원 내부 입소자 관리 정보 엔티티"""
    
    user_id: UUID
    admission_date: date
    # 기본 정보 (users 테이블과 동일)
    user_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    # 입소 관리 정보
    resident_number: Optional[str] = None
    nickname: Optional[str] = None
    discharge_date: Optional[date] = None
    room_number: Optional[str] = None
    floor_number: Optional[int] = None
    bed_number: Optional[str] = None
    adl_level: Optional[str] = "independent"
    mobility_level: Optional[str] = None
    cognitive_level: Optional[str] = None
    medication_schedule: Optional[Dict[str, Any]] = None
    medication_notes: Optional[str] = None
    special_notes: Optional[Dict[str, Any]] = None
    incidents: Optional[Dict[str, Any]] = None
    dietary_restrictions: Optional[Dict[str, Any]] = None
    emergency_contacts: Optional[Dict[str, Any]] = None
    insurance_info: Optional[Dict[str, Any]] = None
    medical_facility_info: Optional[Dict[str, Any]] = None
    care_level: Optional[str] = None
    guardian_name: Optional[str] = None
    guardian_relationship: Optional[str] = None
    guardian_phone: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """유효성 검사"""
        if self.adl_level and self.adl_level not in ['independent', 'partial_assistance', 'full_assistance']:
            raise ValueError(f"유효하지 않은 ADL 수준입니다: {self.adl_level}")
        
        if self.mobility_level and self.mobility_level not in ['independent', 'walker', 'wheelchair', 'bedridden']:
            raise ValueError(f"유효하지 않은 이동 수준입니다: {self.mobility_level}")
        
        if self.cognitive_level and self.cognitive_level not in ['normal', 'mild_impairment', 'moderate_impairment', 'severe_impairment']:
            raise ValueError(f"유효하지 않은 인지 수준입니다: {self.cognitive_level}")
        
        if self.discharge_date and self.discharge_date < self.admission_date:
            raise ValueError("퇴소일은 입소일 이후여야 합니다.")
    
    def is_currently_admitted(self) -> bool:
        """현재 입소 중인지 확인"""
        return self.discharge_date is None
    
    def get_age(self, reference_date: Optional[date] = None) -> Optional[int]:
        """나이 계산 (user_profiles의 date_of_birth 필요)"""
        # 이 메서드는 user_profiles와 조인하여 사용해야 함
        return None
    
    def add_incident(self, incident: Dict[str, Any]) -> None:
        """사건/사고 기록 추가"""
        if self.incidents is None:
            self.incidents = {"incidents": []}
        elif "incidents" not in self.incidents:
            self.incidents["incidents"] = []
        
        self.incidents["incidents"].append(incident)
        self.updated_at = datetime.utcnow()
    
    def update_medication_schedule(self, schedule: list) -> None:
        """복약 일정 업데이트"""
        self.medication_schedule = {"schedule": schedule}
        self.updated_at = datetime.utcnow()

