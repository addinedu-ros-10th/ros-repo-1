"""
어르신 정보 포맷팅 및 템플릿 생성
"""
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def format_room_info(resident_data: Dict) -> str:
    """생활실 정보 포맷팅"""
    floor = resident_data.get('floor_number', '')
    room = resident_data.get('room_number', '')
    bed = resident_data.get('bed_number', '')
    
    if bed:
        return f"{floor}층 {room}호 {bed}번"
    elif floor and room:
        return f"{floor}층 {room}호"
    return "생활실 정보 없음"


def summarize_special_notes(resident_data: Dict) -> List[str]:
    """특이사항 요약"""
    special_notes = resident_data.get('special_notes', {})
    notes = []
    
    # 건강 관련
    health = special_notes.get('health', {})
    if health.get('fall_risk') == '높음' or 'fall_risk' in str(health).lower():
        notes.append("낙상 위험 높음")
    if health.get('diabetes') or 'diabetes' in str(health).lower():
        notes.append("당뇨 관리")
    if health.get('blood_pressure') or 'blood_pressure' in str(health).lower():
        notes.append("고혈압 주의")
    
    # 행동 관련
    behavioral = special_notes.get('behavioral', {})
    if behavioral.get('wandering'):
        notes.append("야간 이동 주의")
    
    # 이동 수준
    mobility = resident_data.get('mobility_level', '')
    if mobility == 'walker':
        notes.append("보행기 사용")
    elif mobility == 'wheelchair':
        notes.append("휠체어 사용")
    
    return notes[:3]  # 최대 3개


def format_display_data(resident_data: Dict, display_format: str = "basic") -> Dict:
    """
    LCD 표시 데이터 포맷팅
    
    Args:
        resident_data: 어르신 정보 딕셔너리
        display_format: "basic", "detailed", "urgent"
    
    Returns:
        {"title": str, "lines": List[str], "show_timestamp": bool}
    """
    name = resident_data.get("nickname") or resident_data.get("user_name", "어르신")
    room_info = format_room_info(resident_data)
    special_notes = summarize_special_notes(resident_data)
    mobility = resident_data.get('mobility_level', '')
    
    if display_format == "basic":
        lines = [
            f"생활실: {room_info}",
            f"상태: {mobility if mobility else '정상'}",
            f"주의: {special_notes[0]}" if special_notes else ""
        ]
    elif display_format == "detailed":
        # 상세 형식 (5줄)
        health_info = []
        if '당뇨' in str(special_notes):
            health_info.append("당뇨")
        if '고혈압' in str(special_notes):
            health_info.append("고혈압")
        health_str = ', '.join(health_info) if health_info else "정상"
        
        lines = [
            f"생활실: {room_info}",
            f"이동: {mobility if mobility else '정상'}",
            f"건강: {health_str}",
            f"주의: {special_notes[0]}" if special_notes else "주의사항 없음"
        ]
        
        # 약물 정보 추가 (있는 경우)
        medication_schedule = resident_data.get('medication_schedule', [])
        if medication_schedule:
            next_med = medication_schedule[0]
            lines.append(f"약물: {next_med.get('medication_name', '')} {next_med.get('time', '')}")
    else:  # urgent
        lines = [
            f"생활실: {room_info}",
            f"⚠️ {special_notes[0]}" if special_notes else "",
            f"보행기 필수 사용" if mobility == 'walker' else ""
        ]
    
    return {
        "title": f"{name} 어르신",
        "lines": [line for line in lines if line],  # 빈 라인 제거
        "show_timestamp": True
    }


# 시나리오별 템플릿 함수들

def format_morning_greeting(resident_data: Dict, weather: Optional[str] = None) -> Dict:
    """아침인사 템플릿"""
    nickname = resident_data.get("nickname") or resident_data.get("user_name", "어르신")
    today = datetime.now()
    
    # 요일 한글 변환
    weekdays = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
    weekday = weekdays[today.weekday()]
    
    lines = [
        f"오늘은 {today.strftime('%Y년 %m월 %d일')}",
        f"{weekday}, {weather or '맑은'} 날씨입니다",
        "좋은 하루 되세요!"
    ]
    
    return {
        "title": f"안녕하세요! {nickname} 어르신",
        "lines": lines,
        "show_timestamp": True
    }


def format_meal_assistance(resident_data: Dict, menu: str, meal_time: str) -> Dict:
    """식사 지원 템플릿"""
    dietary_restrictions = resident_data.get('dietary_restrictions', {})
    restrictions = dietary_restrictions.get('restrictions', [])
    
    lines = [
        f"오늘의 메뉴: {menu}",
        f"{', '.join(restrictions)} 준비" if restrictions else "식사 준비 완료",
        "천천히 드세요"
    ]
    
    return {
        "title": "식사 시간입니다",
        "lines": lines,
        "show_timestamp": True
    }


def format_conversation(resident_data: Dict, topic: str, destination: str) -> Dict:
    """맞춤형 이동식 대화 템플릿"""
    nickname = resident_data.get("nickname") or resident_data.get("user_name", "어르신")
    
    lines = [
        f"주제: {topic}",
        f"목적지: {destination}",
        "천천히 걸어가세요"
    ]
    
    return {
        "title": f"{nickname} 어르신과 대화 중",
        "lines": lines,
        "show_timestamp": True
    }


def format_wandering_detection(resident_data: Dict, location: str, camera_id: str) -> Dict:
    """배회 감지 템플릿"""
    nickname = resident_data.get("nickname") or resident_data.get("user_name", "어르신")
    room_info = format_room_info(resident_data)
    
    lines = [
        f"위치: {location}",
        f"생활실: {room_info}",
        "안전을 위해 생활실로 복귀해주세요"
    ]
    
    return {
        "title": f"⚠️ {nickname} 어르신 발견",
        "lines": lines,
        "show_timestamp": True
    }


def format_visitor_guidance(resident_data: Dict, visitor_name: str, 
                           visitor_relationship: str, meeting_room: str) -> Dict:
    """면회객 안내 템플릿"""
    nickname = resident_data.get("nickname") or resident_data.get("user_name", "어르신")
    
    lines = [
        f"방문자: {visitor_name} ({visitor_relationship})",
        f"{nickname} 어르신 면회",
        f"{meeting_room}로 안내 중"
    ]
    
    return {
        "title": "면회객 안내",
        "lines": lines,
        "show_timestamp": True
    }

