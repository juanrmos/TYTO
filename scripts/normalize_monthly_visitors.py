"""
normalize_monthly_visitors.py
------------------------------
Proceso reproducible de validación y normalización del archivo histórico
de visitas turísticas de la Cueva de las Lechuzas.

Documentos de referencia:
  - docs/01-definicion-y-alcance-del-proyecto.md
  - docs/02-requisitos-del-sistema.md
  - docs/00-mapa-de-construibles-y-preparacion-del-mvp.md

Salidas:
  - data/processed/visitas_mensuales_completas.csv  (todos los meses válidos)
  - data/processed/visitas_mensuales_modelo.csv     (enero 2022 – último mes disponible)
  - data/reports/calidad_datos_mensuales.json       (reporte de calidad)

RESTRICCIONES (ver doc 01, sección 19 y 12 de doc 02):
  - No genera registros diarios sintéticos.
  - No conecta a PostgreSQL.
  - No construye endpoints.
  - No modifica data/raw.
  - No inventa datos ausentes.
  - No rellena meses futuros con cero.
"""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Rutas relativas al directorio raíz del repositorio
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
RAW_FILE = REPO_ROOT / "data" / "raw" / "Tabla_data.csv"
OUT_COMPLETE = REPO_ROOT / "data" / "processed" / "visitas_mensuales_completas.csv"
OUT_MODEL = REPO_ROOT / "data" / "processed" / "visitas_mensuales_modelo.csv"
OUT_REPORT = REPO_ROOT / "data" / "reports" / "calidad_datos_mensuales.json"

# ---------------------------------------------------------------------------
# Inicio del periodo regular del motor (doc 01, sección 10.1 y 25)
# Los datos disponibles en el CSV determinan el fin; no se codifica en duro.
# ---------------------------------------------------------------------------
MODEL_START_YEAR = 2022
MODEL_START_MONTH = 1

# ---------------------------------------------------------------------------
# Mapeo de meses en español a número (doc 02, RD-02 y normalización)
# Se reconoce tanto "Setiembre" como "Septiembre".
# ---------------------------------------------------------------------------
MONTH_MAP: dict[str, int] = {
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "setiembre": 9,
    "septiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
}

# Tipos de visitante aceptados (normalizados a minúsculas)
ACCEPTED_VISITOR_TYPES = {"nacional", "extranjero"}

# Columnas de salida
OUTPUT_COLUMNS = [
    "year",
    "month",
    "month_start",
    "national_visitors",
    "foreign_visitors",
    "total_visitors",
]


# ---------------------------------------------------------------------------
# Detección de delimitador
# ---------------------------------------------------------------------------

def detect_delimiter(raw_text: str) -> str:
    """Detecta el delimitador real inspeccionando la primera línea."""
    first_line = raw_text.split("\n")[0]
    candidates = [";", ",", "\t", "|"]
    counts = {c: first_line.count(c) for c in candidates}
    best = max(counts, key=lambda c: counts[c])
    if counts[best] == 0:
        raise ValueError(
            f"No se pudo detectar un delimitador reconocido en la primera línea: {first_line!r}"
        )
    return best


# ---------------------------------------------------------------------------
# Normalización de texto de cantidad
# ---------------------------------------------------------------------------

def parse_quantity(raw: str, warnings: list[str], row_ref: str) -> int:
    """
    Convierte una cadena de texto a entero.
    Si contiene separadores residuales inequívocos (espacios, puntos de miles),
    los elimina, registra una advertencia y conserva el valor original en el reporte.
    Lanza ValueError si la interpretación es ambigua o no posible.
    """
    original = raw
    value = raw.strip()

    # Eliminar espacios internos (separador de miles en algunos formatos)
    cleaned = value.replace(" ", "").replace("\xa0", "")

    # Eliminar puntos usados como separador de miles SOLO si no hay coma decimal
    # Ejemplo inequívoco: "1.234" → 1234 (no hay coma posterior)
    if re.fullmatch(r"\d{1,3}(\.\d{3})+", cleaned):
        cleaned_no_dot = cleaned.replace(".", "")
        warnings.append(
            f"[{row_ref}] Separador de miles detectado: valor original={original!r}, "
            f"interpretado como {cleaned_no_dot}. Columna: Llegadas."
        )
        cleaned = cleaned_no_dot

    if not re.fullmatch(r"-?\d+", cleaned):
        raise ValueError(
            f"[{row_ref}] Cantidad no convertible a entero: {original!r}"
        )

    result = int(cleaned)
    if result < 0:
        raise ValueError(
            f"[{row_ref}] Cantidad negativa no permitida: {original!r} → {result}"
        )
    return result


# ---------------------------------------------------------------------------
# Función principal de normalización
# ---------------------------------------------------------------------------

def normalize(raw_path: Path) -> dict[str, Any]:
    """
    Lee el CSV oficial y devuelve un diccionario con:
      - 'rows': lista de dicts normalizados (una entrada por año+mes)
      - 'report': metadatos de calidad calculados del archivo real
    Lanza SystemExit con mensaje claro si encuentra cualquier error de validación.
    """
    if not raw_path.exists():
        _fail(f"Archivo de entrada no encontrado: {raw_path}")

    raw_bytes = raw_path.read_bytes()

    # Detectar codificación.
    # Se intenta primero utf-8-sig (maneja BOM \ufeff automáticamente).
    # Si falla, se usa latin-1 (cp1252), que es la codificación habitual
    # de archivos exportados desde Excel en Windows.
    encoding_used = "utf-8-sig"
    try:
        raw_text = raw_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        encoding_used = "latin-1"
        raw_text = raw_bytes.decode("latin-1")

    delimiter = detect_delimiter(raw_text)

    reader = csv.DictReader(raw_text.splitlines(), delimiter=delimiter)
    original_columns = reader.fieldnames or []

    # Validar columnas obligatorias (nombres normalizados)
    normalized_col_map = _build_column_map(original_columns)
    required = {"mes", "año", "tipo de visitante", "llegadas"}
    missing_cols = required - set(normalized_col_map.keys())
    if missing_cols:
        _fail(
            f"Columnas obligatorias ausentes en el archivo: {missing_cols}. "
            f"Columnas encontradas: {original_columns}"
        )

    # Leer todas las filas originales
    all_raw_rows = list(reader)
    original_row_count = len(all_raw_rows)

    warnings: list[str] = []
    errors: list[str] = []

    # Estructura intermedia: (year, month) → {"nacional": int | None, "extranjero": int | None}
    monthly: dict[tuple[int, int], dict[str, int | None]] = {}
    duplicates: list[str] = []
    invalid_values: list[str] = []

    for i, raw_row in enumerate(all_raw_rows, start=2):  # +2: encabezado en fila 1
        row_ref = f"fila {i}"

        mes_raw = raw_row.get(normalized_col_map["mes"], "").strip()
        año_raw = raw_row.get(normalized_col_map["año"], "").strip()
        tipo_raw = raw_row.get(normalized_col_map["tipo de visitante"], "").strip()
        llegadas_raw = raw_row.get(normalized_col_map["llegadas"], "").strip()

        # --- Validar mes ---
        mes_key = mes_raw.lower()
        if mes_key not in MONTH_MAP:
            msg = f"[{row_ref}] Mes desconocido: {mes_raw!r}"
            errors.append(msg)
            invalid_values.append(msg)
            continue
        month = MONTH_MAP[mes_key]

        # --- Validar año ---
        if not re.fullmatch(r"\d{4}", año_raw):
            msg = f"[{row_ref}] Año inválido: {año_raw!r}"
            errors.append(msg)
            invalid_values.append(msg)
            continue
        year = int(año_raw)

        # --- Validar tipo de visitante ---
        tipo_norm = tipo_raw.lower()
        if tipo_norm not in ACCEPTED_VISITOR_TYPES:
            msg = (
                f"[{row_ref}] Tipo de visitante desconocido: {tipo_raw!r}. "
                f"Admitidos: {ACCEPTED_VISITOR_TYPES}"
            )
            errors.append(msg)
            invalid_values.append(msg)
            continue

        # --- Validar cantidad ---
        try:
            cantidad = parse_quantity(llegadas_raw, warnings, row_ref)
        except ValueError as e:
            msg = str(e)
            errors.append(msg)
            invalid_values.append(msg)
            continue

        # --- Detectar duplicado ---
        key = (year, month)
        if key not in monthly:
            monthly[key] = {"nacional": None, "extranjero": None}

        if monthly[key][tipo_norm] is not None:
            dup_msg = (
                f"Duplicado: año={year}, mes={month}, tipo={tipo_norm!r} "
                f"aparece más de una vez."
            )
            duplicates.append(dup_msg)
            errors.append(dup_msg)
            continue

        monthly[key][tipo_norm] = cantidad

    # --- Validar que cada mes tenga nacionales Y extranjeros ---
    incomplete_months: list[str] = []
    for (year, month), vals in list(monthly.items()):
        missing = [t for t in ("nacional", "extranjero") if vals[t] is None]
        if missing:
            msg = (
                f"Mes {year}-{month:02d} carece de categoría: {missing}. "
                "No se incluirá en el resultado."
            )
            incomplete_months.append(msg)
            errors.append(msg)
            del monthly[(year, month)]

    if errors:
        _fail(
            "Se encontraron errores de validación. El proceso no puede continuar:\n"
            + "\n".join(f"  • {e}" for e in errors)
        )

    # --- Construir filas normalizadas ---
    normalized_rows: list[dict[str, Any]] = []
    for (year, month), vals in sorted(monthly.items()):
        national = vals["nacional"]
        foreign = vals["extranjero"]
        total = national + foreign  # type: ignore[operator]

        month_start = f"{year}-{month:02d}-01"
        normalized_rows.append(
            {
                "year": year,
                "month": month,
                "month_start": month_start,
                "national_visitors": national,
                "foreign_visitors": foreign,
                "total_visitors": total,
            }
        )

    # --- Filtrar registros para el modelo ---
    model_rows = [
        r
        for r in normalized_rows
        if (r["year"], r["month"]) >= (MODEL_START_YEAR, MODEL_START_MONTH)
    ]

    # --- Calcular metadatos de cobertura desde datos reales ---
    first_date = normalized_rows[0]["month_start"] if normalized_rows else None
    last_date = normalized_rows[-1]["month_start"] if normalized_rows else None
    first_model_date = model_rows[0]["month_start"] if model_rows else None
    last_model_date = model_rows[-1]["month_start"] if model_rows else None

    # --- Construir reporte ---
    report: dict[str, Any] = {
        "input_file": str(raw_path),
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "encoding_used": encoding_used,
        "delimiter_detected": delimiter,
        "original_columns": original_columns,
        "original_row_count": original_row_count,
        "months_normalized": len(normalized_rows),
        "months_in_model": len(model_rows),
        "first_date_available": first_date,
        "last_date_available": last_date,
        "first_date_model": first_model_date,
        "last_date_model": last_model_date,
        "duplicates_found": duplicates,
        "incomplete_months": incomplete_months,
        "invalid_values": invalid_values,
        "warnings": warnings,
        "validations": {
            "unknown_months": "PASS" if not any("Mes desconocido" in e for e in invalid_values) else "FAIL",
            "invalid_years": "PASS" if not any("Año inválido" in e for e in invalid_values) else "FAIL",
            "unknown_visitor_types": "PASS" if not any("Tipo de visitante" in e for e in invalid_values) else "FAIL",
            "non_integer_quantities": "PASS" if not any("no convertible" in e for e in invalid_values) else "FAIL",
            "negative_quantities": "PASS" if not any("negativa" in e for e in invalid_values) else "FAIL",
            "duplicate_rows": "PASS" if not duplicates else "FAIL",
            "incomplete_months": "PASS" if not incomplete_months else "FAIL",
            "total_consistency": _check_totals(normalized_rows),
        },
        "output_files": {
            "complete": str(OUT_COMPLETE),
            "model": str(OUT_MODEL),
            "report": str(OUT_REPORT),
        },
    }

    return {"rows": normalized_rows, "model_rows": model_rows, "report": report}


