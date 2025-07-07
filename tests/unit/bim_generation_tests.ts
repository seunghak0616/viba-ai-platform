/**
 * BIM 모델 자동 생성 엔진 단위 테스트
 * 
 * VIBA AI 에이전트의 IFC 모델 생성 및 검증 기능 테스트
 * 
 * @version 1.0
 * @author VIBA AI Team
 * @date 2025.07.06
 */

import { describe, test, expect, beforeAll, beforeEach, afterEach } from '@jest/testing-library/jest-dom';
import { 
  AutoBIMGenerator,
  IFCModelGenerator,
  IfcEntityFactory,
  GeometryGenerator,
  MaterialAssigner,
  PropertySetManager,
  RelationshipManager 
} from '../../src/ai/bim-generation';

import {
  IFCValidator,
  GeometryValidator,
  ModelConsistencyChecker,
  StandardsComplianceValidator
} from '../../src/utils/validation';

import {
  BIMTestData,
  IFCTestSchema,
  MockDesignGuidelines,
  SampleBuildingData
} from '../fixtures/bim-test-data';

// =============================================================================
// 테스트 데이터 및 설정
// =============================================================================

interface BIMGenerationTestCase {
  id: string;
  description: string;
  design_guidelines: any;
  expected_entities: string[];
  expected_relationships: string[];
  validation_criteria: any;
  priority: 'high' | 'medium' | 'low';
}

const bimGenerationTestCases: BIMGenerationTestCase[] = [
  {
    id: 'residential_simple_001',
    description: '단순 주거 건물 BIM 모델 생성',
    design_guidelines: {
      buildingType: '단독주택',
      floors: 2,
      area: 120,
      style: 'modern',
      layout: {
        floor_1: ['거실', '주방', '화장실'],
        floor_2: ['침실', '침실', '화장실']
      },
      structure: 'wood_frame',
      dimensions: {
        floor_height: 2.7,
        wall_thickness: 0.15,
        slab_thickness: 0.2
      }
    },
    expected_entities: [
      'IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey',
      'IfcWall', 'IfcSlab', 'IfcDoor', 'IfcWindow', 'IfcSpace'
    ],
    expected_relationships: [
      'IfcRelAggregates', 'IfcRelContainedInSpatialStructure',
      'IfcRelDefinesByProperties', 'IfcRelAssociatesMaterial'
    ],
    validation_criteria: {
      min_entities: 20,
      ifc_version: '4.3',
      geometry_accuracy: 0.01,
      relationship_completeness: 0.95
    },
    priority: 'high'
  },

  {
    id: 'commercial_complex_001',
    description: '복합 상업 건물 BIM 모델 생성',
    design_guidelines: {
      buildingType: '상업복합시설',
      floors: 5,
      area: 2000,
      style: 'contemporary',
      program: {
        floor_1: ['로비', '상점', '카페'],
        floors_2_3: ['사무실'],
        floors_4_5: ['레스토랑', '컨퍼런스룸']
      },
      structure: 'steel_frame',
      facade: 'curtain_wall',
      dimensions: {
        floor_height: 3.5,
        wall_thickness: 0.25,
        slab_thickness: 0.3
      },
      sustainability: {
        green_roof: true,
        solar_panels: true,
        rainwater_collection: true
      }
    },
    expected_entities: [
      'IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey',
      'IfcWall', 'IfcCurtainWall', 'IfcSlab', 'IfcBeam', 'IfcColumn',
      'IfcDoor', 'IfcWindow', 'IfcSpace', 'IfcDistributionElement'
    ],
    expected_relationships: [
      'IfcRelAggregates', 'IfcRelContainedInSpatialStructure',
      'IfcRelDefinesByProperties', 'IfcRelAssociatesMaterial',
      'IfcRelConnectsElements', 'IfcRelSpaceBoundary'
    ],
    validation_criteria: {
      min_entities: 100,
      ifc_version: '4.3',
      geometry_accuracy: 0.005,
      relationship_completeness: 0.98,
      sustainability_features: 3
    },
    priority: 'high'
  },

  {
    id: 'traditional_hanok_001',
    description: '전통 한옥 스타일 BIM 모델 생성',
    design_guidelines: {
      buildingType: '한옥',
      floors: 1,
      area: 150,
      style: 'traditional_korean',
      features: ['중정', '대청마루', '온돌', '기와지붕'],
      materials: {
        structure: '목조',
        roof: '기와',
        walls: '한지_흙벽',
        floor: '마루_온돌'
      },
      proportions: {
        system: 'traditional_module',
        bay_size: 3.0,
        column_spacing: 3.0
      }
    },
    expected_entities: [
      'IfcProject', 'IfcSite', 'IfcBuilding', 'IfcBuildingStorey',
      'IfcWall', 'IfcSlab', 'IfcRoof', 'IfcColumn', 'IfcBeam',
      'IfcDoor', 'IfcWindow', 'IfcSpace'
    ],
    expected_relationships: [
      'IfcRelAggregates', 'IfcRelContainedInSpatialStructure',
      'IfcRelDefinesByProperties', 'IfcRelAssociatesMaterial',
      'IfcRelDefinesByType'
    ],
    validation_criteria: {
      min_entities: 30,
      ifc_version: '4.3',
      geometry_accuracy: 0.01,
      traditional_features: 4,
      material_authenticity: 0.9
    },
    priority: 'medium'
  }
];

