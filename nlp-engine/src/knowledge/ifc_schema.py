"""
IFC 4.3 스키마 정의
==================

IFC (Industry Foundation Classes) 4.3 스키마 구조 및 변환 로직

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import uuid


class IFCVersion(Enum):
    """IFC 버전"""
    IFC2X3 = "IFC2X3"
    IFC4 = "IFC4"
    IFC4X1 = "IFC4X1"
    IFC4X2 = "IFC4X2"
    IFC4X3 = "IFC4X3"


class IFCEntityType(Enum):
    """주요 IFC 엔티티 타입"""
    # 프로젝트 구조
    PROJECT = "IfcProject"
    SITE = "IfcSite"
    BUILDING = "IfcBuilding"
    BUILDING_STOREY = "IfcBuildingStorey"
    SPACE = "IfcSpace"
    
    # 건축 요소
    WALL = "IfcWall"
    WALL_STANDARD_CASE = "IfcWallStandardCase"
    COLUMN = "IfcColumn"
    BEAM = "IfcBeam"
    SLAB = "IfcSlab"
    ROOF = "IfcRoof"
    STAIR = "IfcStair"
    RAMP = "IfcRamp"
    DOOR = "IfcDoor"
    WINDOW = "IfcWindow"
    CURTAIN_WALL = "IfcCurtainWall"
    RAILING = "IfcRailing"
    
    # MEP
    PIPE_SEGMENT = "IfcPipeSegment"
    DUCT_SEGMENT = "IfcDuctSegment"
    CABLE_SEGMENT = "IfcCableSegment"
    FLOW_TERMINAL = "IfcFlowTerminal"
    
    # 가구/장비
    FURNITURE = "IfcFurniture"
    SYSTEM_FURNITURE = "IfcSystemFurnitureElement"
    BUILDING_ELEMENT_PROXY = "IfcBuildingElementProxy"
    
    # 관계
    REL_AGGREGATES = "IfcRelAggregates"
    REL_CONTAINED = "IfcRelContainedInSpatialStructure"
    REL_FILLS = "IfcRelFillsElement"
    REL_VOIDS = "IfcRelVoidsElement"
    REL_CONNECTS = "IfcRelConnectsElements"


@dataclass
class IFCProperty:
    """IFC 속성"""
    name: str
    value: Any
    property_type: str  # IfcText, IfcReal, IfcInteger, etc.
    unit: Optional[str] = None
    description: Optional[str] = None


@dataclass
class IFCMaterial:
    """IFC 재료"""
    name: str
    category: str
    properties: List[IFCProperty]
    
    def to_ifc_dict(self) -> Dict[str, Any]:
        """IFC 딕셔너리로 변환"""
        return {
            "Name": self.name,
            "Category": self.category,
            "Material": {
                "Name": self.name,
                "Properties": [
                    {
                        "Name": prop.name,
                        "NominalValue": {
                            "type": prop.property_type,
                            "value": prop.value
                        },
                        "Unit": prop.unit
                    }
                    for prop in self.properties
                ]
            }
        }


@dataclass
class IFCGeometry:
    """IFC 기하학 정보"""
    representation_type: str  # SweptSolid, Brep, CSG, etc.
    placement: Dict[str, float]  # x, y, z
    direction: Dict[str, float]  # dx, dy, dz
    geometry_data: Any  # 실제 기하학 데이터
    
    def to_ifc_dict(self) -> Dict[str, Any]:
        """IFC 딕셔너리로 변환"""
        return {
            "Representations": [{
                "ContextOfItems": {
                    "ContextType": "Model",
                    "CoordinateSpaceDimension": 3,
                    "Precision": 0.01
                },
                "RepresentationIdentifier": "Body",
                "RepresentationType": self.representation_type,
                "Items": self.geometry_data
            }],
            "ObjectPlacement": {
                "PlacementRelTo": None,
                "RelativePlacement": {
                    "Location": {
                        "Coordinates": [
                            self.placement["x"],
                            self.placement["y"],
                            self.placement["z"]
                        ]
                    },
                    "RefDirection": {
                        "DirectionRatios": [
                            self.direction["dx"],
                            self.direction["dy"],
                            self.direction["dz"]
                        ]
                    }
                }
            }
        }


class IFC43Schema:
    """IFC 4.3 스키마 관리자"""
    
    def __init__(self):
        self.version = IFCVersion.IFC4X3
        self.entity_definitions = self._load_entity_definitions()
        self.property_sets = self._load_property_sets()
        self.material_library = self._load_material_library()
    
    def _load_entity_definitions(self) -> Dict[str, Dict[str, Any]]:
        """엔티티 정의 로드"""
        return {
            "IfcWall": {
                "parent": "IfcBuildingElement",
                "attributes": {
                    "GlobalId": "IfcGloballyUniqueId",
                    "OwnerHistory": "IfcOwnerHistory",
                    "Name": "IfcLabel",
                    "Description": "IfcText",
                    "ObjectType": "IfcLabel",
                    "ObjectPlacement": "IfcLocalPlacement",
                    "Representation": "IfcProductRepresentation",
                    "Tag": "IfcIdentifier",
                    "PredefinedType": "IfcWallTypeEnum"
                },
                "property_sets": ["Pset_WallCommon"]
            },
            "IfcSpace": {
                "parent": "IfcSpatialStructureElement",
                "attributes": {
                    "GlobalId": "IfcGloballyUniqueId",
                    "OwnerHistory": "IfcOwnerHistory",
                    "Name": "IfcLabel",
                    "Description": "IfcText",
                    "ObjectType": "IfcLabel",
                    "ObjectPlacement": "IfcLocalPlacement",
                    "Representation": "IfcProductRepresentation",
                    "LongName": "IfcLabel",
                    "CompositionType": "IfcElementCompositionEnum",
                    "PredefinedType": "IfcSpaceTypeEnum",
                    "ElevationWithFlooring": "IfcLengthMeasure"
                },
                "property_sets": ["Pset_SpaceCommon", "Pset_SpaceOccupancyRequirements"]
            },
            "IfcColumn": {
                "parent": "IfcBuildingElement",
                "attributes": {
                    "GlobalId": "IfcGloballyUniqueId",
                    "OwnerHistory": "IfcOwnerHistory",
                    "Name": "IfcLabel",
                    "Description": "IfcText",
                    "ObjectType": "IfcLabel",
                    "ObjectPlacement": "IfcLocalPlacement",
                    "Representation": "IfcProductRepresentation",
                    "Tag": "IfcIdentifier",
                    "PredefinedType": "IfcColumnTypeEnum"
                },
                "property_sets": ["Pset_ColumnCommon"]
            }
            # ... 더 많은 엔티티 정의
        }
    
    def _load_property_sets(self) -> Dict[str, List[str]]:
        """속성 세트 정의 로드"""
        return {
            "Pset_WallCommon": [
                "Reference",
                "AcousticRating", 
                "FireRating",
                "Combustible",
                "SurfaceSpreadOfFlame",
                "ThermalTransmittance",
                "IsExternal",
                "ExtendToStructure",
                "LoadBearing",
                "Compartmentation"
            ],
            "Pset_SpaceCommon": [
                "Reference",
                "IsExternal",
                "GrossPlannedArea",
                "NetPlannedArea",
                "PubliclyAccessible",
                "HandicapAccessible",
                "GrossVolume",
                "NetVolume",
                "MinimumHeadroom"
            ],
            "Pset_ColumnCommon": [
                "Reference",
                "Status",
                "Slope",
                "Roll",
                "IsExternal",
                "ThermalTransmittance",
                "FireRating",
                "LoadBearing"
            ],
            "Pset_DoorCommon": [
                "Reference",
                "FireRating",
                "AcousticRating",
                "SecurityRating",
                "IsExternal",
                "Infiltration",
                "ThermalTransmittance",
                "HandicapAccessible",
                "FireExit",
                "SelfClosing"
            ]
        }
    
    def _load_material_library(self) -> Dict[str, IFCMaterial]:
        """재료 라이브러리 로드"""
        return {
            "Concrete_C30": IFCMaterial(
                name="Concrete C30/37",
                category="Concrete",
                properties=[
                    IFCProperty("CompressiveStrength", 30, "IfcPressureMeasure", "MPa"),
                    IFCProperty("Density", 2400, "IfcMassDensityMeasure", "kg/m³"),
                    IFCProperty("ThermalConductivity", 1.65, "IfcThermalConductivityMeasure", "W/mK"),
                    IFCProperty("PoissonRatio", 0.2, "IfcPositiveRatioMeasure"),
                    IFCProperty("YoungModulus", 33000, "IfcModulusOfElasticityMeasure", "MPa")
                ]
            ),
            "Steel_S355": IFCMaterial(
                name="Steel S355",
                category="Steel",
                properties=[
                    IFCProperty("YieldStrength", 355, "IfcPressureMeasure", "MPa"),
                    IFCProperty("UltimateStrength", 510, "IfcPressureMeasure", "MPa"),
                    IFCProperty("Density", 7850, "IfcMassDensityMeasure", "kg/m³"),
                    IFCProperty("ThermalConductivity", 50, "IfcThermalConductivityMeasure", "W/mK"),
                    IFCProperty("YoungModulus", 210000, "IfcModulusOfElasticityMeasure", "MPa")
                ]
            ),
            "Glass_Double": IFCMaterial(
                name="Double Glazing",
                category="Glass",
                properties=[
                    IFCProperty("ThermalTransmittance", 1.4, "IfcThermalTransmittanceMeasure", "W/m²K"),
                    IFCProperty("VisibleLightTransmittance", 0.78, "IfcPositiveRatioMeasure"),
                    IFCProperty("SolarHeatGainCoefficient", 0.67, "IfcPositiveRatioMeasure"),
                    IFCProperty("AcousticRating", 32, "IfcSoundPowerMeasure", "dB")
                ]
            ),
            "Insulation_XPS": IFCMaterial(
                name="XPS Insulation",
                category="Insulation",
                properties=[
                    IFCProperty("ThermalConductivity", 0.034, "IfcThermalConductivityMeasure", "W/mK"),
                    IFCProperty("Density", 35, "IfcMassDensityMeasure", "kg/m³"),
                    IFCProperty("CompressiveStrength", 300, "IfcPressureMeasure", "kPa"),
                    IFCProperty("WaterAbsorption", 0.5, "IfcPositiveRatioMeasure", "%")
                ]
            )
        }
    
    def create_entity(self, entity_type: IFCEntityType, 
                     attributes: Dict[str, Any]) -> Dict[str, Any]:
        """IFC 엔티티 생성"""
        entity_def = self.entity_definitions.get(entity_type.value, {})
        
        # 필수 속성 확인
        required_attrs = entity_def.get("attributes", {})
        
        # GlobalId 자동 생성
        if "GlobalId" not in attributes:
            attributes["GlobalId"] = self._generate_global_id()
        
        # 엔티티 구조 생성
        entity = {
            "type": entity_type.value,
            "GlobalId": attributes["GlobalId"],
            "attributes": attributes,
            "properties": {},
            "relationships": []
        }
        
        return entity
    
    def create_spatial_structure(self, project_name: str, 
                               site_name: str,
                               building_name: str,
                               stories: List[str]) -> Dict[str, Any]:
        """공간 구조 생성"""
        # 프로젝트
        project = self.create_entity(IFCEntityType.PROJECT, {
            "Name": project_name,
            "Description": f"VIBA Generated Project - {project_name}",
            "Phase": "Design"
        })
        
        # 사이트
        site = self.create_entity(IFCEntityType.SITE, {
            "Name": site_name,
            "Description": "Building Site",
            "RefLatitude": [37, 33, 0],  # 서울 위도
            "RefLongitude": [126, 58, 0],  # 서울 경도
            "RefElevation": 0.0
        })
        
        # 건물
        building = self.create_entity(IFCEntityType.BUILDING, {
            "Name": building_name,
            "Description": "Main Building",
            "BuildingAddress": {
                "Purpose": "OFFICE",
                "AddressLines": ["123 Main Street"],
                "Town": "Seoul",
                "Region": "Seoul",
                "PostalCode": "12345",
                "Country": "South Korea"
            }
        })
        
        # 층
        building_stories = []
        for i, story_name in enumerate(stories):
            story = self.create_entity(IFCEntityType.BUILDING_STOREY, {
                "Name": story_name,
                "Description": f"Level {i}",
                "Elevation": i * 3.0,  # 3m 층고
                "AboveGround": i >= 0
            })
            building_stories.append(story)
        
        # 관계 설정
        project["relationships"].append({
            "type": IFCEntityType.REL_AGGREGATES.value,
            "RelatingObject": project["GlobalId"],
            "RelatedObjects": [site["GlobalId"]]
        })
        
        site["relationships"].append({
            "type": IFCEntityType.REL_AGGREGATES.value,
            "RelatingObject": site["GlobalId"],
            "RelatedObjects": [building["GlobalId"]]
        })
        
        building["relationships"].append({
            "type": IFCEntityType.REL_AGGREGATES.value,
            "RelatingObject": building["GlobalId"],
            "RelatedObjects": [story["GlobalId"] for story in building_stories]
        })
        
        return {
            "project": project,
            "site": site,
            "building": building,
            "stories": building_stories
        }
    
    def create_wall(self, name: str, 
                   start_point: Tuple[float, float, float],
                   end_point: Tuple[float, float, float],
                   height: float,
                   thickness: float,
                   material: Optional[IFCMaterial] = None,
                   is_external: bool = False) -> Dict[str, Any]:
        """벽체 생성"""
        import numpy as np
        
        # 벽 방향 계산
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        length = np.sqrt(dx**2 + dy**2)
        
        # 중심점
        center_x = (start_point[0] + end_point[0]) / 2
        center_y = (start_point[1] + end_point[1]) / 2
        center_z = start_point[2] + height / 2
        
        # 벽 엔티티 생성
        wall = self.create_entity(IFCEntityType.WALL, {
            "Name": name,
            "Description": "Standard Wall",
            "ObjectType": "STANDARD",
            "Tag": f"W-{name}",
            "PredefinedType": "STANDARD"
        })
        
        # 기하학 정보
        wall["geometry"] = IFCGeometry(
            representation_type="SweptSolid",
            placement={"x": center_x, "y": center_y, "z": center_z},
            direction={"dx": dx/length, "dy": dy/length, "dz": 0},
            geometry_data={
                "SweptArea": {
                    "type": "IfcRectangleProfileDef",
                    "ProfileType": "AREA",
                    "ProfileName": "Wall Profile",
                    "XDim": length,
                    "YDim": thickness
                },
                "ExtrudedDirection": {"DirectionRatios": [0, 0, 1]},
                "Depth": height
            }
        )
        
        # 속성 설정
        wall["properties"]["Pset_WallCommon"] = {
            "IsExternal": is_external,
            "LoadBearing": True,
            "FireRating": "REI120",
            "ThermalTransmittance": 0.3 if is_external else 1.0,
            "AcousticRating": 52
        }
        
        # 재료 할당
        if material:
            wall["material"] = material.to_ifc_dict()
        
        return wall
    
    def create_space(self, name: str,
                    space_type: str,
                    boundary_points: List[Tuple[float, float]],
                    height: float,
                    level_elevation: float = 0.0) -> Dict[str, Any]:
        """공간 생성"""
        # 면적 계산 (간단한 다각형 면적 공식)
        area = 0.0
        n = len(boundary_points)
        for i in range(n):
            j = (i + 1) % n
            area += boundary_points[i][0] * boundary_points[j][1]
            area -= boundary_points[j][0] * boundary_points[i][1]
        area = abs(area) / 2.0
        
        # 중심점 계산
        center_x = sum(p[0] for p in boundary_points) / n
        center_y = sum(p[1] for p in boundary_points) / n
        
        # 공간 엔티티 생성
        space = self.create_entity(IFCEntityType.SPACE, {
            "Name": name,
            "Description": f"{space_type} space",
            "ObjectType": space_type,
            "LongName": name,
            "PredefinedType": self._map_space_type(space_type),
            "ElevationWithFlooring": level_elevation
        })
        
        # 기하학 정보
        space["geometry"] = IFCGeometry(
            representation_type="BoundingBox",
            placement={"x": center_x, "y": center_y, "z": level_elevation + height/2},
            direction={"dx": 1, "dy": 0, "dz": 0},
            geometry_data={
                "BoundingBox": {
                    "Corner": {"Coordinates": [0, 0, 0]},
                    "XDim": max(p[0] for p in boundary_points) - min(p[0] for p in boundary_points),
                    "YDim": max(p[1] for p in boundary_points) - min(p[1] for p in boundary_points),
                    "ZDim": height
                }
            }
        )
        
        # 속성 설정
        space["properties"]["Pset_SpaceCommon"] = {
            "Reference": f"SP-{name}",
            "IsExternal": False,
            "GrossPlannedArea": area,
            "NetPlannedArea": area * 0.95,  # 5% 벽체 제외
            "PubliclyAccessible": space_type in ["lobby", "corridor"],
            "HandicapAccessible": True,
            "GrossVolume": area * height,
            "NetVolume": area * height * 0.95,
            "MinimumHeadroom": height
        }
        
        return space
    
    def _map_space_type(self, space_type: str) -> str:
        """공간 타입 매핑"""
        mapping = {
            "living_room": "INTERNAL",
            "bedroom": "INTERNAL", 
            "kitchen": "INTERNAL",
            "bathroom": "INTERNAL",
            "corridor": "CIRCULATION",
            "stair": "CIRCULATION",
            "balcony": "EXTERNAL",
            "parking": "PARKING"
        }
        return mapping.get(space_type.lower(), "INTERNAL")
    
    def _generate_global_id(self) -> str:
        """IFC GlobalId 생성 (22자 Base64)"""
        import base64
        
        # UUID를 바이트로 변환
        uuid_bytes = uuid.uuid4().bytes
        
        # Base64 인코딩 후 IFC 형식으로 변환
        b64 = base64.b64encode(uuid_bytes).decode('ascii')
        
        # IFC GlobalId 형식으로 변환 (22자)
        # $ 제거, +/를 _$로 변경
        ifc_id = b64.rstrip('=').replace('+', '_').replace('/', '$')[:22]
        
        return ifc_id
    
    def validate_entity(self, entity: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """엔티티 유효성 검증"""
        errors = []
        entity_type = entity.get("type")
        
        if not entity_type:
            errors.append("Entity type is missing")
            return False, errors
        
        # 엔티티 정의 확인
        entity_def = self.entity_definitions.get(entity_type)
        if not entity_def:
            errors.append(f"Unknown entity type: {entity_type}")
            return False, errors
        
        # 필수 속성 확인
        required_attrs = entity_def.get("attributes", {})
        entity_attrs = entity.get("attributes", {})
        
        for attr_name, attr_type in required_attrs.items():
            if attr_name not in entity_attrs:
                errors.append(f"Missing required attribute: {attr_name}")
        
        # GlobalId 형식 확인
        global_id = entity_attrs.get("GlobalId")
        if global_id and len(global_id) != 22:
            errors.append(f"Invalid GlobalId format: {global_id}")
        
        return len(errors) == 0, errors
    
    def export_to_ifc_string(self, entities: List[Dict[str, Any]]) -> str:
        """엔티티를 IFC 문자열로 내보내기"""
        ifc_lines = []
        
        # 헤더
        ifc_lines.append("ISO-10303-21;")
        ifc_lines.append("HEADER;")
        ifc_lines.append("FILE_DESCRIPTION(('ViewDefinition [CoordinationView]'),'2;1');")
        ifc_lines.append("FILE_NAME('VIBA_Export.ifc','2025-07-06T12:00:00',('VIBA'),('VIBA AI'),'IFC4X3','VIBA BIM Engine','');")
        ifc_lines.append("FILE_SCHEMA(('IFC4X3'));")
        ifc_lines.append("ENDSEC;")
        ifc_lines.append("")
        ifc_lines.append("DATA;")
        
        # 엔티티 인스턴스 생성
        instance_id = 1
        for entity in entities:
            line = f"#{instance_id}={entity['type']}("
            
            # 속성 추가
            attrs = entity.get("attributes", {})
            attr_values = []
            
            for attr_name in ["GlobalId", "OwnerHistory", "Name", "Description"]:
                if attr_name in attrs:
                    value = attrs[attr_name]
                    if isinstance(value, str):
                        attr_values.append(f"'{value}'")
                    elif value is None:
                        attr_values.append("$")
                    else:
                        attr_values.append(str(value))
                else:
                    attr_values.append("$")
            
            line += ",".join(attr_values) + ");"
            ifc_lines.append(line)
            instance_id += 1
        
        ifc_lines.append("ENDSEC;")
        ifc_lines.append("")
        ifc_lines.append("END-ISO-10303-21;")
        
        return "\n".join(ifc_lines)