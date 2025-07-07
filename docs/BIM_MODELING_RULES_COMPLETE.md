# BIM 모델링 룰 및 가이드라인 (완전판)

**참조 표준: ISO 16739-1:2024 (IFC 4.3) & ISO 19650-1:2018**  
**문서 버전**: 2.0  
**최종 업데이트**: 2025.07.06  
**기반 자료**: IFC 4.3.2.0 스키마 + AI 학습용 구조화 데이터

---

## 🏛️ 1. IFC 스키마 4계층 구조

### 1.1 계층 구조 개요
```json
{
  "SchemaVersion": "IFC 4.3.2.0",
  "ConceptualLayers": {
    "1_Resource": {
      "description": "기본 데이터 타입, 측정 단위, 기하학적 정의",
      "purpose": "가장 기본적인 구성 요소 정의",
      "independence": "독립적으로 사용 불가, 다른 계층에서 참조"
    },
    "2_Core": {
      "description": "기본 구조, 관계, 공통 개념 정의",
      "entities": ["IfcRoot", "IfcObjectDefinition", "IfcRelationship", "IfcPropertyDefinition"],
      "purpose": "모든 상위 계층의 기반 제공"
    },
    "3_Interoperability": {
      "description": "공통 개념의 특화된 정의",
      "entities": ["IfcProduct", "IfcElement", "IfcSpatialElement"],
      "purpose": "도메인 특화 확장을 위한 중간 계층"
    },
    "4_Domain": {
      "description": "AEC/FM 특화 엔티티 정의",
      "entities": ["IfcWall", "IfcDoor", "IfcWindow", "IfcBeam", "IfcColumn"],
      "purpose": "실제 건물 요소 및 시설 관리 객체 정의"
    }
  }
}
```

### 1.2 핵심 관계 패턴
```typescript
interface CoreRelationshipPatterns {
  SpatialContainment: "IfcRelContainedInSpatialStructure";
  Aggregation: "IfcRelAggregates";
  Nesting: "IfcRelNests";
  TypeAssignment: "IfcRelDefinesByType";
  PropertyAssignment: "IfcRelDefinesByProperties";
  VoidCreation: "IfcRelVoidsElement";
  FillingOpening: "IfcRelFillsElement";
  MaterialAssociation: "IfcRelAssociatesMaterial";
}
```

---

## 🎯 2. 핵심 엔티티 상세 정의

### 2.1 IfcRoot - 최상위 추상 엔티티
```json
{
  "entity_name": "IfcRoot",
  "hierarchy_level": "Core Layer",
  "parent_entity": null,
  "child_entities": ["IfcObjectDefinition", "IfcPropertyDefinition", "IfcRelationship"],
  "definition": "IFC 스키마의 최상위 추상 클래스로, 모든 IFC 엔티티의 공통 상위 타입",
  "abstract": true,
  "attributes": {
    "GlobalId": {
      "type": "IfcGloballyUniqueId",
      "required": true,
      "description": "전 세계적으로 고유한 식별자 (GUID)",
      "constraint": "22자리 base64 인코딩된 문자열",
      "generation": "IFC 표준 알고리즘 사용 필수"
    },
    "OwnerHistory": {
      "type": "IfcOwnerHistory",
      "required": false,
      "description": "소유권, 생성, 수정 이력 정보"
    },
    "Name": {
      "type": "IfcLabel",
      "required": false,
      "description": "선택적 이름 (일부 서브타입에서 필수)"
    },
    "Description": {
      "type": "IfcText",
      "required": false,
      "description": "선택적 설명"
    }
  },
  "modeling_rules": [
    "모든 IFC 객체는 IfcRoot로부터 상속받아야 함",
    "GlobalId는 모델 내에서 유일해야 함",
    "GlobalId 중복 검사 필수",
    "OwnerHistory는 협업 환경에서 변경 추적을 위해 권장",
    "순환 관계 방지 필수"
  ]
}
```

