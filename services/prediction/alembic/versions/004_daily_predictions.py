"""daily predictions — frozen PostgreSQL DDL."""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "CREATE TABLE weather_snapshots (\n\tdestination_id UUID NOT NULL, \n\tfetched_at TIMESTAMP WITH TIME ZONE NOT NULL, \n\tvalid_until TIMESTAMP WITH TIME ZONE NOT NULL, \n\tprovider VARCHAR(50) NOT NULL, \n\traw_response_json JSONB NOT NULL, \n\tnormalized_json JSONB NOT NULL, \n\thorizon_days SMALLINT NOT NULL, \n\tid UUID NOT NULL, \n\tPRIMARY KEY (id), \n\tFOREIGN KEY(destination_id) REFERENCES tourist_destinations (id)\n)"
    )
    op.execute("CREATE INDEX ix_weather_snapshots_fetched_at ON weather_snapshots (fetched_at)")
    op.execute(
        "CREATE INDEX ix_weather_snapshots_destination_id ON weather_snapshots (destination_id)"
    )
    op.execute(
        "CREATE TABLE daily_predictions (\n\tdestination_id UUID NOT NULL, \n\tengine_version_id UUID NOT NULL, \n\tgenerator_version_id UUID NOT NULL, \n\tweather_snapshot_id UUID, \n\tprediction_date DATE NOT NULL, \n\tgenerated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, \n\tref_mensual INTEGER, \n\testimated_visitors_day INTEGER, \n\tscore_afluencia SMALLINT, \n\tnivel_afluencia VARCHAR(10), \n\tscore_conveniencia SMALLINT, \n\tcategoria_recomendacion VARCHAR(30), \n\tis_best_option BOOLEAN NOT NULL, \n\tbest_option_label VARCHAR(40), \n\trecommendation_template_key VARCHAR(60), \n\tactive_factors_json JSONB, \n\tis_degraded BOOLEAN NOT NULL, \n\tdegraded_reason VARCHAR(100), \n\tid UUID NOT NULL, \n\tPRIMARY KEY (id), \n\tCONSTRAINT ck_affluence_score CHECK (score_afluencia BETWEEN 0 AND 100), \n\tCONSTRAINT ck_convenience_score CHECK (score_conveniencia BETWEEN 0 AND 100), \n\tFOREIGN KEY(destination_id) REFERENCES tourist_destinations (id), \n\tFOREIGN KEY(engine_version_id) REFERENCES estimation_engine_versions (id), \n\tFOREIGN KEY(generator_version_id) REFERENCES synthetic_generator_versions (id), \n\tFOREIGN KEY(weather_snapshot_id) REFERENCES weather_snapshots (id)\n)"
    )
    op.execute(
        "CREATE INDEX ix_prediction_destination_date ON daily_predictions (destination_id, prediction_date)"
    )


def downgrade() -> None:
    op.drop_table("daily_predictions")
    op.drop_table("weather_snapshots")
