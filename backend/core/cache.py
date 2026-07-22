import time
from typing import Dict, Any, Optional

class SimpleTTLCache:
    """In-memory TTL Cache to optimize response times and respect API rate limits."""
    def __init__(self, default_ttl: int = 300):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item["expires_at"]:
                return item["data"]
            del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        expire_in = ttl if ttl is not None else self.default_ttl
        self._cache[key] = {
            "data": value,
            "expires_at": time.time() + expire_in
        }

global_cache = SimpleTTLCache(default_ttl=600)
