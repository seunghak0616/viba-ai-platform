# VIBA AI 프로젝트 개발 맥락 정보

## 프로젝트 개요
VIBA AI는 차세대 건축 설계 플랫폼으로, 인공지능과 BIM 기술을 결합한 혁신적인 솔루션입니다.

## 현재까지 완료된 주요 기능들 ✅

### 1. 실시간 WebSocket 통신 구현 (완료)
- 파일: `/backend/websocket_manager.py`
- 기능: Socket.IO를 사용한 실시간 협업, AI 채팅, 프로젝트 알림
- 핵심 클래스: `ConnectionManager`

### 2. UI 자동화 시스템 구축 (완료)  
- 파일: `/tests/ui_automation.py`
- 기능: Playwright를 이용한 E2E 테스트 자동화
- 포함: 로그인, AI 에이전트, 설계 스튜디오, 3D 뷰어, 분석, 협업 테스트

### 3. 자동 데이터 생성기 구현 (완료)
- 파일: `/scripts/auto_data_generator.py`  
- 기능: 테스트용 샘플 데이터 자동 생성
- 포함: 프로젝트, 설계 요청, AI 활동 데이터 생성

### 4. AI 에이전트 백엔드 API 연동 (완료)
- 파일: `/backend/ai_agent_service.py`, `/backend/ai_routes.py`
- 기능: 8개 전문 AI 에이전트 (건축, 구조, 재료, 성능 분석 등)
- 핵심: 채팅 세션, 종합 분석, OpenAI API 연동

### 5. 파일 업로드 및 BIM 처리 시스템 (완료)
- 백엔드: `/backend/file_processor.py`, `/backend/file_routes.py`
- 프론트엔드: `/frontend-react/src/components/FileUpload/FileUpload.tsx`  
- 기능: IFC, DWG, PDF 등 다양한 파일 처리, BIM 데이터 분석
- 포함: 드래그 앤 드롭 업로드, 진행률 표시, 파일 상태 추적

### 6. 사용자 인증 및 권한 관리 강화 (완료)
- 백엔드: `/backend/auth_enhanced.py`, `/backend/auth_routes.py`
- 프론트엔드: `/frontend-react/src/contexts/AuthContext.tsx`, `/frontend-react/src/components/UserManagement/UserManagement.tsx`
- 기능: RBAC (7개 역할), JWT + 리프레시 토큰, 세션 관리, 보안 모니터링
- 역할: 최고관리자, 관리자, 건축사, 엔지니어, 설계자, 클라이언트, 뷰어

## 아키텍처 구조

### 백엔드 (FastAPI)
```
backend/
├── main.py                 # 메인 FastAPI 애플리케이션  
├── auth_enhanced.py        # 강화된 인증 시스템
├── auth_routes.py          # 인증 관련 API 라우터
├── ai_agent_service.py     # AI 에이전트 서비스
├── ai_routes.py           # AI 관련 API 라우터  
├── file_processor.py      # 파일 처리 시스템
├── file_routes.py         # 파일 관련 API 라우터
└── websocket_manager.py   # WebSocket 연결 관리
```

### 프론트엔드 (React + TypeScript)
```
frontend-react/src/
├── components/            # 재사용 가능한 컴포넌트
│   ├── FileUpload/       # 파일 업로드 컴포넌트
│   ├── UserManagement/   # 사용자 관리 컴포넌트
│   └── Layout/          # 레이아웃 컴포넌트
├── pages/               # 페이지 컴포넌트  
│   ├── Dashboard/       # 대시보드
│   ├── Design/         # 설계 스튜디오 (FileUpload 통합됨)
│   ├── Projects/       # 프로젝트 관리
│   └── Auth/          # 인증 페이지
├── contexts/           # React 컨텍스트 (강화된 AuthContext)
└── services/          # API 서비스
```

## 기본 계정 정보
```
최고관리자: superadmin / SuperAdmin123!
관리자: admin / Admin123!  
건축사: architect / Architect123!
엔지니어: engineer / Engineer123!
```

## 테스트 시스템
- 인증 시스템: `python tests/test_auth_enhanced.py`
- 파일 시스템: `python tests/test_file_system.py`  
- UI 자동화: `python tests/ui_automation.py`
- 전체 통합: `python tests/final_integration_test.py`

## 서버 실행 방법
```bash
# 백엔드 (FastAPI)
cd backend && python main.py

# 프론트엔드 (React)  
cd frontend-react && npm start

# 테스트 서버 (통합 테스트용)
python run_test_server.py
```

