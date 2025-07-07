"""
VIBA AI 시스템 최종 통합 테스트
==============================

모든 AI 에이전트와 고도화된 오케스트레이터의 완전한 통합 동작을 검증

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import sys
import os
import json
import time
from typing import Dict, Any, List

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 고도화된 오케스트레이터
from ai.advanced_orchestrator import AdvancedOrchestrator

# 모든 AI 에이전트들
from ai.agents.design_theorist import DesignTheoristAgent
from ai.agents.bim_specialist import BIMSpecialistAgent
from ai.agents.performance_analyst import PerformanceAnalystAgent
from ai.agents.design_reviewer import DesignReviewerAgent
from ai.agents.architectural_design_specialist import ArchitecturalDesignSpecialistAgent
from ai.agents.materials_specialist import MaterialsSpecialistAgent

# MCP 통합
try:
    from ai.agents.mcp_integration_hub import MCPIntegrationHubAgent
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("MCP 통합 허브 사용불가 - 테스트에서 제외")


async def test_system_initialization():
    """시스템 초기화 테스트"""
    print("\n🚀 VIBA AI 시스템 초기화 테스트...")
    
    try:
        # 고도화된 오케스트레이터 생성
        orchestrator = AdvancedOrchestrator()
        print("   ✅ 고도화된 오케스트레이터 생성 성공")
        
        # 모든 AI 에이전트 생성 및 등록
        agents = []
        
        # 1. 설계 이론가 AI
        try:
            design_theorist = DesignTheoristAgent()
            await orchestrator.register_agent(design_theorist)
            agents.append(design_theorist)
            print("   ✅ 설계 이론가 AI 등록 성공")
        except Exception as e:
            print(f"   ❌ 설계 이론가 AI 등록 실패: {e}")
        
        # 2. BIM 전문가 AI
        try:
            bim_specialist = BIMSpecialistAgent()
            await orchestrator.register_agent(bim_specialist)
            agents.append(bim_specialist)
            print("   ✅ BIM 전문가 AI 등록 성공")
        except Exception as e:
            print(f"   ❌ BIM 전문가 AI 등록 실패: {e}")
        
        # 3. 성능 분석가 AI
        try:
            performance_analyst = PerformanceAnalystAgent()
            await orchestrator.register_agent(performance_analyst)
            agents.append(performance_analyst)
            print("   ✅ 성능 분석가 AI 등록 성공")
        except Exception as e:
            print(f"   ❌ 성능 분석가 AI 등록 실패: {e}")
        
        # 4. 설계 검토자 AI
        try:
            design_reviewer = DesignReviewerAgent()
            await orchestrator.register_agent(design_reviewer)
            agents.append(design_reviewer)
            print("   ✅ 설계 검토자 AI 등록 성공")
        except Exception as e:
            print(f"   ❌ 설계 검토자 AI 등록 실패: {e}")
        
        # 5. 건축 디자인 전문가 AI
        try:
            arch_specialist = ArchitecturalDesignSpecialistAgent()
            await orchestrator.register_agent(arch_specialist)
            agents.append(arch_specialist)
            print("   ✅ 건축 디자인 전문가 AI 등록 성공")
        except Exception as e:
            print(f"   ❌ 건축 디자인 전문가 AI 등록 실패: {e}")
        
        # 6. 재료 전문가 AI
        try:
            materials_specialist = MaterialsSpecialistAgent()
            await orchestrator.register_agent(materials_specialist)
            agents.append(materials_specialist)
            print("   ✅ 재료 전문가 AI 등록 성공")
        except Exception as e:
            print(f"   ❌ 재료 전문가 AI 등록 실패: {e}")
        
        # 7. MCP 통합 허브 AI (선택사항)
        if MCP_AVAILABLE:
            try:
                mcp_hub = MCPIntegrationHubAgent()
                await orchestrator.register_agent(mcp_hub)
                agents.append(mcp_hub)
                print("   ✅ MCP 통합 허브 AI 등록 성공")
            except Exception as e:
                print(f"   ❌ MCP 통합 허브 AI 등록 실패: {e}")
        
        # 시스템 상태 확인
        system_status = orchestrator.get_system_status()
        print(f"\n   📊 시스템 상태:")
        print(f"      - 등록된 에이전트: {system_status['total_agents']}개")
        print(f"      - 시스템 상태: {system_status['system_health']}")
        print(f"      - 최적화 기능: {system_status['optimization_status']}")
        
        return orchestrator, agents
        
    except Exception as e:
        print(f"   ❌ 시스템 초기화 실패: {e}")
        return None, []


async def test_simple_design_workflow(orchestrator):
    """간단한 설계 워크플로우 테스트"""
    print("\n🏠 간단한 설계 워크플로우 테스트...")
    
    try:
        # 간단한 주거용 건물 설계 요청
        user_request = "강남에 3층 현대식 주택을 설계해주세요. 친환경적이고 에너지 효율적으로 부탁드립니다."
        
        context = {
            "building_type": "residential",
            "location": "강남",
            "floors": 3,
            "style": "modern",
            "sustainability_priority": "high",
            "energy_efficiency": "high"
        }
        
        start_time = time.time()
        result = await orchestrator.process_intelligent_request(
            user_request,
            context=context,
            optimization_level="adaptive"
        )
        execution_time = time.time() - start_time
        
        print(f"   ⏱️ 실행 시간: {execution_time:.3f}초")
        print(f"   ✅ 처리 성공: {result['success']}")
        
        if result['success']:
            metadata = result['orchestration_metadata']
            print(f"   🤖 사용된 에이전트: {len(metadata['agents_used'])}개")
            print(f"   📈 작업 복잡도: {metadata['task_complexity']:.2f}")
            
            if 'quality_assessment' in result:
                quality = result['quality_assessment']
                print(f"   🏆 품질 점수: {quality['quality_score']:.2f}")
                print(f"   🏅 품질 등급: {quality['quality_level']}")
            
            if 'recommendations' in result:
                recommendations = result['recommendations']
                print(f"   💡 추천사항: {len(recommendations)}개")
                for rec in recommendations[:3]:  # 상위 3개만 출력
                    print(f"      - {rec}")
        else:
            print(f"   ❌ 처리 실패: {result.get('error', '알 수 없는 오류')}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ 워크플로우 테스트 실패: {e}")
        return None


async def test_complex_design_workflow(orchestrator):
    """복잡한 설계 워크플로우 테스트"""
    print("\n🏢 복잡한 설계 워크플로우 테스트...")
    
    try:
        # 복잡한 상업용 건물 설계 요청
        user_request = """
        서울 강남구에 20층 규모의 복합상업건물을 설계해주세요.
        
        요구사항:
        - 1-3층: 상업시설 (카페, 레스토랑, 쇼핑몰)
        - 4-15층: 오피스
        - 16-20층: 호텔
        - 지하 2층: 주차장
        - 옥상: 스카이라운지
        
        특별 요구사항:
        - 최고 수준의 에너지 효율성
        - 한국 전통 건축 요소 포함
        - 지진 내진 설계
        - 스마트 빌딩 시스템
        - 친환경 LEED 플래티넘 등급 취득
        """
        
        context = {
            "building_type": "mixed_use_commercial",
            "location": "강남구",
            "floors": 20,
            "basement": 2,
            "complexity": "very_high",
            "budget_level": "premium",
            "sustainability_priority": "highest",
            "certification_target": "LEED_Platinum",
            "special_requirements": [
                "seismic_design",
                "smart_building",
                "traditional_elements",
                "energy_efficiency"
            ]
        }
        
        start_time = time.time()
        result = await orchestrator.process_intelligent_request(
            user_request,
            context=context,
            optimization_level="adaptive"
        )
        execution_time = time.time() - start_time
        
        print(f"   ⏱️ 실행 시간: {execution_time:.3f}초")
        print(f"   ✅ 처리 성공: {result['success']}")
        
        if result['success']:
            metadata = result['orchestration_metadata']
            print(f"   🤖 사용된 에이전트: {len(metadata['agents_used'])}개")
            print(f"   📊 에이전트 목록: {metadata['agents_used']}")
            print(f"   📈 작업 복잡도: {metadata['task_complexity']:.2f}")
            print(f"   🔧 최적화 적용: {metadata.get('optimization_applied', 0):.2f}")
            
            if 'quality_assessment' in result:
                quality = result['quality_assessment']
                print(f"   🏆 품질 점수: {quality['quality_score']:.2f}")
                print(f"   🏅 품질 등급: {quality['quality_level']}")
            
            # 다음 단계 예측 확인
            if 'next_steps' in result:
                next_steps = result['next_steps']
                print(f"   🔮 예측된 다음 단계: {len(next_steps)}개")
                for step in next_steps[:3]:
                    print(f"      - {step}")
        else:
            print(f"   ❌ 처리 실패: {result.get('error', '알 수 없는 오류')}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ 복잡한 워크플로우 테스트 실패: {e}")
        return None


async def test_materials_integration_workflow(orchestrator):
    """재료 통합 워크플로우 테스트"""
    print("\n🔧 재료 통합 워크플로우 테스트...")
    
    try:
        # 재료 전문가 AI가 포함된 설계 요청
        user_request = """
        친환경 주택을 설계하되, 특히 재료 선택에 중점을 두어주세요.
        
        재료 관련 요구사항:
        - 탄소발자국 최소화
        - 재활용 가능 재료 우선
        - 지역 재료 사용
        - 장기 내구성
        - 경제적 효율성
        
        건물 요구사항:
        - 2층 단독주택
        - 패시브하우스 수준의 에너지 효율
        - 현대적 디자인과 전통 요소 조화
        """
        
        context = {
            "building_type": "residential",
            "sustainability_focus": "materials",
            "energy_standard": "passive_house",
            "material_priorities": [
                "low_carbon_footprint",
                "recyclable",
                "local_sourcing",
                "durability",
                "cost_effectiveness"
            ]
        }
        
        start_time = time.time()
        result = await orchestrator.process_intelligent_request(
            user_request,
            context=context,
            optimization_level="adaptive"
        )
        execution_time = time.time() - start_time
        
        print(f"   ⏱️ 실행 시간: {execution_time:.3f}초")
        print(f"   ✅ 처리 성공: {result['success']}")
        
        if result['success']:
            metadata = result['orchestration_metadata']
            
            # 재료 전문가가 포함되었는지 확인
            agents_used = metadata['agents_used']
            materials_included = 'materials_specialist' in agents_used
            print(f"   🔧 재료 전문가 포함: {'✅' if materials_included else '❌'}")
            print(f"   🤖 사용된 에이전트: {agents_used}")
            
            if 'quality_assessment' in result:
                quality = result['quality_assessment']
                print(f"   🏆 품질 점수: {quality['quality_score']:.2f}")
                print(f"   🏅 품질 등급: {quality['quality_level']}")
        else:
            print(f"   ❌ 처리 실패: {result.get('error', '알 수 없는 오류')}")
        
        return result
        
    except Exception as e:
        print(f"   ❌ 재료 통합 워크플로우 테스트 실패: {e}")
        return None


async def test_performance_optimization():
    """성능 최적화 테스트"""
    print("\n⚡ 성능 최적화 테스트...")
    
    try:
        orchestrator = AdvancedOrchestrator()
        
        # 최소한의 에이전트만 등록 (속도 테스트용)
        design_theorist = DesignTheoristAgent()
        materials_specialist = MaterialsSpecialistAgent()
        
        await orchestrator.register_agent(design_theorist)
        await orchestrator.register_agent(materials_specialist)
        
        # 다양한 최적화 레벨로 테스트
        optimization_levels = ["sequential", "parallel", "adaptive"]
        performance_results = []
        
        test_request = "간단한 2층 주택을 설계해주세요"
        
        for level in optimization_levels:
            print(f"   📊 {level} 최적화 테스트...")
            
            times = []
            for i in range(3):  # 3회 반복 테스트
                start_time = time.time()
                result = await orchestrator.process_intelligent_request(
                    test_request,
                    optimization_level=level
                )
                execution_time = time.time() - start_time
                times.append(execution_time)
            
            avg_time = sum(times) / len(times)
            performance_results.append({
                "level": level,
                "avg_time": avg_time,
                "min_time": min(times),
                "max_time": max(times)
            })
            
            print(f"      ⏱️ 평균 시간: {avg_time:.3f}초")
            print(f"      📈 범위: {min(times):.3f}s ~ {max(times):.3f}s")
        
        # 성능 비교
        print(f"\n   📊 성능 비교 결과:")
        fastest = min(performance_results, key=lambda x: x['avg_time'])
        for perf in performance_results:
            improvement = ((fastest['avg_time'] / perf['avg_time']) - 1) * 100
            status = "🏆" if perf == fastest else f"({improvement:+.1f}%)"
            print(f"      {perf['level']}: {perf['avg_time']:.3f}초 {status}")
        
        return performance_results
        
    except Exception as e:
        print(f"   ❌ 성능 최적화 테스트 실패: {e}")
        return None


async def test_error_handling_and_resilience(orchestrator):
    """오류 처리 및 복원력 테스트"""
    print("\n🛡️ 오류 처리 및 복원력 테스트...")
    
    try:
        test_cases = [
            {
                "name": "빈 입력",
                "request": "",
                "expected": "graceful_failure"
            },
            {
                "name": "모호한 요청", 
                "request": "뭔가 만들어주세요",
                "expected": "clarification_request"
            },
            {
                "name": "불가능한 요청",
                "request": "달에 100층 건물을 지어주세요",
                "expected": "alternative_suggestion"
            },
            {
                "name": "상충하는 요구사항",
                "request": "1평에 10층 초고층 건물을 저비용으로 지어주세요",
                "expected": "constraint_explanation"
            }
        ]
        
        results = []
        
        for test_case in test_cases:
            print(f"   🧪 {test_case['name']} 테스트...")
            
            try:
                result = await orchestrator.process_intelligent_request(
                    test_case['request']
                )
                
                success = result.get('success', False)
                error_msg = result.get('error', '')
                
                print(f"      결과: {'성공' if success else '실패'}")
                if not success and error_msg:
                    print(f"      오류: {error_msg[:100]}...")
                
                results.append({
                    "test": test_case['name'],
                    "success": success,
                    "graceful": True,  # 예외가 발생하지 않으면 graceful
                    "has_error_message": bool(error_msg)
                })
                
            except Exception as e:
                print(f"      ❌ 예외 발생: {e}")
                results.append({
                    "test": test_case['name'],
                    "success": False,
                    "graceful": False,
                    "exception": str(e)
                })
        
        # 복원력 평가
        graceful_count = sum(1 for r in results if r.get('graceful', False))
        total_tests = len(results)
        resilience_score = graceful_count / total_tests
        
        print(f"\n   📊 복원력 점수: {resilience_score:.2f} ({graceful_count}/{total_tests})")
        
        return results
        
    except Exception as e:
        print(f"   ❌ 복원력 테스트 실패: {e}")
        return None


async def test_system_scalability(orchestrator):
    """시스템 확장성 테스트"""
    print("\n📈 시스템 확장성 테스트...")
    
    try:
        # 동시 요청 처리 테스트
        concurrent_levels = [1, 3, 5]
        scalability_results = []
        
        base_request = "간단한 주택을 설계해주세요"
        
        for concurrent_count in concurrent_levels:
            print(f"   🔀 동시 요청 {concurrent_count}개 테스트...")
            
            # 동시 요청 생성
            tasks = []
            for i in range(concurrent_count):
                task = orchestrator.process_intelligent_request(
                    f"{base_request} (요청 {i+1})"
                )
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # 결과 분석
            successful_results = [r for r in results if isinstance(r, dict) and r.get('success', False)]
            success_rate = len(successful_results) / len(results)
            avg_time_per_request = total_time / concurrent_count
            throughput = concurrent_count / total_time
            
            scalability_results.append({
                "concurrent_requests": concurrent_count,
                "total_time": total_time,
                "success_rate": success_rate,
                "avg_time_per_request": avg_time_per_request,
                "throughput": throughput
            })
            
            print(f"      ⏱️ 총 시간: {total_time:.3f}초")
            print(f"      ✅ 성공률: {success_rate:.2f}")
            print(f"      📈 처리량: {throughput:.1f} 요청/초")
        
        # 확장성 분석
        print(f"\n   📊 확장성 분석:")
        for result in scalability_results:
            print(f"      {result['concurrent_requests']}개 동시: "
                  f"{result['throughput']:.1f} req/s, "
                  f"성공률 {result['success_rate']:.2f}")
        
        return scalability_results
        
    except Exception as e:
        print(f"   ❌ 확장성 테스트 실패: {e}")
        return None


async def main():
    """메인 통합 테스트 실행"""
    print("🏗️ VIBA AI 시스템 최종 통합 테스트")
    print("=" * 70)
    
    test_results = {}
    
    try:
        # 1. 시스템 초기화 테스트
        orchestrator, agents = await test_system_initialization()
        if not orchestrator:
            print("❌ 시스템 초기화 실패로 테스트 중단")
            return
        
        test_results['initialization'] = {
            "success": True,
            "agents_count": len(agents)
        }
        
        # 2. 간단한 설계 워크플로우 테스트
        simple_result = await test_simple_design_workflow(orchestrator)
        test_results['simple_workflow'] = simple_result
        
        # 3. 복잡한 설계 워크플로우 테스트
        complex_result = await test_complex_design_workflow(orchestrator)
        test_results['complex_workflow'] = complex_result
        
        # 4. 재료 통합 워크플로우 테스트
        materials_result = await test_materials_integration_workflow(orchestrator)
        test_results['materials_workflow'] = materials_result
        
        # 5. 성능 최적화 테스트
        performance_result = await test_performance_optimization()
        test_results['performance_optimization'] = performance_result
        
        # 6. 오류 처리 및 복원력 테스트
        resilience_result = await test_error_handling_and_resilience(orchestrator)
        test_results['error_resilience'] = resilience_result
        
        # 7. 시스템 확장성 테스트
        scalability_result = await test_system_scalability(orchestrator)
        test_results['scalability'] = scalability_result
        
        print("\n" + "=" * 70)
        print("🎉 모든 통합 테스트 완료!")
        
        # 전체 결과 요약
        print("\n📊 최종 테스트 결과 요약:")
        
        # 초기화 결과
        init_result = test_results['initialization']
        print(f"   ✅ 시스템 초기화: 성공 ({init_result['agents_count']}개 에이전트)")
        
        # 워크플로우 테스트 결과
        workflow_tests = ['simple_workflow', 'complex_workflow', 'materials_workflow']
        workflow_success = 0
        for test_name in workflow_tests:
            result = test_results.get(test_name)
            if result and result.get('success', False):
                workflow_success += 1
                print(f"   ✅ {test_name}: 성공")
            else:
                print(f"   ❌ {test_name}: 실패")
        
        # 성능 테스트 결과
        perf_result = test_results.get('performance_optimization')
        if perf_result:
            fastest_time = min(p['avg_time'] for p in perf_result)
            print(f"   ⚡ 성능 최적화: 최고 {fastest_time:.3f}초")
        
        # 복원력 테스트 결과
        resilience_result = test_results.get('error_resilience')
        if resilience_result:
            graceful_count = sum(1 for r in resilience_result if r.get('graceful', False))
            total_resilience = len(resilience_result)
            resilience_score = graceful_count / total_resilience
            print(f"   🛡️ 시스템 복원력: {resilience_score:.2f} ({graceful_count}/{total_resilience})")
        
        # 확장성 테스트 결과
        scalability_result = test_results.get('scalability')
        if scalability_result:
            max_throughput = max(s['throughput'] for s in scalability_result)
            print(f"   📈 최대 처리량: {max_throughput:.1f} 요청/초")
        
        # 최종 평가
        total_workflow_success = workflow_success / len(workflow_tests)
        
        print(f"\n🏆 전체 시스템 성능:")
        print(f"   - 워크플로우 성공률: {total_workflow_success:.2f}")
        print(f"   - 등록된 AI 에이전트: {init_result['agents_count']}개")
        
        if total_workflow_success >= 0.8:
            print("🎊 VIBA AI 시스템이 완벽하게 통합되어 동작합니다!")
        elif total_workflow_success >= 0.6:
            print("⚠️ VIBA AI 시스템이 대부분 정상 동작하지만 일부 개선이 필요합니다.")
        else:
            print("❌ VIBA AI 시스템에 중대한 문제가 있습니다.")
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ 통합 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(main())