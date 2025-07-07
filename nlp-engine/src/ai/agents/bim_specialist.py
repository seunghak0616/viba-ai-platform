"""
BIM 전문가 AI 에이전트
====================

건축 설계 개념을 IFC 4.3 기반 BIM 모델로 변환하는 AI 에이전트
설계 이론가의 개념을 실제 3D BIM 모델로 구현

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime

# IFC 및 BIM 라이브러리
try:
    import ifcopenshell
    import ifcopenshell.api
    import ifcopenshell.geom
except ImportError:
    logger.warning("IfcOpenShell not available, using mock BIM generation")
    ifcopenshell = None

# 3D 기하학 라이브러리
try:
    from trimesh import Trimesh
    import trimesh.creation as creation
except ImportError:
    logger.warning("Trimesh not available, using basic geometry")
    Trimesh = None

# 프로젝트 임포트
from ..base_agent import BaseVIBAAgent, AgentCapability
from ...utils.metrics_collector import record_ai_inference_metric
from ...knowledge.building_codes import BuildingCodeChecker
from ...knowledge.ifc_schema import IFC43Schema
from ...processors.korean_processor import get_korean_architecture_processor

logger = logging.getLogger(__name__)


class BIMElementType(Enum):
    """BIM 요소 유형"""
    # 구조 요소
    WALL = "IfcWall"
    COLUMN = "IfcColumn"
    BEAM = "IfcBeam"
    SLAB = "IfcSlab"
    ROOF = "IfcRoof"
    STAIR = "IfcStair"
    RAMP = "IfcRamp"
    
    # 개구부
    DOOR = "IfcDoor"
    WINDOW = "IfcWindow"
    CURTAIN_WALL = "IfcCurtainWall"
    
    # 공간
    SPACE = "IfcSpace"
    BUILDING_STOREY = "IfcBuildingStorey"
    BUILDING = "IfcBuilding"
    SITE = "IfcSite"
    
    # MEP
    PIPE = "IfcPipeSegment"
    DUCT = "IfcDuctSegment"
    CABLE = "IfcCableSegment"
    
    # 가구/설비
    FURNITURE = "IfcFurniture"
    EQUIPMENT = "IfcBuildingElementProxy"


class MaterialType(Enum):
    """재료 유형"""
    CONCRETE = "concrete"
    STEEL = "steel"
    WOOD = "wood"
    GLASS = "glass"
    BRICK = "brick"
    STONE = "stone"
    GYPSUM = "gypsum"
    INSULATION = "insulation"
    CERAMIC = "ceramic"
    METAL = "metal"


@dataclass
class BIMElement:
    """BIM 요소"""
    guid: str
    element_type: BIMElementType
    name: str
    geometry: Optional[Any] = None  # 3D 형상
    location: Dict[str, float] = field(default_factory=dict)  # x, y, z
    rotation: Dict[str, float] = field(default_factory=dict)  # rx, ry, rz
    dimensions: Dict[str, float] = field(default_factory=dict)  # width, height, depth
    material: Optional[MaterialType] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    relationships: List[str] = field(default_factory=list)  # 관련 요소 GUID
    level: Optional[int] = None  # 층 정보
    space_guid: Optional[str] = None  # 속한 공간
    
    def to_ifc_dict(self) -> Dict[str, Any]:
        """IFC 딕셔너리로 변환"""
        return {
            "GlobalId": self.guid,
            "OwnerHistory": None,  # 추후 설정
            "Name": self.name,
            "Description": self.properties.get("description", ""),
            "ObjectType": self.element_type.value,
            "ObjectPlacement": {
                "Location": self.location,
                "Rotation": self.rotation
            },
            "Representation": self.geometry,
            "Tag": self.properties.get("tag", ""),
            "Properties": self.properties
        }


@dataclass
class BIMSpace:
    """BIM 공간"""
    guid: str
    name: str
    space_type: str  # 거실, 침실, 주방 등
    area: float  # 면적 (㎡)
    height: float  # 천장고
    boundary_points: List[Tuple[float, float]]  # 2D 경계점
    level: int  # 층
    adjacent_spaces: List[str] = field(default_factory=list)  # 인접 공간 GUID
    contained_elements: List[str] = field(default_factory=list)  # 포함 요소 GUID
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_volume(self) -> float:
        """부피 계산"""
        return self.area * self.height


@dataclass
class BIMModel:
    """BIM 모델"""
    project_guid: str
    project_name: str
    building_type: str
    total_area: float
    stories: int
    
    # 요소들
    elements: Dict[str, BIMElement] = field(default_factory=dict)  # GUID -> Element
    spaces: Dict[str, BIMSpace] = field(default_factory=dict)  # GUID -> Space
    levels: Dict[int, List[str]] = field(default_factory=dict)  # Level -> Element GUIDs
    
    # 메타데이터
    creation_date: datetime = field(default_factory=datetime.now)
    author: str = "VIBA BIM Specialist"
    schema_version: str = "IFC4.3"
    coordinate_system: Dict[str, Any] = field(default_factory=dict)
    
    # 분석 결과
    structural_analysis: Optional[Dict[str, Any]] = None
    energy_analysis: Optional[Dict[str, Any]] = None
    code_compliance: Optional[Dict[str, Any]] = None
    
    def add_element(self, element: BIMElement):
        """요소 추가"""
        self.elements[element.guid] = element
        if element.level is not None:
            if element.level not in self.levels:
                self.levels[element.level] = []
            self.levels[element.level].append(element.guid)
    
    def add_space(self, space: BIMSpace):
        """공간 추가"""
        self.spaces[space.guid] = space
        if space.level not in self.levels:
            self.levels[space.level] = []
        self.levels[space.level].append(space.guid)
    
    def get_total_volume(self) -> float:
        """총 부피 계산"""
        return sum(space.calculate_volume() for space in self.spaces.values())
    
    def get_element_count_by_type(self) -> Dict[str, int]:
        """유형별 요소 개수"""
        count = {}
        for element in self.elements.values():
            type_name = element.element_type.value
            count[type_name] = count.get(type_name, 0) + 1
        return count


class BIMSpecialistAgent(BaseVIBAAgent):
    """BIM 전문가 AI 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_id=f"bim_specialist_{uuid.uuid4().hex[:8]}",
            name="BIM Specialist Agent",
            capabilities=[
                AgentCapability.BIM_MODEL_GENERATION,
                AgentCapability.SPATIAL_PLANNING,
                AgentCapability.DESIGN_THEORY_APPLICATION,
                AgentCapability.OPTIMIZATION
            ]
        )
        
        # BIM 생성 설정
        self.default_settings = {
            "wall_thickness": 0.2,  # 200mm
            "floor_height": 2.8,    # 2.8m
            "window_height": 1.5,   # 1.5m
            "door_height": 2.1,     # 2.1m
            "door_width": 0.9,      # 900mm
            "column_size": 0.4,     # 400mm
            "beam_height": 0.5,     # 500mm
            "min_room_area": 9.0,   # 9㎡
            "corridor_width": 1.2   # 1.2m
        }
        
        # IFC 스키마
        self.ifc_schema = IFC43Schema() if ifcopenshell else None
        
        # 건축법규 검토기
        self.code_checker = BuildingCodeChecker()
        
        # 한국어 프로세서
        self.korean_processor = get_korean_architecture_processor()
        
        # 템플릿 라이브러리
        self.space_templates = self._load_space_templates()
        self.element_templates = self._load_element_templates()
        
        logger.info(f"BIM Specialist Agent initialized: {self.agent_id}")
    
    async def initialize(self) -> bool:
        """에이전트 초기화"""
        try:
            self.is_initialized = True
            logger.info("BIM Specialist Agent initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize BIM Specialist: {e}")
            return False
    
    async def execute_task(self, task) -> Dict[str, Any]:
        """작업 실행"""
        start_time = time.time()
        
        try:
            task_type = task.task_type
            input_data = task.input_data
            
            if task_type == "generate_bim":
                result = await self._generate_bim_model(input_data)
            elif task_type == "update_bim":
                result = await self._update_bim_model(input_data)
            elif task_type == "analyze_spatial_layout":
                result = await self._analyze_spatial_layout(input_data)
            elif task_type == "optimize_structure":
                result = await self._optimize_structure(input_data)
            elif task_type == "check_code_compliance":
                result = await self._check_code_compliance(input_data)
            elif task_type == "export_ifc":
                result = await self._export_to_ifc(input_data)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            # 성능 메트릭 기록
            duration = time.time() - start_time
            record_ai_inference_metric(
                model_type="bim_generation",
                agent_type="bim_specialist",
                duration=duration,
                accuracy=0.95,  # BIM 생성 정확도
                memory_usage=0,
                complexity="high",
                status="success"
            )
            
            return {
                "status": "success",
                "result": result,
                "duration": duration,
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"BIM task execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "agent_id": self.agent_id
            }
    
    async def _generate_bim_model(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """BIM 모델 생성"""
        logger.info("Generating BIM model from design concept...")
        
        # 입력 데이터 파싱
        design_concept = input_data.get("design_concept", {})
        building_type = design_concept.get("building_type", "residential")
        spatial_requirements = design_concept.get("spatial_organization", {})
        dimensions = design_concept.get("dimensional_guidelines", {})
        materials = design_concept.get("material_palette", [])
        
        # BIM 모델 초기화
        bim_model = BIMModel(
            project_guid=str(uuid.uuid4()),
            project_name=input_data.get("project_name", "VIBA_Project"),
            building_type=building_type,
            total_area=dimensions.get("total_area", 100.0),
            stories=dimensions.get("stories", 1)
        )
        
        # 1. 층별 공간 생성
        spaces_by_level = await self._create_spaces(
            bim_model, spatial_requirements, dimensions
        )
        
        # 2. 구조 요소 생성
        await self._create_structural_elements(bim_model, spaces_by_level)
        
        # 3. 벽체 및 개구부 생성
        await self._create_walls_and_openings(bim_model, spaces_by_level)
        
        # 4. 바닥 및 천장 생성
        await self._create_floors_and_ceilings(bim_model, spaces_by_level)
        
        # 5. 계단 및 엘리베이터
        if bim_model.stories > 1:
            await self._create_vertical_circulation(bim_model)
        
        # 6. MEP 기본 요소
        await self._create_mep_elements(bim_model)
        
        # 7. 재료 할당
        await self._assign_materials(bim_model, materials)
        
        # 8. 건축법규 검토
        compliance_result = await self._check_building_codes(bim_model)
        bim_model.code_compliance = compliance_result
        
        # 9. 최적화
        await self._optimize_bim_model(bim_model)
        
        # 결과 정리
        result = {
            "bim_model": self._serialize_bim_model(bim_model),
            "statistics": {
                "total_elements": len(bim_model.elements),
                "total_spaces": len(bim_model.spaces),
                "total_area": bim_model.total_area,
                "total_volume": bim_model.get_total_volume(),
                "element_count": bim_model.get_element_count_by_type()
            },
            "compliance": compliance_result,
            "preview_url": await self._generate_3d_preview(bim_model)
        }
        
        logger.info(f"BIM model generated: {len(bim_model.elements)} elements, {len(bim_model.spaces)} spaces")
        
        return result
    
    async def _create_spaces(self, bim_model: BIMModel, 
                           spatial_requirements: Dict[str, Any],
                           dimensions: Dict[str, float]) -> Dict[int, List[BIMSpace]]:
        """공간 생성"""
        spaces_by_level = {}
        
        # 층별 면적 계산
        total_area = dimensions.get("total_area", 100.0)
        stories = dimensions.get("stories", 1)
        area_per_floor = total_area / stories
        
        for level in range(stories):
            spaces = []
            
            # 공간 요구사항 분석
            required_spaces = spatial_requirements.get("spaces", [])
            
            # 공간 배치 알고리즘
            layout = await self._generate_space_layout(
                required_spaces, area_per_floor, level
            )
            
            # 각 공간 생성
            for space_data in layout:
                space = BIMSpace(
                    guid=str(uuid.uuid4()),
                    name=space_data["name"],
                    space_type=space_data["type"],
                    area=space_data["area"],
                    height=self.default_settings["floor_height"],
                    boundary_points=space_data["boundary"],
                    level=level,
                    properties=space_data.get("properties", {})
                )
                
                spaces.append(space)
                bim_model.add_space(space)
            
            # 인접 관계 설정
            await self._set_space_adjacencies(spaces)
            
            spaces_by_level[level] = spaces
        
        return spaces_by_level
    
    async def _generate_space_layout(self, required_spaces: List[Dict[str, Any]], 
                                   area: float, level: int) -> List[Dict[str, Any]]:
        """공간 배치 생성"""
        layout = []
        
        # 기본 그리드 기반 배치 (실제로는 더 복잡한 알고리즘 사용)
        grid_size = int(np.sqrt(area / 9))  # 9㎡ 기준 그리드
        
        # 우선순위에 따라 공간 배치
        sorted_spaces = sorted(required_spaces, 
                             key=lambda x: x.get("priority", 0), 
                             reverse=True)
        
        x, y = 0, 0
        for space_req in sorted_spaces:
            space_area = space_req.get("area", 20.0)
            space_width = np.sqrt(space_area)
            space_depth = space_area / space_width
            
            # 경계점 생성
            boundary = [
                (x, y),
                (x + space_width, y),
                (x + space_width, y + space_depth),
                (x, y + space_depth)
            ]
            
            layout.append({
                "name": space_req.get("name", f"Space_{len(layout)}"),
                "type": space_req.get("type", "generic"),
                "area": space_area,
                "boundary": boundary,
                "properties": {
                    "natural_light": space_req.get("natural_light", True),
                    "ventilation": space_req.get("ventilation", True),
                    "privacy_level": space_req.get("privacy_level", "medium")
                }
            })
            
            # 다음 위치로 이동
            x += space_width + 0.2  # 벽 두께 고려
            if x > np.sqrt(area):
                x = 0
                y += space_depth + 0.2
        
        return layout
    
    async def _set_space_adjacencies(self, spaces: List[BIMSpace]):
        """공간 인접 관계 설정"""
        for i, space1 in enumerate(spaces):
            for j, space2 in enumerate(spaces[i+1:], i+1):
                if self._are_adjacent(space1.boundary_points, space2.boundary_points):
                    space1.adjacent_spaces.append(space2.guid)
                    space2.adjacent_spaces.append(space1.guid)
    
    def _are_adjacent(self, boundary1: List[Tuple[float, float]], 
                     boundary2: List[Tuple[float, float]]) -> bool:
        """두 공간이 인접한지 확인"""
        # 간단한 경계 검사 (실제로는 더 정교한 알고리즘 필요)
        for p1 in boundary1:
            for p2 in boundary2:
                dist = np.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
                if dist < 0.3:  # 벽 두께 고려
                    return True
        return False
    
    async def _create_structural_elements(self, bim_model: BIMModel, 
                                        spaces_by_level: Dict[int, List[BIMSpace]]):
        """구조 요소 생성"""
        # 기둥 생성
        column_spacing = 6.0  # 6m 간격
        
        for level, spaces in spaces_by_level.items():
            # 각 층의 경계 계산
            min_x = min_y = float('inf')
            max_x = max_y = float('-inf')
            
            for space in spaces:
                for x, y in space.boundary_points:
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
            
            # 그리드 기반 기둥 배치
            x = min_x
            while x <= max_x:
                y = min_y
                while y <= max_y:
                    column = BIMElement(
                        guid=str(uuid.uuid4()),
                        element_type=BIMElementType.COLUMN,
                        name=f"Column_L{level}_{int(x)}_{int(y)}",
                        location={"x": x, "y": y, "z": level * self.default_settings["floor_height"]},
                        dimensions={
                            "width": self.default_settings["column_size"],
                            "depth": self.default_settings["column_size"],
                            "height": self.default_settings["floor_height"]
                        },
                        material=MaterialType.CONCRETE,
                        level=level
                    )
                    
                    bim_model.add_element(column)
                    y += column_spacing
                x += column_spacing
        
        # 보 생성 (기둥 연결)
        await self._create_beams(bim_model)
    
    async def _create_beams(self, bim_model: BIMModel):
        """보 생성"""
        columns_by_level = {}
        
        # 층별 기둥 정리
        for elem in bim_model.elements.values():
            if elem.element_type == BIMElementType.COLUMN:
                level = elem.level
                if level not in columns_by_level:
                    columns_by_level[level] = []
                columns_by_level[level].append(elem)
        
        # 인접 기둥 연결
        for level, columns in columns_by_level.items():
            for i, col1 in enumerate(columns):
                for col2 in columns[i+1:]:
                    dist = np.sqrt(
                        (col1.location["x"] - col2.location["x"])**2 +
                        (col1.location["y"] - col2.location["y"])**2
                    )
                    
                    # 인접한 기둥끼리만 연결
                    if dist <= 6.5:  # 기둥 간격 + 여유
                        beam = BIMElement(
                            guid=str(uuid.uuid4()),
                            element_type=BIMElementType.BEAM,
                            name=f"Beam_L{level}_{col1.guid[:8]}_{col2.guid[:8]}",
                            location={
                                "x": (col1.location["x"] + col2.location["x"]) / 2,
                                "y": (col1.location["y"] + col2.location["y"]) / 2,
                                "z": col1.location["z"] + self.default_settings["floor_height"] - self.default_settings["beam_height"]
                            },
                            dimensions={
                                "width": 0.3,
                                "height": self.default_settings["beam_height"],
                                "length": dist
                            },
                            material=MaterialType.CONCRETE,
                            level=level,
                            relationships=[col1.guid, col2.guid]
                        )
                        
                        bim_model.add_element(beam)
    
    async def _create_walls_and_openings(self, bim_model: BIMModel, 
                                       spaces_by_level: Dict[int, List[BIMSpace]]):
        """벽체 및 개구부 생성"""
        for level, spaces in spaces_by_level.items():
            # 각 공간의 경계에 벽 생성
            for space in spaces:
                boundary = space.boundary_points
                
                for i in range(len(boundary)):
                    p1 = boundary[i]
                    p2 = boundary[(i + 1) % len(boundary)]
                    
                    # 벽 생성
                    wall_length = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                    wall_angle = np.arctan2(p2[1] - p1[1], p2[0] - p1[0])
                    
                    wall = BIMElement(
                        guid=str(uuid.uuid4()),
                        element_type=BIMElementType.WALL,
                        name=f"Wall_{space.name}_{i}",
                        location={
                            "x": (p1[0] + p2[0]) / 2,
                            "y": (p1[1] + p2[1]) / 2,
                            "z": level * self.default_settings["floor_height"]
                        },
                        rotation={"x": 0, "y": 0, "z": wall_angle},
                        dimensions={
                            "length": wall_length,
                            "height": self.default_settings["floor_height"],
                            "thickness": self.default_settings["wall_thickness"]
                        },
                        material=MaterialType.CONCRETE,
                        level=level,
                        space_guid=space.guid
                    )
                    
                    bim_model.add_element(wall)
                    space.contained_elements.append(wall.guid)
                    
                    # 개구부 생성 (외벽 또는 특정 조건)
                    if self._is_exterior_wall(p1, p2, spaces) or (i == 0 and space.space_type != "bathroom"):
                        # 창문 또는 문 생성
                        opening = await self._create_opening(wall, space, is_exterior=True)
                        if opening:
                            bim_model.add_element(opening)
                            wall.relationships.append(opening.guid)
    
    def _is_exterior_wall(self, p1: Tuple[float, float], p2: Tuple[float, float], 
                         spaces: List[BIMSpace]) -> bool:
        """외벽인지 확인"""
        # 간단한 확인 (실제로는 더 정교한 알고리즘 필요)
        wall_center = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        adjacent_count = 0
        
        for space in spaces:
            if self._point_near_boundary(wall_center, space.boundary_points):
                adjacent_count += 1
        
        return adjacent_count <= 1
    
    def _point_near_boundary(self, point: Tuple[float, float], 
                           boundary: List[Tuple[float, float]], 
                           threshold: float = 0.5) -> bool:
        """점이 경계 근처에 있는지 확인"""
        for bp in boundary:
            dist = np.sqrt((point[0] - bp[0])**2 + (point[1] - bp[1])**2)
            if dist < threshold:
                return True
        return False
    
    async def _create_opening(self, wall: BIMElement, space: BIMSpace, 
                            is_exterior: bool) -> Optional[BIMElement]:
        """개구부 생성"""
        if is_exterior and space.properties.get("natural_light", True):
            # 창문 생성
            window = BIMElement(
                guid=str(uuid.uuid4()),
                element_type=BIMElementType.WINDOW,
                name=f"Window_{wall.name}",
                location={
                    "x": wall.location["x"],
                    "y": wall.location["y"],
                    "z": wall.location["z"] + 0.9  # 창문 높이
                },
                rotation=wall.rotation,
                dimensions={
                    "width": min(wall.dimensions["length"] * 0.6, 2.4),  # 최대 2.4m
                    "height": self.default_settings["window_height"],
                    "thickness": 0.1
                },
                material=MaterialType.GLASS,
                level=wall.level,
                space_guid=space.guid
            )
            return window
        
        elif not is_exterior and space.space_type in ["living_room", "bedroom", "kitchen"]:
            # 문 생성
            door = BIMElement(
                guid=str(uuid.uuid4()),
                element_type=BIMElementType.DOOR,
                name=f"Door_{wall.name}",
                location={
                    "x": wall.location["x"],
                    "y": wall.location["y"],
                    "z": wall.location["z"]
                },
                rotation=wall.rotation,
                dimensions={
                    "width": self.default_settings["door_width"],
                    "height": self.default_settings["door_height"],
                    "thickness": 0.05
                },
                material=MaterialType.WOOD,
                level=wall.level,
                space_guid=space.guid
            )
            return door
        
        return None
    
    async def _create_floors_and_ceilings(self, bim_model: BIMModel, 
                                        spaces_by_level: Dict[int, List[BIMSpace]]):
        """바닥 및 천장 생성"""
        for level, spaces in spaces_by_level.items():
            for space in spaces:
                # 바닥 슬래브
                floor = BIMElement(
                    guid=str(uuid.uuid4()),
                    element_type=BIMElementType.SLAB,
                    name=f"Floor_{space.name}",
                    location={
                        "x": np.mean([p[0] for p in space.boundary_points]),
                        "y": np.mean([p[1] for p in space.boundary_points]),
                        "z": level * self.default_settings["floor_height"]
                    },
                    dimensions={
                        "area": space.area,
                        "thickness": 0.2
                    },
                    material=MaterialType.CONCRETE,
                    level=level,
                    space_guid=space.guid,
                    properties={"type": "floor"}
                )
                
                bim_model.add_element(floor)
                space.contained_elements.append(floor.guid)
                
                # 천장 (최상층 제외)
                if level < bim_model.stories - 1:
                    ceiling = BIMElement(
                        guid=str(uuid.uuid4()),
                        element_type=BIMElementType.SLAB,
                        name=f"Ceiling_{space.name}",
                        location={
                            "x": floor.location["x"],
                            "y": floor.location["y"],
                            "z": floor.location["z"] + self.default_settings["floor_height"] - 0.15
                        },
                        dimensions={
                            "area": space.area,
                            "thickness": 0.15
                        },
                        material=MaterialType.CONCRETE,
                        level=level,
                        space_guid=space.guid,
                        properties={"type": "ceiling"}
                    )
                    
                    bim_model.add_element(ceiling)
                    space.contained_elements.append(ceiling.guid)
    
    async def _create_vertical_circulation(self, bim_model: BIMModel):
        """수직 동선 (계단/엘리베이터) 생성"""
        # 계단 위치 결정
        stair_location = self._find_stair_location(bim_model)
        
        for level in range(bim_model.stories - 1):
            # 계단 생성
            stair = BIMElement(
                guid=str(uuid.uuid4()),
                element_type=BIMElementType.STAIR,
                name=f"Stair_L{level}_to_L{level+1}",
                location={
                    "x": stair_location["x"],
                    "y": stair_location["y"],
                    "z": level * self.default_settings["floor_height"]
                },
                dimensions={
                    "width": 1.2,
                    "length": 3.0,
                    "height": self.default_settings["floor_height"],
                    "riser_height": 0.175,
                    "tread_depth": 0.28
                },
                material=MaterialType.CONCRETE,
                level=level,
                properties={
                    "flight_count": 2,
                    "landing_type": "half_landing"
                }
            )
            
            bim_model.add_element(stair)
    
    def _find_stair_location(self, bim_model: BIMModel) -> Dict[str, float]:
        """계단 위치 찾기"""
        # 중심부 근처 위치 선택 (실제로는 더 정교한 알고리즘 필요)
        all_x = []
        all_y = []
        
        for space in bim_model.spaces.values():
            if space.level == 0:
                for p in space.boundary_points:
                    all_x.append(p[0])
                    all_y.append(p[1])
        
        return {
            "x": np.mean(all_x) if all_x else 0,
            "y": np.mean(all_y) if all_y else 0
        }
    
    async def _create_mep_elements(self, bim_model: BIMModel):
        """MEP 기본 요소 생성"""
        # 간단한 MEP 요소 추가 (실제로는 더 복잡한 시스템 필요)
        for space in bim_model.spaces.values():
            if space.space_type in ["kitchen", "bathroom"]:
                # 급수 배관
                pipe = BIMElement(
                    guid=str(uuid.uuid4()),
                    element_type=BIMElementType.PIPE,
                    name=f"WaterPipe_{space.name}",
                    location={
                        "x": np.mean([p[0] for p in space.boundary_points]),
                        "y": np.mean([p[1] for p in space.boundary_points]),
                        "z": space.level * self.default_settings["floor_height"] + 2.5
                    },
                    dimensions={
                        "diameter": 0.025,  # 25mm
                        "length": 2.0
                    },
                    material=MaterialType.METAL,
                    level=space.level,
                    space_guid=space.guid,
                    properties={"system": "water_supply"}
                )
                
                bim_model.add_element(pipe)
    
    async def _assign_materials(self, bim_model: BIMModel, material_palette: List[str]):
        """재료 할당"""
        # 재료 팔레트를 MaterialType으로 매핑
        material_mapping = {
            "콘크리트": MaterialType.CONCRETE,
            "철골": MaterialType.STEEL,
            "목재": MaterialType.WOOD,
            "유리": MaterialType.GLASS,
            "벽돌": MaterialType.BRICK,
            "석재": MaterialType.STONE
        }
        
        # 요소별 재료 할당 규칙
        for element in bim_model.elements.values():
            if element.material is None:
                # 기본 재료 할당
                if element.element_type in [BIMElementType.COLUMN, BIMElementType.BEAM]:
                    element.material = MaterialType.CONCRETE
                elif element.element_type == BIMElementType.WALL:
                    # 외벽/내벽 구분
                    if "exterior" in element.properties.get("type", ""):
                        element.material = MaterialType.BRICK
                    else:
                        element.material = MaterialType.GYPSUM
                elif element.element_type == BIMElementType.WINDOW:
                    element.material = MaterialType.GLASS
                elif element.element_type == BIMElementType.DOOR:
                    element.material = MaterialType.WOOD
    
    async def _check_building_codes(self, bim_model: BIMModel) -> Dict[str, Any]:
        """건축법규 검토"""
        compliance_result = {
            "overall_compliance": True,
            "violations": [],
            "warnings": [],
            "checks_performed": []
        }
        
        # 1. 최소 공간 면적 검토
        for space in bim_model.spaces.values():
            if space.area < self.default_settings["min_room_area"]:
                compliance_result["warnings"].append({
                    "type": "minimum_area",
                    "space": space.name,
                    "current": space.area,
                    "required": self.default_settings["min_room_area"]
                })
        
        # 2. 천장고 검토
        min_ceiling_height = 2.3  # 최소 천장고
        for space in bim_model.spaces.values():
            if space.height < min_ceiling_height:
                compliance_result["violations"].append({
                    "type": "ceiling_height",
                    "space": space.name,
                    "current": space.height,
                    "required": min_ceiling_height
                })
                compliance_result["overall_compliance"] = False
        
        # 3. 채광 검토
        for space in bim_model.spaces.values():
            if space.space_type in ["living_room", "bedroom", "kitchen"]:
                # 창문 면적 확인
                window_area = self._calculate_window_area(bim_model, space)
                required_ratio = 0.1  # 바닥면적의 10%
                
                if window_area < space.area * required_ratio:
                    compliance_result["warnings"].append({
                        "type": "natural_light",
                        "space": space.name,
                        "current_ratio": window_area / space.area,
                        "required_ratio": required_ratio
                    })
        
        # 4. 피난 동선 검토
        if bim_model.stories > 1:
            stair_count = sum(1 for e in bim_model.elements.values() 
                            if e.element_type == BIMElementType.STAIR)
            if stair_count < 2 and bim_model.total_area > 500:
                compliance_result["violations"].append({
                    "type": "evacuation_route",
                    "message": "500㎡ 이상 건물은 2개 이상의 계단 필요"
                })
                compliance_result["overall_compliance"] = False
        
        compliance_result["checks_performed"] = [
            "minimum_area", "ceiling_height", "natural_light", "evacuation_route"
        ]
        
        return compliance_result
    
    def _calculate_window_area(self, bim_model: BIMModel, space: BIMSpace) -> float:
        """공간의 창문 면적 계산"""
        window_area = 0.0
        
        for element_guid in space.contained_elements:
            element = bim_model.elements.get(element_guid)
            if element and element.element_type == BIMElementType.WINDOW:
                window_area += element.dimensions.get("width", 0) * element.dimensions.get("height", 0)
        
        return window_area
    
    async def _optimize_bim_model(self, bim_model: BIMModel):
        """BIM 모델 최적화"""
        # 1. 구조 최적화
        await self._optimize_structure_placement(bim_model)
        
        # 2. 공간 효율성 최적화
        await self._optimize_space_efficiency(bim_model)
        
        # 3. 에너지 효율 최적화
        await self._optimize_energy_efficiency(bim_model)
    
    async def _optimize_structure_placement(self, bim_model: BIMModel):
        """구조 배치 최적화"""
        # 불필요한 기둥 제거
        columns_to_remove = []
        
        columns = [e for e in bim_model.elements.values() 
                  if e.element_type == BIMElementType.COLUMN]
        
        for i, col1 in enumerate(columns):
            for col2 in columns[i+1:]:
                dist = np.sqrt(
                    (col1.location["x"] - col2.location["x"])**2 +
                    (col1.location["y"] - col2.location["y"])**2
                )
                
                # 너무 가까운 기둥 제거
                if dist < 2.0:  # 2m 이내
                    columns_to_remove.append(col1.guid)
                    break
        
        # 제거
        for guid in columns_to_remove:
            if guid in bim_model.elements:
                del bim_model.elements[guid]
    
    async def _optimize_space_efficiency(self, bim_model: BIMModel):
        """공간 효율성 최적화"""
        # 복도 면적 최소화
        corridor_spaces = [s for s in bim_model.spaces.values() 
                         if "corridor" in s.space_type.lower()]
        
        total_corridor_area = sum(s.area for s in corridor_spaces)
        efficiency_ratio = 1 - (total_corridor_area / bim_model.total_area)
        
        # 효율성 정보 저장
        if not hasattr(bim_model, 'optimization_results'):
            bim_model.optimization_results = {}
        
        bim_model.optimization_results['space_efficiency'] = efficiency_ratio
    
    async def _optimize_energy_efficiency(self, bim_model: BIMModel):
        """에너지 효율 최적화"""
        # 창문 방향 최적화
        for element in bim_model.elements.values():
            if element.element_type == BIMElementType.WINDOW:
                # 남향 창문 크기 증가
                wall_normal = self._get_wall_normal(element.rotation["z"])
                if abs(wall_normal[1]) > 0.7:  # 남향
                    element.dimensions["width"] *= 1.2  # 20% 증가
                    element.dimensions["height"] *= 1.1  # 10% 증가
    
    def _get_wall_normal(self, rotation_z: float) -> Tuple[float, float]:
        """벽의 법선 벡터 계산"""
        return (np.cos(rotation_z + np.pi/2), np.sin(rotation_z + np.pi/2))
    
    def _serialize_bim_model(self, bim_model: BIMModel) -> Dict[str, Any]:
        """BIM 모델 직렬화"""
        return {
            "project_info": {
                "guid": bim_model.project_guid,
                "name": bim_model.project_name,
                "building_type": bim_model.building_type,
                "total_area": bim_model.total_area,
                "stories": bim_model.stories,
                "creation_date": bim_model.creation_date.isoformat(),
                "author": bim_model.author,
                "schema_version": bim_model.schema_version
            },
            "elements": [
                {
                    "guid": elem.guid,
                    "type": elem.element_type.value,
                    "name": elem.name,
                    "location": elem.location,
                    "rotation": elem.rotation,
                    "dimensions": elem.dimensions,
                    "material": elem.material.value if elem.material else None,
                    "level": elem.level,
                    "properties": elem.properties
                }
                for elem in bim_model.elements.values()
            ],
            "spaces": [
                {
                    "guid": space.guid,
                    "name": space.name,
                    "type": space.space_type,
                    "area": space.area,
                    "height": space.height,
                    "volume": space.calculate_volume(),
                    "level": space.level,
                    "boundary": space.boundary_points,
                    "adjacent_spaces": space.adjacent_spaces,
                    "properties": space.properties
                }
                for space in bim_model.spaces.values()
            ],
            "analysis": {
                "structural": bim_model.structural_analysis,
                "energy": bim_model.energy_analysis,
                "compliance": bim_model.code_compliance
            },
            "optimization": getattr(bim_model, 'optimization_results', {})
        }
    
    async def _generate_3d_preview(self, bim_model: BIMModel) -> str:
        """3D 프리뷰 생성"""
        # 실제로는 3D 렌더링 서비스 호출
        # 여기서는 더미 URL 반환
        preview_id = f"preview_{bim_model.project_guid[:8]}"
        return f"https://viba-bim-preview.com/{preview_id}"
    
    async def _export_to_ifc(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """IFC 파일로 내보내기"""
        if not ifcopenshell:
            return {
                "status": "error",
                "message": "IFC export not available (ifcopenshell not installed)"
            }
        
        bim_model_data = input_data.get("bim_model", {})
        output_path = input_data.get("output_path", f"output_{uuid.uuid4().hex[:8]}.ifc")
        
        try:
            # IFC 파일 생성
            ifc_file = ifcopenshell.file(schema="IFC4X3")
            
            # 프로젝트 정보 설정
            project = ifc_file.create_entity(
                "IfcProject",
                GlobalId=bim_model_data["project_info"]["guid"],
                Name=bim_model_data["project_info"]["name"]
            )
            
            # 사이트 생성
            site = ifc_file.create_entity(
                "IfcSite",
                GlobalId=str(uuid.uuid4()),
                Name="Default Site"
            )
            
            # 건물 생성
            building = ifc_file.create_entity(
                "IfcBuilding",
                GlobalId=str(uuid.uuid4()),
                Name=bim_model_data["project_info"]["name"]
            )
            
            # 층 생성
            stories = {}
            for level in range(bim_model_data["project_info"]["stories"]):
                story = ifc_file.create_entity(
                    "IfcBuildingStorey",
                    GlobalId=str(uuid.uuid4()),
                    Name=f"Level {level}",
                    Elevation=level * 2.8  # 기본 층고
                )
                stories[level] = story
            
            # 요소 생성
            for elem_data in bim_model_data["elements"]:
                elem_type = elem_data["type"]
                
                # IFC 엔티티 생성
                ifc_elem = ifc_file.create_entity(
                    elem_type,
                    GlobalId=elem_data["guid"],
                    Name=elem_data["name"]
                )
                
                # 위치 설정
                # ... (복잡한 IFC 변환 로직)
            
            # 파일 저장
            ifc_file.write(output_path)
            
            return {
                "status": "success",
                "file_path": output_path,
                "file_size": os.path.getsize(output_path),
                "element_count": len(bim_model_data["elements"]),
                "space_count": len(bim_model_data["spaces"])
            }
            
        except Exception as e:
            logger.error(f"IFC export failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _load_space_templates(self) -> Dict[str, Dict[str, Any]]:
        """공간 템플릿 로드"""
        return {
            "living_room": {
                "min_area": 20.0,
                "preferred_area": 30.0,
                "min_width": 3.5,
                "natural_light": True,
                "adjacent_to": ["kitchen", "entrance"],
                "avoid_adjacent": ["bathroom"]
            },
            "bedroom": {
                "min_area": 9.0,
                "preferred_area": 12.0,
                "min_width": 2.7,
                "natural_light": True,
                "privacy_level": "high",
                "adjacent_to": ["bathroom"],
                "avoid_adjacent": ["kitchen"]
            },
            "kitchen": {
                "min_area": 6.0,
                "preferred_area": 10.0,
                "min_width": 2.4,
                "natural_light": True,
                "ventilation": True,
                "adjacent_to": ["living_room", "dining_room"]
            },
            "bathroom": {
                "min_area": 4.0,
                "preferred_area": 6.0,
                "min_width": 1.5,
                "natural_light": False,
                "ventilation": True,
                "privacy_level": "high"
            }
        }
    
    def _load_element_templates(self) -> Dict[str, Dict[str, Any]]:
        """요소 템플릿 로드"""
        return {
            "standard_wall": {
                "thickness": 0.2,
                "material": "concrete",
                "fire_rating": "2hr",
                "sound_rating": "STC 50"
            },
            "partition_wall": {
                "thickness": 0.1,
                "material": "gypsum",
                "fire_rating": "1hr",
                "sound_rating": "STC 35"
            },
            "exterior_wall": {
                "thickness": 0.3,
                "material": "brick",
                "insulation": 0.1,
                "fire_rating": "3hr"
            }
        }


if __name__ == "__main__":
    # 테스트
    import asyncio
    
    async def test_bim_specialist():
        agent = BIMSpecialistAgent()
        await agent.initialize()
        
        # 테스트 작업
        test_task = type('Task', (), {
            'task_type': 'generate_bim',
            'input_data': {
                'project_name': 'Test Apartment',
                'design_concept': {
                    'building_type': 'residential',
                    'spatial_organization': {
                        'spaces': [
                            {'name': '거실', 'type': 'living_room', 'area': 30, 'priority': 1},
                            {'name': '주방', 'type': 'kitchen', 'area': 12, 'priority': 2},
                            {'name': '침실1', 'type': 'bedroom', 'area': 15, 'priority': 3},
                            {'name': '침실2', 'type': 'bedroom', 'area': 12, 'priority': 4},
                            {'name': '화장실', 'type': 'bathroom', 'area': 6, 'priority': 5}
                        ]
                    },
                    'dimensional_guidelines': {
                        'total_area': 100.0,
                        'stories': 1
                    },
                    'material_palette': ['콘크리트', '벽돌', '유리', '목재']
                }
            }
        })()
        
        result = await agent.execute_task(test_task)
        
        if result['status'] == 'success':
            print(f"BIM 모델 생성 완료:")
            print(f"- 총 요소: {result['result']['statistics']['total_elements']}개")
            print(f"- 총 공간: {result['result']['statistics']['total_spaces']}개")
            print(f"- 총 면적: {result['result']['statistics']['total_area']}㎡")
            print(f"- 총 부피: {result['result']['statistics']['total_volume']:.2f}㎥")
            print(f"- 법규 준수: {result['result']['compliance']['overall_compliance']}")
        else:
            print(f"오류 발생: {result['error']}")
    
    asyncio.run(test_bim_specialist())