"""Runtime settings; secrets never have committed default values."""

import hashlib
import json
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from app.core.parameters import DEFAULT_PARAMETERS


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: SecretStr | None = None
    postgres_user: str = "tyto"
    postgres_password: SecretStr | None = None
    postgres_db: str = "tyto"
    postgres_host: str = "db"
    postgres_port: int = 5432
    sms_base_url: str = "http://sms:8001"
    destination_slug: str = "cueva-lechuzas"
    cors_origins: list[str] = ["http://localhost:8080", "http://localhost:5173"]
    data_dir: Path = Path(__file__).resolve().parents[3] / "data"
    log_level: str = "INFO"
    weather_timeout_seconds: float = Field(default=12, gt=0, le=60)

    def connection_url(self) -> str | URL:
        if self.database_url:
            value = self.database_url.get_secret_value()
            if not value.startswith("postgresql+asyncpg://"):
                raise ValueError("DATABASE_URL debe utilizar PostgreSQL con asyncpg")
            return value
        if not self.postgres_password or self.postgres_password.get_secret_value().startswith(
            "REPLACE_"
        ):
            raise ValueError("Configure POSTGRES_PASSWORD antes de iniciar STP")
        return URL.create(
            "postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


def load_configuration(data_dir: Path) -> tuple[dict, dict]:
    parameters = json.loads((data_dir / "config/engine.json").read_text(encoding="utf-8"))
    calendar = json.loads(
        (data_dir / "calendar/peru_tourist_calendar.json").read_text(encoding="utf-8")
    )
    if parameters.keys() != DEFAULT_PARAMETERS.keys():
        raise ValueError("Configuración de motor incompleta o desconocida")
    if len(parameters["weekday"]) != 7 or len(parameters["season"]) != 12:
        raise ValueError("Factores semanales/mensuales inválidos")
    if not calendar["events"] or calendar["start_year"] > calendar["end_year"]:
        raise ValueError("Calendario inválido")
    return parameters, calendar


def fingerprint(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, ensure_ascii=False, default=str).encode()
    ).hexdigest()
