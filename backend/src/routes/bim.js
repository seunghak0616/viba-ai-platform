import express from 'express';
import { body, param, query, validationResult } from 'express-validator';
import { PrismaClient } from '@prisma/client';
import { catchAsync, AppError } from '../middleware/errorHandler.js';
import { restrictTo, checkOwnership } from '../middleware/auth.js';
import geminiClient from '../config/gemini.js';
import logger from '../utils/logger.js';
import { v4 as uuidv4 } from 'uuid';

const router = express.Router();
const prisma = new PrismaClient();

// 입력 검증 규칙들
const createBimModelValidation = [
  body('name')
    .isLength({ min: 1, max: 100 })
    .withMessage('모델명은 1-100자 사이여야 합니다')
    .trim()
    .escape(),
  body('description')
    .optional()
    .isLength({ max: 500 })
    .withMessage('설명은 500자 이하여야 합니다')
    .trim()
    .escape(),
  body('naturalLanguageInput')
    .isLength({ min: 5, max: 1000 })
    .withMessage('자연어 입력은 5-1000자 사이여야 합니다')
    .trim(),
  body('type')
    .isIn(['APARTMENT', 'HOUSE', 'OFFICE', 'COMMERCIAL', 'INDUSTRIAL', 'CUSTOM'])
    .withMessage('유효한 건물 타입을 선택해주세요'),
  body('projectId')
    .isString()
    .notEmpty()
    .withMessage('프로젝트 ID가 필요합니다')
];

const updateBimModelValidation = [
  param('id')
    .isString()
    .notEmpty()
    .withMessage('유효한 BIM 모델 ID가 필요합니다'),
  body('name')
    .optional()
    .isLength({ min: 1, max: 100 })
    .withMessage('모델명은 1-100자 사이여야 합니다')
    .trim()
    .escape(),
  body('description')
    .optional()
    .isLength({ max: 500 })
    .withMessage('설명은 500자 이하여야 합니다')
    .trim()
    .escape()
];

const optimizeBimModelValidation = [
  param('id')
    .isString()
    .notEmpty()
    .withMessage('유효한 BIM 모델 ID가 필요합니다'),
  body('requirements')
    .optional()
    .isObject()
    .withMessage('요구사항은 객체 형태여야 합니다'),
  body('constraints')
    .optional()
    .isObject()
    .withMessage('제약조건은 객체 형태여야 합니다')
];

// 검증 결과 확인 미들웨어
const checkValidation = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const errorMessages = errors.array().map(error => error.msg);
    return next(new AppError(errorMessages.join(', '), 400));
  }
  next();
};

