import logging
from datetime import datetime, timedelta

import httpx
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import fingerprint
from app.core.estimation_engine import (
    CATEGORY_LABELS,
    LEVEL_LABELS,
    METHODOLOGY_WARNING,
    NO_WEATHER_WARNING,
    WEEK_WARNING,
    classify_affuence_level,
    classify_recommendation,
    compute_affuence_score,
    compute_convenience_score,
    get_active_factors,
    get_recommendation_text,
    select_best_day,
)
from app.core.synthetic_generator import day_factors, generate_month, monthly_reference
from app.core.types import DayResult, MonthlyRecord, WeatherDay
from app.db.models import (
    DailyPrediction,
    EstimationEngineVersion,
    MonthlyVisitorRecord,
    SyntheticGeneratorVersion,
    TouristDestination,
    WeatherSnapshot,
)
from app.schemas.forecast import Destination, ForecastResponse, InternalWeatherResponse

logger = logging.getLogger(__name__)
WEEKDAYS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
CALENDAR_LABELS = {
    "FERIADO_LARGO": "Feriado largo",
    "FERIADO_AISLADO": "Feriado",
    "PUENTE": "Puente",
    "PERIODO_ESPECIAL": "Periodo especial",
}


class ServiceError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message


async def build_forecast(
    session: AsyncSession,
    client: httpx.AsyncClient,
    settings,
    parameters: dict,
    calendar: dict,
    slug: str,
    now: datetime,
) -> ForecastResponse:
    destination = await session.scalar(
        select(TouristDestination).where(
            TouristDestination.slug == slug, TouristDestination.is_active.is_(True)
        )
    )
    if destination is None:
        raise ServiceError(
            404, "DESTINATION_NOT_FOUND", "El destino solicitado no existe o no está disponible."
        )
    generator = await session.scalar(
        select(SyntheticGeneratorVersion).where(
            SyntheticGeneratorVersion.version_code == parameters["generator_version"]
        )
    )
    engine = await session.scalar(
        select(EstimationEngineVersion).where(
            EstimationEngineVersion.version_code == parameters["engine_version"]
        )
    )
    if generator is None or engine is None:
        raise ServiceError(
            503, "ESTIMATION_UNAVAILABLE", "No hay datos suficientes para generar el pronóstico."
        )
    meta = generator.parameters_json
    if (
        engine.weights_json != parameters
        or meta["parameters"] != parameters
        or fingerprint(meta["calendar"]) != fingerprint(calendar)
    ):
        raise ServiceError(
            503, "CONFIGURATION_MISMATCH", "La configuración requiere regenerar los datos."
        )
    records = list(
        (
            await session.scalars(
                select(MonthlyVisitorRecord)
                .where(MonthlyVisitorRecord.destination_id == destination.id)
                .order_by(MonthlyVisitorRecord.year, MonthlyVisitorRecord.month)
            )
        ).all()
    )
    monthly = [
        MonthlyRecord(r.year, r.month, r.total_visitors, r.availability_status) for r in records
    ]
    snapshot, normalized = None, None
    weather_by_date = {}
    try:
        response = await client.get(
            f"{settings.sms_base_url.rstrip('/')}/internal/weather",
            params={
                "latitude": float(destination.latitude),
                "longitude": float(destination.longitude),
                "days": 7,
                "timezone": destination.timezone,
            },
        )
        response.raise_for_status()
        normalized = InternalWeatherResponse.model_validate(response.json())
        if normalized.fetched_at > now + timedelta(minutes=1) or normalized.valid_until <= now:
            raise ValueError("Pronóstico fuera de vigencia")
        weather_by_date = {
            w.date: WeatherDay(**w.model_dump())
            for w in normalized.days
            if now.date() <= w.date < now.date() + timedelta(days=7)
            and str(w.codigo_wmo) in parameters["wmo_penalties"]
        }
        if weather_by_date:
            snapshot = WeatherSnapshot(
                destination_id=destination.id,
                fetched_at=normalized.fetched_at,
                valid_until=normalized.valid_until,
                provider=normalized.provider,
                raw_response_json=normalized.raw_response,
                normalized_json=normalized.model_dump(mode="json", exclude={"raw_response"}),
                horizon_days=len(weather_by_date),
            )
            session.add(snapshot)
            await session.flush()
    except (httpx.HTTPError, ValidationError, ValueError, TypeError):
        logger.warning("Pronóstico semanal continúa sin meteorología")
        normalized, weather_by_date = None, {}
    results, distributions = [], {}
    for offset in range(7):
        target = now.date() + timedelta(days=offset)
        reference = monthly_reference(target, monthly)
        covered = calendar["start_year"] <= target.year <= calendar["end_year"]
        if not covered:
            reference = None
        key = (target.year, target.month)
        if reference is not None and key not in distributions:
            distributions[key] = generate_month(
                *key, reference, parameters["generator_version"], calendar["events"], parameters
            )
        estimated = (
            distributions[key][target.day - 1]["estimated_visitors"]
            if reference is not None
            else None
        )
        crowd = compute_affuence_score(estimated, float(generator.p95_global))
        weather = weather_by_date.get(target)
        convenience = compute_convenience_score(weather, crowd, parameters)
        reason = (
            "NO_HISTORICAL_DATA"
            if crowd is None
            else "WEATHER_UNAVAILABLE"
            if weather is None
            else "ZERO_REPORTED_MONTH"
            if reference == 0
            else None
        )
        results.append(
            DayResult(
                target,
                crowd,
                convenience,
                classify_recommendation(convenience, weather, parameters),
                weather,
                reference,
                estimated,
                day_factors(
                    target, calendar["events"], parameters["generator_version"], parameters
                ),
                reason,
            )
        )
    best, label = select_best_day(results, parameters)
    if best is None:
        raise ServiceError(
            503, "ESTIMATION_UNAVAILABLE", "No hay datos suficientes para generar el pronóstico."
        )
    days = []
    for index, result in enumerate(results):
        level = classify_affuence_level(result.score_afluencia, parameters)
        recommendation, template = get_recommendation_text(result.category, level, result.weather)
        active_factors = get_active_factors(result)
        w = result.weather
        public_weather = (
            None
            if w is None
            else dict(
                condition_label=w.condition_label,
                weather_code=w.codigo_wmo,
                temp_max_c=w.temp_max_c,
                temp_min_c=w.temp_min_c,
                apparent_temp_max_c=w.sensacion_max_c,
                rain_mm=w.lluvia_mm,
                rain_probability_pct=w.prob_lluvia_pct,
                rain_hours=w.horas_lluvia,
                wind_max_kmh=w.viento_max_kmh,
                uv_max=w.uv_max,
                sunshine_hours=round(w.horas_sol_s / 3600, 2),
            )
        )
        days.append(
            dict(
                date=result.date,
                day_of_week=WEEKDAYS[result.date.weekday()],
                is_today=result.date == now.date(),
                is_best=index == best,
                best_label=label if index == best else None,
                calendar_note=CALENDAR_LABELS.get(result.factors["tipo_fecha"]),
                affuence=dict(
                    score=result.score_afluencia, level=level, level_label=LEVEL_LABELS.get(level)
                ),
                convenience=dict(
                    score=result.score_conveniencia,
                    category=result.category,
                    category_label="Datos insuficientes"
                    if level is None
                    else CATEGORY_LABELS[result.category],
                ),
                weather=public_weather,
                recommendation=dict(text=recommendation, template_key=template),
                active_factors=active_factors,
                is_degraded=result.degraded_reason is not None,
                degraded_reason=result.degraded_reason,
            )
        )
        session.add(
            DailyPrediction(
                destination_id=destination.id,
                engine_version_id=engine.id,
                generator_version_id=generator.id,
                weather_snapshot_id=snapshot.id if snapshot and w else None,
                prediction_date=result.date,
                generated_at=now,
                ref_mensual=result.ref_mensual,
                estimated_visitors_day=result.estimated_visitors,
                score_afluencia=result.score_afluencia,
                nivel_afluencia=level,
                score_conveniencia=result.score_conveniencia,
                categoria_recomendacion=result.category,
                is_best_option=index == best,
                best_option_label=label if index == best else None,
                recommendation_template_key=template,
                active_factors_json=active_factors,
                is_degraded=result.degraded_reason is not None,
                degraded_reason=result.degraded_reason,
            )
        )
    warning = None
    if label == "MEJOR_ALTERNATIVA":
        winner = results[best].date
        warning = WEEK_WARNING.format(day=f"{WEEKDAYS[winner.weekday()].lower()} {winner.day}")
    elif label == "MENOR_AFLUENCIA":
        warning = NO_WEATHER_WARNING
    result = ForecastResponse(
        destination=Destination.model_validate(destination),
        generated_at=now,
        engine_version=engine.version_code,
        generator_version=generator.version_code,
        weather_fetched_at=normalized.fetched_at if normalized and weather_by_date else None,
        best_day={"date": results[best].date, "label": label},
        week_warning=warning,
        days=days,
        methodology_warning=METHODOLOGY_WARNING,
    )
    await session.commit()
    return result
