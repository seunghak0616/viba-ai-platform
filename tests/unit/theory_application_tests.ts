/**
 * 건축이론 적용 정확도 평가 테스트
 * 
 * VIBA AI 에이전트의 건축설계이론 적용 능력 및 정확도 검증
 * 
 * @version 1.0
 * @author VIBA AI Team
 * @date 2025.07.06
 */

import { describe, test, expect, beforeAll, beforeEach } from '@jest/testing-library/jest-dom';
import { 
  ArchitecturalTheoryEngine,
  DesignPrincipleApplicator,
  SpacePlanningTheory,
  ProportionSystemCalculator,
  StyleAnalyzer,
  CompositionAnalyzer,
  ContextualDesignEngine,
  TheoryValidationEngine 
} from '../../src/ai/architectural-theory';

import {
  HistoricalStyleDatabase,
  DesignPatternLibrary,
  ProportionSystemsDB,
  CulturalContextAnalyzer,
  ArchitecturalCriticsEngine
} from '../../src/ai/architectural-theory/knowledge-base';

import {
  TheoryTestCases,
  HistoricalReferenceProjects,
  StyleClassificationData,
  ProportionValidationCases,
  CompositionAnalysisData
} from '../fixtures/theory-test-data';

// =============================================================================
// 테스트 데이터 및 설정
// =============================================================================

interface ArchitecturalTheoryTestCase {
  id: string;
  description: string;
  theory_domain: string;
  design_input: any;
  expected_application: any;
  validation_criteria: any;
  historical_references: string[];
  accuracy_threshold: number;
  priority: 'high' | 'medium' | 'low';
}

