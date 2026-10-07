from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Destination(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    slug: str
    name: str
    official_url: str | None
    tickets_url: str | None
    directions_url: str | None


class Affuence(BaseModel):
    score: int | None = Field(ge=0, le=100)
    level: Literal["BAJA", "MEDIA", "ALTA"] | None
    level_label: str | None


class Convenience(BaseModel):
    score: int | None = Field(ge=0, le=100)
    category: Literal["RECOMENDADO", "PRECAUCION", "NO_RECOMENDADO", "SIN_DATOS"]
    category_label: str


class PublicWeather(BaseModel):
    condition_label: str
    weather_code: int
    temp_max_c: float
    temp_min_c: float
    apparent_temp_max_c: float
    rain_mm: float
    rain_probability_pct: float
    rain_hours: float
    wind_max_kmh: float
    uv_max: float
    sunshine_hours: float


class Recommendation(BaseModel):
    text: str
    template_key: str


BestLabel = Literal["MEJOR_OPCION", "MEJOR_ALTERNATIVA", "MENOR_AFLUENCIA"]


class ForecastDay(BaseModel):
    date: date
    day_of_week: str
    is_today: bool
    is_best: bool
    best_label: BestLabel | None
    calendar_note: str | None
    affuence: Affuence
    convenience: Convenience
    weather: PublicWeather | None
    recommendation: Recommendation
    active_factors: list[str] = Field(min_length=1, max_length=4)
    is_degraded: bool
    degraded_reason: str | None


class BestDay(BaseModel):
    date: date
    label: BestLabel


class ForecastResponse(BaseModel):
    destination: Destination
    generated_at: datetime
    engine_version: str
    generator_version: str
    weather_fetched_at: datetime | None
    best_day: BestDay
    week_warning: str | None
    days: list[ForecastDay] = Field(min_length=7, max_length=7)
    methodology_warning: str


class InternalWeatherDay(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    date: date
    lluvia_mm: float = Field(ge=0)
    prob_lluvia_pct: float = Field(ge=0, le=100)
    horas_lluvia: float = Field(ge=0, le=24)
    codigo_wmo: int
    temp_max_c: float
    temp_min_c: float
    sensacion_max_c: float
    viento_max_kmh: float = Field(ge=0)
    uv_max: float = Field(ge=0)
    horas_sol_s: float = Field(ge=0, le=86400)
    condition_label: str

    @model_validator(mode="after")
    def validate_temperature(self):
        if self.temp_min_c > self.temp_max_c:
            raise ValueError("Temperaturas inválidas")
        return self


class InternalWeatherResponse(BaseModel):
    fetched_at: datetime
    valid_until: datetime
    provider: Literal["open-meteo"]
    days: list[InternalWeatherDay]
    raw_response: dict

    @model_validator(mode="after")
    def validate_timestamps(self):
        if (
            self.fetched_at.tzinfo is None
            or self.valid_until.tzinfo is None
            or self.valid_until <= self.fetched_at
        ):
            raise ValueError("Vigencia meteorológica inválida")
        if len({d.date for d in self.days}) != len(self.days):
            raise ValueError("Días meteorológicos duplicados")
        return self
