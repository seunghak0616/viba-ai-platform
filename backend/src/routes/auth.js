import express from 'express';
import bcrypt from 'bcryptjs';
import { body, validationResult } from 'express-validator';
import { PrismaClient } from '@prisma/client';
import { catchAsync, AppError } from '../middleware/errorHandler.js';
import { generateToken, generateRefreshToken, verifyToken } from '../middleware/auth.js';
import config from '../config/index.js';
import logger from '../utils/logger.js';

const router = express.Router();
const prisma = new PrismaClient();

// 입력 검증 규칙
const registerValidation = [
  body('email')
    .isEmail()
    .withMessage('유효한 이메일 주소를 입력하세요')
    .normalizeEmail(),
  body('password')
    .isLength({ min: 8 })
    .withMessage('비밀번호는 최소 8자 이상이어야 합니다')
    .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/)
    .withMessage('비밀번호는 대소문자, 숫자, 특수문자를 포함해야 합니다'),
  body('name')
    .isLength({ min: 2, max: 50 })
    .withMessage('이름은 2-50자 사이여야 합니다')
    .trim(),
  body('company')
    .optional()
    .isLength({ max: 100 })
    .withMessage('회사명은 100자 이하여야 합니다')
    .trim()
];

const loginValidation = [
  body('email')
    .isEmail()
    .withMessage('유효한 이메일 주소를 입력하세요')
    .normalizeEmail(),
  body('password')
    .notEmpty()
    .withMessage('비밀번호를 입력하세요')
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

// 회원가입
router.post('/register', registerValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { email, password, name, company } = req.body;

  // 이메일 중복 확인
  const existingUser = await prisma.user.findUnique({
    where: { email }
  });

  if (existingUser) {
    logger.security('중복 이메일 회원가입 시도', { 
      email, 
      ip: req.ip 
    });
    return next(new AppError('이미 사용 중인 이메일입니다.', 400));
  }

  // 비밀번호 해싱
  const hashedPassword = await bcrypt.hash(password, config.security.bcryptRounds);

  // 사용자 생성
  const user = await prisma.user.create({
    data: {
      email,
      password: hashedPassword,
      name,
      company,
      role: 'USER',
      isActive: true
    },
    select: {
      id: true,
      email: true,
      name: true,
      company: true,
      role: true,
      createdAt: true
    }
  });

  // JWT 토큰 생성
  const token = generateToken(user.id);
  const refreshToken = generateRefreshToken(user.id);

  // 리프레시 토큰을 데이터베이스에 저장
  await prisma.refreshToken.create({
    data: {
      token: refreshToken,
      userId: user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7일
    }
  });

  logger.info('새 사용자 회원가입', {
    userId: user.id,
    email: user.email,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });

  res.status(201).json({
    success: true,
    message: '회원가입이 완료되었습니다.',
    data: {
      user,
      token,
      refreshToken
    }
  });
}));

// 로그인
router.post('/login', loginValidation, checkValidation, catchAsync(async (req, res, next) => {
  const { email, password } = req.body;

  // 사용자 찾기 (비밀번호 포함)
  const user = await prisma.user.findUnique({
    where: { email }
  });

  if (!user) {
    logger.security('존재하지 않는 이메일 로그인 시도', { 
      email, 
      ip: req.ip 
    });
    return next(new AppError('이메일 또는 비밀번호가 올바르지 않습니다.', 401));
  }

  // 계정 잠금 확인 (SQLite 스키마에 맞춤)
  // 추후 계정 잠금 기능은 별도 테이블로 구현 예정

  // 비밀번호 확인
  const isPasswordValid = await bcrypt.compare(password, user.password);

  if (!isPasswordValid) {
    logger.security('잘못된 비밀번호 로그인 시도', { 
      userId: user.id, 
      ip: req.ip
    });
    
    return next(new AppError('이메일 또는 비밀번호가 올바르지 않습니다.', 401));
  }

  // 계정 활성화 확인
  if (!user.isActive) {
    logger.security('비활성 계정 로그인 시도', { 
      userId: user.id, 
      ip: req.ip 
    });
    return next(new AppError('비활성화된 계정입니다. 관리자에게 문의하세요.', 401));
  }

  // 로그인 성공 - 마지막 로그인 시간 업데이트
  await prisma.user.update({
    where: { id: user.id },
    data: {
      lastLoginAt: new Date()
    }
  });

  // JWT 토큰 생성
  const token = generateToken(user.id);
  const refreshToken = generateRefreshToken(user.id);

  // 기존 리프레시 토큰 삭제 후 새로 생성
  await prisma.refreshToken.deleteMany({
    where: { userId: user.id }
  });

  await prisma.refreshToken.create({
    data: {
      token: refreshToken,
      userId: user.id,
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
    }
  });

  logger.info('사용자 로그인 성공', {
    userId: user.id,
    email: user.email,
    ip: req.ip,
    userAgent: req.get('User-Agent')
  });

  // 응답에서 비밀번호 제거
  const { password: _, ...userResponse } = user;

  res.json({
    success: true,
    message: '로그인이 완료되었습니다.',
    data: {
      user: userResponse,
      token,
      refreshToken
    }
  });
}));

// 토큰 갱신
router.post('/refresh', catchAsync(async (req, res, next) => {
  const { refreshToken } = req.body;

  if (!refreshToken) {
    return next(new AppError('리프레시 토큰이 필요합니다.', 401));
  }

  // 리프레시 토큰 검증
  let decoded;
  try {
    decoded = verifyToken(refreshToken);
  } catch (err) {
    return next(new AppError('유효하지 않은 리프레시 토큰입니다.', 401));
  }

  // 데이터베이스에서 리프레시 토큰 확인
  const storedToken = await prisma.refreshToken.findFirst({
    where: {
      token: refreshToken,
      userId: decoded.userId,
      expiresAt: { gt: new Date() }
    },
    include: { user: true }
  });

  if (!storedToken) {
    logger.security('유효하지 않은 리프레시 토큰 사용', { 
      userId: decoded.userId, 
      ip: req.ip 
    });
    return next(new AppError('유효하지 않은 리프레시 토큰입니다.', 401));
  }

  // 새 토큰 생성
  const newToken = generateToken(storedToken.userId);

  logger.info('토큰 갱신', {
    userId: storedToken.userId,
    ip: req.ip
  });

  res.json({
    success: true,
    message: '토큰이 갱신되었습니다.',
    data: {
      token: newToken
    }
  });
}));

// 로그아웃
router.post('/logout', catchAsync(async (req, res, next) => {
  const { refreshToken } = req.body;

  if (refreshToken) {
    // 리프레시 토큰 삭제
    await prisma.refreshToken.deleteMany({
      where: { token: refreshToken }
    });
  }

  logger.info('사용자 로그아웃', {
    ip: req.ip
  });

  res.json({
    success: true,
    message: '로그아웃이 완료되었습니다.'
  });
}));

// 현재 사용자 정보 조회
router.get('/me', catchAsync(async (req, res, next) => {
  let token;
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }

  if (!token) {
    return next(new AppError('토큰이 필요합니다.', 401));
  }

  const decoded = verifyToken(token);
  const user = await prisma.user.findUnique({
    where: { id: decoded.userId },
    select: {
      id: true,
      email: true,
      name: true,
      company: true,
      role: true,
      isActive: true,
      createdAt: true,
      lastLoginAt: true
    }
  });

  if (!user) {
    return next(new AppError('사용자를 찾을 수 없습니다.', 404));
  }

  res.json({
    success: true,
    data: { user }
  });
}));

export default router;