## 다음 진행 예정 작업 🚧
1. 데이터베이스 스키마 최적화 (다음 단계)
2. 성능 모니터링 및 로깅 시스템  
3. Three.js 기반 3D 뷰어 실제 구현
4. CI/CD 파이프라인 구축

## 중요 참고사항
- 모든 백엔드 API는 `/api/` prefix 사용
- 인증은 JWT Bearer 토큰 + 세션 ID 헤더 사용
- 파일 업로드는 프로젝트별 디렉토리 구조
- WebSocket은 Socket.IO 패턴으로 실시간 통신
- React Context를 통한 전역 상태 관리 (인증, 권한)

## API 엔드포인트 요약

### 인증 API
- `POST /api/auth/login` - 사용자 로그인
- `POST /api/auth/refresh` - 토큰 갱신
- `GET /api/auth/me` - 현재 사용자 정보
- `POST /api/auth/users` - 사용자 생성 (관리자)
- `GET /api/auth/security/stats` - 보안 통계

### AI 에이전트 API
- `POST /api/ai/analyze` - AI 분석 실행
- `POST /api/ai/chat` - AI 채팅
- `GET /api/ai/agents` - 에이전트 목록

### 파일 처리 API
- `POST /api/files/upload/{project_id}` - 파일 업로드
- `GET /api/files/status/{file_id}` - 파일 처리 상태
- `POST /api/files/analyze/bim/{file_id}` - BIM 파일 분석
- `GET /api/files/download/{file_id}` - 파일 다운로드

## 보안 및 권한 시스템

### 사용자 역할 계층구조
1. **최고 관리자 (Super Admin)** - 모든 시스템 권한
2. **관리자 (Admin)** - 사용자 관리 및 시스템 모니터링
3. **건축사 (Architect)** - 프로젝트 관리 및 AI 고급 분석
4. **엔지니어 (Engineer)** - 설계 분석 및 파일 처리
5. **설계자 (Designer)** - 기본 설계 도구 사용
6. **클라이언트 (Client)** - 프로젝트 조회 및 기본 채팅
7. **뷰어 (Viewer)** - 읽기 전용 접근

### 권한 분류
- **프로젝트 권한**: create, read, update, delete, manage
- **파일 권한**: upload, download, delete, analyze
- **AI 권한**: analyze, chat, advanced
- **사용자 권한**: create, read, update, delete, manage
- **시스템 권한**: admin, monitor, config

## 기술 스택

### 백엔드
- **FastAPI** - 고성능 웹 프레임워크
- **Socket.IO** - 실시간 WebSocket 통신
- **JWT + bcrypt** - 보안 인증 시스템
- **Redis** - 세션 관리 (선택사항)
- **OpenAI API** - AI 모델 서비스

### 프론트엔드
- **React + TypeScript** - 타입 안전한 UI 라이브러리
- **Material-UI** - 컴포넌트 디자인 시스템
- **React Context** - 전역 상태 관리
- **Axios** - HTTP 클라이언트

### 테스트 및 자동화
- **Playwright** - E2E 브라우저 테스트
- **Python unittest** - 백엔드 단위 테스트
- **Jest** - 프론트엔드 테스트 (예정)

## 파일 처리 지원 형식

### BIM 파일
- **IFC** (.ifc, .ifcxml) - Building Information Modeling
- **DWG/DXF** (.dwg, .dxf) - AutoCAD 도면 파일

### 문서 파일  
- **PDF** (.pdf) - 설계 도서 및 문서
- **Office** (.doc, .docx, .xlsx, .xls) - 오피스 문서
- **텍스트** (.txt, .csv) - 텍스트 파일

### 미디어 파일
- **이미지** (.jpg, .jpeg, .png, .gif, .bmp) - 설계 이미지
- **압축** (.zip, .rar, .7z) - 압축 파일

## 개발 환경 설정

### 필수 요구사항
- Python 3.8+
- Node.js 16+
- Redis (선택사항, 세션 관리용)
- Git

### 환경 변수
```bash
# 필수
VIBA_SECRET_KEY="your-secret-key"
OPENAI_API_KEY="your-openai-key"  # AI 기능 사용 시

# 선택사항
REDIS_HOST="localhost"
REDIS_PORT=6379
```

### 개발 서버 실행 순서
1. 백엔드 서버 실행: `cd backend && python main.py`
2. 프론트엔드 서버 실행: `cd frontend-react && npm start`
3. 브라우저에서 `http://localhost:3000` 접속
4. 기본 계정으로 로그인하여 테스트

---

**이 파일은 새로운 Claude Code 세션에서 프로젝트 맥락을 이어가기 위한 참조 문서입니다.**