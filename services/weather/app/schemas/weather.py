from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WeatherDay(BaseModel):
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
    def temperature_order(self):
        if self.temp_min_c > self.temp_max_c:
            raise ValueError("Temperaturas invertidas")
        return self


class WeatherResponse(BaseModel):
    fetched_at: datetime
    valid_until: datetime
    provider: str = "open-meteo"
    days: list[WeatherDay]
    raw_response: dict
