#!/usr/bin/env node
/**
 * VIBA AI 데이터베이스 통합 마이그레이션 스크립트
 * ==========================================
 * 
 * 기존 데이터베이스에서 통합 스키마로 안전하게 마이그레이션
 * 
 * @version 1.0
 * @author VIBA AI Team
 * @date 2025.07.07
 */

import fs from 'fs';
import path from 'path';
import sqlite3 from 'sqlite3';
import { spawn } from 'child_process';

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
    projectRoot: '/Users/seunghakwoo/Documents/Cursor/Z',
    backendDir: '/Users/seunghakwoo/Documents/Cursor/Z/backend',
    prismaDir: '/Users/seunghakwoo/Documents/Cursor/Z/backend/prisma',
    dataDir: '/Users/seunghakwoo/Documents/Cursor/Z/backend/data',
    backupDir: '/Users/seunghakwoo/Documents/Cursor/Z/backend/backups',
};

// 파일 경로 설정
const paths = {
    currentSchema: path.join(config.prismaDir, 'schema.prisma'),
    unifiedSchema: path.join(config.prismaDir, 'schema-unified-sqlite.prisma'),
    originalSchema: path.join(config.prismaDir, 'schema-original.prisma'),
    currentDb: path.join(config.dataDir, 'dev.db'),
    prismaDb: path.join(config.prismaDir, 'dev.db'),
    backupDb: path.join(config.backupDir, `dev-backup-${Date.now()}.db`),
    migrationLog: path.join(config.backupDir, `migration-log-${Date.now()}.json`),
};

/**
 * 디렉토리 존재 확인 및 생성
 */
function ensureDirectories() {
    log.step('필요한 디렉토리 확인 및 생성');
    
    const directories = [config.backupDir, config.dataDir];
    
    directories.forEach(dir => {
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
            log.info(`디렉토리 생성: ${dir}`);
        }
    });
}

/**
 * 현재 데이터베이스 상태 분석
 */
async function analyzeCurrentState() {
    log.step('현재 데이터베이스 상태 분석');
    
    const analysis = {
        files: {},
        schemas: {},
        data: {},
        timestamp: new Date().toISOString(),
    };
    
    // 데이터베이스 파일 확인
    const dbFiles = [paths.currentDb, paths.prismaDb];
    for (const dbFile of dbFiles) {
        if (fs.existsSync(dbFile)) {
            const stats = fs.statSync(dbFile);
            analysis.files[dbFile] = {
                exists: true,
                size: stats.size,
                modified: stats.mtime.toISOString(),
            };
            log.info(`데이터베이스 파일 발견: ${dbFile} (${stats.size} bytes)`);
        } else {
            analysis.files[dbFile] = { exists: false };
        }
    }
    
    // 스키마 파일 확인
    const schemaFiles = [paths.currentSchema, paths.unifiedSchema, paths.originalSchema];
    for (const schemaFile of schemaFiles) {
        if (fs.existsSync(schemaFile)) {
            const content = fs.readFileSync(schemaFile, 'utf-8');
            analysis.schemas[schemaFile] = {
                exists: true,
                lines: content.split('\\n').length,
                models: (content.match(/^model \\w+/gm) || []).length,
                enums: (content.match(/^enum \\w+/gm) || []).length,
            };
            log.info(`스키마 파일: ${path.basename(schemaFile)} (${analysis.schemas[schemaFile].models} 모델)`);
        } else {
            analysis.schemas[schemaFile] = { exists: false };
        }
    }
    
    return analysis;
}

/**
 * 데이터베이스 백업 생성
 */
async function createBackup() {
    log.step('데이터베이스 백업 생성');
    
    // 메인 데이터베이스 백업
    if (fs.existsSync(paths.currentDb)) {
        fs.copyFileSync(paths.currentDb, paths.backupDb);
        log.success(`백업 생성: ${paths.backupDb}`);
    }
    
    // Prisma 데이터베이스도 백업 (존재하는 경우)
    if (fs.existsSync(paths.prismaDb)) {
        const prismaBackup = paths.backupDb.replace('.db', '-prisma.db');
        fs.copyFileSync(paths.prismaDb, prismaBackup);
        log.success(`Prisma 백업 생성: ${prismaBackup}`);
    }
    
    // 스키마 파일들도 백업
    const schemaBackupDir = path.join(config.backupDir, `schema-backup-${Date.now()}`);
    fs.mkdirSync(schemaBackupDir, { recursive: true });
    
    [paths.currentSchema, paths.originalSchema].forEach(schemaFile => {
        if (fs.existsSync(schemaFile)) {
            const backupFile = path.join(schemaBackupDir, path.basename(schemaFile));
            fs.copyFileSync(schemaFile, backupFile);
            log.info(`스키마 백업: ${backupFile}`);
        }
    });
}

