# 건축설계이론 및 디자인 프로세스 완전 가이드

**문서 버전**: 1.0  
**최종 업데이트**: 2025.07.06  
**적용 범위**: 바이브 코딩 BIM 플랫폼 건축설계 지식 베이스

---

## 🏛️ 1. 건축설계의 기본 이론

### 1.1 건축의 본질과 정의
```typescript
interface ArchitectureEssence {
  vitruvius: {
    firmitas: "견고함 (Structural Integrity)";    // 구조적 안정성
    utilitas: "기능성 (Functionality)";          // 실용적 목적성
    venustas: "아름다움 (Beauty)";               // 미적 가치
  };
  
  contemporary: {
    sustainability: "지속가능성";                // 환경적 책임
    technology: "기술적 혁신";                  // 디지털 통합
    social: "사회적 가치";                      // 공동체 기여
    economic: "경제적 효율";                    // 비용 효과성
  };
}
```

### 1.2 건축설계의 기본 원리
```json
{
  "design_principles": {
    "proportion": {
      "definition": "부분과 전체 간의 조화로운 관계",
      "methods": [
        "황금비 (Golden Ratio: 1:1.618)",
        "모듈러 시스템 (Modular System)",
        "인체 치수 기반 비례 (Anthropometric Scale)",
        "수학적 비례 체계"
      ],
      "application": {
        "facade": "입면의 수평/수직 분할",
        "spaces": "공간의 길이/폭/높이 비율",
        "elements": "건축 요소의 상대적 크기"
      }
    },
    
    "scale": {
      "definition": "인간과 건축물 간의 크기 관계",
      "types": [
        "인간적 스케일 (Human Scale)",
        "도시적 스케일 (Urban Scale)",
        "기념비적 스케일 (Monumental Scale)",
        "친밀한 스케일 (Intimate Scale)"
      ]
    },
    
    "rhythm": {
      "definition": "건축 요소의 반복과 변화",
      "patterns": [
        "일정한 리듬 (Regular Rhythm)",
        "점진적 리듬 (Progressive Rhythm)",
        "교대 리듬 (Alternating Rhythm)",
        "자유 리듬 (Free Rhythm)"
      ]
    },
    
    "balance": {
      "types": [
        "대칭적 균형 (Symmetrical Balance)",
        "비대칭적 균형 (Asymmetrical Balance)",
        "방사형 균형 (Radial Balance)"
      ]
    },
    
    "unity": {
      "methods": [
        "반복 (Repetition)",
        "연속성 (Continuity)",
        "근접성 (Proximity)",
        "유사성 (Similarity)"
      ]
    }
  }
}
```

---

## 🎨 2. 건축디자인 이론 체계

### 2.1 형태생성 이론 (Form Generation Theory)
```typescript
interface FormGenerationTheory {
  // 기능주의 (Functionalism)
  functionalism: {
    principle: "Form follows function";
    advocates: ["Louis Sullivan", "Adolf Loos", "Le Corbusier"];
    characteristics: [
      "장식의 배제",
      "기능적 요구에 따른 형태",
      "효율성과 실용성 추구",
      "표준화와 모듈화"
    ];
    application: {
      plan: "기능적 조닝과 동선 계획",
      elevation: "내부 기능의 외부 표현",
      structure: "구조 시스템의 솔직한 표현"
    };
  };
  
  // 구조주의 (Structuralism)
  structuralism: {
    principle: "구조가 형태를 결정";
    characteristics: [
      "구조 시스템의 가시화",
      "재료의 본성 존중",
      "구조적 논리성",
      "기술적 표현"
    ];
    examples: [
      "Gothic 건축의 리브 볼트",
      "현대 강구조 건축",
      "케이블 구조 건축"
    ];
  };
  
  // 맥락주의 (Contextualism)
  contextualism: {
    principle: "주변 환경과의 조화";
    considerations: [
      "지역 기후와 환경",
      "문화적 맥락",
      "도시 구조와의 관계",
      "역사적 연속성"
    ];
    strategies: [
      "재료와 색상의 조화",
      "스케일의 연속성",
      "가로 경관과의 호응",
      "지형과의 순응"
    ];
  };
}
```

