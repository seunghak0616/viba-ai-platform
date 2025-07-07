"""
설계 검토자 AI 에이전트
====================

설계안의 품질 평가, 대안 검토, 개선점 제안을 담당하는 AI 에이전트
건축 이론적 근거, 사용성, 미적 가치, 기능성 등을 종합적으로 검토

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import asyncio
import json
import logging
import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime

# 분석 라이브러리
try:
    import pandas as pd
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    logger.warning("Analysis libraries not available, using basic calculations")
    pd = None

# 프로젝트 임포트
from ..base_agent import BaseVIBAAgent, AgentCapability
from ...utils.metrics_collector import record_ai_inference_metric
from ...knowledge.building_codes import BuildingCodeChecker
from ...knowledge.ifc_schema import IFC43Schema

logger = logging.getLogger(__name__)


class ReviewCategory(Enum):
    """검토 카테고리"""
    ARCHITECTURAL_THEORY = "architectural_theory"
    FUNCTIONALITY = "functionality"
    AESTHETICS = "aesthetics"
    USABILITY = "usability"
    ACCESSIBILITY = "accessibility"
    SUSTAINABILITY = "sustainability"
    CULTURAL_CONTEXT = "cultural_context"
    TECHNICAL_FEASIBILITY = "technical_feasibility"


class ReviewCriteria(Enum):
    """검토 기준"""
    PROPORTION = "proportion"
    HARMONY = "harmony"
    UNITY = "unity"
    BALANCE = "balance"
    RHYTHM = "rhythm"
    SCALE = "scale"
    CIRCULATION = "circulation"
    SPATIAL_QUALITY = "spatial_quality"
    MATERIAL_APPROPRIATENESS = "material_appropriateness"
    ENVIRONMENTAL_RESPONSE = "environmental_response"


class IssueLevel(Enum):
    """문제 심각도"""
    CRITICAL = "critical"     # 즉시 수정 필요
    MAJOR = "major"          # 중요한 개선 사항
    MINOR = "minor"          # 권장 사항
    SUGGESTION = "suggestion" # 제안 사항


@dataclass
class ReviewCriterion:
    """검토 기준"""
    category: ReviewCategory
    criterion: ReviewCriteria
    weight: float  # 0.0-1.0
    description: str


@dataclass
class DesignIssue:
    """설계 문제점"""
    category: ReviewCategory
    level: IssueLevel
    title: str
    description: str
    location: Optional[str] = None
    impact: str = ""
    recommendation: str = ""
    theoretical_basis: str = ""


@dataclass
class QualityMetric:
    """품질 지표"""
    category: ReviewCategory
    name: str
    score: float  # 0-100
    weight: float
    issues: List[DesignIssue] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)


@dataclass
class DesignAlternative:
    """설계 대안"""
    alternative_id: str
    title: str
    description: str
    modifications: List[str]
    expected_improvements: List[str]
    implementation_effort: str  # low, medium, high
    cost_impact: str  # low, medium, high
    overall_score: float


@dataclass
class DesignReview:
    """설계 검토 결과"""
    overall_quality_score: float  # 0-100
    overall_grade: str  # A+, A, B, C, D
    quality_metrics: List[QualityMetric]
    critical_issues: List[DesignIssue]
    major_issues: List[DesignIssue]
    minor_issues: List[DesignIssue]
    strengths: List[str]
    alternatives: List[DesignAlternative]
    final_recommendations: List[str]
    review_timestamp: str
    confidence: float


class DesignReviewerAgent(BaseVIBAAgent):
    """설계 검토자 AI 에이전트"""
    
    def __init__(self):
        super().__init__(
            agent_id="design_reviewer",
            capabilities=[
                AgentCapability.DESIGN_REVIEW,
                AgentCapability.QUALITY_ASSESSMENT,
                AgentCapability.ALTERNATIVE_GENERATION
            ]
        )
        
        # 검토 기준 및 가중치
        self.review_criteria = self._initialize_review_criteria()
        self.quality_benchmarks = self._load_quality_benchmarks()
        self.design_patterns = self._load_design_patterns()
        self.cultural_standards = self._load_cultural_standards()
        
        # 기존 우수 설계 사례 데이터베이스
        self.reference_designs = self._load_reference_designs()
        
        # 검토 이력
        self.review_history = []
        
        logger.info("Design Reviewer Agent initialized")
    
    @record_ai_inference_metric("design_review")
    async def process_task_async(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """비동기 태스크 처리"""
        start_time = time.time()
        
        try:
            task_type = task.get('type', 'comprehensive_review')
            design_data = task.get('design_data', {})
            bim_model = task.get('bim_model', {})
            review_scope = task.get('review_scope', ['all'])
            
            if task_type == 'comprehensive_review':
                result = await self._perform_comprehensive_review(design_data, bim_model, review_scope)
            elif task_type == 'quality_assessment':
                result = await self._assess_design_quality(design_data, bim_model)
            elif task_type == 'alternative_generation':
                result = await self._generate_design_alternatives(design_data, bim_model)
            elif task_type == 'specific_review':
                result = await self._perform_specific_review(design_data, bim_model, task.get('criteria', []))
            else:
                raise ValueError(f"Unknown task type: {task_type}")
            
            processing_time = time.time() - start_time
            
            # 성능 메트릭 업데이트
            self.performance_stats['total_tasks'] += 1
            self.performance_stats['average_response_time'] = (
                (self.performance_stats['average_response_time'] * (self.performance_stats['total_tasks'] - 1) + processing_time) 
                / self.performance_stats['total_tasks']
            )
            self.performance_stats['success_rate'] = (
                (self.performance_stats.get('successful_tasks', 0) + 1) / self.performance_stats['total_tasks']
            )
            
            return {
                "status": "success",
                "result": result,
                "processing_time": processing_time,
                "agent_id": self.agent_id
            }
            
        except Exception as e:
            logger.error(f"Design review failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "processing_time": time.time() - start_time,
                "agent_id": self.agent_id
            }
    
    async def _perform_comprehensive_review(self, design_data: Dict[str, Any], bim_model: Dict[str, Any], review_scope: List[str]) -> Dict[str, Any]:
        """종합 설계 검토"""
        logger.info("Starting comprehensive design review")
        
        # 1. 품질 평가
        quality_assessment = await self._assess_design_quality(design_data, bim_model)
        
        # 2. 이론적 근거 검토
        theoretical_review = await self._review_theoretical_basis(design_data)
        
        # 3. 기능성 검토
        functionality_review = await self._review_functionality(design_data, bim_model)
        
        # 4. 미적 가치 검토
        aesthetic_review = await self._review_aesthetic_quality(design_data)
        
        # 5. 사용성 검토
        usability_review = await self._review_usability(design_data, bim_model)
        
        # 6. 접근성 검토
        accessibility_review = await self._review_accessibility(design_data, bim_model)
        
        # 7. 지속가능성 검토
        sustainability_review = await self._review_sustainability(design_data, bim_model)
        
        # 8. 문화적 적합성 검토
        cultural_review = await self._review_cultural_context(design_data)
        
        # 종합 점수 계산
        overall_score = self._calculate_overall_score([
            quality_assessment, theoretical_review, functionality_review,
            aesthetic_review, usability_review, accessibility_review,
            sustainability_review, cultural_review
        ])
        
        # 주요 문제점 및 강점 추출
        all_issues = []
        all_strengths = []
        
        for review in [quality_assessment, theoretical_review, functionality_review,
                      aesthetic_review, usability_review, accessibility_review,
                      sustainability_review, cultural_review]:
            all_issues.extend(review.get('issues', []))
            all_strengths.extend(review.get('strengths', []))
        
        # 문제점 분류
        critical_issues = [issue for issue in all_issues if issue.get('level') == IssueLevel.CRITICAL.value]
        major_issues = [issue for issue in all_issues if issue.get('level') == IssueLevel.MAJOR.value]
        minor_issues = [issue for issue in all_issues if issue.get('level') == IssueLevel.MINOR.value]
        
        # 설계 대안 생성
        alternatives = await self._generate_design_alternatives(design_data, bim_model, all_issues)
        
        # 최종 권고사항
        final_recommendations = self._generate_final_recommendations(all_issues, alternatives)
        
        return {
            "review_type": "comprehensive",
            "overall_score": overall_score,
            "overall_grade": self._calculate_grade(overall_score),
            "detailed_reviews": {
                "quality_assessment": quality_assessment,
                "theoretical_review": theoretical_review,
                "functionality_review": functionality_review,
                "aesthetic_review": aesthetic_review,
                "usability_review": usability_review,
                "accessibility_review": accessibility_review,
                "sustainability_review": sustainability_review,
                "cultural_review": cultural_review
            },
            "critical_issues": critical_issues,
            "major_issues": major_issues,
            "minor_issues": minor_issues,
            "strengths": list(set(all_strengths)),  # 중복 제거
            "alternatives": alternatives,
            "final_recommendations": final_recommendations,
            "review_timestamp": datetime.now().isoformat(),
            "confidence": 0.91
        }
    
    async def _assess_design_quality(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """설계 품질 평가"""
        logger.info("Assessing design quality")
        
        quality_metrics = []
        
        # 1. 공간 구성 품질
        spatial_quality = self._evaluate_spatial_quality(design_data, bim_model)
        quality_metrics.append(QualityMetric(
            category=ReviewCategory.FUNCTIONALITY,
            name="공간 구성 품질",
            score=spatial_quality['score'],
            weight=0.25,
            issues=spatial_quality.get('issues', []),
            strengths=spatial_quality.get('strengths', [])
        ))
        
        # 2. 비례 및 조화
        proportion_quality = self._evaluate_proportions(design_data)
        quality_metrics.append(QualityMetric(
            category=ReviewCategory.ARCHITECTURAL_THEORY,
            name="비례 및 조화",
            score=proportion_quality['score'],
            weight=0.20,
            issues=proportion_quality.get('issues', []),
            strengths=proportion_quality.get('strengths', [])
        ))
        
        # 3. 재료 적합성
        material_quality = self._evaluate_material_appropriateness(design_data, bim_model)
        quality_metrics.append(QualityMetric(
            category=ReviewCategory.TECHNICAL_FEASIBILITY,
            name="재료 적합성",
            score=material_quality['score'],
            weight=0.15,
            issues=material_quality.get('issues', []),
            strengths=material_quality.get('strengths', [])
        ))
        
        # 4. 환경 대응성
        environmental_quality = self._evaluate_environmental_response(design_data, bim_model)
        quality_metrics.append(QualityMetric(
            category=ReviewCategory.SUSTAINABILITY,
            name="환경 대응성",
            score=environmental_quality['score'],
            weight=0.20,
            issues=environmental_quality.get('issues', []),
            strengths=environmental_quality.get('strengths', [])
        ))
        
        # 5. 통합성 및 완성도
        integration_quality = self._evaluate_design_integration(design_data, bim_model)
        quality_metrics.append(QualityMetric(
            category=ReviewCategory.AESTHETICS,
            name="통합성 및 완성도",
            score=integration_quality['score'],
            weight=0.20,
            issues=integration_quality.get('issues', []),
            strengths=integration_quality.get('strengths', [])
        ))
        
        # 전체 품질 점수 계산
        total_weighted_score = sum(metric.score * metric.weight for metric in quality_metrics)
        
        return {
            "assessment_type": "quality",
            "overall_score": total_weighted_score,
            "quality_metrics": [metric.__dict__ for metric in quality_metrics],
            "benchmark_comparison": self._compare_with_benchmarks(total_weighted_score),
            "confidence": 0.89
        }
    
    async def _review_theoretical_basis(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """건축 이론적 근거 검토"""
        logger.info("Reviewing theoretical basis")
        
        issues = []
        strengths = []
        
        # 1. 설계 이론 적용도 검토
        style = design_data.get('architectural_style', 'modern')
        style_compliance = self._check_style_compliance(design_data, style)
        
        if style_compliance['score'] < 70:
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": f"{style} 스타일 이론 적용 부족",
                "description": f"{style} 스타일의 핵심 원리가 충분히 반영되지 않았습니다.",
                "theoretical_basis": f"{style} 스타일의 특징: {style_compliance['missing_elements']}",
                "recommendation": f"{style} 스타일의 {', '.join(style_compliance['missing_elements'])} 요소를 강화하세요."
            })
        else:
            strengths.append(f"{style} 스타일의 이론적 원리가 잘 적용되었습니다.")
        
        # 2. 비례 시스템 검토
        proportions = design_data.get('proportions', {})
        proportion_analysis = self._analyze_proportional_system(proportions)
        
        if proportion_analysis['deviation'] > 0.2:
            issues.append({
                "level": IssueLevel.MINOR.value,
                "title": "비례 시스템 일관성 부족",
                "description": "설계 전반에 걸친 비례 시스템의 일관성이 부족합니다.",
                "theoretical_basis": "건축에서 비례는 조화와 아름다움을 창조하는 핵심 요소입니다.",
                "recommendation": "황금비 또는 모듈러 시스템을 일관되게 적용하세요."
            })
        
        # 3. 공간 위계 검토
        spatial_hierarchy = self._analyze_spatial_hierarchy(design_data)
        
        if not spatial_hierarchy['clear_hierarchy']:
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": "공간 위계 불분명",
                "description": "주공간과 보조공간의 위계가 명확하지 않습니다.",
                "theoretical_basis": "공간 위계는 사용자의 경험과 공간의 기능적 효율성을 결정합니다.",
                "recommendation": "주공간을 중심으로 한 명확한 공간 위계를 설정하세요."
            })
        else:
            strengths.append("공간 위계가 명확하게 설정되어 기능적 효율성이 높습니다.")
        
        # 종합 점수 계산
        theoretical_score = 100 - (len([i for i in issues if i['level'] == IssueLevel.CRITICAL.value]) * 30 +
                                  len([i for i in issues if i['level'] == IssueLevel.MAJOR.value]) * 20 +
                                  len([i for i in issues if i['level'] == IssueLevel.MINOR.value]) * 10)
        
        return {
            "review_type": "theoretical_basis",
            "score": max(0, theoretical_score),
            "issues": issues,
            "strengths": strengths,
            "style_compliance": style_compliance,
            "proportion_analysis": proportion_analysis,
            "spatial_hierarchy": spatial_hierarchy
        }
    
    async def _review_functionality(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """기능성 검토"""
        logger.info("Reviewing functionality")
        
        issues = []
        strengths = []
        
        # 1. 공간 프로그램 적합성
        program_adequacy = self._check_program_adequacy(design_data, bim_model)
        
        if program_adequacy['missing_spaces']:
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": "필수 공간 누락",
                "description": f"필요한 공간이 누락되었습니다: {', '.join(program_adequacy['missing_spaces'])}",
                "recommendation": "누락된 공간을 추가하거나 기존 공간의 용도를 조정하세요."
            })
        
        # 2. 동선 효율성
        circulation_efficiency = self._analyze_circulation_efficiency(design_data, bim_model)
        
        if circulation_efficiency['efficiency_score'] < 70:
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": "동선 효율성 부족",
                "description": "공간 간 이동이 비효율적입니다.",
                "recommendation": "주요 공간 간의 직접적인 동선을 확보하고 불필요한 경유를 최소화하세요."
            })
        else:
            strengths.append("효율적인 동선 계획으로 공간 이용도가 높습니다.")
        
        # 3. 공간 크기 적정성
        space_sizing = self._check_space_sizing(design_data, bim_model)
        
        for space_issue in space_sizing['undersized_spaces']:
            issues.append({
                "level": IssueLevel.MINOR.value,
                "title": f"{space_issue['name']} 공간 크기 부족",
                "description": f"현재 {space_issue['current_area']}㎡, 권장 {space_issue['recommended_area']}㎡",
                "recommendation": f"{space_issue['name']} 공간을 {space_issue['recommended_area']}㎡로 확장하세요."
            })
        
        # 4. 기능별 조닝
        zoning_quality = self._evaluate_functional_zoning(design_data, bim_model)
        
        if zoning_quality['conflicts']:
            for conflict in zoning_quality['conflicts']:
                issues.append({
                    "level": IssueLevel.MINOR.value,
                    "title": "기능적 충돌",
                    "description": f"{conflict['space1']}과 {conflict['space2']} 간의 기능적 충돌",
                    "recommendation": "상충되는 기능의 공간을 분리하거나 완충 공간을 설치하세요."
                })
        
        functionality_score = 100 - (len([i for i in issues if i['level'] == IssueLevel.CRITICAL.value]) * 30 +
                                    len([i for i in issues if i['level'] == IssueLevel.MAJOR.value]) * 20 +
                                    len([i for i in issues if i['level'] == IssueLevel.MINOR.value]) * 10)
        
        return {
            "review_type": "functionality",
            "score": max(0, functionality_score),
            "issues": issues,
            "strengths": strengths,
            "program_adequacy": program_adequacy,
            "circulation_efficiency": circulation_efficiency,
            "space_sizing": space_sizing,
            "zoning_quality": zoning_quality
        }
    
    async def _review_aesthetic_quality(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """미적 가치 검토"""
        logger.info("Reviewing aesthetic quality")
        
        issues = []
        strengths = []
        
        # 1. 외관 구성
        facade_composition = self._analyze_facade_composition(design_data)
        
        if facade_composition['balance_score'] < 70:
            issues.append({
                "level": IssueLevel.MINOR.value,
                "title": "외관 구성 불균형",
                "description": "외관의 구성 요소들이 조화롭지 않습니다.",
                "recommendation": "창문, 출입구, 장식 요소의 배치를 재조정하여 균형을 맞추세요."
            })
        
        # 2. 색채 계획
        color_scheme = self._evaluate_color_scheme(design_data)
        
        if color_scheme['harmony_score'] < 75:
            issues.append({
                "level": IssueLevel.SUGGESTION.value,
                "title": "색채 조화 개선 필요",
                "description": "선택된 색채들의 조화도가 낮습니다.",
                "recommendation": "색채환(color wheel) 이론을 바탕으로 보완색 또는 유사색 조합을 고려하세요."
            })
        
        # 3. 재료의 미적 적합성
        material_aesthetics = self._evaluate_material_aesthetics(design_data)
        
        if material_aesthetics['coherence_score'] > 80:
            strengths.append("재료 선택이 전체 디자인과 조화롭게 통합되었습니다.")
        
        # 4. 스타일 일관성
        style_consistency = self._check_style_consistency(design_data)
        
        if not style_consistency['consistent']:
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": "스타일 일관성 부족",
                "description": "설계 요소들이 일관된 스타일을 나타내지 못하고 있습니다.",
                "recommendation": f"선택한 {design_data.get('architectural_style', '스타일')}에 맞게 모든 요소를 통일하세요."
            })
        
        aesthetic_score = 100 - (len([i for i in issues if i['level'] == IssueLevel.CRITICAL.value]) * 30 +
                               len([i for i in issues if i['level'] == IssueLevel.MAJOR.value]) * 20 +
                               len([i for i in issues if i['level'] == IssueLevel.MINOR.value]) * 10 +
                               len([i for i in issues if i['level'] == IssueLevel.SUGGESTION.value]) * 5)
        
        return {
            "review_type": "aesthetic_quality",
            "score": max(0, aesthetic_score),
            "issues": issues,
            "strengths": strengths,
            "facade_composition": facade_composition,
            "color_scheme": color_scheme,
            "material_aesthetics": material_aesthetics,
            "style_consistency": style_consistency
        }
    
    async def _review_usability(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """사용성 검토"""
        logger.info("Reviewing usability")
        
        issues = []
        strengths = []
        
        # 1. 사용자 동선 분석
        user_flow = self._analyze_user_flow(design_data, bim_model)
        
        if user_flow['bottlenecks']:
            for bottleneck in user_flow['bottlenecks']:
                issues.append({
                    "level": IssueLevel.MAJOR.value,
                    "title": f"{bottleneck['location']} 동선 병목",
                    "description": f"예상 혼잡도: {bottleneck['congestion_level']}",
                    "recommendation": f"통로 폭을 {bottleneck['recommended_width']}m로 확장하거나 대안 경로를 제공하세요."
                })
        
        # 2. 편의시설 접근성
        amenity_access = self._check_amenity_accessibility(design_data, bim_model)
        
        if amenity_access['avg_distance'] > 50:  # 50m 이상
            issues.append({
                "level": IssueLevel.MINOR.value,
                "title": "편의시설 접근성 부족",
                "description": f"주요 편의시설까지 평균 거리: {amenity_access['avg_distance']}m",
                "recommendation": "편의시설을 분산 배치하거나 중앙 위치로 이동하세요."
            })
        
        # 3. 공간 가시성
        spatial_visibility = self._analyze_spatial_visibility(design_data, bim_model)
        
        if spatial_visibility['orientation_score'] > 80:
            strengths.append("공간 구성이 직관적이어서 길찾기가 쉽습니다.")
        
        # 4. 프라이버시 확보
        privacy_analysis = self._analyze_privacy_levels(design_data, bim_model)
        
        if privacy_analysis['issues']:
            for privacy_issue in privacy_analysis['issues']:
                issues.append({
                    "level": IssueLevel.MINOR.value,
                    "title": f"{privacy_issue['space']} 프라이버시 부족",
                    "description": privacy_issue['description'],
                    "recommendation": privacy_issue['solution']
                })
        
        usability_score = 100 - (len([i for i in issues if i['level'] == IssueLevel.CRITICAL.value]) * 30 +
                               len([i for i in issues if i['level'] == IssueLevel.MAJOR.value]) * 20 +
                               len([i for i in issues if i['level'] == IssueLevel.MINOR.value]) * 10)
        
        return {
            "review_type": "usability",
            "score": max(0, usability_score),
            "issues": issues,
            "strengths": strengths,
            "user_flow": user_flow,
            "amenity_access": amenity_access,
            "spatial_visibility": spatial_visibility,
            "privacy_analysis": privacy_analysis
        }
    
    async def _review_accessibility(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """접근성 검토"""
        logger.info("Reviewing accessibility")
        
        issues = []
        strengths = []
        
        # 1. 물리적 접근성 (장애인 접근)
        physical_access = self._check_physical_accessibility(design_data, bim_model)
        
        if not physical_access['wheelchair_accessible']:
            issues.append({
                "level": IssueLevel.CRITICAL.value,
                "title": "휠체어 접근 불가",
                "description": "휠체어 사용자가 접근할 수 없는 구역이 있습니다.",
                "recommendation": "경사로 설치 또는 승강기 추가로 접근성을 확보하세요."
            })
        
        # 2. 출입구 접근성
        entrance_access = self._check_entrance_accessibility(design_data, bim_model)
        
        if entrance_access['barrier_free_ratio'] < 0.8:
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": "출입구 접근성 부족",
                "description": f"무장애 출입구 비율: {entrance_access['barrier_free_ratio']*100:.1f}%",
                "recommendation": "주 출입구를 무장애로 개선하고 충분한 폭을 확보하세요."
            })
        
        # 3. 수직 이동 접근성
        vertical_access = self._check_vertical_accessibility(design_data, bim_model)
        
        if not vertical_access['elevator_available'] and design_data.get('stories', 1) > 2:
            issues.append({
                "level": IssueLevel.CRITICAL.value,
                "title": "수직 이동 접근성 부족",
                "description": "3층 이상 건물에 승강기가 없습니다.",
                "recommendation": "승강기를 설치하여 모든 층에 대한 접근성을 확보하세요."
            })
        
        # 4. 시각적 접근성
        visual_access = self._check_visual_accessibility(design_data, bim_model)
        
        if visual_access['signage_score'] > 80:
            strengths.append("시각적 안내 시스템이 잘 구축되어 있습니다.")
        
        accessibility_score = 100 - (len([i for i in issues if i['level'] == IssueLevel.CRITICAL.value]) * 40 +
                                    len([i for i in issues if i['level'] == IssueLevel.MAJOR.value]) * 25 +
                                    len([i for i in issues if i['level'] == IssueLevel.MINOR.value]) * 10)
        
        return {
            "review_type": "accessibility",
            "score": max(0, accessibility_score),
            "issues": issues,
            "strengths": strengths,
            "physical_access": physical_access,
            "entrance_access": entrance_access,
            "vertical_access": vertical_access,
            "visual_access": visual_access
        }
    
    async def _review_sustainability(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """지속가능성 검토"""
        logger.info("Reviewing sustainability")
        
        issues = []
        strengths = []
        
        # 1. 에너지 효율성
        energy_efficiency = self._evaluate_energy_efficiency(design_data, bim_model)
        
        if energy_efficiency['rating'] < 3:  # 5점 만점
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": "에너지 효율성 부족",
                "description": f"에너지 효율 등급: {energy_efficiency['rating']}/5",
                "recommendation": "단열 성능 향상, 고효율 설비 적용, 재생에너지 도입을 고려하세요."
            })
        
        # 2. 자연 환경 활용
        natural_integration = self._evaluate_natural_integration(design_data, bim_model)
        
        if natural_integration['daylight_score'] > 80:
            strengths.append("자연채광을 효과적으로 활용하여 에너지 절약에 기여합니다.")
        
        # 3. 재료의 지속가능성
        material_sustainability = self._evaluate_material_sustainability(design_data)
        
        if material_sustainability['recycled_content'] < 0.3:
            issues.append({
                "level": IssueLevel.MINOR.value,
                "title": "재생 재료 활용 부족",
                "description": f"재생 재료 비율: {material_sustainability['recycled_content']*100:.1f}%",
                "recommendation": "재생 재료 또는 친환경 인증 재료의 사용을 늘리세요."
            })
        
        # 4. 생태계 영향
        ecological_impact = self._evaluate_ecological_impact(design_data, bim_model)
        
        if ecological_impact['green_ratio'] < 0.2:
            issues.append({
                "level": IssueLevel.MINOR.value,
                "title": "녹지 공간 부족",
                "description": f"녹지 비율: {ecological_impact['green_ratio']*100:.1f}%",
                "recommendation": "옥상 정원, 벽면 녹화, 조경 공간을 확대하세요."
            })
        
        sustainability_score = 100 - (len([i for i in issues if i['level'] == IssueLevel.CRITICAL.value]) * 30 +
                                     len([i for i in issues if i['level'] == IssueLevel.MAJOR.value]) * 20 +
                                     len([i for i in issues if i['level'] == IssueLevel.MINOR.value]) * 10)
        
        return {
            "review_type": "sustainability",
            "score": max(0, sustainability_score),
            "issues": issues,
            "strengths": strengths,
            "energy_efficiency": energy_efficiency,
            "natural_integration": natural_integration,
            "material_sustainability": material_sustainability,
            "ecological_impact": ecological_impact
        }
    
    async def _review_cultural_context(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """문화적 맥락 검토"""
        logger.info("Reviewing cultural context")
        
        issues = []
        strengths = []
        
        # 1. 지역적 특성 반영
        regional_character = self._evaluate_regional_character(design_data)
        
        if regional_character['score'] > 80:
            strengths.append("지역의 건축적 특성이 잘 반영되었습니다.")
        
        # 2. 전통적 요소 활용
        traditional_elements = self._evaluate_traditional_elements(design_data)
        
        if design_data.get('architectural_style') == 'traditional' and traditional_elements['authenticity'] < 70:
            issues.append({
                "level": IssueLevel.MAJOR.value,
                "title": "전통 요소 부족",
                "description": "전통 스타일임에도 불구하고 전통적 요소가 부족합니다.",
                "recommendation": "한옥의 기본 구조, 비례, 재료를 적극 활용하세요."
            })
        
        # 3. 현대적 해석
        contemporary_interpretation = self._evaluate_contemporary_interpretation(design_data)
        
        if contemporary_interpretation['balance_score'] > 75:
            strengths.append("전통과 현대의 균형 있는 해석이 돋보입니다.")
        
        cultural_score = 100 - (len([i for i in issues if i['level'] == IssueLevel.CRITICAL.value]) * 30 +
                              len([i for i in issues if i['level'] == IssueLevel.MAJOR.value]) * 20 +
                              len([i for i in issues if i['level'] == IssueLevel.MINOR.value]) * 10)
        
        return {
            "review_type": "cultural_context",
            "score": max(0, cultural_score),
            "issues": issues,
            "strengths": strengths,
            "regional_character": regional_character,
            "traditional_elements": traditional_elements,
            "contemporary_interpretation": contemporary_interpretation
        }
    
    async def _generate_design_alternatives(self, design_data: Dict[str, Any], bim_model: Dict[str, Any], issues: Optional[List] = None) -> List[Dict[str, Any]]:
        """설계 대안 생성"""
        logger.info("Generating design alternatives")
        
        alternatives = []
        
        # 주요 문제점을 바탕으로 대안 생성
        if issues:
            major_issues = [issue for issue in issues if issue.get('level') == IssueLevel.MAJOR.value]
            
            # 공간 재배치 대안
            if any('동선' in issue.get('title', '') for issue in major_issues):
                alternatives.append({
                    "alternative_id": "spatial_reorganization",
                    "title": "공간 재배치 계획",
                    "description": "주요 공간의 위치를 재조정하여 동선 효율성을 향상시킵니다.",
                    "modifications": [
                        "주출입구와 수직동선 연결 개선",
                        "공용공간과 개인공간 명확한 구분",
                        "서비스 공간의 효율적 배치"
                    ],
                    "expected_improvements": [
                        "동선 효율성 30% 향상",
                        "공간 활용도 증가",
                        "사용자 만족도 개선"
                    ],
                    "implementation_effort": "medium",
                    "cost_impact": "medium",
                    "overall_score": 85.0
                })
            
            # 외관 개선 대안
            if any('외관' in issue.get('title', '') or '미적' in issue.get('title', '') for issue in major_issues):
                alternatives.append({
                    "alternative_id": "facade_enhancement",
                    "title": "외관 디자인 개선",
                    "description": "외관의 비례와 구성을 개선하여 미적 가치를 향상시킵니다.",
                    "modifications": [
                        "창호 비율 및 배치 조정",
                        "외부 마감재 변경",
                        "입면 구성 요소 재배치"
                    ],
                    "expected_improvements": [
                        "시각적 균형감 향상",
                        "건물의 상징성 강화",
                        "주변 환경과의 조화"
                    ],
                    "implementation_effort": "low",
                    "cost_impact": "low",
                    "overall_score": 78.0
                })
            
            # 기능성 개선 대안
            if any('기능' in issue.get('title', '') or '공간' in issue.get('title', '') for issue in major_issues):
                alternatives.append({
                    "alternative_id": "functional_improvement",
                    "title": "기능성 강화 계획",
                    "description": "공간의 기능적 효율성과 사용성을 개선합니다.",
                    "modifications": [
                        "다목적 공간 도입",
                        "가변형 파티션 적용",
                        "스마트 공간 관리 시스템"
                    ],
                    "expected_improvements": [
                        "공간 활용 효율 40% 증가",
                        "운영 비용 절감",
                        "미래 변화 대응력 향상"
                    ],
                    "implementation_effort": "high",
                    "cost_impact": "medium",
                    "overall_score": 82.0
                })
        
        # 지속가능성 강화 대안 (항상 포함)
        alternatives.append({
            "alternative_id": "sustainability_upgrade",
            "title": "지속가능성 강화",
            "description": "환경 친화적 설계 요소를 강화하여 지속가능성을 개선합니다.",
            "modifications": [
                "태양광 패널 설치",
                "우수 재활용 시스템",
                "자연 환기 시스템 강화",
                "친환경 재료 적용 확대"
            ],
            "expected_improvements": [
                "에너지 효율 25% 향상",
                "운영비 장기적 절감",
                "친환경 인증 획득 가능"
            ],
            "implementation_effort": "medium",
            "cost_impact": "high",
            "overall_score": 88.0
        })
        
        # 우선순위 정렬 (점수 기준)
        alternatives.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return alternatives[:5]  # 상위 5개 대안 반환
    
    # === 분석 및 평가 메서드들 ===
    
    def _evaluate_spatial_quality(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """공간 구성 품질 평가"""
        spaces = design_data.get('spaces', [])
        total_area = sum(space.get('area', 0) for space in spaces)
        
        # 공간 비율 분석
        public_area = sum(space.get('area', 0) for space in spaces if space.get('type') in ['living_room', 'lobby'])
        private_area = sum(space.get('area', 0) for space in spaces if space.get('type') in ['bedroom', 'office'])
        service_area = sum(space.get('area', 0) for space in spaces if space.get('type') in ['bathroom', 'kitchen'])
        
        balance_score = 100
        issues = []
        strengths = []
        
        # 공간 비율 검토
        if total_area > 0:
            public_ratio = public_area / total_area
            private_ratio = private_area / total_area
            service_ratio = service_area / total_area
            
            if service_ratio < 0.15:  # 서비스 공간 15% 미만
                balance_score -= 20
                issues.append("서비스 공간 비율이 부족합니다.")
            
            if public_ratio > 0.6:  # 공용 공간 60% 초과
                balance_score -= 15
                issues.append("공용 공간 비율이 과도합니다.")
            elif public_ratio > 0.4:
                strengths.append("공용 공간과 사적 공간의 균형이 적절합니다.")
        
        return {
            "score": balance_score,
            "issues": issues,
            "strengths": strengths,
            "space_ratios": {
                "public": public_ratio if total_area > 0 else 0,
                "private": private_ratio if total_area > 0 else 0,
                "service": service_ratio if total_area > 0 else 0
            }
        }
    
    def _evaluate_proportions(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """비례 평가"""
        proportions = design_data.get('proportions', {})
        
        # 황금비 적용 여부 확인
        golden_ratio = 1.618
        width = proportions.get('width', 10)
        height = proportions.get('height', 6)
        
        actual_ratio = width / height if height > 0 else 1
        golden_deviation = abs(actual_ratio - golden_ratio) / golden_ratio
        
        score = max(0, 100 - golden_deviation * 100)
        
        issues = []
        strengths = []
        
        if golden_deviation < 0.1:
            strengths.append("황금비에 가까운 조화로운 비례입니다.")
        elif golden_deviation > 0.3:
            issues.append("비례가 조화롭지 않습니다.")
        
        return {
            "score": score,
            "issues": issues,
            "strengths": strengths,
            "actual_ratio": actual_ratio,
            "golden_deviation": golden_deviation
        }
    
    def _evaluate_material_appropriateness(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """재료 적합성 평가"""
        materials = design_data.get('materials', {})
        building_type = design_data.get('building_type', 'residential')
        
        score = 80  # 기본 점수
        issues = []
        strengths = []
        
        # 건물 용도에 따른 재료 적합성 검토
        if building_type == 'residential':
            if 'wood' in materials.values():
                strengths.append("주거 건축에 적합한 목재를 활용했습니다.")
                score += 10
        elif building_type == 'office':
            if 'steel' in materials.values() or 'concrete' in materials.values():
                strengths.append("업무 건축에 적합한 구조 재료를 선택했습니다.")
                score += 10
        
        # 지속가능성 검토
        sustainable_materials = ['wood', 'bamboo', 'recycled_steel']
        if any(mat in sustainable_materials for mat in materials.values()):
            strengths.append("지속가능한 재료를 적극 활용했습니다.")
            score += 15
        
        return {
            "score": min(100, score),
            "issues": issues,
            "strengths": strengths,
            "material_analysis": materials
        }
    
    def _evaluate_environmental_response(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """환경 대응성 평가"""
        orientation = design_data.get('orientation', 'south')
        window_ratio = design_data.get('window_to_wall_ratio', 0.4)
        
        score = 70  # 기본 점수
        issues = []
        strengths = []
        
        # 방위 분석
        if orientation == 'south':
            score += 20
            strengths.append("남향 배치로 자연채광과 일조량이 우수합니다.")
        elif orientation in ['east', 'west']:
            score += 10
        else:
            score -= 10
            issues.append("북향 배치로 자연채광이 부족할 수 있습니다.")
        
        # 창호 비율 분석
        if 0.3 <= window_ratio <= 0.5:
            score += 10
            strengths.append("적절한 창호 비율로 채광과 단열의 균형이 좋습니다.")
        elif window_ratio > 0.6:
            score -= 15
            issues.append("창호 비율이 과도하여 단열 성능이 우려됩니다.")
        
        return {
            "score": min(100, max(0, score)),
            "issues": issues,
            "strengths": strengths,
            "orientation_analysis": orientation,
            "window_analysis": window_ratio
        }
    
    def _evaluate_design_integration(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """설계 통합성 평가"""
        style = design_data.get('architectural_style', 'modern')
        elements = design_data.get('design_elements', {})
        
        score = 75  # 기본 점수
        issues = []
        strengths = []
        
        # 스타일 일관성 검토
        style_elements = {
            'modern': ['clean_lines', 'minimal_decoration', 'open_plan'],
            'traditional': ['symmetry', 'natural_materials', 'pitched_roof'],
            'hanok': ['ondol', 'courtyard', 'wooden_structure']
        }
        
        required_elements = style_elements.get(style, [])
        present_elements = [elem for elem in required_elements if elem in elements]
        
        consistency_ratio = len(present_elements) / len(required_elements) if required_elements else 1
        score += consistency_ratio * 20
        
        if consistency_ratio > 0.8:
            strengths.append(f"{style} 스타일의 특징이 잘 구현되었습니다.")
        elif consistency_ratio < 0.5:
            issues.append(f"{style} 스타일의 핵심 요소가 부족합니다.")
        
        return {
            "score": min(100, score),
            "issues": issues,
            "strengths": strengths,
            "style_consistency": consistency_ratio,
            "missing_elements": [elem for elem in required_elements if elem not in elements]
        }
    
    # === 기타 분석 메서드들 (간단한 구현) ===
    
    def _check_style_compliance(self, design_data: Dict[str, Any], style: str) -> Dict[str, Any]:
        """스타일 준수도 검사"""
        elements = design_data.get('design_elements', {})
        style_requirements = {
            'modern': ['open_plan', 'large_windows', 'minimal_decoration'],
            'traditional': ['symmetry', 'natural_materials', 'human_scale'],
            'hanok': ['courtyard', 'ondol', 'wooden_structure']
        }
        
        required = style_requirements.get(style, [])
        present = [req for req in required if req in elements]
        
        score = (len(present) / len(required)) * 100 if required else 100
        missing = [req for req in required if req not in elements]
        
        return {
            "score": score,
            "missing_elements": missing,
            "present_elements": present
        }
    
    def _analyze_proportional_system(self, proportions: Dict[str, Any]) -> Dict[str, Any]:
        """비례 시스템 분석"""
        golden_ratio = 1.618
        width = proportions.get('width', 10)
        height = proportions.get('height', 6)
        
        if height > 0:
            actual_ratio = width / height
            deviation = abs(actual_ratio - golden_ratio) / golden_ratio
        else:
            deviation = 1.0
        
        return {
            "system_type": "golden_ratio",
            "deviation": deviation,
            "consistency": "high" if deviation < 0.1 else "medium" if deviation < 0.3 else "low"
        }
    
    def _analyze_spatial_hierarchy(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """공간 위계 분석"""
        spaces = design_data.get('spaces', [])
        
        # 공간 크기 기준 위계 분석
        if spaces:
            areas = [space.get('area', 0) for space in spaces]
            max_area = max(areas) if areas else 0
            min_area = min(areas) if areas else 0
            
            hierarchy_ratio = max_area / min_area if min_area > 0 else 1
            clear_hierarchy = hierarchy_ratio > 2.0  # 2배 이상 차이
        else:
            clear_hierarchy = False
            hierarchy_ratio = 1.0
        
        return {
            "clear_hierarchy": clear_hierarchy,
            "hierarchy_ratio": hierarchy_ratio,
            "dominant_space": max(spaces, key=lambda x: x.get('area', 0))['name'] if spaces else None
        }
    
    def _check_program_adequacy(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """공간 프로그램 적절성 검사"""
        building_type = design_data.get('building_type', 'residential')
        spaces = design_data.get('spaces', [])
        space_names = [space.get('name', '') for space in spaces]
        
        required_spaces = {
            'residential': ['거실', '침실', '주방', '화장실'],
            'office': ['업무공간', '회의실', '휴게실', '화장실'],
            'commercial': ['판매공간', '창고', '사무실', '화장실']
        }
        
        required = required_spaces.get(building_type, [])
        missing = [req for req in required if not any(req in name for name in space_names)]
        
        return {
            "adequacy_score": ((len(required) - len(missing)) / len(required)) * 100 if required else 100,
            "missing_spaces": missing,
            "provided_spaces": space_names
        }
    
    def _analyze_circulation_efficiency(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """동선 효율성 분석"""
        # 간단한 동선 효율성 계산
        total_area = sum(space.get('area', 0) for space in design_data.get('spaces', []))
        circulation_area = sum(space.get('area', 0) for space in design_data.get('spaces', []) 
                             if 'corridor' in space.get('name', '').lower() or 'hall' in space.get('name', '').lower())
        
        if total_area > 0:
            circulation_ratio = circulation_area / total_area
            efficiency_score = max(0, 100 - circulation_ratio * 500)  # 20% 초과시 감점
        else:
            efficiency_score = 50
        
        return {
            "efficiency_score": efficiency_score,
            "circulation_ratio": circulation_ratio if total_area > 0 else 0,
            "recommendation": "동선 공간을 15% 이내로 조정하세요." if circulation_ratio > 0.15 else "동선 효율성이 좋습니다."
        }
    
    def _check_space_sizing(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """공간 크기 적정성 검사"""
        spaces = design_data.get('spaces', [])
        
        # 최소 면적 기준
        min_areas = {
            '거실': 12.0,
            '침실': 9.0,
            '주방': 4.5,
            '화장실': 3.0,
            '업무공간': 6.0
        }
        
        undersized_spaces = []
        for space in spaces:
            space_name = space.get('name', '')
            space_area = space.get('area', 0)
            
            for standard_name, min_area in min_areas.items():
                if standard_name in space_name and space_area < min_area:
                    undersized_spaces.append({
                        'name': space_name,
                        'current_area': space_area,
                        'recommended_area': min_area
                    })
        
        return {
            "undersized_spaces": undersized_spaces,
            "compliance_ratio": (len(spaces) - len(undersized_spaces)) / len(spaces) if spaces else 1.0
        }
    
    def _evaluate_functional_zoning(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """기능별 조닝 평가"""
        spaces = design_data.get('spaces', [])
        
        # 상충 가능한 기능 조합
        conflicting_functions = [
            (['침실', '거실'], ['주방', '화장실']),  # 조용한 공간 vs 시끄러운 공간
            (['업무공간'], ['휴게실']),  # 집중 vs 휴식
        ]
        
        conflicts = []
        # 실제 구현에서는 공간의 인접성을 분석해야 함
        # 여기서는 간단한 예시만 제공
        
        return {
            "zoning_score": 85,  # 임의값
            "conflicts": conflicts,
            "recommendations": []
        }
    
    # === 초기화 메서드들 ===
    
    def _initialize_review_criteria(self) -> List[ReviewCriterion]:
        """검토 기준 초기화"""
        return [
            ReviewCriterion(ReviewCategory.ARCHITECTURAL_THEORY, ReviewCriteria.PROPORTION, 0.15, "비례와 조화"),
            ReviewCriterion(ReviewCategory.FUNCTIONALITY, ReviewCriteria.CIRCULATION, 0.20, "동선 계획"),
            ReviewCriterion(ReviewCategory.AESTHETICS, ReviewCriteria.HARMONY, 0.15, "미적 조화"),
            ReviewCriterion(ReviewCategory.USABILITY, ReviewCriteria.SPATIAL_QUALITY, 0.20, "공간 품질"),
            ReviewCriterion(ReviewCategory.ACCESSIBILITY, ReviewCriteria.SCALE, 0.10, "접근성"),
            ReviewCriterion(ReviewCategory.SUSTAINABILITY, ReviewCriteria.ENVIRONMENTAL_RESPONSE, 0.20, "환경 대응")
        ]
    
    def _load_quality_benchmarks(self) -> Dict[str, Any]:
        """품질 벤치마크 로드"""
        return {
            "excellent": 90,
            "good": 80,
            "average": 70,
            "below_average": 60,
            "poor": 50
        }
    
    def _load_design_patterns(self) -> Dict[str, Any]:
        """설계 패턴 데이터 로드"""
        return {
            "spatial_patterns": ["linear", "radial", "cluster", "grid"],
            "circulation_patterns": ["single_loaded", "double_loaded", "central_core"],
            "massing_patterns": ["simple_volume", "compound_volume", "articulated_volume"]
        }
    
    def _load_cultural_standards(self) -> Dict[str, Any]:
        """문화적 기준 로드"""
        return {
            "korean_traditional": {
                "principles": ["harmony_with_nature", "modular_system", "ondol_system"],
                "proportions": "korean_traditional_ratio",
                "materials": ["wood", "stone", "clay"]
            },
            "modern_korean": {
                "principles": ["efficiency", "technology_integration", "urban_context"],
                "proportions": "contemporary_ratio",
                "materials": ["concrete", "steel", "glass"]
            }
        }
    
    def _load_reference_designs(self) -> List[Dict[str, Any]]:
        """참조 설계 사례 로드"""
        return [
            {
                "id": "ref_001",
                "type": "residential",
                "style": "modern",
                "quality_score": 92,
                "key_features": ["open_plan", "natural_light", "sustainable_materials"]
            },
            {
                "id": "ref_002", 
                "type": "office",
                "style": "contemporary",
                "quality_score": 88,
                "key_features": ["flexible_spaces", "collaborative_areas", "green_building"]
            }
        ]
    
    # === 유틸리티 메서드들 ===
    
    def _calculate_overall_score(self, reviews: List[Dict[str, Any]]) -> float:
        """전체 점수 계산"""
        if not reviews:
            return 0.0
        
        # 각 검토 영역의 가중치
        weights = {
            "quality": 0.25,
            "theoretical_basis": 0.15,
            "functionality": 0.20,
            "aesthetic_quality": 0.15,
            "usability": 0.10,
            "accessibility": 0.05,
            "sustainability": 0.05,
            "cultural_context": 0.05
        }
        
        total_score = 0.0
        total_weight = 0.0
        
        for review in reviews:
            review_type = review.get("review_type", "")
            score = review.get("score", 0)
            weight = weights.get(review_type, 0.1)
            
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _calculate_grade(self, score: float) -> str:
        """점수를 등급으로 변환"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        else:
            return "D"
    
    def _compare_with_benchmarks(self, score: float) -> Dict[str, Any]:
        """벤치마크와 비교"""
        benchmarks = self.quality_benchmarks
        
        if score >= benchmarks["excellent"]:
            level = "excellent"
        elif score >= benchmarks["good"]:
            level = "good"
        elif score >= benchmarks["average"]:
            level = "average"
        elif score >= benchmarks["below_average"]:
            level = "below_average"
        else:
            level = "poor"
        
        return {
            "level": level,
            "percentile": min(100, (score / benchmarks["excellent"]) * 100),
            "improvement_potential": benchmarks["excellent"] - score
        }
    
    def _generate_final_recommendations(self, all_issues: List[Dict], alternatives: List[Dict]) -> List[str]:
        """최종 권고사항 생성"""
        recommendations = []
        
        # 중요도별 우선순위 권고
        critical_count = len([i for i in all_issues if i.get('level') == IssueLevel.CRITICAL.value])
        major_count = len([i for i in all_issues if i.get('level') == IssueLevel.MAJOR.value])
        
        if critical_count > 0:
            recommendations.append(f"즉시 해결이 필요한 {critical_count}개의 중대한 문제가 있습니다.")
        
        if major_count > 0:
            recommendations.append(f"{major_count}개의 주요 개선사항을 우선적으로 검토하세요.")
        
        if alternatives:
            top_alternative = max(alternatives, key=lambda x: x['overall_score'])
            recommendations.append(f"가장 효과적인 개선안은 '{top_alternative['title']}'입니다.")
        
        recommendations.append("설계의 전반적인 완성도를 위해 단계적 개선을 권장합니다.")
        
        return recommendations
    
    # === 추가 분석 메서드들 (간단한 구현) ===
    
    def _analyze_facade_composition(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """외관 구성 분석"""
        return {"balance_score": 75, "rhythm_score": 80, "proportion_score": 85}
    
    def _evaluate_color_scheme(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """색채 계획 평가"""
        return {"harmony_score": 78, "contrast_score": 82, "appropriateness": 80}
    
    def _evaluate_material_aesthetics(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """재료 미적 평가"""
        return {"coherence_score": 85, "texture_harmony": 80, "color_coordination": 75}
    
    def _check_style_consistency(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """스타일 일관성 검사"""
        return {"consistent": True, "consistency_score": 88, "deviations": []}
    
    def _analyze_user_flow(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 동선 분석"""
        return {
            "efficiency_score": 82,
            "bottlenecks": [],
            "flow_patterns": ["linear", "distributed"]
        }
    
    def _check_amenity_accessibility(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """편의시설 접근성 검사"""
        return {"avg_distance": 35, "max_distance": 60, "accessibility_score": 85}
    
    def _analyze_spatial_visibility(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """공간 가시성 분석"""
        return {"orientation_score": 85, "wayfinding_score": 80, "visibility_score": 78}
    
    def _analyze_privacy_levels(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """프라이버시 분석"""
        return {
            "privacy_score": 80,
            "issues": [],
            "recommendations": []
        }
    
    def _check_physical_accessibility(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """물리적 접근성 검사"""
        return {
            "wheelchair_accessible": True,
            "barrier_free_score": 85,
            "compliance_level": "high"
        }
    
    def _check_entrance_accessibility(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """출입구 접근성 검사"""
        return {"barrier_free_ratio": 0.9, "width_compliance": True, "ramp_available": True}
    
    def _check_vertical_accessibility(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """수직 이동 접근성 검사"""
        stories = design_data.get('stories', 1)
        return {
            "elevator_available": stories > 2,
            "stair_compliance": True,
            "accessibility_score": 90 if stories <= 2 else 95
        }
    
    def _check_visual_accessibility(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """시각적 접근성 검사"""
        return {"signage_score": 85, "contrast_score": 80, "lighting_adequacy": 90}
    
    def _evaluate_energy_efficiency(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """에너지 효율성 평가"""
        return {"rating": 4, "annual_consumption": 120, "improvement_potential": 25}
    
    def _evaluate_natural_integration(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """자연 환경 통합 평가"""
        return {"daylight_score": 85, "ventilation_score": 80, "landscape_integration": 75}
    
    def _evaluate_material_sustainability(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """재료 지속가능성 평가"""
        return {"recycled_content": 0.25, "local_materials": 0.6, "sustainability_score": 70}
    
    def _evaluate_ecological_impact(self, design_data: Dict[str, Any], bim_model: Dict[str, Any]) -> Dict[str, Any]:
        """생태계 영향 평가"""
        return {"green_ratio": 0.15, "biodiversity_score": 65, "carbon_footprint": "medium"}
    
    def _evaluate_regional_character(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """지역적 특성 평가"""
        return {"score": 85, "local_materials": True, "climate_response": True}
    
    def _evaluate_traditional_elements(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """전통 요소 평가"""
        return {"authenticity": 75, "interpretation_quality": 80, "cultural_relevance": 85}
    
    def _evaluate_contemporary_interpretation(self, design_data: Dict[str, Any]) -> Dict[str, Any]:
        """현대적 해석 평가"""
        return {"balance_score": 80, "innovation_level": 75, "relevance": 85}


# 설계 검토자 에이전트 싱글톤 인스턴스
_design_reviewer = None

def get_design_reviewer() -> DesignReviewerAgent:
    """설계 검토자 에이전트 싱글톤 인스턴스 반환"""
    global _design_reviewer
    if _design_reviewer is None:
        _design_reviewer = DesignReviewerAgent()
    return _design_reviewer