// BIM 모델 생성
router.post('/', createBimModelValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { name, description, naturalLanguageInput, type, projectId } = req.body;
  const userId = req.user.id;

  // 프로젝트 소유권 확인
  const project = await prisma.project.findFirst({
    where: {
      id: projectId,
      OR: [
        { userId: userId },
        { 
          collaborators: {
            some: {
              userId: userId,
              role: { in: ['EDITOR', 'ADMIN'] }
            }
          }
        }
      ]
    }
  });

  if (!project) {
    logger.security('권한 없는 프로젝트 접근', {
      userId,
      projectId,
      ip: req.ip
    });
    return next(new AppError('프로젝트에 접근할 권한이 없습니다.', 403));
  }

  try {
    // 1. 자연어 입력을 Gemini로 처리
    logger.nlp('BIM 모델 생성 시작', {
      userId,
      projectId,
      input: naturalLanguageInput.substring(0, 100) + '...'
    });

    const nlpResult = await geminiClient.parseNaturalLanguageToBim(
      naturalLanguageInput,
      { projectId, userId, type }
    );

    if (!nlpResult || nlpResult.error) {
      logger.error('NLP 처리 실패', {
        userId,
        error: nlpResult?.error || 'Unknown error',
        input: naturalLanguageInput
      });
      return next(new AppError('자연어 처리에 실패했습니다. 다시 시도해주세요.', 422));
    }

    // 2. 트랜잭션으로 BIM 모델 생성
    const bimModel = await prisma.$transaction(async (tx) => {
      // BIM 모델 생성
      const newModel = await tx.bimModel.create({
        data: {
          id: uuidv4(),
          name,
          description,
          type,
          naturalLanguageInput,
          processedParams: nlpResult,
          userId,
          projectId,
          version: 1,
          isPublic: false,
          isTemplate: false,
          // 기본 메타데이터 설정
          metadata: {
            createdWith: 'gemini-ai',
            processingVersion: '1.0',
            confidence: nlpResult.confidence || 0.8
          }
        },
        include: {
          user: {
            select: { id: true, name: true, email: true }
          },
          project: {
            select: { id: true, name: true }
          }
        }
      });

      // 활동 로그 기록
      await tx.activityLog.create({
        data: {
          action: 'BIM_MODEL_CREATED',
          details: {
            modelId: newModel.id,
            modelName: name,
            type,
            confidence: nlpResult.confidence
          },
          userId,
          projectId,
          bimModelId: newModel.id,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent')
        }
      });

      return newModel;
    });

    logger.bim('BIM 모델 생성 완료', {
      userId,
      modelId: bimModel.id,
      projectId,
      type,
      confidence: nlpResult.confidence
    });

    res.status(201).json({
      success: true,
      message: 'BIM 모델이 성공적으로 생성되었습니다.',
      data: {
        bimModel,
        nlpResult
      }
    });

  } catch (error) {
    logger.error('BIM 모델 생성 오류', {
      userId,
      projectId,
      error: error.message,
      stack: error.stack
    });

    if (error.message.includes('자연어 처리')) {
      return next(new AppError(error.message, 422));
    }

    return next(new AppError('BIM 모델 생성 중 오류가 발생했습니다.', 500));
  }
}));

// BIM 모델 목록 조회
router.get('/', catchAsync(async (req, res, next) => {
  const userId = req.user.id;
  const {
    page = 1,
    limit = 10,
    projectId,
    type,
    search,
    sortBy = 'createdAt',
    sortOrder = 'desc'
  } = req.query;

  // 페이지네이션 검증
  const pageNum = Math.max(1, parseInt(page));
  const limitNum = Math.min(50, Math.max(1, parseInt(limit))); // 최대 50개로 제한
  const skip = (pageNum - 1) * limitNum;

  // 정렬 옵션 검증
  const validSortFields = ['createdAt', 'updatedAt', 'name', 'type'];
  const validSortOrders = ['asc', 'desc'];
  const orderBy = validSortFields.includes(sortBy) ? sortBy : 'createdAt';
  const order = validSortOrders.includes(sortOrder) ? sortOrder : 'desc';

  // 필터 조건 구성
  const where = {
    OR: [
      { userId: userId },
      {
        project: {
          collaborators: {
            some: {
              userId: userId
            }
          }
        }
      }
    ]
  };

  if (projectId) {
    where.projectId = projectId;
  }

  if (type && ['APARTMENT', 'HOUSE', 'OFFICE', 'COMMERCIAL', 'INDUSTRIAL', 'CUSTOM'].includes(type)) {
    where.type = type;
  }

  if (search) {
    where.OR = [
      { name: { contains: search, mode: 'insensitive' } },
      { description: { contains: search, mode: 'insensitive' } }
    ];
  }

  try {
    const [bimModels, total] = await Promise.all([
      prisma.bimModel.findMany({
        where,
        skip,
        take: limitNum,
        orderBy: { [orderBy]: order },
        include: {
          user: {
            select: { id: true, name: true }
          },
          project: {
            select: { id: true, name: true }
          },
          _count: {
            select: { children: true }
          }
        }
      }),
      prisma.bimModel.count({ where })
    ]);

    const totalPages = Math.ceil(total / limitNum);

    logger.api(req, res, Date.now() - req.startTime);

    res.json({
      success: true,
      data: {
        bimModels,
        pagination: {
          page: pageNum,
          limit: limitNum,
          total,
          totalPages,
          hasNext: pageNum < totalPages,
          hasPrev: pageNum > 1
        }
      }
    });

  } catch (error) {
    logger.error('BIM 모델 목록 조회 오류', {
      userId,
      error: error.message,
      query: req.query
    });
    return next(new AppError('BIM 모델 목록을 불러오는 중 오류가 발생했습니다.', 500));
  }
}));

