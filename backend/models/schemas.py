"""SQLAlchemy ORM models for MatchSense.

Three core tables:
- Match: Historical match results with stats and bookmaker odds
- Team: Canonical team names with normalization
- Prediction: Model predictions with full score distributions
"""

from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Match(Base):
    """A single Premier League match with result, stats, and bookmaker odds."""

    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("season", "date", "home_team", "away_team", name="uq_match"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    season: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    home_team: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    away_team: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Result
    home_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    away_goals: Mapped[int] = mapped_column(Integer, nullable=False)
    result: Mapped[str] = mapped_column(String(1), nullable=False)  # H/D/A

    # Half-time
    ht_home_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ht_away_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Match stats
    home_shots: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_shots: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_shots_on_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_shots_on_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_corners: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_corners: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_fouls: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_fouls: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_yellows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_yellows: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_reds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_reds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Bookmaker odds (market average — used as baseline)
    avg_odds_home: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_odds_draw: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_odds_away: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Match {self.home_team} {self.home_goals}-{self.away_goals} "
            f"{self.away_team} ({self.date})>"
        )


class Team(Base):
    """A Premier League team with canonical name for normalization."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    canonical_name: Mapped[str] = mapped_column(String(50), nullable=False)

    def __repr__(self) -> str:
        return f"<Team {self.name}>"


class Prediction(Base):
    """A model prediction for a match, storing full probability distributions."""

    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    match_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )  # null for hypothetical H2H
    model_name: Mapped[str] = mapped_column(String(30), nullable=False)  # "dixon_coles"
    home_team: Mapped[str] = mapped_column(String(50), nullable=False)
    away_team: Mapped[str] = mapped_column(String(50), nullable=False)

    # Outcome probabilities
    prob_home: Mapped[float] = mapped_column(Float, nullable=False)
    prob_draw: Mapped[float] = mapped_column(Float, nullable=False)
    prob_away: Mapped[float] = mapped_column(Float, nullable=False)

    # Most likely score
    predicted_score_home: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_score_away: Mapped[int] = mapped_column(Integer, nullable=False)

    # Full (max_goals+1 x max_goals+1) probability matrix as JSON
    score_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return (
            f"<Prediction {self.model_name}: {self.home_team} vs {self.away_team} "
            f"({self.prob_home:.2f}/{self.prob_draw:.2f}/{self.prob_away:.2f})>"
        )
