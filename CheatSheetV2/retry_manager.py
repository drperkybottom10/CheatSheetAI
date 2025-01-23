import asyncio
from typing import Callable, Any
import logging

logger = logging.getLogger(__name__)

class RetryManager:
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor

    async def retry_async(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        retries = 0
        while retries < self.max_retries:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    logger.error(f"Max retries reached for {func.__name__}. Error: {str(e)}")
                    raise
                wait_time = self.delay * (self.backoff_factor ** (retries - 1))
                logger.warning(f"Retry {retries}/{self.max_retries} for {func.__name__} in {wait_time:.2f} seconds. Error: {str(e)}")
                await asyncio.sleep(wait_time)

    def retry_sync(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        retries = 0
        while retries < self.max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    logger.error(f"Max retries reached for {func.__name__}. Error: {str(e)}")
                    raise
                wait_time = self.delay * (self.backoff_factor ** (retries - 1))
                logger.warning(f"Retry {retries}/{self.max_retries} for {func.__name__} in {wait_time:.2f} seconds. Error: {str(e)}")
                asyncio.sleep(wait_time)
