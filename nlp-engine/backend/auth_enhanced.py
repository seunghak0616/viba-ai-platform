#!/usr/bin/env python3
"""
강화된 사용자 인증 및 권한 관리 시스템
====================================

역할 기반 접근 제어(RBAC), 세션 관리, 보안 강화를 포함한 완전한 인증 시스템

@version 2.0
@author VIBA AI Team
@date 2025.07.07
"""

import jwt
import hashlib
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from fastapi import HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr
from enum import Enum
import os
import redis
import json
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# 보안 설정
security = HTTPBearer()
SECRET_KEY = os.getenv("VIBA_SECRET_KEY", "viba-ai-secret-key-2025")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 15

# Redis 연결 (세션 관리용)
try:
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    logger.warning("Redis 연결 실패 - 메모리 기반 세션 관리 사용")
    REDIS_AVAILABLE = False
    session_store = {}

class UserRole(str, Enum):
    """사용자 역할"""
    SUPER_ADMIN = "super_admin"      # 최고 관리자
    ADMIN = "admin"                  # 관리자
    ARCHITECT = "architect"          # 건축사
    ENGINEER = "engineer"            # 엔지니어
    DESIGNER = "designer"            # 설계자
    CLIENT = "client"                # 클라이언트
    VIEWER = "viewer"                # 뷰어 (읽기 전용)

class Permission(str, Enum):
    """권한 정의"""
    # 프로젝트 권한
    PROJECT_CREATE = "project:create"
    PROJECT_READ = "project:read"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"
    PROJECT_MANAGE = "project:manage"
    
    # 파일 권한
    FILE_UPLOAD = "file:upload"
    FILE_DOWNLOAD = "file:download"
    FILE_DELETE = "file:delete"
    FILE_ANALYZE = "file:analyze"
    
    # AI 권한
    AI_ANALYZE = "ai:analyze"
    AI_CHAT = "ai:chat"
    AI_ADVANCED = "ai:advanced"
    
    # 사용자 권한
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_MANAGE = "user:manage"
    
    # 시스템 권한
    SYSTEM_ADMIN = "system:admin"
    SYSTEM_MONITOR = "system:monitor"
    SYSTEM_CONFIG = "system:config"

# 역할별 권한 매핑
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.SUPER_ADMIN: {
        # 모든 권한
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE, 
        Permission.PROJECT_DELETE, Permission.PROJECT_MANAGE,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE, Permission.FILE_ANALYZE,
        Permission.AI_ANALYZE, Permission.AI_CHAT, Permission.AI_ADVANCED,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, 
        Permission.USER_DELETE, Permission.USER_MANAGE,
        Permission.SYSTEM_ADMIN, Permission.SYSTEM_MONITOR, Permission.SYSTEM_CONFIG
    },
    UserRole.ADMIN: {
        # 관리자 권한 (시스템 관리 제외)
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE, 
        Permission.PROJECT_DELETE, Permission.PROJECT_MANAGE,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE, Permission.FILE_ANALYZE,
        Permission.AI_ANALYZE, Permission.AI_CHAT, Permission.AI_ADVANCED,
        Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_MANAGE,
        Permission.SYSTEM_MONITOR
    },
    UserRole.ARCHITECT: {
        # 건축사 권한
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE, Permission.PROJECT_DELETE,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE, Permission.FILE_ANALYZE,
        Permission.AI_ANALYZE, Permission.AI_CHAT, Permission.AI_ADVANCED,
        Permission.USER_READ
    },
    UserRole.ENGINEER: {
        # 엔지니어 권한
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_ANALYZE,
        Permission.AI_ANALYZE, Permission.AI_CHAT, Permission.AI_ADVANCED,
        Permission.USER_READ
    },
    UserRole.DESIGNER: {
        # 설계자 권한
        Permission.PROJECT_CREATE, Permission.PROJECT_READ, Permission.PROJECT_UPDATE,
        Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_ANALYZE,
        Permission.AI_ANALYZE, Permission.AI_CHAT,
        Permission.USER_READ
    },
    UserRole.CLIENT: {
        # 클라이언트 권한
        Permission.PROJECT_READ,
        Permission.FILE_DOWNLOAD,
        Permission.AI_CHAT,
        Permission.USER_READ
    },
    UserRole.VIEWER: {
        # 뷰어 권한 (읽기 전용)
        Permission.PROJECT_READ,
        Permission.FILE_DOWNLOAD,
        Permission.USER_READ
    }
}

class UserStatus(str, Enum):
    """사용자 상태"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"

class LoginAttempt(BaseModel):
    """로그인 시도 기록"""
    ip_address: str
    user_agent: str
    success: bool
    timestamp: datetime
    failure_reason: Optional[str] = None

class UserSession(BaseModel):
    """사용자 세션"""
    session_id: str
    user_id: str
    username: str
    role: UserRole
    ip_address: str
    user_agent: str
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    is_active: bool = True

class UserProfile(BaseModel):
    """사용자 프로필"""
    user_id: str
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole
    status: UserStatus
    permissions: Set[Permission]
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    login_count: int = 0
    failed_login_attempts: int = 0
    password_changed_at: Optional[datetime] = None
    two_factor_enabled: bool = False
    profile_image: Optional[str] = None

class UserCreate(BaseModel):
    """사용자 생성 요청"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    role: UserRole = UserRole.DESIGNER

