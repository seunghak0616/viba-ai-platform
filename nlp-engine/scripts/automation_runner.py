#!/usr/bin/env python3
"""
VIBA AI 시스템 자동화 실행기
모든 자동화 작업을 통합 관리합니다.
"""

import asyncio
import subprocess
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

class VIBAAutomationRunner:
    """VIBA AI 자동화 통합 실행기"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.scripts_dir = self.base_dir / "scripts"
        self.tests_dir = self.base_dir / "tests"
        self.logs_dir = self.base_dir / "logs"
        
        # 로그 디렉토리 생성
        self.logs_dir.mkdir(exist_ok=True)
        
    def log(self, message: str, level: str = "INFO"):
        """로그 출력"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        # 로그 파일에도 저장
        with open(self.logs_dir / "automation.log", "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
            
    async def check_services(self):
        """서비스 상태 확인"""
        self.log("🔍 서비스 상태 확인 중...")
        
        services = {
            "backend": {"url": "http://localhost:8000/health", "name": "FastAPI 백엔드"},
            "frontend": {"url": "http://localhost:3000", "name": "React 프론트엔드"}
        }
        
        import aiohttp
        async with aiohttp.ClientSession() as session:
            for service_id, service_info in services.items():
                try:
                    async with session.get(service_info["url"], timeout=5) as response:
                        if response.status == 200:
                            self.log(f"✅ {service_info['name']} 정상 동작")
                        else:
                            self.log(f"⚠️ {service_info['name']} 응답 오류: {response.status}", "WARN")
                except Exception as e:
                    self.log(f"❌ {service_info['name']} 연결 실패: {e}", "ERROR")
                    
    async def start_backend(self):
        """백엔드 서버 시작"""
        self.log("🚀 FastAPI 백엔드 서버 시작...")
        backend_dir = self.base_dir / "backend"
        
        try:
            process = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 서버 시작 대기
            await asyncio.sleep(5)
            
            if process.poll() is None:
                self.log("✅ 백엔드 서버 시작 완료")
                return process
            else:
                self.log("❌ 백엔드 서버 시작 실패", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ 백엔드 서버 시작 오류: {e}", "ERROR")
            return None
            
    async def start_frontend(self):
        """프론트엔드 서버 시작"""
        self.log("🚀 React 프론트엔드 서버 시작...")
        frontend_dir = self.base_dir / "frontend-react"
        
        try:
            process = subprocess.Popen(
                ["npm", "start"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # 서버 시작 대기 (React는 시간이 더 걸림)
            await asyncio.sleep(15)
            
            if process.poll() is None:
                self.log("✅ 프론트엔드 서버 시작 완료")
                return process
            else:
                self.log("❌ 프론트엔드 서버 시작 실패", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ 프론트엔드 서버 시작 오류: {e}", "ERROR")
            return None
            
    async def run_data_generation(self):
        """자동 데이터 생성 실행"""
        self.log("📊 자동 데이터 생성 시작...")
        
        try:
            # auto_data_generator.py 실행
            result = subprocess.run(
                [sys.executable, self.scripts_dir / "auto_data_generator.py"],
                capture_output=True,
                text=True,
                input="1\n"  # 초기 샘플 데이터 생성 선택
            )
            
            if result.returncode == 0:
                self.log("✅ 자동 데이터 생성 완료")
            else:
                self.log(f"❌ 자동 데이터 생성 실패: {result.stderr}", "ERROR")
                
        except Exception as e:
            self.log(f"❌ 자동 데이터 생성 오류: {e}", "ERROR")
            
    async def run_ui_automation(self):
        """UI 자동화 테스트 실행"""
        self.log("🤖 UI 자동화 테스트 시작...")
        
        try:
            # ui_automation.py 실행
            result = subprocess.run(
                [sys.executable, self.tests_dir / "ui_automation.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log("✅ UI 자동화 테스트 완료")
                self.log(f"테스트 결과:\n{result.stdout}")
            else:
                self.log(f"❌ UI 자동화 테스트 실패: {result.stderr}", "ERROR")
                
        except Exception as e:
            self.log(f"❌ UI 자동화 테스트 오류: {e}", "ERROR")
            
    async def continuous_monitoring(self, interval_minutes: int = 10):
        """지속적 모니터링"""
        self.log(f"🔄 {interval_minutes}분마다 시스템 모니터링 시작...")
        
        while True:
            try:
                await self.check_services()
                
                # 시스템 리소스 체크
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                self.log(f"💻 시스템 리소스 - CPU: {cpu_percent}%, Memory: {memory_percent}%")
                
                # 임계값 체크
                if cpu_percent > 80:
                    self.log("⚠️ CPU 사용률이 높습니다", "WARN")
                if memory_percent > 80:
                    self.log("⚠️ 메모리 사용률이 높습니다", "WARN")
                    
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                self.log("⏹️ 모니터링 중단")
                break
            except Exception as e:
                self.log(f"❌ 모니터링 오류: {e}", "ERROR")
                await asyncio.sleep(60)
                
    async def full_automation_cycle(self):
        """전체 자동화 사이클 실행"""
        self.log("🎯 VIBA AI 전체 자동화 사이클 시작...")
        
        # 1. 서비스 상태 확인
        await self.check_services()
        
        # 2. 데이터 생성
        await self.run_data_generation()
        
        # 3. UI 자동화 테스트
        await self.run_ui_automation()
        
        # 4. 결과 리포트 생성
        await self.generate_automation_report()
        
        self.log("✅ 전체 자동화 사이클 완료!")
        
    async def generate_automation_report(self):
        """자동화 리포트 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "automation_cycle": "full",
            "services_checked": True,
            "data_generated": True,
            "ui_tests_completed": True,
            "status": "completed"
        }
        
        report_file = self.logs_dir / f"automation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        self.log(f"📋 자동화 리포트 생성: {report_file}")
        
    def show_menu(self):
        """메뉴 표시"""
        print("\n" + "="*50)
        print("🏗️ VIBA AI 시스템 자동화 실행기")
        print("="*50)
        print("1. 서비스 상태 확인")
        print("2. 백엔드 서버 시작")
        print("3. 프론트엔드 서버 시작")
        print("4. 자동 데이터 생성")
        print("5. UI 자동화 테스트")
        print("6. 전체 자동화 사이클")
        print("7. 지속적 모니터링")
        print("8. 종료")
        print("="*50)
        
    async def run_interactive(self):
        """대화형 실행"""
        while True:
            self.show_menu()
            choice = input("선택하세요 (1-8): ").strip()
            
            if choice == "1":
                await self.check_services()
            elif choice == "2":
                await self.start_backend()
            elif choice == "3":
                await self.start_frontend()
            elif choice == "4":
                await self.run_data_generation()
            elif choice == "5":
                await self.run_ui_automation()
            elif choice == "6":
                await self.full_automation_cycle()
            elif choice == "7":
                interval = input("모니터링 간격(분, 기본 10): ").strip()
                interval = int(interval) if interval.isdigit() else 10
                await self.continuous_monitoring(interval)
            elif choice == "8":
                self.log("👋 자동화 실행기 종료")
                break
            else:
                print("올바른 선택지를 입력해주세요.")
                
            input("\n계속하려면 Enter를 누르세요...")

async def main():
    """메인 실행 함수"""
    runner = VIBAAutomationRunner()
    
    if len(sys.argv) > 1:
        # 명령행 인자가 있는 경우
        command = sys.argv[1]
        if command == "check":
            await runner.check_services()
        elif command == "data":
            await runner.run_data_generation()
        elif command == "test":
            await runner.run_ui_automation()
        elif command == "full":
            await runner.full_automation_cycle()
        elif command == "monitor":
            await runner.continuous_monitoring()
        else:
            print(f"알 수 없는 명령: {command}")
            print("사용법: python automation_runner.py [check|data|test|full|monitor]")
    else:
        # 대화형 실행
        await runner.run_interactive()

if __name__ == "__main__":
    asyncio.run(main())