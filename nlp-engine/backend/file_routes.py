from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from typing import List, Optional
import os
import logging
from datetime import datetime

from file_processor import file_processor, bim_analyzer, FileType, ProcessingStatus
from auth import get_current_user

logger = logging.getLogger(__name__)

# API 라우터 생성
router = APIRouter(prefix="/api/files", tags=["Files & BIM"])

# 최대 파일 크기 설정 (100MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {
    'ifc', 'ifcxml',  # BIM
    'dwg', 'dxf',     # CAD
    'pdf',            # 문서
    'jpg', 'jpeg', 'png', 'gif', 'bmp',  # 이미지
    'xlsx', 'xls', 'csv',  # 스프레드시트
    'doc', 'docx', 'txt',  # 문서
    'zip', 'rar', '7z'     # 압축
}

def validate_file(file: UploadFile) -> None:
    """파일 유효성 검사"""
    # 파일 확장자 확인
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다. 허용된 형식: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 파일 크기 확인 (간단한 체크)
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"파일 크기가 너무 큽니다. 최대 크기: {MAX_FILE_SIZE // (1024*1024)}MB"
        )

@router.post("/upload/{project_id}")
async def upload_file(
    project_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """파일 업로드"""
    try:
        # 파일 유효성 검사
        validate_file(file)
        
        # 파일 저장
        file_metadata = await file_processor.save_uploaded_file(
            file_content=file.file,
            filename=file.filename,
            project_id=project_id,
            user_id=current_user["user_id"]
        )
        
        # 백그라운드에서 파일 처리
        background_tasks.add_task(
            file_processor.process_file,
            file_metadata["file_id"]
        )
        
        logger.info(f"파일 업로드 성공: {file.filename} (프로젝트: {project_id})")
        
        return {
            "success": True,
            "file_id": file_metadata["file_id"],
            "filename": file_metadata["original_name"],
            "file_type": file_metadata["file_type"],
            "file_size": file_metadata["file_size"],
            "status": file_metadata["status"],
            "message": "파일이 업로드되었습니다. 처리가 진행 중입니다."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 업로드 오류: {e}")
        raise HTTPException(status_code=500, detail="파일 업로드 중 오류가 발생했습니다.")

@router.post("/upload-multiple/{project_id}")
async def upload_multiple_files(
    project_id: str,
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """여러 파일 동시 업로드"""
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="한 번에 최대 10개의 파일만 업로드할 수 있습니다."
        )
    
    uploaded_files = []
    
    for file in files:
        try:
            # 파일 유효성 검사
            validate_file(file)
            
            # 파일 저장
            file_metadata = await file_processor.save_uploaded_file(
                file_content=file.file,
                filename=file.filename,
                project_id=project_id,
                user_id=current_user["user_id"]
            )
            
            # 백그라운드에서 파일 처리
            background_tasks.add_task(
                file_processor.process_file,
                file_metadata["file_id"]
            )
            
            uploaded_files.append({
                "file_id": file_metadata["file_id"],
                "filename": file_metadata["original_name"],
                "status": "uploaded"
            })
            
        except Exception as e:
            logger.error(f"파일 업로드 실패: {file.filename} - {e}")
            uploaded_files.append({
                "filename": file.filename,
                "status": "failed",
                "error": str(e)
            })
    
    return {
        "success": True,
        "total_files": len(files),
        "uploaded": len([f for f in uploaded_files if f.get("status") == "uploaded"]),
        "failed": len([f for f in uploaded_files if f.get("status") == "failed"]),
        "files": uploaded_files
    }

@router.get("/status/{file_id}")
async def get_file_status(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """파일 처리 상태 조회"""
    try:
        status = await file_processor.get_processing_status(file_id)
        
        # 권한 확인
        if status["user_id"] != current_user["user_id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="파일에 접근할 권한이 없습니다.")
        
        return {
            "success": True,
            "file_id": file_id,
            "status": status["status"],
            "progress": 100 if status["status"] == ProcessingStatus.COMPLETED else 50,
            "processing_details": status.get("processing_details"),
            "error": status.get("error")
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 상태 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="파일 상태를 조회할 수 없습니다.")

@router.get("/project/{project_id}")
async def get_project_files(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """프로젝트의 모든 파일 조회"""
    try:
        files = await file_processor.get_project_files(project_id)
        
        # 사용자별 필터링 (관리자가 아닌 경우)
        if current_user.get("role") != "admin":
            files = [f for f in files if f["user_id"] == current_user["user_id"]]
        
        return {
            "success": True,
            "project_id": project_id,
            "total_files": len(files),
            "files": files
        }
        
    except Exception as e:
        logger.error(f"프로젝트 파일 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="프로젝트 파일을 조회할 수 없습니다.")

@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """파일 삭제"""
    try:
        result = await file_processor.delete_file(file_id, current_user["user_id"])
        
        return {
            "success": True,
            "message": "파일이 삭제되었습니다.",
            "file_id": file_id
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.error(f"파일 삭제 오류: {e}")
        raise HTTPException(status_code=500, detail="파일을 삭제할 수 없습니다.")

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """파일 다운로드"""
    try:
        file_metadata = await file_processor.get_processing_status(file_id)
        
        # 권한 확인
        if file_metadata["user_id"] != current_user["user_id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="파일에 접근할 권한이 없습니다.")
        
        file_path = file_metadata["upload_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
        
        return FileResponse(
            path=file_path,
            filename=file_metadata["original_name"],
            media_type=file_metadata.get("mime_type", "application/octet-stream")
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"파일 다운로드 오류: {e}")
        raise HTTPException(status_code=500, detail="파일을 다운로드할 수 없습니다.")

# BIM 분석 엔드포인트
@router.post("/analyze/bim/{file_id}")
async def analyze_bim_file(
    file_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """BIM 파일 상세 분석"""
    try:
        # 파일 상태 확인
        file_metadata = await file_processor.get_processing_status(file_id)
        
        # 권한 확인
        if file_metadata["user_id"] != current_user["user_id"] and current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="파일에 접근할 권한이 없습니다.")
        
        # BIM 파일인지 확인
        if file_metadata["file_type"] != FileType.IFC:
            raise HTTPException(status_code=400, detail="BIM (IFC) 파일만 분석할 수 있습니다.")
        
        # 처리 완료 확인
        if file_metadata["status"] != ProcessingStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="파일 처리가 완료되지 않았습니다.")
        
        bim_data = file_metadata["processing_details"]["bim_data"]
        
        # BIM 분석 실행
        analysis_results = {
            "spatial_analysis": await bim_analyzer.analyze_spatial_relationships(bim_data),
            "sustainability_analysis": await bim_analyzer.analyze_sustainability(bim_data),
            "cost_analysis": await bim_analyzer.analyze_cost_estimation(bim_data)
        }
        
        return {
            "success": True,
            "file_id": file_id,
            "bim_data": bim_data,
            "analysis_results": analysis_results,
            "analyzed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"BIM 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="BIM 분석 중 오류가 발생했습니다.")

@router.get("/stats")
async def get_file_statistics(current_user: dict = Depends(get_current_user)):
    """파일 통계 정보"""
    try:
        stats = file_processor.get_file_stats()
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"파일 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="통계 정보를 조회할 수 없습니다.")

@router.get("/types")
async def get_supported_file_types():
    """지원되는 파일 타입 목록"""
    return {
        "success": True,
        "file_types": {
            "bim": {
                "extensions": [".ifc", ".ifcxml"],
                "description": "Building Information Modeling files",
                "max_size_mb": 100
            },
            "cad": {
                "extensions": [".dwg", ".dxf"],
                "description": "AutoCAD drawing files",
                "max_size_mb": 50
            },
            "documents": {
                "extensions": [".pdf", ".doc", ".docx", ".txt"],
                "description": "Document files",
                "max_size_mb": 20
            },
            "images": {
                "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                "description": "Image files",
                "max_size_mb": 10
            },
            "spreadsheets": {
                "extensions": [".xlsx", ".xls", ".csv"],
                "description": "Spreadsheet files",
                "max_size_mb": 20
            },
            "archives": {
                "extensions": [".zip", ".rar", ".7z"],
                "description": "Compressed archive files",
                "max_size_mb": 100
            }
        }
    }

# 헬스체크
@router.get("/health")
async def file_service_health():
    """파일 서비스 헬스체크"""
    try:
        stats = file_processor.get_file_stats()
        
        return {
            "status": "healthy",
            "total_files": stats["total_files"],
            "processing_queue": stats["processing"] + stats["pending"],
            "upload_directory": str(file_processor.upload_dir),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"파일 서비스 헬스체크 오류: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }