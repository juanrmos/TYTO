"""synthetic records — frozen PostgreSQL DDL."""

from alembic import op

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TABLE synthetic_generator_versions (\n\tversion_code VARCHAR(20) NOT NULL, \n\tp95_global NUMERIC(12, 4) NOT NULL, \n\tparameters_json JSONB NOT NULL, \n\tgenerated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\trecord_count INTEGER NOT NULL, \n\tid UUID NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (version_code)\n)"
    )
    op.execute(
        "CREATE TABLE synthetic_daily_records (\n\tdestination_id UUID NOT NULL, \n\tgenerator_version_id UUID NOT NULL, \n\tdate DATE NOT NULL, \n\testimated_visitors INTEGER NOT NULL, \n\tday_weight NUMERIC(8, 6) NOT NULL, \n\tfactors_json JSONB NOT NULL, \n\tis_synthetic BOOLEAN DEFAULT 'true' NOT NULL, \n\tid UUID NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_synthetic_day UNIQUE (destination_id, generator_version_id, date), \n\tCONSTRAINT ck_synthetic_nonnegative CHECK (estimated_visitors >= 0), \n\tFOREIGN KEY(destination_id) REFERENCES tourist_destinations (id), \n\tFOREIGN KEY(generator_version_id) REFERENCES synthetic_generator_versions (id)\n)"
    )
    op.execute("CREATE INDEX ix_synthetic_daily_records_date ON synthetic_daily_records (date)")


def downgrade() -> None:
    op.drop_table("synthetic_daily_records")
    op.drop_table("synthetic_generator_versions")
