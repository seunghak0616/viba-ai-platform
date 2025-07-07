/**
 * BIM 모델 관련 API 서비스
 * 안전하고 타입 안전한 BIM 모델 데이터 처리
 */
import {
  BimModel,
  BimModelType,
  NaturalLanguageRequest,
  ProcessedBimParams,
  OptimizationResult,
  ValidationResult,
  Pagination,
  SearchFilters
} from '@types/index';
import { apiGet, apiPost, apiPut, apiDelete, buildQueryString } from '@services/api';

export interface CreateBimModelRequest {
  name: string;
  description?: string;
  naturalLanguageInput: string;
  type: BimModelType;
  projectId: string;
}

export interface UpdateBimModelRequest {
  name?: string;
  description?: string;
  metadata?: Record<string, any>;
  properties?: Record<string, any>;
}

export interface OptimizeBimModelRequest {
  requirements?: Record<string, any>;
  constraints?: Record<string, any>;
}

export interface BimModelListResponse {
  bimModels: BimModel[];
  pagination: Pagination;
}

export interface BimModelResponse {
  bimModel: BimModel;
}

export interface OptimizationResponse {
  optimizedModel: BimModel;
  optimizationResult: OptimizationResult;
}

export interface ValidationResponse {
  validation: ValidationResult;
}

/**
 * BIM 모델 서비스 클래스
 */
class BimModelService {
  private readonly baseUrl = '/bim';

  /**
   * BIM 모델 목록 조회
   */
  async getBimModels(filters: SearchFilters = {}): Promise<BimModelListResponse> {
    try {
      const queryString = buildQueryString(filters);
      const response = await apiGet<BimModelListResponse>(`${this.baseUrl}${queryString}`);
      
      // 응답 데이터 검증
      this.validateBimModelListResponse(response);
      
      return response;
    } catch (error) {
      console.error('Failed to fetch BIM models:', error);
      throw new Error('BIM 모델 목록을 불러오는데 실패했습니다.');
    }
  }

  /**
   * 특정 BIM 모델 조회
   */
  async getBimModel(modelId: string): Promise<BimModelResponse> {
    if (!modelId || typeof modelId !== 'string') {
      throw new Error('유효한 모델 ID가 필요합니다.');
    }

    try {
      const response = await apiGet<BimModelResponse>(`${this.baseUrl}/${modelId}`);
      
      // 응답 데이터 검증
      this.validateBimModelResponse(response);
      
      return response;
    } catch (error) {
      console.error(`Failed to fetch BIM model ${modelId}:`, error);
      throw new Error('BIM 모델을 불러오는데 실패했습니다.');
    }
  }

  /**
   * 새 BIM 모델 생성
   */
  async createBimModel(request: CreateBimModelRequest): Promise<BimModelResponse> {
    // 입력 데이터 검증
    this.validateCreateBimModelRequest(request);

    try {
      const response = await apiPost<BimModelResponse>(this.baseUrl, request);
      
      // 응답 데이터 검증
      this.validateBimModelResponse(response);
      
      return response;
    } catch (error) {
      console.error('Failed to create BIM model:', error);
      throw new Error('BIM 모델 생성에 실패했습니다.');
    }
  }

  /**
   * BIM 모델 업데이트
   */
  async updateBimModel(modelId: string, request: UpdateBimModelRequest): Promise<BimModelResponse> {
    if (!modelId || typeof modelId !== 'string') {
      throw new Error('유효한 모델 ID가 필요합니다.');
    }

    // 입력 데이터 검증
    this.validateUpdateBimModelRequest(request);

    try {
      const response = await apiPut<BimModelResponse>(`${this.baseUrl}/${modelId}`, request);
      
      // 응답 데이터 검증
      this.validateBimModelResponse(response);
      
      return response;
    } catch (error) {
      console.error(`Failed to update BIM model ${modelId}:`, error);
      throw new Error('BIM 모델 업데이트에 실패했습니다.');
    }
  }

