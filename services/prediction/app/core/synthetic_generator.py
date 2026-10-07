"""Deterministic monthly distribution. No network or database operations."""

import calendar
import hashlib
import math
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from app.core.parameters import DEFAULT_PARAMETERS
from app.core.types import MonthlyRecord

PRECEDENCE = ("FERIADO_LARGO", "FERIADO_AISLADO", "PUENTE", "PERIODO_ESPECIAL")


def round_half_up(value: float, digits: int = 0) -> int | float:
    """Round a value using the documented decimal rule.

    Args:
        value: Finite numeric input.
        digits: Number of decimal digits retained.
    Returns:
        Rounded integer or decimal value.
    """
    result = Decimal(str(value)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return int(result) if digits == 0 else float(result)


def monthly_reference(target: date, records: list[MonthlyRecord]) -> int | None:
    """Select the published total or historical median for the calendar month."""
    valid = [
        r
        for r in records
        if r.month == target.month
        and r.year >= 2022
        and r.availability_status in {"AVAILABLE", "ZERO_REPORTED"}
        and r.total_visitors is not None
    ]
    current = [r.total_visitors for r in valid if r.year == target.year]
    if current:
        return current[0]
    values = sorted(r.total_visitors for r in valid if r.year < target.year)
    if not values:
        return None
    middle = len(values) // 2
    return (
        values[middle]
        if len(values) % 2
        else round_half_up((values[middle - 1] + values[middle]) / 2)
    )


def day_factors(
    day: date, calendar_events: list[dict], version: str = "SG-1.0", parameters: dict | None = None
) -> dict:
    """Return deterministic calendar factors and Lehmer variation for a date."""
    p = parameters or DEFAULT_PARAMETERS
    types = {e["type"] for e in calendar_events if e["date"] == day.isoformat()}
    event_type = next((t for t in PRECEDENCE if t in types), "ORDINARIO")
    seed = int(hashlib.sha256(f"{day:%Y-%m}|{version}".encode()).hexdigest()[:8], 16)
    modulus = 2147483647
    state = seed % (modulus - 1) + 1
    for _ in range(day.day):
        state = state * 48271 % modulus
    variation = 1 + (state / modulus * 2 - 1) * p["noise_amplitude"]
    return {
        "factor_semana": p["weekday"][day.weekday()],
        "factor_tipo_fecha": p["calendar"][event_type],
        "factor_temporada": p["season"][day.month - 1],
        "tipo_fecha": event_type,
        "variacion": variation,
    }


def compute_day_weight(
    day: date, calendar_events: list[dict], version: str = "SG-1.0", parameters: dict | None = None
) -> float:
    """Calculate the positive daily weight without changing the monthly total."""
    f = day_factors(day, calendar_events, version, parameters)
    return max(
        f["factor_semana"] * f["factor_tipo_fecha"] * f["factor_temporada"] * f["variacion"], 0.01
    )


def apply_roundoff_correction(records: list[dict], ref_mensual: int) -> list[dict]:
    """Conserve the monthly total, never producing negative daily visitors."""
    result = [dict(r) for r in records]
    difference = ref_mensual - sum(r["estimated_visitors"] for r in result)
    ordered = sorted(result, key=lambda r: (-r["day_weight"], r["date"]))
    if not ordered:
        raise ValueError("El mes no contiene días")
    if difference >= 0:
        ordered[0]["estimated_visitors"] += difference
    else:
        remaining = -difference
        for record in ordered:
            take = min(remaining, record["estimated_visitors"])
            record["estimated_visitors"] -= take
            remaining -= take
            if not remaining:
                break
    return result


def generate_month(
    year: int,
    month: int,
    ref_mensual: int,
    version: str,
    calendar_events: list[dict],
    parameters: dict | None = None,
) -> list[dict]:
    """Distribute an integer monthly total with reproducible, bounded variation."""
    if not isinstance(ref_mensual, int) or isinstance(ref_mensual, bool) or ref_mensual < 0:
        raise ValueError("La referencia mensual debe ser un entero no negativo")
    records = []
    for n in range(1, calendar.monthrange(year, month)[1] + 1):
        day = date(year, month, n)
        records.append(
            {
                "date": day,
                "day_weight": compute_day_weight(day, calendar_events, version, parameters),
                "factors_json": day_factors(day, calendar_events, version, parameters),
            }
        )
    total_weight = sum(r["day_weight"] for r in records)
    for record in records:
        record["estimated_visitors"] = round_half_up(
            ref_mensual * record["day_weight"] / total_weight
        )
    return apply_roundoff_correction(records, ref_mensual)


def compute_p95_global(all_daily_records: list[dict]) -> float:
    """Compute the linear 95th percentile rounded to four decimal places."""
    values = sorted(r["estimated_visitors"] for r in all_daily_records)
    if not values:
        return 0.0
    position = (len(values) - 1) * 0.95
    left = math.floor(position)
    right = math.ceil(position)
    return round_half_up(values[left] + (values[right] - values[left]) * (position - left), 4)
