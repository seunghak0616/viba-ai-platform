import asyncio
import aiohttp
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
import uuid

class VIBAAutoDataGenerator:
    """VIBA AI 시스템 자동 데이터 생성기"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.auth_token = None
        
    async def setup(self):
        """HTTP 세션 설정"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """리소스 정리"""
        if self.session:
            await self.session.close()
            
    async def login(self, email: str = "admin@viba.ai", password: str = "admin123"):
        """자동 로그인"""
        async with self.session.post(f"{self.base_url}/auth/login", json={
            "email": email,
            "password": password
        }) as response:
            if response.status == 200:
                data = await response.json()
                self.auth_token = data.get("access_token")
                print("✅ API 로그인 성공")
            else:
                print("❌ API 로그인 실패")
                
    def get_headers(self):
        """인증 헤더 반환"""
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
        
    async def create_sample_projects(self, count: int = 5):
        """샘플 프로젝트 생성"""
        project_templates = [
            {
                "name": "친환경 주택 설계",
                "description": "30평 규모의 친환경 주택 프로젝트입니다. 태양광 패널과 우수 재활용 시스템을 포함합니다.",
                "building_type": "residential",
                "location": "서울시 강남구",
                "area": 100,
                "floors": 2,
                "budget": 500000000
            },
            {
                "name": "상업용 빌딩 구조 설계",
                "description": "20층 규모의 오피스 빌딩 구조 설계 프로젝트입니다.",
                "building_type": "commercial", 
                "location": "서울시 중구",
                "area": 5000,
                "floors": 20,
                "budget": 15000000000
            },
            {
                "name": "카페 인테리어 디자인",
                "description": "자연 친화적 분위기의 카페 인테리어 설계입니다.",
                "building_type": "commercial",
                "location": "경기도 성남시",
                "area": 80,
                "floors": 1,
                "budget": 100000000
            },
            {
                "name": "아파트 단지 계획",
                "description": "500세대 규모의 친환경 아파트 단지 설계입니다.",
                "building_type": "residential",
                "location": "인천시 연수구",
                "area": 50000,
                "floors": 15,
                "budget": 50000000000
            },
            {
                "name": "공장 시설 설계",
                "description": "스마트 팩토리 개념을 적용한 제조업 시설 설계입니다.",
                "building_type": "industrial",
                "location": "경기도 화성시",
                "area": 10000,
                "floors": 3,
                "budget": 8000000000
            }
        ]
        
        created_projects = []
        for i in range(min(count, len(project_templates))):
            project_data = project_templates[i].copy()
            project_data["name"] += f" v{i+1}"
            
            async with self.session.post(
                f"{self.base_url}/api/projects",
                json=project_data,
                headers=self.get_headers()
            ) as response:
                if response.status == 200:
                    project = await response.json()
                    created_projects.append(project)
                    print(f"✅ 프로젝트 생성: {project_data['name']}")
                    
        return created_projects
        
    async def create_design_requests(self, project_ids: List[str]):
        """설계 요청 생성"""
        request_templates = [
            {
                "request_type": "comprehensive",
                "content": "종합적인 건축 설계 분석을 요청합니다. 구조적 안전성, 친환경성, 비용 효율성을 모두 고려해주세요.",
                "priority": "high"
            },
            {
                "request_type": "structural",
                "content": "건물의 구조적 안전성을 검토하고 최적화 방안을 제시해주세요.",
                "priority": "high"
            },
            {
                "request_type": "materials",
                "content": "친환경적이고 비용 효율적인 건축 재료를 추천해주세요.",
                "priority": "medium"
            },
            {
                "request_type": "cost",
                "content": "상세한 공사비 분석과 비용 절감 방안을 제시해주세요.",
                "priority": "medium"
            }
        ]
        
        for project_id in project_ids:
            for template in request_templates:
                request_data = template.copy()
                request_data["project_id"] = project_id
                
                async with self.session.post(
                    f"{self.base_url}/api/design-requests",
                    json=request_data,
                    headers=self.get_headers()
                ) as response:
                    if response.status == 200:
                        print(f"✅ 설계 요청 생성: {template['request_type']}")
                        
    async def simulate_ai_agent_activity(self):
        """AI 에이전트 활동 시뮬레이션"""
        agents = [
            "materials_specialist",
            "design_theorist", 
            "bim_specialist",
            "structural_engineer",
            "mep_specialist",
            "cost_estimator",
            "schedule_manager",
            "interior_designer"
        ]
        
        activities = []
        for agent in agents:
            # 랜덤한 활동 데이터 생성
            activity_count = random.randint(10, 50)
            accuracy = random.uniform(85, 98)
            satisfaction = random.uniform(4.0, 5.0)
            
            activity = {
                "agent_id": agent,
                "usage_count": activity_count,
                "accuracy_score": round(accuracy, 1),
                "satisfaction_score": round(satisfaction, 1),
                "response_time_avg": random.uniform(1.0, 5.0),
                "date": datetime.now().isoformat()
            }
            activities.append(activity)
            
        return activities
        
    async def generate_analytics_data(self):
        """분석 데이터 생성"""
        # 프로젝트 성과 데이터
        project_metrics = []
        for i in range(10):
            metric = {
                "date": (datetime.now() - timedelta(days=i)).isoformat(),
                "active_projects": random.randint(8, 15),
                "completed_projects": random.randint(2, 5),
                "ai_usage_count": random.randint(100, 300),
                "cost_savings": random.randint(1000000, 5000000),
                "efficiency_score": random.uniform(80, 95),
                "sustainability_score": random.uniform(7.0, 9.5)
            }
            project_metrics.append(metric)
            
        # AI 에이전트 성과 데이터
        agent_metrics = await self.simulate_ai_agent_activity()
        
        return {
            "project_metrics": project_metrics,
            "agent_metrics": agent_metrics,
            "generated_at": datetime.now().isoformat()
        }
        
    async def create_collaboration_data(self, project_ids: List[str]):
        """협업 데이터 생성"""
        team_members = [
            {"name": "김건축", "role": "프로젝트 매니저", "email": "kim@viba.ai"},
            {"name": "이구조", "role": "구조 엔지니어", "email": "lee@viba.ai"},
            {"name": "박디자인", "role": "인테리어 디자이너", "email": "park@viba.ai"},
            {"name": "정AI", "role": "AI 전문가", "email": "jung@viba.ai"},
            {"name": "최예산", "role": "비용 관리자", "email": "choi@viba.ai"}
        ]
        
        # 팀 멤버별 활동 기록 생성
        activities = []
        for project_id in project_ids:
            for member in team_members:
                activity_types = ["comment", "update", "file_upload", "meeting", "ai_analysis"]
                for _ in range(random.randint(3, 8)):
                    activity = {
                        "project_id": project_id,
                        "user_name": member["name"],
                        "user_role": member["role"],
                        "activity_type": random.choice(activity_types),
                        "description": f"{member['name']}이(가) 프로젝트에 기여했습니다.",
                        "timestamp": (datetime.now() - timedelta(
                            hours=random.randint(1, 72)
                        )).isoformat()
                    }
                    activities.append(activity)
                    
        return {
            "team_members": team_members,
            "activities": activities
        }
        
    async def populate_sample_data(self):
        """전체 샘플 데이터 생성"""
        print("🚀 VIBA AI 시스템 샘플 데이터 생성 시작...")
        
        # 1. 프로젝트 생성
        projects = await self.create_sample_projects(5)
        project_ids = [p.get("id", str(uuid.uuid4())) for p in projects]
        
        # 2. 설계 요청 생성
        await self.create_design_requests(project_ids)
        
        # 3. 분석 데이터 생성
        analytics_data = await self.generate_analytics_data()
        with open("sample_data/analytics_data.json", "w", encoding="utf-8") as f:
            json.dump(analytics_data, f, indent=2, ensure_ascii=False)
            
        # 4. 협업 데이터 생성
        collaboration_data = await self.create_collaboration_data(project_ids)
        with open("sample_data/collaboration_data.json", "w", encoding="utf-8") as f:
            json.dump(collaboration_data, f, indent=2, ensure_ascii=False)
            
        print("✅ 샘플 데이터 생성 완료!")
        
    async def continuous_data_generation(self, interval_minutes: int = 30):
        """지속적인 데이터 생성"""
        print(f"🔄 {interval_minutes}분마다 새 데이터 생성 시작...")
        
        while True:
            try:
                # 새로운 AI 활동 데이터 생성
                activity_data = await self.simulate_ai_agent_activity()
                
                # 파일에 저장
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                with open(f"sample_data/ai_activity_{timestamp}.json", "w", encoding="utf-8") as f:
                    json.dump(activity_data, f, indent=2, ensure_ascii=False)
                    
                print(f"📊 새 AI 활동 데이터 생성: {timestamp}")
                
                # 대기
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                print("\n⏹️ 지속적 데이터 생성 중단")
                break
            except Exception as e:
                print(f"❌ 데이터 생성 오류: {e}")
                await asyncio.sleep(60)  # 1분 대기 후 재시도

# CLI 인터페이스
async def main():
    """메인 실행 함수"""
    generator = VIBAAutoDataGenerator()
    
    try:
        await generator.setup()
        await generator.login()
        
        print("1. 초기 샘플 데이터 생성")
        print("2. 지속적 데이터 생성 (30분 간격)")
        print("3. 분석 데이터만 생성")
        
        choice = input("선택하세요 (1-3): ")
        
        if choice == "1":
            await generator.populate_sample_data()
        elif choice == "2":
            await generator.continuous_data_generation()
        elif choice == "3":
            data = await generator.generate_analytics_data()
            print(f"📊 분석 데이터 생성 완료: {len(data['project_metrics'])}개 프로젝트 지표")
        else:
            print("올바른 선택지를 입력해주세요.")
            
    finally:
        await generator.cleanup()

if __name__ == "__main__":
    asyncio.run(main())