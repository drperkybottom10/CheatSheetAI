import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)

def retry(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(f"Attempt {attempts} failed: {str(e)}")
                    if attempts == max_attempts:
                        logger.error(f"Max attempts reached. Function {func.__name__} failed.")
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

class CheatSheetAIException(Exception):
    pass

class LoginError(CheatSheetAIException):
    pass

class NavigationError(CheatSheetAIException):
    pass

class AssignmentProcessingError(CheatSheetAIException):
    pass

class LLMError(CheatSheetAIException):
    pass

class GoogleDocsError(CheatSheetAIException):
    pass