### 2.2 공간 이론 (Space Theory)
```json
{
  "space_concepts": {
    "functional_space": {
      "definition": "특정 기능을 위한 공간",
      "types": [
        "주 공간 (Primary Space)",
        "보조 공간 (Secondary Space)",
        "서비스 공간 (Service Space)",
        "순환 공간 (Circulation Space)"
      ],
      "planning_principles": [
        "기능별 조닝",
        "효율적 동선",
        "적절한 면적 배분",
        "확장성 고려"
      ]
    },
    
    "perceptual_space": {
      "definition": "인간이 경험하는 공간",
      "qualities": [
        "개방감 vs 폐쇄감",
        "친밀감 vs 장엄감",
        "정적 vs 동적",
        "밝음 vs 어둠"
      ],
      "design_tools": [
        "천장 높이 조절",
        "채광 계획",
        "재료와 색상",
        "가구 배치"
      ]
    },
    
    "transitional_space": {
      "definition": "공간 간 전이 영역",
      "types": [
        "현관 (Entrance)",
        "복도 (Corridor)",
        "로비 (Lobby)",
        "계단실 (Stairwell)",
        "발코니 (Balcony)"
      ],
      "functions": [
        "공간의 위계 형성",
        "프라이버시 조절",
        "환경 완충",
        "동선 안내"
      ]
    }
  }
}
```

### 2.3 조형 언어 (Architectural Language)
```typescript
interface ArchitecturalLanguage {
  // 기본 조형 요소
  basicElements: {
    point: {
      architectural: "기둥, 조명, 포인트 요소";
      effect: "시각적 집중, 방향성 제시";
    };
    line: {
      architectural: "보, 처마, 가로, 세로선";
      effect: "방향성, 연속성, 경계 형성";
    };
    plane: {
      architectural: "벽, 바닥, 천장";
      effect: "공간 구획, 보호, 지지";
    };
    volume: {
      architectural: "방, 홀, 매스";
      effect: "공간 창조, 기능 수용";
    };
  };
  
  // 조형 어휘
  vocabulary: {
    opening: {
      types: ["문", "창", "아치", "보이드"];
      functions: ["접근", "채광", "환기", "시각적 연결"];
    };
    enclosure: {
      types: ["벽", "담", "스크린", "커튼월"];
      functions: ["보호", "프라이버시", "기후 조절"];
    };
    connection: {
      types: ["계단", "경사로", "브릿지", "복도"];
      functions: ["수직 동선", "수평 동선", "공간 연결"];
    };
  };
}
```

---

## 📐 3. 설계 프로세스 (Design Process)

### 3.1 설계 단계별 프로세스
```typescript
interface DesignProcess {
  // 1단계: 프로그래밍 (Programming)
  programming: {
    duration: "2-4주";
    activities: [
      "클라이언트 요구사항 분석",
      "부지 조사 및 분석",
      "법규 검토",
      "예산 및 일정 수립",
      "설계 목표 설정"
    ];
    deliverables: [
      "프로그램 보고서",
      "부지 분석도",
      "법규 검토서",
      "프로젝트 일정표"
    ];
  };
  
  // 2단계: 개념설계 (Schematic Design)
  schematicDesign: {
    duration: "3-6주";
    activities: [
      "디자인 컨셉 개발",
      "매스 스터디",
      "배치 계획",
      "기본 평면 구성",
      "구조 시스템 검토"
    ];
    deliverables: [
      "컨셉 다이어그램",
      "매스 모델",
      "기본 도면 (1/200~1/500)",
      "3D 스케치"
    ];
    lod: "LOD 100";
  };
  
  // 3단계: 기본설계 (Design Development)
  designDevelopment: {
    duration: "4-8주";
    activities: [
      "상세 평면 개발",
      "입면 및 단면 개발",
      "구조 시스템 확정",
      "MEP 시스템 기본 계획",
      "재료 및 마감재 선정"
    ];
    deliverables: [
      "기본설계도면 (1/100~1/200)",
      "구조 계획도",
      "설비 계획도",
      "재료 및 색상 계획"
    ];
    lod: "LOD 200-300";
  };
  
  // 4단계: 실시설계 (Construction Documents)
  constructionDocuments: {
    duration: "6-12주";
    activities: [
      "시공 상세도 작성",
      "구조 설계 완료",
      "설비 설계 완료",
      "시방서 작성",
      "수량 산출"
    ];
    deliverables: [
      "실시설계도면 (1/50~1/100)",
      "상세도 (1/10~1/50)",
      "시방서",
      "수량 내역서"
    ];
    lod: "LOD 400";
  };
  
  // 5단계: 시공관리 (Construction Administration)
  constructionAdministration: {
    duration: "시공 기간";
    activities: [
      "시공 검토 및 승인",
      "현장 감리",
      "변경 설계",
      "준공 검사"
    ];
    deliverables: [
      "시공 승인도",
      "변경 설계도",
      "준공도면",
      "사용 설명서"
    ];
    lod: "LOD 500";
  };
}
```

### 3.2 설계 방법론 (Design Methodology)
```json
{
  "design_methods": {
    "analytical_method": {
      "description": "논리적 분석을 통한 설계",
      "process": [
        "문제 정의 및 분석",
        "조건 및 제약 파악",
        "대안 개발 및 평가",
        "최적안 선택 및 개발"
      ],
      "tools": [
        "기능 분석도",
        "관계 다이어그램",
        "매트릭스 분석",
        "의사결정 트리"
      ]
    },
    
    "intuitive_method": {
      "description": "직관과 경험을 통한 설계",
      "process": [
        "영감과 아이디어 발상",
        "스케치와 모델링",
        "시행착오를 통한 발전",
        "감성적 검증"
      ],
      "tools": [
        "프리핸드 스케치",
        "개념 모델",
        "콜라주",
        "무드보드"
      ]
    },
    
    "parametric_method": {
      "description": "매개변수 기반 설계",
      "process": [
        "설계 변수 정의",
        "관계식 설정",
        "알고리즘 개발",
        "최적화 실행"
      ],
      "tools": [
        "Grasshopper",
        "Dynamo",
        "Genetic Algorithm",
        "Machine Learning"
      ]
    }
  }
}
```

---

## 🏗️ 4. 공간 계획 이론

### 4.1 공간 구성 원리
```typescript
interface SpacePlanningPrinciples {
  // 조닝 (Zoning)
  zoning: {
    definition: "기능별 공간 영역 구분";
    types: {
      public: "공적 영역 (로비, 홀, 상점)";
      semipublic: "반공적 영역 (회의실, 식당)";
      private: "사적 영역 (사무실, 침실)";
      service: "서비스 영역 (화장실, 창고, 기계실)";
    };
    principles: [
      "유사 기능의 집약",
      "상충 기능의 분리",
      "접근성 위계",
      "확장성 고려"
    ];
  };
  
  // 동선 계획 (Circulation)
  circulation: {
    definition: "사람과 물건의 이동 경로";
    types: {
      primary: "주 동선 - 주요 목적지 연결";
      secondary: "보조 동선 - 부차적 연결";
      service: "서비스 동선 - 관리/유지보수";
      emergency: "비상 동선 - 피난 경로";
    };
    design_criteria: [
      "최단 거리",
      "명확한 방향성",
      "적절한 폭",
      "안전성 확보"
    ];
  };
  
  // 영역성 (Territoriality)
  territoriality: {
    definition: "공간의 소유와 통제 감각";
    levels: {
      personal: "개인 공간 (1.5m 반경)";
      small_group: "소그룹 공간 (3-4명)";
      large_group: "대그룹 공간 (10명 이상)";
      public: "공공 공간 (불특정 다수)";
    };
    design_strategies: [
      "시각적 차단",
      "레벨 차이",
      "재료 변화",
      "가구 배치"
    ];
  };
}
```