class UserUpdate(BaseModel):
    """사용자 정보 수정 요청"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

class PasswordChange(BaseModel):
    """비밀번호 변경 요청"""
    current_password: str
    new_password: str = Field(..., min_length=8)

class PasswordReset(BaseModel):
    """비밀번호 재설정 요청"""
    email: EmailStr

class AuthEnhanced:
    """강화된 인증 시스템"""
    
    def __init__(self):
        self.users_db: Dict[str, Dict] = {}
        self.sessions: Dict[str, UserSession] = {}
        self.login_attempts: Dict[str, List[LoginAttempt]] = {}
        self.blocked_ips: Set[str] = set()
        self.init_default_users()
        
    def init_default_users(self):
        """기본 사용자 생성"""
        default_users = [
            {
                "username": "superadmin",
                "email": "superadmin@viba.ai",
                "password": "SuperAdmin123!",
                "full_name": "Super Administrator",
                "company": "VIBA AI",
                "role": UserRole.SUPER_ADMIN
            },
            {
                "username": "admin",
                "email": "admin@viba.ai", 
                "password": "Admin123!",
                "full_name": "VIBA Administrator",
                "company": "VIBA AI",
                "role": UserRole.ADMIN
            },
            {
                "username": "architect",
                "email": "architect@viba.ai",
                "password": "Architect123!",
                "full_name": "김건축",
                "company": "건축사사무소",
                "role": UserRole.ARCHITECT
            },
            {
                "username": "engineer",
                "email": "engineer@viba.ai",
                "password": "Engineer123!",
                "full_name": "박구조",
                "company": "구조엔지니어링",
                "role": UserRole.ENGINEER
            }
        ]
        
        for user_data in default_users:
            self.create_user_internal(user_data)
            
    def create_user_internal(self, user_data: Dict):
        """내부 사용자 생성"""
        user_id = self.generate_user_id()
        hashed_password = self.hash_password(user_data["password"])
        
        now = datetime.now()
        permissions = ROLE_PERMISSIONS.get(user_data["role"], set())
        
        user = {
            "user_id": user_id,
            "username": user_data["username"],
            "email": user_data["email"],
            "password": hashed_password,
            "full_name": user_data.get("full_name"),
            "company": user_data.get("company"),
            "department": user_data.get("department"),
            "phone": user_data.get("phone"),
            "role": user_data["role"],
            "status": UserStatus.ACTIVE,
            "permissions": list(permissions),
            "created_at": now,
            "updated_at": now,
            "last_login": None,
            "login_count": 0,
            "failed_login_attempts": 0,
            "password_changed_at": now,
            "two_factor_enabled": False,
            "profile_image": None
        }
        
        self.users_db[user_data["username"]] = user
        logger.info(f"기본 사용자 생성: {user_data['username']} ({user_data['role']})")
        
    def generate_user_id(self) -> str:
        """고유 사용자 ID 생성"""
        return f"user_{secrets.token_hex(8)}"
        
    def generate_session_id(self) -> str:
        """고유 세션 ID 생성"""
        return f"sess_{secrets.token_hex(16)}"
        
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱 (bcrypt 사용)"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
        
    def verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    def create_refresh_token(self, data: dict) -> str:
        """리프레시 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    def verify_token(self, token: str) -> Dict[str, Any]:
        """토큰 검증"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
    def is_ip_blocked(self, ip_address: str) -> bool:
        """IP 차단 여부 확인"""
        return ip_address in self.blocked_ips
        
    def block_ip(self, ip_address: str):
        """IP 차단"""
        self.blocked_ips.add(ip_address)
        logger.warning(f"IP 차단: {ip_address}")
        
    def record_login_attempt(self, username: str, ip_address: str, user_agent: str, 
                           success: bool, failure_reason: Optional[str] = None):
        """로그인 시도 기록"""
        attempt = LoginAttempt(
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            timestamp=datetime.now(),
            failure_reason=failure_reason
        )
        
        if username not in self.login_attempts:
            self.login_attempts[username] = []
            
        self.login_attempts[username].append(attempt)
        
        # 최근 10개만 유지
        self.login_attempts[username] = self.login_attempts[username][-10:]
        
        # 실패 시도가 5회 이상이면 IP 차단
        if not success:
            recent_failures = [
                a for a in self.login_attempts[username][-5:]
                if not a.success and a.ip_address == ip_address
            ]
            if len(recent_failures) >= 5:
                self.block_ip(ip_address)
                
    def create_session(self, user: Dict, ip_address: str, user_agent: str) -> UserSession:
        """사용자 세션 생성"""
        session_id = self.generate_session_id()
        now = datetime.now()
        expires_at = now + timedelta(hours=24)
        
        session = UserSession(
            session_id=session_id,
            user_id=user["user_id"],
            username=user["username"],
            role=user["role"],
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            is_active=True
        )
        
        # 세션 저장
        if REDIS_AVAILABLE:
            redis_client.setex(
                f"session:{session_id}",
                int(timedelta(hours=24).total_seconds()),
                session.model_dump_json()
            )
        else:
            self.sessions[session_id] = session
            
        return session
        
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """세션 조회"""
        try:
            if REDIS_AVAILABLE:
                session_data = redis_client.get(f"session:{session_id}")
                if session_data:
                    return UserSession.model_validate_json(session_data)
            else:
                return self.sessions.get(session_id)
        except Exception as e:
            logger.error(f"세션 조회 오류: {e}")
            
        return None
        
    def update_session_activity(self, session_id: str):
        """세션 활동 시간 업데이트"""
        session = self.get_session(session_id)
        if session:
            session.last_activity = datetime.now()
            
            if REDIS_AVAILABLE:
                redis_client.setex(
                    f"session:{session_id}",
                    int(timedelta(hours=24).total_seconds()),
                    session.model_dump_json()
                )
            else:
                self.sessions[session_id] = session
                
    def revoke_session(self, session_id: str):
        """세션 무효화"""
        if REDIS_AVAILABLE:
            redis_client.delete(f"session:{session_id}")
        else:
            self.sessions.pop(session_id, None)
            
    def authenticate_user(self, username: str, password: str, 
                         ip_address: str, user_agent: str) -> Optional[Dict]:
        """사용자 인증"""
        # IP 차단 확인
        if self.is_ip_blocked(ip_address):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="IP address is blocked due to multiple failed attempts"
            )
            
        user = self.users_db.get(username)
        if not user:
            self.record_login_attempt(username, ip_address, user_agent, False, "User not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
            
        # 사용자 상태 확인
        if user["status"] != UserStatus.ACTIVE:
            self.record_login_attempt(username, ip_address, user_agent, False, f"User status: {user['status']}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {user['status']}"
            )
            
        # 비밀번호 검증
        if not self.verify_password(password, user["password"]):
            user["failed_login_attempts"] += 1
            self.record_login_attempt(username, ip_address, user_agent, False, "Invalid password")
            
            # 5회 실패 시 계정 일시 정지
            if user["failed_login_attempts"] >= 5:
                user["status"] = UserStatus.SUSPENDED
                logger.warning(f"계정 일시 정지: {username} (비밀번호 5회 실패)")
                
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
            
        # 로그인 성공
        user["failed_login_attempts"] = 0
        user["login_count"] += 1
        user["last_login"] = datetime.now()
        
        self.record_login_attempt(username, ip_address, user_agent, True)
        
        return user
        
    def has_permission(self, user: Dict, permission: Permission) -> bool:
        """사용자 권한 확인"""
        user_permissions = set(user.get("permissions", []))
        return permission in user_permissions
        
    def require_permission(self, permission: Permission):
        """권한 요구 데코레이터"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # current_user를 kwargs에서 찾기
                current_user = kwargs.get("current_user")
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                    
                if not self.has_permission(current_user, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission '{permission}' required"
                    )
                    
                return await func(*args, **kwargs)
            return wrapper
        return decorator

