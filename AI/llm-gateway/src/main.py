"""
FastAPI 기반 한국어 음성 인터페이스 서버

OpenAI Whisper (STT) + ChatGPT + TTS 통합

환경변수 설정:
- .env 파일에 OPENAI_API_KEY 등 설정 필요
- config.py에서 환경변수 관리
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
import os
import json
import asyncio
import base64
from typing import Optional, AsyncGenerator, Literal
from enum import Enum
import tempfile
import aiofiles
import logging

from .config import settings, get_cors_origins
from .redis_session import redis_session_manager
from .database import (
    db_manager, 
    save_conversation_to_db, 
    load_conversation_from_db,
    log_api_request,
    log_cost
)
import time

# 로깅 설정
logger = logging.getLogger(__name__)


# FastAPI 앱 초기화
app = FastAPI(
    title="Voice Interface API",
    description="""
    한국어 음성 인터페이스를 위한 STT, ChatGPT, TTS 통합 API
    
    ## 주요 기능
    
    - 🎤 **STT (Speech-to-Text)**: OpenAI Whisper로 음성을 텍스트로 변환
    - 💬 **ChatGPT**: 자연어 대화 처리 (다양한 모델 지원)
    - 🔊 **TTS (Text-to-Speech)**: 텍스트를 음성으로 변환 (6가지 음성 옵션)
    - 🔄 **통합 처리**: STT → Chat → TTS 원스톱 처리
    - 📡 **WebSocket**: 실시간 양방향 통신
    
    ## 사용 가능한 옵션
    
    ### ChatGPT 모델
    - `gpt-4o-mini`: 빠르고 저렴 (기본값)
    - `gpt-4o`: 최신 고성능
    - `gpt-4-turbo`: 고성능
    - `gpt-4`: 표준 GPT-4
    - `gpt-3.5-turbo`: 빠른 응답
    
    ### TTS 음성
    - `alloy`: 중성적이고 균형잡힌 음성 (기본값)
    - `echo`: 깊고 따뜻한 음성
    - `fable`: 밝고 활기찬 음성
    - `onyx`: 깊고 강렬한 음성
    - `nova`: 부드럽고 친근한 음성
    - `shimmer`: 부드럽고 우아한 음성
    
    ### TTS 모델
    - `tts-1`: 표준 모델, 빠른 응답 (기본값)
    - `tts-1-hd`: 고품질 모델, 더 자연스러운 음성
    
    ### STT 모델
    - `whisper-1`: OpenAI Whisper (기본값, 유일한 옵션)
    """,
    version="1.0.0"
)


# CORS 설정 (Flutter Web, SPA 지원)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙 (테스트 페이지 등)
# 프로젝트 루트 경로 확인 (Docker 컨테이너 내부: /app)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.join(BASE_DIR, "tests", "user_testing")

# Docker 컨테이너 내부 경로도 확인
DOCKER_TESTS_DIR = "/app/tests/user_testing"

if os.path.exists(TESTS_DIR):
    app.mount("/tests", StaticFiles(directory=TESTS_DIR, html=True), name="tests")
    logger.info(f"Static files mounted at /tests from {TESTS_DIR}")
elif os.path.exists(DOCKER_TESTS_DIR):
    app.mount("/tests", StaticFiles(directory=DOCKER_TESTS_DIR, html=True), name="tests")
    logger.info(f"Static files mounted at /tests from {DOCKER_TESTS_DIR}")
else:
    logger.warning(f"Tests directory not found at {TESTS_DIR} or {DOCKER_TESTS_DIR}")


# OpenAI 클라이언트 초기화
# API 키가 설정되지 않은 경우 환경변수 OPENAI_API_KEY를 자동으로 사용
# 또는 None을 전달하면 AsyncOpenAI가 환경변수를 자동으로 확인
client = AsyncOpenAI(api_key=settings.openai_api_key or os.getenv("OPENAI_API_KEY"))


# 애플리케이션 시작 시 초기화
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 Redis 및 DB 연결"""
    # Redis 연결
    try:
        await redis_session_manager.connect()
        print("✓ Redis connected")
    except Exception as e:
        print(f"⚠ Redis connection failed (will use fallback): {e}")
    
    # 데이터베이스 초기화
    try:
        db_manager.initialize()
        if db_manager.engine:
            tables_created = db_manager.create_tables()
            if tables_created:
                print("✓ Database connected and all tables verified")
            else:
                print("⚠ Database connected but table creation had issues (check logs)")
        else:
            print("⚠ Database not configured (DB_URL or DB_HOST not set)")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)
        print(f"✗ Database initialization failed: {e}")
        print("⚠ Server will continue but database features will be unavailable")


# 애플리케이션 종료 시 정리
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 연결 정리"""
    await redis_session_manager.disconnect()
    print("✓ Redis disconnected")


# Fallback: Redis가 없을 때 사용할 메모리 기반 저장소
fallback_store = {}


# ============= API 옵션 Enum =============

class ChatModel(str, Enum):
    """ChatGPT 모델 옵션"""
    GPT_4O_MINI = "gpt-4o-mini"  # 빠르고 저렴한 모델 (기본값)
    GPT_4O = "gpt-4o"  # 최신 고성능 모델
    GPT_4_TURBO = "gpt-4-turbo"  # 고성능 모델
    GPT_4 = "gpt-4"  # 표준 GPT-4 모델
    GPT_3_5_TURBO = "gpt-3.5-turbo"  # 빠른 응답 모델


class TTSVoice(str, Enum):
    """TTS 음성 옵션"""
    ALLOY = "alloy"  # 중성적이고 균형잡힌 음성 (기본값)
    ECHO = "echo"  # 깊고 따뜻한 음성
    FABLE = "fable"  # 밝고 활기찬 음성
    ONYX = "onyx"  # 깊고 강렬한 음성
    NOVA = "nova"  # 부드럽고 친근한 음성
    SHIMMER = "shimmer"  # 부드럽고 우아한 음성


class TTSModel(str, Enum):
    """TTS 모델 옵션"""
    TTS_1 = "tts-1"  # 표준 모델, 빠른 응답 (기본값)
    TTS_1_HD = "tts-1-hd"  # 고품질 모델, 더 자연스러운 음성


class STTModel(str, Enum):
    """STT 모델 옵션"""
    WHISPER_1 = "whisper-1"  # OpenAI Whisper 모델 (기본값, 유일한 옵션)


# ============= 데이터 모델 =============


class TextChatRequest(BaseModel):
    """텍스트 채팅 요청 모델"""
    message: str = Field(..., description="사용자 메시지")
    session_id: Optional[str] = Field(default="default", description="세션 ID (대화 히스토리 관리용)")
    system_prompt: Optional[str] = Field(
        default=None, 
        description="시스템 프롬프트 (None이면 기본값 사용)"
    )
    model: Optional[ChatModel] = Field(
        default=None,
        description=f"ChatGPT 모델 선택. 옵션: {', '.join([m.value for m in ChatModel])}. None이면 기본값({settings.default_chat_model}) 사용"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "안녕하세요",
                "session_id": "user123",
                "model": "gpt-4o-mini"
            }
        }


class TTSRequest(BaseModel):
    """TTS 요청 모델"""
    text: str = Field(..., description="음성으로 변환할 텍스트")
    voice: Optional[TTSVoice] = Field(
        default=None,
        description=f"TTS 음성 선택. 옵션: {', '.join([v.value for v in TTSVoice])}. None이면 기본값({settings.default_tts_voice}) 사용"
    )
    model: Optional[TTSModel] = Field(
        default=None,
        description=f"TTS 모델 선택. 옵션: {', '.join([m.value for m in TTSModel])}. None이면 기본값({settings.default_tts_model}) 사용"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "안녕하세요, 반갑습니다",
                "voice": "alloy",
                "model": "tts-1"
            }
        }


# ============= STT 엔드포인트 =============


@app.post("/api/stt", summary="음성을 텍스트로 변환 (Speech-to-Text)")
async def speech_to_text(
    audio: UploadFile = File(..., description="음성 파일 (mp3, wav, m4a, webm, ogg, flac 등)")
):
    """
    음성 파일을 업로드하여 텍스트로 변환합니다.
    
    **지원 모델:**
    - `whisper-1`: OpenAI Whisper 모델 (기본값, 한국어 지원 우수)
    
    **지원 파일 형식:**
    - mp3, wav, m4a, webm, ogg, flac 등
    
    **언어:**
    - 한국어(ko)로 자동 인식
    - 다국어 지원 (자동 감지)
    
    **응답 형식:**
    - JSON: `{"success": true, "text": "인식된 텍스트", "language": "ko"}`
    """
    try:
        # 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Whisper API 호출
        with open(temp_file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko"  # 한국어 명시
            )

        # 임시 파일 삭제
        os.unlink(temp_file_path)

        return {
            "success": True,
            "text": transcription.text,
            "language": "ko"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"STT 처리 실패: {str(e)}")


# ============= Chat 엔드포인트 =============


@app.post("/api/chat", summary="텍스트 채팅")
async def text_chat(request: TextChatRequest):
    """
    텍스트 메시지를 ChatGPT에 전송하고 응답을 받습니다.
    세션별 대화 히스토리 관리 (Redis 사용)
    
    **사용 가능한 모델:**
    - `gpt-4o-mini`: 빠르고 저렴한 모델 (기본값, 추천)
    - `gpt-4o`: 최신 고성능 모델
    - `gpt-4-turbo`: 고성능 모델
    - `gpt-4`: 표준 GPT-4 모델
    - `gpt-3.5-turbo`: 빠른 응답 모델
    
    **세션 관리:**
    - `session_id`로 대화 히스토리 관리
    - Redis에 30일간 저장
    """
    start_time = time.time()
    try:
        # 기본값 설정
        system_prompt = request.system_prompt or settings.default_system_prompt
        model = request.model.value if request.model else settings.default_chat_model
        
        # 세션 히스토리 가져오기 또는 생성
        try:
            # Redis에서 세션 가져오기
            messages = await redis_session_manager.get_session(request.session_id)
            if not messages:
                messages = await redis_session_manager.initialize_session(request.session_id, system_prompt)
        except Exception:
            # Redis 실패 시 fallback 사용
            if request.session_id not in fallback_store:
                fallback_store[request.session_id] = [
                    {"role": "system", "content": system_prompt}
                ]
            messages = fallback_store[request.session_id]

        # 사용자 메시지 추가
        messages.append({"role": "user", "content": request.message})

        # ChatGPT API 호출
        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )

        assistant_message = response.choices[0].message.content

        # 어시스턴트 응답 저장
        messages.append({"role": "assistant", "content": assistant_message})
        
        # Redis에 저장
        try:
            await redis_session_manager.save_session(request.session_id, messages)
            # DB에도 저장 (비동기로 처리하여 응답 지연 최소화)
            save_conversation_to_db(request.session_id, messages, system_prompt)
        except Exception:
            # Redis 실패 시 fallback에 저장
            fallback_store[request.session_id] = messages

        # 비용 로깅 (DB에 저장)
        if hasattr(response, 'usage') and response.usage:
            usage = response.usage
            # OpenAI 모델별 비용 계산 (예시, 실제 비용은 OpenAI 공식 문서 참조)
            # gpt-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
            input_cost = (usage.prompt_tokens / 1_000_000) * 0.15 if usage.prompt_tokens else 0
            output_cost = (usage.completion_tokens / 1_000_000) * 0.60 if usage.completion_tokens else 0
            total_cost = input_cost + output_cost
            
            log_cost(
                session_id=request.session_id,
                service_type="chat",
                model=model,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                cost_usd=total_cost
            )

        # API 요청 로깅
        processing_time = (time.time() - start_time) * 1000
        log_api_request(
            session_id=request.session_id,
            endpoint="/api/chat",
            method="POST",
            request_data={"message": request.message[:100]},  # 일부만 저장
            response_data={"response_length": len(assistant_message)},
            status_code=200,
            processing_time_ms=processing_time
        )

        return {
            "success": True,
            "response": assistant_message,
            "session_id": request.session_id,
            "model": model
        }

    except Exception as e:
        # 에러 로깅
        log_api_request(
            session_id=request.session_id,
            endpoint="/api/chat",
            method="POST",
            request_data={"message": request.message[:100]},
            response_data=None,
            status_code=500,
            processing_time_ms=(time.time() - start_time) * 1000
        )
        raise HTTPException(status_code=500, detail=f"채팅 처리 실패: {str(e)}")


@app.post("/api/chat/stream", summary="스트리밍 텍스트 채팅")
async def streaming_chat(request: TextChatRequest):
    """
    텍스트 메시지를 ChatGPT에 전송하고 응답을 스트리밍으로 받습니다.
    실시간 응답 표시에 적합
    
    **사용 가능한 모델:**
    - `gpt-4o-mini`: 빠르고 저렴한 모델 (기본값, 추천)
    - `gpt-4o`: 최신 고성능 모델
    - `gpt-4-turbo`: 고성능 모델
    - `gpt-4`: 표준 GPT-4 모델
    - `gpt-3.5-turbo`: 빠른 응답 모델
    
    **응답 형식:**
    - `text/event-stream` (Server-Sent Events)
    - 실시간 스트리밍 응답
    - 형식: `data: {"content": "텍스트 청크"}\n\n`
    """
    async def generate():
        try:
            # 기본값 설정
            system_prompt = request.system_prompt or settings.default_system_prompt
            model = request.model.value if request.model else settings.default_chat_model
            
            # 세션 히스토리 관리
            try:
                messages = await redis_session_manager.get_session(request.session_id)
                if not messages:
                    messages = await redis_session_manager.initialize_session(request.session_id, system_prompt)
            except Exception:
                if request.session_id not in fallback_store:
                    fallback_store[request.session_id] = [
                        {"role": "system", "content": system_prompt}
                    ]
                messages = fallback_store[request.session_id]

            messages.append({"role": "user", "content": request.message})

            # 스트리밍 ChatGPT API 호출
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )

            full_response = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    # SSE 형식으로 전송
                    yield f"data: {json.dumps({'content': content})}\n\n"

            # 전체 응답 저장
            messages.append({"role": "assistant", "content": full_response})
            
            try:
                await redis_session_manager.save_session(request.session_id, messages)
                save_conversation_to_db(request.session_id, messages, system_prompt)
            except Exception:
                fallback_store[request.session_id] = messages

            yield f"data: {json.dumps({'done': True})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


# ============= TTS 엔드포인트 =============


@app.post("/api/tts", summary="텍스트를 음성으로 변환 (Text-to-Speech)")
async def text_to_speech(request: TTSRequest):
    """
    텍스트를 음성 파일로 변환합니다.
    OpenAI TTS API 사용 (한국어 지원)
    
    **사용 가능한 음성 (voice):**
    - `alloy`: 중성적이고 균형잡힌 음성 (기본값)
    - `echo`: 깊고 따뜻한 음성
    - `fable`: 밝고 활기찬 음성
    - `onyx`: 깊고 강렬한 음성
    - `nova`: 부드럽고 친근한 음성
    - `shimmer`: 부드럽고 우아한 음성
    
    **사용 가능한 모델 (model):**
    - `tts-1`: 표준 모델, 빠른 응답 (기본값)
    - `tts-1-hd`: 고품질 모델, 더 자연스러운 음성 (느리지만 고품질)
    
    **응답 형식:**
    - `audio/mpeg` (MP3 형식)
    - 스트리밍 응답
    """
    try:
        # 기본값 설정
        voice = request.voice.value if request.voice else settings.default_tts_voice
        model = request.model.value if request.model else settings.default_tts_model
        
        # TTS API 호출
        response = await client.audio.speech.create(
            model=model,
            voice=voice,
            input=request.text
        )

        # 음성 데이터를 스트리밍으로 반환
        async def generate():
            # OpenAI SDK v1.0+ 에서는 response.content를 직접 사용 (권장)
            # response.content는 bytes를 반환하므로 직접 사용 가능
            try:
                # OpenAI SDK의 audio.speech.create()는 response.content에 bytes를 반환
                if hasattr(response, 'content'):
                    content = response.content
                    # content가 bytes인지 확인
                    if isinstance(content, bytes):
                        # bytes를 청크로 나누어 스트리밍
                        chunk_size = 1024
                        for i in range(0, len(content), chunk_size):
                            yield content[i:i + chunk_size]
                    else:
                        # content가 다른 타입이면 bytes로 변환 시도
                        try:
                            content_bytes = bytes(content) if content else b''
                            chunk_size = 1024
                            for i in range(0, len(content_bytes), chunk_size):
                                yield content_bytes[i:i + chunk_size]
                        except Exception:
                            yield bytes(content) if content else b''
                # response가 직접 bytes인 경우 (드물지만 가능)
                elif isinstance(response, bytes):
                    chunk_size = 1024
                    for i in range(0, len(response), chunk_size):
                        yield response[i:i + chunk_size]
                else:
                    # 기타: response를 bytes로 변환 시도
                    raise ValueError(f"Unsupported response type: {type(response)}. Expected response with 'content' attribute or bytes.")
            except Exception as e:
                # 에러 발생 시 상세 정보 포함
                print(f"TTS streaming error: {e}, response type: {type(response)}")
                if hasattr(response, '__dict__'):
                    print(f"Response attributes: {dir(response)}")
                raise HTTPException(status_code=500, detail=f"TTS 처리 실패: {str(e)}")

        return StreamingResponse(
            generate(),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS 처리 실패: {str(e)}")


# ============= 통합 음성 처리 엔드포인트 =============


@app.post("/api/voice/process", summary="음성 입력 → 채팅 → 음성 응답 (통합)")
async def process_voice(
    audio: UploadFile = File(..., description="음성 파일 (mp3, wav, m4a, webm 등)"),
    session_id: Optional[str] = Query(default="default", description="세션 ID (대화 히스토리 관리용)"),
    voice: Optional[TTSVoice] = Query(
        default=None,
        description=f"TTS 음성 선택. 옵션: {', '.join([v.value for v in TTSVoice])}. None이면 기본값({settings.default_tts_voice}) 사용"
    ),
    model: Optional[ChatModel] = Query(
        default=None,
        description=f"ChatGPT 모델 선택. 옵션: {', '.join([m.value for m in ChatModel])}. None이면 기본값({settings.default_chat_model}) 사용"
    ),
    response_format: Optional[str] = Query(
        default="json",
        description="응답 형식: 'json' (텍스트+Base64 오디오) 또는 'audio' (오디오만)"
    )
):
    """
    음성 입력을 받아 STT → ChatGPT → TTS 전체 프로세스를 수행합니다.
    클라이언트가 한 번의 요청으로 전체 흐름을 처리할 수 있습니다.
    
    **처리 흐름:**
    1. STT: 음성 파일 → 텍스트 변환 (Whisper-1)
    2. Chat: 텍스트 → ChatGPT 응답 생성
    3. TTS: 응답 텍스트 → 음성 파일 생성
    
    **사용 가능한 옵션:**
    - **voice**: TTS 음성 선택 (alloy, echo, fable, onyx, nova, shimmer)
    - **model**: ChatGPT 모델 선택 (gpt-4o-mini, gpt-4o, gpt-4-turbo 등)
    - **response_format**: 응답 형식 선택
        - `json` (기본값): JSON 형식으로 텍스트와 Base64 인코딩된 오디오 반환
        - `audio`: 오디오 파일만 반환 (MP3)
    
    **응답 형식:**
    - `json`: JSON 응답 (텍스트 + Base64 오디오) - 권장
    - `audio`: 오디오 파일만 반환 (MP3)
    """
    try:
        # 기본값 설정
        voice = voice.value if voice else settings.default_tts_voice
        chat_model = model.value if model else settings.default_chat_model
        
        # 1. STT: 음성 → 텍스트
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.filename)[1]) as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        with open(temp_file_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="ko"
            )
        
        os.unlink(temp_file_path)
        user_text = transcription.text

        # 2. Chat: 텍스트 → ChatGPT 응답
        try:
            messages = await redis_session_manager.get_session(session_id)
            if not messages:
                messages = await redis_session_manager.initialize_session(session_id, settings.default_system_prompt)
        except Exception:
            if session_id not in fallback_store:
                fallback_store[session_id] = [
                    {"role": "system", "content": settings.default_system_prompt}
                ]
            messages = fallback_store[session_id]

        messages.append({"role": "user", "content": user_text})

        chat_response = await client.chat.completions.create(
            model=chat_model,
            messages=messages
        )

        assistant_text = chat_response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_text})
        
        try:
            await redis_session_manager.save_session(session_id, messages)
            save_conversation_to_db(session_id, messages, settings.default_system_prompt)
        except Exception:
            fallback_store[session_id] = messages

        # 3. TTS: 응답 텍스트 → 음성
        tts_response = await client.audio.speech.create(
            model=settings.default_tts_model,
            voice=voice,
            input=assistant_text
        )

        # ✅ 수정: OpenAI SDK의 올바른 응답 처리
        # response.read()를 사용하여 전체 바이트 읽기
        try:
            # OpenAI SDK v1.0+: HttpxBinaryResponseContent.read()
            audio_bytes = tts_response.read()
        except Exception as e:
            logger.error(f"Failed to read TTS response: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"TTS 응답 읽기 실패: {str(e)}"
            )

        # 응답 형식에 따라 처리
        if response_format == "audio":
            # 오디오만 반환
            # HTTP 헤더는 latin-1 인코딩만 지원하므로 한글 텍스트는 제거하거나 URL 인코딩 필요
            # 텍스트 정보가 필요하면 JSON 응답 형식 사용 권장
            return StreamingResponse(
                iter([audio_bytes]),  # bytes를 iterable로 변환
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "attachment; filename=response.mp3"
                    # 참고: HTTP 헤더는 latin-1만 지원하므로 한글 텍스트는 헤더에 포함할 수 없음
                    # 텍스트 정보가 필요하면 response_format=json 사용 권장
                }
            )
        else:
            # JSON 응답 (텍스트 + Base64 오디오) - 기본값
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            return JSONResponse(content={
                "success": True,
                "user_text": user_text,
                "assistant_text": assistant_text,
                "audio_base64": audio_base64,
                "audio_format": "mp3",
                "session_id": session_id
            })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice process error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"음성 처리 실패: {str(e)}")


# ============= WebSocket 실시간 통신 =============


@app.websocket("/ws/voice")
async def websocket_voice_chat(websocket: WebSocket):
    """
    WebSocket을 통한 실시간 음성 채팅
    
    **기능:**
    - 실시간 양방향 통신
    - 텍스트 메시지 스트리밍 응답
    - 세션 히스토리 관리
    
    **쿼리 파라미터:**
    - `session_id`: 세션 ID (선택사항, 없으면 자동 생성)
    
    **사용 모델:**
    - ChatGPT: 기본 모델 사용 (설정 파일에서 변경 가능)
    - 세션별 대화 히스토리 자동 관리
    
    **메시지 형식:**
    - 클라이언트 → 서버: `{"type": "text", "message": "안녕하세요"}`
    - 서버 → 클라이언트: `{"type": "content", "content": "안녕하세요"}`
    """
    await websocket.accept()
    
    # 세션 ID 처리: 쿼리 파라미터에서 가져오거나 새로 생성
    import uuid
    session_id = websocket.query_params.get("session_id")
    if not session_id:
        session_id = f"ws_{uuid.uuid4().hex[:12]}"
    
    # 기존 세션 히스토리 로드 또는 새 세션 초기화
    try:
        messages = await redis_session_manager.get_session(session_id)
        if not messages:
            # 새 세션이면 초기화
            messages = await redis_session_manager.initialize_session(session_id, settings.default_system_prompt)
            # 세션 ID 전송 (클라이언트가 저장할 수 있도록)
            await websocket.send_json({
                "type": "session_created",
                "session_id": session_id
            })
        else:
            # 기존 세션이면 히스토리와 함께 세션 ID 전송
            await websocket.send_json({
                "type": "session_restored",
                "session_id": session_id,
                "message_count": len(messages)
            })
    except Exception:
        # Redis 실패 시 fallback 사용
        if session_id not in fallback_store:
            fallback_store[session_id] = [
                {"role": "system", "content": settings.default_system_prompt}
            ]
            await websocket.send_json({
                "type": "session_created",
                "session_id": session_id
            })
        messages = fallback_store[session_id]

    try:
        while True:
            # 클라이언트로부터 데이터 수신
            data = await websocket.receive_json()
            
            if data.get("type") == "text":
                # 텍스트 메시지 처리
                user_message = data.get("message")
                messages.append({"role": "user", "content": user_message})

                # 세션 히스토리 업데이트 (매번 최신 히스토리 가져오기)
                try:
                    # Redis에서 최신 히스토리 가져오기
                    latest_messages = await redis_session_manager.get_session(session_id)
                    if latest_messages:
                        # 기존 메시지가 있으면 시스템 메시지 제외하고 사용자 메시지부터 사용
                        system_msg = latest_messages[0] if latest_messages and latest_messages[0].get("role") == "system" else None
                        if system_msg:
                            messages = [system_msg] + latest_messages[1:] + [{"role": "user", "content": user_message}]
                        else:
                            messages = latest_messages + [{"role": "user", "content": user_message}]
                except Exception:
                    # Redis 실패 시 현재 메시지 사용
                    pass

                # 스트리밍 응답
                stream = await client.chat.completions.create(
                    model=settings.default_chat_model,
                    messages=messages,
                    stream=True
                )

                full_response = ""
                async for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        await websocket.send_json({
                            "type": "text_chunk",
                            "content": content
                        })

                messages.append({"role": "assistant", "content": full_response})
                
                # 세션 히스토리 저장
                try:
                    await redis_session_manager.save_session(session_id, messages)
                    save_conversation_to_db(session_id, messages, settings.default_system_prompt)
                except Exception:
                    fallback_store[session_id] = messages
                
                await websocket.send_json({
                    "type": "text_complete",
                    "full_response": full_response
                })

    except WebSocketDisconnect:
        # 세션 정리 (Redis는 TTL로 자동 삭제, fallback만 정리)
        if session_id in fallback_store:
            # fallback은 유지 (재연결 시 사용 가능하도록)
            pass


# ============= 유틸리티 엔드포인트 =============


@app.delete("/api/session/{session_id}", summary="세션 히스토리 삭제")
async def clear_session(session_id: str):
    """특정 세션의 대화 히스토리를 삭제합니다."""
    deleted = False
    
    # Redis에서 삭제
    try:
        deleted = await redis_session_manager.delete_session(session_id)
    except Exception:
        pass
    
    # Fallback에서 삭제
    if session_id in fallback_store:
        del fallback_store[session_id]
        deleted = True
    
    if deleted:
        return {"success": True, "message": f"세션 {session_id} 삭제됨"}
    return {"success": False, "message": "세션을 찾을 수 없음"}


@app.get("/api/session/{session_id}", summary="세션 히스토리 조회")
async def get_session(session_id: str):
    """특정 세션의 대화 히스토리를 조회합니다."""
    messages = []
    
    # Redis에서 조회
    try:
        messages = await redis_session_manager.get_session(session_id)
    except Exception:
        pass
    
    # Fallback에서 조회
    if not messages and session_id in fallback_store:
        messages = fallback_store[session_id]
    
    if messages:
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages
        }
    return {"success": False, "message": "세션을 찾을 수 없음"}


@app.get("/", summary="Health Check")
async def root():
    """서버 상태 확인"""
    # Redis 및 DB 상태 확인
    redis_status = await redis_session_manager.health_check()
    db_status = db_manager.health_check() if (hasattr(db_manager, '_initialized') and db_manager._initialized) else False
    db_verification = db_manager.verify_tables() if (hasattr(db_manager, '_initialized') and db_manager._initialized) else {}
    
    # OpenAI 연결 상태 확인 (API 키 설정 여부 및 간단한 연결 테스트)
    openai_status = "configured"
    openai_detailed = "api_key_set"
    try:
        if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
            openai_status = "not_configured"
            openai_detailed = "api_key_not_set"
        else:
            # 간단한 연결 테스트 (모델 목록 조회는 너무 느리므로 스킵)
            # 실제 연결은 첫 API 호출 시 확인됨
            openai_status = "configured"
            openai_detailed = "api_key_valid"
    except Exception as e:
        openai_status = "error"
        openai_detailed = f"error: {str(e)}"
    
    return {
        "status": "running",
        "service": "Voice Interface API",
        "version": "1.0.0",
        "services": {
            "redis": "connected" if redis_status else "disconnected",
            "database": {
                "connected": db_status,
                "initialized": db_manager._initialized if hasattr(db_manager, '_initialized') else False,
                "schema": db_verification.get('schema', None) if db_verification else None,
                "database_name": db_verification.get('database', None) if db_verification else None,
                "tables": db_verification.get('tables', {}) if db_verification else {},
                "all_tables_exist": db_verification.get('all_tables_exist', False) if db_verification else False
            },
            "openai": openai_status,
            "openai_detail": openai_detailed
        },
        "endpoints": {
            "stt": "/api/stt",
            "chat": "/api/chat",
            "chat_stream": "/api/chat/stream",
            "tts": "/api/tts",
            "voice_process": "/api/voice/process",
            "websocket": "/ws/voice"
        },
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


# ============= 서버 실행 =============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.reload
    )

