import logging
from typing import Literal

import httpx
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse

from app.schemas.weather import WeatherResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health(request: Request) -> dict:
    cache = request.app.state.cache
    return {
        "status": "ok",
        "service": "sms",
        "cache_status": cache.last_status,
        "cache_valid_until": cache.last_valid_until,
    }


@router.get("/internal/weather", response_model=WeatherResponse)
async def weather(
    request: Request,
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    days: int = Query(7, ge=1, le=7),
    timezone: Literal["America/Lima"] = "America/Lima",
):
    start = request.app.state.clock().date()
    key = (latitude, longitude, days, timezone, start)
    try:
        return await request.app.state.cache.get_or_fetch(
            key,
            lambda: request.app.state.provider.fetch(latitude, longitude, days, timezone, start),
        )
    except (httpx.HTTPError, ValueError, TypeError, KeyError):
        logger.warning("Proveedor meteorológico no disponible")
        return JSONResponse(
            status_code=503,
            content={
                "error": "WEATHER_PROVIDER_UNAVAILABLE",
                "message": "No se pudo obtener el pronóstico meteorológico del proveedor externo.",
                "detail": None,
            },
        )
