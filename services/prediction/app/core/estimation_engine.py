"""Pure academic estimation rules and deterministic weekly selection."""

from app.core.parameters import DEFAULT_PARAMETERS
from app.core.synthetic_generator import round_half_up
from app.core.types import DayResult, WeatherDay

CATEGORY_LABELS = {
    "RECOMENDADO": "Recomendado",
    "PRECAUCION": "Visitable con precaución",
    "NO_RECOMENDADO": "No recomendado",
    "SIN_DATOS": "Sin datos meteorológicos",
}
LEVEL_LABELS = {"BAJA": "Baja", "MEDIA": "Media", "ALTA": "Alta"}
TEMPLATES = {
    "RECOMENDADO_BAJA_FAVORABLE": "Buen momento para visitar. Se espera poca concurrencia y condiciones meteorológicas favorables. Consulte horarios y disponibilidad de entradas en los canales oficiales.",
    "RECOMENDADO_MEDIA_FAVORABLE": "Condiciones aceptables para la visita. Se espera una concurrencia moderada con buen clima. Verifique horarios en los canales oficiales.",
    "RECOMENDADO_ALTA_FAVORABLE": "El clima es favorable, aunque se espera alta concurrencia. Planifique con anticipación y confirme disponibilidad de entradas.",
    "PRECAUCION_LLUVIA": "Se esperan lluvias. Puede visitarse con precaución llevando equipo adecuado. Consulte las condiciones antes de salir.",
    "PRECAUCION_ALTA": "Alta concurrencia esperada. Las condiciones meteorológicas son aceptables, pero planifique con tiempo para evitar esperas.",
    "PRECAUCION_MIXTA": "Las condiciones presentan factores a considerar. Revise el pronóstico actualizado y consulte los canales oficiales antes de la visita.",
    "NO_RECOMENDADO_TORMENTA": "Se esperan tormentas eléctricas. No se recomienda la visita por razones de seguridad. Consulte los próximos días.",
    "NO_RECOMENDADO_LLUVIA": "No se recomienda la visita por condiciones meteorológicas adversas. Considere otro día del horizonte disponible.",
    "NO_RECOMENDADO_GENERAL": "Las condiciones del día no son favorables para la visita. Se sugiere evaluar los demás días disponibles.",
    "SIN_DATOS_METEOROLOGICOS": "No se dispone de pronóstico meteorológico para esta fecha. La afluencia estimada es {level}, pero la conveniencia no puede calcularse. Consulte fuentes meteorológicas antes de planificar.",
    "NO_HISTORICAL_DATA": "No se dispone de datos históricos suficientes para estimar esta fecha. Consulte el pronóstico y los canales oficiales antes de planificar.",
}
WEEK_WARNING = "Ninguno de los próximos siete días presenta condiciones completamente recomendables. La mejor alternativa disponible es {day}, donde se espera menor concurrencia y condiciones relativamente mejores."
NO_WEATHER_WARNING = "No se dispone de pronóstico meteorológico suficiente. La fecha señalada corresponde a la menor afluencia estimada."
METHODOLOGY_WARNING = "La afluencia es una estimación académica derivada de registros mensuales oficiales y una distribución diaria sintética con factores de calendario. El pronóstico meteorológico se utiliza para calcular la conveniencia de visita. No representa ocupación real ni conteo en tiempo real. Antes de visitar, consulte horarios, entradas y restricciones en los canales oficiales de SERNANP."


def compute_affuence_score(estimated_visitors: int | None, p95_global: float) -> int | None:
    """Scale synthetic visitors against the fixed historical percentile."""
    if estimated_visitors is None or p95_global <= 0:
        return None
    return max(0, min(round_half_up(estimated_visitors / p95_global * 100), 100))


def classify_affuence_level(score: int | None, parameters: dict | None = None) -> str | None:
    """Map a score to its documented crowd level, preserving missing values."""
    if score is None:
        return None
    low, middle = (parameters or DEFAULT_PARAMETERS)["affluence_thresholds"]
    return "BAJA" if score <= low else "MEDIA" if score <= middle else "ALTA"


def compute_convenience_score(
    weather_day: WeatherDay | None, score_afluencia: int | None, parameters: dict | None = None
) -> int | None:
    """Apply positive weather/crowd penalties and sunshine bonus to a base of 100."""
    if weather_day is None or score_afluencia is None:
        return None
    w, p = weather_day, parameters or DEFAULT_PARAMETERS
    rain = (
        min(w.lluvia_mm / p["rain_divisor"], p["rain_cap"])
        + min(w.prob_lluvia_pct / p["probability_divisor"], p["probability_cap"])
        + min(w.horas_lluvia * p["rain_hours_multiplier"], p["rain_hours_cap"])
    )
    wind = min(max(w.viento_max_kmh - p["wind_start"], 0) * p["wind_multiplier"], p["wind_cap"])
    uv = (
        0
        if w.uv_max <= p["uv_thresholds"][0]
        else p["uv_penalties"][int(w.uv_max >= p["uv_thresholds"][1])]
    )
    heat = (
        0
        if w.sensacion_max_c <= p["heat_thresholds"][0]
        else p["heat_penalties"][int(w.sensacion_max_c > p["heat_thresholds"][1])]
    )
    crowd = (
        0
        if score_afluencia <= p["crowd_thresholds"][0]
        else p["crowd_penalties"][int(score_afluencia > p["crowd_thresholds"][1])]
    )
    wmo = p["wmo_penalties"].get(str(w.codigo_wmo))
    if wmo is None:
        return None
    score = 100 - rain - wind - uv - heat - wmo - crowd + min(w.horas_sol_s / 3600, p["sun_cap"])
    return round_half_up(max(0, min(score, 100)))


