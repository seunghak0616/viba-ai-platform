#!/usr/bin/env python3
"""
VIBA AI FastAPI 백엔드 서버
=========================

고성능 비동기 API 서버 - 건축 설계 플랫폼의 핵심 백엔드

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn
import asyncio
import time
import logging
from datetime import datetime, timedelta
import jwt
import hashlib
import os
import json

# AI 에이전트 관련 임포트
from ai_routes import router as ai_router
from file_routes import router as file_router
from auth_routes import router as auth_router
from websocket_manager import manager
from file_processor import file_processor

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="VIBA AI API",
    description="차세대 AI 건축 설계 플랫폼 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 구체적인 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router)  # 강화된 인증 라우터
app.include_router(ai_router)
app.include_router(file_router)

# 보안 설정
security = HTTPBearer()
SECRET_KEY = os.getenv("VIBA_SECRET_KEY", "viba-ai-secret-key-2025")
ALGORITHM = "HS256"

# 메모리 기반 데이터 저장 (나중에 PostgreSQL로 교체)
users_db = {}
projects_db = {}
sessions_db = {}
system_stats = {
    "total_requests": 0,
    "total_users": 0,
    "total_projects": 0,
    "uptime_start": datetime.now()
}

# ==================== 데이터 모델 ====================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    company: Optional[str] = None
    role: str = Field(default="architect")

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    company: Optional[str]
    role: str
    created_at: datetime
    last_active: datetime

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    building_type: str = Field(..., description="주거용, 상업용, 공업용 등")
    location: Optional[str] = None
    area: Optional[float] = Field(None, gt=0, description="면적 (평방미터)")
    floors: Optional[int] = Field(None, gt=0, description="층수")
    budget: Optional[float] = Field(None, gt=0, description="예산")

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    building_type: str
    location: Optional[str]
    area: Optional[float]
    floors: Optional[int]
    budget: Optional[float]
    owner_id: str
    created_at: datetime
    updated_at: datetime
    status: str

class DesignRequest(BaseModel):
    project_id: str
    request_type: str = Field(..., description="설계 요청 유형")
    content: str = Field(..., min_length=1)
    context: Optional[Dict[str, Any]] = None
    priority: str = Field(default="normal", description="요청 우선순위")

class DesignResponse(BaseModel):
    id: str
    request_id: str
    content: str
    recommendations: List[Dict[str, Any]]
    execution_time: float
    quality_score: float
    created_at: datetime

# ==================== 유틸리티 함수 ====================

def hash_password(password: str) -> str:
    """비밀번호 해싱"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """비밀번호 검증"""
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
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

def generate_id() -> str:
    """고유 ID 생성"""
    return hashlib.md5(f"{datetime.now()}{os.urandom(16)}".encode()).hexdigest()

# ==================== API 엔드포인트 ====================

@app.get("/")
async def root():
    """API 루트"""
    return {
        "message": "VIBA AI API Server",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    uptime = datetime.now() - system_stats["uptime_start"]
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "uptime_seconds": uptime.total_seconds(),
        "system_stats": system_stats
    }

# ==================== 인증 API ====================

@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """사용자 등록"""
    system_stats["total_requests"] += 1
    
    # 중복 확인
    if user_data.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # 이메일 중복 확인
    for user in users_db.values():
        if user["email"] == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    # 사용자 생성
    user_id = generate_id()
    user = {
        "id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "company": user_data.company,
        "role": user_data.role,
        "created_at": datetime.now(),
        "last_active": datetime.now()
    }
    
    users_db[user_data.username] = user
    system_stats["total_users"] += 1
    
    logger.info(f"New user registered: {user_data.username}")
    
    return UserResponse(**user)

@app.post("/auth/login")
async def login(login_data: UserLogin):
    """사용자 로그인"""
    system_stats["total_requests"] += 1
    
    user = users_db.get(login_data.username)
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # 토큰 생성
    access_token = create_access_token(data={"sub": user["username"]})
    
    # 세션 저장
    session_id = generate_id()
    sessions_db[session_id] = {
        "user_id": user["id"],
        "username": user["username"],
        "created_at": datetime.now(),
        "last_active": datetime.now()
    }
    
    user["last_active"] = datetime.now()
    
    logger.info(f"User logged in: {login_data.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """현재 사용자 정보"""
    return UserResponse(**current_user)

# ==================== 프로젝트 관리 API ====================

@app.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate, 
    current_user: dict = Depends(get_current_user)
):
    """프로젝트 생성"""
    system_stats["total_requests"] += 1
    
    project_id = generate_id()
    project = {
        "id": project_id,
        "name": project_data.name,
        "description": project_data.description,
        "building_type": project_data.building_type,
        "location": project_data.location,
        "area": project_data.area,
        "floors": project_data.floors,
        "budget": project_data.budget,
        "owner_id": current_user["id"],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "status": "active"
    }
    
    projects_db[project_id] = project
    system_stats["total_projects"] += 1
    
    logger.info(f"New project created: {project_data.name} by {current_user['username']}")
    
    return ProjectResponse(**project)

@app.get("/projects", response_model=List[ProjectResponse])
async def get_user_projects(current_user: dict = Depends(get_current_user)):
    """사용자 프로젝트 목록"""
    system_stats["total_requests"] += 1
    
    user_projects = [
        ProjectResponse(**project) 
        for project in projects_db.values() 
        if project["owner_id"] == current_user["id"]
    ]
    
    return user_projects

@app.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """프로젝트 상세 정보"""
    system_stats["total_requests"] += 1
    
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 소유자 확인
    if project["owner_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ProjectResponse(**project)

# ==================== 설계 요청 API ====================

@app.post("/design/request")
async def process_design_request(
    request_data: DesignRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """설계 요청 처리"""
    system_stats["total_requests"] += 1
    
    # 프로젝트 확인
    project = projects_db.get(request_data.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if project["owner_id"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # 설계 요청 처리 (Mock)
    start_time = time.time()
    
    # 백그라운드 작업으로 처리
    request_id = generate_id()
    
    async def process_request():
        """비동기 설계 요청 처리"""
        await asyncio.sleep(0.5)  # 처리 시뮬레이션
        
        # Mock 응답 생성
        recommendations = [
            {
                "type": "material",
                "category": "구조재",
                "name": "친환경 콘크리트",
                "description": "탄소 발자국을 줄인 고강도 콘크리트",
                "specifications": {
                    "strength": "40MPa",
                    "sustainability_rating": "A+",
                    "cost_per_m3": 120000
                }
            },
            {
                "type": "design",
                "category": "공간배치", 
                "name": "자연 채광 최적화",
                "description": "남향 배치를 통한 자연 채광 극대화",
                "benefits": ["에너지 절약", "쾌적성 향상", "비타민 D 합성"]
            }
        ]
        
        execution_time = time.time() - start_time
        
        # 응답 저장 (실제로는 데이터베이스에 저장)
        response = {
            "id": generate_id(),
            "request_id": request_id,
            "content": f"'{request_data.content}' 요청에 대한 AI 분석이 완료되었습니다.",
            "recommendations": recommendations,
            "execution_time": execution_time,
            "quality_score": 0.85,
            "created_at": datetime.now()
        }
        
        logger.info(f"Design request processed: {request_id}")
        return response
    
    # 백그라운드 작업 추가
    background_tasks.add_task(process_request)
    
    return {
        "request_id": request_id,
        "status": "processing",
        "message": "설계 요청이 접수되었습니다. 처리 중...",
        "estimated_time": "30-60초"
    }

@app.get("/design/status/{request_id}")
async def get_design_status(
    request_id: str,
    current_user: dict = Depends(get_current_user)
):
    """설계 요청 상태 확인"""
    system_stats["total_requests"] += 1
    
    # Mock 응답 (실제로는 데이터베이스에서 조회)
    return {
        "request_id": request_id,
        "status": "completed",
        "progress": 100,
        "result": {
            "recommendations": 5,
            "quality_score": 0.87,
            "processing_time": 0.8
        }
    }

# ==================== 관리자 API ====================

@app.get("/admin/stats")
async def get_admin_stats(current_user: dict = Depends(get_current_user)):
    """관리자 통계 (권한 확인 필요)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    uptime = datetime.now() - system_stats["uptime_start"]
    
    return {
        "system_stats": system_stats,
        "uptime_hours": uptime.total_seconds() / 3600,
        "active_users": len([u for u in users_db.values() 
                           if (datetime.now() - u["last_active"]).seconds < 3600]),
        "active_sessions": len(sessions_db),
        "database_stats": {
            "users": len(users_db),
            "projects": len(projects_db),
            "sessions": len(sessions_db)
        }
    }

# ==================== 서버 실행 ====================

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 실행"""
    logger.info("VIBA AI 서버 시작...")
    
    # 파일 처리 워커 시작
    asyncio.create_task(file_processor.start_processing_worker())
    logger.info("파일 처리 워커 시작됨")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 실행"""
    logger.info("VIBA AI 서버 종료...")

if __name__ == "__main__":
    print("🚀 VIBA AI FastAPI 서버 시작")
    print("📍 API 문서: http://localhost:8000/docs")
    print("🔧 관리자 문서: http://localhost:8000/redoc")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )