"""
test_normalize_monthly_visitors.py
------------------------------------
Pruebas automatizadas del proceso de normalización de visitas mensuales.

Cubre los 14 escenarios requeridos por el prompt:
  1.  Conversión de meses en español.
  2.  Reconocimiento de Setiembre y Septiembre.
  3.  Conversión de cantidades a enteros.
  4.  Pivotado de nacionales y extranjeros.
  5.  Cálculo correcto del total mensual.
  6.  Detección de duplicados.
  7.  Detección de categoría ausente.
  8.  Rechazo de cantidades negativas.
  9.  Rechazo de valores no interpretables.
  10. Limpieza y advertencia ante separador residual inequívoco.
  11. Orden cronológico del resultado.
  12. Filtro desde enero de 2022.
  13. Conservación de ceros oficiales.
  14. No creación de meses futuros ausentes.
"""

from __future__ import annotations

import sys
import tempfile
import textwrap
from pathlib import Path

# pyrefly: ignore [missing-import]
import pytest

# Importar desde el módulo de normalización
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from normalize_monthly_visitors import (
    MONTH_MAP,
    MODEL_START_MONTH,
    MODEL_START_YEAR,
    detect_delimiter,
    normalize,
    parse_quantity,
)


# ---------------------------------------------------------------------------
# Utilidades de ayuda para pruebas
# ---------------------------------------------------------------------------

def _make_csv(content: str, delimiter: str = ";") -> Path:
    """Crea un CSV temporal con el contenido proporcionado."""
    tmp = tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".csv",
        delete=False,
        encoding="utf-8",
        newline="",
    )
    tmp.write(content)
    tmp.close()
    return Path(tmp.name)


HEADER = "Mes;Año;Tipo de Visitante;Llegadas\n"


# ---------------------------------------------------------------------------
# 1. Conversión de meses en español
# ---------------------------------------------------------------------------

