"""Generate an immutable, versioned synthetic dataset in PostgreSQL."""

import asyncio

from _bootstrap import ROOT  # noqa: F401
from app.config import Settings, load_configuration
from app.db.session import create_database
from app.services.data_pipeline import generate_dataset, seed_destination, seed_engine


async def run() -> None:
    settings = Settings()
    parameters, calendar = load_configuration(settings.data_dir)
    engine, sessions = create_database(settings)
    try:
        async with sessions.begin() as session:
            destination = await seed_destination(session, settings.destination_slug)
            generator = await generate_dataset(session, destination, parameters, calendar)
            await seed_engine(session, parameters)
        print(
            f"Generador {generator.version_code}: {generator.record_count} días; p95={generator.p95_global}"
        )
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run())
