import express from 'express';
import { body, param, query, validationResult } from 'express-validator';
import { PrismaClient } from '@prisma/client';
import { catchAsync, AppError } from '../middleware/errorHandler.js';
import { restrictTo, checkOwnership } from '../middleware/auth.js';
import openaiService from '../services/openaiService.js';
import logger from '../utils/logger.js';
import { v4 as uuidv4 } from 'uuid';

const router = express.Router();
const prisma = new PrismaClient();

// 입력 검증 규칙들
const createParametricModelValidation = [
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
  body('objects')
    .isArray()
    .withMessage('객체 목록이 필요합니다'),
  body('globalParameters')
    .isArray()
    .withMessage('글로벌 매개변수 목록이 필요합니다'),
  body('metadata')
    .optional()
    .isObject()
    .withMessage('메타데이터는 객체 형태여야 합니다')
];

const updateParameterValidation = [
  param('modelId').isString().notEmpty().withMessage('모델 ID가 필요합니다'),
  body('objectId').optional().isString().withMessage('객체 ID는 문자열이어야 합니다'),
  body('parameterName').isString().notEmpty().withMessage('매개변수 이름이 필요합니다'),
  body('value').exists().withMessage('매개변수 값이 필요합니다')
];

const optimizeParametricModelValidation = [
  param('modelId').isString().notEmpty().withMessage('모델 ID가 필요합니다'),
  body('optimization_type')
    .isIn(['performance', 'cost', 'energy', 'structural', 'aesthetic'])
    .withMessage('유효한 최적화 타입을 선택해주세요'),
  body('constraints')
    .optional()
    .isArray()
    .withMessage('제약조건은 배열이어야 합니다')
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

// 파라메트릭 BIM 모델 생성
router.post('/', createParametricModelValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { name, description, objects, globalParameters, relationships, metadata } = req.body;
  const userId = req.user.id;
  const { projectId } = req.query;

  if (!projectId) {
    return next(new AppError('프로젝트 ID가 필요합니다.', 400));
  }

  // 프로젝트 권한 확인
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
    const parametricModel = await prisma.$transaction(async (tx) => {
      // 파라메트릭 BIM 모델 생성
      const newModel = await tx.parametricBimModel.create({
        data: {
          id: uuidv4(),
          name,
          description,
          version: 1,
          objects: objects || [],
          globalParameters: globalParameters || [],
          relationships: relationships || [],
          metadata: {
            ...metadata,
            createdWith: 'parametric-bim-engine',
            engine: 'ParametricBIMEngine',
            version: '1.0.0',
            projectId,
            createdAt: new Date().toISOString(),
            createdBy: userId
          },
          userId,
          projectId,
          isActive: true
        }
      });

      // 활동 로그 기록
      await tx.activityLog.create({
        data: {
          action: 'PARAMETRIC_BIM_CREATED',
          details: {
            modelId: newModel.id,
            modelName: name,
            objectCount: objects?.length || 0,
            parameterCount: globalParameters?.length || 0
          },
          userId,
          projectId,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent')
        }
      });

      return newModel;
    });

    logger.bim('파라메트릭 BIM 모델 생성 완료', {
      userId,
      modelId: parametricModel.id,
      projectId,
      objectCount: objects?.length || 0
    });

    res.status(201).json({
      success: true,
      message: '파라메트릭 BIM 모델이 성공적으로 생성되었습니다.',
      data: parametricModel
    });

  } catch (error) {
    logger.error('파라메트릭 BIM 모델 생성 오류', {
      userId,
      projectId,
      error: error.message,
      stack: error.stack
    });

    return next(new AppError('파라메트릭 BIM 모델 생성 중 오류가 발생했습니다.', 500));
  }
}));

