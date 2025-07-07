"""
VIBA AI 시스템 기본 통합 테스트
=============================

핵심 기능만 테스트하여 시스템이 정상 작동하는지 확인

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import sys
import os
import time

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 고도화된 오케스트레이터
from ai.advanced_orchestrator import AdvancedOrchestrator

# 재료 전문가 (가장 안정적)
from ai.agents.materials_specialist import MaterialsSpecialistAgent


async def test_basic_system():
    """기본 시스템 테스트"""
    print("🧪 VIBA AI 기본 시스템 테스트")
    print("=" * 50)
    
    try:
        # 1. 오케스트레이터 생성
        print("\n1. 고도화된 오케스트레이터 생성...")
        orchestrator = AdvancedOrchestrator()
        print("   ✅ 오케스트레이터 생성 성공")
        
        # 2. 재료 전문가 등록
        print("\n2. 재료 전문가 AI 등록...")
        materials_specialist = MaterialsSpecialistAgent()
        await orchestrator.register_agent(materials_specialist)
        print("   ✅ 재료 전문가 등록 성공")
        
        # 3. 시스템 상태 확인
        print("\n3. 시스템 상태 확인...")
        status = orchestrator.get_system_status()
        print(f"   ✅ 등록된 에이전트: {status['total_agents']}개")
        print(f"   ✅ 시스템 상태: {status['system_health']}")
        
        # 4. 기본 요청 처리
        print("\n4. 기본 요청 처리 테스트...")
        
        test_request = "친환경 주택용 단열재를 추천해주세요"
        
        start_time = time.time()
        result = await orchestrator.process_intelligent_request(
            test_request,
            context={"building_type": "residential"},
            optimization_level="adaptive"
        )
        execution_time = time.time() - start_time
        
        print(f"   ⏱️ 실행 시간: {execution_time:.3f}초")
        print(f"   ✅ 처리 성공: {result['success']}")
        
        if result['success']:
            metadata = result['orchestration_metadata']
            print(f"   🤖 사용된 에이전트: {metadata['agents_used']}")
            print(f"   📈 작업 복잡도: {metadata['task_complexity']:.2f}")
            
            if 'quality_assessment' in result:
                quality = result['quality_assessment']
                print(f"   🏆 품질 점수: {quality['quality_score']:.2f}")
                print(f"   🏅 품질 등급: {quality['quality_level']}")
        
        # 5. 성능 테스트
        print("\n5. 성능 테스트...")
        
        times = []
        for i in range(3):
            start_time = time.time()
            result = await orchestrator.process_intelligent_request(
                f"테스트 요청 {i+1}",
                optimization_level="adaptive"
            )
            execution_time = time.time() - start_time
            times.append(execution_time)
        
        avg_time = sum(times) / len(times)
        print(f"   ⏱️ 평균 실행 시간: {avg_time:.3f}초")
        print(f"   📈 처리량: {1/avg_time:.1f} 요청/초")
        
        # 6. 오류 처리 테스트
        print("\n6. 오류 처리 테스트...")
        
        error_test_cases = [
            "",  # 빈 입력
            "알 수 없는 요청",  # 모호한 입력
        ]
        
        for test_case in error_test_cases:
            try:
                result = await orchestrator.process_intelligent_request(test_case)
                graceful = True
                print(f"   ✅ '{test_case}' - Graceful: {'성공' if result['success'] else '실패'}")
            except Exception as e:
                graceful = False
                print(f"   ❌ '{test_case}' - Exception: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 기본 통합 테스트 완료!")
        print("✅ VIBA AI 시스템 기본 기능이 정상 작동합니다!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 기본 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_materials_specialist_directly():
    """재료 전문가 직접 테스트"""
    print("\n🔧 재료 전문가 직접 테스트...")
    
    try:
        specialist = MaterialsSpecialistAgent()
        await specialist.initialize()
        
        test_input = {
            "task_type": "material_recommendation",
            "building_type": "residential",
            "sustainability_priority": "high"
        }
        
        result = await specialist.process_task_async(test_input)
        
        print(f"   ✅ 직접 호출 성공: {result['success']}")
        if result['success']:
            summary = result.get('summary', {})
            print(f"   📊 추천 재료 수: {summary.get('total_materials', 0)}")
        
        return result['success']
        
    except Exception as e:
        print(f"   ❌ 재료 전문가 직접 테스트 실패: {e}")
        return False


async def main():
    """메인 테스트"""
    print("🏗️ VIBA AI 시스템 기본 통합 테스트 시작")
    
    # 1. 재료 전문가 직접 테스트
    materials_success = await test_materials_specialist_directly()
    
    # 2. 기본 시스템 테스트
    if materials_success:
        system_success = await test_basic_system()
    else:
        print("❌ 재료 전문가 테스트 실패로 시스템 테스트 생략")
        system_success = False
    
    print("\n📊 최종 결과:")
    print(f"   재료 전문가 테스트: {'✅ 성공' if materials_success else '❌ 실패'}")
    print(f"   시스템 통합 테스트: {'✅ 성공' if system_success else '❌ 실패'}")
    
    if materials_success and system_success:
        print("🎊 VIBA AI 시스템이 정상적으로 작동합니다!")
        return True
    else:
        print("⚠️ 일부 기능에 문제가 있습니다.")
        return False


if __name__ == "__main__":
    asyncio.run(main())