def _check_totals(rows: list[dict[str, Any]]) -> str:
    for r in rows:
        if r["total_visitors"] != r["national_visitors"] + r["foreign_visitors"]:
            return "FAIL"
    return "PASS"


def _build_column_map(columns: list[str]) -> dict[str, str]:
    """
    Construye un mapa de nombre normalizado (minúsculas, sin espacios extra,
    sin BOM residual) al nombre original de la columna tal como aparece en el CSV.
    El BOM (\ufeff) puede quedar en la primera columna si el archivo fue leído
    con una codificación que no lo consume automáticamente.
    """
    import unicodedata
    def _norm(s: str) -> str:
        # Eliminar BOM residual, normalizar Unicode y convertir a minúsculas
        return unicodedata.normalize("NFC", s.strip().lstrip("\ufeff")).lower()
    return {_norm(col): col for col in columns}


def _fail(message: str) -> None:
    print(f"\n[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# Escritura de salidas
# ---------------------------------------------------------------------------

def write_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"Leyendo: {RAW_FILE}")
    result = normalize(RAW_FILE)

    rows: list[dict[str, Any]] = result["rows"]
    model_rows: list[dict[str, Any]] = result["model_rows"]
    report: dict[str, Any] = result["report"]

    # Verificar que el archivo original no fue modificado
    original_size_before = os.path.getsize(RAW_FILE)

    write_csv(OUT_COMPLETE, rows, OUTPUT_COLUMNS)
    write_csv(OUT_MODEL, model_rows, OUTPUT_COLUMNS)
    write_report(OUT_REPORT, report)

    original_size_after = os.path.getsize(RAW_FILE)
    assert original_size_before == original_size_after, (
        "¡El archivo original fue modificado accidentalmente!"
    )

    print(f"\n[OK] Archivo completo      : {OUT_COMPLETE}  ({len(rows)} meses)")
    print(f"[OK] Archivo del modelo    : {OUT_MODEL}  ({len(model_rows)} meses)")
    print(f"[OK] Reporte de calidad    : {OUT_REPORT}")
    print(f"\nDelimitador detectado   : {report['delimiter_detected']!r}")
    print(f"Codificacion utilizada  : {report['encoding_used']}")
    print(f"Filas originales        : {report['original_row_count']}")
    print(f"Meses normalizados      : {report['months_normalized']}")
    print(f"Meses en el modelo      : {report['months_in_model']}")
    print(f"Cobertura completa      : {report['first_date_available']} -> {report['last_date_available']}")
    print(f"Cobertura del modelo    : {report['first_date_model']} -> {report['last_date_model']}")

    if report["warnings"]:
        print(f"\nAdvertencias ({len(report['warnings'])}):")
        for w in report["warnings"]:
            print(f"  [!] {w}")
    else:
        print("\nSin advertencias.")

    print("\nValidaciones:")
    for k, v in report["validations"].items():
        icon = "[OK]" if v == "PASS" else "[FAIL]"
        print(f"  {icon} {k}: {v}")

    print("\n[OK] El archivo original data/raw/Tabla_data.csv no fue modificado.")


if __name__ == "__main__":
    main()
