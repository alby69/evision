import hashlib
import json
import logging
from typing import Any, Callable
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Default 12 hours TTL (43,200 seconds)
DEFAULT_TTL_SECONDS = 12 * 3600


class MemoryCache:
    """In-memory TTL cache with hash-based key generation for async service calls."""

    def __init__(self, maxsize: int = 1000, ttl: int = DEFAULT_TTL_SECONDS):
        self._cache: TTLCache = TTLCache(maxsize=maxsize, ttl=ttl)

    def make_key(self, prefix: str, *args: Any, **kwargs: Any) -> str:
        raw_key = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
        hashed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
        return f"{prefix}:{hashed}"

    async def get_or_call(self, prefix: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        key = self.make_key(prefix, *args, **kwargs)
        if key in self._cache:
            logger.debug("Cache hit for key: %s", key)
            return self._cache[key]

        logger.debug("Cache miss for key: %s, executing function...", key)
        result = await func(*args, **kwargs)
        if result is not None:
            self._cache[key] = result
        return result

    def clear(self) -> None:
        self._cache.clear()

    def __contains__(self, key: str) -> bool:
        return key in self._cache

    def __len__(self) -> int:
        return len(self._cache)


# Global cache instance
global_cache = MemoryCache()
