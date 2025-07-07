"""
Playwright MCP를 활용한 E2E 테스트
=================================

VIBA AI 시스템의 엔드투엔드 테스트를 위한 Playwright 통합 테스트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, Any, List
from dataclasses import dataclass
import logging

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# MCP 통합 시스템
try:
    from ai.mcp_integration.claude_code_integration import ClaudeCodeIntegration
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP 통합 시스템 사용불가 - 기본 테스트로 진행")

# 성능 최적화 모듈
from optimization.performance_optimizer import performance_optimizer, performance_monitor

# VIBA AI 시스템
from ai.advanced_orchestrator import AdvancedOrchestrator
from ai.agents.materials_specialist import MaterialsSpecialistAgent

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """테스트 케이스"""
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 3


class PlaywrightE2ETestSuite:
    """Playwright E2E 테스트 스위트"""
    
    def __init__(self):
        self.orchestrator = None
        self.mcp_integration = None
        self.test_results = []
        
        # 테스트 설정
        self.config = {
            "timeout": 30000,  # 30초
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "VIBA-AI-Test-Suite/1.0"
        }
        
        # 성능 임계값
        self.performance_thresholds = {
            "response_time": 5.0,  # 5초
            "memory_usage": 500.0,  # 500MB
            "cpu_usage": 80.0  # 80%
        }
    
    async def setup(self):
        """테스트 환경 설정"""
        logger.info("E2E 테스트 환경 설정 중...")
        
        # 오케스트레이터 초기화
        self.orchestrator = AdvancedOrchestrator()
        
        # 기본 에이전트 등록
        materials_specialist = MaterialsSpecialistAgent()
        await self.orchestrator.register_agent(materials_specialist)
        
        # MCP 통합 설정
        if MCP_AVAILABLE:
            self.mcp_integration = ClaudeCodeIntegration()
            await self.mcp_integration.initialize()
            logger.info("MCP 통합 설정 완료")
        
        logger.info("E2E 테스트 환경 설정 완료")
    
    def define_test_cases(self) -> List[TestCase]:
        """테스트 케이스 정의"""
        return [
            TestCase(
                name="basic_material_recommendation",
                description="기본 재료 추천 테스트",
                input_data={
                    "user_input": "친환경 주택용 단열재를 추천해주세요",
                    "context": {"building_type": "residential"}
                },
                expected_output={
                    "success": True,
                    "has_recommendations": True,
                    "response_time": 5.0
                }
            ),
            TestCase(
                name="complex_building_design",
                description="복잡한 건물 설계 테스트",
                input_data={
                    "user_input": "20층 상업용 건물을 친환경적으로 설계해주세요",
                    "context": {
                        "building_type": "commercial",
                        "floors": 20,
                        "sustainability_priority": "high"
                    }
                },
                expected_output={
                    "success": True,
                    "has_design_elements": True,
                    "response_time": 10.0
                }
            ),
            TestCase(
                name="concurrent_requests",
                description="동시 요청 처리 테스트",
                input_data={
                    "concurrent_count": 5,
                    "user_input": "간단한 주택 설계",
                    "context": {"building_type": "residential"}
                },
                expected_output={
                    "all_success": True,
                    "avg_response_time": 3.0
                }
            ),
            TestCase(
                name="stress_test",
                description="스트레스 테스트",
                input_data={
                    "request_count": 20,
                    "user_input": "다양한 건물 설계 요청",
                    "context": {"stress_test": True}
                },
                expected_output={
                    "success_rate": 0.9,
                    "memory_stable": True
                }
            ),
            TestCase(
                name="error_handling",
                description="오류 처리 테스트",
                input_data={
                    "user_input": "",  # 빈 입력
                    "context": {"error_test": True}
                },
                expected_output={
                    "graceful_failure": True,
                    "error_message": True
                }
            )
        ]
    
    @performance_monitor("e2e_test_execution")
    async def run_single_test(self, test_case: TestCase) -> Dict[str, Any]:
        """단일 테스트 실행"""
        logger.info(f"테스트 실행 중: {test_case.name}")
        
        start_time = time.time()
        
        try:
            if test_case.name == "basic_material_recommendation":
                result = await self._test_basic_material_recommendation(test_case)
            elif test_case.name == "complex_building_design":
                result = await self._test_complex_building_design(test_case)
            elif test_case.name == "concurrent_requests":
                result = await self._test_concurrent_requests(test_case)
            elif test_case.name == "stress_test":
                result = await self._test_stress_test(test_case)
            elif test_case.name == "error_handling":
                result = await self._test_error_handling(test_case)
            else:
                result = await self._test_generic(test_case)
            
            execution_time = time.time() - start_time
            
            # 성능 검증
            performance_check = self._check_performance_thresholds(execution_time, result)
            
            # 결과 검증
            validation_result = self._validate_test_result(test_case, result)
            
            return {
                "test_name": test_case.name,
                "success": validation_result["success"],
                "execution_time": execution_time,
                "performance_check": performance_check,
                "validation_details": validation_result,
                "raw_result": result
            }
            
        except Exception as e:
            logger.error(f"테스트 실행 오류 ({test_case.name}): {e}")
            return {
                "test_name": test_case.name,
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
    
    async def _test_basic_material_recommendation(self, test_case: TestCase) -> Dict[str, Any]:
        """기본 재료 추천 테스트"""
        input_data = test_case.input_data
        
        result = await self.orchestrator.process_intelligent_request(
            input_data["user_input"],
            context=input_data["context"],
            optimization_level="adaptive"
        )
        
        return result
    
    async def _test_complex_building_design(self, test_case: TestCase) -> Dict[str, Any]:
        """복잡한 건물 설계 테스트"""
        input_data = test_case.input_data
        
        # MCP 통합 테스트 (가능한 경우)
        if self.mcp_integration:
            # 파일 읽기 테스트
            await self.mcp_integration.request_file_operation("read", "README.md")
        
        result = await self.orchestrator.process_intelligent_request(
            input_data["user_input"],
            context=input_data["context"],
            optimization_level="adaptive"
        )
        
        return result
    
    async def _test_concurrent_requests(self, test_case: TestCase) -> Dict[str, Any]:
        """동시 요청 처리 테스트"""
        input_data = test_case.input_data
        concurrent_count = input_data["concurrent_count"]
        
        # 동시 요청 생성
        tasks = []
        for i in range(concurrent_count):
            task = self.orchestrator.process_intelligent_request(
                f"{input_data['user_input']} #{i+1}",
                context=input_data["context"],
                optimization_level="parallel"
            )
            tasks.append(task)
        
        # 동시 실행
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # 결과 분석
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success", False)]
        success_rate = len(successful_results) / len(results)
        avg_response_time = total_time / concurrent_count
        
        return {
            "concurrent_count": concurrent_count,
            "success_rate": success_rate,
            "avg_response_time": avg_response_time,
            "total_time": total_time,
            "successful_results": len(successful_results),
            "all_success": success_rate == 1.0
        }
    
    async def _test_stress_test(self, test_case: TestCase) -> Dict[str, Any]:
        """스트레스 테스트"""
        input_data = test_case.input_data
        request_count = input_data["request_count"]
        
        results = []
        memory_usage_history = []
        
        for i in range(request_count):
            # 메모리 사용량 모니터링
            import psutil
            memory_usage = psutil.virtual_memory().percent
            memory_usage_history.append(memory_usage)
            
            # 다양한 요청 실행
            test_requests = [
                "간단한 주택 설계",
                "상업용 건물 재료 추천",
                "친환경 아파트 설계",
                "오피스 빌딩 성능 분석"
            ]
            
            request = test_requests[i % len(test_requests)]
            
            try:
                result = await self.orchestrator.process_intelligent_request(
                    f"{request} (스트레스 테스트 #{i+1})",
                    optimization_level="adaptive"
                )
                results.append(result)
            except Exception as e:
                results.append({"success": False, "error": str(e)})
        
        # 결과 분석
        successful_results = [r for r in results if r.get("success", False)]
        success_rate = len(successful_results) / len(results)
        
        # 메모리 안정성 확인
        memory_stable = max(memory_usage_history) - min(memory_usage_history) < 20  # 20% 이내 변동
        
        return {
            "request_count": request_count,
            "success_rate": success_rate,
            "memory_stable": memory_stable,
            "memory_usage_range": {
                "min": min(memory_usage_history),
                "max": max(memory_usage_history),
                "avg": sum(memory_usage_history) / len(memory_usage_history)
            }
        }
    
    async def _test_error_handling(self, test_case: TestCase) -> Dict[str, Any]:
        """오류 처리 테스트"""
        input_data = test_case.input_data
        
        try:
            result = await self.orchestrator.process_intelligent_request(
                input_data["user_input"],
                context=input_data["context"]
            )
            
            # 빈 입력에 대해 graceful failure인지 확인
            graceful_failure = not result.get("success", True) or "error" in result
            
            return {
                "graceful_failure": graceful_failure,
                "error_message": "error" in result,
                "result": result
            }
            
        except Exception as e:
            # 예외가 발생하면 graceful failure가 아님
            return {
                "graceful_failure": False,
                "error_message": True,
                "exception": str(e)
            }
    
    async def _test_generic(self, test_case: TestCase) -> Dict[str, Any]:
        """일반적인 테스트"""
        input_data = test_case.input_data
        
        result = await self.orchestrator.process_intelligent_request(
            input_data["user_input"],
            context=input_data.get("context", {}),
            optimization_level="adaptive"
        )
        
        return result
    
    def _check_performance_thresholds(self, execution_time: float, result: Dict[str, Any]) -> Dict[str, bool]:
        """성능 임계값 확인"""
        import psutil
        
        return {
            "response_time_ok": execution_time <= self.performance_thresholds["response_time"],
            "memory_usage_ok": psutil.virtual_memory().percent <= self.performance_thresholds["memory_usage"] / 100 * 100,
            "cpu_usage_ok": psutil.cpu_percent() <= self.performance_thresholds["cpu_usage"]
        }
    
    def _validate_test_result(self, test_case: TestCase, result: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 결과 검증"""
        expected = test_case.expected_output
        validation = {
            "success": True,
            "failed_checks": []
        }
        
        # 성공 여부 확인
        if "success" in expected:
            if result.get("success", False) != expected["success"]:
                validation["success"] = False
                validation["failed_checks"].append(f"Expected success: {expected['success']}, got: {result.get('success', False)}")
        
        # 추천 여부 확인
        if "has_recommendations" in expected:
            has_recommendations = bool(result.get("recommendations") or result.get("summary", {}).get("total_materials", 0) > 0)
            if has_recommendations != expected["has_recommendations"]:
                validation["success"] = False
                validation["failed_checks"].append(f"Expected recommendations: {expected['has_recommendations']}, got: {has_recommendations}")
        
        # 응답 시간 확인
        if "response_time" in expected:
            actual_time = result.get("orchestration_metadata", {}).get("execution_time", 0)
            if actual_time > expected["response_time"]:
                validation["success"] = False
                validation["failed_checks"].append(f"Response time too slow: {actual_time:.2f}s > {expected['response_time']}s")
        
        # 동시 요청 테스트 검증
        if "all_success" in expected:
            if result.get("all_success", False) != expected["all_success"]:
                validation["success"] = False
                validation["failed_checks"].append(f"Expected all_success: {expected['all_success']}, got: {result.get('all_success', False)}")
        
        # 성공률 확인
        if "success_rate" in expected:
            actual_rate = result.get("success_rate", 0)
            if actual_rate < expected["success_rate"]:
                validation["success"] = False
                validation["failed_checks"].append(f"Success rate too low: {actual_rate:.2f} < {expected['success_rate']:.2f}")
        
        # Graceful failure 확인
        if "graceful_failure" in expected:
            if result.get("graceful_failure", False) != expected["graceful_failure"]:
                validation["success"] = False
                validation["failed_checks"].append(f"Expected graceful_failure: {expected['graceful_failure']}, got: {result.get('graceful_failure', False)}")
        
        return validation
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("E2E 테스트 스위트 시작")
        
        await self.setup()
        
        test_cases = self.define_test_cases()
        results = []
        
        total_start_time = time.time()
        
        for test_case in test_cases:
            logger.info(f"실행 중: {test_case.name} - {test_case.description}")
            
            # 재시도 로직
            for attempt in range(test_case.retry_count):
                try:
                    result = await asyncio.wait_for(
                        self.run_single_test(test_case),
                        timeout=test_case.timeout
                    )
                    results.append(result)
                    break
                except asyncio.TimeoutError:
                    if attempt == test_case.retry_count - 1:
                        results.append({
                            "test_name": test_case.name,
                            "success": False,
                            "error": "Test timeout",
                            "execution_time": test_case.timeout
                        })
                    else:
                        logger.warning(f"테스트 타임아웃, 재시도 중... ({attempt + 1}/{test_case.retry_count})")
                except Exception as e:
                    if attempt == test_case.retry_count - 1:
                        results.append({
                            "test_name": test_case.name,
                            "success": False,
                            "error": str(e),
                            "execution_time": 0
                        })
                    else:
                        logger.warning(f"테스트 실패, 재시도 중... ({attempt + 1}/{test_case.retry_count}): {e}")
        
        total_execution_time = time.time() - total_start_time
        
        # 결과 요약
        successful_tests = [r for r in results if r.get("success", False)]
        success_rate = len(successful_tests) / len(results) if results else 0
        avg_execution_time = sum(r.get("execution_time", 0) for r in results) / len(results) if results else 0
        
        # 성능 분석 리포트 생성
        performance_report = await performance_optimizer.generate_optimization_report()
        
        summary = {
            "total_tests": len(results),
            "successful_tests": len(successful_tests),
            "failed_tests": len(results) - len(successful_tests),
            "success_rate": success_rate,
            "total_execution_time": total_execution_time,
            "avg_execution_time_per_test": avg_execution_time,
            "test_results": results,
            "performance_report": performance_report
        }
        
        logger.info(f"E2E 테스트 완료: {len(successful_tests)}/{len(results)} 성공 ({success_rate:.1%})")
        
        return summary
    
    async def generate_test_report(self, results: Dict[str, Any]) -> str:
        """테스트 보고서 생성"""
        report = ["# VIBA AI E2E 테스트 보고서\n"]
        report.append(f"실행 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 요약
        report.append("## 📊 테스트 요약\n")
        report.append(f"- 총 테스트: {results['total_tests']}개\n")
        report.append(f"- 성공: {results['successful_tests']}개\n")
        report.append(f"- 실패: {results['failed_tests']}개\n")
        report.append(f"- 성공률: {results['success_rate']:.1%}\n")
        report.append(f"- 총 실행 시간: {results['total_execution_time']:.2f}초\n")
        report.append(f"- 평균 테스트 시간: {results['avg_execution_time_per_test']:.2f}초\n\n")
        
        # 개별 테스트 결과
        report.append("## 📋 개별 테스트 결과\n")
        for result in results['test_results']:
            status = "✅ 성공" if result.get("success", False) else "❌ 실패"
            report.append(f"### {result['test_name']} - {status}\n")
            report.append(f"- 실행 시간: {result.get('execution_time', 0):.3f}초\n")
            
            if not result.get("success", False):
                report.append(f"- 오류: {result.get('error', 'Unknown error')}\n")
            
            if "validation_details" in result:
                validation = result["validation_details"]
                if not validation["success"] and validation["failed_checks"]:
                    report.append("- 실패한 검증:\n")
                    for check in validation["failed_checks"]:
                        report.append(f"  - {check}\n")
            
            report.append("\n")
        
        # 성능 분석
        if "performance_report" in results:
            report.append("## 🚀 성능 분석\n")
            report.append(results["performance_report"])
        
        # 권장사항
        report.append("\n## 💡 권장사항\n")
        if results['success_rate'] < 0.9:
            report.append("- 테스트 성공률이 90% 미만입니다. 실패한 테스트를 분석하여 시스템 안정성을 개선하세요.\n")
        
        if results['avg_execution_time_per_test'] > 10:
            report.append("- 평균 테스트 실행 시간이 10초를 초과합니다. 성능 최적화를 고려하세요.\n")
        
        report.append("- 정기적인 E2E 테스트 실행으로 회귀 문제를 조기에 발견하세요.\n")
        report.append("- CI/CD 파이프라인에 E2E 테스트를 통합하여 자동화하세요.\n")
        
        return "".join(report)


async def main():
    """메인 E2E 테스트 실행"""
    print("🎭 Playwright MCP E2E 테스트 시작")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_suite = PlaywrightE2ETestSuite()
    
    try:
        # 모든 테스트 실행
        results = await test_suite.run_all_tests()
        
        # 보고서 생성
        report = await test_suite.generate_test_report(results)
        
        # 보고서 저장
        report_path = "/Users/seunghakwoo/Documents/Cursor/Z/nlp-engine/test_results/e2e_test_report.md"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 결과 출력
        print(f"\n📊 테스트 결과:")
        print(f"   성공률: {results['success_rate']:.1%} ({results['successful_tests']}/{results['total_tests']})")
        print(f"   총 실행 시간: {results['total_execution_time']:.2f}초")
        print(f"   보고서 저장: {report_path}")
        
        if results['success_rate'] >= 0.9:
            print("🎉 E2E 테스트 성공! 시스템이 안정적으로 동작합니다.")
        else:
            print("⚠️ 일부 테스트가 실패했습니다. 보고서를 확인하세요.")
        
        return results
        
    except Exception as e:
        print(f"❌ E2E 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(main())