### 2.2 IfcObjectDefinition - 객체 정의
```json
{
  "entity_name": "IfcObjectDefinition",
  "hierarchy_level": "Core Layer",
  "parent_entity": "IfcRoot",
  "child_entities": ["IfcObject", "IfcTypeObject", "IfcContext"],
  "definition": "물리적, 공간적, 개념적 모든 객체의 일반화",
  "abstract": true,
  "key_specializations": {
    "IfcObject": {
      "purpose": "시간, 공간, 기타 컨텍스트에서의 개별 객체 인스턴스",
      "subtypes": ["IfcProduct", "IfcProcess", "IfcControl", "IfcActor", "IfcGroup", "IfcResource"]
    },
    "IfcTypeObject": {
      "purpose": "동일한 타입의 모든 객체 인스턴스에 공통적인 정의",
      "usage": "IfcRelDefinesByType 관계로 타입 연결"
    },
    "IfcContext": {
      "purpose": "기본 프로젝트 또는 라이브러리 컨텍스트",
      "types": ["IfcProject", "IfcProjectLibrary"]
    }
  },
  "relationships": {
    "HasAssignments": {
      "inverse": "IfcRelAssigns",
      "cardinality": "0:N",
      "description": "객체 간 링크 관계 (할당)"
    },
    "IsDecomposedBy": {
      "inverse": "IfcRelDecomposes",
      "cardinality": "0:1",
      "description": "전체/부분 계층 구조",
      "rule": "각 객체는 하나의 분해 체인에만 속할 수 있음 (트리 구조)"
    },
    "HasAssociations": {
      "inverse": "IfcRelAssociates",
      "cardinality": "0:N",
      "description": "외부 정보 연결"
    },
    "IsDefinedBy": {
      "inverse": "IfcRelDefines",
      "cardinality": "0:N",
      "description": "타입 정의 또는 속성 집합 정의"
    }
  }
}
```

### 2.3 IfcProduct - 제품/건물 요소
```json
{
  "entity_name": "IfcProduct",
  "hierarchy_level": "Core Layer",
  "parent_entity": "IfcObject",
  "child_entities": ["IfcElement", "IfcSpatialElement", "IfcAnnotation", "IfcGrid"],
  "definition": "기하학적 또는 공간적 컨텍스트와 관련된 모든 객체의 추상적 표현",
  "abstract": true,
  "attributes": {
    "ObjectType": {
      "type": "IfcLabel",
      "required": false,
      "description": "객체 타입 식별자"
    },
    "ObjectPlacement": {
      "type": "IfcObjectPlacement",
      "required": false,
      "description": "객체의 공간적 위치",
      "rule": "ShapeRepresentation이 있으면 필수 (주석 제외)"
    },
    "Representation": {
      "type": "IfcProductRepresentation",
      "required": false,
      "description": "객체의 기하학적 표현"
    }
  },
  "spatial_containment_rules": {
    "relationship": "IfcRelContainedInSpatialStructure",
    "hierarchy": "Project → Site → Building → BuildingStorey → Space",
    "constraint": "각 IfcProduct는 최대 하나의 공간 구조에만 포함 가능",
    "cardinality": "0:1"
  }
}
```

### 2.4 IfcElement - 건물 요소
```json
{
  "entity_name": "IfcElement",
  "hierarchy_level": "Interoperability Layer",
  "parent_entity": "IfcProduct",
  "child_entities": ["IfcBuildingElement", "IfcCivilElement", "IfcDistributionElement"],
  "definition": "건축물에 통합되는 물리적으로 존재하는 모든 구성 요소",
  "abstract": true,
  "attributes": {
    "Tag": {
      "type": "IfcIdentifier",
      "required": false,
      "description": "요소의 태그 또는 라벨"
    }
  },
  "specializations": {
    "IfcBuildingElement": {
      "purpose": "건축 구조 요소",
      "examples": ["IfcWall", "IfcSlab", "IfcColumn", "IfcBeam", "IfcDoor", "IfcWindow"]
    },
    "IfcCivilElement": {
      "purpose": "토목 구조 요소",
      "examples": ["IfcBridge", "IfcTunnel", "IfcRoad", "IfcRailway"]
    },
    "IfcDistributionElement": {
      "purpose": "설비 요소",
      "examples": ["IfcPipeSegment", "IfcDuctSegment", "IfcCableCarrierSegment"]
    }
  },
  "modeling_rules": [
    "각 IfcElement는 정확히 하나의 공간 컨테이너에 포함되어야 함",
    "기하학적 표현 필수",
    "Tag 속성으로 식별 가능",
    "재료 정보 연결 권장 (IfcRelAssociatesMaterial)"
  ]
}
```

---

## 🏗️ 3. 도메인별 상세 엔티티

