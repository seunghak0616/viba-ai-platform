"""
VIBA AI 메트릭 수집기
==================

AI 시스템의 성능, 품질, 사용량 메트릭을 수집하고 Prometheus로 내보내는 모듈

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import time
import psutil
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import asyncio
import threading
from contextlib import asynccontextmanager
import json

# Prometheus 메트릭
from prometheus_client import (
    Counter, Histogram, Gauge, Summary, Info,
    CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST,
    start_http_server
)

logger = logging.getLogger(__name__)


@dataclass
class MetricData:
    """메트릭 데이터 구조"""
    name: str
    metric_type: str  # counter, gauge, histogram, summary
    value: Union[int, float]
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    help_text: str = ""


class VIBAMetricsCollector:
    """VIBA AI 시스템 종합 메트릭 수집기"""
    
    def __init__(self, port: int = 8001, enable_prometheus: bool = True):
        """
        메트릭 수집기 초기화
        
        Args:
            port: Prometheus 메트릭 서버 포트
            enable_prometheus: Prometheus 통합 활성화 여부
        """
        self.port = port
        self.enable_prometheus = enable_prometheus
        self.registry = CollectorRegistry()
        
        # 메트릭 저장소
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.current_metrics: Dict[str, MetricData] = {}
        
        # 시스템 리소스 모니터링
        self.process = psutil.Process()
        self.start_time = time.time()
        
        # 비동기 작업
        self.collection_task: Optional[asyncio.Task] = None
        self.is_collecting = False
        
        # Prometheus 메트릭 정의
        self._initialize_prometheus_metrics()
        
        logger.info(f"VIBA 메트릭 수집기 초기화 완료 (포트: {port})")
    
    def _initialize_prometheus_metrics(self):
        """Prometheus 메트릭 초기화"""
        if not self.enable_prometheus:
            return
        
        # =================================================================
        # AI 모델 성능 메트릭
        # =================================================================
        self.ai_inference_duration = Histogram(
            'viba_ai_inference_duration_seconds',
            'AI 모델 추론 시간',
            ['model_type', 'agent_type', 'complexity'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
        )
        
        self.ai_inference_total = Counter(
            'viba_ai_inference_total',
            'AI 추론 요청 총 횟수',
            ['model_type', 'agent_type', 'status'],
            registry=self.registry
        )
        
        self.ai_model_accuracy = Gauge(
            'viba_ai_model_accuracy',
            'AI 모델 정확도 점수',
            ['model_type', 'agent_type'],
            registry=self.registry
        )
        
        self.ai_model_memory_usage = Gauge(
            'viba_ai_model_memory_usage_bytes',
            'AI 모델 메모리 사용량',
            ['model_type', 'agent_type'],
            registry=self.registry
        )
        
        # =================================================================
        # BIM 처리 메트릭
        # =================================================================
        self.bim_generation_duration = Histogram(
            'viba_bim_generation_duration_seconds',
            'BIM 모델 생성 시간',
            ['building_type', 'complexity', 'style'],
            registry=self.registry,
            buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
        )
        
        self.bim_generation_total = Counter(
            'viba_bim_generation_total',
            'BIM 생성 요청 총 횟수',
            ['building_type', 'status'],
            registry=self.registry
        )
        
        self.bim_model_size = Histogram(
            'viba_bim_model_size_bytes',
            'BIM 모델 파일 크기',
            ['format', 'complexity'],
            registry=self.registry,
            buckets=[1024, 10240, 102400, 1048576, 10485760, 104857600]
        )
        
        self.bim_quality_score = Gauge(
            'viba_bim_quality_score',
            'BIM 모델 품질 점수',
            ['building_type', 'validation_type'],
            registry=self.registry
        )
        
        # =================================================================
        # 성능 분석 메트릭
        # =================================================================
        self.performance_analysis_duration = Histogram(
            'viba_performance_analysis_duration_seconds',
            '성능 분석 실행 시간',
            ['analysis_type', 'building_size'],
            registry=self.registry,
            buckets=[1.0, 5.0, 15.0, 30.0, 60.0, 180.0, 300.0]
        )
        
        self.energy_simulation_accuracy = Gauge(
            'viba_energy_simulation_accuracy',
            '에너지 시뮬레이션 정확도',
            ['building_type', 'climate_zone'],
            registry=self.registry
        )
        
        # =================================================================
        # 사용자 활동 메트릭
        # =================================================================
        self.user_sessions_total = Counter(
            'viba_user_sessions_total',
            '사용자 세션 총 횟수',
            ['user_type', 'region'],
            registry=self.registry
        )
        
        self.user_session_duration = Histogram(
            'viba_user_session_duration_seconds',
            '사용자 세션 지속 시간',
            ['user_type', 'activity_type'],
            registry=self.registry,
            buckets=[60, 300, 900, 1800, 3600, 7200, 14400]
        )
        
        self.design_requests_total = Counter(
            'viba_design_requests_total',
            '설계 요청 총 횟수',
            ['request_type', 'complexity', 'status'],
            registry=self.registry
        )
        
        # =================================================================
        # 시스템 리소스 메트릭
        # =================================================================
        self.system_cpu_usage = Gauge(
            'viba_system_cpu_usage_percent',
            'CPU 사용률',
            ['component'],
            registry=self.registry
        )
        
        self.system_memory_usage = Gauge(
            'viba_system_memory_usage_bytes',
            '메모리 사용량',
            ['component', 'type'],
            registry=self.registry
        )
        
        self.system_disk_usage = Gauge(
            'viba_system_disk_usage_bytes',
            '디스크 사용량',
            ['mount_point', 'type'],
            registry=self.registry
        )
        
        # =================================================================
        # 품질 및 신뢰성 메트릭
        # =================================================================
        self.system_errors_total = Counter(
            'viba_system_errors_total',
            '시스템 오류 총 횟수',
            ['component', 'error_type', 'severity'],
            registry=self.registry
        )
        
        self.system_uptime_seconds = Gauge(
            'viba_system_uptime_seconds',
            '시스템 가동 시간',
            ['component'],
            registry=self.registry
        )
        
        self.data_quality_score = Gauge(
            'viba_data_quality_score',
            '데이터 품질 점수',
            ['data_type', 'source'],
            registry=self.registry
        )
        
        # =================================================================
        # 비즈니스 메트릭
        # =================================================================
        self.projects_created_total = Counter(
            'viba_projects_created_total',
            '생성된 프로젝트 총 수',
            ['project_type', 'template_used'],
            registry=self.registry
        )
        
        self.project_completion_rate = Gauge(
            'viba_project_completion_rate',
            '프로젝트 완료율',
            ['project_type', 'time_period'],
            registry=self.registry
        )
        
        self.user_satisfaction_score = Gauge(
            'viba_user_satisfaction_score',
            '사용자 만족도 점수',
            ['feature', 'user_segment'],
            registry=self.registry
        )
        
        # =================================================================
        # MCP 통합 메트릭
        # =================================================================
        self.mcp_requests_total = Counter(
            'viba_mcp_requests_total',
            'MCP 요청 총 횟수',
            ['service', 'operation', 'status'],
            registry=self.registry
        )
        
        self.mcp_response_duration = Histogram(
            'viba_mcp_response_duration_seconds',
            'MCP 응답 시간',
            ['service', 'operation'],
            registry=self.registry,
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
    
    async def start_collection(self, interval: float = 30.0):
        """메트릭 수집 시작"""
        if self.is_collecting:
            logger.warning("메트릭 수집이 이미 실행 중입니다")
            return
        
        self.is_collecting = True
        
        # Prometheus HTTP 서버 시작
        if self.enable_prometheus:
            try:
                start_http_server(self.port, registry=self.registry)
                logger.info(f"Prometheus 메트릭 서버 시작: http://localhost:{self.port}/metrics")
            except Exception as e:
                logger.error(f"Prometheus 서버 시작 실패: {e}")
        
        # 백그라운드 수집 작업 시작
        self.collection_task = asyncio.create_task(self._collection_loop(interval))
        logger.info(f"메트릭 수집 시작 (간격: {interval}초)")
    
    async def stop_collection(self):
        """메트릭 수집 중단"""
        self.is_collecting = False
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
            
        logger.info("메트릭 수집 중단")
    
    async def _collection_loop(self, interval: float):
        """메트릭 수집 루프"""
        while self.is_collecting:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"메트릭 수집 중 오류: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_system_metrics(self):
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.labels(component='viba_system').set(cpu_percent)
            
            # 메모리 사용량
            memory_info = psutil.virtual_memory()
            self.system_memory_usage.labels(component='viba_system', type='used').set(memory_info.used)
            self.system_memory_usage.labels(component='viba_system', type='available').set(memory_info.available)
            
            # 프로세스별 메모리
            process_memory = self.process.memory_info()
            self.system_memory_usage.labels(component='viba_process', type='rss').set(process_memory.rss)
            self.system_memory_usage.labels(component='viba_process', type='vms').set(process_memory.vms)
            
            # 디스크 사용량
            disk_usage = psutil.disk_usage('/')
            self.system_disk_usage.labels(mount_point='/', type='used').set(disk_usage.used)
            self.system_disk_usage.labels(mount_point='/', type='free').set(disk_usage.free)
            
            # 시스템 가동 시간
            uptime = time.time() - self.start_time
            self.system_uptime_seconds.labels(component='viba_system').set(uptime)
            
        except Exception as e:
            logger.error(f"시스템 메트릭 수집 오류: {e}")
    
    def record_ai_inference(self, model_type: str, agent_type: str, duration: float, 
                           accuracy: float, memory_usage: int, complexity: str = "medium",
                           status: str = "success"):
        """AI 추론 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        # 추론 시간 기록
        self.ai_inference_duration.labels(
            model_type=model_type,
            agent_type=agent_type,
            complexity=complexity
        ).observe(duration)
        
        # 추론 횟수 증가
        self.ai_inference_total.labels(
            model_type=model_type,
            agent_type=agent_type,
            status=status
        ).inc()
        
        # 정확도 업데이트
        if status == "success":
            self.ai_model_accuracy.labels(
                model_type=model_type,
                agent_type=agent_type
            ).set(accuracy)
            
            # 메모리 사용량 업데이트
            self.ai_model_memory_usage.labels(
                model_type=model_type,
                agent_type=agent_type
            ).set(memory_usage)
    
    def record_bim_generation(self, building_type: str, duration: float, model_size: int,
                             quality_score: float, complexity: str = "medium",
                             style: str = "modern", status: str = "success"):
        """BIM 생성 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        # 생성 시간 기록
        self.bim_generation_duration.labels(
            building_type=building_type,
            complexity=complexity,
            style=style
        ).observe(duration)
        
        # 생성 횟수 증가
        self.bim_generation_total.labels(
            building_type=building_type,
            status=status
        ).inc()
        
        if status == "success":
            # 모델 크기 기록
            self.bim_model_size.labels(
                format="ifc",
                complexity=complexity
            ).observe(model_size)
            
            # 품질 점수 업데이트
            self.bim_quality_score.labels(
                building_type=building_type,
                validation_type="automated"
            ).set(quality_score)
    
    def record_performance_analysis(self, analysis_type: str, duration: float,
                                  building_size: str, accuracy: float = None):
        """성능 분석 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        # 분석 시간 기록
        self.performance_analysis_duration.labels(
            analysis_type=analysis_type,
            building_size=building_size
        ).observe(duration)
        
        # 에너지 분석 정확도 (해당하는 경우)
        if analysis_type == "energy" and accuracy is not None:
            self.energy_simulation_accuracy.labels(
                building_type=building_size,
                climate_zone="temperate"
            ).set(accuracy)
    
    def record_user_activity(self, user_type: str, session_duration: float,
                           activity_type: str, region: str = "kr"):
        """사용자 활동 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        # 세션 횟수 증가
        self.user_sessions_total.labels(
            user_type=user_type,
            region=region
        ).inc()
        
        # 세션 지속 시간 기록
        self.user_session_duration.labels(
            user_type=user_type,
            activity_type=activity_type
        ).observe(session_duration)
    
    def record_design_request(self, request_type: str, complexity: str, status: str):
        """설계 요청 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        self.design_requests_total.labels(
            request_type=request_type,
            complexity=complexity,
            status=status
        ).inc()
    
    def record_system_error(self, component: str, error_type: str, severity: str = "error"):
        """시스템 오류 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        self.system_errors_total.labels(
            component=component,
            error_type=error_type,
            severity=severity
        ).inc()
    
    def record_mcp_request(self, service: str, operation: str, duration: float, status: str):
        """MCP 요청 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        # 요청 횟수 증가
        self.mcp_requests_total.labels(
            service=service,
            operation=operation,
            status=status
        ).inc()
        
        # 응답 시간 기록
        self.mcp_response_duration.labels(
            service=service,
            operation=operation
        ).observe(duration)
    
    def record_project_creation(self, project_type: str, template_used: bool = False):
        """프로젝트 생성 메트릭 기록"""
        if not self.enable_prometheus:
            return
        
        template_label = "yes" if template_used else "no"
        self.projects_created_total.labels(
            project_type=project_type,
            template_used=template_label
        ).inc()
    
    def update_business_metrics(self, completion_rates: Dict[str, float],
                              satisfaction_scores: Dict[str, float]):
        """비즈니스 메트릭 업데이트"""
        if not self.enable_prometheus:
            return
        
        # 완료율 업데이트
        for project_type, rate in completion_rates.items():
            self.project_completion_rate.labels(
                project_type=project_type,
                time_period="weekly"
            ).set(rate)
        
        # 만족도 점수 업데이트
        for feature, score in satisfaction_scores.items():
            self.user_satisfaction_score.labels(
                feature=feature,
                user_segment="general"
            ).set(score)
    
    @asynccontextmanager
    async def measure_duration(self, metric_name: str, labels: Dict[str, str] = None):
        """지속 시간 측정 컨텍스트 매니저"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            # 메트릭에 따라 적절한 기록 함수 호출
            logger.debug(f"{metric_name} 완료: {duration:.3f}초")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """메트릭 요약 정보 반환"""
        if not self.enable_prometheus:
            return {"prometheus_disabled": True}
        
        # Prometheus 메트릭을 텍스트 형태로 반환
        metrics_output = generate_latest(self.registry)
        
        return {
            "collection_active": self.is_collecting,
            "metrics_endpoint": f"http://localhost:{self.port}/metrics",
            "uptime_seconds": time.time() - self.start_time,
            "metrics_count": len(self.current_metrics),
            "prometheus_output_size": len(metrics_output)
        }
    
    async def export_metrics_to_file(self, file_path: str):
        """메트릭을 파일로 내보내기"""
        try:
            summary = self.get_metrics_summary()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"메트릭을 파일로 내보냄: {file_path}")
            
        except Exception as e:
            logger.error(f"메트릭 파일 내보내기 실패: {e}")


# 전역 메트릭 수집기 인스턴스
_metrics_collector: Optional[VIBAMetricsCollector] = None

def get_metrics_collector() -> VIBAMetricsCollector:
    """전역 메트릭 수집기 인스턴스 반환"""
    global _metrics_collector
    
    if _metrics_collector is None:
        _metrics_collector = VIBAMetricsCollector()
    
    return _metrics_collector


# 편의 함수들 및 컨텍스트 매니저
from contextlib import contextmanager

@contextmanager
def record_ai_inference_metric(agent_name: str, operation: str):
    """AI 추론 메트릭 기록 컨텍스트 매니저"""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        logger.info(f"Metric: {agent_name}.{operation} took {duration:.3f}s")

def record_ai_inference_detailed(model_type: str, agent_type: str, duration: float, 
                              accuracy: float, memory_usage: int, **kwargs):
    """AI 추론 메트릭 기록 (편의 함수)"""
    collector = get_metrics_collector()
    collector.record_ai_inference(model_type, agent_type, duration, accuracy, memory_usage, **kwargs)


def record_bim_generation_metric(building_type: str, duration: float, model_size: int,
                                quality_score: float, **kwargs):
    """BIM 생성 메트릭 기록 (편의 함수)"""
    collector = get_metrics_collector()
    collector.record_bim_generation(building_type, duration, model_size, quality_score, **kwargs)


def record_user_activity_metric(user_type: str, session_duration: float, activity_type: str, **kwargs):
    """사용자 활동 메트릭 기록 (편의 함수)"""
    collector = get_metrics_collector()
    collector.record_user_activity(user_type, session_duration, activity_type, **kwargs)


async def start_metrics_collection(port: int = 8001, interval: float = 30.0):
    """메트릭 수집 시작 (편의 함수)"""
    collector = get_metrics_collector()
    collector.port = port
    await collector.start_collection(interval)


if __name__ == "__main__":
    # 테스트용 실행
    async def test_metrics():
        collector = VIBAMetricsCollector()
        await collector.start_collection(interval=5.0)
        
        # 테스트 메트릭 기록
        collector.record_ai_inference("nlp", "design_theorist", 2.5, 0.95, 512*1024*1024)
        collector.record_bim_generation("residential", 15.0, 2*1024*1024, 0.92)
        collector.record_user_activity("premium", 1800, "design_creation")
        
        print("메트릭 수집기 테스트 중... http://localhost:8001/metrics 확인")
        
        # 30초 대기
        await asyncio.sleep(30)
        
        await collector.stop_collection()
    
    asyncio.run(test_metrics())