# 전역 인스턴스
auth_enhanced = AuthEnhanced()

def get_client_ip(request: Request) -> str:
    """클라이언트 IP 주소 추출"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host

def get_user_agent(request: Request) -> str:
    """User-Agent 추출"""
    return request.headers.get("User-Agent", "Unknown")

def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """액세스 토큰 검증"""
    try:
        token = credentials.credentials
        payload = auth_enhanced.verify_token(token)
        
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
            
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
            
        return username
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

def get_current_user(
    username: str = Depends(verify_access_token),
    request: Request = None
):
    """현재 사용자 정보 가져오기"""
    user = auth_enhanced.users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    # 사용자 상태 확인
    if user["status"] != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user['status']}"
        )
        
    # 세션 활동 시간 업데이트 (요청이 있을 때만)
    if request:
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            auth_enhanced.update_session_activity(session_id)
            
    return user

def require_permission(permission: Permission):
    """권한 요구 의존성"""
    def dependency(current_user: Dict = Depends(get_current_user)):
        if not auth_enhanced.has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return current_user
    return dependency

def require_role(role: UserRole):
    """역할 요구 의존성"""
    def dependency(current_user: Dict = Depends(get_current_user)):
        if current_user["role"] != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required"
            )
        return current_user
    return dependency

def require_any_role(*roles: UserRole):
    """여러 역할 중 하나 요구 의존성"""
    def dependency(current_user: Dict = Depends(get_current_user)):
        if current_user["role"] not in roles:
            role_names = [role.value for role in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of roles {role_names} required"
            )
        return current_user
    return dependency