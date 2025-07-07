#!/usr/bin/env node
/**
 * VIBA AI 기존 데이터 마이그레이션 스크립트
 * ==========================================
 * 
 * 백업된 데이터베이스에서 새로운 통합 스키마로 데이터 이전
 * 
 * @version 1.0
 * @author VIBA AI Team
 * @date 2025.07.07
 */

import fs from 'fs';
import path from 'path';
import sqlite3 from 'sqlite3';

sqlite3.verbose();

// 색상 정의
const colors = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
};

// 로그 함수
const log = {
    info: (msg) => console.log(`${colors.blue}[INFO]${colors.reset} ${msg}`),
    success: (msg) => console.log(`${colors.green}[SUCCESS]${colors.reset} ${msg}`),
    warning: (msg) => console.log(`${colors.yellow}[WARNING]${colors.reset} ${msg}`),
    error: (msg) => console.log(`${colors.red}[ERROR]${colors.reset} ${msg}`),
    step: (msg) => console.log(`${colors.cyan}[STEP]${colors.reset} ${msg}`),
};

// 설정
const config = {
    backendDir: '/Users/seunghakwoo/Documents/Cursor/Z/backend',
    oldDb: '/Users/seunghakwoo/Documents/Cursor/Z/backend/data/dev-old.db',
    newDb: '/Users/seunghakwoo/Documents/Cursor/Z/backend/data/dev.db',
};

/**
 * 기존 데이터 추출
 */
async function extractOldData() {
    log.step('기존 데이터 추출');
    
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(config.oldDb, sqlite3.OPEN_READONLY, (err) => {
            if (err) {
                log.error(`기존 데이터베이스 열기 실패: ${err.message}`);
                reject(err);
                return;
            }
        });
        
        const extractedData = {};
        
        // 추출할 테이블 목록
        const tables = ['users', 'refresh_tokens', 'projects', 'bim_models', 'activity_logs'];
        
        let pendingTables = tables.length;
        if (pendingTables === 0) {
            db.close();
            resolve(extractedData);
            return;
        }
        
        // 각 테이블의 데이터 추출
        tables.forEach(table => {
            db.all(`SELECT * FROM ${table}`, (err, rows) => {
                if (err) {
                    log.warning(`테이블 ${table} 조회 실패: ${err.message}`);
                    extractedData[table] = [];
                } else {
                    extractedData[table] = rows;
                    log.info(`테이블 ${table}: ${rows.length}개 레코드 추출`);
                }
                
                pendingTables--;
                if (pendingTables === 0) {
                    db.close();
                    resolve(extractedData);
                }
            });
        });
    });
}

/**
 * 새 데이터베이스에 데이터 삽입
 */
