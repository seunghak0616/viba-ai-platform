/**
 * NLP Routes
 * 자연어 처리 API 엔드포인트
 */
import express from 'express';
import { body, validationResult, query } from 'express-validator';
import { PrismaClient } from '@prisma/client';
import authMiddleware from '../middleware/auth.js';
import catchAsync from '../utils/catchAsync.js';
import logger from '../utils/logger.js';
import openaiService from '../services/openaiService.js';

const router = express.Router();
const prisma = new PrismaClient();

// 입력 검증 미들웨어
const checkValidation = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ 
      success: false, 
      errors: errors.array() 
    });
  }
  next();
};

/**
 * POST /api/nlp/parse
 * 자연어를 BIM 파라미터로 변환 (기존 호환성 유지)
 */
router.post('/parse', [
  body('text').isLength({ min: 1, max: 1000 }).withMessage('텍스트는 1-1000자 사이여야 합니다.'),
  body('language').optional().isIn(['ko', 'en']).withMessage('지원되는 언어는 ko, en입니다.')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: '입력 데이터가 올바르지 않습니다.',
        errors: errors.array()
      });
    }

    const { text, language = 'ko' } = req.body;

    // OpenAI를 사용한 향상된 자연어 분석
    const openaiResult = await openaiService.convertToBIMParameters(text, language);
    
    // 기존 형식과 호환되도록 변환
    const analysis = {
      buildingType: geminiResult.buildingType,
      extractedArea: geminiResult.totalArea.value,
      confidence: geminiResult.confidence,
      rooms: geminiResult.rooms,
      orientations: geminiResult.extractedFeatures.orientations,
      roomTypes: geminiResult.extractedFeatures.roomTypes,
      areaKeywords: geminiResult.extractedFeatures.areaKeywords,
      buildingKeywords: geminiResult.extractedFeatures.buildingKeywords
    };
    
    // 기존 형식과 호환되는 결과 생성
    const mockResult = {
      buildingType: analysis.buildingType,
      totalArea: { 
        value: analysis.extractedArea || 30, 
        unit: '평', 
        confidence: analysis.confidence 
      },
      rooms: analysis.rooms || [
        { type: '거실', count: 1, orientation: '남향', area: 15 },
        { type: '침실', count: 2, area: 10 },
        { type: '주방', count: 1, area: 8 },
        { type: '화장실', count: 1, area: 4 }
      ],
      confidence: analysis.confidence,
      extractedFeatures: {
        orientations: analysis.orientations || ['남향'],
        roomTypes: analysis.roomTypes || ['거실', '침실', '주방', '화장실'],
        areaKeywords: analysis.areaKeywords || ['30평'],
        buildingKeywords: analysis.buildingKeywords || ['아파트']
      }
    };

    res.json({
      success: true,
      message: '자연어 처리가 완료되었습니다.',
      data: {
        input: {
          text,
          language
        },
        result: mockResult
      }
    });
  } catch (error) {
    logger.error('NLP parse error:', error);
    res.status(500).json({
      success: false,
      message: '자연어 처리 중 오류가 발생했습니다.'
    });
  }
});

/**
 * @route   POST /api/nlp/process
 * @desc    자연어 입력을 처리하여 BIM 모델 생성 요청으로 변환
 * @access  Private
 */
