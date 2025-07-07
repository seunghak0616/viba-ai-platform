/**
 * 성능 분석 및 최적화 알고리즘 단위 테스트
 * 
 * VIBA AI 에이전트의 건물 성능 분석 및 최적화 기능 검증
 * 
 * @version 1.0
 * @author VIBA AI Team
 * @date 2025.07.06
 */

import { describe, test, expect, beforeAll, beforeEach, afterEach } from '@jest/testing-library/jest-dom';
import { 
  PerformanceAnalyzer,
  EnergyAnalysisEngine,
  ThermalAnalyzer,
  DaylightingAnalyzer,
  StructuralAnalyzer,
  AcousticAnalyzer,
  OptimizationEngine,
  SimulationRunner 
} from '../../src/ai/performance-analysis';

import {
  ClimateDataProvider,
  MaterialPropertiesDB,
  BuildingCodesValidator,
  SustainabilityCalculator
} from '../../src/ai/performance-analysis/data-providers';

import {
  GeneticOptimizer,
  ParticleSwarmOptimizer,
  SimulatedAnnealingOptimizer,
  MultiObjectiveOptimizer
} from '../../src/ai/performance-analysis/optimizers';

import {
  PerformanceTestData,
  MockBuildingModels,
  ClimateTestScenarios,
  OptimizationBenchmarks
} from '../fixtures/performance-test-data';

// =============================================================================
// 테스트 데이터 및 설정
// =============================================================================

interface PerformanceTestCase {
  id: string;
  description: string;
  building_model: any;
  analysis_type: string;
  expected_metrics: any;
  accuracy_threshold: number;
  performance_limit: number; // ms
  priority: 'high' | 'medium' | 'low';
}

const performanceTestCases: PerformanceTestCase[] = [
  {
    id: 'energy_residential_001',
    description: '단독주택 에너지 성능 분석',
    building_model: {
      type: '단독주택',
      floors: 2,
      area: 150,
      envelope: {
        wall_u_value: 0.35,
        roof_u_value: 0.20,
        window_u_value: 1.8,
        window_shgc: 0.4,
        infiltration_rate: 0.5
      },
      location: 'Seoul',
      orientation: 'south'
    },
    analysis_type: 'energy',
    expected_metrics: {
      heating_demand: { min: 40, max: 60, unit: 'kWh/m²·year' },
      cooling_demand: { min: 15, max: 25, unit: 'kWh/m²·year' },
      total_energy: { min: 80, max: 120, unit: 'kWh/m²·year' },
      energy_rating: 'B'
    },
    accuracy_threshold: 0.1, // 10% 오차 허용
    performance_limit: 5000, // 5초
    priority: 'high'
  },

  {
    id: 'daylight_office_001',
    description: '사무소 자연채광 분석',
    building_model: {
      type: '사무소',
      floors: 5,
      area: 1000,
      spaces: [
        {
          name: '일반사무실',
          area: 200,
          window_area: 40,
          window_orientation: 'south',
          required_illuminance: 500
        }
      ],
      location: 'Seoul',
      latitude: 37.5665,
      longitude: 126.9780
    },
    analysis_type: 'daylighting',
    expected_metrics: {
      daylight_factor: { min: 2.0, max: 6.0, unit: '%' },
      useful_daylight_illuminance: { min: 50, max: 90, unit: '%' },
      glare_probability: { max: 0.4, unit: 'DGP' },
      annual_daylight: { min: 2000, max: 4000, unit: 'hours' }
    },
    accuracy_threshold: 0.15,
    performance_limit: 8000,
    priority: 'high'
  },

  {
    id: 'thermal_commercial_001',
    description: '상업시설 열환경 분석',
    building_model: {
      type: '상업시설',
      floors: 3,
      area: 800,
      hvac_system: 'VAV',
      internal_loads: {
        occupancy: 0.1, // persons/m²
        equipment: 15, // W/m²
        lighting: 12 // W/m²
      },
      schedule: 'commercial',
      location: 'Seoul'
    },
    analysis_type: 'thermal',
    expected_metrics: {
      operative_temperature: { min: 20, max: 26, unit: '°C' },
      pmv: { min: -0.5, max: 0.5, unit: 'PMV' },
      ppd: { max: 10, unit: '%' },
      air_velocity: { min: 0.1, max: 0.3, unit: 'm/s' }
    },
    accuracy_threshold: 0.1,
    performance_limit: 10000,
    priority: 'high'
  },

  {
    id: 'structural_highrise_001',
    description: '고층건물 구조 성능 분석',
    building_model: {
      type: '고층사무소',
      floors: 20,
      height: 80,
      structure_type: 'steel_frame',
      seismic_zone: 'I',
      wind_zone: 'B',
      loads: {
        dead_load: 5.0, // kN/m²
        live_load: 2.5, // kN/m²
        wind_load: 1.0, // kN/m²
        seismic_load: 0.8 // kN/m²
      }
    },
    analysis_type: 'structural',
    expected_metrics: {
      max_displacement: { max: 80, unit: 'mm' }, // H/1000
      max_story_drift: { max: 20, unit: 'mm' }, // H/400
      natural_frequency: { min: 0.1, max: 1.0, unit: 'Hz' },
      stress_ratio: { max: 0.9, unit: 'ratio' }
    },
    accuracy_threshold: 0.05,
    performance_limit: 15000,
    priority: 'medium'
  },

  {
    id: 'acoustic_cultural_001',
    description: '문화시설 음향 성능 분석',
    building_model: {
      type: '공연장',
      volume: 5000, // m³
      seats: 500,
      room_shape: 'rectangular',
      materials: {
        walls: 'acoustic_plaster',
        ceiling: 'perforated_metal',
        floor: 'carpet'
      },
      sound_system: 'distributed'
    },
    analysis_type: 'acoustic',
    expected_metrics: {
      reverberation_time: { min: 1.8, max: 2.2, unit: 's' },
      clarity: { min: 0, max: 4, unit: 'dB' },
      speech_intelligibility: { min: 0.7, max: 1.0, unit: 'STI' },
      background_noise: { max: 35, unit: 'dBA' }
    },
    accuracy_threshold: 0.1,
    performance_limit: 12000,
    priority: 'medium'
  }
];

