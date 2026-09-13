"""phase3_models_and_fixtures

Revision ID: a1b2c3d4e5f6
Revises: 4a5961dce17b
Create Date: 2026-09-13 14:00:00.000000

"""
from collections.abc import Sequence
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID
from alembic import op

revision: str = 'a1b2c3d4e5f6'
down_revision: str | Sequence[str] | None = '4a5961dce17b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "models",
        sa.Column("id", UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("model_name", sa.String(length=64), nullable=False),
        sa.Column("version", sa.String(length=64), nullable=False),
        sa.Column("artifact_bytes", sa.LargeBinary(), nullable=False),
        sa.Column("manifest", JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_active_model_per_name",
        "models",
        ["model_name"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )
    op.create_index("idx_models_lookup", "models", ["model_name", "is_active", "updated_at"], unique=False)

    op.create_table(
        "fixtures",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("season", sa.String(length=10), nullable=False),
        sa.Column("gameweek", sa.Integer(), nullable=False),
        sa.Column("kickoff_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("home_team", sa.String(length=50), nullable=False),
        sa.Column("away_team", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), server_default="SCHEDULED", nullable=False),
        sa.Column("precomputed_predictions", JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_fixtures_upcoming", "fixtures", ["status", "kickoff_time"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_fixtures_upcoming", table_name="fixtures")
    op.drop_table("fixtures")
    op.drop_index("idx_models_lookup", table_name="models")
    op.drop_index("uq_active_model_per_name", table_name="models")
    op.drop_table("models")