const theoryTestCases: ArchitecturalTheoryTestCase[] = [
  {
    id: 'proportion_golden_ratio_001',
    description: '황금비 적용 정확도 검증',
    theory_domain: 'proportional_systems',
    design_input: {
      building_type: 'cultural_center',
      facade_width: 60,
      facade_height: 20,
      elements: ['columns', 'windows', 'entrance'],
      style_preference: 'classical'
    },
    expected_application: {
      primary_ratio: 1.618,
      secondary_ratios: [1.272, 2.618], // φ² and φ + 1
      element_proportions: {
        column_spacing: 3.708, // 60/φ⁴
        window_ratio: 1.618,
        entrance_height: 3.236 // 20/φ²
      },
      harmony_score: 0.95
    },
    validation_criteria: {
      ratio_accuracy: 0.02, // 2% 허용 오차
      element_consistency: 0.9,
      overall_harmony: 0.9,
      classical_authenticity: 0.85
    },
    historical_references: ['Parthenon', 'Pantheon', 'Villa_Rotonda'],
    accuracy_threshold: 0.9,
    priority: 'high'
  },

  {
    id: 'korean_traditional_002',
    description: '한국 전통 건축 이론 적용',
    theory_domain: 'traditional_korean',
    design_input: {
      building_type: 'hanok_guesthouse',
      site_characteristics: {
        orientation: 'south_facing',
        slope: 'gentle_south',
        water_feature: 'nearby_stream'
      },
      functional_requirements: ['main_hall', 'guest_rooms', 'courtyard', 'kitchen'],
      target_authenticity: 'high'
    },
    expected_application: {
      spatial_organization: {
        type: 'ㅁ자형_배치',
        courtyard_central: true,
        hierarchy: ['대청마루', '안채', '사랑채', '부속채']
      },
      proportional_system: {
        module_size: '한자', // 약 3.03m
        bay_system: '칸', // 기둥 간격
        roof_proportions: '삼분법'
      },
      material_application: {
        structure: '목조가구법',
        roof: '기와지붕',
        walls: '한지발호흙벽',
        floor: '온돌_마루'
      },
      feng_shui_compliance: 0.9
    },
    validation_criteria: {
      spatial_authenticity: 0.95,
      proportional_accuracy: 0.9,
      material_appropriateness: 0.9,
      cultural_sensitivity: 0.95
    },
    historical_references: ['경복궁_근정전', '창덕궁_인정전', '양동마을_향단'],
    accuracy_threshold: 0.9,
    priority: 'high'
  },

  {
    id: 'modernist_principles_003',
    description: '모더니즘 설계 원칙 적용',
    theory_domain: 'modernism',
    design_input: {
      building_type: 'residential_complex',
      functional_program: {
        units: 50,
        common_spaces: ['lobby', 'gym', 'rooftop_garden'],
        parking: 'underground'
      },
      site_constraints: {
        urban_density: 'high',
        sunlight_access: 'limited_south',
        noise_levels: 'moderate'
      },
      design_philosophy: 'form_follows_function'
    },
    expected_application: {
      formal_principles: {
        geometric_purity: 0.9,
        ornament_elimination: 0.95,
        volume_expression: 'clear_articulation',
        material_honesty: 0.9
      },
      spatial_concepts: {
        open_plan: 0.8,
        flowing_spaces: 0.85,
        natural_light_optimization: 0.9,
        indoor_outdoor_connection: 0.7
      },
      technological_integration: {
        structural_expression: 0.85,
        mechanical_systems_visibility: 0.6,
        material_efficiency: 0.9
      }
    },
    validation_criteria: {
      functional_clarity: 0.9,
      formal_consistency: 0.85,
      material_authenticity: 0.8,
      modernist_orthodoxy: 0.85
    },
    historical_references: ['Villa_Savoye', 'Farnsworth_House', 'Seagram_Building'],
    accuracy_threshold: 0.85,
    priority: 'high'
  },

  {
    id: 'sustainable_design_004',
    description: '지속가능 설계 이론 적용',
    theory_domain: 'sustainability',
    design_input: {
      building_type: 'office_complex',
      climate_zone: 'temperate_continental',
      sustainability_targets: {
        energy_rating: 'net_zero',
        material_impact: 'low_carbon',
        water_management: 'regenerative',
        biodiversity: 'habitat_creation'
      },
      certification_goals: ['LEED_Platinum', 'Living_Building']
    },
    expected_application: {
      passive_design_strategies: {
        solar_orientation: 'optimized',
        natural_ventilation: 0.8,
        daylight_harvesting: 0.9,
        thermal_mass_utilization: 0.85
      },
      renewable_systems: {
        solar_pv_coverage: 0.7,
        geothermal_integration: 0.6,
        rainwater_harvesting: 0.9,
        greywater_recycling: 0.8
      },
      material_strategies: {
        embodied_carbon_reduction: 0.5,
        local_material_ratio: 0.8,
        recycled_content: 0.6,
        lifecycle_optimization: 0.85
      },
      ecosystem_integration: {
        biodiversity_net_gain: 0.3,
        habitat_corridor_creation: 0.7,
        stormwater_management: 0.9
      }
    },
    validation_criteria: {
      energy_performance: 0.95,
      environmental_impact: 0.9,
      resource_efficiency: 0.85,
      ecosystem_benefit: 0.8
    },
    historical_references: ['BioMilano', 'Bullitt_Center', 'ACROS_Fukuoka'],
    accuracy_threshold: 0.85,
    priority: 'high'
  },

  {
    id: 'contextual_urbanism_005',
    description: '맥락적 도시설계 이론 적용',
    theory_domain: 'contextual_design',
    design_input: {
      project_type: 'mixed_use_development',
      urban_context: {
        neighborhood_character: 'historic_preservation_district',
        building_heights: [2, 3, 4], // 층수 분포
        street_patterns: 'grid_with_diagonals',
        green_space_ratio: 0.15
      },
      community_needs: {
        affordable_housing: 0.3,
        local_retail: 0.2,
        public_space: 0.15,
        workspace: 0.35
      }
    },
    expected_application: {
      urban_fabric_integration: {
        height_transition: 'gradual_stepping',
        material_palette_compatibility: 0.85,
        architectural_language_harmony: 0.8,
        street_wall_continuity: 0.9
      },
      public_space_design: {
        pedestrian_connectivity: 0.9,
        community_gathering_spaces: 3,
        green_infrastructure: 0.8,
        accessibility_compliance: 1.0
      },
      cultural_responsiveness: {
        local_identity_expression: 0.85,
        community_input_integration: 0.8,
        historic_reference_appropriateness: 0.9
      }
    },
    validation_criteria: {
      contextual_sensitivity: 0.9,
      community_benefit: 0.85,
      urban_design_quality: 0.85,
      cultural_appropriateness: 0.9
    },
    historical_references: ['Battery_Park_City', 'Seaside_Florida', 'Hammarby_Sjostad'],
    accuracy_threshold: 0.85,
    priority: 'medium'
  }
];

// =============================================================================
// 건축이론 적용 정확도 평가 테스트
// =============================================================================

