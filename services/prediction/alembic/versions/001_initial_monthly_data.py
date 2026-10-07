"""initial monthly data — frozen PostgreSQL DDL."""

from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TABLE tourist_destinations (\n\tslug VARCHAR(100) NOT NULL, \n\tname VARCHAR(200) NOT NULL, \n\tlatitude NUMERIC(9, 6) NOT NULL, \n\tlongitude NUMERIC(9, 6) NOT NULL, \n\ttimezone VARCHAR(50) NOT NULL, \n\tofficial_url TEXT, \n\ttickets_url TEXT, \n\tdirections_url TEXT, \n\tis_active BOOLEAN DEFAULT 'true' NOT NULL, \n\tcreated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tid UUID NOT NULL, \n\tPRIMARY KEY (id), \n\tUNIQUE (slug)\n)"
    )
    op.execute(
        "CREATE TABLE monthly_visitor_records (\n\tdestination_id UUID NOT NULL, \n\tyear SMALLINT NOT NULL, \n\tmonth SMALLINT NOT NULL, \n\ttotal_visitors INTEGER, \n\tnational_visitors INTEGER, \n\tforeign_visitors INTEGER, \n\tavailability_status VARCHAR(30) NOT NULL, \n\tsource_reference VARCHAR(200) NOT NULL, \n\timported_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tid UUID NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT uq_month_source UNIQUE (destination_id, year, month, source_reference), \n\tCONSTRAINT ck_month CHECK (month BETWEEN 1 AND 12), \n\tCONSTRAINT ck_year CHECK (year >= 1900), \n\tCONSTRAINT ck_total CHECK (total_visitors IS NULL OR total_visitors >= 0), \n\tCONSTRAINT ck_national CHECK (national_visitors IS NULL OR national_visitors >= 0), \n\tCONSTRAINT ck_foreign CHECK (foreign_visitors IS NULL OR foreign_visitors >= 0), \n\tCONSTRAINT ck_availability CHECK ((availability_status = 'AVAILABLE' AND total_visitors > 0) OR (availability_status = 'ZERO_REPORTED' AND total_visitors = 0) OR availability_status IN ('INCOMPLETE', 'NOT_YET_AVAILABLE')), \n\tFOREIGN KEY(destination_id) REFERENCES tourist_destinations (id)\n)"
    )


def downgrade() -> None:
    op.drop_table("monthly_visitor_records")
    op.drop_table("tourist_destinations")
