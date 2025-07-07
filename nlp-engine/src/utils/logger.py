"""
로깅 유틸리티 모듈
구조화된 로그 메시지 및 성능 모니터링
"""
import sys
import json
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Union
from functools import wraps
from contextlib import contextmanager

from loguru import logger
from config import settings


class StructuredLogger:
    """구조화된 로그 처리 클래스"""
    
    def __init__(self):
        self._configure_logger()
    
    def _configure_logger(self):
        """로거 설정"""
        # 기본 로거 제거
        logger.remove()
        
        # 콘솔 출력 설정
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        logger.add(
            sys.stdout,
            format=console_format,
            level=settings.log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # 파일 출력 설정
        if settings.log_file:
            # 일반 로그 파일
            logger.add(
                settings.log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                level=settings.log_level,
                rotation=settings.log_rotation,
                retention=settings.log_retention,
                compression="gz",
                encoding="utf-8"
            )
            
            # JSON 형태 로그 파일 (구조화된 데이터)
            json_log_file = str(Path(settings.log_file).with_suffix('.json'))
            logger.add(
                json_log_file,
                format=self._json_formatter,
                level=settings.log_level,
                rotation=settings.log_rotation,
                retention=settings.log_retention,
                compression="gz",
                encoding="utf-8",
                serialize=True
            )
            
            # 에러 전용 로그 파일
            error_log_file = str(Path(settings.log_file).with_suffix('.error.log'))
            logger.add(
                error_log_file,
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
                level="ERROR",
                rotation=settings.log_rotation,
                retention=settings.log_retention,
                compression="gz",
                encoding="utf-8",
                backtrace=True,
                diagnose=True
            )
    
    def _json_formatter(self, record: dict) -> str:
        """JSON 형태로 로그 포맷팅"""
        log_entry = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "logger": record["name"],
            "function": record["function"],
            "line": record["line"],
            "message": record["message"],
            "module": record["module"],
        }
        
        # 추가 필드가 있으면 포함
        if record.get("extra"):
            log_entry.update(record["extra"])
        
        # 예외 정보가 있으면 포함
        if record.get("exception"):
            log_entry["exception"] = {
                "type": record["exception"].type.__name__,
                "value": str(record["exception"].value),
                "traceback": record["exception"].traceback
            }
        
        return json.dumps(log_entry, ensure_ascii=False, default=str)
    
    def nlp_operation(self, operation: str, **kwargs):
        """NLP 작업 로그"""
        log_data = {
            "operation_type": "nlp",
            "operation": operation,
            **kwargs
        }
        logger.bind(**log_data).info(f"NLP Operation: {operation}")
    
    def api_request(self, method: str, path: str, **kwargs):
        """API 요청 로그"""
        log_data = {
            "operation_type": "api",
            "method": method,
            "path": path,
            **kwargs
        }
        logger.bind(**log_data).info(f"API {method} {path}")
    
    def performance(self, operation: str, duration: float, **kwargs):
        """성능 로그"""
        log_data = {
            "operation_type": "performance",
            "operation": operation,
            "duration_ms": round(duration * 1000, 2),
            **kwargs
        }
        logger.bind(**log_data).info(f"Performance: {operation} took {duration:.3f}s")
    
    def error_with_context(self, error: Exception, context: Dict[str, Any], operation: str = None):
        """컨텍스트와 함께 에러 로그"""
        log_data = {
            "operation_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "traceback": traceback.format_exc()
        }
        
        if operation:
            log_data["operation"] = operation
        
        logger.bind(**log_data).error(f"Error in {operation or 'unknown'}: {error}")
    
    def security_event(self, event_type: str, **kwargs):
        """보안 이벤트 로그"""
        log_data = {
            "operation_type": "security",
            "event_type": event_type,
            **kwargs
        }
        logger.bind(**log_data).warning(f"Security Event: {event_type}")
    
    def business_metric(self, metric_name: str, value: Union[int, float], **kwargs):
        """비즈니스 메트릭 로그"""
        log_data = {
            "operation_type": "metric",
            "metric_name": metric_name,
            "metric_value": value,
            **kwargs
        }
        logger.bind(**log_data).info(f"Metric: {metric_name} = {value}")

