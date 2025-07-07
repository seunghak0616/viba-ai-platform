import express from 'express';
import axios from 'axios';
import { body, param, validationResult } from 'express-validator';
import { catchAsync, AppError } from '../middleware/errorHandler.js';
import config from '../config/index.js';
import logger from '../utils/logger.js';

const router = express.Router();

// AI 마이크로서비스 설정
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8001';
const AI_SERVICE_TIMEOUT = parseInt(process.env.AI_SERVICE_TIMEOUT) || 30000;

// 헬스 체크
router.get('/health', catchAsync(async (req, res, next) => {
  try {
    const response = await axios.get(`${AI_SERVICE_URL}/health`, {
      timeout: 5000
    });
    
    res.json({
      success: true,
      message: 'AI 마이크로서비스 연결 정상',
      data: {
        status: response.data.status,
        ai_service_url: AI_SERVICE_URL,
        response_time: response.headers['x-response-time']
      }
    });
  } catch (error) {
    logger.error('AI 마이크로서비스 헬스 체크 실패', {
      url: AI_SERVICE_URL,
      error: error.message
    });
    
    return next(new AppError('AI 마이크로서비스에 연결할 수 없습니다.', 503));
  }
}));

// AI 에이전트 목록 조회
router.get('/agents', catchAsync(async (req, res, next) => {
  try {
    const response = await axios.get(`${AI_SERVICE_URL}/api/agents`, {
      timeout: AI_SERVICE_TIMEOUT,
      headers: {
        'Authorization': req.headers.authorization,
        'Content-Type': 'application/json'
      }
    });
    
    res.json({
      success: true,
      data: response.data
    });
    
  } catch (error) {
    logger.error('AI 에이전트 목록 조회 실패', {
      userId: req.user?.id,
      error: error.message,
      status: error.response?.status
    });
    
    if (error.response?.status === 404) {
      return next(new AppError('AI 에이전트 서비스를 찾을 수 없습니다.', 404));
    }
    
    return next(new AppError('AI 에이전트 목록을 불러오는 중 오류가 발생했습니다.', 502));
  }
}));

// AI 에이전트와 채팅
router.post('/chat', [
  body('agent_id').notEmpty().withMessage('에이전트 ID가 필요합니다'),
  body('message').notEmpty().withMessage('메시지가 필요합니다'),
  body('session_id').optional().isString().withMessage('세션 ID는 문자열이어야 합니다'),
  body('context').optional().isObject().withMessage('컨텍스트는 객체여야 합니다')
], catchAsync(async (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return next(new AppError(errors.array().map(e => e.msg).join(', '), 400));
  }
  
  const { agent_id, message, session_id, context } = req.body;
  
  try {
    const requestData = {
      agent_id,
      message,
      session_id,
      context: {
        ...context,
        user_id: req.user.id,
        user_role: req.user.role
      }
    };
    
    logger.ai('AI 에이전트 채팅 요청', {
      userId: req.user.id,
      agentId: agent_id,
      messageLength: message.length,
      sessionId: session_id
    });
    
    const response = await axios.post(`${AI_SERVICE_URL}/api/chat`, requestData, {
      timeout: AI_SERVICE_TIMEOUT,
      headers: {
        'Authorization': req.headers.authorization,
        'Content-Type': 'application/json'
      }
    });
    
    logger.ai('AI 에이전트 응답 완료', {
      userId: req.user.id,
      agentId: agent_id,
      responseLength: response.data.response?.length || 0,
      responseTime: response.headers['x-response-time']
    });
    
    res.json({
      success: true,
      data: response.data
    });
    
  } catch (error) {
    logger.error('AI 에이전트 채팅 실패', {
      userId: req.user.id,
      agentId: agent_id,
      error: error.message,
      status: error.response?.status
    });
    
    if (error.code === 'ECONNREFUSED') {
      return next(new AppError('AI 서비스에 연결할 수 없습니다. 서비스가 실행 중인지 확인해주세요.', 503));
    }
    
    if (error.response?.status === 422) {
      return next(new AppError('잘못된 요청 데이터입니다.', 422));
    }
    
    return next(new AppError('AI 에이전트와의 통신 중 오류가 발생했습니다.', 502));
  }
}));

