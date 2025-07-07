/**
 * AI 세션 관리 라우터
 * ==================
 * 
 * AI 에이전트 세션 생성, 관리, 통계 조회
 * 
 * @version 1.0
 * @author VIBA AI Team
 * @date 2025.07.07
 */

import express from 'express';
import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';
import { body, validationResult } from 'express-validator';

const router = express.Router();
const prisma = new PrismaClient();

// JWT 토큰 검증 미들웨어
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
        return res.status(401).json({ 
            success: false, 
            message: '인증 토큰이 필요합니다.' 
        });
    }

    jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
        if (err) {
            return res.status(403).json({ 
                success: false, 
                message: '유효하지 않은 토큰입니다.' 
            });
        }
        req.user = user;
        next();
    });
};

/**
 * @route GET /api/ai-sessions
 * @desc 사용자의 AI 세션 목록 조회
 * @access Private
 */
router.get('/', authenticateToken, async (req, res) => {
    try {
        const { status, agentId, limit = 20, offset = 0 } = req.query;
        
        const whereClause = {
            userId: req.user.id,
        };
        
        if (status) {
            whereClause.status = status;
        }
        
        if (agentId) {
            whereClause.agentId = agentId;
        }
        
        const sessions = await prisma.aISession.findMany({
            where: whereClause,
            orderBy: { updatedAt: 'desc' },
            take: parseInt(limit),
            skip: parseInt(offset),
            include: {
                user: {
                    select: { id: true, name: true, email: true }
                },
                project: {
                    select: { id: true, name: true }
                }
            }
        });
        
        const total = await prisma.aISession.count({ where: whereClause });
        
        res.json({
            success: true,
            data: sessions,
            pagination: {
                total,
                limit: parseInt(limit),
                offset: parseInt(offset),
                hasMore: total > parseInt(offset) + parseInt(limit)
            }
        });
        
    } catch (error) {
        console.error('AI 세션 목록 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 세션 목록을 조회하는 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

/**
 * @route POST /api/ai-sessions
 * @desc 새로운 AI 세션 생성
 * @access Private
 */
router.post('/', [
    authenticateToken,
    body('agentId').notEmpty().withMessage('AI 에이전트 ID는 필수입니다.'),
    body('agentName').notEmpty().withMessage('AI 에이전트 이름은 필수입니다.'),
    body('projectId').optional().isString().withMessage('프로젝트 ID는 문자열이어야 합니다.'),
    body('context').optional().isObject().withMessage('컨텍스트는 객체여야 합니다.'),
], async (req, res) => {
    try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({
                success: false,
                message: '입력 값이 올바르지 않습니다.',
                errors: errors.array()
            });
        }
        
        const { agentId, agentName, projectId, context } = req.body;
        
        // 프로젝트 존재 확인 (projectId가 제공된 경우)
        if (projectId) {
            const project = await prisma.project.findFirst({
                where: {
                    id: projectId,
                    OR: [
                        { userId: req.user.id },
                        { 
                            collaborators: {
                                some: { userId: req.user.id, isActive: true }
                            }
                        }
                    ]
                }
            });
            
            if (!project) {
                return res.status(404).json({
                    success: false,
                    message: '프로젝트를 찾을 수 없거나 접근 권한이 없습니다.'
                });
            }
        }
        
        // 세션 만료 시간 설정 (24시간)
        const expiresAt = new Date();
        expiresAt.setHours(expiresAt.getHours() + 24);
        
        const session = await prisma.aISession.create({
            data: {
                sessionId: `ai_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                agentId,
                agentName,
                userId: req.user.id,
                projectId: projectId || null,
                context: context ? JSON.stringify(context) : null,
                expiresAt,
                status: 'ACTIVE'
            },
            include: {
                user: {
                    select: { id: true, name: true, email: true }
                },
                project: {
                    select: { id: true, name: true }
                }
            }
        });
        
        // 활동 로그 기록
        await prisma.activityLog.create({
            data: {
                action: 'AI_SESSION_CREATED',
                details: JSON.stringify({
                    sessionId: session.sessionId,
                    agentId,
                    agentName
                }),
                userId: req.user.id,
                projectId: projectId || null,
                ipAddress: req.ip,
                userAgent: req.get('User-Agent')
            }
        });
        
        res.status(201).json({
            success: true,
            message: 'AI 세션이 성공적으로 생성되었습니다.',
            data: session
        });
        
    } catch (error) {
        console.error('AI 세션 생성 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 세션을 생성하는 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

/**
 * @route GET /api/ai-sessions/:sessionId
 * @desc 특정 AI 세션 조회
 * @access Private
 */
router.get('/:sessionId', authenticateToken, async (req, res) => {
    try {
        const { sessionId } = req.params;
        
        const session = await prisma.aISession.findFirst({
            where: {
                sessionId,
                userId: req.user.id
            },
            include: {
                user: {
                    select: { id: true, name: true, email: true }
                },
                project: {
                    select: { id: true, name: true }
                }
            }
        });
        
        if (!session) {
            return res.status(404).json({
                success: false,
                message: 'AI 세션을 찾을 수 없습니다.'
            });
        }
        
        // 만료된 세션 체크
        if (new Date() > session.expiresAt) {
            await prisma.aISession.update({
                where: { id: session.id },
                data: { status: 'EXPIRED' }
            });
            
            return res.status(410).json({
                success: false,
                message: 'AI 세션이 만료되었습니다.'
            });
        }
        
        res.json({
            success: true,
            data: session
        });
        
    } catch (error) {
        console.error('AI 세션 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 세션을 조회하는 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

/**
 * @route PUT /api/ai-sessions/:sessionId
 * @desc AI 세션 업데이트 (메시지 추가, 상태 변경)
 * @access Private
 */
router.put('/:sessionId', [
    authenticateToken,
    body('messages').optional().isArray().withMessage('메시지는 배열이어야 합니다.'),
    body('status').optional().isIn(['ACTIVE', 'IDLE', 'EXPIRED', 'TERMINATED']).withMessage('올바른 상태값을 입력하세요.'),
    body('responseTime').optional().isNumeric().withMessage('응답 시간은 숫자여야 합니다.'),
    body('tokenUsage').optional().isObject().withMessage('토큰 사용량은 객체여야 합니다.'),
], async (req, res) => {
    try {
        const errors = validationResult(req);
        if (!errors.isEmpty()) {
            return res.status(400).json({
                success: false,
                message: '입력 값이 올바르지 않습니다.',
                errors: errors.array()
            });
        }
        
        const { sessionId } = req.params;
        const { messages, status, responseTime, tokenUsage } = req.body;
        
        const session = await prisma.aISession.findFirst({
            where: {
                sessionId,
                userId: req.user.id
            }
        });
        
        if (!session) {
            return res.status(404).json({
                success: false,
                message: 'AI 세션을 찾을 수 없습니다.'
            });
        }
        
        const updateData = {
            lastActiveAt: new Date(),
            updatedAt: new Date()
        };
        
        if (messages) {
            updateData.messages = JSON.stringify(messages);
            updateData.messageCount = messages.length;
        }
        
        if (status) {
            updateData.status = status;
        }
        
        if (responseTime !== undefined) {
            updateData.responseTime = parseFloat(responseTime);
        }
        
        if (tokenUsage) {
            updateData.tokenUsage = JSON.stringify(tokenUsage);
        }
        
        const updatedSession = await prisma.aISession.update({
            where: { id: session.id },
            data: updateData,
            include: {
                user: {
                    select: { id: true, name: true, email: true }
                },
                project: {
                    select: { id: true, name: true }
                }
            }
        });
        
        res.json({
            success: true,
            message: 'AI 세션이 성공적으로 업데이트되었습니다.',
            data: updatedSession
        });
        
    } catch (error) {
        console.error('AI 세션 업데이트 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 세션을 업데이트하는 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

/**
 * @route DELETE /api/ai-sessions/:sessionId
 * @desc AI 세션 종료/삭제
 * @access Private
 */
router.delete('/:sessionId', authenticateToken, async (req, res) => {
    try {
        const { sessionId } = req.params;
        
        const session = await prisma.aISession.findFirst({
            where: {
                sessionId,
                userId: req.user.id
            }
        });
        
        if (!session) {
            return res.status(404).json({
                success: false,
                message: 'AI 세션을 찾을 수 없습니다.'
            });
        }
        
        await prisma.aISession.update({
            where: { id: session.id },
            data: {
                status: 'TERMINATED',
                updatedAt: new Date()
            }
        });
        
        // 활동 로그 기록
        await prisma.activityLog.create({
            data: {
                action: 'AI_SESSION_TERMINATED',
                details: JSON.stringify({
                    sessionId: session.sessionId,
                    agentId: session.agentId,
                    duration: Date.now() - new Date(session.createdAt).getTime()
                }),
                userId: req.user.id,
                projectId: session.projectId,
                ipAddress: req.ip,
                userAgent: req.get('User-Agent')
            }
        });
        
        res.json({
            success: true,
            message: 'AI 세션이 성공적으로 종료되었습니다.'
        });
        
    } catch (error) {
        console.error('AI 세션 종료 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 세션을 종료하는 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

/**
 * @route GET /api/ai-sessions/stats/summary
 * @desc AI 세션 통계 조회
 * @access Private
 */
router.get('/stats/summary', authenticateToken, async (req, res) => {
    try {
        const { period = '7d' } = req.query;
        
        // 기간 설정
        const periodMap = {
            '1d': 1,
            '7d': 7,
            '30d': 30,
            '90d': 90
        };
        
        const days = periodMap[period] || 7;
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - days);
        
        // 전체 세션 수
        const totalSessions = await prisma.aISession.count({
            where: {
                userId: req.user.id,
                createdAt: { gte: startDate }
            }
        });
        
        // 활성 세션 수
        const activeSessions = await prisma.aISession.count({
            where: {
                userId: req.user.id,
                status: 'ACTIVE',
                expiresAt: { gt: new Date() }
            }
        });
        
        // 에이전트별 사용 통계
        const agentStats = await prisma.aISession.groupBy({
            by: ['agentId', 'agentName'],
            where: {
                userId: req.user.id,
                createdAt: { gte: startDate }
            },
            _count: { agentId: true },
            _avg: { responseTime: true }
        });
        
        // 일별 세션 생성 통계
        const dailyStats = await prisma.$queryRaw`
            SELECT 
                DATE(createdAt) as date,
                COUNT(*) as sessions,
                AVG(responseTime) as avgResponseTime
            FROM ai_sessions 
            WHERE userId = ${req.user.id} 
            AND createdAt >= ${startDate.toISOString()}
            GROUP BY DATE(createdAt)
            ORDER BY date DESC
        `;
        
        res.json({
            success: true,
            data: {
                summary: {
                    totalSessions,
                    activeSessions,
                    period: `${days}일`
                },
                agentStats: agentStats.map(stat => ({
                    agentId: stat.agentId,
                    agentName: stat.agentName,
                    sessionCount: stat._count.agentId,
                    avgResponseTime: stat._avg.responseTime || 0
                })),
                dailyStats
            }
        });
        
    } catch (error) {
        console.error('AI 세션 통계 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: 'AI 세션 통계를 조회하는 중 오류가 발생했습니다.',
            error: error.message
        });
    }
});

export default router;