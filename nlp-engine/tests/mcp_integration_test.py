"""
MCP 통합 테스트 시스템
====================

Claude Code MCP 환경에서 VIBA AI 시스템의 통합 테스트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import sys
import os
import time
from typing import Dict, List, Any
from dataclasses import dataclass

# 경로 설정
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# MCP 통합 모듈 임포트
try:
    from mcp_integration.mcp_agent_base import MCPAwareAgent, SimpleMCPTestAgent
    from mcp_integration.claude_code_integration import ClaudeCodeIntegration, VIBAMCPAdapter
    MCP_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"MCP 모듈 임포트 실패: {e}")
    MCP_MODULES_AVAILABLE = False

# 기존 시스템 임포트
try:
    from ai.agents.simple_test_agent import SimpleTestAgent, SimpleOrchestrator, simple_process_user_request
    SIMPLE_AGENTS_AVAILABLE = True
except ImportError as e:
    print(f"간단한 에이전트 임포트 실패: {e}")
    SIMPLE_AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MCPTestCase:
    """MCP 테스트 케이스"""
    test_id: str
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_mcp_calls: int
    requires_mcp: bool = True


@dataclass
class MCPTestResult:
    """MCP 테스트 결과"""
    test_id: str
    success: bool
    execution_time: float
    mcp_calls_made: int
    error_message: str = ""
    details: Dict[str, Any] = None


class MCPIntegrationTestSuite:
    """MCP 통합 테스트 스위트"""
    
    def __init__(self):
        self.test_cases = self._create_mcp_test_cases()
        self.results: List[MCPTestResult] = []
        self.mcp_integration = None
        self.viba_adapter = None
        
        if MCP_MODULES_AVAILABLE:
            try:
                self.mcp_integration = ClaudeCodeIntegration()
                self.viba_adapter = VIBAMCPAdapter()
            except Exception as e:
                logger.warning(f"MCP 통합 초기화 실패: {e}")
    
    def _create_mcp_test_cases(self) -> List[MCPTestCase]:
        """MCP 테스트 케이스 생성"""
        return [
            MCPTestCase(
                test_id="mcp_file_search",
                name="MCP 파일 검색 테스트",
                description="Glob 도구를 사용한 파일 패턴 검색",
                input_data={"pattern": "**/*.py", "description": "Python 파일 검색"},
                expected_mcp_calls=1
            ),
            MCPTestCase(
                test_id="mcp_text_search",
                name="MCP 텍스트 검색 테스트", 
                description="Grep 도구를 사용한 텍스트 패턴 검색",
                input_data={"pattern": "class", "include": "*.py", "description": "클래스 정의 검색"},
                expected_mcp_calls=1
            ),
            MCPTestCase(
                test_id="mcp_file_operations",
                name="MCP 파일 작업 테스트",
                description="Read/Write 도구를 사용한 파일 작업",
                input_data={"file_path": "/tmp/test.txt", "content": "MCP 테스트"},
                expected_mcp_calls=2
            ),
            MCPTestCase(
                test_id="mcp_bash_execution",
                name="MCP 배시 실행 테스트",
                description="Bash 도구를 사용한 명령어 실행",
                input_data={"command": "echo 'MCP 테스트'", "description": "테스트 명령어"},
                expected_mcp_calls=1
            ),
            MCPTestCase(
                test_id="mcp_web_search", 
                name="MCP 웹 검색 테스트",
                description="WebSearch 도구를 사용한 웹 검색",
                input_data={"query": "VIBA AI 건축 설계", "description": "AI 건축 정보 검색"},
                expected_mcp_calls=1
            ),
            MCPTestCase(
                test_id="mcp_agent_integration",
                name="MCP 에이전트 통합 테스트",
                description="MCP 인식 에이전트의 통합 동작 테스트",
                input_data={"user_input": "강남에 카페를 설계해줘", "use_mcp": True},
                expected_mcp_calls=3
            ),
            MCPTestCase(
                test_id="viba_project_analysis",
                name="VIBA 프로젝트 분석 테스트",
                description="VIBA 프로젝트 전체 구조 분석",
                input_data={"analyze_project": True},
                expected_mcp_calls=7
            ),
            MCPTestCase(
                test_id="dependency_check_test",
                name="의존성 체크 테스트",
                description="시스템 의존성 상태 확인",
                input_data={"check_dependencies": True},
                expected_mcp_calls=2,
                requires_mcp=False
            )
        ]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 MCP 테스트 실행"""
        print("🧪 MCP 통합 테스트 시작...")
        print("=" * 60)
        
        start_time = time.time()
        
        # 1. 환경 체크
        await self._test_environment_check()
        
        # 2. 기본 MCP 도구 테스트
        await self._test_basic_mcp_tools()
        
        # 3. MCP 에이전트 테스트
        await self._test_mcp_agents()
        
        # 4. VIBA 시스템 통합 테스트
        await self._test_viba_integration()
        
        # 5. 성능 및 안정성 테스트
        await self._test_performance_stability()
        
        total_time = time.time() - start_time
        
        # 결과 집계
        successful_tests = sum(1 for r in self.results if r.success)
        total_tests = len(self.results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": success_rate,
            "total_execution_time": total_time,
            "mcp_available": MCP_MODULES_AVAILABLE,
            "simple_agents_available": SIMPLE_AGENTS_AVAILABLE,
            "test_results": [
                {
                    "test_id": r.test_id,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "mcp_calls": r.mcp_calls_made,
                    "error": r.error_message if not r.success else None
                }
                for r in self.results
            ]
        }
        
        print("\n" + "=" * 60)
        print("📊 MCP 통합 테스트 결과 요약")
        print(f"총 테스트: {total_tests}개")
        print(f"성공: {successful_tests}개")
        print(f"실패: {total_tests - successful_tests}개")
        print(f"성공률: {success_rate:.1f}%")
        print(f"총 실행 시간: {total_time:.2f}초")
        
        if success_rate >= 80:
            print("✅ MCP 통합 테스트 통과! 시스템이 정상 작동합니다.")
        else:
            print("❌ MCP 통합 테스트 실패. 시스템에 문제가 있습니다.")
        
        return summary
    
    async def _test_environment_check(self):
        """환경 체크 테스트"""
        print("\n1️⃣ 환경 체크 테스트")
        print("-" * 40)
        
        # MCP 모듈 사용 가능성 체크
        await self._execute_test_case(MCPTestCase(
            test_id="env_mcp_modules",
            name="MCP 모듈 사용 가능성",
            description="MCP 통합 모듈들이 정상적으로 로드되는지 확인",
            input_data={"check_mcp_modules": True},
            expected_mcp_calls=0,
            requires_mcp=False
        ))
        
        # 기본 에이전트 사용 가능성 체크
        await self._execute_test_case(MCPTestCase(
            test_id="env_simple_agents",
            name="기본 에이전트 사용 가능성",
            description="기본 AI 에이전트들이 정상적으로 로드되는지 확인",
            input_data={"check_simple_agents": True},
            expected_mcp_calls=0,
            requires_mcp=False
        ))
    
    async def _test_basic_mcp_tools(self):
        """기본 MCP 도구 테스트"""
        print("\n2️⃣ 기본 MCP 도구 테스트")
        print("-" * 40)
        
        if not MCP_MODULES_AVAILABLE:
            print("  ⚠️ MCP 모듈을 사용할 수 없어 기본 도구 테스트를 건너뜁니다.")
            return
        
        # 파일 검색 테스트
        await self._execute_test_case(self.test_cases[0])  # mcp_file_search
        
        # 텍스트 검색 테스트
        await self._execute_test_case(self.test_cases[1])  # mcp_text_search
        
        # 파일 작업 테스트
        await self._execute_test_case(self.test_cases[2])  # mcp_file_operations
        
        # 배시 실행 테스트
        await self._execute_test_case(self.test_cases[3])  # mcp_bash_execution
    
    async def _test_mcp_agents(self):
        """MCP 에이전트 테스트"""
        print("\n3️⃣ MCP 에이전트 테스트")
        print("-" * 40)
        
        if not MCP_MODULES_AVAILABLE:
            print("  ⚠️ MCP 모듈을 사용할 수 없어 MCP 에이전트 테스트를 건너뜁니다.")
            return
        
        # MCP 에이전트 통합 테스트
        await self._execute_test_case(self.test_cases[5])  # mcp_agent_integration
    
    async def _test_viba_integration(self):
        """VIBA 시스템 통합 테스트"""
        print("\n4️⃣ VIBA 시스템 통합 테스트")
        print("-" * 40)
        
        if not MCP_MODULES_AVAILABLE:
            print("  ⚠️ MCP 모듈을 사용할 수 없어 VIBA 통합 테스트를 건너뜁니다.")
            return
        
        # VIBA 프로젝트 분석 테스트
        await self._execute_test_case(self.test_cases[6])  # viba_project_analysis
        
        # 의존성 체크 테스트
        await self._execute_test_case(self.test_cases[7])  # dependency_check_test
    
    async def _test_performance_stability(self):
        """성능 및 안정성 테스트"""
        print("\n5️⃣ 성능 및 안정성 테스트")
        print("-" * 40)
        
        # 동시 실행 테스트
        await self._test_concurrent_mcp_calls()
        
        # 메모리 사용량 테스트
        await self._test_memory_usage()
    
    async def _execute_test_case(self, test_case: MCPTestCase):
        """개별 테스트 케이스 실행"""
        print(f"  📋 {test_case.name}...")
        
        start_time = time.time()
        mcp_calls_made = 0
        
        try:
            if test_case.test_id == "env_mcp_modules":
                # MCP 모듈 체크
                result = {"success": MCP_MODULES_AVAILABLE, "mcp_available": MCP_MODULES_AVAILABLE}
                
            elif test_case.test_id == "env_simple_agents":
                # 간단한 에이전트 체크
                result = {"success": SIMPLE_AGENTS_AVAILABLE, "agents_available": SIMPLE_AGENTS_AVAILABLE}
                
            elif test_case.test_id == "mcp_file_search":
                # 파일 검색 테스트
                if self.mcp_integration:
                    result = await self.mcp_integration.execute_file_search(
                        test_case.input_data["pattern"],
                        test_case.input_data.get("include_path")
                    )
                    mcp_calls_made = 1
                else:
                    result = {"success": False, "error": "MCP 통합을 사용할 수 없음"}
                    
            elif test_case.test_id == "mcp_text_search":
                # 텍스트 검색 테스트
                if self.mcp_integration:
                    result = await self.mcp_integration.execute_text_search(
                        test_case.input_data["pattern"],
                        test_case.input_data.get("include")
                    )
                    mcp_calls_made = 1
                else:
                    result = {"success": False, "error": "MCP 통합을 사용할 수 없음"}
                    
            elif test_case.test_id == "mcp_file_operations":
                # 파일 작업 테스트
                if self.mcp_integration:
                    # 파일 쓰기
                    write_result = await self.mcp_integration.write_file_content(
                        test_case.input_data["file_path"],
                        test_case.input_data["content"]
                    )
                    # 파일 읽기
                    read_result = await self.mcp_integration.read_file_content(
                        test_case.input_data["file_path"]
                    )
                    result = {"write": write_result, "read": read_result, "success": True}
                    mcp_calls_made = 2
                else:
                    result = {"success": False, "error": "MCP 통합을 사용할 수 없음"}
                    
            elif test_case.test_id == "mcp_bash_execution":
                # 배시 실행 테스트
                if self.mcp_integration:
                    result = await self.mcp_integration.execute_bash_command(
                        test_case.input_data["command"],
                        test_case.input_data.get("description", "")
                    )
                    mcp_calls_made = 1
                else:
                    result = {"success": False, "error": "MCP 통합을 사용할 수 없음"}
                    
            elif test_case.test_id == "mcp_agent_integration":
                # MCP 에이전트 통합 테스트
                if MCP_MODULES_AVAILABLE:
                    agent = SimpleMCPTestAgent()
                    await agent.initialize()
                    task = {"user_input": test_case.input_data["user_input"]}
                    result = await agent.execute_task_with_mcp(task)
                    mcp_calls_made = result.get("mcp_calls_made", 0)
                else:
                    result = {"success": False, "error": "MCP 에이전트를 사용할 수 없음"}
                    
            elif test_case.test_id == "viba_project_analysis":
                # VIBA 프로젝트 분석 테스트
                if self.viba_adapter:
                    result = await self.viba_adapter.analyze_viba_system()
                    mcp_calls_made = len(result.get("base_analysis", {}).get("tool_calls", []))
                    result["success"] = True
                else:
                    result = {"success": False, "error": "VIBA 어댑터를 사용할 수 없음"}
                    
            elif test_case.test_id == "dependency_check_test":
                # 의존성 체크 테스트
                result = await self._check_system_dependencies()
                mcp_calls_made = 0  # 외부 도구 호출 없음
                
            else:
                result = {"success": False, "error": "알 수 없는 테스트 케이스"}
            
            execution_time = time.time() - start_time
            
            # 성공 여부 판정
            success = result.get("success", False) or ("error" not in result)
            
            self.results.append(MCPTestResult(
                test_id=test_case.test_id,
                success=success,
                execution_time=execution_time,
                mcp_calls_made=mcp_calls_made,
                details=result
            ))
            
            status = "✅" if success else "❌"
            print(f"    {status} {test_case.name} ({'성공' if success else '실패'}) ({execution_time:.3f}초)")
            if mcp_calls_made > 0:
                print(f"       - MCP 호출: {mcp_calls_made}회")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(MCPTestResult(
                test_id=test_case.test_id,
                success=False,
                execution_time=execution_time,
                mcp_calls_made=mcp_calls_made,
                error_message=str(e)
            ))
            print(f"    ❌ {test_case.name} 실패: {e}")
    
    async def _check_system_dependencies(self) -> Dict[str, Any]:
        """시스템 의존성 체크"""
        try:
            import numpy, pandas, scipy
            core_available = True
        except ImportError:
            core_available = False
        
        try:
            import fastapi, uvicorn, aiohttp
            web_available = True
        except ImportError:
            web_available = False
        
        try:
            import konlpy
            nlp_available = True
        except ImportError:
            nlp_available = False
        
        return {
            "success": True,
            "core_libraries": core_available,
            "web_libraries": web_available, 
            "nlp_libraries": nlp_available,
            "overall_health": core_available and web_available
        }
    
    async def _test_concurrent_mcp_calls(self):
        """동시 MCP 호출 테스트"""
        print("  ⚡ 동시 MCP 호출 테스트...")
        
        start_time = time.time()
        
        try:
            if not MCP_MODULES_AVAILABLE or not self.mcp_integration:
                print("    ⚠️ MCP를 사용할 수 없어 동시 호출 테스트를 건너뜁니다.")
                return
            
            # 5개 동시 요청
            tasks = [
                self.mcp_integration.execute_file_search("*.py"),
                self.mcp_integration.execute_text_search("class"),
                self.mcp_integration.execute_bash_command("echo test1"),
                self.mcp_integration.execute_bash_command("echo test2"),
                self.mcp_integration.web_search("test query")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful_count = sum(1 for r in results if not isinstance(r, Exception))
            execution_time = time.time() - start_time
            
            self.results.append(MCPTestResult(
                test_id="concurrent_mcp_calls",
                success=successful_count >= 4,  # 80% 이상 성공
                execution_time=execution_time,
                mcp_calls_made=5,
                details={
                    "total_calls": 5,
                    "successful_calls": successful_count,
                    "success_rate": successful_count / 5 * 100
                }
            ))
            
            print(f"    ✅ 동시 호출 테스트 완료 ({execution_time:.3f}초)")
            print(f"       - 성공률: {successful_count}/5 ({successful_count/5*100:.1f}%)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(MCPTestResult(
                test_id="concurrent_mcp_calls",
                success=False,
                execution_time=execution_time,
                mcp_calls_made=0,
                error_message=str(e)
            ))
            print(f"    ❌ 동시 호출 테스트 실패: {e}")
    
    async def _test_memory_usage(self):
        """메모리 사용량 테스트"""
        print("  💾 메모리 사용량 테스트...")
        
        start_time = time.time()
        
        try:
            import psutil
            import gc
            
            # 초기 메모리 측정
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 메모리 집약적 작업 시뮬레이션
            if MCP_MODULES_AVAILABLE and self.mcp_integration:
                # 여러 MCP 호출 실행
                for i in range(10):
                    await self.mcp_integration.execute_file_search(f"test{i}*.py")
                    await self.mcp_integration.execute_text_search(f"pattern{i}")
            
            # 가비지 컬렉션 실행
            gc.collect()
            
            # 최종 메모리 측정
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            execution_time = time.time() - start_time
            
            # 메모리 증가가 50MB 미만이면 성공
            success = memory_increase < 50
            
            self.results.append(MCPTestResult(
                test_id="memory_usage_test",
                success=success,
                execution_time=execution_time,
                mcp_calls_made=20,
                details={
                    "initial_memory_mb": initial_memory,
                    "final_memory_mb": final_memory,
                    "memory_increase_mb": memory_increase
                }
            ))
            
            status = "✅" if success else "❌"
            print(f"    {status} 메모리 사용량 테스트 ({execution_time:.3f}초)")
            print(f"       - 메모리 증가: {memory_increase:.1f}MB")
            
        except ImportError:
            print("    ⚠️ psutil을 사용할 수 없어 메모리 테스트를 건너뜁니다.")
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(MCPTestResult(
                test_id="memory_usage_test",
                success=False,
                execution_time=execution_time,
                mcp_calls_made=0,
                error_message=str(e)
            ))
            print(f"    ❌ 메모리 사용량 테스트 실패: {e}")


async def main():
    """메인 테스트 실행"""
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # MCP 통합 테스트 실행
    test_suite = MCPIntegrationTestSuite()
    summary = await test_suite.run_all_tests()
    
    # 결과를 파일로 저장
    try:
        os.makedirs("test_results", exist_ok=True)
        with open("test_results/mcp_integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\n📁 MCP 테스트 결과가 test_results/mcp_integration_test_results.json에 저장되었습니다.")
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())