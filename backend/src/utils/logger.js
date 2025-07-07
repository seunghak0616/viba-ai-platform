import winston from 'winston';
import DailyRotateFile from 'winston-daily-rotate-file';
import config from '../config/index.js';

// 로그 포맷 정의
const logFormat = winston.format.combine(
  winston.format.timestamp({
    format: 'YYYY-MM-DD HH:mm:ss'
  }),
  winston.format.errors({ stack: true }),
  winston.format.json(),
  winston.format.prettyPrint()
);

// 콘솔 로그 포맷 (개발 환경용)
const consoleFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({
    format: 'HH:mm:ss'
  }),
  winston.format.printf(({ timestamp, level, message, ...meta }) => {
    let metaStr = Object.keys(meta).length ? JSON.stringify(meta, null, 2) : '';
    return `${timestamp} [${level}]: ${message} ${metaStr}`;
  })
);

// 로그 전송 설정
const transports = [];

// 콘솔 출력 (개발 환경)
if (config.env === 'development') {
  transports.push(
    new winston.transports.Console({
      format: consoleFormat,
      level: 'debug'
    })
  );
}

// 파일 로그 (프로덕션 환경에서만)
if (config.env === 'production') {
  transports.push(
    // 에러 로그
    new DailyRotateFile({
      filename: '/app/logs/error-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      level: 'error',
      format: logFormat,
      maxFiles: config.logging.maxFiles,
      maxSize: config.logging.maxSize,
    zippedArchive: true
    }),
    
    // 전체 로그
    new DailyRotateFile({
      filename: '/app/logs/combined-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      format: logFormat,
      maxFiles: config.logging.maxFiles,
      maxSize: config.logging.maxSize,
      zippedArchive: true
    })
  );
}

// 프로덕션 환경에서는 콘솔에도 JSON 형태로 출력
if (config.env === 'production') {
  transports.push(
    new winston.transports.Console({
      format: logFormat,
      level: 'info'
    })
  );
}

// 로거 생성
const logger = winston.createLogger({
  level: config.logging.level,
  format: logFormat,
  defaultMeta: {
    service: 'bim-backend',
    environment: config.env
  },
  transports,
  
  // 예외 처리
  exceptionHandlers: [
    new DailyRotateFile({
      filename: 'logs/exceptions-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxFiles: config.logging.maxFiles,
      maxSize: config.logging.maxSize
    })
  ],
  
  // Promise rejection 처리
  rejectionHandlers: [
    new DailyRotateFile({
      filename: 'logs/rejections-%DATE%.log',
      datePattern: 'YYYY-MM-DD',
      maxFiles: config.logging.maxFiles,
      maxSize: config.logging.maxSize
    })
  ]
});

// 커스텀 로그 메서드 추가
logger.api = (req, res, responseTime) => {
  logger.info('API Request', {
    method: req.method,
    url: req.originalUrl,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    statusCode: res.statusCode,
    responseTime: `${responseTime}ms`,
    userId: req.user?.id || 'anonymous'
  });
};

logger.bim = (action, data) => {
  logger.info('BIM Operation', {
    action,
    ...data,
    timestamp: new Date().toISOString()
  });
};

logger.nlp = (operation, data) => {
  logger.info('NLP Operation', {
    operation,
    ...data,
    timestamp: new Date().toISOString()
  });
};

logger.security = (event, data) => {
  logger.warn('Security Event', {
    event,
    ...data,
    timestamp: new Date().toISOString()
  });
};

export default logger;