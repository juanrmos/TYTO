from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    weather_cache_ttl_seconds: int = Field(default=10800, gt=0, le=86400)
    weather_timeout_seconds: float = Field(default=10, gt=0, le=60)
    open_meteo_url: str = "https://api.open-meteo.com/v1/forecast"
    log_level: str = "INFO"
