import logging
from contextlib import asynccontextmanager
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.routes import router
from app.config import Settings, load_configuration
from app.db.session import create_database
from app.services.forecast import ServiceError


def create_app(settings: Settings | None = None, transport=None, clock=None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logging.basicConfig(level=settings.log_level)
        app.state.parameters, app.state.calendar = load_configuration(settings.data_dir)
        engine, app.state.sessions = create_database(settings)
        async with httpx.AsyncClient(
            timeout=settings.weather_timeout_seconds, transport=transport
        ) as client:
            app.state.http = client
            try:
                yield
            finally:
                await engine.dispose()

    app = FastAPI(title="Tyto · Predicción Turística", version="1.0.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.clock = clock or (lambda: datetime.now(ZoneInfo("America/Lima")))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET"],
        allow_headers=["Content-Type"],
    )
    app.include_router(router)

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError):
        return JSONResponse(
            status_code=exc.status,
            content={"error": exc.code, "message": exc.message, "detail": None},
        )

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

    @app.exception_handler(SQLAlchemyError)
    @app.exception_handler(OSError)
    async def database_error(request: Request, exc: Exception):
        logging.getLogger(__name__).error("No se pudo completar la operación de persistencia")
        return JSONResponse(
            status_code=503,
            content={
                "error": "DATABASE_UNAVAILABLE",
                "message": "El servicio no está disponible temporalmente.",
                "detail": None,
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception):
        logging.getLogger(__name__).error("Error interno: %s", type(exc).__name__)
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "No se pudo completar la solicitud.",
                "detail": None,
            },
        )

    return app


app = create_app()