async function insertNewData(extractedData) {
    log.step('새 데이터베이스에 데이터 삽입');
    
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(config.newDb, (err) => {
            if (err) {
                log.error(`새 데이터베이스 열기 실패: ${err.message}`);
                reject(err);
                return;
            }
        });
        
        db.serialize(() => {
            db.run('BEGIN TRANSACTION');
            
            try {
                // 1. 사용자 데이터 이전
                if (extractedData.users && extractedData.users.length > 0) {
                    const userStmt = db.prepare(`
                        INSERT INTO users (
                            id, email, password, name, company, role, isActive, 
                            emailVerified, emailVerifiedAt, loginAttempts, lockUntil,
                            passwordChangedAt, lastLoginAt, lastLoginIp, preferences,
                            subscription, createdAt, updatedAt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    `);
                    
                    extractedData.users.forEach(user => {
                        userStmt.run([
                            user.id, user.email, user.password, user.name, user.company,
                            user.role, user.isActive, user.emailVerified, user.emailVerifiedAt,
                            user.loginAttempts, user.lockUntil, user.passwordChangedAt,
                            user.lastLoginAt, user.lastLoginIp, user.preferences,
                            user.subscription, user.createdAt, user.updatedAt
                        ]);
                    });
                    userStmt.finalize();
                    log.success(`사용자 ${extractedData.users.length}개 레코드 이전 완료`);
                }
                
                // 2. 리프레시 토큰 데이터 이전
                if (extractedData.refresh_tokens && extractedData.refresh_tokens.length > 0) {
                    const tokenStmt = db.prepare(`
                        INSERT INTO refresh_tokens (id, token, userId, expiresAt, createdAt)
                        VALUES (?, ?, ?, ?, ?)
                    `);
                    
                    extractedData.refresh_tokens.forEach(token => {
                        tokenStmt.run([
                            token.id, token.token, token.userId, token.expiresAt, token.createdAt
                        ]);
                    });
                    tokenStmt.finalize();
                    log.success(`리프레시 토큰 ${extractedData.refresh_tokens.length}개 레코드 이전 완료`);
                }
                
                // 3. 프로젝트 데이터 이전
                if (extractedData.projects && extractedData.projects.length > 0) {
                    const projectStmt = db.prepare(`
                        INSERT INTO projects (
                            id, name, description, status, metadata, settings,
                            userId, createdAt, updatedAt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    `);
                    
                    extractedData.projects.forEach(project => {
                        projectStmt.run([
                            project.id, project.name, project.description, project.status,
                            project.metadata, project.settings, project.userId,
                            project.createdAt, project.updatedAt
                        ]);
                    });
                    projectStmt.finalize();
                    log.success(`프로젝트 ${extractedData.projects.length}개 레코드 이전 완료`);
                }
                
                // 4. BIM 모델 데이터 이전
                if (extractedData.bim_models && extractedData.bim_models.length > 0) {
                    const bimStmt = db.prepare(`
                        INSERT INTO bim_models (
                            id, name, description, type, naturalLanguageInput, processedParams,
                            geometryData, materials, dimensions, spatial, metadata, properties,
                            constraints, ifcFileUrl, thumbnailUrl, previewUrl, version,
                            parentId, isPublic, isTemplate, userId, projectId, createdAt, updatedAt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    `);
                    
                    extractedData.bim_models.forEach(model => {
                        bimStmt.run([
                            model.id, model.name, model.description, model.type,
                            model.naturalLanguageInput, model.processedParams,
                            model.geometryData, model.materials, model.dimensions,
                            model.spatial, model.metadata, model.properties,
                            model.constraints, model.ifcFileUrl, model.thumbnailUrl,
                            model.previewUrl, model.version, model.parentId,
                            model.isPublic, model.isTemplate, model.userId,
                            model.projectId, model.createdAt, model.updatedAt
                        ]);
                    });
                    bimStmt.finalize();
                    log.success(`BIM 모델 ${extractedData.bim_models.length}개 레코드 이전 완료`);
                }
                
                // 5. 활동 로그 데이터 이전
                if (extractedData.activity_logs && extractedData.activity_logs.length > 0) {
                    const logStmt = db.prepare(`
                        INSERT INTO activity_logs (
                            id, action, details, ipAddress, userAgent,
                            userId, projectId, bimModelId, createdAt
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    `);
                    
                    extractedData.activity_logs.forEach(activityLog => {
                        logStmt.run([
                            activityLog.id, activityLog.action, activityLog.details,
                            activityLog.ipAddress, activityLog.userAgent,
                            activityLog.userId, activityLog.projectId,
                            activityLog.bimModelId, activityLog.createdAt
                        ]);
                    });
                    logStmt.finalize();
                    log.success(`활동 로그 ${extractedData.activity_logs.length}개 레코드 이전 완료`);
                }
                
                db.run('COMMIT', (err) => {
                    if (err) {
                        log.error(`트랜잭션 커밋 실패: ${err.message}`);
                        reject(err);
                    } else {
                        log.success('모든 데이터 이전 완료');
                        db.close();
                        resolve();
                    }
                });
                
            } catch (error) {
                db.run('ROLLBACK');
                log.error(`데이터 이전 실패: ${error.message}`);
                reject(error);
            }
        });
    });
}

/**
 * 메인 마이그레이션 프로세스
 */
async function main() {
    console.log(`${colors.magenta}
╔══════════════════════════════════════════════════════════════╗
║                    VIBA AI 데이터 마이그레이션                    ║
║                                                              ║
║          기존 데이터 → 통합 스키마 데이터 이전                      ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
    
    try {
        // 기존 데이터베이스 파일 확인
        if (!fs.existsSync(config.oldDb)) {
            log.error(`기존 데이터베이스 파일을 찾을 수 없습니다: ${config.oldDb}`);
            process.exit(1);
        }
        
        // 새 데이터베이스 파일 확인
        if (!fs.existsSync(config.newDb)) {
            log.error(`새 데이터베이스 파일을 찾을 수 없습니다: ${config.newDb}`);
            process.exit(1);
        }
        
        // 1. 기존 데이터 추출
        const extractedData = await extractOldData();
        
        // 2. 새 데이터베이스에 데이터 삽입
        await insertNewData(extractedData);
        
        console.log(`\\n${colors.green}🎉 데이터 마이그레이션 완료!${colors.reset}`);
        
        // 통계 출력
        const totalRecords = Object.values(extractedData).reduce((sum, records) => sum + records.length, 0);
        console.log(`
📊 마이그레이션 요약:
   • 총 레코드: ${totalRecords}개
   • 사용자: ${extractedData.users?.length || 0}개
   • 프로젝트: ${extractedData.projects?.length || 0}개
   • BIM 모델: ${extractedData.bim_models?.length || 0}개
   • 활동 로그: ${extractedData.activity_logs?.length || 0}개

🚀 다음 단계:
   1. Prisma 클라이언트 재생성
   2. API 서버 재시작
   3. 기능 테스트 수행
        `);
        
    } catch (error) {
        log.error(`마이그레이션 실패: ${error.message}`);
        console.error(error);
        process.exit(1);
    }
}

// 스크립트 실행
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(console.error);
}

export { main, extractOldData, insertNewData };