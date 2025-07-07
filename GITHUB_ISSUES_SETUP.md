# 🎯 VIBA AI - GitHub Issues 설정 가이드

> **프로젝트**: VIBA AI 플랫폼  
> **저장소**: `/Users/seunghakwoo/Documents/Cursor/Z`  
> **설정일**: 2025.07.07

## 📋 GitHub Issues 시스템 활성화

### 🔗 저장소 연결
1. **새 GitHub 저장소 생성**: `viba-ai-platform`
2. **로컬 Git 초기화**: ✅ 완료
3. **원격 저장소 연결**: 예정
4. **초기 커밋 및 푸시**: 예정

### 🏷️ 라벨 시스템

#### Epic 라벨
- 🎯 `epic:architecture` - 아키텍처 통합
- 🎯 `epic:frontend` - 프론트엔드 통합  
- 🎯 `epic:backend` - 백엔드 통합
- 🎯 `epic:ai-service` - AI 서비스 통합
- 🎯 `epic:deployment` - 배포 및 인프라

#### 우선순위 라벨
- 🔴 `priority:high` - 높음 (즉시 처리)
- 🟡 `priority:medium` - 보통 (이번 주)
- 🟢 `priority:low` - 낮음 (향후)

#### 상태 라벨
- ✅ `status:completed` - 완료
- 🔄 `status:in-progress` - 진행 중
- 📋 `status:todo` - 할 일
- ⏸️ `status:blocked` - 차단됨

#### 타입 라벨
- 🐛 `type:bug` - 버그 수정
- ✨ `type:feature` - 새 기능
- 🔧 `type:maintenance` - 유지보수
- 📝 `type:documentation` - 문서화

### 📊 이슈 템플릿

#### Feature Request Template
```markdown
## 🎯 기능 개요
<!-- 기능에 대한 간단한 설명 -->

## 📋 상세 요구사항
<!-- 구체적인 요구사항 리스트 -->

## ✅ 완료 조건
<!-- 완료를 판단할 수 있는 기준 -->

## 🔗 관련 이슈
<!-- 관련된 다른 이슈들 -->

## 📅 예상 작업 시간
<!-- 예상되는 작업 시간 -->
```

#### Bug Report Template
```markdown
## 🐛 버그 설명
<!-- 버그에 대한 명확한 설명 -->

## 🔄 재현 단계
1. 
2. 
3. 

## 💻 환경 정보
- OS: 
- Browser: 
- Version: 

## 📸 스크린샷
<!-- 가능하다면 스크린샷 첨부 -->

## 🎯 예상 동작
<!-- 정상적으로 동작해야 하는 방식 -->
```

### 🏗️ 프로젝트 보드 구성

#### Column 구성
1. **📋 Backlog** - 계획된 작업들
2. **🔄 In Progress** - 현재 진행 중
3. **👀 Review** - 리뷰 중
4. **✅ Done** - 완료된 작업

#### Milestones
- **Phase 1: 아키텍처 통합** (2025.07.07 - 2025.07.09)
- **Phase 2: 프론트엔드 통합** (2025.07.10 - 2025.07.12)
- **Phase 3: 배포 준비** (2025.07.13 - 2025.07.14)

## 🎯 초기 이슈 목록

### Epic: Architecture Integration

#### Issue #1: 최상위 폴더 구조 정리
- **Title**: 최상위 폴더 기준 프로젝트 구조 정리
- **Labels**: `epic:architecture`, `priority:high`, `type:maintenance`
- **Milestone**: Phase 1
- **Description**: 중복 파일 정리 및 핵심 구조 확정

#### Issue #2: AI 서비스 통합
- **Title**: Python AI 마이크로서비스 통합 구조 확정
- **Labels**: `epic:ai-service`, `priority:high`, `type:feature`
- **Milestone**: Phase 1
- **Description**: nlp-engine, ai-service, ai-microservice 통합

#### Issue #3: 백엔드 API 게이트웨이 완성
- **Title**: Node.js 메인 서버 AI 프록시 라우터 최적화
- **Labels**: `epic:backend`, `priority:medium`, `type:feature`
- **Milestone**: Phase 1
- **Description**: AI 마이크로서비스와의 통신 최적화

### Epic: Frontend Integration

#### Issue #4: 프론트엔드 구조 분석
- **Title**: 메인 프론트엔드 vs NLP 엔진 프론트엔드 비교
- **Labels**: `epic:frontend`, `priority:high`, `type:documentation`
- **Milestone**: Phase 2
- **Description**: 통합 가능한 컴포넌트 및 기능 식별

#### Issue #5: AuthContext RBAC 통합
- **Title**: 고급 권한 관리 시스템 통합
- **Labels**: `epic:frontend`, `priority:high`, `type:feature`
- **Milestone**: Phase 2
- **Description**: NLP 엔진의 RBAC 시스템을 메인으로 이전

## 🚀 GitHub Issues 활성화 단계

### Step 1: 저장소 연결
```bash
# GitHub CLI로 저장소 생성
gh repo create viba-ai-platform --public --description "차세대 AI 건축 설계 플랫폼"

# 원격 저장소 연결
git remote add origin https://github.com/[username]/viba-ai-platform.git

# 초기 푸시
git add .
git commit -m "Initial commit: VIBA AI 플랫폼 통합 프로젝트"
git push -u origin main
```

### Step 2: 라벨 및 템플릿 설정
```bash
# 라벨 생성
gh label create "epic:architecture" --color "FF6B6B" --description "아키텍처 통합 작업"
gh label create "priority:high" --color "D73A49" --description "높은 우선순위"
gh label create "status:in-progress" --color "0075CA" --description "진행 중"

# 이슈 템플릿 생성
mkdir -p .github/ISSUE_TEMPLATE
```

### Step 3: 초기 이슈 생성
```bash
# 첫 번째 이슈 생성
gh issue create --title "최상위 폴더 구조 정리" \
  --body "중복 파일 정리 및 핵심 구조 확정" \
  --label "epic:architecture,priority:high"
```

## ✅ 완료 체크리스트

### 기본 설정
- [x] 로컬 Git 저장소 초기화
- [x] .gitignore 파일 생성
- [x] 불필요한 파일 정리
- [ ] GitHub 저장소 생성
- [ ] 원격 저장소 연결

### 이슈 시스템
- [ ] 라벨 시스템 구축
- [ ] 이슈 템플릿 생성
- [ ] 프로젝트 보드 설정
- [ ] 마일스톤 생성
- [ ] 초기 이슈 생성

### 프로젝트 관리
- [ ] Phase 1 이슈들 생성
- [ ] 담당자 배정
- [ ] 우선순위 설정
- [ ] 진행 상황 추적 시작

---

**다음 단계**: GitHub CLI로 저장소 생성 및 이슈 시스템 활성화