// 특정 BIM 모델 조회
router.get('/:id', param('id').isString().notEmpty(), checkValidation, catchAsync(async (req, res, next) => {
  const { id } = req.params;
  const userId = req.user.id;

  try {
    const bimModel = await prisma.bimModel.findFirst({
      where: {
        id,
        OR: [
          { userId: userId },
          { isPublic: true },
          {
            project: {
              collaborators: {
                some: {
                  userId: userId
                }
              }
            }
          }
        ]
      },
      include: {
        user: {
          select: { id: true, name: true, email: true }
        },
        project: {
          select: { id: true, name: true, status: true }
        },
        parent: {
          select: { id: true, name: true, version: true }
        },
        children: {
          select: { id: true, name: true, version: true, createdAt: true },
          orderBy: { version: 'desc' }
        },
        files: {
          select: { id: true, filename: true, fileType: true, size: true, url: true }
        }
      }
    });

    if (!bimModel) {
      logger.security('존재하지 않는 BIM 모델 접근', {
        userId,
        modelId: id,
        ip: req.ip
      });
      return next(new AppError('BIM 모델을 찾을 수 없습니다.', 404));
    }

    // 활동 로그 기록
    await prisma.activityLog.create({
      data: {
        action: 'BIM_MODEL_VIEWED',
        details: {
          modelId: id,
          modelName: bimModel.name
        },
        userId,
        projectId: bimModel.projectId,
        bimModelId: id,
        ipAddress: req.ip,
        userAgent: req.get('User-Agent')
      }
    });

    logger.bim('BIM 모델 조회', {
      userId,
      modelId: id,
      projectId: bimModel.projectId
    });

    res.json({
      success: true,
      data: { bimModel }
    });

  } catch (error) {
    logger.error('BIM 모델 조회 오류', {
      userId,
      modelId: id,
      error: error.message
    });
    return next(new AppError('BIM 모델을 불러오는 중 오류가 발생했습니다.', 500));
  }
}));

// BIM 모델 최적화
router.post('/:id/optimize', optimizeBimModelValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { id } = req.params;
  const { requirements = {}, constraints = {} } = req.body;
  const userId = req.user.id;

  try {
    // BIM 모델 존재 및 권한 확인
    const bimModel = await prisma.bimModel.findFirst({
      where: {
        id,
        OR: [
          { userId: userId },
          {
            project: {
              collaborators: {
                some: {
                  userId: userId,
                  role: { in: ['EDITOR', 'ADMIN'] }
                }
              }
            }
          }
        ]
      },
      include: {
        project: {
          select: { id: true, name: true }
        }
      }
    });

    if (!bimModel) {
      return next(new AppError('BIM 모델을 찾을 수 없거나 권한이 없습니다.', 404));
    }

    logger.nlp('BIM 모델 최적화 시작', {
      userId,
      modelId: id,
      projectId: bimModel.projectId
    });

    // Gemini를 사용한 최적화 제안 생성
    const optimizationResult = await geminiClient.generateOptimizationSuggestions(
      {
        id: bimModel.id,
        name: bimModel.name,
        type: bimModel.type,
        processedParams: bimModel.processedParams,
        geometryData: bimModel.geometryData,
        metadata: bimModel.metadata
      },
      { requirements, constraints }
    );

    if (!optimizationResult || optimizationResult.error) {
      logger.error('최적화 처리 실패', {
        userId,
        modelId: id,
        error: optimizationResult?.error || 'Unknown error'
      });
      return next(new AppError('최적화 처리에 실패했습니다.', 422));
    }

    // 최적화 결과를 모델에 저장 (새 버전으로)
    const optimizedModel = await prisma.$transaction(async (tx) => {
      const newVersion = await tx.bimModel.create({
        data: {
          id: uuidv4(),
          name: `${bimModel.name} (최적화 v${bimModel.version + 1})`,
          description: `최적화된 버전 - ${bimModel.description || ''}`,
          type: bimModel.type,
          naturalLanguageInput: bimModel.naturalLanguageInput,
          processedParams: {
            ...bimModel.processedParams,
            optimization: optimizationResult
          },
          geometryData: bimModel.geometryData,
          materials: bimModel.materials,
          dimensions: bimModel.dimensions,
          spatial: bimModel.spatial,
          metadata: {
            ...bimModel.metadata,
            optimized: true,
            optimizationScore: optimizationResult.overallScore,
            parentVersion: bimModel.version
          },
          version: bimModel.version + 1,
          parentId: bimModel.id,
          userId,
          projectId: bimModel.projectId,
          isPublic: bimModel.isPublic
        },
        include: {
          user: {
            select: { id: true, name: true }
          },
          project: {
            select: { id: true, name: true }
          }
        }
      });

      // 활동 로그 기록
      await tx.activityLog.create({
        data: {
          action: 'BIM_MODEL_OPTIMIZED',
          details: {
            originalModelId: id,
            newModelId: newVersion.id,
            optimizationScore: optimizationResult.overallScore,
            suggestionsCount: optimizationResult.suggestions?.length || 0
          },
          userId,
          projectId: bimModel.projectId,
          bimModelId: newVersion.id,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent')
        }
      });

      return newVersion;
    });

    logger.bim('BIM 모델 최적화 완료', {
      userId,
      originalModelId: id,
      optimizedModelId: optimizedModel.id,
      score: optimizationResult.overallScore
    });

    res.status(201).json({
      success: true,
      message: '최적화된 BIM 모델이 생성되었습니다.',
      data: {
        optimizedModel,
        optimizationResult
      }
    });

  } catch (error) {
    logger.error('BIM 모델 최적화 오류', {
      userId,
      modelId: id,
      error: error.message,
      stack: error.stack
    });

    if (error.message.includes('최적화 처리')) {
      return next(new AppError(error.message, 422));
    }

    return next(new AppError('BIM 모델 최적화 중 오류가 발생했습니다.', 500));
  }
}));

