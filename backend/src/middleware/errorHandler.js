import logger from '../utils/logger.js';
import config from '../config/index.js';

// 커스텀 에러 클래스
export class AppError extends Error {
  constructor(message, statusCode, isOperational = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';

    Error.captureStackTrace(this, this.constructor);
  }
}

// 개발 환경 에러 응답
const sendErrorDev = (err, res) => {
  res.status(err.statusCode).json({
    success: false,
    status: err.status,
    error: err,
    message: err.message,
    stack: err.stack,
    timestamp: new Date().toISOString()
  });
};

// 프로덕션 환경 에러 응답
const sendErrorProd = (err, res) => {
  // 운영 에러 - 클라이언트에게 메시지 전송
  if (err.isOperational) {
    res.status(err.statusCode).json({
      success: false,
      status: err.status,
      message: err.message,
      timestamp: new Date().toISOString()
    });
  } else {
    // 프로그래밍 에러 - 일반적인 메시지만 전송
    logger.error('프로그래밍 에러:', err);
    
    res.status(500).json({
      success: false,
      status: 'error',
      message: '서버 내부 오류가 발생했습니다.',
      timestamp: new Date().toISOString()
    });
  }
};

// 특정 에러 타입 처리
const handleCastErrorDB = (err) => {
  const message = `잘못된 ${err.path}: ${err.value}`;
  return new AppError(message, 400);
};

const handleDuplicateFieldsDB = (err) => {
  const value = err.errmsg?.match(/(["'])(\\?.)*?\1/)?.[0];
  const message = `중복된 필드 값: ${value}. 다른 값을 사용해주세요.`;
  return new AppError(message, 400);
};

const handleValidationErrorDB = (err) => {
  const errors = Object.values(err.errors).map(el => el.message);
  const message = `잘못된 입력 데이터: ${errors.join('. ')}`;
  return new AppError(message, 400);
};

const handleJWTError = () =>
  new AppError('잘못된 토큰입니다. 다시 로그인해주세요.', 401);

const handleJWTExpiredError = () =>
  new AppError('토큰이 만료되었습니다. 다시 로그인해주세요.', 401);

const handleMulterError = (err) => {
  if (err.code === 'LIMIT_FILE_SIZE') {
    return new AppError('파일 크기가 너무 큽니다.', 400);
  }
  if (err.code === 'LIMIT_FILE_COUNT') {
    return new AppError('파일 개수가 너무 많습니다.', 400);
  }
  if (err.code === 'LIMIT_UNEXPECTED_FILE') {
    return new AppError('예상되지 않은 파일 필드입니다.', 400);
  }
  return new AppError('파일 업로드 중 오류가 발생했습니다.', 400);
};

// 메인 에러 핸들러
const errorHandler = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  // 요청 정보와 함께 에러 로깅
  logger.error('에러 발생:', {
    error: err.message,
    stack: err.stack,
    url: req.originalUrl,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    userId: req.user?.id,
    body: req.body,
    params: req.params,
    query: req.query
  });

  if (config.env === 'development') {
    sendErrorDev(err, res);
  } else {
    let error = { ...err };
    error.message = err.message;

    // 특정 에러 타입별 처리
    if (error.name === 'CastError') error = handleCastErrorDB(error);
    if (error.code === 11000) error = handleDuplicateFieldsDB(error);
    if (error.name === 'ValidationError') error = handleValidationErrorDB(error);
    if (error.name === 'JsonWebTokenError') error = handleJWTError();
    if (error.name === 'TokenExpiredError') error = handleJWTExpiredError();
    if (error.name === 'MulterError') error = handleMulterError(error);

    sendErrorProd(error, res);
  }
};

// 비동기 함수 래퍼
export const catchAsync = (fn) => {
  return (req, res, next) => {
    fn(req, res, next).catch(next);
  };
};

// 404 에러 생성
export const createNotFoundError = (resource = '리소스') => {
  return new AppError(`요청한 ${resource}를 찾을 수 없습니다.`, 404);
};

// 권한 에러 생성
export const createForbiddenError = (action = '작업') => {
  return new AppError(`이 ${action}을 수행할 권한이 없습니다.`, 403);
};

// 인증 에러 생성
export const createUnauthorizedError = () => {
  return new AppError('인증이 필요합니다. 로그인해주세요.', 401);
};

// 검증 에러 생성
export const createValidationError = (field, value) => {
  return new AppError(`잘못된 ${field}: ${value}`, 400);
};

export default errorHandler;