"""
FastAPI 메인 애플리케이션
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import markdown

from .config import settings
from .models import (
    DetectionRequest, DetectionResponse, HealthResponse,
    ScenarioTemplateRequest, TemplateResponse, LCDDisplayData,
    EmotionRequest, EmotionResponse, ClearDisplayResponse
)
from .iot_data_client import IoTDataClient
from .ros2_client import ROS2Client, EmotionClient
from .resident_info_formatter import (
    format_display_data, format_room_info, format_morning_greeting, format_meal_assistance,
    format_conversation, format_wandering_detection, format_visitor_guidance
)

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="ROS2 API Server",
    description="""
    ROS2 및 LCD 제어를 위한 FastAPI 서버
    
    ## 주요 기능
    
    - 🔍 **어르신 탐지**: DL 컴포넌트가 어르신을 탐지했을 때 LCD에 정보 표시
    - 📋 **시나리오 템플릿**: 다양한 상황에 맞는 LCD 표시 템플릿 제공
    - 🏥 **어르신 정보 조회**: iot-data-server를 통한 어르신 정보 조회
    - 🖥️ **LCD 제어**: ROS2 서비스를 통한 로봇 LCD 제어
    
    ## 시나리오 템플릿
    
    - **morning_greeting**: 아침인사
    - **meal_assistance**: 식사 지원
    - **conversation**: 맞춤형 이동식 대화
    - **wandering_detection**: 배회 감지
    - **visitor_guidance**: 면회객 안내
    
    ## 문서 링크
    
    - [시나리오 템플릿 테스트 샘플 가이드](http://localhost:8004/docs-files/SCENARIO_TEMPLATE_TEST_SAMPLES.md)
    - [배회 감지 시나리오 샘플](http://localhost:8004/docs-files/WANDERING_DETECTION_SAMPLES.md)
    - [맞춤형 이동식 대화 시나리오 샘플](http://localhost:8004/docs-files/CONVERSATION_SAMPLES.md)
    
    **참고**: 문서 파일은 `/docs-files/` 경로에서 접근할 수 있습니다.  
    링크를 클릭하면 새 탭에서 문서가 열립니다.
    """,
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (문서 파일)
# __file__은 src/main.py이므로 parent.parent는 api-server 디렉토리
docs_dir = Path(__file__).parent.parent / "docs"
docs_dir_resolved = docs_dir.resolve()  # 절대 경로로 변환

# 마크다운 파일을 HTML로 렌더링하는 엔드포인트
@app.get("/docs-files/{filename:path}", response_class=HTMLResponse)
async def serve_markdown_file(filename: str):
    """
    마크다운 파일을 HTML로 렌더링하여 제공
    
    예시:
    - /docs-files/SCENARIO_TEMPLATE_TEST_SAMPLES.md
    - /docs-files/WANDERING_DETECTION_SAMPLES.md
    """
    if not docs_dir_resolved.exists():
        raise HTTPException(status_code=404, detail="docs 디렉토리를 찾을 수 없습니다")
    
    # 파일 경로 보안 검사 (경로 탐색 공격 방지)
    file_path = docs_dir_resolved / filename
    try:
        file_path = file_path.resolve()
        if not str(file_path).startswith(str(docs_dir_resolved.resolve())):
            raise HTTPException(status_code=403, detail="접근이 거부되었습니다")
    except Exception:
        raise HTTPException(status_code=403, detail="잘못된 파일 경로입니다")
    
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {filename}")
    
    # 마크다운 파일 읽기
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
    except Exception as e:
        logger.error(f"파일 읽기 실패: {e}")
        raise HTTPException(status_code=500, detail=f"파일을 읽을 수 없습니다: {str(e)}")
    
    # 마크다운을 HTML로 변환
    try:
        html_content = markdown.markdown(
            markdown_content,
            extensions=['extra', 'codehilite', 'tables', 'fenced_code']
        )
    except Exception as e:
        logger.warning(f"마크다운 확장 로드 실패 (기본 변환 사용): {e}")
        # 확장 없이 기본 변환
        html_content = markdown.markdown(markdown_content)
    
    # HTML 템플릿에 삽입
    html_template = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{filename} - ROS2 API Server 문서</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                padding: 40px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: #333;
                margin-top: 24px;
                margin-bottom: 16px;
            }}
            h1 {{
                border-bottom: 2px solid #eaecef;
                padding-bottom: 10px;
            }}
            code {{
                background-color: #f6f8fa;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
            }}
            pre {{
                background-color: #f6f8fa;
                padding: 16px;
                border-radius: 6px;
                overflow-x: auto;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
            blockquote {{
                border-left: 4px solid #dfe2e5;
                padding-left: 16px;
                margin-left: 0;
                color: #6a737d;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 16px 0;
            }}
            th, td {{
                border: 1px solid #dfe2e5;
                padding: 8px 12px;
                text-align: left;
            }}
            th {{
                background-color: #f6f8fa;
                font-weight: 600;
            }}
            a {{
                color: #0366d6;
                text-decoration: none;
            }}
            a:hover {{
                text-decoration: underline;
            }}
            .back-link {{
                display: inline-block;
                margin-bottom: 20px;
                color: #0366d6;
                text-decoration: none;
            }}
            .back-link:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <a href="/docs" class="back-link">← API 문서로 돌아가기</a>
            {html_content}
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_template)

if docs_dir_resolved.exists():
    logger.info(f"마크다운 문서 서빙 활성화: /docs-files/ -> {docs_dir_resolved}")
else:
    logger.warning(f"docs 디렉토리를 찾을 수 없습니다: {docs_dir_resolved}")

# 전역 클라이언트 인스턴스
iot_data_client: Optional[IoTDataClient] = None
ros2_client: Optional[ROS2Client] = None
emotion_client: Optional[EmotionClient] = None


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 초기화"""
    global iot_data_client, ros2_client, emotion_client
    
    logger.info("ROS2 API Server 시작 중...")
    
    # ROS2 도메인 ID 설정 (환경 변수에서 읽어옴)
    import os
    ros2_domain_id = os.getenv("ROS_DOMAIN_ID", str(settings.ROS2_DOMAIN_ID))
    os.environ["ROS_DOMAIN_ID"] = ros2_domain_id
    logger.info(f"ROS2 도메인 ID: {ros2_domain_id}")
    
    # iot-data-server 클라이언트 초기화
    iot_data_client = IoTDataClient(settings.IOT_DATA_SERVER_URL)
    
    # ROS2 클라이언트 초기화
    try:
        ros2_client = ROS2Client(
            namespace=settings.ROS2_NAMESPACE,
            service_name=settings.ROS2_SERVICE_NAME
        )
        logger.info("ROS2 클라이언트 초기화 완료")
    except Exception as e:
        logger.warning(f"ROS2 클라이언트 초기화 실패 (모킹 모드로 동작): {e}")
        ros2_client = None
    
    # 감정 표현 클라이언트 초기화
    try:
        emotion_client = EmotionClient(
            namespace=settings.ROS2_NAMESPACE,
            service_name=settings.ROS2_EMOTION_SERVICE_NAME
        )
        logger.info("감정 표현 클라이언트 초기화 완료")
    except Exception as e:
        logger.warning(f"감정 표현 클라이언트 초기화 실패 (모킹 모드로 동작): {e}")
        emotion_client = None
    
    logger.info("ROS2 API Server 시작 완료")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 정리"""
    global ros2_client, emotion_client
    
    if ros2_client:
        ros2_client.shutdown()
        logger.info("ROS2 클라이언트 종료 완료")
    
    if emotion_client:
        emotion_client.shutdown()
        logger.info("감정 표현 클라이언트 종료 완료")


@app.get("/", response_model=dict)
async def root():
    """루트 엔드포인트"""
    return {
        "message": "ROS2 API Server",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스 체크"""
    services = {
        "ros2": ros2_client.health_check() if ros2_client else False,
        "emotion": emotion_client.health_check() if emotion_client else False,
        "iot_data_server": await iot_data_client.health_check() if iot_data_client else False,
    }
    
    status = "healthy" if all(services.values()) else "degraded"
    
    return HealthResponse(
        status=status,
        services=services,
        timestamp=datetime.now()
    )


@app.post("/api/detection/resident", response_model=DetectionResponse)
async def detect_resident(request: DetectionRequest):
    """
    어르신 탐지 및 LCD 표시
    
    DL 컴포넌트가 어르신을 탐지했을 때 호출하는 엔드포인트입니다.
    어르신 정보를 조회하고 LCD에 표시합니다.
    """
    try:
        # 어르신 정보 조회
        resident_data = await iot_data_client.get_resident_info(
            user_id=request.user_id,
            nickname=request.nickname
        )
        
        # LCD 표시 데이터 포맷팅
        display_data = format_display_data(resident_data, request.display_format)
        
        # ROS2 서비스를 통해 LCD에 표시
        success = ros2_client.display_resident_info(
            title=display_data["title"],
            lines=display_data["lines"],
            show_timestamp=display_data["show_timestamp"],
            timeout=settings.ROS2_SERVICE_TIMEOUT
        ) if ros2_client else False
        
        if not success:
            logger.warning("LCD 표시 실패 (ROS2 서비스 사용 불가)")
        
        return DetectionResponse(
            success=True,
            message="Resident information displayed on LCD",
            data={
                "user_id": resident_data.get("user_id"),
                "name": resident_data.get("user_name"),
                "nickname": resident_data.get("nickname"),
                "room": format_room_info(resident_data),
                "display_sent": success,
                "lcd_display_data": display_data
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"어르신 탐지 처리 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/templates/scenario", response_model=TemplateResponse)
async def get_scenario_template(request: ScenarioTemplateRequest):
    """
    시나리오별 템플릿 생성 및 LCD 표시
    
    다양한 상황에 맞는 LCD 표시 템플릿을 생성하고 표시합니다.
    
    ## 시나리오 타입
    
    - **morning_greeting**: 아침인사
      - additional_data: `{"weather": "맑은"}` (선택적)
    
    - **meal_assistance**: 식사 지원
      - additional_data: `{"menu": "된장찌개", "meal_time": "12:00"}`
    
    - **conversation**: 맞춤형 이동식 대화
      - additional_data: `{"topic": "오늘 날씨 이야기", "destination": "3층 302호 생활실"}`
    
    - **wandering_detection**: 배회 감지
      - additional_data: `{"location": "1층 복도", "camera_id": "camera_001"}`
    
    - **visitor_guidance**: 면회객 안내
      - additional_data: `{"visitor_name": "정기우", "visitor_relationship": "아들", "meeting_room": "면회실"}`
    
    ## 테스트 샘플
    
    아래 샘플들을 바로 사용하여 테스트할 수 있습니다:
    
    ### 1. 아침인사
    ```json
    {
      "scenario": "morning_greeting",
      "nickname": "Zenitsu Agatsuma",
      "additional_data": {
        "weather": "맑은"
      }
    }
    ```
    
    ### 2. 식사 지원
    ```json
    {
      "scenario": "meal_assistance",
      "nickname": "Zenitsu Agatsuma",
      "additional_data": {
        "menu": "된장찌개",
        "meal_time": "12:00"
      }
    }
    ```
    
    ### 3. 면회객 안내
    ```json
    {
      "scenario": "visitor_guidance",
      "nickname": "Zenitsu Agatsuma",
      "additional_data": {
        "visitor_name": "정기우",
        "visitor_relationship": "아들",
        "meeting_room": "면회실"
      }
    }
    ```
    
    ### 4. 배회 감지
    ```json
    {
      "scenario": "wandering_detection",
      "nickname": "Zenitsu Agatsuma",
      "additional_data": {
        "location": "1층 복도",
        "camera_id": "camera_001"
      }
    }
    ```
    
    ### 5. 맞춤형 이동식 대화
    ```json
    {
      "scenario": "conversation",
      "user_id": "00000000-0000-0000-0000-000000000001",
      "additional_data": {
        "topic": "건강 이야기",
        "destination": "2층 복도"
      }
    }
    ```
    
    ## 상세 문서
    
    더 많은 샘플과 설명은 다음 문서를 참고하세요:
    
    - [시나리오 템플릿 테스트 샘플 가이드](http://localhost:8004/docs-files/SCENARIO_TEMPLATE_TEST_SAMPLES.md)
    - [배회 감지 시나리오 샘플](http://localhost:8004/docs-files/WANDERING_DETECTION_SAMPLES.md)
    - [맞춤형 이동식 대화 시나리오 샘플](http://localhost:8004/docs-files/CONVERSATION_SAMPLES.md)
    
    **참고**: 문서 파일은 `/docs-files/` 경로에서 접근할 수 있습니다.  
    링크를 클릭하면 새 탭에서 문서가 열립니다.
    """
    try:
        # 어르신 정보 조회
        resident_data = await iot_data_client.get_resident_info(
            user_id=request.user_id,
            nickname=request.nickname
        )
        
        additional_data = request.additional_data or {}
        
        # 시나리오별 템플릿 생성
        if request.scenario == "morning_greeting":
            template_data = format_morning_greeting(
                resident_data,
                weather=additional_data.get("weather")
            )
            description = "아침인사 템플릿: 친근한 인사와 함께 오늘의 날짜, 날씨 등 기본 정보 제공"
            
        elif request.scenario == "meal_assistance":
            template_data = format_meal_assistance(
                resident_data,
                menu=additional_data.get("menu", "식사"),
                meal_time=additional_data.get("meal_time", "식사 시간")
            )
            description = "식사 지원 템플릿: 식사 메뉴, 식사 시간, 식이 제한사항 안내"
            
        elif request.scenario == "conversation":
            template_data = format_conversation(
                resident_data,
                topic=additional_data.get("topic", "대화 중"),
                destination=additional_data.get("destination", "이동 중")
            )
            description = "맞춤형 이동식 대화 템플릿: 현재 대화 주제, 이동 목적지, 안전 주의사항 표시"
            
        elif request.scenario == "wandering_detection":
            template_data = format_wandering_detection(
                resident_data,
                location=additional_data.get("location", "알 수 없음"),
                camera_id=additional_data.get("camera_id", "")
            )
            description = "배회 감지 템플릿: 어르신 정보, 현재 위치, 생활실 복귀 안내"
            
        elif request.scenario == "visitor_guidance":
            template_data = format_visitor_guidance(
                resident_data,
                visitor_name=additional_data.get("visitor_name", "방문자"),
                visitor_relationship=additional_data.get("visitor_relationship", ""),
                meeting_room=additional_data.get("meeting_room", "면회실")
            )
            description = "면회객 안내 템플릿: 면회객 정보, 면회 장소, 안내 메시지"
            
        else:
            raise HTTPException(status_code=400, detail=f"알 수 없는 시나리오: {request.scenario}")
        
        # LCD에 표시
        success = ros2_client.display_resident_info(
            title=template_data["title"],
            lines=template_data["lines"],
            show_timestamp=template_data["show_timestamp"],
            timeout=settings.ROS2_SERVICE_TIMEOUT
        ) if ros2_client else False
        
        return TemplateResponse(
            success=success,
            template=LCDDisplayData(**template_data),
            scenario=request.scenario,
            description=description
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"템플릿 생성 중 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/lcd/status", response_model=dict)
async def get_lcd_status():
    """현재 LCD 표시 상태 조회 (향후 구현)"""
    return {
        "message": "LCD 상태 조회 기능은 향후 구현 예정입니다",
        "current_display": None
    }


@app.post("/api/emotion/set", response_model=EmotionResponse)
async def set_emotion(request: EmotionRequest):
    """
    감정 표현 설정
    
    로봇의 감정 표현을 설정합니다. 지원하는 감정 타입:
    - hello: 인사
    - basic: 기본 상태
    - angry: 화남
    - bored: 지루함
    - fun: 재미있음
    - happy: 행복함
    - interest: 관심
    - sad: 슬픔
    """
    try:
        if not emotion_client:
            raise HTTPException(
                status_code=503,
                detail="감정 표현 서비스가 사용 불가능합니다"
            )
        
        # 감정 표현 설정
        success, message = emotion_client.set_emotion(
            emotion=request.emotion,
            timeout=settings.ROS2_EMOTION_SERVICE_TIMEOUT
        )
        
        if success:
            return EmotionResponse(
                success=True,
                message=message,
                emotion=request.emotion
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"감정 표현 설정 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/lcd/clear", response_model=ClearDisplayResponse)
async def clear_lcd_display():
    """
    LCD 화면 지우기
    
    LCD 화면을 검은 화면으로 초기화합니다.
    모든 표시 내용을 지우고 빈 화면으로 만듭니다.
    """
    try:
        if not ros2_client:
            raise HTTPException(
                status_code=503,
                detail="ROS2 서비스가 사용 불가능합니다"
            )
        
        # LCD 화면 지우기
        success, message = ros2_client.clear_display(
            timeout=settings.ROS2_SERVICE_TIMEOUT
        )
        
        if success:
            return ClearDisplayResponse(
                success=True,
                message=message
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"LCD 화면 지우기 중 오류: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# 에러 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """전역 예외 핸들러"""
    logger.error(f"예외 발생: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG
    )

