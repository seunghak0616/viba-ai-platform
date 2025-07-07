-- VIBA AI 통합 데이터베이스 마이그레이션 SQL
-- SQLite용 테이블 생성 스크립트

PRAGMA foreign_keys = ON;

-- ============================================================================
-- 기존 테이블 제거 (필요시)
-- ============================================================================

-- DROP TABLE IF EXISTS usage_stats;
-- DROP TABLE IF EXISTS nlp_cache;
-- DROP TABLE IF EXISTS system_configs;
-- DROP TABLE IF EXISTS error_logs;
-- DROP TABLE IF EXISTS activity_logs;
-- DROP TABLE IF EXISTS ai_sessions;
-- DROP TABLE IF EXISTS collaborations;
-- DROP TABLE IF EXISTS project_files;
-- DROP TABLE IF EXISTS bim_models;
-- DROP TABLE IF EXISTS projects;
-- DROP TABLE IF EXISTS refresh_tokens;
-- DROP TABLE IF EXISTS users;

-- ============================================================================
-- 사용자 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS "users" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "email" TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "company" TEXT,
    "department" TEXT,
    "position" TEXT,
    "phone" TEXT,
    "role" TEXT NOT NULL DEFAULT 'VIEWER',
    "isActive" BOOLEAN NOT NULL DEFAULT 1,
    "emailVerified" BOOLEAN NOT NULL DEFAULT 0,
    "emailVerifiedAt" DATETIME,
    "loginAttempts" INTEGER NOT NULL DEFAULT 0,
    "lockUntil" DATETIME,
    "passwordChangedAt" DATETIME,
    "lastLoginAt" DATETIME,
    "lastLoginIp" TEXT,
    "preferences" TEXT,
    "subscription" TEXT,
    "profile" TEXT,
    "notificationSettings" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" DATETIME
);

CREATE TABLE IF NOT EXISTS "refresh_tokens" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "token" TEXT NOT NULL UNIQUE,
    "userId" TEXT NOT NULL,
    "expiresAt" DATETIME NOT NULL,
    "isRevoked" BOOLEAN NOT NULL DEFAULT 0,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================================
-- 프로젝트 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS "projects" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "status" TEXT NOT NULL DEFAULT 'DRAFT',
    "metadata" TEXT,
    "settings" TEXT,
    "tags" TEXT,
    "buildingInfo" TEXT,
    "location" TEXT,
    "regulations" TEXT,
    "userId" TEXT NOT NULL,
    "isPublic" BOOLEAN NOT NULL DEFAULT 0,
    "isTemplate" BOOLEAN NOT NULL DEFAULT 0,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" DATETIME,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================================
-- BIM 모델 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS "bim_models" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "description" TEXT,
    "type" TEXT NOT NULL,
    "naturalLanguageInput" TEXT,
    "processedParams" TEXT,
    "geometryData" TEXT,
    "materials" TEXT,
    "dimensions" TEXT,
    "spatial" TEXT,
    "metadata" TEXT,
    "properties" TEXT,
    "constraints" TEXT,
    "performanceData" TEXT,
    "ifcFileUrl" TEXT,
    "thumbnailUrl" TEXT,
    "previewUrl" TEXT,
    "version" INTEGER NOT NULL DEFAULT 1,
    "parentId" TEXT,
    "changeLog" TEXT,
    "isPublic" BOOLEAN NOT NULL DEFAULT 0,
    "isTemplate" BOOLEAN NOT NULL DEFAULT 0,
    "isValidated" BOOLEAN NOT NULL DEFAULT 0,
    "userId" TEXT NOT NULL,
    "projectId" TEXT NOT NULL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" DATETIME,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("projectId") REFERENCES "projects" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("parentId") REFERENCES "bim_models" ("id") ON DELETE SET NULL ON UPDATE CASCADE
);

-- ============================================================================
-- 파일 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS "project_files" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "filename" TEXT NOT NULL,
    "originalName" TEXT NOT NULL,
    "mimeType" TEXT NOT NULL,
    "size" INTEGER NOT NULL,
    "fileType" TEXT NOT NULL,
    "url" TEXT NOT NULL,
    "metadata" TEXT,
    "isProcessed" BOOLEAN NOT NULL DEFAULT 0,
    "processedAt" DATETIME,
    "processingLog" TEXT,
    "userId" TEXT NOT NULL,
    "projectId" TEXT NOT NULL,
    "bimModelId" TEXT,
    "category" TEXT,
    "tags" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "deletedAt" DATETIME,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("projectId") REFERENCES "projects" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("bimModelId") REFERENCES "bim_models" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================================
-- 협업 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS "collaborations" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "userId" TEXT NOT NULL,
    "projectId" TEXT NOT NULL,
    "role" TEXT NOT NULL DEFAULT 'VIEWER',
    "permissions" TEXT,
    "invitedBy" TEXT,
    "invitedAt" DATETIME,
    "acceptedAt" DATETIME,
    "revokedAt" DATETIME,
    "isActive" BOOLEAN NOT NULL DEFAULT 1,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("projectId") REFERENCES "projects" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    UNIQUE("userId", "projectId")
);

