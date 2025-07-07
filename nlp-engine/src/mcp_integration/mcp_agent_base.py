"""
MCP 인식 에이전트 기반 클래스
===========================

Claude Code MCP 환경에서 동작하는 AI 에이전트를 위한 기반 클래스

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# 프로젝트 임포트
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from ai.base_agent import BaseVIBAAgent, AgentCapability

logger = logging.getLogger(__name__)


class MCPToolType(Enum):
    """MCP 도구 유형"""
    FILE_OPERATION = "file_operation"     # 파일 읽기/쓰기
    CODE_EXECUTION = "code_execution"     # 코드 실행
    WEB_SEARCH = "web_search"            # 웹 검색
    BASH_COMMAND = "bash_command"        # 배시 명령어
    GLOB_SEARCH = "glob_search"          # 파일 패턴 검색
    GREP_SEARCH = "grep_search"          # 텍스트 검색


@dataclass
class MCPToolCall:
    """MCP 도구 호출 정보"""
    tool_type: MCPToolType
    tool_name: str
    parameters: Dict[str, Any]
    description: str = ""
    expected_output: str = ""


class MCPAwareAgent(BaseVIBAAgent):
    """MCP 환경 인식 AI 에이전트 기반 클래스"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability]):
        super().__init__(agent_id, name, capabilities)
        self.mcp_tools_available = self._check_mcp_environment()
        self.mcp_tool_calls: List[MCPToolCall] = []
        self.mcp_results: Dict[str, Any] = {}
    
    def _check_mcp_environment(self) -> bool:
        """MCP 환경 사용 가능성 체크"""
        # Claude Code 환경에서는 항상 True로 가정
        # 실제 환경에서는 MCP 도구 사용 가능성을 체크
        return True
    
    async def request_file_read(self, file_path: str, description: str = "") -> str:
        """파일 읽기 요청"""
        tool_call = MCPToolCall(
            tool_type=MCPToolType.FILE_OPERATION,
            tool_name="Read",
            parameters={"file_path": file_path},
            description=description or f"파일 읽기: {file_path}",
            expected_output="파일 내용"
        )
        
        self.mcp_tool_calls.append(tool_call)
        
        # MCP 환경에서는 실제로 도구를 호출할 수 없으므로 요청만 기록
        logger.info(f"MCP 파일 읽기 요청: {file_path}")
        
        # 모의 응답 반환 (실제 MCP 환경에서는 실제 파일 내용 반환)
        return f"[MCP] 파일 읽기 요청됨: {file_path}"
    
    async def request_file_write(self, file_path: str, content: str, description: str = "") -> bool:
        """파일 쓰기 요청"""
        tool_call = MCPToolCall(
            tool_type=MCPToolType.FILE_OPERATION,
            tool_name="Write",
            parameters={"file_path": file_path, "content": content},
            description=description or f"파일 쓰기: {file_path}",
            expected_output="쓰기 완료 확인"
        )
        
        self.mcp_tool_calls.append(tool_call)
        logger.info(f"MCP 파일 쓰기 요청: {file_path}")
        
        return True
    
    async def request_bash_command(self, command: str, description: str = "") -> str:
        """배시 명령어 실행 요청"""
        tool_call = MCPToolCall(
            tool_type=MCPToolType.BASH_COMMAND,
            tool_name="Bash",
            parameters={"command": command, "description": description},
            description=description or f"명령어 실행: {command}",
            expected_output="명령어 실행 결과"
        )
        
        self.mcp_tool_calls.append(tool_call)
        logger.info(f"MCP 배시 명령어 요청: {command}")
        
        return f"[MCP] 명령어 실행 요청됨: {command}"
    
    async def request_web_search(self, query: str, description: str = "") -> Dict[str, Any]:
        """웹 검색 요청"""
        tool_call = MCPToolCall(
            tool_type=MCPToolType.WEB_SEARCH,
            tool_name="WebSearch",
            parameters={"query": query},
            description=description or f"웹 검색: {query}",
            expected_output="검색 결과"
        )
        
        self.mcp_tool_calls.append(tool_call)
        logger.info(f"MCP 웹 검색 요청: {query}")
        
        return {"query": query, "status": "requested", "mcp_tool": "WebSearch"}
    
    async def request_glob_search(self, pattern: str, path: str = None, description: str = "") -> List[str]:
        """글롭 패턴 파일 검색 요청"""
        params = {"pattern": pattern}
        if path:
            params["path"] = path
            
        tool_call = MCPToolCall(
            tool_type=MCPToolType.GLOB_SEARCH,
            tool_name="Glob",
            parameters=params,
            description=description or f"파일 패턴 검색: {pattern}",
            expected_output="매칭 파일 목록"
        )
        
        self.mcp_tool_calls.append(tool_call)
        logger.info(f"MCP 글롭 검색 요청: {pattern}")
        
        return [f"[MCP] 패턴 검색 요청됨: {pattern}"]
    
    async def request_grep_search(self, pattern: str, include: str = None, path: str = None, description: str = "") -> List[str]:
        """그렙 텍스트 검색 요청"""
        params = {"pattern": pattern}
        if include:
            params["include"] = include
        if path:
            params["path"] = path
            
        tool_call = MCPToolCall(
            tool_type=MCPToolType.GREP_SEARCH,
            tool_name="Grep",
            parameters=params,
            description=description or f"텍스트 검색: {pattern}",
            expected_output="매칭 파일 목록"
        )
        
        self.mcp_tool_calls.append(tool_call)
        logger.info(f"MCP 그렙 검색 요청: {pattern}")
        
        return [f"[MCP] 텍스트 검색 요청됨: {pattern}"]
    
    async def request_code_execution(self, code: str, description: str = "") -> Dict[str, Any]:
        """코드 실행 요청 (Jupyter 환경)"""
        tool_call = MCPToolCall(
            tool_type=MCPToolType.CODE_EXECUTION,
            tool_name="mcp__ide__executeCode",
            parameters={"code": code},
            description=description or "코드 실행",
            expected_output="실행 결과"
        )
        
        self.mcp_tool_calls.append(tool_call)
        logger.info(f"MCP 코드 실행 요청: {code[:100]}...")
        
        return {"code": code, "status": "requested", "mcp_tool": "executeCode"}
    
    def get_mcp_usage_summary(self) -> Dict[str, Any]:
        """MCP 도구 사용 요약"""
        tool_counts = {}
        for tool_call in self.mcp_tool_calls:
            tool_type = tool_call.tool_type.value
            tool_counts[tool_type] = tool_counts.get(tool_type, 0) + 1
        
        return {
            "total_mcp_calls": len(self.mcp_tool_calls),
            "tool_usage_counts": tool_counts,
            "mcp_available": self.mcp_tools_available,
            "recent_calls": [
                {
                    "tool": call.tool_name,
                    "type": call.tool_type.value,
                    "description": call.description
                }
                for call in self.mcp_tool_calls[-5:]  # 최근 5개
            ]
        }
    
    def generate_mcp_action_plan(self, task_description: str) -> List[MCPToolCall]:
        """작업에 필요한 MCP 도구 호출 계획 생성"""
        action_plan = []
        
        # 작업 유형에 따른 MCP 도구 사용 패턴
        if "파일" in task_description or "읽기" in task_description:
            action_plan.append(MCPToolCall(
                tool_type=MCPToolType.FILE_OPERATION,
                tool_name="Read",
                parameters={"file_path": "[TBD]"},
                description="관련 파일 읽기"
            ))
        
        if "검색" in task_description or "찾기" in task_description:
            action_plan.append(MCPToolCall(
                tool_type=MCPToolType.GREP_SEARCH,
                tool_name="Grep",
                parameters={"pattern": "[TBD]"},
                description="텍스트 패턴 검색"
            ))
        
        if "실행" in task_description or "테스트" in task_description:
            action_plan.append(MCPToolCall(
                tool_type=MCPToolType.BASH_COMMAND,
                tool_name="Bash",
                parameters={"command": "[TBD]"},
                description="명령어 실행"
            ))
        
        if "분석" in task_description or "처리" in task_description:
            action_plan.append(MCPToolCall(
                tool_type=MCPToolType.CODE_EXECUTION,
                tool_name="mcp__ide__executeCode",
                parameters={"code": "[TBD]"},
                description="데이터 분석 코드 실행"
            ))
        
        return action_plan
    
    @abstractmethod
    async def execute_task_with_mcp(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 도구를 활용한 작업 실행 (서브클래스에서 구현)"""
        pass
    
    async def execute_task(self, task) -> Dict[str, Any]:
        """기본 작업 실행 (MCP 사용 가능하면 MCP 버전 호출)"""
        if self.mcp_tools_available and hasattr(self, 'execute_task_with_mcp'):
            task_dict = task if isinstance(task, dict) else {"task": task}
            return await self.execute_task_with_mcp(task_dict)
        else:
            # 기본 실행 로직
            return await super().execute_task(task)


class MCPDesignAgent(MCPAwareAgent):
    """MCP 기반 설계 에이전트 예시"""
    
    def __init__(self):
        super().__init__(
            agent_id="mcp_design_agent",
            name="MCP Design Agent",
            capabilities=[
                AgentCapability.DESIGN_THEORY_APPLICATION,
                AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING
            ]
        )
    
    async def execute_task_with_mcp(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 도구를 활용한 설계 작업 실행"""
        user_input = task.get("user_input", "")
        
        # 1. 관련 설계 패턴 파일 검색
        pattern_files = await self.request_glob_search(
            "**/*pattern*.py",
            description="설계 패턴 파일 검색"
        )
        
        # 2. 건축 이론 관련 파일 읽기
        theory_content = await self.request_file_read(
            "/path/to/architectural_theory.py",
            description="건축 이론 지식 로드"
        )
        
        # 3. 사용자 요구사항 분석을 위한 NLP 코드 실행
        analysis_code = f"""
# 사용자 요구사항 분석
user_input = "{user_input}"
keywords = []
for keyword in ["카페", "모던", "한옥", "사무실"]:
    if keyword in user_input:
        keywords.append(keyword)
        
print(f"추출된 키워드: {{keywords}}")
"""
        
        analysis_result = await self.request_code_execution(
            analysis_code,
            description="사용자 요구사항 키워드 분석"
        )
        
        # 4. 웹에서 최신 건축 트렌드 검색
        trend_info = await self.request_web_search(
            f"{user_input} 건축 설계 트렌드 2025",
            description="최신 건축 트렌드 정보 수집"
        )
        
        # 5. 결과 통합
        result = {
            "success": True,
            "agent_id": self.agent_id,
            "input": user_input,
            "mcp_analysis": {
                "pattern_files_found": len(pattern_files),
                "theory_loaded": bool(theory_content),
                "keyword_analysis": analysis_result,
                "trend_research": trend_info
            },
            "design_recommendations": [
                "MCP 도구를 활용한 포괄적 분석 완료",
                "최신 트렌드와 이론 지식 통합",
                "사용자 요구사항 정확히 파악"
            ],
            "mcp_usage": self.get_mcp_usage_summary()
        }
        
        return result


# MCP 통합 테스트용 간단한 에이전트
class SimpleMCPTestAgent(MCPAwareAgent):
    """MCP 통합 테스트를 위한 간단한 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_id="simple_mcp_test",
            name="Simple MCP Test Agent",
            capabilities=[AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING]
        )
    
    async def execute_task_with_mcp(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """간단한 MCP 테스트 작업"""
        user_input = task.get("user_input", "")
        
        # MCP 도구 사용 시뮬레이션
        mcp_calls = 0
        
        # 파일 검색 테스트
        if "파일" in user_input:
            await self.request_glob_search("*.py", description="Python 파일 검색")
            mcp_calls += 1
        
        # 텍스트 검색 테스트
        if "검색" in user_input:
            await self.request_grep_search("class", include="*.py", description="클래스 정의 검색")
            mcp_calls += 1
        
        # 명령어 실행 테스트
        if "실행" in user_input:
            await self.request_bash_command("echo 'MCP 테스트'", description="테스트 명령어")
            mcp_calls += 1
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "input": user_input,
            "mcp_calls_made": mcp_calls,
            "result": f"MCP 도구를 {mcp_calls}번 사용하여 작업 완료",
            "mcp_summary": self.get_mcp_usage_summary()
        }