### 3.1 IfcWall - 벽체
```typescript
interface IfcWall extends IfcBuildingElement {
  // 속성
  GlobalId: IfcGloballyUniqueId;           // 필수: 고유 식별자
  OwnerHistory?: IfcOwnerHistory;          // 선택: 소유 이력
  Name?: IfcLabel;                         // 선택: 이름
  Description?: IfcText;                   // 선택: 설명
  ObjectType?: IfcLabel;                   // 선택: 객체 유형
  ObjectPlacement?: IfcObjectPlacement;    // 선택: 공간 내 배치
  Representation?: IfcProductRepresentation; // 선택: 기하학적 표현
  Tag?: IfcIdentifier;                     // 선택: 태그
  PredefinedType?: IfcWallTypeEnum;        // 선택: 벽 유형
}

// 벽 유형 열거형
enum IfcWallTypeEnum {
  STANDARD = "STANDARD",           // 표준 벽
  POLYGONAL = "POLYGONAL",         // 다각형 벽
  SHEAR = "SHEAR",                // 전단벽
  ELEMENTEDWALL = "ELEMENTEDWALL", // 조립식 벽
  PLUMBINGWALL = "PLUMBINGWALL",   // 배관 벽
  MOVABLE = "MOVABLE",            // 이동식 벽
  PARAPET = "PARAPET",            // 파라펫
  PARTITIONING = "PARTITIONING",   // 칸막이
  SOLIDWALL = "SOLIDWALL",        // 단단한 벽
  RETAININGWALL = "RETAININGWALL", // 옹벽
  USERDEFINED = "USERDEFINED",    // 사용자 정의
  NOTDEFINED = "NOTDEFINED"       // 정의 안됨
}

// 모델링 규칙
const wallModelingRules = {
  spatialContainment: {
    rule: "IfcWall은 반드시 IfcBuildingStorey에 포함되어야 함",
    relationship: "IfcRelContainedInSpatialStructure"
  },
  geometricRepresentation: {
    constantThickness: {
      representation: "SweptSolid",
      material: "IfcMaterialLayerSetUsage",
      axis: "필수"
    },
    variableThickness: {
      representation: "Brep 또는 CSG",
      material: "IfcMaterialList"
    }
  },
  openings: {
    relationship: "IfcRelVoidsElement",
    opening: "IfcOpeningElement",
    boolean: "차감 연산"
  },
  connections: {
    walls: "IfcRelConnectsPathElements",
    slabs: "IfcRelConnectsElements"
  }
};

// 속성 세트
const wallPropertySets = {
  "Pset_WallCommon": {
    IsExternal: "IfcBoolean",        // 외벽 여부
    LoadBearing: "IfcBoolean",       // 내력벽 여부
    FireRating: "IfcLabel",          // 내화 등급
    AcousticRating: "IfcLabel",      // 차음 등급
    SurfaceSpreadOfFlame: "IfcLabel" // 표면 화염 전파
  },
  "Qto_WallBaseQuantities": {
    Length: "IfcQuantityLength",     // 길이
    Height: "IfcQuantityLength",     // 높이
    Width: "IfcQuantityLength",      // 두께
    GrossArea: "IfcQuantityArea",    // 총 면적
    NetArea: "IfcQuantityArea",      // 순 면적
    GrossVolume: "IfcQuantityVolume",// 총 부피
    NetVolume: "IfcQuantityVolume"   // 순 부피
  }
};
```

### 3.2 IfcDoor - 문
```typescript
interface IfcDoor extends IfcBuildingElement {
  // 필수 속성
  OverallHeight?: IfcPositiveLengthMeasure; // 전체 높이
  OverallWidth?: IfcPositiveLengthMeasure;  // 전체 너비
  PredefinedType?: IfcDoorTypeEnum;         // 문 유형
  OperationType?: IfcDoorTypeOperationEnum; // 작동 방식
  UserDefinedOperationType?: IfcLabel;      // 사용자 정의 작동
}

// 문 모델링 규칙
const doorModelingRules = {
  voidRequirement: {
    rule: "IfcDoor는 반드시 IfcOpeningElement를 채워야 함",
    relationship: "IfcRelFillsElement",
    cardinality: "1:1"
  },
  hostElement: {
    rule: "개구부는 호스트 벽에 Boolean 차감으로 생성",
    relationship: "IfcRelVoidsElement"
  },
  geometricConstraints: {
    rule: "문 지오메트리는 개구부 경계 내에 위치해야 함",
    tolerance: "10mm"
  },
  typeAssignment: {
    relationship: "IfcRelDefinesByType",
    type: "IfcDoorType"
  }
};
```

### 3.3 IfcSlab - 슬래브
```typescript
interface IfcSlab extends IfcBuildingElement {
  PredefinedType?: IfcSlabTypeEnum;
}

enum IfcSlabTypeEnum {
  FLOOR = "FLOOR",           // 바닥
  ROOF = "ROOF",            // 지붕
  LANDING = "LANDING",       // 계단참
  BASESLAB = "BASESLAB",     // 기초 슬래브
  APPROACH = "APPROACH",     // 접근 슬래브
  PAVING = "PAVING",        // 포장
  WEARING = "WEARING",       // 마모층
  SIDEWALK = "SIDEWALK"      // 보도
}
```

