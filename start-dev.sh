#!/bin/bash

# BIM 플랫폼 개발 환경 시작 스크립트
# 에러를 최소화하기 위한 안전한 시작 방법

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 BIM Platform 개발 환경 시작..."

# 1. 환경 변수 확인
echo "📋 환경 변수 확인 중..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다. .env.example을 복사하여 .env를 만드세요."
    cp .env.example .env || echo "❌ .env.example 파일이 없습니다."
    echo "✅ .env 파일을 생성했습니다. 필요한 값들을 설정해주세요."
fi

# 2. 백엔드 의존성 설치 및 확인
echo "📦 백엔드 의존성 설치 중..."
cd backend
if [ ! -d "node_modules" ]; then
    npm install || {
        echo "❌ 백엔드 의존성 설치 실패"
        exit 1
    }
fi

# 3. 데이터베이스 확인 (옵션)
echo "🗄️  데이터베이스 상태 확인 중..."
npm run db:status || echo "⚠️  데이터베이스 연결을 확인해주세요."

# 4. 프론트엔드 의존성 설치
echo "🎨 프론트엔드 의존성 설치 중..."
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install || {
        echo "❌ 프론트엔드 의존성 설치 실패"
        exit 1
    }
fi

# 5. NLP 엔진 설정 (Python)
echo "🧠 NLP 엔진 설정 중..."
cd ../nlp-engine
if [ ! -d "venv" ]; then
    echo "🐍 Python 가상환경 생성 중..."
    python3 -m venv venv || {
        echo "❌ Python 가상환경 생성 실패"
        exit 1
    }
fi

source venv/bin/activate
pip install -r requirements.txt || echo "⚠️  Python 의존성 설치 확인 필요"

cd ..

echo "✅ 모든 컴포넌트 설치 완료!"
echo ""
echo "🎯 다음 단계:"
echo "1. 터미널을 3개 열어주세요"
echo "2. 각 터미널에서 다음 명령어를 실행하세요:"
echo ""
echo "   터미널 1 (백엔드):"
echo "   cd backend && npm run dev"
echo ""
echo "   터미널 2 (프론트엔드):"
echo "   cd frontend && npm run dev"
echo ""
echo "   터미널 3 (NLP 엔진):"
echo "   cd nlp-engine && source venv/bin/activate && python src/main.py"
echo ""
echo "🌐 브라우저에서 http://localhost:3000 접속"