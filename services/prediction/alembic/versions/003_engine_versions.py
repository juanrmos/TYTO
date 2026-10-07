"""engine versions — frozen PostgreSQL DDL."""

from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TABLE estimation_engine_versions (\n\tversion_code VARCHAR(20) NOT NULL, \n\tthresholds_json JSONB NOT NULL, \n\tweights_json JSONB NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tid UUID NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (version_code)\n)"
    )


def downgrade() -> None:
    op.drop_table("estimation_engine_versions")
