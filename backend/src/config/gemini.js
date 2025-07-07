import { GoogleGenerativeAI } from '@google/generative-ai';
import config from './index.js';
import logger from '../utils/logger.js';

// Gemini API 클라이언트 초기화
const genAI = new GoogleGenerativeAI(config.gemini.apiKey);

// Gemini 모델 설정
const geminiConfig = {
  // 기본 모델 설정
  model: config.gemini.model || 'gemini-1.5-pro',
  
  // 생성 설정
  generationConfig: {
    temperature: config.gemini.temperature || 0.7,
    topK: config.gemini.topK || 40,
    topP: config.gemini.topP || 0.95,
    maxOutputTokens: config.gemini.maxTokens || 8192,
    candidateCount: 1,
    stopSequences: [],
  },
  
  // 안전 설정
  safetySettings: [
    {
      category: 'HARM_CATEGORY_HARASSMENT',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE'
    },
    {
      category: 'HARM_CATEGORY_HATE_SPEECH',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE'
    },
    {
      category: 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE'
    },
    {
      category: 'HARM_CATEGORY_DANGEROUS_CONTENT',
      threshold: 'BLOCK_MEDIUM_AND_ABOVE'
    }
  ]
};

// Gemini 클라이언트 클래스
class GeminiClient {
  constructor() {
    this.model = genAI.getGenerativeModel({
      model: geminiConfig.model,
      generationConfig: geminiConfig.generationConfig,
      safetySettings: geminiConfig.safetySettings
    });
    
    this.chatModel = genAI.getGenerativeModel({
      model: geminiConfig.model,
      generationConfig: {
        ...geminiConfig.generationConfig,
        temperature: 0.9 // 채팅에서는 더 창의적으로
      },
      safetySettings: geminiConfig.safetySettings
    });
  }

  /**
   * 자연어 입력을 BIM 파라미터로 변환
   * @param {string} naturalLanguageInput - 자연어 입력
   * @param {object} context - 추가 컨텍스트 정보
   * @returns {Promise<object>} BIM 파라미터 객체
   */
  async parseNaturalLanguageToBim(naturalLanguageInput, context = {}) {
    try {
      const prompt = this._createBimParsingPrompt(naturalLanguageInput, context);
      
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      // JSON 응답 파싱
      const parsedData = this._parseJsonResponse(text);
      
      logger.nlp('Gemini BIM 파싱 완료', {
        input: naturalLanguageInput.substring(0, 100) + '...',
        outputKeys: Object.keys(parsedData),
        confidence: parsedData.confidence || 0
      });
      
      return parsedData;
      
    } catch (error) {
      logger.error('Gemini BIM 파싱 오류:', {
        error: error.message,
        input: naturalLanguageInput,
        context
      });
      throw new Error('자연어 처리 중 오류가 발생했습니다: ' + error.message);
    }
  }

  /**
   * BIM 모델 최적화 제안 생성
   * @param {object} bimData - BIM 모델 데이터
   * @param {object} requirements - 최적화 요구사항
   * @returns {Promise<object>} 최적화 제안
   */
  async generateOptimizationSuggestions(bimData, requirements = {}) {
    try {
      const prompt = this._createOptimizationPrompt(bimData, requirements);
      
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      const suggestions = this._parseJsonResponse(text);
      
      logger.nlp('Gemini 최적화 제안 생성', {
        modelId: bimData.id,
        suggestionsCount: suggestions.suggestions?.length || 0,
        priority: suggestions.priority || 'medium'
      });
      
      return suggestions;
      
    } catch (error) {
      logger.error('Gemini 최적화 제안 오류:', {
        error: error.message,
        modelId: bimData.id
      });
      throw new Error('최적화 제안 생성 중 오류가 발생했습니다: ' + error.message);
    }
  }

  /**
   * 설계 검증 및 피드백 생성
   * @param {object} bimData - BIM 모델 데이터
   * @param {object} standards - 건축 기준 및 규정
   * @returns {Promise<object>} 검증 결과 및 피드백
   */
  async validateDesign(bimData, standards = {}) {
    try {
      const prompt = this._createValidationPrompt(bimData, standards);
      
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      const validation = this._parseJsonResponse(text);
      
      logger.nlp('Gemini 설계 검증 완료', {
        modelId: bimData.id,
        isValid: validation.isValid,
        issuesCount: validation.issues?.length || 0,
        complianceScore: validation.complianceScore || 0
      });
      
      return validation;
      
    } catch (error) {
      logger.error('Gemini 설계 검증 오류:', {
        error: error.message,
        modelId: bimData.id
      });
      throw new Error('설계 검증 중 오류가 발생했습니다: ' + error.message);
    }
  }