# 전역 로거 인스턴스
structured_logger = StructuredLogger()


def log_execution_time(operation_name: str = None):
    """함수 실행 시간 로그 데코레이터"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                structured_logger.performance(operation, duration, status="success")
                return result
            except Exception as e:
                duration = time.time() - start_time
                structured_logger.performance(operation, duration, status="error")
                structured_logger.error_with_context(
                    e, 
                    {"function": func.__name__, "args": str(args)[:200]}, 
                    operation
                )
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            operation = operation_name or f"{func.__module__}.{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                structured_logger.performance(operation, duration, status="success")
                return result
            except Exception as e:
                duration = time.time() - start_time
                structured_logger.performance(operation, duration, status="error")
                structured_logger.error_with_context(
                    e, 
                    {"function": func.__name__, "args": str(args)[:200]}, 
                    operation
                )
                raise
        
        # 함수가 async인지 확인
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@contextmanager
def log_context(operation: str, **context_data):
    """컨텍스트 매니저로 작업 로그"""
    start_time = time.time()
    
    logger.bind(**context_data).info(f"Starting operation: {operation}")
    
    try:
        yield
        duration = time.time() - start_time
        structured_logger.performance(operation, duration, status="success", **context_data)
        logger.bind(**context_data).info(f"Completed operation: {operation}")
        
    except Exception as e:
        duration = time.time() - start_time
        structured_logger.performance(operation, duration, status="error", **context_data)
        structured_logger.error_with_context(e, context_data, operation)
        raise


class RequestLogger:
    """FastAPI 요청 로그 미들웨어용 클래스"""
    
    def __init__(self):
        self.start_time = None
    
    def log_request(self, request, user_id: Optional[str] = None):
        """요청 시작 로그"""
        self.start_time = time.time()
        
        log_data = {
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("user-agent"),
            "client_ip": request.client.host if request.client else None,
            "user_id": user_id,
        }
        
        structured_logger.api_request(
            request.method, 
            request.url.path,
            **log_data
        )
    
    def log_response(self, request, response, user_id: Optional[str] = None):
        """응답 완료 로그"""
        if self.start_time:
            duration = time.time() - self.start_time
            
            log_data = {
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "response_time_ms": round(duration * 1000, 2),
                "user_id": user_id,
            }
            
            if response.status_code >= 400:
                logger.bind(**log_data).warning(
                    f"HTTP {response.status_code} {request.method} {request.url.path}"
                )
            else:
                logger.bind(**log_data).info(
                    f"HTTP {response.status_code} {request.method} {request.url.path}"
                )


# 편의 함수들
def log_nlp_result(operation: str, input_text: str, result: Dict[str, Any], confidence: float):
    """NLP 처리 결과 로그"""
    structured_logger.nlp_operation(
        operation,
        input_length=len(input_text),
        confidence=confidence,
        result_keys=list(result.keys()) if isinstance(result, dict) else None
    )


def log_cache_operation(operation: str, key: str, hit: bool = None, **kwargs):
    """캐시 작업 로그"""
    log_data = {
        "operation_type": "cache",
        "cache_operation": operation,
        "cache_key": key,
        **kwargs
    }
    
    if hit is not None:
        log_data["cache_hit"] = hit
    
    logger.bind(**log_data).debug(f"Cache {operation}: {key}")


def log_model_operation(model_name: str, operation: str, **kwargs):
    """모델 작업 로그"""
    structured_logger.nlp_operation(
        f"{model_name}_{operation}",
        model=model_name,
        **kwargs
    )


# 에러 리포팅 (프로덕션 환경용)
def setup_error_reporting():
    """에러 리포팅 설정 (Sentry 등)"""
    if settings.is_production():
        # 프로덕션 환경에서 외부 에러 리포팅 서비스 설정
        # 예: Sentry, Rollbar 등
        pass


# 초기 설정
setup_error_reporting()

# 로거 내보내기
__all__ = [
    "logger", 
    "structured_logger", 
    "log_execution_time", 
    "log_context",
    "RequestLogger",
    "log_nlp_result",
    "log_cache_operation", 
    "log_model_operation"
]