  /**
   * BIM 모델 삭제
   */
  async deleteBimModel(modelId: string): Promise<void> {
    if (!modelId || typeof modelId !== 'string') {
      throw new Error('유효한 모델 ID가 필요합니다.');
    }

    try {
      await apiDelete(`${this.baseUrl}/${modelId}`);
    } catch (error) {
      console.error(`Failed to delete BIM model ${modelId}:`, error);
      throw new Error('BIM 모델 삭제에 실패했습니다.');
    }
  }

  /**
   * BIM 모델 최적화
   */
  async optimizeBimModel(modelId: string, request: OptimizeBimModelRequest = {}): Promise<OptimizationResponse> {
    if (!modelId || typeof modelId !== 'string') {
      throw new Error('유효한 모델 ID가 필요합니다.');
    }

    try {
      const response = await apiPost<OptimizationResponse>(`${this.baseUrl}/${modelId}/optimize`, request);
      
      // 응답 데이터 검증
      this.validateOptimizationResponse(response);
      
      return response;
    } catch (error) {
      console.error(`Failed to optimize BIM model ${modelId}:`, error);
      throw new Error('BIM 모델 최적화에 실패했습니다.');
    }
  }

  /**
   * BIM 모델 검증
   */
  async validateBimModel(modelId: string, standards: Record<string, any> = {}): Promise<ValidationResponse> {
    if (!modelId || typeof modelId !== 'string') {
      throw new Error('유효한 모델 ID가 필요합니다.');
    }

    try {
      const response = await apiPost<ValidationResponse>(`${this.baseUrl}/${modelId}/validate`, { standards });
      
      // 응답 데이터 검증
      this.validateValidationResponse(response);
      
      return response;
    } catch (error) {
      console.error(`Failed to validate BIM model ${modelId}:`, error);
      throw new Error('BIM 모델 검증에 실패했습니다.');
    }
  }

  // 검증 메서드들

  private validateCreateBimModelRequest(request: CreateBimModelRequest): void {
    if (!request.name || typeof request.name !== 'string' || request.name.trim().length === 0) {
      throw new Error('모델명은 필수입니다.');
    }

    if (request.name.length > 100) {
      throw new Error('모델명은 100자 이하여야 합니다.');
    }

    if (!request.naturalLanguageInput || typeof request.naturalLanguageInput !== 'string') {
      throw new Error('자연어 입력은 필수입니다.');
    }

    if (request.naturalLanguageInput.length < 5 || request.naturalLanguageInput.length > 1000) {
      throw new Error('자연어 입력은 5-1000자 사이여야 합니다.');
    }

    const validTypes: BimModelType[] = ['APARTMENT', 'HOUSE', 'OFFICE', 'COMMERCIAL', 'INDUSTRIAL', 'CUSTOM'];
    if (!validTypes.includes(request.type)) {
      throw new Error('유효한 건물 타입을 선택해주세요.');
    }

    if (!request.projectId || typeof request.projectId !== 'string') {
      throw new Error('프로젝트 ID는 필수입니다.');
    }

    if (request.description && typeof request.description !== 'string') {
      throw new Error('설명은 문자열이어야 합니다.');
    }

    if (request.description && request.description.length > 500) {
      throw new Error('설명은 500자 이하여야 합니다.');
    }
  }

  private validateUpdateBimModelRequest(request: UpdateBimModelRequest): void {
    if (Object.keys(request).length === 0) {
      throw new Error('최소 하나의 필드는 업데이트해야 합니다.');
    }

    if (request.name !== undefined) {
      if (typeof request.name !== 'string' || request.name.trim().length === 0) {
        throw new Error('모델명은 비어있을 수 없습니다.');
      }
      if (request.name.length > 100) {
        throw new Error('모델명은 100자 이하여야 합니다.');
      }
    }

    if (request.description !== undefined) {
      if (typeof request.description !== 'string') {
        throw new Error('설명은 문자열이어야 합니다.');
      }
      if (request.description.length > 500) {
        throw new Error('설명은 500자 이하여야 합니다.');
      }
    }

    if (request.metadata !== undefined && typeof request.metadata !== 'object') {
      throw new Error('메타데이터는 객체여야 합니다.');
    }

    if (request.properties !== undefined && typeof request.properties !== 'object') {
      throw new Error('속성은 객체여야 합니다.');
    }
  }

