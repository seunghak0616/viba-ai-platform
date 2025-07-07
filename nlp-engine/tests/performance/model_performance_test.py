#!/usr/bin/env python3
"""
VIBA AI 모델 성능 테스트
======================

AI 모델의 추론 속도, 메모리 사용량, 정확도 등을 종합적으로 테스트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import time
import psutil
import gc
import numpy as np
import json
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import tracemalloc

# 테스트 환경 설정
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.ai.viba_core import VIBACoreOrchestrator
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class ModelPerformanceTester:
    """AI 모델 성능 테스트 클래스"""
    
    def __init__(self):
        self.results = {}
        self.start_time = time.time()
        
        # 시스템 리소스 모니터링
        self.process = psutil.Process()
        self.initial_memory = self.process.memory_info().rss / 1024 / 1024  # MB
        
        # 테스트 시나리오
        self.test_scenarios = self._load_test_scenarios()
        
    def _load_test_scenarios(self) -> List[Dict[str, Any]]:
        """테스트 시나리오 로드"""
        return [
            {
                "name": "간단한_주거_설계",
                "category": "residential",
                "complexity": "low",
                "input": {
                    "description": "서울에 2층 단독주택을 설계해주세요",
                    "building_type": "단독주택",
                    "style": ["현대적"],
                    "constraints": {
                        "budget": 300000000,
                        "lot_size": 150,
                        "max_floors": 2
                    }
                },
                "expected_duration": 15.0,  # 초
                "expected_accuracy": 0.9
            },
            {
                "name": "복잡한_상업_설계",
                "category": "commercial",
                "complexity": "high", 
                "input": {
                    "description": "강남구에 5층 상업복합시설을 설계해주세요. 1층은 상가, 2-5층은 오피스로 구성해주세요",
                    "building_type": "상업복합시설",
                    "style": ["현대적", "미니멀"],
                    "constraints": {
                        "budget": 2000000000,
                        "lot_size": 500,
                        "max_floors": 5,
                        "parking_spaces": 50
                    }
                },
                "expected_duration": 25.0,
                "expected_accuracy": 0.85
            },
            {
                "name": "친환경_교육시설",
                "category": "educational",
                "complexity": "medium",
                "input": {
                    "description": "친환경 초등학교를 설계해주세요. 자연채광과 에너지 효율을 중점으로 해주세요",
                    "building_type": "교육시설",
                    "style": ["친환경", "모던"],
                    "constraints": {
                        "budget": 1500000000,
                        "lot_size": 3000,
                        "max_floors": 3,
                        "energy_rating": "A+",
                        "green_certification": True
                    }
                },
                "expected_duration": 30.0,
                "expected_accuracy": 0.88
            },
            {
                "name": "한옥_게스트하우스",
                "category": "hospitality",
                "complexity": "medium",
                "input": {
                    "description": "전통 한옥 스타일의 게스트하우스를 설계해주세요",
                    "building_type": "숙박시설",
                    "style": ["한옥", "전통"],
                    "constraints": {
                        "budget": 800000000,
                        "lot_size": 400,
                        "max_floors": 2,
                        "rooms": 8
                    }
                },
                "expected_duration": 20.0,
                "expected_accuracy": 0.87
            }
        ]
    
    async def run_single_scenario_test(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """단일 시나리오 성능 테스트"""
        logger.info(f"🔄 테스트 시작: {scenario['name']}")
        
        # 메모리 추적 시작
        tracemalloc.start()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        start_cpu = self.process.cpu_percent()
        start_time = time.time()
        
        try:
            # VIBA 시스템 초기화
            viba = VIBACoreOrchestrator()
            await viba.initialize()
            
            # 설계 요청 처리
            result = await viba.process_design_request(scenario['input'])
            
            # 성능 메트릭 수집
            end_time = time.time()
            duration = end_time - start_time
            
            end_memory = self.process.memory_info().rss / 1024 / 1024
            memory_usage = end_memory - start_memory
            
            cpu_usage = self.process.cpu_percent()
            
            # 메모리 사용량 상세 분석
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # 정확도 평가
            accuracy_score = result.get('quality_score', 0.0)
            
            # 결과 정리
            test_result = {
                "scenario_name": scenario['name'],
                "category": scenario['category'],
                "complexity": scenario['complexity'],
                "status": result.get('status', 'unknown'),
                "performance_metrics": {
                    "duration": duration,
                    "expected_duration": scenario['expected_duration'],
                    "duration_ratio": duration / scenario['expected_duration'],
                    "memory_usage_mb": memory_usage,
                    "peak_memory_mb": peak / 1024 / 1024,
                    "cpu_usage_percent": cpu_usage,
                    "accuracy_score": accuracy_score,
                    "expected_accuracy": scenario['expected_accuracy'],
                    "accuracy_ratio": accuracy_score / scenario['expected_accuracy']
                },
                "quality_metrics": {
                    "bim_generation_success": result.get('result', {}).get('bim_model') is not None,
                    "design_concept_quality": len(result.get('result', {}).get('design_concept', '')),
                    "performance_analysis_complete": result.get('result', {}).get('performance_report') is not None
                },
                "resource_efficiency": {
                    "memory_per_complexity": memory_usage / {"low": 1, "medium": 2, "high": 3}[scenario['complexity']],
                    "time_per_complexity": duration / {"low": 1, "medium": 2, "high": 3}[scenario['complexity']],
                    "meets_performance_target": duration <= scenario['expected_duration'] * 1.1,  # 10% 여유
                    "meets_accuracy_target": accuracy_score >= scenario['expected_accuracy'] * 0.9  # 10% 여유
                }
            }
            
            # VIBA 시스템 정리
            await viba.shutdown()
            
            logger.info(f"✅ 테스트 완료: {scenario['name']} ({duration:.2f}초, 정확도: {accuracy_score:.3f})")
            
            return test_result
            
        except Exception as e:
            logger.error(f"❌ 테스트 실패: {scenario['name']} - {e}")
            tracemalloc.stop()
            
            return {
                "scenario_name": scenario['name'],
                "category": scenario['category'],
                "status": "failed",
                "error": str(e),
                "performance_metrics": {
                    "duration": time.time() - start_time,
                    "memory_usage_mb": (self.process.memory_info().rss / 1024 / 1024) - start_memory,
                    "accuracy_score": 0.0
                }
            }
    
    async def run_concurrent_load_test(self, concurrent_users: int = 5) -> Dict[str, Any]:
        """동시 사용자 부하 테스트"""
        logger.info(f"🚀 동시 사용자 부하 테스트 시작: {concurrent_users}명")
        
        start_time = time.time()
        start_memory = self.process.memory_info().rss / 1024 / 1024
        
        # 동시 실행할 시나리오 준비
        concurrent_scenarios = []
        for i in range(concurrent_users):
            scenario = self.test_scenarios[i % len(self.test_scenarios)].copy()
            scenario['user_id'] = f"user_{i+1}"
            concurrent_scenarios.append(scenario)
        
        # 동시 실행
        tasks = [self.run_single_scenario_test(scenario) for scenario in concurrent_scenarios]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 분석
        end_time = time.time()
        total_duration = end_time - start_time
        end_memory = self.process.memory_info().rss / 1024 / 1024
        total_memory_usage = end_memory - start_memory
        
        successful_results = [r for r in results if isinstance(r, dict) and r.get('status') != 'failed']
        failed_results = [r for r in results if isinstance(r, Exception) or (isinstance(r, dict) and r.get('status') == 'failed')]
        
        # 성능 통계
        if successful_results:
            durations = [r['performance_metrics']['duration'] for r in successful_results]
            accuracies = [r['performance_metrics']['accuracy_score'] for r in successful_results]
            
            performance_stats = {
                "total_requests": concurrent_users,
                "successful_requests": len(successful_results),
                "failed_requests": len(failed_results),
                "success_rate": len(successful_results) / concurrent_users,
                "total_duration": total_duration,
                "average_response_time": np.mean(durations),
                "p95_response_time": np.percentile(durations, 95),
                "max_response_time": np.max(durations),
                "min_response_time": np.min(durations),
                "average_accuracy": np.mean(accuracies),
                "throughput_requests_per_second": concurrent_users / total_duration,
                "total_memory_usage_mb": total_memory_usage,
                "memory_per_request_mb": total_memory_usage / concurrent_users
            }
        else:
            performance_stats = {
                "total_requests": concurrent_users,
                "successful_requests": 0,
                "failed_requests": concurrent_users,
                "success_rate": 0.0,
                "total_duration": total_duration
            }
        
        return {
            "test_type": "concurrent_load",
            "concurrent_users": concurrent_users,
            "performance_stats": performance_stats,
            "individual_results": results,
            "system_impact": {
                "peak_memory_usage_mb": end_memory,
                "memory_increase_mb": total_memory_usage,
                "cpu_utilization": psutil.cpu_percent(interval=1)
            }
        }
    
    async def run_stress_test(self, max_concurrent: int = 20, step_size: int = 5) -> Dict[str, Any]:
        """스트레스 테스트 - 점진적 부하 증가"""
        logger.info(f"⚡ 스트레스 테스트 시작: 최대 {max_concurrent}명")
        
        stress_results = []
        current_concurrent = step_size
        
        while current_concurrent <= max_concurrent:
            logger.info(f"📊 부하 레벨: {current_concurrent}명 동시 사용자")
            
            # 현재 부하 레벨에서 테스트 실행
            load_result = await self.run_concurrent_load_test(current_concurrent)
            load_result['load_level'] = current_concurrent
            stress_results.append(load_result)
            
            # 성능 저하 확인
            success_rate = load_result['performance_stats']['success_rate']
            avg_response_time = load_result['performance_stats'].get('average_response_time', float('inf'))
            
            logger.info(f"부하 레벨 {current_concurrent}: 성공률 {success_rate:.2%}, 평균 응답시간 {avg_response_time:.2f}초")
            
            # 임계점 도달 시 중단
            if success_rate < 0.8 or avg_response_time > 60:
                logger.warning(f"성능 임계점 도달. 테스트 중단: {current_concurrent}명")
                break
            
            current_concurrent += step_size
            
            # 시스템 복구 대기
            await asyncio.sleep(5)
            gc.collect()  # 가비지 컬렉션 강제 실행
        
        # 스트레스 테스트 결과 분석
        max_stable_load = max([r['load_level'] for r in stress_results if r['performance_stats']['success_rate'] >= 0.95])
        breaking_point = min([r['load_level'] for r in stress_results if r['performance_stats']['success_rate'] < 0.8], default=max_concurrent)
        
        return {
            "test_type": "stress_test",
            "max_tested_load": max([r['load_level'] for r in stress_results]),
            "max_stable_load": max_stable_load,
            "breaking_point": breaking_point,
            "load_test_results": stress_results,
            "performance_degradation": self._analyze_performance_degradation(stress_results)
        }
    
    def _analyze_performance_degradation(self, stress_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """성능 저하 패턴 분석"""
        if len(stress_results) < 2:
            return {}
        
        baseline = stress_results[0]['performance_stats']
        final = stress_results[-1]['performance_stats']
        
        return {
            "response_time_degradation": final.get('average_response_time', 0) / baseline.get('average_response_time', 1),
            "success_rate_degradation": baseline.get('success_rate', 1) - final.get('success_rate', 0),
            "memory_growth_rate": final.get('total_memory_usage_mb', 0) / final.get('total_requests', 1),
            "throughput_degradation": baseline.get('throughput_requests_per_second', 1) / final.get('throughput_requests_per_second', 1)
        }
    
    async def run_endurance_test(self, duration_minutes: int = 30) -> Dict[str, Any]:
        """지속성 테스트 - 장시간 연속 실행"""
        logger.info(f"🕒 지속성 테스트 시작: {duration_minutes}분")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        test_results = []
        iteration = 0
        
        while time.time() < end_time:
            iteration += 1
            logger.info(f"지속성 테스트 반복 {iteration}")
            
            # 랜덤 시나리오 선택
            scenario = np.random.choice(self.test_scenarios)
            result = await self.run_single_scenario_test(scenario)
            result['iteration'] = iteration
            result['elapsed_time'] = time.time() - start_time
            
            test_results.append(result)
            
            # 메모리 누수 체크
            current_memory = self.process.memory_info().rss / 1024 / 1024
            if current_memory > self.initial_memory * 2:  # 메모리 2배 증가 시 경고
                logger.warning(f"메모리 사용량 급증 감지: {current_memory:.1f}MB")
            
            # 짧은 대기
            await asyncio.sleep(10)
        
        # 지속성 테스트 결과 분석
        successful_tests = [r for r in test_results if r.get('status') != 'failed']
        
        if successful_tests:
            durations = [r['performance_metrics']['duration'] for r in successful_tests]
            accuracies = [r['performance_metrics']['accuracy_score'] for r in successful_tests]
            memory_usages = [r['performance_metrics']['memory_usage_mb'] for r in successful_tests]
            
            endurance_stats = {
                "test_duration_minutes": duration_minutes,
                "total_iterations": len(test_results),
                "successful_iterations": len(successful_tests),
                "failure_rate": (len(test_results) - len(successful_tests)) / len(test_results),
                "average_response_time": np.mean(durations),
                "response_time_stability": np.std(durations),
                "average_accuracy": np.mean(accuracies),
                "accuracy_stability": np.std(accuracies),
                "memory_growth_trend": np.polyfit(range(len(memory_usages)), memory_usages, 1)[0],
                "peak_memory_usage": max(memory_usages),
                "memory_leak_detected": np.polyfit(range(len(memory_usages)), memory_usages, 1)[0] > 1.0  # 1MB/iteration 증가 시 누수 의심
            }
        else:
            endurance_stats = {
                "test_duration_minutes": duration_minutes,
                "total_iterations": len(test_results),
                "successful_iterations": 0,
                "failure_rate": 1.0
            }
        
        return {
            "test_type": "endurance_test",
            "endurance_stats": endurance_stats,
            "iteration_results": test_results,
            "system_stability": {
                "final_memory_usage_mb": self.process.memory_info().rss / 1024 / 1024,
                "memory_increase_total_mb": (self.process.memory_info().rss / 1024 / 1024) - self.initial_memory,
                "cpu_average": psutil.cpu_percent(interval=1)
            }
        }
    
    async def run_comprehensive_performance_test(self) -> Dict[str, Any]:
        """종합 성능 테스트 실행"""
        logger.info("🚀 VIBA AI 종합 성능 테스트 시작")
        
        comprehensive_results = {
            "test_session": {
                "start_time": time.time(),
                "system_info": {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                    "python_version": sys.version,
                    "platform": sys.platform
                }
            }
        }
        
        # 1. 개별 시나리오 테스트
        logger.info("📋 1. 개별 시나리오 성능 테스트")
        scenario_results = []
        for scenario in self.test_scenarios:
            result = await self.run_single_scenario_test(scenario)
            scenario_results.append(result)
            await asyncio.sleep(2)  # 테스트 간 간격
        
        comprehensive_results["scenario_tests"] = scenario_results
        
        # 2. 동시 사용자 테스트
        logger.info("👥 2. 동시 사용자 부하 테스트")
        concurrent_result = await self.run_concurrent_load_test(5)
        comprehensive_results["concurrent_load_test"] = concurrent_result
        
        # 3. 스트레스 테스트
        logger.info("⚡ 3. 스트레스 테스트")
        stress_result = await self.run_stress_test(15, 3)
        comprehensive_results["stress_test"] = stress_result
        
        # 4. 지속성 테스트 (단축된 버전)
        logger.info("🕒 4. 지속성 테스트")
        endurance_result = await self.run_endurance_test(10)  # 10분으로 단축
        comprehensive_results["endurance_test"] = endurance_result
        
        # 종합 평가
        comprehensive_results["overall_assessment"] = self._generate_overall_assessment(comprehensive_results)
        comprehensive_results["test_session"]["end_time"] = time.time()
        comprehensive_results["test_session"]["total_duration"] = time.time() - comprehensive_results["test_session"]["start_time"]
        
        return comprehensive_results
    
    def _generate_overall_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """종합 평가 생성"""
        scenario_results = results.get("scenario_tests", [])
        concurrent_result = results.get("concurrent_load_test", {})
        stress_result = results.get("stress_test", {})
        endurance_result = results.get("endurance_test", {})
        
        # 성능 등급 계산
        performance_scores = []
        
        # 개별 시나리오 성능
        if scenario_results:
            scenario_success_rate = len([r for r in scenario_results if r.get('status') != 'failed']) / len(scenario_results)
            avg_accuracy = np.mean([r['performance_metrics']['accuracy_score'] for r in scenario_results if r.get('status') != 'failed'])
            performance_scores.append(scenario_success_rate * avg_accuracy)
        
        # 동시 처리 성능
        if concurrent_result.get("performance_stats"):
            concurrent_score = concurrent_result["performance_stats"]["success_rate"]
            performance_scores.append(concurrent_score)
        
        # 스트레스 내성
        if stress_result.get("max_stable_load"):
            stress_score = min(stress_result["max_stable_load"] / 10, 1.0)  # 10명을 기준으로 정규화
            performance_scores.append(stress_score)
        
        # 안정성
        if endurance_result.get("endurance_stats"):
            stability_score = 1 - endurance_result["endurance_stats"]["failure_rate"]
            performance_scores.append(stability_score)
        
        overall_score = np.mean(performance_scores) if performance_scores else 0.0
        
        # 등급 부여
        if overall_score >= 0.9:
            grade = "A"
            assessment = "Excellent"
        elif overall_score >= 0.8:
            grade = "B"
            assessment = "Good"
        elif overall_score >= 0.7:
            grade = "C"
            assessment = "Acceptable"
        elif overall_score >= 0.6:
            grade = "D"
            assessment = "Poor"
        else:
            grade = "F"
            assessment = "Unacceptable"
        
        return {
            "overall_score": overall_score,
            "performance_grade": grade,
            "assessment": assessment,
            "component_scores": {
                "scenario_performance": performance_scores[0] if len(performance_scores) > 0 else 0,
                "concurrent_handling": performance_scores[1] if len(performance_scores) > 1 else 0,
                "stress_tolerance": performance_scores[2] if len(performance_scores) > 2 else 0,
                "system_stability": performance_scores[3] if len(performance_scores) > 3 else 0
            },
            "recommendations": self._generate_performance_recommendations(results)
        }
    
    def _generate_performance_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        # 개별 시나리오 분석
        scenario_results = results.get("scenario_tests", [])
        slow_scenarios = [r for r in scenario_results if r.get('performance_metrics', {}).get('duration_ratio', 0) > 1.2]
        if slow_scenarios:
            recommendations.append(f"{len(slow_scenarios)}개 시나리오의 응답시간이 목표를 20% 초과합니다. 알고리즘 최적화가 필요합니다.")
        
        # 메모리 사용량 분석
        high_memory_scenarios = [r for r in scenario_results if r.get('performance_metrics', {}).get('memory_usage_mb', 0) > 500]
        if high_memory_scenarios:
            recommendations.append("메모리 사용량이 높은 시나리오가 있습니다. 메모리 최적화를 고려하세요.")
        
        # 정확도 분석
        low_accuracy_scenarios = [r for r in scenario_results if r.get('performance_metrics', {}).get('accuracy_ratio', 0) < 0.9]
        if low_accuracy_scenarios:
            recommendations.append("일부 시나리오에서 정확도가 목표에 미달합니다. 모델 재훈련을 고려하세요.")
        
        # 동시 처리 성능
        concurrent_result = results.get("concurrent_load_test", {})
        if concurrent_result.get("performance_stats", {}).get("success_rate", 1) < 0.95:
            recommendations.append("동시 사용자 처리 성능이 부족합니다. 병렬 처리 최적화가 필요합니다.")
        
        # 스트레스 테스트 결과
        stress_result = results.get("stress_test", {})
        if stress_result.get("max_stable_load", 0) < 10:
            recommendations.append("스트레스 내성이 부족합니다. 시스템 확장성 개선이 필요합니다.")
        
        return recommendations


async def main():
    """메인 테스트 실행 함수"""
    logger.info("🤖 VIBA AI 모델 성능 테스트 시작")
    
    tester = ModelPerformanceTester()
    
    try:
        # 종합 성능 테스트 실행
        results = await tester.run_comprehensive_performance_test()
        
        # 결과 저장
        results_file = Path(__file__).parent.parent.parent / "test-results" / f"model_performance_{int(time.time())}.json"
        results_file.parent.mkdir(exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        # 결과 요약 출력
        print("\n" + "="*60)
        print("🤖 VIBA AI 모델 성능 테스트 결과")
        print("="*60)
        
        assessment = results.get("overall_assessment", {})
        print(f"전체 점수: {assessment.get('overall_score', 0):.3f}")
        print(f"성능 등급: {assessment.get('performance_grade', 'N/A')}")
        print(f"평가: {assessment.get('assessment', 'Unknown')}")
        
        print("\n컴포넌트별 점수:")
        component_scores = assessment.get("component_scores", {})
        for component, score in component_scores.items():
            print(f"  - {component}: {score:.3f}")
        
        print("\n개선 권장사항:")
        for i, rec in enumerate(assessment.get("recommendations", []), 1):
            print(f"  {i}. {rec}")
        
        print(f"\n상세 결과: {results_file}")
        
        # 성능 기준 미달 시 종료 코드 1
        if assessment.get('overall_score', 0) < 0.7:
            logger.warning("성능 기준 미달!")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"성능 테스트 실행 중 오류: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())