"""
System Prompt 빌더 모듈

모든 LLM API 호출에서 일관된 System Prompt를 생성합니다.
TOOLS 목록과 심리 상담 가이드라인을 포함합니다.
"""

from typing import Optional
from .config import settings
from .tools import TOOLS

logger = None

def get_logger():
    """로거 가져오기 (순환 참조 방지)"""
    global logger
    if logger is None:
        import logging
        logger = logging.getLogger(__name__)
    return logger


def build_system_prompt(base_prompt: Optional[str] = None) -> str:
    """
    통합 System Prompt 생성
    
    Args:
        base_prompt: 기본 프롬프트 (None이면 settings.default_system_prompt 사용)
    
    Returns:
        Function Calling 안내와 심리 상담 가이드라인이 포함된 System Prompt
    """
    base = base_prompt or settings.default_system_prompt
    
    # TOOLS 목록 생성
    tools_description = []
    if TOOLS and len(TOOLS) > 0:
        for i, tool in enumerate(TOOLS, 1):
            func_info = tool.get("function", {})
            func_name = func_info.get("name", "unknown")
            func_desc = func_info.get("description", "")
            tools_description.append(f"{i}. {func_name}: {func_desc}")
    else:
        tools_description.append("현재 사용 가능한 함수가 없습니다.")
    
    system_prompt = f"""{base}

중요: 사용자가 데이터 조회나 API 호출을 요청하면 반드시 제공된 함수를 사용해야 합니다. 일반적인 응답으로 대체하지 마세요.

사용 가능한 함수:
{chr(10).join(tools_description)}

규칙:
- 사용자가 데이터 조회를 요청하면 반드시 해당 함수를 호출하세요
- 함수를 사용할 수 있는 경우 일반적인 응답으로 대체하지 마세요
- 함수 호출 결과를 받은 후 사용자에게 명확하게 전달하세요

심리 상담 가이드라인 (어르신 대상):
- 인지행동치료(CBT) 원칙: 부정적 사고 패턴을 인식하고 긍정적으로 전환하도록 돕습니다
- 공감적 경청: 어르신의 감정을 깊이 이해하고 공감하며, 판단하지 않습니다
- 긍정 심리학: 강점과 긍정적 경험에 초점을 맞춰 정서적 웰빙을 향상시킵니다
- 감정 표현 촉진: 어르신이 자신의 감정을 자유롭게 표현할 수 있도록 안전한 환경을 제공합니다
- 우울/불안/고립감 지표 모니터링: 대화 중 우울, 불안, 고립감의 징후를 주의 깊게 관찰하고 적절히 대응합니다
- 건강 상태 관심: 신체적 건강과 수면 패턴에 대한 관심을 표현하고 필요시 전문가 상담을 권장합니다"""
    
    return system_prompt


def get_tools_for_api() -> list:
    """
    API 호출용 TOOLS 목록 반환
    
    Returns:
        TOOLS 리스트 (비어있을 수 있음)
    """
    return TOOLS if TOOLS else []

