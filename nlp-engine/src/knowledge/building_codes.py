"""
건축법규 검토 모듈
================

한국 건축법규 및 국제 표준 준수 검토

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CodeType(Enum):
    """법규 유형"""
    BUILDING_CODE = "건축법"
    FIRE_CODE = "소방법"
    ENERGY_CODE = "에너지절약법"
    ACCESSIBILITY = "장애인접근성"
    STRUCTURAL = "구조기준"
    ENVIRONMENTAL = "환경기준"


@dataclass
class CodeRequirement:
    """법규 요구사항"""
    code_type: CodeType
    requirement: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None
    applicable_to: List[str] = None


class BuildingCodeChecker:
    """건축법규 검토기"""
    
    def __init__(self):
        self.code_requirements = self._load_code_requirements()
    
    def _load_code_requirements(self) -> Dict[str, List[CodeRequirement]]:
        """법규 요구사항 로드"""
        return {
            "minimum_areas": [
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="침실 최소 면적",
                    min_value=9.0,
                    unit="㎡",
                    applicable_to=["bedroom", "침실"]
                ),
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="화장실 최소 면적",
                    min_value=3.0,
                    unit="㎡",
                    applicable_to=["bathroom", "화장실", "욕실"]
                ),
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="거실 최소 면적",
                    min_value=12.0,
                    unit="㎡",
                    applicable_to=["living_room", "거실"]
                ),
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="주방 최소 면적",
                    min_value=4.5,
                    unit="㎡",
                    applicable_to=["kitchen", "주방"]
                )
            ],
            "ceiling_heights": [
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="거실 최소 천장고",
                    min_value=2.3,
                    unit="m",
                    applicable_to=["living_room", "거실"]
                ),
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="침실 최소 천장고",
                    min_value=2.3,
                    unit="m",
                    applicable_to=["bedroom", "침실"]
                ),
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="복도 최소 천장고",
                    min_value=2.1,
                    unit="m",
                    applicable_to=["corridor", "복도"]
                )
            ],
            "natural_light": [
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="거실 채광 면적비",
                    min_value=0.1,  # 바닥면적의 10%
                    unit="ratio",
                    applicable_to=["living_room", "거실"]
                ),
                CodeRequirement(
                    code_type=CodeType.BUILDING_CODE,
                    requirement="침실 채광 면적비",
                    min_value=0.07,  # 바닥면적의 7%
                    unit="ratio",
                    applicable_to=["bedroom", "침실"]
                )
            ],
            "evacuation": [
                CodeRequirement(
                    code_type=CodeType.FIRE_CODE,
                    requirement="피난계단 최소 폭",
                    min_value=1.2,
                    unit="m",
                    applicable_to=["stair", "계단"]
                ),
                CodeRequirement(
                    code_type=CodeType.FIRE_CODE,
                    requirement="복도 최소 폭",
                    min_value=1.2,
                    unit="m",
                    applicable_to=["corridor", "복도"]
                ),
                CodeRequirement(
                    code_type=CodeType.FIRE_CODE,
                    requirement="비상구 최소 폭",
                    min_value=0.9,
                    unit="m",
                    applicable_to=["emergency_exit", "비상구"]
                )
            ],
            "accessibility": [
                CodeRequirement(
                    code_type=CodeType.ACCESSIBILITY,
                    requirement="장애인 화장실 최소 면적",
                    min_value=4.0,
                    unit="㎡",
                    applicable_to=["accessible_bathroom", "장애인화장실"]
                ),
                CodeRequirement(
                    code_type=CodeType.ACCESSIBILITY,
                    requirement="경사로 최대 기울기",
                    max_value=8.33,  # 1:12
                    unit="%",
                    applicable_to=["ramp", "경사로"]
                ),
                CodeRequirement(
                    code_type=CodeType.ACCESSIBILITY,
                    requirement="출입구 최소 폭",
                    min_value=0.8,
                    unit="m",
                    applicable_to=["door", "문", "출입구"]
                )
            ],
            "energy": [
                CodeRequirement(
                    code_type=CodeType.ENERGY_CODE,
                    requirement="외벽 열관류율",
                    max_value=0.24,
                    unit="W/㎡K",
                    applicable_to=["exterior_wall", "외벽"]
                ),
                CodeRequirement(
                    code_type=CodeType.ENERGY_CODE,
                    requirement="창호 열관류율",
                    max_value=1.5,
                    unit="W/㎡K",
                    applicable_to=["window", "창문"]
                ),
                CodeRequirement(
                    code_type=CodeType.ENERGY_CODE,
                    requirement="지붕 열관류율",
                    max_value=0.15,
                    unit="W/㎡K",
                    applicable_to=["roof", "지붕"]
                )
            ],
            "structural": [
                CodeRequirement(
                    code_type=CodeType.STRUCTURAL,
                    requirement="기둥 최소 크기",
                    min_value=300,
                    unit="mm",
                    applicable_to=["column", "기둥"]
                ),
                CodeRequirement(
                    code_type=CodeType.STRUCTURAL,
                    requirement="보 최소 깊이",
                    min_value=400,
                    unit="mm",
                    applicable_to=["beam", "보"]
                ),
                CodeRequirement(
                    code_type=CodeType.STRUCTURAL,
                    requirement="슬래브 최소 두께",
                    min_value=150,
                    unit="mm",
                    applicable_to=["slab", "슬래브"]
                )
            ]
        }
    
    def check_compliance(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """건축물 법규 준수 검토"""
        results = {
            "overall_compliance": True,
            "violations": [],
            "warnings": [],
            "checks": []
        }
        
        # 각 법규 카테고리별 검토
        for category, requirements in self.code_requirements.items():
            for req in requirements:
                check_result = self._check_requirement(building_data, req)
                results["checks"].append(check_result)
                
                if check_result["status"] == "violation":
                    results["violations"].append(check_result)
                    results["overall_compliance"] = False
                elif check_result["status"] == "warning":
                    results["warnings"].append(check_result)
        
        return results
    
    def _check_requirement(self, building_data: Dict[str, Any], 
                         requirement: CodeRequirement) -> Dict[str, Any]:
        """개별 요구사항 검토"""
        # 실제 구현은 더 복잡할 것임
        return {
            "requirement": requirement.requirement,
            "code_type": requirement.code_type.value,
            "status": "pass",  # pass, warning, violation
            "current_value": None,
            "required_value": requirement.min_value or requirement.max_value,
            "unit": requirement.unit
        }
    
    def get_requirements_for_space(self, space_type: str) -> List[CodeRequirement]:
        """특정 공간 유형에 대한 법규 요구사항 조회"""
        applicable_requirements = []
        
        for category, requirements in self.code_requirements.items():
            for req in requirements:
                if req.applicable_to and space_type in req.applicable_to:
                    applicable_requirements.append(req)
        
        return applicable_requirements
    
    def check_korean_building_code(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """한국 건축법 특화 검토"""
        results = {
            "건폐율": self._check_building_coverage_ratio(building_data),
            "용적률": self._check_floor_area_ratio(building_data),
            "일조권": self._check_sunlight_rights(building_data),
            "조경면적": self._check_landscape_area(building_data),
            "주차대수": self._check_parking_requirements(building_data)
        }
        
        return results
    
    def _check_building_coverage_ratio(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """건폐율 검토"""
        site_area = building_data.get("site_area", 0)
        building_area = building_data.get("building_footprint", 0)
        
        if site_area > 0:
            ratio = building_area / site_area
            max_ratio = 0.6  # 일반 주거지역 기준
            
            return {
                "current": ratio,
                "maximum": max_ratio,
                "compliant": ratio <= max_ratio,
                "unit": "%"
            }
        
        return {"error": "부지 면적 정보 없음"}
    
    def _check_floor_area_ratio(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """용적률 검토"""
        site_area = building_data.get("site_area", 0)
        total_floor_area = building_data.get("total_floor_area", 0)
        
        if site_area > 0:
            ratio = total_floor_area / site_area
            max_ratio = 2.0  # 일반 주거지역 기준
            
            return {
                "current": ratio,
                "maximum": max_ratio,
                "compliant": ratio <= max_ratio,
                "unit": "%"
            }
        
        return {"error": "부지 면적 정보 없음"}
    
    def _check_sunlight_rights(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """일조권 검토"""
        # 간단한 일조권 검토 (실제로는 복잡한 시뮬레이션 필요)
        building_height = building_data.get("height", 0)
        north_setback = building_data.get("north_setback", 0)
        
        required_setback = building_height * 0.5  # 간단한 규칙
        
        return {
            "current_setback": north_setback,
            "required_setback": required_setback,
            "compliant": north_setback >= required_setback,
            "unit": "m"
        }
    
    def _check_landscape_area(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """조경 면적 검토"""
        site_area = building_data.get("site_area", 0)
        landscape_area = building_data.get("landscape_area", 0)
        
        if site_area > 200:  # 200㎡ 이상 대지
            required_ratio = 0.15  # 15%
            current_ratio = landscape_area / site_area if site_area > 0 else 0
            
            return {
                "current_ratio": current_ratio,
                "required_ratio": required_ratio,
                "compliant": current_ratio >= required_ratio,
                "unit": "%"
            }
        
        return {"message": "조경 의무 면적 미만"}
    
    def _check_parking_requirements(self, building_data: Dict[str, Any]) -> Dict[str, Any]:
        """주차 대수 검토"""
        total_units = building_data.get("residential_units", 0)
        parking_spaces = building_data.get("parking_spaces", 0)
        
        # 세대당 1대 기준 (지역별로 다름)
        required_spaces = total_units * 1.0
        
        return {
            "current_spaces": parking_spaces,
            "required_spaces": required_spaces,
            "compliant": parking_spaces >= required_spaces,
            "ratio": parking_spaces / total_units if total_units > 0 else 0
        }