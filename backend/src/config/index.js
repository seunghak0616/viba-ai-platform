import dotenv from 'dotenv';

dotenv.config();

const config = {
  env: process.env.NODE_ENV || 'development',
  port: process.env.PORT || 5000,
  
  // 데이터베이스 설정
  database: {
    url: process.env.DATABASE_URL || 'postgresql://bim_user:bim_password@localhost:5432/bim_platform',
    maxConnections: parseInt(process.env.DB_MAX_CONNECTIONS) || 20,
    ssl: process.env.NODE_ENV === 'production'
  },

  // Redis 설정
  redis: {
    url: process.env.REDIS_URL || 'redis://localhost:6379',
    ttl: parseInt(process.env.REDIS_TTL) || 3600 // 1시간
  },

  // JWT 설정
  jwt: {
    secret: process.env.JWT_SECRET || 'your-super-secret-jwt-key',
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
    refreshExpiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d'
  },

  // OpenAI 설정
  openai: {
    apiKey: process.env.OPENAI_API_KEY,
    model: process.env.OPENAI_MODEL || 'gpt-4',
    maxTokens: parseInt(process.env.OPENAI_MAX_TOKENS) || 4096,
    temperature: parseFloat(process.env.OPENAI_TEMPERATURE) || 0.7
  },

  // Gemini AI 설정 (백업용)
  gemini: {
    apiKey: process.env.GEMINI_API_KEY,
    model: process.env.GEMINI_MODEL || 'gemini-1.5-pro',
    maxTokens: parseInt(process.env.GEMINI_MAX_TOKENS) || 8192,
    temperature: parseFloat(process.env.GEMINI_TEMPERATURE) || 0.7,
    topK: parseInt(process.env.GEMINI_TOP_K) || 40,
    topP: parseFloat(process.env.GEMINI_TOP_P) || 0.95,
    safetyLevel: process.env.GEMINI_SAFETY_LEVEL || 'BLOCK_MEDIUM_AND_ABOVE'
  },

  // NLP 엔진 설정
  nlp: {
    url: process.env.NLP_ENGINE_URL || 'http://localhost:8000',
    timeout: parseInt(process.env.NLP_TIMEOUT) || 30000 // 30초
  },

  // CORS 설정
  cors: {
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000'
  },

  // 보안 설정
  security: {
    rateLimitWindow: parseInt(process.env.RATE_LIMIT_WINDOW) || 15, // 분
    rateLimitMax: parseInt(process.env.RATE_LIMIT_MAX) || 100,
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS) || 12
  },

  // 파일 업로드 설정
  upload: {
    maxFileSize: process.env.MAX_FILE_SIZE || '500MB',
    allowedTypes: (process.env.ALLOWED_FILE_TYPES || 'ifc,dwg,dxf,pdf').split(','),
    uploadPath: process.env.UPLOAD_PATH || './uploads',
    tempPath: process.env.TEMP_PATH || './temp'
  },

  // 이메일 설정
  email: {
    service: 'gmail',
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_PASS
  },

  // 로그 설정
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || './logs/app.log',
    maxFiles: process.env.LOG_MAX_FILES || '14d',
    maxSize: process.env.LOG_MAX_SIZE || '20m'
  },

  // 외부 서비스 설정
  services: {
    sentry: {
      dsn: process.env.SENTRY_DSN
    },
    newRelic: {
      licenseKey: process.env.NEW_RELIC_LICENSE_KEY
    }
  },

  // BIM 관련 설정
  bim: {
    defaultUnits: 'metric',
    maxModelSize: '500MB',
    supportedFormats: ['ifc', 'dwg', 'dxf'],
    renderTimeout: 60000, // 1분
    optimizationLevel: process.env.BIM_OPTIMIZATION_LEVEL || 'medium'
  },

  // 캐싱 설정
  cache: {
    defaultTtl: 3600, // 1시간
    maxMemory: process.env.CACHE_MAX_MEMORY || '100mb',
    compressionLevel: parseInt(process.env.CACHE_COMPRESSION_LEVEL) || 6
  },

  // 프로덕션 설정
  production: {
    domain: process.env.DOMAIN || 'bim-platform.com',
    ssl: {
      cert: process.env.SSL_CERT_PATH,
      key: process.env.SSL_KEY_PATH
    },
    cdn: {
      url: process.env.CDN_URL,
      bucket: process.env.S3_BUCKET
    }
  }
};

export default config;