  /**
   * 채팅 기반 설계 도우미
   * @param {string} message - 사용자 메시지
   * @param {Array} history - 대화 히스토리
   * @param {object} projectContext - 프로젝트 컨텍스트
   * @returns {Promise<string>} AI 응답
   */
  async chatAssistant(message, history = [], projectContext = {}) {
    try {
      const conversationHistory = history.map(item => ({
        role: item.role,
        parts: [{ text: item.content }]
      }));
      
      const chat = this.chatModel.startChat({
        history: conversationHistory
      });
      
      const contextualMessage = this._createChatPrompt(message, projectContext);
      const result = await chat.sendMessage(contextualMessage);
      const response = await result.response;
      const text = response.text();
      
      logger.nlp('Gemini 채팅 어시스턴트', {
        messageLength: message.length,
        responseLength: text.length,
        projectId: projectContext.projectId
      });
      
      return text;
      
    } catch (error) {
      logger.error('Gemini 채팅 어시스턴트 오류:', {
        error: error.message,
        message: message.substring(0, 100)
      });
      throw new Error('채팅 처리 중 오류가 발생했습니다: ' + error.message);
    }
  }

  // Private 메서드들

  /**
   * BIM 파싱용 프롬프트 생성
   */
  _createBimParsingPrompt(input, context) {
    return `
당신은 건축 설계 전문가이자 BIM(Building Information Modeling) 시스템입니다.
사용자의 자연어 입력을 분석하여 정확한 BIM 파라미터를 추출해주세요.

# 입력 텍스트
"${input}"

# 컨텍스트 정보
${JSON.stringify(context, null, 2)}

# 분석 요구사항
1. 건물 유형 식별 (아파트, 단독주택, 사무실 등)
2. 공간 구성 분석 (방 개수, 용도, 크기 등)
3. 방향성 정보 추출 (남향, 북향 등)
4. 제약 조건 파악 (예산, 법규, 선호사항 등)
5. 치수 및 면적 정보
6. 특수 요구사항

# 응답 형식 (반드시 유효한 JSON으로만 응답)
{
  "buildingType": "APARTMENT|HOUSE|OFFICE|COMMERCIAL|INDUSTRIAL",
  "totalArea": {
    "value": 숫자,
    "unit": "평|m2",
    "confidence": 0.0-1.0
  },
  "rooms": [
    {
      "type": "거실|침실|주방|화장실|방|베란다",
      "count": 숫자,
      "area": 숫자,
      "orientation": "남향|북향|동향|서향|없음",
      "requirements": ["요구사항1", "요구사항2"]
    }
  ],
  "orientation": {
    "primary": "남향|북향|동향|서향",
    "secondary": "남향|북향|동향|서향|없음",
    "confidence": 0.0-1.0
  },
  "constraints": {
    "budget": 숫자,
    "timeframe": "문자열",
    "regulations": ["규정1", "규정2"],
    "preferences": ["선호사항1", "선호사항2"]
  },
  "dimensions": {
    "length": 숫자,
    "width": 숫자,
    "height": 숫자,
    "floors": 숫자
  },
  "specialRequirements": ["특수요구사항1", "특수요구사항2"],
  "confidence": 0.0-1.0,
  "language": "ko",
  "processedAt": "${new Date().toISOString()}"
}

응답은 반드시 위 JSON 형식으로만 해주세요. 다른 텍스트는 포함하지 마세요.
`;
  }

