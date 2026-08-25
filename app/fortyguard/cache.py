from threading import RLock
from cachetools import TTLCache

class ResponseCache:
    def __init__(self, maxsize: int = 512, ttl: int = 900):
        self._cache = TTLCache(maxsize=maxsize, ttl=ttl)
        self._lock = RLock()

    def get(self, key):
        with self._lock:
            return self._cache.get(key)

    def set(self, key, value):
        with self._lock:
            self._cache[key] = value
