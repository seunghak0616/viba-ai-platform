#!/usr/bin/env python3
"""
VIBA AI 시스템 실행 데모
=====================

전체 VIBA AI 시스템을 실행하고 다양한 건축 설계 요청을 처리하는 데모

@version 1.0
@author VIBA AI Team 
@date 2025.07.06
"""

import asyncio
import sys
import os
import time

# 프로젝트 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# VIBA AI 시스템 컴포넌트
from ai.advanced_orchestrator import AdvancedOrchestrator
from ai.agents.materials_specialist import MaterialsSpecialistAgent

async def initialize_viba_system():
    """VIBA AI 시스템 초기화"""
    print("🏗️ VIBA AI 시스템 초기화 중...")
    print("=" * 60)
    
    # 고도화된 오케스트레이터 생성
    orchestrator = AdvancedOrchestrator()
    
    # AI 에이전트들 등록
    print("\n🤖 AI 에이전트 등록 중...")
    
    # 재료 전문가 AI
    materials_specialist = MaterialsSpecialistAgent()
    await orchestrator.register_agent(materials_specialist)
    print("   ✅ 재료 전문가 AI 등록 완료")
    
    # 시스템 상태 확인
    status = orchestrator.get_system_status()
    print(f"\n📊 시스템 상태:")
    print(f"   - 등록된 에이전트: {status.get('total_agents', 0)}개")
    print(f"   - 시스템 상태: {status.get('system_health', 'unknown')}")
    if 'available_capabilities' in status:
        print(f"   - 사용 가능한 기능: {len(status['available_capabilities'])}개")
    
    print("\n✅ VIBA AI 시스템 초기화 완료!")
    return orchestrator

async def demo_architectural_requests(orchestrator):
    """건축 설계 요청 데모"""
    print("\n🎯 건축 설계 요청 데모 시작")
    print("=" * 60)
    
    # 데모 요청들
    demo_requests = [
        {
            "title": "친환경 주택 설계",
            "request": "30평 규모의 친환경 주택을 설계해주세요. 태양광 패널과 단열재 추천도 포함해서요.",
            "context": {
                "building_type": "residential",
                "area": 100,  # 평방미터
                "sustainability_priority": "high",
                "budget": "medium"
            }
        },
        {
            "title": "상업용 건물 재료 추천",
            "request": "20층 오피스 빌딩의 외벽 마감재를 추천해주세요. 내구성과 미관을 모두 고려해야 합니다.",
            "context": {
                "building_type": "commercial",
                "floors": 20,
                "location": "urban",
                "primary_concern": "durability"
            }
        },
        {
            "title": "펜션 인테리어 설계",
            "request": "제주도에 지을 펜션의 인테리어를 설계해주세요. 자연 친화적이고 편안한 분위기로요.",
            "context": {
                "building_type": "hospitality",
                "location": "jeju",
                "style": "natural",
                "target_guests": "families"
            }
        }
    ]
    
    results = []
    
    for i, demo in enumerate(demo_requests, 1):
        print(f"\n🔄 요청 {i}: {demo['title']}")
        print(f"📝 내용: {demo['request']}")
        
        start_time = time.time()
        
        try:
            result = await orchestrator.process_intelligent_request(
                demo['request'],
                context=demo['context'],
                optimization_level="adaptive"
            )
            
            execution_time = time.time() - start_time
            
            if result['success']:
                print(f"   ✅ 처리 성공 ({execution_time:.3f}초)")
                
                # 메타데이터 출력
                metadata = result.get('orchestration_metadata', {})
                print(f"   🤖 사용된 에이전트: {metadata.get('agents_used', [])}")
                print(f"   📈 작업 복잡도: {metadata.get('task_complexity', 0):.2f}")
                
                # 품질 평가 출력
                if 'quality_assessment' in result:
                    quality = result['quality_assessment']
                    print(f"   🏆 품질 점수: {quality.get('quality_score', 0):.2f}")
                    print(f"   🏅 품질 등급: {quality.get('quality_level', 'unknown')}")
                
                # 결과 요약 출력
                if 'summary' in result:
                    summary = result['summary']
                    if 'total_materials' in summary:
                        print(f"   📊 추천 재료: {summary['total_materials']}개")
                    if 'total_recommendations' in summary:
                        print(f"   💡 추천사항: {summary['total_recommendations']}개")
                
                results.append({
                    'title': demo['title'],
                    'success': True,
                    'execution_time': execution_time,
                    'result': result
                })
                
            else:
                print(f"   ❌ 처리 실패: {result.get('error', 'Unknown error')}")
                results.append({
                    'title': demo['title'],
                    'success': False,
                    'execution_time': execution_time,
                    'error': result.get('error', 'Unknown error')
                })
                
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"   ❌ 예외 발생: {e}")
            results.append({
                'title': demo['title'],
                'success': False,
                'execution_time': execution_time,
                'error': str(e)
            })
    
    return results

