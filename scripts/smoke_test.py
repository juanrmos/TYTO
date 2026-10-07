"""Verify public contracts and optionally the internal SMS health endpoint."""

import argparse
import json
import sys
from datetime import datetime
from urllib.error import URLError
from urllib.request import urlopen
from zoneinfo import ZoneInfo


def get_json(base: str, path: str) -> dict:
    with urlopen(base.rstrip("/") + path, timeout=25) as response:
        return json.load(response)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--sms-url", help="Solo desde la red interna; no publicar SMS")
    args = parser.parse_args()
    try:
        assert get_json(args.base_url, "/health")["status"] == "ok"
        print("OK STP /health")
        destinations = get_json(args.base_url, "/api/v1/destinations")
        assert any(d["slug"] == "cueva-lechuzas" for d in destinations["destinations"])
        print("OK destinos")
        result = get_json(args.base_url, "/api/v1/forecast/cueva-lechuzas")
        assert len(result["days"]) == 7
        assert (
            result["days"][0]["date"] == datetime.now(ZoneInfo("America/Lima")).date().isoformat()
        )
        assert sum(day["is_best"] for day in result["days"]) == 1
        assert result["best_day"]["date"] == next(d["date"] for d in result["days"] if d["is_best"])
        print("OK siete días y mejor opción")
        health = get_json(args.base_url, "/api/v1/health/full")
        assert health["database"] == "ok"
        assert health["weather_service"] in {"ok", "degraded"}
        print("OK salud extendida")
        if args.sms_url:
            assert get_json(args.sms_url, "/health")["service"] == "sms"
            print("OK SMS interno")
        print("Prueba de humo completada.")
    except (AssertionError, URLError, KeyError, ValueError) as exc:
        print(f"ERROR smoke: {type(exc).__name__}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