// BIM 모델 분석 요청
router.post('/analyze-bim', [
  body('model_data').notEmpty().withMessage('BIM 모델 데이터가 필요합니다'),
  body('analysis_type').isIn(['spatial', 'sustainability', 'cost', 'performance']).withMessage('유효한 분석 타입을 선택해주세요'),
  body('project_id').optional().isString().withMessage('프로젝트 ID는 문자열이어야 합니다')
], catchAsync(async (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return next(new AppError(errors.array().map(e => e.msg).join(', '), 400));
  }
  
  const { model_data, analysis_type, project_id } = req.body;
  
  try {
    const requestData = {
      model_data,
      analysis_type,
      project_id,
      user_context: {
        user_id: req.user.id,
        user_role: req.user.role
      }
    };
    
    logger.bim('BIM 모델 AI 분석 요청', {
      userId: req.user.id,
      analysisType: analysis_type,
      projectId: project_id,
      modelSize: JSON.stringify(model_data).length
    });
    
    const response = await axios.post(`${AI_SERVICE_URL}/api/analyze-bim`, requestData, {
      timeout: AI_SERVICE_TIMEOUT * 2, // BIM 분석은 더 오래 걸릴 수 있음
      headers: {
        'Authorization': req.headers.authorization,
        'Content-Type': 'application/json'
      }
    });
    
    logger.bim('BIM 모델 AI 분석 완료', {
      userId: req.user.id,
      analysisType: analysis_type,
      responseTime: response.headers['x-response-time']
    });
    
    res.json({
      success: true,
      data: response.data
    });
    
  } catch (error) {
    logger.error('BIM 모델 AI 분석 실패', {
      userId: req.user.id,
      analysisType: analysis_type,
      error: error.message,
      status: error.response?.status
    });
    
    if (error.code === 'ECONNREFUSED') {
      return next(new AppError('AI 분석 서비스에 연결할 수 없습니다.', 503));
    }
    
    if (error.response?.status === 413) {
      return next(new AppError('BIM 모델 데이터가 너무 큽니다.', 413));
    }
    
    return next(new AppError('BIM 모델 분석 중 오류가 발생했습니다.', 502));
  }
}));

// 자연어 처리 요청
router.post('/nlp/process', [
  body('text').notEmpty().withMessage('처리할 텍스트가 필요합니다'),
  body('task_type').isIn(['bim_extraction', 'design_analysis', 'requirements_parsing']).withMessage('유효한 작업 타입을 선택해주세요')
], catchAsync(async (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return next(new AppError(errors.array().map(e => e.msg).join(', '), 400));
  }
  
  const { text, task_type, context } = req.body;
  
  try {
    const requestData = {
      text,
      task_type,
      context: {
        ...context,
        user_id: req.user.id,
        user_role: req.user.role
      }
    };
    
    logger.nlp('자연어 처리 요청', {
      userId: req.user.id,
      taskType: task_type,
      textLength: text.length
    });
    
    const response = await axios.post(`${AI_SERVICE_URL}/api/nlp/process`, requestData, {
      timeout: AI_SERVICE_TIMEOUT,
      headers: {
        'Authorization': req.headers.authorization,
        'Content-Type': 'application/json'
      }
    });
    
    logger.nlp('자연어 처리 완료', {
      userId: req.user.id,
      taskType: task_type,
      responseTime: response.headers['x-response-time']
    });
    
    res.json({
      success: true,
      data: response.data
    });
    
  } catch (error) {
    logger.error('자연어 처리 실패', {
      userId: req.user.id,
      taskType: task_type,
      error: error.message,
      status: error.response?.status
    });
    
    return next(new AppError('자연어 처리 중 오류가 발생했습니다.', 502));
  }
}));

// AI 세션 상태 조회
router.get('/sessions/:sessionId', catchAsync(async (req, res, next) => {
  const { sessionId } = req.params;
  
  try {
    const response = await axios.get(`${AI_SERVICE_URL}/api/sessions/${sessionId}`, {
      timeout: 10000,
      headers: {
        'Authorization': req.headers.authorization,
        'Content-Type': 'application/json'
      },
      params: {
        user_id: req.user.id
      }
    });
    
    res.json({
      success: true,
      data: response.data
    });
    
  } catch (error) {
    if (error.response?.status === 404) {
      return next(new AppError('세션을 찾을 수 없습니다.', 404));
    }
    
    logger.error('AI 세션 조회 실패', {
      userId: req.user.id,
      sessionId,
      error: error.message
    });
    
    return next(new AppError('AI 세션 정보를 불러오는 중 오류가 발생했습니다.', 502));
  }
}));

export default router;