import express from 'express';
import axios from 'axios';
import logger from '../utils/logger.js';
import authMiddleware from '../middleware/auth.js';

const router = express.Router();

// Python AI 서비스 URL
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// AI 서비스 프록시 미들웨어
const aiProxy = async (req, res, next) => {
  try {
    const aiServiceUrl = `${AI_SERVICE_URL}${req.originalUrl.replace('/api/ai', '/api')}`;
    
    logger.info(`AI 서비스 프록시 요청: ${req.method} ${aiServiceUrl}`);
    
    const response = await axios({
      method: req.method,
      url: aiServiceUrl,
      data: req.body,
      headers: {
        'Content-Type': req.headers['content-type'] || 'application/json',
        'Authorization': req.headers.authorization || ''
      },
      timeout: 30000 // 30초 타임아웃
    });
    
    res.status(response.status).json(response.data);
  } catch (error) {
    logger.error('AI 서비스 프록시 오류:', error.message);
    
    if (error.response) {
      // Python 서비스에서 응답을 받았지만 오류 상태
      res.status(error.response.status).json({
        success: false,
        message: error.response.data?.message || 'AI 서비스 오류',
        error: error.response.data
      });
    } else if (error.request) {
      // 요청은 보냈지만 응답을 받지 못함
      res.status(503).json({
        success: false,
        message: 'AI 서비스에 연결할 수 없습니다.',
        error: 'Service Unavailable'
      });
    } else {
      // 요청 설정 중 오류
      res.status(500).json({
        success: false,
        message: '내부 서버 오류',
        error: error.message
      });
    }
  }
};

// AI 서비스 상태 확인
router.get('/health', async (req, res) => {
  try {
    const response = await axios.get(`${AI_SERVICE_URL}/health`, {
      timeout: 5000
    });
    
    res.json({
      success: true,
      message: 'AI 서비스 연결 정상',
      aiService: response.data
    });
  } catch (error) {
    res.status(503).json({
      success: false,
      message: 'AI 서비스 연결 실패',
      error: error.message
    });
  }
});

// AI 에이전트 목록 조회
router.get('/agents', authMiddleware, aiProxy);

// AI 분석 실행
router.post('/analyze', authMiddleware, aiProxy);

// AI 채팅
router.post('/chat', authMiddleware, aiProxy);

// AI 파일 분석
router.post('/analyze-file', authMiddleware, aiProxy);

// AI 종합 분석
router.post('/comprehensive-analysis', authMiddleware, aiProxy);

// 모든 AI 관련 요청을 프록시
router.all('*', authMiddleware, aiProxy);

export default router;