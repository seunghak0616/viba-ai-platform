#!/usr/bin/env python3
"""
파일 업로드 및 BIM 처리 시스템 통합 테스트
===========================================

전체 파일 처리 워크플로우를 테스트하여 시스템이 올바르게 작동하는지 확인합니다.

@version 1.0
@author VIBA AI Team
@date 2025.07.07
"""

import asyncio
import requests
import json
import time
from pathlib import Path
import io

# 테스트 설정
BASE_URL = "http://localhost:8000"
TEST_PROJECT_ID = "test-project-001"
TEST_USER_TOKEN = None

class FileSystemTester:
    """파일 시스템 테스트 클래스"""
    
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        
    def log(self, message: str, level: str = "INFO"):
        """로깅"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def authenticate(self):
        """사용자 인증"""
        self.log("사용자 인증 중...")
        
        # 로그인
        login_data = {
            "username": "architect",
            "password": "password123"
        }
        
        try:
            response = self.session.post(f"{BASE_URL}/auth/login", json=login_data)
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data["access_token"]
                self.session.headers.update({
                    "Authorization": f"Bearer {self.auth_token}"
                })
                self.log("✅ 인증 성공")
                return True
            else:
                self.log(f"❌ 인증 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 인증 오류: {e}", "ERROR")
            return False
            
    def test_health_check(self):
        """헬스 체크 테스트"""
        self.log("파일 서비스 헬스 체크...")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/files/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 파일 서비스 상태: {data['status']}")
                return True
            else:
                self.log(f"❌ 헬스 체크 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 헬스 체크 오류: {e}", "ERROR")
            return False
            
    def test_file_types(self):
        """지원 파일 타입 조회 테스트"""
        self.log("지원 파일 타입 조회...")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/files/types")
            if response.status_code == 200:
                data = response.json()
                file_types = data["file_types"]
                self.log(f"✅ 지원 파일 타입: {len(file_types)}개")
                for file_type, info in file_types.items():
                    self.log(f"   - {file_type}: {info['extensions']}")
                return True
            else:
                self.log(f"❌ 파일 타입 조회 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 파일 타입 조회 오류: {e}", "ERROR")
            return False
            
    def create_test_file(self, filename: str, content: str) -> io.BytesIO:
        """테스트 파일 생성"""
        file_content = io.BytesIO(content.encode('utf-8'))
        file_content.name = filename
        return file_content
        
    def test_file_upload(self):
        """파일 업로드 테스트"""
        self.log("파일 업로드 테스트...")
        
        # 테스트 파일들
        test_files = [
            ("test_drawing.ifc", "IFC 4.0 테스트 파일 내용..."),
            ("test_plan.pdf", "PDF 테스트 파일 내용..."),
            ("test_image.jpg", "JPEG 이미지 테스트 파일 내용...")
        ]
        
        uploaded_files = []
        
        for filename, content in test_files:
            try:
                # 파일 생성
                file_content = self.create_test_file(filename, content)
                
                # 업로드 요청
                files = {"file": (filename, file_content, "application/octet-stream")}
                response = self.session.post(
                    f"{BASE_URL}/api/files/upload/{TEST_PROJECT_ID}",
                    files=files
                )
                
                if response.status_code == 200:
                    data = response.json()
                    file_id = data["file_id"]
                    uploaded_files.append({
                        "file_id": file_id,
                        "filename": filename,
                        "file_type": data["file_type"]
                    })
                    self.log(f"✅ {filename} 업로드 성공 (ID: {file_id[:8]}...)")
                else:
                    self.log(f"❌ {filename} 업로드 실패: {response.status_code}", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {filename} 업로드 오류: {e}", "ERROR")
                
        return uploaded_files
        
    def test_file_processing_status(self, file_id: str):
        """파일 처리 상태 확인"""
        self.log(f"파일 처리 상태 확인: {file_id[:8]}...")
        
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            try:
                response = self.session.get(f"{BASE_URL}/api/files/status/{file_id}")
                if response.status_code == 200:
                    data = response.json()
                    status = data["status"]
                    progress = data.get("progress", 0)
                    
                    self.log(f"   상태: {status} ({progress}%)")
                    
                    if status == "completed":
                        self.log("✅ 파일 처리 완료")
                        return True
                    elif status == "failed":
                        error = data.get("error", "알 수 없는 오류")
                        self.log(f"❌ 파일 처리 실패: {error}", "ERROR")
                        return False
                    else:
                        time.sleep(2)  # 2초 대기
                        attempt += 1
                        
                else:
                    self.log(f"❌ 상태 확인 실패: {response.status_code}", "ERROR")
                    return False
                    
            except Exception as e:
                self.log(f"❌ 상태 확인 오류: {e}", "ERROR")
                return False
                
        self.log("❌ 파일 처리 시간 초과", "ERROR")
        return False
        
    def test_bim_analysis(self, file_id: str, file_type: str):
        """BIM 분석 테스트"""
        if file_type != "ifc":
            self.log("BIM 분석은 IFC 파일만 가능")
            return True
            
        self.log(f"BIM 분석 테스트: {file_id[:8]}...")
        
        try:
            response = self.session.post(f"{BASE_URL}/api/files/analyze/bim/{file_id}")
            if response.status_code == 200:
                data = response.json()
                bim_data = data["bim_data"]
                analysis_results = data["analysis_results"]
                
                self.log("✅ BIM 분석 완료")
                self.log(f"   건물 정보: {bim_data['building_info']}")
                self.log(f"   요소 수: {sum(bim_data['elements'].values())}개")
                self.log(f"   분석 결과: {len(analysis_results)}개 영역")
                return True
            else:
                self.log(f"❌ BIM 분석 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ BIM 분석 오류: {e}", "ERROR")
            return False
            
    def test_project_files(self):
        """프로젝트 파일 목록 조회"""
        self.log("프로젝트 파일 목록 조회...")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/files/project/{TEST_PROJECT_ID}")
            if response.status_code == 200:
                data = response.json()
                files = data["files"]
                self.log(f"✅ 프로젝트 파일: {len(files)}개")
                for file_info in files:
                    self.log(f"   - {file_info['original_name']} ({file_info['status']})")
                return True
            else:
                self.log(f"❌ 프로젝트 파일 조회 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 프로젝트 파일 조회 오류: {e}", "ERROR")
            return False
            
    def test_file_download(self, file_id: str, filename: str):
        """파일 다운로드 테스트"""
        self.log(f"파일 다운로드 테스트: {filename}")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/files/download/{file_id}")
            if response.status_code == 200:
                content_length = len(response.content)
                self.log(f"✅ {filename} 다운로드 성공 ({content_length} bytes)")
                return True
            else:
                self.log(f"❌ {filename} 다운로드 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ {filename} 다운로드 오류: {e}", "ERROR")
            return False
            
    def test_file_statistics(self):
        """파일 통계 조회"""
        self.log("파일 통계 조회...")
        
        try:
            response = self.session.get(f"{BASE_URL}/api/files/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data["statistics"]
                self.log("✅ 파일 통계:")
                self.log(f"   전체 파일: {stats['total_files']}개")
                self.log(f"   완료: {stats['completed']}개")
                self.log(f"   처리 중: {stats['processing']}개")
                self.log(f"   대기 중: {stats['pending']}개")
                self.log(f"   실패: {stats['failed']}개")
                return True
            else:
                self.log(f"❌ 파일 통계 조회 실패: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ 파일 통계 조회 오류: {e}", "ERROR")
            return False
            
    def run_full_test_suite(self):
        """전체 테스트 스위트 실행"""
        self.log("=== 파일 업로드 및 BIM 처리 시스템 테스트 시작 ===")
        
        test_results = []
        
        # 1. 인증 테스트
        test_results.append(("인증", self.authenticate()))
        
        if not self.auth_token:
            self.log("❌ 인증 실패로 테스트 중단", "ERROR")
            return False
            
        # 2. 헬스 체크
        test_results.append(("헬스체크", self.test_health_check()))
        
        # 3. 파일 타입 조회
        test_results.append(("파일타입", self.test_file_types()))
        
        # 4. 파일 업로드
        uploaded_files = self.test_file_upload()
        test_results.append(("파일업로드", len(uploaded_files) > 0))
        
        # 5. 파일 처리 상태 확인
        processing_results = []
        for file_info in uploaded_files:
            result = self.test_file_processing_status(file_info["file_id"])
            processing_results.append(result)
            
        test_results.append(("파일처리", all(processing_results)))
        
        # 6. BIM 분석 (IFC 파일만)
        bim_results = []
        for file_info in uploaded_files:
            result = self.test_bim_analysis(file_info["file_id"], file_info["file_type"])
            bim_results.append(result)
            
        test_results.append(("BIM분석", all(bim_results)))
        
        # 7. 프로젝트 파일 목록
        test_results.append(("파일목록", self.test_project_files()))
        
        # 8. 파일 다운로드
        download_results = []
        for file_info in uploaded_files:
            result = self.test_file_download(file_info["file_id"], file_info["filename"])
            download_results.append(result)
            
        test_results.append(("파일다운로드", all(download_results)))
        
        # 9. 파일 통계
        test_results.append(("파일통계", self.test_file_statistics()))
        
        # 결과 요약
        self.log("\n=== 테스트 결과 요약 ===")
        passed = 0
        total = len(test_results)
        
        for test_name, result in test_results:
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{test_name}: {status}")
            if result:
                passed += 1
                
        success_rate = (passed / total) * 100
        self.log(f"\n성공률: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            self.log("🎉 파일 처리 시스템이 정상 작동합니다!")
            return True
        else:
            self.log("⚠️  일부 기능에 문제가 있습니다.")
            return False

def main():
    """메인 실행 함수"""
    tester = FileSystemTester()
    
    try:
        success = tester.run_full_test_suite()
        exit_code = 0 if success else 1
        exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n\n테스트가 사용자에 의해 중단되었습니다.")
        exit(1)
    except Exception as e:
        print(f"\n\n예상치 못한 오류 발생: {e}")
        exit(1)

if __name__ == "__main__":
    main()