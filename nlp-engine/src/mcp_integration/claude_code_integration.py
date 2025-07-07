"""
Claude Code MCP 통합
===================

Claude Code 환경의 MCP 도구들과 VIBA AI 시스템 통합

@version 1.0
@author VIBA AI Team  
@date 2025.07.06
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ClaudeCodeTool(Enum):
    """Claude Code에서 사용 가능한 MCP 도구들"""
    TASK = "Task"                           # 작업 위임
    BASH = "Bash"                          # 터미널 명령어
    GLOB = "Glob"                          # 파일 패턴 검색
    GREP = "Grep"                          # 텍스트 검색
    LS = "LS"                             # 디렉토리 목록
    READ = "Read"                         # 파일 읽기
    EDIT = "Edit"                         # 파일 편집
    MULTI_EDIT = "MultiEdit"              # 다중 파일 편집
    WRITE = "Write"                       # 파일 쓰기
    NOTEBOOK_READ = "NotebookRead"        # 노트북 읽기
    NOTEBOOK_EDIT = "NotebookEdit"        # 노트북 편집
    WEB_FETCH = "WebFetch"                # 웹 페이지 가져오기
    TODO_READ = "TodoRead"                # 할일 목록 읽기
    TODO_WRITE = "TodoWrite"              # 할일 목록 쓰기
    WEB_SEARCH = "WebSearch"              # 웹 검색
    MCP_IDE_GET_DIAGNOSTICS = "mcp__ide__getDiagnostics"  # 진단 정보
    MCP_IDE_EXECUTE_CODE = "mcp__ide__executeCode"        # 코드 실행


@dataclass
class MCPIntegrationConfig:
    """MCP 통합 설정"""
    enabled_tools: List[ClaudeCodeTool] = field(default_factory=list)
    max_file_size: int = 1024 * 1024  # 1MB
    timeout_seconds: int = 30
    working_directory: str = ""
    backup_enabled: bool = True


class ClaudeCodeIntegration:
    """Claude Code MCP 통합 관리자"""
    
    def __init__(self, config: Optional[MCPIntegrationConfig] = None):
        self.config = config or MCPIntegrationConfig()
        self.tool_usage_log: List[Dict[str, Any]] = []
        self.available_tools = self._detect_available_tools()
    
    def _detect_available_tools(self) -> List[ClaudeCodeTool]:
        """사용 가능한 Claude Code 도구 감지"""
        # Claude Code 환경에서는 모든 도구가 사용 가능하다고 가정
        return list(ClaudeCodeTool)
    
    def is_tool_available(self, tool: ClaudeCodeTool) -> bool:
        """특정 도구 사용 가능 여부 확인"""
        return tool in self.available_tools
    
    async def execute_file_search(self, pattern: str, include_path: str = None) -> Dict[str, Any]:
        """파일 검색 실행"""
        if not self.is_tool_available(ClaudeCodeTool.GLOB):
            return {"error": "Glob 도구를 사용할 수 없습니다"}
        
        search_result = {
            "tool": "Glob",
            "pattern": pattern,
            "include_path": include_path,
            "status": "simulated",
            "description": f"파일 패턴 '{pattern}' 검색"
        }
        
        self._log_tool_usage(ClaudeCodeTool.GLOB, search_result)
        return search_result
    
    async def execute_text_search(self, pattern: str, file_filter: str = None, path: str = None) -> Dict[str, Any]:
        """텍스트 검색 실행"""
        if not self.is_tool_available(ClaudeCodeTool.GREP):
            return {"error": "Grep 도구를 사용할 수 없습니다"}
        
        search_result = {
            "tool": "Grep",
            "pattern": pattern,
            "file_filter": file_filter,
            "path": path,
            "status": "simulated",
            "description": f"텍스트 패턴 '{pattern}' 검색"
        }
        
        self._log_tool_usage(ClaudeCodeTool.GREP, search_result)
        return search_result
    
    async def read_file_content(self, file_path: str, offset: int = None, limit: int = None) -> Dict[str, Any]:
        """파일 내용 읽기"""
        if not self.is_tool_available(ClaudeCodeTool.READ):
            return {"error": "Read 도구를 사용할 수 없습니다"}
        
        read_result = {
            "tool": "Read",
            "file_path": file_path,
            "offset": offset,
            "limit": limit,
            "status": "simulated",
            "description": f"파일 '{file_path}' 읽기"
        }
        
        self._log_tool_usage(ClaudeCodeTool.READ, read_result)
        return read_result
    
    async def write_file_content(self, file_path: str, content: str) -> Dict[str, Any]:
        """파일 내용 쓰기"""
        if not self.is_tool_available(ClaudeCodeTool.WRITE):
            return {"error": "Write 도구를 사용할 수 없습니다"}
        
        write_result = {
            "tool": "Write",
            "file_path": file_path,
            "content_length": len(content),
            "status": "simulated",
            "description": f"파일 '{file_path}' 쓰기"
        }
        
        self._log_tool_usage(ClaudeCodeTool.WRITE, write_result)
        return write_result
    
    async def edit_file_content(self, file_path: str, old_string: str, new_string: str, replace_all: bool = False) -> Dict[str, Any]:
        """파일 내용 편집"""
        if not self.is_tool_available(ClaudeCodeTool.EDIT):
            return {"error": "Edit 도구를 사용할 수 없습니다"}
        
        edit_result = {
            "tool": "Edit",
            "file_path": file_path,
            "old_string": old_string[:50] + "..." if len(old_string) > 50 else old_string,
            "new_string": new_string[:50] + "..." if len(new_string) > 50 else new_string,
            "replace_all": replace_all,
            "status": "simulated",
            "description": f"파일 '{file_path}' 편집"
        }
        
        self._log_tool_usage(ClaudeCodeTool.EDIT, edit_result)
        return edit_result
    
    async def execute_bash_command(self, command: str, description: str = "") -> Dict[str, Any]:
        """배시 명령어 실행"""
        if not self.is_tool_available(ClaudeCodeTool.BASH):
            return {"error": "Bash 도구를 사용할 수 없습니다"}
        
        bash_result = {
            "tool": "Bash",
            "command": command,
            "description": description or f"명령어 실행: {command}",
            "status": "simulated",
            "safety_note": "실제 환경에서는 명령어 안전성 검토 필요"
        }
        
        self._log_tool_usage(ClaudeCodeTool.BASH, bash_result)
        return bash_result
    
    async def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """코드 실행 (Jupyter 환경)"""
        if not self.is_tool_available(ClaudeCodeTool.MCP_IDE_EXECUTE_CODE):
            return {"error": "코드 실행 도구를 사용할 수 없습니다"}
        
        code_result = {
            "tool": "mcp__ide__executeCode",
            "code": code[:200] + "..." if len(code) > 200 else code,
            "language": language,
            "status": "simulated",
            "description": f"{language} 코드 실행"
        }
        
        self._log_tool_usage(ClaudeCodeTool.MCP_IDE_EXECUTE_CODE, code_result)
        return code_result
    
    async def web_search(self, query: str, allowed_domains: List[str] = None, blocked_domains: List[str] = None) -> Dict[str, Any]:
        """웹 검색 실행"""
        if not self.is_tool_available(ClaudeCodeTool.WEB_SEARCH):
            return {"error": "WebSearch 도구를 사용할 수 없습니다"}
        
        search_result = {
            "tool": "WebSearch",
            "query": query,
            "allowed_domains": allowed_domains,
            "blocked_domains": blocked_domains,
            "status": "simulated",
            "description": f"웹 검색: '{query}'"
        }
        
        self._log_tool_usage(ClaudeCodeTool.WEB_SEARCH, search_result)
        return search_result
    
    async def fetch_web_content(self, url: str, prompt: str) -> Dict[str, Any]:
        """웹 콘텐츠 가져오기"""
        if not self.is_tool_available(ClaudeCodeTool.WEB_FETCH):
            return {"error": "WebFetch 도구를 사용할 수 없습니다"}
        
        fetch_result = {
            "tool": "WebFetch",
            "url": url,
            "prompt": prompt,
            "status": "simulated",
            "description": f"웹 페이지 가져오기: {url}"
        }
        
        self._log_tool_usage(ClaudeCodeTool.WEB_FETCH, fetch_result)
        return fetch_result
    
    async def delegate_task(self, description: str, prompt: str) -> Dict[str, Any]:
        """작업 위임"""
        if not self.is_tool_available(ClaudeCodeTool.TASK):
            return {"error": "Task 도구를 사용할 수 없습니다"}
        
        task_result = {
            "tool": "Task",
            "description": description,
            "prompt": prompt[:100] + "..." if len(prompt) > 100 else prompt,
            "status": "simulated",
            "description": f"작업 위임: {description}"
        }
        
        self._log_tool_usage(ClaudeCodeTool.TASK, task_result)
        return task_result
    
    async def manage_todo_list(self, todos: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """할일 목록 관리"""
        if not self.is_tool_available(ClaudeCodeTool.TODO_WRITE):
            return {"error": "TodoWrite 도구를 사용할 수 없습니다"}
        
        todo_result = {
            "tool": "TodoWrite",
            "todos_count": len(todos) if todos else 0,
            "status": "simulated",
            "description": f"할일 목록 관리: {len(todos) if todos else 0}개 항목"
        }
        
        self._log_tool_usage(ClaudeCodeTool.TODO_WRITE, todo_result)
        return todo_result
    
    def _log_tool_usage(self, tool: ClaudeCodeTool, result: Dict[str, Any]):
        """도구 사용 로그 기록"""
        log_entry = {
            "timestamp": asyncio.get_event_loop().time(),
            "tool": tool.value,
            "result": result
        }
        self.tool_usage_log.append(log_entry)
        
        # 로그 크기 제한 (최근 100개만 유지)
        if len(self.tool_usage_log) > 100:
            self.tool_usage_log = self.tool_usage_log[-100:]
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """도구 사용 통계"""
        tool_counts = {}
        for log_entry in self.tool_usage_log:
            tool = log_entry["tool"]
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
        
        return {
            "total_tool_calls": len(self.tool_usage_log),
            "tool_usage_counts": tool_counts,
            "available_tools": [tool.value for tool in self.available_tools],
            "recent_usage": self.tool_usage_log[-10:] if self.tool_usage_log else []
        }
    
    async def comprehensive_project_analysis(self, project_path: str = ".") -> Dict[str, Any]:
        """프로젝트 포괄적 분석"""
        analysis_result = {
            "project_path": project_path,
            "analysis_steps": [],
            "tool_calls": []
        }
        
        # 1. 프로젝트 구조 파악
        structure_search = await self.execute_file_search("**/*", project_path)
        analysis_result["tool_calls"].append(structure_search)
        analysis_result["analysis_steps"].append("프로젝트 파일 구조 분석")
        
        # 2. Python 파일 찾기
        python_files = await self.execute_file_search("**/*.py", project_path)
        analysis_result["tool_calls"].append(python_files)
        analysis_result["analysis_steps"].append("Python 파일 검색")
        
        # 3. 설정 파일 찾기
        config_files = await self.execute_file_search("**/*config*", project_path)
        analysis_result["tool_calls"].append(config_files)
        analysis_result["analysis_steps"].append("설정 파일 검색")
        
        # 4. 클래스 정의 검색
        class_search = await self.execute_text_search("^class ", "*.py", project_path)
        analysis_result["tool_calls"].append(class_search)
        analysis_result["analysis_steps"].append("클래스 정의 검색")
        
        # 5. 함수 정의 검색
        function_search = await self.execute_text_search("^def ", "*.py", project_path)
        analysis_result["tool_calls"].append(function_search)
        analysis_result["analysis_steps"].append("함수 정의 검색")
        
        # 6. 에러 및 경고 검색
        error_search = await self.execute_text_search("(error|Error|ERROR|exception|Exception)", "*.py", project_path)
        analysis_result["tool_calls"].append(error_search)
        analysis_result["analysis_steps"].append("에러 관련 코드 검색")
        
        # 7. TODO 항목 검색
        todo_search = await self.execute_text_search("(TODO|FIXME|XXX|HACK)", "*", project_path)
        analysis_result["tool_calls"].append(todo_search)
        analysis_result["analysis_steps"].append("TODO 항목 검색")
        
        analysis_result["summary"] = {
            "total_steps": len(analysis_result["analysis_steps"]),
            "total_tool_calls": len(analysis_result["tool_calls"]),
            "analysis_complete": True
        }
        
        return analysis_result
    
    async def automated_code_review(self, file_patterns: List[str] = None) -> Dict[str, Any]:
        """자동화된 코드 리뷰"""
        if not file_patterns:
            file_patterns = ["**/*.py"]
        
        review_result = {
            "file_patterns": file_patterns,
            "review_checks": [],
            "findings": []
        }
        
        # 기본적인 코드 품질 체크
        quality_checks = [
            ("import", "임포트 구문 분석"),
            ("class [A-Z]", "클래스 네이밍 컨벤션 체크"),
            ("def [a-z]", "함수 네이밍 컨벤션 체크"),
            ("# TODO", "미완성 작업 체크"),
            ("print\\(", "디버그 출력 체크"),
            ("except:", "베어 except 체크")
        ]
        
        for pattern, description in quality_checks:
            search_result = await self.execute_text_search(pattern, "*.py")
            review_result["review_checks"].append({
                "check": description,
                "pattern": pattern,
                "result": search_result
            })
        
        # 보안 관련 체크
        security_checks = [
            ("password", "하드코딩된 패스워드 체크"),
            ("secret", "하드코딩된 시크릿 체크"),
            ("eval\\(", "위험한 eval 사용 체크"),
            ("exec\\(", "위험한 exec 사용 체크")
        ]
        
        for pattern, description in security_checks:
            search_result = await self.execute_text_search(pattern, "*.py")
            review_result["review_checks"].append({
                "check": description,
                "pattern": pattern,
                "result": search_result,
                "severity": "high"
            })
        
        review_result["summary"] = {
            "total_checks": len(review_result["review_checks"]),
            "security_checks": len(security_checks),
            "quality_checks": len(quality_checks),
            "review_complete": True
        }
        
        return review_result


# VIBA AI 시스템과 Claude Code MCP 통합을 위한 어댑터
class VIBAMCPAdapter:
    """VIBA AI 시스템과 Claude Code MCP 간의 어댑터"""
    
    def __init__(self):
        self.mcp_integration = ClaudeCodeIntegration()
        self.viba_project_path = "/Users/seunghakwoo/Documents/Cursor/Z"
    
    async def analyze_viba_system(self) -> Dict[str, Any]:
        """VIBA 시스템 분석"""
        analysis = await self.mcp_integration.comprehensive_project_analysis(
            self.viba_project_path
        )
        
        # VIBA 특화 분석 추가
        viba_analysis = {
            "base_analysis": analysis,
            "viba_specific": {}
        }
        
        # AI 에이전트 파일 검색
        agent_search = await self.mcp_integration.execute_file_search(
            "**/agents/*.py", 
            self.viba_project_path
        )
        viba_analysis["viba_specific"]["agents"] = agent_search
        
        # NLP 프로세서 검색
        nlp_search = await self.mcp_integration.execute_file_search(
            "**/processors/*.py",
            self.viba_project_path
        )
        viba_analysis["viba_specific"]["nlp"] = nlp_search
        
        # 설정 파일 검색
        config_search = await self.mcp_integration.execute_file_search(
            "**/requirements.txt",
            self.viba_project_path
        )
        viba_analysis["viba_specific"]["requirements"] = config_search
        
        return viba_analysis
    
    async def perform_viba_code_review(self) -> Dict[str, Any]:
        """VIBA 코드 리뷰 수행"""
        return await self.mcp_integration.automated_code_review([
            "**/src/**/*.py",
            "**/tests/**/*.py"
        ])
    
    async def check_viba_dependencies(self) -> Dict[str, Any]:
        """VIBA 의존성 체크"""
        dependency_result = {
            "import_analysis": {},
            "missing_modules": [],
            "recommendations": []
        }
        
        # 임포트 분석
        import_search = await self.mcp_integration.execute_text_search(
            "^from .* import|^import ",
            "*.py",
            self.viba_project_path
        )
        dependency_result["import_analysis"] = import_search
        
        # 에러 패턴 검색
        error_search = await self.mcp_integration.execute_text_search(
            "ImportError|ModuleNotFoundError",
            "*.py",
            self.viba_project_path
        )
        dependency_result["import_errors"] = error_search
        
        return dependency_result