def print_demo_summary(results):
    """데모 결과 요약 출력"""
    print("\n📊 데모 결과 요약")
    print("=" * 60)
    
    total_requests = len(results)
    successful_requests = sum(1 for r in results if r['success'])
    success_rate = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
    
    total_time = sum(r['execution_time'] for r in results)
    avg_time = total_time / total_requests if total_requests > 0 else 0
    
    print(f"총 요청 수: {total_requests}개")
    print(f"성공한 요청: {successful_requests}개")
    print(f"성공률: {success_rate:.1f}%")
    print(f"총 실행 시간: {total_time:.3f}초")
    print(f"평균 실행 시간: {avg_time:.3f}초")
    
    print(f"\n📋 개별 결과:")
    for result in results:
        status = "✅ 성공" if result['success'] else "❌ 실패"
        print(f"   {result['title']}: {status} ({result['execution_time']:.3f}초)")
        if not result['success']:
            print(f"      오류: {result.get('error', 'Unknown')}")

async def interactive_mode(orchestrator):
    """대화형 모드"""
    print("\n💬 대화형 모드 시작")
    print("=" * 60)
    print("VIBA AI와 대화해보세요! ('quit' 입력 시 종료)")
    print("예시 질문:")
    print("- '아파트 발코니 확장 설계해줘'")
    print("- '카페 인테리어에 어떤 재료가 좋을까?'")
    print("- '친환경 건축 재료 추천해줘'")
    print()
    
    while True:
        try:
            user_input = input("🏗️ 사용자: ").strip()
            
            if user_input.lower() in ['quit', 'exit', '종료', '나가기']:
                print("👋 VIBA AI 세션을 종료합니다.")
                break
            
            if not user_input:
                print("🤔 질문을 입력해주세요.")
                continue
            
            print("🤖 VIBA AI: 요청을 처리하고 있습니다...")
            
            start_time = time.time()
            result = await orchestrator.process_intelligent_request(
                user_input,
                optimization_level="adaptive"
            )
            execution_time = time.time() - start_time
            
            if result['success']:
                print(f"✅ 답변 (처리시간: {execution_time:.3f}초):")
                
                # 주요 정보 출력
                if 'summary' in result:
                    summary = result['summary']
                    if 'total_materials' in summary and summary['total_materials'] > 0:
                        print(f"📊 추천 재료: {summary['total_materials']}개")
                    if 'categories' in summary:
                        print(f"🏷️ 카테고리: {', '.join(summary['categories'])}")
                
                # 메타데이터
                metadata = result.get('orchestration_metadata', {})
                if metadata.get('agents_used'):
                    print(f"🤖 사용된 AI: {', '.join(metadata['agents_used'])}")
                
                print("💡 상세한 결과는 시스템 로그를 확인해주세요.\n")
                
            else:
                print(f"❌ 처리 실패: {result.get('error', 'Unknown error')}\n")
                
        except KeyboardInterrupt:
            print("\n👋 사용자가 중단했습니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}\n")

async def main():
    """메인 함수"""
    print("🎉 VIBA AI 건축 설계 시스템")
    print("차세대 AI 기반 건축 설계 플랫폼")
    print("=" * 60)
    
    try:
        # 1. 시스템 초기화
        orchestrator = await initialize_viba_system()
        
        # 2. 데모 실행
        print("\n🚀 자동 데모를 먼저 실행하겠습니다...")
        results = await demo_architectural_requests(orchestrator)
        print_demo_summary(results)
        
        # 3. 대화형 모드 선택
        print("\n❓ 대화형 모드로 진입하시겠습니까? (y/n): ", end="")
        choice = input().strip().lower()
        
        if choice in ['y', 'yes', '예', 'ㅇ']:
            await interactive_mode(orchestrator)
        else:
            print("🎊 VIBA AI 데모를 완료했습니다!")
            
    except Exception as e:
        print(f"❌ 시스템 오류: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🏗️ VIBA AI 시스템 시작...")
    success = asyncio.run(main())
    
    if success:
        print("\n✅ VIBA AI 시스템이 성공적으로 실행되었습니다!")
    else:
        print("\n❌ VIBA AI 시스템 실행 중 오류가 발생했습니다.")