---

## 🔗 4. 관계(Relationship) 상세 정의

### 4.1 공간 포함 관계
```json
{
  "IfcRelContainedInSpatialStructure": {
    "purpose": "공간 구조 내 요소 포함",
    "attributes": {
      "RelatingStructure": {
        "type": "IfcSpatialElement",
        "cardinality": "1",
        "description": "포함하는 공간 구조"
      },
      "RelatedElements": {
        "type": "SET [1:?] OF IfcProduct",
        "cardinality": "1:N",
        "description": "포함되는 요소들"
      }
    },
    "rules": [
      "각 IfcProduct는 최대 하나의 공간 구조에만 포함",
      "계층적 포함 관계 유지 필수",
      "공간 요소는 IfcRelReferencedInSpatialStructure로 참조 가능"
    ]
  }
}
```

### 4.2 개구부 관계
```json
{
  "IfcRelVoidsElement": {
    "purpose": "요소에 개구부 생성",
    "attributes": {
      "RelatingBuildingElement": {
        "type": "IfcElement",
        "description": "개구부를 포함하는 요소"
      },
      "RelatedOpeningElement": {
        "type": "IfcOpeningElement",
        "description": "개구부 요소"
      }
    },
    "effect": "Boolean 차감 연산",
    "rule": "개구부 지오메트리는 호스트 요소 부피 내에 위치해야 함"
  },
  "IfcRelFillsElement": {
    "purpose": "개구부 채움",
    "attributes": {
      "RelatingOpeningElement": {
        "type": "IfcOpeningElement",
        "description": "채워지는 개구부"
      },
      "RelatedBuildingElement": {
        "type": "IfcElement",
        "description": "채우는 요소 (문, 창 등)"
      }
    },
    "cardinality": "1:1"
  }
}
```

### 4.3 타입 정의 관계
```typescript
interface IfcRelDefinesByType extends IfcRelDefines {
  RelatingType: IfcTypeObject;           // 타입 정의
  RelatedObjects: Set<IfcObject>;        // 타입이 적용되는 객체들
  
  // 규칙
  rules: {
    propertyInheritance: "타입에서 인스턴스로 속성 상속",
    overrideRule: "인스턴스 속성이 타입 속성을 오버라이드",
    consistency: "동일 타입의 모든 인스턴스는 일관된 기본 속성 보유"
  };
}
```

---

## 📋 5. 속성 세트(Pset) 및 수량 산출(Qto)

### 5.1 속성 세트 템플릿
```typescript
interface PropertySetTemplate {
  namePattern: "Pset_*";                  // 명명 규칙
  binding: "IfcRelDefinesByProperties";  // 연결 관계
  structure: {
    header: {
      GlobalId: IfcGloballyUniqueId;
      Name: string;                       // Pset_WallCommon 등
      Description?: string;
    };
    properties: Map<string, Property>;
  };
}

// 공통 속성 세트 예시
const commonPropertySets = {
  "Pset_WallCommon": {
    IsExternal: { type: "IfcBoolean", description: "외벽 여부" },
    LoadBearing: { type: "IfcBoolean", description: "내력벽 여부" },
    FireRating: { type: "IfcLabel", description: "내화 등급" },
    AcousticRating: { type: "IfcLabel", description: "차음 등급" },
    ThermalTransmittance: { type: "IfcThermalTransmittanceMeasure", description: "열관류율" }
  },
  "Pset_DoorCommon": {
    OperationType: { type: "IfcLabel", description: "작동 방식" },
    FireRating: { type: "IfcLabel", description: "내화 등급" },
    AcousticRating: { type: "IfcLabel", description: "차음 등급" },
    SecurityRating: { type: "IfcLabel", description: "보안 등급" },
    IsEmergencyExit: { type: "IfcBoolean", description: "비상구 여부" }
  },
  "Pset_WindowCommon": {
    IsExternal: { type: "IfcBoolean", description: "외창 여부" },
    FireRating: { type: "IfcLabel", description: "내화 등급" },
    AcousticRating: { type: "IfcLabel", description: "차음 등급" },
    ThermalTransmittance: { type: "IfcThermalTransmittanceMeasure", description: "열관류율" },
    GlazingType: { type: "IfcLabel", description: "유리 유형" }
  }
};
```