router.post('/process', 
  authMiddleware,
  [
    body('naturalLanguageInput')
      .isString()
      .isLength({ min: 10, max: 1000 })
      .withMessage('자연어 입력은 10자 이상 1000자 이하여야 합니다.'),
    body('projectId')
      .optional()
      .isString()
      .withMessage('프로젝트 ID는 문자열이어야 합니다.')
  ],
  checkValidation,
  catchAsync(async (req, res) => {
    const { naturalLanguageInput, projectId } = req.body;
    const userId = req.user.id;

    // 자연어 처리 로깅
    logger.nlp('자연어 입력 처리 시작', {
      userId,
      projectId,
      inputLength: naturalLanguageInput.length,
      preview: naturalLanguageInput.substring(0, 100)
    });

    try {
      // 1. Gemini AI를 사용한 자연어 입력 분석
      const geminiResult = await openaiService.convertToBIMParameters(naturalLanguageInput, 'ko');
      
      // 기존 형식과 호환되도록 변환
      const analysis = {
        suggestedName: geminiResult.suggestedName,
        description: geminiResult.description,
        buildingType: geminiResult.buildingType,
        extractedKeywords: Object.values(geminiResult.extractedFeatures).flat(),
        confidence: geminiResult.confidence,
        extractedArea: geminiResult.totalArea.value,
        rooms: geminiResult.rooms,
        orientations: geminiResult.extractedFeatures.orientations,
        roomTypes: geminiResult.extractedFeatures.roomTypes,
        areaKeywords: geminiResult.extractedFeatures.areaKeywords,
        buildingKeywords: geminiResult.extractedFeatures.buildingKeywords,
        // Gemini 추가 정보
        style: geminiResult.style,
        location: geminiResult.location,
        constraints: geminiResult.constraints
      };
      
      // 2. 프로젝트 연결 (선택사항)
      let project = null;
      if (projectId) {
        project = await prisma.project.findUnique({
          where: { 
            id: projectId,
            userId: userId
          }
        });
        
        if (!project) {
          return res.status(404).json({
            success: false,
            message: '프로젝트를 찾을 수 없습니다.'
          });
        }
      }

      // 3. BIM 모델 생성 요청 생성
      // 먼저 프로젝트가 없으면 기본 프로젝트 생성
      let targetProjectId = projectId;
      if (!targetProjectId) {
        const defaultProject = await prisma.project.create({
          data: {
            name: `${analysis.suggestedName} - 프로젝트`,
            description: `자연어 입력을 통해 생성된 프로젝트: ${analysis.description}`,
            status: 'PLANNING',
            userId: userId
          }
        });
        targetProjectId = defaultProject.id;
      }

      const bimRequest = await prisma.bimModel.create({
        data: {
          name: analysis.suggestedName,
          description: analysis.description,
          type: analysis.buildingType,
          naturalLanguageInput: naturalLanguageInput,
          metadata: JSON.stringify({
            analysis: analysis,
            createdAt: new Date().toISOString(),
            userId: userId,
            source: 'natural_language'
          }),
          userId: userId,
          projectId: targetProjectId
        }
      });

      logger.nlp('BIM 모델 생성 요청 완료', {
        userId,
        bimModelId: bimRequest.id,
        buildingType: analysis.buildingType,
        suggestedName: analysis.suggestedName
      });

      res.status(201).json({
        success: true,
        data: {
          bimModel: bimRequest,
          analysis: analysis
        },
        message: '자연어 입력이 성공적으로 처리되었습니다.'
      });

    } catch (error) {
      logger.error('자연어 처리 중 오류 발생', {
        userId,
        error: error.message,
        stack: error.stack
      });

      res.status(500).json({
        success: false,
        message: '자연어 처리 중 오류가 발생했습니다.'
      });
    }
  })
);

/**
 * @route   GET /api/nlp/history
 * @desc    사용자의 자연어 처리 히스토리 조회
 * @access  Private
 */
