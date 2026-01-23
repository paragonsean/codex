from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional


class SimpleCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key not in self._cache:
            return None
        value, timestamp = self._cache[key]
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        self._cache.clear()


class RateLimiter:
    def __init__(self, calls_per_minute: int = 60):
        self.calls_per_minute = calls_per_minute
        self.call_times: list[float] = []

    def wait_if_needed(self) -> None:
        now = time.time()
        cutoff = now - 60.0
        self.call_times = [t for t in self.call_times if t > cutoff]

        if len(self.call_times) >= self.calls_per_minute:
            sleep_time = 60.0 - (now - self.call_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.call_times.append(time.time())