/**
 * 기존 데이터 추출
 */
async function extractExistingData() {
    log.step('기존 데이터 추출');
    
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(paths.currentDb, sqlite3.OPEN_READONLY, (err) => {
            if (err) {
                log.error(`데이터베이스 열기 실패: ${err.message}`);
                reject(err);
                return;
            }
        });
        
        const extractedData = {};
        
        // 테이블 목록 조회
        db.all("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'", (err, tables) => {
            if (err) {
                reject(err);
                return;
            }
            
            log.info(`발견된 테이블: ${tables.map(t => t.name).join(', ')}`);
            
            let pendingTables = tables.length;
            if (pendingTables === 0) {
                db.close();
                resolve(extractedData);
                return;
            }
            
            // 각 테이블의 데이터 추출
            tables.forEach(table => {
                db.all(`SELECT * FROM ${table.name}`, (err, rows) => {
                    if (err) {
                        log.warning(`테이블 ${table.name} 조회 실패: ${err.message}`);
                    } else {
                        extractedData[table.name] = rows;
                        log.info(`테이블 ${table.name}: ${rows.length}개 레코드 추출`);
                    }
                    
                    pendingTables--;
                    if (pendingTables === 0) {
                        db.close();
                        resolve(extractedData);
                    }
                });
            });
        });
    });
}

/**
 * 스키마 업데이트
 */
async function updateSchema() {
    log.step('통합 스키마로 업데이트');
    
    // 현재 스키마를 백업으로 이동
    if (fs.existsSync(paths.currentSchema)) {
        const backupSchema = path.join(config.prismaDir, `schema-backup-${Date.now()}.prisma`);
        fs.copyFileSync(paths.currentSchema, backupSchema);
        log.info(`기존 스키마 백업: ${backupSchema}`);
    }
    
    // 통합 스키마를 메인 스키마로 복사
    if (fs.existsSync(paths.unifiedSchema)) {
        fs.copyFileSync(paths.unifiedSchema, paths.currentSchema);
        log.success('통합 스키마로 교체 완료');
    } else {
        throw new Error('통합 스키마 파일을 찾을 수 없습니다');
    }
}

/**
 * Prisma 마이그레이션 실행
 */
async function runPrismaMigration() {
    log.step('Prisma 마이그레이션 실행');
    
    // spawn is already imported at the top
    
    return new Promise((resolve, reject) => {
        const migration = spawn('npx', ['prisma', 'migrate', 'dev', '--name', 'unified-schema'], {
            cwd: config.backendDir,
            stdio: 'pipe'
        });
        
        let output = '';
        let errorOutput = '';
        
        migration.stdout.on('data', (data) => {
            output += data.toString();
        });
        
        migration.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });
        
        migration.on('close', (code) => {
            if (code === 0) {
                log.success('Prisma 마이그레이션 완료');
                resolve(output);
            } else {
                log.error(`마이그레이션 실패 (exit code: ${code})`);
                log.error(errorOutput);
                reject(new Error(`Migration failed: ${errorOutput}`));
            }
        });
        
        // 마이그레이션 프롬프트에 자동 응답
        migration.stdin.write('y\\n'); // "Yes, I understand" 응답
        migration.stdin.end();
    });
}

/**
 * 데이터 검증
 */