// 프로젝트의 파라메트릭 BIM 모델 목록 조회
router.get('/project/:projectId', catchAsync(async (req, res, next) => {
  const { projectId } = req.params;
  const userId = req.user.id;
  const { page = 1, limit = 10 } = req.query;

  // 페이지네이션 설정
  const pageNum = Math.max(1, parseInt(page));
  const limitNum = Math.min(50, Math.max(1, parseInt(limit)));
  const skip = (pageNum - 1) * limitNum;

  // 프로젝트 권한 확인
  const project = await prisma.project.findFirst({
    where: {
      id: projectId,
      OR: [
        { userId: userId },
        {
          collaborators: {
            some: { userId: userId }
          }
        }
      ]
    }
  });

  if (!project) {
    return next(new AppError('프로젝트에 접근할 권한이 없습니다.', 403));
  }

  try {
    const [models, total] = await Promise.all([
      prisma.parametricBimModel.findMany({
        where: { projectId },
        skip,
        take: limitNum,
        orderBy: { createdAt: 'desc' },
        include: {
          user: {
            select: { id: true, name: true, email: true }
          }
        }
      }),
      prisma.parametricBimModel.count({
        where: { projectId }
      })
    ]);

    const totalPages = Math.ceil(total / limitNum);

    res.json({
      success: true,
      data: {
        models,
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
    logger.error('파라메트릭 BIM 모델 목록 조회 오류', {
      userId,
      projectId,
      error: error.message
    });
    return next(new AppError('모델 목록을 불러오는 중 오류가 발생했습니다.', 500));
  }
}));

// 특정 파라메트릭 BIM 모델 조회
router.get('/:modelId', catchAsync(async (req, res, next) => {
  const { modelId } = req.params;
  const userId = req.user.id;

  try {
    const model = await prisma.parametricBimModel.findFirst({
      where: {
        id: modelId,
        OR: [
          { userId: userId },
          {
            project: {
              collaborators: {
                some: { userId: userId }
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
        }
      }
    });

    if (!model) {
      return next(new AppError('파라메트릭 BIM 모델을 찾을 수 없습니다.', 404));
    }

    // 활동 로그 기록
    await prisma.activityLog.create({
      data: {
        action: 'PARAMETRIC_BIM_VIEWED',
        details: {
          modelId: modelId,
          modelName: model.name
        },
        userId,
        projectId: model.projectId,
        ipAddress: req.ip,
        userAgent: req.get('User-Agent')
      }
    });

    res.json({
      success: true,
      data: model
    });

  } catch (error) {
    logger.error('파라메트릭 BIM 모델 조회 오류', {
      userId,
      modelId,
      error: error.message
    });
    return next(new AppError('모델을 불러오는 중 오류가 발생했습니다.', 500));
  }
}));

// 파라메트릭 BIM 모델 업데이트
router.put('/:modelId', createParametricModelValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { modelId } = req.params;
  const { name, description, objects, globalParameters, relationships, metadata } = req.body;
  const userId = req.user.id;

  try {
    // 권한 확인
    const existingModel = await prisma.parametricBimModel.findFirst({
      where: {
        id: modelId,
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
      return next(new AppError('모델을 찾을 수 없거나 권한이 없습니다.', 404));
    }

    const updatedModel = await prisma.$transaction(async (tx) => {
      const model = await tx.parametricBimModel.update({
        where: { id: modelId },
        data: {
          name: name || existingModel.name,
          description: description || existingModel.description,
          objects: objects || existingModel.objects,
          globalParameters: globalParameters || existingModel.globalParameters,
          relationships: relationships || existingModel.relationships,
          metadata: {
            ...existingModel.metadata,
            ...metadata,
            updatedAt: new Date().toISOString(),
            updatedBy: userId
          },
          version: existingModel.version + 1
        }
      });

      // 활동 로그 기록
      await tx.activityLog.create({
        data: {
          action: 'PARAMETRIC_BIM_UPDATED',
          details: {
            modelId: modelId,
            version: model.version
          },
          userId,
          projectId: model.projectId,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent')
        }
      });

      return model;
    });

    res.json({
      success: true,
      message: '파라메트릭 BIM 모델이 성공적으로 업데이트되었습니다.',
      data: updatedModel
    });

  } catch (error) {
    logger.error('파라메트릭 BIM 모델 업데이트 오류', {
      userId,
      modelId,
      error: error.message
    });
    return next(new AppError('모델 업데이트 중 오류가 발생했습니다.', 500));
  }
}));

// 파라메트릭 매개변수 업데이트
router.patch('/:modelId/parameters', updateParameterValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { modelId } = req.params;
  const { objectId, parameterName, value } = req.body;
  const userId = req.user.id;

  try {
    // 권한 확인
    const model = await prisma.parametricBimModel.findFirst({
      where: {
        id: modelId,
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

    if (!model) {
      return next(new AppError('모델을 찾을 수 없거나 권한이 없습니다.', 404));
    }

    // 매개변수 업데이트 로직
    let updatedData = { ...model };

    if (objectId) {
      // 특정 객체의 매개변수 업데이트
      const objects = [...model.objects];
      const objectIndex = objects.findIndex(obj => obj.id === objectId);
      
      if (objectIndex === -1) {
        return next(new AppError('객체를 찾을 수 없습니다.', 404));
      }

      const parameters = [...objects[objectIndex].parameters];
      const paramIndex = parameters.findIndex(param => param.name === parameterName);
      
      if (paramIndex === -1) {
        return next(new AppError('매개변수를 찾을 수 없습니다.', 404));
      }

      parameters[paramIndex].value = value;
      objects[objectIndex].parameters = parameters;
      updatedData.objects = objects;
    } else {
      // 글로벌 매개변수 업데이트
      const globalParameters = [...model.globalParameters];
      const paramIndex = globalParameters.findIndex(param => param.name === parameterName);
      
      if (paramIndex === -1) {
        return next(new AppError('글로벌 매개변수를 찾을 수 없습니다.', 404));
      }

      globalParameters[paramIndex].value = value;
      updatedData.globalParameters = globalParameters;
    }

    // 데이터베이스 업데이트
    const updatedModel = await prisma.parametricBimModel.update({
      where: { id: modelId },
      data: {
        objects: updatedData.objects,
        globalParameters: updatedData.globalParameters,
        metadata: {
          ...model.metadata,
          lastParameterUpdate: new Date().toISOString(),
          updatedBy: userId
        }
      }
    });

    // 활동 로그 기록
    await prisma.activityLog.create({
      data: {
        action: 'PARAMETRIC_PARAMETER_UPDATED',
        details: {
          modelId: modelId,
          objectId: objectId || 'global',
          parameterName,
          newValue: value
        },
        userId,
        projectId: model.projectId,
        ipAddress: req.ip,
        userAgent: req.get('User-Agent')
      }
    });

    res.json({
      success: true,
      message: '매개변수가 성공적으로 업데이트되었습니다.',
      data: updatedModel
    });

  } catch (error) {
    logger.error('매개변수 업데이트 오류', {
      userId,
      modelId,
      parameterName,
      error: error.message
    });
    return next(new AppError('매개변수 업데이트 중 오류가 발생했습니다.', 500));
  }
}));

// AI 기반 파라메트릭 모델 최적화
router.post('/:modelId/ai-optimize', optimizeParametricModelValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { modelId } = req.params;
  const { optimization_type, constraints = [] } = req.body;
  const userId = req.user.id;

  try {
    // 권한 확인
    const model = await prisma.parametricBimModel.findFirst({
      where: {
        id: modelId,
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

    if (!model) {
      return next(new AppError('모델을 찾을 수 없거나 권한이 없습니다.', 404));
    }

    logger.nlp('파라메트릭 BIM AI 최적화 시작', {
      userId,
      modelId,
      optimization_type,
      constraints
    });

    // OpenAI를 사용한 최적화 제안 생성
    const optimizationPrompt = `
다음 파라메트릭 BIM 모델을 ${optimization_type} 관점에서 최적화해주세요:

모델 정보:
- 이름: ${model.name}
- 객체 수: ${model.objects.length}
- 글로벌 매개변수: ${model.globalParameters.length}개

제약조건: ${constraints.join(', ')}

현재 매개변수들:
${JSON.stringify(model.globalParameters, null, 2)}

최적화 제안을 다음 형식으로 제공해주세요:
1. 변경할 매개변수와 권장 값
2. 최적화 이유
3. 예상 개선 효과
4. 위험 요소
`;

    try {
      const optimizationResult = await openaiService.generateCompletion(optimizationPrompt, {
        max_tokens: 2000,
        temperature: 0.7
      });

      // 최적화 결과를 새 버전으로 저장
      const optimizedModel = await prisma.$transaction(async (tx) => {
        const newVersion = await tx.parametricBimModel.create({
          data: {
            id: uuidv4(),
            name: `${model.name} (AI 최적화 v${model.version + 1})`,
            description: `AI ${optimization_type} 최적화 버전 - ${model.description || ''}`,
            version: model.version + 1,
            objects: model.objects,
            globalParameters: model.globalParameters,
            relationships: model.relationships,
            metadata: {
              ...model.metadata,
              aiOptimized: true,
              optimizationType: optimization_type,
              optimizationResult: optimizationResult,
              parentVersion: model.version,
              optimizedAt: new Date().toISOString(),
              optimizedBy: userId
            },
            userId,
            projectId: model.projectId,
            isActive: true,
            parentId: modelId
          }
        });

        // 활동 로그 기록
        await tx.activityLog.create({
          data: {
            action: 'PARAMETRIC_BIM_AI_OPTIMIZED',
            details: {
              originalModelId: modelId,
              optimizedModelId: newVersion.id,
              optimizationType: optimization_type,
              constraints
            },
            userId,
            projectId: model.projectId,
            ipAddress: req.ip,
            userAgent: req.get('User-Agent')
          }
        });

        return newVersion;
      });

      logger.bim('파라메트릭 BIM AI 최적화 완료', {
        userId,
        originalModelId: modelId,
        optimizedModelId: optimizedModel.id,
        optimizationType: optimization_type
      });

      res.status(201).json({
        success: true,
        message: 'AI 최적화된 파라메트릭 BIM 모델이 생성되었습니다.',
        data: {
          optimized_model: optimizedModel,
          optimization_suggestions: optimizationResult
        }
      });

    } catch (aiError) {
      logger.error('AI 최적화 처리 실패', {
        userId,
        modelId,
        error: aiError.message
      });
      return next(new AppError('AI 최적화 처리에 실패했습니다.', 422));
    }

  } catch (error) {
    logger.error('파라메트릭 BIM AI 최적화 오류', {
      userId,
      modelId,
      error: error.message,
      stack: error.stack
    });

    return next(new AppError('AI 최적화 중 오류가 발생했습니다.', 500));
  }
}));

// 파라메트릭 BIM 모델 공유
router.post('/:modelId/share', catchAsync(async (req, res, next) => {
  const { modelId } = req.params;
  const { permissions = ['view'], expiresAt } = req.body;
  const userId = req.user.id;

  try {
    // 권한 확인
    const model = await prisma.parametricBimModel.findFirst({
      where: {
        id: modelId,
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

    if (!model) {
      return next(new AppError('모델을 찾을 수 없거나 권한이 없습니다.', 404));
    }

    // 공유 토큰 생성
    const shareToken = uuidv4();
    const shareData = {
      id: uuidv4(),
      modelId: modelId,
      shareToken,
      permissions,
      expiresAt: expiresAt || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7일 후 만료
      createdBy: userId,
      createdAt: new Date().toISOString()
    };

    await prisma.parametricBimShare.create({
      data: shareData
    });

    // 공유 URL 생성
    const shareUrl = `${process.env.FRONTEND_URL}/shared/parametric-bim/${shareToken}`;

    res.json({
      success: true,
      message: '파라메트릭 BIM 모델이 성공적으로 공유되었습니다.',
      data: {
        shareUrl,
        shareToken,
        permissions,
        expiresAt: shareData.expiresAt
      }
    });

  } catch (error) {
    logger.error('파라메트릭 BIM 모델 공유 오류', {
      userId,
      modelId,
      error: error.message
    });
    return next(new AppError('모델 공유 중 오류가 발생했습니다.', 500));
  }
}));

// 성능 분석
router.get('/:modelId/performance', catchAsync(async (req, res, next) => {
  const { modelId } = req.params;
  const userId = req.user.id;

  try {
    const model = await prisma.parametricBimModel.findFirst({
      where: {
        id: modelId,
        OR: [
          { userId: userId },
          {
            project: {
              collaborators: {
                some: { userId: userId }
              }
            }
          }
        ]
      }
    });

    if (!model) {
      return next(new AppError('모델을 찾을 수 없습니다.', 404));
    }

    // 성능 분석 데이터 계산
    const performance = {
      objectCount: model.objects.length,
      parameterCount: model.globalParameters.reduce((sum, obj) => 
        sum + (obj.parameters ? obj.parameters.length : 0), model.globalParameters.length
      ),
      constraintCount: model.objects.reduce((sum, obj) => 
        sum + (obj.constraints ? obj.constraints.length : 0), 0
      ),
      relationshipCount: model.relationships.length,
      memoryUsage: JSON.stringify(model).length, // 대략적인 메모리 사용량
      complexity: model.objects.length * 100 + model.globalParameters.length * 50,
      lastUpdated: model.metadata?.updatedAt || model.createdAt
    };

    res.json({
      success: true,
      data: performance
    });

  } catch (error) {
    logger.error('성능 분석 오류', {
      userId,
      modelId,
      error: error.message
    });
    return next(new AppError('성능 분석 중 오류가 발생했습니다.', 500));
  }
}));

// 파라메트릭 BIM 모델 삭제
router.delete('/:modelId', catchAsync(async (req, res, next) => {
  const { modelId } = req.params;
  const userId = req.user.id;

  try {
    // 권한 확인
    const model = await prisma.parametricBimModel.findFirst({
      where: {
        id: modelId,
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

    if (!model) {
      return next(new AppError('모델을 찾을 수 없거나 삭제 권한이 없습니다.', 404));
    }

    await prisma.$transaction(async (tx) => {
      // 공유 데이터 삭제
      await tx.parametricBimShare.deleteMany({
        where: { modelId }
      });

      // 모델 삭제
      await tx.parametricBimModel.delete({
        where: { id: modelId }
      });

      // 활동 로그 기록
      await tx.activityLog.create({
        data: {
          action: 'PARAMETRIC_BIM_DELETED',
          details: {
            modelId: modelId,
            modelName: model.name
          },
          userId,
          projectId: model.projectId,
          ipAddress: req.ip,
          userAgent: req.get('User-Agent')
        }
      });
    });

    res.json({
      success: true,
      message: '파라메트릭 BIM 모델이 성공적으로 삭제되었습니다.'
    });

  } catch (error) {
    logger.error('파라메트릭 BIM 모델 삭제 오류', {
      userId,
      modelId,
      error: error.message
    });
    return next(new AppError('모델 삭제 중 오류가 발생했습니다.', 500));
  }
}));

export default router;