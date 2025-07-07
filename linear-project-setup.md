# VIBA AI 통합 프로젝트 - Linear 태스크 관리

## 프로젝트 개요
**프로젝트명**: VIBA AI Platform Integration  
**목표**: 중복된 백엔드/프론트엔드 구조를 통합하여 단일 프로덕션 시스템 구축  
**기간**: 2025.07.07 ~ 2025.07.14 (1주)

## Phase 1: 아키텍처 통합 (HIGH Priority)

### 🎯 Epic: Backend Architecture Integration
**목표**: Node.js 메인 + Python AI 마이크로서비스 구조 완성

#### Task 1.1: 백엔드 구조 분석 ✅ DONE
- [x] Node.js Express 백엔드 현황 파악
- [x] Python FastAPI 백엔드 현황 파악  
- [x] 중복 기능 및 차이점 분석
- **결과**: Node.js를 메인으로, Python을 AI 전용으로 결정

#### Task 1.2: Node.js 메인 서버 설정 ✅ DONE  
- [x] AI 마이크로서비스 프록시 라우터 생성 (`/backend/src/routes/ai-proxy.js`)
- [x] 환경변수에 AI 서비스 URL 추가 (`AI_SERVICE_URL=http://localhost:8001`)
- [x] Express.js 라우팅 구조 완성
- **결과**: Node.js 메인 서버 준비 완료

#### Task 1.3: Python AI 마이크로서비스 분리 ✅ DONE
- [x] AI 전용 FastAPI 서버 생성 (`/ai-microservice/main.py`)
- [x] 8개 AI 에이전트 연동 구조 설계
- [x] JWT 토큰 검증 및 Node.js 백엔드와 통신 준비
- **결과**: AI 마이크로서비스 아키텍처 완성

#### Task 1.4: 새로운 폴더 구조 생성 🔄 IN PROGRESS
- [x] `/viba-integrated/` 통합 폴더 구조 생성
  ```
  viba-integrated/
  ├── backend/          # Node.js 메인 서버
  ├── frontend/         # React 메인 프론트엔드  
  ├── ai-service/       # Python AI 마이크로서비스
  ├── docs/            # 문서화
  ├── tests/           # 통합 테스트
  ├── scripts/         # 배포/마이그레이션 스크립트
  └── deploy/          # Docker, K8s, Nginx
  ```
- [ ] 기존 파일들을 새 구조로 이동
- [ ] 중복 파일 제거 및 정리

## Phase 2: 프론트엔드 통합 (HIGH Priority)

### 🎯 Epic: Frontend Consolidation
**목표**: `/frontend/`를 메인으로 `/nlp-engine/frontend-react/` 유용한 컴포넌트 통합

#### Task 2.1: 프론트엔드 비교 분석 📋 TODO
- [ ] `/frontend/` 구조 및 기능 분석
- [ ] `/nlp-engine/frontend-react/` 고급 기능 파악
- [ ] 통합 가능한 컴포넌트 식별
- [ ] 마이그레이션 계획 수립

#### Task 2.2: 고급 AuthContext 이전 📋 TODO  
- [ ] `/nlp-engine/frontend-react/src/contexts/AuthContext.tsx` 분석
- [ ] 역할 기반 권한 시스템 (RBAC) 이전
- [ ] hasPermission, hasRole 메서드 통합
- [ ] 세션 관리 고도화

#### Task 2.3: UserManagement 컴포넌트 이전 📋 TODO
- [ ] `/nlp-engine/frontend-react/src/components/UserManagement/` 이전
- [ ] 관리자 UI 통합
- [ ] 사용자 권한 관리 기능 추가

## Phase 3: API 게이트웨이 및 통신 (MEDIUM Priority)

### 🎯 Epic: Service Communication Setup
**목표**: Node.js ↔ Python AI 서비스 간 완벽한 통신

#### Task 3.1: API 게이트웨이 설계 📋 TODO
- [ ] Node.js에서 Python AI 서비스 라우팅 설정
- [ ] 통합 인증 미들웨어 구현  
- [ ] 에러 핸들링 및 재시도 로직
- [ ] API 문서화

#### Task 3.2: 실시간 통신 연동 📋 TODO
- [ ] WebSocket을 통한 AI 응답 실시간 전달
- [ ] 진행률 표시 및 상태 업데이트
- [ ] 세션 관리 동기화

## Phase 4: 정리 및 최적화 (MEDIUM Priority)

### 🎯 Epic: Cleanup and Optimization
**목표**: 중복 제거 및 성능 최적화

#### Task 4.1: 중복 디렉토리 제거 📋 TODO
- [ ] `/frontend 2/` 제거
- [ ] `/ai-service/` 구버전 제거  
- [ ] `/nlp-engine/` 정리 (유용한 파일만 보존)
- [ ] 사용하지 않는 의존성 제거

#### Task 4.2: 설정 파일 표준화 📋 TODO
- [ ] 환경변수 통합 관리
- [ ] Docker Compose 업데이트
- [ ] 개발/프로덕션 환경 분리

## Phase 5: 테스트 및 배포 (LOW Priority)

### 🎯 Epic: Testing and Deployment
**목표**: 통합 테스트 및 프로덕션 배포 준비

#### Task 5.1: 통합 테스트 📋 TODO
- [ ] E2E 테스트 업데이트
- [ ] API 통합 테스트
- [ ] 성능 테스트

#### Task 5.2: 배포 파이프라인 📋 TODO  
- [ ] Docker 다중 서비스 오케스트레이션
- [ ] CI/CD 파이프라인 구축
- [ ] 모니터링 시스템 설정

## 📊 진행 현황

### 완료된 작업 ✅
- 백엔드 아키텍처 분석 및 설계
- Node.js 메인 서버 AI 프록시 구성
- Python AI 마이크로서비스 분리
- 통합 폴더 구조 생성

### 현재 진행 중 🔄
- 파일 이동 및 정리
- Linear 태스크 관리 시스템 설정

### 다음 우선순위 📋
1. 프론트엔드 구조 비교 분석
2. 고급 AuthContext 마이그레이션
3. API 게이트웨이 구현

## 🎯 성공 지표
- [ ] 단일 API 엔드포인트로 모든 기능 접근
- [ ] AI 응답 시간 5초 이내
- [ ] 전체 테스트 통과율 95% 이상
- [ ] 중복 코드 80% 이상 제거

---

**업데이트**: 2025.07.07 - Linear 태스크 관리 시스템 도입
**다음 체크포인트**: 2025.07.08 - Phase 1 완료 목표