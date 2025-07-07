import asyncio
import json
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

class VIBAAIUIAutomation:
    """VIBA AI 시스템 UI 자동화 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.browser: Browser = None
        self.context: BrowserContext = None
        self.page: Page = None
        
    async def setup(self):
        """브라우저 설정 및 초기화"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=False)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
    async def cleanup(self):
        """리소스 정리"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
            
    async def login(self, email: str = "test@viba.ai", password: str = "password123"):
        """자동 로그인"""
        await self.page.goto(f"{self.base_url}/login")
        
        # 로그인 폼 작성
        await self.page.fill('input[type="email"]', email)
        await self.page.fill('input[type="password"]', password)
        await self.page.click('button[type="submit"]')
        
        # 대시보드 로딩 대기
        await self.page.wait_for_url(f"{self.base_url}/dashboard")
        print("✅ 로그인 완료")
        
    async def navigate_to_ai_agents(self):
        """AI 에이전트 페이지로 이동"""
        await self.page.click('text=AI 에이전트')
        await self.page.wait_for_url(f"{self.base_url}/ai-agents")
        print("🤖 AI 에이전트 페이지 이동 완료")
        
    async def test_ai_agent_chat(self, agent_name: str = "재료 전문가 AI"):
        """AI 에이전트 채팅 테스트"""
        # 특정 에이전트 선택
        await self.page.click(f'text={agent_name}')
        await self.page.click('text=AI와 대화하기')
        
        # 채팅 다이얼로그 대기
        await self.page.wait_for_selector('[role="dialog"]')
        
        # 메시지 입력 및 전송
        test_message = "친환경 건축 재료 추천해주세요"
        await self.page.fill('textarea[placeholder*="AI 에이전트에게"]', test_message)
        await self.page.click('button[aria-label="send"] svg')
        
        # AI 응답 대기
        await self.page.wait_for_selector('.MuiCircularProgress-root', state='hidden', timeout=10000)
        
        # 응답 확인
        responses = await self.page.query_selector_all('.MuiPaper-root:has-text("응답")')
        if responses:
            print(f"✅ AI 에이전트 채팅 테스트 완료: {len(responses)}개 응답 수신")
        else:
            print("❌ AI 응답을 받지 못했습니다")
            
        # 다이얼로그 닫기
        await self.page.click('button[aria-label="close"]')
        
    async def test_design_studio_workflow(self):
        """설계 스튜디오 워크플로우 테스트"""
        await self.page.click('text=설계 스튜디오')
        await self.page.wait_for_url(f"{self.base_url}/design-studio")
        
        # 1단계: 프로젝트 기본 정보 입력
        await self.page.fill('textarea[label="설계 요청 내용"]', 
                           "30평 규모의 친환경 주택 설계를 요청합니다. 태양광 패널과 우수 재활용 시스템을 포함해주세요.")
        
        await self.page.select_option('select', value='comprehensive')  # 종합 설계 분석
        await self.page.select_option('select', value='residential')     # 주거용
        await self.page.fill('input[label="위치"]', "서울시 강남구")
        
        # 다음 단계로
        await self.page.click('text=다음')
        
        # 2단계: 상세 요구사항
        await self.page.fill('input[label="면적"]', "100")
        await self.page.fill('input[label="층수"]', "2")
        await self.page.fill('input[label="예산"]', "500000000")
        
        # 특수 요구사항 선택
        await self.page.click('text=무장애 설계')
        await self.page.click('text=태양광 발전')
        await self.page.click('text=우수 재활용')
        
        # 다음 단계로
        await self.page.click('text=다음')
        
        # 3단계: AI 분석 실행
        await self.page.click('text=AI 분석 시작')
        
        # 분석 완료 대기 (최대 30초)
        await self.page.wait_for_selector('text=AI 분석이 완료되었습니다', timeout=30000)
        
        # 결과 확인
        results = await self.page.query_selector_all('.MuiAccordion-root')
        print(f"✅ 설계 스튜디오 테스트 완료: {len(results)}개 분석 결과 생성")
        
    async def test_3d_model_viewer(self):
        """3D 모델 뷰어 테스트"""
        await self.page.click('text=3D 뷰어')
        await self.page.wait_for_url(f"{self.base_url}/model-viewer")
        
        # 레이어 관리 테스트
        await self.page.click('text=레이어')
        await self.page.wait_for_selector('[role="dialog"]')
        
        # 레이어 가시성 토글
        layer_toggles = await self.page.query_selector_all('button[aria-label*="visibility"]')
        if layer_toggles:
            await layer_toggles[0].click()  # 첫 번째 레이어 토글
            
        await self.page.click('text=닫기')
        
        # 줌 컨트롤 테스트
        await self.page.click('button[aria-label*="zoom-in"]')
        await self.page.click('button[aria-label*="zoom-out"]')
        
        print("✅ 3D 모델 뷰어 테스트 완료")
        
    async def test_analytics_dashboard(self):
        """분석 대시보드 테스트"""
        await self.page.click('text=분석')
        await self.page.wait_for_url(f"{self.base_url}/analytics")
        
        # 탭 전환 테스트
        tabs = ['전체 개요', '프로젝트 분석', 'AI 성능', '트렌드 분석']
        for tab in tabs:
            await self.page.click(f'text={tab}')
            await asyncio.sleep(1)  # 로딩 대기
            
        # 기간 선택 테스트
        await self.page.select_option('select[label="기간"]', value='month')
        
        print("✅ 분석 대시보드 테스트 완료")
        
    async def test_collaboration_features(self):
        """협업 기능 테스트"""
        await self.page.click('text=협업')
        await self.page.wait_for_url(f"{self.base_url}/collaboration")
        
        # 멤버 초대 다이얼로그 테스트
        await self.page.click('text=멤버 초대')
        await self.page.wait_for_selector('[role="dialog"]')
        
        await self.page.fill('input[type="email"]', "newmember@viba.ai")
        await self.page.select_option('select', value='editor')
        await self.page.click('text=취소')  # 실제로는 초대하지 않음
        
        # 회의 시작 다이얼로그 테스트
        await self.page.click('text=회의 시작')
        await self.page.wait_for_selector('[role="dialog"]')
        await self.page.click('text=취소')
        
        print("✅ 협업 기능 테스트 완료")
        
    async def capture_screenshot(self, name: str):
        """스크린샷 캡처"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshots/{name}_{timestamp}.png"
        await self.page.screenshot(path=filename, full_page=True)
        print(f"📸 스크린샷 저장: {filename}")
        
    async def generate_test_report(self, results: dict):
        """테스트 리포트 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "test_results": results,
            "total_tests": len(results),
            "passed_tests": sum(1 for result in results.values() if result["status"] == "passed"),
            "failed_tests": sum(1 for result in results.values() if result["status"] == "failed")
        }
        
        with open(f"test_reports/ui_automation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"📊 테스트 리포트 생성 완료: {report['passed_tests']}/{report['total_tests']} 통과")
        
    async def run_full_test_suite(self):
        """전체 테스트 스위트 실행"""
        results = {}
        
        try:
            await self.setup()
            
            # 로그인 테스트
            try:
                await self.login()
                results["login"] = {"status": "passed", "message": "로그인 성공"}
            except Exception as e:
                results["login"] = {"status": "failed", "message": str(e)}
                
            # AI 에이전트 테스트
            try:
                await self.navigate_to_ai_agents()
                await self.test_ai_agent_chat()
                await self.capture_screenshot("ai_agents")
                results["ai_agents"] = {"status": "passed", "message": "AI 에이전트 테스트 성공"}
            except Exception as e:
                results["ai_agents"] = {"status": "failed", "message": str(e)}
                
            # 설계 스튜디오 테스트
            try:
                await self.test_design_studio_workflow()
                await self.capture_screenshot("design_studio")
                results["design_studio"] = {"status": "passed", "message": "설계 스튜디오 테스트 성공"}
            except Exception as e:
                results["design_studio"] = {"status": "failed", "message": str(e)}
                
            # 3D 뷰어 테스트
            try:
                await self.test_3d_model_viewer()
                await self.capture_screenshot("model_viewer")
                results["model_viewer"] = {"status": "passed", "message": "3D 뷰어 테스트 성공"}
            except Exception as e:
                results["model_viewer"] = {"status": "failed", "message": str(e)}
                
            # 분석 대시보드 테스트
            try:
                await self.test_analytics_dashboard()
                await self.capture_screenshot("analytics")
                results["analytics"] = {"status": "passed", "message": "분석 대시보드 테스트 성공"}
            except Exception as e:
                results["analytics"] = {"status": "failed", "message": str(e)}
                
            # 협업 기능 테스트
            try:
                await self.test_collaboration_features()
                await self.capture_screenshot("collaboration")
                results["collaboration"] = {"status": "passed", "message": "협업 기능 테스트 성공"}
            except Exception as e:
                results["collaboration"] = {"status": "failed", "message": str(e)}
                
        finally:
            await self.cleanup()
            await self.generate_test_report(results)
            
        return results

# 실행 스크립트
async def main():
    """메인 실행 함수"""
    automation = VIBAAIUIAutomation()
    results = await automation.run_full_test_suite()
    
    print("\n🎯 VIBA AI UI 자동화 테스트 완료!")
    for test_name, result in results.items():
        status_emoji = "✅" if result["status"] == "passed" else "❌"
        print(f"{status_emoji} {test_name}: {result['message']}")

if __name__ == "__main__":
    asyncio.run(main())