/**
 * 자연어 처리 엔진 단위 테스트
 * 
 * VIBA AI 에이전트의 자연어 이해 및 의도 파악 기능 검증
 * 
 * @version 1.0
 * @author VIBA AI Team
 * @date 2025.07.06
 */

import { describe, test, expect, beforeAll, beforeEach } from '@jest/testing-library/jest-dom';
import { 
  NaturalLanguageProcessor,
  ArchitecturalEntityExtractor,
  IntentClassifier,
  ContextualAnalyzer,
  KoreanLanguageProcessor 
} from '../../src/ai/nlp';

import { 
  ArchitecturalVocabulary,
  BuildingTypeClassifier,
  StyleDetector,
  SpaceTypeAnalyzer 
} from '../../src/ai/nlp/architectural-domains';

// =============================================================================
// 테스트 데이터 및 설정
// =============================================================================

interface NLPTestCase {
  id: string;
  description: string;
  input: string;
  expected: any;
  priority: 'high' | 'medium' | 'low';
  category: string;
}

const architecturalTestCases: NLPTestCase[] = [
  // 기본 건물 유형 인식
  {
    id: 'basic_residential_001',
    description: '단독주택 기본 인식',
    input: '3층 단독주택을 설계해주세요',
    expected: {
      building_type: '단독주택',
      floors: 3,
      intent: 'design_request',
      confidence: 0.9
    },
    priority: 'high',
    category: 'building_type'
  },
  
  {
    id: 'complex_commercial_001',
    description: '복합 상업시설 인식',
    input: '강남에 지상 5층 지하 2층 규모의 오피스텔을 짓고 싶어요. 1층은 상업시설로 하고 2-5층은 주거용으로 계획해주세요',
    expected: {
      building_type: '오피스텔',
      location: '강남',
      floors: { above_ground: 5, below_ground: 2 },
      program: {
        floor_1: '상업시설',
        floors_2_to_5: '주거용'
      },
      intent: 'design_request',
      confidence: 0.85
    },
    priority: 'high',
    category: 'complex_program'
  },

  // 건축 스타일 인식
  {
    id: 'style_modern_001',
    description: '모던 스타일 인식',
    input: '미니멀하고 현대적인 스타일의 카페를 만들어주세요. 깔끔한 선과 큰 창문이 특징이었으면 좋겠어요',
    expected: {
      building_type: '카페',
      style: ['미니멀', '현대적', '모던'],
      design_features: ['깔끔한 선', '큰 창문'],
      intent: 'design_request',
      confidence: 0.9
    },
    priority: 'high',
    category: 'style_recognition'
  },

  {
    id: 'style_traditional_001',
    description: '전통 스타일 인식',
    input: '한옥 스타일로 게스트하우스를 설계해주세요. 마당이 있고 온돌 난방이 들어갔으면 좋겠어요',
    expected: {
      building_type: '게스트하우스',
      style: ['한옥', '전통'],
      features: ['마당', '온돌'],
      heating_system: '온돌',
      intent: 'design_request',
      confidence: 0.95
    },
    priority: 'high',
    category: 'traditional_architecture'
  },

  // 기술적 요구사항 인식
  {
    id: 'technical_specs_001',
    description: '기술적 사양 인식',
    input: 'RC구조로 내진설계를 적용하고 커튼월 시스템을 사용한 20층 오피스 빌딩을 설계해주세요',
    expected: {
      building_type: '오피스 빌딩',
      floors: 20,
      structure_type: 'RC구조',
      seismic_design: true,
      facade_system: '커튼월',
      intent: 'design_request',
      confidence: 0.9
    },
    priority: 'high',
    category: 'technical_requirements'
  },

  // 지속가능성 요구사항
  {
    id: 'sustainability_001',
    description: '친환경 건축 요구사항 인식',
    input: '친환경 인증을 받을 수 있는 패시브하우스로 설계해주세요. 태양광 패널과 빗물 수집 시설도 포함해주세요',
    expected: {
      building_type: '패시브하우스',
      certifications: ['친환경'],
      sustainability_features: ['태양광 패널', '빗물 수집'],
      energy_efficiency: 'passive_house',
      intent: 'design_request',
      confidence: 0.9
    },
    priority: 'high',
    category: 'sustainability'
  },

  // 복잡한 프로그램 분석
  {
    id: 'complex_program_001',
    description: '복잡한 프로그램 분석',
    input: '다목적 문화센터를 설계해주세요. 1층에는 로비와 카페, 2층에는 도서관과 전시공간, 3층에는 강의실과 세미나실, 옥상에는 야외 공연장을 만들어주세요',
    expected: {
      building_type: '문화센터',
      program: {
        floor_1: ['로비', '카페'],
        floor_2: ['도서관', '전시공간'],
        floor_3: ['강의실', '세미나실'],
        rooftop: ['야외 공연장']
      },
      building_function: '다목적',
      intent: 'design_request',
      confidence: 0.85
    },
    priority: 'medium',
    category: 'complex_program'
  },

  // 예산 및 일정 정보
  {
    id: 'budget_schedule_001',
    description: '예산 및 일정 정보 추출',
    input: '예산 30억원 내에서 내년 12월까지 완공 가능한 소규모 호텔을 설계해주세요',
    expected: {
      building_type: '호텔',
      scale: '소규모',
      budget: {
        amount: 3000000000,
        currency: 'KRW'
      },
      schedule: {
        completion_date: '내년 12월',
        constraint: 'completion_deadline'
      },
      intent: 'design_request',
      confidence: 0.8
    },
    priority: 'medium',
    category: 'project_constraints'
  },

  // 애매한 표현 처리
  {
    id: 'ambiguous_001',
    description: '애매한 표현 처리',
    input: '큰 건물 하나 만들어주세요',
    expected: {
      building_type: 'unknown',
      scale: '큰',
      intent: 'design_request',
      confidence: 0.3,
      clarification_needed: [
        '건물 유형을 구체적으로 알려주세요',
        '층수나 면적 등 구체적인 규모를 알려주세요',
        '건물의 용도나 기능을 설명해주세요'
      ]
    },
    priority: 'high',
    category: 'ambiguous_input'
  },

  // 수정 요청 처리
  {
    id: 'modification_001',
    description: '기존 설계 수정 요청',
    input: '방금 설계한 건물에서 창문을 더 크게 만들고 2층에 발코니를 추가해주세요',
    expected: {
      intent: 'modification_request',
      modifications: [
        { element: '창문', change: '크기 증가' },
        { location: '2층', addition: '발코니' }
      ],
      context_required: true,
      confidence: 0.9
    },
    priority: 'medium',
    category: 'modification_request'
  },

  // 질문 및 정보 요청
  {
    id: 'information_request_001',
    description: '정보 요청 처리',
    input: '이 건물의 에너지 효율은 어떻게 될까요?',
    expected: {
      intent: 'information_request',
      query_type: 'performance_analysis',
      subject: 'energy_efficiency',
      context_required: true,
      confidence: 0.95
    },
    priority: 'medium',
    category: 'information_request'
  }
];

