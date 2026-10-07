import asyncio
from copy import deepcopy
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import pytest
from app.adapters.normalizer import normalize_forecast
from app.cache.memory_cache import MemoryCache
from app.config import Settings
from app.main import create_app
from fastapi.testclient import TestClient

NOW = datetime(2026, 10, 6, 10, tzinfo=ZoneInfo("America/Lima"))


def test_normalizer_maps_all_fields(provider_response):
    days = normalize_forecast(provider_response, date(2026, 10, 6), 7)
    assert len(days) == 2
    assert days[0].lluvia_mm == 1.2 and days[0].horas_sol_s == 22320
    assert days[0].condition_label == "Parcialmente nublado"
    assert days[0].sensacion_max_c == 30


@pytest.mark.parametrize(
    "field,value",
    [
        ("precipitation_sum", None),
        ("precipitation_sum", -1),
        ("uv_index_max", float("nan")),
        ("weather_code", 999),
        ("precipitation_probability_max", 101),
        ("temperature_2m_min", 40),
    ],
)
def test_partial_invalid_day_is_omitted(provider_response, field, value):
    provider_response["daily"][field][0] = value
    days = normalize_forecast(provider_response, date(2026, 10, 6), 7)
    assert [d.date for d in days] == [date(2026, 10, 7)]


def test_missing_arrays_duplicate_dates_and_horizon(provider_response):
    with pytest.raises(ValueError):
        normalize_forecast({}, date(2026, 10, 6), 7)
    duplicate = deepcopy(provider_response)
    duplicate["daily"]["time"] = ["2026-10-06"] * 2
    with pytest.raises(ValueError):
        normalize_forecast(duplicate, date(2026, 10, 6), 7)
    assert normalize_forecast(provider_response, date(2026, 11, 1), 7) == []
    provider_response["daily"]["precipitation_sum"] = []
    assert normalize_forecast(provider_response, date(2026, 10, 6), 7) == []


def test_sms_contract_cache_and_errors(provider_response):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=provider_response)

    app = create_app(Settings(), httpx.MockTransport(handler), lambda: NOW)
    with TestClient(app) as client:
        assert client.get("/health").json()["cache_valid_until"] is None
        params = {"latitude": -9.3008, "longitude": -76.0026}
        first = client.get("/internal/weather", params=params)
        assert first.status_code == 200
        assert first.json()["raw_response"] == provider_response
        assert len(first.json()["days"]) == 2
        assert client.get("/health").json()["cache_status"] == "MISS"
        assert client.get("/internal/weather", params=params).json() == first.json()
        assert len(calls) == 1
        assert client.get("/health").json()["cache_status"] == "HIT"
        assert client.get("/internal/weather", params={**params, "days": 8}).status_code == 422
        assert (
            client.get("/internal/weather", params={**params, "latitude": 100}).status_code == 422
        )


@pytest.mark.parametrize("failure", ["timeout", "http", "empty", "invalid"])
def test_provider_failure_is_controlled(failure):
    def handler(request):
        if failure == "timeout":
            raise httpx.ReadTimeout("timeout")
        if failure == "http":
            return httpx.Response(500)
        return httpx.Response(200, json=[] if failure == "invalid" else {})

    with TestClient(create_app(Settings(), httpx.MockTransport(handler), lambda: NOW)) as client:
        response = client.get("/internal/weather?latitude=-9.3&longitude=-76")
        assert response.status_code == 503
        assert response.json()["error"] == "WEATHER_PROVIDER_UNAVAILABLE"
        assert response.json()["detail"] is None


@pytest.mark.asyncio
async def test_ttl_concurrent_calls_and_capacity(provider_response):
    now = [NOW]
    cache = MemoryCache(60, lambda: now[0], max_entries=2)
    calls = 0

    async def fetch():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.001)
        return normalize_forecast(provider_response, NOW.date(), 7), provider_response

    await asyncio.gather(*(cache.get_or_fetch(("same",), fetch) for _ in range(5)))
    assert calls == 1
    now[0] += timedelta(seconds=60)
    await cache.get_or_fetch(("same",), fetch)
    assert calls == 2
    await cache.get_or_fetch(("other",), fetch)
    await cache.get_or_fetch(("third",), fetch)
    assert len(cache.entries) == 2 and ("same",) not in cache.entries

    async def empty():
        return [], {}

    with pytest.raises(ValueError):
        await cache.get_or_fetch(("empty",), empty)