### 5.2 수량 산출 세트
```typescript
const quantitySets = {
  "Qto_WallBaseQuantities": {
    Length: "IfcQuantityLength",
    Height: "IfcQuantityLength",
    Width: "IfcQuantityLength",
    GrossArea: "IfcQuantityArea",
    NetArea: "IfcQuantityArea",
    GrossVolume: "IfcQuantityVolume",
    NetVolume: "IfcQuantityVolume"
  },
  "Qto_SlabBaseQuantities": {
    Area: "IfcQuantityArea",
    Perimeter: "IfcQuantityLength",
    GrossVolume: "IfcQuantityVolume",
    NetVolume: "IfcQuantityVolume",
    Thickness: "IfcQuantityLength"
  },
  "Qto_DoorBaseQuantities": {
    Height: "IfcQuantityLength",
    Width: "IfcQuantityLength",
    Area: "IfcQuantityArea",
    Perimeter: "IfcQuantityLength"
  }
};
```

---

## 🏛️ 6. 공간 구조 계층

### 6.1 공간 계층 구조
```typescript
interface SpatialHierarchy {
  levels: [
    {
      level: 1,
      entity: "IfcProject",
      description: "프로젝트 최상위 컨테이너",
      required: true,
      cardinality: "1",
      relationship: "IfcRelAggregates"
    },
    {
      level: 2,
      entity: "IfcSite",
      description: "부지 또는 캠퍼스",
      required: false,
      cardinality: "0:N",
      relationship: "IfcRelAggregates"
    },
    {
      level: 3,
      entity: "IfcBuilding",
      description: "건물",
      required: true,
      cardinality: "1:N",
      relationship: "IfcRelAggregates"
    },
    {
      level: 4,
      entity: "IfcBuildingStorey",
      description: "층",
      required: true,
      cardinality: "1:N",
      relationship: "IfcRelAggregates"
    },
    {
      level: 5,
      entity: "IfcSpace",
      description: "공간",
      required: false,
      cardinality: "0:N",
      relationship: "IfcRelAggregates"
    }
  ];
  
  containmentRules: [
    "각 물리적 요소는 하나의 공간 구조에만 포함 가능",
    "IfcRelContainedInSpatialStructure 관계 사용",
    "계층적 포함 관계 유지 필수",
    "공간 요소는 IfcRelReferencedInSpatialStructure로 참조 가능"
  ];
}
```

### 6.2 공간 포함 예시
```typescript
// 프로젝트 구조 예시
const projectStructure = {
  project: {
    id: "1jNQjPMH0EuwiLqMCHWjRV",
    name: "바이브 코딩 오피스 빌딩",
    aggregates: [
      {
        site: {
          id: "2K8QjPMH0EuwiLqMCHWjRV",
          name: "강남구 테헤란로 부지",
          aggregates: [
            {
              building: {
                id: "3L9RjPMH0EuwiLqMCHWjRV",
                name: "본관",
                aggregates: [
                  {
                    storey: {
                      id: "4MASjPMH0EuwiLqMCHWjRV",
                      name: "1층",
                      elevation: 0.0,
                      contains: [
                        { element: "IfcWall", count: 24 },
                        { element: "IfcDoor", count: 8 },
                        { element: "IfcWindow", count: 12 },
                        { element: "IfcSlab", count: 1 }
                      ]
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    ]
  }
};
```

---

## 🔧 7. 모델링 검증 규칙

### 7.1 필수 검증 규칙
```json
[
  {
    "RuleID": "GUID_001",
    "Category": "Identification",
    "Description": "모든 IfcRoot 엔티티는 고유한 GlobalId 필요",
    "Trigger": "엔티티 생성",
    "Check": "GlobalId.length == 22 && isBase64(GlobalId) && isUnique(GlobalId)",
    "Severity": "ERROR"
  },
  {
    "RuleID": "WALL_002",
    "Category": "Spatial",
    "Description": "IfcWall은 반드시 IfcBuildingStorey에 포함",
    "Trigger": "IfcWall 인스턴스 생성",
    "Check": "EXISTS(IfcRelContainedInSpatialStructure WHERE RelatedElement = Wall AND RelatingStructure IS IfcBuildingStorey)",
    "Severity": "ERROR"
  },
  {
    "RuleID": "DOOR_003",
    "Category": "Geometry",
    "Description": "IfcDoor는 정확히 하나의 개구부를 채워야 함",
    "Trigger": "IfcDoor 인스턴스 검증",
    "Check": "COUNT(IfcRelFillsElement WHERE RelatedBuildingElement = Door) == 1",
    "Severity": "ERROR"
  },
  {
    "RuleID": "MATERIAL_004",
    "Category": "Properties",
    "Description": "내력벽은 구조 재료 레이어 정의 필수",
    "Precondition": "IfcWall.LoadBearing == TRUE",
    "Check": "EXISTS(IfcRelAssociatesMaterial WHERE RelatedObjects INCLUDES Wall)",
    "Severity": "WARNING"
  },
  {
    "RuleID": "GEOM_005",
    "Category": "Geometry",
    "Description": "모든 IfcProduct는 기하학적 표현 또는 위치 필요",
    "Trigger": "IfcProduct 인스턴스 생성",
    "Check": "(Representation != NULL) OR (ObjectPlacement != NULL)",
    "Severity": "WARNING"
  },
  {
    "RuleID": "TYPE_006",
    "Category": "Type",
    "Description": "타입이 정의된 경우 속성 상속 규칙 적용",
    "Trigger": "IfcRelDefinesByType 관계 생성",
    "Check": "인스턴스 속성이 타입 속성을 적절히 오버라이드",
    "Severity": "INFO"
  }
]
```

