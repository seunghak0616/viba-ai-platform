"""
실제 BIM 데이터 연동 시스템
==========================

외부 BIM 소프트웨어와의 실시간 데이터 교환, 동기화, 버전 관리를 담당
Revit, ArchiCAD, Rhino, SketchUp, FreeCAD 등 주요 BIM 도구 지원

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import os
import time
import aiofiles
import aiohttp
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import zipfile
import shutil
from pathlib import Path

# BIM 데이터 처리 라이브러리
try:
    import ifcopenshell
    import ifcopenshell.api
    import ifcopenshell.util.element
    import pythonic_api as papi  # Revit 연동용
except ImportError:
    logger.warning("BIM libraries not available, using mock implementations")
    ifcopenshell = None

# 파일 형식 처리
try:
    import trimesh  # 3D 모델 처리
    import open3d as o3d  # 포인트 클라우드
    from PIL import Image  # 이미지 처리
except ImportError:
    logger.warning("3D processing libraries not available")
    trimesh = None
    open3d = None

# 프로젝트 임포트
from ..knowledge.ifc_schema import IFC43Schema
from ..utils.metrics_collector import record_ai_inference_metric

logger = logging.getLogger(__name__)


class BIMSoftware(Enum):
    """지원 BIM 소프트웨어"""
    REVIT = "revit"
    ARCHICAD = "archicad"
    RHINO = "rhino"
    SKETCHUP = "sketchup"
    FREECAD = "freecad"
    BLENDER = "blender"
    AUTOCAD = "autocad"
    BENTLEY = "bentley"
    VECTORWORKS = "vectorworks"
    UNKNOWN = "unknown"


class DataFormat(Enum):
    """지원 데이터 형식"""
    IFC = "ifc"
    DWG = "dwg"
    DXF = "dxf"
    RVT = "rvt"
    PLN = "pln"
    3DM = "3dm"
    SKP = "skp"
    FCStd = "fcstd"
    BLEND = "blend"
    OBJ = "obj"
    FBX = "fbx"
    GLB = "glb"
    GLTF = "gltf"
    PLY = "ply"
    STL = "stl"


class SyncMode(Enum):
    """동기화 모드"""
    MANUAL = "manual"           # 수동 동기화
    AUTO = "auto"              # 자동 동기화
    REAL_TIME = "real_time"    # 실시간 동기화
    SCHEDULED = "scheduled"     # 예약 동기화


class ConflictResolution(Enum):
    """충돌 해결 방식"""
    OVERWRITE = "overwrite"    # 덮어쓰기
    MERGE = "merge"           # 병합
    KEEP_BOTH = "keep_both"   # 둘 다 유지
    ASK_USER = "ask_user"     # 사용자 확인


@dataclass
class BIMFile:
    """BIM 파일 정보"""
    file_path: str
    file_name: str
    format: DataFormat
    software: BIMSoftware
    size_mb: float
    checksum: str
    created_at: datetime
    modified_at: datetime
    version: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    

@dataclass
class ProjectData:
    """프로젝트 데이터"""
    project_id: str
    project_name: str
    description: str
    files: List[BIMFile]
    sync_settings: Dict[str, Any]
    last_sync: Optional[datetime] = None
    is_active: bool = True


@dataclass
class SyncResult:
    """동기화 결과"""
    success: bool
    files_processed: int
    files_updated: int
    files_created: int
    files_deleted: int
    conflicts: List[Dict[str, Any]]
    errors: List[str]
    sync_time: float
    timestamp: datetime = field(default_factory=datetime.now)


class BIMDataManager:
    """BIM 데이터 관리자"""
    
    def __init__(self, data_directory: str = "./bim_data"):
        """BIM 데이터 매니저 초기화"""
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        # 하위 디렉토리 생성
        self.projects_dir = self.data_directory / "projects"
        self.cache_dir = self.data_directory / "cache"
        self.temp_dir = self.data_directory / "temp"
        self.exports_dir = self.data_directory / "exports"
        
        for dir_path in [self.projects_dir, self.cache_dir, self.temp_dir, self.exports_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # 프로젝트 관리
        self.projects: Dict[str, ProjectData] = {}
        self.active_connections: Dict[str, Any] = {}
        self.sync_tasks: Dict[str, asyncio.Task] = {}
        
        # IFC 스키마 엔진
        self.ifc_schema = IFC43Schema()
        
        # 지원 형식 매핑
        self.format_software_mapping = {
            DataFormat.RVT: BIMSoftware.REVIT,
            DataFormat.PLN: BIMSoftware.ARCHICAD,
            DataFormat.SKP: BIMSoftware.SKETCHUP,
            DataFormat.FCStd: BIMSoftware.FREECAD,
            DataFormat.BLEND: BIMSoftware.BLENDER,
            DataFormat.DWG: BIMSoftware.AUTOCAD,
            DataFormat.DXF: BIMSoftware.AUTOCAD,
            DataFormat.IFC: BIMSoftware.UNKNOWN
        }
        
        # 메트릭
        self.metrics = {
            "total_files_processed": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "sync_operations": 0,
            "average_processing_time": 0.0
        }
        
        logger.info(f"BIM 데이터 매니저 초기화 완료: {self.data_directory}")
    
    async def create_project(
        self, 
        project_name: str, 
        description: str = "",
        sync_settings: Optional[Dict[str, Any]] = None
    ) -> str:
        """새 프로젝트 생성"""
        
        project_id = self._generate_project_id(project_name)
        
        # 기본 동기화 설정
        if sync_settings is None:
            sync_settings = {
                "sync_mode": SyncMode.MANUAL.value,
                "conflict_resolution": ConflictResolution.ASK_USER.value,
                "auto_backup": True,
                "version_control": True,
                "watch_directories": []
            }
        
        # 프로젝트 디렉토리 생성
        project_dir = self.projects_dir / project_id
        project_dir.mkdir(exist_ok=True)
        
        # 하위 폴더 생성
        (project_dir / "models").mkdir(exist_ok=True)
        (project_dir / "exports").mkdir(exist_ok=True)
        (project_dir / "backups").mkdir(exist_ok=True)
        (project_dir / "versions").mkdir(exist_ok=True)
        
        # 프로젝트 객체 생성
        project = ProjectData(
            project_id=project_id,
            project_name=project_name,
            description=description,
            files=[],
            sync_settings=sync_settings
        )
        
        self.projects[project_id] = project
        
        # 프로젝트 메타데이터 저장
        await self._save_project_metadata(project)
        
        logger.info(f"새 프로젝트 생성: {project_name} ({project_id})")
        return project_id
    
    async def import_bim_file(
        self, 
        project_id: str, 
        file_path: str,
        software_hint: Optional[BIMSoftware] = None
    ) -> BIMFile:
        """BIM 파일 임포트"""
        
        start_time = time.time()
        
        try:
            if project_id not in self.projects:
                raise ValueError(f"프로젝트를 찾을 수 없음: {project_id}")
            
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"파일을 찾을 수 없음: {file_path}")
            
            # 파일 분석
            file_info = await self._analyze_file(file_path, software_hint)
            
            # 프로젝트 디렉토리에 복사
            target_dir = self.projects_dir / project_id / "models"
            target_path = target_dir / file_info.file_name
            
            # 파일 복사
            shutil.copy2(file_path, target_path)
            file_info.file_path = str(target_path)
            
            # 프로젝트에 파일 추가
            self.projects[project_id].files.append(file_info)
            
            # 메타데이터 업데이트
            await self._save_project_metadata(self.projects[project_id])
            
            # IFC로 변환 (필요한 경우)
            if file_info.format != DataFormat.IFC:
                await self._convert_to_ifc(file_info, project_id)
            
            # 메트릭 업데이트
            processing_time = time.time() - start_time
            self.metrics["total_files_processed"] += 1
            self.metrics["successful_imports"] += 1
            self._update_average_processing_time(processing_time)
            
            logger.info(f"파일 임포트 완료: {file_info.file_name} ({processing_time:.2f}초)")
            
            return file_info
            
        except Exception as e:
            self.metrics["failed_imports"] += 1
            logger.error(f"파일 임포트 실패: {file_path} - {e}")
            raise
    
    async def export_to_format(
        self, 
        project_id: str, 
        target_format: DataFormat,
        file_filter: Optional[str] = None
    ) -> List[str]:
        """특정 형식으로 내보내기"""
        
        if project_id not in self.projects:
            raise ValueError(f"프로젝트를 찾을 수 없음: {project_id}")
        
        project = self.projects[project_id]
        exported_files = []
        
        # 내보낼 파일 필터링
        files_to_export = project.files
        if file_filter:
            files_to_export = [f for f in project.files if file_filter in f.file_name]
        
        export_dir = self.projects_dir / project_id / "exports" / target_format.value
        export_dir.mkdir(exist_ok=True)
        
        for bim_file in files_to_export:
            try:
                exported_path = await self._export_file(bim_file, target_format, export_dir)
                exported_files.append(exported_path)
                logger.info(f"파일 내보내기 완료: {bim_file.file_name} -> {target_format.value}")
                
            except Exception as e:
                logger.error(f"파일 내보내기 실패: {bim_file.file_name} - {e}")
        
        return exported_files
    
    async def sync_with_external_source(
        self, 
        project_id: str, 
        source_path: str,
        sync_mode: SyncMode = SyncMode.MANUAL
    ) -> SyncResult:
        """외부 소스와 동기화"""
        
        start_time = time.time()
        sync_result = SyncResult(
            success=False,
            files_processed=0,
            files_updated=0,
            files_created=0,
            files_deleted=0,
            conflicts=[],
            errors=[],
            sync_time=0.0
        )
        
        try:
            if project_id not in self.projects:
                raise ValueError(f"프로젝트를 찾을 수 없음: {project_id}")
            
            project = self.projects[project_id]
            source_path = Path(source_path)
            
            if not source_path.exists():
                raise FileNotFoundError(f"소스 경로를 찾을 수 없음: {source_path}")
            
            logger.info(f"동기화 시작: {project_id} <- {source_path}")
            
            # 소스 디렉토리의 모든 BIM 파일 스캔
            source_files = await self._scan_bim_files(source_path)
            
            for source_file_path in source_files:
                try:
                    # 파일 처리
                    result = await self._process_sync_file(
                        project, 
                        source_file_path, 
                        sync_result
                    )
                    
                    if result:
                        sync_result.files_processed += 1
                        
                except Exception as e:
                    sync_result.errors.append(f"파일 처리 오류 {source_file_path}: {e}")
                    logger.error(f"동기화 파일 처리 실패: {source_file_path} - {e}")
            
            # 동기화 시간 업데이트
            sync_result.sync_time = time.time() - start_time
            sync_result.success = len(sync_result.errors) == 0
            
            # 프로젝트 마지막 동기화 시간 업데이트
            project.last_sync = datetime.now()
            await self._save_project_metadata(project)
            
            # 메트릭 업데이트
            self.metrics["sync_operations"] += 1
            
            logger.info(f"동기화 완료: {sync_result.files_processed}개 파일 처리 ({sync_result.sync_time:.2f}초)")
            
            return sync_result
            
        except Exception as e:
            sync_result.errors.append(f"동기화 오류: {e}")
            sync_result.sync_time = time.time() - start_time
            logger.error(f"동기화 실패: {project_id} - {e}")
            return sync_result
    
    async def setup_real_time_sync(
        self, 
        project_id: str, 
        watch_directories: List[str]
    ):
        """실시간 동기화 설정"""
        
        if project_id not in self.projects:
            raise ValueError(f"프로젝트를 찾을 수 없음: {project_id}")
        
        # 기존 동기화 태스크 중지
        if project_id in self.sync_tasks:
            self.sync_tasks[project_id].cancel()
        
        # 새 동기화 태스크 시작
        task = asyncio.create_task(
            self._real_time_sync_worker(project_id, watch_directories)
        )
        self.sync_tasks[project_id] = task
        
        # 프로젝트 설정 업데이트
        self.projects[project_id].sync_settings.update({
            "sync_mode": SyncMode.REAL_TIME.value,
            "watch_directories": watch_directories
        })
        
        await self._save_project_metadata(self.projects[project_id])
        
        logger.info(f"실시간 동기화 설정 완료: {project_id}")
    
    async def _real_time_sync_worker(self, project_id: str, watch_directories: List[str]):
        """실시간 동기화 워커"""
        
        # 파일 변경 감지 시스템 (watchdog 라이브러리 사용 권장)
        # 여기서는 간단한 폴링 방식으로 구현
        
        file_states = {}  # 파일별 마지막 수정 시간 저장
        
        try:
            while True:
                for watch_dir in watch_directories:
                    watch_path = Path(watch_dir)
                    if not watch_path.exists():
                        continue
                    
                    # BIM 파일 스캔
                    current_files = await self._scan_bim_files(watch_path)
                    
                    for file_path in current_files:
                        try:
                            stat = file_path.stat()
                            last_modified = stat.st_mtime
                            
                            # 새 파일이거나 수정된 파일인지 확인
                            if (str(file_path) not in file_states or 
                                file_states[str(file_path)] < last_modified):
                                
                                # 파일 동기화
                                await self._process_sync_file(
                                    self.projects[project_id], 
                                    file_path, 
                                    SyncResult(False, 0, 0, 0, 0, [], [], 0.0)
                                )
                                
                                file_states[str(file_path)] = last_modified
                                logger.info(f"실시간 동기화: {file_path.name}")
                                
                        except Exception as e:
                            logger.error(f"실시간 동기화 파일 처리 오류: {file_path} - {e}")
                
                # 10초마다 체크
                await asyncio.sleep(10)
                
        except asyncio.CancelledError:
            logger.info(f"실시간 동기화 중지: {project_id}")
        except Exception as e:
            logger.error(f"실시간 동기화 오류: {project_id} - {e}")
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """프로젝트 상태 조회"""
        
        if project_id not in self.projects:
            raise ValueError(f"프로젝트를 찾을 수 없음: {project_id}")
        
        project = self.projects[project_id]
        
        # 파일 통계
        file_stats = {
            "total_files": len(project.files),
            "formats": {},
            "software": {},
            "total_size_mb": 0.0
        }
        
        for file in project.files:
            # 형식별 카운트
            format_name = file.format.value
            if format_name not in file_stats["formats"]:
                file_stats["formats"][format_name] = 0
            file_stats["formats"][format_name] += 1
            
            # 소프트웨어별 카운트
            software_name = file.software.value
            if software_name not in file_stats["software"]:
                file_stats["software"][software_name] = 0
            file_stats["software"][software_name] += 1
            
            # 총 크기
            file_stats["total_size_mb"] += file.size_mb
        
        # 동기화 상태
        sync_status = {
            "last_sync": project.last_sync.isoformat() if project.last_sync else None,
            "sync_mode": project.sync_settings.get("sync_mode", "manual"),
            "is_real_time_active": project_id in self.sync_tasks,
            "watch_directories": project.sync_settings.get("watch_directories", [])
        }
        
        return {
            "project_info": {
                "project_id": project.project_id,
                "project_name": project.project_name,
                "description": project.description,
                "is_active": project.is_active
            },
            "file_statistics": file_stats,
            "sync_status": sync_status,
            "settings": project.sync_settings
        }
    
    async def _analyze_file(
        self, 
        file_path: Path, 
        software_hint: Optional[BIMSoftware] = None
    ) -> BIMFile:
        """파일 분석"""
        
        # 파일 기본 정보
        stat = file_path.stat()
        size_mb = stat.st_size / (1024 * 1024)
        
        # 파일 형식 감지
        file_format = self._detect_file_format(file_path)
        
        # 소프트웨어 추정
        if software_hint:
            software = software_hint
        else:
            software = self.format_software_mapping.get(file_format, BIMSoftware.UNKNOWN)
        
        # 체크섬 계산
        checksum = await self._calculate_checksum(file_path)
        
        # 메타데이터 추출
        metadata = await self._extract_metadata(file_path, file_format)
        
        return BIMFile(
            file_path=str(file_path),
            file_name=file_path.name,
            format=file_format,
            software=software,
            size_mb=size_mb,
            checksum=checksum,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            version=metadata.get("version", "1.0"),
            metadata=metadata
        )
    
    def _detect_file_format(self, file_path: Path) -> DataFormat:
        """파일 형식 감지"""
        
        extension = file_path.suffix.lower()
        
        format_mapping = {
            ".ifc": DataFormat.IFC,
            ".dwg": DataFormat.DWG,
            ".dxf": DataFormat.DXF,
            ".rvt": DataFormat.RVT,
            ".pln": DataFormat.PLN,
            ".3dm": DataFormat.3DM,
            ".skp": DataFormat.SKP,
            ".fcstd": DataFormat.FCStd,
            ".blend": DataFormat.BLEND,
            ".obj": DataFormat.OBJ,
            ".fbx": DataFormat.FBX,
            ".glb": DataFormat.GLB,
            ".gltf": DataFormat.GLTF,
            ".ply": DataFormat.PLY,
            ".stl": DataFormat.STL
        }
        
        return format_mapping.get(extension, DataFormat.IFC)
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """파일 체크섬 계산"""
        
        hash_md5 = hashlib.md5()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def _extract_metadata(self, file_path: Path, file_format: DataFormat) -> Dict[str, Any]:
        """메타데이터 추출"""
        
        metadata = {
            "version": "1.0",
            "units": "mm",
            "coordinate_system": "world",
            "elements_count": 0,
            "spaces_count": 0,
            "materials_count": 0
        }
        
        try:
            if file_format == DataFormat.IFC and ifcopenshell:
                # IFC 파일 메타데이터 추출
                ifc_file = ifcopenshell.open(str(file_path))
                
                metadata.update({
                    "ifc_version": ifc_file.schema,
                    "elements_count": len(ifc_file.by_type("IfcElement")),
                    "spaces_count": len(ifc_file.by_type("IfcSpace")),
                    "materials_count": len(ifc_file.by_type("IfcMaterial"))
                })
                
                # 프로젝트 정보
                projects = ifc_file.by_type("IfcProject")
                if projects:
                    project = projects[0]
                    metadata["project_name"] = getattr(project, "Name", "Unknown")
                    metadata["description"] = getattr(project, "Description", "")
            
            # 기타 형식에 대한 메타데이터 추출 로직 추가 가능
            
        except Exception as e:
            logger.warning(f"메타데이터 추출 실패: {file_path} - {e}")
        
        return metadata
    
    async def _convert_to_ifc(self, bim_file: BIMFile, project_id: str):
        """다른 형식을 IFC로 변환"""
        
        # 실제 변환 로직은 각 소프트웨어별 API나 변환 라이브러리 필요
        # 여기서는 구조만 제공
        
        try:
            if bim_file.format == DataFormat.IFC:
                return  # 이미 IFC
            
            logger.info(f"IFC 변환 시작: {bim_file.file_name} ({bim_file.format.value})")
            
            # 변환된 파일 경로
            ifc_path = self.projects_dir / project_id / "models" / f"{bim_file.file_name}.ifc"
            
            # 실제 변환 로직 (각 형식별로 구현 필요)
            if bim_file.format == DataFormat.DWG:
                await self._convert_dwg_to_ifc(bim_file.file_path, ifc_path)
            elif bim_file.format == DataFormat.OBJ:
                await self._convert_obj_to_ifc(bim_file.file_path, ifc_path)
            # 기타 형식들...
            
            logger.info(f"IFC 변환 완료: {ifc_path}")
            
        except Exception as e:
            logger.error(f"IFC 변환 실패: {bim_file.file_name} - {e}")
    
    async def _convert_dwg_to_ifc(self, dwg_path: str, ifc_path: Path):
        """DWG를 IFC로 변환 (예시)"""
        # 실제 구현에서는 FreeCAD, AutoCAD API, 또는 변환 라이브러리 사용
        logger.warning("DWG to IFC 변환은 추가 라이브러리가 필요합니다")
    
    async def _convert_obj_to_ifc(self, obj_path: str, ifc_path: Path):
        """OBJ를 IFC로 변환 (예시)"""
        # 간단한 기하학적 변환 예시
        if trimesh:
            try:
                # OBJ 파일 로드
                mesh = trimesh.load(obj_path)
                
                # IFC 스키마를 사용해 기본 엔티티 생성
                ifc_data = self.ifc_schema.create_spatial_structure(
                    project_name="Imported Project",
                    site_name="Default Site",
                    building_name="Default Building",
                    stories=["Ground Floor"]
                )
                
                # 메시를 IFC 엔티티로 변환 (간단화된 버전)
                # 실제로는 복잡한 변환 과정 필요
                
                # IFC 파일로 저장
                await self._save_ifc_data(ifc_data, ifc_path)
                
            except Exception as e:
                logger.error(f"OBJ to IFC 변환 오류: {e}")
    
    async def _save_ifc_data(self, ifc_data: Dict[str, Any], ifc_path: Path):
        """IFC 데이터를 파일로 저장"""
        
        # IFC 스키마의 export_to_ifc_string 메서드 사용
        ifc_content = self.ifc_schema.export_to_ifc_string(ifc_data)
        
        async with aiofiles.open(ifc_path, 'w', encoding='utf-8') as f:
            await f.write(ifc_content)
    
    async def _scan_bim_files(self, directory: Path) -> List[Path]:
        """디렉토리에서 BIM 파일 스캔"""
        
        bim_extensions = {
            ".ifc", ".dwg", ".dxf", ".rvt", ".pln", ".3dm", 
            ".skp", ".fcstd", ".blend", ".obj", ".fbx", 
            ".glb", ".gltf", ".ply", ".stl"
        }
        
        bim_files = []
        
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in bim_extensions:
                bim_files.append(file_path)
        
        return bim_files
    
    async def _process_sync_file(
        self, 
        project: ProjectData, 
        source_file_path: Path, 
        sync_result: SyncResult
    ) -> bool:
        """동기화용 파일 처리"""
        
        try:
            # 파일 분석
            file_info = await self._analyze_file(source_file_path)
            
            # 기존 파일과 비교
            existing_file = None
            for f in project.files:
                if f.file_name == file_info.file_name:
                    existing_file = f
                    break
            
            if existing_file:
                # 파일이 변경되었는지 확인
                if existing_file.checksum != file_info.checksum:
                    # 파일 업데이트
                    target_path = self.projects_dir / project.project_id / "models" / file_info.file_name
                    shutil.copy2(source_file_path, target_path)
                    
                    # 기존 파일 정보 업데이트
                    existing_file.checksum = file_info.checksum
                    existing_file.modified_at = file_info.modified_at
                    existing_file.size_mb = file_info.size_mb
                    
                    sync_result.files_updated += 1
                    
            else:
                # 새 파일 추가
                target_path = self.projects_dir / project.project_id / "models" / file_info.file_name
                shutil.copy2(source_file_path, target_path)
                file_info.file_path = str(target_path)
                
                project.files.append(file_info)
                sync_result.files_created += 1
            
            return True
            
        except Exception as e:
            sync_result.errors.append(f"파일 처리 오류 {source_file_path}: {e}")
            return False
    
    async def _export_file(
        self, 
        bim_file: BIMFile, 
        target_format: DataFormat, 
        export_dir: Path
    ) -> str:
        """파일을 특정 형식으로 내보내기"""
        
        source_path = Path(bim_file.file_path)
        target_name = f"{source_path.stem}.{target_format.value}"
        target_path = export_dir / target_name
        
        # 같은 형식이면 단순 복사
        if bim_file.format == target_format:
            shutil.copy2(source_path, target_path)
            return str(target_path)
        
        # 형식 변환 로직
        if target_format == DataFormat.IFC:
            # 다른 형식을 IFC로 변환
            await self._convert_to_ifc(bim_file, "temp")
            # 변환된 파일을 목적지로 복사
            # 실제 구현에서는 변환 결과 경로를 반환받아야 함
            
        elif target_format == DataFormat.OBJ:
            # IFC를 OBJ로 변환
            await self._convert_ifc_to_obj(source_path, target_path)
            
        # 기타 변환...
        
        return str(target_path)
    
    async def _convert_ifc_to_obj(self, ifc_path: Path, obj_path: Path):
        """IFC를 OBJ로 변환"""
        # 실제 변환 로직 구현 필요
        logger.warning("IFC to OBJ 변환은 추가 구현이 필요합니다")
    
    def _generate_project_id(self, project_name: str) -> str:
        """프로젝트 ID 생성"""
        # 프로젝트 이름 + 타임스탬프 기반 ID
        timestamp = int(time.time())
        name_hash = hashlib.md5(project_name.encode()).hexdigest()[:8]
        return f"prj_{name_hash}_{timestamp}"
    
    async def _save_project_metadata(self, project: ProjectData):
        """프로젝트 메타데이터 저장"""
        
        metadata_path = self.projects_dir / project.project_id / "project.json"
        
        # 직렬화 가능한 형태로 변환
        metadata = {
            "project_id": project.project_id,
            "project_name": project.project_name,
            "description": project.description,
            "sync_settings": project.sync_settings,
            "last_sync": project.last_sync.isoformat() if project.last_sync else None,
            "is_active": project.is_active,
            "files": [
                {
                    "file_path": f.file_path,
                    "file_name": f.file_name,
                    "format": f.format.value,
                    "software": f.software.value,
                    "size_mb": f.size_mb,
                    "checksum": f.checksum,
                    "created_at": f.created_at.isoformat(),
                    "modified_at": f.modified_at.isoformat(),
                    "version": f.version,
                    "metadata": f.metadata
                }
                for f in project.files
            ]
        }
        
        async with aiofiles.open(metadata_path, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
    
    def _update_average_processing_time(self, processing_time: float):
        """평균 처리 시간 업데이트"""
        current_avg = self.metrics["average_processing_time"]
        total_files = self.metrics["total_files_processed"]
        
        new_avg = ((current_avg * (total_files - 1)) + processing_time) / total_files
        self.metrics["average_processing_time"] = new_avg
    
    def get_metrics(self) -> Dict[str, Any]:
        """메트릭 조회"""
        return self.metrics.copy()
    
    async def cleanup_temp_files(self):
        """임시 파일 정리"""
        try:
            shutil.rmtree(self.temp_dir)
            self.temp_dir.mkdir(exist_ok=True)
            logger.info("임시 파일 정리 완료")
        except Exception as e:
            logger.error(f"임시 파일 정리 실패: {e}")
    
    async def shutdown(self):
        """데이터 매니저 종료"""
        logger.info("BIM 데이터 매니저 종료 중...")
        
        # 모든 동기화 태스크 중지
        for project_id, task in self.sync_tasks.items():
            task.cancel()
            logger.info(f"동기화 태스크 중지: {project_id}")
        
        # 임시 파일 정리
        await self.cleanup_temp_files()
        
        logger.info("BIM 데이터 매니저 종료 완료")