### 4.2 용도별 공간 계획
```json
{
  "space_planning_by_use": {
    "residential": {
      "dwelling_types": [
        "단독주택 (Detached House)",
        "연립주택 (Townhouse)", 
        "공동주택 (Apartment)",
        "원룸/스튜디오 (Studio)"
      ],
      "space_organization": {
        "public_zone": ["거실", "식당", "부엌"],
        "private_zone": ["침실", "서재", "옷방"],
        "service_zone": ["화장실", "세탁실", "창고"],
        "circulation": ["현관", "복도", "계단"]
      },
      "design_considerations": [
        "가족 구성원별 프라이버시",
        "생활 패턴과 동선",
        "자연 채광과 환기",
        "수납 공간 확보"
      ]
    },
    
    "office": {
      "office_types": [
        "셀룰러 오피스 (Cellular Office)",
        "오픈 플랜 (Open Plan)",
        "컴비네이션 (Combination)",
        "코워킹 스페이스 (Co-working)"
      ],
      "space_standards": {
        "executive": "20-25㎡/인",
        "manager": "15-20㎡/인",
        "staff": "6-12㎡/인",
        "workstation": "4-8㎡/인"
      },
      "support_spaces": [
        "회의실 (Meeting Room)",
        "휴게실 (Break Room)",
        "파일실 (File Room)",
        "복사실 (Copy Room)",
        "서버실 (Server Room)"
      ]
    },
    
    "retail": {
      "store_types": [
        "백화점 (Department Store)",
        "쇼핑센터 (Shopping Mall)",
        "전문점 (Specialty Store)",
        "슈퍼마켓 (Supermarket)"
      ],
      "layout_strategies": {
        "grid": "격자형 - 효율적 진열",
        "racetrack": "순환형 - 고객 유도",
        "free_flow": "자유형 - 브라우징 유도",
        "boutique": "부티크형 - 고급 이미지"
      },
      "design_factors": [
        "고객 동선 유도",
        "상품 진열 효과",
        "계산대 위치",
        "창고 접근성"
      ]
    }
  }
}
```

---

## 🌿 5. 지속가능한 설계 이론

### 5.1 환경 친화적 설계 원리
```typescript
interface SustainableDesign {
  // 패시브 디자인 (Passive Design)
  passiveDesign: {
    principles: {
      orientation: "건물 배치와 향";
      naturalVentilation: "자연 환기";
      daylighting: "자연 채광";
      thermalMass: "축열";
      shading: "차양";
      insulation: "단열";
    };
    
    strategies: {
      summer: [
        "태양열 차단",
        "자연 환기 촉진",
        "증발 냉각 활용",
        "야간 복사 냉각"
      ],
      winter: [
        "태양열 획득",
        "열손실 방지",
        "축열체 활용",
        "바람막이"
      ],
      transition: [
        "가변형 차양",
        "자연 환기 조절",
        "중간기 대응"
      ]
    };
  };
  
  // 능동적 시스템 (Active Systems)
  activeSystems: {
    renewable: [
      "태양광 발전 (Photovoltaic)",
      "태양열 집열 (Solar Thermal)",
      "지열 이용 (Geothermal)",
      "풍력 발전 (Wind Power)"
    ];
    efficient: [
      "고효율 HVAC 시스템",
      "LED 조명",
      "스마트 제어 시스템",
      "에너지 회수 환기"
    ];
  };
  
  // 물 순환 시스템
  waterManagement: {
    conservation: [
      "절수 기기 사용",
      "우수 집수",
      "중수 재이용",
      "투수성 포장"
    ];
    treatment: [
      "자연 정화 시설",
      "습지 시스템",
      "바이오 스웨일"
    ];
  };
}
```

### 5.2 인증 시스템 및 평가 도구
```json
{
  "certification_systems": {
    "leed": {
      "organization": "미국 그린빌딩협회 (USGBC)",
      "categories": [
        "지속가능한 부지 (Sustainable Sites)",
        "물 효율성 (Water Efficiency)",
        "에너지와 대기 (Energy & Atmosphere)",
        "재료와 자원 (Materials & Resources)",
        "실내 환경 품질 (Indoor Environmental Quality)",
        "혁신과 디자인 (Innovation & Design)"
      ],
      "levels": ["Certified", "Silver", "Gold", "Platinum"]
    },
    
    "breeam": {
      "organization": "영국건축연구소 (BRE)",
      "categories": [
        "관리 (Management)",
        "건강과 웰빙 (Health & Wellbeing)",
        "에너지 (Energy)",
        "교통 (Transport)",
        "물 (Water)",
        "재료 (Materials)",
        "폐기물 (Waste)",
        "토지 이용과 생태 (Land Use & Ecology)",
        "오염 (Pollution)"
      ]
    },
    
    "g_seed": {
      "organization": "한국녹색건축인증원",
      "categories": [
        "토지이용 및 교통",
        "에너지 및 환경오염",
        "재료 및 자원",
        "물 순환 관리",
        "유지관리",
        "생태환경",
        "실내환경"
      ]
    }
  }
}
```

---

## 🎭 6. 건축 스타일과 사조

### 6.1 역사적 건축 양식
```typescript
interface ArchitecturalStyles {
  // 고전 건축
  classical: {
    greek: {
      period: "기원전 8-1세기";
      characteristics: [
        "주범식 구조",
        "삼각 페디먼트",
        "도릭/이오닉/코린트 오더",
        "비례와 조화"
      ];
      examples: ["파르테논 신전", "에렉테이온"];
    };
    roman: {
      period: "기원전 1세기-서기 5세기";
      characteristics: [
        "아치와 돔",
        "콘크리트 사용",
        "대공간 창조",
        "실용성 추구"
      ];
      examples: ["판테온", "콜로세움"];
    };
  };
  
  // 중세 건축
  medieval: {
    romanesque: {
      period: "10-12세기";
      characteristics: [
        "두꺼운 벽",
        "반원 아치",
        "작은 창",
        "견고한 외관"
      ];
    };
    gothic: {
      period: "12-16세기";
      characteristics: [
        "첨탑",
        "플라잉 버트레스",
        "스테인드글라스",
        "수직성 강조"
      ];
      examples: ["노트르담", "샤르트르 대성당"];
    };
  };
  
  // 근세 건축
  renaissance: {
    period: "15-17세기";
    characteristics: [
      "고전적 비례",
      "대칭성",
      "원근법",
      "인문주의"
    ];
    key_figures: ["브루넬레스키", "팔라디오"];
  };
  
  baroque: {
    period: "17-18세기";
    characteristics: [
      "곡선과 장식",
      "극적 효과",
      "빛과 그림자",
      "감정적 표현"
    ];
  };
}
```

### 6.2 근현대 건축 사조
```json
{
  "modern_movements": {
    "art_nouveau": {
      "period": "1890-1914",
      "characteristics": [
        "자연적 형태",
        "곡선적 장식",
        "새로운 재료",
        "전체적 디자인"
      ],
      "key_figures": ["안토니 가우디", "빅터 오르타"]
    },
    
    "bauhaus": {
      "period": "1919-1933",
      "principles": [
        "기능성 추구",
        "형태의 단순화",
        "대량생산 적합",
        "예술과 기술의 통합"
      ],
      "key_figures": ["발터 그로피우스", "미스 반 데어 로에"]
    },
    
    "international_style": {
      "period": "1920-1970",
      "characteristics": [
        "기능주의",
        "장식의 배제",
        "수평창",
        "플랫 루프",
        "자유로운 평면"
      ],
      "key_figures": ["르 코르뷔지에", "미스 반 데어 로에"]
    },
    
    "postmodernism": {
      "period": "1960-1990",
      "characteristics": [
        "역사적 참조",
        "상징과 의미",
        "절충주의",
        "맥락주의"
      ],
      "key_figures": ["로버트 벤투리", "찰스 무어"]
    },
    
    "deconstructivism": {
      "period": "1980-현재",
      "characteristics": [
        "형태의 해체",
        "비선형성",
        "충돌과 모순",
        "불안정성"
      ],
      "key_figures": ["프랭크 게리", "자하 하디드"]
    }
  }
}
```

