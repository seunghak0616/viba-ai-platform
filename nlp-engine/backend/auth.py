import jwt
import hashlib
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os

# 보안 설정
security = HTTPBearer()
SECRET_KEY = os.getenv("VIBA_SECRET_KEY", "viba-ai-secret-key-2025")
ALGORITHM = "HS256"

# 임시 사용자 데이터베이스 (실제로는 PostgreSQL 사용)
users_db = {
    "admin": {
        "user_id": "admin-001",
        "username": "admin",
        "email": "admin@viba.ai",
        "password": hashlib.sha256("admin123".encode()).hexdigest(),
        "role": "admin",
        "full_name": "VIBA Admin",
        "company": "VIBA AI",
        "created_at": datetime.now(),
        "last_active": datetime.now()
    },
    "architect": {
        "user_id": "user-001", 
        "username": "architect",
        "email": "architect@viba.ai",
        "password": hashlib.sha256("password123".encode()).hexdigest(),
        "role": "architect",
        "full_name": "김건축",
        "company": "건축사사무소",
        "created_at": datetime.now(),
        "last_active": datetime.now()
    }
}

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """토큰 검증"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )

def get_current_user(username: str = Depends(verify_token)):
    """현재 사용자 정보 가져오기"""
    user = users_db.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    # 마지막 활동 시간 업데이트
    user["last_active"] = datetime.now()
    return user