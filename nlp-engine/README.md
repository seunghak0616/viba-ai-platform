# VIBA AI - 차세대 건축 설계 플랫폼 🏗️

VIBA AI는 인공지능과 BIM(Building Information Modeling) 기술을 결합한 혁신적인 건축 설계 플랫폼입니다. 한국어 자연어 처리, 실시간 협업, 파일 처리, 그리고 강화된 보안 시스템을 통해 완전한 건축 설계 솔루션을 제공합니다.

## 🌟 주요 기능

### 🤖 AI 에이전트 시스템
- **8개 전문 AI 에이전트**: 건축 설계, 구조 분석, 재료 선택, 성능 분석 등
- **지능형 오케스트레이터**: 다중 에이전트 협업 및 태스크 관리
- **실시간 설계 분석**: 종합적인 건축 설계 피드백 제공

### 🏢 BIM 및 파일 처리
- **다양한 파일 형식 지원**: IFC, DWG, PDF, 이미지 등
- **자동 BIM 데이터 분석**: 공간 관계, 지속가능성, 비용 분석
- **실시간 파일 처리**: 백그라운드 워커를 통한 비동기 처리

### 🔐 강화된 보안 시스템
- **역할 기반 접근 제어(RBAC)**: 7개 사용자 역할과 세분화된 권한
- **JWT + 리프레시 토큰**: 안전한 인증 및 자동 토큰 갱신
- **세션 관리**: Redis 지원 다중 디바이스 세션 추적
- **보안 모니터링**: 로그인 시도 추적, IP 차단, 감사 로그

### 📱 현대적인 UI/UX
- **React + TypeScript**: 타입 안전한 모던 프론트엔드
- **Material-UI**: 일관성 있는 디자인 시스템
- **실시간 WebSocket 통신**: 즉시 업데이트 및 협업
- **반응형 디자인**: 모든 디바이스에서 최적화된 경험

### 🌐 실시간 협업
- **WebSocket 기반 실시간 통신**: 즉시 프로젝트 업데이트
- **다중 사용자 동시 작업**: 실시간 협업 환경
- **알림 시스템**: 중요 이벤트 즉시 알림

## 🚀 빠른 시작

### 필수 요구사항
- Python 3.8+
- Node.js 16+
- Redis (선택사항, 세션 관리용)

### 1. 저장소 복제
```bash
git clone https://github.com/your-org/viba-ai.git
cd viba-ai
```

### 2. 백엔드 설정
```bash
cd backend
pip install -r requirements.txt

# 환경 변수 설정 (선택사항)
export VIBA_SECRET_KEY="your-secret-key"
export OPENAI_API_KEY="your-openai-key"

# 서버 실행
python main.py
```

### 3. 프론트엔드 설정
```bash
cd frontend-react
npm install
npm start
```

### 4. 테스트 서버 실행 (통합 테스트용)
```bash
python run_test_server.py
```

## 📋 시스템 아키텍처

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
│   ├── Design/         # 설계 스튜디오
│   ├── Projects/       # 프로젝트 관리
│   └── Auth/          # 인증 페이지
├── contexts/           # React 컨텍스트
└── services/          # API 서비스
```

## 🔧 주요 API 엔드포인트

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

## 👥 사용자 역할 및 권한

### 역할 계층구조
1. **최고 관리자 (Super Admin)** - 모든 시스템 권한
2. **관리자 (Admin)** - 사용자 관리 및 시스템 모니터링
3. **건축사 (Architect)** - 프로젝트 관리 및 AI 고급 분석
4. **엔지니어 (Engineer)** - 설계 분석 및 파일 처리
5. **설계자 (Designer)** - 기본 설계 도구 사용
6. **클라이언트 (Client)** - 프로젝트 조회 및 기본 채팅
7. **뷰어 (Viewer)** - 읽기 전용 접근

### 기본 계정 정보
```
최고관리자: superadmin / SuperAdmin123!
관리자: admin / Admin123!
건축사: architect / Architect123!
엔지니어: engineer / Engineer123!
```

## 🧪 테스트

### 단위 테스트 실행
```bash
# 인증 시스템 테스트
python tests/test_auth_enhanced.py

# 파일 시스템 테스트
python tests/test_file_system.py

# AI 에이전트 테스트
python tests/test_korean_processor.py
```

### UI 자동화 테스트
```bash
# Playwright E2E 테스트
python tests/ui_automation.py
```

### 통합 테스트
```bash
# 전체 시스템 테스트
python tests/final_integration_test.py
```

## 📊 모니터링 및 로깅

### 보안 모니터링
- 로그인 시도 추적
- 실패한 인증 시도 자동 차단
- IP 기반 접근 제어
- 세션 활동 모니터링

### 성능 메트릭스
- API 응답 시간
- 파일 처리 성능
- AI 분석 처리 시간
- 동시 사용자 수

## 🔄 CI/CD 파이프라인

### 개발 워크플로우
1. **코드 푸시** → 자동 테스트 실행
2. **테스트 통과** → 스테이징 환경 배포
3. **검증 완료** → 프로덕션 배포
4. **모니터링** → 성능 및 오류 추적

## 📈 로드맵

### 완료된 기능 ✅
- [x] 실시간 WebSocket 통신 구현
- [x] UI 자동화 시스템 구축
- [x] 자동 데이터 생성기 구현
- [x] AI 에이전트 백엔드 API 연동
- [x] 파일 업로드 및 BIM 처리 시스템
- [x] 사용자 인증 및 권한 관리 강화

### 진행 중인 작업 🚧
- [ ] 데이터베이스 스키마 최적화
- [ ] 성능 모니터링 및 로깅 시스템
- [ ] Three.js 기반 3D 뷰어 실제 구현

### 향후 계획 📋
- [ ] CI/CD 파이프라인 구축
- [ ] 마이크로서비스 아키텍처 전환
- [ ] 모바일 앱 개발
- [ ] 클라우드 네이티브 배포

## 🤝 기여하기

1. 저장소를 포크합니다
2. 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🆘 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/your-org/viba-ai/issues)
- **기능 요청**: [Feature Requests](https://github.com/your-org/viba-ai/discussions)
- **문서**: [Wiki](https://github.com/your-org/viba-ai/wiki)

## 🙏 감사의 말

VIBA AI는 다음 오픈소스 프로젝트들의 도움으로 만들어졌습니다:

- **FastAPI** - 고성능 웹 프레임워크
- **React** - 사용자 인터페이스 라이브러리
- **Material-UI** - React 컴포넌트 라이브러리
- **OpenAI API** - AI 모델 서비스
- **Socket.IO** - 실시간 통신
- **Playwright** - 브라우저 자동화 테스트

---

**VIBA AI** - 인공지능으로 건축의 미래를 설계합니다 🚀