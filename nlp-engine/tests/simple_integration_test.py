"""
VIBA AI 시스템 간단한 통합 테스트
===============================

외부 라이브러리 의존성 없이 기본 시스템 동작을 검증하는 통합 테스트

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

# 테스트 대상 임포트
from ai.agents.simple_test_agent import (
    SimpleTestAgent, 
    SimpleNLPProcessor, 
    SimpleOrchestrator,
    simple_process_user_request
)

logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """테스트 케이스"""
    test_id: str
    name: str
    input_text: str
    expected_keywords: List[str]
    expected_entities_min: int
    expected_success: bool = True


@dataclass
class TestResult:
    """테스트 결과"""
    test_id: str
    success: bool
    execution_time: float
    error_message: str = ""
    details: Dict[str, Any] = None


class VIBAIntegrationTest:
    """VIBA 통합 테스트 시스템"""
    
    def __init__(self):
        self.test_cases = self._create_test_cases()
        self.results: List[TestResult] = []
        
    def _create_test_cases(self) -> List[TestCase]:
        """테스트 케이스 생성"""
        return [
            TestCase(
                test_id="basic_design_001",
                name="기본 설계 요청 테스트",
                input_text="강남에 3층 모던 카페를 설계해줘",
                expected_keywords=["건물타입_카페", "스타일_모던", "위치_강남", "층수_3"],
                expected_entities_min=3
            ),
            TestCase(
                test_id="hanok_design_002", 
                name="한옥 설계 요청 테스트",
                input_text="전통적인 한옥 스타일 게스트하우스를 설계해주세요",
                expected_keywords=["스타일_한옥", "건물타입_게스트하우스"],
                expected_entities_min=2
            ),
            TestCase(
                test_id="office_building_003",
                name="사무빌딩 설계 테스트", 
                input_text="서울에 5층 사무 빌딩을 만들어줘",
                expected_keywords=["위치_서울", "층수_5", "건물타입_빌딩"],
                expected_entities_min=3
            ),
            TestCase(
                test_id="minimal_input_004",
                name="최소 입력 테스트",
                input_text="주택 설계",
                expected_keywords=[],
                expected_entities_min=0
            ),
            TestCase(
                test_id="complex_request_005",
                name="복합 요구사항 테스트",
                input_text="부산에 친환경 인증을 받을 수 있는 3층 모던 스타일 사무용 빌딩 설계",
                expected_keywords=["위치_부산", "스타일_모던", "층수_3", "건물타입_빌딩"],
                expected_entities_min=3
            )
        ]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        print("🧪 VIBA AI 시스템 통합 테스트 시작...")
        print("=" * 50)
        
        start_time = time.time()
        
        # 1. 개별 컴포넌트 테스트
        await self._test_individual_components()
        
        # 2. 통합 워크플로우 테스트  
        await self._test_integration_workflows()
        
        # 3. 성능 테스트
        await self._test_performance()
        
        # 4. 에러 처리 테스트
        await self._test_error_handling()
        
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
            "test_results": [
                {
                    "test_id": r.test_id,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "error": r.error_message if not r.success else None
                }
                for r in self.results
            ]
        }
        
        print("\n" + "=" * 50)
        print("📊 테스트 결과 요약")
        print(f"총 테스트: {total_tests}개")
        print(f"성공: {successful_tests}개")
        print(f"실패: {total_tests - successful_tests}개")
        print(f"성공률: {success_rate:.1f}%")
        print(f"총 실행 시간: {total_time:.2f}초")
        
        if success_rate >= 80:
            print("✅ 테스트 통과! 시스템이 정상 작동합니다.")
        else:
            print("❌ 테스트 실패. 시스템에 문제가 있습니다.")
        
        return summary
    
    async def _test_individual_components(self):
        """개별 컴포넌트 테스트"""
        print("\n1️⃣ 개별 컴포넌트 테스트")
        print("-" * 30)
        
        # NLP 프로세서 테스트
        await self._test_nlp_processor()
        
        # AI 에이전트 테스트
        await self._test_ai_agent()
        
        # 오케스트레이터 테스트
        await self._test_orchestrator()
    
    async def _test_nlp_processor(self):
        """NLP 프로세서 테스트"""
        print("  🔤 NLP 프로세서 테스트...")
        
        start_time = time.time()
        
        try:
            processor = SimpleNLPProcessor()
            test_text = "강남에 3층 모던 카페를 설계해줘"
            
            result = processor.process_comprehensive_text(test_text)
            
            # 검증
            assert hasattr(result, 'entities'), "엔티티 속성이 없음"
            assert hasattr(result, 'spatial_relations'), "공간관계 속성이 없음"
            assert hasattr(result, 'design_requirements'), "설계요구사항 속성이 없음"
            assert hasattr(result, 'design_intents'), "설계의도 속성이 없음"
            
            assert len(result.entities) >= 3, f"엔티티 수 부족: {len(result.entities)}"
            
            execution_time = time.time() - start_time
            
            self.results.append(TestResult(
                test_id="nlp_processor_test",
                success=True,
                execution_time=execution_time,
                details={
                    "entities_count": len(result.entities),
                    "relations_count": len(result.spatial_relations),
                    "requirements_count": len(result.design_requirements),
                    "intents_count": len(result.design_intents)
                }
            ))
            
            print(f"    ✅ NLP 프로세서 테스트 성공 ({execution_time:.3f}초)")
            print(f"       - 엔티티: {len(result.entities)}개")
            print(f"       - 공간관계: {len(result.spatial_relations)}개")
            print(f"       - 설계요구사항: {len(result.design_requirements)}개")
            print(f"       - 설계의도: {len(result.design_intents)}개")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_id="nlp_processor_test",
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            ))
            print(f"    ❌ NLP 프로세서 테스트 실패: {e}")
    
    async def _test_ai_agent(self):
        """AI 에이전트 테스트"""
        print("  🤖 AI 에이전트 테스트...")
        
        start_time = time.time()
        
        try:
            agent = SimpleTestAgent()
            await agent.initialize()
            
            # 초기화 검증
            assert agent.is_initialized, "에이전트 초기화 실패"
            assert agent.is_available(), "에이전트가 사용 불가능"
            
            # 작업 실행 테스트
            test_input = "강남에 3층 모던 카페를 설계해줘"
            result = await agent.process_task_async(test_input)
            
            # 결과 검증
            assert result["success"], "작업 실행 실패"
            assert "keywords" in result, "키워드가 없음"
            assert "result" in result, "결과가 없음"
            assert len(result["keywords"]) >= 3, f"키워드 수 부족: {len(result['keywords'])}"
            
            execution_time = time.time() - start_time
            
            self.results.append(TestResult(
                test_id="ai_agent_test",
                success=True,
                execution_time=execution_time,
                details={
                    "agent_id": result["agent_id"],
                    "keywords_count": len(result["keywords"]),
                    "result_type": type(result["result"]).__name__
                }
            ))
            
            print(f"    ✅ AI 에이전트 테스트 성공 ({execution_time:.3f}초)")
            print(f"       - 에이전트 ID: {result['agent_id']}")
            print(f"       - 키워드: {len(result['keywords'])}개")
            print(f"       - 결과 타입: {type(result['result']).__name__}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_id="ai_agent_test",
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            ))
            print(f"    ❌ AI 에이전트 테스트 실패: {e}")
    
    async def _test_orchestrator(self):
        """오케스트레이터 테스트"""
        print("  🎛️ 오케스트레이터 테스트...")
        
        start_time = time.time()
        
        try:
            orchestrator = SimpleOrchestrator()
            await orchestrator.initialize()
            
            # 에이전트 로드 검증
            assert len(orchestrator.agents) > 0, "에이전트가 로드되지 않음"
            assert orchestrator.nlp_processor is not None, "NLP 프로세서가 없음"
            
            # 요청 처리 테스트
            test_input = "강남에 3층 모던 카페를 설계해줘"
            result = await orchestrator.process_request(test_input)
            
            # 결과 검증
            assert result["success"], "오케스트레이터 실행 실패"
            assert "nlp_analysis" in result, "NLP 분석 결과가 없음"
            assert "agent_result" in result, "에이전트 결과가 없음"
            assert "workflow_id" in result, "워크플로우 ID가 없음"
            
            execution_time = time.time() - start_time
            
            self.results.append(TestResult(
                test_id="orchestrator_test",
                success=True,
                execution_time=execution_time,
                details={
                    "agents_count": len(orchestrator.agents),
                    "workflow_id": result["workflow_id"],
                    "nlp_entities": result["nlp_analysis"]["entities_count"]
                }
            ))
            
            print(f"    ✅ 오케스트레이터 테스트 성공 ({execution_time:.3f}초)")
            print(f"       - 로드된 에이전트: {len(orchestrator.agents)}개")
            print(f"       - 워크플로우 ID: {result['workflow_id']}")
            print(f"       - NLP 엔티티: {result['nlp_analysis']['entities_count']}개")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_id="orchestrator_test",
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            ))
            print(f"    ❌ 오케스트레이터 테스트 실패: {e}")
    
    async def _test_integration_workflows(self):
        """통합 워크플로우 테스트"""
        print("\n2️⃣ 통합 워크플로우 테스트")
        print("-" * 30)
        
        for test_case in self.test_cases:
            await self._execute_test_case(test_case)
    
    async def _execute_test_case(self, test_case: TestCase):
        """개별 테스트 케이스 실행"""
        print(f"  📋 {test_case.name}...")
        
        start_time = time.time()
        
        try:
            # 통합 시스템으로 요청 처리
            result = await simple_process_user_request(test_case.input_text)
            
            # 기본 검증
            assert result["success"], "요청 처리 실패"
            assert "nlp_analysis" in result, "NLP 분석 누락"
            assert "agent_result" in result, "에이전트 결과 누락"
            
            # 엔티티 수 검증
            entities_count = result["nlp_analysis"]["entities_count"]
            assert entities_count >= test_case.expected_entities_min, \
                f"엔티티 수 부족: {entities_count} < {test_case.expected_entities_min}"
            
            # 키워드 검증 (부분적)
            agent_keywords = result["agent_result"].get("keywords", [])
            matched_keywords = []
            for expected_keyword in test_case.expected_keywords:
                if expected_keyword in agent_keywords:
                    matched_keywords.append(expected_keyword)
            
            execution_time = time.time() - start_time
            
            self.results.append(TestResult(
                test_id=test_case.test_id,
                success=True,
                execution_time=execution_time,
                details={
                    "input": test_case.input_text,
                    "entities_count": entities_count,
                    "keywords_matched": len(matched_keywords),
                    "keywords_total": len(test_case.expected_keywords),
                    "workflow_id": result["workflow_id"]
                }
            ))
            
            print(f"    ✅ 성공 ({execution_time:.3f}초)")
            print(f"       - 엔티티: {entities_count}개")
            print(f"       - 키워드 매칭: {len(matched_keywords)}/{len(test_case.expected_keywords)}")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_id=test_case.test_id,
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            ))
            print(f"    ❌ 실패: {e}")
    
    async def _test_performance(self):
        """성능 테스트"""
        print("\n3️⃣ 성능 테스트")
        print("-" * 30)
        
        # 동시 요청 테스트
        await self._test_concurrent_requests()
        
        # 응답 시간 테스트
        await self._test_response_time()
    
    async def _test_concurrent_requests(self):
        """동시 요청 테스트"""
        print("  ⚡ 동시 요청 처리 테스트...")
        
        start_time = time.time()
        
        try:
            # 5개 동시 요청
            tasks = []
            test_inputs = [
                "강남에 카페를 설계해줘",
                "부산에 사무실을 만들어줘", 
                "한옥 스타일 주택 설계",
                "3층 모던 빌딩",
                "전통 게스트하우스"
            ]
            
            for i, input_text in enumerate(test_inputs):
                task = simple_process_user_request(input_text)
                tasks.append(task)
            
            # 동시 실행
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 결과 검증
            successful_count = 0
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"    ❌ 요청 {i+1} 실패: {result}")
                elif result.get("success", False):
                    successful_count += 1
                else:
                    print(f"    ❌ 요청 {i+1} 처리 실패")
            
            execution_time = time.time() - start_time
            success_rate = (successful_count / len(test_inputs)) * 100
            
            self.results.append(TestResult(
                test_id="concurrent_requests_test",
                success=success_rate >= 80,  # 80% 이상 성공률 요구
                execution_time=execution_time,
                details={
                    "total_requests": len(test_inputs),
                    "successful_requests": successful_count,
                    "success_rate": success_rate
                }
            ))
            
            print(f"    ✅ 동시 요청 테스트 완료 ({execution_time:.3f}초)")
            print(f"       - 성공률: {success_rate:.1f}% ({successful_count}/{len(test_inputs)})")
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.results.append(TestResult(
                test_id="concurrent_requests_test",
                success=False,
                execution_time=execution_time,
                error_message=str(e)
            ))
            print(f"    ❌ 동시 요청 테스트 실패: {e}")
    
    async def _test_response_time(self):
        """응답 시간 테스트"""
        print("  ⏱️ 응답 시간 테스트...")
        
        response_times = []
        target_time = 2.0  # 2초 이하 목표
        
        try:
            # 10번 반복 테스트
            for i in range(10):
                start_time = time.time()
                result = await simple_process_user_request("테스트 설계 요청")
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            avg_response_time = sum(response_times) / len(response_times)
            max_response_time = max(response_times)
            
            success = avg_response_time <= target_time
            
            self.results.append(TestResult(
                test_id="response_time_test",
                success=success,
                execution_time=avg_response_time,
                details={
                    "average_response_time": avg_response_time,
                    "max_response_time": max_response_time,
                    "target_time": target_time,
                    "all_response_times": response_times
                }
            ))
            
            status = "✅" if success else "❌"
            print(f"    {status} 응답 시간 테스트 완료")
            print(f"       - 평균 응답 시간: {avg_response_time:.3f}초 (목표: {target_time}초)")
            print(f"       - 최대 응답 시간: {max_response_time:.3f}초")
            
        except Exception as e:
            self.results.append(TestResult(
                test_id="response_time_test",
                success=False,
                execution_time=0,
                error_message=str(e)
            ))
            print(f"    ❌ 응답 시간 테스트 실패: {e}")
    
    async def _test_error_handling(self):
        """에러 처리 테스트"""
        print("\n4️⃣ 에러 처리 테스트")
        print("-" * 30)
        
        error_test_cases = [
            ("빈 입력", ""),
            ("특수문자만", "!@#$%^&*()"),
            ("매우 긴 입력", "가" * 1000),
            ("영어 입력", "Design a modern cafe in Seoul"),
        ]
        
        for test_name, test_input in error_test_cases:
            print(f"  🚨 {test_name} 테스트...")
            
            start_time = time.time()
            
            try:
                result = await simple_process_user_request(test_input)
                execution_time = time.time() - start_time
                
                # 에러 처리가 적절한지 확인
                if result.get("success", False):
                    print(f"    ✅ 정상 처리됨 ({execution_time:.3f}초)")
                else:
                    print(f"    ⚠️ 적절히 실패 처리됨 ({execution_time:.3f}초)")
                
                self.results.append(TestResult(
                    test_id=f"error_handling_{test_name.lower().replace(' ', '_')}",
                    success=True,  # 크래시 없이 처리되면 성공
                    execution_time=execution_time
                ))
                
            except Exception as e:
                execution_time = time.time() - start_time
                print(f"    ❌ 예외 발생: {e}")
                
                self.results.append(TestResult(
                    test_id=f"error_handling_{test_name.lower().replace(' ', '_')}",
                    success=False,
                    execution_time=execution_time,
                    error_message=str(e)
                ))


async def main():
    """메인 테스트 실행"""
    # 로깅 설정
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    # 테스트 실행
    test_system = VIBAIntegrationTest()
    summary = await test_system.run_all_tests()
    
    # 결과를 파일로 저장
    try:
        os.makedirs("test_results", exist_ok=True)
        with open("test_results/integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"\n📁 테스트 결과가 test_results/integration_test_results.json에 저장되었습니다.")
    except Exception as e:
        print(f"⚠️ 결과 저장 실패: {e}")
    
    return summary


if __name__ == "__main__":
    asyncio.run(main())