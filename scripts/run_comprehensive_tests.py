#!/usr/bin/env python3
"""
VIBA AI 종합 테스트 실행 스크립트
==============================

전체 AI 시스템의 단위, 통합, 성능, E2E 테스트를 순차적으로 실행하고
종합 리포트를 생성하는 스크립트

@version 1.0
@author VIBA AI Team
@date 2025.07.06
"""

import os
import sys
import subprocess
import json
import time
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# 프로젝트 루트 디렉토리 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from nlp_engine.src.utils.logger import setup_logger

logger = setup_logger(__name__)


class TestResult:
    """테스트 결과 데이터 클래스"""
    
    def __init__(self, test_name: str, test_type: str):
        self.test_name = test_name
        self.test_type = test_type
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
        self.status = "running"
        self.exit_code: Optional[int] = None
        self.stdout = ""
        self.stderr = ""
        self.metrics: Dict[str, Any] = {}
        
    def complete(self, exit_code: int, stdout: str = "", stderr: str = ""):
        """테스트 완료 처리"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.status = "passed" if exit_code == 0 else "failed"
        
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'test_name': self.test_name,
            'test_type': self.test_type,
            'status': self.status,
            'duration': self.duration,
            'exit_code': self.exit_code,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'metrics': self.metrics
        }


class VIBATestRunner:
    """VIBA AI 종합 테스트 실행기"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.project_root = project_root
        self.test_results: List[TestResult] = []
        self.start_time = time.time()
        
        # 결과 디렉토리 생성
        self.results_dir = self.project_root / "test-results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.results_dir / f"session_{self.timestamp}"
        self.session_dir.mkdir(exist_ok=True)
        
        logger.info(f"테스트 세션 시작: {self.session_dir}")
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None) -> TestResult:
        """명령어 실행 및 결과 수집"""
        test_name = " ".join(command)
        result = TestResult(test_name, "command")
        
        logger.info(f"🔄 실행 중: {test_name}")
        
        try:
            # 환경 변수 설정
            test_env = os.environ.copy()
            if env:
                test_env.update(env)
            
            # 명령어 실행
            process = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                env=test_env,
                timeout=self.config.get('test_timeout', 600)  # 10분 기본 타임아웃
            )
            
            result.complete(process.returncode, process.stdout, process.stderr)
            
            if result.status == "passed":
                logger.info(f"✅ 성공: {test_name} ({result.duration:.2f}초)")
            else:
                logger.error(f"❌ 실패: {test_name} ({result.duration:.2f}초)")
                logger.error(f"Error output: {process.stderr}")
                
        except subprocess.TimeoutExpired:
            result.complete(124, "", "Test timed out")
            logger.error(f"⏰ 타임아웃: {test_name}")
        except Exception as e:
            result.complete(1, "", str(e))
            logger.error(f"💥 예외 발생: {test_name} - {e}")
        
        self.test_results.append(result)
        return result
    
    def run_unit_tests(self) -> Dict[str, TestResult]:
        """단위 테스트 실행"""
        logger.info("🧪 단위 테스트 실행 시작...")
        
        unit_tests = {}
        
        # Python 단위 테스트
        python_tests = [
            "nlp_engine_tests.py",
            "theory_application_tests.py", 
            "bim_generation_tests.py",
            "performance_analysis_tests.py"
        ]
        
        for test_file in python_tests:
            test_name = f"unit_{test_file.replace('.py', '')}"
            result = self.run_command([
                "python", "-m", "pytest", 
                f"tests/unit/{test_file}",
                "-v", "--tb=short",
                f"--junitxml={self.session_dir}/junit_{test_name}.xml",
                f"--cov-report=xml:{self.session_dir}/coverage_{test_name}.xml"
            ])
            unit_tests[test_name] = result
        
        # TypeScript 단위 테스트 (Frontend)
        frontend_result = self.run_command([
            "npm", "run", "test:unit:frontend"
        ], cwd=self.project_root / "frontend")
        unit_tests["unit_frontend"] = frontend_result
        
        # TypeScript 단위 테스트 (Backend)
        backend_result = self.run_command([
            "npm", "run", "test:unit:backend"
        ], cwd=self.project_root / "backend")
        unit_tests["unit_backend"] = backend_result
        
        return unit_tests
    
    def run_integration_tests(self) -> Dict[str, TestResult]:
        """통합 테스트 실행"""
        logger.info("🔗 통합 테스트 실행 시작...")
        
        integration_tests = {}
        
        # 다중 에이전트 통합 테스트
        multi_agent_result = self.run_command([
            "python", "-m", "pytest",
            "tests/integration/multi_agent_integration_tests.py",
            "-v", "--tb=short",
            f"--junitxml={self.session_dir}/junit_integration_multi_agent.xml"
        ])
        integration_tests["multi_agent"] = multi_agent_result
        
        # MCP 통합 테스트
        mcp_result = self.run_command([
            "python", "-m", "pytest",
            "tests/mcp/mcp_integration_tests.py", 
            "-v", "--tb=short",
            f"--junitxml={self.session_dir}/junit_integration_mcp.xml"
        ], env={"TEST_MODE": "true"})
        integration_tests["mcp"] = mcp_result
        
        # API 통합 테스트
        api_result = self.run_command([
            "npm", "run", "test:integration:api"
        ], cwd=self.project_root / "backend")
        integration_tests["api"] = api_result
        
        return integration_tests
    
    def run_performance_tests(self) -> Dict[str, TestResult]:
        """성능 테스트 실행"""
        logger.info("🚀 성능 테스트 실행 시작...")
        
        performance_tests = {}
        
        # AI 모델 성능 테스트
        ai_performance_result = self.run_command([
            "python", "nlp-engine/tests/performance/model_performance_test.py"
        ])
        performance_tests["ai_models"] = ai_performance_result
        
        # API 부하 테스트 (K6가 설치된 경우)
        if self._check_k6_installed():
            api_load_result = self.run_command([
                "k6", "run", "tests/performance/api_load_test.js"
            ])
            performance_tests["api_load"] = api_load_result
        else:
            logger.warning("K6가 설치되지 않아 API 부하 테스트를 건너뜁니다")
        
        return performance_tests
    
    def run_e2e_tests(self) -> Dict[str, TestResult]:
        """E2E 테스트 실행"""
        logger.info("🎭 E2E 테스트 실행 시작...")
        
        e2e_tests = {}
        
        # Playwright E2E 테스트
        if self._check_playwright_installed():
            e2e_result = self.run_command([
                "npx", "playwright", "test", "tests/e2e/",
                "--reporter=json",
                f"--output={self.session_dir}/playwright-results/"
            ], cwd=self.project_root / "frontend")
            e2e_tests["playwright"] = e2e_result
        else:
            logger.warning("Playwright가 설치되지 않아 E2E 테스트를 건너뜁니다")
        
        return e2e_tests
    
    def run_security_tests(self) -> Dict[str, TestResult]:
        """보안 테스트 실행"""
        logger.info("🛡️ 보안 테스트 실행 시작...")
        
        security_tests = {}
        
        # npm audit
        npm_audit_result = self.run_command([
            "npm", "audit", "--audit-level", "high"
        ])
        security_tests["npm_audit"] = npm_audit_result
        
        # Python 보안 스캔 (bandit)
        bandit_result = self.run_command([
            "bandit", "-r", "nlp-engine/src/", 
            "-f", "json", "-o", f"{self.session_dir}/bandit_report.json"
        ])
        security_tests["bandit"] = bandit_result
        
        return security_tests
    
    def run_code_quality_tests(self) -> Dict[str, TestResult]:
        """코드 품질 테스트 실행"""
        logger.info("🎯 코드 품질 테스트 실행 시작...")
        
        quality_tests = {}
        
        # Python 코드 품질
        python_lint_result = self.run_command([
            "npm", "run", "lint:python:check"
        ])
        quality_tests["python_lint"] = python_lint_result
        
        # TypeScript 코드 품질
        typescript_lint_result = self.run_command([
            "npm", "run", "lint:check"
        ])
        quality_tests["typescript_lint"] = typescript_lint_result
        
        # 타입 체크
        type_check_result = self.run_command([
            "npm", "run", "type-check"
        ])
        quality_tests["type_check"] = type_check_result
        
        return quality_tests
    
    def _check_k6_installed(self) -> bool:
        """K6 설치 여부 확인"""
        try:
            subprocess.run(["k6", "version"], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_playwright_installed(self) -> bool:
        """Playwright 설치 여부 확인"""
        try:
            result = subprocess.run(
                ["npx", "playwright", "--version"], 
                capture_output=True, 
                cwd=self.project_root / "frontend"
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """종합 테스트 리포트 생성"""
        logger.info("📊 종합 테스트 리포트 생성 중...")
        
        total_duration = time.time() - self.start_time
        
        # 결과 통계 계산
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == "passed")
        failed_tests = sum(1 for r in self.test_results if r.status == "failed")
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # 테스트 타입별 분류
        results_by_type = {}
        for result in self.test_results:
            test_type = result.test_type
            if test_type not in results_by_type:
                results_by_type[test_type] = []
            results_by_type[test_type].append(result.to_dict())
        
        # 종합 리포트
        comprehensive_report = {
            "execution_summary": {
                "timestamp": self.timestamp,
                "total_duration": total_duration,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "test_coverage": "계산 중...",  # 별도 스크립트에서 계산
            },
            "test_results_by_type": results_by_type,
            "detailed_results": [r.to_dict() for r in self.test_results],
            "environment_info": {
                "python_version": sys.version,
                "node_version": self._get_node_version(),
                "platform": sys.platform,
                "test_session_id": self.timestamp
            },
            "recommendations": self._generate_recommendations()
        }
        
        # JSON 리포트 저장
        report_file = self.session_dir / "comprehensive_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, indent=2, ensure_ascii=False)
        
        # HTML 리포트 생성
        self._generate_html_report(comprehensive_report)
        
        logger.info(f"📋 리포트 저장 완료: {report_file}")
        
        return comprehensive_report
    
    def _get_node_version(self) -> str:
        """Node.js 버전 확인"""
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except FileNotFoundError:
            return "Not installed"
    
    def _generate_recommendations(self) -> List[str]:
        """테스트 결과 기반 개선 권장사항 생성"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r.status == "failed"]
        
        if failed_tests:
            recommendations.append(f"{len(failed_tests)}개의 실패한 테스트를 수정해야 합니다")
        
        slow_tests = [r for r in self.test_results if r.duration and r.duration > 30]
        if slow_tests:
            recommendations.append(f"{len(slow_tests)}개의 느린 테스트 (>30초) 성능 최적화가 필요합니다")
        
        success_rate = len([r for r in self.test_results if r.status == "passed"]) / len(self.test_results) * 100
        if success_rate < 95:
            recommendations.append("전체 성공률이 95% 미만입니다. 품질 개선이 필요합니다")
        
        return recommendations
    
    def _generate_html_report(self, report_data: Dict[str, Any]):
        """HTML 리포트 생성"""
        html_template = """
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VIBA AI 종합 테스트 리포트</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }
                .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; margin-bottom: 30px; }
                .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
                .metric { background: #ecf0f1; padding: 20px; border-radius: 8px; text-align: center; }
                .metric h3 { margin: 0 0 10px 0; color: #34495e; }
                .metric .value { font-size: 2em; font-weight: bold; color: #2980b9; }
                .success { color: #27ae60; }
                .warning { color: #f39c12; }
                .error { color: #e74c3c; }
                .test-results { margin-top: 30px; }
                .test-group { margin-bottom: 25px; border: 1px solid #ddd; border-radius: 5px; }
                .test-group h3 { background: #34495e; color: white; margin: 0; padding: 15px; }
                .test-item { padding: 10px 15px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
                .test-item:last-child { border-bottom: none; }
                .status-badge { padding: 4px 8px; border-radius: 4px; color: white; font-size: 12px; font-weight: bold; }
                .passed { background: #27ae60; }
                .failed { background: #e74c3c; }
                .duration { color: #7f8c8d; font-size: 14px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🤖 VIBA AI 종합 테스트 리포트</h1>
                
                <div class="summary">
                    <div class="metric">
                        <h3>총 테스트</h3>
                        <div class="value">{total_tests}</div>
                    </div>
                    <div class="metric">
                        <h3>성공</h3>
                        <div class="value success">{passed}</div>
                    </div>
                    <div class="metric">
                        <h3>실패</h3>
                        <div class="value error">{failed}</div>
                    </div>
                    <div class="metric">
                        <h3>성공률</h3>
                        <div class="value">{success_rate}</div>
                    </div>
                    <div class="metric">
                        <h3>실행 시간</h3>
                        <div class="value">{duration:.1f}분</div>
                    </div>
                </div>
                
                <div class="test-results">
                    {test_results_html}
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background: #f8f9fa; border-radius: 5px;">
                    <h3>개선 권장사항</h3>
                    <ul>
                        {recommendations_html}
                    </ul>
                </div>
                
                <div style="margin-top: 20px; text-align: center; color: #7f8c8d; font-size: 14px;">
                    생성 시간: {timestamp} | VIBA AI Platform
                </div>
            </div>
        </body>
        </html>
        """
        
        # 테스트 결과 HTML 생성
        test_results_html = ""
        for test_type, results in report_data["test_results_by_type"].items():
            test_results_html += f'<div class="test-group"><h3>{test_type.upper()} 테스트</h3>'
            for result in results:
                status_class = "passed" if result["status"] == "passed" else "failed"
                duration_text = f"{result['duration']:.2f}초" if result['duration'] else "N/A"
                test_results_html += f'''
                <div class="test-item">
                    <span>{result["test_name"]}</span>
                    <div>
                        <span class="status-badge {status_class}">{result["status"].upper()}</span>
                        <span class="duration">{duration_text}</span>
                    </div>
                </div>
                '''
            test_results_html += "</div>"
        
        # 권장사항 HTML 생성
        recommendations_html = ""
        for rec in report_data["recommendations"]:
            recommendations_html += f"<li>{rec}</li>"
        
        # HTML 생성
        html_content = html_template.format(
            total_tests=report_data["execution_summary"]["total_tests"],
            passed=report_data["execution_summary"]["passed"],
            failed=report_data["execution_summary"]["failed"],
            success_rate=report_data["execution_summary"]["success_rate"],
            duration=report_data["execution_summary"]["total_duration"] / 60,
            test_results_html=test_results_html,
            recommendations_html=recommendations_html,
            timestamp=report_data["execution_summary"]["timestamp"]
        )
        
        # HTML 파일 저장
        html_file = self.session_dir / "comprehensive_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"🌐 HTML 리포트 생성 완료: {html_file}")
    
    def run_all_tests(self, test_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("🚀 VIBA AI 종합 테스트 시작...")
        
        all_test_types = ["unit", "integration", "performance", "e2e", "security", "quality"]
        selected_types = test_types or all_test_types
        
        test_results = {}
        
        if "unit" in selected_types:
            test_results["unit"] = self.run_unit_tests()
        
        if "integration" in selected_types:
            test_results["integration"] = self.run_integration_tests()
        
        if "performance" in selected_types:
            test_results["performance"] = self.run_performance_tests()
        
        if "e2e" in selected_types:
            test_results["e2e"] = self.run_e2e_tests()
        
        if "security" in selected_types:
            test_results["security"] = self.run_security_tests()
        
        if "quality" in selected_types:
            test_results["quality"] = self.run_code_quality_tests()
        
        # 종합 리포트 생성
        comprehensive_report = self.generate_comprehensive_report()
        
        logger.info("✅ 모든 테스트 완료!")
        
        return comprehensive_report


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="VIBA AI 종합 테스트 실행")
    parser.add_argument(
        "--types", 
        nargs="*", 
        choices=["unit", "integration", "performance", "e2e", "security", "quality"],
        help="실행할 테스트 타입 (기본값: 모든 테스트)"
    )
    parser.add_argument("--timeout", type=int, default=600, help="테스트 타임아웃 (초)")
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그 출력")
    
    args = parser.parse_args()
    
    # 로깅 레벨 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 테스트 설정
    config = {
        "test_timeout": args.timeout
    }
    
    # 테스트 실행
    runner = VIBATestRunner(config)
    report = runner.run_all_tests(args.types)
    
    # 결과 출력
    print("\n" + "="*60)
    print("🤖 VIBA AI 종합 테스트 결과")
    print("="*60)
    print(f"총 테스트: {report['execution_summary']['total_tests']}")
    print(f"성공: {report['execution_summary']['passed']}")
    print(f"실패: {report['execution_summary']['failed']}")
    print(f"성공률: {report['execution_summary']['success_rate']}")
    print(f"실행 시간: {report['execution_summary']['total_duration']:.2f}초")
    print(f"리포트: {runner.session_dir}/comprehensive_report.html")
    
    # 실패한 테스트가 있으면 종료 코드 1
    if report['execution_summary']['failed'] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()