// =============================================================================
// NLP 엔진 단위 테스트
// =============================================================================

describe('Natural Language Processing Engine Tests', () => {
  let nlpProcessor: NaturalLanguageProcessor;
  let entityExtractor: ArchitecturalEntityExtractor;
  let intentClassifier: IntentClassifier;
  let contextAnalyzer: ContextualAnalyzer;
  let koreanProcessor: KoreanLanguageProcessor;

  beforeAll(async () => {
    // NLP 컴포넌트 초기화
    nlpProcessor = new NaturalLanguageProcessor({
      language: 'ko',
      domain: 'architecture',
      model_path: '/models/architectural-nlp-ko-v1.0'
    });

    entityExtractor = new ArchitecturalEntityExtractor({
      vocabulary_path: '/data/architectural-vocabulary-ko.json',
      embeddings_path: '/models/architectural-embeddings-ko.bin'
    });

    intentClassifier = new IntentClassifier({
      model_path: '/models/intent-classifier-ko.pkl',
      confidence_threshold: 0.7
    });

    contextAnalyzer = new ContextualAnalyzer({
      context_window: 10,
      memory_size: 100
    });

    koreanProcessor = new KoreanLanguageProcessor({
      tokenizer: 'mecab',
      pos_tagger: 'mecab',
      ner_model: 'bert-base-multilingual-cased'
    });

    // 모델 로딩
    await Promise.all([
      nlpProcessor.initialize(),
      entityExtractor.loadVocabulary(),
      intentClassifier.loadModel(),
      koreanProcessor.initialize()
    ]);

    console.log('✅ NLP 컴포넌트 초기화 완료');
  });

  beforeEach(() => {
    // 각 테스트 전 컨텍스트 초기화
    contextAnalyzer.clearContext();
  });

  // =============================================================================
  // 기본 엔티티 추출 테스트
  // =============================================================================

  describe('Architectural Entity Extraction', () => {
    test('should extract building types correctly', async () => {
      const buildingTypeTests = architecturalTestCases.filter(
        tc => tc.category === 'building_type' || tc.category === 'complex_program'
      );

      for (const testCase of buildingTypeTests) {
        const result = await entityExtractor.extractBuildingType(testCase.input);
        
        expect(result.building_type).toBe(testCase.expected.building_type);
        expect(result.confidence).toBeGreaterThanOrEqual(testCase.expected.confidence - 0.1);
        
        // 층수 정보가 있는 경우 검증
        if (testCase.expected.floors) {
          if (typeof testCase.expected.floors === 'number') {
            expect(result.floors).toBe(testCase.expected.floors);
          } else {
            expect(result.floors).toMatchObject(testCase.expected.floors);
          }
        }

        console.log(`✅ ${testCase.description}: ${result.building_type} (신뢰도: ${result.confidence})`);
      }
    });

    test('should recognize architectural styles and features', async () => {
      const styleTests = architecturalTestCases.filter(
        tc => tc.category === 'style_recognition' || tc.category === 'traditional_architecture'
      );

      for (const testCase of styleTests) {
        const result = await entityExtractor.extractStyleFeatures(testCase.input);
        
        // 스타일 인식 검증
        if (testCase.expected.style) {
          const expectedStyles = Array.isArray(testCase.expected.style) 
            ? testCase.expected.style 
            : [testCase.expected.style];
          
          expectedStyles.forEach(expectedStyle => {
            expect(result.styles).toContain(expectedStyle);
          });
        }

        // 디자인 특징 인식 검증
        if (testCase.expected.design_features) {
          testCase.expected.design_features.forEach((feature: string) => {
            expect(result.design_features).toContain(feature);
          });
        }

        // 건축적 특징 인식 검증
        if (testCase.expected.features) {
          testCase.expected.features.forEach((feature: string) => {
            expect(result.architectural_features).toContain(feature);
          });
        }

        expect(result.confidence).toBeGreaterThanOrEqual(testCase.expected.confidence - 0.1);
        
        console.log(`✅ ${testCase.description}: 스타일 ${result.styles.join(', ')} (신뢰도: ${result.confidence})`);
      }
    });

    test('should extract technical specifications', async () => {
      const technicalTests = architecturalTestCases.filter(
        tc => tc.category === 'technical_requirements'
      );

      for (const testCase of technicalTests) {
        const result = await entityExtractor.extractTechnicalSpecs(testCase.input);
        
        // 구조 시스템 검증
        if (testCase.expected.structure_type) {
          expect(result.structure_type).toBe(testCase.expected.structure_type);
        }

        // 내진설계 여부 검증
        if (testCase.expected.seismic_design !== undefined) {
          expect(result.seismic_design).toBe(testCase.expected.seismic_design);
        }

        // 외장 시스템 검증
        if (testCase.expected.facade_system) {
          expect(result.facade_system).toBe(testCase.expected.facade_system);
        }

        expect(result.confidence).toBeGreaterThanOrEqual(testCase.expected.confidence - 0.1);
        
        console.log(`✅ ${testCase.description}: 구조 ${result.structure_type}, 외장 ${result.facade_system}`);
      }
    });

    test('should recognize sustainability requirements', async () => {
      const sustainabilityTests = architecturalTestCases.filter(
        tc => tc.category === 'sustainability'
      );

      for (const testCase of sustainabilityTests) {
        const result = await entityExtractor.extractSustainabilityFeatures(testCase.input);
        
        // 인증 요구사항 검증
        if (testCase.expected.certifications) {
          testCase.expected.certifications.forEach((cert: string) => {
            expect(result.certifications).toContain(cert);
          });
        }

        // 지속가능성 특징 검증
        if (testCase.expected.sustainability_features) {
          testCase.expected.sustainability_features.forEach((feature: string) => {
            expect(result.sustainability_features).toContain(feature);
          });
        }

        // 에너지 효율 등급 검증
        if (testCase.expected.energy_efficiency) {
          expect(result.energy_efficiency).toBe(testCase.expected.energy_efficiency);
        }

        expect(result.confidence).toBeGreaterThanOrEqual(testCase.expected.confidence - 0.1);
        
        console.log(`✅ ${testCase.description}: 인증 ${result.certifications.join(', ')}`);
      }
    });

    test('should parse complex spatial programs', async () => {
      const programTests = architecturalTestCases.filter(
        tc => tc.category === 'complex_program'
      );

      for (const testCase of programTests) {
        const result = await entityExtractor.extractSpatialProgram(testCase.input);
        
        // 프로그램 구조 검증
        if (testCase.expected.program) {
          Object.keys(testCase.expected.program).forEach(floor => {
            expect(result.program).toHaveProperty(floor);
            
            const expectedSpaces = testCase.expected.program[floor];
            const actualSpaces = result.program[floor];
            
            if (Array.isArray(expectedSpaces)) {
              expectedSpaces.forEach(space => {
                expect(actualSpaces).toContain(space);
              });
            } else {
              expect(actualSpaces).toBe(expectedSpaces);
            }
          });
        }

        expect(result.confidence).toBeGreaterThanOrEqual(testCase.expected.confidence - 0.1);
        
        console.log(`✅ ${testCase.description}: 프로그램 분석 완료`);
      }
    });

    test('should extract project constraints (budget, schedule)', async () => {
      const constraintTests = architecturalTestCases.filter(
        tc => tc.category === 'project_constraints'
      );

      for (const testCase of constraintTests) {
        const result = await entityExtractor.extractProjectConstraints(testCase.input);
        
        // 예산 정보 검증
        if (testCase.expected.budget) {
          expect(result.budget.amount).toBe(testCase.expected.budget.amount);
          expect(result.budget.currency).toBe(testCase.expected.budget.currency);
        }

        // 일정 정보 검증
        if (testCase.expected.schedule) {
          expect(result.schedule.completion_date).toBe(testCase.expected.schedule.completion_date);
        }

        // 규모 정보 검증
        if (testCase.expected.scale) {
          expect(result.scale).toBe(testCase.expected.scale);
        }

        expect(result.confidence).toBeGreaterThanOrEqual(testCase.expected.confidence - 0.1);
        
        console.log(`✅ ${testCase.description}: 예산 ${result.budget?.amount || 'N/A'}, 일정 ${result.schedule?.completion_date || 'N/A'}`);
      }
    });
  });

  // =============================================================================
  // 의도 분류 테스트
  // =============================================================================

  describe('Intent Classification', () => {
    test('should classify design requests correctly', async () => {
      const designRequests = architecturalTestCases.filter(
        tc => tc.expected.intent === 'design_request'
      );

      for (const testCase of designRequests) {
        const result = await intentClassifier.classifyIntent(testCase.input);
        
        expect(result.intent).toBe('design_request');
        expect(result.confidence).toBeGreaterThanOrEqual(0.7);
        
        // 의도별 세부 분류 검증
        expect(result.sub_intent).toBeOneOf([
          'new_design', 'design_exploration', 'concept_development'
        ]);
        
        console.log(`✅ 설계 요청 의도 분류: ${result.intent}/${result.sub_intent} (신뢰도: ${result.confidence})`);
      }
    });

    test('should classify modification requests correctly', async () => {
      const modificationRequests = architecturalTestCases.filter(
        tc => tc.expected.intent === 'modification_request'
      );

      for (const testCase of modificationRequests) {
        const result = await intentClassifier.classifyIntent(testCase.input);
        
        expect(result.intent).toBe('modification_request');
        expect(result.confidence).toBeGreaterThanOrEqual(0.7);
        
        // 수정 유형 분류 검증
        expect(result.modification_type).toBeOneOf([
          'element_change', 'addition', 'removal', 'adjustment'
        ]);
        
        console.log(`✅ 수정 요청 의도 분류: ${result.modification_type} (신뢰도: ${result.confidence})`);
      }
    });

    test('should classify information requests correctly', async () => {
      const infoRequests = architecturalTestCases.filter(
        tc => tc.expected.intent === 'information_request'
      );

      for (const testCase of infoRequests) {
        const result = await intentClassifier.classifyIntent(testCase.input);
        
        expect(result.intent).toBe('information_request');
        expect(result.confidence).toBeGreaterThanOrEqual(0.7);
        
        // 정보 요청 유형 검증
        if (testCase.expected.query_type) {
          expect(result.query_type).toBe(testCase.expected.query_type);
        }
        
        console.log(`✅ 정보 요청 의도 분류: ${result.query_type} (신뢰도: ${result.confidence})`);
      }
    });

    test('should handle ambiguous inputs with clarification requests', async () => {
      const ambiguousTests = architecturalTestCases.filter(
        tc => tc.category === 'ambiguous_input'
      );

      for (const testCase of ambiguousTests) {
        const result = await intentClassifier.classifyIntent(testCase.input);
        
        expect(result.intent).toBe('design_request');
        expect(result.confidence).toBeLessThan(0.5); // 낮은 신뢰도
        expect(result.needs_clarification).toBe(true);
        
        // 명확화 질문 검증
        expect(result.clarification_questions).toBeDefined();
        expect(result.clarification_questions.length).toBeGreaterThan(0);
        
        if (testCase.expected.clarification_needed) {
          testCase.expected.clarification_needed.forEach((question: string) => {
            expect(result.clarification_questions.some((q: any) => 
              q.includes(question) || question.includes(q)
            )).toBe(true);
          });
        }
        
        console.log(`✅ 애매한 입력 처리: ${result.clarification_questions.length}개 명확화 질문 생성`);
      }
    });
  });

  // =============================================================================
  // 컨텍스트 분석 테스트
  // =============================================================================

  describe('Contextual Analysis', () => {
    test('should maintain conversation context across multiple turns', async () => {
      const conversationTurns = [
        {
          input: '3층 단독주택을 설계해주세요',
          expected_context: { building_type: '단독주택', floors: 3 }
        },
        {
          input: '거실을 더 넓게 만들어주세요',
          expected_context: { 
            building_type: '단독주택', 
            floors: 3,
            modification: { space: '거실', change: '크기 증가' }
          }
        },
        {
          input: '2층에 발코니도 추가해주세요',
          expected_context: {
            building_type: '단독주택',
            floors: 3,
            modifications: [
              { space: '거실', change: '크기 증가' },
              { location: '2층', addition: '발코니' }
            ]
          }
        }
      ];

      let cumulativeContext = {};

      for (const [index, turn] of conversationTurns.entries()) {
        const result = await contextAnalyzer.analyzeWithContext(
          turn.input, 
          cumulativeContext
        );
        
        // 컨텍스트 누적 확인
        expect(result.context).toMatchObject(turn.expected_context);
        
        // 참조 해결 확인 (2번째 턴부터)
        if (index > 0) {
          expect(result.resolved_references).toBeDefined();
          expect(result.context_continuity_score).toBeGreaterThan(0.8);
        }
        
        cumulativeContext = result.context;
        
        console.log(`✅ 컨텍스트 분석 턴 ${index + 1}: 연속성 점수 ${result.context_continuity_score || 'N/A'}`);
      }
    });

    test('should resolve anaphoric references correctly', async () => {
      const referenceTests = [
        {
          context: { building_type: '사무소', floors: 5 },
          input: '이 건물의 1층에 로비를 만들어주세요',
          expected_resolution: { 
            '이 건물': { type: 'building', reference: '사무소' },
            '1층': { type: 'floor', reference: 'floor_1' }
          }
        },
        {
          context: { building_type: '주택', rooms: ['거실', '주방', '침실'] },
          input: '거실 옆에 있는 방을 더 크게 만들어주세요',
          expected_resolution: {
            '거실': { type: 'room', reference: '거실' },
            '옆에 있는 방': { type: 'room', reference: 'adjacent_room' }
          }
        }
      ];

      for (const testCase of referenceTests) {
        const result = await contextAnalyzer.resolveReferences(
          testCase.input,
          testCase.context
        );
        
        // 참조 해결 검증
        Object.keys(testCase.expected_resolution).forEach(reference => {
          expect(result.resolved_references).toHaveProperty(reference);
          expect(result.resolved_references[reference].type).toBe(
            testCase.expected_resolution[reference].type
          );
        });
        
        expect(result.resolution_confidence).toBeGreaterThan(0.7);
        
        console.log(`✅ 참조 해결: ${Object.keys(result.resolved_references).length}개 참조 해결됨`);
      }
    });

    test('should track design evolution and changes', async () => {
      const designEvolution = [
        {
          stage: 'initial',
          input: '모던 스타일 카페를 설계해주세요',
          expected_state: { building_type: '카페', style: '모던' }
        },
        {
          stage: 'refinement',
          input: '외부에 테라스 좌석도 추가해주세요',
          expected_state: { 
            building_type: '카페', 
            style: '모던',
            outdoor_spaces: ['테라스']
          }
        },
        {
          stage: 'modification',
          input: '스타일을 빈티지로 바꿔주세요',
          expected_state: {
            building_type: '카페',
            style: '빈티지', // 스타일 변경
            outdoor_spaces: ['테라스']
          }
        }
      ];

      let evolutionHistory = [];

      for (const stage of designEvolution) {
        const result = await contextAnalyzer.trackDesignEvolution(
          stage.input,
          evolutionHistory
        );
        
        // 설계 상태 추적 검증
        expect(result.current_state).toMatchObject(stage.expected_state);
        
        // 변경 이력 추적 검증
        if (stage.stage === 'modification') {
          expect(result.changes_detected).toBe(true);
          expect(result.change_summary).toContain('스타일');
        }
        
        evolutionHistory.push({
          stage: stage.stage,
          input: stage.input,
          state: result.current_state,
          timestamp: new Date().toISOString()
        });
        
        console.log(`✅ 설계 진화 추적 - ${stage.stage}: ${result.changes_detected ? '변경 감지됨' : '누적 개선'}`);
      }
    });
  });

  // =============================================================================
  // 한국어 특화 처리 테스트
  // =============================================================================

  describe('Korean Language Specific Processing', () => {
    test('should handle Korean architectural terminology correctly', async () => {
      const koreanTerms = [
        {
          input: '한옥 양식의 전통 가옥을 지어주세요',
          expected_terms: ['한옥', '전통 가옥'],
          expected_style: '전통'
        },
        {
          input: '아파트 단지 내 커뮤니티 시설을 설계해주세요',
          expected_terms: ['아파트 단지', '커뮤니티 시설'],
          expected_type: '커뮤니티 시설'
        },
        {
          input: '지하주차장이 있는 다세대주택을 만들어주세요',
          expected_terms: ['지하주차장', '다세대주택'],
          expected_features: ['지하주차장']
        }
      ];

      for (const testCase of koreanTerms) {
        const result = await koreanProcessor.processArchitecturalTerms(testCase.input);
        
        // 한국어 건축 용어 인식 검증
        testCase.expected_terms.forEach(term => {
          expect(result.recognized_terms).toContain(term);
        });
        
        // 용어 분류 정확성 검증
        expect(result.term_classifications).toBeDefined();
        expect(result.confidence).toBeGreaterThan(0.8);
        
        console.log(`✅ 한국어 건축 용어 처리: ${result.recognized_terms.join(', ')}`);
      }
    });

    test('should parse Korean numbers and units correctly', async () => {
      const numberTests = [
        {
          input: '삼십 평 규모의 주택을 설계해주세요',
          expected: { area: 30, unit: '평' }
        },
        {
          input: '높이 십 미터인 건물을 만들어주세요',
          expected: { height: 10, unit: '미터' }
        },
        {
          input: '오층 건물에 지하 이층을 추가해주세요',
          expected: { 
            above_ground: 5, 
            below_ground: 2 
          }
        }
      ];

      for (const testCase of numberTests) {
        const result = await koreanProcessor.parseKoreanNumbers(testCase.input);
        
        // 한국어 숫자 파싱 검증
        Object.keys(testCase.expected).forEach(key => {
          expect(result[key]).toBe(testCase.expected[key]);
        });
        
        console.log(`✅ 한국어 숫자 파싱: ${JSON.stringify(result)}`);
      }
    });

    test('should handle Korean honorifics and politeness levels', async () => {
      const politenessTests = [
        {
          input: '집을 설계해주세요',
          expected_level: 'polite',
          expected_formality: 'formal'
        },
        {
          input: '건물 좀 만들어줘',
          expected_level: 'casual',
          expected_formality: 'informal'
        },
        {
          input: '주택을 설계해주시겠습니까?',
          expected_level: 'very_polite',
          expected_formality: 'very_formal'
        }
      ];

      for (const testCase of politenessTests) {
        const result = await koreanProcessor.analyzePoliteness(testCase.input);
        
        expect(result.politeness_level).toBe(testCase.expected_level);
        expect(result.formality).toBe(testCase.expected_formality);
        
        console.log(`✅ 한국어 경어 분석: ${result.politeness_level}/${result.formality}`);
      }
    });
  });

  // =============================================================================
  // 성능 및 정확도 테스트
  // =============================================================================

  describe('Performance and Accuracy Tests', () => {
    test('should process inputs within acceptable time limits', async () => {
      const performanceTests = [
        { input: '간단한 주택 설계', max_time: 100 }, // 100ms
        { input: '복잡한 상업시설 프로그램 분석', max_time: 500 }, // 500ms
        { input: '매우 긴 텍스트를 포함한 상세한 설계 요구사항 ' + 'A'.repeat(1000), max_time: 1000 } // 1s
      ];

      for (const testCase of performanceTests) {
        const startTime = Date.now();
        
        const result = await nlpProcessor.process(testCase.input);
        
        const processingTime = Date.now() - startTime;
        
        expect(processingTime).toBeLessThan(testCase.max_time);
        expect(result).toBeDefined();
        
        console.log(`✅ 성능 테스트: ${processingTime}ms (제한: ${testCase.max_time}ms)`);
      }
    });

    test('should maintain high accuracy across test suite', async () => {
      let totalTests = 0;
      let accurateResults = 0;

      const highPriorityTests = architecturalTestCases.filter(
        tc => tc.priority === 'high'
      );

      for (const testCase of highPriorityTests) {
        const result = await nlpProcessor.process(testCase.input);
        
        totalTests++;
        
        // 기본 정확도 검증 (의도 분류)
        if (result.intent === testCase.expected.intent) {
          accurateResults++;
        }
        
        // 신뢰도 임계값 검증
        expect(result.confidence).toBeGreaterThan(0.5);
      }

      const accuracy = accurateResults / totalTests;
      expect(accuracy).toBeGreaterThan(0.9); // 90% 이상 정확도
      
      console.log(`✅ 전체 정확도: ${(accuracy * 100).toFixed(1)}% (${accurateResults}/${totalTests})`);
    });

    test('should handle edge cases gracefully', async () => {
      const edgeCases = [
        '', // 빈 문자열
        '   ', // 공백만
        '!@#$%', // 특수문자만
        'abcdefg', // 영어만
        '123456', // 숫자만
        '가나다라마바사아자차카타파하', // 의미없는 한글
        'A'.repeat(10000) // 매우 긴 텍스트
      ];

      for (const edgeCase of edgeCases) {
        const result = await nlpProcessor.process(edgeCase);
        
        // 에러 없이 처리되어야 함
        expect(result).toBeDefined();
        expect(result.error).toBeUndefined();
        
        // 낮은 신뢰도와 명확화 요청이 있어야 함
        if (edgeCase.trim().length > 0) {
          expect(result.confidence).toBeLessThan(0.5);
          expect(result.needs_clarification).toBe(true);
        }
        
        console.log(`✅ 엣지 케이스 처리: "${edgeCase.substring(0, 20)}..." - 신뢰도 ${result.confidence}`);
      }
    });
  });
});