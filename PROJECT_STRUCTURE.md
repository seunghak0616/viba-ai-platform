# 🏗️ VIBA AI 프로젝트 구조 정리 계획

> **최상위 폴더**: `/Users/seunghakwoo/Documents/Cursor/Z`  
> **작성일**: 2025.07.07  
> **목적**: 최상위 폴더 기준 통합 작업 환경 구축

## 📊 현재 상황 분석

### 🔍 주요 디렉토리 현황
```
/Users/seunghakwoo/Documents/Cursor/Z/
├── backend/              # Node.js 메인 백엔드 (Prisma + Express)
├── frontend/             # React 메인 프론트엔드 (완성도 높음)
├── nlp-engine/           # Python AI 백엔드 + React 프론트엔드
├── ai-service/           # 추가 AI 서비스
├── ai-microservice/      # 새로 생성된 AI 마이크로서비스
├── frontend 2/           # 중복 프론트엔드
├── tests/               # 테스트 파일들
├── docs/                # 문서화
└── viba-integrated/      # 서브폴더 통합 버전 (이전 작업)
```

### ⚠️ 문제점
1. **중복 구조**: 여러 백엔드/프론트엔드 구현
2. **서브폴더 혼재**: `/viba-integrated/` vs 최상위 직접 구조
3. **테스트 파일 산재**: 최상위에 많은 테스트 JS 파일들
4. **설정 파일 중복**: 여러 Docker, 환경설정 파일

## 🎯 통합 계획

### Phase 1: 최상위 폴더 정리 ✅ 진행 중

#### 1.1 핵심 구조 확정
**최종 구조**:
```
/Users/seunghakwoo/Documents/Cursor/Z/
├── backend/              # Node.js 메인 API 서버
├── frontend/             # React 통합 프론트엔드
├── ai-service/           # Python AI 마이크로서비스 (통합)
├── docs/                # 프로젝트 문서
├── tests/               # 통합 테스트
├── scripts/             # 배포/유틸리티 스크립트
├── docker-compose.yml   # 메인 Docker 설정
├── .env                 # 환경 변수
└── .gitignore           # Git 무시 파일
```

#### 1.2 제거할 디렉토리/파일
- [ ] `frontend 2/` - 중복 프론트엔드
- [ ] `ai-microservice/` - `ai-service/`로 통합
- [ ] `nlp-engine/` - 유용한 부분만 추출 후 제거
- [ ] `viba-integrated/` - 서브폴더 제거
- [ ] 최상위 테스트 JS 파일들 (`*test*.js`, `*debug*.js` 등)
- [ ] 중복 Docker 설정 파일들
- [ ] 임시 이미지 파일들 (`*.png` 테스트 결과)

#### 1.3 보존할 핵심 파일
- [x] `README.md` - 메인 프로젝트 문서
- [x] `CLAUDE.md` - 개발 컨텍스트
- [x] `INTEGRATION_PLAN.md` - 통합 계획
- [x] `backend/` - Node.js 메인 백엔드
- [x] `frontend/` - React 메인 프론트엔드
- [x] `docs/` - 프로젝트 문서화

### Phase 2: AI 서비스 통합

#### 2.1 Python AI 서비스 통합
- [ ] `nlp-engine/backend/` → `ai-service/src/` 통합
- [ ] `ai-microservice/` → `ai-service/` 통합
- [ ] 8개 AI 에이전트 최신 버전 확정
- [ ] FastAPI 서버 최종 설정

#### 2.2 프론트엔드 고급 기능 통합
- [ ] `nlp-engine/frontend-react/` 고급 기능 분석
- [ ] AuthContext RBAC 시스템 → `frontend/` 이전
- [ ] UserManagement 컴포넌트 → `frontend/` 이전

### Phase 3: 설정 및 배포

#### 3.1 환경 설정 통합
- [ ] `.env` 파일 통합
- [ ] `docker-compose.yml` 최종 버전
- [ ] `package.json` 통합 (루트 레벨)

#### 3.2 배포 준비
- [ ] `scripts/` 폴더 생성 및 배포 스크립트
- [ ] CI/CD 설정
- [ ] 프로덕션 환경 설정

## 🚀 즉시 실행 계획

### Step 1: 불필요한 파일 정리
```bash
# 테스트 이미지 파일들 제거
rm -f *.png

# 테스트 JS 파일들 tests/ 폴더로 이동
mkdir -p tests/legacy
mv *test*.js *debug*.js *manual*.js tests/legacy/

# 임시 JSON 파일들 정리
rm -f *.json architect_login.json login_user.json
```

### Step 2: .gitignore 생성
- 불필요한 파일들 Git 추적에서 제외
- 개발 환경별 파일들 무시

### Step 3: 중복 디렉토리 정리
- `frontend 2/` 제거 여부 확인 후 삭제
- `viba-integrated/` 유용한 부분 추출 후 제거

### Step 4: 핵심 구조 확정
- `backend/`, `frontend/`, `ai-service/` 최종 정리
- 환경 설정 파일 통합

## 📋 작업 체크리스트

### ✅ 완료
- [x] 현재 상황 분석
- [x] 통합 계획 수립
- [x] PROJECT_STRUCTURE.md 문서 작성

### 🔄 진행 중
- [ ] .gitignore 생성
- [ ] 불필요한 파일 정리
- [ ] 중복 디렉토리 제거

### 📋 예정
- [ ] AI 서비스 통합
- [ ] 프론트엔드 고급 기능 통합
- [ ] 배포 설정 완료

## 🎯 성공 지표

### 단기 목표 (오늘)
- [ ] 최상위 폴더 구조 정리 완료
- [ ] 중복 파일/폴더 제거
- [ ] 핵심 3개 폴더 구조 확정 (backend, frontend, ai-service)

### 중기 목표 (이번 주)
- [ ] 통합 개발 환경 구축
- [ ] GitHub Issues 시스템 활성화
- [ ] CI/CD 파이프라인 구축

---

**다음 액션**: Step 1부터 순차적 실행