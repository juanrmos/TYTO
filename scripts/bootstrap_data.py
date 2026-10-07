"""Idempotent initial import and generation after Alembic migrations."""

import asyncio

from _bootstrap import ROOT  # noqa: F401
from app.config import Settings, load_configuration
from app.db.session import create_database
from app.services.data_pipeline import (
    generate_dataset,
    import_records,
    parse_monthly_csv,
    seed_destination,
    seed_engine,
)


async def run() -> None:
    settings = Settings()
    parameters, calendar = load_configuration(settings.data_dir)
    records = parse_monthly_csv(
        settings.data_dir / "processed/visitas_mensuales_modelo.csv", "MINCETUR:Tabla_data.csv"
    )
    engine, sessions = create_database(settings)
    try:
        async with sessions.begin() as session:
            destination = await seed_destination(session, settings.destination_slug)
            await import_records(session, destination, records)
            version = await generate_dataset(session, destination, parameters, calendar)
            await seed_engine(session, parameters)
        print(f"Inicialización completa: {len(records)} meses, {version.record_count} días.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
