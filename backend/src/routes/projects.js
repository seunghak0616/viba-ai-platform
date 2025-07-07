import express from 'express';
import { body, param, query, validationResult } from 'express-validator';
import { PrismaClient } from '@prisma/client';
import { catchAsync, AppError } from '../middleware/errorHandler.js';
import authMiddleware, { restrictTo } from '../middleware/auth.js';
import logger from '../utils/logger.js';

const router = express.Router();
const prisma = new PrismaClient();

// 모든 라우트에 인증 미들웨어 적용
router.use(authMiddleware);

// 검증 미들웨어
const checkValidation = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const errorMessages = errors.array().map(error => error.msg);
    return next(new AppError(errorMessages.join(', '), 400));
  }
  next();
};

// 프로젝트 목록 조회
router.get('/', 
  [
    query('page').optional().isInt({ min: 1 }).withMessage('페이지는 1 이상이어야 합니다'),
    query('limit').optional().isInt({ min: 1, max: 100 }).withMessage('페이지 크기는 1-100 사이여야 합니다'),
    query('status').optional().isIn(['DRAFT', 'ACTIVE', 'PLANNING', 'COMPLETED', 'ARCHIVED']).withMessage('올바른 상태값을 입력하세요'),
    query('search').optional().isLength({ min: 1 }).withMessage('검색어는 1자 이상이어야 합니다')
  ],
  checkValidation,
  catchAsync(async (req, res) => {
    const page = parseInt(req.query.page) || 1;
    const limit = parseInt(req.query.limit) || 10;
    const status = req.query.status;
    const search = req.query.search;
    const offset = (page - 1) * limit;

    // 검색 조건 구성
    const where = {
      userId: req.user.id
    };

    if (status) {
      where.status = status;
    }

    if (search) {
      where.OR = [
        { name: { contains: search, mode: 'insensitive' } },
        { description: { contains: search, mode: 'insensitive' } }
      ];
    }

    // 프로젝트 목록과 총 개수 조회
    const [projects, total] = await Promise.all([
      prisma.project.findMany({
        where,
        skip: offset,
        take: limit,
        orderBy: { updatedAt: 'desc' },
        include: {
          bimModels: {
            select: {
              id: true,
              name: true,
              type: true,
              version: true,
              createdAt: true
            },
            orderBy: { createdAt: 'desc' },
            take: 3 // 최근 3개만
          },
          _count: {
            select: {
              bimModels: true,
              activityLogs: true
            }
          }
        }
      }),
      prisma.project.count({ where })
    ]);

    logger.info('프로젝트 목록 조회', {
      userId: req.user.id,
      total,
      page,
      limit,
      filters: { status, search }
    });

    res.json({
      success: true,
      data: {
        projects,
        pagination: {
          page,
          limit,
          total,
          totalPages: Math.ceil(total / limit),
          hasNext: page < Math.ceil(total / limit),
          hasPrev: page > 1
        }
      }
    });
  })
);

// 프로젝트 상세 조회
router.get('/:id',
  [
    param('id').isString().withMessage('유효한 프로젝트 ID를 입력하세요')
  ],
  checkValidation,
  catchAsync(async (req, res, next) => {
    const project = await prisma.project.findFirst({
      where: {
        id: req.params.id,
        userId: req.user.id
      },
      include: {
        bimModels: {
          orderBy: { createdAt: 'desc' }
        },
        activityLogs: {
          orderBy: { createdAt: 'desc' },
          take: 20,
          include: {
            user: {
              select: {
                id: true,
                name: true,
                email: true
              }
            }
          }
        },
        _count: {
          select: {
            bimModels: true,
            activityLogs: true
          }
        }
      }
    });

    if (!project) {
      return next(new AppError('프로젝트를 찾을 수 없습니다.', 404));
    }

    logger.info('프로젝트 상세 조회', {
      projectId: project.id,
      userId: req.user.id
    });

    res.json({
      success: true,
      data: { project }
    });
  })
);

// 프로젝트 생성
router.post('/',
  [
    body('name')
      .isLength({ min: 1, max: 100 })
      .withMessage('프로젝트 이름은 1-100자 사이여야 합니다')
      .trim(),
    body('description')
      .optional()
      .isLength({ max: 1000 })
      .withMessage('설명은 1000자 이하여야 합니다')
      .trim(),
    body('status')
      .optional()
      .isIn(['DRAFT', 'ACTIVE', 'PLANNING', 'COMPLETED', 'ARCHIVED'])
      .withMessage('올바른 상태값을 입력하세요'),
    body('settings')
      .optional()
      .isObject()
      .withMessage('설정은 객체 형식이어야 합니다')
  ],
  checkValidation,
  catchAsync(async (req, res) => {
    const { name, description, status = 'DRAFT', settings } = req.body;

    // 동일한 이름의 프로젝트가 있는지 확인
    const existingProject = await prisma.project.findFirst({
      where: {
        name,
        userId: req.user.id
      }
    });

    if (existingProject) {
      return res.status(400).json({
        success: false,
        message: '이미 같은 이름의 프로젝트가 존재합니다.'
      });
    }

    const project = await prisma.project.create({
      data: {
        name,
        description,
        status,
        settings: settings ? JSON.stringify(settings) : null,
        userId: req.user.id
      },
      include: {
        _count: {
          select: {
            bimModels: true,
            activityLogs: true
          }
        }
      }
    });

    // 활동 로그 생성
    await prisma.activityLog.create({
      data: {
        action: 'PROJECT_CREATED',
        details: `프로젝트 '${project.name}'가 생성되었습니다.`,
        userId: req.user.id,
        projectId: project.id
      }
    });

    logger.info('프로젝트 생성', {
      projectId: project.id,
      projectName: project.name,
      userId: req.user.id
    });

    res.status(201).json({
      success: true,
      message: '프로젝트가 성공적으로 생성되었습니다.',
      data: { project }
    });
  })
);

export default router;