---

## 🔬 7. 건축 심리학과 행동 이론

### 7.1 환경 심리학 (Environmental Psychology)
```typescript
interface EnvironmentalPsychology {
  // 공간 인지
  spatialCognition: {
    wayfinding: {
      definition: "공간에서 길찾기 능력";
      factors: [
        "공간의 가독성",
        "이정표 (Landmark)",
        "경로의 연속성",
        "공간의 차별성"
      ];
      design_strategies: [
        "명확한 동선 체계",
        "시각적 이정표",
        "공간별 특성 부여",
        "적절한 사인 시스템"
      ];
    };
    
    personalSpace: {
      definition: "개인이 필요로 하는 공간";
      distances: {
        intimate: "0-45cm - 가족, 연인";
        personal: "45-120cm - 친구, 동료";
        social: "120-360cm - 업무, 공식 관계";
        public: "360cm+ - 공개 연설, 공연";
      };
    };
    
    territoriality: {
      definition: "공간에 대한 소유감";
      types: [
        "1차 영역 - 개인 전용 공간",
        "2차 영역 - 집단 공유 공간",
        "3차 영역 - 공공 임시 사용"
      ];
    };
  };
  
  // 환경 스트레스
  environmentalStress: {
    factors: {
      crowding: "과밀 - 개인 공간 침해";
      noise: "소음 - 청각적 불쾌감";
      air_quality: "공기질 - 건강과 쾌적성";
      lighting: "조명 - 시각적 피로";
      temperature: "온도 - 열적 불쾌감";
    };
    
    design_responses: [
      "적절한 공간 밀도",
      "소음 차단과 흡음",
      "자연 환기 시스템",
      "자연광 활용",
      "열환경 조절"
    ];
  };
}
```

### 7.2 색채 심리학 (Color Psychology)
```json
{
  "color_psychology": {
    "warm_colors": {
      "red": {
        "psychological_effects": ["열정", "에너지", "자극", "주의"],
        "physical_effects": ["맥박 증가", "체온 상승", "식욕 증진"],
        "applications": ["레스토랑", "피트니스", "소매점"]
      },
      "orange": {
        "psychological_effects": ["활기", "창의성", "친근감", "따뜻함"],
        "applications": ["카페", "놀이 공간", "크리에이티브 오피스"]
      },
      "yellow": {
        "psychological_effects": ["명랑", "집중", "낙관", "경계"],
        "applications": ["학습 공간", "어린이 시설", "사인"]
      }
    },
    
    "cool_colors": {
      "blue": {
        "psychological_effects": ["평온", "신뢰", "안정", "집중"],
        "physical_effects": ["혈압 감소", "심박 안정", "체온 감소"],
        "applications": ["사무실", "의료시설", "침실"]
      },
      "green": {
        "psychological_effects": ["자연", "균형", "안정", "회복"],
        "applications": ["병원", "휴게실", "명상 공간"]
      },
      "purple": {
        "psychological_effects": ["고급", "신비", "창의", "명상"],
        "applications": ["스파", "갤러리", "프리미엄 공간"]
      }
    },
    
    "neutral_colors": {
      "white": {
        "effects": ["순수", "깨끗", "넓음", "미니멀"],
        "applications": ["의료시설", "갤러리", "모던 공간"]
      },
      "gray": {
        "effects": ["안정", "중성", "전문적", "현대적"],
        "applications": ["사무실", "전시 공간", "배경색"]
      },
      "brown": {
        "effects": ["안정", "자연", "전통", "편안함"],
        "applications": ["주거 공간", "카페", "전통 건축"]
      }
    }
  }
}
```

