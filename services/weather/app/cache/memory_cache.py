import asyncio
from collections import OrderedDict
from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta

from app.schemas.weather import WeatherResponse


class MemoryCache:
    def __init__(self, ttl_seconds: int, clock: Callable[[], datetime], max_entries: int = 64):
        self.ttl = ttl_seconds
        self.clock = clock
        self.max_entries = max_entries
        self.entries: OrderedDict[tuple, WeatherResponse] = OrderedDict()
        self.lock = asyncio.Lock()
        self.last_status = "MISS"
        self.last_valid_until = None

    async def get_or_fetch(
        self, key: tuple, fetch: Callable[[], Awaitable[tuple[list, dict]]]
    ) -> WeatherResponse:
        async with self.lock:
            now = self.clock()
            cached = self.entries.get(key)
            if cached and now < cached.valid_until:
                self.entries.move_to_end(key)
                self.last_status = "HIT"
                self.last_valid_until = cached.valid_until
                return cached
            self.last_status = "MISS"
            self.last_valid_until = None
            days, raw = await fetch()
            if not days:
                raise ValueError("El proveedor no devolvió días completos")
            now = self.clock()
            value = WeatherResponse(
                fetched_at=now,
                valid_until=now + timedelta(seconds=self.ttl),
                days=days,
                raw_response=raw,
            )
            self.entries[key] = value
            self.entries.move_to_end(key)
            while len(self.entries) > self.max_entries:
                self.entries.popitem(last=False)
            self.last_valid_until = value.valid_until
            return value
