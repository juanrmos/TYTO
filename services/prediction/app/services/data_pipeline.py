"""Validated, transactional imports and immutable generator version materialization."""

import csv
from datetime import date
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import fingerprint
from app.core.synthetic_generator import compute_p95_global, generate_month
from app.db.models import (
    EstimationEngineVersion,
    MonthlyVisitorRecord,
    SyntheticDailyRecord,
    SyntheticGeneratorVersion,
    TouristDestination,
)

OFFICIAL_URL = "https://visitaareasnaturales.sernanp.gob.pe/anps/parque-nacional-de-tingo-maria/"


def parse_monthly_csv(path: Path, source: str) -> list[dict]:
    if not source or len(source) > 200:
        raise ValueError("La referencia de fuente debe tener entre 1 y 200 caracteres")
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"year", "month", "total_visitors"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Faltan columnas obligatorias en el CSV")
        records, seen = [], set()
        for line, row in enumerate(reader, 2):
            year, month = int(row["year"]), int(row["month"])
            date(year, month, 1)
            if year < 1900 or (year, month) in seen:
                raise ValueError(f"Año inválido o mes duplicado en fila {line}")
            seen.add((year, month))

            def number(name):
                value = row.get(name, "")
                if value is None or not value.strip():
                    return None
                result = int(value)
                if result < 0:
                    raise ValueError(f"Valor negativo en fila {line}")
                return result

            total, national, foreign = [
                number(k) for k in ("total_visitors", "national_visitors", "foreign_visitors")
            ]
            status = row.get("availability_status") or (
                "ZERO_REPORTED" if total == 0 else "AVAILABLE"
            )
            if status not in {"AVAILABLE", "ZERO_REPORTED", "INCOMPLETE", "NOT_YET_AVAILABLE"}:
                raise ValueError(f"Estado desconocido en fila {line}")
            if status == "AVAILABLE" and (total is None or total <= 0):
                raise ValueError("AVAILABLE requiere total positivo")
            if status == "ZERO_REPORTED" and total != 0:
                raise ValueError("ZERO_REPORTED requiere cero explícito")
            if status == "NOT_YET_AVAILABLE" and total is not None:
                raise ValueError("Un mes no publicado no puede tener un total")
            if (
                all(v is not None for v in (total, national, foreign))
                and total != national + foreign
            ):
                raise ValueError(f"Total inconsistente en fila {line}")
            records.append(
                dict(
                    year=year,
                    month=month,
                    total_visitors=total,
                    national_visitors=national,
                    foreign_visitors=foreign,
                    availability_status=status,
                    source_reference=source,
                )
            )
    if not records:
        raise ValueError("El CSV no contiene registros")
    return records


async def seed_destination(session: AsyncSession, slug: str) -> TouristDestination:
    await session.execute(
        insert(TouristDestination)
        .values(
            slug=slug,
            name="Cueva de las Lechuzas",
            latitude=-9.3008,
            longitude=-76.0026,
            timezone="America/Lima",
            official_url=OFFICIAL_URL,
            tickets_url="https://visitaareasnaturales.sernanp.gob.pe/tuticket/",
            directions_url=OFFICIAL_URL,
            is_active=True,
        )
        .on_conflict_do_nothing(index_elements=["slug"])
    )
    return await session.scalar(select(TouristDestination).where(TouristDestination.slug == slug))


async def import_records(
    session: AsyncSession, destination: TouristDestination, records: list[dict]
) -> int:
    count = 0
    for record in records:
        existing = await session.scalar(
            select(MonthlyVisitorRecord).where(
                MonthlyVisitorRecord.destination_id == destination.id,
                MonthlyVisitorRecord.year == record["year"],
                MonthlyVisitorRecord.month == record["month"],
            )
        )
        if existing:
            if any(getattr(existing, k) != v for k, v in record.items()):
                raise ValueError(
                    "El mes ya existe con datos o fuente distintos; revisar antes de sustituir"
                )
            continue
        session.add(MonthlyVisitorRecord(destination_id=destination.id, **record))
        count += 1
    await session.flush()
    return count


async def generate_dataset(
    session: AsyncSession, destination: TouristDestination, parameters: dict, calendar: dict
) -> SyntheticGeneratorVersion:
    # Serialize bootstrap/regeneration transactions for a destination.
    await session.execute(
        text("SELECT pg_advisory_xact_lock(hashtext(:slug))"), {"slug": destination.slug}
    )
    monthly = list(
        (
            await session.scalars(
                select(MonthlyVisitorRecord)
                .where(
                    MonthlyVisitorRecord.destination_id == destination.id,
                    MonthlyVisitorRecord.year >= 2022,
                    MonthlyVisitorRecord.availability_status.in_(["AVAILABLE", "ZERO_REPORTED"]),
                )
                .order_by(MonthlyVisitorRecord.year, MonthlyVisitorRecord.month)
            )
        ).all()
    )
    if not monthly:
        raise ValueError("No existen datos mensuales para generar el patrón")
    if any(not calendar["start_year"] <= r.year <= calendar["end_year"] for r in monthly):
        raise ValueError("Actualizar el calendario antes de ampliar el periodo de datos")
    metadata = {
        "parameters": parameters,
        "calendar": calendar,
        "source_records": [
            {
                "year": r.year,
                "month": r.month,
                "total": r.total_visitors,
                "status": r.availability_status,
                "source": r.source_reference,
            }
            for r in monthly
        ],
    }
    metadata["fingerprint"] = fingerprint(metadata)
    version = await session.scalar(
        select(SyntheticGeneratorVersion).where(
            SyntheticGeneratorVersion.version_code == parameters["generator_version"]
        )
    )
    if version:
        if version.parameters_json["fingerprint"] != metadata["fingerprint"]:
            raise ValueError("Entradas modificadas: asigne una nueva generator_version")
        return version
    daily = []
    for row in monthly:
        records = generate_month(
            row.year,
            row.month,
            row.total_visitors,
            parameters["generator_version"],
            calendar["events"],
            parameters,
        )
        if sum(r["estimated_visitors"] for r in records) != row.total_visitors:
            raise ValueError("Error de conservación mensual")
        daily.extend(records)
    version = SyntheticGeneratorVersion(
        version_code=parameters["generator_version"],
        p95_global=compute_p95_global(daily),
        parameters_json=metadata,
        record_count=len(daily),
    )
    session.add(version)
    await session.flush()
    session.add_all(
        [
            SyntheticDailyRecord(
                destination_id=destination.id, generator_version_id=version.id, **r
            )
            for r in daily
        ]
    )
    return version


async def seed_engine(session: AsyncSession, parameters: dict) -> EstimationEngineVersion:
    existing = await session.scalar(
        select(EstimationEngineVersion).where(
            EstimationEngineVersion.version_code == parameters["engine_version"]
        )
    )
    if existing:
        if existing.weights_json != parameters:
            raise ValueError("Parámetros modificados: asigne una nueva engine_version")
        return existing
    version = EstimationEngineVersion(
        version_code=parameters["engine_version"],
        weights_json=parameters,
        thresholds_json={k: v for k, v in parameters.items() if "threshold" in k or "limit" in k},
    )
    session.add(version)
    await session.flush()
    return version
