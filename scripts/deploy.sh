#!/bin/bash
# VIBA AI 프로덕션 배포 스크립트
# 프로젝트 루트: /Users/seunghakwoo/Documents/Cursor/Z/

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
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

# 프로젝트 루트 디렉토리 확인
PROJECT_ROOT="/Users/seunghakwoo/Documents/Cursor/Z"
if [ ! -d "$PROJECT_ROOT" ]; then
    log_error "프로젝트 루트 디렉토리를 찾을 수 없습니다: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"
log_info "프로젝트 디렉토리: $(pwd)"

# 환경 변수 파일 확인
ENV_FILE="$PROJECT_ROOT/.env.production"
if [ ! -f "$ENV_FILE" ]; then
    log_warning ".env.production 파일이 없습니다. 예시 파일을 복사합니다."
    cp "$PROJECT_ROOT/.env.production.example" "$ENV_FILE"
    log_warning "⚠️ $ENV_FILE 파일을 수정하여 실제 값을 입력해주세요!"
    exit 1
fi

# Docker 및 Docker Compose 확인
if ! command -v docker &> /dev/null; then
    log_error "Docker가 설치되어 있지 않습니다."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    log_error "Docker Compose가 설치되어 있지 않습니다."
    exit 1
fi

# 배포 모드 선택
DEPLOY_MODE=${1:-production}
case $DEPLOY_MODE in
    "development"|"dev")
        COMPOSE_FILE="docker-compose.integration.yml"
        log_info "개발 환경 배포를 시작합니다..."
        ;;
    "production"|"prod")
        COMPOSE_FILE="docker-compose.production.yml"
        log_info "프로덕션 환경 배포를 시작합니다..."
        ;;
    *)
        log_error "올바른 배포 모드를 선택하세요: development, production"
        exit 1
        ;;
esac

# 필요한 디렉토리 생성
log_info "필요한 디렉토리를 생성합니다..."
mkdir -p logs/nginx logs/backend logs/ai-service logs/postgres logs/redis
mkdir -p uploads ai-temp database/init monitoring/grafana/dashboards monitoring/grafana/datasources

# 기존 컨테이너 정리 (선택사항)
read -p "기존 컨테이너를 정리하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "기존 컨테이너를 정리합니다..."
    docker-compose -f "$COMPOSE_FILE" down -v --remove-orphans || true
    docker system prune -f || true
fi

# 환경 변수 로드
log_info "환경 변수를 로드합니다..."
set -a
source "$ENV_FILE"
set +a

# Docker 이미지 빌드
log_info "Docker 이미지를 빌드합니다..."
docker-compose -f "$COMPOSE_FILE" build --no-cache

# 서비스 시작
log_info "서비스를 시작합니다..."
docker-compose -f "$COMPOSE_FILE" up -d

# 헬스체크 대기
log_info "서비스 헬스체크를 확인합니다..."
sleep 30

# 서비스 상태 확인
check_service() {
    local service_name=$1
    local url=$2
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_success "$service_name 서비스가 정상적으로 실행 중입니다."
            return 0
        fi
        log_info "$service_name 서비스 대기 중... ($attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    log_error "$service_name 서비스가 시작되지 않았습니다."
    return 1
}

# 각 서비스 헬스체크
if [ "$DEPLOY_MODE" = "production" ] || [ "$DEPLOY_MODE" = "prod" ]; then
    check_service "Backend" "http://localhost:5001/health"
    check_service "AI Service" "http://localhost:8000/health"
    check_service "Frontend" "http://localhost:3000/health"
else
    check_service "Backend" "http://localhost:5001/health"
    check_service "AI Service" "http://localhost:8000/health"
    check_service "Frontend" "http://localhost:3000"
fi

# 데이터베이스 마이그레이션 (프로덕션 모드)
if [ "$DEPLOY_MODE" = "production" ] || [ "$DEPLOY_MODE" = "prod" ]; then
    log_info "데이터베이스 마이그레이션을 실행합니다..."
    docker-compose -f "$COMPOSE_FILE" exec backend npm run migrate || log_warning "마이그레이션 실패 - 수동으로 확인하세요."
fi

# 최종 상태 확인
log_info "전체 서비스 상태를 확인합니다..."
docker-compose -f "$COMPOSE_FILE" ps

# 배포 완료 메시지
log_success "🎉 VIBA AI 플랫폼 배포가 완료되었습니다!"
echo
echo "=== 서비스 접속 정보 ==="
if [ "$DEPLOY_MODE" = "production" ] || [ "$DEPLOY_MODE" = "prod" ]; then
    echo "🌐 프론트엔드: http://localhost"
    echo "🔧 백엔드 API: http://localhost/api"
    echo "🤖 AI 서비스: http://localhost:8000/docs"
    echo "📊 모니터링: http://localhost:3001 (Grafana)"
    echo "🔍 메트릭스: http://localhost:9090 (Prometheus)"
else
    echo "🌐 프론트엔드: http://localhost:3000"
    echo "🔧 백엔드 API: http://localhost:5000/api"
    echo "🤖 AI 서비스: http://localhost:8000/docs"
fi
echo
echo "=== 로그 확인 ==="
echo "docker-compose -f $COMPOSE_FILE logs -f [service_name]"
echo
echo "=== 서비스 중지 ==="
echo "docker-compose -f $COMPOSE_FILE down"