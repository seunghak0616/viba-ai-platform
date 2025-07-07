/**
 * OpenAI Service
 * OpenAI API를 사용한 자연어 처리 서비스
 */
import OpenAI from 'openai';
import config from '../config/index.js';
import logger from '../utils/logger.js';

class OpenAIService {
  constructor() {
    if (!config.openai.apiKey) {
      logger.warn('OpenAI API 키가 설정되지 않았습니다. 모의 응답을 사용합니다.');
      this.mockMode = true;
      this.openai = null;
    } else {
      this.mockMode = false;
      this.openai = new OpenAI({
        apiKey: config.openai.apiKey,
      });
    }
  }

  /**
   * 자연어 입력을 BIM 파라미터로 변환
   * @param {string} naturalLanguageInput - 자연어 입력
   * @param {string} language - 언어 코드 (ko, en)
   * @returns {Object} 변환된 BIM 파라미터
   */
  async convertToBIMParameters(naturalLanguageInput, language = 'ko') {
    try {
      if (this.mockMode) {
        return this._getMockBIMParameters(naturalLanguageInput);
      }

      const prompt = this._createBIMParameterPrompt(naturalLanguageInput, language);
      
      logger.nlp('OpenAI API 호출 시작', {
        inputLength: naturalLanguageInput.length,
        language,
        model: config.openai.model
      });

      const completion = await this.openai.chat.completions.create({
        model: config.openai.model,
        messages: [
          {
            role: "system",
            content: "당신은 건축 BIM 전문가입니다. 자연어 입력을 정확한 BIM 파라미터로 변환해주세요."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: config.openai.temperature,
        max_tokens: config.openai.maxTokens,
        response_format: { type: "json_object" }
      });

      const responseText = completion.choices[0].message.content;

      logger.nlp('OpenAI API 응답 수신', {
        responseLength: responseText.length,
        inputPreview: naturalLanguageInput.substring(0, 50)
      });

      // JSON 응답 파싱
      try {
        const bimParameters = JSON.parse(responseText);
        return this._validateAndNormalizeBIMParameters(bimParameters);
      } catch (parseError) {
        logger.error('OpenAI 응답 JSON 파싱 실패', {
          error: parseError.message,
          rawResponse: responseText
        });
        // 파싱 실패시 기본 분석으로 폴백
        return this._getFallbackBIMParameters(naturalLanguageInput);
      }

    } catch (error) {
      logger.error('OpenAI API 호출 실패', {
        error: error.message,
        stack: error.stack
      });
      // API 실패시 기본 분석으로 폴백
      return this._getFallbackBIMParameters(naturalLanguageInput);
    }
  }

  /**
   * BIM 설계 검증 및 개선 제안
   * @param {Object} bimData - BIM 데이터
   * @param {string} language - 언어 코드
   * @returns {Object} 검증 결과 및 개선 제안
   */
  async validateAndOptimizeBIM(bimData, language = 'ko') {
    try {
      if (this.mockMode) {
        return this._getMockValidationResult(bimData);
      }

      const prompt = this._createValidationPrompt(bimData, language);
      
      const completion = await this.openai.chat.completions.create({
        model: config.openai.model,
        messages: [
          {
            role: "system",
            content: "당신은 건축 설계 검증 전문가입니다. BIM 데이터를 분석하여 타당성을 검증하고 개선안을 제시해주세요."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: config.openai.temperature,
        max_tokens: config.openai.maxTokens,
        response_format: { type: "json_object" }
      });

      const responseText = completion.choices[0].message.content;

      try {
        const validationResult = JSON.parse(responseText);
        return this._normalizeValidationResult(validationResult);
      } catch (parseError) {
        logger.error('검증 결과 JSON 파싱 실패', {
          error: parseError.message,
          rawResponse: responseText
        });
        return this._getMockValidationResult(bimData);
      }

    } catch (error) {
      logger.error('BIM 검증 API 호출 실패', {
        error: error.message,
        stack: error.stack
      });
      return this._getMockValidationResult(bimData);
    }
  }

  /**
   * 자연어 설명 생성
   * @param {Object} bimData - BIM 데이터
   * @param {string} language - 언어 코드
   * @returns {string} 자연어 설명
   */
  async generateDescription(bimData, language = 'ko') {
    try {
      if (this.mockMode) {
        return this._getMockDescription(bimData);
      }

      const prompt = this._createDescriptionPrompt(bimData, language);
      
      const completion = await this.openai.chat.completions.create({
        model: config.openai.model,
        messages: [
          {
            role: "system",
            content: "당신은 건축 설명 전문가입니다. BIM 데이터를 바탕으로 자연스러운 건물 설명을 작성해주세요."
          },
          {
            role: "user",
            content: prompt
          }
        ],
        temperature: config.openai.temperature,
        max_tokens: 500
      });

      return completion.choices[0].message.content.trim();

    } catch (error) {
      logger.error('설명 생성 API 호출 실패', {
        error: error.message,
        stack: error.stack
      });
      return this._getMockDescription(bimData);
    }
  }

  /**
   * BIM 파라미터 변환을 위한 프롬프트 생성
   */
  _createBIMParameterPrompt(input, language) {
    const promptTemplates = {
      ko: `
다음 자연어 입력을 분석하여 BIM(Building Information Modeling) 파라미터로 변환해주세요.

입력: "${input}"

다음 JSON 형식으로 응답해주세요:
{
  "buildingType": "건물 유형 (RESIDENTIAL/COMMERCIAL/OFFICE/INDUSTRIAL/PUBLIC)",
  "totalArea": {
    "value": 숫자,
    "unit": "단위 (평/㎡)",
    "confidence": 0.0-1.0
  },
  "rooms": [
    {
      "type": "방 종류",
      "count": 개수,
      "area": 면적,
      "orientation": "방향",
      "requirements": ["요구사항1", "요구사항2"]
    }
  ],
  "style": {
    "architectural": "건축 스타일",
    "interior": "인테리어 스타일",
    "keywords": ["키워드1", "키워드2"]
  },
  "location": {
    "address": "주소",
    "region": "지역",
    "climate": "기후 조건"
  },
  "constraints": {
    "budget": "예산 관련",
    "timeline": "일정 관련",
    "regulations": ["법규1", "법규2"]
  },
  "extractedFeatures": {
    "orientations": ["방향1", "방향2"],
    "roomTypes": ["방타입1", "방타입2"],
    "areaKeywords": ["면적키워드1"],
    "buildingKeywords": ["건물키워드1"],
    "styleKeywords": ["스타일키워드1"]
  },
  "confidence": 0.0-1.0,
  "suggestedName": "프로젝트 제안 이름",
  "description": "상세 설명"
}

주의사항:
- 명시되지 않은 정보는 null 또는 빈 배열로 설정
- confidence는 추출된 정보의 확실성을 나타냄
- 모든 숫자는 정수로 반환
- 면적 단위는 입력에서 추출하되, 없으면 "평" 사용
- 응답은 반드시 유효한 JSON 형식이어야 함
`,
      en: `
Analyze the following natural language input and convert it to BIM (Building Information Modeling) parameters.

Input: "${input}"

Please respond in the following JSON format:
{
  "buildingType": "Building type (RESIDENTIAL/COMMERCIAL/OFFICE/INDUSTRIAL/PUBLIC)",
  "totalArea": {
    "value": number,
    "unit": "unit (sqft/sqm)",
    "confidence": 0.0-1.0
  },
  "rooms": [
    {
      "type": "room type",
      "count": number,
      "area": area,
      "orientation": "orientation",
      "requirements": ["requirement1", "requirement2"]
    }
  ],
  "style": {
    "architectural": "architectural style",
    "interior": "interior style", 
    "keywords": ["keyword1", "keyword2"]
  },
  "location": {
    "address": "address",
    "region": "region",
    "climate": "climate conditions"
  },
  "constraints": {
    "budget": "budget related",
    "timeline": "timeline related",
    "regulations": ["regulation1", "regulation2"]
  },
  "extractedFeatures": {
    "orientations": ["orientation1", "orientation2"],
    "roomTypes": ["roomtype1", "roomtype2"],
    "areaKeywords": ["areakeyword1"],
    "buildingKeywords": ["buildingkeyword1"],
    "styleKeywords": ["stylekeyword1"]
  },
  "confidence": 0.0-1.0,
  "suggestedName": "suggested project name",
  "description": "detailed description"
}

Notes:
- Set unspecified information to null or empty arrays
- confidence represents certainty of extracted information
- All numbers should be integers
- Use area unit from input, default to "sqft" if not specified
- Response must be valid JSON format
`
    };

    return promptTemplates[language] || promptTemplates.ko;
  }

  /**
   * BIM 검증을 위한 프롬프트 생성
   */
  _createValidationPrompt(bimData, language) {
    const promptTemplates = {
      ko: `
다음 BIM 데이터를 분석하여 설계의 타당성을 검증하고 개선 제안을 해주세요.

BIM 데이터:
${JSON.stringify(bimData, null, 2)}

다음 JSON 형식으로 응답해주세요:
{
  "isValid": true/false,
  "score": 0-100,
  "issues": [
    {
      "type": "문제 유형",
      "severity": "low/medium/high",
      "message": "문제 설명",
      "location": "문제 위치"
    }
  ],
  "suggestions": [
    {
      "type": "개선 유형",
      "priority": "low/medium/high",
      "message": "개선 제안",
      "expectedBenefit": "예상 효과"
    }
  ],
  "compliance": {
    "buildingCode": true/false,
    "fireCode": true/false,
    "accessibilityCode": true/false,
    "energyCode": true/false
  },
  "efficiency": {
    "spaceUtilization": 0-100,
    "circulation": 0-100,
    "lighting": 0-100,
    "ventilation": 0-100
  },
  "cost": {
    "estimatedRange": "예상 비용 범위",
    "costPerArea": "단위면적당 비용",
    "savings": ["절약 방안1", "절약 방안2"]
  }
}`,
      en: `
Analyze the following BIM data to validate the design feasibility and provide improvement suggestions.

BIM Data:
${JSON.stringify(bimData, null, 2)}

Please respond in the following JSON format:
{
  "isValid": true/false,
  "score": 0-100,
  "issues": [
    {
      "type": "issue type",
      "severity": "low/medium/high", 
      "message": "issue description",
      "location": "issue location"
    }
  ],
  "suggestions": [
    {
      "type": "improvement type",
      "priority": "low/medium/high",
      "message": "improvement suggestion",
      "expectedBenefit": "expected benefit"
    }
  ],
  "compliance": {
    "buildingCode": true/false,
    "fireCode": true/false,
    "accessibilityCode": true/false,
    "energyCode": true/false
  },
  "efficiency": {
    "spaceUtilization": 0-100,
    "circulation": 0-100,
    "lighting": 0-100,
    "ventilation": 0-100
  },
  "cost": {
    "estimatedRange": "estimated cost range",
    "costPerArea": "cost per unit area",
    "savings": ["saving method1", "saving method2"]
  }
}`
    };

    return promptTemplates[language] || promptTemplates.ko;
  }

  /**
   * 설명 생성을 위한 프롬프트 생성
   */
  _createDescriptionPrompt(bimData, language) {
    const promptTemplates = {
      ko: `
다음 BIM 데이터를 바탕으로 건물에 대한 자연스러운 설명을 생성해주세요.

BIM 데이터:
${JSON.stringify(bimData, null, 2)}

요구사항:
- 일반인이 이해하기 쉬운 자연스러운 한국어로 작성
- 건물의 주요 특징과 공간 구성을 중심으로 설명
- 200-300자 정도의 적당한 길이
- 건축 전문용어는 최소화하고 일상 용어 사용

예시 형식:
"이 건물은 [특징]한 [건물유형]으로, 총 [면적]의 공간에 [주요공간들]이 효율적으로 배치되어 있습니다. [특별한 장점이나 특징]하여 [사용목적]에 최적화된 설계입니다."`,
      en: `
Generate a natural description of the building based on the following BIM data.

BIM Data:
${JSON.stringify(bimData, null, 2)}

Requirements:
- Write in natural English that is easy for general public to understand
- Focus on main features and spatial composition of the building  
- About 150-200 words in appropriate length
- Minimize architectural jargon and use everyday terms

Example format:
"This building is a [characteristic] [building type] with [main spaces] efficiently arranged in a total area of [area]. [Special advantages or features] make it optimized for [intended use]."`
    };

    return promptTemplates[language] || promptTemplates.ko;
  }

  /**
   * BIM 파라미터 검증 및 정규화
   */
  _validateAndNormalizeBIMParameters(params) {
    const normalized = {
      buildingType: params.buildingType || 'RESIDENTIAL',
      totalArea: {
        value: parseInt(params.totalArea?.value) || 30,
        unit: params.totalArea?.unit || '평',
        confidence: Math.min(Math.max(params.totalArea?.confidence || 0.5, 0), 1)
      },
      rooms: Array.isArray(params.rooms) ? params.rooms.map(room => ({
        type: room.type || '방',
        count: parseInt(room.count) || 1,
        area: parseInt(room.area) || 10,
        orientation: room.orientation || '남향',
        requirements: Array.isArray(room.requirements) ? room.requirements : []
      })) : [],
      style: {
        architectural: params.style?.architectural || '현대적',
        interior: params.style?.interior || '모던',
        keywords: Array.isArray(params.style?.keywords) ? params.style.keywords : []
      },
      location: {
        address: params.location?.address || '',
        region: params.location?.region || '',
        climate: params.location?.climate || ''
      },
      constraints: {
        budget: params.constraints?.budget || '',
        timeline: params.constraints?.timeline || '',
        regulations: Array.isArray(params.constraints?.regulations) ? params.constraints.regulations : []
      },
      extractedFeatures: {
        orientations: Array.isArray(params.extractedFeatures?.orientations) ? params.extractedFeatures.orientations : [],
        roomTypes: Array.isArray(params.extractedFeatures?.roomTypes) ? params.extractedFeatures.roomTypes : [],
        areaKeywords: Array.isArray(params.extractedFeatures?.areaKeywords) ? params.extractedFeatures.areaKeywords : [],
        buildingKeywords: Array.isArray(params.extractedFeatures?.buildingKeywords) ? params.extractedFeatures.buildingKeywords : [],
        styleKeywords: Array.isArray(params.extractedFeatures?.styleKeywords) ? params.extractedFeatures.styleKeywords : []
      },
      confidence: Math.min(Math.max(params.confidence || 0.5, 0), 1),
      suggestedName: params.suggestedName || '새 프로젝트',
      description: params.description || ''
    };

    return normalized;
  }

  /**
   * 검증 결과 정규화
   */
  _normalizeValidationResult(result) {
    return {
      isValid: result.isValid !== false,
      score: Math.min(Math.max(parseInt(result.score) || 70, 0), 100),
      issues: Array.isArray(result.issues) ? result.issues : [],
      suggestions: Array.isArray(result.suggestions) ? result.suggestions : [],
      compliance: {
        buildingCode: result.compliance?.buildingCode !== false,
        fireCode: result.compliance?.fireCode !== false,
        accessibilityCode: result.compliance?.accessibilityCode !== false,
        energyCode: result.compliance?.energyCode !== false
      },
      efficiency: {
        spaceUtilization: Math.min(Math.max(parseInt(result.efficiency?.spaceUtilization) || 75, 0), 100),
        circulation: Math.min(Math.max(parseInt(result.efficiency?.circulation) || 80, 0), 100),
        lighting: Math.min(Math.max(parseInt(result.efficiency?.lighting) || 75, 0), 100),
        ventilation: Math.min(Math.max(parseInt(result.efficiency?.ventilation) || 75, 0), 100)
      },
      cost: {
        estimatedRange: result.cost?.estimatedRange || '정보 없음',
        costPerArea: result.cost?.costPerArea || '정보 없음',
        savings: Array.isArray(result.cost?.savings) ? result.cost.savings : []
      }
    };
  }

  /**
   * 모의 BIM 파라미터 생성 (API 키가 없을 때)
   */
  _getMockBIMParameters(input) {
    // 기존 analyzeNaturalLanguage 함수 결과를 OpenAI 형식으로 변환
    const basicAnalysis = this._basicAnalyze(input);
    
    return {
      buildingType: basicAnalysis.buildingType,
      totalArea: {
        value: basicAnalysis.extractedArea || 30,
        unit: '평',
        confidence: basicAnalysis.confidence
      },
      rooms: basicAnalysis.rooms || [],
      style: {
        architectural: '현대적',
        interior: '모던',
        keywords: ['깔끔한', '실용적']
      },
      location: {
        address: '',
        region: '',
        climate: ''
      },
      constraints: {
        budget: '',
        timeline: '',
        regulations: []
      },
      extractedFeatures: {
        orientations: basicAnalysis.orientations || [],
        roomTypes: basicAnalysis.roomTypes || [],
        areaKeywords: basicAnalysis.areaKeywords || [],
        buildingKeywords: basicAnalysis.buildingKeywords || [],
        styleKeywords: []
      },
      confidence: basicAnalysis.confidence,
      suggestedName: basicAnalysis.suggestedName,
      description: basicAnalysis.description
    };
  }

  /**
   * 모의 검증 결과 생성
   */
  _getMockValidationResult(bimData) {
    return {
      isValid: true,
      score: 85,
      issues: [],
      suggestions: [
        {
          type: 'optimization',
          priority: 'medium',
          message: '거실 공간을 10% 더 넓게 하면 활용도가 향상됩니다.',
          expectedBenefit: '공간 활용도 증가'
        },
        {
          type: 'efficiency',
          priority: 'low',
          message: '주방과 다이닝 공간의 동선을 최적화할 수 있습니다.',
          expectedBenefit: '생활 동선 개선'
        }
      ],
      compliance: {
        buildingCode: true,
        fireCode: true,
        accessibilityCode: true,
        energyCode: true
      },
      efficiency: {
        spaceUtilization: 85,
        circulation: 78,
        lighting: 82,
        ventilation: 80
      },
      cost: {
        estimatedRange: '2억-3억원',
        costPerArea: '평당 600-800만원',
        savings: ['표준 자재 사용', '효율적인 공간 배치']
      }
    };
  }

  /**
   * 모의 설명 생성
   */
  _getMockDescription(bimData) {
    const type = bimData.type || bimData.buildingType || 'RESIDENTIAL';
    const typeNames = {
      'RESIDENTIAL': '주거용 건물',
      'COMMERCIAL': '상업용 건물',
      'OFFICE': '사무용 건물',
      'INDUSTRIAL': '산업용 건물',
      'PUBLIC': '공공 건물'
    };

    return `이 건물은 현대적인 ${typeNames[type]}로, 효율적인 공간 배치와 실용적인 설계가 특징입니다. 자연 채광을 최대한 활용하고 쾌적한 실내 환경을 제공하도록 계획되었습니다.`;
  }

  /**
   * 폴백 BIM 파라미터 생성
   */
  _getFallbackBIMParameters(input) {
    return this._getMockBIMParameters(input);
  }

  /**
   * 기본 자연어 분석 (기존 로직)
   */
  _basicAnalyze(input) {
    // 기존 analyzeNaturalLanguage 함수와 동일한 로직
    const analysis = {
      suggestedName: '',
      description: '',
      buildingType: 'RESIDENTIAL',
      extractedKeywords: [],
      confidence: 0,
      extractedArea: null,
      rooms: [],
      orientations: [],
      roomTypes: [],
      areaKeywords: [],
      buildingKeywords: []
    };

    const keywords = input.toLowerCase().split(/\s+/).filter(word => word.length >= 2);
    
    // 건물 유형 분석
    if (keywords.some(word => ['아파트', '빌라', '주택', '집', '거주', '원룸', '투룸', '쓰리룸'].includes(word))) {
      analysis.buildingType = 'RESIDENTIAL';
    } else if (keywords.some(word => ['사무실', '오피스', '사무', '업무', '회사'].includes(word))) {
      analysis.buildingType = 'OFFICE';
    } else if (keywords.some(word => ['카페', '매장', '상점', '쇼핑', '상업'].includes(word))) {
      analysis.buildingType = 'COMMERCIAL';
    } else if (keywords.some(word => ['공장', '창고', '생산', '제조', '산업'].includes(word))) {
      analysis.buildingType = 'INDUSTRIAL';
    } else if (keywords.some(word => ['학교', '병원', '도서관', '공공', '관공서'].includes(word))) {
      analysis.buildingType = 'PUBLIC';
    }

    // 면적 추출
    const areaMatches = input.match(/(\d+)\s*평/g);
    if (areaMatches) {
      analysis.extractedArea = parseInt(areaMatches[0].replace('평', ''));
      analysis.areaKeywords = areaMatches;
    }

    // 방향 추출
    const orientationWords = ['남향', '북향', '동향', '서향', '남동향', '남서향', '북동향', '북서향'];
    analysis.orientations = keywords.filter(word => orientationWords.includes(word));

    // 방 종류 추출
    const roomWords = ['거실', '침실', '주방', '화장실', '욕실', '베란다', '발코니', '드레스룸', '서재', '다이닝', '팬트리'];
    analysis.roomTypes = keywords.filter(word => roomWords.includes(word));

    if (analysis.roomTypes.length > 0) {
      analysis.rooms = analysis.roomTypes.map(roomType => ({
        type: roomType,
        count: 1,
        orientation: analysis.orientations[0] || '남향',
        area: this._getEstimatedRoomArea(roomType, analysis.extractedArea)
      }));
    }

    const buildingTypeNames = {
      'RESIDENTIAL': '주거 건물',
      'OFFICE': '사무 건물',
      'COMMERCIAL': '상업 건물', 
      'INDUSTRIAL': '산업 건물',
      'PUBLIC': '공공 건물'
    };

    analysis.suggestedName = analysis.extractedArea ? 
      `${analysis.extractedArea}평 ${buildingTypeNames[analysis.buildingType]} 프로젝트` :
      `${buildingTypeNames[analysis.buildingType]} 프로젝트`;
    
    analysis.description = `${input.substring(0, 100)}${input.length > 100 ? '...' : ''}`;
    
    let confidenceScore = 0.3;
    if (analysis.extractedArea) confidenceScore += 0.2;
    if (analysis.roomTypes.length > 0) confidenceScore += 0.2;
    if (analysis.orientations.length > 0) confidenceScore += 0.1;
    
    analysis.confidence = Math.min(confidenceScore, 0.9);

    return analysis;
  }

  /**
   * 방 타입별 예상 면적 계산
   */
  _getEstimatedRoomArea(roomType, totalArea = 30) {
    const areaRatios = {
      '거실': 0.4,
      '침실': 0.25,
      '주방': 0.15,
      '화장실': 0.08,
      '욕실': 0.1,
      '베란다': 0.05,
      '발코니': 0.05,
      '드레스룸': 0.08,
      '서재': 0.2,
      '다이닝': 0.2,
      '팬트리': 0.05
    };

    return Math.round((areaRatios[roomType] || 0.1) * totalArea);
  }
}

export default new OpenAIService();