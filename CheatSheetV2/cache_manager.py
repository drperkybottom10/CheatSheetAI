import asyncio
from typing import Any, Callable
import json
import os
import hashlib

class CacheManager:
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _get_cache_key(self, func: Callable, *args, **kwargs) -> str:
        key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_file(self, cache_key: str) -> str:
        return os.path.join(self.cache_dir, f"{cache_key}.json")

    async def cached_async(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        cache_key = self._get_cache_key(func, *args, **kwargs)
        cache_file = self._get_cache_file(cache_key)

        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)

        result = await func(*args, **kwargs)

        with open(cache_file, 'w') as f:
            json.dump(result, f)

        return result

    def cached_sync(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        cache_key = self._get_cache_key(func, *args, **kwargs)
        cache_file = self._get_cache_file(cache_key)

        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)

        result = func(*args, **kwargs)

        with open(cache_file, 'w') as f:
            json.dump(result, f)

        return result

    async def clear_cache(self):
        for file in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir, file))