  private validateBimModelListResponse(response: BimModelListResponse): void {
    if (!response || typeof response !== 'object') {
      throw new Error('잘못된 응답 형식입니다.');
    }

    if (!Array.isArray(response.bimModels)) {
      throw new Error('BIM 모델 목록이 배열이 아닙니다.');
    }

    if (!response.pagination || typeof response.pagination !== 'object') {
      throw new Error('페이지네이션 정보가 없습니다.');
    }

    // 페이지네이션 검증
    const { pagination } = response;
    if (typeof pagination.page !== 'number' || pagination.page < 1) {
      throw new Error('잘못된 페이지 번호입니다.');
    }

    if (typeof pagination.total !== 'number' || pagination.total < 0) {
      throw new Error('잘못된 총 개수입니다.');
    }
  }

  private validateBimModelResponse(response: BimModelResponse): void {
    if (!response || typeof response !== 'object') {
      throw new Error('잘못된 응답 형식입니다.');
    }

    if (!response.bimModel || typeof response.bimModel !== 'object') {
      throw new Error('BIM 모델 데이터가 없습니다.');
    }

    const model = response.bimModel;
    
    // 필수 필드 검증
    const requiredFields = ['id', 'name', 'type', 'userId', 'projectId', 'createdAt', 'updatedAt'];
    for (const field of requiredFields) {
      if (!(field in model)) {
        throw new Error(`필수 필드 '${field}'가 없습니다.`);
      }
    }

    // 타입 검증
    if (typeof model.id !== 'string' || model.id.length === 0) {
      throw new Error('잘못된 모델 ID입니다.');
    }

    if (typeof model.name !== 'string' || model.name.length === 0) {
      throw new Error('잘못된 모델명입니다.');
    }

    const validTypes: BimModelType[] = ['APARTMENT', 'HOUSE', 'OFFICE', 'COMMERCIAL', 'INDUSTRIAL', 'CUSTOM'];
    if (!validTypes.includes(model.type)) {
      throw new Error('잘못된 건물 타입입니다.');
    }
  }

  private validateOptimizationResponse(response: OptimizationResponse): void {
    if (!response || typeof response !== 'object') {
      throw new Error('잘못된 최적화 응답 형식입니다.');
    }

    if (!response.optimizedModel || !response.optimizationResult) {
      throw new Error('최적화 결과 데이터가 없습니다.');
    }

    // 최적화 결과 검증
    const result = response.optimizationResult;
    if (typeof result.overallScore !== 'number' || result.overallScore < 0 || result.overallScore > 100) {
      throw new Error('잘못된 최적화 점수입니다.');
    }

    if (!Array.isArray(result.suggestions)) {
      throw new Error('최적화 제안이 배열이 아닙니다.');
    }
  }

  private validateValidationResponse(response: ValidationResponse): void {
    if (!response || typeof response !== 'object') {
      throw new Error('잘못된 검증 응답 형식입니다.');
    }

    if (!response.validation || typeof response.validation !== 'object') {
      throw new Error('검증 결과 데이터가 없습니다.');
    }

    const validation = response.validation;
    
    if (typeof validation.isValid !== 'boolean') {
      throw new Error('잘못된 검증 결과입니다.');
    }

    if (typeof validation.complianceScore !== 'number' || 
        validation.complianceScore < 0 || 
        validation.complianceScore > 100) {
      throw new Error('잘못된 준수 점수입니다.');
    }

    if (!Array.isArray(validation.issues)) {
      throw new Error('검증 이슈가 배열이 아닙니다.');
    }
  }
}

// 싱글톤 인스턴스 생성
export const bimModelService = new BimModelService();

// 편의 함수들
export const {
  getBimModels,
  getBimModel,
  createBimModel,
  updateBimModel,
  deleteBimModel,
  optimizeBimModel,
  validateBimModel
} = bimModelService;

export default bimModelService;