// =============================================================================
// BIM 생성 엔진 단위 테스트
// =============================================================================

describe('BIM Model Generation Engine Tests', () => {
  let bimGenerator: AutoBIMGenerator;
  let ifcGenerator: IFCModelGenerator;
  let entityFactory: IfcEntityFactory;
  let geometryGenerator: GeometryGenerator;
  let materialAssigner: MaterialAssigner;
  let propertyManager: PropertySetManager;
  let relationshipManager: RelationshipManager;
  let validator: IFCValidator;

  beforeAll(async () => {
    // BIM 생성 컴포넌트 초기화
    bimGenerator = new AutoBIMGenerator({
      ifc_version: '4.3.2.0',
      units: 'metric',
      precision: 3,
      validation_enabled: true
    });

    ifcGenerator = new IFCModelGenerator({
      schema_path: '/schemas/IFC4_3.exp',
      templates_path: '/templates/building-types',
      materials_db: '/data/materials-kr.json'
    });

    entityFactory = new IfcEntityFactory({
      guid_generator: 'uuid_v4',
      naming_convention: 'semantic',
      inheritance_validation: true
    });

    geometryGenerator = new GeometryGenerator({
      engine: 'opencascade',
      mesh_quality: 'high',
      boolean_operations: true,
      curve_tolerance: 0.001
    });

    materialAssigner = new MaterialAssigner({
      materials_database: '/data/korean-building-materials.json',
      sustainability_data: '/data/environmental-impact.json',
      cost_data: '/data/material-costs-kr.json'
    });

    propertyManager = new PropertySetManager({
      standard_psets: '/data/psets/IFC4_3-psets.json',
      custom_psets: '/data/psets/korean-building-psets.json',
      validation_rules: '/data/pset-validation-rules.json'
    });

    relationshipManager = new RelationshipManager({
      auto_relationships: true,
      consistency_checking: true,
      circular_reference_detection: true
    });

    validator = new IFCValidator({
      schema_version: '4.3.2.0',
      strict_mode: true,
      custom_rules: '/validation/korean-building-rules.json'
    });

    // 컴포넌트 초기화
    await Promise.all([
      bimGenerator.initialize(),
      ifcGenerator.loadSchema(),
      entityFactory.initialize(),
      geometryGenerator.initialize(),
      materialAssigner.loadDatabase(),
      propertyManager.loadPropertySets(),
      validator.loadSchema()
    ]);

    console.log('✅ BIM 생성 컴포넌트 초기화 완료');
  });

  beforeEach(() => {
    // 각 테스트 전 상태 초기화
    entityFactory.clearCache();
    relationshipManager.clearRelationships();
  });

  afterEach(() => {
    // 테스트 후 정리
    geometryGenerator.clearGeometryCache();
  });

  // =============================================================================
  // IFC 엔티티 생성 테스트
  // =============================================================================

  describe('IFC Entity Creation Tests', () => {
    test('should create valid IFC project structure', async () => {
      const projectInfo = {
        name: '테스트 프로젝트',
        description: 'BIM 생성 엔진 테스트용 프로젝트',
        site_name: '테스트 부지',
        building_name: '테스트 건물'
      };

      // 프로젝트 구조 생성
      const projectStructure = await ifcGenerator.createProjectStructure(projectInfo);

      // 기본 엔티티 존재 확인
      expect(projectStructure.project).toBeDefined();
      expect(projectStructure.site).toBeDefined();
      expect(projectStructure.building).toBeDefined();

      // GUID 유효성 검증
      expect(projectStructure.project.GlobalId).toMatch(/^[0-9A-Za-z_$]{22}$/);
      expect(projectStructure.site.GlobalId).toMatch(/^[0-9A-Za-z_$]{22}$/);
      expect(projectStructure.building.GlobalId).toMatch(/^[0-9A-Za-z_$]{22}$/);

      // 계층 관계 확인
      expect(projectStructure.project.IsDecomposedBy).toContain(projectStructure.site);
      expect(projectStructure.site.IsDecomposedBy).toContain(projectStructure.building);

      console.log('✅ IFC 프로젝트 구조 생성 성공');
    });

    test('should create building storeys correctly', async () => {
      const buildingInfo = {
        floors: 3,
        floor_height: 3.0,
        ground_level: 0.0
      };

      const storeys = await ifcGenerator.createBuildingStoreys(buildingInfo);

      expect(storeys).toHaveLength(3);

      storeys.forEach((storey, index) => {
        expect(storey.entity_type).toBe('IfcBuildingStorey');
        expect(storey.Name).toBe(`${index + 1}층`);
        expect(storey.Elevation).toBe(index * buildingInfo.floor_height);
        expect(storey.GlobalId).toMatch(/^[0-9A-Za-z_$]{22}$/);
      });

      console.log('✅ 건물 층 생성 성공:', storeys.length, '개 층');
    });

    test('should generate walls with proper geometry', async () => {
      const wallParameters = [
        {
          id: 'wall-001',
          start_point: [0, 0, 0],
          end_point: [5, 0, 0],
          height: 3.0,
          thickness: 0.2,
          material: '콘크리트'
        },
        {
          id: 'wall-002',
          start_point: [5, 0, 0],
          end_point: [5, 4, 0],
          height: 3.0,
          thickness: 0.2,
          material: '콘크리트'
        }
      ];

      const walls = await Promise.all(
        wallParameters.map(params => 
          ifcGenerator.createWall(params)
        )
      );

      walls.forEach((wall, index) => {
        expect(wall.entity_type).toBe('IfcWall');
        expect(wall.GlobalId).toMatch(/^[0-9A-Za-z_$]{22}$/);
        expect(wall.Representation).toBeDefined();
        expect(wall.ObjectPlacement).toBeDefined();

        // 기하학적 표현 검증
        const geometry = wall.Representation.Representations[0];
        expect(geometry.RepresentationType).toBe('SweptSolid');
        expect(geometry.Items[0].Depth).toBe(wallParameters[index].thickness);

        // 재료 할당 확인
        expect(wall.HasAssociations).toBeDefined();
        expect(wall.HasAssociations.some((assoc: any) => 
          assoc.entity_type === 'IfcRelAssociatesMaterial'
        )).toBe(true);
      });

      console.log('✅ 벽체 생성 및 기하학적 표현 생성 성공:', walls.length, '개 벽체');
    });

    test('should create doors and windows with host relationships', async () => {
      // 먼저 호스트 벽 생성
      const hostWall = await ifcGenerator.createWall({
        id: 'host-wall-001',
        start_point: [0, 0, 0],
        end_point: [6, 0, 0],
        height: 3.0,
        thickness: 0.2,
        material: '콘크리트'
      });

      // 문 생성
      const door = await ifcGenerator.createDoor({
        id: 'door-001',
        host_wall: hostWall,
        position: [2, 0, 0],
        width: 0.9,
        height: 2.1,
        opening_direction: 'right',
        door_type: 'single_swing'
      });

      // 창문 생성
      const window = await ifcGenerator.createWindow({
        id: 'window-001',
        host_wall: hostWall,
        position: [4, 0, 1],
        width: 1.2,
        height: 1.5,
        sill_height: 1.0,
        window_type: 'casement'
      });

      // 문 검증
      expect(door.entity_type).toBe('IfcDoor');
      expect(door.OverallWidth).toBe(0.9);
      expect(door.OverallHeight).toBe(2.1);

      // 창문 검증
      expect(window.entity_type).toBe('IfcWindow');
      expect(window.OverallWidth).toBe(1.2);
      expect(window.OverallHeight).toBe(1.5);

      // 개구부 관계 확인
      expect(hostWall.HasOpenings).toBeDefined();
      expect(hostWall.HasOpenings.length).toBe(2);

      console.log('✅ 문과 창문 생성 및 호스트 관계 설정 성공');
    });

    test('should create structural elements (beams, columns)', async () => {
      const structuralElements = [
        {
          type: 'column',
          id: 'column-001',
          position: [0, 0, 0],
          height: 3.0,
          cross_section: 'rectangular',
          dimensions: [0.4, 0.4],
          material: '고강도콘크리트'
        },
        {
          type: 'beam',
          id: 'beam-001',
          start_point: [0, 0, 3.0],
          end_point: [5, 0, 3.0],
          cross_section: 'rectangular',
          dimensions: [0.3, 0.6],
          material: '고강도콘크리트'
        }
      ];

      const column = await ifcGenerator.createColumn(structuralElements[0]);
      const beam = await ifcGenerator.createBeam(structuralElements[1]);

      // 기둥 검증
      expect(column.entity_type).toBe('IfcColumn');
      expect(column.ObjectType).toBe('Column');
      expect(column.Representation).toBeDefined();

      // 보 검증
      expect(beam.entity_type).toBe('IfcBeam');
      expect(beam.ObjectType).toBe('Beam');
      expect(beam.Representation).toBeDefined();

      // 구조 요소 연결 관계 확인
      const connection = await relationshipManager.createStructuralConnection(column, beam);
      expect(connection.entity_type).toBe('IfcRelConnectsElements');

      console.log('✅ 구조 요소(기둥, 보) 생성 및 연결 성공');
    });

    test('should generate spaces with boundaries', async () => {
      // 공간을 둘러싸는 벽체들 생성
      const walls = await Promise.all([
        ifcGenerator.createWall({
          id: 'room-wall-1',
          start_point: [0, 0, 0],
          end_point: [4, 0, 0],
          height: 3.0,
          thickness: 0.15
        }),
        ifcGenerator.createWall({
          id: 'room-wall-2',
          start_point: [4, 0, 0],
          end_point: [4, 3, 0],
          height: 3.0,
          thickness: 0.15
        }),
        ifcGenerator.createWall({
          id: 'room-wall-3',
          start_point: [4, 3, 0],
          end_point: [0, 3, 0],
          height: 3.0,
          thickness: 0.15
        }),
        ifcGenerator.createWall({
          id: 'room-wall-4',
          start_point: [0, 3, 0],
          end_point: [0, 0, 0],
          height: 3.0,
          thickness: 0.15
        })
      ]);

      // 공간 생성
      const space = await ifcGenerator.createSpace({
        id: 'space-001',
        name: '거실',
        space_type: 'living_room',
        boundary_walls: walls,
        floor_area: 12.0,
        volume: 36.0
      });

      expect(space.entity_type).toBe('IfcSpace');
      expect(space.Name).toBe('거실');
      expect(space.LongName).toBe('living_room');

      // 공간 경계 관계 확인
      expect(space.BoundedBy).toBeDefined();
      expect(space.BoundedBy.length).toBe(walls.length);

      // 공간 속성 확인
      const areaProperty = space.IsDefinedBy.find((pset: any) => 
        pset.RelatingPropertyDefinition.Name === 'Pset_SpaceCommon'
      );
      expect(areaProperty).toBeDefined();

      console.log('✅ 공간 생성 및 경계 설정 성공:', space.Name);
    });
  });

  // =============================================================================
  // 기하학적 표현 생성 테스트
  // =============================================================================

  describe('Geometry Generation Tests', () => {
    test('should generate accurate swept solid geometry', async () => {
      const profileData = {
        type: 'rectangle',
        width: 5.0,
        height: 0.2
      };

      const extrusionData = {
        direction: [0, 0, 1],
        depth: 3.0
      };

      const sweptSolid = await geometryGenerator.createSweptSolid(
        profileData,
        extrusionData
      );

      expect(sweptSolid.entity_type).toBe('IfcExtrudedAreaSolid');
      expect(sweptSolid.Depth).toBe(3.0);
      expect(sweptSolid.SweptArea.XDim).toBe(5.0);
      expect(sweptSolid.SweptArea.YDim).toBe(0.2);

      // 기하학적 정확도 검증
      const volume = await geometryGenerator.calculateVolume(sweptSolid);
      const expectedVolume = 5.0 * 0.2 * 3.0;
      expect(Math.abs(volume - expectedVolume)).toBeLessThan(0.001);

      console.log('✅ Swept Solid 기하학적 표현 생성 성공');
    });

    test('should create complex roof geometry', async () => {
      const roofParameters = {
        type: 'gabled',
        footprint: [
          [0, 0, 3.0],
          [10, 0, 3.0],
          [10, 8, 3.0],
          [0, 8, 3.0]
        ],
        ridge_height: 2.0,
        overhang: 0.5
      };

      const roofGeometry = await geometryGenerator.createRoofGeometry(roofParameters);

      expect(roofGeometry.entity_type).toBe('IfcFacetedBrep');
      expect(roofGeometry.Outer.CfsFaces.length).toBeGreaterThan(4); // 최소 지붕면 + 처마

      // 지붕 표면적 계산 검증
      const surfaceArea = await geometryGenerator.calculateSurfaceArea(roofGeometry);
      expect(surfaceArea).toBeGreaterThan(80); // 기본 면적보다 큰지 확인

      console.log('✅ 복잡한 지붕 기하학적 표현 생성 성공');
    });

    test('should perform boolean operations correctly', async () => {
      // 기본 벽체 생성
      const wallGeometry = await geometryGenerator.createSweptSolid(
        { type: 'rectangle', width: 0.2, height: 3.0 },
        { direction: [1, 0, 0], depth: 5.0 }
      );

      // 문 개구부 생성
      const doorOpening = await geometryGenerator.createSweptSolid(
        { type: 'rectangle', width: 0.3, height: 2.1 }, // 벽보다 두꺼운 개구부
        { direction: [1, 0, 0], depth: 0.9 }
      );

      // Boolean 차집합 연산
      const wallWithOpening = await geometryGenerator.performBooleanDifference(
        wallGeometry,
        doorOpening
      );

      expect(wallWithOpening).toBeDefined();

      // 결과 볼륨 검증
      const originalVolume = await geometryGenerator.calculateVolume(wallGeometry);
      const openingVolume = await geometryGenerator.calculateVolume(doorOpening);
      const resultVolume = await geometryGenerator.calculateVolume(wallWithOpening);

      expect(Math.abs(resultVolume - (originalVolume - openingVolume))).toBeLessThan(0.001);

      console.log('✅ Boolean 연산(차집합) 정확도 검증 성공');
    });

    test('should validate geometry consistency', async () => {
      const testGeometries = [
        await geometryGenerator.createSweptSolid(
          { type: 'rectangle', width: 2.0, height: 0.2 },
          { direction: [0, 0, 1], depth: 3.0 }
        ),
        await geometryGenerator.createSweptSolid(
          { type: 'circle', radius: 1.0 },
          { direction: [0, 0, 1], depth: 2.0 }
        )
      ];

      for (const geometry of testGeometries) {
        const validation = await geometryGenerator.validateGeometry(geometry);

        expect(validation.is_valid).toBe(true);
        expect(validation.is_manifold).toBe(true);
        expect(validation.is_closed).toBe(true);
        expect(validation.has_self_intersections).toBe(false);
        expect(validation.volume).toBeGreaterThan(0);
      }

      console.log('✅ 기하학적 일관성 검증 성공');
    });
  });

  // =============================================================================
  // 재료 및 속성 할당 테스트
  // =============================================================================

  describe('Material and Property Assignment Tests', () => {
    test('should assign materials correctly', async () => {
      const materialSpecs = [
        {
          element_type: 'wall',
          material_name: '콘크리트',
          properties: {
            compressive_strength: 25, // MPa
            density: 2400, // kg/m³
            thermal_conductivity: 1.75 // W/mK
          }
        },
        {
          element_type: 'slab',
          material_name: '철근콘크리트',
          properties: {
            compressive_strength: 30,
            density: 2500,
            thermal_conductivity: 2.3
          }
        }
      ];

      for (const spec of materialSpecs) {
        const material = await materialAssigner.createMaterial(spec);

        expect(material.entity_type).toBe('IfcMaterial');
        expect(material.Name).toBe(spec.material_name);

        // 재료 속성 확인
        const properties = await materialAssigner.getMaterialProperties(material);
        expect(properties.compressive_strength).toBe(spec.properties.compressive_strength);
        expect(properties.density).toBe(spec.properties.density);
        expect(properties.thermal_conductivity).toBe(spec.properties.thermal_conductivity);

        // 지속가능성 데이터 확인
        const sustainabilityData = await materialAssigner.getSustainabilityData(material);
        expect(sustainabilityData).toHaveProperty('carbon_footprint');
        expect(sustainabilityData).toHaveProperty('recyclability');
      }

      console.log('✅ 재료 할당 및 속성 설정 성공');
    });

    test('should create layered materials for walls', async () => {
      const layerSpec = {
        layers: [
          { material: '외부마감석', thickness: 0.03, function: 'finish' },
          { material: '단열재', thickness: 0.10, function: 'insulation' },
          { material: '콘크리트', thickness: 0.15, function: 'structure' },
          { material: '내부마감재', thickness: 0.02, function: 'finish' }
        ],
        total_thickness: 0.30
      };

      const layeredMaterial = await materialAssigner.createMaterialLayerSet(layerSpec);

      expect(layeredMaterial.entity_type).toBe('IfcMaterialLayerSet');
      expect(layeredMaterial.MaterialLayers.length).toBe(4);

      // 층별 두께 검증
      let totalThickness = 0;
      layeredMaterial.MaterialLayers.forEach((layer: any, index: number) => {
        expect(layer.LayerThickness).toBe(layerSpec.layers[index].thickness);
        totalThickness += layer.LayerThickness;
      });

      expect(Math.abs(totalThickness - layerSpec.total_thickness)).toBeLessThan(0.001);

      // 열전달 계산 검증
      const thermalProperties = await materialAssigner.calculateThermalProperties(layeredMaterial);
      expect(thermalProperties.u_value).toBeDefined();
      expect(thermalProperties.thermal_mass).toBeDefined();

      console.log('✅ 다층 재료 시스템 생성 및 열성능 계산 성공');
    });

    test('should assign property sets correctly', async () => {
      // 테스트용 벽체 생성
      const wall = await ifcGenerator.createWall({
        id: 'test-wall-pset',
        start_point: [0, 0, 0],
        end_point: [5, 0, 0],
        height: 3.0,
        thickness: 0.2
      });

      // 표준 속성 세트 할당
      const psetCommon = await propertyManager.assignPropertySet(wall, 'Pset_WallCommon', {
        'LoadBearing': true,
        'IsExternal': true,
        'FireRating': 'F60',
        'ThermalTransmittance': 0.35
      });

      // 커스텀 속성 세트 할당
      const psetKorean = await propertyManager.assignPropertySet(wall, 'Pset_WallKorean', {
        'BuildingCode': '건축법',
        'FireResistance': '준불연',
        'SeismicDesign': true,
        'KSStandard': 'KS F 4002'
      });

      // 속성 세트 할당 확인
      expect(wall.IsDefinedBy).toBeDefined();
      expect(wall.IsDefinedBy.length).toBeGreaterThanOrEqual(2);

      // 속성 값 검증
      const commonPset = wall.IsDefinedBy.find((rel: any) => 
        rel.RelatingPropertyDefinition.Name === 'Pset_WallCommon'
      );
      expect(commonPset).toBeDefined();

      const koreanPset = wall.IsDefinedBy.find((rel: any) => 
        rel.RelatingPropertyDefinition.Name === 'Pset_WallKorean'
      );
      expect(koreanPset).toBeDefined();

      console.log('✅ 속성 세트 할당 및 검증 성공');
    });

    test('should calculate quantities automatically', async () => {
      const building = await bimGenerator.generateBIMModel({
        buildingType: '소규모 사무소',
        floors: 3,
        floor_area: 200,
        wall_thickness: 0.2,
        floor_height: 3.0
      });

      // 자동 수량 산출
      const quantities = await propertyManager.calculateQuantities(building);

      // 기본 수량 검증
      expect(quantities.walls).toHaveProperty('area');
      expect(quantities.walls).toHaveProperty('volume');
      expect(quantities.walls).toHaveProperty('length');

      expect(quantities.slabs).toHaveProperty('area');
      expect(quantities.slabs).toHaveProperty('volume');
      expect(quantities.slabs).toHaveProperty('thickness');

      expect(quantities.spaces).toHaveProperty('floor_area');
      expect(quantities.spaces).toHaveProperty('volume');
      expect(quantities.spaces).toHaveProperty('perimeter');

      // 수량 값 합리성 검증
      expect(quantities.walls.area).toBeGreaterThan(0);
      expect(quantities.slabs.area).toBeCloseTo(200 * 3, 50); // 3층 x 200㎡ ± 50㎡
      expect(quantities.spaces.floor_area).toBeCloseTo(600, 100); // 총 연면적

      console.log('✅ 자동 수량 산출 성공:', quantities);
    });
  });

  // =============================================================================
  // 관계 및 연결성 테스트
  // =============================================================================

  describe('Relationship and Connectivity Tests', () => {
    test('should establish spatial containment relationships', async () => {
      // 계층 구조 생성
      const project = await ifcGenerator.createProject({ name: '테스트 프로젝트' });
      const site = await ifcGenerator.createSite({ name: '테스트 부지' });
      const building = await ifcGenerator.createBuilding({ name: '테스트 건물' });
      const storey = await ifcGenerator.createBuildingStorey({ name: '1층', elevation: 0.0 });
      const wall = await ifcGenerator.createWall({
        id: 'containment-test-wall',
        start_point: [0, 0, 0],
        end_point: [5, 0, 0],
        height: 3.0,
        thickness: 0.2
      });

      // 관계 설정
      const relationships = await relationshipManager.establishSpatialContainment([
        { parent: project, child: site },
        { parent: site, child: building },
        { parent: building, child: storey },
        { parent: storey, child: wall }
      ]);

      // 관계 검증
      expect(relationships.length).toBe(4);
      relationships.forEach(rel => {
        expect(rel.entity_type).toBe('IfcRelAggregates');
        expect(rel.RelatingObject).toBeDefined();
        expect(rel.RelatedObjects).toBeDefined();
      });

      // 계층 구조 무결성 검증
      const hierarchy = await relationshipManager.getHierarchy(project);
      expect(hierarchy.children).toContain(site);
      expect(hierarchy.children[0].children).toContain(building);
      expect(hierarchy.children[0].children[0].children).toContain(storey);

      console.log('✅ 공간 포함 관계 설정 및 검증 성공');
    });

    test('should create element connections correctly', async () => {
      // 연결할 구조 요소들 생성
      const column = await ifcGenerator.createColumn({
        id: 'connection-column',
        position: [0, 0, 0],
        height: 3.0,
        cross_section: 'rectangular',
        dimensions: [0.4, 0.4]
      });

      const beam = await ifcGenerator.createBeam({
        id: 'connection-beam',
        start_point: [0, 0, 3.0],
        end_point: [5, 0, 3.0],
        cross_section: 'rectangular',
        dimensions: [0.3, 0.6]
      });

      const wall = await ifcGenerator.createWall({
        id: 'connection-wall',
        start_point: [0, 0, 0],
        end_point: [5, 0, 0],
        height: 3.0,
        thickness: 0.2
      });

      // 연결 관계 생성
      const connections = await Promise.all([
        relationshipManager.createElementConnection(column, beam, 'rigid'),
        relationshipManager.createElementConnection(beam, wall, 'support'),
        relationshipManager.createElementConnection(wall, column, 'attachment')
      ]);

      // 연결 관계 검증
      connections.forEach(connection => {
        expect(connection.entity_type).toBe('IfcRelConnectsElements');
        expect(connection.RelatingElement).toBeDefined();
        expect(connection.RelatedElement).toBeDefined();
        expect(connection.ConnectionGeometry).toBeDefined();
      });

      // 연결 그래프 완전성 검증
      const connectionGraph = await relationshipManager.buildConnectionGraph([column, beam, wall]);
      expect(connectionGraph.nodes.length).toBe(3);
      expect(connectionGraph.edges.length).toBe(3);

      console.log('✅ 요소 간 연결 관계 생성 및 검증 성공');
    });

    test('should handle space boundary relationships', async () => {
      // 공간과 경계 요소들 생성
      const space = await ifcGenerator.createSpace({
        id: 'boundary-test-space',
        name: '테스트 룸',
        space_type: 'office'
      });

      const boundaryWalls = await Promise.all([
        ifcGenerator.createWall({
          id: 'boundary-wall-1',
          start_point: [0, 0, 0],
          end_point: [4, 0, 0],
          height: 3.0,
          thickness: 0.15
        }),
        ifcGenerator.createWall({
          id: 'boundary-wall-2', 
          start_point: [4, 0, 0],
          end_point: [4, 3, 0],
          height: 3.0,
          thickness: 0.15
        })
      ]);

      const floor = await ifcGenerator.createSlab({
        id: 'boundary-floor',
        perimeter: [[0, 0, 0], [4, 0, 0], [4, 3, 0], [0, 3, 0]],
        thickness: 0.2,
        slab_type: 'floor'
      });

      // 공간 경계 관계 설정
      const spaceBoundaries = await relationshipManager.createSpaceBoundaries(
        space,
        [...boundaryWalls, floor]
      );

      // 경계 관계 검증
      expect(spaceBoundaries.length).toBe(3); // 2개 벽 + 1개 바닥
      spaceBoundaries.forEach(boundary => {
        expect(boundary.entity_type).toBe('IfcRelSpaceBoundary');
        expect(boundary.RelatingSpace).toBe(space);
        expect(boundary.RelatedBuildingElement).toBeDefined();
        expect(boundary.PhysicalOrVirtualBoundary).toBe('PHYSICAL');
      });

      // 공간 형상 자동 계산 검증
      const spaceGeometry = await geometryGenerator.calculateSpaceGeometry(space, spaceBoundaries);
      expect(spaceGeometry.floor_area).toBeCloseTo(12.0, 0.1);
      expect(spaceGeometry.volume).toBeCloseTo(36.0, 0.5);

      console.log('✅ 공간 경계 관계 설정 및 형상 계산 성공');
    });

    test('should detect and prevent circular references', async () => {
      // 순환 참조를 유발할 수 있는 요소들 생성
      const elementA = await ifcGenerator.createWall({
        id: 'circular-test-a',
        start_point: [0, 0, 0],
        end_point: [5, 0, 0],
        height: 3.0,
        thickness: 0.2
      });

      const elementB = await ifcGenerator.createWall({
        id: 'circular-test-b',
        start_point: [5, 0, 0],
        end_point: [5, 4, 0],
        height: 3.0,
        thickness: 0.2
      });

      // 정상적인 관계 설정
      const validRelation = await relationshipManager.createRelationship(
        elementA, elementB, 'IfcRelConnectsElements'
      );
      expect(validRelation).toBeDefined();

      // 순환 참조 시도 (A -> B -> A)
      const circularAttempt = relationshipManager.createRelationship(
        elementB, elementA, 'IfcRelConnectsElements'
      );

      // 순환 참조 감지 및 방지 확인
      await expect(circularAttempt).rejects.toThrow('Circular reference detected');

      // 관계 그래프 유효성 확인
      const isAcyclic = await relationshipManager.validateAcyclicity();
      expect(isAcyclic).toBe(true);

      console.log('✅ 순환 참조 감지 및 방지 성공');
    });
  });

  // =============================================================================
  // 전체 모델 생성 테스트
  // =============================================================================

  describe('Complete Model Generation Tests', () => {
    test.each(bimGenerationTestCases.filter(tc => tc.priority === 'high'))(
      'should generate complete BIM model for $description',
      async (testCase) => {
        // 전체 BIM 모델 생성
        const startTime = Date.now();
        const bimModel = await bimGenerator.generateBIMModel(testCase.design_guidelines);
        const generationTime = Date.now() - startTime;

        // 기본 모델 구조 검증
        expect(bimModel).toBeDefined();
        expect(bimModel.project).toBeDefined();
        expect(bimModel.entities).toBeDefined();
        expect(bimModel.relationships).toBeDefined();

        // 예상 엔티티 존재 확인
        testCase.expected_entities.forEach(entityType => {
          const entitiesOfType = bimModel.entities.filter((e: any) => e.entity_type === entityType);
          expect(entitiesOfType.length).toBeGreaterThan(0);
        });

        // 예상 관계 존재 확인
        testCase.expected_relationships.forEach(relType => {
          const relationshipsOfType = bimModel.relationships.filter((r: any) => r.entity_type === relType);
          expect(relationshipsOfType.length).toBeGreaterThan(0);
        });

        // 최소 엔티티 수 확인
        expect(bimModel.entities.length).toBeGreaterThanOrEqual(testCase.validation_criteria.min_entities);

        // IFC 표준 준수 검증
        const ifcValidation = await validator.validateModel(bimModel);
        expect(ifcValidation.is_valid).toBe(true);
        expect(ifcValidation.ifc_version).toBe(testCase.validation_criteria.ifc_version);

        // 기하학적 정확도 검증
        const geometryValidation = await validator.validateGeometry(bimModel);
        expect(geometryValidation.accuracy_score).toBeGreaterThanOrEqual(
          testCase.validation_criteria.geometry_accuracy
        );

        // 관계 완전성 검증
        const relationshipCompleteness = await validator.validateRelationships(bimModel);
        expect(relationshipCompleteness.completeness_score).toBeGreaterThanOrEqual(
          testCase.validation_criteria.relationship_completeness
        );

        // 성능 검증 (5초 이내 생성)
        expect(generationTime).toBeLessThan(5000);

        console.log(`✅ ${testCase.description} 완료 - 생성시간: ${generationTime}ms, 엔티티: ${bimModel.entities.length}개`);
      }
    );

    test('should handle complex architectural programs', async () => {
      const complexProgram = {
        buildingType: '복합문화시설',
        floors: 4,
        area: 3000,
        program: {
          floor_1: {
            spaces: ['로비', '카페', '전시장', '상점'],
            ceiling_height: 4.5
          },
          floor_2: {
            spaces: ['도서관', '열람실', '사무실'],
            ceiling_height: 3.5
          },
          floor_3: {
            spaces: ['강의실', '세미나실', '회의실'],
            ceiling_height: 3.2
          },
          floor_4: {
            spaces: ['공연장', '리허설실', '음향실'],
            ceiling_height: 6.0
          }
        },
        special_requirements: {
          accessibility: true,
          fire_safety: 'enhanced',
          acoustic_design: true,
          sustainability: 'LEED_Gold'
        }
      };

      const complexModel = await bimGenerator.generateBIMModel(complexProgram);

      // 복잡한 프로그램 구현 검증
      expect(complexModel.entities.filter((e: any) => e.entity_type === 'IfcSpace').length).toBeGreaterThanOrEqual(12);
      expect(complexModel.entities.filter((e: any) => e.entity_type === 'IfcBuildingStorey').length).toBe(4);

      // 특수 요구사항 구현 검증
      const accessibilityElements = complexModel.entities.filter((e: any) => 
        e.entity_type === 'IfcRamp' || 
        (e.entity_type === 'IfcDoor' && e.OverallWidth >= 1.0)
      );
      expect(accessibilityElements.length).toBeGreaterThan(0);

      // 지속가능성 요소 확인
      const sustainabilityElements = complexModel.entities.filter((e: any) => 
        e.ObjectType && (
          e.ObjectType.includes('Solar') ||
          e.ObjectType.includes('Green') ||
          e.ObjectType.includes('Efficient')
        )
      );
      expect(sustainabilityElements.length).toBeGreaterThan(0);

      console.log('✅ 복잡한 건축 프로그램 BIM 모델 생성 성공');
    });

    test('should export to standard file formats', async () => {
      const simpleModel = await bimGenerator.generateBIMModel({
        buildingType: '단독주택',
        floors: 2,
        area: 150
      });

      // IFC 파일 내보내기
      const ifcFile = await bimGenerator.exportToIFC(simpleModel, {
        version: '4.3',
        units: 'metric',
        precision: 3
      });

      expect(ifcFile).toBeDefined();
      expect(ifcFile.content).toContain('ISO-10303-21');
      expect(ifcFile.content).toContain('FILE_DESCRIPTION');
      expect(ifcFile.content).toContain('ENDSEC');

      // glTF 내보내기 (시각화용)
      const gltfFile = await bimGenerator.exportToGLTF(simpleModel, {
        include_materials: true,
        optimize_meshes: true,
        texture_size: 1024
      });

      expect(gltfFile).toBeDefined();
      expect(gltfFile.scenes).toBeDefined();
      expect(gltfFile.meshes.length).toBeGreaterThan(0);

      console.log('✅ 표준 파일 형식 내보내기 성공 (IFC, glTF)');
    });
  });

  // =============================================================================
  // 성능 및 품질 테스트
  // =============================================================================

  describe('Performance and Quality Tests', () => {
    test('should generate models within acceptable time limits', async () => {
      const performanceTests = [
        { complexity: 'simple', entities: 50, timeLimit: 1000 },
        { complexity: 'medium', entities: 200, timeLimit: 3000 },
        { complexity: 'complex', entities: 500, timeLimit: 8000 }
      ];

      for (const test of performanceTests) {
        const guidelines = BIMTestData.createComplexityBasedGuidelines(test.complexity);
        
        const startTime = Date.now();
        const model = await bimGenerator.generateBIMModel(guidelines);
        const endTime = Date.now();

        expect(endTime - startTime).toBeLessThan(test.timeLimit);
        expect(model.entities.length).toBeGreaterThanOrEqual(test.entities);

        console.log(`✅ ${test.complexity} 모델 생성 성능: ${endTime - startTime}ms`);
      }
    });

    test('should maintain memory efficiency during generation', async () => {
      const initialMemory = process.memoryUsage();

      // 대용량 모델 생성
      const largeModel = await bimGenerator.generateBIMModel({
        buildingType: '대형복합시설',
        floors: 20,
        area: 10000,
        detailed_modeling: true
      });

      const finalMemory = process.memoryUsage();
      const memoryIncrease = finalMemory.heapUsed - initialMemory.heapUsed;

      // 메모리 사용량이 500MB를 넘지 않아야 함
      expect(memoryIncrease).toBeLessThan(500 * 1024 * 1024);

      // 생성된 모델이 유효해야 함
      expect(largeModel.entities.length).toBeGreaterThan(1000);

      console.log(`✅ 메모리 효율성 검증: ${Math.round(memoryIncrease / 1024 / 1024)}MB 증가`);
    });

    test('should validate model quality consistently', async () => {
      const qualityTests = Array.from({ length: 10 }, (_, i) => ({
        id: `quality-test-${i}`,
        guidelines: BIMTestData.createRandomGuidelines()
      }));

      const qualityScores = [];

      for (const test of qualityTests) {
        const model = await bimGenerator.generateBIMModel(test.guidelines);
        const quality = await validator.assessModelQuality(model);
        
        qualityScores.push(quality.overall_score);
        
        // 기본 품질 기준 충족
        expect(quality.overall_score).toBeGreaterThan(0.8);
        expect(quality.geometry_quality).toBeGreaterThan(0.9);
        expect(quality.relationship_quality).toBeGreaterThan(0.85);
      }

      // 품질 일관성 검증 (표준편차가 0.1 이하)
      const avgScore = qualityScores.reduce((a, b) => a + b, 0) / qualityScores.length;
      const stdDev = Math.sqrt(
        qualityScores.map(score => Math.pow(score - avgScore, 2))
          .reduce((a, b) => a + b, 0) / qualityScores.length
      );

      expect(stdDev).toBeLessThan(0.1);

      console.log(`✅ 모델 품질 일관성 검증: 평균 ${avgScore.toFixed(3)}, 표준편차 ${stdDev.toFixed(3)}`);
    });
  });
});