"""
심리 상담 분석 모듈

어르신의 대화 내용을 분석하여 심리, 정서, 건강 상태를 평가합니다.
GDS (Geriatric Depression Scale), GAI (Geriatric Anxiety Inventory) 등의 
평가 도구를 기반으로 분석합니다.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# 심리 상담 평가 지표
PSYCHOLOGICAL_INDICATORS = {
    "depression": {
        "name": "우울감",
        "keywords": ["슬프", "우울", "힘들", "의미없", "죽고 싶", "아무것도 하고 싶지 않", "피곤", "무기력"],
        "positive_keywords": ["기쁘", "행복", "즐거", "만족", "감사"]
    },
    "anxiety": {
        "name": "불안감",
        "keywords": ["걱정", "불안", "두려", "무서", "떨리", "초조", "불안정", "걱정되"],
        "positive_keywords": ["안심", "편안", "차분", "평온"]
    },
    "loneliness": {
        "name": "고립감",
        "keywords": ["외로", "혼자", "쓸쓸", "외톨이", "아무도 없", "만나고 싶", "보고 싶"],
        "positive_keywords": ["함께", "만나", "대화", "친구", "가족"]
    },
    "sleep": {
        "name": "수면 패턴",
        "keywords": ["잠 못", "불면", "잠 안", "밤에 깨", "잠이 안"],
        "positive_keywords": ["잠 잘", "편안히 잠", "잠 푹"]
    },
    "health": {
        "name": "건강 상태",
        "keywords": ["아프", "아픈", "병", "통증", "몸이 안", "힘들", "피곤"],
        "positive_keywords": ["건강", "좋아", "괜찮", "컨디션 좋"]
    }
}


def analyze_conversation_messages(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    대화 메시지를 분석하여 심리, 정서, 건강 상태를 평가합니다.
    
    Args:
        messages: 대화 메시지 리스트 (role, content 포함)
    
    Returns:
        분석 결과 딕셔너리
    """
    try:
        # 사용자 메시지만 추출
        user_messages = [msg["content"] for msg in messages if msg.get("role") == "user"]
        all_text = " ".join(user_messages).lower()
        
        analysis_results = {}
        
        for indicator_key, indicator in PSYCHOLOGICAL_INDICATORS.items():
            # 부정적 키워드 카운트
            negative_count = sum(1 for keyword in indicator["keywords"] if keyword in all_text)
            # 긍정적 키워드 카운트
            positive_count = sum(1 for keyword in indicator["positive_keywords"] if keyword in all_text)
            
            # 점수 계산 (0-100, 높을수록 우려)
            # 부정적 키워드 1개당 +20점, 긍정적 키워드 1개당 -10점
            score = min(100, max(0, (negative_count * 20) - (positive_count * 10)))
            
            # 등급 결정
            if score >= 60:
                grade = "warning"  # 경고
            elif score >= 40:
                grade = "concern"  # 우려
            elif score >= 20:
                grade = "normal"  # 보통
            elif score >= 10:
                grade = "good"  # 양호
            else:
                grade = "excellent"  # 우수
            
            analysis_results[indicator_key] = {
                "name": indicator["name"],
                "score": score,
                "grade": grade,
                "negative_keyword_count": negative_count,
                "positive_keyword_count": positive_count,
                "details": {
                    "negative_keywords_found": [kw for kw in indicator["keywords"] if kw in all_text],
                    "positive_keywords_found": [kw for kw in indicator["positive_keywords"] if kw in all_text]
                }
            }
        
        # 전체 평균 점수
        avg_score = sum(result["score"] for result in analysis_results.values()) / len(analysis_results)
        
        # 전체 등급
        if avg_score >= 50:
            overall_grade = "warning"
        elif avg_score >= 35:
            overall_grade = "concern"
        elif avg_score >= 20:
            overall_grade = "normal"
        elif avg_score >= 10:
            overall_grade = "good"
        else:
            overall_grade = "excellent"
        
        return {
            "overall_score": round(avg_score, 2),
            "overall_grade": overall_grade,
            "indicators": analysis_results,
            "analyzed_at": datetime.utcnow().isoformat(),
            "message_count": len(user_messages)
        }
    
    except Exception as e:
        logger.error(f"Error analyzing conversation messages: {e}", exc_info=True)
        return {
            "error": str(e),
            "overall_score": 0,
            "overall_grade": "unknown"
        }


def save_psychological_analysis(session_id: str, analysis_result: Dict[str, Any], db_manager) -> Optional[int]:
    """
    심리 상담 분석 결과를 DB에 저장합니다.
    
    Args:
        session_id: 세션 ID
        analysis_result: 분석 결과
        db_manager: 데이터베이스 관리자
    
    Returns:
        저장된 분석 ID (실패 시 None)
    """
    if not db_manager or not db_manager._initialized:
        logger.warning("Database not initialized, skipping psychological analysis save")
        return None
    
    try:
        from .database import PsychologicalCounselingAnalysis
        
        with db_manager.get_session() as session:
            # 각 지표별로 분석 결과 저장
            saved_ids = []
            
            if "indicators" in analysis_result:
                for indicator_key, indicator_data in analysis_result["indicators"].items():
                    analysis = PsychologicalCounselingAnalysis(
                        session_id=session_id,
                        analysis_type=indicator_key,  # depression, anxiety, loneliness, sleep, health
                        analysis_result=indicator_data,
                        score=indicator_data.get("score", 0),
                        grade=indicator_data.get("grade", "unknown")
                    )
                    session.add(analysis)
                    session.flush()
                    saved_ids.append(analysis.id)
            
            # 전체 분석 결과도 저장
            overall_analysis = PsychologicalCounselingAnalysis(
                session_id=session_id,
                analysis_type="overall",
                analysis_result=analysis_result,
                score=int(analysis_result.get("overall_score", 0)),
                grade=analysis_result.get("overall_grade", "unknown")
            )
            session.add(overall_analysis)
            session.commit()
            
            logger.info(f"Saved psychological analysis: session_id={session_id}, saved_count={len(saved_ids) + 1}")
            return overall_analysis.id
    
    except Exception as e:
        logger.error(f"Failed to save psychological analysis: {e}", exc_info=True)
        return None

