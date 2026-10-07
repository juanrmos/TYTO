import logging
from datetime import date

import httpx

from app.adapters.normalizer import FIELD_MAP, normalize_forecast

logger = logging.getLogger(__name__)


class OpenMeteoClient:
    def __init__(self, client: httpx.AsyncClient, url: str):
        self.client = client
        self.url = url

    async def fetch(
        self, latitude: float, longitude: float, days: int, timezone: str, start: date
    ) -> tuple[list, dict]:
        response = await self.client.get(
            self.url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "timezone": timezone,
                "forecast_days": days,
                "daily": ",".join(FIELD_MAP),
                "wind_speed_unit": "kmh",
                "temperature_unit": "celsius",
                "precipitation_unit": "mm",
            },
        )
        response.raise_for_status()
        raw = response.json()
        if not isinstance(raw, dict):
            raise ValueError("Respuesta inválida del proveedor")
        logger.info("Pronóstico obtenido de Open-Meteo")
        return normalize_forecast(raw, start, days), raw
