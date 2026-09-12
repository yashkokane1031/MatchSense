"""initial_tables

Revision ID: 4a5961dce17b
Revises:
Create Date: 2026-09-12 21:28:31.579708

"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '4a5961dce17b'
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: create matches, teams, and predictions tables."""
    # Teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("canonical_name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # Matches table
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("season", sa.String(length=10), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("home_team", sa.String(length=50), nullable=False),
        sa.Column("away_team", sa.String(length=50), nullable=False),
        sa.Column("home_goals", sa.Integer(), nullable=False),
        sa.Column("away_goals", sa.Integer(), nullable=False),
        sa.Column("result", sa.String(length=1), nullable=False),
        sa.Column("ht_home_goals", sa.Integer(), nullable=True),
        sa.Column("ht_away_goals", sa.Integer(), nullable=True),
        sa.Column("home_shots", sa.Integer(), nullable=True),
        sa.Column("away_shots", sa.Integer(), nullable=True),
        sa.Column("home_shots_on_target", sa.Integer(), nullable=True),
        sa.Column("away_shots_on_target", sa.Integer(), nullable=True),
        sa.Column("home_corners", sa.Integer(), nullable=True),
        sa.Column("away_corners", sa.Integer(), nullable=True),
        sa.Column("home_fouls", sa.Integer(), nullable=True),
        sa.Column("away_fouls", sa.Integer(), nullable=True),
        sa.Column("home_yellows", sa.Integer(), nullable=True),
        sa.Column("away_yellows", sa.Integer(), nullable=True),
        sa.Column("home_reds", sa.Integer(), nullable=True),
        sa.Column("away_reds", sa.Integer(), nullable=True),
        sa.Column("avg_odds_home", sa.Float(), nullable=True),
        sa.Column("avg_odds_draw", sa.Float(), nullable=True),
        sa.Column("avg_odds_away", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("season", "date", "home_team", "away_team", name="uq_match"),
    )
    op.create_index(op.f("ix_matches_season"), "matches", ["season"], unique=False)
    op.create_index(op.f("ix_matches_date"), "matches", ["date"], unique=False)
    op.create_index(op.f("ix_matches_home_team"), "matches", ["home_team"], unique=False)
    op.create_index(op.f("ix_matches_away_team"), "matches", ["away_team"], unique=False)

    # Predictions table
    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=True),
        sa.Column("model_name", sa.String(length=30), nullable=False),
        sa.Column("home_team", sa.String(length=50), nullable=False),
        sa.Column("away_team", sa.String(length=50), nullable=False),
        sa.Column("prob_home", sa.Float(), nullable=False),
        sa.Column("prob_draw", sa.Float(), nullable=False),
        sa.Column("prob_away", sa.Float(), nullable=False),
        sa.Column("predicted_score_home", sa.Integer(), nullable=False),
        sa.Column("predicted_score_away", sa.Integer(), nullable=False),
        sa.Column("score_distribution", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_predictions_match_id"), "predictions", ["match_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema: drop predictions, matches, and teams tables."""
    op.drop_index(op.f("ix_predictions_match_id"), table_name="predictions")
    op.drop_table("predictions")
    op.drop_index(op.f("ix_matches_away_team"), table_name="matches")
    op.drop_index(op.f("ix_matches_home_team"), table_name="matches")
    op.drop_index(op.f("ix_matches_date"), table_name="matches")
    op.drop_index(op.f("ix_matches_season"), table_name="matches")
    op.drop_table("matches")
    op.drop_table("teams")
