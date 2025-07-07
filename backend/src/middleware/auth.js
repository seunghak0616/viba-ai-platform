import jwt from 'jsonwebtoken';
import { AppError, catchAsync } from './errorHandler.js';
import config from '../config/index.js';
import logger from '../utils/logger.js';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

// JWT 토큰 생성
export const generateToken = (userId) => {
  return jwt.sign({ userId }, config.jwt.secret, {
    expiresIn: config.jwt.expiresIn
  });
};

// 리프레시 토큰 생성
export const generateRefreshToken = (userId) => {
  return jwt.sign({ userId }, config.jwt.secret, {
    expiresIn: config.jwt.refreshExpiresIn
  });
};

// 토큰 검증
export const verifyToken = (token) => {
  return jwt.verify(token, config.jwt.secret);
};

// 인증 미들웨어
const authMiddleware = catchAsync(async (req, res, next) => {
  // 1) 토큰 확인
  let token;
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  } else if (req.cookies?.jwt) {
    token = req.cookies.jwt;
  }

  if (!token) {
    logger.security('토큰 없음', { 
      ip: req.ip, 
      url: req.originalUrl,
      userAgent: req.get('User-Agent')
    });
    return next(new AppError('로그인이 필요합니다. 토큰을 제공해주세요.', 401));
  }

  // 2) 토큰 검증
  let decoded;
  try {
    decoded = verifyToken(token);
  } catch (err) {
    logger.security('토큰 검증 실패', { 
      error: err.message,
      ip: req.ip,
      token: token.substring(0, 20) + '...'
    });
    
    if (err.name === 'TokenExpiredError') {
      return next(new AppError('토큰이 만료되었습니다. 다시 로그인해주세요.', 401));
    }
    return next(new AppError('잘못된 토큰입니다.', 401));
  }

  // 3) 사용자 존재 확인
  const user = await prisma.user.findUnique({
    where: { id: decoded.userId },
    select: {
      id: true,
      email: true,
      name: true,
      role: true,
      isActive: true,
      passwordChangedAt: true
    }
  });

  if (!user) {
    logger.security('사용자 없음', { 
      userId: decoded.userId,
      ip: req.ip
    });
    return next(new AppError('토큰에 해당하는 사용자가 존재하지 않습니다.', 401));
  }

  // 4) 계정 활성화 확인
  if (!user.isActive) {
    logger.security('비활성 계정 접근', { 
      userId: user.id,
      ip: req.ip
    });
    return next(new AppError('비활성화된 계정입니다. 관리자에게 문의하세요.', 401));
  }

  // 5) 계정 잠금 확인 (SQLite 스키마에 맞춤)
  // 추후 계정 잠금 기능은 별도 테이블로 구현 예정

  // 6) 비밀번호 변경 후 토큰 발급 확인
  if (user.passwordChangedAt) {
    const changedTimestamp = parseInt(user.passwordChangedAt.getTime() / 1000, 10);
    if (decoded.iat < changedTimestamp) {
      logger.security('비밀번호 변경 후 구 토큰 사용', { 
        userId: user.id,
        ip: req.ip
      });
      return next(new AppError('비밀번호가 변경되었습니다. 다시 로그인해주세요.', 401));
    }
  }

  // 7) 사용자 정보를 req 객체에 추가
  req.user = user;
  
  // 8) 로그인 기록
  logger.info('인증 성공', {
    userId: user.id,
    email: user.email,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    url: req.originalUrl
  });

  next();
});

// 역할 기반 권한 확인
export const restrictTo = (...roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      logger.security('권한 부족', {
        userId: req.user.id,
        userRole: req.user.role,
        requiredRoles: roles,
        url: req.originalUrl,
        ip: req.ip
      });
      return next(new AppError('이 작업을 수행할 권한이 없습니다.', 403));
    }
    next();
  };
};

// 리소스 소유권 확인
export const checkOwnership = (Model, paramName = 'id') => {
  return catchAsync(async (req, res, next) => {
    const resourceId = req.params[paramName];
    const resource = await Model.findUnique({
      where: { id: resourceId },
      select: { userId: true }
    });

    if (!resource) {
      return next(new AppError('리소스를 찾을 수 없습니다.', 404));
    }

    if (resource.userId !== req.user.id && req.user.role !== 'ADMIN') {
      logger.security('소유권 위반', {
        userId: req.user.id,
        resourceId,
        resourceOwner: resource.userId,
        ip: req.ip
      });
      return next(new AppError('이 리소스에 접근할 권한이 없습니다.', 403));
    }

    next();
  });
};

// 선택적 인증 (토큰이 있으면 검증, 없어도 진행)
export const optionalAuth = catchAsync(async (req, res, next) => {
  let token;
  if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
    token = req.headers.authorization.split(' ')[1];
  }

  if (token) {
    try {
      const decoded = verifyToken(token);
      const user = await prisma.user.findUnique({
        where: { id: decoded.userId },
        select: {
          id: true,
          email: true,
          name: true,
          role: true,
          isActive: true
        }
      });

      if (user && user.isActive) {
        req.user = user;
      }
    } catch (err) {
      // 토큰이 잘못되어도 진행
      logger.warn('선택적 인증 실패', { error: err.message });
    }
  }

  next();
});

export default authMiddleware;