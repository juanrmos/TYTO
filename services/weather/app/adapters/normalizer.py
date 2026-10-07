"""Translate provider fields and reject incomplete or invalid days."""

from datetime import date, timedelta

from pydantic import ValidationError

from app.schemas.weather import WeatherDay

FIELD_MAP = {
    "precipitation_sum": "lluvia_mm",
    "precipitation_probability_max": "prob_lluvia_pct",
    "precipitation_hours": "horas_lluvia",
    "weather_code": "codigo_wmo",
    "temperature_2m_max": "temp_max_c",
    "temperature_2m_min": "temp_min_c",
    "apparent_temperature_max": "sensacion_max_c",
    "wind_speed_10m_max": "viento_max_kmh",
    "uv_index_max": "uv_max",
    "sunshine_duration": "horas_sol_s",
}
WMO_LABELS = {
    0: "Despejado",
    1: "Despejado",
    2: "Parcialmente nublado",
    3: "Parcialmente nublado",
    45: "Niebla",
    48: "Niebla",
    51: "Llovizna",
    53: "Llovizna",
    55: "Llovizna",
    56: "Llovizna",
    57: "Llovizna",
    61: "Lluvia moderada a fuerte",
    63: "Lluvia moderada a fuerte",
    65: "Lluvia moderada a fuerte",
    66: "Lluvia helada",
    67: "Lluvia helada",
    71: "Nieve",
    73: "Nieve",
    75: "Nieve",
    77: "Nieve",
    80: "Chubascos",
    81: "Chubascos",
    82: "Chubascos",
    85: "Chubascos de nieve",
    86: "Chubascos de nieve",
    95: "Tormenta eléctrica",
    96: "Tormenta con granizo",
    99: "Tormenta con granizo",
}


def normalize_forecast(raw: dict, start: date, days: int) -> list[WeatherDay]:
    daily = raw.get("daily")
    if not isinstance(daily, dict) or not isinstance(daily.get("time"), list):
        raise ValueError("Respuesta meteorológica sin fechas")
    times = daily["time"]
    if len(times) != len(set(times)):
        raise ValueError("Fechas meteorológicas duplicadas")
    expected = {start + timedelta(days=i) for i in range(days)}
    results = []
    for index, raw_date in enumerate(times):
        try:
            day = date.fromisoformat(raw_date)
            if day not in expected:
                continue
            values = {internal: daily[external][index] for external, internal in FIELD_MAP.items()}
            code = values["codigo_wmo"]
            if code not in WMO_LABELS:
                continue
            results.append(WeatherDay(date=day, condition_label=WMO_LABELS[code], **values))
        except (ValueError, TypeError, KeyError, IndexError, ValidationError):
            continue
    return sorted(results, key=lambda w: w.date)