router.get('/history',
  authMiddleware,
  [
    query('page').optional().isInt({ min: 1 }).withMessage('페이지는 1 이상이어야 합니다.'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('제한은 1-100 사이여야 합니다.')
  ],
  checkValidation,
  catchAsync(async (req, res) => {
    const userId = req.user.id;
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const skip = (page - 1) * limit;

    const [bimModels, totalCount] = await Promise.all([
      prisma.bimModel.findMany({
        where: { 
          userId: userId,
          naturalLanguageInput: { not: null }
        },
        select: {
          id: true,
          name: true,
          description: true,
          type: true,
          naturalLanguageInput: true,
          createdAt: true,
          project: {
            select: {
              id: true,
              name: true
            }
          }
        },
        orderBy: { createdAt: 'desc' },
        skip: skip,
        take: limit
      }),
      prisma.bimModel.count({
        where: { 
          userId: userId,
          naturalLanguageInput: { not: null }
        }
      })
    ]);

    res.json({
      success: true,
      data: {
        bimModels,
        pagination: {
          page,
          limit,
          totalCount,
          totalPages: Math.ceil(totalCount / limit)
        }
      }
    });
  })
);

/**
 * @route   GET /api/nlp/suggestions
 * @desc    자연어 입력을 위한 예시 텍스트 제공
 * @access  Private
 */
router.get('/suggestions',
  authMiddleware,
  catchAsync(async (req, res) => {
    const suggestions = [
      {
        category: '주거 건물',
        examples: [
          '서울 강남구에 20평 규모의 아파트 설계해주세요.',
          '3층 단독주택을 현대적인 스타일로 만들어주세요.',
          '침실 2개, 화장실 2개가 있는 빌라를 설계해주세요.',
          '원룸형 오피스텔 인테리어를 효율적으로 배치해주세요.'
        ]
      },
      {
        category: '상업 건물',
        examples: [
          '카페 매장을 위한 인테리어 설계를 해주세요.',
          '소규모 사무실 공간을 효율적으로 배치해주세요.',
          '쇼핑몰 내부 매장 레이아웃을 만들어주세요.',
          '레스토랑 주방과 홀 공간을 최적화해주세요.'
        ]
      },
      {
        category: '공공 건물',
        examples: [
          '학교 교실 배치를 최적화해주세요.',
          '병원 외래 진료실 설계를 해주세요.',
          '도서관 열람실과 서가 배치를 계획해주세요.',
          '체육관 내부 운동시설 배치를 설계해주세요.'
        ]
      },
      {
        category: '산업 건물',
        examples: [
          '공장 내 생산라인 배치를 효율적으로 설계해주세요.',
          '창고 공간을 최대한 활용할 수 있게 계획해주세요.',
          '연구소 실험실 공간 배치를 안전하게 설계해주세요.',
          '물류센터 분류 시설을 효율적으로 배치해주세요.'
        ]
      }
    ];

    res.json({
      success: true,
      data: suggestions
    });
  })
);

/**
 * POST /api/nlp/validate
 * BIM 설계 검증
 */
router.post('/validate', [
  body('bimData').isObject().withMessage('BIM 데이터는 객체여야 합니다.')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        success: false,
        message: '입력 데이터가 올바르지 않습니다.',
        errors: errors.array()
      });
    }

    const { bimData } = req.body;

    // Gemini AI를 사용한 향상된 검증 결과
    const validationResult = await openaiService.validateAndOptimizeBIM(bimData, 'ko');

    res.json({
      success: true,
      message: 'BIM 설계 검증이 완료되었습니다.',
      data: {
        validation: validationResult
      }
    });
  } catch (error) {
    logger.error('NLP validate error:', error);
    res.status(500).json({
      success: false,
      message: 'BIM 설계 검증 중 오류가 발생했습니다.'
    });
  }
});

/**
 * @route   POST /api/nlp/enhance
 * @desc    Gemini AI를 사용한 고급 자연어 처리
 * @access  Private
 */
router.post('/enhance',
  authMiddleware,
  [
    body('naturalLanguageInput')
      .isString()
      .isLength({ min: 10, max: 2000 })
      .withMessage('자연어 입력은 10자 이상 2000자 이하여야 합니다.'),
    body('language')
      .optional()
      .isIn(['ko', 'en'])
      .withMessage('지원되는 언어는 ko, en입니다.'),
    body('includeValidation')
      .optional()
      .isBoolean()
      .withMessage('검증 포함 여부는 boolean이어야 합니다.')
  ],
  checkValidation,
  catchAsync(async (req, res) => {
    const { naturalLanguageInput, language = 'ko', includeValidation = false } = req.body;
    const userId = req.user.id;

    logger.nlp('Gemini 고급 자연어 처리 시작', {
      userId,
      inputLength: naturalLanguageInput.length,
      language,
      includeValidation
    });

    try {
      // 1. Gemini AI로 BIM 파라미터 추출
      const bimParameters = await openaiService.convertToBIMParameters(naturalLanguageInput, language);
      
      // 2. 자연어 설명 생성
      const description = await openaiService.generateDescription(bimParameters, language);
      
      // 3. 검증 수행 (요청시)
      let validation = null;
      if (includeValidation) {
        validation = await openaiService.validateAndOptimizeBIM(bimParameters, language);
      }

      // 4. 응답 데이터 구성
      const response = {
        input: {
          text: naturalLanguageInput,
          language
        },
        bimParameters,
        description,
        processing: {
          timestamp: new Date().toISOString(),
          model: 'gemini-1.5-pro',
          confidence: bimParameters.confidence
        }
      };

      if (validation) {
        response.validation = validation;
      }

      logger.nlp('Gemini 고급 자연어 처리 완료', {
        userId,
        confidence: bimParameters.confidence,
        hasValidation: !!validation
      });

      res.json({
        success: true,
        data: response,
        message: 'Gemini AI 자연어 처리가 완료되었습니다.'
      });

    } catch (error) {
      logger.error('Gemini 자연어 처리 중 오류 발생', {
        userId,
        error: error.message,
        stack: error.stack
      });

      res.status(500).json({
        success: false,
        message: 'Gemini AI 자연어 처리 중 오류가 발생했습니다.'
      });
    }
  })
);