// BIM 모델 검증
router.post('/:id/validate', param('id').isString().notEmpty(), checkValidation, catchAsync(async (req, res, next) => {
  const { id } = req.params;
  const { standards = {} } = req.body;
  const userId = req.user.id;

  try {
    // BIM 모델 존재 및 권한 확인
    const bimModel = await prisma.bimModel.findFirst({
      where: {
        id,
        OR: [
          { userId: userId },
          {
            project: {
              collaborators: {
                some: {
                  userId: userId
                }
              }
            }
          }
        ]
      }
    });

    if (!bimModel) {
      return next(new AppError('BIM 모델을 찾을 수 없거나 권한이 없습니다.', 404));
    }

    logger.nlp('BIM 모델 검증 시작', {
      userId,
      modelId: id,
      projectId: bimModel.projectId
    });

    // Gemini를 사용한 설계 검증
    const validationResult = await geminiClient.validateDesign(
      {
        id: bimModel.id,
        name: bimModel.name,
        type: bimModel.type,
        processedParams: bimModel.processedParams,
        geometryData: bimModel.geometryData,
        metadata: bimModel.metadata
      },
      standards
    );

    if (!validationResult || validationResult.error) {
      logger.error('검증 처리 실패', {
        userId,
        modelId: id,
        error: validationResult?.error || 'Unknown error'
      });
      return next(new AppError('검증 처리에 실패했습니다.', 422));
    }

    // 검증 결과를 활동 로그에 기록
    await prisma.activityLog.create({
      data: {
        action: 'BIM_MODEL_VALIDATED',
        details: {
          modelId: id,
          isValid: validationResult.isValid,
          complianceScore: validationResult.complianceScore,
          issuesCount: validationResult.issues?.length || 0
        },
        userId,
        projectId: bimModel.projectId,
        bimModelId: id,
        ipAddress: req.ip,
        userAgent: req.get('User-Agent')
      }
    });

    logger.bim('BIM 모델 검증 완료', {
      userId,
      modelId: id,
      isValid: validationResult.isValid,
      score: validationResult.complianceScore
    });

    res.json({
      success: true,
      message: 'BIM 모델 검증이 완료되었습니다.',
      data: {
        validation: validationResult
      }
    });

  } catch (error) {
    logger.error('BIM 모델 검증 오류', {
      userId,
      modelId: id,
      error: error.message
    });

    if (error.message.includes('검증 처리')) {
      return next(new AppError(error.message, 422));
    }

    return next(new AppError('BIM 모델 검증 중 오류가 발생했습니다.', 500));
  }
}));