---

## 🌍 8. 문화와 지역성

### 8.1 기후와 건축
```typescript
interface ClimateResponsiveDesign {
  // 열대 기후
  tropical: {
    characteristics: [
      "고온 다습",
      "강우량 많음",
      "태양 고도 높음"
    ];
    strategies: [
      "높은 천장",
      "큰 처마",
      "자연 환기",
      "투수성 재료",
      "stilts/기둥"
    ];
    examples: ["말레이시아 전통 가옥", "태국 스틸트 하우스"];
  };
  
  // 온대 기후
  temperate: {
    characteristics: [
      "사계절 구분",
      "적당한 강우",
      "온도 변화 큼"
    ];
    strategies: [
      "단열 강화",
      "계절별 대응",
      "적절한 개구부",
      "축열체 활용"
    ];
    examples: ["한국 한옥", "독일 패시브 하우스"];
  };
  
  // 건조 기후
  arid: {
    characteristics: [
      "높은 일교차",
      "강한 일사",
      "낮은 습도"
    ];
    strategies: [
      "두꺼운 벽체",
      "작은 개구부",
      "중정",
      "축열과 야간 냉각"
    ];
    examples: ["모로코 리아드", "이란 전통 건축"];
  };
  
  // 한랭 기후
  cold: {
    characteristics: [
      "긴 겨울",
      "강설",
      "강풍"
    ];
    strategies: [
      "최대 단열",
      "컴팩트한 형태",
      "남향 배치",
      "방풍벽"
    ];
    examples: ["이누이트 이글루", "스칸디나비아 건축"];
  };
}
```

### 8.2 한국 전통 건축의 특성
```json
{
  "korean_traditional": {
    "philosophical_basis": {
      "yin_yang": "음양론 - 대립과 조화",
      "five_elements": "오행설 - 목화토금수",
      "feng_shui": "풍수지리 - 자연과의 조화",
      "confucianism": "유교 - 사회적 위계와 예절"
    },
    
    "spatial_characteristics": {
      "courtyard": {
        "name": "마당",
        "functions": ["작업 공간", "의례 공간", "채광과 환기", "자연 도입"]
      },
      "ondol": {
        "name": "온돌",
        "system": "바닥 복사 난방",
        "materials": ["구들장", "황토", "연도"]
      },
      "daecheong": {
        "name": "대청",
        "function": "여름철 시원한 공간",
        "features": ["높은 천장", "통풍", "우물마루"]
      }
    },
    
    "construction_system": {
      "mokguri": {
        "name": "목구조",
        "joints": ["짜임", "맞춤", "이음"],
        "no_nails": "철물 사용 최소화"
      },
      "dancheong": {
        "name": "단청",
        "purpose": ["목재 보호", "장식", "권위 표현"],
        "colors": ["청(靑)", "적(赤)", "황(黃)", "백(白)", "흑(黑)"]
      }
    },
    
    "design_principles": {
      "asymmetry": "비대칭의 균형",
      "naturalness": "자연스러움",
      "modesty": "검소함과 절제",
      "harmony": "주변과의 조화"
    }
  }
}
```

---

## 💡 9. 현대 건축의 새로운 패러다임