/**
 * @route   POST /api/nlp/describe
 * @desc    BIM 데이터를 자연어로 설명 생성
 * @access  Private
 */
router.post('/describe',
  authMiddleware,
  [
    body('bimData').isObject().withMessage('BIM 데이터는 객체여야 합니다.'),
    body('language').optional().isIn(['ko', 'en']).withMessage('지원되는 언어는 ko, en입니다.')
  ],
  checkValidation,
  catchAsync(async (req, res) => {
    const { bimData, language = 'ko' } = req.body;
    const userId = req.user.id;

    try {
      const description = await openaiService.generateDescription(bimData, language);

      logger.nlp('BIM 설명 생성 완료', {
        userId,
        language,
        descriptionLength: description.length
      });

      res.json({
        success: true,
        data: {
          description,
          bimData,
          language,
          timestamp: new Date().toISOString()
        },
        message: 'BIM 설명이 생성되었습니다.'
      });

    } catch (error) {
      logger.error('BIM 설명 생성 중 오류 발생', {
        userId,
        error: error.message,
        stack: error.stack
      });

      res.status(500).json({
        success: false,
        message: 'BIM 설명 생성 중 오류가 발생했습니다.'
      });
    }
  })
);

/**
 * @route   GET /api/nlp/capabilities
 * @desc    Gemini AI 기능 및 상태 확인
 * @access  Private
 */
router.get('/capabilities',
  authMiddleware,
  catchAsync(async (req, res) => {
    const capabilities = {
      service: 'Gemini AI',
      model: 'gemini-1.5-pro',
      status: openaiService.mockMode ? 'mock' : 'active',
      features: {
        naturalLanguageProcessing: true,
        bimParameterExtraction: true,
        designValidation: true,
        descriptionGeneration: true,
        multiLanguageSupport: ['ko', 'en']
      },
      limits: {
        maxInputLength: 2000,
        maxTokens: 8192,
        supportedLanguages: ['ko', 'en'],
        supportedBuildingTypes: ['RESIDENTIAL', 'COMMERCIAL', 'OFFICE', 'INDUSTRIAL', 'PUBLIC']
      },
      performance: {
        averageResponseTime: '2-5초',
        confidenceRange: '0.0-1.0',
        accuracy: openaiService.mockMode ? '모의 모드' : '높음'
      }
    };

    res.json({
      success: true,
      data: capabilities
    });
  })
);

/**
 * 자연어 입력 분석 함수
 * @param {string} input - 자연어 입력 텍스트
 * @returns {Object} 분석 결과
 */