### 7.2 기하학적 검증
```typescript
const geometricValidation = {
  clashDetection: {
    method: "BoundingBox 또는 정밀 지오메트리",
    tolerance: 1, // mm
    categories: ["하드 충돌", "소프트 충돌", "여유 공간"]
  },
  spatialInclusion: {
    rule: "모든 요소는 포함 공간 경계 내에 위치",
    check: "Element.BoundingBox ⊆ Space.BoundingBox"
  },
  openingValidation: {
    rule: "개구부는 호스트 요소 두께를 관통해야 함",
    check: "Opening.Depth >= Host.Thickness"
  }
};
```

---

## 🚀 8. AI 기반 BIM 자동화

### 8.1 자연어 처리 기반 모델 생성
```typescript
interface AIBIMGenerator {
  // 자연어 입력을 BIM 파라미터로 변환
  processNaturalLanguage(input: string): BIMParameters {
    // NLP 처리
    const entities = extractEntities(input);
    const quantities = extractQuantities(input);
    const relationships = inferRelationships(entities);
    
    return {
      buildingType: entities.type,
      area: quantities.area,
      floors: quantities.floors,
      spaces: generateSpaces(entities, quantities),
      materials: suggestMaterials(entities.type),
      constraints: applyBuildingCodes(entities.location)
    };
  }
  
  // AI 기반 공간 최적화
  optimizeSpaceLayout(params: BIMParameters): OptimizedLayout {
    const algorithm = new GeneticAlgorithm({
      objectives: ['space_efficiency', 'circulation', 'natural_light'],
      constraints: ['building_code', 'structural', 'mep'],
      populationSize: 100,
      generations: 50
    });
    
    return algorithm.optimize(params);
  }
}
```

### 8.2 머신러닝 기반 패턴 학습
```typescript
const patternLearning = {
  // 과거 프로젝트 분석
  analyzeHistoricalProjects: (projects: Project[]) => {
    const patterns = {
      spaceLayouts: extractLayoutPatterns(projects),
      materialChoices: extractMaterialPatterns(projects),
      designPreferences: extractDesignPatterns(projects)
    };
    
    return trainModel(patterns);
  },
  
  // 사용자 선호도 학습
  userPreferenceLearning: {
    feedback: "continuous",
    personalization: "individual_profile",
    adaptation: "real_time"
  },
  
  // 예측 모델
  predictOptimalDesign: (requirements: Requirements) => {
    const predictions = {
      layout: predictLayout(requirements),
      materials: predictMaterials(requirements),
      cost: predictCost(requirements),
      timeline: predictTimeline(requirements)
    };
    
    return predictions;
  }
};
```

---

## 📊 9. ISO 19650 기반 정보 관리

### 9.1 정보 요구사항 정의
```yaml
Asset_Information_Requirements (AIR):
  목적: 자산 전체 생애주기 정보 관리
  범위: 
    설계단계: 
      - LOD 100: 개념 설계
      - LOD 200: 기본 설계
      - LOD 300: 실시 설계
      - LOD 400: 시공 도서
    시공단계: 
      - LOD 350: 시공 조정
      - LOD 400: 제작/조립
    운영단계: 
      - LOD 500: 준공 모델
      - FM 데이터 통합

Exchange_Information_Requirements (EIR):
  납품형식: 
    - IFC 4.3 (필수)
    - Native files (선택)
    - COBie (FM용)
  품질기준: 
    - ISO 16739-1:2024 준수
    - buildingSMART 인증
  보안수준: 
    - ISO 19650-5 적용
  납품시점: 
    - 각 설계 단계 마일스톤
    - 주요 의사결정 시점
```

