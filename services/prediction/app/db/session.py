from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Settings


def create_database(settings: Settings):
    engine = create_async_engine(
        settings.connection_url(), pool_pre_ping=True, connect_args={"timeout": 10}
    )
    return engine, async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