// BIM 모델 업데이트
router.put('/:id', updateBimModelValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { id } = req.params;
  const { name, description, metadata, properties } = req.body;
  const userId = req.user.id;

  try {
    // 권한 확인
    const existingModel = await prisma.bimModel.findFirst({
      where: {
        id,
        OR: [
          { userId: userId },
          {
            project: {
              collaborators: {
                some: {
                  userId: userId,
                  role: { in: ['EDITOR', 'ADMIN'] }
                }
              }
            }
          }
        ]
      }
    });

    if (!existingModel) {
      return next(new AppError('BIM 모델을 찾을 수 없거나 권한이 없습니다.', 404));
    }

    // 업데이트 데이터 준비
    const updateData = {};
    if (name !== undefined) updateData.name = name;
    if (description !== undefined) updateData.description = description;
    if (metadata !== undefined) updateData.metadata = { ...existingModel.metadata, ...metadata };
    if (properties !== undefined) updateData.properties = { ...existingModel.properties, ...properties };

    const updatedModel = await prisma.$transaction(async (tx) => {
      const model = await tx.bimModel.update({
        where: { id },
        data: updateData,
        include: {
          user: {
            select: { id: true, name: true }
          },
          project: {
            select: { id: true, name: true }
          }
        }
      });

      // 활동 로그 기록
      await tx.activityLog.create({
        data: {
          action: 'BIM_MODEL_UPDATED',
          details: {
            modelId: id,
            updatedFields: Object.keys(updateData)
          },
          userId,
          projectId: model.projectId,
          bimModelId: id,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent')
        }
      });

      return model;
    });

    logger.bim('BIM 모델 업데이트 완료', {
      userId,
      modelId: id,
      updatedFields: Object.keys(updateData)
    });

    res.json({
      success: true,
      message: 'BIM 모델이 성공적으로 업데이트되었습니다.',
      data: { bimModel: updatedModel }
    });

  } catch (error) {
    logger.error('BIM 모델 업데이트 오류', {
      userId,
      modelId: id,
      error: error.message
    });
    return next(new AppError('BIM 모델 업데이트 중 오류가 발생했습니다.', 500));
  }
}));

// BIM 모델 삭제
router.delete('/:id', param('id').isString().notEmpty(), checkValidation, catchAsync(async (req, res, next) => {
  const { id } = req.params;
  const userId = req.user.id;

  try {
    // 권한 확인
    const bimModel = await prisma.bimModel.findFirst({
      where: {
        id,
        OR: [
          { userId: userId },
          {
            project: {
              collaborators: {
                some: {
                  userId: userId,
                  role: 'ADMIN'
                }
              }
            }
          }
        ]
      }
    });

    if (!bimModel) {
      return next(new AppError('BIM 모델을 찾을 수 없거나 삭제 권한이 없습니다.', 404));
    }

    await prisma.$transaction(async (tx) => {
      // 관련 파일들 삭제 (실제 파일 삭제는 별도 작업으로)
      await tx.projectFile.deleteMany({
        where: { bimModelId: id }
      });

      // BIM 모델 삭제
      await tx.bimModel.delete({
        where: { id }
      });

      // 활동 로그 기록
      await tx.activityLog.create({
        data: {
          action: 'BIM_MODEL_DELETED',
          details: {
            modelId: id,
            modelName: bimModel.name
          },
          userId,
          projectId: bimModel.projectId,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent')
        }
      });
    });

    logger.bim('BIM 모델 삭제 완료', {
      userId,
      modelId: id,
      projectId: bimModel.projectId
    });

    res.json({
      success: true,
      message: 'BIM 모델이 성공적으로 삭제되었습니다.'
    });

  } catch (error) {
    logger.error('BIM 모델 삭제 오류', {
      userId,
      modelId: id,
      error: error.message
    });
    return next(new AppError('BIM 모델 삭제 중 오류가 발생했습니다.', 500));
  }
}));

export default router;