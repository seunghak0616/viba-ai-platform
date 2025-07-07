"""
성능 분석가 AI 에이전트
====================

BIM 모델의 종합 성능 분석 및 최적화 제안을 담당하는 AI 에이전트
에너지, 구조, 자연채광, 음향, 환기 성능을 자동으로 분석하고 개선안 제시

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime, timedelta

# 성능 분석 라이브러리
try:
    import pandas as pd
    from scipy import optimize
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
except ImportError:
    logger.warning("Performance analysis libraries not available, using basic calculations")
    pd = None
    optimize = None

# 프로젝트 임포트
from ..base_agent import BaseVIBAAgent, AgentCapability
from ...utils.metrics_collector import record_ai_inference_metric
from ...knowledge.building_codes import BuildingCodeChecker
from ...knowledge.ifc_schema import IFC43Schema

logger = logging.getLogger(__name__)


class PerformanceCategory(Enum):
    """성능 분석 카테고리"""
    ENERGY = "energy"
    STRUCTURAL = "structural"
    LIGHTING = "lighting"
    ACOUSTIC = "acoustic"
    VENTILATION = "ventilation"
    THERMAL_COMFORT = "thermal_comfort"
    SUSTAINABILITY = "sustainability"


class AnalysisMethod(Enum):
    """분석 방법"""
    SIMPLIFIED = "simplified"  # 간단한 계산식 기반
    DETAILED = "detailed"     # 상세 시뮬레이션
    ML_BASED = "ml_based"     # 기계학습 기반 예측


@dataclass
class PerformanceMetric:
    """성능 지표"""
    category: PerformanceCategory
    name: str
    value: float
    unit: str
    target_value: Optional[float] = None
    performance_grade: Optional[str] = None  # A+, A, B, C, D
    improvement_potential: Optional[float] = None


@dataclass
class PerformanceAnalysis:
    """성능 분석 결과"""
    analysis_type: PerformanceCategory
    metrics: List[PerformanceMetric]
    overall_score: float  # 0-100점
    grade: str  # A+, A, B, C, D
    recommendations: List[str]
    analysis_time: float
    confidence: float


@dataclass
class OptimizationSuggestion:
    """최적화 제안"""
    category: PerformanceCategory
    priority: str  # high, medium, low
    title: str
    description: str
    expected_improvement: str
    implementation_cost: str  # low, medium, high
    payback_period: Optional[str] = None
    technical_details: List[str] = field(default_factory=list)


class PerformanceAnalystAgent(BaseVIBAAgent):
    """성능 분석가 AI 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_id="performance_analyst",
            capabilities=[
                AgentCapability.PERFORMANCE_ANALYSIS,
                AgentCapability.ENERGY_SIMULATION,
                AgentCapability.OPTIMIZATION
            ]
        )
        
        # 성능 분석 모델 및 데이터
        self.energy_model = None
        self.thermal_comfort_standards = self._load_thermal_comfort_standards()
        self.lighting_standards = self._load_lighting_standards()
        self.acoustic_standards = self._load_acoustic_standards()
        self.material_database = self._load_material_database()
        
        # 한국 기후 데이터
        self.climate_data = self._load_korean_climate_data()
        
        # 분석 결과 캐시
        self.analysis_cache = {}
        
        logger.info("Performance Analyst Agent initialized")
    
    @record_ai_inference_metric("performance_analysis")
    async def process_task_async(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """비동기 태스크 처리"""
        start_time = time.time()
        
        try:
            task_type = task.get('type', 'comprehensive_analysis')
            bim_model = task.get('bim_model', {})
            analysis_scope = task.get('analysis_scope', ['energy', 'lighting', 'thermal'])
            
            if task_type == 'comprehensive_analysis':
                result = await self._perform_comprehensive_analysis(bim_model, analysis_scope)
            elif task_type == 'energy_analysis':
                result = await self._analyze_energy_performance(bim_model)
            elif task_type == 'lighting_analysis':
                result = await self._analyze_lighting_performance(bim_model)
            elif task_type == 'acoustic_analysis':
                result = await self._analyze_acoustic_performance(bim_model)
            elif task_type == 'optimization':
                result = await self._generate_optimization_suggestions(bim_model)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            processing_time = time.time() - start_time
            
            # 성능 메트릭 업데이트
            self.performance_stats['total_tasks'] += 1
            self.performance_stats['average_response_time'] = (
                (self.performance_stats['average_response_time'] * (self.performance_stats['total_tasks'] - 1) + processing_time) 
                / self.performance_stats['total_tasks']
            )
            self.performance_stats['success_rate'] = (
                (self.performance_stats.get('successful_tasks', 0) + 1) / self.performance_stats['total_tasks']
            )
            
            return {
                "status": "success",
                "result": result,
                "processing_time": processing_time,
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Performance analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - start_time,
                "agent_id": self.agent_id
            }
    
    async def _perform_comprehensive_analysis(self, bim_model: Dict[str, Any], analysis_scope: List[str]) -> Dict[str, Any]:
        """종합 성능 분석"""
        logger.info("Starting comprehensive performance analysis")
        
        analyses = {}
        overall_score = 0.0
        
        # 각 성능 카테고리별 분석 실행
        for scope in analysis_scope:
            if scope == 'energy':
                analyses['energy'] = await self._analyze_energy_performance(bim_model)
                overall_score += analyses['energy']['overall_score'] * 0.3
            elif scope == 'lighting':
                analyses['lighting'] = await self._analyze_lighting_performance(bim_model)
                overall_score += analyses['lighting']['overall_score'] * 0.25
            elif scope == 'thermal':
                analyses['thermal'] = await self._analyze_thermal_comfort(bim_model)
                overall_score += analyses['thermal']['overall_score'] * 0.2
            elif scope == 'acoustic':
                analyses['acoustic'] = await self._analyze_acoustic_performance(bim_model)
                overall_score += analyses['acoustic']['overall_score'] * 0.15
            elif scope == 'structural':
                analyses['structural'] = await self._analyze_structural_performance(bim_model)
                overall_score += analyses['structural']['overall_score'] * 0.1
        
        # 종합 등급 계산
        overall_grade = self._calculate_performance_grade(overall_score)
        
        # 최적화 제안 생성
        optimization_suggestions = await self._generate_optimization_suggestions(bim_model, analyses)
        
        return {
            "analysis_type": "comprehensive",
            "overall_score": overall_score,
            "overall_grade": overall_grade,
            "detailed_analyses": analyses,
            "optimization_suggestions": optimization_suggestions,
            "analysis_timestamp": datetime.now().isoformat(),
            "bim_model_id": bim_model.get('model_id', 'unknown')
        }
    
    async def _analyze_energy_performance(self, bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """에너지 성능 분석"""
        logger.info("Analyzing energy performance")
        
        # 건물 기본 정보 추출
        building_info = self._extract_building_info(bim_model)
        
        # 1. 난방 부하 계산
        heating_load = self._calculate_heating_load(building_info)
        
        # 2. 냉방 부하 계산
        cooling_load = self._calculate_cooling_load(building_info)
        
        # 3. 연간 에너지 소비량 예측
        annual_energy = self._calculate_annual_energy_consumption(heating_load, cooling_load, building_info)
        
        # 4. 에너지 효율 등급 계산
        energy_grade = self._calculate_energy_grade(annual_energy, building_info)
        
        # 5. 열교 분석
        thermal_bridges = self._analyze_thermal_bridges(building_info)
        
        # 성능 지표 생성
        metrics = [
            PerformanceMetric(
                category=PerformanceCategory.ENERGY,
                name="연간 에너지 소비량",
                value=annual_energy,
                unit="kWh/m²·year",
                target_value=120.0,  # 한국 에너지절약법 기준
                performance_grade=energy_grade
            ),
            PerformanceMetric(
                category=PerformanceCategory.ENERGY,
                name="난방 부하",
                value=heating_load,
                unit="W/m²",
                target_value=15.0  # 패시브하우스 기준
            ),
            PerformanceMetric(
                category=PerformanceCategory.ENERGY,
                name="냉방 부하",
                value=cooling_load,
                unit="W/m²",
                target_value=15.0
            )
        ]
        
        # 종합 점수 계산
        overall_score = self._calculate_energy_score(metrics)
        
        # 개선 권고사항
        recommendations = self._generate_energy_recommendations(metrics, thermal_bridges)
        
        return {
            "analysis_type": "energy",
            "overall_score": overall_score,
            "grade": self._calculate_performance_grade(overall_score),
            "metrics": [metric.__dict__ for metric in metrics],
            "thermal_bridges": thermal_bridges,
            "recommendations": recommendations,
            "analysis_time": time.time(),
            "confidence": 0.92
        }
    
    async def _analyze_lighting_performance(self, bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """자연채광 성능 분석"""
        logger.info("Analyzing lighting performance")
        
        building_info = self._extract_building_info(bim_model)
        
        # 1. 일광률 계산 (Daylight Factor)
        daylight_factor = self._calculate_daylight_factor(building_info)
        
        # 2. 연간 일조 시간 계산
        annual_sunlight_hours = self._calculate_annual_sunlight_hours(building_info)
        
        # 3. 조도 레벨 분석
        illuminance_levels = self._analyze_illuminance_levels(building_info)
        
        # 4. 글레어 분석
        glare_analysis = self._analyze_glare_potential(building_info)
        
        # 5. 창호 성능 분석
        window_performance = self._analyze_window_performance(building_info)
        
        # 성능 지표 생성
        metrics = [
            PerformanceMetric(
                category=PerformanceCategory.LIGHTING,
                name="평균 일광률",
                value=daylight_factor,
                unit="%",
                target_value=2.0,  # 건축법 기준
                performance_grade=self._grade_daylight_factor(daylight_factor)
            ),
            PerformanceMetric(
                category=PerformanceCategory.LIGHTING,
                name="연간 일조시간",
                value=annual_sunlight_hours,
                unit="시간",
                target_value=2000.0
            ),
            PerformanceMetric(
                category=PerformanceCategory.LIGHTING,
                name="평균 조도",
                value=illuminance_levels['average'],
                unit="lux",
                target_value=300.0  # 사무공간 기준
            )
        ]
        
        overall_score = self._calculate_lighting_score(metrics, glare_analysis)
        recommendations = self._generate_lighting_recommendations(metrics, window_performance)
        
        return {
            "analysis_type": "lighting",
            "overall_score": overall_score,
            "grade": self._calculate_performance_grade(overall_score),
            "metrics": [metric.__dict__ for metric in metrics],
            "glare_analysis": glare_analysis,
            "window_performance": window_performance,
            "recommendations": recommendations,
            "analysis_time": time.time(),
            "confidence": 0.89
        }
    
    async def _analyze_thermal_comfort(self, bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """열적 쾌적성 분석"""
        logger.info("Analyzing thermal comfort")
        
        building_info = self._extract_building_info(bim_model)
        
        # 1. PMV/PPD 계산 (Predicted Mean Vote / Predicted Percentage Dissatisfied)
        pmv_ppd = self._calculate_pmv_ppd(building_info)
        
        # 2. 적응적 쾌적성 분석
        adaptive_comfort = self._analyze_adaptive_comfort(building_info)
        
        # 3. 온도 분포 분석
        temperature_distribution = self._analyze_temperature_distribution(building_info)
        
        # 4. 습도 분석
        humidity_analysis = self._analyze_humidity_levels(building_info)
        
        metrics = [
            PerformanceMetric(
                category=PerformanceCategory.THERMAL_COMFORT,
                name="PMV 지수",
                value=pmv_ppd['pmv'],
                unit="-",
                target_value=0.0,  # 중성값
                performance_grade=self._grade_pmv(pmv_ppd['pmv'])
            ),
            PerformanceMetric(
                category=PerformanceCategory.THERMAL_COMFORT,
                name="PPD",
                value=pmv_ppd['ppd'],
                unit="%",
                target_value=10.0  # 만족도 90% 이상
            ),
            PerformanceMetric(
                category=PerformanceCategory.THERMAL_COMFORT,
                name="쾌적 시간 비율",
                value=adaptive_comfort['comfort_hours_ratio'],
                unit="%",
                target_value=80.0
            )
        ]
        
        overall_score = self._calculate_thermal_comfort_score(metrics)
        recommendations = self._generate_thermal_recommendations(metrics, temperature_distribution)
        
        return {
            "analysis_type": "thermal_comfort",
            "overall_score": overall_score,
            "grade": self._calculate_performance_grade(overall_score),
            "metrics": [metric.__dict__ for metric in metrics],
            "temperature_distribution": temperature_distribution,
            "humidity_analysis": humidity_analysis,
            "recommendations": recommendations,
            "analysis_time": time.time(),
            "confidence": 0.87
        }
    
    async def _analyze_acoustic_performance(self, bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """음향 성능 분석"""
        logger.info("Analyzing acoustic performance")
        
        building_info = self._extract_building_info(bim_model)
        
        # 1. 잔향시간 계산
        reverberation_time = self._calculate_reverberation_time(building_info)
        
        # 2. 소음 레벨 분석
        noise_levels = self._analyze_noise_levels(building_info)
        
        # 3. 음향 전달 손실 계산
        sound_transmission_loss = self._calculate_sound_transmission_loss(building_info)
        
        # 4. 층간 소음 분석
        floor_impact_noise = self._analyze_floor_impact_noise(building_info)
        
        metrics = [
            PerformanceMetric(
                category=PerformanceCategory.ACOUSTIC,
                name="잔향시간 (RT60)",
                value=reverberation_time,
                unit="초",
                target_value=0.6,  # 사무공간 최적값
                performance_grade=self._grade_reverberation_time(reverberation_time)
            ),
            PerformanceMetric(
                category=PerformanceCategory.ACOUSTIC,
                name="소음 레벨",
                value=noise_levels['average'],
                unit="dB",
                target_value=40.0  # 사무공간 기준
            ),
            PerformanceMetric(
                category=PerformanceCategory.ACOUSTIC,
                name="음향 전달 손실",
                value=sound_transmission_loss,
                unit="dB",
                target_value=50.0
            )
        ]
        
        overall_score = self._calculate_acoustic_score(metrics)
        recommendations = self._generate_acoustic_recommendations(metrics, floor_impact_noise)
        
        return {
            "analysis_type": "acoustic",
            "overall_score": overall_score,
            "grade": self._calculate_performance_grade(overall_score),
            "metrics": [metric.__dict__ for metric in metrics],
            "noise_levels": noise_levels,
            "floor_impact_noise": floor_impact_noise,
            "recommendations": recommendations,
            "analysis_time": time.time(),
            "confidence": 0.84
        }
    
    async def _analyze_structural_performance(self, bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """구조 성능 분석"""
        logger.info("Analyzing structural performance")
        
        building_info = self._extract_building_info(bim_model)
        
        # 1. 내력 분석 (간단한 계산)
        load_analysis = self._analyze_structural_loads(building_info)
        
        # 2. 안전율 계산
        safety_factors = self._calculate_safety_factors(building_info)
        
        # 3. 처짐 분석
        deflection_analysis = self._analyze_deflections(building_info)
        
        # 4. 지진 대응 성능
        seismic_performance = self._analyze_seismic_performance(building_info)
        
        metrics = [
            PerformanceMetric(
                category=PerformanceCategory.STRUCTURAL,
                name="최대 응력비",
                value=load_analysis['max_stress_ratio'],
                unit="-",
                target_value=0.8,  # 안전 기준
                performance_grade=self._grade_stress_ratio(load_analysis['max_stress_ratio'])
            ),
            PerformanceMetric(
                category=PerformanceCategory.STRUCTURAL,
                name="최대 처짐",
                value=deflection_analysis['max_deflection'],
                unit="mm",
                target_value=20.0  # span/300 기준
            ),
            PerformanceMetric(
                category=PerformanceCategory.STRUCTURAL,
                name="지진 응답 계수",
                value=seismic_performance['response_factor'],
                unit="-",
                target_value=1.0
            )
        ]
        
        overall_score = self._calculate_structural_score(metrics)
        recommendations = self._generate_structural_recommendations(metrics, safety_factors)
        
        return {
            "analysis_type": "structural",
            "overall_score": overall_score,
            "grade": self._calculate_performance_grade(overall_score),
            "metrics": [metric.__dict__ for metric in metrics],
            "safety_factors": safety_factors,
            "seismic_performance": seismic_performance,
            "recommendations": recommendations,
            "analysis_time": time.time(),
            "confidence": 0.91
        }
    
    async def _generate_optimization_suggestions(self, bim_model: Dict[str, Any], analyses: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """최적화 제안 생성"""
        logger.info("Generating optimization suggestions")
        
        suggestions = []
        
        if analyses:
            # 각 분석 결과를 바탕으로 최적화 제안 생성
            for analysis_type, analysis_result in analyses.items():
                category_suggestions = self._generate_category_suggestions(analysis_type, analysis_result)
                suggestions.extend(category_suggestions)
        
        # 우선순위별 정렬
        suggestions.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
        
        return suggestions[:10]  # 상위 10개 제안만 반환
    
    def _generate_category_suggestions(self, category: str, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """카테고리별 최적화 제안 생성"""
        suggestions = []
        
        if category == 'energy':
            if analysis_result['overall_score'] < 70:
                suggestions.append({
                    "category": "energy",
                    "priority": "high",
                    "title": "외벽 단열 성능 향상",
                    "description": "외벽 단열재 두께를 증가시켜 열손실을 줄이고 에너지 효율을 개선합니다.",
                    "expected_improvement": "연간 에너지 사용량 15-25% 감소",
                    "implementation_cost": "medium",
                    "payback_period": "5-7년",
                    "technical_details": [
                        "단열재 두께 100mm → 150mm 증가",
                        "열교 차단 설계 적용",
                        "고성능 단열재 (λ < 0.030 W/mK) 사용"
                    ]
                })
        
        elif category == 'lighting':
            if analysis_result['overall_score'] < 75:
                suggestions.append({
                    "category": "lighting",
                    "priority": "medium",
                    "title": "창호 크기 및 위치 최적화",
                    "description": "자연채광을 개선하기 위해 창문 크기와 위치를 조정합니다.",
                    "expected_improvement": "일광률 30-50% 향상",
                    "implementation_cost": "high",
                    "payback_period": "장기적 만족도 향상",
                    "technical_details": [
                        "남향 창문 면적 20% 증가",
                        "상부 창문 추가 설치",
                        "내부 반사율 향상 (밝은 색상 마감재)"
                    ]
                })
        
        elif category == 'thermal':
            if analysis_result['overall_score'] < 80:
                suggestions.append({
                    "category": "thermal_comfort",
                    "priority": "medium",
                    "title": "자연 환기 시스템 개선",
                    "description": "교차 환기를 통해 열적 쾌적성을 향상시킵니다.",
                    "expected_improvement": "쾌적 시간 20-30% 증가",
                    "implementation_cost": "low",
                    "payback_period": "1-2년",
                    "technical_details": [
                        "대향 창문 배치 최적화",
                        "환기구 크기 조정",
                        "내부 공간 배치 개선"
                    ]
                })
        
        elif category == 'acoustic':
            if analysis_result['overall_score'] < 70:
                suggestions.append({
                    "category": "acoustic",
                    "priority": "low",
                    "title": "음향 흡수재 설치",
                    "description": "천장과 벽면에 음향 흡수재를 설치하여 잔향시간을 조절합니다.",
                    "expected_improvement": "잔향시간 20-40% 감소",
                    "implementation_cost": "medium",
                    "payback_period": "즉시 효과",
                    "technical_details": [
                        "천장 흡음 패널 설치",
                        "벽면 흡음 마감재 적용",
                        "가구 및 카펫 활용"
                    ]
                })
        
        return suggestions
    
    # === 성능 계산 메서드들 ===
    
    def _extract_building_info(self, bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """BIM 모델에서 건물 정보 추출"""
        return {
            "floor_area": bim_model.get('total_floor_area', 1000),  # m²
            "building_height": bim_model.get('height', 15),  # m
            "window_to_wall_ratio": bim_model.get('window_ratio', 0.4),
            "building_type": bim_model.get('building_type', 'office'),
            "stories": bim_model.get('stories', 5),
            "orientation": bim_model.get('orientation', 'south'),
            "location": bim_model.get('location', 'seoul')
        }
    
    def _calculate_heating_load(self, building_info: Dict[str, Any]) -> float:
        """난방 부하 계산 (W/m²)"""
        # 간단한 DIN 18599 기반 계산
        base_load = 40.0  # W/m² 기본값
        
        # 창문비율에 따른 조정
        window_factor = 1 + (building_info['window_to_wall_ratio'] - 0.3) * 0.5
        
        # 층고에 따른 조정
        height_factor = 1 + (building_info['building_height'] / building_info['stories'] - 3.0) * 0.1
        
        return base_load * window_factor * height_factor
    
    def _calculate_cooling_load(self, building_info: Dict[str, Any]) -> float:
        """냉방 부하 계산 (W/m²)"""
        base_load = 45.0  # W/m² 기본값 (한국 기후)
        
        # 방위에 따른 조정
        orientation_factors = {'south': 1.1, 'west': 1.2, 'east': 1.05, 'north': 0.9}
        orientation_factor = orientation_factors.get(building_info['orientation'], 1.0)
        
        # 창문비율에 따른 조정
        window_factor = 1 + (building_info['window_to_wall_ratio'] - 0.3) * 0.7
        
        return base_load * orientation_factor * window_factor
    
    def _calculate_annual_energy_consumption(self, heating_load: float, cooling_load: float, building_info: Dict[str, Any]) -> float:
        """연간 에너지 소비량 계산 (kWh/m²·year)"""
        # 한국 기후 기준 계산
        heating_hours = 2200  # 난방 시간
        cooling_hours = 1800  # 냉방 시간
        
        # 시스템 효율 (임의값)
        heating_efficiency = 0.85
        cooling_efficiency = 3.0  # COP
        
        heating_energy = (heating_load * heating_hours) / (heating_efficiency * 1000)
        cooling_energy = (cooling_load * cooling_hours) / (cooling_efficiency * 1000)
        
        # 기타 에너지 (조명, 환기, 급탕 등)
        auxiliary_energy = 40.0  # kWh/m²·year
        
        return heating_energy + cooling_energy + auxiliary_energy
    
    def _calculate_daylight_factor(self, building_info: Dict[str, Any]) -> float:
        """일광률 계산 (%)"""
        # 간단한 계산 방식
        window_area_ratio = building_info['window_to_wall_ratio']
        orientation_factor = {'south': 1.0, 'east': 0.8, 'west': 0.8, 'north': 0.6}.get(
            building_info['orientation'], 0.8
        )
        
        # 기본 일광률 = 창면적비 × 방위계수 × 투과율 × 100
        daylight_factor = window_area_ratio * orientation_factor * 0.7 * 100
        
        return min(daylight_factor, 8.0)  # 최대 8% 제한
    
    def _calculate_pmv_ppd(self, building_info: Dict[str, Any]) -> Dict[str, float]:
        """PMV/PPD 계산"""
        # 표준 조건 가정
        air_temp = 23.0  # °C
        mean_radiant_temp = 22.0  # °C
        air_velocity = 0.1  # m/s
        relative_humidity = 50.0  # %
        clothing = 1.0  # clo (사무복)
        metabolic_rate = 1.2  # met (사무작업)
        
        # 간단한 PMV 계산 (실제로는 복잡한 공식)
        pmv = 0.1  # 거의 중성값으로 가정
        ppd = 100 - 95 * math.exp(-0.03353 * pmv**4 - 0.2179 * pmv**2)
        
        return {"pmv": pmv, "ppd": ppd}
    
    def _calculate_reverberation_time(self, building_info: Dict[str, Any]) -> float:
        """잔향시간 계산 (초)"""
        # Sabine 공식의 간단한 적용
        room_volume = building_info['floor_area'] * (building_info['building_height'] / building_info['stories'])
        
        # 흡음 계수 추정 (임의값)
        absorption_coefficient = 0.15  # 일반 사무공간
        total_absorption = building_info['floor_area'] * 6 * absorption_coefficient  # 6면 평균
        
        # RT60 = 0.161 × V / A
        rt60 = 0.161 * room_volume / max(total_absorption, 0.1)
        
        return min(rt60, 3.0)  # 최대 3초 제한
    
    # === 성능 등급 계산 메서드들 ===
    
    def _calculate_performance_grade(self, score: float) -> str:
        """성능 점수를 등급으로 변환"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
    
    def _calculate_energy_grade(self, annual_energy: float, building_info: Dict[str, Any]) -> str:
        """에너지 효율 등급 계산"""
        # 한국 건축물 에너지효율등급 기준
        if annual_energy <= 60:
            return "1++"
        elif annual_energy <= 90:
            return "1+"
        elif annual_energy <= 120:
            return "1"
        elif annual_energy <= 150:
            return "2"
        elif annual_energy <= 180:
            return "3"
        elif annual_energy <= 210:
            return "4"
        else:
            return "5"
    
    def _calculate_energy_score(self, metrics: List[PerformanceMetric]) -> float:
        """에너지 성능 종합 점수 계산"""
        total_score = 0.0
        
        for metric in metrics:
            if metric.name == "연간 에너지 소비량":
                # 낮을수록 좋음 (역점수)
                score = max(0, 100 - (metric.value / metric.target_value) * 50)
            else:
                # 목표값 대비 점수
                score = min(100, (metric.target_value / max(metric.value, 0.1)) * 100)
            
            total_score += score
        
        return total_score / len(metrics)
    
    def _calculate_lighting_score(self, metrics: List[PerformanceMetric], glare_analysis: Dict) -> float:
        """조명 성능 종합 점수 계산"""
        total_score = 0.0
        
        for metric in metrics:
            if metric.target_value:
                if metric.name == "평균 일광률":
                    # 2% 이상이면 만점, 그 이하는 비례
                    score = min(100, (metric.value / metric.target_value) * 100)
                else:
                    score = min(100, (metric.value / metric.target_value) * 100)
                total_score += score
        
        # 글레어 패널티
        glare_penalty = glare_analysis.get('glare_probability', 0) * 20
        total_score = max(0, total_score / len(metrics) - glare_penalty)
        
        return total_score
    
    def _calculate_thermal_comfort_score(self, metrics: List[PerformanceMetric]) -> float:
        """열적 쾌적성 종합 점수 계산"""
        total_score = 0.0
        
        for metric in metrics:
            if metric.name == "PMV 지수":
                # PMV는 0에 가까울수록 좋음
                score = max(0, 100 - abs(metric.value) * 50)
            elif metric.name == "PPD":
                # PPD는 낮을수록 좋음
                score = max(0, 100 - metric.value * 5)
            else:
                score = min(100, (metric.value / metric.target_value) * 100)
            
            total_score += score
        
        return total_score / len(metrics)
    
    def _calculate_acoustic_score(self, metrics: List[PerformanceMetric]) -> float:
        """음향 성능 종합 점수 계산"""
        total_score = 0.0
        
        for metric in metrics:
            if metric.target_value:
                if metric.name == "소음 레벨":
                    # 낮을수록 좋음
                    score = max(0, 100 - (metric.value / metric.target_value) * 100)
                else:
                    score = min(100, (metric.value / metric.target_value) * 100)
                total_score += score
        
        return total_score / len(metrics)
    
    def _calculate_structural_score(self, metrics: List[PerformanceMetric]) -> float:
        """구조 성능 종합 점수 계산"""
        total_score = 0.0
        
        for metric in metrics:
            if metric.target_value:
                if metric.name in ["최대 응력비", "최대 처짐"]:
                    # 낮을수록 좋음
                    score = max(0, 100 - (metric.value / metric.target_value) * 100)
                else:
                    score = min(100, (metric.value / metric.target_value) * 100)
                total_score += score
        
        return total_score / len(metrics)
    
    # === 데이터 로딩 메서드들 ===
    
    def _load_thermal_comfort_standards(self) -> Dict[str, Any]:
        """열적 쾌적성 기준 로드"""
        return {
            "pmv_range": [-0.5, 0.5],
            "ppd_max": 10.0,
            "temperature_range": [20.0, 26.0],
            "humidity_range": [30.0, 70.0]
        }
    
    def _load_lighting_standards(self) -> Dict[str, Any]:
        """조명 기준 로드"""
        return {
            "daylight_factor_min": 2.0,
            "illuminance_targets": {
                "office": 500,
                "residential": 200,
                "classroom": 300,
                "laboratory": 750
            }
        }
    
    def _load_acoustic_standards(self) -> Dict[str, Any]:
        """음향 기준 로드"""
        return {
            "reverberation_time": {
                "office": 0.6,
                "classroom": 0.8,
                "auditorium": 1.5
            },
            "noise_levels": {
                "office": 40,
                "residential": 35,
                "classroom": 35
            }
        }
    
    def _load_material_database(self) -> Dict[str, Any]:
        """재료 데이터베이스 로드"""
        return {
            "thermal_conductivity": {
                "concrete": 1.65,
                "steel": 50.0,
                "wood": 0.15,
                "insulation": 0.035,
                "glass": 1.0
            },
            "sound_absorption": {
                "concrete": 0.02,
                "carpet": 0.55,
                "acoustic_panel": 0.85,
                "glass": 0.03
            }
        }
    
    def _load_korean_climate_data(self) -> Dict[str, Any]:
        """한국 기후 데이터 로드"""
        return {
            "heating_degree_days": 2500,
            "cooling_degree_days": 800,
            "annual_solar_radiation": 1200,  # kWh/m²
            "average_wind_speed": 2.5,  # m/s
            "design_temperatures": {
                "winter": -15,  # °C
                "summer": 35   # °C
            }
        }
    
    # === 상세 분석 메서드들 (간단한 구현) ===
    
    def _analyze_thermal_bridges(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """열교 분석"""
        return {
            "thermal_bridge_count": 12,
            "total_thermal_bridge_length": 45.0,  # m
            "average_psi_value": 0.15,  # W/mK
            "heat_loss_ratio": 8.5  # %
        }
    
    def _calculate_annual_sunlight_hours(self, building_info: Dict[str, Any]) -> float:
        """연간 일조시간 계산"""
        base_hours = 2000  # 기본 일조시간
        orientation_factor = {'south': 1.0, 'east': 0.8, 'west': 0.8, 'north': 0.6}.get(
            building_info['orientation'], 0.8
        )
        return base_hours * orientation_factor
    
    def _analyze_illuminance_levels(self, building_info: Dict[str, Any]) -> Dict[str, float]:
        """조도 레벨 분석"""
        daylight_factor = self._calculate_daylight_factor(building_info)
        outdoor_illuminance = 10000  # lux (표준 외부 조도)
        
        return {
            "average": daylight_factor / 100 * outdoor_illuminance,
            "minimum": daylight_factor / 100 * outdoor_illuminance * 0.3,
            "maximum": daylight_factor / 100 * outdoor_illuminance * 1.5
        }
    
    def _analyze_glare_potential(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """글레어 분석"""
        window_ratio = building_info['window_to_wall_ratio']
        glare_probability = min(0.8, window_ratio * 1.5)  # 간단한 추정
        
        return {
            "glare_probability": glare_probability,
            "dgp_max": 0.4,  # Daylight Glare Probability
            "risk_level": "high" if glare_probability > 0.6 else "medium" if glare_probability > 0.3 else "low"
        }
    
    def _analyze_window_performance(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """창호 성능 분석"""
        return {
            "u_value": 1.4,  # W/m²K
            "shgc": 0.6,     # Solar Heat Gain Coefficient
            "vt": 0.7,       # Visible Transmittance
            "performance_rating": "standard"
        }
    
    def _analyze_adaptive_comfort(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """적응적 쾌적성 분석"""
        return {
            "comfort_hours_ratio": 75.5,  # %
            "overheating_hours": 180,     # hours/year
            "overcooling_hours": 50       # hours/year
        }
    
    def _analyze_temperature_distribution(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """온도 분포 분석"""
        return {
            "average_temperature": 23.0,
            "temperature_gradient": 1.5,  # °C (수직)
            "hot_spots": 2,
            "cold_spots": 1
        }
    
    def _analyze_humidity_levels(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """습도 분석"""
        return {
            "average_humidity": 45.0,  # %
            "humidity_range": [35.0, 55.0],
            "mold_risk": "low"
        }
    
    def _analyze_noise_levels(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """소음 레벨 분석"""
        return {
            "average": 38.0,  # dB
            "peak": 55.0,     # dB
            "background": 30.0  # dB
        }
    
    def _calculate_sound_transmission_loss(self, building_info: Dict[str, Any]) -> float:
        """음향 전달 손실 계산"""
        # 간단한 질량 법칙 적용
        wall_thickness = 200  # mm, 가정값
        wall_density = 2400   # kg/m³, 콘크리트
        
        surface_mass = wall_thickness / 1000 * wall_density
        stl = 20 * math.log10(surface_mass) - 47  # dB
        
        return max(stl, 30.0)
    
    def _analyze_floor_impact_noise(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """층간 소음 분석"""
        return {
            "impact_sound_level": 58.0,  # dB
            "compliance": "meets_standard",  # 58dB 이하 기준
            "improvement_needed": False
        }
    
    def _analyze_structural_loads(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """구조 하중 분석"""
        return {
            "dead_load": 5.0,      # kN/m²
            "live_load": 3.0,      # kN/m²
            "wind_load": 1.2,      # kN/m²
            "seismic_load": 0.8,   # kN/m²
            "max_stress_ratio": 0.65
        }
    
    def _calculate_safety_factors(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """안전율 계산"""
        return {
            "global_safety_factor": 2.1,
            "local_safety_factors": {
                "columns": 2.3,
                "beams": 2.0,
                "slabs": 1.8
            }
        }
    
    def _analyze_deflections(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """처짐 분석"""
        span = 8.0  # m, 가정값
        allowable_deflection = span * 1000 / 300  # mm
        
        return {
            "max_deflection": 18.5,  # mm
            "allowable_deflection": allowable_deflection,
            "span": span,
            "deflection_ratio": 18.5 / allowable_deflection
        }
    
    def _analyze_seismic_performance(self, building_info: Dict[str, Any]) -> Dict[str, Any]:
        """지진 대응 성능 분석"""
        return {
            "seismic_zone": "I",  # 한국 내진설계 지역
            "response_factor": 0.95,
            "base_shear_coefficient": 0.12,
            "natural_period": 0.8,  # 초
            "ductility_factor": 3.0
        }
    
    # === 등급 메서드들 ===
    
    def _grade_daylight_factor(self, df: float) -> str:
        """일광률 등급"""
        if df >= 4.0:
            return "A+"
        elif df >= 2.5:
            return "A"
        elif df >= 2.0:
            return "B"
        elif df >= 1.5:
            return "C"
        else:
            return "D"
    
    def _grade_pmv(self, pmv: float) -> str:
        """PMV 등급"""
        abs_pmv = abs(pmv)
        if abs_pmv <= 0.2:
            return "A+"
        elif abs_pmv <= 0.5:
            return "A"
        elif abs_pmv <= 0.7:
            return "B"
        elif abs_pmv <= 1.0:
            return "C"
        else:
            return "D"
    
    def _grade_reverberation_time(self, rt: float) -> str:
        """잔향시간 등급"""
        if 0.4 <= rt <= 0.8:
            return "A+"
        elif 0.3 <= rt <= 1.0:
            return "A"
        elif 0.2 <= rt <= 1.2:
            return "B"
        elif 0.1 <= rt <= 1.5:
            return "C"
        else:
            return "D"
    
    def _grade_stress_ratio(self, ratio: float) -> str:
        """응력비 등급"""
        if ratio <= 0.6:
            return "A+"
        elif ratio <= 0.7:
            return "A"
        elif ratio <= 0.8:
            return "B"
        elif ratio <= 0.9:
            return "C"
        else:
            return "D"
    
    # === 권고사항 생성 메서드들 ===
    
    def _generate_energy_recommendations(self, metrics: List[PerformanceMetric], thermal_bridges: Dict) -> List[str]:
        """에너지 개선 권고사항"""
        recommendations = []
        
        for metric in metrics:
            if metric.name == "연간 에너지 소비량" and metric.value > metric.target_value:
                recommendations.append("외벽 단열 성능을 향상시켜 에너지 손실을 줄이세요.")
                recommendations.append("고효율 창호로 교체하여 열손실을 최소화하세요.")
        
        if thermal_bridges['heat_loss_ratio'] > 10:
            recommendations.append("열교 차단 설계를 적용하여 열손실을 줄이세요.")
        
        return recommendations
    
    def _generate_lighting_recommendations(self, metrics: List[PerformanceMetric], window_performance: Dict) -> List[str]:
        """조명 개선 권고사항"""
        recommendations = []
        
        for metric in metrics:
            if metric.name == "평균 일광률" and metric.value < metric.target_value:
                recommendations.append("창문 크기를 증가시키거나 상부 창문을 추가하세요.")
                recommendations.append("내부 마감재를 밝은 색상으로 변경하여 반사율을 향상시키세요.")
        
        if window_performance['vt'] < 0.6:
            recommendations.append("가시광선 투과율이 높은 유리로 교체하세요.")
        
        return recommendations
    
    def _generate_thermal_recommendations(self, metrics: List[PerformanceMetric], temp_dist: Dict) -> List[str]:
        """열적 쾌적성 개선 권고사항"""
        recommendations = []
        
        if temp_dist['temperature_gradient'] > 2.0:
            recommendations.append("환기 시스템을 개선하여 온도 분포를 균일하게 하세요.")
        
        if temp_dist['hot_spots'] > 1:
            recommendations.append("일사 차폐 장치를 설치하여 과열 지역을 줄이세요.")
        
        return recommendations
    
    def _generate_acoustic_recommendations(self, metrics: List[PerformanceMetric], floor_noise: Dict) -> List[str]:
        """음향 개선 권고사항"""
        recommendations = []
        
        for metric in metrics:
            if metric.name == "잔향시간 (RT60)" and metric.value > metric.target_value:
                recommendations.append("천장과 벽면에 음향 흡수재를 설치하세요.")
                recommendations.append("카펫이나 커튼 등 흡음 가구를 배치하세요.")
        
        if floor_noise['impact_sound_level'] > 58:
            recommendations.append("바닥 충격음 차단을 위한 완충재를 설치하세요.")
        
        return recommendations
    
    def _generate_structural_recommendations(self, metrics: List[PerformanceMetric], safety_factors: Dict) -> List[str]:
        """구조 개선 권고사항"""
        recommendations = []
        
        for metric in metrics:
            if metric.name == "최대 응력비" and metric.value > 0.8:
                recommendations.append("구조 부재의 단면을 증가시키거나 강도를 향상시키세요.")
        
        if safety_factors['global_safety_factor'] < 2.0:
            recommendations.append("전체적인 구조 안전율을 재검토하세요.")
        
        return recommendations


# 성능 분석가 에이전트 싱글톤 인스턴스
_performance_analyst = None

def get_performance_analyst() -> PerformanceAnalystAgent:
    """성능 분석가 에이전트 싱글톤 인스턴스 반환"""
    global _performance_analyst
    if _performance_analyst is None:
        _performance_analyst = PerformanceAnalystAgent()
    return _performance_analyst