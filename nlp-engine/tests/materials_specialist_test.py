"""
재료 전문가 AI 에이전트 테스트
=============================

재료 전문가 AI 에이전트의 기능을 종합적으로 테스트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import sys
import os
import json
import time
from typing import Dict, Any

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# 재료 전문가 에이전트 임포트
from ai.agents.materials_specialist import MaterialsSpecialistAgent


async def test_materials_specialist_initialization():
    """재료 전문가 에이전트 초기화 테스트"""
    print("\n🧪 재료 전문가 AI 에이전트 초기화 테스트...")
    
    try:
        specialist = MaterialsSpecialistAgent()
        
        # 초기화
        init_result = await specialist.initialize()
        
        print(f"   ✅ 초기화 결과: {init_result}")
        print(f"   ✅ 에이전트 ID: {specialist.agent_id}")
        print(f"   ✅ 이름: {specialist.name}")
        print(f"   ✅ 능력: {[cap.value for cap in specialist.capabilities]}")
        
        return specialist
        
    except Exception as e:
        print(f"   ❌ 초기화 실패: {e}")
        return None


async def test_material_recommendation():
    """재료 추천 테스트"""
    print("\n🏗️ 재료 추천 테스트...")
    
    specialist = MaterialsSpecialistAgent()
    await specialist.initialize()
    
    # 주거용 건물 재료 추천
    test_input = {
        "task_type": "material_recommendation",
        "building_type": "residential",
        "climate_zone": "temperate",
        "budget_level": "medium",
        "sustainability_priority": "high",
        "performance_requirements": {
            "thermal_performance": "good",
            "durability": "high"
        }
    }
    
    result = await specialist.process_task_async(test_input)
    
    print(f"   ✅ 추천 성공: {result['success']}")
    
    if result['success']:
        summary = result['summary']
        print(f"   ✅ 총 재료 수: {summary['total_materials']}")
        print(f"   ✅ 예상 비용: {summary['estimated_cost']:,}원")
        print(f"   ✅ 지속가능성 점수: {summary['overall_sustainability']:.1f}")
        print(f"   ✅ 성능 점수: {summary['performance_score']:.1f}")
        
        # 카테고리별 추천 재료 출력
        recommendations = result['recommendations']
        for category, materials in recommendations.items():
            print(f"\n   📦 {category} 카테고리:")
            if isinstance(materials, list) and materials:
                for i, material in enumerate(materials[:2]):  # 상위 2개만 출력
                    print(f"      {i+1}. {material.get('name', 'Unknown')} - {material.get('cost_per_m2', 0):,}원/m²")
            else:
                print(f"      재료 데이터 없음")
    
    return result


async def test_performance_analysis():
    """성능 분석 테스트"""
    print("\n📊 재료 성능 분석 테스트...")
    
    specialist = MaterialsSpecialistAgent()
    await specialist.initialize()
    
    test_input = {
        "task_type": "performance_analysis",
        "analysis_type": "comprehensive",
        "materials": [
            {"material_id": "concrete_c24", "name": "일반콘크리트 C24"},
            {"material_id": "steel_sm490", "name": "구조용강재 SM490"},
            {"material_id": "glulam_24f", "name": "집성재 24f-v5"}
        ]
    }
    
    result = await specialist.process_task_async(test_input)
    
    print(f"   ✅ 분석 성공: {result['success']}")
    
    if result['success']:
        individual_results = result['individual_results']
        print(f"   ✅ 분석된 재료 수: {len(individual_results)}")
        
        for material_id, analysis in individual_results.items():
            print(f"\n   🔍 {material_id} 분석 결과:")
            print(f"      - 열성능: {analysis['thermal_performance']['grade']}")
            print(f"      - 구조성능: {analysis['structural_performance']['grade']}")
            print(f"      - 내구성: {analysis['durability_analysis']['grade']}")
            print(f"      - 환경영향: {analysis['environmental_impact']['grade']}")
            print(f"      - 경제성: {analysis['cost_effectiveness']['grade']}")
        
        overall = result['overall_assessment']
        print(f"\n   📈 전체 평가: {overall['overall_grade']}")
        print(f"   💪 주요 강점: {', '.join(overall['key_strengths'])}")
        print(f"   🔧 개선 영역: {', '.join(overall['improvement_areas'])}")
    
    return result


async def test_cost_optimization():
    """비용 최적화 테스트"""
    print("\n💰 비용 최적화 테스트...")
    
    specialist = MaterialsSpecialistAgent()
    await specialist.initialize()
    
    test_input = {
        "task_type": "cost_optimization",
        "budget_constraint": 5000000,  # 500만원 예산
        "performance_targets": {
            "thermal_performance": 7.0,
            "structural_safety": 8.0,
            "durability": 25  # 25년 이상
        },
        "building_requirements": {
            "building_type": "residential",
            "area_sqm": 100,
            "climate_zone": "temperate"
        }
    }
    
    result = await specialist.process_task_async(test_input)
    
    print(f"   ✅ 최적화 성공: {result['success']}")
    
    if result['success']:
        optimization = result['optimization_results']
        print(f"   ✅ 비용 절감: {result['cost_savings']:,}원")
        print(f"   ✅ 성능 영향: {result['performance_impact']}")
    
    return result


async def test_sustainability_assessment():
    """지속가능성 평가 테스트"""
    print("\n🌱 지속가능성 평가 테스트...")
    
    specialist = MaterialsSpecialistAgent()
    await specialist.initialize()
    
    test_input = {
        "task_type": "sustainability_assessment",
        "materials": [
            {"material_id": "cellulose_insulation", "name": "셀룰로오스 단열재"},
            {"material_id": "eps_insulation", "name": "EPS 단열재"},
            {"material_id": "rockwool_insulation", "name": "암면 단열재"}
        ],
        "criteria": ["carbon_footprint", "recyclability", "durability", "renewable_content"]
    }
    
    result = await specialist.process_task_async(test_input)
    
    print(f"   ✅ 평가 성공: {result['success']}")
    
    if result['success']:
        scores = result['individual_scores']
        print(f"   ✅ 전체 지속가능성 점수: {result['overall_sustainability_score']:.1f}")
        print(f"   ✅ 지속가능성 등급: {result['sustainability_grade']}")
        
        print("\n   📊 개별 재료 점수:")
        for material_id, score in scores.items():
            print(f"      - {material_id}: {score:.1f}점")
        
        improvements = result['improvement_suggestions']
        if improvements:
            print(f"\n   💡 개선 제안:")
            for suggestion in improvements:
                print(f"      - {suggestion}")
    
    return result


async def test_material_comparison():
    """재료 비교 테스트"""
    print("\n⚖️ 재료 비교 테스트...")
    
    specialist = MaterialsSpecialistAgent()
    await specialist.initialize()
    
    test_input = {
        "task_type": "material_comparison",
        "materials": [
            {"material_id": "concrete_c24", "name": "일반콘크리트"},
            {"material_id": "steel_sm490", "name": "구조용강재"},
            {"material_id": "glulam_24f", "name": "집성재"}
        ],
        "criteria": ["cost", "performance", "sustainability", "durability"]
    }
    
    result = await specialist.process_task_async(test_input)
    
    print(f"   ✅ 비교 성공: {result['success']}")
    
    if result['success']:
        matrix = result['comparison_matrix']
        recommendations = result['recommendations']
        
        print("\n   📊 비교 매트릭스:")
        for criterion, scores in matrix.items():
            print(f"      {criterion}: {scores}")
        
        print("\n   🏆 추천 순위:")
        for i, rec in enumerate(recommendations):
            print(f"      {i+1}. {rec['material_id']} (점수: {rec['overall_score']:.1f}) - {rec['recommendation']}")
            if rec['strengths']:
                print(f"         강점: {', '.join(rec['strengths'])}")
            if rec['weaknesses']:
                print(f"         약점: {', '.join(rec['weaknesses'])}")
    
    return result


async def test_comprehensive_analysis():
    """종합 재료 분석 테스트"""
    print("\n🎯 종합 재료 분석 테스트...")
    
    specialist = MaterialsSpecialistAgent()
    await specialist.initialize()
    
    # 자연어 입력 테스트
    test_cases = [
        {
            "user_input": "친환경적이고 경제적인 주택용 단열재를 추천해주세요",
            "context": {"building_type": "residential", "area_sqm": 120}
        },
        {
            "user_input": "고급 상업건물에 적합한 외벽 마감재를 비교 분석해주세요",
            "context": {"building_type": "commercial", "budget_level": "high"}
        },
        {
            "user_input": "비용을 최적화하면서 성능을 유지할 수 있는 구조재를 찾아주세요",
            "context": {"budget_constraint": 8000000, "performance_priority": "high"}
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n   테스트 케이스 {i+1}: {test_case['user_input']}")
        
        result = await specialist.process_task_async(test_case)
        
        if result['success']:
            summary = result['summary']
            print(f"      ✅ 분석 완료")
            print(f"      ✅ 분석된 재료: {summary.get('total_materials_analyzed', 0)}개")
            print(f"      ✅ 핵심 인사이트: {len(summary.get('key_insights', []))}개")
            print(f"      ✅ 다음 단계: {len(summary.get('next_steps', []))}개")
            
            if summary.get('top_recommendations'):
                print("      🏆 주요 추천:")
                for rec in summary['top_recommendations'][:3]:
                    print(f"         - {rec['category']}: {rec['material']} ({rec['reason']})")
        else:
            print(f"      ❌ 분석 실패: {result.get('error', '알 수 없는 오류')}")
        
        results.append(result)
    
    return results


async def test_performance_benchmarks():
    """성능 벤치마크 테스트"""
    print("\n⚡ 성능 벤치마크 테스트...")
    
    specialist = MaterialsSpecialistAgent()
    await specialist.initialize()
    
    # 다양한 크기의 요청으로 성능 측정
    test_scenarios = [
        {"name": "단순 추천", "materials": 5},
        {"name": "중간 분석", "materials": 15},
        {"name": "대규모 분석", "materials": 30}
    ]
    
    performance_results = []
    
    for scenario in test_scenarios:
        print(f"   📊 {scenario['name']} 시나리오...")
        
        # 테스트 데이터 생성
        materials = [
            {"material_id": f"material_{i}", "name": f"재료 {i}"}
            for i in range(scenario['materials'])
        ]
        
        test_input = {
            "task_type": "material_comparison",
            "materials": materials,
            "criteria": ["cost", "performance", "sustainability", "durability"]
        }
        
        start_time = time.time()
        result = await specialist.process_task_async(test_input)
        execution_time = time.time() - start_time
        
        performance_results.append({
            "scenario": scenario['name'],
            "materials_count": scenario['materials'],
            "execution_time": execution_time,
            "success": result['success'],
            "throughput": scenario['materials'] / execution_time if execution_time > 0 else 0
        })
        
        print(f"      ⏱️ 실행 시간: {execution_time:.3f}초")
        print(f"      📈 처리량: {scenario['materials'] / execution_time:.1f} 재료/초")
        print(f"      ✅ 성공: {result['success']}")
    
    # 성능 요약
    print("\n   📊 성능 요약:")
    for perf in performance_results:
        print(f"      {perf['scenario']}: {perf['execution_time']:.3f}초 ({perf['throughput']:.1f} 재료/초)")
    
    return performance_results


async def main():
    """메인 테스트 실행"""
    print("🏗️ 재료 전문가 AI 에이전트 종합 테스트 시작")
    print("=" * 60)
    
    test_results = {}
    
    try:
        # 1. 초기화 테스트
        specialist = await test_materials_specialist_initialization()
        if not specialist:
            print("❌ 초기화 실패로 테스트 중단")
            return
        
        # 2. 재료 추천 테스트
        test_results['recommendation'] = await test_material_recommendation()
        
        # 3. 성능 분석 테스트
        test_results['performance'] = await test_performance_analysis()
        
        # 4. 비용 최적화 테스트
        test_results['cost_optimization'] = await test_cost_optimization()
        
        # 5. 지속가능성 평가 테스트
        test_results['sustainability'] = await test_sustainability_assessment()
        
        # 6. 재료 비교 테스트
        test_results['comparison'] = await test_material_comparison()
        
        # 7. 종합 분석 테스트
        test_results['comprehensive'] = await test_comprehensive_analysis()
        
        # 8. 성능 벤치마크 테스트
        test_results['performance_benchmark'] = await test_performance_benchmarks()
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 완료!")
        
        # 전체 결과 요약
        print("\n📊 테스트 결과 요약:")
        
        success_count = 0
        total_tests = 0
        
        for test_name, result in test_results.items():
            if test_name == 'comprehensive':
                # 종합 분석은 여러 결과가 있음
                sub_success = sum(1 for r in result if r.get('success', False))
                sub_total = len(result)
                success_count += sub_success
                total_tests += sub_total
                print(f"   ✅ {test_name}: {sub_success}/{sub_total} 성공")
            elif test_name == 'performance_benchmark':
                # 성능 벤치마크는 별도 처리
                bench_success = sum(1 for r in result if r.get('success', False))
                bench_total = len(result)
                success_count += bench_success
                total_tests += bench_total
                print(f"   ✅ {test_name}: {bench_success}/{bench_total} 성공")
            else:
                # 일반 테스트
                is_success = result.get('success', False) if isinstance(result, dict) else False
                success_count += 1 if is_success else 0
                total_tests += 1
                status = "✅" if is_success else "❌"
                print(f"   {status} {test_name}: {'성공' if is_success else '실패'}")
        
        print(f"\n🏆 전체 성공률: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
        
        if success_count == total_tests:
            print("🎊 재료 전문가 AI 에이전트가 완벽하게 동작합니다!")
        else:
            print("⚠️ 일부 테스트에서 문제가 발견되었습니다.")
        
        return test_results
        
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    asyncio.run(main())