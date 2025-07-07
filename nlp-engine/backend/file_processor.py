import os
import uuid
import asyncio
import logging
import json
import shutil
from typing import Dict, List, Optional, Any, BinaryIO
from datetime import datetime
from pathlib import Path
import hashlib
import mimetypes
from enum import Enum

logger = logging.getLogger(__name__)

class FileType(str, Enum):
    """지원되는 파일 타입"""
    IFC = "ifc"                 # IFC 파일 (BIM)
    DWG = "dwg"                 # AutoCAD 도면
    PDF = "pdf"                 # PDF 문서
    IMAGE = "image"             # 이미지 파일
    EXCEL = "excel"             # 엑셀 파일
    DOCUMENT = "document"       # 문서 파일
    ARCHIVE = "archive"         # 압축 파일
    OTHER = "other"             # 기타

class ProcessingStatus(str, Enum):
    """처리 상태"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class FileProcessor:
    """파일 처리 및 BIM 데이터 관리 클래스"""
    
    def __init__(self, upload_dir: str = "./uploads", processed_dir: str = "./processed"):
        self.upload_dir = Path(upload_dir)
        self.processed_dir = Path(processed_dir)
        self.temp_dir = Path("./temp")
        
        # 디렉토리 생성
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        # 파일 타입 매핑
        self.file_type_mapping = {
            '.ifc': FileType.IFC,
            '.ifcxml': FileType.IFC,
            '.dwg': FileType.DWG,
            '.dxf': FileType.DWG,
            '.pdf': FileType.PDF,
            '.jpg': FileType.IMAGE,
            '.jpeg': FileType.IMAGE,
            '.png': FileType.IMAGE,
            '.gif': FileType.IMAGE,
            '.bmp': FileType.IMAGE,
            '.xlsx': FileType.EXCEL,
            '.xls': FileType.EXCEL,
            '.csv': FileType.EXCEL,
            '.doc': FileType.DOCUMENT,
            '.docx': FileType.DOCUMENT,
            '.txt': FileType.DOCUMENT,
            '.zip': FileType.ARCHIVE,
            '.rar': FileType.ARCHIVE,
            '.7z': FileType.ARCHIVE,
        }
        
        # 처리 대기열
        self.processing_queue = asyncio.Queue()
        self.processing_status = {}
        
    def get_file_type(self, filename: str) -> FileType:
        """파일 타입 확인"""
        ext = Path(filename).suffix.lower()
        return self.file_type_mapping.get(ext, FileType.OTHER)
        
    def generate_file_id(self) -> str:
        """고유 파일 ID 생성"""
        return str(uuid.uuid4())
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """파일 해시 계산"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
        
    async def save_uploaded_file(
        self, 
        file_content: BinaryIO, 
        filename: str,
        project_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """업로드된 파일 저장"""
        try:
            file_id = self.generate_file_id()
            file_type = self.get_file_type(filename)
            
            # 프로젝트별 디렉토리 생성
            project_dir = self.upload_dir / project_id
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # 파일 저장
            safe_filename = f"{file_id}_{filename}"
            file_path = project_dir / safe_filename
            
            # 파일 쓰기
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file_content, f)
                
            # 파일 정보 수집
            file_size = file_path.stat().st_size
            file_hash = self.calculate_file_hash(file_path)
            
            # 파일 메타데이터
            file_metadata = {
                "file_id": file_id,
                "original_name": filename,
                "safe_name": safe_filename,
                "file_type": file_type,
                "file_size": file_size,
                "file_hash": file_hash,
                "mime_type": mimetypes.guess_type(filename)[0],
                "project_id": project_id,
                "user_id": user_id,
                "upload_path": str(file_path),
                "uploaded_at": datetime.now().isoformat(),
                "status": ProcessingStatus.PENDING,
                "processing_details": None
            }
            
            # 처리 대기열에 추가
            await self.processing_queue.put(file_metadata)
            self.processing_status[file_id] = file_metadata
            
            logger.info(f"파일 업로드 완료: {filename} (ID: {file_id}, Type: {file_type})")
            
            return file_metadata
            
        except Exception as e:
            logger.error(f"파일 업로드 실패: {e}")
            raise
            
    async def process_file(self, file_id: str) -> Dict[str, Any]:
        """파일 처리 실행"""
        if file_id not in self.processing_status:
            raise ValueError(f"파일을 찾을 수 없습니다: {file_id}")
            
        file_metadata = self.processing_status[file_id]
        file_type = file_metadata["file_type"]
        
        try:
            # 처리 시작
            file_metadata["status"] = ProcessingStatus.PROCESSING
            file_metadata["processing_started_at"] = datetime.now().isoformat()
            
            # 파일 타입별 처리
            if file_type == FileType.IFC:
                result = await self.process_ifc_file(file_metadata)
            elif file_type == FileType.DWG:
                result = await self.process_dwg_file(file_metadata)
            elif file_type == FileType.PDF:
                result = await self.process_pdf_file(file_metadata)
            elif file_type == FileType.IMAGE:
                result = await self.process_image_file(file_metadata)
            else:
                result = await self.process_generic_file(file_metadata)
                
            # 처리 완료
            file_metadata["status"] = ProcessingStatus.COMPLETED
            file_metadata["processing_completed_at"] = datetime.now().isoformat()
            file_metadata["processing_details"] = result
            
            logger.info(f"파일 처리 완료: {file_id}")
            return file_metadata
            
        except Exception as e:
            logger.error(f"파일 처리 실패: {file_id} - {e}")
            file_metadata["status"] = ProcessingStatus.FAILED
            file_metadata["error"] = str(e)
            raise
            
    async def process_ifc_file(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """IFC 파일 처리 (BIM 데이터)"""
        file_path = Path(file_metadata["upload_path"])
        
        # IFC 파일 분석 시뮬레이션
        await asyncio.sleep(2)  # 실제로는 IFC 파싱 라이브러리 사용
        
        # 모의 BIM 데이터 추출
        bim_data = {
            "format_version": "IFC4",
            "project_info": {
                "name": "Sample Building Project",
                "description": "IFC model from uploaded file",
                "author": "VIBA AI System",
                "organization": "VIBA Architecture"
            },
            "building_info": {
                "total_floors": 5,
                "total_area": 2500.0,
                "height": 18.5,
                "building_type": "commercial"
            },
            "elements": {
                "walls": 127,
                "floors": 5,
                "columns": 48,
                "beams": 92,
                "doors": 35,
                "windows": 84,
                "stairs": 2,
                "roofs": 1
            },
            "materials": [
                {"name": "Concrete", "volume": 850.5, "unit": "m³"},
                {"name": "Steel", "weight": 125.3, "unit": "ton"},
                {"name": "Glass", "area": 420.0, "unit": "m²"}
            ],
            "spatial_structure": {
                "site": "Default Site",
                "building": "Building 01",
                "storeys": ["Ground Floor", "1st Floor", "2nd Floor", "3rd Floor", "Roof"]
            },
            "coordinate_system": {
                "origin": [0, 0, 0],
                "north_direction": [0, 1, 0],
                "units": "meters"
            }
        }
        
        # 3D 뷰 데이터 생성용 정보
        view_data = {
            "bbox": {
                "min": [-20, -15, 0],
                "max": [20, 15, 18.5]
            },
            "center": [0, 0, 9.25],
            "camera_distance": 50,
            "default_view": "perspective"
        }
        
        # 분석 결과
        analysis_results = {
            "structural_analysis": {
                "load_bearing_elements": 175,
                "non_structural_elements": 119,
                "structural_integrity": "verified"
            },
            "quantity_takeoff": {
                "concrete_volume": 850.5,
                "steel_weight": 125.3,
                "total_cost_estimate": 1250000000
            },
            "energy_analysis": {
                "estimated_consumption": "120 kWh/m²/year",
                "energy_class": "B",
                "renewable_potential": "30%"
            }
        }
        
        return {
            "bim_data": bim_data,
            "view_data": view_data,
            "analysis_results": analysis_results,
            "processing_time": 2.1,
            "file_format": "IFC4"
        }
        
    async def process_dwg_file(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """DWG 파일 처리 (AutoCAD 도면)"""
        await asyncio.sleep(1.5)
        
        return {
            "drawing_info": {
                "format": "AutoCAD 2018",
                "layers": 25,
                "blocks": 48,
                "entities": 1247,
                "layouts": ["Model", "Layout1", "Layout2"]
            },
            "extents": {
                "min": [-50, -30, 0],
                "max": [50, 30, 20]
            },
            "units": "meters",
            "scale": "1:100",
            "processing_time": 1.5
        }
        
    async def process_pdf_file(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """PDF 파일 처리"""
        await asyncio.sleep(0.5)
        
        return {
            "document_info": {
                "pages": 15,
                "title": "건축 설계 도서",
                "author": "VIBA Architecture",
                "creation_date": "2025-01-01"
            },
            "content_analysis": {
                "has_drawings": True,
                "has_specifications": True,
                "has_calculations": False,
                "text_extractable": True
            },
            "processing_time": 0.5
        }
        
    async def process_image_file(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """이미지 파일 처리"""
        await asyncio.sleep(0.3)
        
        return {
            "image_info": {
                "width": 1920,
                "height": 1080,
                "format": "JPEG",
                "color_mode": "RGB",
                "dpi": 72
            },
            "thumbnails_generated": {
                "small": "thumb_small.jpg",
                "medium": "thumb_medium.jpg",
                "large": "thumb_large.jpg"
            },
            "processing_time": 0.3
        }
        
    async def process_generic_file(self, file_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """일반 파일 처리"""
        await asyncio.sleep(0.2)
        
        return {
            "file_info": {
                "processed": True,
                "indexable": False
            },
            "processing_time": 0.2
        }
        
    async def get_processing_status(self, file_id: str) -> Dict[str, Any]:
        """파일 처리 상태 조회"""
        if file_id not in self.processing_status:
            raise ValueError(f"파일을 찾을 수 없습니다: {file_id}")
            
        return self.processing_status[file_id]
        
    async def get_project_files(self, project_id: str) -> List[Dict[str, Any]]:
        """프로젝트의 모든 파일 조회"""
        project_files = []
        
        for file_id, metadata in self.processing_status.items():
            if metadata["project_id"] == project_id:
                project_files.append(metadata)
                
        return sorted(project_files, key=lambda x: x["uploaded_at"], reverse=True)
        
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        """파일 삭제"""
        if file_id not in self.processing_status:
            raise ValueError(f"파일을 찾을 수 없습니다: {file_id}")
            
        metadata = self.processing_status[file_id]
        
        # 권한 확인
        if metadata["user_id"] != user_id:
            raise PermissionError("파일을 삭제할 권한이 없습니다")
            
        # 파일 삭제
        file_path = Path(metadata["upload_path"])
        if file_path.exists():
            file_path.unlink()
            
        # 메타데이터 제거
        del self.processing_status[file_id]
        
        logger.info(f"파일 삭제 완료: {file_id}")
        return True
        
    async def start_processing_worker(self):
        """백그라운드 파일 처리 워커"""
        logger.info("파일 처리 워커 시작")
        
        while True:
            try:
                # 대기열에서 파일 가져오기
                file_metadata = await self.processing_queue.get()
                file_id = file_metadata["file_id"]
                
                logger.info(f"파일 처리 시작: {file_id}")
                
                # 파일 처리
                await self.process_file(file_id)
                
            except Exception as e:
                logger.error(f"파일 처리 워커 오류: {e}")
                await asyncio.sleep(1)
                
    def get_file_stats(self) -> Dict[str, Any]:
        """파일 통계 정보"""
        stats = {
            "total_files": len(self.processing_status),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "by_type": {}
        }
        
        for metadata in self.processing_status.values():
            status = metadata["status"]
            file_type = metadata["file_type"]
            
            if status == ProcessingStatus.PENDING:
                stats["pending"] += 1
            elif status == ProcessingStatus.PROCESSING:
                stats["processing"] += 1
            elif status == ProcessingStatus.COMPLETED:
                stats["completed"] += 1
            elif status == ProcessingStatus.FAILED:
                stats["failed"] += 1
                
            if file_type not in stats["by_type"]:
                stats["by_type"][file_type] = 0
            stats["by_type"][file_type] += 1
            
        return stats

# BIM 데이터 분석기
class BIMAnalyzer:
    """BIM 데이터 고급 분석 클래스"""
    
    def __init__(self):
        self.analysis_cache = {}
        
    async def analyze_spatial_relationships(self, bim_data: Dict[str, Any]) -> Dict[str, Any]:
        """공간 관계 분석"""
        await asyncio.sleep(0.5)
        
        return {
            "adjacency_matrix": self._generate_adjacency_matrix(bim_data),
            "circulation_paths": self._analyze_circulation(bim_data),
            "space_efficiency": 0.82,
            "connectivity_score": 0.91
        }
        
    async def analyze_sustainability(self, bim_data: Dict[str, Any]) -> Dict[str, Any]:
        """지속가능성 분석"""
        await asyncio.sleep(0.8)
        
        return {
            "carbon_footprint": {
                "embodied_carbon": 450.5,  # tCO2e
                "operational_carbon": 25.3,  # tCO2e/year
                "total_lifecycle": 1206.5  # tCO2e
            },
            "energy_performance": {
                "heating_demand": 45.2,  # kWh/m²/year
                "cooling_demand": 38.7,  # kWh/m²/year
                "lighting_demand": 15.3,  # kWh/m²/year
                "renewable_generation": 30.0  # kWh/m²/year
            },
            "water_usage": {
                "potable_water": 120.5,  # L/person/day
                "recycled_water": 45.2,  # L/person/day
                "rainwater_harvesting": 25000  # L/year
            },
            "material_health": {
                "recycled_content": 0.35,
                "local_materials": 0.62,
                "low_emission_materials": 0.88
            },
            "certification_potential": {
                "leed": "Gold",
                "breeam": "Very Good",
                "well": "Silver"
            }
        }
        
    async def analyze_cost_estimation(self, bim_data: Dict[str, Any]) -> Dict[str, Any]:
        """비용 추정 분석"""
        await asyncio.sleep(0.6)
        
        materials = bim_data.get("materials", [])
        total_cost = 0
        cost_breakdown = []
        
        # 재료별 비용 계산
        material_costs = {
            "Concrete": 150000,  # 원/m³
            "Steel": 1200000,    # 원/ton
            "Glass": 250000      # 원/m²
        }
        
        for material in materials:
            unit_cost = material_costs.get(material["name"], 100000)
            quantity = material.get("volume", material.get("weight", material.get("area", 0)))
            cost = unit_cost * quantity
            total_cost += cost
            
            cost_breakdown.append({
                "material": material["name"],
                "quantity": quantity,
                "unit": material["unit"],
                "unit_cost": unit_cost,
                "total_cost": cost
            })
            
        # 공사비 추가
        labor_cost = total_cost * 0.4
        equipment_cost = total_cost * 0.15
        overhead_cost = total_cost * 0.2
        
        return {
            "material_cost": total_cost,
            "labor_cost": labor_cost,
            "equipment_cost": equipment_cost,
            "overhead_cost": overhead_cost,
            "total_cost": total_cost + labor_cost + equipment_cost + overhead_cost,
            "cost_breakdown": cost_breakdown,
            "cost_per_sqm": (total_cost + labor_cost + equipment_cost + overhead_cost) / bim_data["building_info"]["total_area"],
            "confidence_level": 0.85
        }
        
    def _generate_adjacency_matrix(self, bim_data: Dict[str, Any]) -> List[List[int]]:
        """인접 행렬 생성 (모의)"""
        num_spaces = 10  # 예시
        matrix = [[0 for _ in range(num_spaces)] for _ in range(num_spaces)]
        
        # 일부 연결 설정
        connections = [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5)]
        for i, j in connections:
            matrix[i][j] = 1
            matrix[j][i] = 1
            
        return matrix
        
    def _analyze_circulation(self, bim_data: Dict[str, Any]) -> Dict[str, Any]:
        """동선 분석 (모의)"""
        return {
            "main_circulation": ["Entrance", "Lobby", "Corridor", "Stairs/Elevator"],
            "secondary_circulation": ["Emergency Exit", "Service Corridor"],
            "circulation_efficiency": 0.78,
            "bottlenecks": ["Main Entrance", "Ground Floor Elevator"]
        }

# 전역 인스턴스
file_processor = FileProcessor()
bim_analyzer = BIMAnalyzer()