// =============================================================================
// 성능 분석 엔진 단위 테스트
// =============================================================================

describe('Performance Analysis Engine Tests', () => {
  let performanceAnalyzer: PerformanceAnalyzer;
  let energyEngine: EnergyAnalysisEngine;
  let thermalAnalyzer: ThermalAnalyzer;
  let daylightAnalyzer: DaylightingAnalyzer;
  let structuralAnalyzer: StructuralAnalyzer;
  let acousticAnalyzer: AcousticAnalyzer;
  let optimizationEngine: OptimizationEngine;
  let simulationRunner: SimulationRunner;

  beforeAll(async () => {
    // 성능 분석 컴포넌트 초기화
    performanceAnalyzer = new PerformanceAnalyzer({
      precision: 'high',
      parallel_processing: true,
      cache_enabled: true,
      validation_enabled: true
    });

    energyEngine = new EnergyAnalysisEngine({
      calculation_method: 'hourly',
      weather_data_source: 'TMY3',
      hvac_modeling: 'detailed',
      renewable_energy: true
    });

    thermalAnalyzer = new ThermalAnalyzer({
      cfd_enabled: true,
      comfort_standards: ['ASHRAE_55', 'ISO_7730'],
      adaptive_comfort: true,
      humidity_control: true
    });

    daylightAnalyzer = new DaylightingAnalyzer({
      calculation_engine: 'radiance',
      sky_models: ['CIE_clear', 'CIE_overcast', 'perez'],
      glare_analysis: true,
      circadian_lighting: true
    });

    structuralAnalyzer = new StructuralAnalyzer({
      analysis_type: 'dynamic',
      finite_element_mesh: 'adaptive',
      material_nonlinearity: true,
      geometric_nonlinearity: false
    });

    acousticAnalyzer = new AcousticAnalyzer({
      calculation_method: 'ray_tracing',
      frequency_bands: 'octave',
      diffusion_modeling: true,
      auralization: false
    });

    optimizationEngine = new OptimizationEngine({
      algorithms: ['genetic', 'particle_swarm', 'simulated_annealing'],
      multi_objective: true,
      constraint_handling: 'penalty',
      convergence_criteria: 0.001
    });

    simulationRunner = new SimulationRunner({
      parallel_jobs: 4,
      cloud_computing: false,
      result_caching: true,
      progress_tracking: true
    });

    // 컴포넌트 초기화 및 데이터 로딩
    await Promise.all([
      performanceAnalyzer.initialize(),
      energyEngine.loadWeatherData(),
      thermalAnalyzer.loadComfortModels(),
      daylightAnalyzer.loadSkyModels(),
      structuralAnalyzer.loadMaterialProperties(),
      acousticAnalyzer.loadAcousticDatabase(),
      optimizationEngine.initialize(),
      simulationRunner.setupEnvironment()
    ]);

    console.log('✅ 성능 분석 컴포넌트 초기화 완료');
  });

  beforeEach(() => {
    // 각 테스트 전 캐시 및 상태 초기화
    performanceAnalyzer.clearCache();
    simulationRunner.clearJobQueue();
  });

  afterEach(() => {
    // 테스트 후 임시 파일 정리
    simulationRunner.cleanupTempFiles();
  });

  // =============================================================================
  // 에너지 성능 분석 테스트
  // =============================================================================

  describe('Energy Performance Analysis', () => {
    test('should calculate heating and cooling loads accurately', async () => {
      const testCase = performanceTestCases.find(tc => tc.id === 'energy_residential_001')!;
      
      const startTime = Date.now();
      const energyAnalysis = await energyEngine.analyzeEnergyPerformance(testCase.building_model);
      const analysisTime = Date.now() - startTime;

      // 성능 시간 검증
      expect(analysisTime).toBeLessThan(testCase.performance_limit);

      // 에너지 수요 검증
      expect(energyAnalysis.heating_demand).toBeWithinRange(
        testCase.expected_metrics.heating_demand.min,
        testCase.expected_metrics.heating_demand.max
      );

      expect(energyAnalysis.cooling_demand).toBeWithinRange(
        testCase.expected_metrics.cooling_demand.min,
        testCase.expected_metrics.cooling_demand.max
      );

      expect(energyAnalysis.total_energy_consumption).toBeWithinRange(
        testCase.expected_metrics.total_energy.min,
        testCase.expected_metrics.total_energy.max
      );

      // 에너지 등급 검증
      expect(energyAnalysis.energy_rating).toBe(testCase.expected_metrics.energy_rating);

      // 월별 분해 데이터 검증
      expect(energyAnalysis.monthly_data).toHaveLength(12);
      energyAnalysis.monthly_data.forEach((month: any) => {
        expect(month.heating).toBeGreaterThanOrEqual(0);
        expect(month.cooling).toBeGreaterThanOrEqual(0);
        expect(month.total).toBeGreaterThan(0);
      });

      console.log(`✅ 에너지 분석 완료: ${analysisTime}ms, 총 에너지 ${energyAnalysis.total_energy_consumption} kWh/m²·year`);
    });

    test('should analyze renewable energy potential', async () => {
      const buildingWithRenewables = {
        ...performanceTestCases[0].building_model,
        roof_area: 100,
        roof_orientation: 'south',
        roof_tilt: 30,
        shading_obstructions: false
      };

      const renewableAnalysis = await energyEngine.analyzeRenewableEnergy(buildingWithRenewables);

      // 태양광 발전 잠재량 검증
      expect(renewableAnalysis.solar_pv).toBeDefined();
      expect(renewableAnalysis.solar_pv.annual_generation).toBeGreaterThan(0);
      expect(renewableAnalysis.solar_pv.capacity_factor).toBeWithinRange(0.12, 0.18); // 한국 평균

      // 태양열 온수 잠재량 검증
      expect(renewableAnalysis.solar_thermal).toBeDefined();
      expect(renewableAnalysis.solar_thermal.annual_output).toBeGreaterThan(0);

      // 경제성 분석 검증
      expect(renewableAnalysis.economics).toBeDefined();
      expect(renewableAnalysis.economics.payback_period).toBeGreaterThan(0);
      expect(renewableAnalysis.economics.lcoe).toBeGreaterThan(0);

      console.log('✅ 신재생에너지 잠재량 분석 완료');
    });

    test('should perform parametric energy analysis', async () => {
      const baseModel = performanceTestCases[0].building_model;
      
      const parameters = {
        wall_u_value: [0.20, 0.35, 0.50],
        window_u_value: [1.4, 1.8, 2.2],
        window_shgc: [0.3, 0.4, 0.5],
        infiltration_rate: [0.3, 0.5, 0.7]
      };

      const parametricResults = await energyEngine.runParametricAnalysis(baseModel, parameters);

      // 결과 구조 검증
      expect(parametricResults.results).toBeDefined();
      expect(parametricResults.results.length).toBe(3 * 3 * 3 * 3); // 모든 조합

      // 민감도 분석 결과 검증
      expect(parametricResults.sensitivity_analysis).toBeDefined();
      expect(parametricResults.sensitivity_analysis.most_influential).toBeDefined();

      // 최적 조합 검증
      expect(parametricResults.optimal_combination).toBeDefined();
      expect(parametricResults.optimal_combination.energy_savings).toBeGreaterThan(0);

      console.log('✅ 매개변수 에너지 분석 완료:', parametricResults.results.length, '개 케이스');
    });

    test('should validate against building energy codes', async () => {
      const buildingModel = performanceTestCases[0].building_model;
      
      const codeCompliance = await energyEngine.validateEnergyCode(buildingModel, {
        code: 'KS_F_2295', // 건축물 에너지효율등급 인증기준
        version: '2023',
        building_type: '단독주택',
        climate_zone: '중부1지역'
      });

      // 법규 준수 검증
      expect(codeCompliance.compliant).toBeDefined();
      expect(codeCompliance.energy_performance_index).toBeDefined();
      expect(codeCompliance.energy_performance_index).toBeLessThanOrEqual(100);

      // 세부 요구사항 검증
      expect(codeCompliance.envelope_performance).toBeDefined();
      expect(codeCompliance.envelope_performance.wall_u_value).toBeLessThanOrEqual(0.36);
      expect(codeCompliance.envelope_performance.roof_u_value).toBeLessThanOrEqual(0.18);
      expect(codeCompliance.envelope_performance.window_u_value).toBeLessThanOrEqual(1.8);

      // 등급 산정 검증
      expect(codeCompliance.efficiency_grade).toBeOneOf(['1+++', '1++', '1+', '1', '2', '3', '4', '5']);

      console.log('✅ 에너지 법규 검증 완료:', codeCompliance.efficiency_grade, '등급');
    });
  });

  // =============================================================================
  // 자연채광 분석 테스트
  // =============================================================================

  describe('Daylighting Analysis', () => {
    test('should calculate daylight metrics accurately', async () => {
      const testCase = performanceTestCases.find(tc => tc.id === 'daylight_office_001')!;
      
      const startTime = Date.now();
      const daylightAnalysis = await daylightAnalyzer.analyzeDaylighting(testCase.building_model);
      const analysisTime = Date.now() - startTime;

      // 성능 시간 검증
      expect(analysisTime).toBeLessThan(testCase.performance_limit);

      // 주광률 검증
      expect(daylightAnalysis.daylight_factor.average).toBeWithinRange(
        testCase.expected_metrics.daylight_factor.min,
        testCase.expected_metrics.daylight_factor.max
      );

      // 유용한 자연채광 조도 검증
      expect(daylightAnalysis.useful_daylight_illuminance).toBeWithinRange(
        testCase.expected_metrics.useful_daylight_illuminance.min,
        testCase.expected_metrics.useful_daylight_illuminance.max
      );

      // 글레어 확률 검증
      expect(daylightAnalysis.glare_probability.max).toBeLessThanOrEqual(
        testCase.expected_metrics.glare_probability.max
      );

      // 연간 자연채광 시간 검증
      expect(daylightAnalysis.annual_daylight_hours).toBeWithinRange(
        testCase.expected_metrics.annual_daylight.min,
        testCase.expected_metrics.annual_daylight.max
      );

      // 조도 분포 균등성 검증
      expect(daylightAnalysis.uniformity_ratio).toBeGreaterThan(0.4); // IESNA 기준

      console.log(`✅ 자연채광 분석 완료: ${analysisTime}ms, 평균 주광률 ${daylightAnalysis.daylight_factor.average}%`);
    });

    test('should optimize window design for daylighting', async () => {
      const baseSpace = {
        width: 10,
        depth: 6,
        height: 3,
        orientation: 'south',
        latitude: 37.5665
      };

      const windowConfigurations = [
        { width: 3, height: 1.5, sill_height: 1.0, shading: false },
        { width: 4, height: 1.8, sill_height: 0.8, shading: false },
        { width: 5, height: 2.0, sill_height: 0.6, shading: true },
        { width: 6, height: 2.2, sill_height: 0.4, shading: true }
      ];

      const optimizationResults = await daylightAnalyzer.optimizeWindowDesign(
        baseSpace,
        windowConfigurations
      );

      // 최적 창호 설계 검증
      expect(optimizationResults.optimal_configuration).toBeDefined();
      expect(optimizationResults.optimal_configuration.daylight_performance).toBeGreaterThan(0.7);
      expect(optimizationResults.optimal_configuration.glare_control).toBeLessThan(0.4);

      // 에너지 절약 효과 검증
      expect(optimizationResults.energy_savings).toBeDefined();
      expect(optimizationResults.energy_savings.lighting_reduction).toBeGreaterThan(0);

      // 시간별 성능 분석 검증
      expect(optimizationResults.hourly_analysis).toBeDefined();
      expect(optimizationResults.hourly_analysis.length).toBe(8760); // 연간 시간

      console.log('✅ 창호 설계 최적화 완료');
    });

    test('should analyze seasonal daylight variations', async () => {
      const testSpace = performanceTestCases[1].building_model.spaces[0];
      
      const seasonalAnalysis = await daylightAnalyzer.analyzeSeasonalVariations(testSpace);

      // 계절별 데이터 검증
      expect(seasonalAnalysis.spring).toBeDefined();
      expect(seasonalAnalysis.summer).toBeDefined();
      expect(seasonalAnalysis.autumn).toBeDefined();
      expect(seasonalAnalysis.winter).toBeDefined();

      // 하지/동지 극값 검증
      expect(seasonalAnalysis.summer.max_illuminance).toBeGreaterThan(
        seasonalAnalysis.winter.max_illuminance
      );

      expect(seasonalAnalysis.summer.daylight_hours).toBeGreaterThan(
        seasonalAnalysis.winter.daylight_hours
      );

      // 월별 변화 추이 검증
      expect(seasonalAnalysis.monthly_trends).toHaveLength(12);
      seasonalAnalysis.monthly_trends.forEach((month: any) => {
        expect(month.average_df).toBeGreaterThan(0);
        expect(month.peak_illuminance).toBeGreaterThan(0);
      });

      console.log('✅ 계절별 자연채광 변화 분석 완료');
    });

    test('should evaluate circadian lighting potential', async () => {
      const workSpace = {
        type: 'office',
        area: 200,
        occupancy_schedule: '09:00-18:00',
        target_illuminance: 500,
        target_cct: 4000,
        circadian_requirements: true
      };

      const circadianAnalysis = await daylightAnalyzer.analyzeCircadianLighting(workSpace);

      // 서카디안 리듬 지원 검증
      expect(circadianAnalysis.circadian_stimulus).toBeDefined();
      expect(circadianAnalysis.circadian_stimulus.morning).toBeGreaterThan(0.3);
      expect(circadianAnalysis.circadian_stimulus.afternoon).toBeGreaterThan(0.2);

      // 색온도 변화 검증
      expect(circadianAnalysis.color_temperature_profile).toBeDefined();
      expect(circadianAnalysis.color_temperature_profile.length).toBe(24); // 시간별

      // 건강 및 웰빙 지수 검증
      expect(circadianAnalysis.wellbeing_index).toBeWithinRange(0, 1);
      expect(circadianAnalysis.sleep_quality_impact).toBeDefined();

      console.log('✅ 서카디안 조명 분석 완료:', circadianAnalysis.wellbeing_index);
    });
  });

  // =============================================================================
  // 열환경 분석 테스트
  // =============================================================================

  describe('Thermal Comfort Analysis', () => {
    test('should calculate thermal comfort metrics', async () => {
      const testCase = performanceTestCases.find(tc => tc.id === 'thermal_commercial_001')!;
      
      const startTime = Date.now();
      const thermalAnalysis = await thermalAnalyzer.analyzeThermalComfort(testCase.building_model);
      const analysisTime = Date.now() - startTime;

      // 성능 시간 검증
      expect(analysisTime).toBeLessThan(testCase.performance_limit);

      // 작용온도 검증
      expect(thermalAnalysis.operative_temperature.mean).toBeWithinRange(
        testCase.expected_metrics.operative_temperature.min,
        testCase.expected_metrics.operative_temperature.max
      );

      // PMV 지수 검증
      expect(Math.abs(thermalAnalysis.pmv.mean)).toBeLessThanOrEqual(0.5); // 쾌적 범위

      // PPD 지수 검증
      expect(thermalAnalysis.ppd.mean).toBeLessThanOrEqual(
        testCase.expected_metrics.ppd.max
      );

      // 기류 속도 검증
      expect(thermalAnalysis.air_velocity.mean).toBeWithinRange(
        testCase.expected_metrics.air_velocity.min,
        testCase.expected_metrics.air_velocity.max
      );

      // 적응적 쾌적 모델 검증
      expect(thermalAnalysis.adaptive_comfort).toBeDefined();
      expect(thermalAnalysis.adaptive_comfort.compliance_rate).toBeGreaterThan(0.8);

      console.log(`✅ 열환경 분석 완료: ${analysisTime}ms, PMV ${thermalAnalysis.pmv.mean}`);
    });

    test('should perform CFD thermal analysis', async () => {
      const complexSpace = {
        geometry: 'L_shaped',
        area: 300,
        volume: 900,
        hvac_layout: 'ceiling_diffusers',
        heat_sources: [
          { type: 'occupants', count: 30, heat_gain: 100 },
          { type: 'equipment', power: 3000, location: 'distributed' },
          { type: 'lighting', power: 2400, location: 'ceiling' }
        ],
        boundary_conditions: {
          walls: { temperature: 22, heat_transfer: 'mixed' },
          windows: { solar_heat_gain: 200, area: 60 }
        }
      };

      const cfdAnalysis = await thermalAnalyzer.runCFDAnalysis(complexSpace);

      // CFD 결과 검증
      expect(cfdAnalysis.velocity_field).toBeDefined();
      expect(cfdAnalysis.temperature_field).toBeDefined();
      expect(cfdAnalysis.pressure_field).toBeDefined();

      // 온도 분포 균등성 검증
      expect(cfdAnalysis.temperature_uniformity).toBeGreaterThan(0.7);
      expect(cfdAnalysis.max_temperature_difference).toBeLessThan(3.0); // 3°C 이내

      // 기류 패턴 검증
      expect(cfdAnalysis.air_change_effectiveness).toBeGreaterThan(0.9);
      expect(cfdAnalysis.ventilation_efficiency).toBeGreaterThan(0.8);

      // 드래프트 위험도 검증
      expect(cfdAnalysis.draft_risk.percentage).toBeLessThan(15); // 15% 미만

      console.log('✅ CFD 열환경 분석 완료');
    });

    test('should optimize HVAC system performance', async () => {
      const hvacSystem = {
        type: 'VAV_with_reheat',
        zones: 8,
        capacity: 500, // kW
        efficiency: 0.85,
        control_strategy: 'optimum_start',
        setpoints: {
          heating: 20,
          cooling: 26,
          deadband: 2
        }
      };

      const hvacOptimization = await thermalAnalyzer.optimizeHVACSystem(hvacSystem);

      // 최적화 결과 검증
      expect(hvacOptimization.optimized_setpoints).toBeDefined();
      expect(hvacOptimization.energy_savings).toBeGreaterThan(0);
      expect(hvacOptimization.comfort_improvement).toBeGreaterThan(0);

      // 제어 전략 검증
      expect(hvacOptimization.optimal_control).toBeDefined();
      expect(hvacOptimization.optimal_control.schedule).toBeDefined();
      expect(hvacOptimization.optimal_control.reset_strategies).toBeDefined();

      // 경제성 분석 검증
      expect(hvacOptimization.economics.annual_savings).toBeGreaterThan(0);
      expect(hvacOptimization.economics.payback_period).toBeLessThan(10);

      console.log('✅ HVAC 시스템 최적화 완료');
    });
  });

  // =============================================================================
  // 구조 성능 분석 테스트
  // =============================================================================

  describe('Structural Performance Analysis', () => {
    test('should analyze structural response under loads', async () => {
      const testCase = performanceTestCases.find(tc => tc.id === 'structural_highrise_001')!;
      
      const startTime = Date.now();
      const structuralAnalysis = await structuralAnalyzer.analyzeStructuralPerformance(testCase.building_model);
      const analysisTime = Date.now() - startTime;

      // 성능 시간 검증
      expect(analysisTime).toBeLessThan(testCase.performance_limit);

      // 최대 변위 검증
      expect(structuralAnalysis.max_displacement).toBeLessThanOrEqual(
        testCase.expected_metrics.max_displacement.max
      );

      // 층간변위 검증
      expect(structuralAnalysis.max_story_drift).toBeLessThanOrEqual(
        testCase.expected_metrics.max_story_drift.max
      );

      // 고유 진동수 검증
      expect(structuralAnalysis.natural_frequency).toBeWithinRange(
        testCase.expected_metrics.natural_frequency.min,
        testCase.expected_metrics.natural_frequency.max
      );

      // 응력비 검증
      expect(structuralAnalysis.max_stress_ratio).toBeLessThanOrEqual(
        testCase.expected_metrics.stress_ratio.max
      );

      // 동적 특성 검증
      expect(structuralAnalysis.modal_analysis).toBeDefined();
      expect(structuralAnalysis.modal_analysis.modes.length).toBeGreaterThanOrEqual(3);

      console.log(`✅ 구조 해석 완료: ${analysisTime}ms, 최대변위 ${structuralAnalysis.max_displacement}mm`);
    });

    test('should perform seismic response analysis', async () => {
      const seismicBuilding = {
        ...performanceTestCases[3].building_model,
        seismic_design: {
          importance_factor: 1.2,
          response_modification: 5.0,
          fundamental_period: 2.5,
          base_shear_coefficient: 0.08
        }
      };

      const seismicAnalysis = await structuralAnalyzer.analyzeSeismicResponse(seismicBuilding);

      // 내진 응답 검증
      expect(seismicAnalysis.response_spectrum_analysis).toBeDefined();
      expect(seismicAnalysis.base_shear).toBeGreaterThan(0);
      expect(seismicAnalysis.overturning_moment).toBeGreaterThan(0);

      // 층별 응답 검증
      expect(seismicAnalysis.story_responses).toHaveLength(seismicBuilding.floors);
      seismicAnalysis.story_responses.forEach((story: any) => {
        expect(story.drift_ratio).toBeLessThan(0.005); // 0.5% 제한
        expect(story.acceleration).toBeGreaterThan(0);
      });

      // 내진 성능 평가 검증
      expect(seismicAnalysis.performance_level).toBeOneOf(['IO', 'LS', 'CP']); // Immediate Occupancy, Life Safety, Collapse Prevention
      expect(seismicAnalysis.safety_factor).toBeGreaterThan(1.0);

      console.log('✅ 내진 응답 해석 완료:', seismicAnalysis.performance_level);
    });

    test('should optimize structural design', async () => {
      const designParameters = {
        objective: 'minimize_weight',
        constraints: {
          max_displacement: 50, // mm
          max_stress_ratio: 0.8,
          min_frequency: 0.2 // Hz
        },
        variables: {
          column_sizes: ['400x400', '450x450', '500x500'],
          beam_sizes: ['300x600', '350x650', '400x700'],
          steel_grades: ['SS400', 'SM490', 'SM520']
        }
      };

      const structuralOptimization = await structuralAnalyzer.optimizeStructuralDesign(
        performanceTestCases[3].building_model,
        designParameters
      );

      // 최적화 결과 검증
      expect(structuralOptimization.optimized_design).toBeDefined();
      expect(structuralOptimization.weight_reduction).toBeGreaterThan(0);
      expect(structuralOptimization.cost_savings).toBeGreaterThan(0);

      // 제약조건 만족 검증
      expect(structuralOptimization.constraint_satisfaction.displacement).toBe(true);
      expect(structuralOptimization.constraint_satisfaction.stress).toBe(true);
      expect(structuralOptimization.constraint_satisfaction.frequency).toBe(true);

      // 구조 성능 개선 검증
      expect(structuralOptimization.performance_improvement.stiffness).toBeGreaterThan(0);
      expect(structuralOptimization.performance_improvement.strength).toBeGreaterThan(0);

      console.log('✅ 구조 설계 최적화 완료');
    });
  });

  // =============================================================================
  // 음향 성능 분석 테스트
  // =============================================================================

  describe('Acoustic Performance Analysis', () => {
    test('should analyze room acoustics', async () => {
      const testCase = performanceTestCases.find(tc => tc.id === 'acoustic_cultural_001')!;
      
      const startTime = Date.now();
      const acousticAnalysis = await acousticAnalyzer.analyzeRoomAcoustics(testCase.building_model);
      const analysisTime = Date.now() - startTime;

      // 성능 시간 검증
      expect(analysisTime).toBeLessThan(testCase.performance_limit);

      // 잔향시간 검증
      expect(acousticAnalysis.reverberation_time.RT60).toBeWithinRange(
        testCase.expected_metrics.reverberation_time.min,
        testCase.expected_metrics.reverberation_time.max
      );

      // 명료도 검증
      expect(acousticAnalysis.clarity.C80).toBeWithinRange(
        testCase.expected_metrics.clarity.min,
        testCase.expected_metrics.clarity.max
      );

      // 어음명료도 검증
      expect(acousticAnalysis.speech_intelligibility.STI).toBeWithinRange(
        testCase.expected_metrics.speech_intelligibility.min,
        testCase.expected_metrics.speech_intelligibility.max
      );

      // 배경소음 검증
      expect(acousticAnalysis.background_noise.LAeq).toBeLessThanOrEqual(
        testCase.expected_metrics.background_noise.max
      );

      // 주파수별 응답 검증
      expect(acousticAnalysis.frequency_response).toBeDefined();
      expect(acousticAnalysis.frequency_response.length).toBe(31); // 1/3 옥타브 밴드

      console.log(`✅ 음향 분석 완료: ${analysisTime}ms, RT60 ${acousticAnalysis.reverberation_time.RT60}s`);
    });

    test('should optimize acoustic treatment', async () => {
      const concertHall = {
        volume: 15000, // m³
        seats: 1200,
        stage_area: 200,
        ceiling_height: 20,
        target_rt60: 2.0,
        target_clarity: 2.0,
        budget_constraint: 500000 // USD
      };

      const acousticTreatments = [
        { type: 'absorption', material: 'mineral_wool', area: 500, cost: 50 },
        { type: 'diffusion', material: 'wood_diffuser', area: 200, cost: 150 },
        { type: 'reflection', material: 'hard_plaster', area: 800, cost: 30 },
        { type: 'variable', material: 'rotating_panels', area: 100, cost: 300 }
      ];

      const acousticOptimization = await acousticAnalyzer.optimizeAcousticTreatment(
        concertHall,
        acousticTreatments
      );

      // 최적 음향 처리 검증
      expect(acousticOptimization.optimal_treatment).toBeDefined();
      expect(acousticOptimization.achieved_rt60).toBeCloseTo(concertHall.target_rt60, 1);
      expect(acousticOptimization.achieved_clarity).toBeCloseTo(concertHall.target_clarity, 1);

      // 예산 제약 확인
      expect(acousticOptimization.total_cost).toBeLessThanOrEqual(concertHall.budget_constraint);

      // 성능 개선도 검증
      expect(acousticOptimization.performance_improvement).toBeGreaterThan(0.8);

      console.log('✅ 음향 처리 최적화 완료');
    });

    test('should analyze noise control', async () => {
      const mixedUseBuilding = {
        zones: [
          { type: 'retail', noise_limit: 45, area: 500 },
          { type: 'office', noise_limit: 40, area: 1000 },
          { type: 'residential', noise_limit: 35, area: 800 }
        ],
        noise_sources: [
          { type: 'traffic', level: 70, distance: 50 },
          { type: 'hvac', level: 55, location: 'roof' },
          { type: 'mechanical', level: 65, location: 'basement' }
        ]
      };

      const noiseAnalysis = await acousticAnalyzer.analyzeNoiseControl(mixedUseBuilding);

      // 소음 제어 효과 검증
      expect(noiseAnalysis.noise_reduction).toBeDefined();
      noiseAnalysis.noise_reduction.forEach((zone: any) => {
        expect(zone.achieved_level).toBeLessThanOrEqual(zone.target_level);
      });

      // 차음 성능 검증
      expect(noiseAnalysis.sound_insulation).toBeDefined();
      expect(noiseAnalysis.sound_insulation.walls.STC).toBeGreaterThan(45);
      expect(noiseAnalysis.sound_insulation.floors.IIC).toBeLessThan(50);

      // 진동 제어 검증
      expect(noiseAnalysis.vibration_control).toBeDefined();
      expect(noiseAnalysis.vibration_control.isolation_efficiency).toBeGreaterThan(0.8);

      console.log('✅ 소음 제어 분석 완료');
    });
  });

  // =============================================================================
  // 최적화 알고리즘 테스트
  // =============================================================================

  describe('Optimization Algorithms', () => {
    test('should perform single-objective optimization', async () => {
      const optimizationProblem = {
        objective: 'minimize_energy_consumption',
        variables: {
          wall_thickness: { min: 0.15, max: 0.35, step: 0.05 },
          insulation_thickness: { min: 0.05, max: 0.20, step: 0.025 },
          window_area_ratio: { min: 0.2, max: 0.6, step: 0.1 },
          hvac_efficiency: { min: 0.8, max: 0.95, step: 0.05 }
        },
        constraints: {
          max_cost: 1000000,
          min_comfort_score: 0.8,
          min_daylight_factor: 2.0
        }
      };

      const geneticOptimizer = new GeneticOptimizer({
        population_size: 50,
        generations: 100,
        crossover_rate: 0.8,
        mutation_rate: 0.1
      });

      const startTime = Date.now();
      const optimizationResult = await geneticOptimizer.optimize(optimizationProblem);
      const optimizationTime = Date.now() - startTime;

      // 최적화 결과 검증
      expect(optimizationResult.best_solution).toBeDefined();
      expect(optimizationResult.best_fitness).toBeGreaterThan(0);
      expect(optimizationResult.convergence_history).toBeDefined();

      // 제약조건 만족 검증
      expect(optimizationResult.constraint_satisfaction.cost).toBe(true);
      expect(optimizationResult.constraint_satisfaction.comfort).toBe(true);
      expect(optimizationResult.constraint_satisfaction.daylight).toBe(true);

      // 성능 개선 검증
      expect(optimizationResult.improvement_percentage).toBeGreaterThan(10);

      console.log(`✅ 단일목적 최적화 완료: ${optimizationTime}ms, 개선율 ${optimizationResult.improvement_percentage}%`);
    });

    test('should perform multi-objective optimization', async () => {
      const multiObjectiveProblem = {
        objectives: [
          { name: 'minimize_energy', weight: 0.4, direction: 'minimize' },
          { name: 'minimize_cost', weight: 0.3, direction: 'minimize' },
          { name: 'maximize_comfort', weight: 0.3, direction: 'maximize' }
        ],
        variables: {
          building_orientation: { values: [0, 45, 90, 135, 180, 225, 270, 315] },
          window_type: { values: ['double', 'triple', 'smart'] },
          shading_system: { values: ['none', 'fixed', 'dynamic'] },
          hvac_system: { values: ['split', 'vrf', 'central'] }
        }
      };

      const multiOptimizer = new MultiObjectiveOptimizer({
        algorithm: 'NSGA-II',
        population_size: 100,
        generations: 200
      });

      const multiOptResult = await multiOptimizer.optimize(multiObjectiveProblem);

      // 파레토 프론트 검증
      expect(multiOptResult.pareto_front).toBeDefined();
      expect(multiOptResult.pareto_front.length).toBeGreaterThan(10);

      // 다양성 지수 검증
      expect(multiOptResult.diversity_index).toBeGreaterThan(0.5);

      // 수렴성 검증
      expect(multiOptResult.convergence_metric).toBeLessThan(0.01);

      // 최적해 집합 검증
      multiOptResult.pareto_front.forEach((solution: any) => {
        expect(solution.objectives.energy).toBeGreaterThan(0);
        expect(solution.objectives.cost).toBeGreaterThan(0);
        expect(solution.objectives.comfort).toBeWithinRange(0, 1);
      });

      console.log('✅ 다목적 최적화 완료:', multiOptResult.pareto_front.length, '개 파레토 해');
    });

    test('should compare optimization algorithms', async () => {
      const benchmarkProblem = OptimizationBenchmarks.createStandardProblem('building_energy');

      const algorithms = [
        new GeneticOptimizer({ population_size: 50, generations: 100 }),
        new ParticleSwarmOptimizer({ swarm_size: 50, iterations: 100 }),
        new SimulatedAnnealingOptimizer({ initial_temp: 1000, cooling_rate: 0.95 })
      ];

      const algorithmComparison = await Promise.all(
        algorithms.map(async (algorithm) => {
          const startTime = Date.now();
          const result = await algorithm.optimize(benchmarkProblem);
          const endTime = Date.now();

          return {
            algorithm: algorithm.constructor.name,
            best_fitness: result.best_fitness,
            convergence_speed: result.convergence_generation,
            computation_time: endTime - startTime,
            solution_quality: result.solution_quality
          };
        })
      );

      // 알고리즘 성능 비교 검증
      algorithmComparison.forEach(result => {
        expect(result.best_fitness).toBeGreaterThan(0);
        expect(result.convergence_speed).toBeGreaterThan(0);
        expect(result.computation_time).toBeLessThan(30000); // 30초 제한
        expect(result.solution_quality).toBeGreaterThan(0.5);
      });

      // 최고 성능 알고리즘 식별
      const bestAlgorithm = algorithmComparison.reduce((best, current) =>
        current.best_fitness > best.best_fitness ? current : best
      );

      console.log('✅ 최적화 알고리즘 비교 완료. 최고 성능:', bestAlgorithm.algorithm);
    });

    test('should handle optimization constraints effectively', async () => {
      const constrainedProblem = {
        objective: 'maximize_performance',
        variables: {
          design_param_1: { min: 0, max: 100 },
          design_param_2: { min: 0, max: 100 },
          design_param_3: { min: 0, max: 100 }
        },
        constraints: [
          { type: 'inequality', expression: 'x1 + x2 <= 150' },
          { type: 'inequality', expression: 'x2 + x3 <= 120' },
          { type: 'equality', expression: 'x1 + x2 + x3 = 200' }
        ]
      };

      const constraintOptimizer = new GeneticOptimizer({
        constraint_handling: 'penalty_function',
        penalty_coefficient: 1000
      });

      const constrainedResult = await constraintOptimizer.optimize(constrainedProblem);

      // 제약조건 만족 검증
      expect(constrainedResult.constraint_violations).toBe(0);
      expect(constrainedResult.feasible_solutions_ratio).toBeGreaterThan(0.8);

      // 해의 품질 검증
      expect(constrainedResult.best_solution).toBeDefined();
      expect(constrainedResult.solution_feasibility).toBe(true);

      console.log('✅ 제약 최적화 완료');
    });
  });

  // =============================================================================
  // 종합 성능 및 품질 테스트
  // =============================================================================

  describe('Comprehensive Performance Tests', () => {
    test('should perform integrated building performance analysis', async () => {
      const comprehensiveBuilding = {
        type: '친환경 복합시설',
        floors: 8,
        area: 5000,
        programs: ['office', 'retail', 'conference', 'parking'],
        sustainability_targets: {
          energy_rating: 'A+++',
          green_certification: 'LEED_Platinum',
          carbon_neutral: true
        }
      };

      const integratedAnalysis = await performanceAnalyzer.runIntegratedAnalysis(comprehensiveBuilding);

      // 통합 성능 지표 검증
      expect(integratedAnalysis.overall_performance_score).toBeGreaterThan(0.8);
      expect(integratedAnalysis.energy_performance).toBeDefined();
      expect(integratedAnalysis.environmental_performance).toBeDefined();
      expect(integratedAnalysis.comfort_performance).toBeDefined();
      expect(integratedAnalysis.economic_performance).toBeDefined();

      // 상호작용 효과 분석 검증
      expect(integratedAnalysis.interaction_effects).toBeDefined();
      expect(integratedAnalysis.interaction_effects.energy_comfort).toBeDefined();
      expect(integratedAnalysis.interaction_effects.daylight_energy).toBeDefined();

      // 지속가능성 목표 달성도 검증
      expect(integratedAnalysis.sustainability_compliance.energy_rating).toBe('A+++');
      expect(integratedAnalysis.sustainability_compliance.certification_score).toBeGreaterThan(80);

      console.log('✅ 통합 건물 성능 분석 완료');
    });

    test('should validate analysis accuracy with reference data', async () => {
      const referenceBuilding = PerformanceTestData.getValidatedReferenceBuilding('office_medium');
      const referenceResults = PerformanceTestData.getReferenceResults(referenceBuilding.id);

      // 동일한 조건으로 분석 실행
      const analysisResults = await performanceAnalyzer.runComprehensiveAnalysis(referenceBuilding);

      // 에너지 분석 정확도 검증
      const energyAccuracy = Math.abs(
        (analysisResults.energy.total - referenceResults.energy.total) / referenceResults.energy.total
      );
      expect(energyAccuracy).toBeLessThan(0.1); // 10% 오차 이내

      // 자연채광 분석 정확도 검증
      const daylightAccuracy = Math.abs(
        (analysisResults.daylight.average_df - referenceResults.daylight.average_df) / 
        referenceResults.daylight.average_df
      );
      expect(daylightAccuracy).toBeLessThan(0.15); // 15% 오차 이내

      // 열환경 분석 정확도 검증
      const thermalAccuracy = Math.abs(
        analysisResults.thermal.pmv_mean - referenceResults.thermal.pmv_mean
      );
      expect(thermalAccuracy).toBeLessThan(0.2); // PMV 0.2 이내

      console.log('✅ 분석 정확도 검증 완료');
    });

    test('should maintain consistent performance across multiple runs', async () => {
      const testBuilding = performanceTestCases[0].building_model;
      const numRuns = 10;
      const results = [];

      for (let i = 0; i < numRuns; i++) {
        const result = await performanceAnalyzer.analyzeEnergyPerformance(testBuilding);
        results.push(result.total_energy_consumption);
      }

      // 결과 일관성 검증
      const mean = results.reduce((sum, val) => sum + val, 0) / results.length;
      const variance = results.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / results.length;
      const coefficient_of_variation = Math.sqrt(variance) / mean;

      expect(coefficient_of_variation).toBeLessThan(0.02); // 2% 이내 변동

      console.log('✅ 분석 일관성 검증 완료:', `CV = ${(coefficient_of_variation * 100).toFixed(2)}%`);
    });

    test('should scale efficiently with building complexity', async () => {
      const complexityLevels = [
        { elements: 100, time_limit: 2000 },
        { elements: 500, time_limit: 8000 },
        { elements: 1000, time_limit: 15000 },
        { elements: 2000, time_limit: 25000 }
      ];

      const scalabilityResults = [];

      for (const level of complexityLevels) {
        const complexBuilding = PerformanceTestData.createComplexBuilding(level.elements);
        
        const startTime = Date.now();
        const result = await performanceAnalyzer.runQuickAnalysis(complexBuilding);
        const endTime = Date.now();

        const analysisTime = endTime - startTime;
        
        expect(analysisTime).toBeLessThan(level.time_limit);
        
        scalabilityResults.push({
          elements: level.elements,
          time: analysisTime,
          time_per_element: analysisTime / level.elements
        });
      }

      // 선형 스케일링 검증 (시간 복잡도 O(n) 이하)
      const timeIncreaseRatio = scalabilityResults[3].time / scalabilityResults[0].time;
      const elementIncreaseRatio = scalabilityResults[3].elements / scalabilityResults[0].elements;
      
      expect(timeIncreaseRatio).toBeLessThan(elementIncreaseRatio * 1.5); // 50% 오버헤드 허용

      console.log('✅ 확장성 검증 완료');
    });
  });
});