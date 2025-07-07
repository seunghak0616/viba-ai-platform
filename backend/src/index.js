import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import compression from 'compression';
import rateLimit from 'express-rate-limit';
import { createServer } from 'http';
import { Server } from 'socket.io';
import dotenv from 'dotenv';

import config from './config/index.js';
import logger from './utils/logger.js';
import errorHandler from './middleware/errorHandler.js';
import authMiddleware from './middleware/auth.js';

// Routes (including new unified routes)
import authRoutes from './routes/auth.js';
import projectRoutes from './routes/projects.js';
import bimRoutes from './routes/bim.js';
import parametricBimRoutes from './routes/parametric-bim.js';
import nlpRoutes from './routes/nlp.js';
import aiRoutes from './routes/ai.js';
import aiSessionRoutes from './routes/ai-sessions.js';

// AI 마이크로서비스 프록시
import aiProxyRoutes from './routes/ai-proxy.js';

// Load environment variables
dotenv.config();

const app = express();
const server = createServer(app);
const io = new Server(server, {
  cors: {
    origin: config.cors.origin,
    methods: ["GET", "POST", "PUT", "DELETE"]
  }
});

// Security middleware
app.use(helmet({
  contentSecurityPolicy: false,
  crossOriginEmbedderPolicy: false
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: config.security.rateLimitWindow * 60 * 1000, // 15 minutes
  max: config.security.rateLimitMax, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use(limiter);

// CORS
app.use(cors({
  origin: config.cors.origin,
  credentials: true
}));

// Compression
app.use(compression());

// Body parsing
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Logging
app.use(morgan('combined', { stream: { write: message => logger.info(message.trim()) } }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || '1.0.0',
    environment: config.env
  });
});

// API routes
app.use('/api/auth', authRoutes);
app.use('/api/projects', projectRoutes);
app.use('/api/bim', authMiddleware, bimRoutes);
app.use('/api/parametric-bim', authMiddleware, parametricBimRoutes);
app.use('/api/nlp', nlpRoutes);
app.use('/api/ai', aiRoutes);

// AI 마이크로서비스 프록시 라우트
app.use('/api/ai-agents', authMiddleware, aiProxyRoutes);

// Static files
app.use('/uploads', express.static('uploads'));

// WebSocket connection handling
io.on('connection', (socket) => {
  logger.info(`새로운 WebSocket 연결: ${socket.id}`);
  
  // 프로젝트 룸 참가
  socket.on('join-project', (projectId) => {
    socket.join(`project-${projectId}`);
    logger.info(`Socket ${socket.id}가 프로젝트 ${projectId}에 참가`);
  });

  // 실시간 BIM 모델 업데이트
  socket.on('bim-update', (data) => {
    socket.to(`project-${data.projectId}`).emit('bim-updated', data);
  });

  // 채팅 메시지
  socket.on('chat-message', (data) => {
    socket.to(`project-${data.projectId}`).emit('new-message', data);
  });

  // 연결 해제
  socket.on('disconnect', () => {
    logger.info(`WebSocket 연결 해제: ${socket.id}`);
  });
});

// Error handling
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    success: false,
    message: '요청한 엔드포인트를 찾을 수 없습니다.',
    path: req.originalUrl
  });
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Process terminated');
    process.exit(0);
  });
});

process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

const PORT = config.port;
server.listen(PORT, () => {
  logger.info(`🚀 바이브 코딩 BIM 플랫폼 백엔드 서버가 포트 ${PORT}에서 실행 중입니다.`);
  logger.info(`🌍 환경: ${config.env}`);
  logger.info(`📊 Health check: http://localhost:${PORT}/health`);
});

export { io };
export default app;