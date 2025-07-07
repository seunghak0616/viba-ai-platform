#!/bin/bash

# 바이브 코딩 BIM 플랫폼 Docker 개발 환경 스크립트

set -e

echo "🚀 바이브 코딩 BIM 플랫폼 Docker 개발 환경 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 함수 정의
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Docker 설치 확인
check_docker() {
    log_info "Docker 설치 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        log_info "Docker Desktop을 설치해주세요: https://www.docker.com/products/docker-desktop/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        log_info "Docker Compose를 설치해주세요."
        exit 1
    fi
    
    log_success "Docker 환경 확인 완료"
}

# 기존 컨테이너 정리
cleanup_containers() {
    log_info "기존 컨테이너 정리 중..."
    
    # 실행 중인 컨테이너 중지
    docker-compose down 2>/dev/null || true
    
    # BIM 관련 컨테이너 강제 제거
    docker rm -f bim-backend bim-frontend-dev bim-database bim-adminer 2>/dev/null || true
    
    log_success "컨테이너 정리 완료"
}

# 데이터 디렉토리 생성
setup_directories() {
    log_info "필요한 디렉토리 생성 중..."
    
    mkdir -p backend/data
    mkdir -p backend/logs
    mkdir -p frontend/node_modules
    
    # 권한 설정 (macOS/Linux)
    chmod 755 backend/data
    chmod 755 backend/logs
    
    log_success "디렉토리 설정 완료"
}

# Docker 이미지 빌드
build_images() {
    log_info "Docker 이미지 빌드 중..."
    
    # 백엔드 개발 이미지 빌드
    log_info "백엔드 개발 이미지 빌드 중..."
    docker build -t bim-backend-dev:latest -f Dockerfile.backend.dev .
    
    log_success "이미지 빌드 완료"
}

# 서비스 시작
start_services() {
    log_info "서비스 시작 중..."
    
    # Docker Compose로 서비스 시작
    docker-compose up -d
    
    log_success "서비스 시작 완료"
}

# 서비스 상태 확인
check_health() {
    log_info "서비스 상태 확인 중..."
    
    # 잠시 대기 (서비스 시작 시간)
    sleep 10
    
    # 백엔드 헬스 체크
    log_info "백엔드 서비스 확인 중..."
    for i in {1..30}; do
        if curl -f -s http://localhost:5001/health > /dev/null; then
            log_success "✅ 백엔드 서비스 정상 (http://localhost:5001)"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "❌ 백엔드 서비스 응답 없음"
            docker-compose logs backend
            exit 1
        fi
        
        sleep 2
    done
    
    # 프론트엔드 확인
    log_info "프론트엔드 서비스 확인 중..."
    for i in {1..30}; do
        if curl -f -s http://localhost:3000 > /dev/null; then
            log_success "✅ 프론트엔드 서비스 정상 (http://localhost:3000)"
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "❌ 프론트엔드 서비스 응답 없음"
            docker-compose logs frontend-dev
            exit 1
        fi
        
        sleep 2
    done
}

# 개발 정보 출력
show_dev_info() {
    echo ""
    log_success "🎉 바이브 코딩 BIM 플랫폼 Docker 환경이 준비되었습니다!"
    echo ""
    echo "📍 서비스 접속 URL:"
    echo "  🌐 프론트엔드: http://localhost:3000"
    echo "  🔧 백엔드 API: http://localhost:5001"
    echo "  💾 Adminer (DB 관리): http://localhost:8080 (선택사항)"
    echo ""
    echo "🔧 유용한 Docker 명령어:"
    echo "  docker-compose logs -f           # 모든 서비스 로그 보기"
    echo "  docker-compose logs -f backend   # 백엔드 로그만 보기"
    echo "  docker-compose logs -f frontend-dev # 프론트엔드 로그만 보기"
    echo "  docker-compose restart backend   # 백엔드 재시작"
    echo "  docker-compose down              # 모든 서비스 중지"
    echo "  docker-compose exec backend sh   # 백엔드 컨테이너 접속"
    echo ""
    echo "📁 개발 팁:"
    echo "  - backend/src/ 파일 변경시 자동 재시작됩니다"
    echo "  - frontend/ 파일 변경시 자동 리로드됩니다"
    echo "  - 데이터베이스는 backend/data/dev.db에 저장됩니다"
    echo ""
}

# 메인 실행
main() {
    case "${1:-start}" in
        "start")
            check_docker
            cleanup_containers
            setup_directories
            build_images
            start_services
            check_health
            show_dev_info
            ;;
        "stop")
            log_info "서비스 중지 중..."
            docker-compose down
            log_success "서비스 중지 완료"
            ;;
        "restart")
            log_info "서비스 재시작 중..."
            docker-compose restart
            check_health
            log_success "서비스 재시작 완료"
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "clean")
            log_info "전체 환경 정리 중..."
            docker-compose down -v
            docker rmi bim-backend:latest 2>/dev/null || true
            docker system prune -f
            log_success "환경 정리 완료"
            ;;
        "help")
            echo "사용법: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  start   - 개발 환경 시작 (기본값)"
            echo "  stop    - 서비스 중지"
            echo "  restart - 서비스 재시작"
            echo "  logs    - 실시간 로그 보기"
            echo "  clean   - 전체 환경 정리"
            echo "  help    - 도움말 표시"
            ;;
        *)
            log_error "알 수 없는 명령어: $1"
            log_info "사용법: $0 {start|stop|restart|logs|clean|help}"
            exit 1
            ;;
    esac
}

# 스크립트 실행
main "$@"