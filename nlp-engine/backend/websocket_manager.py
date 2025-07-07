import asyncio
import json
import logging
from typing import Dict, List, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class ConnectionManager:
    """WebSocket 연결 관리자"""
    
    def __init__(self):
        # 활성 연결들
        self.active_connections: Dict[str, WebSocket] = {}
        # 사용자별 연결 매핑
        self.user_connections: Dict[str, Set[str]] = {}
        # 프로젝트별 연결 매핑
        self.project_connections: Dict[str, Set[str]] = {}
        # AI 에이전트 세션
        self.ai_agent_sessions: Dict[str, Dict] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, connection_id: str = None) -> str:
        """클라이언트 연결"""
        if connection_id is None:
            connection_id = str(uuid.uuid4())
            
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        # 사용자별 연결 추가
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        logger.info(f"User {user_id} connected with connection {connection_id}")
        
        # 연결 확인 메시지 전송
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
        return connection_id
        
    def disconnect(self, connection_id: str, user_id: str = None):
        """클라이언트 연결 해제"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
            
        # 사용자별 연결에서 제거
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
                
        # 프로젝트별 연결에서 제거
        for project_id, connections in self.project_connections.items():
            connections.discard(connection_id)
            
        # AI 에이전트 세션 정리
        if connection_id in self.ai_agent_sessions:
            del self.ai_agent_sessions[connection_id]
            
        logger.info(f"Connection {connection_id} disconnected")
        
    async def join_project(self, connection_id: str, project_id: str):
        """프로젝트 채널 참여"""
        if project_id not in self.project_connections:
            self.project_connections[project_id] = set()
        self.project_connections[project_id].add(connection_id)
        
        await self.send_personal_message({
            "type": "project_joined",
            "project_id": project_id,
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
    async def leave_project(self, connection_id: str, project_id: str):
        """프로젝트 채널 떠나기"""
        if project_id in self.project_connections:
            self.project_connections[project_id].discard(connection_id)
            
        await self.send_personal_message({
            "type": "project_left", 
            "project_id": project_id,
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
    async def send_personal_message(self, message: dict, connection_id: str):
        """개인 메시지 전송"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {e}")
                self.disconnect(connection_id)
                
    async def send_to_user(self, message: dict, user_id: str):
        """사용자의 모든 연결에 메시지 전송"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id].copy():
                await self.send_personal_message(message, connection_id)
                
    async def broadcast_to_project(self, message: dict, project_id: str, exclude_connection: str = None):
        """프로젝트 참여자들에게 브로드캐스트"""
        if project_id in self.project_connections:
            for connection_id in self.project_connections[project_id].copy():
                if connection_id != exclude_connection:
                    await self.send_personal_message(message, connection_id)
                    
    async def broadcast_to_all(self, message: dict):
        """모든 연결에 브로드캐스트"""
        for connection_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, connection_id)
            
    # AI 에이전트 관련 메서드들
    async def start_ai_session(self, connection_id: str, agent_id: str, user_id: str):
        """AI 에이전트 세션 시작"""
        session_id = str(uuid.uuid4())
        self.ai_agent_sessions[connection_id] = {
            "session_id": session_id,
            "agent_id": agent_id,
            "user_id": user_id,
            "started_at": datetime.now(),
            "message_count": 0
        }
        
        await self.send_personal_message({
            "type": "ai_session_started",
            "session_id": session_id,
            "agent_id": agent_id,
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
        return session_id
        
    async def send_ai_message(self, connection_id: str, message: str, user_id: str):
        """AI 에이전트에게 메시지 전송"""
        if connection_id not in self.ai_agent_sessions:
            await self.send_personal_message({
                "type": "error",
                "message": "AI 세션이 활성화되지 않았습니다."
            }, connection_id)
            return
            
        session = self.ai_agent_sessions[connection_id]
        session["message_count"] += 1
        
        # 사용자 메시지 확인
        await self.send_personal_message({
            "type": "ai_message_received",
            "session_id": session["session_id"],
            "message": message,
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
        # AI 응답 처리 시뮬레이션 (실제로는 AI 엔진과 연동)
        await asyncio.sleep(1)  # 처리 시간 시뮬레이션
        
        # AI 응답 생성 (실제 AI 엔진으로 교체해야 함)
        ai_response = await self._generate_ai_response(session["agent_id"], message)
        
        await self.send_personal_message({
            "type": "ai_response",
            "session_id": session["session_id"],
            "agent_id": session["agent_id"],
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
    async def _generate_ai_response(self, agent_id: str, message: str) -> str:
        """AI 응답 생성 (모의 구현)"""
        responses = {
            "materials_specialist": f"재료 전문가 AI가 '{message}' 요청을 분석했습니다. 친환경 재료와 비용 효율적인 솔루션을 제안드립니다.",
            "design_theorist": f"설계 이론가 AI가 '{message}' 요청을 검토했습니다. 공간 구성과 설계 이론에 기반한 제안을 드립니다.",
            "bim_specialist": f"BIM 전문가 AI가 '{message}' 요청을 처리했습니다. 3D 모델링과 IFC 변환 방안을 제시합니다.",
            "structural_engineer": f"구조 엔지니어 AI가 '{message}' 요청을 분석했습니다. 구조 안전성과 최적화 방안을 제안합니다.",
            "mep_specialist": f"MEP 전문가 AI가 '{message}' 요청을 검토했습니다. 기계/전기/배관 시스템 설계를 제안드립니다.",
            "cost_estimator": f"비용 추정 AI가 '{message}' 요청을 분석했습니다. 정확한 비용 산출과 예산 최적화 방안을 제시합니다.",
            "schedule_manager": f"일정 관리 AI가 '{message}' 요청을 처리했습니다. 프로젝트 일정과 리소스 배분 계획을 제안합니다.",
            "interior_designer": f"인테리어 디자인 AI가 '{message}' 요청을 검토했습니다. 공간 디자인과 인테리어 계획을 제안드립니다."
        }
        
        return responses.get(agent_id, f"AI 에이전트가 '{message}' 요청을 처리했습니다.")
        
    async def end_ai_session(self, connection_id: str):
        """AI 에이전트 세션 종료"""
        if connection_id in self.ai_agent_sessions:
            session = self.ai_agent_sessions[connection_id]
            del self.ai_agent_sessions[connection_id]
            
            await self.send_personal_message({
                "type": "ai_session_ended",
                "session_id": session["session_id"],
                "message_count": session["message_count"],
                "duration": (datetime.now() - session["started_at"]).total_seconds(),
                "timestamp": datetime.now().isoformat()
            }, connection_id)
            
    # 협업 기능
    async def send_project_notification(self, project_id: str, notification: dict, exclude_user: str = None):
        """프로젝트 알림 전송"""
        message = {
            "type": "project_notification",
            "project_id": project_id,
            "notification": notification,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_project(message, project_id)
        
    async def send_design_update(self, project_id: str, update_data: dict):
        """설계 업데이트 알림"""
        message = {
            "type": "design_update",
            "project_id": project_id,
            "update": update_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_project(message, project_id)
        
    async def send_analysis_result(self, project_id: str, analysis_data: dict):
        """분석 결과 알림"""
        message = {
            "type": "analysis_result",
            "project_id": project_id,
            "analysis": analysis_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self.broadcast_to_project(message, project_id)
        
    def get_connection_stats(self) -> dict:
        """연결 상태 통계"""
        return {
            "total_connections": len(self.active_connections),
            "total_users": len(self.user_connections),
            "active_projects": len(self.project_connections),
            "ai_sessions": len(self.ai_agent_sessions)
        }

# 전역 연결 관리자 인스턴스
manager = ConnectionManager()

# WebSocket 메시지 핸들러
class WebSocketHandler:
    """WebSocket 메시지 처리기"""
    
    def __init__(self, connection_manager: ConnectionManager):
        self.manager = connection_manager
        
    async def handle_message(self, websocket: WebSocket, connection_id: str, message_data: dict):
        """메시지 처리"""
        message_type = message_data.get("type")
        
        try:
            if message_type == "ping":
                await self.handle_ping(connection_id)
            elif message_type == "join_project":
                await self.handle_join_project(connection_id, message_data)
            elif message_type == "leave_project":
                await self.handle_leave_project(connection_id, message_data)
            elif message_type == "start_ai_session":
                await self.handle_start_ai_session(connection_id, message_data)
            elif message_type == "ai_message":
                await self.handle_ai_message(connection_id, message_data)
            elif message_type == "end_ai_session":
                await self.handle_end_ai_session(connection_id)
            elif message_type == "project_update":
                await self.handle_project_update(connection_id, message_data)
            else:
                await self.manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}"
                }, connection_id)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.manager.send_personal_message({
                "type": "error",
                "message": "메시지 처리 중 오류가 발생했습니다."
            }, connection_id)
            
    async def handle_ping(self, connection_id: str):
        """핑 응답"""
        await self.manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }, connection_id)
        
    async def handle_join_project(self, connection_id: str, message_data: dict):
        """프로젝트 참여"""
        project_id = message_data.get("project_id")
        if project_id:
            await self.manager.join_project(connection_id, project_id)
            
    async def handle_leave_project(self, connection_id: str, message_data: dict):
        """프로젝트 떠나기"""
        project_id = message_data.get("project_id")
        if project_id:
            await self.manager.leave_project(connection_id, project_id)
            
    async def handle_start_ai_session(self, connection_id: str, message_data: dict):
        """AI 세션 시작"""
        agent_id = message_data.get("agent_id")
        user_id = message_data.get("user_id")
        if agent_id and user_id:
            await self.manager.start_ai_session(connection_id, agent_id, user_id)
            
    async def handle_ai_message(self, connection_id: str, message_data: dict):
        """AI 메시지 처리"""
        message = message_data.get("message")
        user_id = message_data.get("user_id")
        if message and user_id:
            await self.manager.send_ai_message(connection_id, message, user_id)
            
    async def handle_end_ai_session(self, connection_id: str):
        """AI 세션 종료"""
        await self.manager.end_ai_session(connection_id)
        
    async def handle_project_update(self, connection_id: str, message_data: dict):
        """프로젝트 업데이트"""
        project_id = message_data.get("project_id")
        update_data = message_data.get("update")
        if project_id and update_data:
            await self.manager.send_project_notification(project_id, update_data)

# 전역 메시지 핸들러 인스턴스
websocket_handler = WebSocketHandler(manager)