  /**
   * 최적화 제안용 프롬프트 생성
   */
  _createOptimizationPrompt(bimData, requirements) {
    return `
당신은 건축 설계 최적화 전문가입니다.
주어진 BIM 모델을 분석하여 최적화 제안을 해주세요.

# BIM 모델 데이터
${JSON.stringify(bimData, null, 2)}

# 최적화 요구사항
${JSON.stringify(requirements, null, 2)}

# 분석 기준
1. 공간 효율성 (면적 활용도, 동선 최적화)
2. 비용 효율성 (재료비, 시공비 절약)
3. 에너지 효율성 (채광, 환기, 단열)
4. 구조적 안전성 (내력벽, 기둥 배치)
5. 법규 준수성 (건축법, 소방법 등)
6. 거주 편의성 (생활 동선, 프라이버시)

# 응답 형식 (반드시 유효한 JSON으로만 응답)
{
  "overallScore": 0-100,
  "suggestions": [
    {
      "category": "공간|비용|에너지|구조|법규|편의성",
      "priority": "HIGH|MEDIUM|LOW",
      "title": "제안 제목",
      "description": "상세 설명",
      "impact": "예상 효과",
      "implementation": "구현 방법",
      "estimatedCost": 숫자,
      "estimatedSavings": 숫자,
      "difficulty": "EASY|MEDIUM|HARD"
    }
  ],
  "compliance": {
    "buildingCode": true/false,
    "fireCode": true/false,
    "accessibilityCode": true/false,
    "issues": ["이슈1", "이슈2"]
  },
  "efficiency": {
    "spaceUtilization": 0-100,
    "energyEfficiency": 0-100,
    "costEfficiency": 0-100
  },
  "processedAt": "${new Date().toISOString()}"
}

응답은 반드시 위 JSON 형식으로만 해주세요.
`;
  }

  /**
   * 설계 검증용 프롬프트 생성
   */
  _createValidationPrompt(bimData, standards) {
    return `
당신은 건축 설계 검증 전문가입니다.
주어진 BIM 모델이 건축 기준과 규정에 부합하는지 검증해주세요.

# BIM 모델 데이터
${JSON.stringify(bimData, null, 2)}

# 적용 기준 및 규정
${JSON.stringify(standards, null, 2)}

# 검증 항목
1. 건축법 준수 (건폐율, 용적률, 높이 제한)
2. 소방법 준수 (피난 통로, 소방 설비)
3. 접근성 기준 (장애인 접근성)
4. 구조 안전성 (내진 설계, 하중 계산)
5. 환경 기준 (일조권, 환기, 소음)

# 응답 형식 (반드시 유효한 JSON으로만 응답)
{
  "isValid": true/false,
  "complianceScore": 0-100,
  "issues": [
    {
      "category": "건축법|소방법|접근성|구조|환경",
      "severity": "CRITICAL|HIGH|MEDIUM|LOW",
      "code": "법규 조항",
      "description": "문제 설명",
      "suggestion": "해결 방안",
      "location": "문제 위치"
    }
  ],
  "compliance": {
    "buildingCode": {
      "passed": true/false,
      "details": "상세 내용"
    },
    "fireCode": {
      "passed": true/false,
      "details": "상세 내용"
    },
    "accessibility": {
      "passed": true/false,
      "details": "상세 내용"
    },
    "structural": {
      "passed": true/false,
      "details": "상세 내용"
    },
    "environmental": {
      "passed": true/false,
      "details": "상세 내용"
    }
  },
  "recommendations": ["권장사항1", "권장사항2"],
  "processedAt": "${new Date().toISOString()}"
}

응답은 반드시 위 JSON 형식으로만 해주세요.
`;
  }

  /**
   * 채팅용 프롬프트 생성
   */
  _createChatPrompt(message, context) {
    return `
당신은 친근하고 전문적인 건축 설계 어시스턴트입니다.
사용자의 질문에 대해 도움이 되는 답변을 해주세요.

# 현재 프로젝트 컨텍스트
${JSON.stringify(context, null, 2)}

# 사용자 메시지
"${message}"

# 응답 가이드라인
1. 친근하고 이해하기 쉬운 언어 사용
2. 전문적이지만 복잡하지 않은 설명
3. 구체적이고 실용적인 조언 제공
4. 필요시 단계별 가이드 제공
5. 안전성과 법규 준수 강조

한국어로 자연스럽게 응답해주세요.
`;
  }

  /**
   * JSON 응답 파싱 (안전한 파싱)
   */
  _parseJsonResponse(text) {
    try {
      // 마크다운 코드 블록 제거
      const cleanText = text.replace(/```json\n?/g, '').replace(/```\n?/g, '').trim();
      
      // JSON 파싱 시도
      return JSON.parse(cleanText);
      
    } catch (error) {
      logger.error('JSON 파싱 오류:', {
        error: error.message,
        text: text.substring(0, 500)
      });
      
      // 파싱 실패시 기본값 반환
      return {
        error: 'JSON 파싱 실패',
        originalText: text,
        confidence: 0
      };
    }
  }
}

// 싱글톤 인스턴스 생성
const geminiClient = new GeminiClient();

export default geminiClient;