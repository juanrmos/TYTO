from dataclasses import replace
from datetime import date, timedelta

import pytest
from app.core.estimation_engine import (
    classify_affuence_level,
    classify_recommendation,
    compute_affuence_score,
    compute_convenience_score,
    get_active_factors,
    get_recommendation_text,
    select_best_day,
)
from app.core.synthetic_generator import day_factors, monthly_reference
from app.core.types import DayResult, MonthlyRecord, WeatherDay


@pytest.fixture
def weather():
    return WeatherDay(date(2026, 5, 6), 0, 5, 0, 1, 28, 20, 27, 10, 6, 18000, "Despejado")


def result(day, crowd, convenience, category="RECOMENDADO", weather=None):
    return DayResult(day, crowd, convenience, category, weather, factors=day_factors(day, []))


def test_cp01_workday(weather):
    score = compute_convenience_score(weather, 20)
    assert score == 100
    assert classify_recommendation(score, weather) == "RECOMENDADO"
    assert "El mes presenta afluencia histórica baja" in get_active_factors(
        result(weather.date, 20, score)
    )


def test_cp02_busy_weekend(weather):
    w = replace(
        weather,
        date=date(2026, 7, 4),
        lluvia_mm=2,
        prob_lluvia_pct=20,
        horas_lluvia=2,
        codigo_wmo=2,
        viento_max_kmh=8,
        uv_max=8,
        sensacion_max_c=28,
        horas_sol_s=0,
    )
    assert compute_convenience_score(w, 82) == 76
    factors = get_active_factors(result(w.date, 82, 76, weather=w))
    assert "Es fin de semana" in factors
    assert "Afluencia histórica alta para esta fecha" in factors


def test_cp03_rainy_holiday(weather):
    w = replace(
        weather,
        lluvia_mm=25,
        prob_lluvia_pct=90,
        horas_lluvia=6,
        codigo_wmo=63,
        viento_max_kmh=15,
        uv_max=8,
        sensacion_max_c=28,
        horas_sol_s=0,
    )
    assert compute_convenience_score(w, 85) == 33
    assert classify_recommendation(33, w) == "NO_RECOMENDADO"
    d = result(w.date, 85, 33, weather=w)
    d.factors["tipo_fecha"] = "FERIADO_AISLADO"
    assert "Es feriado" in get_active_factors(d)


def test_cp04_low_crowd_storm(weather):
    w = replace(
        weather,
        codigo_wmo=95,
        lluvia_mm=30,
        prob_lluvia_pct=95,
        horas_lluvia=5,
        viento_max_kmh=50,
        uv_max=10,
        sensacion_max_c=37,
        horas_sol_s=0,
    )
    assert compute_convenience_score(w, 20) == 0
    assert classify_recommendation(0, w) == "NO_RECOMENDADO"
    assert (
        get_active_factors(result(w.date, 20, 0, weather=w))[0] == "Se esperan tormentas eléctricas"
    )


def test_cp05_unfavorable_week():
    days = [
        result(date(2026, 10, 6) + timedelta(days=i), 30 + i, 30 + i * 4, "PRECAUCION")
        for i in range(7)
    ]
    assert select_best_day(days) == (6, "MEJOR_ALTERNATIVA")


def test_cp06_tie_crowd():
    assert select_best_day(
        [result(date(2026, 10, 7), 35, 72), result(date(2026, 10, 8), 28, 72)]
    ) == (1, "MEJOR_OPCION")


def test_cp07_tie_date():
    assert select_best_day(
        [result(date(2026, 10, 9), 40, 71), result(date(2026, 10, 10), 40, 71)]
    ) == (0, "MEJOR_OPCION")


def test_cp09_no_history(weather):
    assert monthly_reference(date(2026, 10, 6), []) is None
    assert compute_affuence_score(None, 100) is None
    assert compute_convenience_score(weather, None) is None
    assert classify_affuence_level(None) is None
    assert get_recommendation_text("SIN_DATOS", None, weather)[1] == "NO_HISTORICAL_DATA"


@pytest.mark.parametrize(
    "score,level",
    [(0, "BAJA"), (33, "BAJA"), (34, "MEDIA"), (66, "MEDIA"), (67, "ALTA"), (100, "ALTA")],
)
def test_crowd_boundaries(score, level):
    assert classify_affuence_level(score) == level


