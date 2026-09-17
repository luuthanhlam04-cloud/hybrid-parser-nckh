# -*- coding: utf-8 -*-
import logging
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from pydantic import ValidationError
import openai

from src.llm_extraction.schema_manager import SemanticExtraction

logger = logging.getLogger(__name__)

def safe_retry_extractor(max_attempts: int = 3):
    """
    Decorator sử dụng tenacity để tự động thử lại (retry) khi gọi API LLM thất bại.
    - Tự động thử lại khi gặp:
      + ValidationError (Pydantic)
      + APIConnectionError, APITimeoutError
      + InternalServerError, RateLimitError
    - BẮT BUỘC: Nếu sau max_attempts lần thử lại mà Pydantic vẫn quăng ValidationError
      hoặc lỗi không phục hồi được, hàm chủ động try-except và fallback an toàn về:
      SemanticExtraction(entities=[], relations=[])
    - Đảm bảo hệ thống KHÔNG BAO GIỜ GHI CHUỖI LỖI (như '1 validation error') VÀO FILE JSON ĐẦU RA.
    """
    def decorator(func):
        retrying_func = retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=2, max=10),
            retry=(
                retry_if_exception_type(ValidationError) |
                retry_if_exception_type(openai.APIConnectionError) |
                retry_if_exception_type(openai.APITimeoutError) |
                retry_if_exception_type(openai.InternalServerError) |
                retry_if_exception_type(openai.RateLimitError)
            ),
            before_sleep=lambda retry_state: logger.warning(
                f"Lỗi gọi LLM. Đang thử lại lần thứ {retry_state.attempt_number}... "
                f"Lý do: {retry_state.outcome.exception()}"
            ),
            reraise=True
        )(func)

        @wraps(func)
        def wrapper(*args, **kwargs) -> SemanticExtraction:
            try:
                return retrying_func(*args, **kwargs)
            except ValidationError as ve:
                logger.error(
                    f"ValidationError sau {max_attempts} lần retry thất bại: {ve}. "
                    f"Fail-safe: Trả về SemanticExtraction rỗng an toàn."
                )
                return SemanticExtraction(entities=[], relations=[])
            except Exception as e:
                logger.error(
                    f"Ngoại lệ sau {max_attempts} lần retry thất bại: {e}. "
                    f"Fail-safe: Trả về SemanticExtraction rỗng an toàn."
                )
                return SemanticExtraction(entities=[], relations=[])

        return wrapper
    return decorator

# Alias để tương thích ngược
create_retry_decorator = safe_retry_extractor