### 9.1 디지털 건축 (Digital Architecture)
```typescript
interface DigitalArchitecture {
  // 파라메트릭 디자인
  parametricDesign: {
    definition: "매개변수와 알고리즘을 이용한 설계";
    tools: ["Grasshopper", "Dynamo", "Generative Components"];
    advantages: [
      "복잡한 형태 구현",
      "변수 변경으로 즉시 수정",
      "성능 최적화",
      "대안 비교 용이"
    ];
    applications: [
      "자유곡면 건축",
      "구조 최적화",
      "환경 성능 분석",
      "제조와 시공"
    ];
  };
  
  // 생성형 디자인
  generativeDesign: {
    definition: "AI와 알고리즘이 설계안을 생성";
    process: [
      "목표와 제약 조건 설정",
      "알고리즘 실행",
      "다수 대안 생성",
      "최적안 선택"
    ];
    benefits: [
      "인간이 생각하지 못한 솔루션",
      "성능 최적화",
      "시간 단축",
      "객관적 평가"
    ];
  };
  
  // 가상/증강 현실
  vrAr: {
    vr: {
      applications: [
        "설계 검토",
        "공간 체험",
        "클라이언트 프레젠테이션",
        "시공 시뮬레이션"
      ];
    };
    ar: {
      applications: [
        "현장 정보 오버레이",
        "시공 가이드",
        "유지보수 지원",
        "교육과 훈련"
      ];
    };
  };
}
```

### 9.2 스마트 건축 (Smart Building)
```json
{
  "smart_building": {
    "iot_integration": {
      "sensors": [
        "온습도 센서",
        "조도 센서", 
        "공기질 센서",
        "동작 감지 센서",
        "에너지 모니터링"
      ],
      "controls": [
        "HVAC 자동 제어",
        "조명 자동 조절",
        "보안 시스템",
        "화재 감지",
        "에너지 관리"
      ]
    },
    
    "ai_integration": {
      "machine_learning": [
        "사용 패턴 학습",
        "에너지 사용 예측",
        "유지보수 예측",
        "보안 위험 감지"
      ],
      "optimization": [
        "에너지 효율 최적화",
        "공간 사용 최적화", 
        "유지보수 일정 최적화",
        "사용자 경험 개선"
      ]
    },
    
    "sustainability": {
      "energy_management": [
        "실시간 에너지 모니터링",
        "피크 수요 관리",
        "재생에너지 통합",
        "에너지 저장 시스템"
      ],
      "resource_efficiency": [
        "물 사용량 모니터링",
        "폐기물 관리",
        "실내 공기질 관리",
        "탄소 발자국 추적"
      ]
    }
  }
}
```

---

## 📚 10. 참고 문헌 및 자료

### 10.1 필수 도서
```yaml
기본_이론서:
  - "건축 공간론" - 하세가와 아이
  - "건축의 복잡성과 대립성" - 로버트 벤투리
  - "패턴 랭귀지" - 크리스토퍼 알렉산더
  - "건축을 향하여" - 르 코르뷔지에
  - "건축학개론" - 김광현

역사_이론서:
  - "서양건축사" - 니콜라우스 페브스너
  - "한국건축사" - 신영훈
  - "현대건축사" - 케네스 프램튼
  - "20세기 건축" - 피터 베하리

실무_기술서:
  - "건축계획론" - 일본건축학회
  - "건축환경계획" - 빅터 올가이
  - "시간 설계자 디자인" - 팀 브라운
  - "지속가능한 건축" - 브라이언 에드워즈
```

### 10.2 온라인 자료
```typescript
const onlineResources = {
  academicJournals: [
    "Architectural Review",
    "Domus",
    "GA Document", 
    "대한건축학회논문집",
    "건축"
  ],
  
  websites: [
    "ArchDaily - 건축 뉴스와 프로젝트",
    "Dezeen - 디자인과 건축",
    "Detail - 건축 상세 정보",
    "buildingSMART - BIM 표준",
    "한국건축가협회"
  ],
  
  databases: [
    "Avery Index to Architectural Periodicals",
    "Art Index",
    "국가건축정책위원회 자료실",
    "건축도시연구정보센터"
  ]
};
```

---

**이 가이드는 건축설계와 디자인 이론의 포괄적 지식 베이스로, 바이브 코딩 BIM 플랫폼의 건축 전문성 강화를 위한 참고 자료입니다.**

**지속적인 업데이트를 통해 최신 건축 이론과 실무 지식을 반영해 나가겠습니다.**

---

*© 2025 바이브 코딩 BIM 플랫폼. All rights reserved.*