async function validateMigration() {
    log.step('마이그레이션 결과 검증');
    
    return new Promise((resolve, reject) => {
        const db = new sqlite3.Database(paths.currentDb, sqlite3.OPEN_READONLY, (err) => {
            if (err) {
                reject(err);
                return;
            }
        });
        
        // 새로운 테이블들이 생성되었는지 확인
        db.all("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'", (err, tables) => {
            if (err) {
                reject(err);
                return;
            }
            
            const tableNames = tables.map(t => t.name);
            const expectedTables = [
                'users', 'refresh_tokens', 'projects', 'bim_models', 
                'project_files', 'collaborations', 'ai_sessions',
                'activity_logs', 'error_logs', 'system_configs',
                'nlp_cache', 'usage_stats'
            ];
            
            log.info(`현재 테이블: ${tableNames.join(', ')}`);
            
            const missingTables = expectedTables.filter(table => !tableNames.includes(table));
            if (missingTables.length > 0) {
                log.warning(`누락된 테이블: ${missingTables.join(', ')}`);
            } else {
                log.success('모든 예상 테이블이 존재합니다');
            }
            
            // 기존 데이터 확인
            let pendingChecks = tableNames.length;
            const validation = { tables: {}, totalRecords: 0 };
            
            tableNames.forEach(tableName => {
                db.get(`SELECT COUNT(*) as count FROM ${tableName}`, (err, result) => {
                    if (err) {
                        log.warning(`테이블 ${tableName} 카운트 실패: ${err.message}`);
                        validation.tables[tableName] = { error: err.message };
                    } else {
                        validation.tables[tableName] = { count: result.count };
                        validation.totalRecords += result.count;
                        log.info(`테이블 ${tableName}: ${result.count}개 레코드`);
                    }
                    
                    pendingChecks--;
                    if (pendingChecks === 0) {
                        db.close();
                        resolve(validation);
                    }
                });
            });
        });
    });
}

/**
 * 마이그레이션 로그 저장
 */
async function saveMigrationLog(analysis, extractedData, validation) {
    log.step('마이그레이션 로그 저장');
    
    const migrationLog = {
        timestamp: new Date().toISOString(),
        version: '1.0',
        status: 'completed',
        analysis,
        extractedData: Object.keys(extractedData).reduce((acc, table) => {
            acc[table] = extractedData[table].length;
            return acc;
        }, {}),
        validation,
        backupFiles: {
            database: paths.backupDb,
            schema: paths.currentSchema.replace('.prisma', `-backup-${Date.now()}.prisma`)
        }
    };
    
    fs.writeFileSync(paths.migrationLog, JSON.stringify(migrationLog, null, 2));
    log.success(`마이그레이션 로그 저장: ${paths.migrationLog}`);
}

/**
 * 메인 마이그레이션 프로세스
 */
async function main() {
    console.log(`${colors.magenta}
╔══════════════════════════════════════════════════════════════╗
║                 VIBA AI 데이터베이스 통합 마이그레이션                ║
║                                                              ║
║  기존 스키마 → 통합 스키마 (AI 에이전트 + 협업 + 파일 관리)          ║
╚══════════════════════════════════════════════════════════════╝
${colors.reset}`);
    
    try {
        // 1. 준비 단계
        ensureDirectories();
        
        // 2. 현재 상태 분석
        const analysis = await analyzeCurrentState();
        
        // 3. 백업 생성
        await createBackup();
        
        // 4. 기존 데이터 추출
        const extractedData = await extractExistingData();
        
        // 5. 스키마 업데이트
        await updateSchema();
        
        // 6. Prisma 마이그레이션 실행
        await runPrismaMigration();
        
        // 7. 결과 검증
        const validation = await validateMigration();
        
        // 8. 로그 저장
        await saveMigrationLog(analysis, extractedData, validation);
        
        console.log(`\\n${colors.green}🎉 데이터베이스 통합 마이그레이션 완료!${colors.reset}`);
        console.log(`
📊 마이그레이션 요약:
   • 백업 파일: ${paths.backupDb}
   • 총 레코드: ${validation.totalRecords}개
   • 테이블 수: ${Object.keys(validation.tables).length}개
   • 로그 파일: ${paths.migrationLog}

🚀 다음 단계:
   1. 프론트엔드 API 연동 업데이트
   2. AI 에이전트 세션 관리 테스트
   3. 파일 업로드 기능 테스트
   4. 협업 기능 활성화
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

export {
    main,
    analyzeCurrentState,
    createBackup,
    extractExistingData,
    updateSchema,
    runPrismaMigration,
    validateMigration,
};