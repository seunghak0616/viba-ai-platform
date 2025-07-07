#!/usr/bin/env python3
"""
강화된 인증 API 라우터
====================

사용자 관리, 권한 관리, 세션 관리를 위한 완전한 API 엔드포인트

@version 2.0
@author VIBA AI Team  
@date 2025.07.07
"""

from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from auth_enhanced import (
    auth_enhanced, UserCreate, UserUpdate, PasswordChange, PasswordReset,
    UserProfile, UserSession, UserRole, UserStatus, Permission,
    get_current_user, get_client_ip, get_user_agent,
    require_permission, require_role, require_any_role
)

logger = logging.getLogger(__name__)

# API 라우터 생성
router = APIRouter(prefix="/api/auth", tags=["Enhanced Authentication"])

# ==================== 인증 엔드포인트 ====================

@router.post("/login")
async def login(
    request: Request,
    username: str,
    password: str
):
    """강화된 로그인"""
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    try:
        # 사용자 인증
        user = auth_enhanced.authenticate_user(username, password, ip_address, user_agent)
        
        # 토큰 생성
        token_data = {"sub": user["username"], "role": user["role"]}
        access_token = auth_enhanced.create_access_token(token_data)
        refresh_token = auth_enhanced.create_refresh_token(token_data)
        
        # 세션 생성
        session = auth_enhanced.create_session(user, ip_address, user_agent)
        
        # 사용자 프로필 생성
        user_profile = UserProfile(
            user_id=user["user_id"],
            username=user["username"],
            email=user["email"],
            full_name=user.get("full_name"),
            company=user.get("company"),
            department=user.get("department"),
            phone=user.get("phone"),
            role=user["role"],
            status=user["status"],
            permissions=set(user["permissions"]),
            created_at=user["created_at"],
            updated_at=user["updated_at"],
            last_login=user.get("last_login"),
            login_count=user["login_count"],
            failed_login_attempts=user["failed_login_attempts"],
            password_changed_at=user.get("password_changed_at"),
            two_factor_enabled=user["two_factor_enabled"],
            profile_image=user.get("profile_image")
        )
        
        logger.info(f"사용자 로그인 성공: {username} from {ip_address}")
        
        return {
            "success": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 1800,  # 30분
            "session_id": session.session_id,
            "user": user_profile.model_dump(exclude={"permissions"}),
            "permissions": list(user_profile.permissions)
        }
        
    except HTTPException as e:
        logger.warning(f"로그인 실패: {username} from {ip_address} - {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """토큰 새로고침"""
    try:
        payload = auth_enhanced.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
            
        user = auth_enhanced.users_db.get(username)
        if not user or user["status"] != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
            
        # 새 액세스 토큰 생성
        token_data = {"sub": user["username"], "role": user["role"]}
        new_access_token = auth_enhanced.create_access_token(token_data)
        
        return {
            "success": True,
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": 1800
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 새로고침 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(
    request: Request,
    current_user: Dict = Depends(get_current_user)
):
    """로그아웃"""
    try:
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            auth_enhanced.revoke_session(session_id)
            
        logger.info(f"사용자 로그아웃: {current_user['username']}")
        
        return {
            "success": True,
            "message": "Successfully logged out"
        }
        
    except Exception as e:
        logger.error(f"로그아웃 오류: {e}")
        return {
            "success": True,
            "message": "Logged out (with errors)"
        }

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: Dict = Depends(get_current_user)):
    """현재 사용자 프로필 조회"""
    return UserProfile(
        user_id=current_user["user_id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user.get("full_name"),
        company=current_user.get("company"),
        department=current_user.get("department"),
        phone=current_user.get("phone"),
        role=current_user["role"],
        status=current_user["status"],
        permissions=set(current_user["permissions"]),
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"],
        last_login=current_user.get("last_login"),
        login_count=current_user["login_count"],
        failed_login_attempts=current_user["failed_login_attempts"],
        password_changed_at=current_user.get("password_changed_at"),
        two_factor_enabled=current_user["two_factor_enabled"],
        profile_image=current_user.get("profile_image")
    )

@router.put("/me")
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: Dict = Depends(get_current_user)
):
    """현재 사용자 프로필 수정"""
    try:
        # 업데이트 가능한 필드만 수정
        updateable_fields = ["email", "full_name", "company", "department", "phone"]
        
        for field in updateable_fields:
            value = getattr(user_update, field, None)
            if value is not None:
                current_user[field] = value
                
        current_user["updated_at"] = datetime.now()
        
        logger.info(f"사용자 프로필 수정: {current_user['username']}")
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "user": UserProfile(**current_user).model_dump(exclude={"permissions"})
        }
        
    except Exception as e:
        logger.error(f"프로필 수정 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    current_user: Dict = Depends(get_current_user)
):
    """비밀번호 변경"""
    try:
        # 현재 비밀번호 확인
        if not auth_enhanced.verify_password(password_change.current_password, current_user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
            
        # 새 비밀번호 해싱 및 저장
        new_hashed_password = auth_enhanced.hash_password(password_change.new_password)
        current_user["password"] = new_hashed_password
        current_user["password_changed_at"] = datetime.now()
        current_user["updated_at"] = datetime.now()
        
        logger.info(f"비밀번호 변경: {current_user['username']}")
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"비밀번호 변경 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )

# ==================== 사용자 관리 엔드포인트 ====================

@router.post("/users", response_model=UserProfile)
async def create_user(
    user_create: UserCreate,
    current_user: Dict = Depends(require_permission(Permission.USER_CREATE))
):
    """사용자 생성 (관리자 권한 필요)"""
    try:
        # 중복 확인
        if user_create.username in auth_enhanced.users_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
            
        # 이메일 중복 확인
        for user in auth_enhanced.users_db.values():
            if user["email"] == user_create.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
                
        # 사용자 생성
        user_data = {
            "username": user_create.username,
            "email": user_create.email,
            "password": user_create.password,
            "full_name": user_create.full_name,
            "company": user_create.company,
            "department": user_create.department,
            "phone": user_create.phone,
            "role": user_create.role
        }
        
        auth_enhanced.create_user_internal(user_data)
        
        # 생성된 사용자 반환
        created_user = auth_enhanced.users_db[user_create.username]
        
        logger.info(f"사용자 생성: {user_create.username} by {current_user['username']}")
        
        return UserProfile(**created_user)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 생성 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )

@router.get("/users", response_model=List[UserProfile])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    current_user: Dict = Depends(require_permission(Permission.USER_READ))
):
    """사용자 목록 조회"""
    try:
        users = list(auth_enhanced.users_db.values())
        
        # 필터링
        if role:
            users = [u for u in users if u["role"] == role]
        if status:
            users = [u for u in users if u["status"] == status]
            
        # 페이징
        users = users[skip:skip + limit]
        
        # UserProfile로 변환
        user_profiles = []
        for user in users:
            user_profiles.append(UserProfile(**user))
            
        return user_profiles
        
    except Exception as e:
        logger.error(f"사용자 목록 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/users/{username}", response_model=UserProfile)
async def get_user(
    username: str,
    current_user: Dict = Depends(require_permission(Permission.USER_READ))
):
    """특정 사용자 조회"""
    user = auth_enhanced.users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        
    return UserProfile(**user)

@router.put("/users/{username}")
async def update_user(
    username: str,
    user_update: UserUpdate,
    current_user: Dict = Depends(require_permission(Permission.USER_UPDATE))
):
    """사용자 정보 수정 (관리자 권한 필요)"""
    try:
        user = auth_enhanced.users_db.get(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # 수정 가능한 필드 업데이트
        update_fields = ["email", "full_name", "company", "department", "phone", "role", "status"]
        
        for field in update_fields:
            value = getattr(user_update, field, None)
            if value is not None:
                user[field] = value
                
                # 역할 변경 시 권한 업데이트
                if field == "role":
                    from auth_enhanced import ROLE_PERMISSIONS
                    user["permissions"] = list(ROLE_PERMISSIONS.get(value, set()))
                    
        user["updated_at"] = datetime.now()
        
        logger.info(f"사용자 정보 수정: {username} by {current_user['username']}")
        
        return {
            "success": True,
            "message": "User updated successfully",
            "user": UserProfile(**user).model_dump(exclude={"permissions"})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 수정 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User update failed"
        )

@router.delete("/users/{username}")
async def delete_user(
    username: str,
    current_user: Dict = Depends(require_permission(Permission.USER_DELETE))
):
    """사용자 삭제 (관리자 권한 필요)"""
    try:
        if username not in auth_enhanced.users_db:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
            
        # 자기 자신은 삭제할 수 없음
        if username == current_user["username"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
            )
            
        # 사용자 삭제 (실제로는 상태를 DELETED로 변경)
        auth_enhanced.users_db[username]["status"] = UserStatus.DELETED
        auth_enhanced.users_db[username]["updated_at"] = datetime.now()
        
        logger.info(f"사용자 삭제: {username} by {current_user['username']}")
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"사용자 삭제 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User deletion failed"
        )

# ==================== 세션 관리 엔드포인트 ====================

@router.get("/sessions")
async def get_user_sessions(
    current_user: Dict = Depends(get_current_user)
):
    """현재 사용자의 세션 목록"""
    try:
        user_sessions = []
        
        # Redis 또는 메모리에서 세션 조회
        if hasattr(auth_enhanced, 'sessions'):
            for session in auth_enhanced.sessions.values():
                if session.user_id == current_user["user_id"]:
                    user_sessions.append(session.model_dump())
                    
        return {
            "success": True,
            "sessions": user_sessions
        }
        
    except Exception as e:
        logger.error(f"세션 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """특정 세션 무효화"""
    try:
        session = auth_enhanced.get_session(session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
            
        # 본인의 세션만 무효화 가능 (관리자는 모든 세션 가능)
        if session.user_id != current_user["user_id"] and current_user["role"] not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot revoke other user's session"
            )
            
        auth_enhanced.revoke_session(session_id)
        
        return {
            "success": True,
            "message": "Session revoked successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 무효화 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session revocation failed"
        )

# ==================== 권한 관리 엔드포인트 ====================

@router.get("/permissions")
async def get_permissions(current_user: Dict = Depends(get_current_user)):
    """현재 사용자 권한 조회"""
    return {
        "success": True,
        "user_id": current_user["user_id"],
        "username": current_user["username"],
        "role": current_user["role"],
        "permissions": current_user["permissions"]
    }

@router.get("/roles")
async def get_roles(current_user: Dict = Depends(require_permission(Permission.USER_READ))):
    """역할 목록 조회"""
    from auth_enhanced import ROLE_PERMISSIONS
    
    roles_info = []
    for role, permissions in ROLE_PERMISSIONS.items():
        roles_info.append({
            "role": role.value,
            "name": role.value.replace("_", " ").title(),
            "permissions": list(permissions),
            "permission_count": len(permissions)
        })
        
    return {
        "success": True,
        "roles": roles_info
    }

# ==================== 보안 모니터링 엔드포인트 ====================

@router.get("/security/stats")
async def get_security_stats(
    current_user: Dict = Depends(require_permission(Permission.SYSTEM_MONITOR))
):
    """보안 통계 조회"""
    try:
        total_users = len(auth_enhanced.users_db)
        active_users = len([u for u in auth_enhanced.users_db.values() if u["status"] == UserStatus.ACTIVE])
        blocked_ips = len(auth_enhanced.blocked_ips)
        
        # 최근 로그인 시도 통계
        recent_attempts = 0
        failed_attempts = 0
        
        for attempts in auth_enhanced.login_attempts.values():
            for attempt in attempts[-10:]:  # 최근 10개
                if attempt.timestamp > datetime.now() - timedelta(hours=24):
                    recent_attempts += 1
                    if not attempt.success:
                        failed_attempts += 1
                        
        return {
            "success": True,
            "statistics": {
                "total_users": total_users,
                "active_users": active_users,
                "suspended_users": len([u for u in auth_enhanced.users_db.values() if u["status"] == UserStatus.SUSPENDED]),
                "blocked_ips": blocked_ips,
                "recent_login_attempts_24h": recent_attempts,
                "failed_attempts_24h": failed_attempts,
                "active_sessions": len(getattr(auth_enhanced, 'sessions', {}))
            }
        }
        
    except Exception as e:
        logger.error(f"보안 통계 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security statistics"
        )

@router.get("/security/login-history/{username}")
async def get_login_history(
    username: str,
    current_user: Dict = Depends(require_permission(Permission.USER_READ))
):
    """사용자 로그인 기록 조회"""
    try:
        # 본인이거나 관리자만 조회 가능
        if username != current_user["username"] and current_user["role"] not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot view other user's login history"
            )
            
        attempts = auth_enhanced.login_attempts.get(username, [])
        
        return {
            "success": True,
            "username": username,
            "login_history": [attempt.model_dump() for attempt in attempts]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 기록 조회 오류: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve login history"
        )