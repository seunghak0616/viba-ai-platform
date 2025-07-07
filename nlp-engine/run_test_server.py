#!/usr/bin/env python3
"""
VIBA AI 테스트 서버 실행 스크립트
==============================

파일 업로드 및 BIM 처리 시스템 테스트를 위한 서버를 실행합니다.

@version 1.0
@author VIBA AI Team
@date 2025.07.07
"""

import uvicorn
import sys
import os
from pathlib import Path

# 백엔드 디렉토리를 Python 경로에 추가
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

def run_server():
    """테스트 서버 실행"""
    print("🚀 VIBA AI 테스트 서버 시작")
    print("📁 파일 업로드 및 BIM 처리 시스템 활성화")
    print("📍 API 문서: http://localhost:8000/docs")
    print("🔧 파일 관리: http://localhost:8000/api/files/health")
    print("\n테스트를 위한 기본 계정:")
    print("  사용자명: architect")
    print("  비밀번호: password123")
    print("\n서버를 중지하려면 Ctrl+C를 누르세요.\n")
    
    try:
        # 현재 디렉토리를 백엔드로 변경
        os.chdir(backend_dir)
        
        # FastAPI 서버 실행
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n✅ 서버가 정상적으로 종료되었습니다.")
    except Exception as e:
        print(f"\n❌ 서버 실행 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_server()