async function analyzeNaturalLanguage(input) {
  const analysis = {
    suggestedName: '',
    description: '',
    buildingType: 'RESIDENTIAL',
    extractedKeywords: [],
    confidence: 0,
    extractedArea: null,
    rooms: [],
    orientations: [],
    roomTypes: [],
    areaKeywords: [],
    buildingKeywords: []
  };

  // 키워드 추출 및 정제
  const keywords = input.toLowerCase()
    .split(/\s+/)
    .filter(word => word.length >= 2);
  
  // 건물 유형 분석
  if (keywords.some(word => ['아파트', '빌라', '주택', '집', '거주', '원룸', '투룸', '쓰리룸'].includes(word))) {
    analysis.buildingType = 'RESIDENTIAL';
    analysis.buildingKeywords = keywords.filter(word => ['아파트', '빌라', '주택', '집', '거주', '원룸', '투룸', '쓰리룸'].includes(word));
  } else if (keywords.some(word => ['사무실', '오피스', '사무', '업무', '회사'].includes(word))) {
    analysis.buildingType = 'OFFICE';
    analysis.buildingKeywords = keywords.filter(word => ['사무실', '오피스', '사무', '업무', '회사'].includes(word));
  } else if (keywords.some(word => ['카페', '매장', '상점', '쇼핑', '상업', '레스토랑', '음식점'].includes(word))) {
    analysis.buildingType = 'COMMERCIAL';
    analysis.buildingKeywords = keywords.filter(word => ['카페', '매장', '상점', '쇼핑', '상업', '레스토랑', '음식점'].includes(word));
  } else if (keywords.some(word => ['공장', '창고', '생산', '제조', '산업', '물류'].includes(word))) {
    analysis.buildingType = 'INDUSTRIAL';
    analysis.buildingKeywords = keywords.filter(word => ['공장', '창고', '생산', '제조', '산업', '물류'].includes(word));
  } else if (keywords.some(word => ['학교', '병원', '도서관', '공공', '관공서', '체육관'].includes(word))) {
    analysis.buildingType = 'PUBLIC';
    analysis.buildingKeywords = keywords.filter(word => ['학교', '병원', '도서관', '공공', '관공서', '체육관'].includes(word));
  }

  // 면적 추출
  const areaMatches = input.match(/(\d+)\s*평/g);
  if (areaMatches) {
    analysis.extractedArea = parseInt(areaMatches[0].replace('평', ''));
    analysis.areaKeywords = areaMatches;
  }

  // 방향 추출
  const orientationWords = ['남향', '북향', '동향', '서향', '남동향', '남서향', '북동향', '북서향'];
  analysis.orientations = keywords.filter(word => orientationWords.includes(word));

  // 방 종류 추출
  const roomWords = ['거실', '침실', '주방', '화장실', '욕실', '베란다', '발코니', '드레스룸', '서재', '다이닝', '팬트리'];
  analysis.roomTypes = keywords.filter(word => roomWords.includes(word));

  // 방 정보 생성 (간단한 추정)
  if (analysis.roomTypes.length > 0) {
    analysis.rooms = analysis.roomTypes.map(roomType => ({
      type: roomType,
      count: 1,
      orientation: analysis.orientations[0] || '남향',
      area: getEstimatedRoomArea(roomType, analysis.extractedArea)
    }));
  }

  // 중요 키워드 추출
  const stopWords = ['은', '는', '이', '가', '을', '를', '에', '에서', '으로', '로', '와', '과', '의', '도', '만', '까지', '부터', '하고', '그리고', '또는', '하지만', '그러나', '하여', '해서', '해주세요', '만들어주세요', '설계해주세요'];
  const importantKeywords = keywords.filter(word => 
    word.length >= 2 && 
    !stopWords.includes(word)
  );
  
  analysis.extractedKeywords = [...new Set(importantKeywords)].slice(0, 10);

  // 제안 이름 생성
  const buildingTypeNames = {
    'RESIDENTIAL': '주거 건물',
    'OFFICE': '사무 건물', 
    'COMMERCIAL': '상업 건물',
    'INDUSTRIAL': '산업 건물',
    'PUBLIC': '공공 건물'
  };

  if (analysis.extractedArea) {
    analysis.suggestedName = `${analysis.extractedArea}평 ${buildingTypeNames[analysis.buildingType]} 프로젝트`;
  } else {
    analysis.suggestedName = `${buildingTypeNames[analysis.buildingType]} 프로젝트`;
  }
  
  // 설명 생성
  analysis.description = `${input.substring(0, 100)}${input.length > 100 ? '...' : ''}`;
  
  // 신뢰도 설정
  let confidenceScore = 0.3; // 기본 점수
  if (analysis.buildingKeywords.length > 0) confidenceScore += 0.2;
  if (analysis.extractedArea) confidenceScore += 0.2;
  if (analysis.roomTypes.length > 0) confidenceScore += 0.2;
  if (analysis.orientations.length > 0) confidenceScore += 0.1;
  
  analysis.confidence = Math.min(confidenceScore, 0.9);

  return analysis;
}

/**
 * 방 타입별 예상 면적 계산
 * @param {string} roomType - 방 타입
 * @param {number} totalArea - 전체 면적
 * @returns {number} 예상 면적
 */
function getEstimatedRoomArea(roomType, totalArea = 30) {
  const areaRatios = {
    '거실': 0.4,
    '침실': 0.25,
    '주방': 0.15,
    '화장실': 0.08,
    '욕실': 0.1,
    '베란다': 0.05,
    '발코니': 0.05,
    '드레스룸': 0.08,
    '서재': 0.2,
    '다이닝': 0.2,
    '팬트리': 0.05
  };

  return Math.round((areaRatios[roomType] || 0.1) * totalArea);
}

export default router;