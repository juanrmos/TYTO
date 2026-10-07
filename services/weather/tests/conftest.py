import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


@pytest.fixture
def provider_response():
    return {
        "daily": {
            "time": ["2026-10-06", "2026-10-07"],
            "precipitation_sum": [1.2, 0],
            "precipitation_probability_max": [15, 10],
            "precipitation_hours": [0.5, 0],
            "weather_code": [2, 1],
            "temperature_2m_max": [28, 29],
            "temperature_2m_min": [20, 21],
            "apparent_temperature_max": [30, 31],
            "wind_speed_10m_max": [12, 10],
            "uv_index_max": [7, 6],
            "sunshine_duration": [22320, 24000],
        }
    }