### 9.2 공통 데이터 환경 (CDE)
```
CDE_Structure:
├── WIP (Work in Progress)
│   ├── S1_개인작업영역 (비공개)
│   └── S2_팀작업영역 (팀 내 공유)
├── SHARED (Shared)
│   ├── S3_팀간_공유 (검토/조정)
│   └── S4_클라이언트_공유 (승인 대기)
├── PUBLISHED (Published)
│   ├── A1_승인완료 (공식 발행)
│   └── A2_시공정보 (현장 사용)
└── ARCHIVED (Archived)
    ├── AR1_과거버전 (버전 이력)
    └── AR2_참조자료 (변경 불가)

상태 전환 규칙:
  S1 → S2: 팀 리더 검토
  S2 → S3: QA 통과
  S3 → S4: 조정 완료
  S4 → A1: 클라이언트 승인
  A1 → AR1: 새 버전 발행 시
```

---

## 🔒 10. 정보 보안 및 품질 관리

### 10.1 ISO 19650-5 기반 보안
```typescript
const securityFramework = {
  // 정보 분류
  informationClassification: {
    PU: { level: "Public", description: "공개 정보" },
    IN: { level: "Internal", description: "내부 정보" },
    CO: { level: "Confidential", description: "기밀 정보" },
    SE: { level: "Secret", description: "비밀 정보" }
  },
  
  // 접근 제어 매트릭스
  accessControl: {
    roles: ["Viewer", "Modeler", "Coordinator", "Manager", "Admin"],
    permissions: {
      Viewer: ["read"],
      Modeler: ["read", "create", "update"],
      Coordinator: ["read", "create", "update", "validate"],
      Manager: ["read", "create", "update", "delete", "approve"],
      Admin: ["*"]
    }
  },
  
  // 암호화 정책
  encryption: {
    atRest: "AES-256",
    inTransit: "TLS 1.3",
    keyManagement: "HSM"
  }
};
```

### 10.2 품질 검증 체크리스트
```typescript
const qualityChecklist = {
  schemaCompliance: {
    expressValidation: "IFC 4.3 EXPRESS 규칙 준수",
    whereRules: "WHERE 절 조건 만족",
    uniqueConstraints: "UNIQUE 제약 준수",
    inverseConsistency: "INVERSE 관계 일관성"
  },
  
  geometricQuality: {
    noOverlaps: "요소 중복 없음",
    noGaps: "연결부 틈새 없음",
    tolerances: "허용 오차 범위 내",
    coordinateSystem: "좌표계 일관성"
  },
  
  dataCompleteness: {
    requiredProperties: "필수 속성 100%",
    typeConsistency: "타입 일치성",
    referentialIntegrity: "참조 무결성",
    noOrphans: "고아 객체 없음"
  }
};
```

---

## 📈 11. 성과 지표 (KPI)

### 11.1 정량적 지표
```typescript
const quantitativeKPIs = {
  modelQuality: {
    ifcValidation: { target: "> 95%", measure: "스키마 준수율" },
    clashFree: { target: "> 98%", measure: "충돌 없는 요소 비율" },
    dataCompleteness: { target: "> 90%", measure: "필수 데이터 완성도" }
  },
  
  processEfficiency: {
    modelingTime: { target: "< 2일/층", measure: "모델링 소요 시간" },
    reworkRate: { target: "< 5%", measure: "재작업 비율" },
    automationRate: { target: "> 70%", measure: "자동화 비율" }
  },
  
  collaboration: {
    issueResolution: { target: "< 24시간", measure: "이슈 해결 시간" },
    changeIntegration: { target: "< 4시간", measure: "변경 통합 시간" },
    stakeholderSatisfaction: { target: "> 4.0/5.0", measure: "만족도" }
  }
};
```

### 11.2 정성적 평가
```yaml
Qualitative_Assessment:
  모델_품질:
    - 시각적 정확성
    - 정보 명확성
    - 사용 편의성
    
  프로세스_효율성:
    - 워크플로우 자연스러움
    - 도구 통합성
    - 학습 용이성
    
  협업_효과성:
    - 의사소통 개선
    - 정보 투명성
    - 팀워크 향상
```

---

## 🌟 12. 실무 적용 가이드

