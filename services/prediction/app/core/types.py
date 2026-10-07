"""Value objects shared by the pure estimation functions."""

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class WeatherDay:
    date: date
    lluvia_mm: float
    prob_lluvia_pct: float
    horas_lluvia: float
    codigo_wmo: int
    temp_max_c: float
    temp_min_c: float
    sensacion_max_c: float
    viento_max_kmh: float
    uv_max: float
    horas_sol_s: float
    condition_label: str = ""


@dataclass(frozen=True)
class MonthlyRecord:
    year: int
    month: int
    total_visitors: int | None
    availability_status: str = "AVAILABLE"


@dataclass
class DayResult:
    date: date
    score_afluencia: int | None
    score_conveniencia: int | None
    category: str
    weather: WeatherDay | None = None
    ref_mensual: int | None = None
    estimated_visitors: int | None = None
    factors: dict = field(default_factory=dict)
    degraded_reason: str | None = None