describe('Architectural Theory Application Tests', () => {
  let theoryEngine: ArchitecturalTheoryEngine;
  let principleApplicator: DesignPrincipleApplicator;
  let spacePlanningTheory: SpacePlanningTheory;
  let proportionCalculator: ProportionSystemCalculator;
  let styleAnalyzer: StyleAnalyzer;
  let compositionAnalyzer: CompositionAnalyzer;
  let contextualEngine: ContextualDesignEngine;
  let validationEngine: TheoryValidationEngine;

  beforeAll(async () => {
    // 건축이론 엔진 초기화
    theoryEngine = new ArchitecturalTheoryEngine({
      knowledge_depth: 'comprehensive',
      cultural_domains: ['western', 'korean', 'japanese', 'islamic'],
      historical_periods: ['classical', 'medieval', 'renaissance', 'modern', 'contemporary'],
      theoretical_frameworks: ['formalist', 'functionalist', 'phenomenological', 'sustainable']
    });

    principleApplicator = new DesignPrincipleApplicator({
      principle_types: ['proportion', 'scale', 'rhythm', 'balance', 'unity', 'contrast'],
      application_precision: 'high',
      cultural_adaptation: true,
      modern_interpretation: true
    });

    spacePlanningTheory = new SpacePlanningTheory({
      planning_methodologies: ['alexander_pattern', 'hillier_space_syntax', 'lynch_imageability'],
      circulation_analysis: 'advanced',
      spatial_hierarchy: true,
      functional_zoning: 'flexible'
    });

    proportionCalculator = new ProportionSystemCalculator({
      systems: ['golden_ratio', 'modular', 'anthropometric', 'musical', 'traditional_korean'],
      precision_level: 'high',
      validation_methods: ['mathematical', 'perceptual', 'historical'],
      cultural_variants: true
    });

    styleAnalyzer = new StyleAnalyzer({
      style_database: 'comprehensive',
      analysis_depth: 'deep',
      cultural_sensitivity: 'high',
      contemporary_interpretation: true
    });

    compositionAnalyzer = new CompositionAnalyzer({
      analysis_methods: ['gestalt', 'classical', 'modern'],
      visual_perception: 'advanced',
      spatial_composition: true,
      material_composition: true
    });

    contextualEngine = new ContextualDesignEngine({
      context_analysis: 'multi_layered',
      cultural_interpretation: 'sensitive',
      environmental_integration: 'holistic',
      community_engagement: 'participatory'
    });

    validationEngine = new TheoryValidationEngine({
      validation_methods: ['expert_evaluation', 'historical_comparison', 'user_perception'],
      accuracy_metrics: 'comprehensive',
      cultural_competence: 'high'
    });

    // 지식 베이스 로딩
    await Promise.all([
      theoryEngine.loadKnowledgeBase(),
      principleApplicator.loadDesignPrinciples(),
      spacePlanningTheory.loadPlanningTheories(),
      proportionCalculator.loadProportionSystems(),
      styleAnalyzer.loadStyleDatabase(),
      compositionAnalyzer.loadCompositionRules(),
      contextualEngine.loadContextualFrameworks(),
      validationEngine.loadValidationCriteria()
    ]);

    console.log('✅ 건축이론 엔진 초기화 완료');
  });

  beforeEach(() => {
    // 각 테스트 전 상태 초기화
    theoryEngine.clearAnalysisCache();
    validationEngine.resetValidationState();
  });

  // =============================================================================
  // 비례 시스템 적용 테스트
  // =============================================================================

  describe('Proportional Systems Application', () => {
    test('should apply golden ratio correctly', async () => {
      const testCase = theoryTestCases.find(tc => tc.id === 'proportion_golden_ratio_001')!;
      
      const proportionApplication = await proportionCalculator.applyGoldenRatio(
        testCase.design_input
      );

      // 기본 황금비 적용 검증
      expect(proportionApplication.primary_ratio).toBeCloseTo(
        testCase.expected_application.primary_ratio,
        3 // 소수점 3자리까지 정확
      );

      // 보조 비율 계산 검증
      testCase.expected_application.secondary_ratios.forEach((expectedRatio: number, index: number) => {
        expect(proportionApplication.secondary_ratios[index]).toBeCloseTo(expectedRatio, 3);
      });

      // 요소별 비례 적용 검증
      Object.keys(testCase.expected_application.element_proportions).forEach(element => {
        const expectedValue = testCase.expected_application.element_proportions[element];
        const actualValue = proportionApplication.element_proportions[element];
        expect(actualValue).toBeCloseTo(expectedValue, 2);
      });

      // 조화도 점수 검증
      expect(proportionApplication.harmony_score).toBeGreaterThanOrEqual(
        testCase.expected_application.harmony_score
      );

      // 역사적 정확성 검증
      const historicalValidation = await validationEngine.validateAgainstHistoricalReferences(
        proportionApplication,
        testCase.historical_references
      );
      expect(historicalValidation.accuracy_score).toBeGreaterThanOrEqual(
        testCase.validation_criteria.classical_authenticity
      );

      console.log('✅ 황금비 적용 정확도 검증 완료');
    });

    test('should calculate modular proportions accurately', async () => {
      const modularInput = {
        building_type: 'residential_tower',
        module_size: 3.6, // 3.6m 모듈
        repetition_count: 15,
        variation_allowance: 0.1
      };

      const modularSystem = await proportionCalculator.applyModularSystem(modularInput);

      // 모듈 시스템 일관성 검증
      expect(modularSystem.base_module).toBe(modularInput.module_size);
      expect(modularSystem.derived_modules.length).toBeGreaterThan(0);

      // 파생 모듈 계산 검증
      modularSystem.derived_modules.forEach((derivedModule: any) => {
        const ratio = derivedModule.size / modularInput.module_size;
        expect(ratio).toBeCloseTo(Math.round(ratio), 0.01); // 정수배 관계
      });

      // 반복 패턴 검증
      expect(modularSystem.repetition_pattern).toBeDefined();
      expect(modularSystem.repetition_pattern.consistency_score).toBeGreaterThan(0.9);

      // 변화 허용치 준수 검증
      expect(modularSystem.variation_compliance).toBeGreaterThan(0.95);

      console.log('✅ 모듈러 비례 시스템 적용 검증 완료');
    });

    test('should adapt proportions to cultural contexts', async () => {
      const culturalVariations = [
        { culture: 'korean_traditional', expected_module: 'kan_system' },
        { culture: 'japanese_traditional', expected_module: 'tatami_system' },
        { culture: 'islamic_classical', expected_module: 'geometric_pattern' },
        { culture: 'western_classical', expected_module: 'classical_orders' }
      ];

      const adaptationResults = [];

      for (const variation of culturalVariations) {
        const culturalAdaptation = await proportionCalculator.adaptToCulturalContext(
          {
            building_type: 'cultural_center',
            cultural_context: variation.culture,
            authenticity_level: 'high'
          }
        );

        adaptationResults.push({
          culture: variation.culture,
          proportional_system: culturalAdaptation.proportional_system,
          authenticity_score: culturalAdaptation.authenticity_score
        });

        // 문화적 적합성 검증
        expect(culturalAdaptation.proportional_system.type).toBe(variation.expected_module);
        expect(culturalAdaptation.authenticity_score).toBeGreaterThan(0.85);
      }

      // 문화적 다양성 처리 능력 검증
      const uniqueSystems = new Set(adaptationResults.map(r => r.proportional_system.type));
      expect(uniqueSystems.size).toBe(culturalVariations.length);

      console.log('✅ 문화적 맥락 비례 적응 검증 완료');
    });
  });

  // =============================================================================
  // 한국 전통 건축 이론 적용 테스트
  // =============================================================================

  describe('Korean Traditional Architecture Theory', () => {
    test('should apply traditional korean spatial principles', async () => {
      const testCase = theoryTestCases.find(tc => tc.id === 'korean_traditional_002')!;
      
      const traditionalApplication = await theoryEngine.applyKoreanTraditionalTheory(
        testCase.design_input
      );

      // 공간 구성 원리 검증
      expect(traditionalApplication.spatial_organization.type).toBe(
        testCase.expected_application.spatial_organization.type
      );
      expect(traditionalApplication.spatial_organization.courtyard_central).toBe(true);

      // 위계 구조 검증
      const expectedHierarchy = testCase.expected_application.spatial_organization.hierarchy;
      expectedHierarchy.forEach((expectedSpace: string, index: number) => {
        expect(traditionalApplication.spatial_organization.hierarchy[index]).toBe(expectedSpace);
      });

      // 비례 체계 검증
      expect(traditionalApplication.proportional_system.module_size).toBe(
        testCase.expected_application.proportional_system.module_size
      );

      // 재료 적용 적절성 검증
      Object.keys(testCase.expected_application.material_application).forEach(element => {
        const expectedMaterial = testCase.expected_application.material_application[element];
        const actualMaterial = traditionalApplication.material_application[element];
        expect(actualMaterial).toBe(expectedMaterial);
      });

      // 풍수 원리 준수 검증
      expect(traditionalApplication.feng_shui_compliance).toBeGreaterThanOrEqual(
        testCase.expected_application.feng_shui_compliance
      );

      // 문화적 진정성 검증
      const culturalValidation = await validationEngine.validateCulturalAuthenticity(
        traditionalApplication,
        'korean_traditional'
      );
      expect(culturalValidation.authenticity_score).toBeGreaterThanOrEqual(
        testCase.validation_criteria.cultural_sensitivity
      );

      console.log('✅ 한국 전통 건축 이론 적용 검증 완료');
    });

    test('should interpret traditional principles in contemporary context', async () => {
      const contemporaryHanok = {
        building_type: 'modern_hanok_house',
        contemporary_requirements: {
          insulation_standards: 'passive_house',
          accessibility: 'universal_design',
          technology_integration: 'smart_home',
          energy_efficiency: 'net_zero'
        },
        traditional_elements: {
          spatial_concept: 'courtyard_focus',
          material_inspiration: 'natural_materials',
          proportional_reference: 'traditional_kan',
          cultural_symbols: 'subtle_integration'
        }
      };

      const contemporaryInterpretation = await theoryEngine.interpretTraditionalPrinciplesContemporary(
        contemporaryHanok
      );

      // 전통 원리 현대적 해석 검증
      expect(contemporaryInterpretation.principle_adaptations).toBeDefined();
      expect(contemporaryInterpretation.principle_adaptations.length).toBeGreaterThan(0);

      // 성능 기준 충족 검증
      expect(contemporaryInterpretation.performance_compliance.insulation).toBeGreaterThan(0.9);
      expect(contemporaryInterpretation.performance_compliance.accessibility).toBe(1.0);
      expect(contemporaryInterpretation.performance_compliance.energy_efficiency).toBeGreaterThan(0.95);

      // 문화적 연속성 검증
      expect(contemporaryInterpretation.cultural_continuity.spatial_essence_preservation).toBeGreaterThan(0.8);
      expect(contemporaryInterpretation.cultural_continuity.material_spirit_retention).toBeGreaterThan(0.7);

      // 혁신성 평가
      expect(contemporaryInterpretation.innovation_index).toBeGreaterThan(0.6);
      expect(contemporaryInterpretation.innovation_index).toBeLessThan(0.9); // 과도한 혁신 방지

      console.log('✅ 전통 원리 현대적 해석 검증 완료');
    });
  });

  // =============================================================================
  // 모더니즘 설계 원칙 적용 테스트
  // =============================================================================

  describe('Modernist Design Principles', () => {
    test('should apply modernist principles accurately', async () => {
      const testCase = theoryTestCases.find(tc => tc.id === 'modernist_principles_003')!;
      
      const modernistApplication = await theoryEngine.applyModernistPrinciples(
        testCase.design_input
      );

      // 형태적 원칙 적용 검증
      expect(modernistApplication.formal_principles.geometric_purity).toBeGreaterThanOrEqual(
        testCase.expected_application.formal_principles.geometric_purity
      );
      expect(modernistApplication.formal_principles.ornament_elimination).toBeGreaterThanOrEqual(
        testCase.expected_application.formal_principles.ornament_elimination
      );

      // 공간적 개념 적용 검증
      expect(modernistApplication.spatial_concepts.open_plan).toBeGreaterThanOrEqual(
        testCase.expected_application.spatial_concepts.open_plan
      );
      expect(modernistApplication.spatial_concepts.natural_light_optimization).toBeGreaterThanOrEqual(
        testCase.expected_application.spatial_concepts.natural_light_optimization
      );

      // 기술적 통합 검증
      expect(modernistApplication.technological_integration.structural_expression).toBeGreaterThanOrEqual(
        testCase.expected_application.technological_integration.structural_expression
      );

      // 모더니즘 정통성 검증
      const orthodoxValidation = await validationEngine.validateModernistOrthodoxy(
        modernistApplication,
        testCase.historical_references
      );
      expect(orthodoxValidation.orthodoxy_score).toBeGreaterThanOrEqual(
        testCase.validation_criteria.modernist_orthodoxy
      );

      // 기능적 명확성 검증
      expect(modernistApplication.functional_clarity).toBeGreaterThanOrEqual(
        testCase.validation_criteria.functional_clarity
      );

      console.log('✅ 모더니즘 설계 원칙 적용 검증 완료');
    });

    test('should balance modernist ideals with practical constraints', async () => {
      const practicalConstraints = {
        budget_limitations: 0.7, // 30% 예산 제약
        code_requirements: {
          accessibility: 'ADA_compliance',
          fire_safety: 'enhanced',
          seismic: 'high_risk_zone'
        },
        client_preferences: {
          traditional_elements: 0.3,
          comfort_features: 'high_priority',
          maintenance_ease: 'important'
        }
      };

      const balancedDesign = await theoryEngine.balanceModernismWithConstraints(
        theoryTestCases[2].design_input,
        practicalConstraints
      );

      // 이상과 현실의 균형 검증
      expect(balancedDesign.modernist_integrity).toBeGreaterThan(0.7); // 70% 이상 모더니즘 원칙 유지
      expect(balancedDesign.practical_viability).toBeGreaterThan(0.8); // 80% 이상 실용적 요구사항 충족

      // 제약조건 해결 검증
      expect(balancedDesign.constraint_resolution.budget_compliance).toBe(true);
      expect(balancedDesign.constraint_resolution.code_compliance).toBe(true);
      expect(balancedDesign.constraint_resolution.client_satisfaction).toBeGreaterThan(0.8);

      // 창의적 해결책 평가
      expect(balancedDesign.creative_solutions).toBeDefined();
      expect(balancedDesign.creative_solutions.length).toBeGreaterThan(0);

      console.log('✅ 모더니즘 이상과 실용적 제약 균형 검증 완료');
    });
  });

  // =============================================================================
  // 지속가능 설계 이론 적용 테스트
  // =============================================================================

  describe('Sustainable Design Theory Application', () => {
    test('should apply comprehensive sustainability principles', async () => {
      const testCase = theoryTestCases.find(tc => tc.id === 'sustainable_design_004')!;
      
      const sustainabilityApplication = await theoryEngine.applySustainabilityTheory(
        testCase.design_input
      );

      // 패시브 설계 전략 검증
      expect(sustainabilityApplication.passive_design_strategies.solar_orientation).toBe('optimized');
      expect(sustainabilityApplication.passive_design_strategies.natural_ventilation).toBeGreaterThanOrEqual(
        testCase.expected_application.passive_design_strategies.natural_ventilation
      );

      // 재생에너지 시스템 검증
      expect(sustainabilityApplication.renewable_systems.solar_pv_coverage).toBeGreaterThanOrEqual(
        testCase.expected_application.renewable_systems.solar_pv_coverage
      );
      expect(sustainabilityApplication.renewable_systems.rainwater_harvesting).toBeGreaterThanOrEqual(
        testCase.expected_application.renewable_systems.rainwater_harvesting
      );

      // 재료 전략 검증
      expect(sustainabilityApplication.material_strategies.embodied_carbon_reduction).toBeGreaterThanOrEqual(
        testCase.expected_application.material_strategies.embodied_carbon_reduction
      );
      expect(sustainabilityApplication.material_strategies.local_material_ratio).toBeGreaterThanOrEqual(
        testCase.expected_application.material_strategies.local_material_ratio
      );

      // 생태계 통합 검증
      expect(sustainabilityApplication.ecosystem_integration.biodiversity_net_gain).toBeGreaterThanOrEqual(
        testCase.expected_application.ecosystem_integration.biodiversity_net_gain
      );

      // 인증 목표 달성 가능성 검증
      const certificationAnalysis = await validationEngine.analyzeCertificationFeasibility(
        sustainabilityApplication,
        testCase.design_input.certification_goals
      );
      expect(certificationAnalysis.leed_platinum_probability).toBeGreaterThan(0.8);
      expect(certificationAnalysis.living_building_probability).toBeGreaterThan(0.7);

      console.log('✅ 지속가능 설계 이론 적용 검증 완료');
    });

    test('should optimize lifecycle environmental impact', async () => {
      const lifecycleOptimization = {
        analysis_period: 50, // 50년
        environmental_indicators: [
          'global_warming_potential',
          'ozone_depletion_potential',
          'acidification_potential',
          'eutrophication_potential',
          'photochemical_ozone_creation'
        ],
        optimization_targets: {
          carbon_neutrality_year: 15, // 15년 내 탄소 중립
          material_circularity: 0.8, // 80% 순환 재료
          energy_autonomy: 0.9, // 90% 에너지 자립
          water_autonomy: 0.7 // 70% 물 자립
        }
      };

      const lifecycleOptimizationResult = await theoryEngine.optimizeLifecycleImpact(
        theoryTestCases[3].design_input,
        lifecycleOptimization
      );

      // 생애주기 환경영향 최적화 검증
      expect(lifecycleOptimizationResult.carbon_payback_period).toBeLessThanOrEqual(
        lifecycleOptimization.optimization_targets.carbon_neutrality_year
      );

      // 순환성 지표 검증
      expect(lifecycleOptimizationResult.material_circularity_achieved).toBeGreaterThanOrEqual(
        lifecycleOptimization.optimization_targets.material_circularity * 0.9 // 90% 달성
      );

      // 자립도 지표 검증
      expect(lifecycleOptimizationResult.energy_autonomy_level).toBeGreaterThanOrEqual(
        lifecycleOptimization.optimization_targets.energy_autonomy * 0.9
      );

      // 환경 영향 지표 개선 검증
      lifecycleOptimization.environmental_indicators.forEach(indicator => {
        expect(lifecycleOptimizationResult.impact_reductions[indicator]).toBeGreaterThan(0.5); // 50% 이상 개선
      });

      console.log('✅ 생애주기 환경영향 최적화 검증 완료');
    });
  });

  // =============================================================================
  // 맥락적 설계 이론 적용 테스트
  // =============================================================================

  describe('Contextual Design Theory Application', () => {
    test('should integrate with urban fabric sensitively', async () => {
      const testCase = theoryTestCases.find(tc => tc.id === 'contextual_urbanism_005')!;
      
      const contextualApplication = await contextualEngine.analyzeAndIntegrateContext(
        testCase.design_input
      );

      // 도시 직물 통합 검증
      expect(contextualApplication.urban_fabric_integration.height_transition).toBe(
        testCase.expected_application.urban_fabric_integration.height_transition
      );
      expect(contextualApplication.urban_fabric_integration.material_palette_compatibility).toBeGreaterThanOrEqual(
        testCase.expected_application.urban_fabric_integration.material_palette_compatibility
      );

      // 공공 공간 설계 검증
      expect(contextualApplication.public_space_design.pedestrian_connectivity).toBeGreaterThanOrEqual(
        testCase.expected_application.public_space_design.pedestrian_connectivity
      );
      expect(contextualApplication.public_space_design.accessibility_compliance).toBe(1.0);

      // 문화적 반응성 검증
      expect(contextualApplication.cultural_responsiveness.local_identity_expression).toBeGreaterThanOrEqual(
        testCase.expected_application.cultural_responsiveness.local_identity_expression
      );

      // 맥락적 민감성 검증
      const sensitivityValidation = await validationEngine.validateContextualSensitivity(
        contextualApplication,
        testCase.design_input.urban_context
      );
      expect(sensitivityValidation.sensitivity_score).toBeGreaterThanOrEqual(
        testCase.validation_criteria.contextual_sensitivity
      );

      console.log('✅ 맥락적 설계 이론 적용 검증 완료');
    });

    test('should respond to community needs appropriately', async () => {
      const communityEngagement = {
        stakeholder_groups: [
          { name: 'long_term_residents', influence: 0.3, concerns: ['gentrification', 'community_cohesion'] },
          { name: 'local_businesses', influence: 0.25, concerns: ['foot_traffic', 'parking', 'visibility'] },
          { name: 'city_planners', influence: 0.2, concerns: ['zoning_compliance', 'infrastructure_capacity'] },
          { name: 'environmental_groups', influence: 0.15, concerns: ['green_space', 'sustainability'] },
          { name: 'cultural_organizations', influence: 0.1, concerns: ['cultural_preservation', 'public_art'] }
        ],
        participation_methods: ['public_meetings', 'design_charrettes', 'online_surveys', 'focus_groups'],
        consensus_building: 'collaborative_priority_setting'
      };

      const communityResponseDesign = await contextualEngine.respondToCommunityNeeds(
        theoryTestCases[4].design_input,
        communityEngagement
      );

      // 이해관계자 관심사 반영 검증
      communityEngagement.stakeholder_groups.forEach(group => {
        const responseScore = communityResponseDesign.stakeholder_responses[group.name];
        expect(responseScore.concern_addressed_percentage).toBeGreaterThan(0.7); // 70% 이상 관심사 반영
        expect(responseScore.satisfaction_level).toBeGreaterThan(0.75); // 75% 이상 만족도
      });

      // 합의 구축 효과성 검증
      expect(communityResponseDesign.consensus_metrics.overall_approval).toBeGreaterThan(0.8);
      expect(communityResponseDesign.consensus_metrics.major_opposition).toBeLessThan(0.15); // 15% 미만 강한 반대

      // 공동체 혜택 최대화 검증
      expect(communityResponseDesign.community_benefits.economic_impact).toBeGreaterThan(0);
      expect(communityResponseDesign.community_benefits.social_cohesion_enhancement).toBeGreaterThan(0.6);
      expect(communityResponseDesign.community_benefits.cultural_vitality_increase).toBeGreaterThan(0.7);

      console.log('✅ 공동체 요구 반응형 설계 검증 완료');
    });
  });

  // =============================================================================
  // 통합 이론 적용 및 검증 테스트
  // =============================================================================

  describe('Integrated Theory Application and Validation', () => {
    test('should synthesize multiple theoretical frameworks', async () => {
      const multiTheoryProject = {
        project_type: 'cultural_education_complex',
        theoretical_requirements: {
          cultural_authenticity: { framework: 'korean_traditional', weight: 0.3 },
          functional_efficiency: { framework: 'modernist', weight: 0.25 },
          environmental_responsibility: { framework: 'sustainable_design', weight: 0.25 },
          social_engagement: { framework: 'contextual_urbanism', weight: 0.2 }
        },
        integration_challenges: [
          'traditional_vs_modern_materials',
          'openness_vs_intimacy_balance',
          'global_vs_local_identity',
          'efficiency_vs_experiential_richness'
        ]
      };

      const theorySynthesis = await theoryEngine.synthesizeMultipleFrameworks(multiTheoryProject);

      // 이론 통합 품질 검증
      expect(theorySynthesis.integration_coherence).toBeGreaterThan(0.8);
      expect(theorySynthesis.theoretical_conflicts_resolved).toBeGreaterThan(0.9);

      // 각 프레임워크 기여도 검증
      Object.keys(multiTheoryProject.theoretical_requirements).forEach(requirement => {
        const expectedWeight = multiTheoryProject.theoretical_requirements[requirement].weight;
        const actualContribution = theorySynthesis.framework_contributions[requirement];
        expect(Math.abs(actualContribution - expectedWeight)).toBeLessThan(0.1); // 10% 허용 편차
      });

      // 통합 혁신성 검증
      expect(theorySynthesis.synthesis_innovation_index).toBeGreaterThan(0.6);
      expect(theorySynthesis.precedent_uniqueness_score).toBeGreaterThan(0.7);

      // 실현 가능성 검증
      expect(theorySynthesis.implementation_feasibility.technical).toBeGreaterThan(0.8);
      expect(theorySynthesis.implementation_feasibility.economic).toBeGreaterThan(0.75);
      expect(theorySynthesis.implementation_feasibility.social_acceptance).toBeGreaterThan(0.8);

      console.log('✅ 다중 이론 프레임워크 통합 검증 완료');
    });

    test('should validate theory application accuracy comprehensively', async () => {
      // 모든 테스트 케이스에 대한 종합 검증
      const comprehensiveValidation = await Promise.all(
        theoryTestCases.map(async testCase => {
          const applicationResult = await theoryEngine.applyTheoryFramework(
            testCase.theory_domain,
            testCase.design_input
          );

          const validationResult = await validationEngine.comprehensiveValidation(
            applicationResult,
            testCase.expected_application,
            testCase.validation_criteria,
            testCase.historical_references
          );

          return {
            test_case_id: testCase.id,
            theory_domain: testCase.theory_domain,
            accuracy_score: validationResult.accuracy_score,
            validation_details: validationResult.detailed_scores,
            meets_threshold: validationResult.accuracy_score >= testCase.accuracy_threshold
          };
        })
      );

      // 전체 정확도 검증
      const overallAccuracy = comprehensiveValidation.reduce(
        (sum, result) => sum + result.accuracy_score, 0
      ) / comprehensiveValidation.length;

      expect(overallAccuracy).toBeGreaterThan(0.85); // 평균 85% 이상 정확도

      // 개별 케이스 임계값 달성 검증
      const passedCases = comprehensiveValidation.filter(result => result.meets_threshold);
      expect(passedCases.length / comprehensiveValidation.length).toBeGreaterThan(0.8); // 80% 이상 케이스 통과

      // 이론 도메인별 성능 분석
      const domainPerformance = {};
      comprehensiveValidation.forEach(result => {
        if (!domainPerformance[result.theory_domain]) {
          domainPerformance[result.theory_domain] = [];
        }
        domainPerformance[result.theory_domain].push(result.accuracy_score);
      });

      Object.keys(domainPerformance).forEach(domain => {
        const domainAverage = domainPerformance[domain].reduce((a, b) => a + b, 0) / 
                             domainPerformance[domain].length;
        expect(domainAverage).toBeGreaterThan(0.8); // 각 도메인 80% 이상
      });

      console.log('✅ 종합 이론 적용 정확도 검증 완료:', `평균 정확도 ${(overallAccuracy * 100).toFixed(1)}%`);
    });

    test('should demonstrate cultural competence across contexts', async () => {
      const culturalCompetenceTest = {
        cultural_contexts: [
          { name: 'korean_traditional', test_scenarios: 3 },
          { name: 'japanese_minimalism', test_scenarios: 2 },
          { name: 'islamic_geometric', test_scenarios: 2 },
          { name: 'scandinavian_functionalism', test_scenarios: 2 },
          { name: 'latin_american_regionalism', test_scenarios: 2 }
        ],
        competence_criteria: {
          cultural_sensitivity: 0.9,
          historical_accuracy: 0.85,
          contemporary_relevance: 0.8,
          cross_cultural_synthesis: 0.75
        }
      };

      const culturalCompetenceResults = [];

      for (const context of culturalCompetenceTest.cultural_contexts) {
        const contextResults = await theoryEngine.assessCulturalCompetence(
          context.name,
          context.test_scenarios
        );

        culturalCompetenceResults.push({
          cultural_context: context.name,
          competence_scores: contextResults.competence_scores,
          overall_competence: contextResults.overall_competence
        });

        // 개별 문화적 맥락 역량 검증
        expect(contextResults.overall_competence).toBeGreaterThan(0.8);
        
        Object.keys(culturalCompetenceTest.competence_criteria).forEach(criterion => {
          expect(contextResults.competence_scores[criterion]).toBeGreaterThanOrEqual(
            culturalCompetenceTest.competence_criteria[criterion] * 0.9 // 90% 달성
          );
        });
      }

      // 문화적 다양성 처리 능력 검증
      const diversityHandling = culturalCompetenceResults.reduce((sum, result) => 
        sum + result.overall_competence, 0
      ) / culturalCompetenceResults.length;

      expect(diversityHandling).toBeGreaterThan(0.85); // 전체 평균 85% 이상

      // 교차 문화적 통합 능력 검증
      const crossCulturalTest = await theoryEngine.testCrossCulturalSynthesis(
        culturalCompetenceTest.cultural_contexts.slice(0, 3)
      );
      expect(crossCulturalTest.synthesis_success_rate).toBeGreaterThan(0.75);

      console.log('✅ 문화적 역량 검증 완료');
    });
  });
});