"""Exercise public contracts and persisted results against isolated PostgreSQL."""

import asyncio
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import pytest
from app.config import Settings
from app.db.models import DailyPrediction, WeatherSnapshot
from app.db.session import create_database
from app.main import create_app
from fastapi.testclient import TestClient
from sqlalchemy import func, select

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="Requires PostgreSQL test URL"),
]
NOW = datetime(2026, 10, 6, 10, tzinfo=ZoneInfo("America/Lima"))


def test_weekly_contract_persistence_and_degradation():
    settings = Settings(database_url=os.environ["TEST_DATABASE_URL"])
    available = [True]

    def provider(request):
        if request.url.path == "/health":
            return httpx.Response(200, json={"status": "ok"})
        if not available[0]:
            raise httpx.ConnectError("Controlled provider failure", request=request)
        days = [
            {
                "date": (NOW.date() + timedelta(days=i)).isoformat(),
                "lluvia_mm": 0,
                "prob_lluvia_pct": 0,
                "horas_lluvia": 0,
                "codigo_wmo": 0,
                "temp_max_c": 25,
                "temp_min_c": 18,
                "sensacion_max_c": 25,
                "viento_max_kmh": 5,
                "uv_max": 3,
                "horas_sol_s": 25000,
                "condition_label": "Despejado",
            }
            for i in range(7)
        ]
        return httpx.Response(
            200,
            json={
                "fetched_at": NOW.isoformat(),
                "valid_until": (NOW + timedelta(hours=3)).isoformat(),
                "provider": "open-meteo",
                "days": days,
                "raw_response": {"integration_test": True},
            },
        )

    async def counts():
        engine, sessions = create_database(settings)
        try:
            async with sessions() as session:
                return (
                    await session.scalar(select(func.count()).select_from(DailyPrediction)),
                    await session.scalar(select(func.count()).select_from(WeatherSnapshot)),
                )
        finally:
            await engine.dispose()

    before = asyncio.run(counts())
    app = create_app(settings, httpx.MockTransport(provider), lambda: NOW)
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        assert client.get("/api/v1/health/full").json()["database"] == "ok"
        assert (
            client.get("/api/v1/destinations").json()["destinations"][0]["slug"] == "cueva-lechuzas"
        )
        path = "/api/v1/forecast/cueva-lechuzas"
        response = client.get(path)
        assert response.status_code == 200, response.text
        result = response.json()
        assert len(result["days"]) == 7
        assert all(day["weather"] is not None for day in result["days"])
        assert sum(day["is_best"] for day in result["days"]) == 1
        assert result["best_day"]["date"] == next(
            day["date"] for day in result["days"] if day["is_best"]
        )
        assert client.get("/api/v1/forecast/unknown").status_code == 404
        assert client.get(path, params={"from_date": "2026-10-07"}).status_code == 400
        assert client.get(path, params={"from_date": "invalid"}).status_code == 422
        available[0] = False
        degraded = client.get(path)
        assert degraded.status_code == 200
        data = degraded.json()
        assert data["best_day"]["label"] == "MENOR_AFLUENCIA"
        assert all(day["weather"] is None and day["is_degraded"] for day in data["days"])
    after = asyncio.run(counts())
    assert after == (before[0] + 14, before[1] + 1)
