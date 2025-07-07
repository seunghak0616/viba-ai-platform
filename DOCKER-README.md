# 🐋 바이브 코딩 BIM 플랫폼 - Docker 환경

**✨ 최신 업데이트: 건축 전문 시스템 + 3D BIM 뷰어 연동 완료!**

이 문서는 Docker를 사용하여 최신 기능이 완전히 통합된 BIM 플랫폼 개발 환경을 구성하는 방법을 설명합니다.

## 📋 사전 요구사항

### 1. Docker 설치
- **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/mac/install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/windows/install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

### 2. 시스템 요구사항
- **RAM**: 최소 4GB, 권장 8GB 이상
- **디스크**: 최소 10GB 여유 공간
- **포트**: 3000, 5001, 8080 포트가 사용 가능해야 함

## 🚀 빠른 시작

### 1. 개발 환경 시작
```bash
# 스크립트 실행 권한 부여 (최초 1회)
chmod +x docker-dev.sh

# 개발 환경 시작
./docker-dev.sh start
```

### 2. 서비스 접속
- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:5001
- **3D BIM 뷰어**: http://localhost:3000/3d-viewer
- **테스트 페이지**: http://localhost:3000/test.html
- **Adminer (DB 관리)**: http://localhost:8080 (선택사항)

### 3. 🎉 새로운 기능 체험하기
```bash
# 1. 브라우저에서 http://localhost:3000 접속
# 2. 회원가입/로그인 후 "프로젝트 관리" 이동
# 3. "새 프로젝트" 버튼으로 건축 전문 프로젝트 생성
# 4. 15개 카테고리 프리셋으로 빠른 입력 체험
# 5. 프로젝트 생성 후 3D 뷰어에서 즉시 확인
```

## 🔧 Docker 명령어

### 기본 명령어
```bash
# 개발 환경 시작
./docker-dev.sh start

# 서비스 중지
./docker-dev.sh stop

# 서비스 재시작
./docker-dev.sh restart

# 실시간 로그 보기
./docker-dev.sh logs

# 전체 환경 정리
./docker-dev.sh clean

# 도움말
./docker-dev.sh help
```

### 상세 Docker Compose 명령어
```bash
# 특정 서비스 로그 보기
docker-compose logs -f backend      # 백엔드 로그
docker-compose logs -f frontend-dev # 프론트엔드 로그

# 특정 서비스 재시작
docker-compose restart backend
docker-compose restart frontend-dev

# 컨테이너 내부 접속
docker-compose exec backend sh     # 백엔드 컨테이너 접속
docker-compose exec frontend-dev sh # 프론트엔드 컨테이너 접속

# 서비스 스케일링 (필요시)
docker-compose up -d --scale backend=2
```

## 📁 프로젝트 구조

```
├── Dockerfile.backend          # 백엔드 Docker 이미지
├── Dockerfile.frontend         # 프론트엔드 Docker 이미지
├── docker-compose.yml          # Docker Compose 설정
├── docker-dev.sh              # 개발 환경 스크립트
├── .dockerignore              # Docker 빌드 제외 파일
├── docker/
│   └── nginx.conf             # Nginx 설정 (프로덕션용)
├── backend/
│   ├── data/                  # SQLite 데이터베이스 파일
│   └── src/                   # 백엔드 소스코드
└── frontend/
    └── src/                   # 프론트엔드 소스코드
```

## 🔄 개발 워크플로우

### 1. 코드 변경시
- **백엔드**: `backend/src/` 파일 변경시 자동으로 서버가 재시작됩니다
- **프론트엔드**: `frontend/src/` 파일 변경시 자동으로 페이지가 리로드됩니다

### 2. 의존성 추가시
```bash
# 백엔드 의존성 추가
docker-compose exec backend npm install <package-name>
docker-compose restart backend

# 프론트엔드 의존성 추가
docker-compose exec frontend-dev npm install <package-name>
```

### 3. 데이터베이스 초기화
```bash
# 데이터베이스 마이그레이션
docker-compose exec backend npx prisma migrate deploy

# 데이터베이스 시드 데이터 추가
docker-compose exec backend npm run db:seed
```

## 🐛 문제 해결

### 1. 포트 충돌
```bash
# 사용 중인 포트 확인
lsof -i :3000
lsof -i :5001

# 기존 프로세스 종료 후 재시작
./docker-dev.sh stop
./docker-dev.sh start
```

### 2. 컨테이너 빌드 실패
```bash
# Docker 캐시 정리 후 재빌드
docker system prune -f
./docker-dev.sh clean
./docker-dev.sh start
```

### 3. 서비스 연결 실패
```bash
# 서비스 상태 확인
docker-compose ps

# 네트워크 상태 확인
docker network ls
docker network inspect bim_bim-network

# 서비스 재시작
./docker-dev.sh restart
```

### 4. 로그 확인
```bash
# 모든 서비스 로그
docker-compose logs

# 특정 서비스 로그 (실시간)
docker-compose logs -f backend
docker-compose logs -f frontend-dev
```

## 🔒 보안 고려사항

### 개발 환경
- SQLite 데이터베이스 사용 (로컬 파일)
- 개발 모드에서만 실행
- CORS 설정이 느슨함

### 프로덕션 배포시 주의사항
- 환경 변수로 시크릿 관리
- HTTPS 설정 필요
- 데이터베이스를 PostgreSQL로 변경 권장
- CORS 정책 강화 필요

## 📊 성능 최적화

### 1. 개발 환경 최적화
```bash
# Docker Desktop 리소스 할당 증가
# Settings > Resources > Memory: 6-8GB 권장
```

### 2. 빌드 최적화
```bash
# 멀티스테이지 빌드 사용 (이미 적용됨)
# .dockerignore로 불필요한 파일 제외 (이미 적용됨)
```

## 🧪 테스트

### 1. 자동 테스트
```bash
# 백엔드 테스트
docker-compose exec backend npm test

# 프론트엔드 테스트
docker-compose exec frontend-dev npm test
```

### 2. E2E 테스트
```bash
# Playwright 테스트 (호스트에서 실행)
cd tests
node simple-test.js
```

## 📞 지원

문제가 발생하거나 질문이 있으시면:
1. 로그를 확인하세요: `./docker-dev.sh logs`
2. 서비스를 재시작해보세요: `./docker-dev.sh restart`
3. 전체 환경을 정리 후 재시작: `./docker-dev.sh clean && ./docker-dev.sh start`

---

🎉 **Docker 환경에서 바이브 코딩 BIM 플랫폼 개발을 즐기세요!**