@pytest.mark.parametrize(
    "score,category",
    [
        (0, "NO_RECOMENDADO"),
        (39, "NO_RECOMENDADO"),
        (40, "PRECAUCION"),
        (69, "PRECAUCION"),
        (70, "RECOMENDADO"),
        (100, "RECOMENDADO"),
    ],
)
def test_convenience_boundaries(weather, score, category):
    assert classify_recommendation(score, weather) == category


def test_safety_gate_and_nulls(weather):
    assert classify_recommendation(95, replace(weather, codigo_wmo=95)) == "PRECAUCION"
    assert classify_recommendation(95, replace(weather, prob_lluvia_pct=70)) == "PRECAUCION"
    assert classify_recommendation(None, weather) == "SIN_DATOS"
    assert compute_convenience_score(None, 20) is None
    assert compute_convenience_score(replace(weather, codigo_wmo=999), 20) is None
    assert compute_affuence_score(50, 0) is None
    assert compute_affuence_score(100, 50) == 100
    assert compute_affuence_score(1, 200) == 1


@pytest.mark.parametrize("uv,expected", [(6, 0), (6.5, 5), (9.5, 5), (10, 10)])
def test_fractional_uv(weather, uv, expected):
    w = replace(weather, uv_max=uv, horas_sol_s=0, prob_lluvia_pct=0)
    assert compute_convenience_score(w, 20) == 100 - expected


def test_tie_band_is_anchored_and_order_independent():
    days = [
        result(date(2026, 10, 6), 80, 72),
        result(date(2026, 10, 7), 40, 71),
        result(date(2026, 10, 8), 10, 70),
    ]
    assert select_best_day(days)[0] == 1
    assert select_best_day(list(reversed(days)))[0] == 1
    days = [
        result(date(2026, 10, 6), None, None, "SIN_DATOS"),
        result(date(2026, 10, 7), 20, None, "SIN_DATOS"),
    ]
    assert select_best_day(days) == (1, "MENOR_AFLUENCIA")
    assert select_best_day(days[:1]) == (None, None)
    assert select_best_day([]) == (None, None)


@pytest.mark.parametrize(
    "category,level,changes,key",
    [
        ("RECOMENDADO", "BAJA", {}, "RECOMENDADO_BAJA_FAVORABLE"),
        ("RECOMENDADO", "MEDIA", {}, "RECOMENDADO_MEDIA_FAVORABLE"),
        ("RECOMENDADO", "ALTA", {}, "RECOMENDADO_ALTA_FAVORABLE"),
        ("PRECAUCION", "BAJA", {"prob_lluvia_pct": 40}, "PRECAUCION_LLUVIA"),
        ("PRECAUCION", "ALTA", {}, "PRECAUCION_ALTA"),
        ("PRECAUCION", "MEDIA", {}, "PRECAUCION_MIXTA"),
        ("NO_RECOMENDADO", "BAJA", {"codigo_wmo": 95, "lluvia_mm": 20}, "NO_RECOMENDADO_TORMENTA"),
        ("NO_RECOMENDADO", "BAJA", {"lluvia_mm": 15}, "NO_RECOMENDADO_LLUVIA"),
        ("NO_RECOMENDADO", "BAJA", {}, "NO_RECOMENDADO_GENERAL"),
    ],
)
def test_templates(weather, category, level, changes, key):
    text, actual = get_recommendation_text(category, level, replace(weather, **changes))
    assert actual == key and text and "{" not in text


def test_no_weather_template_and_fallback_factor():
    assert "Baja" in get_recommendation_text("SIN_DATOS", "BAJA", None)[0]
    d = result(date(2026, 10, 6), 40, 80)
    assert len(get_active_factors(d)) == 1
    d.factors["tipo_fecha"] = "PUENTE"
    assert "Es día puente" in get_active_factors(d)


def test_monthly_reference_states():
    target = date(2026, 10, 6)
    records = [
        MonthlyRecord(2022, 10, 0, "ZERO_REPORTED"),
        MonthlyRecord(2023, 10, 11),
        MonthlyRecord(2024, 10, 99, "INCOMPLETE"),
        MonthlyRecord(2025, 9, 100),
    ]
    assert monthly_reference(target, records) == 6
    assert monthly_reference(target, records + [MonthlyRecord(2026, 10, 42)]) == 42
    assert monthly_reference(target, [MonthlyRecord(2025, 10, 5)]) == 5
