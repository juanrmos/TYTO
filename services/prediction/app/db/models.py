"""PostgreSQL entities and constraints for the seven documented tables."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Identity:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


class TouristDestination(Identity, Base):
    __tablename__ = "tourist_destinations"
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    latitude: Mapped[float] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float] = mapped_column(Numeric(9, 6))
    timezone: Mapped[str] = mapped_column(String(50))
    official_url: Mapped[str | None] = mapped_column(Text)
    tickets_url: Mapped[str | None] = mapped_column(Text)
    directions_url: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MonthlyVisitorRecord(Identity, Base):
    __tablename__ = "monthly_visitor_records"
    destination_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tourist_destinations.id"))
    year: Mapped[int] = mapped_column(SmallInteger)
    month: Mapped[int] = mapped_column(SmallInteger)
    total_visitors: Mapped[int | None] = mapped_column(Integer)
    national_visitors: Mapped[int | None] = mapped_column(Integer)
    foreign_visitors: Mapped[int | None] = mapped_column(Integer)
    availability_status: Mapped[str] = mapped_column(String(30))
    source_reference: Mapped[str] = mapped_column(String(200))
    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    __table_args__ = (
        UniqueConstraint(
            "destination_id", "year", "month", "source_reference", name="uq_month_source"
        ),
        CheckConstraint("month BETWEEN 1 AND 12", name="ck_month"),
        CheckConstraint("year >= 1900", name="ck_year"),
        CheckConstraint("total_visitors IS NULL OR total_visitors >= 0", name="ck_total"),
        CheckConstraint("national_visitors IS NULL OR national_visitors >= 0", name="ck_national"),
        CheckConstraint("foreign_visitors IS NULL OR foreign_visitors >= 0", name="ck_foreign"),
        CheckConstraint(
            "(availability_status = 'AVAILABLE' AND total_visitors > 0) OR "
            "(availability_status = 'ZERO_REPORTED' AND total_visitors = 0) OR "
            "availability_status IN ('INCOMPLETE', 'NOT_YET_AVAILABLE')",
            name="ck_availability",
        ),
    )


class SyntheticGeneratorVersion(Identity, Base):
    __tablename__ = "synthetic_generator_versions"
    version_code: Mapped[str] = mapped_column(String(20), unique=True)
    p95_global: Mapped[float] = mapped_column(Numeric(12, 4))
    parameters_json: Mapped[dict] = mapped_column(JSONB)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    record_count: Mapped[int] = mapped_column(Integer)


class SyntheticDailyRecord(Identity, Base):
    __tablename__ = "synthetic_daily_records"
    destination_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tourist_destinations.id"))
    generator_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("synthetic_generator_versions.id")
    )
    date: Mapped[date] = mapped_column(Date, index=True)
    estimated_visitors: Mapped[int] = mapped_column(Integer)
    day_weight: Mapped[float] = mapped_column(Numeric(8, 6))
    factors_json: Mapped[dict] = mapped_column(JSONB)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    __table_args__ = (
        UniqueConstraint("destination_id", "generator_version_id", "date", name="uq_synthetic_day"),
        CheckConstraint("estimated_visitors >= 0", name="ck_synthetic_nonnegative"),
    )


class EstimationEngineVersion(Identity, Base):
    __tablename__ = "estimation_engine_versions"
    version_code: Mapped[str] = mapped_column(String(20), unique=True)
    thresholds_json: Mapped[dict] = mapped_column(JSONB)
    weights_json: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WeatherSnapshot(Identity, Base):
    __tablename__ = "weather_snapshots"
    destination_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tourist_destinations.id"), index=True
    )
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    valid_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    provider: Mapped[str] = mapped_column(String(50), default="open-meteo")
    raw_response_json: Mapped[dict] = mapped_column(JSONB)
    normalized_json: Mapped[dict] = mapped_column(JSONB)
    horizon_days: Mapped[int] = mapped_column(SmallInteger)


class DailyPrediction(Identity, Base):
    __tablename__ = "daily_predictions"
    destination_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tourist_destinations.id"))
    engine_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("estimation_engine_versions.id")
    )
    generator_version_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("synthetic_generator_versions.id")
    )
    weather_snapshot_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("weather_snapshots.id")
    )
    prediction_date: Mapped[date] = mapped_column(Date)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    ref_mensual: Mapped[int | None] = mapped_column(Integer)
    estimated_visitors_day: Mapped[int | None] = mapped_column(Integer)
    score_afluencia: Mapped[int | None] = mapped_column(SmallInteger)
    nivel_afluencia: Mapped[str | None] = mapped_column(String(10))
    score_conveniencia: Mapped[int | None] = mapped_column(SmallInteger)
    categoria_recomendacion: Mapped[str | None] = mapped_column(String(30))
    is_best_option: Mapped[bool] = mapped_column(Boolean, default=False)
    best_option_label: Mapped[str | None] = mapped_column(String(40))
    recommendation_template_key: Mapped[str | None] = mapped_column(String(60))
    active_factors_json: Mapped[list | None] = mapped_column(JSONB)
    is_degraded: Mapped[bool] = mapped_column(Boolean, default=False)
    degraded_reason: Mapped[str | None] = mapped_column(String(100))
    __table_args__ = (
        Index("ix_prediction_destination_date", "destination_id", "prediction_date"),
        CheckConstraint("score_afluencia BETWEEN 0 AND 100", name="ck_affluence_score"),
        CheckConstraint("score_conveniencia BETWEEN 0 AND 100", name="ck_convenience_score"),
    )
