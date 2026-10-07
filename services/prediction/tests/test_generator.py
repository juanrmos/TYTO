import csv
from datetime import date
from pathlib import Path

import pytest
from app.config import load_configuration
from app.core.synthetic_generator import (
    apply_roundoff_correction,
    compute_day_weight,
    compute_p95_global,
    day_factors,
    generate_month,
)

DATA = Path(__file__).resolve().parents[3] / "data"


def test_cp08_exact_month():
    rows = generate_month(2026, 10, 2047, "SG-1.0", [])
    assert sum(r["estimated_visitors"] for r in rows) == 2047
    assert all(r["estimated_visitors"] >= 0 for r in rows)
    assert len(rows) == 31


def test_cp10_reproducibility():
    a = generate_month(2026, 10, 2047, "SG-1.0", [])
    assert a == generate_month(2026, 10, 2047, "SG-1.0", [])
    assert a != generate_month(2026, 10, 2047, "SG-1.1", [])


@pytest.mark.parametrize(
    "year,month,length", [(2024, 2, 29), (2025, 2, 28), (2026, 4, 30), (2026, 10, 31)]
)
def test_small_monthly_totals(year, month, length):
    for total in range(100):
        rows = generate_month(year, month, total, "SG-1.0", [])
        assert len(rows) == length
        assert sum(r["estimated_visitors"] for r in rows) == total
        assert min(r["estimated_visitors"] for r in rows) >= 0


def test_all_official_months_and_p95():
    parameters, calendar = load_configuration(DATA)
    with (DATA / "processed/visitas_mensuales_modelo.csv").open(encoding="utf-8") as f:
        source = list(csv.DictReader(f))
    daily = []
    for row in source:
        generated = generate_month(
            int(row["year"]),
            int(row["month"]),
            int(row["total_visitors"]),
            "SG-1.0",
            calendar["events"],
            parameters,
        )
        assert sum(r["estimated_visitors"] for r in generated) == int(row["total_visitors"])
        daily.extend(generated)
    assert len(source) == 56 and len(daily) == 1704
    assert compute_p95_global(daily) > 0


def test_calendar_validity_and_precedence():
    _, calendar = load_configuration(DATA)
    dates = [e["date"] for e in calendar["events"]]
    assert len(dates) == len(set(dates))
    assert "2023-06-07" not in dates and "2024-06-07" in dates
    assert "2026-10-09" not in dates
    day = date(2026, 4, 2)
    factors = day_factors(day, calendar["events"])
    assert factors["tipo_fecha"] == "FERIADO_LARGO"
    assert 0.97 <= factors["variacion"] <= 1.03
    assert compute_day_weight(day, calendar["events"]) > compute_day_weight(day, [])


def test_roundoff_never_negative():
    rows = [
        {"date": date(2026, 1, i), "day_weight": 1, "estimated_visitors": 1} for i in range(1, 5)
    ]
    corrected = apply_roundoff_correction(rows, 1)
    assert [r["estimated_visitors"] for r in corrected] == [0, 0, 0, 1]
    assert rows[0]["estimated_visitors"] == 1
    with pytest.raises(ValueError):
        apply_roundoff_correction([], 0)
    with pytest.raises(ValueError):
        generate_month(2026, 1, -1, "SG-1.0", [])


def test_percentile_definition():
    assert compute_p95_global([]) == 0
    assert compute_p95_global([{"estimated_visitors": 0}]) == 0
    assert compute_p95_global([{"estimated_visitors": v} for v in [0, 10, 20]]) == 19