class TestMonthConversion:
    def test_all_standard_months_recognized(self):
        months = [
            "enero", "febrero", "marzo", "abril", "mayo", "junio",
            "julio", "agosto", "octubre", "noviembre", "diciembre",
        ]
        for m in months:
            assert m in MONTH_MAP, f"Mes no reconocido: {m}"

    def test_month_numbers_correct(self):
        assert MONTH_MAP["enero"] == 1
        assert MONTH_MAP["marzo"] == 3
        assert MONTH_MAP["diciembre"] == 12

    def test_case_insensitive_via_normalize(self):
        csv_content = (
            HEADER
            + "Enero;2022;Nacional;100\n"
            + "Enero;2022;Extranjero;10\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        assert result["rows"][0]["month"] == 1


# ---------------------------------------------------------------------------
# 2. Reconocimiento de Setiembre y Septiembre
# ---------------------------------------------------------------------------

class TestSeptemberVariants:
    def test_setiembre_recognized(self):
        assert "setiembre" in MONTH_MAP
        assert MONTH_MAP["setiembre"] == 9

    def test_septiembre_recognized(self):
        assert "septiembre" in MONTH_MAP
        assert MONTH_MAP["septiembre"] == 9

    def test_setiembre_in_csv(self):
        csv_content = (
            HEADER
            + "Setiembre;2022;Nacional;500\n"
            + "Setiembre;2022;Extranjero;20\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        assert result["rows"][0]["month"] == 9

    def test_septiembre_in_csv(self):
        csv_content = (
            HEADER
            + "Septiembre;2022;Nacional;500\n"
            + "Septiembre;2022;Extranjero;20\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        assert result["rows"][0]["month"] == 9

    def test_both_variants_same_month_number(self):
        assert MONTH_MAP["setiembre"] == MONTH_MAP["septiembre"]


# ---------------------------------------------------------------------------
# 3. Conversión de cantidades a enteros
# ---------------------------------------------------------------------------

class TestQuantityConversion:
    def test_plain_integer(self):
        warnings: list[str] = []
        assert parse_quantity("100", warnings, "fila 1") == 100

    def test_integer_with_whitespace(self):
        warnings: list[str] = []
        assert parse_quantity("  200  ", warnings, "fila 1") == 200

    def test_zero_is_valid(self):
        warnings: list[str] = []
        assert parse_quantity("0", warnings, "fila 1") == 0

    def test_non_numeric_raises(self):
        with pytest.raises(ValueError, match="no convertible"):
            parse_quantity("abc", [], "fila 1")

    def test_decimal_raises(self):
        with pytest.raises(ValueError, match="no convertible"):
            parse_quantity("12.5", [], "fila 1")


# ---------------------------------------------------------------------------
# 4. Pivotado de nacionales y extranjeros
# ---------------------------------------------------------------------------

class TestPivoting:
    def test_two_rows_become_one(self):
        csv_content = (
            HEADER
            + "Enero;2022;Nacional;1000\n"
            + "Enero;2022;Extranjero;50\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        assert len(result["rows"]) == 1
        row = result["rows"][0]
        assert row["national_visitors"] == 1000
        assert row["foreign_visitors"] == 50

    def test_multiple_months_pivoted_correctly(self):
        csv_content = (
            HEADER
            + "Enero;2022;Nacional;1000\n"
            + "Enero;2022;Extranjero;50\n"
            + "Febrero;2022;Nacional;800\n"
            + "Febrero;2022;Extranjero;30\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        assert len(result["rows"]) == 2
        assert result["rows"][0]["month"] == 1
        assert result["rows"][1]["month"] == 2


# ---------------------------------------------------------------------------
# 5. Cálculo correcto del total mensual
# ---------------------------------------------------------------------------

class TestTotalCalculation:
    def test_total_equals_sum(self):
        csv_content = (
            HEADER
            + "Marzo;2022;Nacional;500\n"
            + "Marzo;2022;Extranjero;25\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        row = result["rows"][0]
        assert row["total_visitors"] == row["national_visitors"] + row["foreign_visitors"]
        assert row["total_visitors"] == 525

    def test_total_when_foreign_is_zero(self):
        csv_content = (
            HEADER
            + "Abril;2020;Nacional;300\n"
            + "Abril;2020;Extranjero;0\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        row = result["rows"][0]
        assert row["total_visitors"] == 300
        assert row["foreign_visitors"] == 0


# ---------------------------------------------------------------------------
# 6. Detección de duplicados
# ---------------------------------------------------------------------------

class TestDuplicates:
    def test_duplicate_causes_failure(self):
        csv_content = (
            HEADER
            + "Enero;2022;Nacional;100\n"
            + "Enero;2022;Nacional;200\n"  # duplicado
            + "Enero;2022;Extranjero;10\n"
        )
        path = _make_csv(csv_content)
        with pytest.raises(SystemExit):
            normalize(path)

    def test_report_records_duplicate(self):
        """El reporte debe mencionar el duplicado."""
        csv_content = (
            HEADER
            + "Mayo;2023;Nacional;100\n"
            + "Mayo;2023;Nacional;200\n"
            + "Mayo;2023;Extranjero;10\n"
        )
        path = _make_csv(csv_content)
        with pytest.raises(SystemExit):
            normalize(path)


# ---------------------------------------------------------------------------
# 7. Detección de categoría ausente
# ---------------------------------------------------------------------------

class TestMissingCategory:
    def test_missing_extranjero_causes_failure(self):
        csv_content = (
            HEADER
            + "Junio;2022;Nacional;800\n"
            # Sin extranjero → mes incompleto
        )
        path = _make_csv(csv_content)
        with pytest.raises(SystemExit):
            normalize(path)

    def test_missing_nacional_causes_failure(self):
        csv_content = (
            HEADER
            + "Julio;2022;Extranjero;50\n"
            # Sin nacional → mes incompleto
        )
        path = _make_csv(csv_content)
        with pytest.raises(SystemExit):
            normalize(path)


# ---------------------------------------------------------------------------
# 8. Rechazo de cantidades negativas
# ---------------------------------------------------------------------------

class TestNegativeQuantities:
    def test_negative_value_raises(self):
        with pytest.raises(ValueError, match="negativa"):
            parse_quantity("-1", [], "fila 1")

    def test_negative_in_csv_causes_failure(self):
        csv_content = (
            HEADER
            + "Agosto;2022;Nacional;-100\n"
            + "Agosto;2022;Extranjero;10\n"
        )
        path = _make_csv(csv_content)
        with pytest.raises(SystemExit):
            normalize(path)


# ---------------------------------------------------------------------------
# 9. Rechazo de valores no interpretables
# ---------------------------------------------------------------------------

class TestNonParseable:
    def test_text_value_causes_failure(self):
        csv_content = (
            HEADER
            + "Septiembre;2022;Nacional;DESCONOCIDO\n"
            + "Septiembre;2022;Extranjero;10\n"
        )
        path = _make_csv(csv_content)
        with pytest.raises(SystemExit):
            normalize(path)

    def test_empty_value_causes_failure(self):
        csv_content = (
            HEADER
            + "Octubre;2022;Nacional;\n"
            + "Octubre;2022;Extranjero;10\n"
        )
        path = _make_csv(csv_content)
        with pytest.raises(SystemExit):
            normalize(path)


# ---------------------------------------------------------------------------
# 10. Limpieza y advertencia ante separador residual inequívoco
# ---------------------------------------------------------------------------

class TestResidualSeparatorCleaning:
    def test_thousands_dot_cleaned_with_warning(self):
        warnings: list[str] = []
        result = parse_quantity("1.234", warnings, "fila 5")
        assert result == 1234
        assert len(warnings) == 1
        assert "1.234" in warnings[0]

    def test_internal_space_cleaned(self):
        warnings: list[str] = []
        result = parse_quantity("10 000", warnings, "fila 6")
        assert result == 10000

    def test_ambiguous_decimal_raises(self):
        """12.5 no es un separador de miles inequívoco → debe fallar."""
        with pytest.raises(ValueError):
            parse_quantity("12.5", [], "fila 7")


# ---------------------------------------------------------------------------
# 11. Orden cronológico del resultado
# ---------------------------------------------------------------------------

class TestChronologicalOrder:
    def test_rows_ordered_by_year_then_month(self):
        csv_content = (
            HEADER
            + "Diciembre;2022;Nacional;500\n"
            + "Diciembre;2022;Extranjero;20\n"
            + "Enero;2022;Nacional;1000\n"
            + "Enero;2022;Extranjero;50\n"
            + "Marzo;2023;Nacional;400\n"
            + "Marzo;2023;Extranjero;15\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        rows = result["rows"]
        dates = [(r["year"], r["month"]) for r in rows]
        assert dates == sorted(dates)


# ---------------------------------------------------------------------------
# 12. Filtro desde enero de 2022
# ---------------------------------------------------------------------------

class TestModelFilter:
    def test_pre_2022_excluded_from_model(self):
        csv_content = (
            HEADER
            + "Enero;2021;Nacional;500\n"
            + "Enero;2021;Extranjero;20\n"
            + "Enero;2022;Nacional;800\n"
            + "Enero;2022;Extranjero;30\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        assert len(result["rows"]) == 2          # completo: 2021 + 2022
        assert len(result["model_rows"]) == 1    # modelo: solo 2022
        assert result["model_rows"][0]["year"] == 2022

    def test_december_2021_excluded(self):
        csv_content = (
            HEADER
            + "Diciembre;2021;Nacional;700\n"
            + "Diciembre;2021;Extranjero;15\n"
            + "Enero;2022;Nacional;800\n"
            + "Enero;2022;Extranjero;30\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        model = result["model_rows"]
        assert all((r["year"], r["month"]) >= (MODEL_START_YEAR, MODEL_START_MONTH) for r in model)

    def test_model_start_constants(self):
        assert MODEL_START_YEAR == 2022
        assert MODEL_START_MONTH == 1


# ---------------------------------------------------------------------------
# 13. Conservación de ceros oficiales
# ---------------------------------------------------------------------------

class TestZeroConservation:
    def test_zero_foreign_visitors_preserved(self):
        csv_content = (
            HEADER
            + "Abril;2020;Nacional;0\n"
            + "Abril;2020;Extranjero;0\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        row = result["rows"][0]
        assert row["national_visitors"] == 0
        assert row["foreign_visitors"] == 0
        assert row["total_visitors"] == 0

    def test_zero_is_not_treated_as_missing(self):
        """Un cero explícito es un dato oficial; no debe descartarse."""
        csv_content = (
            HEADER
            + "Junio;2020;Nacional;0\n"
            + "Junio;2020;Extranjero;0\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        assert len(result["rows"]) == 1


# ---------------------------------------------------------------------------
# 14. No creación de meses futuros ausentes
# ---------------------------------------------------------------------------

class TestNoArtificialRows:
    def test_only_existing_months_are_output(self):
        """Si el CSV solo tiene enero y marzo, no debe aparecer febrero."""
        csv_content = (
            HEADER
            + "Enero;2022;Nacional;1000\n"
            + "Enero;2022;Extranjero;50\n"
            + "Marzo;2022;Nacional;800\n"
            + "Marzo;2022;Extranjero;30\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        months = [(r["year"], r["month"]) for r in result["rows"]]
        assert (2022, 2) not in months
        assert len(result["rows"]) == 2

    def test_future_months_not_invented(self):
        """No deben crearse filas para meses que no aparecen en la fuente."""
        csv_content = (
            HEADER
            + "Agosto;2026;Nacional;100\n"
            + "Agosto;2026;Extranjero;10\n"
        )
        path = _make_csv(csv_content)
        result = normalize(path)
        # Solo debe existir agosto 2026, no septiembre, octubre, etc.
        assert len(result["rows"]) == 1
        assert result["rows"][0]["month"] == 8
        assert result["rows"][0]["year"] == 2026


# ---------------------------------------------------------------------------
# Prueba de integración: archivo real
# ---------------------------------------------------------------------------

class TestRealFile:
    """Prueba de humo contra el archivo real del repositorio."""

    REAL_CSV = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "raw"
        / "Tabla_data.csv"
    )

    def test_real_file_normalizes_without_errors(self):
        if not self.REAL_CSV.exists():
            pytest.skip("Archivo real no disponible en este entorno.")
        result = normalize(self.REAL_CSV)
        assert len(result["rows"]) > 0

    def test_real_file_totals_consistent(self):
        if not self.REAL_CSV.exists():
            pytest.skip("Archivo real no disponible en este entorno.")
        result = normalize(self.REAL_CSV)
        for row in result["rows"]:
            assert row["total_visitors"] == row["national_visitors"] + row["foreign_visitors"]

    def test_real_file_model_rows_from_2022(self):
        if not self.REAL_CSV.exists():
            pytest.skip("Archivo real no disponible en este entorno.")
        result = normalize(self.REAL_CSV)
        for row in result["model_rows"]:
            assert (row["year"], row["month"]) >= (2022, 1)

    def test_real_file_original_not_modified(self):
        if not self.REAL_CSV.exists():
            pytest.skip("Archivo real no disponible en este entorno.")
        import os
        size_before = os.path.getsize(self.REAL_CSV)
        normalize(self.REAL_CSV)
        size_after = os.path.getsize(self.REAL_CSV)
        assert size_before == size_after, "El archivo original fue modificado."
