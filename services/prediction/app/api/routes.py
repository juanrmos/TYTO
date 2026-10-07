from datetime import date

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.models import EstimationEngineVersion, SyntheticGeneratorVersion, TouristDestination
from app.schemas.forecast import ForecastResponse
from app.services.forecast import ServiceError, build_forecast

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "stp", "version": "1.0.0"}


@router.get("/api/v1/destinations")
async def destinations(request: Request) -> dict:
    async with request.app.state.sessions() as session:
        rows = await session.scalars(
            select(TouristDestination).where(TouristDestination.is_active.is_(True))
        )
        return {
            "destinations": [
                {"slug": r.slug, "name": r.name, "is_active": r.is_active} for r in rows
            ]
        }


@router.get("/api/v1/forecast/{destination_slug}", response_model=ForecastResponse)
async def forecast(request: Request, destination_slug: str, from_date: date | None = None):
    state = request.app.state
    now = state.clock()
    if from_date is not None and from_date != now.date():
        raise ServiceError(
            400, "INVALID_DATE_RANGE", "Solo se permite consultar hoy y los seis días siguientes."
        )
    async with state.sessions() as session:
        return await build_forecast(
            session,
            state.http,
            state.settings,
            state.parameters,
            state.calendar,
            destination_slug,
            now,
        )


@router.get("/api/v1/health/full")
async def full_health(request: Request):
    state = request.app.state
    database, weather, engine_code, generator_code = "ok", "ok", None, None
    try:
        async with state.sessions() as session:
            await session.execute(text("SELECT 1"))
            engine_code = await session.scalar(
                select(EstimationEngineVersion.version_code).where(
                    EstimationEngineVersion.version_code == state.parameters["engine_version"]
                )
            )
            generator_code = await session.scalar(
                select(SyntheticGeneratorVersion.version_code).where(
                    SyntheticGeneratorVersion.version_code == state.parameters["generator_version"]
                )
            )
    except (SQLAlchemyError, OSError):
        database = "error"
    try:
        response = await state.http.get(f"{state.settings.sms_base_url.rstrip('/')}/health")
        response.raise_for_status()
        if response.json().get("status") != "ok":
            weather = "degraded"
    except (httpx.HTTPError, ValueError, AttributeError):
        weather = "degraded"
    status = (
        "error"
        if database == "error"
        else ("ok" if weather == "ok" and engine_code and generator_code else "degraded")
    )
    return JSONResponse(
        status_code=503 if database == "error" else 200,
        content={
            "status": status,
            "database": database,
            "weather_service": weather,
            "engine_version": engine_code,
            "generator_version": generator_code,
        },
    )
