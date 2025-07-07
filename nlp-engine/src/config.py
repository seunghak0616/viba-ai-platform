"""
NLP 엔진 설정 모듈
환경 변수 및 설정 관리
"""
import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from loguru import logger

class Settings(BaseSettings):
    """애플리케이션 설정 클래스"""
    
    # 기본 설정
    app_name: str = "BIM NLP Engine"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    
    # 서버 설정
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Gemini AI 설정
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-pro"
    gemini_max_tokens: int = 8192
    gemini_temperature: float = 0.7
    gemini_top_k: int = 40
    gemini_top_p: float = 0.95
    gemini_safety_level: str = "BLOCK_MEDIUM_AND_ABOVE"
    
    # Redis 설정
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0
    cache_ttl: int = 3600  # 1시간
    
    # 데이터베이스 설정
    database_url: Optional[str] = None
    
    # 로그 설정
    log_level: str = "INFO"
    log_file: str = "./logs/nlp_engine.log"
    log_rotation: str = "1 day"
    log_retention: str = "30 days"
    
    # NLP 모델 설정
    korean_tokenizer: str = "mecab"  # mecab, okt, komoran, hannanum
    sentence_model: str = "jhgan/ko-sroberta-multitask"
    max_text_length: int = 1000
    min_confidence: float = 0.6
    
    # 건축 도메인 설정
    building_types: List[str] = [
        "APARTMENT", "HOUSE", "OFFICE", 
        "COMMERCIAL", "INDUSTRIAL", "CUSTOM"
    ]
    area_units: List[str] = ["평", "m2", "㎡"]
    orientations: List[str] = ["남향", "북향", "동향", "서향", "남동향", "남서향", "북동향", "북서향"]
    
    # 보안 설정
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # 파일 업로드 설정
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["txt", "json", "csv"]
    upload_dir: str = "./uploads"
    
    # 모니터링 설정
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # 성능 설정
    request_timeout: int = 30
    max_concurrent_requests: int = 100
    rate_limit_per_minute: int = 60
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # 환경 변수 접두사
        env_prefix = ""
    
    @validator("environment")
    def validate_environment(cls, v):
        """환경 설정 검증"""
        allowed = ["development", "testing", "production"]
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v):
        """로그 레벨 검증"""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"Log level must be one of {allowed}")
        return v.upper()
    
    @validator("korean_tokenizer")
    def validate_tokenizer(cls, v):
        """한국어 토크나이저 검증"""
        allowed = ["mecab", "okt", "komoran", "hannanum"]
        if v.lower() not in allowed:
            raise ValueError(f"Korean tokenizer must be one of {allowed}")
        return v.lower()
    
    @validator("gemini_temperature")
    def validate_temperature(cls, v):
        """Gemini temperature 검증"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Temperature must be between 0.0 and 1.0")
        return v
    
    @validator("gemini_top_p")
    def validate_top_p(cls, v):
        """Gemini top_p 검증"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Top_p must be between 0.0 and 1.0")
        return v
    
    @validator("min_confidence")
    def validate_confidence(cls, v):
        """최소 신뢰도 검증"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v
    
    def get_redis_config(self) -> dict:
        """Redis 설정 딕셔너리 반환"""
        config = {
            "url": self.redis_url,
            "db": self.redis_db,
            "encoding": "utf-8",
            "decode_responses": True,
        }
        if self.redis_password:
            config["password"] = self.redis_password
        return config
    
    def get_gemini_config(self) -> dict:
        """Gemini AI 설정 딕셔너리 반환"""
        return {
            "api_key": self.gemini_api_key,
            "model": self.gemini_model,
            "generation_config": {
                "temperature": self.gemini_temperature,
                "top_k": self.gemini_top_k,
                "top_p": self.gemini_top_p,
                "max_output_tokens": self.gemini_max_tokens,
            }
        }
    
    def is_production(self) -> bool:
        """프로덕션 환경 여부 확인"""
        return self.environment == "production"
    
    def is_development(self) -> bool:
        """개발 환경 여부 확인"""
        return self.environment == "development"

# 설정 인스턴스 생성
try:
    settings = Settings()
    logger.info(f"Settings loaded successfully for {settings.environment} environment")
except Exception as e:
    logger.error(f"Failed to load settings: {e}")
    raise

# 디렉토리 생성
def create_directories():
    """필요한 디렉토리 생성"""
    directories = [
        os.path.dirname(settings.log_file),
        settings.upload_dir,
        "./models_cache",
        "./data/temp"
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")

# 환경별 설정 적용
def apply_environment_settings():
    """환경별 특별 설정 적용"""
    if settings.is_production():
        # 프로덕션 환경 설정
        settings.debug = False
        settings.log_level = "INFO"
        settings.workers = os.cpu_count() or 1
        logger.info("Production environment settings applied")
        
    elif settings.is_development():
        # 개발 환경 설정
        settings.debug = True
        settings.log_level = "DEBUG"
        settings.workers = 1
        logger.info("Development environment settings applied")

# 초기화 함수 호출
create_directories()
apply_environment_settings()

# 설정 검증
def validate_required_settings():
    """필수 설정 검증"""
    required_fields = ["gemini_api_key"]
    missing_fields = []
    
    for field in required_fields:
        value = getattr(settings, field, None)
        if not value:
            missing_fields.append(field)
    
    if missing_fields:
        error_msg = f"Missing required settings: {', '.join(missing_fields)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("All required settings validated successfully")

# 설정 요약 출력
def print_settings_summary():
    """설정 요약 출력 (민감한 정보 제외)"""
    if settings.debug:
        summary = {
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "environment": settings.environment,
            "host": settings.host,
            "port": settings.port,
            "gemini_model": settings.gemini_model,
            "korean_tokenizer": settings.korean_tokenizer,
            "log_level": settings.log_level,
            "max_text_length": settings.max_text_length,
            "min_confidence": settings.min_confidence,
        }
        logger.debug(f"Settings summary: {summary}")

# 초기 검증 및 요약 출력
validate_required_settings()
print_settings_summary()