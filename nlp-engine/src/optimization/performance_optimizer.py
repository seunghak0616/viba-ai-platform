"""
VIBA AI 시스템 성능 최적화 모듈
==============================

시스템 전체의 성능을 분석하고 최적화하는 고급 모듈

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import time
import cProfile
import pstats
import io
import psutil
import json
import logging
import os
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import numpy as np
from functools import lru_cache, wraps
import concurrent.futures
import aiofiles
import pickle

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""
    function_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    call_count: int = 1
    cache_hits: int = 0
    cache_misses: int = 0
    
    @property
    def avg_execution_time(self) -> float:
        return self.execution_time / self.call_count if self.call_count > 0 else 0
    
    @property
    def cache_hit_rate(self) -> float:
        total_cache_calls = self.cache_hits + self.cache_misses
        return self.cache_hits / total_cache_calls if total_cache_calls > 0 else 0


class PerformanceOptimizer:
    """시스템 성능 최적화기"""
    
    def __init__(self):
        self.metrics = defaultdict(lambda: PerformanceMetrics("", 0, 0, 0))
        self.profiler = cProfile.Profile()
        self.optimization_history = deque(maxlen=1000)
        
        # 캐싱 설정
        self.cache_config = {
            "max_size": 1000,
            "ttl": 300,  # 5분
            "strategy": "lru"
        }
        
        # 비동기 처리 설정
        self.async_config = {
            "max_workers": 10,
            "queue_size": 100,
            "timeout": 30
        }
        
        # 메모리 관리 설정
        self.memory_config = {
            "max_memory_percent": 80,
            "gc_threshold": 70,
            "cache_cleanup_threshold": 60
        }
    
    def performance_monitor(self, name: Optional[str] = None):
        """성능 모니터링 데코레이터"""
        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                func_name = name or f"{func.__module__}.{func.__name__}"
                
                # 시작 메트릭 수집
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                start_cpu = psutil.cpu_percent(interval=None)
                
                try:
                    # 함수 실행
                    result = await func(*args, **kwargs)
                    
                    # 종료 메트릭 수집
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    end_cpu = psutil.cpu_percent(interval=None)
                    
                    # 메트릭 업데이트
                    metrics = self.metrics[func_name]
                    metrics.function_name = func_name
                    metrics.execution_time += (end_time - start_time)
                    metrics.memory_usage = max(metrics.memory_usage, end_memory - start_memory)
                    metrics.cpu_usage = max(metrics.cpu_usage, end_cpu - start_cpu)
                    metrics.call_count += 1
                    
                    # 성능 이상 감지
                    if end_time - start_time > 1.0:  # 1초 이상
                        logger.warning(f"Slow function: {func_name} took {end_time - start_time:.3f}s")
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in {func_name}: {e}")
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                func_name = name or f"{func.__module__}.{func.__name__}"
                
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
                start_cpu = psutil.cpu_percent(interval=None)
                
                try:
                    result = func(*args, **kwargs)
                    
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    end_cpu = psutil.cpu_percent(interval=None)
                    
                    metrics = self.metrics[func_name]
                    metrics.function_name = func_name
                    metrics.execution_time += (end_time - start_time)
                    metrics.memory_usage = max(metrics.memory_usage, end_memory - start_memory)
                    metrics.cpu_usage = max(metrics.cpu_usage, end_cpu - start_cpu)
                    metrics.call_count += 1
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in {func_name}: {e}")
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def optimized_cache(self, maxsize: int = 128, ttl: int = 300):
        """최적화된 캐싱 데코레이터"""
        def decorator(func: Callable):
            cache = {}
            cache_times = {}
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # 캐시 키 생성
                cache_key = str(args) + str(kwargs)
                
                # 캐시 확인
                if cache_key in cache:
                    # TTL 확인
                    if time.time() - cache_times[cache_key] < ttl:
                        self.metrics[func.__name__].cache_hits += 1
                        return cache[cache_key]
                    else:
                        # 만료된 캐시 제거
                        del cache[cache_key]
                        del cache_times[cache_key]
                
                # 캐시 미스
                self.metrics[func.__name__].cache_misses += 1
                
                # 함수 실행
                result = await func(*args, **kwargs)
                
                # 캐시 크기 관리
                if len(cache) >= maxsize:
                    # LRU 방식으로 가장 오래된 항목 제거
                    oldest_key = min(cache_times, key=cache_times.get)
                    del cache[oldest_key]
                    del cache_times[oldest_key]
                
                # 캐시 저장
                cache[cache_key] = result
                cache_times[cache_key] = time.time()
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                cache_key = str(args) + str(kwargs)
                
                if cache_key in cache:
                    if time.time() - cache_times[cache_key] < ttl:
                        self.metrics[func.__name__].cache_hits += 1
                        return cache[cache_key]
                    else:
                        del cache[cache_key]
                        del cache_times[cache_key]
                
                self.metrics[func.__name__].cache_misses += 1
                result = func(*args, **kwargs)
                
                if len(cache) >= maxsize:
                    oldest_key = min(cache_times, key=cache_times.get)
                    del cache[oldest_key]
                    del cache_times[oldest_key]
                
                cache[cache_key] = result
                cache_times[cache_key] = time.time()
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    async def profile_async_function(self, func: Callable, *args, **kwargs):
        """비동기 함수 프로파일링"""
        # CPU 프로파일링
        self.profiler.enable()
        
        try:
            result = await func(*args, **kwargs)
        finally:
            self.profiler.disable()
        
        # 프로파일 결과 분석
        s = io.StringIO()
        ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # 상위 20개 함수
        
        profile_result = s.getvalue()
        
        return result, profile_result
    
    async def optimize_database_queries(self, queries: List[str]) -> List[str]:
        """데이터베이스 쿼리 최적화"""
        optimized_queries = []
        
        for query in queries:
            # 쿼리 분석
            if "SELECT" in query.upper():
                # 인덱스 힌트 추가
                if "WHERE" in query.upper() and "/*+ INDEX" not in query:
                    query = query.replace("SELECT", "SELECT /*+ INDEX */", 1)
                
                # LIMIT 추가 (없는 경우)
                if "LIMIT" not in query.upper():
                    query += " LIMIT 1000"
            
            # 조인 최적화
            if "JOIN" in query.upper():
                # INNER JOIN을 우선적으로 사용
                query = query.replace("LEFT JOIN", "LEFT OUTER JOIN")
            
            optimized_queries.append(query)
        
        return optimized_queries
    
    async def optimize_memory_usage(self):
        """메모리 사용량 최적화"""
        current_memory = psutil.virtual_memory().percent
        
        if current_memory > self.memory_config["max_memory_percent"]:
            logger.warning(f"High memory usage: {current_memory}%")
            
            # 가비지 컬렉션 강제 실행
            import gc
            gc.collect()
            
            # 캐시 정리
            if current_memory > self.memory_config["cache_cleanup_threshold"]:
                await self._cleanup_caches()
            
            # 메모리 사용량 재확인
            new_memory = psutil.virtual_memory().percent
            logger.info(f"Memory optimized: {current_memory}% -> {new_memory}%")
    
    async def _cleanup_caches(self):
        """캐시 정리"""
        # LRU 캐시 정리
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, 'cache_clear'):
                attr.cache_clear()
                logger.info(f"Cleared cache for {attr_name}")
    
    async def optimize_async_operations(self, operations: List[Callable]) -> List[Any]:
        """비동기 작업 최적화"""
        # 작업을 배치로 나누기
        batch_size = self.async_config["max_workers"]
        results = []
        
        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]
            
            # 배치 병렬 실행
            batch_results = await asyncio.gather(
                *[op() for op in batch],
                return_exceptions=True
            )
            
            results.extend(batch_results)
        
        return results
    
    def parallel_process(self, func: Callable, items: List[Any], max_workers: int = None) -> List[Any]:
        """병렬 처리 최적화"""
        max_workers = max_workers or self.async_config["max_workers"]
        
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(func, items))
        
        return results
    
    async def analyze_bottlenecks(self) -> Dict[str, Any]:
        """병목점 분석"""
        bottlenecks = {
            "slow_functions": [],
            "memory_intensive": [],
            "cpu_intensive": [],
            "cache_inefficient": []
        }
        
        for func_name, metrics in self.metrics.items():
            # 느린 함수 (평균 실행 시간 > 0.5초)
            if metrics.avg_execution_time > 0.5:
                bottlenecks["slow_functions"].append({
                    "function": func_name,
                    "avg_time": metrics.avg_execution_time,
                    "call_count": metrics.call_count
                })
            
            # 메모리 집약적 함수 (> 100MB)
            if metrics.memory_usage > 100:
                bottlenecks["memory_intensive"].append({
                    "function": func_name,
                    "memory_mb": metrics.memory_usage
                })
            
            # CPU 집약적 함수 (> 50%)
            if metrics.cpu_usage > 50:
                bottlenecks["cpu_intensive"].append({
                    "function": func_name,
                    "cpu_percent": metrics.cpu_usage
                })
            
            # 캐시 비효율적 함수 (캐시 히트율 < 50%)
            if metrics.cache_hit_rate < 0.5 and (metrics.cache_hits + metrics.cache_misses) > 10:
                bottlenecks["cache_inefficient"].append({
                    "function": func_name,
                    "hit_rate": metrics.cache_hit_rate,
                    "total_calls": metrics.cache_hits + metrics.cache_misses
                })
        
        # 정렬
        for category in bottlenecks:
            if category == "slow_functions":
                bottlenecks[category].sort(key=lambda x: x["avg_time"], reverse=True)
            elif category == "memory_intensive":
                bottlenecks[category].sort(key=lambda x: x["memory_mb"], reverse=True)
            elif category == "cpu_intensive":
                bottlenecks[category].sort(key=lambda x: x["cpu_percent"], reverse=True)
            elif category == "cache_inefficient":
                bottlenecks[category].sort(key=lambda x: x["hit_rate"])
        
        return bottlenecks
    
    async def generate_optimization_report(self) -> str:
        """최적화 보고서 생성"""
        bottlenecks = await self.analyze_bottlenecks()
        
        report = ["# VIBA AI 시스템 성능 최적화 보고서\n"]
        report.append(f"생성 시간: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 전체 요약
        total_functions = len(self.metrics)
        total_calls = sum(m.call_count for m in self.metrics.values())
        total_time = sum(m.execution_time for m in self.metrics.values())
        
        report.append("## 전체 요약\n")
        report.append(f"- 모니터링된 함수: {total_functions}개\n")
        report.append(f"- 총 호출 횟수: {total_calls:,}회\n")
        report.append(f"- 총 실행 시간: {total_time:.2f}초\n")
        avg_time = total_time/total_calls if total_calls > 0 else 0
        report.append(f"- 평균 함수 실행 시간: {avg_time:.4f}초\n\n")
        
        # 병목점 분석
        report.append("## 병목점 분석\n")
        
        # 느린 함수
        if bottlenecks["slow_functions"]:
            report.append("### 🐌 느린 함수 (상위 5개)\n")
            for i, func in enumerate(bottlenecks["slow_functions"][:5]):
                report.append(f"{i+1}. **{func['function']}**\n")
                report.append(f"   - 평균 실행 시간: {func['avg_time']:.3f}초\n")
                report.append(f"   - 호출 횟수: {func['call_count']}회\n")
        
        # 메모리 집약적 함수
        if bottlenecks["memory_intensive"]:
            report.append("\n### 💾 메모리 집약적 함수 (상위 5개)\n")
            for i, func in enumerate(bottlenecks["memory_intensive"][:5]):
                report.append(f"{i+1}. **{func['function']}**\n")
                report.append(f"   - 메모리 사용량: {func['memory_mb']:.1f}MB\n")
        
        # CPU 집약적 함수
        if bottlenecks["cpu_intensive"]:
            report.append("\n### 🔥 CPU 집약적 함수 (상위 5개)\n")
            for i, func in enumerate(bottlenecks["cpu_intensive"][:5]):
                report.append(f"{i+1}. **{func['function']}**\n")
                report.append(f"   - CPU 사용률: {func['cpu_percent']:.1f}%\n")
        
        # 캐시 비효율적 함수
        if bottlenecks["cache_inefficient"]:
            report.append("\n### 📦 캐시 비효율적 함수 (상위 5개)\n")
            for i, func in enumerate(bottlenecks["cache_inefficient"][:5]):
                report.append(f"{i+1}. **{func['function']}**\n")
                report.append(f"   - 캐시 히트율: {func['hit_rate']:.1%}\n")
                report.append(f"   - 총 캐시 접근: {func['total_calls']}회\n")
        
        # 최적화 권장사항
        report.append("\n## 💡 최적화 권장사항\n")
        
        recommendations = await self._generate_recommendations(bottlenecks)
        for i, rec in enumerate(recommendations):
            report.append(f"{i+1}. {rec}\n")
        
        # 시스템 리소스 현황
        report.append("\n## 📊 시스템 리소스 현황\n")
        report.append(f"- CPU 사용률: {psutil.cpu_percent()}%\n")
        report.append(f"- 메모리 사용률: {psutil.virtual_memory().percent}%\n")
        report.append(f"- 디스크 사용률: {psutil.disk_usage('/').percent}%\n")
        
        return "".join(report)
    
    async def _generate_recommendations(self, bottlenecks: Dict[str, List]) -> List[str]:
        """최적화 권장사항 생성"""
        recommendations = []
        
        # 느린 함수에 대한 권장사항
        if bottlenecks["slow_functions"]:
            slow_count = len(bottlenecks["slow_functions"])
            recommendations.append(
                f"**성능 개선**: {slow_count}개의 느린 함수가 발견되었습니다. "
                "비동기 처리, 캐싱, 알고리즘 최적화를 고려하세요."
            )
        
        # 메모리 최적화 권장사항
        if bottlenecks["memory_intensive"]:
            recommendations.append(
                "**메모리 최적화**: 메모리 집약적 함수들에 대해 "
                "스트리밍 처리, 배치 크기 조정, 메모리 풀 사용을 검토하세요."
            )
        
        # CPU 최적화 권장사항
        if bottlenecks["cpu_intensive"]:
            recommendations.append(
                "**CPU 최적화**: CPU 집약적 작업에 대해 "
                "병렬 처리, 벡터화, Cython 사용을 고려하세요."
            )
        
        # 캐시 최적화 권장사항
        if bottlenecks["cache_inefficient"]:
            avg_hit_rate = np.mean([f["hit_rate"] for f in bottlenecks["cache_inefficient"]])
            recommendations.append(
                f"**캐시 최적화**: 평균 캐시 히트율이 {avg_hit_rate:.1%}로 낮습니다. "
                "캐시 키 전략, TTL 조정, 캐시 크기 증가를 검토하세요."
            )
        
        # 일반적인 권장사항
        recommendations.extend([
            "**비동기 I/O**: 파일 및 네트워크 작업에 aiofiles와 aiohttp 사용",
            "**연결 풀링**: 데이터베이스 및 HTTP 연결에 대한 연결 풀 구현",
            "**프로파일링**: 정기적인 프로파일링으로 새로운 병목점 조기 발견",
            "**모니터링**: Prometheus와 Grafana를 활용한 실시간 성능 모니터링"
        ])
        
        return recommendations
    
    async def apply_automatic_optimizations(self):
        """자동 최적화 적용"""
        logger.info("자동 최적화 시작...")
        
        # 1. 메모리 최적화
        await self.optimize_memory_usage()
        
        # 2. 캐시 정리
        current_memory = psutil.virtual_memory().percent
        if current_memory > 70:
            await self._cleanup_caches()
        
        # 3. 가비지 컬렉션
        import gc
        gc.collect()
        
        # 4. 프로세스 우선순위 조정
        p = psutil.Process()
        p.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS if os.name == 'nt' else 10)
        
        logger.info("자동 최적화 완료")
    
    async def save_performance_data(self, filepath: str):
        """성능 데이터 저장"""
        data = {
            "metrics": dict(self.metrics),
            "optimization_history": list(self.optimization_history),
            "timestamp": time.time()
        }
        
        async with aiofiles.open(filepath, 'wb') as f:
            await f.write(pickle.dumps(data))
        
        logger.info(f"성능 데이터 저장 완료: {filepath}")
    
    async def load_performance_data(self, filepath: str):
        """성능 데이터 로드"""
        try:
            async with aiofiles.open(filepath, 'rb') as f:
                data = pickle.loads(await f.read())
            
            self.metrics = defaultdict(lambda: PerformanceMetrics("", 0, 0, 0), data["metrics"])
            self.optimization_history = deque(data["optimization_history"], maxlen=1000)
            
            logger.info(f"성능 데이터 로드 완료: {filepath}")
            
        except Exception as e:
            logger.error(f"성능 데이터 로드 실패: {e}")


# 전역 성능 최적화기 인스턴스
performance_optimizer = PerformanceOptimizer()

# 편의 함수들
performance_monitor = performance_optimizer.performance_monitor
optimized_cache = performance_optimizer.optimized_cache


async def run_performance_analysis():
    """성능 분석 실행"""
    optimizer = performance_optimizer
    
    # 병목점 분석
    bottlenecks = await optimizer.analyze_bottlenecks()
    
    # 보고서 생성
    report = await optimizer.generate_optimization_report()
    
    # 보고서 저장
    report_path = "performance_report.md"
    async with aiofiles.open(report_path, 'w', encoding='utf-8') as f:
        await f.write(report)
    
    print(f"성능 분석 보고서 생성 완료: {report_path}")
    
    # 자동 최적화 적용
    await optimizer.apply_automatic_optimizations()
    
    return report


if __name__ == "__main__":
    asyncio.run(run_performance_analysis())