-- ============================================================================
-- AI 에이전트 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS "ai_sessions" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "sessionId" TEXT NOT NULL UNIQUE,
    "agentId" TEXT NOT NULL,
    "agentName" TEXT NOT NULL,
    "status" TEXT NOT NULL DEFAULT 'ACTIVE',
    "userId" TEXT,
    "projectId" TEXT,
    "context" TEXT,
    "messages" TEXT,
    "messageCount" INTEGER NOT NULL DEFAULT 0,
    "responseTime" REAL,
    "tokenUsage" TEXT,
    "expiresAt" DATETIME NOT NULL,
    "lastActiveAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("projectId") REFERENCES "projects" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================================
-- 로깅 및 모니터링
-- ============================================================================

CREATE TABLE IF NOT EXISTS "activity_logs" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "action" TEXT NOT NULL,
    "details" TEXT,
    "result" TEXT,
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "sessionId" TEXT,
    "userId" TEXT NOT NULL,
    "projectId" TEXT,
    "bimModelId" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY ("userId") REFERENCES "users" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("projectId") REFERENCES "projects" ("id") ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY ("bimModelId") REFERENCES "bim_models" ("id") ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "error_logs" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "level" TEXT NOT NULL,
    "message" TEXT NOT NULL,
    "stack" TEXT,
    "context" TEXT,
    "method" TEXT,
    "url" TEXT,
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "userId" TEXT,
    "category" TEXT,
    "tags" TEXT,
    "isResolved" BOOLEAN NOT NULL DEFAULT 0,
    "resolvedAt" DATETIME,
    "resolvedBy" TEXT,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 시스템 관리
-- ============================================================================

CREATE TABLE IF NOT EXISTS "system_configs" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "key" TEXT NOT NULL UNIQUE,
    "value" TEXT NOT NULL,
    "category" TEXT NOT NULL,
    "description" TEXT,
    "isActive" BOOLEAN NOT NULL DEFAULT 1,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 캐싱 및 최적화
-- ============================================================================

CREATE TABLE IF NOT EXISTS "nlp_cache" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "inputText" TEXT NOT NULL,
    "inputHash" TEXT NOT NULL UNIQUE,
    "processedResult" TEXT NOT NULL,
    "language" TEXT NOT NULL DEFAULT 'ko',
    "confidence" REAL,
    "hitCount" INTEGER NOT NULL DEFAULT 1,
    "lastUsedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "expiresAt" DATETIME,
    "isValid" BOOLEAN NOT NULL DEFAULT 1,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 통계 및 분석
-- ============================================================================

CREATE TABLE IF NOT EXISTS "usage_stats" (
    "id" TEXT NOT NULL PRIMARY KEY,
    "date" DATETIME NOT NULL,
    "userId" TEXT,
    "apiCalls" INTEGER NOT NULL DEFAULT 0,
    "modelsGenerated" INTEGER NOT NULL DEFAULT 0,
    "filesUploaded" INTEGER NOT NULL DEFAULT 0,
    "aiMessages" INTEGER NOT NULL DEFAULT 0,
    "storageUsed" INTEGER NOT NULL DEFAULT 0,
    "avgResponseTime" REAL,
    "errorRate" REAL,
    "createdAt" DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE("date", "userId")
);

-- ============================================================================
-- 인덱스 생성
-- ============================================================================

-- 사용자 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_users_email" ON "users"("email");
CREATE INDEX IF NOT EXISTS "idx_users_role" ON "users"("role");
CREATE INDEX IF NOT EXISTS "idx_users_active" ON "users"("isActive");

-- 프로젝트 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_projects_user" ON "projects"("userId");
CREATE INDEX IF NOT EXISTS "idx_projects_status" ON "projects"("status");
CREATE INDEX IF NOT EXISTS "idx_projects_public" ON "projects"("isPublic");

-- BIM 모델 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_bim_models_user" ON "bim_models"("userId");
CREATE INDEX IF NOT EXISTS "idx_bim_models_project" ON "bim_models"("projectId");
CREATE INDEX IF NOT EXISTS "idx_bim_models_type" ON "bim_models"("type");

-- 파일 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_project_files_user" ON "project_files"("userId");
CREATE INDEX IF NOT EXISTS "idx_project_files_project" ON "project_files"("projectId");
CREATE INDEX IF NOT EXISTS "idx_project_files_type" ON "project_files"("fileType");

-- AI 세션 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_ai_sessions_user" ON "ai_sessions"("userId");
CREATE INDEX IF NOT EXISTS "idx_ai_sessions_agent" ON "ai_sessions"("agentId");
CREATE INDEX IF NOT EXISTS "idx_ai_sessions_status" ON "ai_sessions"("status");
CREATE INDEX IF NOT EXISTS "idx_ai_sessions_expires" ON "ai_sessions"("expiresAt");

-- 로그 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_activity_logs_user" ON "activity_logs"("userId");
CREATE INDEX IF NOT EXISTS "idx_activity_logs_action" ON "activity_logs"("action");
CREATE INDEX IF NOT EXISTS "idx_activity_logs_created" ON "activity_logs"("createdAt");

-- 캐시 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_nlp_cache_hash" ON "nlp_cache"("inputHash");
CREATE INDEX IF NOT EXISTS "idx_nlp_cache_valid" ON "nlp_cache"("isValid");

-- 통계 관련 인덱스
CREATE INDEX IF NOT EXISTS "idx_usage_stats_date" ON "usage_stats"("date");
CREATE INDEX IF NOT EXISTS "idx_usage_stats_user" ON "usage_stats"("userId");