### 12.1 단계별 구현 로드맵
```typescript
const implementationRoadmap = {
  phase1_Foundation: {
    duration: "2개월",
    tasks: [
      "IFC 파서 구현",
      "기본 엔티티 모델링",
      "공간 구조 생성",
      "기본 검증 엔진"
    ]
  },
  
  phase2_CoreFeatures: {
    duration: "3개월",
    tasks: [
      "전체 건축 요소 구현",
      "관계 시스템 구축",
      "속성 세트 관리",
      "고급 검증 규칙"
    ]
  },
  
  phase3_Advanced: {
    duration: "3개월",
    tasks: [
      "AI/ML 통합",
      "자동화 시스템",
      "협업 플랫폼",
      "성능 최적화"
    ]
  },
  
  phase4_Production: {
    duration: "2개월",
    tasks: [
      "buildingSMART 인증",
      "사용자 교육",
      "도구 통합",
      "운영 체계 구축"
    ]
  }
};
```

### 12.2 모범 사례 (Best Practices)
```yaml
Modeling_Best_Practices:
  계획_단계:
    - 프로젝트 요구사항 명확화
    - 모델링 목적 정의
    - LOD 수준 합의
    - 명명 규칙 수립
    
  모델링_단계:
    - 공간 구조 우선 생성
    - 단계별 검증 수행
    - 일관된 모델링 방법
    - 정기적 품질 검토
    
  검증_단계:
    - 자동 검증 우선
    - 시각적 검토 병행
    - 이슈 즉시 해결
    - 검증 이력 관리
    
  납품_단계:
    - 최종 품질 검증
    - 메타데이터 완성
    - 문서화 포함
    - 인수인계 교육
```

---

## 📚 부록

### A. IFC 4.3 (ISO 16739-1:2024) 핵심 개선사항
- **인프라 확장**: 교량, 도로, 철도, 수로, 항만 완전 지원
- **지형 모델링**: 복잡한 지형 및 지질 정보 표현 강화
- **정렬 정의**: 선형 인프라를 위한 정렬 개념 도입
- **4D/5D 통합**: 시간 및 비용 정보 네이티브 지원
- **성능 최적화**: 대용량 모델 처리 효율 30% 향상

### B. 자주 사용하는 IFC 엔티티 참조
```typescript
// 건축 요소
const buildingElements = {
  구조체: ["IfcWall", "IfcSlab", "IfcColumn", "IfcBeam", "IfcRoof", "IfcStair", "IfcRamp"],
  개구부: ["IfcDoor", "IfcWindow", "IfcOpeningElement"],
  마감재: ["IfcCovering", "IfcCurtainWall", "IfcRailing"],
  설비: ["IfcPipeSegment", "IfcDuctSegment", "IfcCableCarrierSegment", "IfcFlowTerminal"]
};

// 공간 요소
const spatialElements = {
  외부: ["IfcSite", "IfcExternalSpatialElement"],
  건물: ["IfcBuilding", "IfcBuildingStorey", "IfcSpace"],
  구역: ["IfcZone", "IfcSpatialZone"]
};

// 관리 요소
const managementElements = {
  프로세스: ["IfcTask", "IfcProcedure", "IfcEvent"],
  자원: ["IfcConstructionResource", "IfcCrewResource", "IfcLaborResource"],
  비용: ["IfcCostItem", "IfcCostSchedule"]
};
```

### C. 에러 코드 및 해결 방법
```typescript
const errorCodes = {
  // 스키마 오류
  SCH001: {
    message: "필수 속성 누락",
    solution: "GlobalId, Name 등 필수 속성 확인"
  },
  SCH002: {
    message: "잘못된 엔티티 타입",
    solution: "IFC 4.3 스키마의 유효한 엔티티 사용"
  },
  
  // 관계 오류
  REL001: {
    message: "순환 참조 감지",
    solution: "관계 체인에서 순환 제거"
  },
  REL002: {
    message: "고아 객체 발견",
    solution: "모든 요소를 적절한 공간 구조에 포함"
  },
  
  // 지오메트리 오류
  GEO001: {
    message: "유효하지 않은 지오메트리",
    solution: "자체 교차, 열린 솔리드 등 확인"
  },
  GEO002: {
    message: "충돌 감지",
    solution: "요소 간 최소 간격 유지"
  }
};
```

---

**본 문서는 ISO 16739-1:2024 및 ISO 19650 표준을 기반으로 작성된 바이브 코딩 BIM 플랫폼의 공식 모델링 가이드라인입니다.**

**지속적인 업데이트와 개선을 통해 업계 최고 수준의 BIM 모델링 품질을 추구합니다.**

---

*© 2025 바이브 코딩 BIM 플랫폼. All rights reserved.*