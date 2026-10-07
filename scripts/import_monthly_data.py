"""Import validated monthly records transactionally; safe to rerun."""

import argparse
import asyncio

from _bootstrap import ROOT  # noqa: F401
from app.config import Settings
from app.db.session import create_database
from app.services.data_pipeline import import_records, parse_monthly_csv, seed_destination


async def run() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=str)
    parser.add_argument("--source", default="MINCETUR:Tabla_data.csv")
    args = parser.parse_args()
    from pathlib import Path

    settings = Settings()
    path = (
        Path(args.file)
        if args.file
        else settings.data_dir / "processed/visitas_mensuales_modelo.csv"
    )
    records = parse_monthly_csv(path, args.source)
    engine, sessions = create_database(settings)
    try:
        async with sessions.begin() as session:
            destination = await seed_destination(session, settings.destination_slug)
            count = await import_records(session, destination, records)
        print(f"Importación verificada: {len(records)} meses; {count} registros nuevos.")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