def classify_recommendation(
    score: int | None, weather_day: WeatherDay | None, parameters: dict | None = None
) -> str:
    """Apply numeric thresholds and the minimum weather conditions."""
    if score is None or weather_day is None:
        return "SIN_DATOS"
    p = parameters or DEFAULT_PARAMETERS
    caution, recommended = p["convenience_thresholds"]
    if score < caution:
        return "NO_RECOMENDADO"
    if (
        score >= recommended
        and weather_day.prob_lluvia_pct < p["recommendation_rain_limit"]
        and weather_day.codigo_wmo < 95
    ):
        return "RECOMENDADO"
    return "PRECAUCION"


def select_best_day(
    day_results: list[DayResult], parameters: dict | None = None
) -> tuple[int | None, str | None]:
    """Select a deterministic winner using a tie band anchored at the maximum."""
    candidates = [
        (i, d)
        for i, d in enumerate(day_results)
        if d.category == "RECOMENDADO"
        and d.score_conveniencia is not None
        and d.score_afluencia is not None
    ]
    label = "MEJOR_OPCION"
    if not candidates:
        candidates = [
            (i, d)
            for i, d in enumerate(day_results)
            if d.score_conveniencia is not None and d.score_afluencia is not None
        ]
        label = "MEJOR_ALTERNATIVA"
    if candidates:
        maximum = max(d.score_conveniencia for _, d in candidates)
        tolerance = (parameters or DEFAULT_PARAMETERS)["tie_tolerance"]
        candidates = [(i, d) for i, d in candidates if maximum - d.score_conveniencia <= tolerance]
    else:
        candidates = [(i, d) for i, d in enumerate(day_results) if d.score_afluencia is not None]
        label = "MENOR_AFLUENCIA"
    if not candidates:
        return None, None
    return min(candidates, key=lambda item: (item[1].score_afluencia, item[1].date))[0], label


def get_recommendation_text(
    category: str, affuence_level: str | None, weather_day: WeatherDay | None
) -> tuple[str, str]:
    """Select a fixed Spanish template and its stable key."""
    if affuence_level is None:
        key = "NO_HISTORICAL_DATA"
    elif weather_day is None or category == "SIN_DATOS":
        key = "SIN_DATOS_METEOROLOGICOS"
    elif category == "RECOMENDADO":
        key = f"RECOMENDADO_{affuence_level}_FAVORABLE"
    elif category == "PRECAUCION":
        suffix = (
            "LLUVIA"
            if weather_day.prob_lluvia_pct >= 40
            else ("ALTA" if affuence_level == "ALTA" else "MIXTA")
        )
        key = f"PRECAUCION_{suffix}"
    else:
        suffix = (
            "TORMENTA"
            if weather_day.codigo_wmo >= 95
            else ("LLUVIA" if weather_day.lluvia_mm >= 15 else "GENERAL")
        )
        key = f"NO_RECOMENDADO_{suffix}"
    return TEMPLATES[key].format(level=LEVEL_LABELS.get(affuence_level, "")), key


def get_active_factors(day_context: DayResult) -> list[str]:
    """Return up to four applicable explanations, prioritizing adverse weather."""
    d, w = day_context, day_context.weather
    factors = []
    if w:
        for applies, text in [
            (w.codigo_wmo >= 95, "Se esperan tormentas eléctricas"),
            (w.prob_lluvia_pct >= 60, "Alta probabilidad de lluvia"),
            (w.lluvia_mm >= 10, "Se esperan lluvias significativas"),
            (w.viento_max_kmh >= 40, "Vientos fuertes esperados"),
            (w.uv_max >= 10, "Índice UV muy alto"),
        ]:
            if applies:
                factors.append(text)
    event = {
        "FERIADO_LARGO": "Es feriado largo",
        "FERIADO_AISLADO": "Es feriado",
        "PUENTE": "Es día puente",
        "PERIODO_ESPECIAL": "Periodo turístico especial",
    }
    if d.factors.get("tipo_fecha") in event:
        factors.append(event[d.factors["tipo_fecha"]])
    if d.date.weekday() >= 5:
        factors.append("Es fin de semana")
    season = d.factors.get("factor_temporada", 1)
    if season >= 1.15:
        factors.append("El mes presenta afluencia histórica alta")
    elif season <= 0.90:
        factors.append("El mes presenta afluencia histórica baja")
    if d.score_afluencia is not None:
        if d.score_afluencia <= 25:
            factors.append("Afluencia histórica baja para esta fecha")
        elif d.score_afluencia >= 75:
            factors.append("Afluencia histórica alta para esta fecha")
    return factors[:4] or ["Estimación basada en el patrón mensual y el día de la semana"]
