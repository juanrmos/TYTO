import logging
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.adapters.open_meteo import OpenMeteoClient
from app.api.routes import router
from app.cache.memory_cache import MemoryCache
from app.config import Settings


def create_app(settings: Settings | None = None, transport=None, clock=None) -> FastAPI:
    settings = settings or Settings()
    clock = clock or (lambda: datetime.now(ZoneInfo("America/Lima")))

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logging.basicConfig(level=settings.log_level)
        async with httpx.AsyncClient(
            timeout=settings.weather_timeout_seconds, transport=transport
        ) as client:
            app.state.provider = OpenMeteoClient(client, settings.open_meteo_url)
            yield

    app = FastAPI(title="Tyto · Servicio Meteorológico", version="1.0.0", lifespan=lifespan)
    app.state.clock = clock
    app.state.cache = MemoryCache(settings.weather_cache_ttl_seconds, clock)
    app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "VALIDATION_ERROR",
                "message": "Los parámetros de la solicitud no son válidos.",
                "detail": None,
            },
        )

    return app


app = create_app()
