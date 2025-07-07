"""
재료 전문가 AI 에이전트
=====================

건축 재료의 선택, 성능, 비용, 지속가능성을 전문적으로 분석하고 추천하는 AI 에이전트

@version 1.0
@author VIBA AI Team  
@date 2025.07.06
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import math

from ..base_agent import BaseVIBAAgent, AgentCapability

logger = logging.getLogger(__name__)


class MaterialCategory(Enum):
    """재료 카테고리"""
    STRUCTURAL = "structural"           # 구조재
    FINISHING = "finishing"             # 마감재
    INSULATION = "insulation"           # 단열재
    WATERPROOFING = "waterproofing"     # 방수재
    ROOFING = "roofing"                 # 지붕재
    FLOORING = "flooring"               # 바닥재
    WALL = "wall"                       # 벽체재
    WINDOW = "window"                   # 창호재
    MECHANICAL = "mechanical"           # 기계설비재
    ELECTRICAL = "electrical"           # 전기설비재


class SustainabilityGrade(Enum):
    """지속가능성 등급"""
    EXCELLENT = "excellent"             # 우수 (A등급)
    GOOD = "good"                       # 양호 (B등급)
    FAIR = "fair"                       # 보통 (C등급)
    POOR = "poor"                       # 미흡 (D등급)
    VERY_POOR = "very_poor"             # 매우미흡 (E등급)


@dataclass
class MaterialPerformance:
    """재료 성능 정보"""
    thermal_conductivity: float = 0.0      # 열전도율 (W/mK)
    fire_resistance: int = 0                # 내화성능 (분)
    water_resistance: float = 0.0           # 내수성 (%)
    durability: int = 0                     # 내구성 (년)
    acoustic_performance: float = 0.0       # 음향성능 (dB)
    thermal_expansion: float = 0.0          # 열팽창계수
    compressive_strength: float = 0.0       # 압축강도 (MPa)
    tensile_strength: float = 0.0           # 인장강도 (MPa)


@dataclass
class MaterialEnvironment:
    """재료 환경 정보"""
    carbon_footprint: float = 0.0          # 탄소발자국 (kg CO2/kg)
    recycled_content: float = 0.0           # 재활용 함량 (%)
    recyclability: float = 0.0              # 재활용 가능성 (%)
    renewable_content: float = 0.0          # 재생가능 함량 (%)
    embodied_energy: float = 0.0            # 내재에너지 (MJ/kg)
    voc_emission: float = 0.0               # VOC 방출량 (mg/m²h)
    sustainability_grade: SustainabilityGrade = SustainabilityGrade.FAIR


@dataclass
class MaterialCost:
    """재료 비용 정보"""
    unit_price: float = 0.0                # 단가 (원/단위)
    unit: str = "m²"                       # 단위
    installation_cost: float = 0.0         # 시공비 (원/단위)
    maintenance_cost: float = 0.0          # 유지비 (원/년/단위)
    lifespan: int = 0                      # 수명 (년)
    total_lifecycle_cost: float = 0.0      # 총 생애주기비용


@dataclass
class BuildingMaterial:
    """건축 재료 정보"""
    material_id: str
    name: str
    category: MaterialCategory
    subcategory: str = ""
    manufacturer: str = ""
    model: str = ""
    description: str = ""
    
    # 성능 정보
    performance: MaterialPerformance = field(default_factory=MaterialPerformance)
    environment: MaterialEnvironment = field(default_factory=MaterialEnvironment)
    cost: MaterialCost = field(default_factory=MaterialCost)
    
    # 적용 정보
    applicable_parts: List[str] = field(default_factory=list)
    climate_suitability: List[str] = field(default_factory=list)
    building_types: List[str] = field(default_factory=list)
    
    # 품질 정보
    certifications: List[str] = field(default_factory=list)
    standards: List[str] = field(default_factory=list)
    quality_grade: str = "B"


class MaterialsSpecialistAgent(BaseVIBAAgent):
    """재료 전문가 AI 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_id="materials_specialist",
            name="건축 재료 전문가",
            capabilities=[
                AgentCapability.PERFORMANCE_ANALYSIS,
                AgentCapability.OPTIMIZATION,
                AgentCapability.QUALITY_ASSESSMENT,
                AgentCapability.NATURAL_LANGUAGE_UNDERSTANDING
            ]
        )
        self.materials_database = self._initialize_materials_database()
        self.material_combinations = {}
        self.performance_cache = {}
        
    async def initialize(self) -> bool:
        """에이전트 초기화"""
        try:
            logger.info("재료 전문가 AI 에이전트 초기화 중...")
            
            # 재료 데이터베이스 로드
            await self._load_material_specifications()
            
            # 성능 분석 모델 준비
            await self._prepare_analysis_models()
            
            logger.info("재료 전문가 AI 에이전트 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"재료 전문가 AI 에이전트 초기화 실패: {e}")
            return False
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행 (추상 메서드 구현)"""
        return await self.process_task_async(task)
    
    async def process_task_async(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """비동기 작업 처리"""
        try:
            task_type = input_data.get("task_type", "material_recommendation")
            
            if task_type == "material_recommendation":
                return await self._recommend_materials(input_data)
            elif task_type == "performance_analysis":
                return await self._analyze_material_performance(input_data)
            elif task_type == "cost_optimization":
                return await self._optimize_material_costs(input_data)
            elif task_type == "sustainability_assessment":
                return await self._assess_sustainability(input_data)
            elif task_type == "material_comparison":
                return await self._compare_materials(input_data)
            else:
                return await self._comprehensive_material_analysis(input_data)
                
        except Exception as e:
            logger.error(f"재료 전문가 작업 처리 실패: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _recommend_materials(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """재료 추천"""
        
        # 입력 데이터 분석
        building_type = input_data.get("building_type", "residential")
        climate_zone = input_data.get("climate_zone", "temperate")
        budget_level = input_data.get("budget_level", "medium")
        sustainability_priority = input_data.get("sustainability_priority", "medium")
        performance_requirements = input_data.get("performance_requirements", {})
        
        # 부위별 재료 추천
        recommendations = {}
        
        # 구조재 추천
        structural_materials = await self._recommend_structural_materials(
            building_type, climate_zone, performance_requirements
        )
        recommendations["structural"] = structural_materials
        
        # 단열재 추천
        insulation_materials = await self._recommend_insulation_materials(
            climate_zone, budget_level, sustainability_priority
        )
        recommendations["insulation"] = insulation_materials
        
        # 마감재 추천
        finishing_materials = await self._recommend_finishing_materials(
            building_type, budget_level, performance_requirements
        )
        recommendations["finishing"] = finishing_materials
        
        # 창호재 추천
        window_materials = await self._recommend_window_materials(
            climate_zone, performance_requirements
        )
        recommendations["windows"] = window_materials
        
        # 지붕재 추천
        roofing_materials = await self._recommend_roofing_materials(
            climate_zone, building_type, sustainability_priority
        )
        recommendations["roofing"] = roofing_materials
        
        # 총 비용 및 성능 분석
        try:
            total_analysis = await self._analyze_total_system_performance(recommendations)
        except Exception as e:
            logger.error(f"전체 시스템 성능 분석 실패: {e}")
            total_analysis = {
                "total_cost": 0,
                "sustainability_score": 0,
                "performance_score": 0
            }
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "task_type": "material_recommendation",
            "building_type": building_type,
            "climate_zone": climate_zone,
            "recommendations": recommendations,
            "total_analysis": total_analysis,
            "summary": {
                "total_materials": sum(len(materials) for materials in recommendations.values()),
                "estimated_cost": total_analysis.get("total_cost", 0),
                "overall_sustainability": total_analysis.get("sustainability_score", 0),
                "performance_score": total_analysis.get("performance_score", 0)
            }
        }
    
    async def _recommend_structural_materials(self, building_type: str, climate_zone: str, 
                                            requirements: Dict) -> List[Dict[str, Any]]:
        """구조재 추천"""
        
        if building_type in ["residential", "low_rise"]:
            # 저층 건물용 구조재
            materials = [
                {
                    "material_id": "concrete_c24",
                    "name": "일반콘크리트 C24",
                    "type": "concrete",
                    "strength": "24 MPa",
                    "application": "기초, 기둥, 보",
                    "cost_per_m3": 120000,
                    "sustainability_score": 6.5,
                    "advantages": ["경제적", "시공성 양호", "내구성 우수"],
                    "considerations": ["탄소배출량 높음"]
                },
                {
                    "material_id": "steel_sm490",
                    "name": "구조용강재 SM490",
                    "type": "steel",
                    "strength": "490 MPa",
                    "application": "골조, 지붕 구조",
                    "cost_per_kg": 1200,
                    "sustainability_score": 7.2,
                    "advantages": ["고강도", "재활용 가능", "시공 신속"],
                    "considerations": ["부식 방지 필요"]
                },
                {
                    "material_id": "glulam_24f",
                    "name": "집성재 24f-v5",
                    "type": "engineered_wood",
                    "strength": "24 MPa",
                    "application": "보, 기둥, 지붕 구조",
                    "cost_per_m3": 850000,
                    "sustainability_score": 9.1,
                    "advantages": ["친환경", "가벼움", "미적효과"],
                    "considerations": ["화재 방지 처리 필요"]
                }
            ]
        else:
            # 고층 건물용 구조재
            materials = [
                {
                    "material_id": "concrete_c35",
                    "name": "고강도콘크리트 C35",
                    "type": "high_strength_concrete",
                    "strength": "35 MPa",
                    "application": "기둥, 벽체, 코어",
                    "cost_per_m3": 180000,
                    "sustainability_score": 6.8,
                    "advantages": ["고강도", "내구성", "경제성"],
                    "considerations": ["양생 관리 중요"]
                },
                {
                    "material_id": "steel_sm570",
                    "name": "고강도강재 SM570",
                    "type": "high_strength_steel",
                    "strength": "570 MPa",
                    "application": "주요 골조",
                    "cost_per_kg": 1400,
                    "sustainability_score": 7.5,
                    "advantages": ["초고강도", "경량화", "내진성"],
                    "considerations": ["용접 기술 요구"]
                }
            ]
        
        # 기후 조건에 따른 추가 고려사항
        for material in materials:
            if climate_zone == "humid":
                material["climate_considerations"] = ["습도 방지", "곰팡이 저항성"]
            elif climate_zone == "cold":
                material["climate_considerations"] = ["동결융해 저항성", "열교 방지"]
            elif climate_zone == "hot":
                material["climate_considerations"] = ["열팽창 고려", "자외선 저항성"]
        
        return materials
    
    async def _recommend_insulation_materials(self, climate_zone: str, budget_level: str, 
                                            sustainability_priority: str) -> List[Dict[str, Any]]:
        """단열재 추천"""
        
        materials = []
        
        if sustainability_priority == "high":
            # 친환경 단열재 우선
            materials.extend([
                {
                    "material_id": "cellulose_insulation",
                    "name": "셀룰로오스 단열재",
                    "type": "natural",
                    "thermal_conductivity": 0.039,
                    "thickness_mm": 150,
                    "cost_per_m2": 15000,
                    "sustainability_score": 9.2,
                    "recycled_content": 85,
                    "advantages": ["재활용 소재", "우수한 단열성", "흡음성"],
                    "applications": ["벽체", "지붕", "바닥"]
                },
                {
                    "material_id": "sheep_wool_insulation",
                    "name": "양털 단열재",
                    "type": "natural",
                    "thermal_conductivity": 0.035,
                    "thickness_mm": 100,
                    "cost_per_m2": 25000,
                    "sustainability_score": 9.5,
                    "advantages": ["천연소재", "습도조절", "무독성"],
                    "applications": ["내벽", "지붕"]
                }
            ])
        
        if budget_level in ["low", "medium"]:
            # 경제적 단열재
            materials.extend([
                {
                    "material_id": "eps_insulation",
                    "name": "비드법단열재 (EPS)",
                    "type": "synthetic",
                    "thermal_conductivity": 0.031,
                    "thickness_mm": 100,
                    "cost_per_m2": 8000,
                    "sustainability_score": 5.5,
                    "advantages": ["경제적", "시공 용이", "경량"],
                    "applications": ["외벽", "지붕", "바닥"]
                },
                {
                    "material_id": "rockwool_insulation",
                    "name": "암면 단열재",
                    "type": "mineral",
                    "thermal_conductivity": 0.034,
                    "thickness_mm": 100,
                    "cost_per_m2": 12000,
                    "sustainability_score": 7.1,
                    "advantages": ["내화성", "흡음성", "내구성"],
                    "applications": ["벽체", "지붕", "바닥"]
                }
            ])
        
        if budget_level == "high":
            # 고성능 단열재
            materials.extend([
                {
                    "material_id": "polyurethane_foam",
                    "name": "폴리우레탄 단열재",
                    "type": "high_performance",
                    "thermal_conductivity": 0.020,
                    "thickness_mm": 80,
                    "cost_per_m2": 35000,
                    "sustainability_score": 6.2,
                    "advantages": ["최고 단열성능", "접착력 우수", "기밀성"],
                    "applications": ["외벽", "지붕"]
                },
                {
                    "material_id": "aerogel_insulation",
                    "name": "에어로겔 단열재",
                    "type": "ultra_high_performance",
                    "thermal_conductivity": 0.013,
                    "thickness_mm": 50,
                    "cost_per_m2": 80000,
                    "sustainability_score": 7.8,
                    "advantages": ["초고성능", "얇은 두께", "내화성"],
                    "applications": ["특수부위", "제약공간"]
                }
            ])
        
        # 기후별 특화 추천
        climate_specific = self._get_climate_specific_insulation(climate_zone)
        materials.extend(climate_specific)
        
        return materials
    
    async def _recommend_finishing_materials(self, building_type: str, budget_level: str, 
                                           requirements: Dict) -> List[Dict[str, Any]]:
        """마감재 추천"""
        
        materials = {
            "interior_wall": [],
            "exterior_wall": [],
            "flooring": [],
            "ceiling": []
        }
        
        # 내부 벽체 마감재
        if budget_level == "high":
            materials["interior_wall"].extend([
                {
                    "material_id": "natural_stone_marble",
                    "name": "천연석 (대리석)",
                    "cost_per_m2": 80000,
                    "durability_years": 50,
                    "maintenance": "low",
                    "sustainability_score": 7.5,
                    "advantages": ["고급감", "내구성", "내열성"]
                },
                {
                    "material_id": "solid_wood_panel",
                    "name": "원목패널",
                    "cost_per_m2": 60000,
                    "durability_years": 30,
                    "maintenance": "medium",
                    "sustainability_score": 8.8,
                    "advantages": ["친환경", "온화감", "흡습성"]
                }
            ])
        else:
            materials["interior_wall"].extend([
                {
                    "material_id": "ceramic_tile",
                    "name": "세라믹 타일",
                    "cost_per_m2": 25000,
                    "durability_years": 25,
                    "maintenance": "low",
                    "sustainability_score": 6.8,
                    "advantages": ["경제적", "다양한 디자인", "청소 용이"]
                },
                {
                    "material_id": "wallpaper_vinyl",
                    "name": "비닐 벽지",
                    "cost_per_m2": 8000,
                    "durability_years": 10,
                    "maintenance": "low",
                    "sustainability_score": 4.2,
                    "advantages": ["저렴", "시공 용이", "교체 용이"]
                }
            ])
        
        # 외부 벽체 마감재
        materials["exterior_wall"].extend([
            {
                "material_id": "brick_exterior",
                "name": "적벽돌",
                "cost_per_m2": 45000,
                "durability_years": 100,
                "maintenance": "very_low",
                "sustainability_score": 8.5,
                "advantages": ["초장기내구성", "단열효과", "전통미"]
            },
            {
                "material_id": "fiber_cement_siding",
                "name": "섬유시멘트 사이딩",
                "cost_per_m2": 35000,
                "durability_years": 30,
                "maintenance": "low",
                "sustainability_score": 7.2,
                "advantages": ["내화성", "내후성", "다양한 텍스처"]
            },
            {
                "material_id": "metal_panel",
                "name": "금속패널",
                "cost_per_m2": 55000,
                "durability_years": 40,
                "maintenance": "low",
                "sustainability_score": 7.8,
                "advantages": ["경량", "재활용가능", "현대적 디자인"]
            }
        ])
        
        # 바닥재
        if building_type == "residential":
            materials["flooring"].extend([
                {
                    "material_id": "hardwood_oak",
                    "name": "참나무 원목마루",
                    "cost_per_m2": 50000,
                    "durability_years": 50,
                    "sustainability_score": 8.9,
                    "advantages": ["천연소재", "온화감", "가치상승"]
                },
                {
                    "material_id": "laminate_flooring",
                    "name": "강화마루",
                    "cost_per_m2": 20000,
                    "durability_years": 15,
                    "sustainability_score": 6.1,
                    "advantages": ["경제적", "내마모성", "시공 용이"]
                }
            ])
        else:
            materials["flooring"].extend([
                {
                    "material_id": "polished_concrete",
                    "name": "연마콘크리트",
                    "cost_per_m2": 30000,
                    "durability_years": 30,
                    "sustainability_score": 8.2,
                    "advantages": ["내구성", "유지보수 용이", "산업적 미감"]
                },
                {
                    "material_id": "vinyl_tile",
                    "name": "비닐타일",
                    "cost_per_m2": 15000,
                    "durability_years": 20,
                    "sustainability_score": 5.5,
                    "advantages": ["방수성", "시공 신속", "다양한 패턴"]
                }
            ])
        
        return materials
    
    async def _recommend_window_materials(self, climate_zone: str, 
                                        requirements: Dict) -> List[Dict[str, Any]]:
        """창호재 추천"""
        
        materials = []
        
        if climate_zone in ["cold", "very_cold"]:
            # 고단열 창호
            materials.extend([
                {
                    "material_id": "triple_glazed_upvc",
                    "name": "3중유리 PVC창",
                    "frame_material": "UPVC",
                    "glazing": "triple_low_e",
                    "u_value": 0.8,
                    "cost_per_m2": 250000,
                    "sustainability_score": 7.5,
                    "advantages": ["최고 단열성능", "결로 방지", "경제적"]
                },
                {
                    "material_id": "triple_glazed_wood",
                    "name": "3중유리 목재창",
                    "frame_material": "engineered_wood",
                    "glazing": "triple_low_e_argon",
                    "u_value": 0.7,
                    "cost_per_m2": 350000,
                    "sustainability_score": 9.1,
                    "advantages": ["친환경", "미적효과", "초고단열"]
                }
            ])
        elif climate_zone in ["hot", "very_hot"]:
            # 차열 성능 우선
            materials.extend([
                {
                    "material_id": "double_glazed_aluminum",
                    "name": "2중유리 알루미늄창",
                    "frame_material": "thermal_break_aluminum",
                    "glazing": "double_solar_control",
                    "shgc": 0.25,
                    "cost_per_m2": 180000,
                    "sustainability_score": 6.8,
                    "advantages": ["차열성능", "내구성", "경량"]
                },
                {
                    "material_id": "high_performance_glazing",
                    "name": "고성능 차열유리창",
                    "frame_material": "composite",
                    "glazing": "spectrally_selective",
                    "shgc": 0.18,
                    "cost_per_m2": 320000,
                    "sustainability_score": 8.2,
                    "advantages": ["최고 차열성능", "자연채광 확보"]
                }
            ])
        else:
            # 균형적 성능
            materials.extend([
                {
                    "material_id": "double_glazed_upvc",
                    "name": "2중유리 PVC창",
                    "frame_material": "UPVC",
                    "glazing": "double_low_e",
                    "u_value": 1.4,
                    "cost_per_m2": 150000,
                    "sustainability_score": 7.2,
                    "advantages": ["균형적 성능", "경제적", "유지보수 용이"]
                },
                {
                    "material_id": "wood_aluminum_composite",
                    "name": "우드-알루미늄 복합창",
                    "frame_material": "wood_aluminum",
                    "glazing": "double_low_e",
                    "u_value": 1.2,
                    "cost_per_m2": 280000,
                    "sustainability_score": 8.5,
                    "advantages": ["미적효과", "고성능", "내구성"]
                }
            ])
        
        return materials
    
    async def _recommend_roofing_materials(self, climate_zone: str, building_type: str, 
                                         sustainability_priority: str) -> List[Dict[str, Any]]:
        """지붕재 추천"""
        
        materials = []
        
        if sustainability_priority == "high":
            materials.extend([
                {
                    "material_id": "clay_tile_traditional",
                    "name": "전통 기와",
                    "material_type": "ceramic",
                    "lifespan_years": 100,
                    "cost_per_m2": 45000,
                    "sustainability_score": 9.2,
                    "advantages": ["초장수명", "재활용가능", "전통미", "단열효과"]
                },
                {
                    "material_id": "green_roof_extensive",
                    "name": "경량형 녹화지붕",
                    "material_type": "living_roof",
                    "lifespan_years": 40,
                    "cost_per_m2": 80000,
                    "sustainability_score": 9.8,
                    "advantages": ["최고 친환경성", "단열효과", "빗물관리", "생태적"]
                }
            ])
        
        if climate_zone in ["hot", "very_hot"]:
            materials.extend([
                {
                    "material_id": "cool_roof_membrane",
                    "name": "쿨루프 멤브레인",
                    "material_type": "reflective_membrane",
                    "lifespan_years": 25,
                    "cost_per_m2": 35000,
                    "solar_reflectance": 0.85,
                    "sustainability_score": 8.1,
                    "advantages": ["열섬효과 저감", "에너지 절약", "내구성"]
                },
                {
                    "material_id": "metal_roof_reflective",
                    "name": "고반사 금속지붕",
                    "material_type": "coated_steel",
                    "lifespan_years": 50,
                    "cost_per_m2": 60000,
                    "solar_reflectance": 0.75,
                    "sustainability_score": 8.5,
                    "advantages": ["장수명", "재활용가능", "반사성능"]
                }
            ])
        
        if building_type == "residential":
            materials.extend([
                {
                    "material_id": "asphalt_shingle_architectural",
                    "name": "건축용 아스팔트 슁글",
                    "material_type": "composite",
                    "lifespan_years": 30,
                    "cost_per_m2": 25000,
                    "sustainability_score": 6.2,
                    "advantages": ["경제적", "시공 용이", "다양한 색상"]
                },
                {
                    "material_id": "concrete_tile",
                    "name": "콘크리트 기와",
                    "material_type": "concrete",
                    "lifespan_years": 50,
                    "cost_per_m2": 40000,
                    "sustainability_score": 7.8,
                    "advantages": ["내구성", "화재저항", "단열효과"]
                }
            ])
        
        return materials
    
    def _get_climate_specific_insulation(self, climate_zone: str) -> List[Dict[str, Any]]:
        """기후별 특화 단열재"""
        
        if climate_zone == "humid":
            return [
                {
                    "material_id": "breathable_insulation",
                    "name": "투습 단열재",
                    "type": "breathable",
                    "vapor_permeability": "high",
                    "mold_resistance": "excellent",
                    "cost_per_m2": 18000,
                    "sustainability_score": 8.2,
                    "advantages": ["곰팡이 방지", "습도 조절", "투습성"]
                }
            ]
        elif climate_zone == "seismic":
            return [
                {
                    "material_id": "flexible_insulation",
                    "name": "유연 단열재",
                    "type": "flexible",
                    "seismic_compatibility": "excellent",
                    "cost_per_m2": 22000,
                    "sustainability_score": 7.8,
                    "advantages": ["내진성", "유연성", "균열 방지"]
                }
            ]
        
        return []
    
    async def _analyze_material_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """재료 성능 분석"""
        
        materials = input_data.get("materials", [])
        analysis_type = input_data.get("analysis_type", "comprehensive")
        
        results = {}
        
        for material in materials:
            material_id = material.get("material_id", "")
            material_data = self.materials_database.get(material_id, {})
            
            performance_analysis = {
                "thermal_performance": self._analyze_thermal_performance(material_data),
                "structural_performance": self._analyze_structural_performance(material_data),
                "durability_analysis": self._analyze_durability(material_data),
                "environmental_impact": self._analyze_environmental_impact(material_data),
                "cost_effectiveness": self._analyze_cost_effectiveness(material_data)
            }
            
            results[material_id] = performance_analysis
        
        # 종합 평가
        overall_assessment = self._generate_overall_assessment(results)
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "task_type": "performance_analysis",
            "analysis_type": analysis_type,
            "individual_results": results,
            "overall_assessment": overall_assessment
        }
    
    async def _optimize_material_costs(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """재료 비용 최적화"""
        
        budget_constraint = input_data.get("budget_constraint", 0)
        performance_targets = input_data.get("performance_targets", {})
        building_requirements = input_data.get("building_requirements", {})
        
        # 최적화 알고리즘 실행
        optimization_results = await self._run_cost_optimization_algorithm(
            budget_constraint, performance_targets, building_requirements
        )
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "task_type": "cost_optimization",
            "optimization_results": optimization_results,
            "cost_savings": optimization_results.get("cost_savings", 0),
            "performance_impact": optimization_results.get("performance_impact", {})
        }
    
    async def _assess_sustainability(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """지속가능성 평가"""
        
        materials = input_data.get("materials", [])
        assessment_criteria = input_data.get("criteria", ["carbon_footprint", "recyclability", "durability"])
        
        sustainability_scores = {}
        
        for material in materials:
            material_id = material.get("material_id", "")
            material_data = self.materials_database.get(material_id, {})
            
            score = self._calculate_sustainability_score(material_data, assessment_criteria)
            sustainability_scores[material_id] = score
        
        # 총합 지속가능성 점수
        overall_score = sum(sustainability_scores.values()) / len(sustainability_scores) if sustainability_scores else 0
        
        # 개선 제안
        improvement_suggestions = self._generate_sustainability_improvements(sustainability_scores)
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "task_type": "sustainability_assessment",
            "individual_scores": sustainability_scores,
            "overall_sustainability_score": overall_score,
            "sustainability_grade": self._get_sustainability_grade(overall_score),
            "improvement_suggestions": improvement_suggestions
        }
    
    async def _compare_materials(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """재료 비교 분석"""
        
        materials_to_compare = input_data.get("materials", [])
        comparison_criteria = input_data.get("criteria", ["cost", "performance", "sustainability", "durability"])
        
        comparison_matrix = {}
        
        for criterion in comparison_criteria:
            comparison_matrix[criterion] = {}
            
            for material in materials_to_compare:
                material_id = material.get("material_id", "")
                material_data = self.materials_database.get(material_id, {})
                
                score = self._evaluate_material_criterion(material_data, criterion)
                comparison_matrix[criterion][material_id] = score
        
        # 최적 선택 추천
        recommendations = self._generate_material_recommendations(comparison_matrix, materials_to_compare)
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "task_type": "material_comparison",
            "comparison_matrix": comparison_matrix,
            "recommendations": recommendations
        }
    
    async def _comprehensive_material_analysis(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """종합 재료 분석"""
        
        user_input = input_data.get("user_input", "")
        context = input_data.get("context", {})
        
        # 자연어 입력 분석
        analysis_requirements = self._parse_user_requirements(user_input)
        
        # 각 분석 수행
        results = {}
        
        if analysis_requirements.get("need_recommendation", True):
            results["recommendations"] = await self._recommend_materials({
                **analysis_requirements,
                **context
            })
        
        if analysis_requirements.get("need_performance_analysis", False):
            results["performance_analysis"] = await self._analyze_material_performance({
                "materials": analysis_requirements.get("materials", []),
                **context
            })
        
        if analysis_requirements.get("need_cost_optimization", False):
            results["cost_optimization"] = await self._optimize_material_costs({
                **analysis_requirements,
                **context
            })
        
        if analysis_requirements.get("need_sustainability", False):
            results["sustainability"] = await self._assess_sustainability({
                "materials": analysis_requirements.get("materials", []),
                **context
            })
        
        # 종합 요약
        summary = self._generate_comprehensive_summary(results, analysis_requirements)
        
        return {
            "success": True,
            "agent_id": self.agent_id,
            "task_type": "comprehensive_analysis",
            "user_requirements": analysis_requirements,
            "detailed_results": results,
            "summary": summary
        }
    
    def _parse_user_requirements(self, user_input: str) -> Dict[str, Any]:
        """사용자 요구사항 파싱"""
        
        # 키워드 기반 분석
        requirements = {
            "building_type": "residential",
            "climate_zone": "temperate",
            "budget_level": "medium",
            "sustainability_priority": "medium",
            "need_recommendation": True,
            "need_performance_analysis": False,
            "need_cost_optimization": False,
            "need_sustainability": False
        }
        
        # 건물 유형 식별
        if any(word in user_input for word in ["아파트", "주택", "빌라", "주거"]):
            requirements["building_type"] = "residential"
        elif any(word in user_input for word in ["상업", "사무", "오피스", "상가"]):
            requirements["building_type"] = "commercial"
        elif any(word in user_input for word in ["공장", "창고", "산업"]):
            requirements["building_type"] = "industrial"
        
        # 예산 수준 식별
        if any(word in user_input for word in ["저렴", "경제적", "싸게", "예산"]):
            requirements["budget_level"] = "low"
        elif any(word in user_input for word in ["고급", "프리미엄", "최고급"]):
            requirements["budget_level"] = "high"
        
        # 지속가능성 우선순위
        if any(word in user_input for word in ["친환경", "녹색", "지속가능", "에코"]):
            requirements["sustainability_priority"] = "high"
            requirements["need_sustainability"] = True
        
        # 분석 요구사항
        if any(word in user_input for word in ["성능", "분석", "평가"]):
            requirements["need_performance_analysis"] = True
        
        if any(word in user_input for word in ["비용", "가격", "경제성", "최적화"]):
            requirements["need_cost_optimization"] = True
        
        return requirements
    
    def _initialize_materials_database(self) -> Dict[str, Any]:
        """재료 데이터베이스 초기화"""
        
        # 기본 재료 데이터베이스 (실제로는 외부 DB에서 로드)
        return {
            "concrete_c24": {
                "name": "일반콘크리트 C24",
                "category": MaterialCategory.STRUCTURAL,
                "performance": {
                    "compressive_strength": 24.0,
                    "thermal_conductivity": 1.7,
                    "fire_resistance": 120,
                    "durability": 50
                },
                "cost": {
                    "unit_price": 120000,
                    "unit": "m³",
                    "lifespan": 50
                },
                "environment": {
                    "carbon_footprint": 0.3,
                    "recycled_content": 10,
                    "sustainability_grade": SustainabilityGrade.FAIR
                }
            }
            # 추가 재료들...
        }
    
    async def _load_material_specifications(self):
        """재료 사양 로드"""
        # 실제로는 외부 데이터베이스나 API에서 로드
        pass
    
    async def _prepare_analysis_models(self):
        """분석 모델 준비"""
        # 실제로는 ML 모델 로드 및 초기화
        pass
    
    def _analyze_thermal_performance(self, material_data: Dict) -> Dict[str, Any]:
        """열성능 분석"""
        return {
            "thermal_conductivity": material_data.get("performance", {}).get("thermal_conductivity", 0),
            "thermal_resistance": 1.0 / material_data.get("performance", {}).get("thermal_conductivity", 1.0),
            "grade": "good"
        }
    
    def _analyze_structural_performance(self, material_data: Dict) -> Dict[str, Any]:
        """구조 성능 분석"""
        return {
            "compressive_strength": material_data.get("performance", {}).get("compressive_strength", 0),
            "tensile_strength": material_data.get("performance", {}).get("tensile_strength", 0),
            "grade": "satisfactory"
        }
    
    def _analyze_durability(self, material_data: Dict) -> Dict[str, Any]:
        """내구성 분석"""
        return {
            "expected_lifespan": material_data.get("performance", {}).get("durability", 0),
            "maintenance_requirements": "low",
            "grade": "good"
        }
    
    def _analyze_environmental_impact(self, material_data: Dict) -> Dict[str, Any]:
        """환경 영향 분석"""
        return {
            "carbon_footprint": material_data.get("environment", {}).get("carbon_footprint", 0),
            "recyclability": material_data.get("environment", {}).get("recycled_content", 0),
            "grade": "fair"
        }
    
    def _analyze_cost_effectiveness(self, material_data: Dict) -> Dict[str, Any]:
        """비용 효율성 분석"""
        return {
            "initial_cost": material_data.get("cost", {}).get("unit_price", 0),
            "lifecycle_cost": material_data.get("cost", {}).get("unit_price", 0) * 1.5,
            "grade": "good"
        }
    
    def _generate_overall_assessment(self, results: Dict) -> Dict[str, Any]:
        """전체 평가 생성"""
        return {
            "overall_grade": "satisfactory",
            "key_strengths": ["경제성", "내구성"],
            "improvement_areas": ["지속가능성"],
            "recommendations": ["친환경 재료 고려"]
        }
    
    async def _run_cost_optimization_algorithm(self, budget: float, targets: Dict, 
                                             requirements: Dict) -> Dict[str, Any]:
        """비용 최적화 알고리즘"""
        return {
            "optimized_materials": [],
            "cost_savings": budget * 0.15,
            "performance_impact": {"thermal": "maintained", "structural": "improved"}
        }
    
    def _calculate_sustainability_score(self, material_data: Dict, criteria: List[str]) -> float:
        """지속가능성 점수 계산"""
        # 간단한 점수 계산 (실제로는 더 복잡한 알고리즘)
        base_score = 7.0
        
        env_data = material_data.get("environment", {})
        if "carbon_footprint" in criteria:
            carbon = env_data.get("carbon_footprint", 0.5)
            base_score -= carbon * 2  # 탄소발자국이 높을수록 점수 감소
        
        if "recyclability" in criteria:
            recycled = env_data.get("recycled_content", 0) / 100
            base_score += recycled * 2  # 재활용 함량이 높을수록 점수 증가
        
        return max(1.0, min(10.0, base_score))
    
    def _get_sustainability_grade(self, score: float) -> str:
        """지속가능성 등급"""
        if score >= 9.0:
            return "A"
        elif score >= 8.0:
            return "B"
        elif score >= 7.0:
            return "C"
        elif score >= 6.0:
            return "D"
        else:
            return "E"
    
    def _generate_sustainability_improvements(self, scores: Dict) -> List[str]:
        """지속가능성 개선 제안"""
        suggestions = []
        
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        
        if avg_score < 7.0:
            suggestions.append("재활용 함량이 높은 재료로 대체 검토")
            suggestions.append("탄소발자국이 낮은 지역 재료 사용 고려")
        
        if avg_score < 6.0:
            suggestions.append("친환경 인증 재료 우선 선택")
            suggestions.append("재생가능 에너지로 생산된 재료 고려")
        
        return suggestions
    
    def _evaluate_material_criterion(self, material_data: Dict, criterion: str) -> float:
        """재료 기준 평가"""
        # 기준별 점수 계산
        if criterion == "cost":
            cost = material_data.get("cost", {}).get("unit_price", 100000)
            return max(1, 10 - (cost / 50000))  # 가격이 낮을수록 높은 점수
        elif criterion == "sustainability":
            return self._calculate_sustainability_score(material_data, ["carbon_footprint", "recyclability"])
        elif criterion == "durability":
            durability = material_data.get("performance", {}).get("durability", 20)
            return min(10, durability / 10)  # 내구성이 높을수록 높은 점수
        else:
            return 5.0  # 기본 점수
    
    def _generate_material_recommendations(self, comparison_matrix: Dict, materials: List) -> List[Dict]:
        """재료 추천 생성"""
        recommendations = []
        
        for material in materials:
            material_id = material.get("material_id", "")
            
            # 종합 점수 계산
            total_score = 0
            criteria_count = 0
            
            for criterion, scores in comparison_matrix.items():
                if material_id in scores:
                    total_score += scores[material_id]
                    criteria_count += 1
            
            avg_score = total_score / criteria_count if criteria_count > 0 else 0
            
            recommendations.append({
                "material_id": material_id,
                "overall_score": avg_score,
                "recommendation": "추천" if avg_score >= 7.0 else "검토 필요",
                "strengths": self._identify_material_strengths(material_id, comparison_matrix),
                "weaknesses": self._identify_material_weaknesses(material_id, comparison_matrix)
            })
        
        # 점수순 정렬
        recommendations.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return recommendations
    
    def _identify_material_strengths(self, material_id: str, comparison_matrix: Dict) -> List[str]:
        """재료 강점 식별"""
        strengths = []
        
        for criterion, scores in comparison_matrix.items():
            if material_id in scores and scores[material_id] >= 8.0:
                strengths.append(criterion)
        
        return strengths
    
    def _identify_material_weaknesses(self, material_id: str, comparison_matrix: Dict) -> List[str]:
        """재료 약점 식별"""
        weaknesses = []
        
        for criterion, scores in comparison_matrix.items():
            if material_id in scores and scores[material_id] <= 5.0:
                weaknesses.append(criterion)
        
        return weaknesses
    
    def _generate_comprehensive_summary(self, results: Dict, requirements: Dict) -> Dict[str, Any]:
        """종합 요약 생성"""
        
        summary = {
            "total_materials_analyzed": 0,
            "top_recommendations": [],
            "cost_analysis": {},
            "sustainability_summary": {},
            "key_insights": [],
            "next_steps": []
        }
        
        # 결과 분석
        if "recommendations" in results:
            rec_data = results["recommendations"]
            if rec_data.get("success"):
                try:
                    summary["total_materials_analyzed"] = rec_data["summary"]["total_materials"]
                    summary["top_recommendations"] = self._extract_top_recommendations(rec_data)
                except Exception as e:
                    logger.error(f"추천 결과 분석 실패: {e}")
                    summary["total_materials_analyzed"] = 0
                    summary["top_recommendations"] = []
        
        # 핵심 인사이트 생성
        summary["key_insights"] = [
            "경제성과 성능의 균형을 고려한 재료 선택이 중요합니다",
            "지역 기후 특성에 맞는 재료 선택으로 장기 성능을 확보할 수 있습니다",
            "지속가능한 재료 사용으로 환경 부담을 줄이고 장기 가치를 높일 수 있습니다"
        ]
        
        # 다음 단계 제안
        summary["next_steps"] = [
            "선택된 재료의 상세 시방서 검토",
            "공급업체 및 시공업체와의 협의",
            "최종 비용 산출 및 예산 조정",
            "시공 일정에 따른 재료 공급 계획 수립"
        ]
        
        return summary
    
    def _extract_top_recommendations(self, rec_data: Dict) -> List[Dict]:
        """최상위 추천 재료 추출"""
        top_recs = []
        
        recommendations = rec_data.get("recommendations", {})
        
        for category, materials in recommendations.items():
            if materials and len(materials) > 0:
                # 각 카테고리에서 최고 점수 재료 선택
                best_material = max(materials, key=lambda x: x.get("sustainability_score", 0))
                top_recs.append({
                    "category": category,
                    "material": best_material.get("name", ""),
                    "reason": f"최고 {category} 성능 및 지속가능성"
                })
        
        return top_recs[:5]  # 상위 5개만 반환
    
    async def _analyze_total_system_performance(self, recommendations: Dict) -> Dict[str, Any]:
        """전체 시스템 성능 분석"""
        
        total_cost = 0
        sustainability_scores = []
        performance_scores = []
        
        for category, materials in recommendations.items():
            if materials:
                # 첫 번째 추천 재료 기준으로 계산
                material = materials[0]
                total_cost += material.get("cost_per_m2", 0) * 100  # 가정: 100m² 기준
                sustainability_scores.append(material.get("sustainability_score", 5.0))
                performance_scores.append(7.0)  # 기본 성능 점수
        
        avg_sustainability = sum(sustainability_scores) / len(sustainability_scores) if sustainability_scores else 0
        avg_performance = sum(performance_scores) / len(performance_scores) if performance_scores else 0
        
        return {
            "total_cost": total_cost,
            "sustainability_score": avg_sustainability,
            "performance_score": avg_performance,
            "cost_per_sqm": total_cost / 100 if total_cost > 0 else 0,
            "overall_grade": self._calculate_overall_grade(avg_sustainability, avg_performance, total_cost)
        }
    
    def _calculate_overall_grade(self, sustainability: float, performance: float, cost: float) -> str:
        """전체 등급 계산"""
        
        # 정규화된 점수 계산
        sust_norm = sustainability / 10.0
        perf_norm = performance / 10.0
        cost_norm = max(0, 1 - (cost / 10000000))  # 1천만원 기준 정규화
        
        # 가중 평균
        overall_score = (sust_norm * 0.3 + perf_norm * 0.4 + cost_norm * 0.3) * 100
        
        if overall_score >= 90:
            return "A"
        elif overall_score >= 80:
            return "B"
        elif overall_score >= 70:
            return "C"
        elif overall_score >= 60:
            return "D"
        else:
            return "E"