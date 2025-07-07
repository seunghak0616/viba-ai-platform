from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import json
import logging

from .ai_agent_service import ai_service, AgentType, AnalysisType
from .websocket_manager import manager, websocket_handler
from .auth import get_current_user

logger = logging.getLogger(__name__)
security = HTTPBearer()

# API 라우터 생성
router = APIRouter(prefix="/api/ai", tags=["AI Agents"])

# Request/Response 모델들
class ChatSessionRequest(BaseModel):
    agent_id: AgentType
    context: Optional[Dict[str, Any]] = None

class ChatMessageRequest(BaseModel):
    session_id: str
    message: str

class AnalysisRequest(BaseModel):
    request_type: AnalysisType
    content: str
    building_type: str
    location: str
    area: float
    floors: int
    budget: float
    sustainability: str = "medium"
    style: str = "modern"
    special_requirements: List[str] = []

class AgentResponse(BaseModel):
    session_id: str
    agent_id: str
    agent_name: str
    response: str
    response_time: float
    timestamp: str
    confidence: float = 0.95

class AnalysisResponse(BaseModel):
    analysis_id: str
    status: str
    results: Dict[str, Any]
    overall_score: float
    processing_time: float
    timestamp: str

# AI 에이전트 관련 엔드포인트
@router.get("/agents")
async def get_all_agents():
    """모든 AI 에이전트 정보 조회"""
    try:
        agents = ai_service.get_all_agents()
        return {
            "success": True,
            "agents": agents,
            "total_count": len(agents)
        }
    except Exception as e:
        logger.error(f"에이전트 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="에이전트 정보를 가져올 수 없습니다")

@router.get("/agents/{agent_id}")
async def get_agent_info(agent_id: AgentType):
    """특정 AI 에이전트 정보 조회"""
    try:
        agent_info = ai_service.get_agent_info(agent_id)
        return {
            "success": True,
            "agent": agent_info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"에이전트 정보 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="에이전트 정보를 가져올 수 없습니다")

@router.post("/chat/start")
async def start_chat_session(
    request: ChatSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """AI 에이전트와 채팅 세션 시작"""
    try:
        session_id = await ai_service.start_session(
            agent_id=request.agent_id,
            user_id=current_user["user_id"],
            context=request.context
        )
        
        agent_info = ai_service.get_agent_info(request.agent_id)
        
        return {
            "success": True,
            "session_id": session_id,
            "agent_id": request.agent_id,
            "agent_name": agent_info["name"],
            "message": f"{agent_info['name']}와의 채팅 세션이 시작되었습니다."
        }
    except Exception as e:
        logger.error(f"채팅 세션 시작 오류: {e}")
        raise HTTPException(status_code=500, detail="채팅 세션을 시작할 수 없습니다")

@router.post("/chat/message", response_model=AgentResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    current_user: dict = Depends(get_current_user)
):
    """AI 에이전트에게 메시지 전송"""
    try:
        response = await ai_service.send_message(
            session_id=request.session_id,
            message=request.message
        )
        
        return AgentResponse(**response)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"메시지 전송 오류: {e}")
        raise HTTPException(status_code=500, detail="메시지를 전송할 수 없습니다")

@router.post("/chat/end")
async def end_chat_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """AI 에이전트 채팅 세션 종료"""
    try:
        session_summary = await ai_service.end_session(session_id)
        
        return {
            "success": True,
            "session_summary": session_summary,
            "message": "채팅 세션이 종료되었습니다."
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"세션 종료 오류: {e}")
        raise HTTPException(status_code=500, detail="세션을 종료할 수 없습니다")

@router.post("/analysis/comprehensive", response_model=AnalysisResponse)
async def run_comprehensive_analysis(
    request: AnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """종합 설계 분석 실행"""
    try:
        # 요청 데이터를 딕셔너리로 변환
        project_data = {
            "request_type": request.request_type,
            "content": request.content,
            "building_type": request.building_type,
            "location": request.location,
            "area": request.area,
            "floors": request.floors,
            "budget": request.budget,
            "sustainability": request.sustainability,
            "style": request.style,
            "special_requirements": request.special_requirements,
            "user_id": current_user["user_id"]
        }
        
        # 종합 분석 실행
        analysis_result = await ai_service.run_comprehensive_analysis(project_data)
        
        return AnalysisResponse(
            analysis_id=analysis_result["analysis_id"],
            status="completed",
            results=analysis_result["agent_results"],
            overall_score=analysis_result["overall_score"],
            processing_time=analysis_result["processing_time"],
            timestamp=analysis_result["generated_at"]
        )
        
    except Exception as e:
        logger.error(f"종합 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="분석을 수행할 수 없습니다")

@router.get("/analysis/{analysis_id}")
async def get_analysis_result(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """분석 결과 조회"""
    try:
        result = ai_service.get_analysis_result(analysis_id)
        
        return {
            "success": True,
            "analysis": result
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"분석 결과 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="분석 결과를 가져올 수 없습니다")

@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """세션 정보 조회"""
    try:
        session_info = ai_service.get_session_info(session_id)
        
        # 사용자 권한 확인
        if session_info["user_id"] != current_user["user_id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="세션에 접근할 권한이 없습니다")
            
        return {
            "success": True,
            "session": session_info
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 정보 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="세션 정보를 가져올 수 없습니다")

# WebSocket 엔드포인트
@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """AI 에이전트 WebSocket 연결"""
    connection_id = None
    try:
        # 연결 승인 및 관리자에 등록
        connection_id = await manager.connect(websocket, user_id)
        
        logger.info(f"AI WebSocket 연결됨: {user_id} ({connection_id})")
        
        while True:
            # 클라이언트로부터 메시지 수신
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # 메시지 처리
            await websocket_handler.handle_message(websocket, connection_id, message_data)
            
    except WebSocketDisconnect:
        logger.info(f"AI WebSocket 연결 해제: {user_id}")
    except Exception as e:
        logger.error(f"WebSocket 오류: {e}")
        await manager.send_personal_message({
            "type": "error",
            "message": "연결 오류가 발생했습니다."
        }, connection_id)
    finally:
        if connection_id:
            manager.disconnect(connection_id, user_id)

# AI 에이전트 상태 및 통계
@router.get("/stats")
async def get_ai_stats(current_user: dict = Depends(get_current_user)):
    """AI 에이전트 통계 정보"""
    try:
        # WebSocket 연결 통계
        connection_stats = manager.get_connection_stats()
        
        # AI 에이전트 성능 통계 (모의 데이터)
        agent_stats = {
            "total_sessions_today": 47,
            "average_response_time": 2.3,
            "user_satisfaction": 4.7,
            "most_used_agent": "materials_specialist",
            "analysis_completed_today": 12
        }
        
        return {
            "success": True,
            "connection_stats": connection_stats,
            "agent_stats": agent_stats,
            "timestamp": "2025-01-07T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"AI 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="통계 정보를 가져올 수 없습니다")

# AI 에이전트 설정 업데이트
@router.put("/agents/{agent_id}/config")
async def update_agent_config(
    agent_id: AgentType,
    config: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """AI 에이전트 설정 업데이트 (관리자 전용)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
        
    try:
        # 에이전트 설정 업데이트 (실제 구현 필요)
        logger.info(f"에이전트 설정 업데이트: {agent_id}")
        
        return {
            "success": True,
            "message": f"{agent_id} 설정이 업데이트되었습니다.",
            "updated_config": config
        }
    except Exception as e:
        logger.error(f"에이전트 설정 업데이트 오류: {e}")
        raise HTTPException(status_code=500, detail="설정을 업데이트할 수 없습니다")

# 에러 핸들러
@router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return HTTPException(status_code=400, detail=str(exc))

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"예상치 못한 오류: {exc}")
    return HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다")

# 헬스체크
@router.get("/health")
async def ai_health_check():
    """AI 서비스 헬스체크"""
    try:
        # AI 서비스 상태 확인
        agents_count = len(ai_service.get_all_agents())
        active_sessions = len(ai_service.sessions)
        
        return {
            "status": "healthy",
            "agents_available": agents_count,
            "active_sessions": active_sessions,
            "websocket_connections": len(manager.active_connections),
            "timestamp": "2025-01-07T10:30:00Z"
        }
    except Exception as e:
        logger.error(f"AI 헬스체크 오류: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-01-07T10:30:00Z"
        }