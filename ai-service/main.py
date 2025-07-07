#!/usr/bin/env python3
"""
VIBA AI 마이크로서비스
====================

AI 에이전트 전용 FastAPI 마이크로서비스
- 포트: 8000
- 역할: AI 에이전트, NLP 처리, 파일 분석

@version 1.0
@author VIBA AI Team
@date 2025.07.07
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
import asyncio
import time
import logging
from datetime import datetime, timedelta
import jwt
import hashlib
import os
import json
import sys

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
nlp_engine_dir = os.path.join(parent_dir, 'nlp-engine')
sys.path.insert(0, nlp_engine_dir)

# AI 에이전트 관련 임포트
try:
    from ai_agents import ai_manager
    AI_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"AI 에이전트 임포트 오류: {e}")
    AI_AGENTS_AVAILABLE = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="VIBA AI 마이크로서비스",
    description="AI 에이전트 전용 마이크로서비스",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React 개발 서버
        "http://localhost:5000",  # Node.js 메인 서버
        "http://localhost:5173",  # Vite 개발 서버
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 애플리케이션 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행되는 이벤트"""
    logger.info("🚀 VIBA AI 마이크로서비스 시작 중...")
    
    if AI_AGENTS_AVAILABLE:
        logger.info("✅ AI 에이전트 시스템 로드 완료")
        logger.info(f"📊 등록된 에이전트: {len(ai_manager.agents)}개")
        
        # 주기적 세션 정리 작업 시작
        asyncio.create_task(periodic_cleanup())
        logger.info("🧹 주기적 세션 정리 작업 시작")
    else:
        logger.warning("⚠️ AI 에이전트 시스템을 로드할 수 없습니다. 기본 모드로 실행됩니다.")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행되는 이벤트"""
    logger.info("🛑 VIBA AI 마이크로서비스 종료 중...")
    
    if AI_AGENTS_AVAILABLE:
        # 마지막 세션 정리
        ai_manager.cleanup_expired_sessions()
        logger.info("🧹 최종 세션 정리 완료")

# 주기적 세션 정리 작업
async def periodic_cleanup():
    """주기적으로 만료된 세션 정리"""
    while True:
        try:
            await asyncio.sleep(3600)  # 1시간마다 실행
            if AI_AGENTS_AVAILABLE:
                ai_manager.cleanup_expired_sessions()
                logger.info("🧹 주기적 세션 정리 실행 완료")
        except Exception as e:
            logger.error(f"주기적 세션 정리 실패: {e}")

# 건강 상태 확인 엔드포인트
@app.get("/health")
async def health_check():
    """AI 마이크로서비스 상태 확인"""
    return {
        "status": "OK",
        "service": "VIBA AI 마이크로서비스",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "uptime": time.time()
    }

# 서비스 정보 엔드포인트
@app.get("/")
async def root():
    """서비스 정보"""
    return {
        "service": "VIBA AI 마이크로서비스",
        "description": "AI 에이전트, NLP 처리, 파일 분석 전용 서비스",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# 라우터 등록 (시도)
try:
    # app.include_router(auth_router, prefix="/api")
    # app.include_router(ai_router, prefix="/api")
    # app.include_router(file_router, prefix="/api")
    logger.info("기본 AI 엔드포인트를 사용합니다.")
except Exception as e:
    logger.warning(f"라우터 등록 실패: {e}")
    logger.warning("기본 AI 엔드포인트만 제공됩니다.")

# Pydantic 모델 정의
class ChatRequest(BaseModel):
    message: str = Field(..., description="사용자 메시지")
    agent_id: str = Field(..., description="AI 에이전트 ID")
    session_id: Optional[str] = Field(None, description="세션 ID (선택사항)")
    user_id: Optional[str] = Field(None, description="사용자 ID (선택사항)")

class SessionRequest(BaseModel):
    agent_id: str = Field(..., description="AI 에이전트 ID")
    user_id: Optional[str] = Field(None, description="사용자 ID (선택사항)")

# AI 에이전트 엔드포인트
@app.get("/api/agents")
async def get_ai_agents():
    """AI 에이전트 목록 조회"""
    if AI_AGENTS_AVAILABLE:
        try:
            agents = ai_manager.list_agents()
            return {
                "success": True,
                "agents": agents,
                "total": len(agents)
            }
        except Exception as e:
            logger.error(f"AI 에이전트 목록 조회 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "agents": []
            }
    else:
        # Fallback 에이전트 목록
        return {
            "success": True,
            "agents": [
                {
                    "id": "materials_specialist",
                    "name": "재료 전문가 AI",
                    "description": "건축 재료 선택과 친환경 솔루션을 제안하는 전문 AI입니다.",
                    "specialty": "재료 공학",
                    "experience": "10,000+ 프로젝트 경험",
                    "capabilities": ["친환경 재료 추천", "비용 최적화", "성능 분석"]
                },
                {
                    "id": "design_theorist",
                    "name": "설계 이론가 AI",
                    "description": "건축 설계 이론과 공간 구성을 전문으로 하는 AI입니다.",
                    "specialty": "설계 이론",
                    "experience": "5,000+ 설계 분석",
                    "capabilities": ["공간 설계", "비례 시스템", "동선 계획"]
                },
                {
                    "id": "bim_specialist",
                    "name": "BIM 전문가 AI",
                    "description": "BIM 모델링과 3D 설계를 담당하는 전문 AI입니다.",
                    "specialty": "BIM 모델링",
                    "experience": "2,000+ BIM 모델",
                    "capabilities": ["3D 모델링", "IFC 변환", "충돌 검사"]
                },
                {
                    "id": "structural_engineer",
                    "name": "구조 엔지니어 AI",
                    "description": "구조 계산과 안전성 검토를 수행하는 AI입니다.",
                    "specialty": "구조 공학",
                    "experience": "15,000+ 구조 해석",
                    "capabilities": ["구조 계산", "안전성 검토", "내진 설계"]
                }
            ],
            "total": 4
        }

@app.post("/api/sessions")
async def create_session(request: SessionRequest):
    """새로운 채팅 세션 생성"""
    if not AI_AGENTS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI 에이전트 서비스가 현재 사용할 수 없습니다."
        )
    
    try:
        session_id = ai_manager.create_session(
            agent_id=request.agent_id,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "session_id": session_id,
            "agent_id": request.agent_id,
            "created_at": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"세션 생성 실패: {e}")
        raise HTTPException(status_code=500, detail="세션 생성 중 오류가 발생했습니다.")

@app.post("/api/chat")
async def ai_chat(request: ChatRequest):
    """AI 에이전트와 채팅"""
    if not AI_AGENTS_AVAILABLE:
        return {
            "success": False,
            "error": "AI 에이전트 서비스가 현재 사용할 수 없습니다.",
            "response": "죄송합니다. AI 서비스가 일시적으로 사용할 수 없습니다.",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # 세션 ID가 없으면 새로 생성
        session_id = request.session_id
        if not session_id:
            session_id = ai_manager.create_session(
                agent_id=request.agent_id,
                user_id=request.user_id
            )
        
        # AI 에이전트와 채팅
        response = await ai_manager.chat(
            session_id=session_id,
            message=request.message,
            user_id=request.user_id
        )
        
        return {
            "success": True,
            "session_id": session_id,
            **response
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"AI 채팅 실패: {e}")
        
        # 폴백 응답
        return {
            "success": False,
            "error": str(e),
            "response": "죄송합니다. 현재 AI 서비스에 문제가 발생했습니다.",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str):
    """세션 정보 조회"""
    if not AI_AGENTS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI 에이전트 서비스가 현재 사용할 수 없습니다."
        )
    
    try:
        session = ai_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        return {
            "success": True,
            "session": {
                "session_id": session.session_id,
                "agent_id": session.agent_id,
                "user_id": session.user_id,
                "message_count": len(session.messages),
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "expires_at": session.expires_at.isoformat()
            }
        }
    except Exception as e:
        logger.error(f"세션 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="세션 조회 중 오류가 발생했습니다.")

@app.get("/api/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, limit: int = 50):
    """세션 메시지 기록 조회"""
    if not AI_AGENTS_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="AI 에이전트 서비스가 현재 사용할 수 없습니다."
        )
    
    try:
        session = ai_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
        
        # 최근 메시지만 반환
        messages = session.messages[-limit:] if limit > 0 else session.messages
        
        return {
            "success": True,
            "session_id": session_id,
            "messages": messages,
            "total": len(session.messages)
        }
    except Exception as e:
        logger.error(f"메시지 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="메시지 조회 중 오류가 발생했습니다.")

@app.get("/api/stats")
async def get_service_stats():
    """서비스 통계 조회"""
    if not AI_AGENTS_AVAILABLE:
        return {
            "success": False,
            "error": "AI 에이전트 서비스가 현재 사용할 수 없습니다.",
            "stats": {}
        }
    
    try:
        stats = ai_manager.get_session_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"통계 조회 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "stats": {}
        }

# 백그라운드 작업 - 만료된 세션 정리
@app.post("/api/cleanup")
async def cleanup_expired_sessions(background_tasks: BackgroundTasks):
    """만료된 세션 정리 (백그라운드 작업)"""
    if not AI_AGENTS_AVAILABLE:
        return {"success": False, "message": "AI 에이전트 서비스가 사용할 수 없습니다."}
    
    try:
        def cleanup_task():
            ai_manager.cleanup_expired_sessions()
            logger.info("만료된 세션 정리 작업 완료")
        
        background_tasks.add_task(cleanup_task)
        return {"success": True, "message": "세션 정리 작업이 시작되었습니다."}
    except Exception as e:
        logger.error(f"세션 정리 작업 실패: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/analyze")
async def ai_analyze(request: dict):
    """AI 분석 엔드포인트"""
    return {
        "success": True,
        "message": "AI 분석 서비스가 준비 중입니다.",
        "analysis": {
            "type": "기본 분석",
            "result": "분석 결과가 여기에 표시됩니다."
        },
        "timestamp": datetime.now().isoformat()
    }

# 전역 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"예외 발생: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "내부 서버 오류",
            "error": str(exc)
        }
    )

if __name__ == "__main__":
    port = int(os.getenv("AI_SERVICE_PORT", 8000))
    
    logger.info(f"🤖 VIBA AI 마이크로서비스 시작")
    logger.info(f"📊 포트: {port}")
    logger.info(f"📖 API 문서: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )